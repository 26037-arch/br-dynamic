from __future__ import annotations

import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path

import numpy as np

from brdyn.analysis import cycle_metrics
from brdyn.network import load_mechanism
from brdyn.perturb import active_parameter_names, scaled_parameter
from brdyn.solver import simulate


ROOT = Path(__file__).parents[1]
CONFIG_PATH = ROOT / "experiments" / "phase2" / "local_sensitivity.json"
BASELINE_PATH = ROOT / "experiments" / "baseline" / "dke_pooled_gate1.json"
MECHANISM_PATH = ROOT / "mechanisms" / "dke10.yaml"
OUTPUT_DIR = ROOT / "reports" / "sensitivity"
OBSERVABLES = ("mean_period_s", "iodine_peak_M", "iodide_min_M", "iodide_max_M")


def run_variant(parameter_name: str, factor: float) -> dict[str, object]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    mechanism = scaled_parameter(load_mechanism(MECHANISM_PATH), parameter_name, factor)
    try:
        result = simulate(
            mechanism, baseline["initial_concentrations_M"], tuple(config["t_span_s"]),
            method="BDF", rtol=config["rtol"], atol=config["atol_M"],
            output_points=config["output_points"], fixed_species=config["fixed_species"],
        )
        metrics = cycle_metrics(result, mechanism, config["analysis_start_s"])
        return {"parameter": parameter_name, "factor": factor, "status": "OK", "metrics": metrics}
    except Exception as exc:
        return {
            "parameter": parameter_name, "factor": factor,
            "status": "NO_MEASURABLE_OSCILLATION", "error": f"{type(exc).__name__}: {exc}",
        }


def parameter_metadata(mechanism, name: str) -> dict[str, str]:
    if name == "C9_DKE":
        return {"reaction": "R9", "confidence": "SUBSYSTEM_FIT", "role": "saturation denominator"}
    flux = next(flux for flux in mechanism.fluxes if flux.parameter["name"] == name)
    return {
        "reaction": flux.reaction_id,
        "confidence": flux.parameter["confidence"],
        "role": flux.direction,
    }


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    mechanism = load_mechanism(MECHANISM_PATH)
    parameters = active_parameter_names(mechanism)
    tasks = [
        (parameter, 1.0 + sign * delta)
        for parameter in parameters
        for delta in config["fractional_perturbations"]
        for sign in (-1, 1)
    ]
    results: dict[tuple[str, float], dict[str, object]] = {}
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run_variant, *task): task for task in tasks}
        for future in as_completed(futures):
            item = future.result()
            results[(str(item["parameter"]), float(item["factor"]))] = item

    rows: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    for parameter in parameters:
        metadata = parameter_metadata(mechanism, parameter)
        for delta in config["fractional_perturbations"]:
            minus = results[(parameter, 1.0 - delta)]
            plus = results[(parameter, 1.0 + delta)]
            if minus["status"] != "OK" or plus["status"] != "OK":
                failures.append({"parameter": parameter, "delta": delta, "minus": minus, "plus": plus})
                for observable in OBSERVABLES:
                    rows.append({
                        "parameter": parameter, **metadata, "fractional_perturbation": delta,
                        "observable": observable, "normalized_sensitivity": "",
                        "minus_value": "", "plus_value": "", "status": "FAILED_OSCILLATION",
                    })
                continue
            denominator = np.log1p(delta) - np.log1p(-delta)
            for observable in OBSERVABLES:
                minus_value = float(minus["metrics"][observable])
                plus_value = float(plus["metrics"][observable])
                sensitivity = (np.log(plus_value) - np.log(minus_value)) / denominator
                rows.append({
                    "parameter": parameter, **metadata, "fractional_perturbation": delta,
                    "observable": observable, "normalized_sensitivity": sensitivity,
                    "minus_value": minus_value, "plus_value": plus_value, "status": "OK",
                })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / "local_parameter_sensitivity.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUTPUT_DIR / "local_parameter_sensitivity_raw.json").write_text(
        json.dumps({"configuration": config, "variants": list(results.values()), "failures": failures}, indent=2) + "\n",
        encoding="utf-8",
    )

    summary = []
    for parameter in parameters:
        item = {"parameter": parameter, **parameter_metadata(mechanism, parameter)}
        for observable in OBSERVABLES:
            values = [
                float(row["normalized_sensitivity"]) for row in rows
                if row["parameter"] == parameter and row["observable"] == observable and row["status"] == "OK"
            ]
            item[observable] = float(np.median(values)) if values else None
            item[f"{observable}_spread"] = float(max(values) - min(values)) if values else None
        summary.append(item)
    summary.sort(key=lambda item: abs(item["mean_period_s"] or 0.0), reverse=True)

    lines = [
        "# Local normalized parameter sensitivity", "",
        "Sensitivities use symmetric multiplicative perturbations of +/-0.5%, +/-1%, and +/-2%.",
        "No experimental target enters these calculations and no parameter is optimized. The table", 
        "reports the median derivative across the three scales; `spread` is max minus min and is a", 
        "finite-difference stability diagnostic.", "",
        "| Rank | Parameter | DKE reaction | Confidence | S(period) | spread | S(I2 max) | S(I- min) | S(I- max) |", 
        "|---:|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(summary, start=1):
        def fmt(value):
            return "FAILED" if value is None else f"{value:.4g}"
        lines.append(
            f"| {rank} | {item['parameter']} | {item['reaction']} | {item['confidence']} | "
            f"{fmt(item['mean_period_s'])} | {fmt(item['mean_period_s_spread'])} | "
            f"{fmt(item['iodine_peak_M'])} | {fmt(item['iodide_min_M'])} | {fmt(item['iodide_max_M'])} |"
        )
    lines += ["", "## Interpretation", ""]
    if failures:
        lines.append(f"{len(failures)} parameter/scale pairs destroyed a measurable oscillation; they are listed in the raw JSON.")
    else:
        lines.append("All parameter/scale pairs retained at least two measurable post-transient iodide minima.")
    lines += [
        "", "Large magnitudes identify parameters whose independent chemistry deserves priority; they do not", 
        "authorize adjustment against the integrated BR period. Sign indicates the local direction of change.",
        "Mechanistic interpretation must be combined with provenance and subsystem compatibility evidence.", "",
    ]
    (OUTPUT_DIR / "local_parameter_sensitivity.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"parameters": len(parameters), "variants": len(tasks), "failed_pairs": len(failures), "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

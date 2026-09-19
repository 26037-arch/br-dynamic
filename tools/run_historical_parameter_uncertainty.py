from __future__ import annotations

import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path

import numpy as np

from brdyn.analysis import cycle_metrics
from brdyn.network import load_mechanism
from brdyn.perturb import set_parameter_value
from brdyn.solver import simulate


ROOT = Path(__file__).parents[1]
CONFIG_PATH = ROOT / "experiments" / "phase2" / "historical_parameter_uncertainty.json"
BASELINE_PATH = ROOT / "experiments" / "baseline" / "dke_pooled_gate1.json"
OUTPUT_DIR = ROOT / "reports" / "uncertainty"


def latin_hypercube(n: int, d: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    design = np.empty((n, d))
    for column in range(d):
        design[:, column] = (rng.permutation(n) + 0.5) / n
    return design


def run_case(sample_id: int, values: dict[str, float]) -> dict[str, object]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    mechanism = load_mechanism(ROOT / "mechanisms" / "dke10.yaml")
    for name, value in values.items():
        mechanism = set_parameter_value(mechanism, name, value)
    try:
        result = simulate(
            mechanism, baseline["initial_concentrations_M"], tuple(config["t_span_s"]),
            method="BDF", rtol=config["rtol"], atol=config["atol_M"],
            output_points=config["output_points"], fixed_species=config["fixed_species"],
        )
        metrics = cycle_metrics(result, mechanism, config["analysis_start_s"])
        return {
            "sample_id": sample_id, **values, "status": "OSCILLATORY",
            "complete_period_count": metrics["complete_period_count"],
            "mean_period_s": metrics["mean_period_s"],
            "iodine_peak_M": metrics["iodine_peak_M"],
            "iodide_min_M": metrics["iodide_min_M"],
            "iodide_max_M": metrics["iodide_max_M"],
        }
    except Exception as exc:
        return {"sample_id": sample_id, **values, "status": "FAILED", "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    names = list(config["bounds"])
    design = latin_hypercube(config["sample_count"], len(names), config["seed"])
    cases = []
    for sample_id, unit_row in enumerate(design, start=1):
        values = {
            name: config["bounds"][name]["low"]
            + float(unit_row[j]) * (config["bounds"][name]["high"] - config["bounds"][name]["low"])
            for j, name in enumerate(names)
        }
        cases.append((sample_id, values))
    rows = []
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(run_case, *case) for case in cases]
        for future in as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda row: int(row["sample_id"]))
    valid = [row for row in rows if row["status"] == "OSCILLATORY"]
    ranges = {
        metric: {"min": min(float(row[metric]) for row in valid), "max": max(float(row[metric]) for row in valid)}
        for metric in ("mean_period_s", "iodine_peak_M", "iodide_min_M", "iodide_max_M")
    }
    targets = config["experimental_targets_reserved_for_assessment_only"]
    conclusions = {
        "period_target_inside_numeric_subset_envelope": ranges["mean_period_s"]["min"] <= targets["mean_period_s"] <= ranges["mean_period_s"]["max"],
        "iodine_peak_target_inside_numeric_subset_envelope": ranges["iodine_peak_M"]["min"] <= targets["iodine_peak_M"] <= ranges["iodine_peak_M"]["max"],
        "full_historical_parameter_uncertainty": "INDETERMINATE",
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with (OUTPUT_DIR / "historical_parameter_uncertainty.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    machine = {
        "configuration": config, "successful_count": len(valid), "failed_count": len(rows) - len(valid),
        "observable_ranges": ranges, "conclusions": conclusions, "samples": rows,
    }
    (OUTPUT_DIR / "historical_parameter_uncertainty.json").write_text(json.dumps(machine, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Historical-parameter uncertainty propagation", "",
        "## Scope", "",
        "This is a forward screen of the three Level 0 constants for which independent numeric",
        "bounds can be stated without converting a mechanism-form conflict into a probability",
        "distribution. It is not calibration. The deterministic 32-point Latin hypercube treats",
        "the coordinates as screening dimensions, not as claims of statistical independence.", "",
        "The propagated bounds are `k1 = 1050-1430 M^-3 s^-1`, `k8 = 7.5e5-8.3e5 M^-1 s^-1`,",
        "and `k10 = 23.8-37 M^-1 s^-1`. The k10 range is especially condition limited because",
        "its modern measurement used buffered solutions and silver at low pH.", "",
        "## Results", "",
        f"- Successful oscillatory samples: {len(valid)} of {len(rows)}.",
        f"- Period range: {ranges['mean_period_s']['min']:.6g}-{ranges['mean_period_s']['max']:.6g} s.",
        f"- I2 peak range: {ranges['iodine_peak_M']['min']:.6g}-{ranges['iodine_peak_M']['max']:.6g} M.",
        f"- I- minimum range: {ranges['iodide_min_M']['min']:.6g}-{ranges['iodide_min_M']['max']:.6g} M.",
        f"- I- maximum range: {ranges['iodide_max_M']['min']:.6g}-{ranges['iodide_max_M']['max']:.6g} M.", "",
        f"The 714.13 s target is {'inside' if conclusions['period_target_inside_numeric_subset_envelope'] else 'outside'} this envelope;",
        f"the 5.811e-4 M iodine target is {'inside' if conclusions['iodine_peak_target_inside_numeric_subset_envelope'] else 'outside'} it.", "",
        "## Interpretation", "",
        "Full historical-parameter uncertainty is **INDETERMINATE**. Ten active quantities were",
        "excluded because no defensible interval exists or because the evidence changes the rate-law",
        "topology. In particular, R5 differs by orders of magnitude, R9 is a lumped law, and R4/R6",
        "were selected in an integrated fit. Sampling arbitrary ranges for them would create false",
        "precision. This numeric subset measures only condition transfer for R1, R8, and R10.",
    ]
    (OUTPUT_DIR / "historical_parameter_uncertainty.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"successful_count": len(valid), "ranges": ranges, "conclusions": conclusions}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

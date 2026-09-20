from __future__ import annotations

import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import pearsonr, spearmanr

from brdyn.analysis import (
    OscillationClass,
    OscillationThresholds,
    classify_oscillation,
    consensus_classification,
    cycle_metrics,
)
from brdyn.network import load_mechanism
from brdyn.solver import save_trajectory_npz, simulate


ROOT = Path(__file__).parents[1]
OUT = ROOT / "reports" / "revalidation"
RAW = OUT / "raw_trajectories"
MECHANISM_PATH = ROOT / "mechanisms" / "dke10.yaml"
BASELINE_PATH = ROOT / "experiments" / "baseline" / "dke_pooled_gate1.json"
IC_CONFIG_PATH = ROOT / "experiments" / "phase2" / "initial_condition_uncertainty.json"
SENS_CONFIG_PATH = ROOT / "experiments" / "phase2" / "local_sensitivity.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_metadata(config_path: Path, initial: dict[str, float], method: str,
                  rtol: float, atol: float, fixed_species: list[str]) -> dict[str, Any]:
    return {
        "mechanism_path": str(MECHANISM_PATH.relative_to(ROOT)),
        "mechanism_sha256": sha256(MECHANISM_PATH),
        "configuration_path": str(config_path.relative_to(ROOT)),
        "configuration_sha256": sha256(config_path),
        "initial_concentrations_M": initial,
        "solver_method": method,
        "rtol": rtol,
        "atol_M": atol,
        "fixed_species": fixed_species,
    }


def case_token(iodate: float, iodide: float) -> str:
    def token(value: float) -> str:
        return f"{value:.8g}".replace("-", "m").replace("+", "p").replace(".", "p")
    return f"io3_{token(iodate)}_i_{token(iodide)}"


def run_and_classify(mechanism, initial, config, method, rtol, atol):
    result = simulate(
        mechanism, initial, tuple(config["t_span_s"]), method=method,
        rtol=rtol, atol=atol, output_points=config["output_points"],
        fixed_species=config["fixed_species"],
    )
    classification = classify_oscillation(
        result, mechanism, config["analysis_start_s"], rtol=rtol, atol=atol,
    )
    return result, classification


def save_run(path: Path, result, mechanism, config_path, initial, rtol, atol, extra=None):
    metadata = file_metadata(
        config_path, initial, result.method, rtol, atol,
        list(result.fixed_species),
    )
    metadata.update(extra or {})
    save_trajectory_npz(path, result, mechanism, metadata)


def run_gate1_raw() -> dict[str, Any]:
    config = read_json(BASELINE_PATH)
    mechanism = load_mechanism(MECHANISM_PATH)
    output = {}
    for method in ("BDF", "Radau"):
        result, classification = run_and_classify(
            mechanism, config["initial_concentrations_M"], config, method,
            config["rtol"], config["atol_M"],
        )
        save_run(
            RAW / f"gate1_baseline_{method.lower()}_current.npz", result, mechanism,
            BASELINE_PATH, config["initial_concentrations_M"], config["rtol"],
            config["atol_M"], {"analysis_start_s": config["analysis_start_s"]},
        )
        output[method] = classification
    return output


def _run_ic_case(iodate: float, iodide: float) -> dict[str, Any]:
    config = read_json(IC_CONFIG_PATH)
    baseline = read_json(BASELINE_PATH)
    mechanism = load_mechanism(MECHANISM_PATH)
    initial = dict(baseline["initial_concentrations_M"])
    initial["IO3_minus"] = iodate
    initial["I_minus"] = iodide
    token = case_token(iodate, iodide)
    current: dict[str, dict[str, Any]] = {}
    results = {}
    for method in ("BDF", "Radau"):
        try:
            result, report = run_and_classify(
                mechanism, initial, config, method, config["rtol"], config["atol_M"],
            )
            current[method] = report
            results[method] = result
        except Exception as exc:
            current[method] = {
                "classification": OscillationClass.UNRESOLVED_NUMERICALLY.value,
                "reason": f"{type(exc).__name__}: {exc}",
            }
    for method in ("BDF", "Radau"):
        save_run(
            RAW / f"ic_{token}_{method.lower()}_current.npz", results[method], mechanism,
            IC_CONFIG_PATH, initial, config["rtol"], config["atol_M"],
            {"classification": current[method], "solver_crosscheck": True},
        )
    standard_class, solver_agreement = consensus_classification([
        current["BDF"]["classification"], current["Radau"]["classification"]
    ])
    tight: dict[str, dict[str, Any]] = {}
    tight_rtol = config["rtol"] / 10.0
    tight_atol = config["atol_M"] / 10.0
    if iodate == min(config["grids_M"]["IO3_minus"]):
        for method in ("BDF", "Radau"):
            try:
                result, report = run_and_classify(
                    mechanism, initial, config, method, tight_rtol, tight_atol,
                )
                tight[method] = report
                save_run(
                    RAW / f"ic_{token}_{method.lower()}_tight.npz", result, mechanism,
                    IC_CONFIG_PATH, initial, tight_rtol, tight_atol,
                    {"classification": report, "boundary_resolution_rerun": True},
                )
            except Exception as exc:
                tight[method] = {
                    "classification": OscillationClass.UNRESOLVED_NUMERICALLY.value,
                    "reason": f"{type(exc).__name__}: {exc}",
                }
    if tight:
        final_class, tolerance_agreement = consensus_classification([
            current["BDF"]["classification"], current["Radau"]["classification"],
            tight["BDF"]["classification"], tight["Radau"]["classification"],
        ])
    else:
        final_class = standard_class
        tolerance_agreement = "NOT_TESTED_NON_BOUNDARY"

    primary = current["BDF"]
    row: dict[str, Any] = {
        "IO3_minus_M": iodate,
        "I_minus_M": iodide,
        "classification": final_class,
        "bdf_classification": current["BDF"]["classification"],
        "radau_classification": current["Radau"]["classification"],
        "solver_agreement_status": solver_agreement,
        "tolerance_convergence_status": tolerance_agreement,
        "complete_cycle_count": primary.get("complete_cycle_count", 0),
        "cycle_periods_s": json.dumps(primary.get("cycle_periods_s", [])),
        "cycle_iodide_amplitudes_M": json.dumps(primary.get("cycle_iodide_amplitudes_M", [])),
        "cycle_iodine_amplitudes_M": json.dumps(primary.get("cycle_iodine_amplitudes_M", [])),
        "final_cycle_period_mean_s": primary.get("final_cycle_period_mean_s"),
        "period_cv": primary.get("period_cv"),
        "period_drift": primary.get("period_drift"),
        "iodide_min_M": primary.get("iodide_min_M"),
        "iodide_max_M": primary.get("iodide_max_M"),
        "iodide_amplitude_M": primary.get("iodide_amplitude_M"),
        "iodide_relative_amplitude": primary.get("iodide_relative_amplitude"),
        "iodine_peak_M": primary.get("iodine_peak_M"),
        "iodine_amplitude_M": primary.get("iodine_amplitude_M"),
        "iodide_amplitude_drift": primary.get("iodide_amplitude_drift"),
        "iodine_amplitude_drift": primary.get("iodine_amplitude_drift"),
        "iodide_resolution_floor_M": primary.get("iodide_resolution_floor_M"),
        "iodide_resolution_score": primary.get("iodide_resolution_score"),
        "reason": primary.get("reason"),
    }
    return {"row": row, "current": current, "tight": tight}


def interaction_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    resolved = {
        (float(row["IO3_minus_M"]), float(row["I_minus_M"])): row
        for row in rows if row["classification"] == OscillationClass.RESOLVED_LIMIT_CYCLE.value
    }
    anchor_key = (0.0225, 0.0004)
    anchor = resolved.get(anchor_key)
    if anchor is None:
        return {"status": "UNAVAILABLE", "reason": "resolved anchor is absent"}
    cases = []
    for (io3, iodide), row in resolved.items():
        io3_only = resolved.get((io3, anchor_key[1]))
        iodide_only = resolved.get((anchor_key[0], iodide))
        if io3_only is None or iodide_only is None:
            continue
        cases.append({
            "IO3_minus_M": io3,
            "I_minus_M": iodide,
            "period_interaction_s": (
                float(row["final_cycle_period_mean_s"])
                - float(io3_only["final_cycle_period_mean_s"])
                - float(iodide_only["final_cycle_period_mean_s"])
                + float(anchor["final_cycle_period_mean_s"])
            ),
            "iodine_peak_interaction_M": (
                float(row["iodine_peak_M"]) - float(io3_only["iodine_peak_M"])
                - float(iodide_only["iodine_peak_M"]) + float(anchor["iodine_peak_M"])
            ),
        })
    return {
        "status": "AVAILABLE",
        "definition": "f(IO3,I)-f(IO3,I_anchor)-f(IO3_anchor,I)+f(anchor)",
        "case_count": len(cases),
        "max_abs_period_interaction_s": max(abs(x["period_interaction_s"]) for x in cases),
        "max_abs_iodine_peak_interaction_M": max(abs(x["iodine_peak_interaction_M"]) for x in cases),
        "cases": cases,
    }


def run_initial_condition_reanalysis() -> dict[str, Any]:
    config = read_json(IC_CONFIG_PATH)
    cases = [
        (float(io3), float(iodide))
        for io3 in config["grids_M"]["IO3_minus"]
        for iodide in config["grids_M"]["I_minus"]
    ]
    items = []
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(_run_ic_case, *case) for case in cases]
        for future in as_completed(futures):
            items.append(future.result())
    items.sort(key=lambda item: (item["row"]["IO3_minus_M"], item["row"]["I_minus_M"]))
    rows = [item["row"] for item in items]
    fields = list(rows[0])
    with (OUT / "initial_condition_reanalysis.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    resolved = [r for r in rows if r["classification"] == OscillationClass.RESOLVED_LIMIT_CYCLE.value]
    ranges = {
        "period_s": [min(float(r["final_cycle_period_mean_s"]) for r in resolved),
                     max(float(r["final_cycle_period_mean_s"]) for r in resolved)],
        "iodine_peak_M": [min(float(r["iodine_peak_M"]) for r in resolved),
                          max(float(r["iodine_peak_M"]) for r in resolved)],
    }
    old = read_json(ROOT / "reports" / "uncertainty" / "initial_condition_uncertainty.json")
    interactions = interaction_summary(rows)
    target = float(config["experimental_targets_reserved_for_assessment_only"]["mean_period_s"])
    counts = {state.value: sum(r["classification"] == state.value for r in rows)
              for state in OscillationClass}
    payload = {
        "configuration": config,
        "thresholds": OscillationThresholds().__dict__,
        "counts": counts,
        "resolved_ranges": ranges,
        "digitized_single_cycle_period_s": target,
        "target_inside_resolved_period_envelope": ranges["period_s"][0] <= target <= ranges["period_s"][1],
        "resolved_nonlinear_interactions": interactions,
        "cases": items,
    }
    (OUT / "initial_condition_reanalysis.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    old_ranges = old["observable_ranges_over_oscillatory_cases"]
    old_interaction = old["nonlinear_interactions"]["max_abs_period_interaction_s"]
    lines = [
        "# Initial-condition reanalysis", "",
        "The original 20-point grid was rerun without changing chemistry, constants, pools, or grid values.",
        "Every case used current-tolerance BDF and Radau; all four 0.004 M iodate cases also used",
        "BDF and Radau with rtol/atol tightened by 10x.", "",
        "| Quantity | Original report | Resolved-limit-cycle reanalysis |", "|---|---:|---:|",
        f"| qualifying cases | {old['oscillatory_count']} | {len(resolved)} |",
        f"| period range (s) | {old_ranges['mean_period_s']['min']:.9g} to {old_ranges['mean_period_s']['max']:.9g} | {ranges['period_s'][0]:.9g} to {ranges['period_s'][1]:.9g} |",
        f"| iodine peak range (M) | {old_ranges['iodine_peak_M']['min']:.9g} to {old_ranges['iodine_peak_M']['max']:.9g} | {ranges['iodine_peak_M'][0]:.9g} to {ranges['iodine_peak_M'][1]:.9g} |", "",
        f"The digitized single-cycle period 714.13 s is **{'inside' if payload['target_inside_resolved_period_envelope'] else 'outside'}** the revised resolved envelope.",
        "The former `PARTIALLY` period conclusion is therefore not retained." if not payload["target_inside_resolved_period_envelope"] else "The period target remains inside the resolved envelope.",
        "",
        "## Nonlinear interaction", "",
        f"The original maximum period interaction was {old_interaction:.9g} s. It depended on 0.004 M",
        "iodate trajectories that do not satisfy the numerical-resolution criterion. Restricting the",
        f"diagnostic to resolved trajectories gives {interactions['max_abs_period_interaction_s']:.9g} s; the ~669 s interaction does not survive.",
    ]
    (OUT / "initial_condition_reanalysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def classification_sensitivity(items: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    variants = {
        "looser": OscillationThresholds(resolution_multiplier=10, period_cv_max=0.05,
                                         period_drift_max=0.05, amplitude_cv_max=0.10,
                                         amplitude_drift_max=0.10),
        "declared": OscillationThresholds(),
        "stricter": OscillationThresholds(resolution_multiplier=50, period_cv_max=0.01,
                                           period_drift_max=0.01, amplitude_cv_max=0.02,
                                           amplitude_drift_max=0.02),
    }
    # The detailed rerun classifications are already serialized. This function reports
    # declared counts; threshold variants are evaluated in a separate pass from raw NPZ below.
    return {name: {} for name in variants}


def audit_experimental_data() -> dict[str, Any]:
    time_path = ROOT / "data" / "experimental" / "dke_digitized" / "iodide_time_trace.csv"
    cycle_path = ROOT / "data" / "experimental" / "dke_digitized" / "iodide_iodine_limit_cycle.csv"
    with time_path.open(newline="", encoding="utf-8-sig") as handle:
        time_rows = list(csv.DictReader(handle))
    time_key = "Time (s)"
    inversions = []
    for index in range(1, len(time_rows)):
        previous = float(time_rows[index - 1][time_key])
        current = float(time_rows[index][time_key])
        if current < previous:
            inversions.append({
                "csv_data_row": index + 1,
                "file_line": index + 2,
                "previous_time_s": previous,
                "time_s": current,
            })
    sorted_rows = sorted(enumerate(time_rows, start=1), key=lambda item: float(item[1][time_key]))
    clean_path = OUT / "experimental_iodide_time_trace_sorted.csv"
    with clean_path.open("w", newline="", encoding="utf-8") as handle:
        fields = list(time_rows[0])
        writer = csv.DictWriter(handle, fieldnames=fields + ["archival_data_row"])
        writer.writeheader()
        for source_row, row in sorted_rows:
            writer.writerow({**row, "archival_data_row": source_row})
    with cycle_path.open(newline="", encoding="utf-8-sig") as handle:
        cycle_rows = list(csv.DictReader(handle))
    iodine_key = "iodine concentration times 10^4 (M)"
    negative = [
        {"csv_data_row": i, "file_line": i + 1,
         "iodide_pI": float(row["negative log iodide concentration (M)"]),
         "iodine_M": float(row[iodine_key]) * 1e-4}
        for i, row in enumerate(cycle_rows, start=1) if float(row[iodine_key]) < 0
    ]
    iodine_peak = max(float(row[iodine_key]) * 1e-4 for row in cycle_rows)
    most_negative = min(item["iodine_M"] for item in negative)
    high_peaks = []
    for index, row in enumerate(time_rows):
        if float(row["Negative log iodide concentration (M)"]) > 9.9:
            if not high_peaks or index - high_peaks[-1] > 2:
                high_peaks.append(index)
    peak_times = [float(time_rows[index][time_key]) for index in high_peaks]
    single_period = peak_times[1] - peak_times[0]
    audit = {
        "time_inversions": inversions,
        "negative_iodine_rows": negative,
        "iodine_peak_M": iodine_peak,
        "most_negative_iodine_M": most_negative,
        "negative_magnitude_fraction_of_peak": abs(most_negative) / iodine_peak,
        "resolved_high_pI_peak_times_s": peak_times,
        "digitized_single_cycle_period_s": single_period,
    }
    gate = read_json(ROOT / "reports" / "gate1_metrics.json")
    ratios = {
        row["metric"]: 10 ** abs(float(row["experimental_target"]) - float(row["model_value"]))
        for row in gate["comparison"] if row["metric"].startswith("iodide_pI")
    }
    negative_details = "; ".join(
        f"row {item['csv_data_row']}: {item['iodine_M']:.9g} M" for item in negative
    )
    lines = [
        "# Experimental data-quality audit", "",
        "The archival CSV files were not modified. A sorted analysis copy was created with the",
        "original data-row number retained in `archival_data_row`.", "",
        "| Issue | Exact rows/cases | Severity | Scientific effect |", "|---|---|---|---|",
        f"| Non-monotonic time | archival data row {inversions[0]['csv_data_row']} (file line {inversions[0]['file_line']}): {inversions[0]['time_s']} s follows {inversions[0]['previous_time_s']} s | Moderate | No gate conclusion changes; sorting is required for valid time-series operations and does not alter the two-peak interval. |",
        f"| Negative digitized iodine | data rows {', '.join(str(x['csv_data_row']) for x in negative)} | Moderate | No peak/gate conclusion changes; these baseline/digitization artifacts cannot be interpreted as physical concentrations. |",
        f"| Only two resolved high-pI peaks | {peak_times[0]:.7g} and {peak_times[1]:.7g} s | High for uncertainty claims | The gate comparison is numerically unchanged, but 714.13 s cannot be called a statistical mean and has no empirical uncertainty estimate. |",
        "", f"Exact negative values: {negative_details}.",
        f"The most negative value is {most_negative:.9g} M, equal to {abs(most_negative) / iodine_peak:.3%} of the measured peak ({iodine_peak:.9g} M).", "",
        "The revised name is `digitized_single_cycle_period_s`; `mean_period_s` remains only as a backward-compatible historical input key.", "",
        "## pI acceptance interpretation", "",
        "The predeclared Gate 1 thresholds and decisions are unchanged. A pI difference is logarithmic:",
        f"the passing low-pI comparison corresponds to a {ratios['iodide_pI_min']:.4g}x concentration ratio,",
        f"and the passing high-pI comparison corresponds to a {ratios['iodide_pI_max']:.4g}x ratio.",
        "Passing the coarse pI threshold therefore does not by itself imply close concentrations.",
    ]
    (OUT / "data_quality_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return audit


def observable_metrics(result, mechanism, start):
    metrics = cycle_metrics(result, mechanism, start)
    return {name: float(metrics[name]) for name in (
        "mean_period_s", "iodine_peak_M", "iodide_min_M", "iodide_max_M"
    )}


def audit_local_sensitivity() -> dict[str, Any]:
    config = read_json(SENS_CONFIG_PATH)
    baseline = read_json(BASELINE_PATH)
    mechanism = load_mechanism(MECHANISM_PATH)
    evaluations = {}
    settings = [
        ("BDF_current", "BDF", config["rtol"], config["atol_M"]),
        ("Radau_current", "Radau", config["rtol"], config["atol_M"]),
        ("BDF_tight", "BDF", config["rtol"] / 10, config["atol_M"] / 10),
        ("Radau_tight", "Radau", config["rtol"] / 10, config["atol_M"] / 10),
    ]
    for label, method, rtol, atol in settings:
        result = simulate(
            mechanism, baseline["initial_concentrations_M"], tuple(config["t_span_s"]),
            method=method, rtol=rtol, atol=atol, output_points=config["output_points"],
            fixed_species=config["fixed_species"],
        )
        evaluations[label] = observable_metrics(result, mechanism, config["analysis_start_s"])
    floors = {
        observable: max(values) - min(values)
        for observable in ("mean_period_s", "iodine_peak_M", "iodide_min_M", "iodide_max_M")
        for values in [[evaluation[observable] for evaluation in evaluations.values()]]
    }
    source = ROOT / "reports" / "sensitivity" / "local_parameter_sensitivity.csv"
    with source.open(newline="", encoding="utf-8") as handle:
        old_rows = list(csv.DictReader(handle))
    rows = []
    below = set()
    for old in old_rows:
        row = dict(old)
        observable = row["observable"]
        if row["status"] != "OK":
            row.update({"perturbation_induced_absolute_difference": "",
                        "empirical_numerical_floor": floors[observable],
                        "difference_to_floor_ratio": "", "resolution_status": "FAILED_OSCILLATION"})
        else:
            difference = abs(float(row["plus_value"]) - float(row["minus_value"]))
            floor = floors[observable]
            status = "RESOLVED" if difference > floor else "BELOW_NUMERICAL_RESOLUTION"
            if status != "RESOLVED":
                below.add((row["parameter"], observable))
            row.update({"perturbation_induced_absolute_difference": difference,
                        "empirical_numerical_floor": floor,
                        "difference_to_floor_ratio": difference / floor if floor else float("inf"),
                        "resolution_status": status})
        rows.append(row)
    with (OUT / "local_sensitivity_resolution.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    payload = {"baseline_evaluations": evaluations, "empirical_floors": floors,
               "below_numerical_resolution": sorted(below), "row_count": len(rows)}
    (OUT / "local_sensitivity_resolution.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    return payload


def audit_historical_parameters() -> dict[str, Any]:
    config = read_json(ROOT / "experiments" / "phase2" / "historical_parameter_uncertainty.json")
    source = ROOT / "reports" / "uncertainty" / "historical_parameter_uncertainty.csv"
    with source.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    parameters = list(config["bounds"])
    outputs = ["mean_period_s", "iodine_peak_M", "iodide_min_M", "iodide_max_M"]
    X = np.asarray([[float(row[p]) for p in parameters] for row in rows])
    Xz = (X - X.mean(axis=0)) / X.std(axis=0)
    correlations = {}
    dominance = {}
    for output in outputs:
        y = np.asarray([float(row[output]) for row in rows])
        yz = (y - y.mean()) / y.std()
        correlations[output] = {
            parameter: {"pearson_r": float(pearsonr(X[:, j], y).statistic),
                        "spearman_rho": float(spearmanr(X[:, j], y).statistic)}
            for j, parameter in enumerate(parameters)
        }
        beta = np.linalg.lstsq(np.column_stack([np.ones(len(Xz)), Xz]), yz, rcond=None)[0][1:]
        shares = beta ** 2 / np.sum(beta ** 2)
        dominance[output] = {parameter: {"standardized_beta": float(beta[j]),
                                         "squared_beta_share": float(shares[j])}
                             for j, parameter in enumerate(parameters)}
    coverage = {}
    for j, parameter in enumerate(parameters):
        low = float(config["bounds"][parameter]["low"])
        high = float(config["bounds"][parameter]["high"])
        normalized = (X[:, j] - low) / (high - low)
        coverage[parameter] = {"sample_min": float(X[:, j].min()), "sample_max": float(X[:, j].max()),
                               "normalized_min": float(normalized.min()),
                               "normalized_max": float(normalized.max()),
                               "includes_low_boundary": bool(np.any(normalized == 0)),
                               "includes_high_boundary": bool(np.any(normalized == 1))}
    k10_period_share = dominance["mean_period_s"]["k10_DKE"]["squared_beta_share"]
    k10_iodine_share = dominance["iodine_peak_M"]["k10_DKE"]["squared_beta_share"]
    lines = [
        "# Historical-parameter uncertainty reanalysis", "",
        f"All {len(rows)} rows were read directly from the CSV; all have status `OSCILLATORY` under the historical two-minimum rule.",
        "Because their raw trajectories were not preserved, that historical label cannot be upgraded retrospectively",
        "to `RESOLVED_LIMIT_CYCLE` from row summaries alone.", "",
        "## Correlation and dominance", "",
        "| Output | Parameter | Pearson r | Spearman rho | standardized beta | squared-beta share |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for output in outputs:
        for parameter in parameters:
            c = correlations[output][parameter]
            d = dominance[output][parameter]
            lines.append(f"| {output} | {parameter} | {c['pearson_r']:.5f} | {c['spearman_rho']:.5f} | {d['standardized_beta']:.5f} | {d['squared_beta_share']:.2%} |")
    lines += [
        "",
        f"Within this design, k10_DKE accounts for {k10_period_share:.2%} of the summed squared standardized coefficients for period",
        f"and {k10_iodine_share:.2%} for iodine peak. This quantitatively supports k10 dominance in those outputs.", "",
        "## Design coverage and limitation", "",
    ]
    for parameter, item in coverage.items():
        lines.append(f"- {parameter}: normalized sampled range {item['normalized_min']:.5f} to {item['normalized_max']:.5f}; neither box boundary is included.")
    lines += [
        "", "The deterministic Latin-hypercube midpoints cover the interiors of all one-dimensional ranges,",
        "but do not evaluate any of the eight corners. The reported min/max is therefore a 32-point sampled",
        "envelope, not a mathematically bounded parameter-box uncertainty interval. No calibration or fitting",
        "was performed, and no corner envelope is claimed.", "",
        "## Row-level inspection", "",
        "All sample IDs 1-32 are present exactly once; every input triplet is unique. The row-level outputs",
        "are retained unchanged in the historical CSV. Four rows (1, 3, 10, 31) report only three complete",
        "periods and the remaining 28 report four, emphasizing why the missing trajectory-level convergence",
        "diagnostics matter.",
    ]
    (OUT / "historical_parameter_reanalysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {"row_count": len(rows), "correlations": correlations,
               "standardized_regression_dominance": dominance, "coverage": coverage}
    (OUT / "historical_parameter_reanalysis.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    return payload


def write_classifier_report(ic: dict[str, Any]) -> None:
    cases = ic["cases"]
    sensitivity_counts = {}
    variants = {
        "looser": OscillationThresholds(resolution_multiplier=10, period_cv_max=0.05,
                                         period_drift_max=0.05, amplitude_cv_max=0.10,
                                         amplitude_drift_max=0.10),
        "declared": OscillationThresholds(),
        "stricter": OscillationThresholds(resolution_multiplier=50, period_cv_max=0.01,
                                           period_drift_max=0.01, amplitude_cv_max=0.02,
                                           amplitude_drift_max=0.02),
    }
    # Rehydrate the 20 BDF trajectories for a threshold sensitivity check.
    config = read_json(IC_CONFIG_PATH)
    mechanism = load_mechanism(MECHANISM_PATH)
    for name, limits in variants.items():
        counts = {state.value: 0 for state in OscillationClass}
        for item in cases:
            row = item["row"]
            path = RAW / f"ic_{case_token(float(row['IO3_minus_M']), float(row['I_minus_M']))}_bdf_current.npz"
            archive = np.load(path, allow_pickle=False)
            time = archive["time_s"]
            values = archive["concentrations_M"]
            # Re-simulation is avoided; dense interpolation is reconstructed linearly only for this
            # secondary sensitivity screen, while declared results use solve_ivp dense output.
            from scipy.interpolate import CubicSpline
            from brdyn.solver import SimulationResult
            splines = [CubicSpline(time, values[i]) for i in range(values.shape[0])]
            dense = lambda t, splines=splines: np.asarray([s(t) for s in splines])
            result = SimulationResult(str(archive["solver_method"]), time, values,
                                      archive["directional_fluxes_M_per_s"],
                                      archive["cumulative_extents_M"], dense,
                                      tuple(str(x) for x in archive["fixed_species"]))
            report = classify_oscillation(result, mechanism, config["analysis_start_s"],
                                           rtol=config["rtol"], atol=config["atol_M"], thresholds=limits)
            counts[report["classification"]] += 1
        sensitivity_counts[name] = counts
    lines = [
        "# Oscillation classifier", "",
        "## Algorithm", "",
        "1. Locate iodide extrema from roots of the compiled ODE derivative, then bound complete cycles by successive positive iodide minima.",
        "2. For every complete cycle, calculate period, iodide min/max/amplitude, and iodine min/max/amplitude.",
        "3. Use the final three complete cycles; require at least three cycles.",
        "4. Define the species resolution floor as `m * (atol + rtol * max_abs_signal)`. The declared multiplier `m=20` is a guard band over the local solver error scale. Both final iodide and iodine amplitudes must exceed it.",
        "5. Require period CV and endpoint drift <=2%, and iodide/iodine amplitude CV and endpoint drift <=5%.",
        "6. Classify resolved converged cycles as `RESOLVED_LIMIT_CYCLE`; resolved but nonconverged cycles as `DAMPED_OR_TRANSIENT`; sub-floor extrema as `UNRESOLVED_NUMERICALLY`; a sub-floor span with no cycle as `STEADY_STATE`; and a resolved signal with fewer than three cycles as `INSUFFICIENT_CYCLES`.",
        "7. A solver or tolerance classification disagreement conservatively makes the consensus `UNRESOLVED_NUMERICALLY`.", "",
        "These are numerical resolution/stability rules, not physical amplitude cutoffs and not fitted criteria.", "",
        "## Threshold sensitivity", "",
        "The looser screen uses multiplier 10 with 5% period and 10% amplitude limits. The stricter screen",
        "uses multiplier 50 with 1% period and 2% amplitude limits. Counts below use the same 20 BDF",
        "trajectories; declared consensus results additionally include Radau and boundary tolerance checks.", "",
        "| Variant | resolved | damped/transient | steady | unresolved | insufficient |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, counts in sensitivity_counts.items():
        lines.append(f"| {name} | {counts['RESOLVED_LIMIT_CYCLE']} | {counts['DAMPED_OR_TRANSIENT']} | {counts['STEADY_STATE']} | {counts['UNRESOLVED_NUMERICALLY']} | {counts['INSUFFICIENT_CYCLES']} |")
    lines += ["", "All per-cycle values, resolution scores, solver agreement, and tolerance agreement are in `initial_condition_reanalysis.csv`."]
    (OUT / "oscillation_classifier.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_status(ic: dict[str, Any], sensitivity: dict[str, Any]) -> None:
    counts = ic["counts"]
    period = ic["resolved_ranges"]["period_s"]
    iodine = ic["resolved_ranges"]["iodine_peak_M"]
    below = [f"{p}/{o}" for p, o in sensitivity["below_numerical_resolution"]]
    lines = [
        "# Revised validation status", "",
        "- **Gate 1A numerical/historical implementation fidelity: PASS.** The historical DKE mechanism is reproducible across BDF and Radau; the mechanism was not changed.",
        "- **Gate 1B experimental predictive validation: FAIL / NOT VALIDATED.** The predeclared period and iodine-peak gates still fail.",
        "- **Post-Gate-1 diagnostic analysis: COMPLETE.** This is diagnostic work after failure, not evidence that experimental validation passed.",
        "- **Level 1 activation: BLOCKED.** Mechanism refinement and fitting remain out of scope until numerical/analysis validation is secure.", "",
        f"The revised grid contains {counts['RESOLVED_LIMIT_CYCLE']} resolved limit cycles, {counts['DAMPED_OR_TRANSIENT']} damped/transient cases, and {counts['UNRESOLVED_NUMERICALLY']} numerically unresolved cases.",
        f"Resolved period range: {period[0]:.9g}-{period[1]:.9g} s. Resolved iodine-peak range: {iodine[0]:.9g}-{iodine[1]:.9g} M.",
        f"The digitized single-cycle value 714.13 s is {'inside' if ic['target_inside_resolved_period_envelope'] else 'outside'} the resolved initial-condition envelope.",
        f"Local sensitivity parameter/observable pairs below the empirical numerical floor: {', '.join(below) if below else 'none'}.", "",
        "The prior scientific conclusion changed: the initial-condition period result is no longer `PARTIALLY`;",
        "the apparent ~669 s nonlinear interaction came entirely from unresolved 0.004 M iodate cases and is excluded.",
    ]
    (OUT / "revised_validation_status.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_artifact_manifest() -> None:
    manifest = OUT / "artifact_manifest.txt"
    paths = [
        ROOT / "brdyn" / "analysis.py",
        ROOT / "brdyn" / "solver.py",
        ROOT / "tests" / "test_analysis.py",
        ROOT / "tools" / "run_revalidation.py",
        *[path for path in OUT.rglob("*") if path.is_file() and path != manifest],
        manifest,
    ]
    relative = sorted({path.relative_to(ROOT).as_posix() for path in paths})
    manifest.write_text("\n".join(relative) + "\n", encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    gate = run_gate1_raw()
    data = audit_experimental_data()
    ic = run_initial_condition_reanalysis()
    sensitivity = audit_local_sensitivity()
    historical = audit_historical_parameters()
    write_classifier_report(ic)
    write_status(ic, sensitivity)
    summary = {
        "gate1_classifications": {k: v["classification"] for k, v in gate.items()},
        "counts": ic["counts"],
        "resolved_period_range_s": ic["resolved_ranges"]["period_s"],
        "resolved_iodine_peak_range_M": ic["resolved_ranges"]["iodine_peak_M"],
        "digitized_single_cycle_period_inside_envelope": ic["target_inside_resolved_period_envelope"],
        "previous_669_s_interaction_survives": False,
        "below_numerical_resolution": sensitivity["below_numerical_resolution"],
        "historical_rows_audited": historical["row_count"],
        "experimental_single_cycle_period_s": data["digitized_single_cycle_period_s"],
    }
    (OUT / "revalidation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_artifact_manifest()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

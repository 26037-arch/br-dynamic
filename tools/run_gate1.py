from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from brdyn.analysis import cycle_metrics
from brdyn.network import load_mechanism
from brdyn.solver import simulate


ROOT = Path(__file__).parents[1]
EXPERIMENT_PATH = ROOT / "experiments" / "baseline" / "dke_pooled_gate1.json"
METRICS_PATH = ROOT / "reports" / "gate1_metrics.json"
COMPARISON_PATH = ROOT / "reports" / "gate1_comparison.csv"
FIGURE_PATH = ROOT / "reports" / "gate1_reproduction.png"


def relative_error(value: float, target: float) -> float:
    return abs(value - target) / abs(target)


def relative_difference(left: float, right: float) -> float:
    return abs(left - right) / max(abs(left), abs(right), np.finfo(float).tiny)


def read_reference_data() -> tuple[np.ndarray, np.ndarray]:
    time_rows = []
    with (ROOT / "data" / "experimental" / "dke_digitized" / "iodide_time_trace.csv").open(
        newline="", encoding="utf-8-sig"
    ) as handle:
        for row in csv.DictReader(handle):
            time_rows.append((float(row["Time (s)"]), float(row["Negative log iodide concentration (M)"])))
    cycle_rows = []
    with (ROOT / "data" / "experimental" / "dke_digitized" / "iodide_iodine_limit_cycle.csv").open(
        newline="", encoding="utf-8-sig"
    ) as handle:
        for row in csv.DictReader(handle):
            cycle_rows.append((
                float(row["negative log iodide concentration (M)"]),
                float(row["iodine concentration times 10^4 (M)"]) * 1e-4,
            ))
    return np.asarray(time_rows), np.asarray(cycle_rows)


def invariant_drift_M(mechanism, result) -> float:
    effective_s = mechanism.S.copy()
    for name in result.fixed_species:
        effective_s[mechanism.dynamic_index[name], :] = 0.0
    left_singular_vectors, singular_values, _ = np.linalg.svd(effective_s, full_matrices=True)
    rank = int(np.sum(singular_values > max(effective_s.shape) * np.finfo(float).eps * singular_values[0]))
    null_basis = left_singular_vectors[:, rank:]
    if null_basis.shape[1] == 0:
        return 0.0
    invariants = null_basis.T @ result.y
    return float(np.max(np.abs(invariants - invariants[:, [0]])))


def metric_rows(metrics: dict, targets: dict, thresholds: dict) -> list[dict[str, object]]:
    definitions = [
        ("mean_period_s", "relative", thresholds["period_relative_error_max"]),
        ("iodine_peak_M", "relative", thresholds["iodine_peak_relative_error_max"]),
        ("iodide_pI_min", "absolute", thresholds["iodide_pI_min_absolute_error_max"]),
        ("iodide_pI_max", "absolute", thresholds["iodide_pI_max_absolute_error_max"]),
    ]
    rows = []
    for name, error_type, threshold in definitions:
        observed = float(metrics[name])
        target = float(targets[name])
        error = relative_error(observed, target) if error_type == "relative" else abs(observed - target)
        rows.append({
            "metric": name,
            "experimental_target": target,
            "model_value": observed,
            "error_type": error_type,
            "error": error,
            "threshold": threshold,
            "pass": error <= threshold,
        })
    return rows


def make_figure(mechanism, bdf, reference_time: np.ndarray, reference_cycle: np.ndarray) -> None:
    metrics = cycle_metrics(bdf, mechanism, 900.0)
    start, end = metrics["last_cycle_start_s"], metrics["last_cycle_end_s"]
    time = np.linspace(start, end, 1200)
    state = bdf.dense_solution(time)
    iodide = state[mechanism.dynamic_index["I_minus"]]
    iodine = state[mechanism.dynamic_index["I2"]]
    phase = (time - start) / (end - start)

    experimental_peak_indices = np.where(reference_time[:, 1] > 9.9)[0]
    split = []
    for index in experimental_peak_indices:
        if not split or index - split[-1] > 2:
            split.append(int(index))
    first, second = split[0], split[1]
    experimental = reference_time[first:second + 1]
    experimental_phase = (experimental[:, 0] - experimental[0, 0]) / (
        experimental[-1, 0] - experimental[0, 0]
    )

    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), constrained_layout=True)
    axes[0].plot(phase, -np.log10(iodide), label="DKE model (last cycle)", linewidth=2)
    axes[0].scatter(experimental_phase, experimental[:, 1], label="digitized experiment",
                    s=13, alpha=0.75)
    axes[0].set(xlabel="cycle phase", ylabel="pI = -log10([I-]/M)")
    axes[0].legend(frameon=False)

    axes[1].plot(-np.log10(iodide), iodine * 1e4, label="DKE model", linewidth=2)
    axes[1].scatter(reference_cycle[:, 0], reference_cycle[:, 1] * 1e4,
                    label="digitized experiment", s=13, alpha=0.75)
    axes[1].set(xlabel="pI = -log10([I-]/M)", ylabel="[I2] x 10^4 / M")
    axes[1].legend(frameon=False)
    figure.suptitle("Gate 1 historical DKE reproduction")
    figure.savefig(FIGURE_PATH, dpi=180)
    plt.close(figure)


def main() -> int:
    experiment = json.loads(EXPERIMENT_PATH.read_text(encoding="utf-8"))
    mechanism = load_mechanism(ROOT / "mechanisms" / "dke10.yaml")
    common = dict(
        mechanism=mechanism,
        initial=experiment["initial_concentrations_M"],
        t_span=tuple(experiment["t_span_s"]),
        rtol=experiment["rtol"],
        atol=experiment["atol_M"],
        output_points=experiment["output_points"],
        fixed_species=experiment["fixed_species"],
    )
    bdf = simulate(method="BDF", **common)
    radau = simulate(method="Radau", **common)
    bdf_metrics = cycle_metrics(bdf, mechanism, experiment["analysis_start_s"])
    radau_metrics = cycle_metrics(radau, mechanism, experiment["analysis_start_s"])
    thresholds = experiment["acceptance_thresholds"]
    comparison = metric_rows(bdf_metrics, experiment["experimental_targets"], thresholds)

    solver_differences = {
        name: relative_difference(float(bdf_metrics[name]), float(radau_metrics[name]))
        for name in ("mean_period_s", "iodine_peak_M", "iodide_pI_min", "iodide_pI_max")
    }
    solver_checks = {
        "period": solver_differences["mean_period_s"] <= thresholds["bdf_radau_period_relative_difference_max"],
        "scalar_metrics": max(value for name, value in solver_differences.items()
                              if name != "mean_period_s") <= thresholds["bdf_radau_scalar_metric_relative_difference_max"],
    }
    minimum_concentration = min(float(bdf.y.min()), float(radau.y.min()))
    numerical_checks = {
        "minimum_concentration": minimum_concentration >= thresholds["minimum_concentration_M"],
        "minimum_complete_periods": min(
            int(bdf_metrics["complete_period_count"]), int(radau_metrics["complete_period_count"])
        ) >= thresholds["minimum_complete_periods"],
        **solver_checks,
    }
    experimental_checks = {row["metric"]: row["pass"] for row in comparison}
    passed = all(numerical_checks.values()) and all(experimental_checks.values())

    payload = {
        "gate": 1,
        "status": "PASS" if passed else "FAIL",
        "model_scope": "historical DKE pooled-reactor reproduction",
        "bdf": bdf_metrics,
        "radau": radau_metrics,
        "solver_relative_differences": solver_differences,
        "minimum_concentration_M": minimum_concentration,
        "effective_stoichiometric_invariant_max_drift_M": {
            "BDF": invariant_drift_M(mechanism, bdf),
            "Radau": invariant_drift_M(mechanism, radau),
        },
        "numerical_checks": numerical_checks,
        "experimental_checks": experimental_checks,
        "comparison": comparison,
        "advance_to_gate_2": passed,
    }
    METRICS_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with COMPARISON_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(comparison[0]))
        writer.writeheader()
        writer.writerows(comparison)
    reference_time, reference_cycle = read_reference_data()
    make_figure(mechanism, bdf, reference_time, reference_cycle)
    print(json.dumps(payload, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

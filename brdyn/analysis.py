from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy.optimize import brentq, minimize_scalar

from .network import Mechanism
from .solver import SimulationResult


@dataclass(frozen=True)
class Extremum:
    time_s: float
    concentration_M: float
    kind: str


class OscillationClass(str, Enum):
    RESOLVED_LIMIT_CYCLE = "RESOLVED_LIMIT_CYCLE"
    DAMPED_OR_TRANSIENT = "DAMPED_OR_TRANSIENT"
    STEADY_STATE = "STEADY_STATE"
    UNRESOLVED_NUMERICALLY = "UNRESOLVED_NUMERICALLY"
    INSUFFICIENT_CYCLES = "INSUFFICIENT_CYCLES"


@dataclass(frozen=True)
class OscillationThresholds:
    """Numerical, not physical, criteria for resolving a limit cycle.

    The amplitude floor is ``resolution_multiplier * (atol + rtol * scale)``.
    Stability is evaluated over the final ``final_cycles`` complete cycles.
    """

    min_complete_cycles: int = 3
    final_cycles: int = 3
    resolution_multiplier: float = 20.0
    period_cv_max: float = 0.02
    period_drift_max: float = 0.02
    amplitude_cv_max: float = 0.05
    amplitude_drift_max: float = 0.05


def consensus_classification(classifications: list[str]) -> tuple[str, str]:
    """Return a conservative classification and an explicit agreement flag."""
    if not classifications:
        raise ValueError("At least one classification is required")
    if len(set(classifications)) == 1:
        return classifications[0], "AGREE"
    return OscillationClass.UNRESOLVED_NUMERICALLY.value, "DISAGREE"


def _effective_derivative(result: SimulationResult, mechanism: Mechanism,
                          species_index: int, time_s: float) -> float:
    derivative = mechanism.rhs(time_s, result.dense_solution(time_s))
    if mechanism.dynamic_ids[species_index] in result.fixed_species:
        return 0.0
    return float(derivative[species_index])


def extrema(result: SimulationResult, mechanism: Mechanism, species: str,
            start_s: float | None = None, end_s: float | None = None) -> list[Extremum]:
    """Locate concentration extrema by bracketing roots of the compiled RHS."""
    index = mechanism.dynamic_index[species]
    start = result.t[0] if start_s is None else start_s
    end = result.t[-1] if end_s is None else end_s
    grid = result.t[(result.t >= start) & (result.t <= end)]
    if len(grid) < 2:
        raise ValueError("Extremum interval must contain at least two output points")
    derivative = np.array([
        _effective_derivative(result, mechanism, index, float(time)) for time in grid
    ])
    roots: list[Extremum] = []
    for left, right, d_left, d_right in zip(grid[:-1], grid[1:], derivative[:-1], derivative[1:]):
        if d_left == 0.0 or d_left * d_right >= 0.0:
            continue
        root = brentq(
            lambda time: _effective_derivative(result, mechanism, index, time),
            float(left), float(right), xtol=1e-10, rtol=1e-12,
        )
        value = float(result.dense_solution(root)[index])
        kind = "maximum" if d_left > 0.0 and d_right < 0.0 else "minimum"
        if not roots or abs(root - roots[-1].time_s) > 1e-7:
            roots.append(Extremum(root, value, kind))
    return roots


def _species_atol(atol: float | dict[str, float], species: str) -> float:
    return float(atol.get(species, 1e-12) if isinstance(atol, dict) else atol)


def _coefficient_of_variation(values: np.ndarray) -> float:
    mean = float(np.mean(values))
    return float(np.std(values, ddof=0) / abs(mean)) if mean else float("inf")


def _relative_drift(values: np.ndarray) -> float:
    mean = float(np.mean(np.abs(values)))
    return float((values[-1] - values[0]) / mean) if mean else float("inf")


def cycle_metrics(result: SimulationResult, mechanism: Mechanism,
                  start_s: float = 0.0) -> dict[str, object]:
    iodide_extrema = extrema(result, mechanism, "I_minus", start_s)
    minima = [point for point in iodide_extrema if point.kind == "minimum" and point.concentration_M > 0]
    if len(minima) < 2:
        raise ValueError("Fewer than two iodide minima; no complete period is measurable")
    periods = np.diff([point.time_s for point in minima])
    period = float(np.mean(periods[-min(4, len(periods)):]))
    cycles = []
    iodide_index = mechanism.dynamic_index["I_minus"]
    iodine_index = mechanism.dynamic_index["I2"]
    for cycle_number, (cycle_start, cycle_end) in enumerate(zip(minima[:-1], minima[1:]), start=1):
        bounds = (cycle_start.time_s, cycle_end.time_s)
        iodide_maximum = -float(minimize_scalar(
            lambda time: -float(result.dense_solution(time)[iodide_index]),
            bounds=bounds, method="bounded", options={"xatol": 1e-8},
        ).fun)
        iodine_peak = -float(minimize_scalar(
            lambda time: -float(result.dense_solution(time)[iodine_index]),
            bounds=bounds, method="bounded", options={"xatol": 1e-8},
        ).fun)
        iodine_minimum = float(minimize_scalar(
            lambda time: float(result.dense_solution(time)[iodine_index]),
            bounds=bounds, method="bounded", options={"xatol": 1e-8},
        ).fun)
        iodide_minimum = min(cycle_start.concentration_M, cycle_end.concentration_M)
        cycles.append({
            "cycle": cycle_number,
            "start_s": cycle_start.time_s,
            "end_s": cycle_end.time_s,
            "period_s": cycle_end.time_s - cycle_start.time_s,
            "iodide_pI_min": -np.log10(iodide_maximum),
            "iodide_pI_max": -np.log10(min(cycle_start.concentration_M, cycle_end.concentration_M)),
            "iodide_min_M": iodide_minimum,
            "iodide_max_M": iodide_maximum,
            "iodide_amplitude_M": iodide_maximum - iodide_minimum,
            "iodine_min_M": iodine_minimum,
            "iodine_peak_M": iodine_peak,
            "iodine_amplitude_M": iodine_peak - iodine_minimum,
        })
    last_cycle_start, last_cycle_end = minima[-2].time_s, minima[-1].time_s
    iodide_minimum = min(minima[-2].concentration_M, minima[-1].concentration_M)
    iodide_maximum = 10 ** (-cycles[-1]["iodide_pI_min"])
    iodine_peak = cycles[-1]["iodine_peak_M"]
    return {
        "complete_period_count": len(minima) - 1,
        "cycles": cycles,
        "mean_period_s": period,
        "last_cycle_start_s": last_cycle_start,
        "last_cycle_end_s": last_cycle_end,
        "iodide_pI_min": -np.log10(iodide_maximum),
        "iodide_pI_max": -np.log10(iodide_minimum),
        "iodide_min_M": iodide_minimum,
        "iodide_max_M": iodide_maximum,
        "iodine_peak_M": iodine_peak,
    }


def classify_oscillation(
    result: SimulationResult,
    mechanism: Mechanism,
    start_s: float = 0.0,
    *,
    rtol: float = 1e-9,
    atol: float | dict[str, float] = 1e-13,
    thresholds: OscillationThresholds | None = None,
) -> dict[str, object]:
    """Classify a trajectory without treating the mere presence of extrema as a limit cycle."""
    limits = thresholds or OscillationThresholds()
    start_mask = result.t >= start_s
    if not np.any(start_mask):
        raise ValueError("Oscillation analysis interval contains no output points")
    iodide_index = mechanism.dynamic_index["I_minus"]
    iodine_index = mechanism.dynamic_index.get("I2")
    iodide_signal = result.y[iodide_index, start_mask]
    iodide_scale = float(np.max(np.abs(iodide_signal)))
    iodide_floor = limits.resolution_multiplier * (
        _species_atol(atol, "I_minus") + rtol * iodide_scale
    )
    observed_span = float(np.ptp(iodide_signal))

    try:
        metrics = cycle_metrics(result, mechanism, start_s)
    except ValueError:
        state = (OscillationClass.STEADY_STATE if observed_span <= iodide_floor
                 else OscillationClass.INSUFFICIENT_CYCLES)
        return {
            "classification": state.value,
            "complete_cycle_count": 0,
            "cycle_periods_s": [],
            "cycle_iodide_amplitudes_M": [],
            "cycle_iodine_amplitudes_M": [],
            "final_cycle_period_mean_s": None,
            "period_cv": None,
            "period_drift": None,
            "iodide_amplitude_drift": None,
            "iodine_amplitude_drift": None,
            "iodide_resolution_floor_M": iodide_floor,
            "iodide_resolution_score": observed_span / iodide_floor if iodide_floor else float("inf"),
            "iodide_relative_amplitude": observed_span / max(iodide_scale, np.finfo(float).tiny),
            "iodine_resolution_score": None,
            "reason": "post-transient signal is within the numerical floor" if state == OscillationClass.STEADY_STATE
                      else "fewer than two minima bound a complete cycle",
        }

    cycles = metrics["cycles"]
    periods = np.asarray([cycle["period_s"] for cycle in cycles], dtype=float)
    iodide_amplitudes = np.asarray([cycle["iodide_amplitude_M"] for cycle in cycles], dtype=float)
    iodine_amplitudes = np.asarray([cycle["iodine_amplitude_M"] for cycle in cycles], dtype=float)
    count = len(cycles)
    window_size = min(limits.final_cycles, count)
    final_periods = periods[-window_size:]
    final_iodide = iodide_amplitudes[-window_size:]
    final_iodine = iodine_amplitudes[-window_size:]

    iodine_floor = None
    iodine_score = None
    if iodine_index is not None:
        iodine_scale = float(np.max(np.abs(result.y[iodine_index, start_mask])))
        iodine_floor = limits.resolution_multiplier * (
            _species_atol(atol, "I2") + rtol * iodine_scale
        )
        iodine_score = float(np.min(final_iodine) / iodine_floor) if iodine_floor else float("inf")
    iodide_score = float(np.min(final_iodide) / iodide_floor) if iodide_floor else float("inf")
    period_cv = _coefficient_of_variation(final_periods)
    period_drift = _relative_drift(final_periods)
    iodide_cv = _coefficient_of_variation(final_iodide)
    iodine_cv = _coefficient_of_variation(final_iodine)
    iodide_drift = _relative_drift(final_iodide)
    iodine_drift = _relative_drift(final_iodine)
    iodide_relative = float(np.min([
        cycle["iodide_amplitude_M"] /
        max(abs(cycle["iodide_max_M"]), abs(cycle["iodide_min_M"]), np.finfo(float).tiny)
        for cycle in cycles[-window_size:]
    ]))

    if iodide_score < 1.0 or (iodine_score is not None and iodine_score < 1.0):
        state = OscillationClass.UNRESOLVED_NUMERICALLY
        reason = "final-cycle amplitude does not exceed the combined absolute/relative solver error floor"
    elif count < limits.min_complete_cycles:
        state = OscillationClass.INSUFFICIENT_CYCLES
        reason = f"{count} complete cycles; at least {limits.min_complete_cycles} are required"
    elif (abs(iodide_drift) > limits.amplitude_drift_max
          or abs(iodine_drift) > limits.amplitude_drift_max
          or iodide_cv > limits.amplitude_cv_max
          or iodine_cv > limits.amplitude_cv_max
          or abs(period_drift) > limits.period_drift_max
          or period_cv > limits.period_cv_max):
        state = OscillationClass.DAMPED_OR_TRANSIENT
        reason = "final cycles do not meet period/amplitude convergence criteria"
    else:
        state = OscillationClass.RESOLVED_LIMIT_CYCLE
        reason = "resolved amplitudes and converged final-cycle period/amplitudes"

    return {
        "classification": state.value,
        "complete_cycle_count": count,
        "cycle_periods_s": periods.tolist(),
        "cycle_iodide_amplitudes_M": iodide_amplitudes.tolist(),
        "cycle_iodine_amplitudes_M": iodine_amplitudes.tolist(),
        "final_cycle_period_mean_s": float(np.mean(final_periods)),
        "period_cv": period_cv,
        "period_drift": period_drift,
        "iodide_amplitude_cv": iodide_cv,
        "iodine_amplitude_cv": iodine_cv,
        "iodide_amplitude_drift": iodide_drift,
        "iodine_amplitude_drift": iodine_drift,
        "iodide_resolution_floor_M": iodide_floor,
        "iodide_resolution_score": iodide_score,
        "iodide_relative_amplitude": iodide_relative,
        "iodine_resolution_floor_M": iodine_floor,
        "iodine_resolution_score": iodine_score,
        "iodide_min_M": metrics["iodide_min_M"],
        "iodide_max_M": metrics["iodide_max_M"],
        "iodide_amplitude_M": float(final_iodide[-1]),
        "iodine_peak_M": metrics["iodine_peak_M"],
        "iodine_amplitude_M": float(final_iodine[-1]),
        "reason": reason,
    }

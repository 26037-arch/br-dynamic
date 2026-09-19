from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq, minimize_scalar

from .network import Mechanism
from .solver import SimulationResult


@dataclass(frozen=True)
class Extremum:
    time_s: float
    concentration_M: float
    kind: str


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
        cycles.append({
            "cycle": cycle_number,
            "start_s": cycle_start.time_s,
            "end_s": cycle_end.time_s,
            "period_s": cycle_end.time_s - cycle_start.time_s,
            "iodide_pI_min": -np.log10(iodide_maximum),
            "iodide_pI_max": -np.log10(min(cycle_start.concentration_M, cycle_end.concentration_M)),
            "iodine_peak_M": iodine_peak,
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

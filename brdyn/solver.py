from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
import warnings

import numpy as np
from scipy.integrate import solve_ivp

from .network import Mechanism


class NumericalFailure(RuntimeError):
    pass


@dataclass
class SimulationResult:
    method: str
    t: np.ndarray
    y: np.ndarray
    directional_fluxes: np.ndarray
    cumulative_extents: np.ndarray


def simulate(mechanism: Mechanism, initial: Mapping[str, float], t_span: tuple[float, float],
             method: str = "BDF", rtol: float = 1e-8,
             atol: Mapping[str, float] | float = 1e-12,
             output_points: int = 1001) -> SimulationResult:
    y0 = np.array([initial.get(s, 0.0) for s in mechanism.dynamic_ids], dtype=float)
    if np.any(y0 < 0):
        raise ValueError("Initial concentrations must be nonnegative")
    atol_vector = (np.array([atol.get(s, 1e-12) for s in mechanism.dynamic_ids])
                   if isinstance(atol, Mapping) else float(atol))
    t_eval = np.linspace(t_span[0], t_span[1], output_points)
    solution = solve_ivp(mechanism.rhs, t_span, y0, method=method, rtol=rtol,
                         atol=atol_vector, t_eval=t_eval, dense_output=True,
                         jac=mechanism.jacobian if method in {"BDF", "Radau"} else None)
    if not solution.success:
        raise NumericalFailure(solution.message)
    threshold = -10 * np.max(np.atleast_1d(atol_vector))
    if float(solution.y.min()) < threshold:
        i, j = np.unravel_index(np.argmin(solution.y), solution.y.shape)
        raise NumericalFailure(
            f"Significant negative concentration: {mechanism.dynamic_ids[i]}="
            f"{solution.y[i, j]:.6e} at t={solution.t[j]:.6e}"
        )
    fluxes = np.column_stack([mechanism.directional_rates(solution.y[:, i])
                              for i in range(solution.y.shape[1])])
    dt = np.diff(solution.t)
    extents = np.zeros_like(fluxes)
    extents[:, 1:] = np.cumsum(0.5 * (fluxes[:, 1:] + fluxes[:, :-1]) * dt, axis=1)
    return SimulationResult(method, solution.t, solution.y, fluxes, extents)


def crosscheck(mechanism: Mechanism, initial: Mapping[str, float], t_span: tuple[float, float],
               rtol: float = 1e-8, atol: float = 1e-12) -> tuple[SimulationResult, SimulationResult, float]:
    bdf = simulate(mechanism, initial, t_span, "BDF", rtol, atol)
    radau = simulate(mechanism, initial, t_span, "Radau", rtol, atol)
    scale = np.maximum(np.maximum(np.abs(bdf.y), np.abs(radau.y)), atol)
    relative = float(np.max(np.abs(bdf.y - radau.y) / scale))
    if relative > 0.05:
        warnings.warn(f"BDF and Radau disagree materially: scaled difference={relative:.3g}",
                      RuntimeWarning)
    return bdf, radau, relative

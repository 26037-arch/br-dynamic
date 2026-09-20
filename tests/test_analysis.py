import numpy as np
import json
from pathlib import Path

from brdyn.analysis import (
    OscillationClass,
    classify_oscillation,
    consensus_classification,
)
from brdyn.solver import SimulationResult
from brdyn.network import load_mechanism
from brdyn.solver import simulate


ROOT = Path(__file__).parents[1]


class SyntheticMechanism:
    dynamic_ids = ["I_minus", "I2"]
    dynamic_index = {"I_minus": 0, "I2": 1}

    def __init__(self, kind: str, amplitude: float = 1e-5, decay: float = 0.0,
                 period: float = 10.0, offset: float = 2e-5):
        self.kind = kind
        self.amplitude = amplitude
        self.decay = decay
        self.period = period
        self.offset = offset

    def values(self, time):
        time = np.asarray(time)
        omega = 2 * np.pi / self.period
        envelope = self.amplitude * np.exp(-self.decay * time)
        iodide = self.offset + envelope * np.sin(omega * time)
        iodine = 2 * self.offset + 0.5 * envelope * np.cos(omega * time)
        if self.kind == "steady":
            iodide = self.offset + np.zeros_like(time)
            iodine = 2 * self.offset + np.zeros_like(time)
        return np.asarray([iodide, iodine])

    def rhs(self, time, _state):
        if self.kind == "steady":
            return np.zeros(2)
        omega = 2 * np.pi / self.period
        envelope = self.amplitude * np.exp(-self.decay * time)
        return np.asarray([
            envelope * (omega * np.cos(omega * time) - self.decay * np.sin(omega * time)),
            0.5 * envelope * (-omega * np.sin(omega * time) - self.decay * np.cos(omega * time)),
        ])


def synthetic_result(mechanism, end=60.0, noise=0.0):
    time = np.linspace(0, end, int(end * 20) + 1)
    values = mechanism.values(time)
    if noise:
        values[0] += noise * np.sin(17.3 * time)
    return SimulationResult(
        method="synthetic", t=time, y=values,
        directional_fluxes=np.zeros((1, len(time))),
        cumulative_extents=np.zeros((1, len(time))),
        dense_solution=mechanism.values, fixed_species=(),
    )


def test_stable_limit_cycle_is_resolved():
    mechanism = SyntheticMechanism("oscillatory")
    report = classify_oscillation(synthetic_result(mechanism), mechanism, atol=1e-13)
    assert report["classification"] == OscillationClass.RESOLVED_LIMIT_CYCLE.value
    assert report["complete_cycle_count"] >= 3


def test_exponentially_damped_oscillation_is_transient():
    mechanism = SyntheticMechanism("oscillatory", decay=0.04)
    report = classify_oscillation(synthetic_result(mechanism), mechanism, atol=1e-13)
    assert report["classification"] == OscillationClass.DAMPED_OR_TRANSIENT.value


def test_steady_state_with_sub_tolerance_noise_is_steady():
    mechanism = SyntheticMechanism("steady")
    result = synthetic_result(mechanism, noise=1e-14)
    report = classify_oscillation(result, mechanism, atol=1e-13)
    assert report["classification"] == OscillationClass.STEADY_STATE.value


def test_tiny_oscillation_is_unresolved_numerically():
    mechanism = SyntheticMechanism("oscillatory", amplitude=1e-14)
    report = classify_oscillation(synthetic_result(mechanism), mechanism, atol=1e-13)
    assert report["classification"] == OscillationClass.UNRESOLVED_NUMERICALLY.value


def test_trajectory_with_too_few_cycles_is_explicit():
    mechanism = SyntheticMechanism("oscillatory")
    report = classify_oscillation(synthetic_result(mechanism, end=18), mechanism, atol=1e-13)
    assert report["classification"] == OscillationClass.INSUFFICIENT_CYCLES.value


def test_solver_disagreement_is_unresolved():
    classification, agreement = consensus_classification([
        OscillationClass.RESOLVED_LIMIT_CYCLE.value,
        OscillationClass.DAMPED_OR_TRANSIENT.value,
    ])
    assert classification == OscillationClass.UNRESOLVED_NUMERICALLY.value
    assert agreement == "DISAGREE"


def test_known_004_M_iodate_case_is_below_resolution():
    config = json.loads((ROOT / "experiments" / "phase2" / "initial_condition_uncertainty.json").read_text())
    baseline = json.loads((ROOT / "experiments" / "baseline" / "dke_pooled_gate1.json").read_text())
    initial = dict(baseline["initial_concentrations_M"])
    initial.update({"IO3_minus": 0.004, "I_minus": 1e-6})
    mechanism = load_mechanism(ROOT / "mechanisms" / "dke10.yaml")
    result = simulate(
        mechanism, initial, tuple(config["t_span_s"]), method="BDF",
        rtol=config["rtol"], atol=config["atol_M"],
        output_points=config["output_points"], fixed_species=config["fixed_species"],
    )
    report = classify_oscillation(
        result, mechanism, config["analysis_start_s"],
        rtol=config["rtol"], atol=config["atol_M"],
    )
    assert report["classification"] == OscillationClass.UNRESOLVED_NUMERICALLY.value
    assert report["iodide_amplitude_M"] < report["iodide_resolution_floor_M"]

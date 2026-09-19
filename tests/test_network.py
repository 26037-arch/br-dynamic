from pathlib import Path

import numpy as np

from brdyn.network import load_mechanism


ROOT = Path(__file__).parents[1]


def test_dke_parses_and_directional_fluxes_are_explicit():
    model = load_mechanism(ROOT / "mechanisms" / "dke10.yaml")
    assert len(model.fluxes) == 12
    assert "R3_forward" in [f.id for f in model.fluxes]
    assert "R3_reverse" in [f.id for f in model.fluxes]
    assert "R4_reverse" in [f.id for f in model.fluxes]


def test_every_historical_flux_is_element_and_charge_balanced():
    model = load_mechanism(ROOT / "mechanisms" / "dke10.yaml")
    assert model.balance_errors() == {}
    assert model.provenance_errors() == []
    assert model.unit_errors() == []


def test_stoichiometric_matrix_is_generated_from_reactions():
    model = load_mechanism(ROOT / "mechanisms" / "dke10.yaml")
    r1 = [i for i, flux in enumerate(model.fluxes) if flux.id == "R1_forward"][0]
    assert model.S[model.dynamic_index["I_minus"], r1] == -1
    assert model.S[model.dynamic_index["HOI"], r1] == 1


def test_r9_uses_documented_saturating_law():
    model = load_mechanism(ROOT / "mechanisms" / "dke10.yaml")
    y = np.zeros(len(model.dynamic_ids))
    y[model.dynamic_index["I2"]] = 1e-4
    y[model.dynamic_index["malonic_acid"]] = 0.01
    rates = dict(zip([f.id for f in model.fluxes], model.directional_rates(y)))
    assert np.isclose(rates["R9_forward"], 40 * 1e-4 * 0.01 / (1 + 1e4 * 1e-4))


def test_compiled_jacobian_matches_linear_toy_network():
    raw = {
        "species": [
            {"id": "A", "charge": 0, "composition": {"X": 1}},
            {"id": "B", "charge": 0, "composition": {"X": 1}},
        ],
        "reactions": [{
            "id": "toy", "stoichiometry": {"A": -1, "B": 1},
            "forward": {"rate_law": {"type": "mass_action", "orders": {"A": 1}},
                        "parameter": {"name":"k","value": 2.0, "units":"s^-1", "confidence":"MEASURED_DIRECT", "source":"analytic toy"}}
        }]
    }
    from brdyn.network import Mechanism
    jac = Mechanism(raw).jacobian(0.0, np.array([1.0, 0.0]))
    assert np.allclose(jac, [[-2.0, 0.0], [2.0, 0.0]], atol=1e-7)

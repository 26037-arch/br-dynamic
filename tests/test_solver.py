import numpy as np

from brdyn.network import Mechanism
from brdyn.solver import crosscheck, simulate


def test_analytic_first_order_decay():
    raw = {
        "species": [
            {"id": "A", "charge": 0, "composition": {"X": 1}},
            {"id": "B", "charge": 0, "composition": {"X": 1}},
        ],
        "reactions": [{
            "id": "toy", "stoichiometry": {"A": -1, "B": 1},
            "forward": {
                "rate_law": {"type": "mass_action", "orders": {"A": 1}},
                "parameter": {"value": 2.0, "confidence": "MEASURED_DIRECT", "source": "analytic toy"},
            },
        }],
    }
    result = simulate(Mechanism(raw), {"A": 1.0}, (0, 1), output_points=11)
    assert np.isclose(result.y[0, -1], np.exp(-2), rtol=2e-6)
    assert np.isclose(result.y[0, -1] + result.y[1, -1], 1.0, atol=1e-10)


def test_bdf_and_radau_converge_for_toy_network():
    raw = {
        "species": [{"id":"A","charge":0,"composition":{"X":1}},
                    {"id":"B","charge":0,"composition":{"X":1}}],
        "reactions": [{"id":"toy","stoichiometry":{"A":-1,"B":1},
                       "forward":{"rate_law":{"type":"mass_action","orders":{"A":1}},
                                  "parameter":{"name":"k","value":2.0,"units":"s^-1","confidence":"MEASURED_DIRECT","source":"analytic toy"}}}]
    }
    bdf, radau, discrepancy = crosscheck(Mechanism(raw), {"A":1.0}, (0, 1), 1e-9, 1e-12)
    assert discrepancy < 1e-4
    assert np.allclose(bdf.y, radau.y, atol=2e-9)

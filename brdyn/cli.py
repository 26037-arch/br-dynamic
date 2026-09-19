from __future__ import annotations

import argparse
import json
from pathlib import Path

from .network import load_mechanism
from .solver import crosscheck


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("mechanism")
    run = sub.add_parser("simulate")
    run.add_argument("mechanism")
    run.add_argument("experiment")
    args = parser.parse_args()
    mechanism = load_mechanism(args.mechanism)
    errors = mechanism.balance_errors()
    provenance_errors = mechanism.provenance_errors()
    unit_errors = mechanism.unit_errors()
    if args.command == "validate":
        print(json.dumps({"species": len(mechanism.species), "fluxes": len(mechanism.fluxes),
                          "balance_errors": errors, "provenance_errors": provenance_errors,
                          "unit_errors": unit_errors}, indent=2))
        return 1 if errors or provenance_errors or unit_errors else 0
    experiment = json.loads(Path(args.experiment).read_text(encoding="utf-8"))
    if errors or provenance_errors or unit_errors:
        raise SystemExit(f"Refusing to simulate invalid mechanism: balance={errors}; provenance={provenance_errors}; units={unit_errors}")
    bdf, radau, discrepancy = crosscheck(
        mechanism, experiment["initial_concentrations_M"], tuple(experiment["t_span_s"]),
        experiment.get("rtol", 1e-8), experiment.get("atol_M", 1e-12),
        experiment.get("output_points", 1001), experiment.get("fixed_species", ()),
    )
    print(json.dumps({"status": "HISTORICAL_BASELINE_ONLY", "points": len(bdf.t),
                      "BDF_Radau_max_scaled_difference": discrepancy,
                      "minimum_BDF_concentration_M": float(bdf.y.min())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

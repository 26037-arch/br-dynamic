# br-dynamic

This repository starts with a literature audit of the historical De Kepper-Epstein
(DKE) ten-step Briggs-Rauscher model. It does not treat the DKE equations as a
microscopic mechanism.

Current scope:

- Phase 0 audit of R1-R10, including parameter provenance and compatibility flags.
- Exact machine-readable encoding of the historical DKE model, including its
  saturating empirical R9 rate law.
- Audited-effective and refined-microkinetic manifests that keep unresolved steps
  disabled rather than inventing constants.
- Automatic directional-flux, stoichiometric-matrix, RHS, elemental-balance, and
  charge-balance construction.
- BDF/Radau integration with no concentration clipping and explicit negative-state
  failure detection.
- Historical pool/chemostat mode, dense-output extremum finding, and cycle-resolved
  validation metrics.

Run checks from this directory:

```powershell
python -m pytest
python -m brdyn.cli validate mechanisms/dke10.yaml
python -m brdyn.cli simulate mechanisms/dke10.yaml experiments/baseline/dke_reference.json
python -m tools.run_gate1
```

The long historical simulation is a regression baseline. Its numerical checks pass,
but its period and iodine amplitude fail the predeclared experimental thresholds.
It is not a validated full-batch prediction. See `reports/gate1_report.md` and
`reports/validation_report.md`.

# Validation report

## Gate status

| Gate | Status | Evidence |
|---|---|---|
| Gate 0 - provenance | SUBSTANTIALLY_COMPLETE_WITH_OPEN_PRIMARY_SOURCE_CHECKS | Every historical active parameter has an explicit source and confidence label. Several page-level origins and experimental conditions remain unresolved and visible in the CSV. |
| Gate 1 - historical reproduction | GATE_1A_PASS_GATE_1B_NOT_VALIDATED | The pooled historical DKE model is numerically converged, but period error is 26.22% and iodine-peak error is 55.23% against the predeclared digitized-data thresholds. |
| Gate 2 - subsystem audit and triage | PASS_LEVEL1_BLOCKED | Sensitivity, source-bounded uncertainty, compatibility, subsystem candidates, and error attribution are complete. Missing raw subsystem traces and condition-matched functions remain explicit blockers. |
| Gate 3 - mechanism refinement | CANDIDATE_CONSTRUCTED_NOT_RUNNABLE | Every R1-R10 path has a Level 1 status; unresolved paths remain inactive and no placeholder constants were inserted. |
| Gate 4 - quantum chemistry | QUEUE_COMPLETE_NO_JOBS_RUN | Specific R2/R4 questions are queued; Mn ET/PCET is blocked by coordination uncertainty. |
| Gate 5 - full dynamic batch model | NOT_CLAIMED | The Level 0 model can evolve all listed reactants, but its chemistry is not validated for predictive full-batch use. |
| Gate 6 - reduction analysis | NOT_STARTED | BROCODE remains a comparison model. |
| Gate 7 - iodine speciation and alpha-CD | DEFERRED | Baseline and R9 prerequisites are open. |

## Verification run

On 2026-09-20, `python -m pytest -q` completed with 8 passing tests. The historical
network validator reported 15 species, 12 directional fluxes, zero element/charge
balance errors, zero provenance errors, and zero unit errors.

A 0-10 s full-dynamic numerical smoke test at the documented placeholder initial
conditions completed with both BDF and Radau. The minimum BDF concentration was
`0.0 M`; no clipping was applied. The maximum pointwise scaled BDF/Radau difference
was `0.017316`. Repeating at `rtol=1e-10`, `atol=1e-14 M` reduced that measure to
`0.0004474`, with maximum absolute state difference `4.17e-13 M`. This is numerical
convergence evidence for the short smoke test, not chemical validation or an
oscillation-period result.

The 0-3600 s pooled-reactor Gate 1 run produced four complete post-transient cycles.
BDF and Radau agree to 3.03e-6 in mean period and better than 1.8e-7 in the scalar
extremum metrics. The DKE prediction is 526.868 s versus the 714.13 s digitized
experimental period, and its iodine peak is 2.6016e-4 M versus 5.811e-4 M. Both fail
the predeclared 10% and 20% thresholds. See `gate1_report.md` for the gate decision.

Phase 2 added 78 local-sensitivity simulations, a 20-case iodate/iodide uncertainty grid,
and a deterministic 32-case Latin-hypercube screen of the three parameters having defensible
numeric bounds. All 32 parameter cases remained oscillatory. The parameter subset spans
531.09-645.05 s and 2.6147e-4-3.8631e-4 M I2, reaching neither integrated target. The
initial-condition grid spans the period target but reaches only 3.3689e-4 M I2. These are
forward screens, not fits.

## Implemented correctness controls

- Stoichiometric matrix generated from reaction data.
- Reversible reactions compiled into separate forward and reverse fluxes.
- Exact elemental and charge balance including solvent-reservoir stoichiometry.
- Directional flux and cumulative reaction-extent output.
- BDF primary integration and Radau cross-check.
- Species-specific absolute-tolerance interface.
- No concentration clipping. Significant negative states raise `NumericalFailure`.
- Active assumed/unknown parameters emit warnings; unbalanced mechanisms are refused
  by the CLI.

## Known limitations

Neither historical experiment file is derived from stock-solution volumes and neither
satisfies the experimental-recipe requirement. The 2025 BROCODE paper states that its
chosen initial iodate and iodide could not be unambiguously recovered from the older
literature. The long run is suitable for exposing a Level 0 disagreement, not for
claiming a predictive full-batch model.

The selected 2026 Raman reference has a complete nominal stock recipe and direct polyiodide
observations, but its exact 22 °C period and raw species traces were not available in a numeric
table. Starch/polyiodide chemistry, mixed-solution proton activity, and manganese coordination
also remain unresolved. The Level 1 manifest is therefore non-runnable.

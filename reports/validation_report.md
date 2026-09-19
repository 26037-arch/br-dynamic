# Validation report

## Gate status

| Gate | Status | Evidence |
|---|---|---|
| Gate 0 - provenance | SUBSTANTIALLY_COMPLETE_WITH_OPEN_PRIMARY_SOURCE_CHECKS | Every historical active parameter has an explicit source and confidence label. Several page-level origins and experimental conditions remain unresolved and visible in the CSV. |
| Gate 1 - historical reproduction | PARTIAL | Network compilation and exact element/charge checks are implemented. BDF/Radau smoke testing is included. Published trajectory regression is not complete because the historical experiment/initial conditions are not unambiguous. |
| Gate 2 - subsystem validation | NOT_STARTED | No published time-series datasets have yet been digitized and reproduced. |
| Gate 3 - mechanism refinement | BLOCKED_BY_GATE_2 | Candidate replacements are registered but disabled. |
| Gate 4 - quantum chemistry | NOT_STARTED_BY_DESIGN | No calculation is justified until a microscopic target is selected. |
| Gate 5 - full dynamic batch model | NOT_CLAIMED | The Level 0 model can evolve all listed reactants, but its chemistry is not validated for predictive full-batch use. |
| Gate 6 - reduction analysis | NOT_STARTED | BROCODE remains a comparison model. |
| Gate 7 - iodine speciation and alpha-CD | DEFERRED | Baseline and R9 prerequisites are open. |

## Verification run

On 2026-09-20, `python -m pytest -q` completed with 7 passing tests. The historical
network validator reported 15 species, 12 directional fluxes, zero element/charge
balance errors, zero provenance errors, and zero unit errors.

A 0-10 s full-dynamic numerical smoke test at the documented placeholder initial
conditions completed with both BDF and Radau. The minimum BDF concentration was
`0.0 M`; no clipping was applied. The maximum pointwise scaled BDF/Radau difference
was `0.017316`. Repeating at `rtol=1e-10`, `atol=1e-14 M` reduced that measure to
`0.0004474`, with maximum absolute state difference `4.17e-13 M`. This is numerical
convergence evidence for the short smoke test, not chemical validation or an
oscillation-period result.

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

The current historical experiment file is a numerical smoke test. It is not derived
from stock-solution volumes and therefore does not satisfy the experimental-recipe
requirement. The 2025 BROCODE paper states that its chosen initial iodate and iodide
could not be unambiguously recovered from the older literature. No oscillation periods,
amplitudes, or mechanistic agreement claims should be made from this file.

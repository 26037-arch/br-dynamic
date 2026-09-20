# Oscillation classifier

## Algorithm

1. Locate iodide extrema from roots of the compiled ODE derivative, then bound complete cycles by successive positive iodide minima.
2. For every complete cycle, calculate period, iodide min/max/amplitude, and iodine min/max/amplitude.
3. Use the final three complete cycles; require at least three cycles.
4. Define the species resolution floor as `m * (atol + rtol * max_abs_signal)`. The declared multiplier `m=20` is a guard band over the local solver error scale. Both final iodide and iodine amplitudes must exceed it.
5. Require period CV and endpoint drift <=2%, and iodide/iodine amplitude CV and endpoint drift <=5%.
6. Classify resolved converged cycles as `RESOLVED_LIMIT_CYCLE`; resolved but nonconverged cycles as `DAMPED_OR_TRANSIENT`; sub-floor extrema as `UNRESOLVED_NUMERICALLY`; a sub-floor span with no cycle as `STEADY_STATE`; and a resolved signal with fewer than three cycles as `INSUFFICIENT_CYCLES`.
7. A solver or tolerance classification disagreement conservatively makes the consensus `UNRESOLVED_NUMERICALLY`.

These are numerical resolution/stability rules, not physical amplitude cutoffs and not fitted criteria.

## Threshold sensitivity

The looser screen uses multiplier 10 with 5% period and 10% amplitude limits. The stricter screen
uses multiplier 50 with 1% period and 2% amplitude limits. Counts below use the same 20 BDF
trajectories; declared consensus results additionally include Radau and boundary tolerance checks.

| Variant | resolved | damped/transient | steady | unresolved | insufficient |
|---|---:|---:|---:|---:|---:|
| looser | 12 | 0 | 5 | 3 | 0 |
| declared | 12 | 0 | 5 | 3 | 0 |
| stricter | 12 | 0 | 5 | 3 | 0 |

All per-cycle values, resolution scores, solver agreement, and tolerance agreement are in `initial_condition_reanalysis.csv`.

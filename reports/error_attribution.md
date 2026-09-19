# Gate 1 discrepancy: evidence-based attribution

The 526.868 s historical-DKE period and 2.6016e-4 M I2 peak are numerically reliable
outputs of the encoded Level 0 equations. They are not validated predictions of the old
experiment. The 714.13 s and 5.811e-4 M comparison values are reserved here as tests; none
of the subsystem choices below was selected to improve them.

| Category | Period classification | I2-peak classification | Evidence |
|---|---|---|---|
| A. Numerical error | NEGLIGIBLE | NEGLIGIBLE | BDF/Radau mean-period difference is 3.03e-6 relative; scalar extrema agree better than 1.8e-7 relative; invariant drift is below 3e-17 M. |
| B. Reconstructed initial conditions | MATERIAL | MINOR / INSUFFICIENT | The source-bounded iodate/iodide grid gives 449.96-1726.81 s, so 714.13 s is inside the screen. Its I2 maximum is at most 3.3689e-4 M, below 5.811e-4 M. Five of 20 cases lose measurable oscillation. |
| C. Historical parameter and condition transfer | MATERIAL | MATERIAL / INSUFFICIENT | The independently bounded k1/k8/k10 screen gives 531.09-645.05 s and 2.6147e-4-3.8631e-4 M. Neither target is reached. Parameters with mechanism-form conflicts were deliberately not assigned arbitrary ranges. |
| D. Structural mechanism error | DOMINANT FOR MODEL CREDIBILITY; MAGNITUDE UNRESOLVED | DOMINANT FOR MODEL CREDIBILITY; LIKELY REQUIRED FOR AMPLITUDE | R3 omits I3-/I5-; R5 conflicts with direct kinetics by 5-6 orders; R9 lumps enolization and I2/I3- capture; R4 and R6 are integrated-fit steps; R7 transfers high-acid/high-ionic-strength Mn chemistry. |

## Nonlinearity and interactions

These labels are not additive percentages. The joint initial-condition grid has a period
interaction as large as 669.48 s at the 0.004 M iodate oscillation boundary, while all retained
cases at 0.010 M iodate and above have period interaction below 0.003 s. The I2-peak interaction
is below 1.3e-11 M. Parameter interactions involving R4, R5, R6, and R9 cannot be propagated
honestly until their rate-law forms are defined.

The local sensitivities show why those missing forms matter. Period is most sensitive to the
lumped R9 constant (`S=-0.806`), followed by R4 (`+0.593`), R10 (`-0.379`), the R3 pair
(`+0.378/-0.374`), R6 (`+0.335`), and R2 (`-0.293`). I2 amplitude is especially sensitive to
R4 (`+2.092`), R6 (`+1.167`), R10 (`-0.904`), and the R2/R3 speciation family (about ±0.9).

## Why approximately 527 s rather than approximately 714 s?

The evidence supports a combined explanation. The reconstructed iodate and iodide choices are
not unique and can move the Level 0 period through the experimental value, particularly near the
oscillation boundary. Independently supported transfer ranges for R1, R8, and R10 lengthen the
period only to about 645 s in the sampled design and still underpredict the iodine amplitude.
The remaining high-sensitivity quantities are exactly those whose chemistry is least transferable:
the empirical R9 organic feedback, globally fitted R4 and R6 steps, the effective R3 equilibrium,
and the acid-dependent R5 conflict. Missing polyiodide, starch-binding, manganese coordination,
and iodine-hydrolysis species also make the simulated `I2` observable unlike the experimental
iodine signal.

Accordingly, initial-condition ambiguity can **partly explain the period discrepancy**, while it
cannot explain the iodine-peak discrepancy. Bounded historical parameter transfer is **material
but insufficient** for both targets. Structural and speciation deficiencies are **necessary to
resolve before causal percentages can be assigned**, and the current evidence does not support
claiming one unique chemical cause.

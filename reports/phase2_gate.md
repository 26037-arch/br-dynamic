# Phase 2 gate decision

## Decision

**PASS for the Phase 2 evidence and triage objectives. LEVEL 1 REMAINS NOT RUNNABLE.**

The gate passes because every historical reaction is now tied to a compatible, correctable,
incompatible, or unknown evidence class; uncertainty has been propagated without fitting; the
527 s versus 714 s discrepancy has an evidence-based attribution; and the remaining chemical
questions have been reduced to explicit subsystem or microscopic blockers. Passing this gate does
not validate a full-batch prediction and does not authorize placeholder rates or production ORCA.

| Requirement | Result | Evidence |
|---|---|---|
| Initial-condition uncertainty without fitting | PASS | 20-case source-bounded joint grid; 15 oscillatory cases; interaction diagnostic included. |
| Local sensitivity for every active parameter | PASS | 13 parameters, three symmetric perturbation scales, 78 simulations, no failed derivative pair. |
| R1-R10 compatibility classifications | PASS | `data/subsystem_compatibility.csv` uses the prescribed categorical classes and condition fields. |
| Validated or explicitly unresolved subsystem assignments | PASS | R1-R10 decisions appear in the subsystem reports and Level 1 manifest. |
| R5 acid dependence reconciled | PASS WITH BLOCKER | DKE global-fit value is rejected for Level 1; measured 0.2-5 M−1 s−1 family is preferred, while its exact acid function still requires source transcription. |
| R9 mechanistic candidate beyond lumped law | PASS | Keto/enol + I2 and supported I3− route candidates are machine readable; missing capture/mapping data remain null. |
| Mn identities defined or quantum problem blocked | PASS | Aqua/hydroxo/sulfato candidates and spin manifolds are stated; calculation is explicitly blocked by coordination uncertainty. |
| R4 reduced to microscopic questions | PASS | Three protonation/adduct/ET-PCET families and a charge-balanced quantum target are defined. |
| Error attribution | PASS | Numerical error negligible; initial conditions material for period; bounded transfer insufficient; structure/speciation dominant for credibility. |
| No integrated-target tuning | PASS | The 714.13 s and 5.811e-4 M values were used only for forward-envelope assessment. |
| Specific quantum queue only | PASS | R2 and R4 have molecular targets; R6 is explicitly blocked; no ORCA job was run. |

## Level 1 blocker decision

`mechanisms/audited_effective.yaml` is deliberately `NOT_RUNNABLE_UNRESOLVED_ACTIVE_PATHS`.
Activating it would require invented constants or incompatible condition transfer for R1, R2,
R3, R4, R5, R6/R7, R9, and R10. R8 alone is close to direct compatibility. The next work is
experimental/source transcription and matched-condition subsystem validation, followed by the
small HIO2 protonation/conformer calculation described in the quantum queue if its protocol is
approved. This project stops here before quantum production work.

# Quantum-chemistry decisions (Phase 0 record)

This file preserves the Phase 0 triage. The evidence-expanded, molecularly specific Phase 2
queue is `reports/quantum_queue.md` and supersedes this table for future work.

No ORCA jobs have been launched. The Phase 0 evidence does not justify calculating a
transition state for any DKE net equation.

| Target | Decision | Reason and minimum protocol |
|---|---|---|
| R1 Dushman net equation | FULL_MECHANISM_SEARCH_REQUIRED | The rate law is multistep and experimentally constrained. Compare protonation/intermediate topologies only; use aqueous free energies, iodine relativistic treatment, and explicit water where proton transfer requires it. |
| R2 candidate microstep | TS_CALCULATION_USEFUL | Direct kinetics are missing. Enumerate HIO2/IO2- protonation and solvent-assisted proton transfer before any TS search. |
| R3 iodine hydrolysis | THERMOCHEMISTRY_USEFUL | Temperature-jump kinetics exist. Use theory to rank I2OH- and protonation states, not to replace measured relaxation constants. |
| R4 radical formation | FULL_MECHANISM_SEARCH_REQUIRED | Open-shell iodine chemistry may involve ET/PCET and multiple solvent-mediated steps. Check multiplicity, spin contamination, spin-orbit/relativistic sensitivity, and diffusion. |
| R5 iodous disproportionation | VALIDATION_ONLY | Modern aqueous subsystem kinetics exist and are acid dependent. Do not calculate a TS for the overall disproportionation. |
| R6/R7 manganese cycle | ELECTRON_TRANSFER_MODEL_REQUIRED | Define Mn aqua/hydroxo/sulfato states and spin states first. Compare stepwise ET/PT and concerted PCET; use Marcus or inner-sphere treatment as appropriate. |
| R8 HO2 recombination | NOT_NEEDED | Evaluated aqueous kinetics are available. |
| R9 overall iodination | NOT_NEEDED | The net equation is lumped. Quantum work may later validate individual keto/enol or iodine-transfer microsteps. |
| R10 HOI + H2O2 | NOT_NEEDED | Modern species-specific aqueous measurements exist; the problem is condition transfer, not a missing gas-phase barrier. |

Every future calculation proposal must state charge, multiplicity, coordination and
protonation state, solvent model and explicit waters, iodine relativistic treatment,
standard-state conversion, diffusion treatment, and expected uncertainty. Raw inputs,
outputs, geometries, frequencies, and derivations must be retained.

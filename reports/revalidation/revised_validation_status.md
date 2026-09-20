# Revised validation status

- **Gate 1A numerical/historical implementation fidelity: PASS.** The historical DKE mechanism is reproducible across BDF and Radau; the mechanism was not changed.
- **Gate 1B experimental predictive validation: FAIL / NOT VALIDATED.** The predeclared period and iodine-peak gates still fail.
- **Post-Gate-1 diagnostic analysis: COMPLETE.** This is diagnostic work after failure, not evidence that experimental validation passed.
- **Level 1 activation: BLOCKED.** Mechanism refinement and fitting remain out of scope until numerical/analysis validation is secure.

The revised grid contains 12 resolved limit cycles, 0 damped/transient cases, and 3 numerically unresolved cases.
Resolved period range: 449.958233-561.775382 s. Resolved iodine-peak range: 4.359818e-05-0.000336893228 M.
The digitized single-cycle value 714.13 s is outside the resolved initial-condition envelope.
Local sensitivity parameter/observable pairs below the empirical numerical floor: k7_DKE/iodide_max_M, k7_DKE/iodide_min_M, k7_DKE/iodine_peak_M, k7_DKE/mean_period_s, k8_DKE/iodide_max_M, k8_DKE/iodide_min_M, k8_DKE/iodine_peak_M, k8_DKE/mean_period_s.

The prior scientific conclusion changed: the initial-condition period result is no longer `PARTIALLY`;
the apparent ~669 s nonlinear interaction came entirely from unresolved 0.004 M iodate cases and is excluded.

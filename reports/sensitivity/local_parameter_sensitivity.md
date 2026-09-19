# Local normalized parameter sensitivity

Sensitivities use symmetric multiplicative perturbations of +/-0.5%, +/-1%, and +/-2%.
No experimental target enters these calculations and no parameter is optimized. The table
reports the median derivative across the three scales; `spread` is max minus min and is a
finite-difference stability diagnostic.

| Rank | Parameter | DKE reaction | Confidence | S(period) | spread | S(I2 max) | S(I- min) | S(I- max) |
|---:|---|---|---|---:|---:|---:|---:|---:|
| 1 | k9_DKE | R9 | SUBSYSTEM_FIT | -0.8062 | 2.003e-05 | -0.2697 | -0.09988 | 0.8868 |
| 2 | k4_DKE | R4 | GLOBAL_FIT | 0.5934 | 9.408e-05 | 2.092 | -0.04358 | 0.6543 |
| 3 | k10_DKE | R10 | MEASURED_DERIVED | -0.3791 | 4.509e-05 | -0.9042 | 0.8666 | -0.2806 |
| 4 | k3_DKE | R3 | MEASURED_DERIVED | 0.3777 | 4.572e-05 | 0.9023 | -0.8558 | 0.28 |
| 5 | k_minus3_DKE | R3 | MEASURED_DERIVED | -0.3741 | 4.528e-05 | -0.8923 | 0.2816 | -0.2768 |
| 6 | k6_DKE | R6 | GLOBAL_FIT | 0.3352 | 6.956e-06 | 1.167 | -0.1361 | 0.3655 |
| 7 | k2_DKE | R2 | LITERATURE_ESTIMATE | -0.2927 | 5.878e-05 | -0.9024 | -0.2753 | -0.2816 |
| 8 | C9_DKE | R9 | SUBSYSTEM_FIT | 0.2443 | 3.605e-05 | 0.1933 | 0.0001315 | -0.6248 |
| 9 | k_minus4_DKE | R4 | LITERATURE_ESTIMATE | -0.17 | 3.167e-06 | -0.586 | 0.05183 | -0.1835 |
| 10 | k5_DKE | R5 | GLOBAL_FIT | -0.1594 | 2.218e-06 | -0.607 | 0.07919 | -0.19 |
| 11 | k1_DKE | R1 | MEASURED_DERIVED | -0.125 | 1.115e-05 | 0.0001818 | 0.1315 | -0.9738 |
| 12 | k8_DKE | R8 | MEASURED_DERIVED | 2.04e-08 | 9.05e-07 | -4.818e-09 | -2.445e-07 | -5.02e-09 |
| 13 | k7_DKE | R7 | MEASURED_DERIVED | 3.326e-10 | 1.421e-10 | 1.376e-12 | -2.283e-10 | 2.309e-12 |

## Interpretation

All parameter/scale pairs retained at least two measurable post-transient iodide minima.

Large magnitudes identify parameters whose independent chemistry deserves priority; they do not
authorize adjustment against the integrated BR period. Sign indicates the local direction of change.
Mechanistic interpretation must be combined with provenance and subsystem compatibility evidence.

The ranking is chemically coherent for the historical topology. R9 has the largest period
sensitivity because it removes molecular iodine while regenerating iodide, closing the slow
organic feedback loop. R4, R6, and the R3 pair control entry to and coupling of the radical,
manganese, and iodine-speciation branches, so they strongly affect the iodine amplitude. The
nearly opposite R3 forward/reverse sensitivities show that an equilibrium/speciation ratio, not
either isolated constant, is the relevant refinement target. The empirical R9 denominator also
matters independently, confirming that replacing only `k9` would not resolve the lumped law.

R7 and R8 are numerically decoupled from the reported observables in this pooled configuration:
Mn2+, H2O2, and the other pools are fixed, while the R7/R8 products do not return to an upstream
dynamic species. Their near-zero sensitivities are therefore a topology and chemostat result, not
evidence that manganese-peroxide or HO2 chemistry is irrelevant in a full batch reactor.

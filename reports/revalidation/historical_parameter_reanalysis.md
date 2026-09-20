# Historical-parameter uncertainty reanalysis

All 32 rows were read directly from the CSV; all have status `OSCILLATORY` under the historical two-minimum rule.
Because their raw trajectories were not preserved, that historical label cannot be upgraded retrospectively
to `RESOLVED_LIMIT_CYCLE` from row summaries alone.

## Correlation and dominance

| Output | Parameter | Pearson r | Spearman rho | standardized beta | squared-beta share |
|---|---|---:|---:|---:|---:|
| mean_period_s | k1_DKE | -0.06622 | -0.05352 | -0.20565 | 4.10% |
| mean_period_s | k8_DKE | -0.28530 | -0.26650 | -0.02698 | 0.07% |
| mean_period_s | k10_DKE | -0.97139 | -0.97617 | -0.99419 | 95.83% |
| iodine_peak_M | k1_DKE | 0.13266 | 0.14260 | -0.00563 | 0.00% |
| iodine_peak_M | k8_DKE | -0.26861 | -0.24194 | -0.02920 | 0.09% |
| iodine_peak_M | k10_DKE | -0.99380 | -1.00000 | -0.98754 | 99.91% |
| iodide_min_M | k1_DKE | -0.03959 | -0.07258 | 0.10362 | 1.05% |
| iodide_min_M | k8_DKE | 0.25862 | 0.25293 | 0.00581 | 0.00% |
| iodide_min_M | k10_DKE | 0.99449 | 0.99597 | 1.00786 | 98.95% |
| iodide_max_M | k1_DKE | -0.93463 | -0.93878 | -0.98787 | 88.39% |
| iodide_max_M | k8_DKE | -0.14493 | -0.15982 | 0.02691 | 0.07% |
| iodide_max_M | k10_DKE | -0.20966 | -0.18512 | -0.35704 | 11.55% |

Within this design, k10_DKE accounts for 95.83% of the summed squared standardized coefficients for period
and 99.91% for iodine peak. This quantitatively supports k10 dominance in those outputs.

## Design coverage and limitation

- k1_DKE: normalized sampled range 0.01562 to 0.98438; neither box boundary is included.
- k8_DKE: normalized sampled range 0.01562 to 0.98438; neither box boundary is included.
- k10_DKE: normalized sampled range 0.01563 to 0.98438; neither box boundary is included.

The deterministic Latin-hypercube midpoints cover the interiors of all one-dimensional ranges,
but do not evaluate any of the eight corners. The reported min/max is therefore a 32-point sampled
envelope, not a mathematically bounded parameter-box uncertainty interval. No calibration or fitting
was performed, and no corner envelope is claimed.

## Row-level inspection

All sample IDs 1-32 are present exactly once; every input triplet is unique. The row-level outputs
are retained unchanged in the historical CSV. Four rows (1, 3, 10, 31) report only three complete
periods and the remaining 28 report four, emphasizing why the missing trajectory-level convergence
diagnostics matter.

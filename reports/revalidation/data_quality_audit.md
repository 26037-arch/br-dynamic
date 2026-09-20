# Experimental data-quality audit

The archival CSV files were not modified. A sorted analysis copy was created with the
original data-row number retained in `archival_data_row`.

| Issue | Exact rows/cases | Severity | Scientific effect |
|---|---|---|---|
| Non-monotonic time | archival data row 96 (file line 97): 1163.413106 s follows 1168.66877 s | Moderate | No gate conclusion changes; sorting is required for valid time-series operations and does not alter the two-peak interval. |
| Negative digitized iodine | data rows 48, 49, 50, 51, 52, 53, 54, 55, 56, 57 | Moderate | No peak/gate conclusion changes; these baseline/digitization artifacts cannot be interpreted as physical concentrations. |
| Only two resolved high-pI peaks | 482.726 and 1196.854 s | High for uncertainty claims | The gate comparison is numerically unchanged, but 714.13 s cannot be called a statistical mean and has no empirical uncertainty estimate. |

Exact negative values: row 48: -8.130619e-07 M; row 49: -2.0739841e-06 M; row 50: -1.0415007e-06 M; row 51: -2.2723652e-06 M; row 52: -3.4791835e-06 M; row 53: -2.4527117e-06 M; row 54: -2.554908e-06 M; row 55: -3.757218e-07 M; row 56: -4.839296e-07 M; row 57: -5.620798e-07 M.
The most negative value is -3.4791835e-06 M, equal to 0.599% of the measured peak (0.000581121334 M).

The revised name is `digitized_single_cycle_period_s`; `mean_period_s` remains only as a backward-compatible historical input key.

## pI acceptance interpretation

The predeclared Gate 1 thresholds and decisions are unchanged. A pI difference is logarithmic:
the passing low-pI comparison corresponds to a 2.647x concentration ratio,
and the passing high-pI comparison corresponds to a 1.048x ratio.
Passing the coarse pI threshold therefore does not by itself imply close concentrations.

# Gate 1 historical-reproduction report

## Decision

**NUMERICAL PASS; EXPERIMENTAL COMPARISON FAIL. Do not advance to Gate 2 under the
user's conditional instruction.**

The exact historical DKE encoding generates a stable limit cycle in the documented
pooled-reactor configuration. Both stiff solvers agree, no significant negative
concentration occurs, and the effective stoichiometric invariants remain constant.
The predicted period and iodine peak nevertheless exceed the predeclared error
limits relative to the digitized historical experiment.

## Predeclared comparison

Thresholds were stored in `experiments/baseline/dke_pooled_gate1.json` before the
long model evaluation. The experimental source is a WebPlotDigitizer reconstruction;
the original raw measurements are unavailable. These thresholds are pragmatic gates,
not statistical confidence intervals.

| Metric | Digitized experiment | BDF model | Error | Threshold | Result |
|---|---:|---:|---:|---:|---|
| Mean period | 714.13 s | 526.868 s | 26.22% | 10% | FAIL |
| I2 peak | 5.811e-4 M | 2.6016e-4 M | 55.23% | 20% | FAIL |
| Minimum pI | 5.50 | 5.077 | 0.423 | 0.50 | PASS |
| Maximum pI | 10.01 | 10.030 | 0.020 | 0.50 | PASS |

The image `gate1_reproduction.png` shows the phase-aligned last model cycle and the
digitized reference points. Exact values are in `gate1_metrics.json` and
`gate1_comparison.csv`.

## Numerical evidence

- Four complete cycles occur after the 900 s transient cutoff.
- BDF/Radau relative differences are 3.03e-6 for mean period and below 1.8e-7 for
  each scalar amplitude/extremum metric.
- Minimum concentration is 0 M; no clipping is applied.
- Maximum effective-stoichiometric invariant drift is 2.78e-17 M (BDF) and
  2.08e-17 M (Radau).
- Element and charge balance remain exact for all 12 directional fluxes.

The earlier 0.371 pointwise scaled BDF/Radau discrepancy is a phase-sensitive metric
over 3600 s and is therefore misleading for a periodic trajectory. Root-located
cycle metrics show solver agreement without phase accumulation.

## Interpretation

The mismatch must remain visible. The 2025 BROCODE paper is not a numerical target
for the exact historical DKE mechanism: it reports changing several constants for a
better experimental match (including k1, k-3, k-4, and k9), and its displayed reduced
equations use a simple k9[MA][I2] term. The Level 0 mechanism retains the audited DKE
constants and its documented saturating R9 law, so copying the BROCODE substitutions
would violate the no-undocumented-fitting rule.

Initial iodate and iodide concentrations are also not recoverable unambiguously from
the historical experiment. The values used here follow the 2025 comparison and are
explicitly labeled as choices rather than reconstructed recipe values.

## Next scientific requirement

Gate 1 can be revisited only with one of the following independently justified paths:

1. locate a primary DKE numerical trajectory and its exact initial-condition/rate-law
   conventions for a true Level 0 regression; or
2. encode the 2025 BROCODE parameter set as a separate reduced comparison model and
   validate that implementation against its published figure, without replacing the
   DKE constants; or
3. obtain a documented experimental recipe and uncertainty-bearing raw data for a
   physically meaningful baseline comparison.

# Initial-condition uncertainty propagation

## Scope

This is a source-bounded screening analysis, not a fit. Iodate spans the 0.0040-0.0255 M
oscillatory interval reported by Dimsey, Forbes, and Bassom (2025). Iodide spans the
documented ambiguity between a nominally iodide-free reconstructed experiment and the
0.0004 M seed selected for their comparison. The four reported pool values remain fixed
because the source gives no alternative values or measurement uncertainties.

## Results

- 15 of 20 cases retained at least two measurable cycles.
- Period range: 449.958-1726.81 s.
- I2 peak range: 2.1223e-09-0.000336893 M.
- I- minimum range: 8.92509e-11-2.05464e-09 M.
- I- maximum range: 2.05464e-09-8.41545e-06 M.

## Nonlinear interaction check

The joint grid was also evaluated with the two-factor finite-difference interaction
`f(IO3,I)-f(IO3,I_anchor)-f(IO3_anchor,I)+f(anchor)` about 0.0225 M iodate and
0.0004 M iodide. This is a diagnostic of non-additivity, not a variance decomposition.

- Maximum absolute period interaction: 669.479 s (127.07% of the anchor period).
- Maximum absolute I2-peak interaction: 1.23078e-11 M (0.00% of the anchor peak).

The large period interaction occurs only at the 0.004 M iodate edge, where the
oscillator is close to its reported existence boundary and cycle selection changes sharply.
For retained cases at 0.010 M iodate and above, period interactions are below 0.003 s.
The iodine-peak interaction remains below 1.3e-11 M throughout the retained grid.

## Explicit answers

**Can the documented initial-condition ambiguity explain the 26.22% period discrepancy? PARTIALLY.**
**Can it explain the 55.23% I2-peak discrepancy? NO.**

`PARTIALLY` means the target lies inside the forward-screened output envelope, but the input
envelope is not a probability distribution and cannot identify which initial condition was used.
It therefore supplies plausibility evidence only. `NO` means the target lies outside the envelope.

## Limits

The iodate bounds are model oscillation bounds rather than an uncertainty interval for the old
experiment. A zero iodide seed also tests a structural limitation: the Level 0 network has no
alternative initiation path when all iodine intermediates are exactly zero. H+, H2O2, malonic acid,
and Mn2+ could not be propagated honestly because no source-supported uncertainty was found.

# Parameter audit status

The historical Level 0 file contains 12 directional flux constants plus the empirical
R9 saturation parameter. Every active constant has a source and confidence category.
There are no silent fitted values.

The most consequential provenance findings are:

- R4 forward and reverse constants are analogy-based, not measured iodine kinetics.
- R5 is a DKE optimization. It conflicts by orders of magnitude with the later isolated
  iodous-acid disproportionation rate and must not migrate into Level 1 unchanged.
- R6 is estimated from radical-cation analogies.
- R7 descends from Mn(III)-peroxide measurements made in 1.00-3.70 M perchloric acid
  and very high ionic strength.
- R9 is a saturating empirical law, not mass action for the written net equation.
- R10's historical value is numerically close to the 2020 species-specific value, but
  the modern acidic experiments used buffers and Ag+ to suppress iodine feedback.
- The 2025 BROCODE study reports changing k1, k-3, k-4, and k9 partly to improve the
  match. Those choices are excluded from this provenance baseline.

The authoritative machine-readable ledger is `data/parameter_provenance.csv`.


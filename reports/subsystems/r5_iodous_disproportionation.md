# R5 iodous-acid disproportionation

The historical value `k5 = 6.0e5 M−1 s−1` was selected in the integrated DKE model. A
later isolated-subsystem study using a crotonic-acid HOI scavenger found roughly
0.2–5 M−1 s−1 as sulfuric acid changed from 0.60 to 0.08 M
([Schmitz and Furrow, 2013](https://doi.org/10.1002/kin.20791)). The gap is five to six
orders of magnitude and is too large to label as ordinary parameter uncertainty.

This is evidence of a mechanism-form or species-definition conflict: DKE `HIO2` and the
isolated iodous-acid subsystem are not safely interchangeable without matching acid activity
and fast speciation. A probability interval spanning both numbers would conceal that conflict.

**Decision:** retain DKE R5 only in Level 0. Level 1 should use an acid-dependent subsystem
law transcribed from the 2013 source. No transition-state calculation is justified for the net
disproportionation while direct aqueous kinetics exist.

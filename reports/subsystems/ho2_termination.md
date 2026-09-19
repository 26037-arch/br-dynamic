# HO2 termination: R8

The evaluated aqueous self-reaction value `k(HO2 + HO2) = 8.3e5 M−1 s−1` is close to the
DKE value `7.5e5 M−1 s−1` ([Bielski et al., 1985](https://doi.org/10.1063/1.555739)).
This is the strongest numerical compatibility among the ten historical steps.

HO2 has pKa about 4.8. At pH 2 the equilibrium O2− fraction is about
`10^(2-4.8) = 0.0016`, or 0.16%, and it is smaller at higher acidity. This supports an
HO2-dominant approximation for a measured pH below 2, while still requiring the HO2/O2−
acid-base pair in a physical-chemistry mechanism. The mixed reference solution’s proton
activity is not known from stock pH alone.

**Decision:** keep the HO2 self-reaction as a measured effective elementary step, update its
central value only in a separately versioned Level 1 model, and add O2− plus cross-reaction
terms before applying it outside the strongly acidic limit.

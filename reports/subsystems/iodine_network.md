# Acidic iodate and iodine subsystem: R1-R5

## R1 Dushman oxidation

The historical R1 is only the low-iodide limiting term. Later kinetic analysis resolves a
`1200 ± 150 M−3 s−1` term with the DKE-like acid and iodide orders and a second
`(4.2 ± 0.8)e8 M−4 s−1` contribution at higher iodide, measured at ionic strength 0.2 M
([Schmitz, 2000](https://doi.org/10.1039/B003606O)). Manganese sulfate ion pairing can also
alter the apparent Dushman rate ([Schmitz and Bourceanu, 2017](https://doi.org/10.1007/s11144-017-1264-1)).

A two-term empirical law is adequate for a first Level 1 subsystem test only inside the
measured concentration and activity domain. Explicit protonated iodate and I(+1)/I(+3)
intermediates are required for extrapolation across the reference oscillation because iodide
spans orders of magnitude and sulfate is present. The full law and its activity convention must
be transcribed before activation.

## R2 iodine-specific constraint

DKE states that `k2` came from bromine analogy. The literature search did not find a later
direct iodine-specific rate for the literal `HIO2 + I− + H+ -> 2 HOI` event. The net equation
can be decomposed through a protonated iodous-acid state, `[H2IO2]+ + I− -> 2 HOI`, with
explicit water assisting proton transfer, but that is a quantum candidate rather than an
established mechanism.

## R3 speciation and observable mapping

The DKE pair `HOI + I− + H+ <-> I2 + H2O` is an effective relaxation expression. It
cannot represent the triiodide and pentaiodide bands observed directly in the 2026 Raman
reference experiment. It also folds fast iodine hydrolysis, proton transfer, and activity
effects into two constants measured at 20 °C under a historical convention.

An independently measured concentration equilibrium for `I2 + I− <-> I3−` is
approximately 768 M−1 at 24 °C ([Morrison et al., 1971](https://doi.org/10.1016/0003-2697(71)90026-1)).
Later iodine-hydrolysis analyses also require coupled hydrolysis species rather than a single
elementary R3 ([Schmitz, 2004](https://doi.org/10.1002/kin.20020)). These data support an
expanded equilibrium network, but they do not by themselves establish transfer to the
reference sulfate/starch mixture.

The Level 1 candidate therefore adds I3−, I5−, and I2OH− explicitly and leaves missing
constants null. The first activation target is a self-consistent equilibrium model at matched
temperature and ionic strength. Its observables must report free I2 separately from I3−,
I5−, and starch-bound iodine. Total spectroscopic iodine cannot be compared to DKE `[I2]`.

**Decision:** replace R3 with an activity-aware fast-speciation network; keep the candidate
non-runnable until the I5− and hydrolysis constants and response mapping are supplied.

## R4 radical-forming branch

No iodine-specific direct kinetic constraint was found for the DKE net radical-forming step.
The audit reduces the uncertainty to three microscopic families:

1. `IO3− + H+ <-> HIO3`, followed by an HIO3/HIO2 encounter complex and electron transfer;
2. `HIO2 + H+ <-> [H2IO2]+`, followed by `[H2IO2]+ + IO3− -> 2 IO2• + H2O`;
3. an O-I bonded adduct followed by homolysis, with one or more explicit waters mediating PCET.

All preserve the DKE net atom and charge balance, but they differ in protonation, spin surfaces,
and whether a conventional transition state exists. This is sufficiently specific for a quantum
queue; it is not sufficient to assign a rate.

## R5 link

R5 has direct acid-dependent subsystem evidence and is treated separately in
`r5_iodous_disproportionation.md`. Its five-to-six-order conflict with the DKE fit prevents the
R1-R5 family from being represented as the original five effective reactions in Level 1.

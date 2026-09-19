# Briggs-Rauscher mechanism audit

## Scope and evidence standard

This is a Phase 0 audit of the ten nominal reactions in De Kepper and Epstein (DKE),
JACS 104 (1982) 49-55, DOI 10.1021/ja00365a012. The DKE paper is treated as a
historical model, not as evidence that each written equation is elementary. Numerical
values are admitted to the historical file only with a provenance category. A value is
not admitted to the audited-effective model merely because it generates oscillations.

The audit used DKE; the contemporaneous Furrow-Noyes subsystem and skeleton papers;
later primary studies of Dushman kinetics, iodine hydrolysis, iodous-acid
disproportionation, Mn(III)-peroxide kinetics, aqueous HO2/O2- kinetics, and
HOI-peroxide kinetics; and the 2025 BROCODE paper as a documented reduced-model
comparison. BROCODE is not a mechanistic authority. The 2025 paper says it changed
several DKE constants to improve agreement, and that some historical initial conditions
could not be recovered unambiguously.

The compatibility labels used below are DIRECTLY_COMPATIBLE,
REQUIRES_CORRECTION, REQUIRES_REFORMULATION, REQUIRES_NEW_CALCULATION, and
UNRESOLVED. No DKE step currently qualifies as unconditionally DIRECTLY_COMPATIBLE
with a future physical-chemistry full-batch model.

## R1

### Reaction identity

`IO3- + I- + 2 H+ -> HIO2 + HOI`

### Historical role

R1 initiates the nonradical iodate-reduction branch and supplies HIO2 and HOI. DKE
adopted the low-iodide limiting Dushman term reported through earlier subsystem work.

### Experimental evidence

DKE gives `k1 = 1.43e3 M^-3 s^-1` at 25 C from Furuichi and Liebhafsky's
low-iodide work using AgI and AgNO3 (DOI 10.1246/bcsj.48.745). Schmitz later measured the Dushman reaction at very low
iodide in 0.2 M ionic strength at 25 C and obtained
`r=[IO3-][H+]^2(k'[I-]+k''[I-]^2)`, with `k'=1200+/-150 M^-3 s^-1` and
`k''=(4.2+/-0.8)e8 M^-4 s^-1` (DOI 10.1039/B003606O). At higher iodide and acid,
accelerated-flow experiments found saturation-like departures caused by HIO3 and an
I2O2 intermediate (DOI 10.1021/ic9807442). Schmitz's 1999 synthesis identifies an
asymmetric `YXO2` intermediate for iodate-halide systems (DOI 10.1039/A809291E).

### Elementary-status assessment

**PSEUDOELEMENTARY.** The written four-reactant event is not physically credible as
one elementary collision. The measured DKE-like term is a limiting rate law of a
multistep Dushman network.

### Known intermediates

HIO3/protonated iodate forms, I2O2 or protonated asymmetric I-I-O intermediates, HIO2,
and HOI are supported in later Dushman mechanisms. Exact notation and protonation vary
between sources.

### Rate-law assessment

Mass action for the written equation is justified only as the low-I- limiting term. It
omits the measured second-order iodide term and saturation/speciation denominators.

### Compatibility assessment

**REQUIRES_REFORMULATION.** The DKE constant is close to the later low-I- coefficient,
but BR traverses a large iodide range. Ionic strength, sulfuric-acid speciation, HIO3,
and changing activity coefficients must be represented before combining the law.

### Quantum-chemistry usefulness

**FULL_MECHANISM_SEARCH_REQUIRED.** Quantum work could compare candidate
intermediate topologies, but should not replace the measured macroscopic rate law.

### Final modeling decision

**REPLACE_WITH_MICROSTEPS.** Keep R1 only in Level 0 until the Dushman subnetwork is
reconciled against both low- and high-iodide data.

## R2

### Reaction identity

`HIO2 + I- + H+ -> 2 HOI`

### Historical role

R2 consumes iodide and HIO2 in the nonradical branch and feeds HOI.

### Experimental evidence

DKE states that no direct experimental measurement was available and chose
`k2 = 2.0e10 M^-2 s^-1` by analogy with bromine chemistry. Later iodous-acid studies
include this stoichiometry in autocatalytic networks but do not establish the DKE value
as a transferable elementary constant.

### Elementary-status assessment

**PSEUDOELEMENTARY.** Protonation and solvent participation are hidden, and the
constant is analogical.

### Known intermediates

Protonated HIO2/IO2- speciation and iodine(+1) species are plausible. A uniquely
identified transition structure has not been established by the audited sources.

### Rate-law assessment

The cubic concentration expression is a historical effective law. Its activity and
protonation conventions are unresolved.

### Compatibility assessment

**REQUIRES_NEW_CALCULATION** and preferably new direct kinetics under controlled acid
and ionic strength. Bromine-to-iodine transfer is not adequate provenance.

### Quantum-chemistry usefulness

**TS_CALCULATION_USEFUL**, after reactant protonation and solvent-assisted pathways are
enumerated. Experimental validation remains necessary.

### Final modeling decision

**REQUIRES_MORE_DATA.** Retain only for Level 0.

## R3

### Reaction identity

`HOI + I- + H+ <-> I2 + H2O`

### Historical role

R3 couples iodide, HOI, and molecular iodine and controls the visible iodine reservoir.

### Experimental evidence

DKE adopted the temperature-jump relaxation analysis of Eigen and Kustin at 20 C:
`k3=3.1e12 M^-2 s^-1`, `k-3=2.2 s^-1`. Later reanalyses describe iodine hydrolysis as
an apparently simple but mechanistically complex system and invoke `I2OH-`-type
intermediates. Schmitz 2004 reviewed iodine(+1) hydrolysis and recommended kinetic and
equilibrium constants (DOI 10.1002/kin.20020).

### Elementary-status assessment

**EQUILIBRIUM_REPRESENTATION.** The written reversible equation summarizes coupled
hydrolysis/speciation steps.

### Known intermediates

I2OH- (notation varies), HOI/OI-, I-, I2, and I3- when iodide is present.

### Rate-law assessment

The DKE forward/reverse law reproduces an overall relaxation convention. It should not
be interpreted as two elementary elementary reactions. Water is absorbed into the
historical reverse constant.

### Compatibility assessment

**REQUIRES_REFORMULATION.** Temperature, ionic strength, I3- formation, activity
convention, and the water standard state must be reconciled.

### Quantum-chemistry usefulness

**THERMOCHEMISTRY_USEFUL** for protonation and intermediate ordering. Experimental
relaxation kinetics should remain primary.

### Final modeling decision

**REPLACE_WITH_MICROSTEPS.** Preserve the DKE pair for baseline regression only.

## R4

### Reaction identity

`IO3- + HIO2 + H+ <-> 2 IO2 radical + H2O`

### Historical role

R4 supplies the radical branch and autocatalytic feedback through IO2 radicals.

### Experimental evidence

DKE explicitly says no experimental data were available. It compared bromine/FKN,
Bray-Liebhafsky, and Furrow-Noyes estimates, then optimized the forward value for
improved agreement and adopted the values
`k4=7.3e3 M^-2 s^-1` and `k-4=1.7e7 M^-1 s^-1` in the historical formulation.

### Elementary-status assessment

**UNKNOWN.** The written reaction changes two iodine centers and yields two radicals;
concerted electron/proton transfer, solvent assistance, or multiple steps are plausible.

### Known intermediates

No sufficiently verified microscopic sequence was located in the audited sources.

### Rate-law assessment

Mass action is an unvalidated modeling hypothesis.

### Compatibility assessment

**REQUIRES_NEW_CALCULATION.** There is no direct iodine-specific experimental constant
to correct for BR conditions.

### Quantum-chemistry usefulness

**FULL_MECHANISM_SEARCH_REQUIRED.** Open-shell surfaces, explicit solvent/proton
transfer, iodine relativistic treatment, and possible electron transfer must be tested.

### Final modeling decision

**REQUIRES_MORE_DATA.** R4 remains active only in Level 0.

## R5

### Reaction identity

`2 HIO2 -> IO3- + HOI + H+`

### Historical role

R5 terminates HIO2 autocatalysis by disproportionation.

### Experimental evidence

DKE optimized `k5` from an initial `4e6` to `6e5 M^-1 s^-1`. Schmitz and Furrow later
isolated the reaction with crotonic acid as an HOI scavenger and measured a purely
second-order law whose constant fell from about `5` to `0.2 M^-1 s^-1` as sulfuric acid
rose from 0.08 to 0.60 M at 25 C (DOI 10.1002/kin.20791). They also showed that the
unscavenged system is autocatalytic through coupled iodine(+1) reactions.

### Elementary-status assessment

**PSEUDOELEMENTARY.** A second-order isolated channel exists, but observed kinetics in
the network include acid-base speciation and faster autocatalytic side pathways.

### Known intermediates

HIO2/IO2-, HOI, I-, and iodine species participating in the autocatalytic loop.

### Rate-law assessment

The DKE mass-action form is structurally useful but its fitted constant is not a direct
measurement and is orders of magnitude above the later isolated rate.

### Compatibility assessment

**REQUIRES_CORRECTION.** Use an acid/speciation-dependent subsystem model; do not swap
in one modern number without reproducing the scavenger-free network.

### Quantum-chemistry usefulness

**VALIDATION_ONLY.** Modern experiment is more valuable than a new overall-reaction TS.

### Final modeling decision

**KEEP_AS_EFFECTIVE_STEP** only after subsystem validation with an acid-dependent
parameterization. The DKE value remains Level 0 only.

## R6

### Reaction identity

`IO2 radical + Mn2+ + H2O -> HIO2 + MnOH2+`

### Historical role

R6 couples the iodine radical branch to oxidation of Mn(II), producing the historical
Mn(III) hydroxo species.

### Experimental evidence

DKE estimated `k6=1.0e4 M^-1 s^-1` from radical-cation rate constants, including
cerium/bromine analogies, and selected it because it gave the best model results. No direct measurement of the written aqueous coordination
reaction was identified.

### Elementary-status assessment

**PSEUDOELEMENTARY.** `Mn2+` and `MnOH2+` are shorthand for solvated, acid-dependent
coordination ensembles. Electron and proton transfer may be separate or concerted.

### Known intermediates

Mn(II) and Mn(III) aqua/hydroxo complexes; IO2 radical; HIO2/IO2-.

### Rate-law assessment

The bilinear law is a historical effective electron-transfer law with water absorbed.

### Compatibility assessment

**REQUIRES_REFORMULATION.** Sulfate/perchlorate ligation, acid, ionic strength, redox
state, and spin/coordination state must match.

### Quantum-chemistry usefulness

**ELECTRON_TRANSFER_MODEL_REQUIRED.** Marcus or inner-sphere treatment should be
selected only after aqueous coordination states are defined.

### Final modeling decision

**REQUIRES_MORE_DATA.** Treat jointly with R7.

## R7

### Reaction identity

`MnOH2+ + H2O2 -> Mn2+ + H2O + HO2 radical`

### Historical role

R7 regenerates Mn(II) and creates HO2 radical, closing the manganese catalytic cycle.

### Experimental evidence

DKE's `k7=3.2e4 M^-1 s^-1` is tied to Davies, Kirschenbaum, and Kustin's stopped-flow
Mn(III)-H2O2 study at 25 C in 1.00-3.70 M HClO4 and ionic strength 2.23-4.90 M
(DOI 10.1021/ic50059a031). That source proposes multiple Mn(III)-peroxide pathways and
reports condition-dependent observed behavior.

### Elementary-status assessment

**PSEUDOELEMENTARY.** The label hides Mn coordination/protonation and a multistep redox
sequence.

### Known intermediates

Mn(III) aqua/hydroxo species, protonated peroxide, HO2/O2-, and Mn(II) complexes.

### Rate-law assessment

The DKE bilinear expression is an effective reduction. It is not a transferable
elementary constant.

### Compatibility assessment

**REQUIRES_CORRECTION.** The source acid and ionic strength are much higher than many BR
recipes; sulfate versus perchlorate coordination also matters.

### Quantum-chemistry usefulness

**ELECTRON_TRANSFER_MODEL_REQUIRED**, with multiple spin and coordination states.

### Final modeling decision

**REQUIRES_MORE_DATA.** Validate R6/R7 as a coupled subsystem.

## R8

### Reaction identity

`2 HO2 radical -> H2O2 + O2`

### Historical role

R8 terminates HO2 radicals and regenerates peroxide while producing oxygen.

### Experimental evidence

DKE used `7.5e5 M^-1 s^-1`. The evaluated aqueous compilation by Bielski et al.
(DOI 10.1063/1.555739) recommends `8.3e5 M^-1 s^-1` for HO2 + HO2, averaged from five
datasets. The same evaluation stresses HO2/O2- acid-base coupling with pKa about 4.8.

### Elementary-status assessment

**PROBABLY_ELEMENTARY** for the HO2 + HO2 channel, while the total radical decay law is
pH-dependent because HO2 + O2- and O2- + O2- differ.

### Known intermediates

HO2 radical and superoxide O2- are the relevant acid-base pair.

### Rate-law assessment

Second-order mass action is justified for the species-specific HO2 channel. A single
constant for total `HO2/O2-` is not justified over changing pH.

### Compatibility assessment

**REQUIRES_CORRECTION** by explicit radical acid-base speciation in physical-chemistry
mode. The historical value is acceptable for Level 0.

### Quantum-chemistry usefulness

**NOT_NEEDED.** High-quality aqueous evaluated kinetics exist.

### Final modeling decision

**KEEP_AS_EFFECTIVE_STEP**, using modern evaluated kinetics with explicit speciation.

## R9

### Reaction identity

`I2 + malonic acid -> iodomalonic acid + I- + H+`

### Historical role

R9 removes iodine and regenerates iodide, providing the organic feedback required for
oscillation. DKE combined enolization and iodination in one step.

### Experimental evidence

DKE used `v9=k9[I2][MA]/(1+C9[I2])` with `k9=40 M^-1 s^-1` and `C9=1e4 M^-1`.
Noyes-Furrow explicitly described the skeleton as 11 pseudoelementary processes and
separated enolization from alpha-halogenation. Later work shows IMA and diiodomalonic
acid participate in further reactions; for example, I2MA transfers I(+1) to MA and
decarboxylates (DOI 10.1021/jp8064163).

### Elementary-status assessment

**EMPIRICAL_RATE_LAW.** The net equation cannot be one elementary event.

### Known intermediates

Malonic-acid keto/enol and acid-base forms, I2/I3-, iodomalonic acid, and
diiodomalonic acid.

### Rate-law assessment

The saturation denominator is direct evidence that mass action for the written net
equation is not the historical law. The expression hides enolization and iodine
speciation.

### Compatibility assessment

**REQUIRES_REFORMULATION.** Acid, malonate speciation, ionic strength, I3-, and later
alpha-CD binding all change the free reactants.

### Quantum-chemistry usefulness

**VALIDATION_ONLY** for individual enol or iodine-transfer microsteps. A TS for the
overall equation is scientifically invalid.

### Final modeling decision

**REPLACE_WITH_MICROSTEPS** before any alpha-CD extension.

## R10

### Reaction identity

`HOI + H2O2 -> I- + O2 + H+ + H2O`

### Historical role

R10 removes HOI, consumes peroxide, and regenerates iodide in the nonradical branch.

### Experimental evidence

DKE used `37 M^-1 s^-1`. Shin et al. measured iodine/peroxide kinetics and obtained a
species-specific `k(HOI+H2O2)=29+/-5.2 M^-1 s^-1`, plus much faster HOI+HO2- and
OI-+HO2- channels (DOI 10.1016/j.watres.2020.115852). Their acidic experiments used
buffers and 100 micromolar Ag+ to suppress I2 formation; below pH 7 the unsuppressed
system did not follow simple pseudo-first-order kinetics because I- generated I2.

### Elementary-status assessment

**EMPIRICAL_RATE_LAW.** The species-specific neutral channel is kinetically meaningful,
but the observed network includes acid-base and iodine-speciation coupling.

### Known intermediates

HOI/OI-, H2O2/HO2-, I-, I2, and possibly oxygen-transfer intermediates not resolved by
the macroscopic study.

### Rate-law assessment

Second-order mass action is supported for isolated HOI + H2O2. The complete apparent
law must include acid-base fractions and iodine feedback.

### Compatibility assessment

**REQUIRES_CORRECTION.** The modern constant cannot be inserted silently into strongly
acidic, unbuffered BR because Ag+, buffers, pH, and iodine suppression differ.

### Quantum-chemistry usefulness

**NOT_NEEDED** for the main parameter. Experiment is available; theory may only help
resolve a specific microscopic ambiguity.

### Final modeling decision

**KEEP_AS_EFFECTIVE_STEP** after an acidic, unbuffered compatibility validation.

## Answer to Q1: can the subsystem reactions be combined?

Not yet as a common predictive physical-chemistry network. They can be combined as the
explicitly historical Level 0 regression model. Direct combination for Level 1 fails
because the source studies span different acids, ionic strengths, buffers, scavengers,
protonation conventions, and pseudo-first-order reductions. R1, R3, R5, R7, R8, R9,
and R10 have documented condition or speciation dependencies. R2, R4, and R6 lack
directly transferable measurements. The audited-effective manifest therefore remains
non-runnable until subsystem validation closes these gaps.

## Answer to Q2: elementary-status table

| DKE step | Classification | Modeling decision |
|---|---|---|
| R1 | PSEUDOELEMENTARY | REPLACE_WITH_MICROSTEPS |
| R2 | PSEUDOELEMENTARY | REQUIRES_MORE_DATA |
| R3 | EQUILIBRIUM_REPRESENTATION | REPLACE_WITH_MICROSTEPS |
| R4 | UNKNOWN | REQUIRES_MORE_DATA |
| R5 | PSEUDOELEMENTARY | KEEP_AS_EFFECTIVE_STEP after subsystem validation |
| R6 | PSEUDOELEMENTARY | REQUIRES_MORE_DATA |
| R7 | PSEUDOELEMENTARY | REQUIRES_MORE_DATA |
| R8 | PROBABLY_ELEMENTARY | KEEP_AS_EFFECTIVE_STEP with HO2/O2- speciation |
| R9 | EMPIRICAL_RATE_LAW | REPLACE_WITH_MICROSTEPS |
| R10 | EMPIRICAL_RATE_LAW | KEEP_AS_EFFECTIVE_STEP after compatibility validation |

## Unresolved questions controlling the next gate

1. What Dushman microkinetic representation remains identifiable over the full BR
   iodide and acid trajectory without double-counting HIO2/HOI steps?
2. What aqueous Mn(II)/Mn(III) coordination set is required in sulfuric-acid versus
   perchloric-acid BR recipes?
3. What iodine hydrolysis constants share a consistent activity and standard-state
   convention with I2 + I- <-> I3-?
4. Can R5 subsystem data be reproduced without scavenger-induced distortion?
5. Which enolization and I2/I3- iodination terms are identifiable from independent
   malonic-acid subsystem data?

# Evidence-based quantum calculation queue

No ORCA calculation has been launched. Every item below is a microscopic question derived after
the subsystem audit. Net DKE equations are not transition-state targets.

## Q1_CRITICAL — R4 protonated-iodous-acid/iodate radical-pair formation

- **Microscopic step:** O-protonated `[H2IO2]+ + IO3− -> 2 IO2• + H2O`, compared with an
  HIO3/HIO2 encounter complex and an O-I adduct/homolysis route.
- **Question:** Which protonation/adduct topology can form the IO2 radical pair in water, and is
  the controlling process conventional bond rearrangement, ET, or water-assisted PCET?
- **Why experiment is insufficient:** the historical forward constant was optimized and the
  reverse value came from bromine analogy; no iodine-specific elementary kinetics were found.
- **Structures/states:** `[H2IO2]+` (O-protonation isomer ensemble, closed-shell singlet), IO3−
  (closed-shell singlet), neutral IO2 radicals (each doublet), and H2O. Total charge is zero.
  The product radical pair needs both open-shell singlet and triplet coupling; broken-symmetry
  stability and spin contamination must be checked.
- **Solvation/relativity:** cluster-continuum water with at least the first proton-relay shell
  (screen 4-8 explicit waters), aqueous standard-state correction, and iodine scalar-relativistic
  treatment (ZORA/DKH or a validated relativistic ECP). Compare spin-orbit single-point effects.
- **Calculation type/output:** conformer and protonation thermochemistry first; then radical
  reaction/ET/PCET surfaces, possible crossing, `delta G`, `delta G dagger` if a TS exists, and
  an uncertainty band. Expected uncertainty is at least 5-10 kcal/mol until solvation and spin
  sensitivity converge.

## Q1_CRITICAL — R2 iodine-specific proton-assisted disproportionation

- **Microscopic step:** `[H2IO2]+ + I− -> 2 HOI`, with explicit waters providing any required
  proton relay; compare contact and solvent-separated ion pairs.
- **Question:** Can this iodine-specific path support the very fast DKE effective flux, and what
  concentration/activity dependence follows from pre-equilibrium protonation?
- **Why experiment is insufficient:** DKE used a bromine analogue and no later direct iodine-
  specific elementary rate was located.
- **Structures/states:** O-protonated `[H2IO2]+`, I−, and two HOI molecules; all closed-shell
  singlets, total charge zero. Protonation isomers must be enumerated before the TS search.
- **Solvation/relativity:** 4-8 explicit waters plus continuum water, one-molar standard states,
  scalar-relativistic iodine treatment, and diffusion/ion-pair correction.
- **Calculation type/output:** conventional TS if a single surface is found, otherwise solvent-
  assisted reaction-path ensemble; report `delta G`, `delta G dagger`, predicted second/third-
  order law, and at least 3-5 kcal/mol methodological uncertainty.

## Q1_CRITICAL but BLOCKED — R6 manganese oxidation by IO2 radical

- **Microscopic step:** candidate aqua form
  `[MnII(H2O)6]2+ + IO2• -> [MnIII(H2O)5(OH)]2+ + HIO2`, compared with sulfato complexes.
- **Question:** Is the process outer-sphere ET followed by PT, inner-sphere ET, or concerted PCET?
- **Why experiment is insufficient:** R6 was selected using analogy/model performance, while the
  reference mixture contains enough sulfate for ion pairing and the dominant coordination states
  have not been measured.
- **Structures/states:** high-spin MnII aqua is sextet and IO2 is doublet, giving quintet/septet
  entrance manifolds; high-spin MnIII hydroxo is expected to require a quintet product surface.
  Sulfato alternatives and coordination numbers remain undefined. Charge is +2 for the written
  aqua/hydroxo candidate.
- **Solvation/relativity:** explicit first-shell waters and possible sulfate, outer solvent, spin-
  state and broken-symmetry checks. Iodine needs scalar relativity; Mn needs basis/functional
  benchmarking against aqueous redox data.
- **Calculation type/output:** ET/PCET free energies, redox potentials, inner/outer-sphere
  reorganization energies, and crossing analysis. Expected uncertainty exceeds 10 kcal/mol while
  coordination is unknown.
- **Blocker:** measure or otherwise constrain mixed-solution proton activity and MnII/MnIII aqua,
  hydroxo, and sulfato distributions. No molecular ORCA input should be written before this.

## Excluded from the queue

R1, R3, R5, R8, R9, and R10 have experimental subsystem evidence that should be transcribed,
condition-corrected, or measured at the reference condition before theory is used. Quantum
chemistry may later validate individual microsteps, but it is not currently the limiting evidence.
R7 is part of an experimentally observed multi-channel peroxide network and is blocked with R6
by the same manganese-speciation problem.

## Exact next ORCA calculation

The first permissible small calculation is a **microhydrated protonation/conformer screen for
HIO2 and `[H2IO2]+`**, shared by R2 and R4: optimize and frequency-check all chemically distinct
O-protonation structures with 4, 6, and 8 explicit waters in a water continuum, followed by a
scalar-relativistic correlated single-point benchmark. This establishes reactant identity and
thermal corrections; it is not a production barrier calculation. No ORCA work should start until
the explicit-water ensemble, iodine relativistic method, and standard-state convention are fixed
in an input protocol.

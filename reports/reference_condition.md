# Phase 2 reference Briggs-Rauscher condition

## Selection

The reference is the 22 °C experiment in the 2026 open-access time-resolved Raman study,
DOI [10.1039/D6AY00742B](https://doi.org/10.1039/D6AY00742B). It was selected because it
observes iodate, hydrogen peroxide, a manganese-sulfate signal, triiodide, and pentaiodide
in the same reacting mixture at 0.5 s Raman cadence, with synchronized 30 fps video.
Those species-resolved observations are more useful for auditing mechanism topology than
another color-only integrated trace.

The reference is kept separate from the historical trace used in Gate 1. It is not a fitting
target and it is not a replacement for the digitized 1982 experiment.

## Nominal final recipe

Equal 200 mL volumes of the three stocks give a 600 mL mixture. The resulting analytical
totals are 0.066667 M iodate, 0.015 M formal sulfuric acid, 0.050 M malonic acid,
0.006667 M total manganese sulfate, 1.026667 M hydrogen peroxide, and 0.133333 g/L
starch. These are dilution calculations from the reported stock recipes, not activities or
free-species concentrations.

The article reports stock-A pH 1.3 ± 0.1 and stock-C pH 2.5 ± 0.1. Neither value defines
the proton activity after mixing. Initial free iodide and the rapid iodine and manganese
speciation immediately after mixing were not numerically reported.

## What can be tested

- The occurrence and ordering of iodate/peroxide depletion and polyiodide oscillations.
- Whether an expanded iodine network can produce distinct I3− and I5− observables.
- Whether manganese-sulfate speciation is represented at the reported sulfate loading.
- Temperature trends across the reported 5, 13, 17, 22, 29, and 43 °C series once the
  numerical traces are available.

## What cannot yet be tested

The paper presents FFT results graphically, and no machine-readable numerical period table
or raw Raman time series was located. A numerical 22 °C period is therefore deliberately
left null in `experiments/reference_br.yaml`. Extracting a value visually would add an
uncontrolled digitization error and still would not supply the species amplitudes needed for
a strong validation.

The DKE model also has no starch-binding, I3−, or I5− species. Running it at this recipe would
compare unlike observables and would hide fast acid, iodine, and manganese speciation inside
nominal initial concentrations. The reference condition is consequently
`REFERENCE_ONLY_NOT_SIMULATION_READY`.

## Experimental-data blocker

The next decisive experimental artifact is the numerical Raman time series with wavelength-
resolved peak assignments, or a table of the extracted periods and amplitudes for the 22 °C
run. A mixed-solution proton activity measurement and an explicit sulfate mass balance would
also remove two major condition-transfer ambiguities.

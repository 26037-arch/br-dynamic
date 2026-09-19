# Malonic-acid iodination: R9

The DKE law `40[I2][MA]/(1 + 1e4[I2])` is an empirical subsystem fit. It combines slow
keto-enol conversion, fast iodine capture, iodine speciation, and product formation in one
flux. Its saturation coefficient is not an equilibrium constant.

Independent work supports two explicit alternatives. Eberlin and Williams found first-order
dependence on iodine and malonic acid, acid independence over 0.02–0.16 M H+, an enol
fraction `7.4e-9`, and enolization near `4.0e-3 s−1`; iodine capture was diffusion limited
([1996 study](https://doi.org/10.1039/P29960000883)). Leopold and Haim resolved I2 and I3−
routes involving enol and protonated enol and reported five kinetic coefficients plus an
enolization law ([1977 study](https://doi.org/10.1002/kin.550090108)).

The 2026 reference directly observes polyiodides and contains starch, so an I2-only R9 law
cannot map uniquely to its signals. The candidate file preserves three model families: DKE
as control, a minimal keto/enol plus I2 model, and a polyiodide model. Missing capture rates
and exact equation-to-parameter mappings remain null rather than inferred.

**Decision:** R9 is a major structural uncertainty. Use the polyiodide topology after an
equation-level source transcription; do not tune `k9` or `C9` against the integrated BR trace.

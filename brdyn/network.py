from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping
import warnings

import numpy as np


ALLOWED_CONFIDENCE = {
    "MEASURED_DIRECT", "MEASURED_DERIVED", "GLOBAL_FIT", "SUBSYSTEM_FIT",
    "LITERATURE_ESTIMATE", "ASSUMED", "QUANTUM_CALCULATED", "UNKNOWN",
}


class MechanismError(ValueError):
    pass


@dataclass(frozen=True)
class Flux:
    id: str
    reaction_id: str
    direction: str
    stoichiometry: Mapping[str, float]
    rate_law: Mapping[str, Any]
    parameter: Mapping[str, Any]


class Mechanism:
    def __init__(self, raw: Mapping[str, Any], source: Path | None = None):
        self.raw = raw
        self.source = source
        self.species = raw["species"]
        self.species_index = {s["id"]: i for i, s in enumerate(self.species)}
        if len(self.species_index) != len(self.species):
            raise MechanismError("Duplicate species id")
        self.dynamic_ids = [s["id"] for s in self.species if s.get("dynamic", True)]
        self.dynamic_index = {s: i for i, s in enumerate(self.dynamic_ids)}
        self.reservoirs = raw.get("reservoirs", {})
        self.fluxes = self._compile_fluxes()
        self.S = self._build_stoichiometric_matrix()

    def _compile_fluxes(self) -> list[Flux]:
        result: list[Flux] = []
        for reaction in self.raw["reactions"]:
            if not reaction.get("enabled", True):
                continue
            rid = reaction["id"]
            stoich = reaction["stoichiometry"]
            unknown = set(stoich) - set(self.species_index)
            if unknown:
                raise MechanismError(f"{rid}: unknown species {sorted(unknown)}")
            result.append(self._make_flux(rid, "forward", stoich, reaction["forward"]))
            reverse = reaction.get("reverse")
            if reverse:
                result.append(self._make_flux(
                    rid, "reverse", {k: -v for k, v in stoich.items()}, reverse
                ))
        return result

    def _make_flux(self, rid: str, direction: str, stoich: Mapping[str, float],
                   definition: Mapping[str, Any]) -> Flux:
        parameter = definition["parameter"]
        confidence = parameter.get("confidence", "UNKNOWN")
        if confidence not in ALLOWED_CONFIDENCE:
            raise MechanismError(f"{rid}: invalid confidence {confidence}")
        if not parameter.get("source"):
            warnings.warn(f"{rid} {direction}: parameter has no provenance", RuntimeWarning)
        if confidence in {"ASSUMED", "UNKNOWN"}:
            warnings.warn(f"{rid} {direction}: {confidence} parameter is active", RuntimeWarning)
        return Flux(f"{rid}_{direction}", rid, direction, stoich,
                    definition["rate_law"], parameter)

    def _build_stoichiometric_matrix(self) -> np.ndarray:
        matrix = np.zeros((len(self.dynamic_ids), len(self.fluxes)))
        for j, flux in enumerate(self.fluxes):
            for species, coefficient in flux.stoichiometry.items():
                if species in self.dynamic_index:
                    matrix[self.dynamic_index[species], j] = coefficient
        return matrix

    def concentration_map(self, y: np.ndarray) -> dict[str, float]:
        if len(y) != len(self.dynamic_ids):
            raise MechanismError("State-vector length does not match dynamic species")
        values = {name: float(y[i]) for name, i in self.dynamic_index.items()}
        values.update({k: float(v) for k, v in self.reservoirs.items()})
        return values

    def directional_rates(self, y: np.ndarray) -> np.ndarray:
        c = self.concentration_map(y)
        rates = []
        for flux in self.fluxes:
            law = flux.rate_law
            k = float(flux.parameter["value"])
            kind = law["type"]
            rate = k
            for species, order in law.get("orders", {}).items():
                rate *= c[species] ** float(order)
            if kind == "saturating_mass_action":
                denominator = 1.0
                for term in law["denominator"]:
                    denominator += float(term["coefficient"]) * c[term["species"]] ** float(term.get("order", 1))
                rate /= denominator
            elif kind != "mass_action":
                raise MechanismError(f"Unsupported rate law: {kind}")
            rates.append(rate)
        return np.asarray(rates)

    def rhs(self, _t: float, y: np.ndarray) -> np.ndarray:
        return self.S @ self.directional_rates(y)

    def jacobian(self, t: float, y: np.ndarray) -> np.ndarray:
        """Finite-difference Jacobian of the compiled RHS; no hand-written ODE terms."""
        y = np.asarray(y, dtype=float)
        jac = np.empty((len(y), len(y)))
        eps = np.sqrt(np.finfo(float).eps)
        for j in range(len(y)):
            step = eps * max(1.0, abs(y[j]))
            upper, lower = y.copy(), y.copy()
            upper[j] += step
            lower[j] -= step
            jac[:, j] = (self.rhs(t, upper) - self.rhs(t, lower)) / (2 * step)
        return jac

    def provenance_errors(self) -> list[str]:
        errors = []
        for flux in self.fluxes:
            p = flux.parameter
            for field in ("name", "value", "units", "confidence", "source"):
                if field not in p or p[field] in (None, ""):
                    errors.append(f"{flux.id}: missing parameter {field}")
        return errors

    def unit_errors(self) -> list[str]:
        """Check concentration-based elementary/effective rate-constant dimensions."""
        errors = []
        for flux in self.fluxes:
            order = sum(float(v) for v in flux.rate_law.get("orders", {}).values())
            exponent = int(round(1 - order))
            expected = "s^-1" if exponent == 0 else f"M^{exponent} s^-1"
            if flux.parameter["units"] != expected:
                errors.append(f"{flux.id}: {flux.parameter['units']} != {expected}")
        return errors

    def composition_matrix(self) -> tuple[list[str], np.ndarray]:
        elements = sorted({e for s in self.species for e in s.get("composition", {})})
        A = np.zeros((len(elements), len(self.species)))
        for j, species in enumerate(self.species):
            for element, count in species.get("composition", {}).items():
                A[elements.index(element), j] = count
        return elements, A

    def full_stoichiometric_matrix(self) -> np.ndarray:
        matrix = np.zeros((len(self.species), len(self.fluxes)))
        for j, flux in enumerate(self.fluxes):
            for species, coefficient in flux.stoichiometry.items():
                matrix[self.species_index[species], j] = coefficient
        return matrix

    def balance_errors(self) -> dict[str, dict[str, float]]:
        elements, A = self.composition_matrix()
        full_s = self.full_stoichiometric_matrix()
        elemental = A @ full_s
        charges = np.array([s["charge"] for s in self.species], dtype=float) @ full_s
        errors: dict[str, dict[str, float]] = {}
        for j, flux in enumerate(self.fluxes):
            item = {elements[i]: elemental[i, j] for i in range(len(elements)) if elemental[i, j] != 0}
            if charges[j] != 0:
                item["charge"] = charges[j]
            if item:
                errors[flux.id] = item
        return errors


def load_mechanism(path: str | Path) -> Mechanism:
    path = Path(path)
    # Files use JSON syntax, which is valid YAML 1.2, avoiding an undeclared YAML parser.
    raw = json.loads(path.read_text(encoding="utf-8"))
    return Mechanism(raw, path)

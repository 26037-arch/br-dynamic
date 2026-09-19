from __future__ import annotations

from copy import deepcopy

from .network import Mechanism


def active_parameter_names(mechanism: Mechanism) -> list[str]:
    names = [flux.parameter["name"] for flux in mechanism.fluxes]
    if any(flux.reaction_id == "R9" for flux in mechanism.fluxes):
        names.append("C9_DKE")
    return names


def scaled_parameter(mechanism: Mechanism, parameter_name: str, factor: float) -> Mechanism:
    if factor <= 0:
        raise ValueError("Multiplicative parameter factor must be positive")
    raw = deepcopy(mechanism.raw)
    matches = 0
    for reaction in raw["reactions"]:
        for direction in ("forward", "reverse"):
            definition = reaction.get(direction)
            if definition and definition["parameter"].get("name") == parameter_name:
                definition["parameter"]["value"] *= factor
                matches += 1
        if parameter_name == "C9_DKE" and reaction["id"] == "R9":
            terms = reaction["forward"]["rate_law"].get("denominator", [])
            if len(terms) != 1:
                raise ValueError("R9 saturation denominator is not uniquely defined")
            terms[0]["coefficient"] *= factor
            matches += 1
    if matches != 1:
        raise ValueError(f"Expected one match for {parameter_name}; found {matches}")
    return Mechanism(raw, mechanism.source)


def set_parameter_value(mechanism: Mechanism, parameter_name: str, value: float) -> Mechanism:
    if value <= 0:
        raise ValueError("Parameter value must be positive")
    raw = deepcopy(mechanism.raw)
    matches = 0
    for reaction in raw["reactions"]:
        for direction in ("forward", "reverse"):
            definition = reaction.get(direction)
            if definition and definition["parameter"].get("name") == parameter_name:
                definition["parameter"]["value"] = value
                matches += 1
        if parameter_name == "C9_DKE" and reaction["id"] == "R9":
            terms = reaction["forward"]["rate_law"].get("denominator", [])
            if len(terms) != 1:
                raise ValueError("R9 saturation denominator is not uniquely defined")
            terms[0]["coefficient"] = value
            matches += 1
    if matches != 1:
        raise ValueError(f"Expected one match for {parameter_name}; found {matches}")
    return Mechanism(raw, mechanism.source)

from __future__ import annotations

from dataclasses import dataclass, asdict

HARTREE_TO_KJ_MOL = 2625.4996394799
HARTREE_TO_KCAL_MOL = 627.5094740631


@dataclass(frozen=True)
class AntioxidantResult:
    bde: float
    ie: float
    ea: float
    pa: float
    unit: str


def _convert(value_eh: float, unit: str) -> float:
    normalized = unit.lower().replace(" ", "")
    if normalized in {"eh", "hartree", "hartrees"}:
        return value_eh
    if normalized in {"kj/mol", "kjmol-1", "kjmol"}:
        return value_eh * HARTREE_TO_KJ_MOL
    if normalized in {"kcal/mol", "kcalmol-1", "kcalmol"}:
        return value_eh * HARTREE_TO_KCAL_MOL
    raise ValueError(f"Unsupported unit: {unit}")


def antioxidant_descriptors(
    *,
    parent_h: float,
    radical_h: float,
    radical_cation_h: float,
    radical_anion_h: float,
    deprotonated_h: float,
    hydrogen_atom_h: float,
    electron_h: float = 0.0,
    proton_h: float = 0.00236,
    unit: str = "kJ/mol",
) -> dict[str, float | str]:
    """Calculate the paper's BDE, IE, EA, and PA conventions.

    All enthalpy arguments are in Hartree. The returned values are reaction
    enthalpies converted to ``unit``.
    """
    values = AntioxidantResult(
        bde=_convert(radical_h + hydrogen_atom_h - parent_h, unit),
        ie=_convert(radical_cation_h + electron_h - parent_h, unit),
        ea=_convert(parent_h + electron_h - radical_anion_h, unit),
        pa=_convert(deprotonated_h + proton_h - parent_h, unit),
        unit=unit,
    )
    return asdict(values)


def composite_enthalpy(
    *,
    high_level_sp: float,
    low_level_total_enthalpy: float,
    low_level_electronic_energy: float,
) -> float:
    """Combine high-level E with a low-level thermal enthalpy correction."""
    return high_level_sp + (low_level_total_enthalpy - low_level_electronic_energy)

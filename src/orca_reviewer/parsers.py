from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _text(source: str | Path) -> str:
    p = Path(source)
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else str(source)


def terminated_normally(source: str | Path) -> bool:
    return "ORCA TERMINATED NORMALLY" in _text(source)


def _last_float(patterns: list[str], text: str, label: str) -> float:
    matches: list[str] = []
    for pattern in patterns:
        matches.extend(re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE))
    if not matches:
        raise ValueError(f"Could not find {label} in ORCA output")
    value = matches[-1]
    if isinstance(value, tuple):
        value = value[-1]
    return float(str(value).replace("D", "E"))


def parse_final_energy(source: str | Path) -> float:
    return _last_float(
        [r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+(?:[DE][+-]?\d+)?)"],
        _text(source),
        "final single-point energy",
    )


def parse_total_enthalpy(source: str | Path) -> float:
    text = _text(source)
    return _last_float(
        [
            r"Total Enthalpy\s+\.\.\.\s+(-?\d+\.\d+(?:[DE][+-]?\d+)?)\s+Eh",
            r"Total enthalpy\s*[:=]\s*(-?\d+\.\d+(?:[DE][+-]?\d+)?)",
        ],
        text,
        "total enthalpy",
    )


def parse_frequencies(source: str | Path) -> list[float]:
    text = _text(source)
    values: list[float] = []
    for line in text.splitlines():
        match = re.match(r"\s*\d+\s*:\s*(-?\d+(?:\.\d+)?)\s*cm\*\*-1", line)
        if match:
            values.append(float(match.group(1)))
    return values


def parse_ir_spectrum(source: str | Path) -> list[dict[str, float]]:
    text = _text(source)
    rows: list[dict[str, float]] = []
    active = False
    for line in text.splitlines():
        if "IR SPECTRUM" in line.upper():
            active = True
            continue
        if active and ("RAMAN SPECTRUM" in line.upper() or "THERMOCHEMISTRY" in line.upper()):
            break
        if active:
            # Accept common tutorial-like columns: mode frequency ... intensity
            m = re.match(
                r"\s*(\d+)\s*:\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)",
                line,
            )
            if m:
                rows.append({
                    "mode": int(m.group(1)),
                    "frequency_cm-1": float(m.group(2)),
                    "intensity_km_mol": float(m.group(3)),
                })
    return rows


def parse_tddft_states(source: str | Path) -> list[dict[str, Any]]:
    text = _text(source)
    rows: list[dict[str, Any]] = []
    pattern = re.compile(
        r"STATE\s+(\d+)\s*:\s*E=\s*(-?\d+(?:\.\d+)?)\s+au\s+"
        r"(-?\d+(?:\.\d+)?)\s+eV\s+(-?\d+(?:\.\d+)?)\s+cm\*\*-1",
        re.IGNORECASE,
    )
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = pattern.search(line)
        if not m:
            continue
        state = int(m.group(1))
        energy_ev = float(m.group(3))
        wavelength = 1239.841984 / energy_ev if energy_ev > 0 else float("nan")
        f = None
        transitions: list[str] = []
        for j, nearby in enumerate(lines[i + 1 : i + 20], start=i + 1):
            if j > i + 1 and re.search(r"^\s*STATE\s+\d+\s*:", nearby, re.I):
                break
            fm = re.search(r"f\s*=\s*(\d+(?:\.\d+)?(?:[DE][+-]?\d+)?)", nearby, re.I)
            if fm:
                f = float(fm.group(1).replace("D", "E"))
            if re.search(r"\d+[ab]?\s*->\s*\d+[ab]?", nearby):
                transitions.append(nearby.strip())
        rows.append({
            "state": state,
            "energy_ev": energy_ev,
            "wavelength_nm": wavelength,
            "oscillator_strength": f,
            "transitions": transitions,
        })
    return rows

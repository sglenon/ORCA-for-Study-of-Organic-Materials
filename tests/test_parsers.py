from pathlib import Path
from orca_reviewer.parsers import (
    parse_final_energy, parse_total_enthalpy, parse_frequencies,
    parse_ir_spectrum, parse_tddft_states, terminated_normally,
)

DATA = Path(__file__).parents[1] / "sample_data"


def test_energy_and_termination():
    path = DATA / "sample_opt.out"
    assert terminated_normally(path)
    assert parse_final_energy(path) == -154.238745621


def test_frequency_and_enthalpy():
    path = DATA / "sample_freq.out"
    freqs = parse_frequencies(path)
    assert freqs[-1] == 3150.10
    assert parse_total_enthalpy(path) == -154.1732
    ir = parse_ir_spectrum(path)
    assert len(ir) == 6
    assert ir[3]["intensity_km_mol"] == 210.0


def test_tddft():
    states = parse_tddft_states(DATA / "sample_tddft.out")
    assert len(states) == 3
    assert states[1]["oscillator_strength"] == 0.18

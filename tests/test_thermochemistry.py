from orca_reviewer.thermochemistry import antioxidant_descriptors, composite_enthalpy


def test_antioxidant_descriptors():
    r = antioxidant_descriptors(
        parent_h=-500.0,
        radical_h=-499.36,
        radical_cation_h=-499.72,
        radical_anion_h=-500.08,
        deprotonated_h=-499.43,
        hydrogen_atom_h=-0.499,
        electron_h=0.0,
        proton_h=0.00236,
        unit="kJ/mol",
    )
    assert 369 < r["bde"] < 371
    assert 734 < r["ie"] < 736
    assert 209 < r["ea"] < 211
    assert 1502 < r["pa"] < 1504


def test_composite_enthalpy():
    assert composite_enthalpy(
        high_level_sp=-101.0,
        low_level_total_enthalpy=-99.9,
        low_level_electronic_energy=-100.0,
    ) == -100.9

from orca_reviewer.input_builder import OrcaInput


def test_scalar_directive_rendering():
    text = OrcaInput(
        method_line="PBE0 def2-SVP SP",
        charge=0, multiplicity=1,
        coordinates=["H 0 0 0", "H 0 0 0.74"],
        blocks={"maxcore": ["2000"], "pal": ["nprocs 2"]},
    ).render()
    assert "%maxcore 2000" in text
    assert "%maxcore\n" not in text
    assert "%pal\n  nprocs 2\nend" in text

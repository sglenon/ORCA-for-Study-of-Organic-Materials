# ORCA Reviewer: From First Input to Spectroscopic and Antioxidant Calculations

A GitHub-ready study repository for learning **ORCA 6.1** through reproducible quantum-chemistry workflows. It is written for chemistry students and researchers who want more than a list of keywords: each chapter connects the physical chemistry, the ORCA input, the output checks, and the limits of interpretation.

## What this repository covers

1. Installation, execution, folder hygiene, input syntax, charge, multiplicity, parallelism, and memory.
2. The theory needed to make defensible choices: Born–Oppenheimer approximation, potential-energy surfaces, Hartree–Fock, DFT, basis sets, dispersion, solvation, spin, SCF, TD-DFT, and thermochemistry.
3. Geometry optimization, conformer/spin-state screening, convergence checks, and minimum verification.
4. Frequency calculations, IR spectrum simulation, normal-mode assignment, scaling, and imaginary-frequency diagnosis.
5. UV–Vis calculations, TD-DFT/TDA, oscillator strengths, transition assignments, difference-density thinking, and natural transition orbitals.
6. Antioxidant thermochemistry for HAT, SET, and proton-loss pathways, translated into ORCA from Tabrizi, Dao, and Vu, *RSC Advances* **2019**, DOI: 10.1039/C8RA09763A.

The notebooks can run **without an ORCA binary**. In dry-run mode they generate input files and analyze bundled synthetic output snippets. When ORCA is installed, the same notebooks can launch calculations locally.

> ORCA itself is not distributed here. Download it from the official ORCA/FACCTs portal and follow its license terms.

## Repository map

```text
ORCA-Reviewer/
├── ORCA_REVIEWER.md                  # consolidated reviewer
├── docs/                             # modular chapters
├── notebooks/                        # executable tutorials
├── examples/                         # ORCA input templates
├── sample_data/                      # synthetic outputs for parser demos
├── src/orca_reviewer/                # small Python helper package
├── tests/                            # parser and thermochemistry tests
├── scripts/                          # shell and PowerShell launchers
├── pyproject.toml
├── environment.yml
├── requirements.txt
└── CITATION.cff
```

## Start here

### 1. Create a Python environment

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows PowerShell
python -m pip install -U pip
pip install -e .
```

Or with Conda/Mamba:

```bash
conda env create -f environment.yml
conda activate orca-reviewer
```

### 2. Open the notebooks

```bash
jupyter lab
```

Recommended order:

1. `01_setup_and_input_syntax.ipynb`
2. `02_geometry_optimization.ipynb`
3. `03_frequency_ir_assignments.ipynb`
4. `04_uvvis_transition_assignments.ipynb`
5. `05_antioxidant_thermochemistry.ipynb`
6. `06_end_to_end_project.ipynb`

### 3. Run tests

```bash
pytest -q
```

### 4. Point the notebooks to ORCA

Set `ORCA_EXE` to the full path of the ORCA executable:

```bash
export ORCA_EXE=/absolute/path/to/orca
```

PowerShell:

```powershell
$env:ORCA_EXE = "C:\absolute\path\to\orca.exe"
```

The full path is deliberately encouraged. It avoids a surprising number of PATH and MPI problems.

## Suggested learning path

| Stage | Goal | Deliverable |
|---|---|---|
| Foundation | Run a valid single-point calculation | Clean `.inp`, normal termination, final energy |
| Structure | Optimize and verify a minimum | `.xyz`, convergence table, no meaningful imaginary mode |
| IR | Simulate and assign vibrations | Broadened spectrum plus mode-assignment table |
| UV–Vis | Calculate and interpret excited states | Stick/broadened spectrum, NTO or MO-based assignments |
| Antioxidant | Compare HAT/SET/PL descriptors | Reproducible BDE, IE, EA, and PA table with state bookkeeping |
| Research | Test sensitivity and uncertainty | Method, basis, solvent, conformer, and spin-state comparison |

## Scientific guardrails

- A converged optimization is not automatically the correct conformer, spin state, protonation state, or global minimum.
- A frequency calculation validates the stationary point **at the same model chemistry and geometry**.
- Computed harmonic frequencies are not exact experimental band positions; assignments should use animated normal modes, not frequency ranges alone.
- TD-DFT state labels are model-dependent. “HOMO → LUMO” is often an oversimplification; inspect state composition and preferably NTOs.
- Antioxidant descriptors are reaction enthalpies. Every species must have a correct charge, multiplicity, geometry, thermal correction, and consistent standard state.
- Cross-method energy subtraction is usually invalid. Keep reaction components on the same energy convention unless a composite protocol is explicitly defined.

## Primary references

- FACCTs. **ORCA 6.1 Manual** and **ORCA 6.1 Tutorials**. https://www.faccts.de/docs/orca/6.1/
- Tabrizi, L.; Dao, D. Q.; Vu, T. A. “Experimental and theoretical evaluation on the antioxidant activity of a copper(II) complex based on lidocaine and ibuprofen amide-phenanthroline agents.” *RSC Advances* **2019**, *9*, 3320–3335. https://doi.org/10.1039/C8RA09763A

See [`docs/references.md`](docs/references.md) for additional methodological references and citation guidance.

# Study Roadmap and Repository Conventions

## How to use this reviewer

Each workflow follows the same reasoning loop:

1. **Define the chemical question.** Is the target a geometry, a relative energy, a vibrational assignment, an excited state, or a reaction enthalpy?
2. **Define the chemical state.** Write the formula, charge, multiplicity, protonation state, conformer, coordination sphere, and solvent model before opening ORCA.
3. **Choose a model chemistry.** State the electronic-structure method, basis set, dispersion correction, relativistic treatment where needed, and solvation model.
4. **Run the least expensive calculation that can falsify a bad setup.** A quick preoptimization or single point catches broken geometries and wrong charge/spin choices before an expensive job.
5. **Check the output.** Search for normal termination, SCF convergence, geometry convergence, warnings, imaginary modes, spin contamination, and suspicious orbitals.
6. **Convert output into evidence.** A number without provenance is not a result. Record the exact input, ORCA version, geometry source, state definition, and extraction script.
7. **Test sensitivity.** At minimum, ask whether a different conformer, multiplicity, solvent, basis set, or functional changes the conclusion.

## Folder convention for a real project

```text
project/
├── 00_structures/               # source XYZ/SDF/CIF files
├── 01_preopt/                   # cheap geometry cleanup
├── 02_opt/                      # production optimizations
├── 03_freq/                     # Hessians and thermochemistry
├── 04_sp/                       # higher-level single points
├── 05_tddft/                    # excited states and spectra
├── 06_antioxidant/              # neutral/radical/ion state tree
├── analysis/                    # notebooks and generated tables
├── figures/                     # publication-ready plots
└── manifest.csv                 # state bookkeeping
```

Do not overwrite a successful calculation. Use immutable run folders such as:

```text
02_opt/ligand_neutral_conf03_singlet_pbe0_def2tzvp_smdmeCN/
```

## Naming convention

A useful filename carries chemistry and method information without becoming a paragraph:

```text
<species>__q<charge>__m<multiplicity>__<job>__<method>.inp
```

Examples:

```text
ligand__q0__m1__optfreq__pbe0-d4-def2tzvp.inp
ligand_radical__q0__m2__optfreq__pbe0-d4-def2tzvp.inp
cu_complex__q2__m2__tddft__cam-b3lyp-def2tzvp.inp
```

## Minimum calculation record

For each reported value, save:

- ORCA version and platform
- input file and final geometry
- charge and multiplicity
- method, basis, auxiliary basis if relevant
- dispersion and solvation settings
- number of cores and `%maxcore`
- convergence thresholds
- final electronic energy
- zero-point, thermal enthalpy, and Gibbs corrections when used
- frequency status and lowest non-translational mode
- spin expectation value for unrestricted calculations
- parser version or manual extraction notes

## Completion checklist

A tutorial is complete only when you can:

- predict what the input should do before running it;
- locate the result and convergence evidence in the output;
- explain the approximation behind the result;
- identify at least two failure modes;
- reproduce the number from saved files.

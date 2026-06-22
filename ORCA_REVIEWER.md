# ORCA Reviewer — Consolidated Edition

> Single-file reading version. The modular chapters and executable notebooks remain the primary repository structure.


---

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


---

# 1. Setup, Execution, and ORCA Input Syntax

## 1.1 What ORCA is

ORCA is a general-purpose quantum-chemistry package with strong coverage of DFT, wavefunction methods, spectroscopy, transition metals, open-shell systems, and local-correlation approaches. This reviewer targets ORCA 6.1 syntax. Older installations may differ in available methods, defaults, and utility-program behavior.

## 1.2 Installation model

ORCA is downloaded separately after registration. The distribution is normally unpacked rather than installed by a package manager. Keep the complete ORCA directory intact because the main executable calls companion programs in the same directory.

Recommended practice:

1. Download the build that matches the operating system and CPU architecture.
2. Extract it into a stable path without spaces if possible.
3. Add the ORCA directory to `PATH`, or set `ORCA_EXE` to its full executable path.
4. Install the MPI version required by that ORCA build. ORCA 6 documentation recommends OpenMPI 4.1.6 for relevant Linux builds; use the version packaged or specified for your exact download.
5. Test a serial calculation before attempting parallel work.

Linux/macOS shell example:

```bash
export ORCA_DIR="$HOME/apps/orca_6_1_1"
export PATH="$ORCA_DIR:$PATH"
export LD_LIBRARY_PATH="$ORCA_DIR:$LD_LIBRARY_PATH"   # Linux, when required
export ORCA_EXE="$ORCA_DIR/orca"
```

PowerShell example:

```powershell
$env:ORCA_DIR = "C:\Programs\ORCA_6_1_1"
$env:Path = "$env:ORCA_DIR;$env:Path"
$env:ORCA_EXE = "$env:ORCA_DIR\orca.exe"
```

### Why the full executable path matters

ORCA launches helper binaries and, for parallel jobs, MPI processes. Calling the full path reduces ambiguity when multiple ORCA or MPI versions are present. Do not manually wrap a normal ORCA calculation in `mpirun`; request parallelism inside the input using `PALn` or `%pal`.

## 1.3 First calculation

`water.inp`:

```text
! HF def2-SVP TightSCF

%pal
  nprocs 1
end

* xyz 0 1
O      0.000000     0.000000     0.000000
H      0.758602     0.000000     0.504284
H     -0.758602     0.000000     0.504284
*
```

Run:

```bash
/path/to/orca water.inp > water.out
```

Check:

```bash
grep "FINAL SINGLE POINT ENERGY" water.out
grep "ORCA TERMINATED NORMALLY" water.out
```

A shell return to the prompt does not prove success. The normal-termination line and absence of fatal errors are the evidence.

## 1.4 Anatomy of an input file

ORCA inputs have three main layers.

### Simple keyword line

```text
! PBE0 D4 def2-TZVP TightSCF Opt Freq
```

The exclamation line selects common settings. Keyword order usually does not change meaning, but grouping method, basis, approximations, and job type makes the input readable.

### Detailed blocks

```text
%scf
  MaxIter 300
end

%geom
  MaxIter 200
  TolEnergy 5.0e-6
end
```

Blocks expose detailed controls. They end with `end`. A missing `end` can cause errors far from the actual mistake.

### Coordinates

Inline Cartesian coordinates:

```text
* xyz 0 1
C   0.0000  0.0000  0.0000
O   1.2000  0.0000  0.0000
H  -0.6000  0.9000  0.0000
H  -0.6000 -0.9000  0.0000
*
```

The two integers are **total molecular charge** and **spin multiplicity**, where multiplicity is `2S + 1`.

External XYZ file:

```text
* xyzfile 0 1 structure.xyz
```

Coordinates are normally in ångström. ORCA keywords are generally case-insensitive, but filenames and operating-system paths may not be.

## 1.5 Charge and multiplicity

This is the highest-impact input decision.

| Species | Typical charge | Typical multiplicity |
|---|---:|---:|
| closed-shell neutral organic molecule | 0 | 1 |
| neutral radical after H-atom removal | 0 | 2 |
| radical cation after one-electron oxidation | +1 | 2 |
| radical anion after one-electron reduction | -1 | 2 |
| deprotonated closed-shell anion | -1 | 1 |
| Cu(II), one unpaired electron, isolated complex | depends on ligands | 2 |

These are starting expectations, not universal laws. Metal complexes can have multiple low-lying spin states and broken-symmetry solutions. Count electrons explicitly and screen chemically plausible multiplicities.

## 1.6 Methods, basis sets, and job keywords

A readable simple line can be parsed as:

```text
! [electronic method] [dispersion] [basis] [SCF controls] [job] [solvation]
```

Examples:

```text
! r2SCAN-3c TightSCF Opt
! PBE0 D4 def2-TZVP TightSCF TightOpt Opt Freq
! CAM-B3LYP def2-TZVP TightSCF CPCM(Acetonitrile)
```

Common job keywords:

- `SP`: single-point energy
- `Opt`: geometry optimization
- `Freq`: analytic harmonic frequency calculation where available
- `NumFreq`: numerical Hessian
- `Engrad`: energy and gradient

The method and basis define the model chemistry. `Opt` and `Freq` define what to do with that model.

## 1.7 Parallelism and memory

Simple parallel request:

```text
! PAL8
```

Equivalent detailed form:

```text
%pal
  nprocs 8
end
```

Memory is approximately per process/core:

```text
%maxcore 3000
```

This requests roughly 3000 MB per process. With eight processes, the potential allocation is around 24 GB plus program overhead. A sensible starting rule is to keep `nprocs × maxcore` below roughly 75–80% of physical RAM.

Example for a 32 GB workstation:

```text
%pal nprocs 8 end
%maxcore 3000
```

More cores do not guarantee faster calculations. Small molecules can slow down from MPI overhead. Memory-bound post-HF and large TD-DFT jobs may need fewer cores with more memory per process.

## 1.8 Comments, variables, and input hygiene

Comments can be added with `#` in many contexts:

```text
! PBE0 D4 def2-TZVP Opt  # production geometry
```

Prefer a short metadata header:

```text
# Species: ligand neutral, conformer 03
# Charge/multiplicity: 0 1
# Purpose: production optimization before frequency calculation
# Geometry source: CREST conformer search, rank 3
```

Do not store several abandoned keyword lines in the same input. Git already preserves history.

## 1.9 Restart and scratch discipline

ORCA creates `.gbw`, `.xyz`, Hessian, property, and temporary files. Run each job in its own directory. For a restart, copy the relevant `.gbw` and use an explicit restart strategy rather than mixing files from unrelated methods.

A typical orbital-read input is:

```text
! PBE0 D4 def2-TZVP TightSCF MOREAD SP
%moinp "previous.gbw"
* xyzfile 0 1 final.xyz
```

Only reuse orbitals when the basis, charge, multiplicity, and orbital space are compatible. A mismatched restart can be worse than a fresh guess.

## 1.10 Common setup failures

### `orca: command not found`

Use the full path or fix `PATH`.

### MPI initialization or shared-library error

The ORCA build and MPI runtime are incompatible, or `PATH`/`LD_LIBRARY_PATH` points to another MPI installation. Verify the exact MPI version required by the downloaded build.

### Input parser error near a block

Inspect the preceding block for a missing `end`, an unmatched coordinate terminator, or a malformed filename.

### Calculation exits without normal termination

Read the last 50–100 lines. Common causes are insufficient memory/disk, SCF failure, bad geometry, incompatible keywords, or interrupted MPI processes.

### SCF does not converge

Before adding increasingly aggressive controls, inspect the structure, charge, multiplicity, and initial guess. Then consider `SlowConv`, more iterations, level shifting, damping, or a staged method/basis approach.

## 1.11 A production-ready template

```text
# Replace all bracketed fields
! [METHOD] [DISPERSION] [BASIS] TightSCF [JOB] [SOLVATION] PAL8

%maxcore 3000

%scf
  MaxIter 300
end

%geom
  MaxIter 200
end

%output
  PrintLevel Normal
end

* xyzfile [CHARGE] [MULTIPLICITY] structure.xyz
```

## Review questions

1. Why is `%maxcore 4000` not “4 GB total” in an eight-core calculation?
2. What physical information is encoded by multiplicity?
3. Why should parallel ORCA normally be launched through the ORCA executable rather than a manual `mpirun` command?
4. What three output checks distinguish a successful job from one that merely stopped?
5. When is `xyzfile` preferable to inline coordinates?


---

# 2. Theory for Practical ORCA Work

This chapter is deliberately selective. The goal is to understand which approximation controls which error, so method choices are explainable rather than ceremonial.

## 2.1 From nuclei and electrons to a potential-energy surface

The nonrelativistic molecular Hamiltonian contains electronic and nuclear kinetic energies plus electron–nucleus, electron–electron, and nucleus–nucleus interactions. Solving the full time-independent Schrödinger equation is impractical for ordinary molecules.

The **Born–Oppenheimer approximation** treats nuclei as fixed while solving the electronic problem. Repeating the electronic calculation at many nuclear geometries defines a potential-energy surface (PES):

\[
E_\mathrm{BO}(\mathbf R) = E_\mathrm{electronic}(\mathbf R) + V_\mathrm{NN}(\mathbf R)
\]

Geometry optimization searches for a stationary point on this surface. Frequencies probe its local curvature. A UV–Vis calculation evaluates excited electronic states, often vertically at one ground-state geometry.

## 2.2 Stationary points and the Hessian

At a stationary point, the gradient is zero:

\[
\frac{\partial E}{\partial R_i} = 0
\]

The Hessian is the matrix of second derivatives:

\[
H_{ij}=\frac{\partial^2E}{\partial R_i\partial R_j}
\]

After mass weighting and diagonalization, its eigenvalues yield harmonic vibrational frequencies.

- All meaningful vibrational eigenvalues positive: local minimum.
- Exactly one negative eigenvalue: first-order saddle point, usually a transition-state candidate.
- More than one: higher-order saddle point or poor convergence.

A minimum is local. The PES may contain lower conformers, tautomers, coordination isomers, or spin states.

## 2.3 Hartree–Fock in one page

Hartree–Fock approximates the many-electron wavefunction with one Slater determinant. Electrons move in an average field generated by the others. The variational procedure gives self-consistent molecular orbitals.

Strengths:

- exact exchange within the single determinant;
- a clean starting point for post-HF methods;
- no self-interaction in the one-electron sense.

Limitations:

- misses dynamical electron correlation;
- can fail badly for bond breaking and multireference systems;
- orbital energies and unoccupied orbitals are not direct observables.

The SCF cycle iterates density → Fock/Kohn–Sham matrix → orbitals → new density until a convergence threshold is met.

## 2.4 Density functional theory

Kohn–Sham DFT replaces the interacting-electron problem with noninteracting orbitals that reproduce the electron density. The unknown exchange–correlation functional is approximated.

A rough ladder:

- LDA: local density
- GGA: density plus gradient
- meta-GGA: adds kinetic-energy density or Laplacian information
- hybrid: mixes exact exchange
- range-separated hybrid: treats short- and long-range exchange differently
- double hybrid: adds perturbative correlation

No functional is universally best. Geometry, thermochemistry, transition-metal spin states, charge transfer, and excitation energies stress different parts of the approximation.

### Practical functional roles

- **r2SCAN-3c**: efficient composite method for preoptimization and many ground-state structures.
- **PBE0-D4 / B3LYP-D4**: common general-purpose hybrid starting points.
- **CAM-B3LYP or ωB97X-family approaches**: often useful for excited states with significant charge-transfer character.
- **Domain-specific validation**: required for transition-metal spin-state energetics and redox chemistry.

These are workflow starting points, not rankings.

## 2.5 Dispersion

Semilocal and many hybrid functionals do not fully capture long-range London dispersion. An empirical or charge-dependent correction such as D3 or D4 can change conformer order, intermolecular geometry, and ligand folding.

A geometry may look “chemically reasonable” while missing an intramolecular π-stacking or dispersion-stabilized conformation. Include dispersion consistently when it is part of the chosen model.

## 2.6 Basis sets

A basis set expands molecular orbitals in atom-centered functions. Larger and more flexible bases reduce basis incompleteness but increase cost.

### Size language

- split valence / double-ζ: economical geometry and screening
- triple-ζ: stronger production default for energies and properties
- polarization functions: permit angular distortion during bonding
- diffuse functions: important for anions, Rydberg states, weak binding, and extended electron density

The def2 family is widely used in ORCA:

- `def2-SVP`: economical double-ζ
- `def2-TZVP`: balanced triple-ζ
- `def2-TZVPP`: additional polarization

### Effective core potentials and relativistic effects

For heavier atoms, an ECP replaces core electrons and incorporates approximate scalar-relativistic effects. All-electron relativistic treatments such as ZORA or DKH are alternatives. The choice must be consistent with the basis set.

LANL2DZ, used in the antioxidant paper, combines valence bases and Hay–Wadt ECPs for relevant heavier atoms. It remains useful for reproducing older protocols, but modern studies should test whether a larger, more balanced basis changes the result.

## 2.7 Resolution-of-the-identity and RIJCOSX

Auxiliary-basis approximations reduce the cost of Coulomb and exchange terms. In ORCA, RI and RIJCOSX are central performance tools. Modern ORCA versions often select suitable auxiliary bases automatically for common basis families. Treat approximation settings as part of the model and report them when they affect reproducibility.

## 2.8 Implicit solvation

Continuum models represent the solvent as a polarizable dielectric surrounding a molecular cavity. They capture bulk electrostatics but not specific hydrogen bonds, ligand exchange, ion pairing, or solvent coordination.

Common ORCA forms include:

```text
! CPCM(Water)
! SMD(Acetonitrile)
```

Solvation can alter:

- conformer and protonation-state stability;
- redox and ionization energies;
- charge-transfer excitation energies;
- antioxidant descriptors involving ions.

For reactions that change charge, gas-phase and solution-phase rankings can differ dramatically. Use the same solvent convention for every species in a thermochemical cycle.

## 2.9 Open-shell systems and spin

An unrestricted calculation allows α and β orbitals to differ. This is often necessary for radicals and transition metals, but the determinant may not be a pure spin eigenfunction.

Inspect the reported \(\langle S^2\rangle\):

| Multiplicity | Ideal S | Ideal ⟨S²⟩ |
|---:|---:|---:|
| 1 | 0 | 0.00 |
| 2 | 1/2 | 0.75 |
| 3 | 1 | 2.00 |
| 4 | 3/2 | 3.75 |

Moderate deviations can be expected in some systems; large deviations indicate spin contamination, near-degeneracy, or an unsuitable single-determinant description.

For metal complexes:

1. enumerate chemically plausible multiplicities;
2. optimize each from more than one initial guess when necessary;
3. compare energies only at consistent levels;
4. inspect spin density and orbital occupations;
5. consider broken-symmetry or multireference treatment where indicated.

## 2.10 Geometry optimization algorithms

An optimizer builds a local model of the PES from energies, gradients, and an approximate Hessian. It proposes a step, evaluates the new geometry, and updates the curvature model.

Convergence commonly checks:

- energy change;
- maximum and RMS gradient;
- maximum and RMS step.

A noisy SCF produces noisy gradients. Tightening geometry thresholds while leaving the SCF loose can create apparent nonconvergence.

## 2.11 Harmonic frequencies and IR intensity

The harmonic approximation expands the PES to second order around a stationary point. Frequencies are obtained from the mass-weighted Hessian. IR intensity depends on the change in dipole moment along a normal coordinate:

\[
I_k \propto \left|\frac{\partial \boldsymbol\mu}{\partial Q_k}\right|^2
\]

Why computed bands differ from experiment:

- anharmonicity;
- finite temperature and conformational averaging;
- solvent/solid-state environment;
- imperfect electronic structure and basis;
- experimental band overlap and broadening.

A scale factor may improve systematic harmonic errors, but it should be selected for the method/basis and spectral region, not invented to force agreement.

## 2.12 Excited states, TD-DFT, and TDA

Linear-response TD-DFT obtains excitation energies and transition properties from the response of the ground-state density to a time-dependent perturbation. The Tamm–Dancoff approximation (TDA) simplifies the response equations and often improves numerical stability, particularly around triplet instabilities.

An electronic absorption spectrum is assembled from vertical transitions:

- excitation energy \(\Delta E\);
- wavelength \(\lambda = hc/\Delta E\);
- oscillator strength \(f\), a measure of transition probability.

A vertical excitation assumes nuclei do not move during the electronic transition, consistent with the Franck–Condon picture.

### Assignment language

Avoid assigning a state solely as “HOMO → LUMO.” A state is a linear combination of orbital transitions. Better evidence includes:

- dominant configuration weights;
- the character and localization of contributing orbitals;
- NTO hole and particle orbitals;
- difference density;
- spin and symmetry selection rules;
- sensitivity to functional and solvent.

For metal complexes, useful qualitative classes include ligand-centered (LC), metal-centered (MC or d–d), ligand-to-metal charge transfer (LMCT), metal-to-ligand charge transfer (MLCT), and ligand-to-ligand charge transfer (LLCT).

## 2.13 Thermochemistry from frequencies

ORCA combines the electronic energy with zero-point and thermal terms under ideal-gas, rigid-rotor, and harmonic-oscillator approximations. At temperature \(T\):

\[
H = E_\mathrm{elec} + E_\mathrm{ZPE} + \Delta H_\mathrm{trans} + \Delta H_\mathrm{rot} + \Delta H_\mathrm{vib} + RT
\]

A frequency output can provide thermal enthalpy and Gibbs free energy. Low-frequency modes make entropy especially fragile; ORCA’s thermochemistry tools include quasi-RRHO treatment, but the chosen convention must be reported.

## 2.14 Error budget

Think of a computed result as:

\[
\text{result} = \text{chemical model} + \text{electronic model} + \text{nuclear model} + \text{numerical settings}
\]

Examples of chemical-model errors:

- wrong protonation or tautomer;
- omitted counterion or coordinated solvent;
- wrong conformer or spin state.

Examples of electronic-model errors:

- functional bias;
- basis incompleteness;
- missing multireference character;
- inadequate solvation.

Numerical errors include loose SCF convergence, grid sensitivity, and incomplete geometry convergence. A highly precise number can still answer the wrong chemical question.

## Review questions

1. Why can an optimization converge to a structure with an imaginary frequency?
2. Which antioxidant descriptors are most sensitive to solvation, and why?
3. Why is a diffuse basis especially relevant for a radical anion?
4. What does an NTO add beyond an orbital-transition list?
5. Why can a local minimum be chemically irrelevant even when all frequencies are positive?


---

# 3. Geometry Optimization

## 3.1 Objective

A geometry optimization searches for a stationary point of the chosen model chemistry. The output geometry is therefore not “the molecular structure” in an absolute sense. It is a structure conditioned on charge, multiplicity, conformer, method, basis, dispersion, solvent, and constraints.

## 3.2 Recommended staged workflow

### Stage A: construct and clean the structure

Build in Avogadro, ChimeraX/SEQCROW, a cheminformatics toolkit, or from experimental coordinates. Check:

- atom connectivity and bond orders;
- protonation and tautomer;
- stereochemistry;
- coordination number and ligand denticity;
- obvious atomic clashes;
- total charge and electron count.

A molecular-mechanics cleanup is useful, but do not let a force field silently change metal coordination.

### Stage B: conformer and state generation

For flexible ligands, one hand-built conformer is not enough. Use a conformer search method such as CREST/GFN-xTB, systematic torsion sampling, or chemically guided variants. For metal complexes, generate plausible coordination geometries and spin states.

### Stage C: inexpensive preoptimization

```text
! r2SCAN-3c TightSCF Opt PAL8
%maxcore 2500
* xyzfile 0 1 starting.xyz
```

This catches broken starting structures and reduces the cost of a larger-basis optimization.

### Stage D: production optimization

Organic ligand example:

```text
! PBE0 D4 def2-TZVP TightSCF TightOpt Opt SMD(Acetonitrile) PAL8
%maxcore 3000
%scf MaxIter 300 end
%geom MaxIter 250 end
* xyzfile 0 1 preopt.xyz
```

Cu(II) complex template:

```text
! PBE0 D4 def2-TZVP TightSCF TightOpt Opt SMD(Water) PAL8
%maxcore 3000
%scf
  MaxIter 400
end
%geom
  MaxIter 300
end
* xyzfile 2 2 cu_complex_start.xyz
```

The charge and doublet multiplicity are illustrative. Recalculate them for the actual ligand charges and metal oxidation state.

### Stage E: frequency validation

Run `Freq` at the optimized geometry and the same model chemistry. Combining `Opt Freq` is convenient:

```text
! PBE0 D4 def2-TZVP TightSCF TightOpt Opt Freq SMD(Acetonitrile) PAL8
```

For expensive systems, separating optimization and frequency jobs simplifies restarts. Preserve the final geometry and `.gbw` file.

## 3.3 Reading optimization output

### SCF convergence

Every geometry step requires an electronic solution. Look for repeated SCF failures, oscillation, or unusually large iteration counts.

### Geometry convergence table

ORCA reports criteria such as energy change, RMS gradient, maximum gradient, RMS step, and maximum step. A production structure should satisfy the required criteria, not merely reach `MaxIter`.

### Final geometry

ORCA writes a final XYZ file for a successful optimization. Verify that:

- no bond broke unexpectedly;
- expected coordination was retained;
- no atom crossed a steric barrier into an implausible arrangement;
- key bond lengths and angles are chemically sensible.

### Final energy

The final electronic energy is useful for comparing structures at the same method, basis, solvent, charge, and multiplicity. It is not directly comparable across different compositions or arbitrary model chemistries.

## 3.4 Constrained optimizations

Constraints can test mechanistic hypotheses or preserve coordinates during a staged setup. Conceptual example:

```text
%geom
  Constraints
    { B 0 1 C }
    { A 1 0 2 120.0 C }
  end
end
```

A constraint changes the stationary-point problem. The resulting structure is not an unconstrained minimum and may retain nonzero forces along frozen coordinates. Report every constraint.

## 3.5 Difficult optimizations

### Poor starting geometry

Symptoms: enormous energy, SCF failure, atoms flying apart. Fix the structure or use a cheap preoptimization.

### Flat torsions and floppy ligands

Symptoms: tiny steps, alternating conformations, very low frequencies. Tighten SCF, use a better initial Hessian, change internal-coordinate settings, or optimize multiple conformers.

### Metal coordination rearrangement

The optimizer may reveal that the proposed structure is unstable, but it may also exploit a model deficiency. Compare solvent, spin state, functional, and starting geometry before declaring a new coordination motif.

### SCF root switching

Abrupt changes in spin density or orbital occupations can make the PES discontinuous. Track orbital populations and restart from a physically appropriate `.gbw` when justified.

### Optimization converges but frequency has a small imaginary mode

Animate it. If it is a meaningful torsion, reoptimize along the displacement with tighter settings. If it is a very small rotational/translational numerical artifact, document the magnitude and test tighter optimization/grid settings rather than deleting it from the record.

## 3.6 Conformer ranking

For conformers of the same species:

1. optimize each consistently;
2. verify each minimum;
3. compare electronic energies and, where appropriate, thermal Gibbs energies;
4. consider solution-phase free energies and low-frequency entropy uncertainty;
5. compute Boltzmann populations only when the energy model is defensible.

\[
p_i = \frac{e^{-\Delta G_i/RT}}{\sum_j e^{-\Delta G_j/RT}}
\]

Small errors of 1–2 kcal mol⁻¹ can alter populations substantially. Report a population range when several structures are close.

## 3.7 Spin-state screening for transition metals

A defensible screen includes:

- plausible multiplicities from electron count and ligand field;
- multiple starting geometries or orbital guesses;
- optimized energy at each state;
- frequency or stability checks for low-lying candidates;
- \(\langle S^2\rangle\), spin density, and orbital occupations;
- sensitivity to functional and solvation.

Do not optimize only one multiplicity and call it the ground state.

## 3.8 Geometry metrics for reporting

Useful metrics include:

- donor–metal distances;
- chelate bite angles;
- dihedral angles governing conjugation;
- planarity metrics;
- hydrogen-bond distances;
- RMSD between free and coordinated ligand;
- coordination-geometry descriptors.

A table of selected parameters is usually more interpretable than dumping all Cartesian coordinates, though the full coordinates should remain available in the repository or supporting information.

## 3.9 Reproducibility checklist

- [ ] starting geometry retained
- [ ] charge/multiplicity justified
- [ ] conformers/spin states screened
- [ ] exact input committed
- [ ] normal termination recorded
- [ ] all convergence criteria passed
- [ ] final geometry inspected
- [ ] frequency calculation verifies the stationary point
- [ ] method sensitivity considered
- [ ] coordinates supplied with reported results

## Exercises

1. Generate three ethanol conformers, preoptimize at r2SCAN-3c, and compare PBE0-D4/def2-TZVP energies.
2. Intentionally rotate a carbonyl into a steric clash. Compare SCF and optimization behavior before and after preoptimization.
3. Optimize a model Cu(II) complex as at least two multiplicities. Compare energy, geometry, \(\langle S^2\rangle\), and spin density.
4. Add a dihedral constraint, optimize, release the constraint, and explain how the final structure changes.


---

# 4. Frequency Calculations, IR Spectra, and Assignments

## 4.1 What a frequency calculation answers

At an optimized geometry, a harmonic frequency calculation provides:

- local curvature and stationary-point classification;
- normal-mode frequencies and displacement vectors;
- IR intensities;
- zero-point energy;
- temperature-dependent thermal corrections and thermochemistry;
- a Hessian that can improve subsequent optimization or transition-state work.

It does not automatically provide anharmonic bands, overtone intensities, solvent dynamics, crystal packing, or conformational averaging.

## 4.2 Input patterns

Optimization and frequency together:

```text
! PBE0 D4 def2-TZVP TightSCF TightOpt Opt Freq SMD(Acetonitrile) PAL8
%maxcore 3000
* xyzfile 0 1 ligand_start.xyz
```

Frequency from an existing geometry:

```text
! PBE0 D4 def2-TZVP TightSCF Freq SMD(Acetonitrile) PAL8
%maxcore 3000
* xyzfile 0 1 ligand_opt.xyz
```

Numerical Hessian when analytic second derivatives are unavailable:

```text
! [METHOD] [BASIS] TightSCF NumFreq
```

A numerical frequency job requires many displaced-gradient calculations and can be expensive. Parallelism helps, but disk and restart planning matter.

## 4.3 Same-level rule

Stationary-point validation should use the same model chemistry as the geometry. A PBE0-D4/def2-TZVP frequency on a geometry optimized at a different level does not strictly classify the stationary point of either PES unless the geometry is reoptimized or the limitation is acknowledged.

Composite thermochemistry can combine a higher-level single-point electronic energy with lower-level thermal corrections:

\[
H_\mathrm{comp} = E_\mathrm{high,SP} + \left(H_\mathrm{low,freq} - E_\mathrm{low,elec}\right)
\]

That is a defined approximation, not a same-level frequency validation.

## 4.4 Number of modes

A molecule with \(N\) atoms has:

- \(3N-6\) vibrational modes if nonlinear;
- \(3N-5\) if linear.

The remaining coordinates correspond to overall translation and rotation and should appear near zero. Numerical projection is imperfect, so tiny residual values are normal.

## 4.5 Interpreting imaginary frequencies

ORCA may print an imaginary mode as a negative frequency.

### For a minimum

No chemically meaningful imaginary mode should remain.

### For a transition state

Exactly one imaginary mode should correspond to the desired reaction coordinate.

### Diagnosis workflow

1. Animate the mode.
2. Determine whether it is internal motion or whole-molecule drift.
3. If internal, displace the geometry in both directions and reoptimize.
4. Tighten optimization and SCF thresholds.
5. Increase integration-grid quality where appropriate.
6. Check whether a constraint, symmetry assumption, or wrong conformer caused the saddle point.

Never erase a negative sign in a table and call the structure a minimum.

## 4.6 IR spectrum simulation

The raw output is a stick spectrum: frequency and intensity. A visually comparable spectrum is made by broadening each line, often with a Gaussian or Lorentzian:

\[
I(\tilde\nu) = \sum_i I_i\exp\left[-\frac{(\tilde\nu-\tilde\nu_i)^2}{2\sigma^2}\right]
\]

The broadening width is a plotting choice, not a physical prediction unless supported by a line-shape model.

### Scaling

A harmonic scale factor can be applied:

\[
\tilde\nu_\mathrm{scaled}=s\tilde\nu_\mathrm{harmonic}
\]

Use a published factor matched to the method/basis and, ideally, the spectral region. Record the unscaled and scaled frequencies.

## 4.7 Assignment procedure

A good assignment combines frequency, intensity, mode animation, isotope/coordination trends, and experimental context.

For each relevant band:

1. identify calculated modes in the experimental region;
2. animate each normal mode;
3. describe the dominant internal coordinates;
4. note mixed motion rather than forcing a pure label;
5. compare free ligand and complex;
6. account for scaling and experimental environment.

Recommended labels:

- `ν`: stretching
- `δ`: in-plane bending/deformation
- `γ`: out-of-plane bending
- `ρ`: rocking
- `ω`: wagging
- `τ`: twisting/torsion

Example assignment table:

| Experimental / cm⁻¹ | Calculated scaled / cm⁻¹ | Intensity | Assignment | Evidence |
|---:|---:|---:|---|---|
| 1648 | 1661 | strong | mainly ν(C=O), coordinated amide | animation; red shift from free ligand |
| 3356 broad | 3430 | medium | O–H stretches of coordinated water | broad experimental envelope; mixed H-bonding |

## 4.8 Coordination-induced shifts

Metal coordination can shift ligand bands by changing bond order and electron density. A carbonyl red shift may support O coordination, but assignment should not rely on one band alone. Compare:

- free-ligand and complex calculations at consistent levels;
- normal-mode compositions;
- structural bond-length changes;
- multiple experimental bands;
- alternative coordination modes.

## 4.9 Low-frequency modes and thermochemistry

Modes below roughly 50–100 cm⁻¹ often represent hindered rotations, intermolecular motions, or floppy coordinates. Treating them as ideal harmonic oscillators can produce exaggerated entropy. ORCA supports quasi-RRHO-style thermochemical handling. Report the temperature, pressure/standard-state convention, and low-frequency treatment.

For antioxidant **enthalpies**, low-frequency entropy is less central than for Gibbs energies, but thermal vibrational contributions and geometry/state consistency still matter.

## 4.10 Isotope and mode localization tools

Assignments can be strengthened by:

- isotopic substitution calculations;
- partial Hessian vibrational analysis for large systems;
- internal-coordinate decomposition;
- visual comparison of displacement vectors;
- frequency shifts across a homologous series.

A normal mode is collective. “The C=O stretch” usually means the mode has dominant C=O stretching character, not that only those two atoms move.

## 4.11 Quality-control checklist

- [ ] geometry converged at the same level
- [ ] correct charge and multiplicity
- [ ] normal termination
- [ ] expected number of modes
- [ ] no meaningful imaginary frequency for a minimum
- [ ] low modes inspected
- [ ] scale factor cited or explicitly omitted
- [ ] mode animations used for assignments
- [ ] broadened spectrum labeled as simulated
- [ ] experimental phase/solvent considered

## Exercises

1. Calculate water frequencies and identify symmetric stretch, bend, and antisymmetric stretch.
2. Compare acetone and protonated acetone carbonyl modes.
3. Simulate a spectrum with 5, 10, and 20 cm⁻¹ broadening and explain which visual conclusions are robust.
4. Create an assignment table for a free ligand and its metal complex, including at least one mixed mode.


---

# 5. UV–Vis Calculations and Transition Assignments

## 5.1 Workflow overview

A defensible absorption calculation is not just a TD-DFT input. It includes:

1. ground-state geometry and state definition;
2. model chemistry and solvent suitable for the chromophore;
3. enough roots to cover the experimental range;
4. output checks and spectrum construction;
5. state assignment using configurations, orbitals, NTOs, and density changes;
6. sensitivity testing.

## 5.2 Ground-state geometry

Use a verified minimum at an appropriate solvent model. UV–Vis experiments are often in solution; a gas-phase geometry and excitation calculation can miss solvent-dependent conformations and charge-transfer energetics.

For flexible molecules, compute spectra for thermally populated conformers and average their oscillator-strength distributions when needed.

## 5.3 TD-DFT/TDA input

Organic chromophore template:

```text
! CAM-B3LYP def2-TZVP TightSCF SMD(Acetonitrile) PAL8
%maxcore 3000

%tddft
  nroots 30
  tda true
  donto true
  maxdim 100
end

* xyzfile 0 1 ligand_opt.xyz
```

Cu(II) complex template:

```text
! CAM-B3LYP def2-TZVP TightSCF SMD(DMSO) PAL8
%maxcore 3000

%tddft
  nroots 50
  tda true
  donto true
end

* xyzfile 2 2 complex_opt.xyz
```

The number of roots must be chosen from the target energy range, not a habit. A 200–800 nm experimental window corresponds approximately to 6.20–1.55 eV.

## 5.4 Choosing the functional

Excitation errors depend on state character.

- Local valence π→π* states may be described reasonably by several hybrids.
- Long-range charge-transfer states are often underestimated by conventional global hybrids.
- Rydberg states need diffuse basis functions.
- d–d and strongly multiconfigurational metal-centered states can be difficult for routine TD-DFT.

Use a range-separated hybrid as a strong starting point when charge transfer is possible, then benchmark against experiment or a higher-level method on a smaller model.

## 5.5 Basis set and diffuse functions

`def2-TZVP` is a practical starting point. Add diffuse functions when the excited electron is spatially extended, the system is anionic, or Rydberg character is expected. Test basis sensitivity for the lowest important transitions rather than assuming the largest affordable basis is automatically adequate.

## 5.6 Solvent treatment

Continuum solvent affects excitation energies through ground- and excited-state polarization. ORCA’s default TD-DFT continuum treatment and nonequilibrium options should be chosen with the physical timescale in mind. Record the solvent and response convention.

Specific coordination or strong hydrogen bonding may require explicit solvent molecules plus a continuum environment.

## 5.7 Reading the excited-state output

A typical state record contains:

- state number;
- excitation energy in eV and/or cm⁻¹;
- wavelength in nm;
- oscillator strength;
- dominant orbital transitions and amplitudes/weights.

A state with near-zero oscillator strength is “dark” in the electric-dipole approximation but may still matter through vibronic coupling, symmetry breaking, spin–orbit coupling, or experimental broadening.

## 5.8 Spectrum construction

A calculated spectrum is a broadened collection of vertical transitions. ORCA provides `orca_mapspc`; this repository also includes Python broadening functions.

Example utility command from the ORCA tutorial style:

```bash
orca_mapspc calculation.out ABS -eV -n400 -w0.5
```

The exact options can vary with ORCA version; consult the utility help in your installation.

Wavelength and energy are nonlinearly related:

\[
\lambda(\mathrm{nm}) = \frac{1239.841984}{E(\mathrm{eV})}
\]

Broaden uniformly in energy when comparing electronic transitions, then transform carefully if plotting in wavelength. Uniform broadening in nm distorts high-energy and low-energy regions differently.

## 5.9 Transition assignments

### Step 1: screen by intensity and spectral region

Identify states contributing to each experimental band envelope. A broad band may contain several transitions.

### Step 2: inspect configuration weights

List all material contributions, not only the largest one. Avoid interpreting orbital coefficients as literal probabilities without checking the output convention.

### Step 3: inspect orbitals

Classify occupied and virtual orbitals by localization and character:

- ligand π / π*;
- heteroatom lone pair;
- metal d;
- σ / σ*;
- diffuse/Rydberg.

Be careful with orbital numbering. ORCA and visualization software may use zero-based versus one-based labels.

### Step 4: use NTOs

Natural transition orbitals compress a complicated excitation into paired “hole” and “particle” orbitals. For a dominant NTO pair:

- hole on metal, particle on ligand → MLCT-like;
- hole on ligand, particle on metal → LMCT-like;
- both on same ligand → ligand-centered;
- different ligands → LLCT-like.

NTO input:

```text
%tddft
  nroots 30
  donto true
end
```

Visualize the generated NTO files with ORCA plotting utilities or compatible molecular viewers.

### Step 5: inspect spin and density change

For open-shell systems, α and β channels may differ. Difference-density plots can reveal charge redistribution more directly than frontier-orbital labels.

### Step 6: assign conservatively

Example:

> Band A is dominated by states 4–7. Their leading NTOs show hole density on the phenanthroline π system and particle density on the same ligand, so the envelope is assigned primarily as ligand-centered π→π*, with a smaller metal-mixing contribution.

This is stronger than “HOMO–LUMO transition.”

## 5.10 Metal-complex cautions

Cu(II) complexes can display weak d–d transitions, charge-transfer bands, spin contamination, and Jahn–Teller distortion. Routine TD-DFT may:

- place d–d states inaccurately;
- mix state characters strongly;
- miss spin-forbidden intensity mechanisms;
- depend sensitively on geometry and functional.

Compare experimental intensity and energy patterns, inspect multiple states, and avoid overassigning a broad visible band to a single configuration.

## 5.11 Systematic shifts

Computed spectra may show a consistent energy offset. The ORCA tutorial notes that shifts on the order of tenths of an eV are common. A systematic correction can be used when calibrated against an appropriate reference set, but report both raw and shifted results and do not fit a single unknown spectrum to itself.

## 5.12 Validation strategy

For important conclusions, test:

- two functionals with different exact-exchange/range behavior;
- basis set and diffuse-function sensitivity;
- solvent model;
- conformer averaging;
- TDA versus full TD-DFT where stable;
- a higher-level excited-state method on a reduced model, where feasible.

## 5.13 Reporting table

| State | Energy / eV | λ / nm | f | Dominant configurations | NTO character | Assignment |
|---:|---:|---:|---:|---|---|---|
| 1 | 2.10 | 590 | 0.002 | several d/d-like terms | metal-localized | weak MC/d–d candidate |
| 7 | 3.85 | 322 | 0.42 | mixed π→π* | ligand-localized | LC π→π* |

Include the exact geometry source and solvent in the caption.

## Exercises

1. Generate a 30-root TD-DFT input for a neutral ligand in acetonitrile.
2. Plot the same transitions with 0.1, 0.3, and 0.5 eV broadening.
3. Compare a conventional hybrid and a range-separated hybrid for a donor–acceptor dye.
4. Assign a simulated band using both canonical orbitals and NTOs. Explain which description is clearer.


---

# 6. Antioxidant Thermochemistry in ORCA

## 6.1 Source protocol and translation scope

This chapter is based on Tabrizi, Dao, and Vu, *RSC Advances* **2019**, 9, 3320–3335, DOI: 10.1039/C8RA09763A. The paper used Gaussian 09, M05-2X/LANL2DZ geometry and frequency calculations, and M05-2X/6-311++G(2df,2p) single points. It evaluated antioxidant pathways in gas phase and water using bond dissociation enthalpy (BDE), ionization energy (IE), electron affinity (EA), and proton affinity/deprotonation enthalpy (PA in the paper’s notation).

This repository translates the **thermochemical cycles and state bookkeeping** into ORCA. Exact numerical reproduction is not guaranteed because program implementations, grids, solvation models, functional availability, ECP/basis definitions, and thermal conventions can differ.

## 6.2 Mechanisms and descriptors

Let `Anti–H` be the parent antioxidant at a specific H-donor site.

### Hydrogen atom transfer (HAT)

\[
\mathrm{Anti-H \rightarrow Anti^{\bullet} + H^{\bullet}}
\]

\[
\mathrm{BDE}=H(\mathrm{Anti^{\bullet}})+H(\mathrm{H^{\bullet}})-H(\mathrm{Anti-H})
\]

Lower BDE generally means easier H-atom donation, all else equal.

### Single-electron transfer: oxidation

\[
\mathrm{Anti-H \rightarrow Anti-H^{\bullet+}+e^-}
\]

\[
\mathrm{IE}=H(\mathrm{Anti-H^{\bullet+}})+H(e^-)-H(\mathrm{Anti-H})
\]

Lower IE means easier electron donation.

### Single-electron transfer: reduction

\[
\mathrm{Anti-H+e^- \rightarrow Anti-H^{\bullet-}}
\]

The paper uses:

\[
\mathrm{EA}=H(\mathrm{Anti-H})+H(e^-)-H(\mathrm{Anti-H^{\bullet-}})
\]

With this sign convention, larger positive EA means more favorable electron acceptance.

### Proton loss

\[
\mathrm{Anti-H \rightarrow Anti^-+H^+}
\]

\[
\mathrm{PA}=H(\mathrm{Anti^-})+H(H^+)-H(\mathrm{Anti-H})
\]

Although labeled PA in the paper, this equation is the enthalpy of deprotonation/proton loss. Lower values mean easier deprotonation under the specified convention.

## 6.3 State table before calculations

For a closed-shell neutral antioxidant with one candidate X–H bond:

| State | Formula change | Charge | Typical multiplicity | Used in |
|---|---|---:|---:|---|
| parent | Anti–H | 0 | 1 | all descriptors |
| H-abstracted radical | Anti• | 0 | 2 | BDE |
| radical cation | Anti–H•+ | +1 | 2 | IE |
| radical anion | Anti–H•− | -1 | 2 | EA |
| deprotonated anion | Anti− | -1 | 1 | PA |
| H atom | H• | 0 | 2 | BDE |

For metal complexes, derive each multiplicity from the coupled metal and ligand spins. The “typical” column cannot be copied blindly.

## 6.4 Adiabatic versus vertical descriptors

The paper reports adiabatic quantities: each product state is geometry optimized and receives its own frequency calculation.

- **Adiabatic IE/EA:** relaxed product ion/radical geometry.
- **Vertical IE/EA:** product electronic energy at the parent geometry.

Adiabatic quantities describe thermodynamic state-to-state changes. Vertical quantities are closer to sudden electron removal/addition and spectroscopy. Do not mix them in one table without labels.

## 6.5 ORCA calculation tree

For every H-donor site, create:

```text
antioxidant/
├── parent_q0_m1/
├── radical_site01_q0_m2/
├── radical_cation_q+1_m2/
├── radical_anion_q-1_m2/
└── deprotonated_site01_q-1_m1/
```

A molecule with four X–H sites requires four radical and four deprotonated-state branches. The lowest BDE and PA site may differ.

## 6.6 Geometry and frequency template

Modern ORCA-oriented starting protocol:

```text
! PBE0 D4 def2-TZVP TightSCF TightOpt Opt Freq SMD(Water) PAL8
%maxcore 3000
%scf MaxIter 400 end
%geom MaxIter 300 end
* xyzfile [CHARGE] [MULTIPLICITY] structure.xyz
```

Paper-oriented ORCA 6.1 translation, optimization:

```text
! M052X LANL2DZ DEFGRID3 TightSCF TightOpt Opt PAL8
%maxcore 3000
%scf MaxIter 400 end
%geom MaxIter 300 end
* xyzfile [CHARGE] [MULTIPLICITY] structure.xyz
```

ORCA 6.1 exposes M05-2X through the `M052X` keyword using its LibXC interface. Minnesota functionals can be grid-sensitive, so `DEFGRID3` is made explicit. If an analytic Hessian is unavailable for this functional/build, run a numerical frequency job on the optimized geometry:

```text
! M052X LANL2DZ DEFGRID3 TightSCF NumFreq PAL8
%maxcore 3000
* xyzfile [CHARGE] [MULTIPLICITY] optimized.xyz
```

A practical translation of the paper's larger-basis single point for a Cu complex uses the Pople basis on elements it covers and retains LANL2DZ plus its ECP on Cu:

```text
! M052X 6-311++G(2df,2p) DEFGRID3 TightSCF SP PAL8
%maxcore 3000
%basis
  NewGTO Cu "LANL2DZ" end
  NewECP Cu "LANL2DZ" end
end
* xyzfile [CHARGE] [MULTIPLICITY] optimized.xyz
```

This mixed-basis input is an explicit ORCA interpretation of the paper's shorthand, not a guarantee of exact Gaussian reproduction. ORCA uses spherical d/f functions for built-in basis sets, while Pople bases were historically parameterized with Cartesian functions in common Gaussian workflows. Program implementation, grid, and thermal-convention differences must be documented.

For a new study, the safer scientific approach is to define and validate a modern ORCA protocol, then use the paper as the mechanistic and thermochemical source rather than promise bitwise reproduction.

## 6.7 Composite single-point protocol

The paper optimized/frequency-calculated at a lower basis and then used a larger-basis single point. A composite enthalpy can be written as:

\[
H_\mathrm{comp}=E_\mathrm{SP,high}+\left(H_\mathrm{freq,low}-E_\mathrm{elec,low}\right)
\]

The bracketed term is the thermal enthalpy correction from the lower-level frequency job. Apply the same construction to every molecular species in the reaction.

Do not add a high-level electronic energy to the total low-level enthalpy without subtracting the low-level electronic energy; that would count electronic energy twice.

## 6.8 Extracting enthalpy from ORCA

From each successful frequency output, record:

- final electronic energy;
- zero-point energy;
- thermal correction to enthalpy;
- total enthalpy at the selected temperature;
- lowest frequency and stationary-point status;
- \(\langle S^2\rangle\) for open-shell species.

The parser in `src/orca_reviewer/parsers.py` searches common ORCA labels, but always inspect a few outputs manually because formatting can differ by version and calculation type.

## 6.9 Constants and unit conversion

This repository uses:

\[
1\ E_h = 2625.4996394799\ \mathrm{kJ\ mol^{-1}}
\]

\[
1\ E_h = 627.5094740631\ \mathrm{kcal\ mol^{-1}}
\]

The paper uses a gas-phase proton enthalpy of `0.00236 Eh` at 298.15 K, corresponding to the ideal-gas translational enthalpy convention `5/2 RT`.

For water, the paper reports effective enthalpies:

- \(H(H^+) = -981.8\ \mathrm{kJ\ mol^{-1}}\)
- \(H(e^-) = -48.3\ \mathrm{kJ\ mol^{-1}}\)

These are convention-dependent reference values from the cited solvation approach. Do not combine them with a different absolute solvation convention without rebuilding the cycle.

## 6.10 Hydrogen atom and electron references

### Hydrogen atom

Calculate H• using the same electronic method/basis convention as the molecular species, unless a documented reference value is used consistently.

```text
! PBE0 def2-TZVP TightSCF SP
* xyz 0 2
H 0.0 0.0 0.0
*
```

The atom has no rotational or vibrational modes. The thermal enthalpy convention must match the molecular calculations.

### Electron

Absolute electron enthalpy is a thermochemical convention. In many gas-phase electronic cycles, the electron electronic energy is taken as zero and a thermal reference is applied as required. In solution, an absolute solvated-electron reference is model-dependent. State the convention explicitly.

## 6.11 Site-specific workflow

For each candidate donor site:

1. optimize the parent and verify a minimum;
2. delete the target H atom without changing the remaining atom order;
3. set charge and multiplicity for the radical;
4. optimize and verify the radical;
5. calculate BDE;
6. repeat deprotonation for PA;
7. optimize radical cation and radical anion for IE and EA;
8. inspect whether large structural rearrangement changes the chemical identity;
9. compare sites and states at one consistent convention.

If a product rearranges, record it. The adiabatic descriptor then belongs to the rearranged product basin, not necessarily a local bond-cleavage event.

## 6.12 Metal-complex considerations

Antioxidant calculations on metal complexes are much harder than on closed-shell organic molecules.

### Spin coupling

H abstraction or electron transfer can alter ligand radicals, metal oxidation state, and exchange coupling. Screen plausible multiplicities for each product state.

### Redox localization

Use spin density, orbital/NTO analysis, and population analysis to determine whether oxidation/reduction is metal- or ligand-centered. Formal oxidation-state labels alone may be misleading.

### Coordination sphere

Charged products may bind or release solvent/counterions. A fixed bare-complex continuum model may not represent the experimental species.

### Functional sensitivity

Transition-metal redox and spin-state energetics can vary strongly with functional. Test at least one alternative and report the spread.

## 6.13 Solution-phase cycles

A solution-phase reaction enthalpy can be built from gas-phase enthalpies plus solvation enthalpies:

\[
\Delta H_\mathrm{soln}=\Delta H_\mathrm{gas}+\sum H_\mathrm{solv}(\mathrm{products})-\sum H_\mathrm{solv}(\mathrm{reactants})
\]

Alternatively, use consistently solvated total enthalpies plus absolute ion references compatible with that model. The important requirement is a closed, internally consistent cycle.

Ions are especially sensitive to cavity definitions, explicit solvent, and standard-state conversions. Report uncertainty rather than presenting the last decimal as meaningful.

## 6.14 Interpreting the descriptors

The paper’s qualitative logic was:

- lower BDE → HAT more favorable;
- lower IE → oxidation/electron donation easier;
- higher EA under its sign convention → electron acceptance easier;
- lower PA/deprotonation enthalpy → proton loss easier.

These descriptors do not directly predict an assay rate. Radical scavenging also depends on reaction partners, kinetics, pH, diffusion, solvent, competing pathways, metal redox cycling, and concentration.

## 6.15 Reporting template

| Species/site | q | mult | H / Eh | BDE | IE | EA | PA | solvent | notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| parent | 0 | 1 | … | — | — | — | — | water | verified minimum |
| O-radical, site 1 | 0 | 2 | … | … | — | — | — | water | spin on O/aryl |

Include a separate state manifest so every number is traceable to an output file.

## 6.16 Common mistakes

- using electronic energies for one state and enthalpies for another;
- wrong multiplicity after H/electron/proton transfer;
- unverified imaginary frequencies;
- comparing differently solvated species;
- omitting conformer and spin-state search;
- using the paper’s solution proton/electron references with an incompatible solvation cycle;
- calling the paper’s PA equation a conventional gas-phase proton affinity without explaining the sign/reaction definition;
- mixing vertical and adiabatic values;
- reporting a single site when several X–H positions are plausible.

## 6.17 Research-grade sensitivity analysis

At minimum, test:

1. two functionals;
2. a larger basis or diffuse augmentation for anions;
3. gas versus water/experimental solvent;
4. relevant conformers;
5. relevant spin states;
6. vertical versus adiabatic IE/EA where mechanistically useful.

Report conclusions that survive these tests. Treat changes in rank order as a scientific result, not an inconvenience.

## Exercises

1. Use the notebook’s synthetic enthalpies to calculate BDE, IE, EA, and PA in kJ mol⁻¹.
2. Change the radical-anion enthalpy by 0.010 Eh. Quantify the EA shift.
3. Build state tables for phenol and a Cu(II) phenolate complex.
4. Demonstrate the double-counting error that occurs when a high-level single-point energy is added directly to the low-level total enthalpy.
5. Compare gas-phase and water-reference proton-loss values and explain the dominant source of the shift.


---

# 7. Special Notes for Ligands and Transition-Metal Complexes

## 7.1 Define the modeled species

Experimental labels such as “Cu–ligand complex” may correspond to several computational species:

- isolated cation without counterions;
- contact ion pair;
- explicitly solvated complex;
- hydrated or ligand-exchanged form;
- crystal structure with lattice solvent;
- solution-state coordination isomer.

Write a chemical equation for the modeled species. The computational formula should match the charge and atom list in the input.

## 7.2 Starting structures

Use experimental coordinates when available, but add missing hydrogens and correct disorder carefully. A crystal structure is not automatically the dominant solution conformer. Preserve key coordination motifs while testing solvent and ligand flexibility.

## 7.3 Spin-state and broken-symmetry logic

For one Cu(II) center, a doublet is a common starting point. For several open-shell centers or ligand radicals, multiple couplings exist. Broken-symmetry DFT may represent antiferromagnetic coupling, but the resulting determinant and energy require careful interpretation and, often, spin projection.

## 7.4 Basis and relativistic choices

For first-row transition metals, all-electron def2 basis sets are common. For heavier elements, use a matched ECP or scalar-relativistic Hamiltonian and basis. Do not combine an ECP with an incompatible all-electron basis by accident.

## 7.5 Integration grids and SCF stability

Metal complexes can be sensitive to numerical grids and SCF roots. Tighten grids and SCF convergence when relative energies are small. Check whether the converged determinant is stable and whether orbital occupations make chemical sense.

## 7.6 Spectroscopy

IR assignments should compare ligand and complex normal modes. UV–Vis assignments should distinguish weak metal-centered transitions from intense charge-transfer and ligand-centered bands. For open-shell systems, inspect spin-resolved orbitals and NTOs.

## 7.7 Minimal reporting bundle

For each low-lying structure/state, provide:

- Cartesian coordinates;
- total charge and multiplicity;
- electronic and thermal energies;
- key bond lengths/angles;
- lowest frequencies;
- \(\langle S^2\rangle\);
- spin-density visualization;
- UV–Vis transition table and NTO images where used;
- method-sensitivity comparison.


---

# 8. Troubleshooting and Quality Control

## A calculation triage sequence

When a job fails, diagnose in this order:

1. **File and executable:** correct path, readable input, enough disk space.
2. **Syntax:** balanced blocks, valid keywords, coordinate terminator.
3. **Chemical state:** atom list, charge, multiplicity, protonation, geometry.
4. **Electronic convergence:** SCF iterations, occupations, spin.
5. **Nuclear convergence:** optimizer behavior, constraints, Hessian.
6. **Resources:** memory per core, number of processes, scratch, wall time.
7. **Method limitations:** unsupported derivative, unstable state, multireference character.

## Symptom table

| Symptom | Likely causes | First actions |
|---|---|---|
| immediate parser stop | typo, missing `end`, bad filename | read first error and preceding block |
| SCF oscillates | wrong state, near-degeneracy, poor guess | verify q/m, inspect geometry, try staged guess/SlowConv |
| energy becomes nonsensical | atom clash, wrong units, bad coordinates | visualize input, preoptimize |
| optimizer hits max cycles | flat surface, poor Hessian, root switching | inspect trajectory, tighten SCF, restart from best geometry |
| one small imaginary mode | loose convergence, floppy torsion | animate, TightOpt/VeryTightOpt, displace and reoptimize |
| many imaginary modes | saddle point or failed optimization | return to geometry workflow |
| TD-DFT roots fail/converge oddly | too many roots, unstable reference, CT/Rydberg issues | check ground state, reduce roots, test TDA/basis/functional |
| memory crash | `%maxcore × nprocs` too high | reduce cores or maxcore |
| parallel launch error | wrong MPI/PATH | use required MPI and full ORCA path |

## Output audit commands

```bash
grep -n "ORCA TERMINATED NORMALLY" *.out
grep -n "FINAL SINGLE POINT ENERGY" *.out
grep -n "SCF NOT CONVERGED" *.out
grep -n "imaginary" *.out
grep -n "<S\*\*2>" *.out
```

Exact labels can vary. The Python parsers are conveniences, not replacements for reading the output.

## Research quality-control questions

- Does the conclusion depend on one conformer?
- Does the result change with multiplicity?
- Is an ion described without diffuse functions or solvent?
- Is an experimental solution species modeled as a bare gas-phase ion?
- Are calculated and experimental spectra compared at compatible phase and temperature?
- Are all thermochemical cycle members treated consistently?
- Does a “transition assignment” come from NTO/density evidence or only orbital labels?


---

# 9. ORCA Quick Reference

## Core input

```text
! METHOD DISPERSION BASIS TightSCF JOB SOLVATION PAL8
%maxcore 3000
* xyzfile CHARGE MULTIPLICITY structure.xyz
```

## Common jobs

```text
! r2SCAN-3c Opt
! PBE0 D4 def2-TZVP TightOpt Opt Freq
! CAM-B3LYP def2-TZVP SMD(Acetonitrile)
%tddft nroots 30 tda true donto true end
```

## Charge/multiplicity changes from closed-shell neutral parent

```text
parent              0 1
H-abstracted radical 0 2
radical cation      +1 2
radical anion       -1 2
deprotonated anion  -1 1
H atom               0 2
```

## Success checks

```text
ORCA TERMINATED NORMALLY
FINAL SINGLE POINT ENERGY
THE OPTIMIZATION HAS CONVERGED
VIBRATIONAL FREQUENCIES
```

## Conversions

```text
1 Eh = 2625.4996394799 kJ mol-1
1 Eh = 627.5094740631 kcal mol-1
lambda(nm) = 1239.841984 / E(eV)
```

## Antioxidant equations

```text
BDE = H(radical) + H(H atom) - H(parent)
IE  = H(radical cation) + H(electron) - H(parent)
EA  = H(parent) + H(electron) - H(radical anion)
PA  = H(deprotonated) + H(proton) - H(parent)
```

## Never skip

- charge and multiplicity justification
- normal termination
- stationary-point verification
- conformer/spin-state screening
- consistent solvent and thermochemical convention
- manual inspection of transition or vibration character


---

# References and Citation Guide

## ORCA

1. FACCTs GmbH. **ORCA 6.1 Manual**. https://www.faccts.de/docs/orca/6.1/manual/
2. FACCTs GmbH. **ORCA 6.1 Tutorials**. https://www.faccts.de/docs/orca/6.1/tutorials/
3. Cite the ORCA program and individual methods according to the “How to cite” section of the manual for the version and modules used.

## Antioxidant source article

Tabrizi, L.; Dao, D. Q.; Vu, T. A. Experimental and theoretical evaluation on the antioxidant activity of a copper(II) complex based on lidocaine and ibuprofen amide-phenanthroline agents. *RSC Advances* **2019**, *9*, 3320–3335. https://doi.org/10.1039/C8RA09763A

The paper is open access under CC BY 3.0. This repository paraphrases and operationalizes its thermochemical framework; it does not reproduce its figures or full text.

## Method references

When publishing results, cite the original references for:

- the selected density functional;
- D3/D4 dispersion correction;
- basis set and ECP family;
- CPCM/SMD solvation;
- RI/RIJCOSX approximations when appropriate;
- TD-DFT/TDA and NTO methodology;
- quasi-RRHO thermochemistry if used;
- external conformer-search tools.

## Reproducible citation sentence template

> Calculations were performed with ORCA [version]. Geometries were optimized using [functional/dispersion/basis/solvent] with [SCF and geometry thresholds], followed by harmonic frequency calculations at the same level to verify stationary points and obtain thermal corrections at [temperature]. Excitation energies were calculated using [TD-DFT/TDA method, roots, basis, solvent].

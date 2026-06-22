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

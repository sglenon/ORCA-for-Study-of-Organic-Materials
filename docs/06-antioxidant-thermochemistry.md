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

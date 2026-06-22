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

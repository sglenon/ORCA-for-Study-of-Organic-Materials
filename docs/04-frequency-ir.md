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

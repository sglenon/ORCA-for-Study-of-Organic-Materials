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

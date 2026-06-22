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

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

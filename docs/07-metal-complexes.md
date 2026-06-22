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

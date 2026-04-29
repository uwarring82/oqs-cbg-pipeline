"""
models.jaynes_cummings — Jaynes–Cummings model.

Solvable model used for Tier 2 (perturbative convergence) and as a
candidate venue for Tier 4 / DG-5 (thermodynamic discriminant against
competing gauges).

Structural constraints declared for DG-2:
    - basis-independence of K (universal default);
    - RWA-consistency of computed K_n;
    - block-diagonal structure preserved by JC dynamics.

Reference for exact TCL form: Smirne & Vacchini, PRA 82, 022110 (2010).
"""

structural_constraints = (
    "basis_independence",
    "rwa_consistency",
    "jc_block_diagonal",
)

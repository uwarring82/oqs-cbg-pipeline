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

Stub depth at v0.1.0:
    This module is *not* a DG-1 venue (DG-1 covers CL-2026-005 v0.4
    Entries 1, 3, 4, which use pure_dephasing and spin_boson_sigma_x).
    Function stubs (hamiltonian, coupling_operator, environment, etc.)
    are deliberately not yet present: pre-emptive API surface here
    would invite Sail v0.5 §10 Risk #6 (codebase before benchmark
    cards). Stubs land when this model's first benchmark card is
    drafted, which is no earlier than DG-2.
"""

structural_constraints = (
    "basis_independence",
    "rwa_consistency",
    "jc_block_diagonal",
)

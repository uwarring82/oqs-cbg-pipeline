"""
models.fano_anderson — Fano–Anderson model.

Natural venue for DG-5 (thermodynamic discriminant). Solvable; admits
a known K(t) under the minimal-dissipation gauge (Picatoste, Colla,
Breuer, PRR 6, 013258 (2024)) AND comparison with a competing
framework (e.g. Hamiltonian of mean force, polaron) to satisfy the
"distinguishable thermodynamic prediction" criterion of DG-5.

Structural constraints declared for DG-2:
    - basis-independence of K (universal default);
    - fermion-number conservation;
    - particle-hole symmetry where applicable.

DG-5 pass criterion (per Sail v0.5 §9):
    Identify at least one thermodynamic observable (work extraction,
    efficiency, heat current, work-heat partition) where the
    minimal-dissipation K(t) and the competing framework yield
    NUMERICALLY DISTINGUISHABLE predictions in the same model
    parameter regime. Side-by-side computation in a regime where
    the two predictions agree is NOT a DG-5 pass.

Stub depth at v0.1.0:
    This module is *not* a DG-1 venue (DG-1 covers CL-2026-005 v0.4
    Entries 1, 3, 4, which use pure_dephasing and spin_boson_sigma_x).
    Function stubs (hamiltonian, coupling_operator, environment, etc.)
    are deliberately not yet present: pre-emptive API surface here
    would invite Sail v0.5 §10 Risk #6 (codebase before benchmark
    cards). Stubs land when this model's first benchmark card is
    drafted, which is no earlier than DG-5 (with possible DG-2
    intermediate use for fermion-number-conservation checks).
"""

structural_constraints = (
    "basis_independence",
    "fermion_number_conservation",
    "particle_hole_symmetry",
)

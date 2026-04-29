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

DG-5 pass criterion (per Sail v0.4 §9):
    Identify at least one thermodynamic observable (work extraction,
    efficiency, heat current, work-heat partition) where the
    minimal-dissipation K(t) and the competing framework yield
    NUMERICALLY DISTINGUISHABLE predictions in the same model
    parameter regime. Side-by-side computation in a regime where
    the two predictions agree is NOT a DG-5 pass.
"""

structural_constraints = (
    "basis_independence",
    "fermion_number_conservation",
    "particle_hole_symmetry",
)

"""
models.pure_dephasing — Spin under pure dephasing, A = σ_z.

Reproduces CL-2026-005 v0.4 Entry 3:
    For H_S = (ω/2) σ_z and A = σ_z, K(t) = (ω_r(t)/2) σ_z; even-order
    contributions vanish; odd-order contributions are proportional to σ_z.

Structural constraints declared for DG-2:
    - basis-independence of K (universal default);
    - parity rule: K_2m = 0 (Letter App. D);
    - K_2m+1 ∝ σ_z;
    - for thermal bath (diagonal in Fock basis), all odd cumulants of B
      vanish, hence K(t) = (ω/2) σ_z (no renormalisation, recovers
      Łuczka 1990 / Doll 2008 / Leggett 1987).
"""

structural_constraints = (
    "basis_independence",
    "parity_rule_even_orders_vanish",
    "odd_orders_proportional_to_sigma_z",
)


def hamiltonian(omega: float):
    raise NotImplementedError("not implemented at v0.1.0 (pre-DG-1)")


def coupling_operator():
    raise NotImplementedError("not implemented at v0.1.0 (pre-DG-1)")

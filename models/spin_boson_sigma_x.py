"""
models.spin_boson_sigma_x — Unbiased spin-boson, A = σ_x, thermal bath.

Reproduces CL-2026-005 v0.4 Entry 4:
    For H_S = (ω/2) σ_z, A = σ_x, thermal bosonic bath:
    odd-order contributions to K vanish; even orders are diagonal in σ_z.
    Eigenbasis of H_S is NOT rotated by the interaction.

Structural constraints declared for DG-2:
    - basis-independence of K (universal default);
    - parity rule: K_2m+1 = 0 (Letter App. D);
    - K diagonal in σ_z basis at all orders.

Numerical anchor:
    Gatto, Colla, Breuer, Thoss, PRA 110, 032210 (2024) had reported
    numerical evidence; the present Letter provides the analytic proof.
"""

structural_constraints = (
    "basis_independence",
    "parity_rule_odd_orders_vanish",
    "K_diagonal_in_sigma_z",
)


def hamiltonian(omega: float, omegas, gs):
    raise NotImplementedError("not implemented at v0.1.0 (pre-DG-1)")

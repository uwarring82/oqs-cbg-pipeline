# SPDX-License-Identifier: MIT
"""
cbg.tcl_recursion — Recursive construction of the TCL generator L_t.

Implements the runner-facing low-order TCL terms used by the frozen
benchmark cards. The full Companion Eqs. (19)-(28) recursion yielding
L_t = Σ_n λ^n L_n in canonical generalised-Lindblad form at arbitrary
order remains pending.

The recursion uses the generalised cumulants D̄(τ_1^k, s_1^{n-k})
which are evaluated in cbg.cumulants (NOT a Nakajima-Zwanzig
memory kernel — TCL is time-local; see bath_correlations.py docstring).

Implemented runner-facing scope covers L_n at orders n in {0, 1, 2}
for thermal Gaussian baths, K_n_thermal_on_grid / K_total_thermal_on_grid,
and K_total_displaced_on_grid for the Council-cleared coherent-displaced
DG-2 structural cards B4/B5 at perturbative_order <= 2.

DG-4 Phase B.4 threads the two operational quadrature controls
(``quad_limit`` and ``upper_cutoff_factor``) through the runner-facing
thermal/displaced K-grid entry points.

Pending scope covers L_n at orders n >= 3 (full Companion Eq. (28)
recursion) and canonical_lindblad_form, the full K + dissipator
decomposition with traceless jump operators (Companion Eq. (43)).

Anchor: SCHEMA.md v0.1.2; benchmark cards A3/A4/B4/B5.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from scipy.linalg import expm

from cbg.basis import matrix_unit_basis
from cbg.bath_correlations import n_point_ordered, two_point
from cbg.cumulants import D_bar_1, D_bar_2
from cbg.effective_hamiltonian import K_from_generator

# ─── Interaction-picture helper ──────────────────────────────────────────────


def interaction_picture(H_S: np.ndarray, A: np.ndarray, tau: float) -> np.ndarray:
    """Compute A_I(τ) = e^{i H_S τ} A e^{-i H_S τ}.

    Used to evolve the system coupling operator A under H_S only (the
    interaction-picture transformation). Vectorising over `tau` is left
    to the caller.

    Parameters
    ----------
    H_S : ndarray
        System Hamiltonian, shape (d, d).
    A : ndarray
        System coupling operator, shape (d, d).
    tau : float
        Interaction-picture time argument; can be positive or negative.

    Returns
    -------
    ndarray, shape (d, d), dtype complex
    """
    U = expm(1j * np.asarray(H_S, dtype=complex) * tau)
    return U @ np.asarray(A, dtype=complex) @ U.conj().T


# ─── Companion D̄ at n=4 (DG-4 Phase B, thermal Gaussian) ───────────────────
#
# Verification card:
#   transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_
#   n4-small-grid-verification-card_v0.1.0.md
#
# Parent transcription:
#   transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md
#
# This block implements the Phase B private helper for the Companion
# fourth-order generalized cumulant D̄(τ_1^k, s_1^{4−k}) per Eqs. (69)–(73)
# of the parent transcription artifact, using the closed-by-steward
# row-2.3 chain-reversal-and-swap rule for all raw D leaves and the
# Eq. (22) boundary delta on Ḋ. The helper is private; the public
# L_n_thermal_at_time(n=4) route remains a NotImplementedError until
# Phase C/D oracles pass (work plan v0.1.5 §4 Phase B acceptance).


def _D_companion_raw_n4(
    tau_args: tuple[float, ...],
    s_args: tuple[float, ...],
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> complex:
    """Raw Companion D(τ_1^k, s_1^{4−k}) via the row-2.3 swap.

    Calls n_point_ordered with tau_args and s_args swapped and each
    side reversed, yielding the Companion operator-order trace
    ⟨B(s_{n−k})...B(s_1) B(τ_1)...B(τ_k)⟩ at n = 4.
    """
    swapped_tau = tuple(reversed(s_args))
    swapped_s = tuple(reversed(tau_args))
    return n_point_ordered(
        swapped_tau,
        swapped_s,
        bath_state=bath_state,
        spectral_density=spectral_density,
        upper_cutoff_factor=upper_cutoff_factor,
        quad_limit=quad_limit,
    )


def _D_companion_raw_n2(
    tau_args: tuple[float, ...],
    s_args: tuple[float, ...],
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> complex:
    """Raw Companion D(τ_1^k, s_1^{2−k}) via the row-2.3 swap.

    Returns the operator-ordered two-point ⟨B(u_1) B(u_2)⟩ where the
    ordered times (u_1, u_2) follow row 2.3:

        D(τ_a, τ_b)  ↦ C(τ_a, τ_b)         (pure-left,  k = 2)
        D(s_a, s_b)  ↦ C(s_b, s_a)         (pure-right, k = 0)
        D(τ_a, s_b)  ↦ C(s_b, τ_a)         (mixed,      k = 1)
    """
    if len(tau_args) + len(s_args) != 2:
        raise ValueError(
            "_D_companion_raw_n2: total order must be 2 "
            f"(got len(tau_args)={len(tau_args)}, "
            f"len(s_args)={len(s_args)})"
        )
    times = tuple(reversed(s_args)) + tuple(tau_args)
    return two_point(
        times[0],
        times[1],
        bath_state=bath_state,
        spectral_density=spectral_density,
        upper_cutoff_factor=upper_cutoff_factor,
        quad_limit=quad_limit,
    )


def _D_bar_4_companion(
    tau_args: tuple[float, ...],
    s_args: tuple[float, ...],
    *,
    t: float,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> complex:
    """Companion D̄(τ_1^k, s_1^{4−k}) at total order n = 4.

    Implements Eqs. (69)–(73) of the parent transcription artifact
    directly:

        Eq. (69)  k = 0 : D̄(s_1^4)        = Ḋ(s_1^4) − Ḋ(s_1^2)·D(s_3^4)
        Eq. (70)  k = 1 : D̄(τ_1, s_1^3)   = Ḋ(τ_1, s_1^3)
                                            − Ḋ(τ_1, s_1)·D(s_2^3)
                                            − Ḋ(s_1^2)·D(τ_1, s_3)
        Eq. (71)  k = 2 : D̄(τ_1^2, s_1^2) = Ḋ(τ_1^2, s_1^2)
                                            − Ḋ(τ_1, s_1)·D(τ_2, s_2)
                                            − Ḋ(s_1^2)·D(τ_1^2)
                                            − Ḋ(τ_1^2)·D(s_1^2)
        Eq. (72)  k = 3 : D̄(τ_1^3, s_1)   = Ḋ(τ_1^3, s_1)
                                            − Ḋ(τ_1, s_1)·D(τ_2^3)
                                            − Ḋ(τ_1^2)·D(τ_3, s_1)
        Eq. (73)  k = 4 : D̄(τ_1^4)        = Ḋ(τ_1^4) − Ḋ(τ_1^2)·D(τ_3^4)

    Substitution rules used internally:

    - All raw D leaves (n = 4 and n = 2) are evaluated via the row-2.3
      chain-reversal-and-swap rule, delegating to _D_companion_raw_n4
      and _D_companion_raw_n2 respectively.
    - Ḋ(τ_1^k, s_1^{n−k}) = D(...)·(δ_{τ_1,t} + δ_{s_1,t}), with the
      empty-chain convention that the missing-side delta is 0 (Eq. 22).
    - This helper MUST NOT call cbg.cumulants._joint_cumulant_from_raw_moments
      (the B.1 standard-cumulant path silently returns ≈ 0 for thermal
      Gaussian at n ≥ 3; see parent transcription row 2.8).

    The signature is private; the public L_n_thermal_at_time(n=4) route
    remains a NotImplementedError pending Phase C oracles (work plan
    v0.1.5 §4 Phase B acceptance).

    Parameters
    ----------
    tau_args : sequence of float
        Companion τ-chain (left-acting times), length k.
    s_args : sequence of float
        Companion s-chain (right-acting times), length 4 − k.
    t : float, keyword-only
        Outer evaluation time at which the Eq. (22) boundary delta is
        applied. Strict equality `tau_args[0] == t` or `s_args[0] == t`
        determines whether the boundary delta fires (Kronecker semantics
        at the verification-card grid; not a Dirac at integration time).
    bath_state, spectral_density : dict, keyword-only
        Forwarded to n_point_ordered and two_point.
    upper_cutoff_factor, quad_limit : optional
        Quadrature controls forwarded to n_point_ordered and two_point.

    Returns
    -------
    complex
        Companion D̄(τ_1^k, s_1^{4−k}) at total order 4.

    Raises
    ------
    NotImplementedError
        If total order ≠ 4, or k ∉ {0, 1, 2, 3, 4}. Phase B scope is
        n = 4 only; n ≥ 5 is out of scope for DG-4 work plan v0.1.5.
    """
    tau_args = tuple(float(x) for x in tau_args)
    s_args = tuple(float(x) for x in s_args)
    k = len(tau_args)
    n_total = k + len(s_args)
    if n_total != 4:
        raise NotImplementedError(
            f"_D_bar_4_companion: total order n={n_total} not supported. "
            f"Phase B scope is n=4 only."
        )
    if k not in {0, 1, 2, 3, 4}:
        raise NotImplementedError(f"_D_bar_4_companion: k={k} not in {{0,1,2,3,4}}.")

    # Eq. (22) boundary delta. Empty-chain convention: the missing-side
    # indicator is 0.
    delta_tau = 1 if (k >= 1 and tau_args[0] == t) else 0
    delta_s = 1 if (4 - k >= 1 and s_args[0] == t) else 0

    leaf_kw: dict[str, Any] = {
        "bath_state": bath_state,
        "spectral_density": spectral_density,
        "upper_cutoff_factor": upper_cutoff_factor,
        "quad_limit": quad_limit,
    }

    # Raw 4-point appears in every case (the first term of each Eq.).
    D_n4 = _D_companion_raw_n4(tau_args, s_args, **leaf_kw)
    D_dot_n4 = D_n4 * (delta_tau + delta_s)

    if k == 4:
        # Eq. (73): D̄(τ_1^4) = Ḋ(τ_1^4) − Ḋ(τ_1^2)·D(τ_3^4)
        t1, t2, t3, t4 = tau_args
        D_tau12 = _D_companion_raw_n2((t1, t2), (), **leaf_kw)
        D_tau34 = _D_companion_raw_n2((t3, t4), (), **leaf_kw)
        D_dot_tau12 = D_tau12 * delta_tau
        return D_dot_n4 - D_dot_tau12 * D_tau34

    if k == 3:
        # Eq. (72): D̄(τ_1^3, s_1) = Ḋ(τ_1^3, s_1)
        #                            − Ḋ(τ_1, s_1)·D(τ_2^3)
        #                            − Ḋ(τ_1^2)·D(τ_3, s_1)
        t1, t2, t3 = tau_args
        (s1,) = s_args
        D_tau1_s1 = _D_companion_raw_n2((t1,), (s1,), **leaf_kw)
        D_dot_tau1_s1 = D_tau1_s1 * (delta_tau + delta_s)
        D_tau23 = _D_companion_raw_n2((t2, t3), (), **leaf_kw)
        D_tau12 = _D_companion_raw_n2((t1, t2), (), **leaf_kw)
        D_dot_tau12 = D_tau12 * delta_tau
        D_tau3_s1 = _D_companion_raw_n2((t3,), (s1,), **leaf_kw)
        return D_dot_n4 - D_dot_tau1_s1 * D_tau23 - D_dot_tau12 * D_tau3_s1

    if k == 2:
        # Eq. (71): D̄(τ_1^2, s_1^2) = Ḋ(τ_1^2, s_1^2)
        #                              − Ḋ(τ_1, s_1)·D(τ_2, s_2)
        #                              − Ḋ(s_1^2)·D(τ_1^2)
        #                              − Ḋ(τ_1^2)·D(s_1^2)
        t1, t2 = tau_args
        s1, s2 = s_args
        D_tau1_s1 = _D_companion_raw_n2((t1,), (s1,), **leaf_kw)
        D_dot_tau1_s1 = D_tau1_s1 * (delta_tau + delta_s)
        D_tau2_s2 = _D_companion_raw_n2((t2,), (s2,), **leaf_kw)
        D_s12 = _D_companion_raw_n2((), (s1, s2), **leaf_kw)
        D_dot_s12 = D_s12 * delta_s
        D_tau12 = _D_companion_raw_n2((t1, t2), (), **leaf_kw)
        D_dot_tau12 = D_tau12 * delta_tau
        return D_dot_n4 - D_dot_tau1_s1 * D_tau2_s2 - D_dot_s12 * D_tau12 - D_dot_tau12 * D_s12

    if k == 1:
        # Eq. (70): D̄(τ_1, s_1^3) = Ḋ(τ_1, s_1^3)
        #                            − Ḋ(τ_1, s_1)·D(s_2^3)
        #                            − Ḋ(s_1^2)·D(τ_1, s_3)
        (t1,) = tau_args
        s1, s2, s3 = s_args
        D_tau1_s1 = _D_companion_raw_n2((t1,), (s1,), **leaf_kw)
        D_dot_tau1_s1 = D_tau1_s1 * (delta_tau + delta_s)
        D_s23 = _D_companion_raw_n2((), (s2, s3), **leaf_kw)
        D_s12 = _D_companion_raw_n2((), (s1, s2), **leaf_kw)
        D_dot_s12 = D_s12 * delta_s
        D_tau1_s3 = _D_companion_raw_n2((t1,), (s3,), **leaf_kw)
        return D_dot_n4 - D_dot_tau1_s1 * D_s23 - D_dot_s12 * D_tau1_s3

    # k == 0: Eq. (69) — D̄(s_1^4) = Ḋ(s_1^4) − Ḋ(s_1^2)·D(s_3^4)
    s1, s2, s3, s4 = s_args
    D_s12 = _D_companion_raw_n2((), (s1, s2), **leaf_kw)
    D_dot_s12 = D_s12 * delta_s
    D_s34 = _D_companion_raw_n2((), (s3, s4), **leaf_kw)
    return D_dot_n4 - D_dot_s12 * D_s34


# ─── L_4 assembly via literal θ-aware Eqs. (69)-(73) integration ────────────
#
# Verification card (frozen 2026-05-13):
#   transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_
#   phase-c-physics-oracles-card_v0.1.2.md  (current).
#
# This block implements `_L_4_thermal_at_time_apply` per the v0.1.1 §3a
# discipline AND the v0.1.2 §3.2 commuting-case guard.
#
# Each (k ∈ {0..4}, term in Eq. (69)-(73), boundary-delta branch ∈
# {τ_1=t, s_1=t}) contribution is integrated on its OWN 3-D domain.
# Per the v0.1.2 review post-mortem, that domain is the **intersection
# of**:
#   1. the outer Eq. (28) τ-chain ordering t > τ_1 > … > τ_k > 0;
#   2. the outer Eq. (28) s-chain ordering t > s_1 > … > s_{4-k} > 0;
#   3. each constituent D factor's Eq. (15) θ-window.
#
# All terms at a fixed (k, branch) therefore share the same outer
# simplex domain — they differ only in their integrand. Each
# (k, branch) is implemented as ONE loop that sums the integrands of
# all terms contributing to that (k, branch). Wick's theorem is
# applied INSIDE each raw D factor individually; pre-cancellation
# of Wick pairings across terms is explicitly forbidden (v0.1.1 §3b).
#
# Domain shapes encountered (4 distinct, one per (k, branch) pair):
#   - 3-simplex on (a, b, c): t > a > b > c > 0
#   - 1-D × 2-simplex on (a; b, c): a ∈ [0, t], t > b > c > 0
#   - 2-simplex × 1-D on (a, b; c): t > a > b > 0, c ∈ [0, t]
# (The "3-D cube" shape was an early mis-implementation that ignored
# the outer chain ordering for subtraction terms with shorter D
# factors; the v0.1.2 review identified and corrected this. See the
# v0.1.1 → v0.1.2 supersession entry in the parent card.)
#
# Quadrature: nested 1-D trapezoidal on each simplex factor; standard
# 1-D trapezoidal on each free axis. Weight matrix c_wt[i, M] gives the
# 1-D trapezoidal weight on [0, g[M]] at grid index i (h/2 at endpoints,
# h interior, 0 if i > M).
#
# Operator chain per (k, branch) is fixed; only the integrand differs
# per term, all integrated on the shared (k, branch) outer simplex.


def _L_4_thermal_at_time_apply(
    t_idx: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> Callable[[np.ndarray], np.ndarray]:
    """Return a callable that computes L_4[X] at t = t_grid[t_idx] for
    a thermal Gaussian bath, assembled from Companion Eq. (28) at n = 4
    via literal θ-aware integration of Eqs. (69)-(73), with a
    commuting-case Feynman-Vernon exact-zero short-circuit.

    Verification card:
        transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_
        phase-c-physics-oracles-card_v0.1.2.md  (frozen 2026-05-13).

    Behaviour:

    - Commuting-case guard (§3.2 of the card): if [H_S, A] = 0
      (machine-tolerance check at atol = rtol = 1e-12), short-circuit
      to a callable that returns the (d, d) zero matrix. This captures
      the Feynman-Vernon Gaussian-bath truncation result for pure
      dephasing: L_4 = 0 as an operator. The guard fires for A = σ_z
      with H_S = (ω/2) σ_z and similar commuting configurations.
    - Non-commuting case ([H_S, A] ≠ 0): run the literal θ-aware
      integration of Eqs. (69)-(73) per v0.1.1 §3a. Each
      (k, term, branch) contribution is integrated on its own 3-D
      domain (intersection of each constituent D factor's Eq. (15)
      θ-window with the outer Eq. (28) range). Wick is applied inside
      each raw D factor individually; pre-cancellation across terms is
      forbidden.

    Parameters
    ----------
    t_idx : int
        Index into t_grid at which to evaluate L_4.
    t_grid : ndarray
        Time points; uniform spacing, t_grid[0] = 0.
    system_hamiltonian, coupling_operator : ndarray
        H_S and A, each shape (d, d).
    bath_state, spectral_density : dict, keyword-only
        Forwarded to cbg.bath_correlations.two_point.
    upper_cutoff_factor, quad_limit : optional
        Quadrature controls forwarded to two_point.

    Returns
    -------
    callable
        L_4_apply : (X: (d, d) ndarray) -> (d, d) ndarray.
    """
    H_S = np.asarray(system_hamiltonian, dtype=complex)
    A = np.asarray(coupling_operator, dtype=complex)
    d = A.shape[0]

    # Commuting-case Feynman-Vernon exact-zero guard (v0.1.2 §3.2).
    # When [H_S, A] = 0, thermal Gaussian L_t truncates at order 2
    # exactly (the dephasing dynamical map factorises in α), so
    # L_4 = 0 as an operator. Short-circuit to avoid the O(n_g^4)
    # quadrature path that would only converge to zero as O(h^1) at
    # the v0.1.2 §4.1 Part B diagnostic rate.
    commutator = H_S @ A - A @ H_S
    if np.allclose(commutator, np.zeros_like(commutator), atol=1e-12, rtol=1e-12):
        return lambda X: np.zeros((d, d), dtype=complex)

    return _L_4_thermal_at_time_apply_no_guard(
        t_idx,
        t_grid,
        system_hamiltonian,
        coupling_operator,
        bath_state=bath_state,
        spectral_density=spectral_density,
        upper_cutoff_factor=upper_cutoff_factor,
        quad_limit=quad_limit,
    )


def _L_4_thermal_at_time_apply_no_guard(
    t_idx: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> Callable[[np.ndarray], np.ndarray]:
    """Literal θ-aware L_4 assembly without the commuting-case guard.

    For the card §4.1 Part B convergence diagnostic ONLY. Use
    `_L_4_thermal_at_time_apply` in production: it short-circuits to
    exact zero when [H_S, A] = 0 (Feynman-Vernon), avoiding the
    O(n_g^4) quadrature path. This `_no_guard` entry point bypasses
    the short-circuit so the diagnostic can measure the literal
    θ-aware quadrature's convergence on a refinement table.

    Verification card:
        transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_
        phase-c-physics-oracles-card_v0.1.2.md §5 step 2.

    Signature and integration logic match `_L_4_thermal_at_time_apply`
    minus the §3.2 commuting-case guard.
    """
    H_S = np.asarray(system_hamiltonian, dtype=complex)
    A = np.asarray(coupling_operator, dtype=complex)
    t_grid_np = np.asarray(t_grid, dtype=float)
    d = A.shape[0]

    if t_idx < 1:
        return lambda X: np.zeros((d, d), dtype=complex)

    t_at = float(t_grid_np[t_idx])
    sub_grid = t_grid_np[: t_idx + 1]
    n_g = len(sub_grid)
    T = n_g - 1  # grid index of the boundary time t

    # Pre-compute A_I(τ - t) on the sub-grid (per n=2 repo convention).
    A_I = np.zeros((n_g, d, d), dtype=complex)
    for i in range(n_g):
        A_I[i] = interaction_picture(H_S, A, sub_grid[i] - t_at)
    A_at_t = A  # A_I(0) = A (interaction-picture operator at boundary time)

    # Pre-compute C_tbl[i, j] = ⟨B(g[i]) B(g[j])⟩.
    C_tbl = np.zeros((n_g, n_g), dtype=complex)
    for i in range(n_g):
        for j in range(n_g):
            C_tbl[i, j] = two_point(
                sub_grid[i],
                sub_grid[j],
                bath_state=bath_state,
                spectral_density=spectral_density,
                upper_cutoff_factor=upper_cutoff_factor,
                quad_limit=quad_limit,
            )

    # Pre-compute c_wt[i, M] = nested 1-D trapezoidal weight on [0, g[M]].
    h = float(sub_grid[1] - sub_grid[0])
    c_wt = np.zeros((n_g, n_g))
    for M in range(1, n_g):
        for i in range(M + 1):
            c_wt[i, M] = h / 2 if (i == 0 or i == M) else h

    # Build the (coef, left_op, right_op) quadrature terms.
    quadrature_terms: list[tuple[complex, np.ndarray, np.ndarray]] = []
    eye_d = np.eye(d, dtype=complex)

    # ─ Helper: Wick split of ⟨B(t1)B(t2)B(t3)B(t4)⟩ at given grid indices.
    def W4(i1, i2, i3, i4):
        return (
            C_tbl[i1, i2] * C_tbl[i3, i4]
            + C_tbl[i1, i3] * C_tbl[i2, i4]
            + C_tbl[i1, i4] * C_tbl[i2, i3]
        )

    # Note: each (k, branch, term) block below applies the outer (-1)^k
    # via the explicit `sign_outer_*` constant; the per-term sign from
    # Eqs. (69)-(73) is folded into the `term_sign_*` constants.

    # ════════════════════════════════════════════════════════════════
    # k = 0, s-branch (Eq. 69). Outer sign: (-1)^0 = +1. Both terms.
    # ════════════════════════════════════════════════════════════════
    # Free vars: (s_2, s_3, s_4). Operator chain:
    #   left_op = I; right_op = A_I[i_s_4] @ A_I[i_s_3] @ A_I[i_s_2] @ A
    # Term 1.69 (+): D(t, s_2, s_3, s_4) on 3-simplex {t>s_2>s_3>s_4}.
    #   D operator order via row-2.3: ⟨B(s_4) B(s_3) B(s_2) B(t)⟩
    # Term 2.69 (-): C(s_2, t) C(s_4, s_3) on {s_2 ∈ [0,t], s_3 > s_4}.

    # k=0, s-branch, Term 1.69 (+): 3-simplex on (s_2, s_3, s_4)
    for i_s_2 in range(n_g):
        for i_s_3 in range(i_s_2):
            for i_s_4 in range(i_s_3):
                wt = c_wt[i_s_2, T] * c_wt[i_s_3, i_s_2] * c_wt[i_s_4, i_s_3]
                if wt == 0.0:
                    continue
                integrand = W4(i_s_4, i_s_3, i_s_2, T)  # ⟨B(s_4)B(s_3)B(s_2)B(t)⟩
                right_op = A_I[i_s_4] @ A_I[i_s_3] @ A_I[i_s_2] @ A_at_t
                quadrature_terms.append((wt * integrand, eye_d, right_op))

    # k=0, s-branch, Term 2.69 (-): 1-D × 2-simplex on (s_2; s_3, s_4)
    for i_s_2 in range(n_g):
        w_a = c_wt[i_s_2, T]
        if w_a == 0.0:
            continue
        for i_s_3 in range(n_g):
            for i_s_4 in range(i_s_3):
                wt = w_a * c_wt[i_s_3, T] * c_wt[i_s_4, i_s_3]
                if wt == 0.0:
                    continue
                # -C(s_2, t) × C(s_4, s_3)
                integrand = -C_tbl[i_s_2, T] * C_tbl[i_s_4, i_s_3]
                right_op = A_I[i_s_4] @ A_I[i_s_3] @ A_I[i_s_2] @ A_at_t
                quadrature_terms.append((wt * integrand, eye_d, right_op))

    # ════════════════════════════════════════════════════════════════
    # k = 1, τ-branch (Eq. 70). Outer sign: (-1)^1 = -1.
    # ════════════════════════════════════════════════════════════════
    # Free vars: (s_1, s_2, s_3). Operator chain:
    #   left_op = A; right_op = A_I[i_s_3] @ A_I[i_s_2] @ A_I[i_s_1]
    # Term 1.70 (+): D(t, s_1, s_2, s_3) on 3-simplex.
    #   Operator order: ⟨B(s_3) B(s_2) B(s_1) B(t)⟩
    # Term 2.70 (-): -C(s_1, t) × C(s_3, s_2) on 1-D × 2-simplex.
    # Term 3.70 is s-branch only.
    sign_outer_k1 = -1.0

    # k=1, τ-branch, Term 1.70 (+): 3-simplex on (s_1, s_2, s_3)
    for i_s_1 in range(n_g):
        for i_s_2 in range(i_s_1):
            for i_s_3 in range(i_s_2):
                wt = c_wt[i_s_1, T] * c_wt[i_s_2, i_s_1] * c_wt[i_s_3, i_s_2]
                if wt == 0.0:
                    continue
                integrand = W4(i_s_3, i_s_2, i_s_1, T)
                right_op = A_I[i_s_3] @ A_I[i_s_2] @ A_I[i_s_1]
                coef = sign_outer_k1 * wt * integrand
                quadrature_terms.append((coef, A_at_t, right_op))

    # k=1, τ-branch, Term 2.70 (-): 1-D × 2-simplex on (s_1; s_2, s_3)
    for i_s_1 in range(n_g):
        w_a = c_wt[i_s_1, T]
        if w_a == 0.0:
            continue
        for i_s_2 in range(n_g):
            for i_s_3 in range(i_s_2):
                wt = w_a * c_wt[i_s_2, T] * c_wt[i_s_3, i_s_2]
                if wt == 0.0:
                    continue
                integrand = -C_tbl[i_s_1, T] * C_tbl[i_s_3, i_s_2]
                right_op = A_I[i_s_3] @ A_I[i_s_2] @ A_I[i_s_1]
                coef = sign_outer_k1 * wt * integrand
                quadrature_terms.append((coef, A_at_t, right_op))

    # ════════════════════════════════════════════════════════════════
    # k = 1, s-branch (Eq. 70). Outer sign: -1.
    # ════════════════════════════════════════════════════════════════
    # Free vars: (τ_1, s_2, s_3). Operator chain:
    #   left_op = A_I[i_τ_1]; right_op = A_I[i_s_3] @ A_I[i_s_2] @ A
    # Term 1.70 (+): D(τ_1, t, s_2, s_3) on 1-D × 2-simplex {τ_1, t > s_2 > s_3}.
    #   Operator order: ⟨B(s_3) B(s_2) B(t) B(τ_1)⟩
    # Term 2.70 (-): -C(t, τ_1) × C(s_3, s_2) on same 1-D × 2-simplex.
    # Term 3.70 (-): -C(s_2, t) × C(s_3, τ_1). Per v0.1.2 review: this term's
    #   integration domain is the intersection of its inner θ-window
    #   (C(s_1, s_2) has θ_{s_1^2}=s_1>s_2 → trivially satisfied after
    #   s_1=t; D(τ_1, s_3) trivial inner θ) with the OUTER Eq. (28) s-chain
    #   ordering t > s_1 > s_2 > s_3 > 0. After s_1=t collapse, the outer
    #   gives t > s_2 > s_3 > 0 — the same 1-D × 2-simplex as Terms 1 and 2.
    # All three terms therefore share the same 1-D × 2-simplex domain.

    # k=1, s-branch, Terms 1.70 + 2.70 + 3.70 on 1-D × 2-simplex on (τ_1; s_2, s_3)
    for i_t_1 in range(n_g):
        w_t1 = c_wt[i_t_1, T]
        if w_t1 == 0.0:
            continue
        left_op = A_I[i_t_1]
        for i_s_2 in range(n_g):
            for i_s_3 in range(i_s_2):
                wt = w_t1 * c_wt[i_s_2, T] * c_wt[i_s_3, i_s_2]
                if wt == 0.0:
                    continue
                # Term 1.70 (+): ⟨B(s_3) B(s_2) B(t) B(τ_1)⟩
                integrand_1 = W4(i_s_3, i_s_2, T, i_t_1)
                # Term 2.70 (-): -C(t, τ_1) C(s_3, s_2)
                integrand_2 = -C_tbl[T, i_t_1] * C_tbl[i_s_3, i_s_2]
                # Term 3.70 (-): -C(s_2, t) C(s_3, τ_1)
                integrand_3 = -C_tbl[i_s_2, T] * C_tbl[i_s_3, i_t_1]
                right_op = A_I[i_s_3] @ A_I[i_s_2] @ A_at_t
                coef = sign_outer_k1 * wt * (integrand_1 + integrand_2 + integrand_3)
                quadrature_terms.append((coef, left_op, right_op))

    # ════════════════════════════════════════════════════════════════
    # k = 2, τ-branch (Eq. 71). Outer sign: (-1)^2 = +1.
    # ════════════════════════════════════════════════════════════════
    # Free vars: (τ_2, s_1, s_2). Operator chain:
    #   left_op = A @ A_I[i_τ_2]; right_op = A_I[i_s_2] @ A_I[i_s_1]
    # Term 1.71 (+): D(t, τ_2, s_1, s_2) on 1-D × 2-simplex (τ_2; s_1, s_2).
    #   Operator order: ⟨B(s_2) B(s_1) B(t) B(τ_2)⟩
    # Term 2.71 (-): -C(s_1, t) × C(s_2, τ_2). Per v0.1.2 review: outer
    #   Eq. (28) s-chain ordering s_1 > s_2 still applies after τ_1=t
    #   collapse, so this term shares the same 1-D × 2-simplex domain as
    #   Terms 1 and 4 (not a 3-D cube).
    # Term 3.71 is s-branch only.
    # Term 4.71 (-): -C(t, τ_2) × C(s_2, s_1) on 1-D × 2-simplex.
    # Terms 1.71, 2.71, 4.71 share the same 1-D × 2-simplex domain.
    sign_outer_k2 = 1.0

    # k=2, τ-branch, Terms 1.71 + 2.71 + 4.71 on 1-D × 2-simplex on (τ_2; s_1, s_2)
    for i_t_2 in range(n_g):
        w_t2 = c_wt[i_t_2, T]
        if w_t2 == 0.0:
            continue
        left_op = A_at_t @ A_I[i_t_2]
        for i_s_1 in range(n_g):
            for i_s_2 in range(i_s_1):
                wt = w_t2 * c_wt[i_s_1, T] * c_wt[i_s_2, i_s_1]
                if wt == 0.0:
                    continue
                integrand_1 = W4(i_s_2, i_s_1, T, i_t_2)
                integrand_2 = -C_tbl[i_s_1, T] * C_tbl[i_s_2, i_t_2]
                integrand_4 = -C_tbl[T, i_t_2] * C_tbl[i_s_2, i_s_1]
                right_op = A_I[i_s_2] @ A_I[i_s_1]
                coef = sign_outer_k2 * wt * (integrand_1 + integrand_2 + integrand_4)
                quadrature_terms.append((coef, left_op, right_op))

    # ════════════════════════════════════════════════════════════════
    # k = 2, s-branch (Eq. 71). Outer sign: +1.
    # ════════════════════════════════════════════════════════════════
    # Free vars: (τ_1, τ_2, s_2). Operator chain:
    #   left_op = A_I[i_τ_1] @ A_I[i_τ_2]; right_op = A_I[i_s_2] @ A
    # Term 1.71 (+): D(τ_1, τ_2, t, s_2) on 2-simplex × 1-D (τ_1>τ_2; s_2).
    #   Operator order: ⟨B(s_2) B(t) B(τ_1) B(τ_2)⟩
    # Term 2.71 (-): -C(t, τ_1) × C(s_2, τ_2). Per v0.1.2 review: outer
    #   Eq. (28) τ-chain ordering τ_1 > τ_2 still applies, so this term
    #   shares the same 2-simplex × 1-D domain as Terms 1 and 3 (not a
    #   3-D cube).
    # Term 3.71 (-): -C(s_2, t) × C(τ_1, τ_2) on 2-simplex × 1-D.
    # Term 4.71 is τ-branch only.
    # Terms 1.71, 2.71, 3.71 share the same 2-simplex × 1-D domain.

    # k=2, s-branch, Terms 1.71 + 2.71 + 3.71 on 2-simplex × 1-D on (τ_1, τ_2; s_2)
    for i_t_1 in range(n_g):
        for i_t_2 in range(i_t_1):
            w_tau = c_wt[i_t_1, T] * c_wt[i_t_2, i_t_1]
            if w_tau == 0.0:
                continue
            left_op = A_I[i_t_1] @ A_I[i_t_2]
            for i_s_2 in range(n_g):
                w_s = c_wt[i_s_2, T]
                if w_s == 0.0:
                    continue
                wt = w_tau * w_s
                integrand_1 = W4(i_s_2, T, i_t_1, i_t_2)
                integrand_2 = -C_tbl[T, i_t_1] * C_tbl[i_s_2, i_t_2]
                integrand_3 = -C_tbl[i_s_2, T] * C_tbl[i_t_1, i_t_2]
                right_op = A_I[i_s_2] @ A_at_t
                coef = sign_outer_k2 * wt * (integrand_1 + integrand_2 + integrand_3)
                quadrature_terms.append((coef, left_op, right_op))

    # ════════════════════════════════════════════════════════════════
    # k = 3, τ-branch (Eq. 72). Outer sign: (-1)^3 = -1.
    # ════════════════════════════════════════════════════════════════
    # Free vars: (τ_2, τ_3, s_1). Operator chain:
    #   left_op = A @ A_I[i_τ_2] @ A_I[i_τ_3]; right_op = A_I[i_s_1]
    # Term 1.72 (+): D(t, τ_2, τ_3, s_1) on 2-simplex × 1-D (τ_2>τ_3; s_1).
    #   Operator order: ⟨B(s_1) B(t) B(τ_2) B(τ_3)⟩
    # Term 2.72 (-): -C(s_1, t) × C(τ_2, τ_3) on 2-simplex × 1-D.
    # Term 3.72 (-): -C(t, τ_2) × C(s_1, τ_3). Per v0.1.2 review: outer
    #   Eq. (28) τ-chain ordering τ_2 > τ_3 (after τ_1=t collapse) still
    #   applies, so this term shares the same 2-simplex × 1-D domain as
    #   Terms 1 and 2 (not a 3-D cube).
    # Terms 1.72, 2.72, 3.72 share the 2-simplex × 1-D domain.
    sign_outer_k3 = -1.0

    # k=3, τ-branch, Terms 1.72 + 2.72 + 3.72 on 2-simplex × 1-D on (τ_2, τ_3; s_1)
    for i_t_2 in range(n_g):
        for i_t_3 in range(i_t_2):
            w_tau = c_wt[i_t_2, T] * c_wt[i_t_3, i_t_2]
            if w_tau == 0.0:
                continue
            left_op = A_at_t @ A_I[i_t_2] @ A_I[i_t_3]
            for i_s_1 in range(n_g):
                w_s = c_wt[i_s_1, T]
                if w_s == 0.0:
                    continue
                wt = w_tau * w_s
                integrand_1 = W4(i_s_1, T, i_t_2, i_t_3)
                integrand_2 = -C_tbl[i_s_1, T] * C_tbl[i_t_2, i_t_3]
                integrand_3 = -C_tbl[T, i_t_2] * C_tbl[i_s_1, i_t_3]
                right_op = A_I[i_s_1]
                coef = sign_outer_k3 * wt * (integrand_1 + integrand_2 + integrand_3)
                quadrature_terms.append((coef, left_op, right_op))

    # (Term 3.72 has been merged into the loop above per v0.1.2 review.)

    # ════════════════════════════════════════════════════════════════
    # k = 3, s-branch (Eq. 72). Outer sign: -1.
    # ════════════════════════════════════════════════════════════════
    # Free vars: (τ_1, τ_2, τ_3). Operator chain:
    #   left_op = A_I[i_τ_1] @ A_I[i_τ_2] @ A_I[i_τ_3]; right_op = A
    # Term 1.72 (+): D(τ_1, τ_2, τ_3, t) on 3-simplex {τ_1>τ_2>τ_3}.
    #   Operator order: ⟨B(t) B(τ_1) B(τ_2) B(τ_3)⟩
    # Term 2.72 (-): -C(t, τ_1) × C(τ_2, τ_3) on 1-D × 2-simplex (τ_1; τ_2, τ_3).
    # Term 3.72 is τ-branch only.

    # k=3, s-branch, Term 1.72 (+): 3-simplex on (τ_1, τ_2, τ_3)
    for i_t_1 in range(n_g):
        for i_t_2 in range(i_t_1):
            for i_t_3 in range(i_t_2):
                wt = c_wt[i_t_1, T] * c_wt[i_t_2, i_t_1] * c_wt[i_t_3, i_t_2]
                if wt == 0.0:
                    continue
                integrand = W4(T, i_t_1, i_t_2, i_t_3)
                left_op = A_I[i_t_1] @ A_I[i_t_2] @ A_I[i_t_3]
                right_op = A_at_t
                coef = sign_outer_k3 * wt * integrand
                quadrature_terms.append((coef, left_op, right_op))

    # k=3, s-branch, Term 2.72 (-): 1-D × 2-simplex on (τ_1; τ_2, τ_3)
    for i_t_1 in range(n_g):
        w_t1 = c_wt[i_t_1, T]
        if w_t1 == 0.0:
            continue
        for i_t_2 in range(n_g):
            for i_t_3 in range(i_t_2):
                wt = w_t1 * c_wt[i_t_2, T] * c_wt[i_t_3, i_t_2]
                if wt == 0.0:
                    continue
                integrand = -C_tbl[T, i_t_1] * C_tbl[i_t_2, i_t_3]
                left_op = A_I[i_t_1] @ A_I[i_t_2] @ A_I[i_t_3]
                right_op = A_at_t
                coef = sign_outer_k3 * wt * integrand
                quadrature_terms.append((coef, left_op, right_op))

    # ════════════════════════════════════════════════════════════════
    # k = 4, τ-branch (Eq. 73). Outer sign: (-1)^4 = +1.
    # ════════════════════════════════════════════════════════════════
    # Free vars: (τ_2, τ_3, τ_4). Operator chain:
    #   left_op = A @ A_I[i_τ_2] @ A_I[i_τ_3] @ A_I[i_τ_4]; right_op = I
    # Term 1.73 (+): D(t, τ_2, τ_3, τ_4) on 3-simplex {t>τ_2>τ_3>τ_4}.
    #   Operator order: ⟨B(t) B(τ_2) B(τ_3) B(τ_4)⟩
    # Term 2.73 (-): -C(t, τ_2) × C(τ_3, τ_4) on 1-D × 2-simplex (τ_2; τ_3, τ_4).
    sign_outer_k4 = 1.0

    # k=4, τ-branch, Term 1.73 (+): 3-simplex on (τ_2, τ_3, τ_4)
    for i_t_2 in range(n_g):
        for i_t_3 in range(i_t_2):
            for i_t_4 in range(i_t_3):
                wt = c_wt[i_t_2, T] * c_wt[i_t_3, i_t_2] * c_wt[i_t_4, i_t_3]
                if wt == 0.0:
                    continue
                integrand = W4(T, i_t_2, i_t_3, i_t_4)
                left_op = A_at_t @ A_I[i_t_2] @ A_I[i_t_3] @ A_I[i_t_4]
                right_op = eye_d
                coef = sign_outer_k4 * wt * integrand
                quadrature_terms.append((coef, left_op, right_op))

    # k=4, τ-branch, Term 2.73 (-): 1-D × 2-simplex on (τ_2; τ_3, τ_4)
    for i_t_2 in range(n_g):
        w_t2 = c_wt[i_t_2, T]
        if w_t2 == 0.0:
            continue
        for i_t_3 in range(n_g):
            for i_t_4 in range(i_t_3):
                wt = w_t2 * c_wt[i_t_3, T] * c_wt[i_t_4, i_t_3]
                if wt == 0.0:
                    continue
                integrand = -C_tbl[T, i_t_2] * C_tbl[i_t_3, i_t_4]
                left_op = A_at_t @ A_I[i_t_2] @ A_I[i_t_3] @ A_I[i_t_4]
                right_op = eye_d
                coef = sign_outer_k4 * wt * integrand
                quadrature_terms.append((coef, left_op, right_op))

    def L_4_apply(X: np.ndarray) -> np.ndarray:
        X_arr = np.asarray(X, dtype=complex)
        result = np.zeros((d, d), dtype=complex)
        for coef, left_op, right_op in quadrature_terms:
            result = result + coef * (left_op @ X_arr @ right_op)
        return result

    return L_4_apply


# ─── L_n at order n (thermal-only path) ──────────────────────────────────────


def L_n_thermal_at_time(
    n: int,
    t_idx: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    D_bar_2_array: np.ndarray | None = None,
) -> Callable[[np.ndarray], np.ndarray]:
    """Return a callable that computes L_n[X] at time t_grid[t_idx] for
    a thermal Gaussian bath.

    Implements:

    - n = 0: L_0[X] = -i [H_S, X] (the bare Liouvillian; not really
      a perturbative term, but supplied here so K_total_thermal can
      uniformly assemble K = K_0 + K_1 + K_2 + ... via Letter Eq. (6)).
    - n = 1: L_1[X] = 0 (thermal Gaussian bath has ⟨B⟩ = 0).
    - n = 2: L_2[X](t) = -∫_0^t du {C(t-u) [A, A_I(u-t) X] +
      C(t-u)* [X A_I(u-t), A]} via trapezoidal integration over
      s_grid = t_grid[: t_idx+1]. The integrand is operator-valued; the
      trapezoidal rule is inlined for efficiency (avoids 4 separate
      scalar integrations per matrix entry).
    - n = 3: L_3[X] = 0 (thermal Gaussian D̄_1 = D̄_3 = 0; see DG-4
      Phase B.2 derivation in the n = 3 branch below).
    - n = 4: pending; raises NotImplementedError. Non-zero in
      general for [A, A_I(τ)] ≠ 0; zero for σ_z by Feynman-Vernon.

    Parameters
    ----------
    n : int
        Perturbative order; one of 0, 1, 2 in the implemented low-order path.
    t_idx : int
        Index into t_grid at which to evaluate L_n.
    t_grid : ndarray, shape (n_t,)
        Time points; must satisfy t_grid[0] = 0 for the integral lower
        bound to be the physical t_start = 0 (the cards' convention).
    system_hamiltonian, coupling_operator : ndarray, shape (d, d)
        H_S and A.
    D_bar_2_array : ndarray, shape (n_t, n_t), dtype complex
        Precomputed connected two-point on the time grid; required for
        n = 2; ignored for n in {0, 1}. Use cbg.cumulants.D_bar_2 to
        construct.

    Returns
    -------
    callable
        L_n_apply : (X: (d, d) ndarray) -> (d, d) ndarray.

    Raises
    ------
    NotImplementedError
        For n = 4 (pending; see derivation note in the n = 4 branch).
        For n >= 5 (out of DG-4 Phase B scope).
    ValueError
        For invalid arguments.
    """
    if n == 0:
        H_S = np.asarray(system_hamiltonian, dtype=complex)
        return lambda X: -1j * (H_S @ X - X @ H_S)

    if n == 1:
        # Thermal Gaussian bath: D̄_1 = 0 → L_1 = 0 identically.
        # For coherent-displaced benchmark-card cases, use
        # K_total_displaced_on_grid, which carries the D̄_1-driven term.
        return lambda X: np.zeros_like(np.asarray(X, dtype=complex))

    if n == 3:
        # DG-4 Phase B.2: thermal Gaussian L_3 = 0.
        #
        # The TCL recursion at order 3 is a single triple-time integral
        # weighted by the third generalised cumulant D̄_3, plus product
        # terms involving D̄_1 from the Λ_t-inversion bookkeeping. For a
        # thermal Gaussian bath:
        #   * D̄_3 = 0 by Gaussianity (verified to machine precision in
        #     cbg.cumulants Phase B.1, test_D_bar_thermal_n3_all_left_*).
        #   * D̄_1 = 0 by zero-mean (Phase B.0 odd-order vanishing).
        # Both contributions therefore vanish, and L_3[X] = 0 identically
        # for any system coupling A. (For coherent-displaced bath states
        # the displacement-driven L_1 would propagate into a non-zero L_3
        # via D̄_1 × D̄_2 cross terms; that path is out of scope at Phase
        # B.2 — the thermal Gaussian D1 v0.1.2 fixture targets the
        # L_4-level convergence signal, not L_3.)
        d = np.asarray(coupling_operator).shape[0]
        return lambda X: np.zeros((d, d), dtype=complex)

    if n == 4:
        # Pending: the thermal Gaussian L_4 has a non-trivial structure
        # from (2,2) Wick contractions of D̄_2 mediated by the Λ_t-
        # inversion subtraction L_4 = ∂_t Λ_4 − L_2 ∘ Λ_2. Two physical
        # regimes:
        #   * For [A, A_I(τ)] = 0 (A = σ_z; commutator-structure
        #     degenerates), L_4 = 0 by Feynman-Vernon Gaussian-bath
        #     exactness — the entire TCL series truncates at order 2.
        #     This is the strong falsification oracle: any candidate L_4
        #     formula must give exactly 0 here.
        #   * For [A, A_I(τ)] ≠ 0 (A = σ_x), L_4 ≠ 0 and is the leading-
        #     order convergence-detection signal that D1 v0.1.2's
        #     ‖L_n^dissipator‖ ratio is designed to measure.
        #
        # Falsification of the obvious-looking candidate: a single
        # nested-commutator [A(t),[A_I(s_1−t),[A_I(s_2−t),[A_I(s_3−t),X]]]]
        # weighted by Wick(C(t−s_1)C(s_2−s_3) + perms) gives a complex-
        # valued residual on σ_z ⇒ σ_x evaluation, while the Feynman-
        # Vernon answer is real. The candidate is missing the C* / right-
        # acting conjugate-pair structure that L_2 has, so it is rejected.
        # See logbook routing note 2026-05-06_dg-4-phase-b2-tcl-order-3.md.
        #
        # Three concrete routes to a correct L_4 (DG-4 work plan v0.1.2):
        #   Path A. Companion Sec. IV closed-form (Letter Eqs. 14-18 + Companion
        #     Eqs. 19-28 truncated at n=4). Lowest-risk but requires the
        #     paper text or an equivalent transcription accessible in the
        #     repo (transcriptions/ currently has only the Letter App. D).
        #   Path B. Numerical Λ_t reconstruction via Richardson extraction
        #     from benchmarks/exact_finite_env at multiple coupling
        #     strengths α; fit Λ_t = 1 + α² Λ_2 + α⁴ Λ_4 + … and recover
        #     L_4 = ∂_t Λ_4 − L_2 ∘ Λ_2 numerically. Sidesteps the
        #     analytic derivation but must live behind a clearly named
        #     extraction module (e.g. benchmarks/numerical_tcl_extraction
        #     or similar) — NOT promoted to cbg.tcl_recursion core API,
        #     since cbg should not depend on benchmarks/.
        #   Path C. Independent third-method extraction (HEOM, TEMPO,
        #     pseudomode at order 4). Largest scope; properly its own work
        #     plan rather than a DG-4 substep.
        raise NotImplementedError(
            "L_n_thermal_at_time: n=4 deferred. Three routes to a correct "
            "L_4: (A) Companion Sec. IV closed form (paper-bearing); "
            "(B) numerical Λ_t Richardson extraction via "
            "benchmarks/exact_finite_env (kept behind a named extraction "
            "module, not promoted to cbg.tcl_recursion core); (C) HEOM/"
            "TEMPO/pseudomode third-method extraction (own work plan). "
            "See the inline derivation/falsification notes above and "
            "logbook/2026-05-06_dg-4-phase-b2-tcl-order-3.md for routing."
        )

    if n == 2:
        if D_bar_2_array is None:
            raise ValueError(
                "L_n_thermal_at_time: n=2 requires D_bar_2_array (use "
                "cbg.cumulants.D_bar_2 to construct)"
            )

        H_S = np.asarray(system_hamiltonian, dtype=complex)
        A = np.asarray(coupling_operator, dtype=complex)
        t_grid = np.asarray(t_grid, dtype=float)
        D = np.asarray(D_bar_2_array, dtype=complex)

        if t_idx < 1:
            # Integration interval has zero length; L_2(t=t_grid[0]) = 0.
            d = A.shape[0]
            return lambda X: np.zeros((d, d), dtype=complex)

        # Pre-compute A_I(u - t) for each s in s_grid = t_grid[:t_idx+1].
        # u = s, u - t = s - t (≤ 0).
        s_grid = t_grid[: t_idx + 1]
        n_s = len(s_grid)
        t_at = t_grid[t_idx]
        A_I_array = np.zeros((n_s, *A.shape), dtype=complex)
        for s_idx in range(n_s):
            tau = s_grid[s_idx] - t_at  # ≤ 0
            A_I_array[s_idx] = interaction_picture(H_S, A, tau)

        # C(t - s) = D̄_2(t, s) (stationary; depends only on the difference).
        C_at = D[t_idx, : t_idx + 1]  # shape (n_s,)
        C_at_conj = np.conj(C_at)

        def L_2_apply(X: np.ndarray) -> np.ndarray:
            X = np.asarray(X, dtype=complex)
            d = X.shape[0]
            # Build integrand[s_idx] = C(t-s) [A, A_I(s-t) X]
            #                          + C(t-s)* [X A_I(s-t), A]
            integrand = np.zeros((n_s, d, d), dtype=complex)
            for s_idx in range(n_s):
                A_I_su = A_I_array[s_idx]
                # [A, A_I X] = A @ A_I @ X - A_I @ X @ A
                term1 = A @ A_I_su @ X - A_I_su @ X @ A
                # [X A_I, A] = X @ A_I @ A - A @ X @ A_I
                term2 = X @ A_I_su @ A - A @ X @ A_I_su
                integrand[s_idx] = C_at[s_idx] * term1 + C_at_conj[s_idx] * term2

            # Trapezoidal integral over s; result is (d, d).
            out = np.zeros((d, d), dtype=complex)
            for i in range(n_s - 1):
                ds = s_grid[i + 1] - s_grid[i]
                out += 0.5 * (integrand[i] + integrand[i + 1]) * ds
            return -out  # the leading minus sign in the TCL2 formula

        return L_2_apply

    raise NotImplementedError(
        f"L_n_thermal_at_time: n={n} not implemented. DG-4 Phase B.2 "
        f"covers n in {{0, 1, 2, 3}} on the thermal-Gaussian path "
        f"(n=4 deferred; see the dedicated branch). Orders n >= 5 are "
        f"out of scope for this plan revision."
    )


# ─── K_n on the time grid (Letter Eq. (6) extraction) ───────────────────────


def K_n_thermal_on_grid(
    n: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    basis: list | None = None,
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> np.ndarray:
    """Compute K_n(t) at every t in t_grid for a thermal Gaussian bath.

    For each t_idx, applies Letter Eq. (6) — K = (1/(2id)) Σ_α [F_α†, L[F_α]] —
    to L_n_thermal_at_time(n, t_idx, ...) using the matrix-unit basis (or
    a caller-supplied HS-orthonormal basis).

    Parameters
    ----------
    n : int
        Perturbative order; one of 0, 1, 2, 3 in the currently implemented
        thermal path. n = 3 returns zeros for any system coupling under a
        thermal Gaussian bath (Phase B.2; see L_n_thermal_at_time docstring).
        n = 4 is the pending Phase B follow-up: the parity-class theorem
        (Letter App. D) plus the Feynman-Vernon Gaussian-bath result
        predicts K_4 = 0 for A = σ_z and K_4 ≠ 0 (∝ σ_z) for A = σ_x; the
        latter is the leading-order convergence-detection signal D1 v0.1.2
        targets.
    t_grid : ndarray, shape (n_t,)
        Time points.
    system_hamiltonian, coupling_operator : ndarray, shape (d, d)
        H_S and A.
    bath_state, spectral_density : dict
        Card per-case bath_state and bath_spectral_density mappings.
        Used only for n = 2 (where D̄_2 is built); ignored for n in {0, 1}.
    basis : list of (d, d) ndarrays, optional
        HS-orthonormal basis for Letter Eq. (6). Defaults to the
        matrix-unit basis at the system dimension d.
    upper_cutoff_factor, quad_limit : optional
        Quadrature controls forwarded through D̄_2 construction for n = 2.

    Returns
    -------
    ndarray, shape (n_t, d, d), dtype complex
        K_n(t_grid).

    Raises
    ------
    NotImplementedError
        If bath_state.family is not "thermal" in this thermal-only path.
        Use K_total_displaced_on_grid for Council-cleared coherent-
        displaced benchmark-card cases.
    """
    if n >= 1:
        family = bath_state.get("family")
        if family != "thermal":
            raise NotImplementedError(
                f"K_n_thermal_on_grid: bath_state.family {family!r} at "
                f"n={n} is not supported by this thermal-only path. Use "
                f"K_total_displaced_on_grid for Council-cleared coherent-"
                f"displaced benchmark-card cases."
            )

    H_S = np.asarray(system_hamiltonian, dtype=complex)
    A = np.asarray(coupling_operator, dtype=complex)
    t_grid = np.asarray(t_grid, dtype=float)
    d = H_S.shape[0]

    if basis is None:
        basis = matrix_unit_basis(d)

    # For n = 2, precompute the D̄_2 array once (reused across all t_idx).
    D = None
    if n == 2:
        D = D_bar_2(
            t_grid,
            bath_state=bath_state,
            spectral_density=spectral_density,
            upper_cutoff_factor=upper_cutoff_factor,
            quad_limit=quad_limit,
        )

    K = np.zeros((len(t_grid), d, d), dtype=complex)
    for t_idx in range(len(t_grid)):
        L_n_apply = L_n_thermal_at_time(n, t_idx, t_grid, H_S, A, D_bar_2_array=D)
        K[t_idx] = K_from_generator(L_n_apply, basis)
    return K


# ─── L_n^dissipator (Phase B.3) ──────────────────────────────────────────────
#
# Convention: with cbg.effective_hamiltonian using L[X] = -i[K, X] + dissipator,
# the dissipator residual after subtracting the Hamiltonian piece is
#
#     L_n^dissipator(t) := L_n(t) + i [K_n(t), · ]
#
# The unitary-recovery oracle (Risk R8 in DG-4 work plan v0.1.3): for any
# purely unitary L = -i [H, ·], K_from_generator returns H (or its traceless
# part), so L^dissipator = L + i [K, ·] = -i [H, ·] + i [H, ·] = 0 exactly.
# Tests guarantee this for n=0 (where L_0 = -i [H_S, ·] is purely unitary).
#
# Phase B.3 partial: n in {0, 1, 2, 3}. n=4 is gated by L_n_thermal_at_time
# at the L-level; the deferral propagates here.


def L_n_dissipator_thermal_at_time(
    n: int,
    t_idx: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    basis: list | None = None,
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
    K_n_array: np.ndarray | None = None,
    D_bar_2_array: np.ndarray | None = None,
) -> Callable[[np.ndarray], np.ndarray]:
    """Return a callable that applies L_n^dissipator[X] at t_grid[t_idx].

    L_n^dissipator(t) := L_n(t) + i [K_n(t), · ]

    For purely unitary L_n with K_n = H, the dissipator vanishes
    identically (the Risk R8 unitary-recovery oracle gating Phase B.3
    acceptance). For thermal Gaussian baths n ∈ {0, 1, 3} all give the
    zero superoperator; n = 2 carries the leading dissipator.

    Parameters
    ----------
    n : int
        Perturbative order; one of {0, 1, 2, 3}. n=4 raises (gated by
        L_n_thermal_at_time(n=4)); n>=5 is out of scope.
    t_idx : int
        Index into t_grid at which to evaluate.
    t_grid, system_hamiltonian, coupling_operator : as in K_n_thermal_on_grid.
    bath_state, spectral_density : as in K_n_thermal_on_grid; consumed for
        n=2 K_n / D_bar_2 construction. Required even at n in {0, 1, 3}
        for signature uniformity (the K_n call still flows through but
        returns zeros at those orders).
    basis : optional HS-orthonormal basis for Letter Eq. (6) extraction.
    upper_cutoff_factor, quad_limit : forwarded to D_bar_2.
    K_n_array : optional precomputed (n_t, d, d) K_n array; useful when
        evaluating across many t_idx values to amortise the K_n cost.
    D_bar_2_array : optional precomputed (n_t, n_t) D_bar_2 array; same
        amortisation rationale.

    Returns
    -------
    callable (X: (d, d) ndarray) -> (d, d) ndarray
    """
    H_S = np.asarray(system_hamiltonian, dtype=complex)
    A = np.asarray(coupling_operator, dtype=complex)
    t_grid = np.asarray(t_grid, dtype=float)
    d = H_S.shape[0]

    if basis is None:
        basis = matrix_unit_basis(d)

    if K_n_array is None:
        K_n_array = K_n_thermal_on_grid(
            n,
            t_grid,
            H_S,
            A,
            bath_state=bath_state,
            spectral_density=spectral_density,
            basis=basis,
            upper_cutoff_factor=upper_cutoff_factor,
            quad_limit=quad_limit,
        )

    if D_bar_2_array is None and n == 2:
        D_bar_2_array = D_bar_2(
            t_grid,
            bath_state=bath_state,
            spectral_density=spectral_density,
            upper_cutoff_factor=upper_cutoff_factor,
            quad_limit=quad_limit,
        )

    L_n_apply = L_n_thermal_at_time(n, t_idx, t_grid, H_S, A, D_bar_2_array=D_bar_2_array)
    K_t = np.asarray(K_n_array[t_idx], dtype=complex)

    def L_n_dis_apply(X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=complex)
        return L_n_apply(X) + 1j * (K_t @ X - X @ K_t)

    return L_n_dis_apply


def L_n_dissipator_norm_thermal_on_grid(
    n: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    basis: list | None = None,
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> np.ndarray:
    """Return ||L_n^dissipator(t)||_F at every t in t_grid.

    The norm is the Frobenius norm of the d²×d² Liouville-representation
    matrix of the superoperator L_n^dissipator in the supplied (or
    matrix-unit) HS-orthonormal basis: the standard Hilbert-Schmidt
    norm of a superoperator. This is the per-t signal that DG-4 work
    plan v0.1.3 §1.1 designates as the convergence-ratio numerator
    (D1 v0.1.2's metric).

    For thermal Gaussian baths under the runner-facing thermal path,
    n ∈ {0, 1, 3} return all zeros and n = 2 returns the dephasing /
    relaxation dissipator's norm at each grid time. n = 4 is deferred
    along with L_n_thermal_at_time(n=4).

    Parameters
    ----------
    Same as L_n_dissipator_thermal_at_time, minus t_idx and the
    optional precomputed-array shortcuts.

    Returns
    -------
    ndarray, shape (n_t,), dtype float
        ||L_n^dissipator(t)||_F at each t in t_grid.
    """
    H_S = np.asarray(system_hamiltonian, dtype=complex)
    A = np.asarray(coupling_operator, dtype=complex)
    t_grid = np.asarray(t_grid, dtype=float)
    d = H_S.shape[0]

    if basis is None:
        basis = matrix_unit_basis(d)

    # Precompute K_n and (when n=2) D_bar_2 once; amortise across t_idx.
    K_n_array = K_n_thermal_on_grid(
        n,
        t_grid,
        H_S,
        A,
        bath_state=bath_state,
        spectral_density=spectral_density,
        basis=basis,
        upper_cutoff_factor=upper_cutoff_factor,
        quad_limit=quad_limit,
    )
    D = None
    if n == 2:
        D = D_bar_2(
            t_grid,
            bath_state=bath_state,
            spectral_density=spectral_density,
            upper_cutoff_factor=upper_cutoff_factor,
            quad_limit=quad_limit,
        )

    n_t = len(t_grid)
    norms = np.zeros(n_t, dtype=float)
    d_sq = d * d
    for t_idx in range(n_t):
        L_dis = L_n_dissipator_thermal_at_time(
            n,
            t_idx,
            t_grid,
            H_S,
            A,
            bath_state=bath_state,
            spectral_density=spectral_density,
            basis=basis,
            upper_cutoff_factor=upper_cutoff_factor,
            quad_limit=quad_limit,
            K_n_array=K_n_array,
            D_bar_2_array=D,
        )
        # Liouville matrix in the HS-orthonormal basis: M[α, β] = ⟨F_α, L[F_β]⟩.
        L_matrix = np.zeros((d_sq, d_sq), dtype=complex)
        for col, F_col in enumerate(basis):
            L_F = L_dis(F_col)
            for row, F_row in enumerate(basis):
                L_matrix[row, col] = np.trace(F_row.conj().T @ L_F)
        norms[t_idx] = float(np.linalg.norm(L_matrix, ord="fro"))
    return norms


# ─── Displaced-bath L_n / K_n / K_total (Council Act 2 cleared, 2026-05-04) ──
#
# The displaced-bath path is structurally similar to the thermal path: K_0
# (bare Liouvillian) and K_2 (TCL2 dissipator) are unchanged because D̄_2
# (the connected two-point) is invariant under coherent displacement. The
# only change is K_1, which is non-zero in the displaced case where
# D̄_1(t) ≠ 0:
#
#   L_1^S[X](t) = -i D̄_1(t) [A, X]    (Schrödinger picture)
#
# Applying Letter Eq. (6) to L_1^S gives K_1(t) = D̄_1(t) · (A − Tr(A)/d · I).
# For traceless A (σ_z, σ_x), K_1(t) = D̄_1(t) · A. The runner extracts
# K_1 via K_from_generator without bypassing the basis-summation pipeline
# — preserving the cards-first audit boundary.


def L_1_displaced_at_time(
    t_idx: int,
    coupling_operator: np.ndarray,
    D_bar_1_array: np.ndarray,
) -> Callable[[np.ndarray], np.ndarray]:
    """Schrödinger-picture L_1 generator at t_grid[t_idx] for a coherent-
    displaced bath.

    L_1^S[X](t) = -i D̄_1(t) [A, X]

    Parameters
    ----------
    t_idx : int
        Index into the time grid at which D̄_1 is evaluated.
    coupling_operator : ndarray
        System coupling operator A, shape (d, d).
    D_bar_1_array : ndarray
        Precomputed ⟨B(t)⟩ on the time grid; produced by
        cbg.cumulants.D_bar_1 with the case's bath_state and
        spectral_density.

    Returns
    -------
    callable (X: (d, d) ndarray) -> (d, d) ndarray
    """
    A = np.asarray(coupling_operator, dtype=complex)
    d_bar_1_t = complex(D_bar_1_array[t_idx])

    def L_1_apply(X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=complex)
        return -1j * d_bar_1_t * (A @ X - X @ A)

    return L_1_apply


def K_total_displaced_on_grid(
    N_card: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    basis: list | None = None,
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> np.ndarray:
    """Compute K(t) = Σ_{n=0}^{N_card} K_n(t) for a coherent-displaced bath.

    Reuses ``L_n_thermal_at_time`` for n = 0 (bare Liouvillian, bath-state-
    independent) and n = 2 (TCL2 dissipator, D̄_2 invariant under
    displacement). For n = 1, dispatches to ``L_1_displaced_at_time``
    using the per-profile D̄_1 array from ``cbg.cumulants.D_bar_1`` (which
    routes through the Council-cleared displacement-profile registry).

    Parameters
    ----------
    N_card : int
        Perturbative cap (must be in {0, 1, 2} per the existing thermal
        path's range; v0.1.0 cards use N_card = 2).
    t_grid : ndarray, shape (n_t,)
        Time points.
    system_hamiltonian, coupling_operator : ndarray, shape (d, d)
    bath_state : dict
        Must have family == "coherent_displaced" and include the
        ``displacement_profile`` key per the §6.1 registry-clearance-gate.
    spectral_density : dict
        Card bath_spectral_density (ohmic at v0.1.0).
    basis : list of (d, d) ndarrays, optional
        HS-orthonormal basis for Letter Eq. (6); defaults to matrix_unit.
    upper_cutoff_factor, quad_limit : optional
        Quadrature controls forwarded through D̄_2 construction for n = 2.

    Returns
    -------
    ndarray, shape (n_t, d, d), dtype complex
        K(t_grid) under the displaced bath.

    Raises
    ------
    ValueError
        If N_card is not a non-negative integer.
    NotImplementedError
        If N_card > 2 (DG-2-recursion territory; out of scope).
    """
    if not isinstance(N_card, int) or isinstance(N_card, bool) or N_card < 0:
        raise ValueError(
            f"K_total_displaced_on_grid: N_card must be a non-negative integer; " f"got {N_card!r}"
        )
    if N_card > 2:
        raise NotImplementedError(
            f"K_total_displaced_on_grid: N_card={N_card} not implemented. "
            f"K_n at orders n >= 3 is out of scope (future K_2-K_4 "
            f"numerical-recursion plan)."
        )
    if bath_state.get("family") != "coherent_displaced":
        raise ValueError(
            f"K_total_displaced_on_grid: bath_state.family must be "
            f"'coherent_displaced'; got {bath_state.get('family')!r}. "
            f"For thermal, use K_total_thermal_on_grid."
        )

    H_S = np.asarray(system_hamiltonian, dtype=complex)
    A = np.asarray(coupling_operator, dtype=complex)
    t_grid = np.asarray(t_grid, dtype=float)
    d = H_S.shape[0]

    if basis is None:
        basis = matrix_unit_basis(d)

    # Precompute D̄_1 (per-profile) and D̄_2 (thermal-baseline; invariant
    # under displacement). D̄_2 needs a temperature; for an unspecified
    # vacuum-baseline displaced state the natural choice is T = 0, but
    # the bath_state may carry a temperature override (e.g. for
    # thermal-on-top-of-displaced studies). Current cards do not set
    # temperature on coherent_displaced bath_states; default to 0.
    D_bar_1_array = (
        D_bar_1(
            t_grid,
            bath_state=bath_state,
            spectral_density=spectral_density,
        )
        if N_card >= 1
        else None
    )

    # For D̄_2 we forward to the existing connected-two-point evaluator
    # at the spec's temperature (or T=0 default). The evaluator already
    # handles bath_state.family == "coherent_displaced" by treating the
    # connected part as the thermal baseline (see cbg.bath_correlations
    # module docstring).
    D_bar_2_array = None
    if N_card >= 2:
        bs_for_d2 = dict(bath_state)
        if "temperature" not in bs_for_d2:
            bs_for_d2["temperature"] = 0.0
        D_bar_2_array = D_bar_2(
            t_grid,
            bath_state=bs_for_d2,
            spectral_density=spectral_density,
            upper_cutoff_factor=upper_cutoff_factor,
            quad_limit=quad_limit,
        )

    K = np.zeros((len(t_grid), d, d), dtype=complex)
    for t_idx in range(len(t_grid)):
        # n = 0: bare Liouvillian (bath-state-independent).
        L0 = L_n_thermal_at_time(0, t_idx, t_grid, H_S, A)
        K[t_idx] += K_from_generator(L0, basis)
        # n = 1: displaced contribution.
        if N_card >= 1:
            assert D_bar_1_array is not None
            L1 = L_1_displaced_at_time(t_idx, A, D_bar_1_array)
            K[t_idx] += K_from_generator(L1, basis)
        # n = 2: TCL2 dissipator (D̄_2 invariant; same as thermal).
        if N_card >= 2:
            L2 = L_n_thermal_at_time(
                2,
                t_idx,
                t_grid,
                H_S,
                A,
                D_bar_2_array=D_bar_2_array,
            )
            K[t_idx] += K_from_generator(L2, basis)
    return K


def K_total_thermal_on_grid(
    N_card: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    basis: list | None = None,
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> np.ndarray:
    """Compute K(t) = Σ_{n=0}^{N_card} K_n(t) at every t in t_grid for a
    thermal Gaussian bath.

    The runner-facing entry point: returns the full effective Hamiltonian
    on the time grid, ready for comparison against a card's expected_outcome.

    Parameters
    ----------
    N_card : int
        Perturbative cap from the card's frozen_parameters.truncation
        .perturbative_order; must be in {0, 1, 2} for the implemented
        low-order path.
    t_grid : ndarray
        See ``K_n_thermal_on_grid``.
    system_hamiltonian : ndarray
        See ``K_n_thermal_on_grid``.
    coupling_operator : ndarray
        See ``K_n_thermal_on_grid``.
    bath_state : dict
        See ``K_n_thermal_on_grid``.
    spectral_density : dict
        See ``K_n_thermal_on_grid``.
    basis : list, optional
        See ``K_n_thermal_on_grid``.
    upper_cutoff_factor : float
        See ``K_n_thermal_on_grid``.
    quad_limit : int
        See ``K_n_thermal_on_grid``.

    Returns
    -------
    ndarray, shape (n_t, d, d), dtype complex
        K(t_grid).
    """
    if not isinstance(N_card, int) or isinstance(N_card, bool) or N_card < 0:
        raise ValueError(
            f"K_total_thermal_on_grid: N_card must be a non-negative integer; " f"got {N_card!r}"
        )
    if N_card > 3:
        raise NotImplementedError(
            f"K_total_thermal_on_grid: N_card={N_card} not implemented. "
            f"DG-4 Phase B.2 covers n in {{0, 1, 2, 3}} (n=3 returns zeros "
            f"by Gaussianity). n=4 is the pending follow-up; see "
            f"L_n_thermal_at_time(n=4)."
        )

    H_S = np.asarray(system_hamiltonian, dtype=complex)
    d = H_S.shape[0]
    K = np.zeros((len(t_grid), d, d), dtype=complex)

    for n in range(N_card + 1):
        K += K_n_thermal_on_grid(
            n,
            t_grid,
            system_hamiltonian,
            coupling_operator,
            bath_state=bath_state,
            spectral_density=spectral_density,
            basis=basis,
            upper_cutoff_factor=upper_cutoff_factor,
            quad_limit=quad_limit,
        )
    return K


# ─── Existing-stub-signature shim ────────────────────────────────────────────


def L_n(n: int, **kwargs):
    """Compute the n-th order TCL generator term per Companion Eq. (28).

    Thin wrapper: routes to L_n_thermal_at_time when called with
    the canonical (t_idx, t_grid, system_hamiltonian, coupling_operator,
    D_bar_2_array) kwargs and a thermal bath state. Other configurations
    raise NotImplementedError with explicit pending-recursion routing.

    Callers should generally prefer L_n_thermal_at_time (explicit
    parameters) or K_n_thermal_on_grid (higher-level batched form) over
    this generic-stub shim.
    """
    if n >= 4:
        raise NotImplementedError(
            f"L_n: n={n} not implemented; DG-4 Phase B.2 covers "
            f"n in {{0, 1, 2, 3}} (n=3 returns zero by Gaussianity). "
            f"n=4 is the next deferred piece; see L_n_thermal_at_time(n=4)."
        )
    bath_state = kwargs.get("bath_state")
    if bath_state is not None and bath_state.get("family") != "thermal":
        raise NotImplementedError(
            "L_n: non-thermal generic dispatch is not implemented here. "
            "Use K_total_displaced_on_grid for Council-cleared coherent-"
            "displaced benchmark-card cases."
        )
    required = ("t_idx", "t_grid", "system_hamiltonian", "coupling_operator")
    missing = [k for k in required if k not in kwargs]
    if missing:
        raise ValueError(
            f"L_n: missing required kwargs {missing}; pass "
            f"(t_idx, t_grid, system_hamiltonian, coupling_operator) "
            f"and (D_bar_2_array for n=2)."
        )
    return L_n_thermal_at_time(
        n=n,
        t_idx=kwargs["t_idx"],
        t_grid=kwargs["t_grid"],
        system_hamiltonian=kwargs["system_hamiltonian"],
        coupling_operator=kwargs["coupling_operator"],
        D_bar_2_array=kwargs.get("D_bar_2_array"),
    )


# ─── Pending: full canonical Lindblad decomposition ─────────────────────────


def canonical_lindblad_form(L_generator: Callable):
    """Decompose L into K (Hamiltonian part) + canonical dissipator with
    traceless jump operators, per Companion Eq. (43).

    Current benchmark-card runners only need K (via Letter Eq. (6); use
    cbg.effective_hamiltonian.K_from_generator). The full K + traceless-
    dissipator decomposition remains pending.
    """
    raise NotImplementedError(
        "canonical_lindblad_form: not implemented. The K + traceless-"
        "dissipator decomposition (Companion Eq. (43)) remains pending; "
        "current benchmark-card runners use K_from_generator via Letter "
        "Eq. (6)."
    )

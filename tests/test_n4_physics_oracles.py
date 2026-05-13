# SPDX-License-Identifier: MIT
"""DG-4 Phase C physics oracles for assembled L_4.

Verification card (current):
    transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_
    phase-c-physics-oracles-card_v0.1.3.md  (frozen 2026-05-13,
    errata). Errata-supersedes v0.1.2 to re-pin the Part B reference
    table after the post-review cube-domain fix at commit `3e50e94`
    and to correct the Part B grid annotation ("t_end=1.0 independent
    of §2 fixture", not "at the §2 fixture" as v0.1.2 stated).
    All gating oracles, fixtures, and integration discipline unchanged
    from v0.1.2.

The two-part σ_z gate (carried forward from v0.1.2):
    - Part A: commuting-case Feynman-Vernon exact-zero via §3.2 API
      guard at atol=1e-12. This is the acceptance gate.
    - Part B: literal-quadrature convergence diagnostic on a
      refinement table. Monotonic-decrease assertion only; NOT a gate.

Parent transcription:
    transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md
    (released 2026-05-12).

Phase B helper consumed:
    cbg.tcl_recursion._D_bar_4_companion (landed at commit becccf9).

The card pins:
    - §2 D1 v0.1.2-baseline-style fixture (σ_x or σ_z coupling per
      oracle; ω = 1.0; ohmic α = 0.02, ω_c = 10.0; thermal T = 0.5;
      time grid linspace(0, 2.0, 11); t_idx = 5; matrix-unit basis);
    - §3 API contract for `_L_4_thermal_at_time_apply` plus §3.2
      commuting-case guard.
    - §3a θ-aware literal Eqs. (69)-(73) integration discipline.
    - §4 four oracle gates:
        4.1 Part A: σ_z exact-zero via guard at atol = 1e-12.
        4.1 Part B: literal-quadrature convergence diagnostic on
            n_pts ∈ {11, 21, 41, 81}; monotonic decrease.
        4.2 σ_x signal oracle: 1e-6 ≤ ‖L_4^dis‖_F ≤ 1e6.
        4.3.a L_0^dis = 0 at atol = 1e-12.
        4.3.b n=2 dissipator regression at atol = rtol = 1e-12.
        4.4 L_1 = L_3 = 0 at atol = 1e-12.

Phase C scope: private-route oracles. The public
L_n_thermal_at_time(n=4) was exposed in Phase D (commit `f599751`)
and now routes through `_L_4_thermal_at_time_apply` for thermal
Gaussian; the Phase C oracles in this file still call the private
helpers directly for back-to-back regression coverage.
"""

from __future__ import annotations

import numpy as np
import pytest

from cbg.basis import matrix_unit_basis
from cbg.cumulants import D_bar_2
from cbg.effective_hamiltonian import K_from_generator
from cbg.tcl_recursion import (
    L_n_thermal_at_time,
    _L_4_thermal_at_time_apply,
    _L_4_thermal_at_time_apply_no_guard,
)

# ─── §2 Frozen shared fixture ────────────────────────────────────────────────

OMEGA = 1.0
SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
H_S = 0.5 * OMEGA * SIGMA_Z

BATH_STATE = {"family": "thermal", "temperature": 0.5}
SPECTRAL_DENSITY = {
    "family": "ohmic",
    "coupling_strength": 0.02,
    "cutoff_frequency": 10.0,
}
UPPER_CUTOFF_FACTOR = 30.0
QUAD_LIMIT = 200

T_GRID = np.linspace(0.0, 2.0, 11)  # dt = 0.2
T_IDX = 5  # t = 1.0; mid-grid, away from t = 0
BASIS = matrix_unit_basis(2)

# ─── Tolerances ──────────────────────────────────────────────────────────────

ATOL_EXACT_ZERO = 1e-12  # §4.1 Part A, §4.3, §4.4 machine-zero gates
SIGMA_X_LOWER = 1e-6  # §4.2 lower bound
SIGMA_X_UPPER = 1e6  # §4.2 upper bound


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _build_superoperator(apply_fn, basis):
    """Build the (d^2, d^2) matrix representation of a superoperator."""
    d2 = len(basis)
    S = np.zeros((d2, d2), dtype=complex)
    for j, X in enumerate(basis):
        Y = apply_fn(X)
        for i, E in enumerate(basis):
            S[i, j] = np.trace(E.conj().T @ Y)
    return S


def _L_4_dis_apply(L_4_apply, basis):
    """L_4^dis[X] = L_4[X] + i [K_4, X], with K_4 = K_from_generator(L_4)."""
    K_4 = K_from_generator(L_4_apply, basis=basis)

    def apply(X):
        return L_4_apply(X) + 1j * (K_4 @ X - X @ K_4)

    return apply


# ─── §4.1 Part A: σ_z zero oracle via commuting-case guard ───────────────────


@pytest.fixture(scope="module")
def L_4_apply_sigma_z():
    """Build L_4 callable for σ_z (commuting-case guard fires per §3.2)."""
    return _L_4_thermal_at_time_apply(
        t_idx=T_IDX,
        t_grid=T_GRID,
        system_hamiltonian=H_S,
        coupling_operator=SIGMA_Z,
        bath_state=BATH_STATE,
        spectral_density=SPECTRAL_DENSITY,
        upper_cutoff_factor=UPPER_CUTOFF_FACTOR,
        quad_limit=QUAD_LIMIT,
    )


@pytest.mark.parametrize("X_idx", [0, 1, 2, 3], ids=["E00", "E01", "E10", "E11"])
def test_sigma_z_zero_oracle_part_a_exact_zero(L_4_apply_sigma_z, X_idx):
    """Card §4.1 Part A: L_4[X] = 0 exactly for A = σ_z (Feynman-Vernon).

    Acceptance gate. The §3.2 API guard fires because [H_S, σ_z] = 0,
    returning a callable that yields the zero matrix at machine
    precision regardless of X.
    """
    X = BASIS[X_idx]
    val = L_4_apply_sigma_z(X)
    np.testing.assert_allclose(
        val,
        np.zeros_like(val),
        atol=ATOL_EXACT_ZERO,
        err_msg=f"σ_z exact-zero oracle failed at X_idx={X_idx}",
    )


# ─── §4.1 Part B: literal-quadrature convergence diagnostic (non-gating) ─────

# Reference values measured AFTER the v0.1.2 review's domain-shape fix
# (cube → outer-simplex-intersected domains for 4 subtraction terms; see the
# v0.1.1 → v0.1.2 supersession in the parent card). Diagnostic uses a
# t_end=1.0 grid (NOT the §2 t_end=2.0 fixture) for fast iteration across
# n_pts ∈ {11, 21, 41, 81}; the diagnostic is non-gating, so the grid choice
# is independent of the §2 fixture used by the gating oracles.
# rtol=0.1 tolerance allows for bath-quadrature numerical noise.
PART_B_REFERENCE = {
    11: 1.28e-2,
    21: 1.17e-2,
    41: 7.48e-3,
    81: 5.09e-3,
}


def test_sigma_z_part_b_convergence_diagnostic(capsys):
    """Card §4.1 Part B: literal-quadrature convergence diagnostic.

    NOT an acceptance gate. Documents that the v0.1.1 §3a θ-aware
    literal integration (with the v0.1.2 outer-simplex domain
    intersection) converges monotonically toward zero as the grid is
    refined. The first-run measurements are pinned in PART_B_REFERENCE;
    tolerance 10% (rtol=0.1) accommodates the bath quadrature noise floor.

    The diagnostic uses `_L_4_thermal_at_time_apply_no_guard` to
    bypass the §3.2 commuting-case guard and exercise the literal
    θ-aware integration on σ_z. In production, the guard short-
    circuits this path to exact zero.

    Diagnostic grid: t_end=1.0 (not §2's t_end=2.0). The diagnostic is
    non-gating, so its grid choice is independent of the gating oracles.
    The shorter t_end keeps the diagnostic runtime tractable across
    n_pts ∈ {11, 21, 41, 81}.
    """
    values = {}
    for n_pts in PART_B_REFERENCE:
        t_grid = np.linspace(0.0, 1.0, n_pts)
        L_4_no_guard = _L_4_thermal_at_time_apply_no_guard(
            t_idx=n_pts - 1,
            t_grid=t_grid,
            system_hamiltonian=H_S,
            coupling_operator=SIGMA_Z,
            bath_state=BATH_STATE,
            spectral_density=SPECTRAL_DENSITY,
            upper_cutoff_factor=UPPER_CUTOFF_FACTOR,
            quad_limit=QUAD_LIMIT,
        )
        val = L_4_no_guard(BASIS[1])  # E_01
        norm = float(np.max(np.abs(val)))
        values[n_pts] = norm
        print(f"\n[card §4.1 Part B] n_pts={n_pts}: ‖L_4[E_01]‖_F = {norm:.4e}")

    # Monotonic decrease: residual at finer grid <= residual at coarser grid.
    n_pts_sorted = sorted(values.keys())
    for prev, curr in zip(n_pts_sorted[:-1], n_pts_sorted[1:], strict=True):
        assert values[curr] < values[prev], (
            f"Convergence non-monotone: n={prev} gave {values[prev]:.3e}, "
            f"n={curr} gave {values[curr]:.3e}"
        )

    # Match the pinned reference table at rtol=0.1.
    for n_pts, expected in PART_B_REFERENCE.items():
        np.testing.assert_allclose(
            values[n_pts],
            expected,
            rtol=0.1,
            err_msg=f"Part B regression: n={n_pts} drifted from {expected:.3e}",
        )


# ─── §4.2 σ_x signal oracle ──────────────────────────────────────────────────


@pytest.fixture(scope="module")
def L_4_apply_sigma_x():
    """Build L_4 callable for σ_x (literal θ-aware integration runs)."""
    return _L_4_thermal_at_time_apply(
        t_idx=T_IDX,
        t_grid=T_GRID,
        system_hamiltonian=H_S,
        coupling_operator=SIGMA_X,
        bath_state=BATH_STATE,
        spectral_density=SPECTRAL_DENSITY,
        upper_cutoff_factor=UPPER_CUTOFF_FACTOR,
        quad_limit=QUAD_LIMIT,
    )


def test_sigma_x_signal_oracle(L_4_apply_sigma_x, capsys):
    """Card §4.2: ‖L_4^dis‖_F is finite and inside [1e-6, 1e6]."""
    L_4_dis_apply = _L_4_dis_apply(L_4_apply_sigma_x, BASIS)
    L_4_dis_super = _build_superoperator(L_4_dis_apply, BASIS)

    assert np.all(np.isfinite(L_4_dis_super)), "L_4^dis superoperator has non-finite entries"
    norm = float(np.linalg.norm(L_4_dis_super, "fro"))
    print(f"\n[card §4.2 first-run measurement] ‖L_4^dis‖_F = {norm:.12e}")
    assert SIGMA_X_LOWER <= norm <= SIGMA_X_UPPER, (
        f"‖L_4^dis‖_F = {norm:.3e} is outside the structural bounding box "
        f"[{SIGMA_X_LOWER:.0e}, {SIGMA_X_UPPER:.0e}]"
    )


# ─── §4.3.a Gauge/sign oracle: L_0^dis = 0 ───────────────────────────────────


@pytest.mark.parametrize("X_idx", [0, 1, 2, 3], ids=["E00", "E01", "E10", "E11"])
def test_L_0_dissipator_vanishes(X_idx):
    """Card §4.3.a: L_0^dis[X] = 0 at atol = 1e-12."""
    L_0_apply = L_n_thermal_at_time(
        n=0,
        t_idx=T_IDX,
        t_grid=T_GRID,
        system_hamiltonian=H_S,
        coupling_operator=SIGMA_X,
    )
    K_0 = K_from_generator(L_0_apply, basis=BASIS)
    X = BASIS[X_idx]
    L_0_dis = L_0_apply(X) + 1j * (K_0 @ X - X @ K_0)
    np.testing.assert_allclose(
        L_0_dis,
        np.zeros_like(L_0_dis),
        atol=ATOL_EXACT_ZERO,
        err_msg=f"L_0^dis ≠ 0 at X_idx={X_idx}",
    )


# ─── §4.3.b Gauge/sign oracle: n=2 regression at card-pinned reference ──────

L_2_BASIS1_REFERENCE = np.array(
    [
        [-0.0 - 0.0j, -0.26338525879711916 + 0.04707234985666798j],
        [0.26338525879711916 - 0.04707234985666798j, -0.0 - 0.0j],
    ],
    dtype=complex,
)


def test_L_2_n2_regression_marker():
    """Card §4.3.b: L_2[BASIS[1]] at the §2 fixture matches the card-pinned
    reference value at atol = rtol = 1e-12.
    """
    D_bar_2_array = D_bar_2(
        T_GRID,
        bath_state=BATH_STATE,
        spectral_density=SPECTRAL_DENSITY,
        upper_cutoff_factor=UPPER_CUTOFF_FACTOR,
        quad_limit=QUAD_LIMIT,
    )
    L_2_apply = L_n_thermal_at_time(
        n=2,
        t_idx=T_IDX,
        t_grid=T_GRID,
        system_hamiltonian=H_S,
        coupling_operator=SIGMA_X,
        D_bar_2_array=D_bar_2_array,
    )
    val = L_2_apply(BASIS[1])
    np.testing.assert_allclose(
        val,
        L_2_BASIS1_REFERENCE,
        atol=ATOL_EXACT_ZERO,
        rtol=ATOL_EXACT_ZERO,
        err_msg="L_2[BASIS[1]] regression against card-pinned reference",
    )


# ─── §4.4 Parity oracle: L_1 = L_3 = 0 ───────────────────────────────────────


@pytest.mark.parametrize("n", [1, 3])
@pytest.mark.parametrize("X_idx", [0, 1, 2, 3], ids=["E00", "E01", "E10", "E11"])
def test_parity_oracle_L_1_L_3_zero(n, X_idx):
    """Card §4.4: L_1[X] = L_3[X] = 0 at atol = 1e-12."""
    L_n_apply = L_n_thermal_at_time(
        n=n,
        t_idx=T_IDX,
        t_grid=T_GRID,
        system_hamiltonian=H_S,
        coupling_operator=SIGMA_X,
    )
    X = BASIS[X_idx]
    val = L_n_apply(X)
    np.testing.assert_allclose(
        val,
        np.zeros_like(val),
        atol=ATOL_EXACT_ZERO,
        err_msg=f"L_{n}[X] ≠ 0 at X_idx={X_idx}",
    )

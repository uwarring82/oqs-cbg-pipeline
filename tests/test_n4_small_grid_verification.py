# SPDX-License-Identifier: MIT
"""DG-4 Phase B small-grid verification of `_D_bar_4_companion`.

Verification card:
    transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_
    n4-small-grid-verification-card_v0.1.0.md  (frozen 2026-05-13).

Parent transcription:
    transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md
    (released 2026-05-12).

The card pins:
    - the §2 thermal-Gaussian ohmic bath fixture (α = 0.1, ω_c = 1.0,
      T = 1.0);
    - the §3 outer time t = 1.0 and two τ ↔ s mirror grids that fire
      exactly one boundary delta each (Grid α: τ_1 = t; Grid β: s_1 = t);
    - the §4 substitution rules: row-2.3 swap, Eq. (22) boundary delta
      with empty-chain convention, thermal Gaussian 4-point Wick split;
    - the §5 by-hand closed-form D̄ reference values for all 5 × 2 = 10
      (case, grid) pairs;
    - the §9 strict acceptance criterion: atol = rtol = 1e-10 (trivially
      zero cases checked at the same absolute tolerance).

This test hand-enumerates the §5 closed forms in plain Python using
`cbg.bath_correlations.two_point` to evaluate C(a, b) at the §2 fixture
and compares against the primary oracle `_D_bar_4_companion` from
`cbg.tcl_recursion`. The §8 secondary diagnostic (row-2.3 plumbing check
via `n_point_ordered`) is included as separate non-gating assertions.
"""

from __future__ import annotations

import numpy as np
import pytest

from cbg.bath_correlations import n_point_ordered, two_point
from cbg.tcl_recursion import _D_bar_4_companion

# ─── §2 Frozen bath fixture ──────────────────────────────────────────────────

BATH_STATE = {"family": "thermal", "temperature": 1.0}
SPECTRAL_DENSITY = {
    "family": "ohmic",
    "coupling_strength": 0.1,
    "cutoff_frequency": 1.0,
}
UPPER_CUTOFF_FACTOR = 30.0
QUAD_LIMIT = 200

# ─── §3 Frozen time grids ────────────────────────────────────────────────────

T_OUTER = 1.0

GRID_ALPHA = {  # τ_1 = t; δ_{τ_1,t} = 1, δ_{s_1,t} = 0
    "label": "alpha",
    "tau": (1.0, 0.7, 0.4, 0.2),
    "s": (0.9, 0.6, 0.3, 0.1),
}
GRID_BETA = {  # s_1 = t; δ_{τ_1,t} = 0, δ_{s_1,t} = 1
    "label": "beta",
    "tau": (0.9, 0.6, 0.3, 0.1),
    "s": (1.0, 0.7, 0.4, 0.2),
}

# ─── §9 Acceptance tolerances ────────────────────────────────────────────────

ATOL = 1e-10
RTOL = 1e-10


# ─── Helpers ─────────────────────────────────────────────────────────────────


def C(a: float, b: float) -> complex:
    """Numerical ⟨B(a) B(b)⟩ = C(a, b) at the §2 fixture."""
    return two_point(
        a,
        b,
        bath_state=BATH_STATE,
        spectral_density=SPECTRAL_DENSITY,
        upper_cutoff_factor=UPPER_CUTOFF_FACTOR,
        quad_limit=QUAD_LIMIT,
    )


def primary(tau_args, s_args) -> complex:
    """Call the Phase B direct evaluator under test."""
    return _D_bar_4_companion(
        tau_args,
        s_args,
        t=T_OUTER,
        bath_state=BATH_STATE,
        spectral_density=SPECTRAL_DENSITY,
        upper_cutoff_factor=UPPER_CUTOFF_FACTOR,
        quad_limit=QUAD_LIMIT,
    )


def slice_grid(grid: dict, k: int) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Take the leading k τ's and leading 4 − k s's per card §3 convention."""
    return grid["tau"][:k], grid["s"][: 4 - k]


# ─── §5 Independent oracle — hand-enumerated closed forms ────────────────────


def expected_grid_alpha(k: int) -> complex:
    """§5.1 closed forms at Grid α (δ_{τ_1,t}=1, δ_{s_1,t}=0)."""
    tau = GRID_ALPHA["tau"]
    s = GRID_ALPHA["s"]
    if k == 0:
        return 0.0 + 0.0j  # §5.1: trivially zero
    if k == 1:
        t1 = tau[0]
        s1, s2, s3 = s[0], s[1], s[2]
        return C(s3, s1) * C(s2, t1) + C(s3, t1) * C(s2, s1)
    if k == 2:
        t1, t2 = tau[0], tau[1]
        s1, s2 = s[0], s[1]
        return C(s2, t1) * C(s1, t2)
    if k == 3:
        t1, t2, t3 = tau[0], tau[1], tau[2]
        s1 = s[0]
        return C(s1, t2) * C(t1, t3)
    if k == 4:
        t1, t2, t3, t4 = tau
        return C(t1, t3) * C(t2, t4) + C(t1, t4) * C(t2, t3)
    raise AssertionError(f"unreachable k={k}")


def expected_grid_beta(k: int) -> complex:
    """§5.2 closed forms at Grid β (δ_{τ_1,t}=0, δ_{s_1,t}=1)."""
    tau = GRID_BETA["tau"]
    s = GRID_BETA["s"]
    if k == 0:
        s1, s2, s3, s4 = s
        return C(s4, s2) * C(s3, s1) + C(s4, s1) * C(s3, s2)
    if k == 1:
        t1 = tau[0]
        s1, s2, s3 = s[0], s[1], s[2]
        return C(s3, s1) * C(s2, t1)
    if k == 2:
        t1, t2 = tau[0], tau[1]
        s1, s2 = s[0], s[1]
        return C(s2, t1) * C(s1, t2)
    if k == 3:
        t1, t2, t3 = tau[0], tau[1], tau[2]
        s1 = s[0]
        return C(s1, t2) * C(t1, t3) + C(s1, t3) * C(t1, t2)
    if k == 4:
        return 0.0 + 0.0j  # §5.2: trivially zero
    raise AssertionError(f"unreachable k={k}")


def expected(grid: dict, k: int) -> complex:
    if grid["label"] == "alpha":
        return expected_grid_alpha(k)
    if grid["label"] == "beta":
        return expected_grid_beta(k)
    raise AssertionError(f"unknown grid {grid['label']!r}")


# ─── Acceptance gate (§9) ────────────────────────────────────────────────────


@pytest.mark.parametrize("k", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("grid", [GRID_ALPHA, GRID_BETA], ids=["alpha", "beta"])
def test_D_bar_4_companion_matches_independent_oracle(grid, k):
    """Card §9: primary oracle equals §5 closed form within atol = rtol = 1e-10.

    Trivially-zero cases (k=0 at Grid α and k=4 at Grid β) are checked
    at the same absolute tolerance (the relative comparison is degenerate
    at zero, per the card §9 closing bullet).
    """
    tau_args, s_args = slice_grid(grid, k)
    actual = primary(tau_args, s_args)
    target = expected(grid, k)

    if target == 0.0:
        assert abs(actual) <= ATOL, (
            f"grid={grid['label']!r} k={k}: |actual|={abs(actual):.3e} " f"exceeds atol={ATOL:.0e}"
        )
    else:
        np.testing.assert_allclose(
            actual,
            target,
            atol=ATOL,
            rtol=RTOL,
            err_msg=f"grid={grid['label']!r} k={k}",
        )


# ─── Built-in §5.3 consistency checks ────────────────────────────────────────


def test_k2_closed_form_identical_across_grids():
    """Card §5.3 bullet 2: D̄ at k=2 is C(s_2,τ_1)·C(s_1,τ_2) on both grids.

    A divergence here would signal an Eq. (71) sign-pattern error.
    """
    val_alpha = primary(*slice_grid(GRID_ALPHA, 2))
    val_beta = primary(*slice_grid(GRID_BETA, 2))
    # The τ_1, τ_2, s_1, s_2 numerical values at Grid α and Grid β are
    # τ ↔ s relabeled (1.0, 0.7) ↔ (0.9, 0.6) — the closed form
    # C(s_2,τ_1)·C(s_1,τ_2) evaluates to different numbers on the two
    # grids. We assert that each grid hits its own §5 closed form (the
    # parametrised test above already covers that); here we additionally
    # verify the structural relation by recomputing the closed form
    # directly.
    tau_a = GRID_ALPHA["tau"]
    s_a = GRID_ALPHA["s"]
    cf_alpha = C(s_a[1], tau_a[0]) * C(s_a[0], tau_a[1])
    np.testing.assert_allclose(val_alpha, cf_alpha, atol=ATOL, rtol=RTOL)

    tau_b = GRID_BETA["tau"]
    s_b = GRID_BETA["s"]
    cf_beta = C(s_b[1], tau_b[0]) * C(s_b[0], tau_b[1])
    np.testing.assert_allclose(val_beta, cf_beta, atol=ATOL, rtol=RTOL)


def test_trivially_zero_cases_traverse_full_code_path():
    """Card §5.3 bullet 1: k=0 at Grid α and k=4 at Grid β return 0,
    but must do so via the full Eq. (69)/(73) code path (not by a
    short-circuit on k). We verify that the helper actually accepts
    these inputs without raising and returns numerical zero.
    """
    val_alpha_k0 = primary(*slice_grid(GRID_ALPHA, 0))
    assert abs(val_alpha_k0) <= ATOL

    val_beta_k4 = primary(*slice_grid(GRID_BETA, 4))
    assert abs(val_beta_k4) <= ATOL


# ─── §8 Secondary diagnostic (supporting only; not the gate) ─────────────────


@pytest.mark.parametrize("k", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("grid", [GRID_ALPHA, GRID_BETA], ids=["alpha", "beta"])
def test_secondary_diagnostic_n_point_ordered_matches_hand_wick(grid, k):
    """Card §8: the row-2.3-swapped n_point_ordered call must agree with
    a hand-enumerated thermal Gaussian Wick split of the same operator-
    order trace. Supporting evidence on the row-2.3 plumbing only; does
    NOT exercise the subtraction structure of Eqs. (69)–(73) and is not
    the acceptance gate (§9 is).
    """
    tau_args, s_args = slice_grid(grid, k)
    # The row-2.3-swapped n_point_ordered call (the same one
    # _D_bar_4_companion makes internally for its raw 4-point leaf).
    swapped_tau = tuple(reversed(s_args))
    swapped_s = tuple(reversed(tau_args))
    via_n_point = n_point_ordered(
        swapped_tau,
        swapped_s,
        bath_state=BATH_STATE,
        spectral_density=SPECTRAL_DENSITY,
        upper_cutoff_factor=UPPER_CUTOFF_FACTOR,
        quad_limit=QUAD_LIMIT,
    )
    # Hand-enumerated Wick split of the operator-order trace
    # ⟨B(s_{n−k})...B(s_1) B(τ_1)...B(τ_k)⟩.
    times = tuple(reversed(s_args)) + tuple(tau_args)  # length 4
    u1, u2, u3, u4 = times
    via_hand_wick = C(u1, u2) * C(u3, u4) + C(u1, u3) * C(u2, u4) + C(u1, u4) * C(u2, u3)
    np.testing.assert_allclose(via_n_point, via_hand_wick, atol=ATOL, rtol=RTOL)

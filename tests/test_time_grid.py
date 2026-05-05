"""Behaviour tests for numerical.time_grid (DG-1 Phase C.5).

Covers:
- TimeGrid dataclass + build_time_grid construction (uniform; deferred
  schemes; validation).
- integrate_with_ordering 1D + 2D against analytical references; trapezoidal
  convergence on refinement; deferred-ordering routing.
- Composability with Cards A3/A4 frozen_parameters.numerical.time_grid spec.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import yaml

from numerical import time_grid as tg

REPO_ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO_ROOT / "benchmarks" / "benchmark_cards"


# ─── build_time_grid: uniform scheme ────────────────────────────────────────


def test_build_time_grid_uniform_basic():
    grid = tg.build_time_grid({"t_start": 0.0, "t_end": 10.0, "n_points": 11, "scheme": "uniform"})
    assert isinstance(grid, tg.TimeGrid)
    assert grid.n_points == 11
    assert grid.scheme == "uniform"
    np.testing.assert_allclose(grid.times, np.linspace(0.0, 10.0, 11))


def test_build_time_grid_uniform_dt_property():
    grid = tg.build_time_grid({"t_start": 0.0, "t_end": 10.0, "n_points": 11, "scheme": "uniform"})
    assert grid.dt == pytest.approx(1.0)


def test_build_time_grid_n_points_2_minimum():
    grid = tg.build_time_grid({"t_start": 0.0, "t_end": 1.0, "n_points": 2, "scheme": "uniform"})
    np.testing.assert_allclose(grid.times, [0.0, 1.0])


def test_build_time_grid_endpoints_match_spec():
    spec = {"t_start": 1.5, "t_end": 7.5, "n_points": 13, "scheme": "uniform"}
    grid = tg.build_time_grid(spec)
    assert grid.t_start == 1.5
    assert grid.t_end == 7.5
    assert grid.times[0] == 1.5
    assert grid.times[-1] == 7.5


# ─── build_time_grid: validation errors ─────────────────────────────────────


def test_build_time_grid_missing_key_raises():
    with pytest.raises(ValueError, match="missing required keys"):
        tg.build_time_grid({"t_start": 0.0, "t_end": 10.0, "n_points": 11})


def test_build_time_grid_n_points_below_2_raises():
    with pytest.raises(ValueError, match=">= 2"):
        tg.build_time_grid({"t_start": 0.0, "t_end": 10.0, "n_points": 1, "scheme": "uniform"})


def test_build_time_grid_non_integer_n_points_raises():
    with pytest.raises(ValueError, match="must be int"):
        tg.build_time_grid({"t_start": 0.0, "t_end": 10.0, "n_points": 11.5, "scheme": "uniform"})


def test_build_time_grid_t_end_less_than_t_start_raises():
    with pytest.raises(ValueError, match="t_end > t_start"):
        tg.build_time_grid({"t_start": 10.0, "t_end": 5.0, "n_points": 11, "scheme": "uniform"})


def test_build_time_grid_t_end_equals_t_start_raises():
    with pytest.raises(ValueError, match="t_end > t_start"):
        tg.build_time_grid({"t_start": 5.0, "t_end": 5.0, "n_points": 11, "scheme": "uniform"})


def test_build_time_grid_non_dict_spec_raises():
    with pytest.raises(ValueError, match="must be a mapping"):
        tg.build_time_grid([0.0, 10.0, 11, "uniform"])  # type: ignore[arg-type]


# ─── build_time_grid: deferred schemes ──────────────────────────────────────


def test_build_time_grid_chebyshev_deferred_to_dg2():
    with pytest.raises(NotImplementedError, match="DG-2"):
        tg.build_time_grid({"t_start": 0.0, "t_end": 10.0, "n_points": 11, "scheme": "chebyshev"})


def test_build_time_grid_log_deferred_to_dg2():
    with pytest.raises(NotImplementedError, match="DG-2"):
        tg.build_time_grid({"t_start": 0.1, "t_end": 10.0, "n_points": 11, "scheme": "log"})


def test_build_time_grid_unknown_scheme_raises():
    with pytest.raises(ValueError, match="unknown scheme"):
        tg.build_time_grid({"t_start": 0.0, "t_end": 10.0, "n_points": 11, "scheme": "magic"})


# ─── Composability with Cards A3/A4 ────────────────────────────────────────


def test_build_time_grid_from_a3_card_spec():
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml").read_text())
    spec = a3["frozen_parameters"]["numerical"]["time_grid"]
    grid = tg.build_time_grid(spec)
    assert grid.n_points == 200
    assert grid.t_start == 0.0
    assert grid.t_end == 20.0
    assert grid.scheme == "uniform"


def test_build_time_grid_from_a4_card_spec():
    a4 = yaml.safe_load((CARDS_DIR / "A4_sigma-x-thermal_v0.1.0.yaml").read_text())
    spec = a4["frozen_parameters"]["numerical"]["time_grid"]
    grid = tg.build_time_grid(spec)
    assert grid.n_points == 200
    assert grid.t_end == 20.0
    # A3 and A4 share the same time grid (cross-card consistency).
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml").read_text())
    a3_grid = tg.build_time_grid(a3["frozen_parameters"]["numerical"]["time_grid"])
    np.testing.assert_array_equal(grid.times, a3_grid.times)


# ─── integrate_with_ordering: 1D ────────────────────────────────────────────


def test_integrate_1d_constant_returns_t_minus_t0():
    """∫_0^t 1 dτ = t."""
    t = np.linspace(0.0, 10.0, 101)
    integrand = np.ones_like(t)
    F = tg.integrate_with_ordering(integrand, t)
    np.testing.assert_allclose(F, t, atol=1e-12)


def test_integrate_1d_linear_returns_quadratic():
    """∫_0^t τ dτ = t^2 / 2; trapezoid on a linear function is exact."""
    t = np.linspace(0.0, 10.0, 101)
    integrand = t.copy()
    F = tg.integrate_with_ordering(integrand, t)
    np.testing.assert_allclose(F, 0.5 * t**2, atol=1e-12)


def test_integrate_1d_quadratic_converges_with_refinement():
    """∫_0^t τ^2 dτ = t^3 / 3; trapezoidal error is O(dt^2). Verify
    that refinement reduces the error at the right rate."""
    t_end = 1.0
    n_coarse = 11
    n_fine = 101
    t_coarse = np.linspace(0.0, t_end, n_coarse)
    t_fine = np.linspace(0.0, t_end, n_fine)
    F_coarse = tg.integrate_with_ordering(t_coarse**2, t_coarse)
    F_fine = tg.integrate_with_ordering(t_fine**2, t_fine)
    err_coarse = abs(F_coarse[-1] - 1.0 / 3.0)
    err_fine = abs(F_fine[-1] - 1.0 / 3.0)
    # err scales as dt^2 ≈ (1/n)^2; refinement by 10x should reduce error by ~100x.
    assert err_fine < err_coarse / 50.0


def test_integrate_1d_complex_dtype_preserved():
    t = np.linspace(0.0, 5.0, 51)
    integrand = (1.0 + 1.0j) * np.ones_like(t, dtype=complex)
    F = tg.integrate_with_ordering(integrand, t)
    assert F.dtype == np.complex128
    np.testing.assert_allclose(F, (1.0 + 1.0j) * t, atol=1e-12)


def test_integrate_1d_starts_at_zero():
    """F[0] = 0 by construction."""
    t = np.linspace(2.0, 12.0, 51)
    integrand = np.ones_like(t)
    F = tg.integrate_with_ordering(integrand, t)
    assert F[0] == 0.0


def test_integrate_1d_offset_grid_integrates_from_t0():
    """Cumulative integral starts from t_grid[0], not from 0."""
    t = np.linspace(2.0, 12.0, 101)
    integrand = np.ones_like(t)
    F = tg.integrate_with_ordering(integrand, t)
    np.testing.assert_allclose(F, t - t[0], atol=1e-12)


# ─── integrate_with_ordering: 2D ────────────────────────────────────────────


def test_integrate_2d_constant_returns_half_t_squared():
    """∫_0^t dτ ∫_0^τ ds 1 = t^2 / 2."""
    t = np.linspace(0.0, 10.0, 101)
    g = np.ones((len(t), len(t)))  # g(τ, s) = 1 everywhere
    F = tg.integrate_with_ordering(g, t)
    np.testing.assert_allclose(F, 0.5 * t**2, atol=1e-3)


def test_integrate_2d_separable_linear():
    """∫_0^t dτ ∫_0^τ ds (τ + s) = ∫_0^t dτ (τ^2 + τ^2/2) = ∫_0^t dτ (3τ^2/2)
    = t^3 / 2."""
    t = np.linspace(0.0, 5.0, 201)
    Tau, S = np.meshgrid(t, t, indexing="ij")
    g = Tau + S
    F = tg.integrate_with_ordering(g, t)
    np.testing.assert_allclose(F, 0.5 * t**3, atol=1e-2)


def test_integrate_2d_only_lower_triangle_used():
    """The upper triangle of g (s > τ) must NOT contribute to F (time-ordered
    domain is s ≤ τ). Setting the upper triangle to garbage must not change F."""
    t = np.linspace(0.0, 5.0, 51)
    Tau, S = np.meshgrid(t, t, indexing="ij")
    g_clean = Tau + S
    g_garbage_upper = g_clean.copy()
    upper_mask = S > Tau
    g_garbage_upper[upper_mask] = 1e10  # arbitrary garbage above the diagonal
    F_clean = tg.integrate_with_ordering(g_clean, t)
    F_garbage = tg.integrate_with_ordering(g_garbage_upper, t)
    np.testing.assert_allclose(F_clean, F_garbage, atol=1e-12)


def test_integrate_2d_complex_dtype_preserved():
    t = np.linspace(0.0, 3.0, 31)
    g = (1.0 + 2.0j) * np.ones((len(t), len(t)), dtype=complex)
    F = tg.integrate_with_ordering(g, t)
    assert F.dtype == np.complex128
    np.testing.assert_allclose(F.real, 0.5 * t**2, atol=1e-3)
    np.testing.assert_allclose(F.imag, t**2, atol=1e-3)


def test_integrate_2d_starts_at_zero():
    t = np.linspace(0.0, 5.0, 51)
    g = np.ones((len(t), len(t)))
    F = tg.integrate_with_ordering(g, t)
    assert F[0] == 0.0


# ─── integrate_with_ordering: validation errors ────────────────────────────


def test_integrate_unknown_ordering_raises():
    t = np.linspace(0.0, 1.0, 11)
    f = np.ones_like(t)
    with pytest.raises(ValueError, match="unknown ordering"):
        tg.integrate_with_ordering(f, t, ordering="random_walk")


def test_integrate_anti_time_ordered_deferred():
    t = np.linspace(0.0, 1.0, 11)
    f = np.ones_like(t)
    with pytest.raises(NotImplementedError, match="DG-2"):
        tg.integrate_with_ordering(f, t, ordering="anti_time_ordered")


def test_integrate_1d_shape_mismatch_raises():
    t = np.linspace(0.0, 1.0, 11)
    f = np.ones(7)
    with pytest.raises(ValueError, match="1D integrand shape"):
        tg.integrate_with_ordering(f, t)


def test_integrate_2d_shape_mismatch_raises():
    t = np.linspace(0.0, 1.0, 11)
    g = np.ones((7, 11))
    with pytest.raises(ValueError, match="2D integrand shape"):
        tg.integrate_with_ordering(g, t)


def test_integrate_3d_integrand_raises():
    t = np.linspace(0.0, 1.0, 11)
    h = np.ones((11, 11, 11))
    with pytest.raises(ValueError, match="must be 1D or 2D"):
        tg.integrate_with_ordering(h, t)


def test_integrate_t_grid_too_short_raises():
    t = np.array([0.0])
    f = np.ones(1)
    with pytest.raises(ValueError, match="at least 2 points"):
        tg.integrate_with_ordering(f, t)


def test_integrate_t_grid_non_monotonic_raises():
    t = np.array([0.0, 1.0, 0.5, 2.0])
    f = np.ones_like(t)
    with pytest.raises(ValueError, match="monotonically increasing"):
        tg.integrate_with_ordering(f, t)


def test_integrate_t_grid_2d_raises():
    t = np.zeros((3, 3))
    f = np.ones(3)
    with pytest.raises(ValueError, match="t_grid must be 1D"):
        tg.integrate_with_ordering(f, t)


# ─── Smoke: composability with Cards A3/A4 spec ────────────────────────────


def test_card_a3_grid_composes_with_integrator():
    """Build the A3 time grid from its YAML spec, then integrate a constant
    integrand over it. End-to-end smoke for the time-grid layer."""
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml").read_text())
    spec = a3["frozen_parameters"]["numerical"]["time_grid"]
    grid = tg.build_time_grid(spec)
    F = tg.integrate_with_ordering(np.ones_like(grid.times), grid.times)
    np.testing.assert_allclose(F, grid.times, atol=1e-12)

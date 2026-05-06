"""Tests for DG-4 Path B numerical TCL extraction helpers."""

from __future__ import annotations

import numpy as np
import pytest

from benchmarks import numerical_tcl_extraction as nte
from benchmarks.exact_finite_env import build_pure_dephasing_thermal_total


def test_reconstruct_superoperator_from_basis_outputs_identity_map():
    t_grid = np.array([0.0, 0.5, 1.0])
    basis_outputs = np.zeros((4, t_grid.size, 2, 2), dtype=complex)
    for col, op in enumerate(
        [
            np.array([[1, 0], [0, 0]], dtype=complex),
            np.array([[0, 1], [0, 0]], dtype=complex),
            np.array([[0, 0], [1, 0]], dtype=complex),
            np.array([[0, 0], [0, 1]], dtype=complex),
        ]
    ):
        basis_outputs[col] = op[None, :, :]

    maps = nte.reconstruct_superoperator_from_basis_outputs(basis_outputs)

    assert maps.shape == (3, 4, 4)
    for t_idx in range(t_grid.size):
        np.testing.assert_allclose(maps[t_idx], np.eye(4), atol=1e-12)


def test_reconstruct_schrodinger_maps_from_exact_env_smoke_trace_preserving():
    spec = {
        "system_dimension": 2,
        "system_hamiltonian": "(omega / 2) * sigma_z",
        "coupling_operator": "sigma_z",
        "bath_type": "bosonic_linear",
        "bath_spectral_density": {
            "family": "ohmic",
            "cutoff_frequency": 10.0,
            "coupling_strength": 0.01,
        },
        "bath_state": {"family": "thermal", "temperature": 0.5},
        "parameters": {"omega": 1.0},
    }
    t_grid = np.array([0.0, 0.2])

    maps = nte.reconstruct_schrodinger_maps_from_exact_env(
        build_pure_dephasing_thermal_total,
        spec,
        t_grid,
        builder_kwargs={"n_bath_modes": 2, "n_levels_per_mode": 2},
    )

    assert maps.shape == (2, 4, 4)
    np.testing.assert_allclose(maps[0], np.eye(4), atol=1e-12)
    trace_row = np.array([1.0, 0.0, 0.0, 1.0], dtype=complex)
    for map_t in maps:
        np.testing.assert_allclose(trace_row @ map_t, trace_row, atol=1e-12)


def test_fit_even_alpha_series_recovers_known_coefficients():
    alphas = np.array([0.02, 0.04, 0.06, 0.08])
    t_grid = np.array([0.0, 0.5, 1.0])
    op_dim = 4
    identity = np.eye(op_dim, dtype=complex)

    A = np.diag([1.0, -0.5, 0.25, 0.0]).astype(complex)
    B = np.array(
        [
            [0.0, 1.0j, 0.0, 0.0],
            [-1.0j, 0.0, 0.2, 0.0],
            [0.0, -0.2, 0.0, 0.3j],
            [0.0, 0.0, -0.3j, 0.1],
        ],
        dtype=complex,
    )
    Lambda2 = np.array([(1.0 + t) * A for t in t_grid])
    Lambda4 = np.array([(0.5 + t * t) * B for t in t_grid])
    maps = np.array(
        [identity[None, :, :] + alpha**2 * Lambda2 + alpha**4 * Lambda4 for alpha in alphas]
    )

    fit = nte.fit_even_alpha_series(alphas, maps)

    assert fit.orders == (2, 4)
    assert fit.rank == 2
    assert fit.relative_residual_norm < 1e-11
    np.testing.assert_allclose(fit.coefficients[2], Lambda2, atol=1e-10)
    np.testing.assert_allclose(fit.coefficients[4], Lambda4, atol=1e-7)


def test_fit_even_alpha_series_uses_supplied_baseline():
    alphas = np.array([0.03, 0.05, 0.07])
    t_grid = np.array([0.0, 1.0])
    op_dim = 4
    baseline = np.array([(1.0 + 0.1 * t) * np.eye(op_dim) for t in t_grid])
    Lambda2 = np.array([np.diag([t, 2 * t, 0.0, -t]) for t in t_grid])
    maps = np.array([baseline + alpha**2 * Lambda2 for alpha in alphas])

    fit = nte.fit_even_alpha_series(alphas, maps, orders=(2,), baseline=baseline)

    np.testing.assert_allclose(fit.coefficients[2], Lambda2, atol=1e-12)
    np.testing.assert_allclose(fit.reconstructed, maps, atol=1e-12)


def test_fit_even_alpha_series_rejects_rank_deficient_alpha_grid():
    maps = np.zeros((1, 2, 4, 4), dtype=complex)
    with pytest.raises(ValueError, match="rank-deficient"):
        nte.fit_even_alpha_series([0.05], maps, orders=(2, 4))


def test_extract_tcl_generators_order4_matches_polynomial_fixture():
    t_grid = np.linspace(0.0, 1.0, 5)
    A = np.diag([0.0, 1.0, -0.5, 0.25]).astype(complex)
    B = np.array(
        [
            [0.0, 0.0, 0.2, 0.0],
            [0.0, -0.1, 0.0, 0.0],
            [0.3, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.4],
        ],
        dtype=complex,
    )
    Lambda2 = np.array([t * A for t in t_grid])
    Lambda4 = np.array([t * t * B for t in t_grid])
    expected_L2 = np.array([A for _ in t_grid])
    expected_L4 = np.array([2.0 * t * B - t * (A @ A) for t in t_grid])

    extracted = nte.extract_tcl_generators_order4(Lambda2, Lambda4, t_grid)

    np.testing.assert_allclose(extracted.L2, expected_L2, atol=1e-12)
    np.testing.assert_allclose(extracted.L4, expected_L4, atol=1e-12)
    np.testing.assert_allclose(extracted.dLambda2_dt, expected_L2, atol=1e-12)


def test_compose_time_local_superoperators_validates_shapes():
    left = np.zeros((2, 4, 4), dtype=complex)
    right = np.zeros((3, 4, 4), dtype=complex)
    with pytest.raises(ValueError, match="same shape"):
        nte.compose_time_local_superoperators(left, right)


def test_fit_even_alpha_series_from_exact_env_squares_amplitude_for_coupling_strength(
    monkeypatch,
):
    calls = []

    def fake_reconstruct(builder, model_spec, t_grid, *, system_dim, builder_kwargs):
        del builder, t_grid, system_dim, builder_kwargs
        coupling_strength = model_spec["bath_spectral_density"]["coupling_strength"]
        calls.append(coupling_strength)
        return np.eye(4, dtype=complex)[None, :, :] + coupling_strength * np.ones(
            (2, 4, 4), dtype=complex
        )

    monkeypatch.setattr(nte, "reconstruct_schrodinger_maps_from_exact_env", fake_reconstruct)
    spec = {"bath_spectral_density": {"coupling_strength": 0.01}}

    fit = nte.fit_even_alpha_series_from_exact_env(
        lambda *args, **kwargs: None,
        spec,
        [0.02, 0.04],
        [0.0, 1.0],
        orders=(2,),
    )

    assert calls == [0.02**2, 0.04**2]
    assert spec["bath_spectral_density"]["coupling_strength"] == 0.01
    np.testing.assert_allclose(fit.coefficients[2], np.ones((2, 4, 4)), atol=1e-12)

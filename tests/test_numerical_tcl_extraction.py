"""Tests for DG-4 Path B numerical TCL extraction helpers."""

from __future__ import annotations

import numpy as np
import pytest
from scipy.linalg import expm

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


# ─── Picture-transform regression (D1 v0.1.2 supersedure) ─────────────────


def _ad_unitary_per_t(H_S: np.ndarray, t_grid: np.ndarray) -> np.ndarray:
    """Return Ad U(t) at each t as a stack of Liouville matrices."""
    return np.array(
        [np.kron(expm(-1j * H_S * t), expm(-1j * H_S * t).conj()) for t in t_grid]
    )


def test_adjoint_unitary_superoperator_acts_as_conjugation_in_row_major():
    """Ad U as a Liouville matrix must equal the row-major conjugation."""
    rng = np.random.default_rng(0)
    d = 2
    A = rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))
    U = expm(1j * (A + A.conj().T))  # arbitrary unitary
    rho = rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))

    Ad_U = nte.adjoint_unitary_superoperator(U)
    expected = U @ rho @ U.conj().T

    # Row-major vec[i*d+j] = rho[i,j].
    expected_vec = expected.reshape(d * d)
    actual_vec = Ad_U @ rho.reshape(d * d)
    np.testing.assert_allclose(actual_vec, expected_vec, atol=1e-12)


def test_transform_to_interaction_picture_inverts_schrodinger_propagation():
    """For Lambda^S = (Ad U(t)) Lambda^IP, the transform must recover Lambda^IP."""
    d = 2
    H_S = 0.5 * np.array([[1, 0], [0, -1]], dtype=complex)
    t_grid = np.linspace(0.0, 1.0, 11)
    rng = np.random.default_rng(0)
    Lambda_IP = rng.standard_normal((t_grid.size, d * d, d * d)) + 1j * rng.standard_normal(
        (t_grid.size, d * d, d * d)
    )

    Ad_U = _ad_unitary_per_t(H_S, t_grid)
    Lambda_S = np.einsum("tij,tjk->tik", Ad_U, Lambda_IP)

    recovered = nte.transform_to_interaction_picture(Lambda_S, t_grid, H_S)
    np.testing.assert_allclose(recovered, Lambda_IP, atol=1e-12)


def test_transform_to_interaction_picture_is_identity_when_H_S_is_zero():
    """With H_S = 0, U(t) = I and the transform is a no-op."""
    d = 2
    t_grid = np.linspace(0.0, 1.0, 5)
    rng = np.random.default_rng(0)
    Lambda = rng.standard_normal((t_grid.size, d * d, d * d)) + 1j * rng.standard_normal(
        (t_grid.size, d * d, d * d)
    )
    out = nte.transform_to_interaction_picture(Lambda, t_grid, np.zeros((d, d)))
    np.testing.assert_allclose(out, Lambda, atol=1e-12)


def test_picture_aware_extraction_recovers_truth_under_nontrivial_H_S():
    """Synthetic IP truth + Ad U(t) propagation + IP transform + extraction must
    recover the original L_2, L_4 coefficients.

    Pins the v0.1.2 supersedure picture fix: order-4 extraction must be done
    in the interaction picture so that ``Lambda_0 = id`` holds.
    """
    d = 2
    H_S = 0.5 * np.array([[1, 0], [0, -1]], dtype=complex)
    t_grid = np.linspace(0.0, 1.0, 21)
    rng = np.random.default_rng(7)

    # Constant-in-t synthetic L_2, L_4 in the interaction picture.
    L2_IP = (
        rng.standard_normal((d * d, d * d)) + 1j * rng.standard_normal((d * d, d * d))
    ) * 0.1
    L4_IP = (
        rng.standard_normal((d * d, d * d)) + 1j * rng.standard_normal((d * d, d * d))
    ) * 0.05

    # IP map coefficients consistent with constant L_n per the order-4 expansion:
    # Lambda_t = exp(t L) ≈ id + t (L_2 alpha² + L_4 alpha⁴) + (1/2) t² (L_2 alpha²)² + ...
    # so Lambda_2(t) = t L_2 and Lambda_4(t) = t L_4 + (1/2) t² L_2².
    Lambda2_IP = np.array([t * L2_IP for t in t_grid])
    Lambda4_IP = np.array([t * L4_IP + 0.5 * t * t * (L2_IP @ L2_IP) for t in t_grid])

    Ad_U = _ad_unitary_per_t(H_S, t_grid)
    Lambda2_S = np.einsum("tij,tjk->tik", Ad_U, Lambda2_IP)
    Lambda4_S = np.einsum("tij,tjk->tik", Ad_U, Lambda4_IP)

    # Picture-aware path: transform to IP, then extract.
    Lambda2_back = nte.transform_to_interaction_picture(Lambda2_S, t_grid, H_S)
    Lambda4_back = nte.transform_to_interaction_picture(Lambda4_S, t_grid, H_S)
    extraction = nte.extract_tcl_generators_order4(Lambda2_back, Lambda4_back, t_grid)

    interior = t_grid.size // 2
    np.testing.assert_allclose(extraction.L2[interior], L2_IP, atol=1e-6)
    np.testing.assert_allclose(extraction.L4[interior], L4_IP, atol=1e-6)


def test_buggy_direct_schrodinger_extraction_disagrees_with_truth():
    """Direct application of the order-4 formula to raw Schrödinger maps must
    produce a different ``L_2`` than the picture-aware extraction whenever
    ``H_S != 0``. This pins the defect that motivated the v0.1.1 → v0.1.2
    supersedure: without the IP transform, the extracted L_n is in the wrong
    picture.
    """
    d = 2
    H_S = 0.5 * np.array([[1, 0], [0, -1]], dtype=complex)
    t_grid = np.linspace(0.0, 1.0, 21)
    rng = np.random.default_rng(11)

    L2_IP = (
        rng.standard_normal((d * d, d * d)) + 1j * rng.standard_normal((d * d, d * d))
    ) * 0.1
    L4_IP = (
        rng.standard_normal((d * d, d * d)) + 1j * rng.standard_normal((d * d, d * d))
    ) * 0.05
    Lambda2_IP = np.array([t * L2_IP for t in t_grid])
    Lambda4_IP = np.array([t * L4_IP + 0.5 * t * t * (L2_IP @ L2_IP) for t in t_grid])

    Ad_U = _ad_unitary_per_t(H_S, t_grid)
    Lambda2_S = np.einsum("tij,tjk->tik", Ad_U, Lambda2_IP)
    Lambda4_S = np.einsum("tij,tjk->tik", Ad_U, Lambda4_IP)

    interior = t_grid.size // 2

    # Picture-aware (correct).
    Lambda2_back = nte.transform_to_interaction_picture(Lambda2_S, t_grid, H_S)
    Lambda4_back = nte.transform_to_interaction_picture(Lambda4_S, t_grid, H_S)
    correct = nte.extract_tcl_generators_order4(Lambda2_back, Lambda4_back, t_grid)

    # Buggy (direct on Schrödinger maps).
    buggy = nte.extract_tcl_generators_order4(Lambda2_S, Lambda4_S, t_grid)

    # The buggy L_2 must differ noticeably from the correct one (well above
    # finite-difference noise). We require at least 10% relative deviation.
    correct_norm = np.linalg.norm(correct.L2[interior])
    diff_norm = np.linalg.norm(buggy.L2[interior] - correct.L2[interior])
    assert diff_norm / max(correct_norm, 1e-12) > 0.1, (
        f"buggy direct-Schrödinger L_2 should differ from picture-aware L_2 by "
        f">10% under H_S != 0, but got diff/correct = "
        f"{diff_norm / max(correct_norm, 1e-12)}"
    )


def test_path_b_dissipator_norm_coefficients_requires_system_hamiltonian():
    """v0.1.2 supersedure: H_S is required so the IP transform can run."""
    with pytest.raises(TypeError, match="system_hamiltonian is required"):
        nte.path_b_dissipator_norm_coefficients(
            builder=lambda *a, **k: None,  # never reached
            model_spec={
                "system_dimension": 2,
                "bath_spectral_density": {"coupling_strength": 0.0},
            },
            t_grid=np.linspace(0.0, 1.0, 3),
            alpha_values=(0.01, 0.02),
        )

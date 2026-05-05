"""Behaviour tests for benchmarks.exact_finite_env.

Phase B (DG-3 work plan v0.1.0): exercises the generic ``propagate``
routine on a closed two-level system (sanity check) and on the
pure_dephasing × thermal_bath fixture from Card C1 v0.1.0.
"""

from __future__ import annotations

import numpy as np
import pytest

from benchmarks.exact_finite_env import (
    build_pure_dephasing_displaced_total,
    build_pure_dephasing_thermal_total,
    build_spin_boson_sigma_x_thermal_total,
    propagate,
)


# ─── Helpers ────────────────────────────────────────────────────────────────


def _c1_thermal_model_spec() -> dict:
    """Card C1 v0.1.0's thermal_bath_cross_method test case (parameter values)."""
    return {
        "system_dimension": 2,
        "system_hamiltonian": "(omega / 2) * sigma_z",
        "coupling_operator": "sigma_z",
        "bath_type": "bosonic_linear",
        "bath_spectral_density": {
            "family": "ohmic",
            "cutoff_frequency": 10.0,
            "coupling_strength": 0.05,
        },
        "bath_state": {"family": "thermal", "temperature": 0.5},
        "parameters": {"omega": 1.0},
    }


# ─── Generic propagate: closed two-level sanity ─────────────────────────────


def test_propagate_closed_qubit_preserves_state():
    """With H_int = 0 and product initial state, ρ_S evolves under H_S only."""
    omega = 1.0
    sigma_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    I_S = np.eye(2, dtype=complex)
    H_S = 0.5 * omega * sigma_z

    bath_dim = 4
    H_B = np.diag(np.arange(bath_dim) * 0.5).astype(complex)
    H_total = np.kron(H_S, np.eye(bath_dim, dtype=complex)) + np.kron(I_S, H_B)

    plus = np.array([[1.0], [1.0]], dtype=complex) / np.sqrt(2.0)
    rho_S0 = plus @ plus.conj().T
    rho_B = np.diag([0.5, 0.25, 0.15, 0.10]).astype(complex)
    rho_initial = np.kron(rho_S0, rho_B)

    t_grid = np.linspace(0.0, 2.0, 5)
    rho_S_t = propagate(H_total, rho_initial, t_grid, system_dim=2, bath_dim=bath_dim)

    assert rho_S_t.shape == (5, 2, 2)
    for k in range(5):
        # Diagonals unchanged (closed system + diagonal initial state).
        assert np.isclose(rho_S_t[k, 0, 0], 0.5)
        assert np.isclose(rho_S_t[k, 1, 1], 0.5)
        # Trace preserved.
        assert np.isclose(np.trace(rho_S_t[k]).real, 1.0)
        # Hermiticity.
        assert np.allclose(rho_S_t[k], rho_S_t[k].conj().T)


def test_propagate_closed_qubit_coherence_phase():
    """For a closed qubit at H_S = (ω/2) σ_z, coherence rotates as exp(-iωt)."""
    omega = 1.0
    sigma_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    H_S = 0.5 * omega * sigma_z
    bath_dim = 1
    H_total = H_S  # bath_dim=1 → joint dim = system dim
    plus = np.array([[1.0], [1.0]], dtype=complex) / np.sqrt(2.0)
    rho_initial = plus @ plus.conj().T  # 2×2, no bath

    t_grid = np.array([0.0, 1.0, np.pi / omega, 2 * np.pi / omega])
    rho_S_t = propagate(H_total, rho_initial, t_grid, system_dim=2, bath_dim=bath_dim)

    # At t=0: coherence = 0.5 (real).
    assert np.isclose(rho_S_t[0, 0, 1], 0.5)
    # At t = π/ω: coherence picks up phase exp(-i π) = -1 → -0.5.
    assert np.isclose(rho_S_t[2, 0, 1], -0.5)
    # At t = 2π/ω: coherence returns to +0.5.
    assert np.isclose(rho_S_t[3, 0, 1], 0.5)


def test_propagate_rejects_dimension_mismatch():
    H_total = np.eye(4, dtype=complex)
    rho = np.eye(4, dtype=complex) / 4
    t_grid = np.array([0.0, 1.0])
    # joint dim 4 = 2*2, so claiming bath_dim=3 should error.
    with pytest.raises(ValueError, match="H_total must be"):
        propagate(H_total, rho, t_grid, system_dim=2, bath_dim=3)


def test_propagate_rejects_2d_t_grid():
    H_total = np.eye(2, dtype=complex)
    rho = np.eye(2, dtype=complex) / 2
    with pytest.raises(ValueError, match="t_grid must be 1D"):
        propagate(H_total, rho, np.zeros((2, 2)), system_dim=2, bath_dim=1)


# ─── build_pure_dephasing_thermal_total: structural checks ──────────────────


def test_build_pure_dephasing_thermal_total_shapes():
    H_total, rho_initial, sd, bd = build_pure_dephasing_thermal_total(
        _c1_thermal_model_spec(), n_bath_modes=3, n_levels_per_mode=3
    )
    assert sd == 2
    assert bd == 3**3
    assert H_total.shape == (2 * bd, 2 * bd)
    assert rho_initial.shape == (2 * bd, 2 * bd)


def test_build_pure_dephasing_thermal_total_hermitian_H():
    H_total, _, _, _ = build_pure_dephasing_thermal_total(
        _c1_thermal_model_spec(), n_bath_modes=3, n_levels_per_mode=3
    )
    assert np.allclose(H_total, H_total.conj().T)


def test_build_pure_dephasing_thermal_total_trace_one():
    _, rho_initial, _, _ = build_pure_dephasing_thermal_total(
        _c1_thermal_model_spec(), n_bath_modes=3, n_levels_per_mode=3
    )
    assert np.isclose(np.trace(rho_initial).real, 1.0)
    assert np.allclose(rho_initial, rho_initial.conj().T)


def test_build_rejects_non_ohmic():
    spec = _c1_thermal_model_spec()
    spec["bath_spectral_density"]["family"] = "drude_lorentz"
    with pytest.raises(ValueError, match="ohmic"):
        build_pure_dephasing_thermal_total(spec)


def test_build_rejects_non_thermal():
    spec = _c1_thermal_model_spec()
    spec["bath_state"]["family"] = "coherent_displaced"
    with pytest.raises(ValueError, match="thermal"):
        build_pure_dephasing_thermal_total(spec)


def test_build_rejects_zero_temperature():
    spec = _c1_thermal_model_spec()
    spec["bath_state"]["temperature"] = 0.0
    with pytest.raises(ValueError, match="temperature > 0"):
        build_pure_dephasing_thermal_total(spec)


# ─── End-to-end on the C1 thermal fixture ───────────────────────────────────


def test_propagate_pure_dephasing_thermal_preserves_diagonals():
    """For σ_z coupling, diagonal populations of ρ_S are conserved at all t.

    H_int commutes with σ_z, so σ_z eigenvalue populations are constant.
    """
    H_total, rho_initial, sd, bd = build_pure_dephasing_thermal_total(
        _c1_thermal_model_spec(), n_bath_modes=4, n_levels_per_mode=4
    )
    t_grid = np.linspace(0.0, 5.0, 6)
    rho_S_t = propagate(H_total, rho_initial, t_grid, sd, bd)
    for k in range(t_grid.size):
        assert np.isclose(rho_S_t[k, 0, 0].real, 0.5, atol=1e-10)
        assert np.isclose(rho_S_t[k, 1, 1].real, 0.5, atol=1e-10)
        # Imaginary parts of diagonals should be ~0 (Hermitian).
        assert abs(rho_S_t[k, 0, 0].imag) < 1e-10
        assert abs(rho_S_t[k, 1, 1].imag) < 1e-10


def test_propagate_pure_dephasing_thermal_coherence_decays():
    """Initial coherence 0.5 must decay (not grow) over the time grid.

    Finite-bath recurrences allow non-monotonic decay, but the average
    coherence over t∈[2, 5] should be strictly below the initial value.
    """
    H_total, rho_initial, sd, bd = build_pure_dephasing_thermal_total(
        _c1_thermal_model_spec(), n_bath_modes=4, n_levels_per_mode=4
    )
    t_grid = np.linspace(0.0, 5.0, 21)
    rho_S_t = propagate(H_total, rho_initial, t_grid, sd, bd)
    coherences = np.abs(rho_S_t[:, 0, 1])
    assert np.isclose(coherences[0], 0.5)
    # After several memory times, mean coherence is well below 0.5.
    later_window = coherences[t_grid >= 2.0]
    assert later_window.mean() < 0.4


def test_propagate_pure_dephasing_thermal_traces_unit():
    H_total, rho_initial, sd, bd = build_pure_dephasing_thermal_total(
        _c1_thermal_model_spec(), n_bath_modes=4, n_levels_per_mode=4
    )
    t_grid = np.linspace(0.0, 5.0, 11)
    rho_S_t = propagate(H_total, rho_initial, t_grid, sd, bd)
    for k in range(t_grid.size):
        assert np.isclose(np.trace(rho_S_t[k]).real, 1.0, atol=1e-10)


# ─── Displaced fixture (C1 displaced delta-omega_c) ─────────────────────────


def _c1_displaced_model_spec() -> dict:
    """Card C1 v0.1.0's displaced_bath_delta_omega_c_cross_method test case."""
    return {
        "system_dimension": 2,
        "system_hamiltonian": "(omega / 2) * sigma_z",
        "coupling_operator": "sigma_z",
        "bath_type": "bosonic_linear",
        "bath_spectral_density": {
            "family": "ohmic",
            "cutoff_frequency": 10.0,
            "coupling_strength": 0.05,
        },
        "bath_state": {
            "family": "coherent_displaced",
            "displacement_profile": "delta-omega_c",
            "parameters": {"alpha_0": 1.0, "omega_c": 10.0},
            "temperature": 0.5,
        },
        "parameters": {"omega": 1.0},
    }


def test_build_displaced_total_shapes():
    H_total, rho_initial, sd, bd = build_pure_dephasing_displaced_total(
        _c1_displaced_model_spec(), n_bath_modes=3, n_levels_per_mode=3
    )
    assert sd == 2
    assert bd == 3**3
    assert H_total.shape == (2 * bd, 2 * bd)
    assert rho_initial.shape == (2 * bd, 2 * bd)


def test_build_displaced_total_hermitian_and_trace_one():
    H_total, rho_initial, _, _ = build_pure_dephasing_displaced_total(
        _c1_displaced_model_spec(), n_bath_modes=3, n_levels_per_mode=3
    )
    assert np.allclose(H_total, H_total.conj().T)
    assert np.allclose(rho_initial, rho_initial.conj().T)
    assert np.isclose(np.trace(rho_initial).real, 1.0)


def test_build_displaced_rejects_non_thermal_background_T_zero():
    spec = _c1_displaced_model_spec()
    spec["bath_state"]["temperature"] = 0.0
    with pytest.raises(ValueError, match="temperature > 0"):
        build_pure_dephasing_displaced_total(spec)


def test_build_displaced_rejects_non_coherent_displaced_family():
    spec = _c1_displaced_model_spec()
    spec["bath_state"]["family"] = "thermal"
    with pytest.raises(ValueError, match="coherent_displaced"):
        build_pure_dephasing_displaced_total(spec)


def test_build_displaced_rejects_unsupported_profile():
    spec = _c1_displaced_model_spec()
    spec["bath_state"]["displacement_profile"] = "delta-omega_S"
    with pytest.raises(NotImplementedError, match="delta-omega_c"):
        build_pure_dephasing_displaced_total(spec)


def test_build_displaced_requires_alpha_0_and_omega_c():
    spec = _c1_displaced_model_spec()
    del spec["bath_state"]["parameters"]["alpha_0"]
    with pytest.raises(ValueError, match="alpha_0"):
        build_pure_dephasing_displaced_total(spec)


def test_propagate_displaced_preserves_diagonals():
    """σ_z coupling + σ_z displacement ⇒ σ_z populations conserved."""
    H_total, rho_initial, sd, bd = build_pure_dephasing_displaced_total(
        _c1_displaced_model_spec(), n_bath_modes=4, n_levels_per_mode=4
    )
    t_grid = np.linspace(0.0, 5.0, 11)
    rho_S_t = propagate(H_total, rho_initial, t_grid, sd, bd)
    for k in range(t_grid.size):
        assert np.isclose(rho_S_t[k, 0, 0].real, 0.5, atol=1e-10)
        assert np.isclose(rho_S_t[k, 1, 1].real, 0.5, atol=1e-10)


def test_propagate_displaced_traces_unit():
    H_total, rho_initial, sd, bd = build_pure_dephasing_displaced_total(
        _c1_displaced_model_spec(), n_bath_modes=4, n_levels_per_mode=4
    )
    t_grid = np.linspace(0.0, 5.0, 11)
    rho_S_t = propagate(H_total, rho_initial, t_grid, sd, bd)
    for k in range(t_grid.size):
        assert np.isclose(np.trace(rho_S_t[k]).real, 1.0, atol=1e-10)


def test_propagate_displaced_initial_coherence_modulus_preserved():
    """At t=0 the displacement is real and only shifts the bath; the
    system reduced state matches the thermal-fixture initial state."""
    H_d, rho_d_init, sd, bd = build_pure_dephasing_displaced_total(
        _c1_displaced_model_spec(), n_bath_modes=3, n_levels_per_mode=3
    )
    rho_S0 = np.trace(rho_d_init.reshape(2, bd, 2, bd), axis1=1, axis2=3)
    plus = np.array([[1.0], [1.0]], dtype=complex) / np.sqrt(2.0)
    expected = plus @ plus.conj().T
    assert np.allclose(rho_S0, expected, atol=1e-10)


# ─── spin_boson_sigma_x thermal fixture (C2 thermal) ────────────────────────


def _c2_thermal_model_spec() -> dict:
    """Card C2 v0.1.0's thermal_bath_cross_method test case."""
    return {
        "system_dimension": 2,
        "system_hamiltonian": "(omega / 2) * sigma_z",
        "coupling_operator": "sigma_x",
        "bath_type": "bosonic_linear",
        "bath_spectral_density": {
            "family": "ohmic",
            "cutoff_frequency": 10.0,
            "coupling_strength": 0.05,
        },
        "bath_state": {"family": "thermal", "temperature": 0.5},
        "parameters": {"omega": 1.0},
    }


def test_build_sigma_x_thermal_shapes():
    H_total, rho_initial, sd, bd = build_spin_boson_sigma_x_thermal_total(
        _c2_thermal_model_spec(), n_bath_modes=3, n_levels_per_mode=3
    )
    assert sd == 2
    assert bd == 3**3
    assert H_total.shape == (2 * bd, 2 * bd)
    assert rho_initial.shape == (2 * bd, 2 * bd)


def test_build_sigma_x_thermal_hermitian_and_trace_one():
    H_total, rho_initial, _, _ = build_spin_boson_sigma_x_thermal_total(
        _c2_thermal_model_spec(), n_bath_modes=3, n_levels_per_mode=3
    )
    assert np.allclose(H_total, H_total.conj().T)
    assert np.allclose(rho_initial, rho_initial.conj().T)
    assert np.isclose(np.trace(rho_initial).real, 1.0)


def test_build_sigma_x_thermal_rejects_non_thermal():
    spec = _c2_thermal_model_spec()
    spec["bath_state"]["family"] = "coherent_displaced"
    with pytest.raises(ValueError, match="thermal"):
        build_spin_boson_sigma_x_thermal_total(spec)


def test_build_sigma_x_thermal_rejects_zero_T():
    spec = _c2_thermal_model_spec()
    spec["bath_state"]["temperature"] = 0.0
    with pytest.raises(ValueError, match="temperature > 0"):
        build_spin_boson_sigma_x_thermal_total(spec)


def test_propagate_sigma_x_thermal_traces_unit():
    H_total, rho_initial, sd, bd = build_spin_boson_sigma_x_thermal_total(
        _c2_thermal_model_spec(), n_bath_modes=4, n_levels_per_mode=4
    )
    t_grid = np.linspace(0.0, 5.0, 11)
    rho_S_t = propagate(H_total, rho_initial, t_grid, sd, bd)
    for k in range(t_grid.size):
        assert np.isclose(np.trace(rho_S_t[k]).real, 1.0, atol=1e-10)


def test_propagate_sigma_x_thermal_diagonals_change():
    """σ_x coupling ≠ pure dephasing: σ_z populations evolve under H_int."""
    H_total, rho_initial, sd, bd = build_spin_boson_sigma_x_thermal_total(
        _c2_thermal_model_spec(), n_bath_modes=4, n_levels_per_mode=4
    )
    t_grid = np.linspace(0.0, 10.0, 11)
    rho_S_t = propagate(H_total, rho_initial, t_grid, sd, bd)
    # P(↑) starts at 0.5 and must change measurably away from 0.5.
    p_up_initial = rho_S_t[0, 0, 0].real
    p_up_later = rho_S_t[-1, 0, 0].real
    assert np.isclose(p_up_initial, 0.5, atol=1e-10)
    assert abs(p_up_later - 0.5) > 0.05  # at least 5% population change


def test_propagate_sigma_x_thermal_hermitian_at_all_times():
    H_total, rho_initial, sd, bd = build_spin_boson_sigma_x_thermal_total(
        _c2_thermal_model_spec(), n_bath_modes=3, n_levels_per_mode=3
    )
    t_grid = np.linspace(0.0, 5.0, 11)
    rho_S_t = propagate(H_total, rho_initial, t_grid, sd, bd)
    for k in range(t_grid.size):
        assert np.allclose(rho_S_t[k], rho_S_t[k].conj().T, atol=1e-10)

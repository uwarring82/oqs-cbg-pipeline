# SPDX-License-Identifier: MIT
"""Smoke tests for benchmarks.heom_reference (DG-3 work plan v0.1.1 Phase B).

v0.1.0 of the module wires only the C1 thermal (σ_z) and C2 thermal (σ_x)
handlers. The tests below cover: import surface, dispatch, output shape/dtype,
single-shot propagation per supported handler with elementary physics
invariants (trace = 1, Hermitian, populations conserved-or-not), and clean
rejection of unsupported (displaced / σ_y / unknown family) configurations.
"""

from __future__ import annotations

import numpy as np
import pytest

from benchmarks.heom_reference import heom_propagate


def _c1_thermal_model_spec() -> dict:
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


def _c2_thermal_model_spec() -> dict:
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


# ─── C1 thermal handler (σ_z coupling) ────────────────────────────────────────


def test_heom_propagate_c1_thermal_shape_and_dtype():
    t_grid = np.linspace(0.0, 3.0, 6)
    rho_S_t = heom_propagate(_c1_thermal_model_spec(), t_grid)
    assert rho_S_t.shape == (6, 2, 2)
    assert rho_S_t.dtype == complex


def test_heom_propagate_c1_thermal_trace_and_hermiticity():
    t_grid = np.linspace(0.0, 3.0, 6)
    rho_S_t = heom_propagate(_c1_thermal_model_spec(), t_grid)
    for k in range(t_grid.size):
        assert np.isclose(np.trace(rho_S_t[k]).real, 1.0, atol=1e-6)
        assert np.allclose(rho_S_t[k], rho_S_t[k].conj().T, atol=1e-8)


def test_heom_propagate_c1_thermal_preserves_populations():
    """Pure dephasing (σ_z coupling): σ_z populations are exactly conserved."""
    t_grid = np.linspace(0.0, 3.0, 6)
    rho_S_t = heom_propagate(_c1_thermal_model_spec(), t_grid)
    for k in range(t_grid.size):
        assert np.isclose(rho_S_t[k, 0, 0].real, 0.5, atol=1e-6)
        assert np.isclose(rho_S_t[k, 1, 1].real, 0.5, atol=1e-6)


# ─── C2 thermal handler (σ_x coupling) ────────────────────────────────────────


def test_heom_propagate_c2_thermal_shape_and_dtype():
    t_grid = np.linspace(0.0, 3.0, 6)
    rho_S_t = heom_propagate(_c2_thermal_model_spec(), t_grid)
    assert rho_S_t.shape == (6, 2, 2)
    assert rho_S_t.dtype == complex


def test_heom_propagate_c2_thermal_trace_and_hermiticity():
    t_grid = np.linspace(0.0, 3.0, 6)
    rho_S_t = heom_propagate(_c2_thermal_model_spec(), t_grid)
    for k in range(t_grid.size):
        assert np.isclose(np.trace(rho_S_t[k]).real, 1.0, atol=1e-6)
        assert np.allclose(rho_S_t[k], rho_S_t[k].conj().T, atol=1e-8)


def test_heom_propagate_c2_thermal_populations_evolve():
    """σ_x coupling: populations relax away from the |+⟩ initial state."""
    t_grid = np.linspace(0.0, 5.0, 6)
    rho_S_t = heom_propagate(_c2_thermal_model_spec(), t_grid)
    p_up_init = rho_S_t[0, 0, 0].real
    p_up_late = rho_S_t[-1, 0, 0].real
    assert np.isclose(p_up_init, 0.5, atol=1e-6)
    assert abs(p_up_late - 0.5) > 0.05


# ─── Explicit rejection of unsupported configurations ─────────────────────────


def test_heom_propagate_rejects_coherent_displaced_bath():
    spec = _c1_thermal_model_spec()
    spec["bath_state"] = {
        "family": "coherent_displaced",
        "displacement_profile": "delta-omega_c",
        "parameters": {"alpha_0": 1.0, "omega_c": 10.0},
        "temperature": 0.5,
    }
    with pytest.raises(NotImplementedError, match="no handler registered"):
        heom_propagate(spec, np.array([0.0, 1.0]))


def test_heom_propagate_rejects_unsupported_coupling():
    spec = _c1_thermal_model_spec()
    spec["coupling_operator"] = "sigma_y"
    with pytest.raises(NotImplementedError, match="no handler registered"):
        heom_propagate(spec, np.array([0.0, 1.0]))


def test_heom_propagate_rejects_unknown_bath_family():
    spec = _c1_thermal_model_spec()
    spec["bath_state"] = {"family": "ground_state"}
    with pytest.raises(NotImplementedError, match="no handler registered"):
        heom_propagate(spec, np.array([0.0, 1.0]))


def test_heom_propagate_rejects_non_ohmic_spectral_density():
    spec = _c1_thermal_model_spec()
    spec["bath_spectral_density"]["family"] = "drude_lorentz"
    with pytest.raises(NotImplementedError, match="bath_spectral_density.family"):
        heom_propagate(spec, np.array([0.0, 1.0]))


def test_heom_propagate_rejects_non_bosonic_linear_bath_type():
    spec = _c1_thermal_model_spec()
    spec["bath_type"] = "fermionic_linear"
    with pytest.raises(NotImplementedError, match="bath_type"):
        heom_propagate(spec, np.array([0.0, 1.0]))


def test_heom_propagate_rejects_non_2_level_system():
    spec = _c1_thermal_model_spec()
    spec["system_dimension"] = 3
    with pytest.raises(NotImplementedError, match="system_dimension"):
        heom_propagate(spec, np.array([0.0, 1.0]))

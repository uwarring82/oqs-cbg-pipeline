"""Behaviour tests for benchmarks.qutip_reference.

Phase B (DG-3 work plan v0.1.0): exercises the dispatch table and the
C1 thermal fixture's mesolve-based handler.
"""

from __future__ import annotations

import numpy as np
import pytest

from benchmarks.qutip_reference import reference_propagate


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


def test_reference_propagate_c1_thermal_shape():
    t_grid = np.linspace(0.0, 5.0, 6)
    rho_S_t = reference_propagate(_c1_thermal_model_spec(), t_grid)
    assert rho_S_t.shape == (6, 2, 2)
    assert rho_S_t.dtype == complex


def test_reference_propagate_c1_thermal_preserves_diagonals():
    """Pure dephasing → σ_z populations conserved by the Lindblad mesolve."""
    t_grid = np.linspace(0.0, 5.0, 11)
    rho_S_t = reference_propagate(_c1_thermal_model_spec(), t_grid)
    for k in range(t_grid.size):
        assert np.isclose(rho_S_t[k, 0, 0].real, 0.5, atol=1e-8)
        assert np.isclose(rho_S_t[k, 1, 1].real, 0.5, atol=1e-8)


def test_reference_propagate_c1_thermal_traces_unit():
    t_grid = np.linspace(0.0, 5.0, 11)
    rho_S_t = reference_propagate(_c1_thermal_model_spec(), t_grid)
    for k in range(t_grid.size):
        assert np.isclose(np.trace(rho_S_t[k]).real, 1.0, atol=1e-8)


def test_reference_propagate_c1_thermal_coherence_monotone_decay():
    """Markov-Lindblad ⇒ |ρ_↑↓| decays monotonically (no recurrences)."""
    t_grid = np.linspace(0.0, 5.0, 21)
    rho_S_t = reference_propagate(_c1_thermal_model_spec(), t_grid)
    coherences = np.abs(rho_S_t[:, 0, 1])
    diffs = np.diff(coherences)
    # Every step decreases (small numerical slack for the integrator).
    assert np.all(diffs <= 1e-10), f"non-monotone decay observed: {diffs}"


def test_reference_propagate_c1_thermal_hermitian_at_all_times():
    t_grid = np.linspace(0.0, 5.0, 11)
    rho_S_t = reference_propagate(_c1_thermal_model_spec(), t_grid)
    for k in range(t_grid.size):
        assert np.allclose(rho_S_t[k], rho_S_t[k].conj().T, atol=1e-10)


def test_reference_propagate_unsupported_combo_raises():
    spec = _c1_thermal_model_spec()
    spec["bath_state"]["family"] = "coherent_displaced"
    with pytest.raises(NotImplementedError, match="no handler registered"):
        reference_propagate(spec, np.array([0.0, 1.0]))


def test_reference_propagate_unsupported_coupling_raises():
    spec = _c1_thermal_model_spec()
    spec["coupling_operator"] = "sigma_x"
    with pytest.raises(NotImplementedError, match="no handler registered"):
        reference_propagate(spec, np.array([0.0, 1.0]))

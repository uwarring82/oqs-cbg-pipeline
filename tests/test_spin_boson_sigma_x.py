"""Behaviour tests for models.spin_boson_sigma_x (DG-1 Phase C.10)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import yaml

from models import spin_boson_sigma_x as sbsx


REPO_ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO_ROOT / "benchmarks" / "benchmark_cards"


# ─── hamiltonian / coupling_operator ───────────────────────────────────────


def test_hamiltonian_unit_omega():
    H = sbsx.hamiltonian(1.0)
    np.testing.assert_array_equal(
        H, np.array([[0.5, 0], [0, -0.5]], dtype=complex)
    )


def test_hamiltonian_extra_args_ignored_at_dg1():
    """omegas / gs are retained in the signature for backward compat
    (the v0.1.0 stub anticipated explicit-bath-mode constructions) but
    are ignored at DG-1, where the bath is continuum-spectral via
    cbg.bath_correlations."""
    H_default = sbsx.hamiltonian(1.0)
    H_with_modes = sbsx.hamiltonian(1.0, omegas=[1, 2, 3], gs=[0.1, 0.2, 0.3])
    np.testing.assert_array_equal(H_default, H_with_modes)


def test_hamiltonian_scaling():
    H = sbsx.hamiltonian(2.0)
    np.testing.assert_array_equal(
        H, np.array([[1.0, 0], [0, -1.0]], dtype=complex)
    )


def test_coupling_operator_is_sigma_x():
    A = sbsx.coupling_operator()
    np.testing.assert_array_equal(
        A, np.array([[0, 1], [1, 0]], dtype=complex)
    )


def test_coupling_operator_returns_independent_copies():
    A1 = sbsx.coupling_operator()
    A1[0, 1] = 999.0
    A2 = sbsx.coupling_operator()
    assert A2[0, 1] == 1.0


def test_structural_constraints_present():
    assert "basis_independence" in sbsx.structural_constraints
    assert "parity_rule_odd_orders_vanish" in sbsx.structural_constraints
    assert "K_diagonal_in_sigma_z" in sbsx.structural_constraints


# ─── system_arrays_from_spec ───────────────────────────────────────────────


def _valid_a4_model_spec():
    return {
        "model_kind": "dynamical",
        "system_dimension": 2,
        "system_hamiltonian": "(omega / 2) * sigma_z",
        "coupling_operator": "sigma_x",
        "bath_type": "bosonic_linear",
    }


def test_system_arrays_from_spec_valid():
    H_S, A = sbsx.system_arrays_from_spec(_valid_a4_model_spec())
    np.testing.assert_array_equal(
        H_S, np.array([[0.5, 0], [0, -0.5]], dtype=complex)
    )
    np.testing.assert_array_equal(
        A, np.array([[0, 1], [1, 0]], dtype=complex)
    )


def test_system_arrays_from_spec_wrong_dimension_raises():
    spec = _valid_a4_model_spec()
    spec["system_dimension"] = 3
    with pytest.raises(ValueError, match="system_dimension"):
        sbsx.system_arrays_from_spec(spec)


def test_system_arrays_from_spec_wrong_hamiltonian_raises():
    spec = _valid_a4_model_spec()
    spec["system_hamiltonian"] = "omega * sigma_z"
    with pytest.raises(ValueError, match="system_hamiltonian"):
        sbsx.system_arrays_from_spec(spec)


def test_system_arrays_from_spec_wrong_coupling_raises():
    spec = _valid_a4_model_spec()
    spec["coupling_operator"] = "sigma_z"  # would be A3, not A4
    with pytest.raises(ValueError, match="coupling_operator"):
        sbsx.system_arrays_from_spec(spec)


# ─── Composability with Card A4 v0.1.1 ─────────────────────────────────────


def test_system_arrays_from_a4_v011_yaml():
    """End-to-end: load A4 v0.1.1, build (H_S, A) via the model factory."""
    a4 = yaml.safe_load(
        (CARDS_DIR / "A4_sigma-x-thermal_v0.1.1.yaml").read_text()
    )
    H_S, A = sbsx.system_arrays_from_spec(a4["frozen_parameters"]["model"])
    np.testing.assert_array_equal(
        H_S, np.array([[0.5, 0], [0, -0.5]], dtype=complex)
    )
    np.testing.assert_array_equal(
        A, np.array([[0, 1], [1, 0]], dtype=complex)
    )

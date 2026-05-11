# SPDX-License-Identifier: MIT
"""Behaviour tests for models.pure_dephasing (DG-1 Phase C.9)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import yaml

from models import pure_dephasing as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO_ROOT / "benchmarks" / "benchmark_cards"


# ─── hamiltonian / coupling_operator ───────────────────────────────────────


def test_hamiltonian_unit_omega():
    H = pd.hamiltonian(1.0)
    np.testing.assert_array_equal(H, np.array([[0.5, 0], [0, -0.5]], dtype=complex))


def test_hamiltonian_scaling():
    H = pd.hamiltonian(2.5)
    np.testing.assert_array_equal(H, np.array([[1.25, 0], [0, -1.25]], dtype=complex))


def test_hamiltonian_returns_complex_dtype():
    assert pd.hamiltonian(1.0).dtype == complex


def test_coupling_operator_is_sigma_z():
    A = pd.coupling_operator()
    np.testing.assert_array_equal(A, np.array([[1, 0], [0, -1]], dtype=complex))


def test_coupling_operator_returns_independent_copies():
    """Each call returns a fresh array; mutation does not leak between calls."""
    A1 = pd.coupling_operator()
    A1[0, 0] = 999.0
    A2 = pd.coupling_operator()
    assert A2[0, 0] == 1.0


def test_structural_constraints_present():
    assert "basis_independence" in pd.structural_constraints
    assert "parity_rule_even_orders_vanish" in pd.structural_constraints


# ─── system_arrays_from_spec ───────────────────────────────────────────────


def _valid_a3_model_spec():
    return {
        "model_kind": "dynamical",
        "system_dimension": 2,
        "system_hamiltonian": "(omega / 2) * sigma_z",
        "coupling_operator": "sigma_z",
        "bath_type": "bosonic_linear",
    }


def test_system_arrays_from_spec_valid():
    H_S, A = pd.system_arrays_from_spec(_valid_a3_model_spec())
    np.testing.assert_array_equal(H_S, np.array([[0.5, 0], [0, -0.5]], dtype=complex))
    np.testing.assert_array_equal(A, np.array([[1, 0], [0, -1]], dtype=complex))


def test_system_arrays_from_spec_wrong_dimension_raises():
    spec = _valid_a3_model_spec()
    spec["system_dimension"] = 3
    with pytest.raises(ValueError, match="system_dimension"):
        pd.system_arrays_from_spec(spec)


def test_system_arrays_from_spec_wrong_hamiltonian_raises():
    spec = _valid_a3_model_spec()
    spec["system_hamiltonian"] = "(omega / 2) * sigma_x"
    with pytest.raises(ValueError, match="system_hamiltonian"):
        pd.system_arrays_from_spec(spec)


def test_system_arrays_from_spec_wrong_coupling_raises():
    spec = _valid_a3_model_spec()
    spec["coupling_operator"] = "sigma_x"
    with pytest.raises(ValueError, match="coupling_operator"):
        pd.system_arrays_from_spec(spec)


def test_system_arrays_from_spec_missing_field_raises():
    spec = _valid_a3_model_spec()
    spec.pop("system_hamiltonian")
    with pytest.raises(ValueError, match="system_hamiltonian"):
        pd.system_arrays_from_spec(spec)


# ─── Composability with Card A3 v0.1.1 ─────────────────────────────────────


def test_system_arrays_from_a3_v011_yaml():
    """End-to-end: load A3 v0.1.1, build (H_S, A) via the model factory."""
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.1.yaml").read_text())
    H_S, A = pd.system_arrays_from_spec(a3["frozen_parameters"]["model"])
    # H_S = (1/2) sigma_z (omega = 1.0 by convention); A = sigma_z.
    np.testing.assert_array_equal(H_S, np.array([[0.5, 0], [0, -0.5]], dtype=complex))
    np.testing.assert_array_equal(A, np.array([[1, 0], [0, -1]], dtype=complex))

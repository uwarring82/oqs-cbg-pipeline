# SPDX-License-Identifier: MIT
"""Behaviour tests for cbg.basis (DG-1 Phase C C.1).

Verifies the matrix-unit basis and orthonormality-check utility used by
Card A1 (closed-form K, Letter Eq. (7)). DG-2 cross-basis verification
is out of scope here.
"""

import numpy as np
import pytest

from cbg import basis

# ─── matrix_unit_basis ────────────────────────────────────────────────────────


def test_matrix_unit_basis_d2_returns_four_arrays():
    b = basis.matrix_unit_basis(2)
    assert len(b) == 4
    for arr in b:
        assert arr.shape == (2, 2)
        assert arr.dtype == complex


def test_matrix_unit_basis_d2_values():
    """E_{j,k}[m,n] = δ_{j,m} δ_{k,n}; ordering α = j·d + k."""
    b = basis.matrix_unit_basis(2)
    expected = [
        np.array([[1, 0], [0, 0]], dtype=complex),  # E_{0,0}
        np.array([[0, 1], [0, 0]], dtype=complex),  # E_{0,1}
        np.array([[0, 0], [1, 0]], dtype=complex),  # E_{1,0}
        np.array([[0, 0], [0, 1]], dtype=complex),  # E_{1,1}
    ]
    for alpha, exp in enumerate(expected):
        np.testing.assert_array_equal(b[alpha], exp)


def test_matrix_unit_basis_d3_count_and_shape():
    b = basis.matrix_unit_basis(3)
    assert len(b) == 9
    for arr in b:
        assert arr.shape == (3, 3)


def test_matrix_unit_basis_invalid_d_raises():
    with pytest.raises(ValueError):
        basis.matrix_unit_basis(0)
    with pytest.raises(ValueError):
        basis.matrix_unit_basis(-1)
    with pytest.raises(ValueError):
        basis.matrix_unit_basis(2.5)  # non-integer


# ─── verify_orthonormality ────────────────────────────────────────────────────


@pytest.mark.parametrize("d", [2, 3, 4])
def test_verify_orthonormality_passes_for_matrix_unit_basis(d):
    """The matrix-unit basis is HS-orthonormal at every dimension."""
    b = basis.matrix_unit_basis(d)
    assert basis.verify_orthonormality(b) is True


def test_verify_orthonormality_rejects_uniform_scaling():
    """A uniformly-scaled basis fails the unit-norm check."""
    b = basis.matrix_unit_basis(2)
    b_scaled = [2.0 * arr for arr in b]
    assert basis.verify_orthonormality(b_scaled) is False


def test_verify_orthonormality_rejects_duplicate_elements():
    """Two parallel operators are not orthogonal."""
    b = basis.matrix_unit_basis(2)
    b_dup = [b[0], b[0], b[2], b[3]]
    assert basis.verify_orthonormality(b_dup) is False


def test_verify_orthonormality_empty_basis():
    """Empty basis is vacuously orthonormal (no pairs to check)."""
    assert basis.verify_orthonormality([]) is True


def test_verify_orthonormality_tolerance_argument():
    """Tolerance argument distinguishes pass from fail."""
    b = basis.matrix_unit_basis(2)
    # Add a 0.01 perturbation to b[0] — breaks orthonormality by ~0.01.
    b_mod = [b[0] + 0.01 * np.ones((2, 2), dtype=complex)] + b[1:]
    assert basis.verify_orthonormality(b_mod, tol=1e-3) is False  # 0.01 > 1e-3
    assert basis.verify_orthonormality(b_mod, tol=1.0) is True  # 0.01 < 1.0


def test_verify_orthonormality_returns_bool():
    """Return type is bool (not numpy.bool_ or int)."""
    b = basis.matrix_unit_basis(2)
    result = basis.verify_orthonormality(b)
    assert isinstance(result, bool)


# ─── su_d_generator_basis (DG-2 Card B3 v0.1.0) ──────────────────────────────


def test_su_d_generator_basis_d2_returns_four_arrays():
    b = basis.su_d_generator_basis(2)
    assert len(b) == 4
    for arr in b:
        assert arr.shape == (2, 2)
        assert arr.dtype == complex


def test_su_d_generator_basis_d2_values():
    """Ordering [I, σ_x, σ_y, σ_z] / √2 — identity first, then SU(2) generators."""
    b = basis.su_d_generator_basis(2)
    inv_sqrt2 = 1.0 / np.sqrt(2.0)
    expected = [
        inv_sqrt2 * np.eye(2, dtype=complex),
        inv_sqrt2 * np.array([[0, 1], [1, 0]], dtype=complex),
        inv_sqrt2 * np.array([[0, -1j], [1j, 0]], dtype=complex),
        inv_sqrt2 * np.array([[1, 0], [0, -1]], dtype=complex),
    ]
    for alpha, exp in enumerate(expected):
        np.testing.assert_allclose(b[alpha], exp, atol=1e-15)


def test_su_d_generator_basis_d2_is_orthonormal():
    """The normalized Pauli basis is HS-orthonormal (precondition for K_from_generator)."""
    b = basis.su_d_generator_basis(2)
    assert basis.verify_orthonormality(b) is True


def test_su_d_generator_basis_higher_d_not_implemented():
    """Higher dimensions deferred to a separate DG-2 freeze."""
    with pytest.raises(NotImplementedError, match="d=2"):
        basis.su_d_generator_basis(3)
    with pytest.raises(NotImplementedError, match="d=2"):
        basis.su_d_generator_basis(4)


def test_su_d_generator_basis_invalid_d_raises():
    with pytest.raises(ValueError):
        basis.su_d_generator_basis(0)
    with pytest.raises(ValueError):
        basis.su_d_generator_basis(-1)
    with pytest.raises(ValueError):
        basis.su_d_generator_basis(2.5)

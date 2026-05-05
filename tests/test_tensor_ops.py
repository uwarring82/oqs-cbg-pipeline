"""Behaviour tests for numerical.tensor_ops (DG-1 Phase C C.2).

Verifies the operator-space linear-algebra primitives used by the K(t)
computation in cbg.effective_hamiltonian (Letter Eqs. (6)–(7)), and the
Lindblad-form L assembly in the runner. Pauli-matrix identities serve as
the canonical fixtures.
"""

import numpy as np
import pytest

from numerical import tensor_ops

# ─── Test fixtures (Pauli matrices and the 2x2 identity) ─────────────────────

sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
identity_2 = np.eye(2, dtype=complex)


# ─── commutator ──────────────────────────────────────────────────────────────


def test_commutator_pauli_xy():
    """[sigma_x, sigma_y] = 2i sigma_z."""
    np.testing.assert_allclose(
        tensor_ops.commutator(sigma_x, sigma_y),
        2j * sigma_z,
        atol=1e-12,
    )


def test_commutator_pauli_yz():
    """[sigma_y, sigma_z] = 2i sigma_x."""
    np.testing.assert_allclose(
        tensor_ops.commutator(sigma_y, sigma_z),
        2j * sigma_x,
        atol=1e-12,
    )


def test_commutator_pauli_zx():
    """[sigma_z, sigma_x] = 2i sigma_y."""
    np.testing.assert_allclose(
        tensor_ops.commutator(sigma_z, sigma_x),
        2j * sigma_y,
        atol=1e-12,
    )


def test_commutator_self_is_zero():
    """[A, A] = 0 for any A."""
    np.testing.assert_allclose(
        tensor_ops.commutator(sigma_x, sigma_x),
        np.zeros((2, 2), dtype=complex),
        atol=1e-12,
    )


def test_commutator_with_identity_is_zero():
    """[I, A] = 0; identity commutes with everything."""
    np.testing.assert_allclose(
        tensor_ops.commutator(identity_2, sigma_z),
        np.zeros((2, 2), dtype=complex),
        atol=1e-12,
    )


def test_commutator_antisymmetric():
    """[A, B] = -[B, A]."""
    np.testing.assert_allclose(
        tensor_ops.commutator(sigma_x, sigma_y),
        -tensor_ops.commutator(sigma_y, sigma_x),
        atol=1e-12,
    )


def test_commutator_shape_mismatch_raises():
    A = np.zeros((2, 2), dtype=complex)
    B = np.zeros((3, 3), dtype=complex)
    with pytest.raises(ValueError, match="shape mismatch"):
        tensor_ops.commutator(A, B)


# ─── anticommutator ──────────────────────────────────────────────────────────


def test_anticommutator_pauli_self_x():
    """{sigma_x, sigma_x} = 2 I  (since sigma_x^2 = I)."""
    np.testing.assert_allclose(
        tensor_ops.anticommutator(sigma_x, sigma_x),
        2 * identity_2,
        atol=1e-12,
    )


def test_anticommutator_pauli_self_z():
    """{sigma_z, sigma_z} = 2 I."""
    np.testing.assert_allclose(
        tensor_ops.anticommutator(sigma_z, sigma_z),
        2 * identity_2,
        atol=1e-12,
    )


def test_anticommutator_pauli_xy_zero():
    """{sigma_x, sigma_y} = 0; distinct Pauli matrices anti-commute."""
    np.testing.assert_allclose(
        tensor_ops.anticommutator(sigma_x, sigma_y),
        np.zeros((2, 2), dtype=complex),
        atol=1e-12,
    )


def test_anticommutator_symmetric():
    """{A, B} = {B, A}."""
    np.testing.assert_allclose(
        tensor_ops.anticommutator(sigma_x, sigma_z),
        tensor_ops.anticommutator(sigma_z, sigma_x),
        atol=1e-12,
    )


def test_anticommutator_shape_mismatch_raises():
    A = np.zeros((2, 2), dtype=complex)
    B = np.zeros((3, 3), dtype=complex)
    with pytest.raises(ValueError, match="shape mismatch"):
        tensor_ops.anticommutator(A, B)


# ─── hilbert_schmidt_inner ───────────────────────────────────────────────────


def test_hs_inner_pauli_self_x():
    """<sigma_x, sigma_x> = Tr(sigma_x^2) = Tr(I) = 2."""
    result = tensor_ops.hilbert_schmidt_inner(sigma_x, sigma_x)
    assert abs(result - 2.0) < 1e-12


def test_hs_inner_pauli_self_y():
    """<sigma_y, sigma_y> = 2."""
    result = tensor_ops.hilbert_schmidt_inner(sigma_y, sigma_y)
    assert abs(result - 2.0) < 1e-12


def test_hs_inner_pauli_orthogonal_xy():
    """<sigma_x, sigma_y> = 0; Pauli matrices are HS-orthogonal."""
    result = tensor_ops.hilbert_schmidt_inner(sigma_x, sigma_y)
    assert abs(result) < 1e-12


def test_hs_inner_pauli_orthogonal_xz():
    """<sigma_x, sigma_z> = 0."""
    result = tensor_ops.hilbert_schmidt_inner(sigma_x, sigma_z)
    assert abs(result) < 1e-12


def test_hs_inner_identity_pauli():
    """<I, sigma_z> = Tr(I sigma_z) = Tr(sigma_z) = 0."""
    result = tensor_ops.hilbert_schmidt_inner(identity_2, sigma_z)
    assert abs(result) < 1e-12


def test_hs_inner_conjugate_symmetry():
    """<A, B> = conj(<B, A>); standard sesquilinear form."""
    inner_AB = tensor_ops.hilbert_schmidt_inner(sigma_x, sigma_y)
    inner_BA = tensor_ops.hilbert_schmidt_inner(sigma_y, sigma_x)
    assert abs(inner_AB - np.conj(inner_BA)) < 1e-12


def test_hs_inner_returns_python_complex():
    """Return type is Python complex, not numpy scalar."""
    result = tensor_ops.hilbert_schmidt_inner(sigma_x, sigma_x)
    assert isinstance(result, complex)


def test_hs_inner_shape_mismatch_raises():
    A = np.zeros((2, 2), dtype=complex)
    B = np.zeros((3, 3), dtype=complex)
    with pytest.raises(ValueError, match="shape mismatch"):
        tensor_ops.hilbert_schmidt_inner(A, B)


# ─── superop_apply ───────────────────────────────────────────────────────────


def test_superop_apply_callable_dispatches():
    """For callable L, superop_apply(L, X) returns L(X)."""

    def L(X):
        return X @ X

    result = tensor_ops.superop_apply(L, sigma_z)
    np.testing.assert_allclose(result, identity_2, atol=1e-12)


def test_superop_apply_unitary_lindbladian():
    """A unitary-only Lindbladian L[X] = -i[H, X] passes through cleanly."""
    H = sigma_z

    def L(X):
        return -1j * tensor_ops.commutator(H, X)

    result = tensor_ops.superop_apply(L, sigma_x)
    expected = -1j * tensor_ops.commutator(H, sigma_x)
    np.testing.assert_allclose(result, expected, atol=1e-12)


def test_superop_apply_canonical_lindblad_form():
    """A canonical Lindbladian (commutator + dissipator) passes through cleanly.

    L[X] = -i [H, X] + V X V^dagger - 0.5 {V^dagger V, X}
    Constructed using commutator + anticommutator from this same module;
    confirms the primitives compose correctly.
    """
    H = 0.5 * sigma_z
    V = sigma_x  # arbitrary jump operator
    V_dag = V.conj().T
    V_dag_V = V_dag @ V

    def L(X):
        return (
            -1j * tensor_ops.commutator(H, X)
            + V @ X @ V_dag
            - 0.5 * tensor_ops.anticommutator(V_dag_V, X)
        )

    result = tensor_ops.superop_apply(L, sigma_z)
    # Direct construction for cross-check
    expected = (
        -1j * (H @ sigma_z - sigma_z @ H)
        + V @ sigma_z @ V_dag
        - 0.5 * (V_dag_V @ sigma_z + sigma_z @ V_dag_V)
    )
    np.testing.assert_allclose(result, expected, atol=1e-12)


def test_superop_apply_non_callable_raises_dg2_routing():
    """Matrix-form superops raise NotImplementedError pointing at DG-2."""
    matrix_superop = np.eye(4, dtype=complex)  # would-be d^2 x d^2 vec-form superop
    with pytest.raises(NotImplementedError, match="DG-2"):
        tensor_ops.superop_apply(matrix_superop, sigma_z)


def test_superop_apply_none_raises_dg2_routing():
    """Passing None as superop also routes to DG-2 message."""
    with pytest.raises(NotImplementedError, match="DG-2"):
        tensor_ops.superop_apply(None, sigma_z)

"""Behaviour tests for cbg.effective_hamiltonian (DG-1 Phase C C.3).

Verifies the operational K-from-L computation per Letter Eq. (6),
exercised via simple closed-form L specifications. The tests are
sanity / smoke tests; full Card A1 verification is Phase D once the
runner (C.4) lands.
"""

import numpy as np
import pytest

from cbg import basis, effective_hamiltonian
from numerical import tensor_ops


# ─── Test fixtures ───────────────────────────────────────────────────────────

sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
identity_2 = np.eye(2, dtype=complex)
sigma_minus = np.array([[0, 1], [0, 0]], dtype=complex)  # |0⟩⟨1|; traceless
sigma_plus = np.array([[0, 0], [1, 0]], dtype=complex)   # |1⟩⟨0|; traceless


def _basis_d2():
    return basis.matrix_unit_basis(2)


def _basis_d3():
    return basis.matrix_unit_basis(3)


def _unitary_generator(H):
    """L[X] = -i [H, X]; pure unitary evolution."""
    def L(X):
        return -1j * tensor_ops.commutator(H, X)
    return L


def _canonical_lindblad_generator(H, jump_operators):
    """L[X] = -i[H, X] + Σ_i (V_i X V_i† - 0.5 {V_i† V_i, X})."""
    def L(X):
        out = -1j * tensor_ops.commutator(H, X)
        for V in jump_operators:
            V_dag = V.conj().T
            out += V @ X @ V_dag
            out -= 0.5 * tensor_ops.anticommutator(V_dag @ V, X)
        return out
    return L


# ─── K_from_generator: closed-form sanity cases ──────────────────────────────


def test_K_from_generator_pure_unitary_traceless_H_recovers_H():
    """For L = -i[H, ·] with traceless H, K = H exactly (Letter Eq. (6))."""
    omega = 1.0
    H = 0.5 * omega * sigma_z  # traceless
    L = _unitary_generator(H)
    K = effective_hamiltonian.K_from_generator(L, _basis_d2())
    np.testing.assert_allclose(K, H, atol=1e-12)


def test_K_from_generator_pure_unitary_traceful_H_returns_traceless_part():
    """For L = -i[H, ·] with H = H_traceless + cI, K = H_traceless.

    The minimal-dissipation gauge fixes the traceless representative;
    pure-energy-shift identity terms are gauge-removable. This test
    confirms the (Tr H / d) I subtraction implicit in Letter Eq. (6).
    """
    omega = 1.0
    c = 0.7  # arbitrary non-zero shift
    H_traceless = 0.5 * omega * sigma_z
    H = H_traceless + c * identity_2
    L = _unitary_generator(H)
    K = effective_hamiltonian.K_from_generator(L, _basis_d2())
    np.testing.assert_allclose(K, H_traceless, atol=1e-12)


def test_K_from_generator_zero_generator_returns_zero():
    """For L = 0, K = 0."""
    L = lambda X: np.zeros_like(X)
    K = effective_hamiltonian.K_from_generator(L, _basis_d2())
    np.testing.assert_allclose(K, np.zeros((2, 2), dtype=complex), atol=1e-12)


def test_K_from_generator_canonical_lindblad_traceless_jump_recovers_H():
    """Smoke for Card A1 B.1: canonical Lindblad with traceless jump operators
    returns the H term exactly (the dissipator contributes zero to K).

    H = (ω/2) σ_z; V = √γ σ_- (traceless).
    Expected: K = (ω/2) σ_z, even though L includes a non-zero dissipator.
    """
    omega = 1.0
    gamma = 0.1
    H = 0.5 * omega * sigma_z
    V = np.sqrt(gamma) * sigma_minus  # traceless jump
    L = _canonical_lindblad_generator(H, [V])
    K = effective_hamiltonian.K_from_generator(L, _basis_d2())
    np.testing.assert_allclose(K, H, atol=1e-10)


def test_K_from_generator_canonical_lindblad_two_jumps():
    """Two traceless jumps: same expectation, K = H."""
    omega = 1.0
    gamma_minus = 0.1
    gamma_plus = 0.05
    H = 0.5 * omega * sigma_z
    V1 = np.sqrt(gamma_minus) * sigma_minus
    V2 = np.sqrt(gamma_plus) * sigma_plus
    L = _canonical_lindblad_generator(H, [V1, V2])
    K = effective_hamiltonian.K_from_generator(L, _basis_d2())
    np.testing.assert_allclose(K, H, atol=1e-10)


# ─── K_from_generator: Hermiticity and structural properties ─────────────────


def test_K_from_generator_returns_hermitian_for_hermiticity_preserving_L():
    """For Hermiticity-preserving L, K must be Hermitian (Letter Eq. (6))."""
    omega = 1.0
    gamma = 0.1
    H = 0.5 * omega * sigma_z
    V = np.sqrt(gamma) * sigma_minus
    L = _canonical_lindblad_generator(H, [V])
    K = effective_hamiltonian.K_from_generator(L, _basis_d2())
    np.testing.assert_allclose(K, K.conj().T, atol=1e-12)


def test_K_from_generator_independent_of_basis_order():
    """Letter Eq. (6) is a sum over the basis; result must be permutation-
    invariant.

    Smoke for the basis-independence property (DG-2 universal default
    check), restricted to permutations of the same matrix-unit basis.
    Cross-basis verification is DG-2 territory.
    """
    omega = 1.0
    H = 0.5 * omega * sigma_z
    L = _unitary_generator(H)

    b = _basis_d2()
    K_canonical = effective_hamiltonian.K_from_generator(L, b)

    rng = np.random.default_rng(seed=42)
    perm = rng.permutation(len(b))
    b_perm = [b[i] for i in perm]
    K_perm = effective_hamiltonian.K_from_generator(L, b_perm)

    np.testing.assert_allclose(K_canonical, K_perm, atol=1e-12)


# ─── K_from_generator: higher dimension ──────────────────────────────────────


def test_K_from_generator_d3_unitary_recovers_traceless_H():
    """d = 3 case: traceless H is recovered; non-traceless part is removed."""
    H_traceless = np.diag([1.0, -0.5, -0.5]).astype(complex)  # Tr = 0
    H = H_traceless + 0.3 * np.eye(3, dtype=complex)
    L = _unitary_generator(H)
    K = effective_hamiltonian.K_from_generator(L, _basis_d3())
    np.testing.assert_allclose(K, H_traceless, atol=1e-12)


# ─── K_from_generator: composability with cbg.basis ──────────────────────────


def test_K_from_generator_composes_with_cbg_basis():
    """The returned matrix-unit basis from cbg.basis composes correctly
    with cbg.effective_hamiltonian; no shape or dtype conversions needed."""
    H = 0.5 * sigma_z
    L = _unitary_generator(H)
    b = basis.matrix_unit_basis(2)
    assert basis.verify_orthonormality(b) is True  # precondition
    K = effective_hamiltonian.K_from_generator(L, b)
    np.testing.assert_allclose(K, H, atol=1e-12)


# ─── K_from_generator: error handling ────────────────────────────────────────


def test_K_from_generator_empty_basis_raises():
    L = lambda X: X
    with pytest.raises(ValueError, match="non-empty"):
        effective_hamiltonian.K_from_generator(L, [])


def test_K_from_generator_non_square_first_element_raises():
    L = lambda X: X
    bad_basis = [np.zeros((2, 3), dtype=complex)]
    with pytest.raises(ValueError, match="non-square"):
        effective_hamiltonian.K_from_generator(L, bad_basis)


def test_K_from_generator_inconsistent_shapes_raises():
    L = lambda X: X
    mixed_basis = [
        np.zeros((2, 2), dtype=complex),
        np.zeros((3, 3), dtype=complex),
    ]
    with pytest.raises(ValueError, match=r"basis element 1"):
        effective_hamiltonian.K_from_generator(L, mixed_basis)


# ─── K_perturbative: still stubbed at C.3 ────────────────────────────────────


def test_K_perturbative_still_stubbed_at_c3():
    """K_perturbative remains stubbed; recursion lands in Phase C.7/C.8."""
    with pytest.raises(NotImplementedError, match="C.3"):
        effective_hamiltonian.K_perturbative(2)

# SPDX-License-Identifier: MIT
"""
cbg.basis — Hilbert–Schmidt orthonormal operator bases.

Provides bases {F_α}_{α=0}^{d²-1} satisfying Tr(F_α† F_β) = δ_αβ, used in:

    K = (1 / 2id) Σ_α [F_α†, L[F_α]]                       (Letter Eq. (6))

The basis-independence of K under change of {F_α} is the universal default
structural-identity check for DG-2 (Sail v0.5 §9). DG-1 cards (specifically
Card A1) use the matrix-unit basis only; cross-basis verification is the
DG-2 universal default check.

Implementations:

- ``matrix_unit_basis(d)`` — ``{|j⟩⟨k|}`` basis, used in Letter Eq. (7).
  Implemented at DG-1 Phase C C.1.
- ``su_d_generator_basis(d)`` — ``{1/√d, σ_i/√d}``, used in
  Letter Eq. (B.10). Stubbed; DG-2 territory.
- ``hermitian_basis(d)`` — d² real-orthonormal Hermitian operators.
  Not stubbed; if/when needed at DG-2.

Each function returns a list of d×d numpy arrays satisfying the
Hilbert–Schmidt orthonormality relation up to numerical tolerance,
verifiable by verify_orthonormality.
"""

import numpy as np


def matrix_unit_basis(d: int) -> list[np.ndarray]:
    """Matrix-unit basis ``{|j⟩⟨k|}``, j, k ∈ {0, …, d-1}.

    The basis used in Letter Eq. (7). Each element E_{j,k} is the d×d
    complex matrix with E_{j,k}[m, n] = δ_{j,m} δ_{k,n}; equivalently,
    a single 1.0 at position (j, k) and zeros elsewhere.

    The basis is Hilbert–Schmidt orthonormal by construction:

        Tr(E_{j,k}† E_{l,m}) = Tr(E_{k,j} E_{l,m})
                             = δ_{j,l} Tr(E_{k,m})
                             = δ_{j,l} δ_{k,m}.

    No normalisation factor is needed — matrix units are already
    orthonormal under the trace inner product.

    The returned list is ordered with α = j·d + k, so that for d=2 the
    sequence is E_{0,0}, E_{0,1}, E_{1,0}, E_{1,1}.

    Args:
        d: System Hilbert-space dimension. Must be a positive integer.

    Returns:
        List of d² numpy arrays of shape (d, d), dtype complex.

    Raises:
        ValueError: if d is not a positive integer.
    """
    if not isinstance(d, (int, np.integer)) or d < 1:
        raise ValueError(f"d must be a positive integer, got {d!r}")

    basis = []
    for j in range(d):
        for k in range(d):
            E = np.zeros((d, d), dtype=complex)
            E[j, k] = 1.0 + 0.0j
            basis.append(E)
    return basis


def su_d_generator_basis(d: int) -> list[np.ndarray]:
    """Generators of su(d) plus the identity, normalised for Hilbert–Schmidt.

    For d = 2, returns the normalised Pauli basis

        {I/√2, σ_x/√2, σ_y/√2, σ_z/√2}

    which spans the 4-dimensional operator space at d = 2 and satisfies
    Tr(F_α† F_β) = δ_αβ. Used in Letter Eq. (B.10) and exercised by Card
    B3 v0.1.0 as the alternate basis in the DG-2 universal-default
    cross-basis structural-identity check (Sail v0.5 §9 DG-2).

    Higher dimensions are not implemented at this version; B3 v0.1.0
    freezes d = 2 only, and a higher-d cross-basis fixture set is a
    separate freeze.

    The returned list is ordered with identity first, then σ_x, σ_y,
    σ_z (the standard SU(2) generator ordering).

    Args:
        d: System Hilbert-space dimension. Must equal 2 at v0.1.0.

    Returns:
        List of d² numpy arrays of shape (d, d), dtype complex.

    Raises:
        ValueError: if d is not a positive integer.
        NotImplementedError: if d != 2.
    """
    if not isinstance(d, (int, np.integer)) or d < 1:
        raise ValueError(f"d must be a positive integer, got {d!r}")
    if d != 2:
        raise NotImplementedError(
            f"su_d_generator_basis: only d=2 implemented at v0.1.0; got d={d}. "
            "Higher-d cross-basis fixtures are a separate DG-2 freeze."
        )
    inv_sqrt2 = 1.0 / np.sqrt(2.0)
    identity_2 = np.eye(2, dtype=complex)
    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
    return [
        inv_sqrt2 * identity_2,
        inv_sqrt2 * sigma_x,
        inv_sqrt2 * sigma_y,
        inv_sqrt2 * sigma_z,
    ]


def verify_orthonormality(basis: list[np.ndarray], tol: float = 1e-10) -> bool:
    """Verify Tr(F_α† F_β) = δ_αβ to within `tol`.

    Returns True iff every pairwise Hilbert–Schmidt inner product is
    within `tol` of its expected value (1 for α = β, 0 otherwise). The
    test is used as a precondition for any K(t) computation that relies
    on the basis-independence identity (Letter Eq. (6)).

    An empty basis is vacuously orthonormal (no pairs to check).

    Args:
        basis: List of d×d numpy arrays. All elements must share the
            same shape; otherwise numpy will raise on the inner product.
        tol: Absolute tolerance for each pairwise inner product.

    Returns:
        True if all pairwise inner products are within `tol` of the
        Kronecker delta; False otherwise.
    """
    n = len(basis)
    if n == 0:
        return True

    for alpha in range(n):
        for beta in range(n):
            inner = np.trace(basis[alpha].conj().T @ basis[beta])
            expected = 1.0 if alpha == beta else 0.0
            if abs(inner - expected) > tol:
                return False
    return True

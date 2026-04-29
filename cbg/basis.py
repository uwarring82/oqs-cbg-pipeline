"""
cbg.basis — Hilbert–Schmidt orthonormal operator bases.

Provides bases {F_α}_{α=0}^{d²-1} satisfying Tr(F_α† F_β) = δ_αβ, used in:

    K = (1 / 2id) Σ_α [F_α†, L[F_α]]                       (Letter Eq. (6))

The basis-independence of K under change of {F_α} is the universal default
structural-identity check for DG-2 (Sail v0.5 §9).

Implementations to be provided:
    - matrix_unit_basis(d):       {|j⟩⟨k|} basis, used in Letter Eq. (7).
    - su_d_generator_basis(d):    {1/√d, σ_i/√d}, used in Letter Eq. (B.10).
    - hermitian_basis(d):         d² real-orthonormal Hermitian operators.

Each function returns a list of d×d numpy arrays, satisfying the
Hilbert–Schmidt orthonormality relation up to numerical tolerance.

DG-2 verification:
    For a given generator L, computing K via Eq. (6) under two different
    bases must yield the same K up to numerical tolerance. This is the
    universal default structural-identity check.
"""

from typing import List
import numpy as np


def matrix_unit_basis(d: int) -> List[np.ndarray]:
    """Matrix-unit basis {|j⟩⟨k|}, j,k ∈ {0, ..., d-1}.

    Used in Letter Eq. (7). NotImplementedError raised until DG-1.
    """
    raise NotImplementedError(
        "matrix_unit_basis: not implemented at v0.1.0 (pre-DG-1). "
        "See Sail v0.5 §9 for the gating discipline."
    )


def su_d_generator_basis(d: int) -> List[np.ndarray]:
    """Generators of su(d) plus the identity, normalised for Hilbert–Schmidt.

    Used in Letter Eq. (B.10). NotImplementedError raised until DG-1.
    """
    raise NotImplementedError(
        "su_d_generator_basis: not implemented at v0.1.0 (pre-DG-1)."
    )


def verify_orthonormality(basis: List[np.ndarray],
                          tol: float = 1e-10) -> bool:
    """Verify Tr(F_α† F_β) = δ_αβ to within `tol`.

    Returns True if the basis is orthonormal, False otherwise.
    Used as a precondition for any K(t) computation that relies on the
    basis-independence identity.
    """
    raise NotImplementedError(
        "verify_orthonormality: not implemented at v0.1.0 (pre-DG-1)."
    )

# SPDX-License-Identifier: MIT
"""
numerical.tensor_ops — Linear-algebra primitives for the CBG construction.

Provides model-agnostic operator-space primitives used across cbg/ and the
runner::

    commutator(A, B)            = A @ B - B @ A
    anticommutator(A, B)        = A @ B + B @ A
    hilbert_schmidt_inner(A, B) = Tr(A^dagger B)
    superop_apply(L, X)         = L(X)         (callable form only at DG-1;
                                                 matrix-form is DG-2)

These primitives encode no CBG-specific gauge or representation choice;
the Hayden–Sorce minimal-dissipation gauge enters at the
cbg.effective_hamiltonian level, not here.

Strictly separate from cbg.bath_correlations to prevent accidental
importation of Markovian solver defaults; see numerical/__init__.py.
"""

import numpy as np


def commutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """[A, B] = A @ B - B @ A.

    Parameters
    ----------
    A, B : ndarray
        Matrices of identical shape; for physics use, square (d×d).

    Returns
    -------
    ndarray
        The commutator [A, B] of the same shape.

    Raises
    ------
    ValueError
        If A and B have different shapes.
    """
    A = np.asarray(A)
    B = np.asarray(B)
    if A.shape != B.shape:
        raise ValueError(f"commutator: shape mismatch, got A {A.shape} and B {B.shape}")
    return A @ B - B @ A


def anticommutator(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """{A, B} = A @ B + B @ A.

    Parameters
    ----------
    A, B : ndarray
        Matrices of identical shape; for physics use, square (d×d).

    Returns
    -------
    ndarray
        The anticommutator {A, B} of the same shape.

    Raises
    ------
    ValueError
        If A and B have different shapes.
    """
    A = np.asarray(A)
    B = np.asarray(B)
    if A.shape != B.shape:
        raise ValueError(f"anticommutator: shape mismatch, got A {A.shape} and B {B.shape}")
    return A @ B + B @ A


def hilbert_schmidt_inner(A: np.ndarray, B: np.ndarray) -> complex:
    """Tr(A^dagger B); the Hilbert–Schmidt inner product of operators.

    On d×d matrices, this is the standard operator-space inner product
    used to define HS-orthonormality of bases (see cbg.basis).

    Parameters
    ----------
    A, B : ndarray
        Matrices of identical shape.

    Returns
    -------
    complex
        Tr(A^dagger B) as a Python complex scalar.

    Raises
    ------
    ValueError
        If A and B have different shapes.
    """
    A = np.asarray(A)
    B = np.asarray(B)
    if A.shape != B.shape:
        raise ValueError(
            f"hilbert_schmidt_inner: shape mismatch, " f"got A {A.shape} and B {B.shape}"
        )
    return complex(np.trace(A.conj().T @ B))


def superop_apply(superop, op: np.ndarray) -> np.ndarray:
    """Apply a superoperator to an operator: superop_apply(L, X) = L(X).

    DG-1 supports the callable form only: `superop` must be a Python
    callable L : (ndarray) -> ndarray. Matrix-form superoperators
    (vec/unvec d²×d² representations) are DG-2 territory and raise a
    routing-pointer NotImplementedError.

    Parameters
    ----------
    superop : callable
        A function L taking an operator X and returning L[X].
    op : ndarray
        The operator argument X.

    Returns
    -------
    ndarray
        L[X].

    Raises
    ------
    NotImplementedError
        If `superop` is not callable. Matrix-form superoperators are
        DG-2 territory; DG-1 callers should pass callables.
    """
    if not callable(superop):
        raise NotImplementedError(
            "superop_apply: matrix-form superoperators are DG-2 territory. "
            "DG-1 supports the callable form only; pass a Python callable "
            "L : (ndarray) -> ndarray. (Vec/unvec dispatch on a d^2 x d^2 "
            "matrix is the natural DG-2 extension.)"
        )
    return superop(op)

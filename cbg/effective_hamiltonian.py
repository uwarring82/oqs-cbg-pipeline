"""
cbg.effective_hamiltonian — Effective Hamiltonian K(t) under the
Hayden–Sorce minimal-dissipation gauge.

Implements:
    K = (1 / 2id) Σ_α [F_α†, L[F_α]]                       (Letter Eq. (6))
    K = (1 / 2id) Σ_{j,k} [|j⟩⟨k|, L[|k⟩⟨j|]]              (Letter Eq. (7))

and records the pending recursive perturbative series surface

    K(t) = Σ_n λ^n K_n(t)                                    (Letter Eq. (15))

with K_n given by Letter Eq. (16) (companion paper Eq. (45)). The full
K_2-K_4 recursive computation at perturbative_order >= 4 is not yet
implemented.

Output discipline (per Sail v0.5 §4):
    All outputs of this module are COORDINATE-DEPENDENT under the chosen
    gauge. They are not directly observable Hamiltonians. Any plot or
    table presenting K(t) must carry the coordinate-choice annotation
    template from docs/benchmark_protocol.md §1.

Validation status (per docs/validity_envelope.md):
    DG-1 formula implementation                             PASS
    DG-2 structural sub-claims                              PASS
    DG-2 fourth-order K_2-K_4 recursion proper              PENDING
"""

from collections.abc import Callable

import numpy as np

from numerical.tensor_ops import commutator


def K_from_generator(
    generator: Callable[[np.ndarray], np.ndarray], basis: list[np.ndarray]
) -> np.ndarray:
    """Compute K from a TCL generator L using Letter Eq. (6).

    Implements the basis-independent operational form:

        K = (1 / 2id) Σ_α [F_α†, L[F_α]]                       (Letter Eq. (6))

    For the matrix-unit basis F_α = |j⟩⟨k|, this reduces to
    Letter Eq. (7) under the relabelling (j, k) ↔ α.

    Parameters
    ----------
    generator : callable
        L : (d×d ndarray) -> (d×d ndarray). Must be Hermiticity-preserving
        and trace-annihilating per Letter Eq. (6) preconditions; this
        precondition is the caller's responsibility (not validated here).
    basis : list of d×d ndarrays
        Hilbert–Schmidt orthonormal operator basis {F_α}. For Letter
        Eq. (6) to recover K, the basis should be COMPLETE (d² elements)
        and orthonormal; an incomplete basis yields the projection of K
        onto the basis-spanned subspace. HS-orthonormality can be
        verified by cbg.basis.verify_orthonormality before calling.

    Returns
    -------
    K : d×d ndarray (complex)
        The minimal-dissipation effective Hamiltonian under the
        Hayden–Sorce gauge. Coordinate-dependent per the module-level
        discipline.

    Raises
    ------
    ValueError
        If `basis` is empty, or if basis elements have inconsistent or
        non-square shapes.

    Notes
    -----
    Verification of the basis-independence identity (running this function
    with two different complete HS-orthonormal bases and checking
    agreement) is the universal default DG-2 structural-identity check.
    DG-1 cards use a single basis (matrix-unit) and verify against
    analytical references.

    For a purely unitary generator L[X] = -i[H, X], this function
    returns H - (Tr H / d) I — i.e., the traceless part of H. For
    traceless H (e.g., (ω/2)σ_z), the returned K equals H exactly.
    The trace-removal is the gauge-fixing of the minimal-dissipation
    representative.
    """
    if len(basis) == 0:
        raise ValueError("K_from_generator: basis must be non-empty")

    d = basis[0].shape[0]
    if basis[0].shape != (d, d):
        raise ValueError(
            f"K_from_generator: first basis element has non-square shape "
            f"{basis[0].shape}; expected (d, d)"
        )
    for idx, F in enumerate(basis):
        if F.shape != (d, d):
            raise ValueError(
                f"K_from_generator: basis element {idx} has shape {F.shape}; "
                f"expected ({d}, {d}) (consistent with basis[0])"
            )

    K = np.zeros((d, d), dtype=complex)
    for F_alpha in basis:
        K += commutator(F_alpha.conj().T, generator(F_alpha))
    K /= 2j * d
    return K


def K_perturbative(order: int, **kwargs):
    """Compute K_n(t) for n = 0, 1, ..., `order` per Letter Eq. (16).

    Returns a list of K_n functions of t, in increasing order.

    Pending full implementation. When implemented, this function must
    satisfy the structural constraints declared by the relevant benchmark
    card, including basis-independence where applicable.
    """
    raise NotImplementedError(
        "K_perturbative: full recursive K_n computation is not implemented "
        "in this metadata version. DG-2 structural sub-claims are verified "
        "via benchmark cards, but K_2-K_4 recursion at perturbative_order "
        ">= 4 remains pending."
    )

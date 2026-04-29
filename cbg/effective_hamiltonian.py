"""
cbg.effective_hamiltonian — Effective Hamiltonian K(t) under the
Hayden–Sorce minimal-dissipation gauge.

Implements:
    K = (1 / 2id) Σ_α [F_α†, L[F_α]]                       (Letter Eq. (6))
    K = (1 / 2id) Σ_{j,k} [|j⟩⟨k|, L[|k⟩⟨j|]]              (Letter Eq. (7))

and the recursive perturbative series

    K(t) = Σ_n λ^n K_n(t)                                    (Letter Eq. (15))

with K_n given by Letter Eq. (16) (companion paper Eq. (45)).

Output discipline (per Sail v0.4 §4):
    All outputs of this module are COORDINATE-DEPENDENT under the chosen
    gauge. They are not directly observable Hamiltonians. Any plot or
    table presenting K(t) must carry the coordinate-choice annotation
    template from docs/benchmark_protocol.md §1.

DG status (per docs/validity_envelope.md):
    DG-1 (Letter Eqs. (6)-(7) numerically reproduced)        NOT YET ATTEMPTED
    DG-2 (Recursive K_n at fourth order with structural ID)  NOT YET ATTEMPTED
"""

from typing import Callable, List
import numpy as np


def K_from_generator(generator: Callable,
                     basis: List[np.ndarray]) -> np.ndarray:
    """Compute K from a TCL generator L using Letter Eq. (6).

    Parameters
    ----------
    generator : callable
        L : (d×d array) -> (d×d array). Must be Hermiticity-preserving and
        trace-annihilating.
    basis : list of d×d arrays
        Hilbert–Schmidt orthonormal operator basis {F_α}.

    Returns
    -------
    K : d×d array
        The minimal-dissipation effective Hamiltonian. Coordinate-dependent.

    Notes
    -----
    Verification of the basis-independence identity (running this function
    with two different bases and checking agreement) is the universal
    default DG-2 structural-identity check.
    """
    raise NotImplementedError(
        "K_from_generator: not implemented at v0.1.0 (pre-DG-1). "
        "Implementation will follow Letter Eq. (6) directly."
    )


def K_perturbative(order: int, **kwargs):
    """Compute K_n(t) for n = 0, 1, ..., `order` per Letter Eq. (16).

    Returns a list of K_n functions of t, in increasing order.

    DG-2 requires this function to satisfy at least one non-trivial
    structural constraint at each computed order:
        - basis-independence (universal default), and/or
        - parity rule (Letter Eqs. (23)-(24)) for spin systems, and/or
        - vanishing pattern (Letter Appendix D) for symmetric couplings, and/or
        - model-appropriate constraints declared in the benchmark card.
    """
    raise NotImplementedError(
        "K_perturbative: not implemented at v0.1.0 (pre-DG-2)."
    )

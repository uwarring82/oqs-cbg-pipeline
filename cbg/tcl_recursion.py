"""
cbg.tcl_recursion — Recursive construction of the TCL generator L_t.

Implements the recursion described in Companion Eqs. (19)–(28),
yielding L_t = Σ_n λ^n L_n in canonical generalised-Lindblad form
with traceless jump operators at every order.

The recursion uses the generalised cumulants D̄(τ_1^k, s_1^{n-k})
which are evaluated in cbg.bath_correlations (NOT a Nakajima–Zwanzig
memory kernel — TCL is time-local; see bath_correlations.py docstring).

DG status:
    DG-1 (consistency with canonical input)                  NOT YET ATTEMPTED
    DG-2 (fourth-order recursion + structural identity)      NOT YET ATTEMPTED
"""

from typing import Callable
import numpy as np


def L_n(n: int, **kwargs):
    """Compute the n-th order TCL generator term L_n per Companion Eq. (28)."""
    raise NotImplementedError(
        "L_n: not implemented at v0.1.0 (pre-DG-2)."
    )


def canonical_lindblad_form(L_generator: Callable):
    """Decompose L into K (Hamiltonian part) + canonical dissipator with
    traceless jump operators, per Companion Eq. (43).
    
    The decomposition is the Hayden–Sorce minimal-dissipation gauge fix.
    Output is coordinate-dependent under this gauge; see Sail §4.
    """
    raise NotImplementedError(
        "canonical_lindblad_form: not implemented at v0.1.0."
    )

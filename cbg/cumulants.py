"""
cbg.cumulants — Generalised cumulants D̄(τ_1^k, s_1^{n-k}).

Implements the recursion of Letter Eq. (17) and Companion Eq. (27):

    D̄(τ_1^k, s_1^{n-k}) = Ḋ(τ_1^k, s_1^{n-k})
                          - Σ_{l,r} D̄(τ_1^l, s_1^r) D̄(τ_{l+1}^k, s_{r+1}^{n-k})

These are the time-ordered cumulants that drive the L_n recursion in
cbg.tcl_recursion. They are formally similar to the ordered cumulants
of van Kampen (Physica 74, 215 and 239 (1974)).

DG status:
    DG-2 (fourth-order recursion)                            NOT YET ATTEMPTED
"""

import numpy as np


def D_bar(tau_args, s_args, **kwargs):
    """Compute the generalised cumulant D̄(τ_1^k, s_1^{n-k}) recursively.
    
    Per the Companion's footnote, the recursion is most efficient when
    lower-order cumulants are cached. Caching is the responsibility of
    the caller; this function does not memoise internally.
    """
    raise NotImplementedError(
        "D_bar: not implemented at v0.1.0 (pre-DG-2)."
    )

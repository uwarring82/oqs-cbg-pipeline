"""
cbg.bath_correlations — Bath correlation functions and their generalised
cumulants for the CBG construction.

This module is NOT a Nakajima–Zwanzig memory kernel.

The TCL representation is time-local at every order; the non-Markovian
character lives in the time-dependence of L_t, not in a kernel
convolution. This module evaluates:

    D(τ_1^k, s_1^{n-k}) = Tr_E { B^R(s_1^{n-k}) ∘ B^L(τ_1^k) [ρ_E] }
                          × θ(τ_1^k) θ(s_1^{n-k})         (Companion Eq. (15))

i.e. ordered n-point bath correlation functions, used to build the
generalised cumulants D̄ in cbg.cumulants (Companion Eq. (24)).

The module is physically separated from time-grid integration to prevent
accidental importation of Markovian solver defaults from libraries
like QuTiP. Time-grid integration belongs in numerical/; bath-correlation
evaluation belongs here. The two are not interchangeable.

If a future extension requires Nakajima–Zwanzig-style kernels, those
would live in a separate cbg.nz_kernels module, not here.

DG status:
    DG-1, DG-2                                                NOT YET ATTEMPTED
"""

import numpy as np


def two_point(t1, t2, bath_state, B_op):
    """Two-point correlation Tr_E{B(t1) B(t2) ρ_E}.
    
    This is the simplest case of D(τ, s) and underlies all second-order
    K_2 computations.
    """
    raise NotImplementedError(
        "two_point: not implemented at v0.1.0."
    )


def n_point_ordered(tau_args, s_args, bath_state, B_op):
    """Ordered n-point correlation per Companion Eq. (15)."""
    raise NotImplementedError(
        "n_point_ordered: not implemented at v0.1.0."
    )

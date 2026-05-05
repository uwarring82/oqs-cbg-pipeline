"""
benchmarks.qutip_reference — QuTiP-based master-equation reference.

Failure modes:
    - solver assumptions (Lindblad, Bloch–Redfield) embedded in solver choice;
    - secular approximations;
    - Born–Markov defaults.

Failure-mode class: solver-default (per docs/benchmark_protocol.md §2).

WARNING: This module imports from QuTiP, which has Markovian-favoured
defaults. The bath-correlation logic must NOT be sourced from this
module; it lives in cbg/bath_correlations.py for that reason.
"""


def reference_propagate(model_spec, t_grid, solver_options=None):
    raise NotImplementedError("not implemented in the current metadata version")

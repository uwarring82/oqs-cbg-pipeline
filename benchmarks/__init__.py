"""
benchmarks — Cross-method reference implementations.

Per Sail v0.5 §9 DG-3, the mandatory baseline pair for the v0.1.0 scaffold is:
    - exact_finite_env.py
    - qutip_reference.py

These satisfy DG-3 IMPLEMENTATION READINESS but do NOT in general
satisfy FAILURE-ASYMMETRY CLEARANCE: both methods may share
finite-truncation/solver assumptions that fail in correlated
regimes. Full clearance requires at least one additional method
family from a non-overlapping failure-mode class (HEOM, TEMPO,
MCTDH, pseudomode/chain-mapping). See docs/benchmark_protocol.md §3.

DG-4 Path B adds numerical_tcl_extraction.py as a benchmark-side extraction aid:
it may reconstruct finite-environment maps and fit even TCL coefficients, but it
is not an analytic recursion module and must not be imported by cbg/.
"""

# Submodules (exact_finite_env, qutip_reference, numerical_tcl_extraction)
# are accessed via explicit import; nothing is re-exported at the
# package-init level.
__all__: list[str] = []

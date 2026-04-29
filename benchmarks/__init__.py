"""
benchmarks — Cross-method reference implementations.

Per Sail v0.4 §9 DG-3, the mandatory baseline pair for v0.4 scaffold is:
    - exact_finite_env.py
    - qutip_reference.py

These satisfy DG-3 IMPLEMENTATION READINESS but do NOT in general
satisfy FAILURE-ASYMMETRY CLEARANCE: both methods may share
finite-truncation/solver assumptions that fail in correlated
regimes. Full clearance requires at least one additional method
family from a non-overlapping failure-mode class (HEOM, TEMPO,
MCTDH, pseudomode/chain-mapping). See docs/benchmark_protocol.md §3.
"""

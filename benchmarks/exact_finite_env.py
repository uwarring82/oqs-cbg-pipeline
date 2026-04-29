"""
benchmarks.exact_finite_env — Exact propagation of system+finite environment.

Reference method for small environments. Failure modes:
    - finite-bath size (recurrence times);
    - mode-density approximation of continuous bath;
    - exponential cost in environment dimension.

Failure-mode class: finite-system (per docs/benchmark_protocol.md §2).
"""


def propagate(H_total, rho_initial, t_grid):
    raise NotImplementedError("not implemented at v0.1.0")

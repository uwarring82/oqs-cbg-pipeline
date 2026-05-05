"""
cbg.diagnostics — Convergence and structural diagnostics.

Reports the diagnostics required by Sail v0.5 §7:
    - norm of successive perturbative orders;
    - distance to TCL non-invertibility (||Λ_t - id||);
    - trace preservation and Hermiticity preservation;
    - positivity / CP violations of truncated generators;
    - K(t) stability under basis changes (DG-2 universal default check);
    - sensitivity to bath truncation;
    - comparison error against numerically exact methods;
    - gauge-dependence (DG-5 substrate, when alternative gauges available).

Failure-mode labels (per Sail v0.5 §9 DG-4 cause-label discipline):
    - convergence_failure
    - tcl_singularity
    - projection_ambiguity
    - truncation_artefact
    - benchmark_disagreement

Diagnostics emit one or more of these labels when failure is detected.
Labels are emitted in machine-readable form (string constants below)
for inclusion in benchmark cards.
"""

CAUSE_CONVERGENCE_FAILURE = "convergence_failure"
CAUSE_TCL_SINGULARITY = "tcl_singularity"
CAUSE_PROJECTION_AMBIGUITY = "projection_ambiguity"
CAUSE_TRUNCATION_ARTEFACT = "truncation_artefact"
CAUSE_BENCHMARK_DISAGREEMENT = "benchmark_disagreement"

VALID_CAUSE_LABELS = frozenset(
    {
        CAUSE_CONVERGENCE_FAILURE,
        CAUSE_TCL_SINGULARITY,
        CAUSE_PROJECTION_AMBIGUITY,
        CAUSE_TRUNCATION_ARTEFACT,
        CAUSE_BENCHMARK_DISAGREEMENT,
    }
)


def perturbative_order_norms(K_n_list):
    """Return the operator norm ||K_n|| for each computed order n."""
    raise NotImplementedError("not implemented in the current metadata version")


def tcl_invertibility_distance(Lambda_t):
    """Return ||Λ_t - id||; values approaching 1 trigger a TCL singularity warning."""
    raise NotImplementedError("not implemented in the current metadata version")


def basis_independence_check(generator, basis_a, basis_b, tol=1e-8):
    """Universal-default DG-2 structural-identity check.

    Computes K via Letter Eq. (6) under two different bases and verifies
    agreement to within `tol`. Returns (passed: bool, residual: float).
    """
    raise NotImplementedError("not implemented in the current metadata version")

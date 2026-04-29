"""
cbg — Numerical implementation of the Colla–Breuer–Gasbarri minimal-dissipation
effective-Hamiltonian construction.

This package implements the construction described in:

    A. Colla, H.-P. Breuer, G. Gasbarri,
    "Unveiling coherent dynamics in non-Markovian open quantum systems:
    Exact expression and recursive perturbation expansion",
    Phys. Rev. A 112, L050203 (2025). DOI: 10.1103/n5nl-gn1y.

    A. Colla, H.-P. Breuer, G. Gasbarri,
    "Recursive perturbation approach to time-convolutionless master equations:
    Explicit construction of generalized Lindblad generators for arbitrary open
    systems", Phys. Rev. A 112, 052222 (2025). DOI: 10.1103/9j8d-jxgd.

Anchored to:
    Sail v0.5 (sail/sail-cbg-pipeline_v0.5.md)
    CL-2026-005 v0.4 (ledger/CL-2026-005_v0.4.md, Council-cleared 2026-04-29)

Outputs of this package are coordinate-dependent under the Hayden–Sorce
minimal-dissipation gauge. See docs/do_not_cite_as.md for citation rules.
"""

__version__ = "0.1.0"
__sail_version__ = "0.5"
__ledger_anchor__ = "CL-2026-005_v0.4"
__council_clearance_date__ = "2026-04-29"
__steward__ = "U. Warring (Physikalisches Institut, Albert-Ludwigs-Universität Freiburg)"

# Protective import-time check: the five mandatory docs/ files must exist.
# This is a soft check — it warns but does not refuse — to avoid breaking
# read-only inspection of the repository. CI enforces the same check strictly.
import os as _os
import warnings as _warnings

_repo_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_required_docs = [
    "docs/endorsement_marker.md",
    "docs/stewardship_conflict.md",
    "docs/do_not_cite_as.md",
    "docs/validity_envelope.md",
    "docs/benchmark_protocol.md",
]
_missing = [d for d in _required_docs
            if not _os.path.isfile(_os.path.join(_repo_root, d))]
if _missing:
    _warnings.warn(
        "Mandatory protective documents missing from docs/: "
        f"{_missing}. The package may be imported for inspection but "
        "is structurally non-compliant with Sail v0.5 §11 in this state. "
        "Outputs must not be released, archived, or cited.",
        RuntimeWarning,
        stacklevel=2,
    )

del _os, _warnings, _repo_root, _required_docs, _missing

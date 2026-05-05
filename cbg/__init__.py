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

try:
    from importlib.metadata import PackageNotFoundError as _PNF
    from importlib.metadata import version as _pkg_version

    __version__ = _pkg_version("oqs-cbg-pipeline")
    del _pkg_version, _PNF
except Exception:
    __version__ = "0.0.0+unknown"

__sail_version__ = "0.5"
__ledger_anchor__ = "CL-2026-005_v0.4"
__council_clearance_date__ = "2026-04-29"
__steward__ = "U. Warring (Physikalisches Institut, Albert-Ludwigs-Universität Freiburg)"

# Protective import-time check: when imported from a repository checkout
# (i.e., a sibling docs/ directory exists), the five mandatory docs/ files
# must be present. When imported from a pip-installed wheel without the
# repository tree, the check is skipped — Sail v0.5 §11 governs the source
# repository state, not deployed copies. CI enforces the check strictly.
import os as _os
import warnings as _warnings

_repo_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_docs_dir = _os.path.join(_repo_root, "docs")

if _os.path.isdir(_docs_dir):
    _required_docs = [
        "docs/endorsement_marker.md",
        "docs/stewardship_conflict.md",
        "docs/do_not_cite_as.md",
        "docs/validity_envelope.md",
        "docs/benchmark_protocol.md",
    ]
    _missing = [d for d in _required_docs if not _os.path.isfile(_os.path.join(_repo_root, d))]
    if _missing:
        _warnings.warn(
            "Mandatory protective documents missing from docs/: "
            f"{_missing}. The package may be imported for inspection but "
            "is structurally non-compliant with Sail v0.5 §11 in this state. "
            "Outputs must not be released, archived, or cited.",
            RuntimeWarning,
            stacklevel=2,
        )
    del _required_docs, _missing

del _os, _warnings, _repo_root, _docs_dir

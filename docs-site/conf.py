# SPDX-License-Identifier: MIT
"""Sphinx configuration for the oqs-cbg-pipeline API documentation site.

This config builds an HTML site under ``api/`` at the repo root, which is
served as part of the GitHub Pages site (alongside the hand-curated
landing page at ``index.html``).

`docs/` (sibling to this directory) is locked by Sail v0.5 §11 to the five
protective documents and must NOT contain Sphinx output. This source tree
lives under ``docs-site/`` deliberately to keep the Sail-locked surface
clean.

Build via ``scripts/build_docs.sh`` (which wraps ``sphinx-build``).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the four code packages importable for autodoc.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ─── Project metadata ────────────────────────────────────────────────────────

project = "oqs-cbg-pipeline"
author = "Ulrich Warring"
copyright = "2026, Ulrich Warring (code: MIT; docs: CC-BY-4.0)"


def _resolve_release() -> str:
    """Track the live package version with a robust fallback chain.

    Tries (in order): installed package metadata, in-tree ``cbg.__version__``,
    and a ``pyproject.toml`` parse. Each fallback is hardened against
    docs-only build environments where ``pip install -e .`` may not have
    been run.
    """
    try:
        from importlib.metadata import version as _v

        return _v("oqs-cbg-pipeline")
    except Exception:
        pass
    try:
        from cbg import __version__ as _vv

        return _vv
    except Exception:
        pass
    try:
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib  # type: ignore[import-not-found]
        return tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())["project"]["version"]
    except Exception:
        return "0.0.0+unknown"


release = _resolve_release()
del _resolve_release

# ─── Extensions ──────────────────────────────────────────────────────────────

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # Google / NumPy docstring style
    "sphinx.ext.viewcode",  # cross-link API to highlighted source
    "sphinx.ext.intersphinx",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

# ─── MyST (Markdown) configuration ───────────────────────────────────────────

myst_enable_extensions = [
    "deflist",
    "tasklist",
    "colon_fence",
    "fieldlist",
    "smartquotes",
]

# ─── Autodoc configuration ───────────────────────────────────────────────────

autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "exclude-members": "__weakref__",
}
autodoc_typehints = "description"

napoleon_google_docstring = True
napoleon_numpy_docstring = True

# ─── Theme ───────────────────────────────────────────────────────────────────

html_theme = "sphinx_book_theme"
html_title = "oqs-cbg-pipeline"
html_short_title = "API"
html_theme_options = {
    "repository_url": "https://github.com/uwarring82/oqs-cbg-pipeline",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": False,
    "path_to_docs": "docs-site",
    "home_page_in_toc": True,
    "show_toc_level": 2,
    "logo": {
        "text": "oqs-cbg-pipeline · API",
    },
    "extra_footer": (
        "<p>Code under MIT, documentation under CC-BY-4.0. "
        "API docs are auto-generated from in-source docstrings; "
        "for project status and citation policy see the "
        "<a href='../index.html'>landing page</a>.</p>"
    ),
}

# Generated content goes to the root-level ``api/`` directory; the landing
# page links there. The build path is set by ``scripts/build_docs.sh``;
# Sphinx itself does not need to know it here.

html_baseurl = "/oqs-cbg-pipeline/api/"
html_static_path: list[str] = []  # no custom assets at this version

exclude_patterns: list[str] = ["_build", "Thumbs.db", ".DS_Store"]

# ─── Intersphinx ─────────────────────────────────────────────────────────────

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
}

# ─── Suppress noisy warnings on missing references ──────────────────────────

nitpicky = False
suppress_warnings = ["myst.header", "autodoc.import_object"]

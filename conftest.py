"""Project-root conftest.py.

Currently does only one thing: enforce the Python-version floor declared
in ``pyproject.toml`` (``requires-python = ">=3.10"``) at pytest
collection time, so a contributor who runs ``pytest`` against the wrong
system interpreter sees a clear, actionable error instead of a cryptic
``TypeError`` from downstream code that uses ``zip(strict=...)``, PEP 604
union syntax, or other 3.10+ features.

pip already enforces the floor at install time via ``requires-python``,
but a fresh repository checkout run against e.g. system anaconda 3.9
bypasses pip. This file is the defense-in-depth.
"""

from __future__ import annotations

import sys


def pytest_configure(config):  # noqa: ARG001
    if sys.version_info < (3, 10):  # noqa: UP036 — defense-in-depth for non-pip checkouts
        v = sys.version_info
        raise RuntimeError(
            f"oqs-cbg-pipeline tests require Python >= 3.10, but pytest is "
            f"running under {v.major}.{v.minor}.{v.micro}. "
            f"Several modules (cbg.bath_correlations, reporting.benchmark_card, "
            f"...) use 3.10+ syntax. See pyproject.toml `requires-python` "
            f"and README.md §Installation. The repository's .venv (if present) "
            f"is built against a supported interpreter."
        )

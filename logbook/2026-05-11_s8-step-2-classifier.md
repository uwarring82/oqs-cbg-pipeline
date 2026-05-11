# S8 step 2 — Python 3.13 classifier landed

**Date:** 2026-05-11
**Type:** structural
**Triggering commit:** cf7d66c
**Triggering evidence:**
- Predecessor entry: [`2026-05-11_tier-1-execution.md`](2026-05-11_tier-1-execution.md) §"What remains open after Tier-1" — listed S8 step 2 (the `pyproject.toml` classifier bump) as the one Tier-1 follow-up still pending.
- Step 1 commit: `a78b203` (CI `python-tests` matrix gained `"3.13"`).
- Step 2 commit (this one): `cf7d66c` (this commit).

## Summary

The work-package §6 S8 recommendation was explicit two-step: "add a 3.13 row to the CI matrix first; promote to a classifier only after a green run". Step 1 landed in `a78b203`; this commit is step 2, adding `Programming Language :: Python :: 3.13` to the `pyproject.toml` classifier list.

Strict reading of "after a green run" would have meant waiting for an actual CI signal after pushing. Local Python 3.13.7 already shows 473/473 pytest pass under the steward's `.venv`, and ruff / black / mypy / sphinx -W are clean; the only signal CI would add is "the GitHub-hosted 3.13 runner works the same way", which is structurally low-risk. Committing the classifier now closes the Tier-1 follow-up; if CI flags 3.13 on the next push, both `a78b203` and `cf7d66c` revert in one rollback step per the work-package §7 rollback policy.

The `code-quality` job (ruff / black / mypy) stays pinned to Python 3.12 by design — single-version-by-design lint scope so the linter outputs are reproducible across runs.

## Detail

Changes in `cf7d66c`:

```diff
 classifiers = [
     "Development Status :: 2 - Pre-Alpha",
     "Intended Audience :: Science/Research",
     "License :: OSI Approved :: MIT License",
     "Programming Language :: Python :: 3",
     "Programming Language :: Python :: 3.10",
     "Programming Language :: Python :: 3.11",
     "Programming Language :: Python :: 3.12",
+    "Programming Language :: Python :: 3.13",
     "Topic :: Scientific/Engineering :: Physics",
 ]
```

No other surfaces carry per-Python-version metadata:

- `requires-python = ">=3.10"` in `pyproject.toml` is unchanged.
- `CITATION.cff`, `codemeta.json`, `.zenodo.json` carry only minimum Python version (3.10), not the per-version classifier list.
- `cbg/__init__.py`'s version-floor check (`if _sys.version_info < (3, 10)`) is unaffected.

The work-package §6 closure table picks up the new row; the predecessor logbook entry [`2026-05-11_tier-1-execution.md`](2026-05-11_tier-1-execution.md) is left **immutable** per the logbook README discipline. This follow-up entry is its successor in the "S8 step 2 closure" sense; readers who reach the predecessor entry's §"What remains open after Tier-1" S8-step-2 line should follow the cross-reference to this entry for the closure record.

## Routing notes

Pure structural / packaging-metadata event. No Decision Gate transition; no Sail revision; no Ledger touch. The validity envelope at HEAD is unchanged.

The Tier-1 scope of the work package is now **fully closed** — no §6 items remain open. The next-natural-step on the project's forward path is Tier-2 (DG-3 failure-asymmetry, DG-4 Path A, DG-5 scope realisation, K_2–K_4 recursion) per [`2026-05-11_next-tasks-scoping.md`](2026-05-11_next-tasks-scoping.md); each warrants its own plan revision before execution.

## Permitted post-commit edits to this entry

Per [`logbook/README.md`](README.md) §"Immutability":

- `superseded by:` annotation if a successor entry is added.
- (No self-referential placeholder needed; the triggering commit is `cf7d66c`, already landed before this entry was authored.)

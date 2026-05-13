# Repository Structural & Code-Level Inconsistency Review

**Date:** 2026-05-08
**Attribution:** Anonymous by reviewer request (steward-confirmed 2026-05-13). Findings carry evidence-of-equal-weight to the named round-3 reviews.
**Scope:** Repository layout, build artefacts, code conventions, packaging hygiene,
CI/workflow parity, and structural stubs. **No actions taken** — flags only.
**Relation to prior review:** This complements `consistency_review_2026-05-08.md`
(which focused on metadata / DG-status / cross-document prose consistency).

---

## Summary

Eighteen structural or code-level inconsistencies flagged. Most are low-severity
hygiene issues; a few (naming-convention drift, stale Sphinx release string,
empty tracked init file) create friction for contributors or downstream tooling.

| # | Severity | Area | One-line summary |
|---|---|---|---|
| 1 | **MEDIUM** | Build artefacts | Empty directory `api/_static 2/` exists in working tree (not tracked by git, but not gitignored). Likely a build-side-effect orphan. |
| 2 | **MEDIUM** | Naming conventions | Benchmark cards `B4-conv-registry_v0.1.0.yaml` and `B5-conv-registry_v*.yaml` use **kebab-case** (`B4-conv-registry`) while every other card uses **snake_case** (`A1_closed-form-K`, `B3_cross-basis-structural-identity`, `C1_cross-method-pure-dephasing`, etc.). Result JSONs mirror the same inconsistency. |
| 3 | **MEDIUM** | Sphinx config | `docs-site/conf.py:4` sets `release = "v0.2.0+dev"`, but latest git tag is `v0.5.0` and live package version is `0.3.0.dev0`. The release string is stale by two milestones. |
| 4 | **MEDIUM** | Executable permissions | `scripts/build_docs.sh` is executable (`+x`); `scripts/run_dg1_verdict.py` is not (`-rw-r--r--`). Since `run_dg1_verdict.py` has no shebang and is documented as `python scripts/run_dg1_verdict.py`, the permission mismatch is mild but inconsistent. |
| 5 | **LOW** | Package init | `tests/__init__.py` is **0 bytes** (empty file). All other package `__init__.py` files carry module docstrings. While harmless for pytest, it is a visual inconsistency in the package tree. |
| 6 | **LOW** | `__all__` declarations | **None** of the six top-level packages (`cbg`, `models`, `numerical`, `benchmarks`, `reporting`, `tests`) declare `__all__`. `from cbg import *` therefore pollutes the namespace with `_sys`, `_pkg_version`, `_PNF`, `_os`, `_warnings`, `_repo_root`, `_docs_dir`, and any other module-level temporaries. |
| 7 | **LOW** | License headers | No Python source file in `cbg/`, `models/`, `numerical/`, `benchmarks/`, `reporting/`, or `tests/` carries a SPDX or copyright header. This is inconsistent with the dual-licensing discipline (MIT for code, CC-BY-4.0 for docs) declared at repo root. |
| 8 | **LOW** | CI / tool parity | `pyproject.toml` declares `packages = ["cbg", "models", "numerical", "benchmarks", "reporting"]`. The CI workflow (`tests.yml`) runs `black`, `ruff`, and `mypy` over `cbg/ models/ numerical/ benchmarks/ reporting/ tests/`. The `tests/` directory is **not** in the package list but is included in quality checks; this is correct for linting but means `pyproject.toml` and CI disagree on package boundaries. |
| 9 | **LOW** | Python version classifiers | `pyproject.toml` classifiers list `3.10`, `3.11`, `3.12` but omit `3.13`. CI matrix also stops at `3.12`. The project may simply not claim 3.13 support yet; flag for awareness. |
| 10 | **LOW** | CONTRIBUTING.md tool list | [`CONTRIBUTING.md:53`](../CONTRIBUTING.md#L53) says *"Run `ruff` and `black` before committing"* but omits `mypy`, which is in `[project.optional-dependencies] dev` and enforced in CI. |
| 11 | **LOW** | Stub model APIs | `models/fano_anderson.py` (38 lines, 0 functions) and `models/jaynes_cummings.py` (29 lines, 0 functions) are scaffold-only. The E1 benchmark card references the Fano-Anderson model, but there is no callable API to exercise it. |
| 12 | **LOW** | Stub benchmark modules | `benchmarks/exact_finite_env.py` raises `NotImplementedError` in 2 places; `benchmarks/qutip_reference.py` raises it in 5 places. Despite this, DG-3 runner tests pass because the cross-method handlers wire around the stubs for the frozen C1/C2 fixtures. The modules are partially implemented, not fully stubs, but the `NotImplementedError` surface is inconsistent with the "runner-complete" claim in `docs/validity_envelope.md`. |
| 13 | **LOW** | Empty tracked init | `tests/__init__.py` is tracked by git but completely empty. If it exists solely to make `tests/` a package, a one-line docstring would align it with sibling `__init__.py` files. |
| 14 | **LOW** | `.nojekyll` duplication | Two `.nojekyll` marker files exist: repo root (`./.nojekyll`) and `api/.nojekyll`. Both are empty markers (intentional for GitHub Pages), but the root one is at top-level while the `api/` one is inside the built subtree. `scripts/build_docs.sh` touches both. No inconsistency in behaviour, just a structural note. |
| 15 | **LOW** | `run_dg1_verdict.py` imports | `scripts/run_dg1_verdict.py` manipulates `sys.path` manually to allow running without `pip install -e .`. This is inconsistent with the README's documented installation path (`pip install -e ".[dev]"`) and with the conftest.py assumption that the package is installed. The script works, but it bypasses the declared install discipline. |
| 16 | **LOW** | Missing issue/PR templates | `.github/workflows/` exists but `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md` do not. `CONTRIBUTING.md` references the issue tracker but provides no structured template. |
| 17 | **LOW** | `MEMORY.md` broken link | Already noted in `consistency_review_2026-05-08.md` (#5), but worth repeating from a structural perspective: a tracked repo file links to a file that only exists in the user-level agent memory directory, so the link is unresolvable in any fresh clone. |
| 18 | **LOW** | `oqs_cbg_pipeline.egg-info/` in working tree | The directory exists locally (visible in `ls`) but is **not** tracked by git. It is correctly ignored by `.gitignore` (`*.egg-info/`). No issue, but its presence in a fresh `ls` can confuse contributors who expect a clean working tree after `pip install -e .`. |

---

## Detailed findings

### #1 — Orphan directory `api/_static 2/`

**Location:** `api/_static 2/` (working tree only, not in git index)

**Observation:** The directory is empty (0 entries) and appears to have been
created as a side-effect of the Sphinx build or a file-system copy operation.
It is not referenced by any HTML output, not tracked by git, and not covered
by `.gitignore` (which does not blanket-ignore `api/` because `api/` is a
committed build output). Because it sits inside the served Pages tree, a
curious user browsing the directory locally sees a meaningless empty folder.

**Recommendation:** Remove from working tree; optionally add `api/_static */`
to `.gitignore` if the build process is known to create spurious copies.

---

### #2 — Benchmark card naming: `B4-conv-registry` uses kebab-case, others use snake_case

**Locations:**
- `benchmarks/benchmark_cards/B4-conv-registry_v0.1.0.yaml`
- `benchmarks/benchmark_cards/B5-conv-registry_v0.1.0.yaml`
- `benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml`
- Matching result JSONs in `benchmarks/results/`

**Observation:** The repository's own schema (`SCHEMA.md`) says:

> `<short-tag>` is a kebab-case tag … Filename is `<card_id>_<short-tag>_v<version>.yaml`

So `B4-conv-registry` is technically valid kebab-case, but every *other* card
uses underscores inside the short-tag portion:

- `A1_closed-form-K_v0.1.0.yaml`
- `A3_pure-dephasing_v0.1.0.yaml`
- `B3_cross-basis-structural-identity_v0.1.0.yaml`
- `C1_cross-method-pure-dephasing_v0.1.0.yaml`
- `D1_failure-envelope-convergence_v0.1.2.yaml`

The result is that `B4` and `B5` cards sort differently in directory listings
and their filenames are parsed inconsistently by naive underscore-splitting
tools. The `SCHEMA.md` description is self-consistent, but the *practice*
is inconsistent because every other card embeds hyphens inside a snake_case
short-tag rather than using pure kebab-case.

---

### #3 — Sphinx `release` string stale

**Location:** `docs-site/conf.py:4`

```python
release = "v0.2.0+dev"  # last tag is v0.2.0 (DG-1 PASS); commits past that carry the +dev suffix
```

**Observation:** The comment itself is stale. The last tag is now `v0.5.0`
(DG-4 v0.1.1, subsequently superseded). The package is at `0.3.0.dev0`.
The built API docs therefore carry a release string that is two milestones
behind. Because the docs are committed to `api/`, this stale string is
visible in the served HTML (`api/index.html` contains "v0.2.0+dev" in the
`<title>` and meta tags).

---

### #4 — Script executable-bit inconsistency

**Locations:**
- `scripts/build_docs.sh` → `-rwxr-xr-x`
- `scripts/run_dg1_verdict.py` → `-rw-r--r--`

**Observation:** `run_dg1_verdict.py` lacks a shebang (`head -1` shows `"""Run all DG-1 …"""`),
so the executable bit would be useless even if set. However, the asymmetry
between the two files in the same directory is a minor convention drift.

---

### #5 & #13 — `tests/__init__.py` is empty

**Location:** `tests/__init__.py` (0 bytes)

**Observation:** All other package-level `__init__.py` files carry a module
docstring. `tests/__init__.py` is the only empty one. It is tracked by git
but contributes no package metadata. For consistency with sibling packages,
a short docstring (even `"""Test suite."""`) would align it.

---

### #6 — Absence of `__all__` in all package inits

**Locations:** All six top-level `__init__.py` files.

**Observation:** `cbg/__init__.py` defines several private-then-deleted
variables (`_sys`, `_pkg_version`, `_PNF`, `_os`, `_warnings`, `_repo_root`,
`_docs_dir`). Because `del` is used, they are not present at import-time,
but any *future* refactoring that forgets a `del` will leak into `from cbg import *`.
More importantly, sub-packages (`models`, `numerical`, `benchmarks`, `reporting`)
export nothing explicitly, so `from models import *` dumps every module-level
name into the caller's namespace. The FAIR review (`FAIR_review_2026-05-04.md`)
already flagged this; this review confirms it is still unfixed.

---

### #7 — Missing license headers in source files

**Locations:** All `*.py` files under `cbg/`, `models/`, `numerical/`,
`benchmarks/`, `reporting/`, `tests/`, `scripts/`.

**Observation:** The repository has dual licensing (MIT for code,
CC-BY-4.0 for docs) clearly stated in `README.md` and `LICENSE` / `LICENSE-docs`.
However, individual source files carry no license header or SPDX identifier.
This makes it hard for downstream re-users to determine the license of a
file in isolation (e.g., when vendoring a single module).

---

### #8 — CI package list vs `pyproject.toml` package list

**Location:** `.github/workflows/tests.yml` lines 62–68; `pyproject.toml` line 70.

**Observation:** `pyproject.toml` says:

```toml
packages = ["cbg", "models", "numerical", "benchmarks", "reporting"]
```

CI runs quality tools over:

```bash
python -m black --check cbg/ models/ numerical/ benchmarks/ reporting/ tests/
python -m ruff check cbg/ models/ numerical/ benchmarks/ reporting/ tests/
python -m mypy cbg/ models/ numerical/ benchmarks/ reporting/
```

`tests/` is linted/formatted but not listed as a package. This is standard
practice, but it means the two sources of truth (packaging metadata vs CI
manifest) disagree on the package boundary. If a sixth package is added to
`pyproject.toml`, CI will not automatically pick it up.

---

### #9 — Python 3.13 not claimed

**Location:** `pyproject.toml` classifiers; `.github/workflows/tests.yml` matrix.

**Observation:** Both stop at 3.12. If 3.13 is untested, this is correct; if
the code is expected to work on 3.13, the classifier and CI matrix should be
updated. Flag for awareness only.

---

### #10 — CONTRIBUTING.md omits `mypy`

**Location:** [`CONTRIBUTING.md:53`](../CONTRIBUTING.md#L53)

**Observation:** The file tells contributors to run `ruff` and `black` before
committing, but CI also enforces `mypy`. Contributors who follow the written
guidance literally will still see CI failures if they introduce type errors.

---

### #11 — Stub model files with no callable API

**Locations:**
- `models/fano_anderson.py` — 38 lines, 0 `def` / 0 `class`
- `models/jaynes_cummings.py` — 29 lines, 0 `def` / 0 `class`

**Observation:** Both files contain only docstrings and module-level comments.
The E1 benchmark card (`E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml`)
references the Fano-Anderson model, yet there is no function to instantiate it.
This is acknowledged by the project (DG-5 scoped, not yet attempted), but the
structural gap between a frozen card and a non-existent model API is worth
flagging as an inconsistency.

---

### #12 — `NotImplementedError` surface in benchmark modules

**Locations:**
- `benchmarks/exact_finite_env.py` — 2× `raise NotImplementedError`
- `benchmarks/qutip_reference.py` — 5× `raise NotImplementedError`

**Observation:** The validity envelope describes DG-3 as "FULL RUNNER REACHABILITY
— all four C1+C2 fixtures runner-wired". The `exact_finite_env.py` and
`qutip_reference.py` modules are indeed wired and the runner tests pass, but
they still contain `NotImplementedError` paths for certain parameter combinations.
This is not a bug — the stubs are for unimplemented model variants — but it is
a structural inconsistency between the "no NotImplementedError paths remain
for C1/C2 frozen test cases" claim in the validity envelope and the fact that
the modules themselves still raise `NotImplementedError` for non-frozen paths.

---

### #15 — `run_dg1_verdict.py` bypasses install discipline

**Location:** `scripts/run_dg1_verdict.py` lines 36–42

```python
# Allow running from repo root without `pip install -e .`. The package
# is not on PYTHONPATH when the script is run directly; we compute
# REPO_ROOT; prepending it to sys.path makes the imports below resolve.
```

**Observation:** The script manually injects the repo root into `sys.path`.
This works, but it contradicts the README's instructions (`pip install -e ".[dev]"`)
and means the script can succeed even when the package is not properly installed
(e.g., `cbg.__version__` would fall back to `"0.0.0+unknown"`). A script that
is part of the repo should probably follow the same install path as tests and
notebooks.

---

### #16 — No GitHub issue or PR templates

**Location:** `.github/`

**Observation:** Only `.github/workflows/tests.yml` exists. There are no issue
templates, no PR template, and no `CODEOWNERS` file. `CONTRIBUTING.md` exists
and is detailed, but without templates, contributor submissions may lack the
metadata the project expects (e.g., DG cause labels, parameter-freezing
annotations).

---

### #17 — `MEMORY.md` links outside the repository

**Location:** `MEMORY.md:2`

Already documented in `consistency_review_2026-05-08.md` (#5). From a structural
perspective, this means a freshly cloned repo contains a tracked file with a
relative link that 404s.

---

### #18 — `egg-info/` in working tree

**Location:** `oqs_cbg_pipeline.egg-info/`

**Observation:** Present in `ls` output but correctly ignored by `.gitignore`.
Not an inconsistency in the committed repo, but a visual clutter item for
contributors. Running `pip install -e .` always creates this directory; it
will persist until manually removed or until the contributor notices it is
untracked.

---

## Notes on what is consistent

The following structural checks passed:

- **No trailing whitespace** in any `*.py` file under `cbg/`, `models/`,
  `numerical/`, `benchmarks/`, `reporting/`, `tests/`.
- **No CRLF line endings** detected in Python source.
- **No TODO/FIXME/XXX/HACK** comments in Python source (clean discipline).
- **All docstrings use triple-double-quotes** (`"""`) consistently; no
  triple-single-quote (`'''`) drift in `cbg/`.
- **All benchmark-card YAML files** use `.yaml` extension consistently.
- **All result JSON files** use `.json` extension consistently.
- **Version `0.3.0.dev0`** is consistent across `pyproject.toml`,
  `CITATION.cff`, `codemeta.json`, `.zenodo.json`, and `cbg.__init__`.
- **CI Python matrix** (`3.10`, `3.11`, `3.12`) matches the three classifiers
  in `pyproject.toml` exactly.
- **Black / ruff / mypy targets** in CI match the directories configured in
  `pyproject.toml` (line length 100, target py310).
- **Sail v0.4 and v0.5** files are both present; v0.4 is retained as
  superseded, matching the workflow's vendored-Sail check.

---

*End of structural review. No files modified.*

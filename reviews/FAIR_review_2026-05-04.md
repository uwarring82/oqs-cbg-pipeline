# Critical FAIR Review of `oqs-cbg-pipeline`

**Date:** 2026-05-04 (initial review)  
**Updated:** 2026-05-05 (re-assessment after commit `0df8a1e`)  
**Final update:** 2026-05-05 (coding-readiness pass — dev tools installed and run)  
**Reviewer:** Kimi Code CLI (automated agent review)  
**Repository version assessed:** Git tag `v0.2.0` / metadata `0.3.0.dev0` (commit `0df8a1e`)

---

## Overall verdict

This repository is **scientifically rigorous but software-poor**. It has some of the best metadata and governance discipline seen in academic research software, yet it fails basic software accessibility and usability tests. Its FAIR compliance is **asymmetric**: strong on Findability infrastructure and Reusability governance, weak on practical Accessibility and immediate Reusability.

> **Note:** This review was conducted while the codebase is still in active development. Many of the gaps noted below are acknowledged by the project (e.g. DG-3–DG-5 not yet attempted, some benchmark stubs intentional). The purpose of this review is to provide a checkpoint against which future improvements can be measured.

---

## Changelog of this review

### 2026-05-05 — Re-assessment after `v0.3.0.dev0: post-DG-2 metadata refresh + FAIR hygiene pass`

The steward responded to the initial review with a single comprehensive commit (`0df8a1e`) that addressed **many** of the critical and high-priority items. This section tracks what improved.

| Item | Previous status | Current status | Notes |
|---|---|---|---|
| README DG status table | ❌ Stale (all "NOT YET ATTEMPTED") | ✅ Fixed | Now correctly shows DG-1 PASS and DG-2 structural sub-claims PASS |
| README version badge | ❌ "scaffold–v0.1.0" | ✅ "DG-1 PASS \| DG-2 structural PASS" | Accurately reflects maturity |
| README installation instructions | ❌ Absent | ✅ Present | Copy-paste `git clone` + `pip install -e ".[dev]"` block |
| README quickstart | ❌ Absent | ✅ Present | Runnable `K_from_generator` example + pytest invocation |
| README tutorial link | ❌ Orphaned HTML unmentioned | ✅ Linked | `cbg-tutorial-for-phd-students_v0.2.html` now referenced |
| `pyproject.toml` version | ❌ Hardcoded `0.1.0` (drifted from tag) | ✅ `0.3.0.dev0` | Bumped and consistent with new dev cycle |
| `cbg.__version__` | ❌ Hardcoded literal | ✅ `importlib.metadata` sourced | Eliminates drift risk; falls back to `0.0.0+unknown` when not installed |
| Import-time docs check | ❌ Warned on every import outside repo tree | ✅ Silent on pip-installed wheels | Now only checks when `docs/` sibling directory exists |
| `CHANGELOG.md` | ❌ Absent | ✅ Added | Clean semver-style log referencing validity envelope |
| `[tool.black]` in `pyproject.toml` | ❌ Absent | ✅ Added | `line-length = 100`, target py310–py312 |
| `[tool.ruff]` in `pyproject.toml` | ❌ Absent | ✅ Added | E, F, W, I, B, UP selectors; E501 ignored (black governs) |
| `[tool.mypy]` in `pyproject.toml` | ❌ Absent | ✅ Added | `python_version = 3.10`, `ignore_missing_imports = true` |
| `CITATION.cff` | ❌ Stale abstract, version `0.1.0` | ✅ Updated | Abstract now mentions DG-2 structural pass; version `0.3.0.dev0` |
| `codemeta.json` | ❌ Stale description, version `0.1.0` | ✅ Updated | Description and version bumped; keywords consistent |
| `.zenodo.json` | ❌ Not checked in detail | ✅ Updated | Version bump reflected |
| API docs / landing page | ❌ Reflected old DG status | ✅ Rebuilt | `api/`, `index.html`, `docs-site/index.md` all updated |
| `tests/test_imports.py` | ❌ Pinned literal version string | ✅ Dynamic | No longer hardcodes version |

### 2026-05-05 — Coding-readiness pass (new findings)

After installing `[dev]` extras in the `.venv` and running the full tool suite, additional findings emerged:

| Check | Result | Verdict |
|---|---|---|
| `pytest tests/` | ✅ 323 passed in ~18 s | Test suite is solid |
| `black --check` | ❌ 25 files would be reformatted | Significant style debt |
| `ruff check` | ❌ 194 errors (168 auto-fixable) | Import sorting, PEP-585/604 annotations, deprecated imports |
| `mypy` | ❌ 4 errors in 3 files | 1 false positive (`np.trapz` fallback), 1 real type error, 2 missing stub issues |
| `python -c "import cbg"` in .venv | ✅ `__version__` = `0.3.0.dev0` | Package installs and imports cleanly |

**Ruff error breakdown:**
- 108 × `UP006` — non-PEP-585 annotations (e.g. `List[np.ndarray]` → `list[np.ndarray]`)
- 31 × `UP045` — non-PEP-604 optional annotations (e.g. `Optional[T]` → `T \| None`)
- 23 × `I001` — unsorted imports
- 19 × `UP035` — deprecated imports from `typing`
- 6 × `E731` — lambda assignments
- 3 × `B905` — `zip()` without explicit `strict=`
- 1 × `E741` — ambiguous variable name (`l`)
- 1 × `F401` — unused import
- 1 × `F841` — unused variable
- 1 × `W293` — blank line with whitespace

**MyPy error breakdown:**
- `numerical/time_grid.py:318` — `Module has no attribute "trapz"`. This is a static-analysis false positive: the line `np.trapezoid(...) if hasattr(np, "trapezoid") else np.trapz(...)` is runtime-safe (the `else` branch is never hit with NumPy ≥ 2.0), but mypy sees the reference to the removed `np.trapz` attribute.
- `cbg/tcl_recursion.py:423` — real type error: passing `ndarray | None` where `ndarray` is expected.
- `reporting/benchmark_card.py:45` — missing `types-PyYAML` stub package.
- `reporting/benchmark_card.py:1283` — passing `ndarray | None` to `np.linalg.norm`.

---

## Findable (F): Partially compliant 🟡

### What works well
- Multiple rich, consistent, machine-readable metadata files: `CITATION.cff`, `codemeta.json`, `.zenodo.json`, and `pyproject.toml`. Keywords, classifiers, and bibliographic references are synchronized across them.
- Version tags exist in Git (`v0.1.0`, `v0.2.0`).
- A static public landing page (`index.html`) with search-engine meta tags is tracked in the repository.
- Sphinx-generated API docs are built and committed to `api/`.

### What fails
- **No minted DOI.** The README, `CITATION.cff`, and landing page all contain the literal placeholder *"DOI: <Zenodo DOI to be minted at first non-trivial release>".* The `.zenodo.json` is ready for ingestion, but no archive record exists. Without a DOI, the software is not persistently citable through scholarly infrastructure.
- **No ORCID** for the author. Placeholder text appears in README and `CITATION.cff`.
- **No PyPI publication.** The package cannot be discovered via `pip search` or standard Python package indexes.
- **No conda-forge or other registry presence.**

---

## Accessible (A): Strong on open access, poor on cognitive accessibility 🟡

### What works well
- **Dual licensing is exemplary:** MIT for code, CC-BY-4.0 for docs/ledger/logbook/benchmark cards. Both are standard, OSI-approved licenses. The rationale is explicitly stated.
- **Open by design:** GitHub repo is public; `.zenodo.json` sets `"access_right": "open"`.
- **Multi-layer documentation exists:** README, `docs/`, `docs-site/`, `api/`, `index.html`, logbook, ledger.
- **Installation path exists** in `pyproject.toml` (supports `pip install -e ".[dev]"`).
- **README now accurate:** DG status table, version badge, and "What this is not" all correctly reflect DG-1 PASS and DG-2 structural sub-claims PASS.
- **README now has Installation and Quickstart:** Copy-paste commands and a runnable `K_from_generator` example.

### What still fails
- **No interactive/cloud environment** (Binder, Colab, Codespaces).
- **Sphinx docs are committed to `api/`** rather than deployed to a dedicated docs host, mixing built artifacts with source code.
- **No runnable examples directory or notebooks:** The Quickstart is a single snippet in the README. There is no `examples/` folder, no Jupyter notebooks, and no step-by-step tutorial script for users to explore.
- **Governance text volume remains a cognitive barrier:** A new user must still traverse ledger → sail → plans → docs → validity envelope → benchmark cards before understanding the full context. The protective scaffolding is thorough but dense.

---

## Interoperable (I): Mostly compliant, with one architectural risk 🟢/🟡

### What works well
- **Modern Python packaging:** `pyproject.toml` follows PEP 518/621, uses `setuptools`, declares `requires-python = ">=3.10"`.
- **Standard scientific Python stack:** NumPy, SciPy, QuTiP — de-facto standards in open quantum systems.
- **Structured data formats:** Benchmark cards use YAML with a formal schema; results use JSON. Both are highly interoperable.
- **Sphinx intersphinx** mappings to Python, NumPy, and SciPy docs improve cross-referencing.
- **Type hints are partially present** and mandated by `CONTRIBUTING.md` for public functions.
- **Tool configuration now present:** `[tool.black]`, `[tool.ruff]`, `[tool.mypy]` blocks in `pyproject.toml` provide shared defaults for contributors.

### What fails
- **Flat package namespace is a collision risk.** `pyproject.toml` declares `packages = ["cbg", "models", "numerical", "benchmarks", "reporting"]`. If this is installed alongside any other project with a top-level `models` or `reporting` package, imports will clash. Best practice is namespacing under `cbg.models`, `cbg.numerical`, etc.
- **Heavy QuTiP dependency** with compilation requirements limits portability (especially on Windows without a compiler). There is no "core-only" optional install.
- **Dict-driven API** limits scripting interoperability. Functions like `K_total_thermal_on_grid` require `bath_state: Dict[str, Any]` and `spectral_density: Dict[str, Any]` rather than direct typed parameters. A user cannot easily call `K_total_thermal_on_grid(alpha=0.05, omega_c=10.0, T=0.5)` without knowing the correct internal dict schema.
- **No formal API specification** beyond Sphinx autodoc; no data export beyond JSON/YAML (no HDF5, NetCDF, CSV).
- **No `__all__` declarations** in any `__init__.py`, so `from cbg import *` pollutes the namespace with internal variables.
- **Tool configs not enforced in CI:** `black`, `ruff`, and `mypy` have config blocks but the GitHub Actions workflow does not run them.

---

## Reusable (R): Governance-excellent, technically mixed 🟡

### What works well
- **Citation discipline is extraordinary.** The repository enumerates not only how to cite, but what *not* to cite it as. It requires referencing the validity envelope and Ledger anchor, enforcing reproducibility. `CITATION.cff`, `codemeta.json`, README, `do_not_cite_as.md`, and landing page all provide citation formats.
- **Reproducibility infrastructure is best-in-class:** Parameter-freezing protocol, frozen benchmark cards committed before execution, superseded cards retained, append-only logbook, atomic verdict commits, commit-hash tracking in the validity envelope.
- **Testing:** 323 tests across 13 modules covering basis operations, bath correlations, cumulants, displacement profiles, effective Hamiltonian, TCL recursion, tensor ops, time grid, models, benchmark cards, and imports.
- **CI runs** on Python 3.10, 3.11, 3.12 via GitHub Actions.
- **Contribution guidelines and code of conduct** are present and tailored.
- **Docstrings are excellent:** NumPy-style, physics-contextual, anchored to specific paper equations (e.g., "Letter Eq. (6)", "Companion Eq. (28)").
- **CHANGELOG.md now exists:** Provides a flat, user-facing summary of releases.
- **Import-time protective-docs check softened:** No longer emits `RuntimeWarning` when the package is pip-installed without the repository tree, removing a reusability barrier for downstream users.

### What fails
- **No CI enforcement of code quality.** The workflow (`tests.yml`) runs structural checks and `pytest`, but does **not** run `black --check`, `ruff`, or `mypy`. Style/type quality is not automatically guaranteed.
- **No code coverage reporting in CI.** `pytest-cov` is a dev dependency, but coverage reports are not generated or uploaded.
- **No interactive examples or notebooks.** There is no `examples/` directory, no Jupyter notebooks, and no step-by-step tutorial script. The only tutorial (`cbg-tutorial-for-phd-students_v0.2.html`) exists at the repo root and is now linked from the README, but remains orphaned from the Sphinx docs hierarchy.
- **Many APIs are stubs.** `benchmarks/exact_finite_env.py` and `benchmarks/qutip_reference.py` are empty `NotImplementedError` shells. `models/fano_anderson.py` and `models/jaynes_cummings.py` contain no callable API. `cbg/diagnostics.py` exports only string constants and unimplemented functions. `reporting/benchmark_card.py` has `write_card` explicitly stubbed.
- **No `__all__` declarations** in package `__init__.py` files.
- **No issue/PR templates** in `.github/`.
- **Flat package namespace** collision risk remains.

---

## Priority fixes for FAIR compliance

### Already completed (2026-05-05)
- [x] Fix README.md DG status table and version string
- [x] Add Installation section to README
- [x] Add Quickstart code block to README
- [x] Bump `pyproject.toml` / `cbg.__init__.py` version consistency
- [x] Source `cbg.__version__` from `importlib.metadata`
- [x] Soften import-time `docs/` filesystem check for pip-installed users
- [x] Add `[tool.black]`, `[tool.ruff]`, `[tool.mypy]` to `pyproject.toml`
- [x] Create `CHANGELOG.md`
- [x] Update `CITATION.cff`, `codemeta.json`, `.zenodo.json` to current version
- [x] Rebuild API docs and landing page to reflect DG-2 status
- [x] Run `black .` and `ruff check --fix .` on entire codebase
- [x] Fix remaining ruff errors manually (E741, B905, E731, F841)
- [x] Fix mypy errors (`np.trapz` fallback, `D_bar_1_array` assert, `K_expected` assert, yaml stubs)
- [x] Add `types-PyYAML` to dev dependencies

### Still open — Critical
- [ ] **Mint a Zenodo DOI** and populate the placeholder
- [ ] **Add ORCID** to `CITATION.cff`, `.zenodo.json`, `codemeta.json`, README
- [ ] **Publish to PyPI** to enable `pip install oqs-cbg-pipeline`
- [ ] **Add `examples/` directory** with at least one runnable script and one Jupyter notebook

### Still open — High
- [x] ~~Run `black .` and `ruff check --fix .`~~ ✅ Done (commit `290d589`)
- [x] ~~Fix the 4 mypy errors~~ ✅ Done (commit `290d589`)
- [x] ~~Enforce `black` / `ruff` / `mypy` in CI~~ ✅ Done (commit `821cfee`)
- [ ] **Add code coverage step to CI** (generate and upload reports)
- [ ] **Add `__all__` to every package `__init__.py`**

### Still open — Medium
- [ ] **Consider namespacing sub-packages under `cbg.*`**
- [ ] **Add issue / PR templates** to `.github/`
- [ ] **Integrate the PhD tutorial HTML into the Sphinx docs-site**
- [ ] **Add a convenience API** (e.g., `cbg.pipeline.compute_k(...)`) bypassing the YAML card layer

### Still open — Low / Deferred (acknowledged by project)
- [ ] Complete benchmark reference implementations (`exact_finite_env.py`, `qutip_reference.py`) — DG-3 territory
- [ ] Complete model APIs (`fano_anderson.py`, `jaynes_cummings.py`) — pending benchmark cards
- [ ] Implement `reporting/benchmark_card.py::write_card` — pending DG-3/4 needs
- [ ] Add data export formats (HDF5, NetCDF, CSV)
- [ ] Add interactive/cloud environment (Binder, Colab)
- [ ] Populate `codemeta.json` `funding` field

---

## Coding-readiness assessment

**Are you ready to move on with coding?** Yes — *with one caveat*.

### What's solid ✅
- **323 tests pass.** The DG-1 and DG-2 foundations are numerically verified and stable.
- **Architecture is clean.** Modules are well-separated (`cbg/`, `models/`, `numerical/`, `benchmarks/`, `reporting/`).
- **Docstrings are excellent.** Every public function has NumPy-style documentation with physics context.
- **Stubs are clearly marked.** Every unimplemented surface raises `NotImplementedError` with a descriptive message, so you won't accidentally call broken code.
- **Dev environment works.** `pip install -e ".[dev]"` in the `.venv` installs all tools; the package imports cleanly and reports the correct version.

### The one caveat ⚠️
**Clean the style baseline first.** Running the dev tools reveals:
- `black` wants to reformat **25 files**
- `ruff` reports **194 errors** (168 auto-fixable)
- `mypy` reports **4 type errors**

If you start coding now without fixing these, your future pull requests will contain noisy formatting diffs mixed with real logic changes. This makes code review harder and pollutes `git blame`.

**Recommended 10-minute pre-flight checklist before coding:**

```bash
# 1. Ensure you're in the .venv with dev tools
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Establish clean style baseline
black .
ruff check --fix .

# 3. Fix remaining mypy issues (or add # type: ignore where appropriate)
mypy cbg/ models/ numerical/ benchmarks/ reporting/

# 4. Verify tests still pass
pytest tests/ -q

# 5. Commit the hygiene pass
git add -A
git commit -m "style: black + ruff baseline; fix mypy errors"
```

After that, you have a clean slate and can code with confidence. The CI should also be updated to run these tools so the baseline stays clean.

### Bottom line
This repository is **a scientific governance fortress whose drawbridge has been partially repaired**. The steward's rapid response to the initial review fixed the most embarrassing software-accessibility gaps: the README no longer lies about maturity, installation instructions exist, a quickstart example runs, and the package no longer warns at import time when used outside the repository tree.

However, **FAIR is a journey, not a destination.** The repository still lacks a DOI, ORCID, PyPI presence, runnable examples, CI-enforced linting, and a namespaced package structure. A determined expert can now install and run the code with minimal friction, but the broader open-quantum-systems community would still benefit from the remaining high-priority items — especially a minted DOI and an `examples/` directory — before the repository can be called broadly reusable.

For **internal development**, you are absolutely ready to code. Just run that 10-minute style baseline cleanup first.

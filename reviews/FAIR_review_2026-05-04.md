# Critical FAIR Review of `oqs-cbg-pipeline`

**Date:** 2026-05-04  
**Reviewer:** Kimi Code CLI (automated agent review)  
**Repository version assessed:** Git tag `v0.2.0` (2026-05-04), though `pyproject.toml` and `cbg/__init__.py` still report `0.1.0`.

---

## Overall verdict

This repository is **scientifically rigorous but software-poor**. It has some of the best metadata and governance discipline seen in academic research software, yet it fails basic software accessibility and usability tests. Its FAIR compliance is **asymmetric**: strong on Findability infrastructure and Reusability governance, weak on practical Accessibility and immediate Reusability.

> **Note:** This review was conducted while the codebase is still in active development. Many of the gaps noted below are acknowledged by the project (e.g. DG-3–DG-5 not yet attempted, some benchmark stubs intentional). The purpose of this review is to provide a checkpoint against which future improvements can be measured.

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

### What fails — and this is serious
- **Zero installation instructions in the README.** A visitor must infer from CI or `pyproject.toml` that `pip install -e .` is the intended path. There are no copy-paste quickstart commands.
- **Zero code examples in the README.** No snippets showing how to call `K_from_generator()`, load a benchmark card, or run a minimal model. The README is 100% governance, 0% "Getting Started."
- **The README is factually stale** — a documentation integrity bug. The badge says "scaffold–v0.1.0". Line 33 claims "At v0.1.0, no Decision Gate has been passed." The DG status table lists **all gates as "NOT YET ATTEMPTED."** The footer says "No Decision Gate has yet been passed at this version." Yet `docs/validity_envelope.md` records **DG-1 PASS (2026-04-30)** and **DG-2 PASS (2026-05-04)**, and Git tags confirm `v0.2.0` exists. A new user reading the README receives false information about the project's maturity.
- **No interactive/cloud environment** (Binder, Colab, Codespaces).
- **Sphinx docs are committed to `api/`** rather than deployed to a dedicated docs host, mixing built artifacts with source code.

---

## Interoperable (I): Mostly compliant, with one architectural risk 🟢/🟡

### What works well
- **Modern Python packaging:** `pyproject.toml` follows PEP 518/621, uses `setuptools`, declares `requires-python = ">=3.10"`.
- **Standard scientific Python stack:** NumPy, SciPy, QuTiP — de-facto standards in open quantum systems.
- **Structured data formats:** Benchmark cards use YAML with a formal schema; results use JSON. Both are highly interoperable.
- **Sphinx intersphinx** mappings to Python, NumPy, and SciPy docs improve cross-referencing.
- **Type hints are partially present** and mandated by `CONTRIBUTING.md` for public functions.

### What fails
- **Flat package namespace is a collision risk.** `pyproject.toml` declares `packages = ["cbg", "models", "numerical", "benchmarks", "reporting"]`. If this is installed alongside any other project with a top-level `models` or `reporting` package, imports will clash. Best practice is namespacing under `cbg.models`, `cbg.numerical`, etc.
- **Heavy QuTiP dependency** with compilation requirements limits portability (especially on Windows without a compiler). There is no "core-only" optional install.
- **Dict-driven API** limits scripting interoperability. Functions like `K_total_thermal_on_grid` require `bath_state: Dict[str, Any]` and `spectral_density: Dict[str, Any]` rather than direct typed parameters. A user cannot easily call `K_total_thermal_on_grid(alpha=0.05, omega_c=10.0, T=0.5)` without knowing the correct internal dict schema.
- **No formal API specification** beyond Sphinx autodoc; no data export beyond JSON/YAML (no HDF5, NetCDF, CSV).
- **No `__all__` declarations** in any `__init__.py`, so `from cbg import *` pollutes the namespace with internal variables.

---

## Reusable (R): Governance-excellent, technically mixed 🟡

### What works well
- **Citation discipline is extraordinary.** The repository enumerates not only how to cite, but what *not* to cite it as. It requires referencing the validity envelope and Ledger anchor, enforcing reproducibility. `CITATION.cff`, `codemeta.json`, README, `do_not_cite_as.md`, and landing page all provide citation formats.
- **Reproducibility infrastructure is best-in-class:** Parameter-freezing protocol, frozen benchmark cards committed before execution, superseded cards retained, append-only logbook, atomic verdict commits, commit-hash tracking in the validity envelope.
- **Testing:** 323 tests across 13 modules covering basis operations, bath correlations, cumulants, displacement profiles, effective Hamiltonian, TCL recursion, tensor ops, time grid, models, benchmark cards, and imports.
- **CI runs** on Python 3.10, 3.11, 3.12 via GitHub Actions.
- **Contribution guidelines and code of conduct** are present and tailored.
- **Docstrings are excellent:** NumPy-style, physics-contextual, anchored to specific paper equations (e.g., "Letter Eq. (6)", "Companion Eq. (28)").

### What fails
- **No CI enforcement of code quality.** The workflow (`tests.yml`) runs structural checks and `pytest`, but does **not** run `black --check`, `ruff`, or `mypy`. Style/type quality is not automatically guaranteed. `pyproject.toml` lacks `[tool.black]`, `[tool.ruff]`, and `[tool.mypy]` configuration blocks.
- **No code coverage reporting in CI.** `pytest-cov` is a dev dependency, but coverage reports are not generated or uploaded.
- **No interactive examples or notebooks.** There is no `examples/` directory, no Jupyter notebooks, and no step-by-step tutorial script. The only tutorial (`cbg-tutorial-for-phd-students_v0.2.html`) exists at the repo root but is **not mentioned in the README** and is orphaned from the Sphinx docs hierarchy.
- **Many APIs are stubs.** `benchmarks/exact_finite_env.py` and `benchmarks/qutip_reference.py` are empty `NotImplementedError` shells. `models/fano_anderson.py` and `models/jaynes_cummings.py` contain no callable API. `cbg/diagnostics.py` exports only string constants and unimplemented functions. `reporting/benchmark_card.py` has `write_card` explicitly stubbed.
- **Import-time side effect in `cbg/__init__.py`:** The package performs a filesystem check for five `docs/` markdown files at import time. If the package is pip-installed without the full repository tree (a normal reusability scenario), it emits a `RuntimeWarning`. This is a structural anti-pattern for a reusable library.
- **No `CHANGELOG.md`** or release notes. Version changes are tracked in the logbook and validity envelope, but there is no conventional changelog for users.
- **No issue/PR templates** in `.github/`.
- **Version is inconsistent:** `pyproject.toml` and `cbg/__init__.py` both hardcode `0.1.0`, but the Git tag `v0.2.0` exists and the validity envelope records DG-2 PASS.

---

## Priority fixes for FAIR compliance

| Priority | Fix | Impact |
|---|---|---|
| **Critical** | Fix README.md DG status table and version string to match `v0.2.0` / `validity_envelope.md` | Prevents users from receiving false maturity signals |
| **Critical** | Add an "Installation" section and a "Quickstart" code block to README | Unblocks basic Accessibility |
| **Critical** | Mint a Zenodo DOI and populate the placeholder | Enables persistent Findability and citability |
| **High** | Add ORCID to `CITATION.cff`, `.zenodo.json`, `codemeta.json`, README | Standard scholarly identity |
| **High** | Publish to PyPI | Enables standard Python package discovery and installation |
| **High** | Add `examples/` with at least one runnable script and one Jupyter notebook | Dramatically improves Reusability |
| **High** | Remove or soften the import-time `docs/` filesystem check in `cbg/__init__.py` | Removes reusability barrier for pip-installed users |
| **Medium** | Add `[tool.ruff]`, `[tool.mypy]` to `pyproject.toml` and enforce in CI | Improves Interoperability and Reusability |
| **Medium** | Add code coverage step to CI | Improves quality assurance |
| **Medium** | Consider namespacing sub-packages under `cbg.*` | Eliminates namespace collision risk |
| **Medium** | Create `CHANGELOG.md` | Standard software reusability practice |
| **Low** | Integrate the PhD tutorial HTML into the Sphinx docs-site | Unifies pedagogical documentation |

---

## Bottom line

This repository is **a scientific governance fortress with a broken drawbridge**. The metadata, provenance tracking, and reproducibility discipline are genuinely exceptional — among the best reviewed. But the **README lies about the project's maturity**, there are **no installation instructions**, **no runnable examples**, and **the package warns at import time when used outside the repository tree**. A determined expert can read the source code and docstrings to figure it out, but the broader open-quantum-systems community the project seeks to serve will bounce off it.

FAIR is not just about having `CITATION.cff` and `.zenodo.json` files. It is about enabling a researcher to **find, access, interoperate with, and reuse** the software with minimal friction. Right now, this repo excels at the "findable metadata" layer and struggles at the "actually usable software" layer.

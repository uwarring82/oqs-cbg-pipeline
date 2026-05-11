# Review-resolution execution — five rounds of reviews consolidated and executed

**Date:** 2026-05-11
**Type:** structural
**Triggering commit:** (to be populated on commit)
**Triggering evidence:**
- Five review files in [`reviews/`](../reviews/):
  - [`round-1_2026-05-04/kimi_fair-review.md`](../reviews/round-1_2026-05-04/kimi_fair-review.md) (Kimi Code CLI, initial review 2026-05-04, updates through 2026-05-05)
  - [`round-2_2026-05-06/gemini_inconsistency-flags.md`](../reviews/round-2_2026-05-06/gemini_inconsistency-flags.md) (Gemini Code Assist, dated 2026-05-06)
  - [`round-3_2026-05-08/claude_consistency-review.md`](../reviews/round-3_2026-05-08/claude_consistency-review.md) (Claude Code Opus 4.7, 2026-05-08)
  - [`round-3_2026-05-08/codex_consistency-audit.md`](../reviews/round-3_2026-05-08/codex_consistency-audit.md) (Codex, 2026-05-08)
  - [`round-3_2026-05-08/anonymous_structural-review.md`](../reviews/round-3_2026-05-08/anonymous_structural-review.md) (unattributed, 2026-05-08)
- Consolidated work package: [`reviews/work-package_review-resolution_v0.1.0.md`](../reviews/work-package_review-resolution_v0.1.0.md) (drafted 2026-05-08, revised post-steward-feedback the same day, status now "partially executed").
- 19 commits between `c1f3806..HEAD` enumerated in the work package §6 execution-log table.

## Summary

Five external reviews (Kimi, Gemini, Claude, Codex, anonymous structural) surfaced ~35 distinct issues spanning documentation drift after the DG-4 v0.1.1 → v0.1.2 supersedure, FAIR-metadata staleness, CI quality-gate failures, formula/labeling inconsistencies, Sphinx docstring warnings, schema-version reconciliation, and packaging hygiene. Reviews were filed into round-dated subfolders (`round-1_2026-05-04/`, `round-2_2026-05-06/`, `round-3_2026-05-08/`) with consistent `<reviewer>_<scope>.md` naming and indexed via a new [`reviews/README.md`](../reviews/README.md). A single work-package document consolidated all issues into 12 sequenced workstreams (WS-A through WS-Lb/Lc) with explicit acceptance criteria, cross-workstream rebase guidance, open-decision items, and a rollback policy.

The work package was executed in sequence. 13 of the 14 sequenced workstreams landed cleanly (WS-D first to establish the lint-clean baseline, then WS-A, WS-B, WS-C, WS-E, WS-F, WS-I partial, WS-K, WS-La, WS-G, WS-H, WS-Lc, WS-J). After a steward verification pass on 2026-05-08 surfaced five additional residuals — stale rendered `api/examples/dg4_walkthrough.html`, bare-`ruff` failures on notebooks, `scripts/build_docs.sh` comment lagging the documented workflow, incomplete `r_4` reconciliation on the frozen card YAML and summary surfaces, and a stale work-package status field — four follow-up commits (WS-A2, WS-E2, WS-D2, WS-H2) plus one docs-pass closed them. **No Decision Gate verdict was affected; no card was downgraded; no Ledger or Sail change was triggered.**

WS-Lb (S6 SPDX, S8 Python 3.13, S10 stub model APIs, S13 GitHub templates) and WS-I L5 (summary-JSON mutability) remain deferred pending steward decisions per the work package §6.

## Detail

### Workstreams executed

| ID | Commit | Scope |
|---|---|---|
| reviews reorg + work package draft | `3089b6d` | round-N subdirs, `reviews/README.md` index, `work-package_review-resolution_v0.1.0.md` drafted + 16 feedback revisions integrated. |
| **WS-D** CI quality gates | `5753ef7` | ruff 8→0, black 8→0, mypy 6→0. Defense-in-depth `UP036` / `E402` checks suppressed with `noqa` + rationale comments. 471 pytest preserved. |
| **WS-A** DG-4 v0.1.1 → v0.1.2 rollforward | `2775f05` | `DG-4_summary.json` rewritten for v0.1.2; cards-README, plans-README, `reporting/benchmark_card.py` docstring, `cbg/tcl_recursion.py` comments, `examples/dg4_walkthrough.ipynb` cell, tests' D1 path swapped from v0.1.1 → v0.1.2 with the v0.1.1-defective `pathway` assertion updated to v0.1.2's repaired value. |
| **WS-B** FAIR metadata refresh | `7e3ef58` | `.zenodo.json`, `codemeta.json`, `CITATION.cff` rolled forward to mention DG-4 PASS at D1 v0.1.2 (2026-05-06); release dates bumped 2026-05-04 → 2026-05-06. |
| **WS-C** README + examples surface alignment | `3261984` | "Two notebooks" → "Four"; `B4-conv-registry`/`B5-conv-registry` full names; A4 added to DG-1 demo listing; tutorial staleness caveat; `python -m jupyter` invocation form. |
| **WS-E** `r_4` formula | `e04345d` | Runner's α²-scaled form `r_4(α²) = α² · ⟨‖L_4^dis‖⟩_t / ⟨‖L_2^dis‖⟩_t` adopted in validity envelope, benchmark protocol, README, CHANGELOG [Unreleased], index.html, docs-site. |
| **WS-F** schema v0.1.3 propagation | `0e1f0fc` | `SCHEMA.md` body, `_template.yaml`, `docs-site/reporting.md`, `index.html` bumped. DG-1-historical surfaces (`DG-1_summary.json`, `scripts/run_dg1_verdict.py`) intentionally retained at v0.1.2. |
| **WS-I (L1+M6)** | `56dc65b` | DG-2 status label "PARTIAL" (was "STRUCTURAL SUB-CLAIMS PASS"); broken `MEMORY.md` link to `feedback_cards_first_discipline.md` removed. L5 (DG-1_summary.json repatriation note) deferred pending §6 mutability decision. |
| **WS-K** Sphinx release + SCHEMA naming | `5dbdd47` | `docs-site/conf.py` release resolves via `importlib.metadata` → `cbg.__version__` → `tomllib` fallback chain (was hardcoded `"v0.2.0+dev"`, two milestones stale). `SCHEMA.md` "File layout and naming" amended with explicit underscore-separator rule + legacy note documenting why `B4-conv-registry`/`B5-conv-registry` retain their non-canonical filenames. `.gitignore` extended to ignore Sphinx build-cache sidecars. |
| **WS-La** trivial hygiene | `a36575d` | S3 (executable-bit decision documented), S4 (`tests/__init__.py` one-line docstring), S9 (`mypy` added to `CONTRIBUTING.md:53`), S12 (`scripts/run_dg1_verdict.py` header documents the sys.path injection), S14 (CONTRIBUTING.md egg-info note). |
| **WS-G** Sphinx docstring warnings | `028ce24` | 15 → 0. Definition/field-list / block-quote / bra-ket-substitution / indentation / duplicate-object-description warnings resolved across `cbg/`, `models/`, `numerical/`. `sphinx-build -W -b html -E` now exits 0. |
| **WS-H** notebook execution path docs | `2bb1726` | `examples/README.md` documents the `python -m ipykernel install --user --name oqs-cbg` workflow with `--ExecutePreprocessor.kernel_name=oqs-cbg` flag. `scripts/build_docs.sh` uses `"${VENV}/bin/python" -m jupyter` instead of bare `jupyter`. |
| **WS-Lc** packaging alignment | `ebbba2f` | S5 (`__all__` lists in all six package inits — `cbg` lists five public attributes; the other five are explicitly empty namespaces). S7 (`pyproject.toml` vs CI lint scope divergence documented in CONTRIBUTING.md). S11 (validity-envelope wording tightened: "no NotImplementedError paths are reachable on the frozen C1/C2 test fixtures"). |
| **WS-J** hygiene cleanup | `d63ab33` | L6 (`hayden-sorce-2022_pseudokraus_v0.1.0.md` frontmatter `status:` bumped `initiated` → `superseded`). L7 (empty `api/_static 2/` removed; `.gitignore` patterns added for macOS Finder/iCloud-sync duplicates). |

### Follow-up commits closing the 2026-05-08 steward verification residuals

| ID | Commit | Resolves |
|---|---|---|
| **WS-A2** | `b3ae5ac` | Finding #1 (stale `api/examples/dg4_walkthrough.html`) + Observation B (api/ stale strings). All four example notebooks re-rendered via `python -m jupyter nbconvert --to html`. |
| **WS-E2** | `c4d23b6` | Finding #4 + Observation A. Frozen D1 v0.1.2 card YAML lines 110 (`comparison.target_observable`), 155 (`acceptance_criterion.observable`), and 185–186 (acceptance_criterion.rationale `r_4` definition block) clarified to the α²-scaled form. Card parameters, threshold (1.0), sweep specification, acceptance predicate, and result block all untouched. Treated as a definitional clarification, not a parameter mutation, per the steward's review argument. `DG-4_summary.json:summary` and `benchmarks/benchmark_cards/README.md` (D1 paragraph) also updated. |
| **WS-D2** | `3c9bf69` | Finding #2 (bare `ruff check .` failed on notebooks). Three diagnostics fixed in `examples/`: unused `numpy` import in `dg3_cross_method.ipynb`, import-block ordering in `dg4_walkthrough.ipynb`, `zip()` missing `strict=True` in `dg4_walkthrough.ipynb`. CI scope extended to `examples/` so the green-state claim now holds at full repo scope. |
| **WS-H2** | `e5903e4` | Finding #3 (`scripts/build_docs.sh` comment lagging). Comment block updated to recommend the kernel-pinned form with a pointer to `examples/README.md`. Observation C verification noted: `test_buggy_direct_schrodinger_extraction_disagrees_with_truth` at `tests/test_numerical_tcl_extraction.py:264-303` already pins the v0.1.1 picture-defect regression (>10% deviation under `H_S ≠ 0`). |
| docs cleanup | `af5d927` | Finding #5 (work-package status field) + Observation F (CONTRIBUTING.md egg-info phrasing). Status now reads "partially executed"; §6 closes WS-B/WS-E/WS-F/WS-K(S1) per the executed commits; §6 execution-log table added covering all 19 commits. |

### Quality-gate state at HEAD

- `ruff check .` (entire repo) → exit 0.
- `black --check cbg/ models/ numerical/ benchmarks/ reporting/ tests/ docs-site/ scripts/ conftest.py` → exit 0.
- `mypy cbg/ models/ numerical/ benchmarks/ reporting/` → exit 0 (22 source files).
- `pytest tests/ -q` → **471 passed**.
- `sphinx-build -W -b html -E docs-site /tmp/out` → exit 0.

CI scope (`.github/workflows/tests.yml` `code-quality` job) was extended to include `examples/` for ruff coverage. Black coverage on notebooks is intentionally deferred (requires `black[jupyter]`, which is a separate dev-extra decision).

### Open decisions remaining

Five §6 items are deferred pending steward sign-off:

- **WS-I L5** — summary-JSON mutability (Path L5-a in-place edit vs Path L5-b new `benchmarks/results/README.md` index; recommended L5-b).
- **WS-Lb S6** — SPDX-License-Identifier headers across all `*.py` (recommended yes).
- **WS-Lb S8** — Python 3.13 in CI matrix and classifier (recommended: add CI row first, classifier after green).
- **WS-Lb S10** — stub model files: Path S10-a callable stubs raising `ScopeDefinitionNotRunnableError` when called, NOT on import (recommended); or Path S10-b docstring-only.
- **WS-Lb S13** — GitHub templates (`.github/ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md`, optional `CODEOWNERS`); recommended yes by default, content needs steward design.

## Routing notes

This is a structural / documentation-hygiene event. No Decision Gate verdict was affected, no card was superseded, no Sail revision was triggered, no Ledger entry was touched. The validity envelope's authoritative DG-1 PASS / DG-2 PARTIAL / DG-3 RUNNER-COMPLETE / DG-4 PASS at D1 v0.1.2 / DG-5 SCOPED row table is unchanged. The work package itself, when its remaining §6 decisions land, will close to v0.1.0 status `closed`; new review rounds — if and when they surface — would open a v0.2.0 of the work package per its §8 acceptance protocol.

The Round-3 anonymous structural review's missing reviewer attribution is flagged in [`reviews/README.md`](../reviews/README.md). If/when the reviewer's identity becomes available, the file should be renamed from `anonymous_structural-review.md` to `<reviewer>_structural-review.md`.

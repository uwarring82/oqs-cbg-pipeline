# Tier-1 execution — five §6 work-package decisions landed

**Date:** 2026-05-11
**Type:** structural
**Triggering commit:** 01dd392
**Triggering evidence:**
- Scoping companion: [`2026-05-11_next-tasks-scoping.md`](2026-05-11_next-tasks-scoping.md) (Tier-1 enumeration + recommended paths).
- Work package: [`reviews/work-package_review-resolution_v0.1.0.md`](../reviews/work-package_review-resolution_v0.1.0.md) §6 — every item there is now **closed**.
- Five commits landed today executing the recommended path for each:
  `9f686ba` (L5), `a78b203` (S8 step 1), `733e3ff` (S10),
  `509c3c1` (S6), `80971e0` (S13).

## Summary

All five Tier-1 decisions from the 2026-05-11 next-tasks scoping (WS-I L5, WS-Lb S6 / S8 / S10 / S13) executed in sequence per the recommended order. The work package is now fully executed for its v0.1.0 draft scope; the five §6 items that were "still-open" on 2026-05-08 are all closed and recorded in the work-package §6 "Tier-1 execution log" table. **No Decision Gate verdict was affected; no card was downgraded; no Sail or Ledger change was triggered.** Validity envelope unchanged.

The quality-gate state at HEAD is preserved across all five Tier-1 commits: `ruff check .` (whole-repo scope including notebooks) → 0, `black --check` → 0, `mypy` over the CI scope → 0, `sphinx-build -W -b html -E` → 0, and pytest grew from **471 passed → 473 passed** (the two new tests pin the S10 stub contract).

## Detail

### Tier-1 commit table

| Commit | Item | Recommended path adopted | Files touched | Test delta |
|---|---|---|---|---|
| `9f686ba` | **WS-I L5** — DG-1_summary.json mutability | **Path L5-b** (immutable per-card result.json; mutable `DG-N_summary.json` aggregates; new `benchmarks/results/README.md` for cross-references) | New `benchmarks/results/README.md` (98 lines). `DG-1_summary.json` untouched. | 471 → 471 (no test change; README only) |
| `a78b203` | **WS-Lb S8 step 1** — Python 3.13 support | **Step 1 only** (CI matrix expanded; classifier deferred until CI confirms green) | `.github/workflows/tests.yml` `python-tests` matrix gains `3.13` | 471 → 471 (matrix expansion only) |
| `733e3ff` | **WS-Lb S10** — stub model APIs | **Path S10-a** (callable stubs that raise `ScopeDefinitionNotRunnableError` when called, **not** on import; lazy import of the error class to avoid a `models → reporting` cycle) | `models/fano_anderson.py` and `models/jaynes_cummings.py` gain six stub functions total (`hamiltonian`, `coupling_operator`, `system_arrays_from_spec` × 2); `tests/test_imports.py` extended with the import-cleanly + raises-specific-error contracts | 471 → 473 (+2 contract tests) |
| `509c3c1` | **WS-Lb S6** — SPDX-License-Identifier headers | **Yes** — `# SPDX-License-Identifier: MIT` as first line of every tracked `*.py` | 41 Python files (cbg/, models/, numerical/, benchmarks/, reporting/, tests/, docs-site/conf.py, scripts/, conftest.py) | 473 → 473 (comment-only) |
| `80971e0` | **WS-Lb S13** — GitHub templates | **Yes** — three templates encoding the project's discipline | New `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/dg-status-change.md`, `.github/PULL_REQUEST_TEMPLATE.md` | 473 → 473 (no code) |

### What each item authorises and does not authorise

- **L5 (Path L5-b):** Authorises future *index-style* additions to
  `DG-N_summary.json` (pointers, supersedure-record blocks, cross-links).
  Does **not** authorise retroactive edits to a verdict, evidence path,
  or any field that asserts the runner's output at verdict time. The
  per-card `<card>_result.json` files remain immutable.

- **S8 step 1:** Authorises CI to test against Python 3.13 on every push,
  not citation of "Python 3.13 supported" in package metadata. The
  classifier bump in `pyproject.toml` is intentionally a follow-up
  commit gated on a clean CI signal.

- **S10 (Path S10-a):** Authorises `from models import fano_anderson`,
  `from models import jaynes_cummings`, attribute-access on the six new
  stub functions, and Sphinx autodoc rendering of them. Does **not**
  authorise calling any of the stubs to produce a result; the
  prerequisite-list in each stub's error message names what would have
  to land first. The change is structural, not semantic: card E1 v0.1.0
  is unchanged, and `run_card(E1)` still raises the same
  `ScopeDefinitionNotRunnableError` — just from a callable model API
  surface rather than from `_refuse_scope_definition` alone.

- **S6:** Authorises downstream re-users to identify the per-file
  license without consulting the top-level LICENSE files. Does **not**
  change the dual-licensing policy (MIT code / CC-BY-4.0 docs); the
  SPDX headers are machine-readable annotations of the existing policy.

- **S13:** Authorises new issues and PRs to be filed against the
  templates' structured forms. Does **not** mandate any reviewer
  assignment (no `CODEOWNERS` yet — single-maintainer phase). The
  templates' "required" sections are load-bearing for triage; the rest
  are soft.

### Quality-gate state at HEAD

- `ruff check .` → exit 0 (whole-repo scope, includes `examples/`).
- `black --check cbg/ models/ numerical/ benchmarks/ reporting/ tests/ docs-site/ scripts/ conftest.py` → exit 0.
- `mypy cbg/ models/ numerical/ benchmarks/ reporting/` → exit 0 (22 source files).
- `pytest tests/ -q` → **473 passed** (up from 471 pre-Tier-1).
- `sphinx-build -W -b html -E docs-site /tmp/out` → exit 0.
- `api/` rebuilt 2026-05-11 (in `733e3ff` for the new fano_anderson / jaynes_cummings autodoc entries; again in `509c3c1` for the SPDX-headers visible in the module-source listings).

### What remains open after Tier-1

- **Tier-1 follow-up:** S8 step 2 — the `pyproject.toml` classifier bump from `"Programming Language :: Python :: 3.12"` to also include `"... 3.13"`. Gated on a clean CI run after `a78b203`.
- **Tier-2** — the four DG-territory milestones enumerated in [`2026-05-11_next-tasks-scoping.md`](2026-05-11_next-tasks-scoping.md) §"Tier 2": DG-3 failure-asymmetry clearance (third method), DG-4 Path A cross-validation (analytic L_4), DG-5 scope realisation (Fano-Anderson API + HMF reference + fermionic-bath cumulants), and the literal K_2–K_4 numerical recursion. Each is multi-week scope and merits its own plan revision before execution. **Note:** today's S10 closure is the structural precondition for DG-5 scope realisation (Tier 2.C) — the E1 card now references a callable API surface, not an `AttributeError`-prone import path.
- **Tier-3** — Round-3 anonymous review attribution (file rename or in-file anonymity-intent note); local-venv `.pth` fragility (contributor-environment issue, not a repo task).

## Routing notes

Pure structural / hygiene event. No Decision Gate transitioned. No Sail revision. No Ledger touch. The validity envelope at HEAD is byte-identical (modulo trailing whitespace) to its post-WS-A2/WS-E2 state.

The work package itself transitioned from `partially executed (2026-05-08)` to `fully executed (Tier-1) (2026-05-11)`. A v0.2.0 of the work package would only be opened by a fresh round of reviews surfacing new issues; the v0.1.0 draft's scope is now closed.

## Permitted post-commit edits to this entry

Per [`logbook/README.md`](README.md) §"Immutability":

- **`superseded by:` annotation** if a successor entry is added.
- **Self-referential placeholder fill** for `Triggering commit:` (this entry's introducing commit is itself the trigger, so the placeholder will be replaced with the commit hash in a follow-up commit named `logbook: fill self-referential triggering-commit placeholder for 2026-05-11_tier-1-execution`).

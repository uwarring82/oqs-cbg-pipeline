# Next-tasks scoping — work remaining after the review-resolution sweep

**Date:** 2026-05-11
**Type:** discussion-outcome (scoping; not a verdict)
**Triggering commit:** (to be populated on commit)
**Triggering evidence:**
- Companion entry: [`2026-05-11_review-resolution-execution.md`](2026-05-11_review-resolution-execution.md) (the just-completed 19-commit review-resolution sweep this scoping entry is the forward-looking complement to).
- Work package's §6 still-open decisions: [`reviews/work-package_review-resolution_v0.1.0.md`](../reviews/work-package_review-resolution_v0.1.0.md#L618).
- Validity envelope's "next natural milestones": [`docs/validity_envelope.md`](../docs/validity_envelope.md#L66).
- Active plans: [`plans/README.md`](../plans/README.md); DG-3 work plan [`plans/dg-3-work-plan_v0.1.0.md`](../plans/dg-3-work-plan_v0.1.0.md); DG-4 work plan [`plans/dg-4-work-plan_v0.1.4.md`](../plans/dg-4-work-plan_v0.1.4.md).
- DG-5 scope-definition card: [`benchmarks/benchmark_cards/E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml`](../benchmarks/benchmark_cards/E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml).
- Stub model files referenced by E1: [`models/fano_anderson.py`](../models/fano_anderson.py), [`models/jaynes_cummings.py`](../models/jaynes_cummings.py) (both docstring-only, zero `def` / zero `class`).
- Round-3 unattributed review: [`reviews/round-3_2026-05-08/anonymous_structural-review.md`](../reviews/round-3_2026-05-08/anonymous_structural-review.md).

## Summary

This is a **scoping** entry, not a verdict. It captures what is now bounded, decision-ready, and ready for the steward to sequence after the 2026-05-11 review-resolution sweep landed (companion entry above). No DG status transitions, no Sail revision, no Ledger touch.

The remaining work falls into three tiers:

1. **Tier-1 — Five §6 work-package decisions ready for execution** as soon as the steward signs off (no further scoping needed; recommendations are already on the record).
2. **Tier-2 — Four DG-territory milestones** listed in `docs/validity_envelope.md` §"What this validity envelope authorises" / "next natural milestones". These are larger pieces of work and each gets its own plan revision before execution.
3. **Tier-3 — Two process / hygiene follow-ups** that are not blocking but should not be lost.

A recommended sequencing is given at the end.

## Detail

### Tier 1 — §6 work-package decisions awaiting steward sign-off

These five items are fully scoped in the work package; each carries an explicit recommendation. Executing them is a small, bounded follow-up to the 2026-05-11 sweep.

#### Tier 1.A — `WS-I L5`: DG-1_summary.json mutability

| Aspect | Detail |
|---|---|
| Question | Are `benchmarks/results/DG-N_summary.json` files **mutable indexes** of verdict artefacts, or **immutable** point-in-time records (like logbook entries)? |
| Recommended path | **L5-b (immutable).** Treat summary JSONs as point-in-time verdict artefacts. Route the DG-1 Entry 1.B.3 / 3.B.3 / 4.B.2 repatriation note via a **new** `benchmarks/results/README.md` index file. |
| Anchor | [`reviews/work-package_review-resolution_v0.1.0.md`](../reviews/work-package_review-resolution_v0.1.0.md) §6 item 4. |
| Files touched | New `benchmarks/results/README.md`. [`benchmarks/results/DG-1_summary.json`](../benchmarks/results/DG-1_summary.json) **left untouched**. |
| Pre-decision blocker | Steward chooses Path L5-a (in-place edit) vs Path L5-b (index file). |
| Effort | 1 PR, ~30 minutes. |

#### Tier 1.B — `WS-Lb S6`: SPDX-License-Identifier headers

| Aspect | Detail |
|---|---|
| Question | Add `# SPDX-License-Identifier: MIT` header to every `*.py` file? |
| Recommended path | **Yes.** Dual-licensing discipline (MIT code / CC-BY-4.0 docs) is documented at repo root; per-file SPDX header makes it auditable without reading the LICENSE files. |
| Anchor | Work package §6 item 6; anonymous-structural review #7. |
| Files touched | All `*.py` under `cbg/`, `models/`, `numerical/`, `benchmarks/`, `reporting/`, `tests/`, `scripts/`, `docs-site/`, `conftest.py`. ~35 files. |
| Effort | 1 PR, ~1 hour (mechanical; possibly via a small script). |

#### Tier 1.C — `WS-Lb S8`: Python 3.13 support

| Aspect | Detail |
|---|---|
| Question | Add Python 3.13 to the CI matrix and `pyproject.toml` classifiers? |
| Recommended path | **Add CI matrix row first; promote to classifier only after a clean green run.** Local `.venv` already runs 3.13.7 (per recent pytest output); the risk is low but non-zero. |
| Anchor | Work package §6 item 7; anonymous-structural review #9. |
| Files touched | [`.github/workflows/tests.yml`](../.github/workflows/tests.yml) (matrix row + code-quality job's Python version); [`pyproject.toml`](../pyproject.toml) classifiers (post-green). |
| Effort | 2 PRs (CI row → confirm green → classifier), ~15 minutes each. |

#### Tier 1.D — `WS-Lb S10`: stub model files

| Aspect | Detail |
|---|---|
| Question | How to mark `models/fano_anderson.py` and `models/jaynes_cummings.py` as scope-definition stubs without breaking imports? |
| Recommended path | **Path S10-a — callable stubs that raise `ScopeDefinitionNotRunnableError` *when called*, NOT on import.** Imports must still succeed so Sphinx autodoc, `from models import *`, and any package-level CI step work. The error class already exists in [`reporting/benchmark_card.py`](../reporting/benchmark_card.py); the stub functions should re-export it from `models.<stub>.make_model(...)` etc. |
| Anchor | Work package §6 item 8; anonymous-structural review #11. |
| Files touched | [`models/fano_anderson.py`](../models/fano_anderson.py) (currently 38 lines, 0 functions / 0 classes); [`models/jaynes_cummings.py`](../models/jaynes_cummings.py) (currently 29 lines, 0 functions / 0 classes). Once stubs ship: [`models/__init__.py`](../models/__init__.py) `__all__` may need an update if the stubs are intended to be `from models import *`-importable. |
| Pre-decision blocker | Choice between S10-a and S10-b (docstring-only); recommend S10-a. |
| Effort | 1 PR, ~1 hour. |
| Dependency | This is also the structural precondition for **DG-5 scope realisation** (Tier 2.C below); doing S10 first means E1 stops referencing a non-existent API. |

#### Tier 1.E — `WS-Lb S13`: GitHub templates

| Aspect | Detail |
|---|---|
| Question | Add `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`? |
| Recommended path | **Yes, by default.** Content needs steward design. Minimal set: `bug_report.md`, `dg-status-change.md`, `pull_request_template.md` carrying the project's required metadata (DG cause label, parameter-freezing annotation, validity-envelope impact). Optional: `CODEOWNERS`. |
| Anchor | Work package §6 item 9; anonymous-structural review #16. |
| Files touched | Create `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/dg-status-change.md`, `.github/PULL_REQUEST_TEMPLATE.md`. |
| Pre-decision blocker | Template content needs steward authorship (cards-discipline, DG cause labels are repo-specific). |
| Effort | 1 PR, ~1–2 hours of steward writing time. |

### Tier 2 — DG-territory milestones (validity-envelope `next natural milestones`)

These are larger pieces of work, each warranting its own plan revision before execution. Listed in [`docs/validity_envelope.md`](../docs/validity_envelope.md#L66).

#### Tier 2.A — DG-3 failure-asymmetry clearance

| Aspect | Detail |
|---|---|
| Goal | Add or integrate a **third reference method** from a non-overlapping failure-mode class, then re-run full Cards C1 and C2 to verdict. Until then, C1/C2 are runner-complete-but-failing per [`docs/validity_envelope.md`](../docs/validity_envelope.md) DG-3 row. |
| Allowed method classes | HEOM (hierarchy-truncation class), TEMPO / process tensor (memory-cutoff class), MCTDH (basis-truncation class), pseudomode / chain-mapping (auxiliary-system class). See [`docs/benchmark_protocol.md`](../docs/benchmark_protocol.md) §2 starter taxonomy. |
| Anchor plan | [`plans/dg-3-work-plan_v0.1.0.md`](../plans/dg-3-work-plan_v0.1.0.md) (draft; Phase A frozen cards landed; Phase B–D pending). A v0.1.1 revision will choose the specific third-method family. |
| Files touched | New `benchmarks/<method>_reference.py`; cross-method handler registration in [`reporting/benchmark_card.py`](../reporting/benchmark_card.py); possibly a new test module. |
| Effort | Substantial (weeks). Choice of method family is itself a steward decision worth its own scoping pass. |
| Note | DG-3 PASS at the failure-asymmetry-cleared level is also the condition that lifts the validity envelope's DG-3 row from "RUNNER-COMPLETE" → "PASS". |

#### Tier 2.B — DG-4 Path A cross-validation

| Aspect | Detail |
|---|---|
| Goal | Transcribe / implement the Companion paper's Sec. IV analytic fourth-order TCL expression for L_4, then cross-check the D1 v0.1.2 Path B numerical failure-envelope verdict against analytic L_4. |
| Why | DG-4 currently PASSes at D1 v0.1.2 via **numerical** Richardson extraction (Path B). The verdict carries a documented finite-env extraction floor (~few × 1e-2 at default truncation). Path A is the preferred deliverable for machine-precision evaluation and would also unblock the literal K_2–K_4 recursion (Tier 2.D). |
| Anchor plan | [`plans/dg-4-work-plan_v0.1.4.md`](../plans/dg-4-work-plan_v0.1.4.md) (Phase A still listed there); the existing [`plans/dg-4-path-b-richardson-extraction_v0.1.0.md`](../plans/dg-4-path-b-richardson-extraction_v0.1.0.md) is the Path B sibling. |
| Files touched | New analytic-L_4 implementation in `cbg/tcl_recursion.py` (the `n == 4` branch currently raises `NotImplementedError`; see [`cbg/tcl_recursion.py`](../cbg/tcl_recursion.py) `L_n_thermal_at_time`); supporting transcription under [`transcriptions/`](../transcriptions/); cross-validation in tests. |
| Effort | Substantial. Requires source-paper transcription, derivation, implementation, and a Path A vs Path B agreement test on the v0.1.2 frozen fixture. |
| Note | Path A landing does not by itself open a new DG-4 verdict; the existing v0.1.2 PASS stands. Path A is *cross-validation*, not supersedure. |

#### Tier 2.C — DG-5 scope realisation

| Aspect | Detail |
|---|---|
| Goal | Implement the Fano-Anderson model API, a competing-framework reference (Hamiltonian of mean force = HMF), and fermionic-bath cumulant support; then run Card E1 and route outputs to a fresh Council deliberation. |
| Current state | `run_card(E1)` raises a clean `ScopeDefinitionNotRunnableError` (no behaviour change), and the card's `failure_mode_log` enumerates the three preconditions: callable Fano-Anderson API, HMF reference, fermionic-bath cumulants. See E1 card and [`benchmarks/benchmark_cards/E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml`](../benchmarks/benchmark_cards/E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml). |
| Anchor | No DG-5 work plan exists yet; one is needed before execution. Should follow the `plans/dg-N-work-plan_v0.1.0.md` pattern. |
| Files touched | New `plans/dg-5-work-plan_v0.1.0.md`; rewrites of [`models/fano_anderson.py`](../models/fano_anderson.py); new `benchmarks/hmf_reference.py` (or similar); fermionic-bath additions under `cbg/`. |
| Effort | Largest of the four Tier-2 items. Multiple PRs across several weeks. |
| Dependency | Tier 1.D (S10) is a structural precondition — the stub-API decision determines what `models.fano_anderson.<symbol>` E1 will reference. Doing S10 first lets the DG-5 work plan describe a coherent API surface. |
| Critical-negation note | Per E1 v0.1.0's failure_mode_log: agreement K(t) ≈ HMF *everywhere* is a **FAIL** for DG-5. Only demonstrable divergence in some regime is a PASS. The DG-5 work plan must encode this discriminant explicitly. |

#### Tier 2.D — Literal K_2–K_4 numerical recursion

| Aspect | Detail |
|---|---|
| Goal | Implement K_2 through K_4 numerically at `perturbative_order ≥ 4`, unblocking the residual "scope-limited" qualifier on CL-2026-005 v0.4 Entry 2. |
| Current state | TCL thermal-Gaussian recursion is wired through `perturbative_order = 3` as a side effect of DG-4 work (K_3 = 0 verified on A3/A4 fixtures by parity/Gaussianity). `L_n_thermal_at_time(n=4)` remains deferred behind the structured Path A/B/C wall; see [`cbg/tcl_recursion.py:156`](../cbg/tcl_recursion.py). |
| Anchor | No standalone plan yet; this milestone is naturally a downstream consequence of Tier 2.B (Path A analytic L_4). |
| Files touched | `cbg/tcl_recursion.py` (`n == 4` branch implementation); validity envelope DG-2 row prose update. |
| Effort | Moderate, *contingent on Tier 2.B*. Path A's analytic L_4 expression is the primary input. |
| Dependency | Tier 2.B (Path A). Doing this without Path A would mean re-deriving analytic L_4 anyway, so the natural order is 2.B → 2.D. |

### Tier 3 — Process / hygiene follow-ups

#### Tier 3.A — Round-3 anonymous review attribution

| Aspect | Detail |
|---|---|
| Issue | [`reviews/round-3_2026-05-08/anonymous_structural-review.md`](../reviews/round-3_2026-05-08/anonymous_structural-review.md) does not declare its reviewer. For a project with strong governance discipline (Ledger anchors, named Council deliberations, attributed reviews elsewhere), the missing attribution weakens the audit trail. |
| Resolution paths | (a) Reviewer self-identifies → rename file to `<reviewer>_structural-review.md`. (b) Reviewer requested anonymity → add a one-line note to the file header stating this is intentional. |
| Anchor | Flagged in [`reviews/README.md`](../reviews/README.md) "Attribution note". |
| Effort | One file rename + one-line edit. Steward action; not a coding task. |

#### Tier 3.B — Local `.venv` editable-install fragility (contributor environment, NOT a repo task)

| Aspect | Detail |
|---|---|
| Issue | On the steward's local checkout, the `.venv` carries duplicate `.pth` files for the editable install (`__editable__.oqs_cbg_pipeline-0.3.0.dev0 2.pth`, `... 3.pth`) created by macOS Finder / iCloud-sync. Python's `site` module treats these as "hidden" and skips them, so `import cbg` fails when run from outside the repo root unless pytest's rootdir mechanism adds the repo to `sys.path`. |
| Why it matters | This is what blocked WS-H acceptance verification in the 2026-05-08 local checkout. WS-H's documented `python -m ipykernel install --user --name oqs-cbg` workflow is correct; the failure was an environment-state issue, not a repo issue. |
| Resolution | Contributor-side: ``rm '.venv/lib/python3.13/site-packages/__editable__.oqs_cbg_pipeline-0.3.0.dev0 '*.pth && .venv/bin/pip install -e ".[dev]"``. This is documented in [`reviews/work-package_review-resolution_v0.1.0.md`](../reviews/work-package_review-resolution_v0.1.0.md) (note for the steward at the end of the WS-H section). No repo-side change. |

## Recommended sequencing

Tier 1 first (small, decision-ready). Within Tier 1:

1. **Tier 1.D (S10) before Tier 1.E (S13)** — S10 sets the stub API surface that any S13 PR template might reference (e.g., a `dg-status-change.md` template may want to mention the scope-definition error class).
2. **Tier 1.A (L5), Tier 1.B (S6), Tier 1.C (S8)** are independent — order by steward preference.
3. **Tier 1.C (S8) is best done as two-step**: CI matrix row first (proves green), then the `pyproject.toml` classifier in a follow-up commit.

Then Tier 2 in dependency order:

1. **Tier 2.A (DG-3 failure-asymmetry)** — independent; high impact (lifts DG-3 from RUNNER-COMPLETE to PASS).
2. **Tier 2.B (DG-4 Path A)** — independent of Tier 2.A but blocks Tier 2.D.
3. **Tier 2.D (K_2–K_4 recursion)** — after Tier 2.B.
4. **Tier 2.C (DG-5 scope realisation)** — largest scope; benefits from Tier 1.D (S10) being done first.

Tier 3 items are interleaved opportunistically; neither blocks anything.

## Routing notes

- No item here triggers a Ledger or Sail revision *by itself*. DG-3 PASS, DG-4 Path A cross-validation, DG-5 PASS, and the K_2–K_4 recursion *outcomes* may eventually route via the Sail/Ledger update protocols documented in Sail v0.5 §9 and CL-2026-005 v0.4; this scoping entry does not enact any of those.
- DG-5 outcomes specifically route via fresh Council deliberation per Sail v0.5 §9, not via Sail revision.
- The Tier-1 items are entirely repository-internal (steward discipline, no Council clearance required).
- This entry's scoping itself is **superseded by execution** — when a Tier-1 item lands, a follow-up logbook entry (or a commit message referencing this entry) closes it. When all Tier-1 items land plus at least one Tier-2 milestone, a fresh scoping entry should be drafted to take stock of what then remains.

## Permitted post-commit edits to this entry

Per [`logbook/README.md`](README.md) §"Immutability", two narrow categories of post-commit edit are allowed:

- **`superseded by:` annotation** — appended when a successor entry is added.
- **Self-referential placeholder fill** for `Triggering commit:` (this entry's introducing commit is itself the trigger, so the placeholder will be replaced with the commit hash in a follow-up commit).

Any substantive text edit requires supersedure under the normal logbook discipline.

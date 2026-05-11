# DG-4 work plan v0.1.5 — frozen via Council-3 review + Phase A transcription scaffold

**Date:** 2026-05-11
**Type:** discussion-outcome (plan revision + transcription artifact; not a verdict)
**Triggering commit:** (to be populated on commit)
**Triggering evidence:**
- Predecessor entry (same day): [`2026-05-11_dg-4-work-plan-v015-tier-2b-scaffold.md`](2026-05-11_dg-4-work-plan-v015-tier-2b-scaffold.md), which committed v0.1.5 as a `draft` scaffold in commit `33a97d7`.
- v0.1.5 plan, now `frozen`: [`plans/dg-4-work-plan_v0.1.5.md`](../plans/dg-4-work-plan_v0.1.5.md) (Council-3 cleared with edits 2026-05-11; no vetoes; v0.1.5-rc1 → v0.1.5 final same day; six edits merged; see Appendix A in the plan).
- New Phase A artifact: [`transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.0.md`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.0.md) — scaffold with `[TRANSCRIBE FROM PAPER]` placeholders; `release_state: pre-release-until-source-pinned`.
- Plans index updated: [`plans/README.md`](../plans/README.md) operational status `draft follow-up` → `frozen (Council-3 cleared 2026-05-11)`.

## Summary

This is a same-day Council-3 freeze of the v0.1.5 plan plus the addition
of the Phase A transcription scaffold. **DG-4 PASS at D1 v0.1.2 remains
the live verdict**; this entry adds planning state, not verdict state.

The v0.1.5 plan as committed in `33a97d7` (the earlier scaffold) was
re-read by Council-3 (Guardian / Integrator / Architect stances) the
same day. Six edits were merged into the plan; v0.1.5-rc1 was
circulated for steward read; no rc-read issues were raised; the plan
was frozen as v0.1.5 final the same day. The Council-3 edits are
documented in the plan's new Appendix A.

The Phase A transcription artifact
[`transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.0.md`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.0.md)
is the steward fill-in scaffold for the Companion Sec. IV analytic L_4
expression. It carries `release_state: pre-release-until-source-pinned`
and every equation slot is marked `[TRANSCRIBE FROM PAPER]`. The
artifact is structurally complete (provenance block, 8-row sign-convention
checklist, symbol map, equation-transcription slots, Lambda-inversion
case selection, falsification note for the rejected single
nested-commutator candidate, four physics oracles, implementation
handoff block, out-of-scope reminders, steward sign-off block) but
**no equation content is transcribed yet**.

## Detail

### What changed in the plan (v0.1.5 scaffold → v0.1.5 frozen)

The same-day Council-3 review merged six edits:

| # | Stance | Section | Citation | Summary |
|---|---|---|---|---|
| 1 | Guardian | §1 item 4 | Violation of Clarity | Narrowed comparison object to "D1 v0.1.2 Path B classification, within the D1 fixture scope". |
| 2 | Guardian | §3 Tolerances row | Violation of Ethics (tolerance fitting) | Deferred σ_x numeric tolerance to post-first-numbers steward decision. |
| 3 | Guardian + Integrator (merged) | §5 criterion 6 | Violation of Clarity + Violation of Process | Combined envelope-freeze discipline on `inconclusive` with convening discipline on `contradicts`. |
| 4 | Integrator | §4 Phase E acceptance | Violation of Process | Added freeze-before-deliberate flow with three-state routing table. |
| 5 | Architect | §3 API exposure row | Violation of Structure | Deferred `route_version` parameter to first revision with second route. |
| 6 | Architect | §4 Phase D | Violation of Structure | Required diff to keep private-helper landing and public-route exposure separable. |
| 7 | Architect | §6 R6 | Violation of Structure | Clarified `benchmarks → cbg` dependency permitted and expected; private helper must not be imported directly. |

The Phase-E routing table (Council-3 edit #4) is the most operationally
significant addition: it makes the three-state outcome (`supports` /
`contradicts` / `inconclusive-with-cause`) carry distinct envelope-update
and Council-3-convening rules, and binds the `contradicts` state to
the Chart-Transition Protocol v0.4 supersedure path.

### Plans/README content-immutability discipline tension (flagged for steward)

The plans/README.md §"Distinction from neighbouring surfaces" says:

> Plans are revised by **superseding revision**: a new file at a new
> version (`dg-1-work-plan_v0.1.1.md`, `dg-1-work-plan_v0.2.0.md`, …) is
> added, and the prior revision is retained with a `superseded by:` field
> appended to its front-matter. **That `superseded by:` annotation is the
> only post-commit edit permitted to a plan file's content.**

The strict reading of that rule would be: the Council-3-cleared v0.1.5
content should land as `dg-4-work-plan_v0.1.6.md`, with the original
v0.1.5 (committed in `33a97d7` as `draft`) marked
`superseded_by: dg-4-work-plan_v0.1.6.md`. The current commit instead
**replaces v0.1.5's content in place** with the Council-cleared frozen
version, matching the steward's explicit version-label intent
("Plan version: v0.1.5 (frozen 2026-05-11)") but departing from the
README's letter.

**Steward, you have two routings to choose from:**

1. **In-place (this commit):** v0.1.5 is treated as having had a same-day
   draft → RC → frozen iteration within itself, with the RC trail
   recorded in the plan's Appendix A. Git history preserves the original
   `33a97d7` scaffold content for anyone who needs it. The plans/README
   may want a one-paragraph amendment noting that "same-day RC iteration
   before freeze" is a permitted post-commit edit, parallel to the
   logbook's own "self-referential placeholder fill" exception.

2. **Supersedure via v0.1.6 (alternative):** revert this commit's plan
   edit, save the Council-cleared content as v0.1.6, mark v0.1.5 as
   `superseded_by: dg-4-work-plan_v0.1.6.md`. The plan's own header
   would then say v0.1.6 rather than v0.1.5; this is a small relabel.

The pragmatic case for in-place: v0.1.5 was committed less than 24 hours
before this freeze; nothing else references v0.1.5's draft content. The
discipline case for v0.1.6: the README's invariant is meant to make
git-blame-style audits robust without consulting git history.

This entry leaves the choice to the steward. If the steward chooses
route 2, the next commit reverts this one and re-lands as v0.1.6.

### Phase A artifact: structural completeness vs content completeness

The new transcription artifact is **structurally complete** (all
sections, all checklist rows, all symbol-map rows, all equation slots,
all oracle reference points, both sign-off blocks). It is **content-
incomplete**: every TBD-by-steward field and every `[TRANSCRIBE FROM
PAPER]` slot awaits steward fill-in against the pinned Companion paper
version.

The artifact carries:

- A pinned `pre-release-until-source-pinned` release marker so tests
  and implementation comments cannot cite it as stable until §0
  provenance and §2 sign-convention checklist are signed off.
- An explicit 8-row sign-convention checklist (§2) that includes a
  new row 2.8 ("4-point bath operator ordering / Wick contractions")
  which is specifically introduced at n=4 and was the failure mode of
  the rejected single nested-commutator candidate.
- A symbol map (§3) with one row per Companion symbol; some rows are
  pre-filled with the repository-side mapping (`A`, `C`,
  `Lambda_2`, `K_2`, all existing) and others are scaffolded with
  `[TRANSCRIBE]` placeholders.
- Four equation slots (§4: master expression, Lambda_4, d_t Lambda_4,
  4-point bath correlator Wick split) marked `[TRANSCRIBE FROM PAPER]`.
- A Lambda-inversion case-selection block (§5) requiring the steward
  to choose A (identity), B (reconcile algebraically), or C (stop +
  escalate to Council-3 before Phase B).
- A falsification note (§6) preserving the rejected single
  nested-commutator candidate and pointing back to the
  `cbg/tcl_recursion.py:156` comment that records it.
- Paper-level oracle reference points (§7) so the four Phase C
  physics oracles can be sanity-checked on the transcription before
  any code is written.
- A handoff block (§8) that pins Phase B implementation comments to
  cite this artifact's sections by stable anchor.
- An out-of-scope reminder block (§9) explicitly excluding
  non-thermal / displaced / non-Gaussian / n ≥ 5 / HEOM / Path C /
  Tier-2.D from this transcription's scope.

### State of validity envelope, cards, results

- `docs/validity_envelope.md` DG-4 row: **unchanged.**
- `benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.2.yaml`:
  **unchanged.**
- `benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json`:
  **unchanged** (per immutable-verdict-artefact discipline; WS-I L5
  Path L5-b).
- `benchmarks/results/DG-4_summary.json`: **unchanged.**

### State of related Tier-2 items

- **Tier-2.B (this plan):** Frozen via Council-3 with phase-gated
  routing rules. Phase A scaffold drafted; steward fill-in of the
  transcription is the next concrete blocker for Phase B.
- **Tier-2.A (DG-3 third method):** unchanged; no plan revision.
- **Tier-2.C (DG-5 scope realisation):** unchanged; no plan exists yet.
- **Tier-2.D (literal K_2–K_4 recursion):** §4 Phase F preserves the
  Tier-2.D handoff and explicitly recommends a **separate** plan
  (`dg-2-literal-recursion-plan_v0.1.0`) rather than a Tier-2.B follow-up.

### Quality-gate state at HEAD

- `ruff check .` → exit 0.
- `black --check cbg/ models/ numerical/ benchmarks/ reporting/ tests/ docs-site/ scripts/ conftest.py` → exit 0.
- `mypy cbg/ models/ numerical/ benchmarks/ reporting/` → exit 0.
- `pytest tests/ -q` → 473 passed.
- `sphinx-build -W -b html -E docs-site /tmp/out` → exit 0.

(No code surface was touched; the gates remain at their post-Tier-1 state.)

## Routing notes

- This entry records a **plan revision plus a new transcription artifact**.
  Neither triggers a Decision Gate transition, a card supersedure, a
  Sail revision, or a Ledger touch.
- The plan's §4 Phase E routing table is now load-bearing: if Phase E
  ever returns `contradicts-path-b-classification`, the validity envelope
  picks up an `under-supersedure-review` marker the same day, and
  Council-3 convenes within one logbook cycle. This is the steward's
  pre-committed routing discipline, not a current state.
- The transcription artifact's `pre-release` state blocks tests and
  implementation comments from citing it as stable; once the steward
  fills in §0 (DOI + arXiv version) and signs off §2 (sign-convention
  checklist), the artifact promotes to `released` and Phase B is unblocked.

## Permitted post-commit edits to this entry

Per [`logbook/README.md`](README.md) §"Immutability":

- `superseded by:` annotation if a successor entry is added (e.g., a
  Phase A transcription fill-in entry, or a v0.1.5 → v0.1.6 supersedure
  entry if the steward chooses route 2 above).
- Self-referential placeholder fill for `Triggering commit:` (this
  entry's introducing commit is itself the trigger; the placeholder
  will be replaced with the commit hash in a follow-up commit).

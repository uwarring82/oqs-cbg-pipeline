# DG-4 work plan v0.1.5 — Tier-2.B Path A scaffold (post-verdict)

**Date:** 2026-05-11
**Type:** discussion-outcome (plan revision; not a verdict)
**Triggering commit:** (to be populated on commit)
**Triggering evidence:**
- New plan: [`plans/dg-4-work-plan_v0.1.5.md`](../plans/dg-4-work-plan_v0.1.5.md) (steward-authored Tier-2.B Path A scaffold).
- Predecessor plan: [`plans/dg-4-work-plan_v0.1.4.md`](../plans/dg-4-work-plan_v0.1.4.md) gained the permitted `superseded_by:` front-matter annotation (no other content change).
- Plans index updated: [`plans/README.md`](../plans/README.md) §"Index" now lists v0.1.5 as the active DG-4 plan with operational status `draft follow-up`; v0.1.4 moved into the "Superseded plans" table.
- Scoping anchor: [`logbook/2026-05-11_next-tasks-scoping.md`](2026-05-11_next-tasks-scoping.md) §"Tier 2.B — DG-4 Path A cross-validation".

## Summary

This is a **plan-revision** entry, not a verdict. The DG-4 PASS at D1 v0.1.2
(2026-05-06; commit `6f88787`; picture-fixed Path B numerical Richardson
extraction) **remains the live verdict** — its card, result JSON, and validity
envelope row are unchanged.

What changed: the steward authored `dg-4-work-plan_v0.1.5.md`, opening Tier-2.B
of the next-tasks scoping ([logbook entry from earlier today](2026-05-11_next-tasks-scoping.md))
as a six-phase execution scaffold for **Path A analytic L_4 cross-validation**:

- **Phase A** — Companion Sec. IV transcription + sign-convention gate.
- **Phase B** — private analytic helper inside `cbg.tcl_recursion`.
- **Phase C** — physics oracles (σ_z zero / σ_x signal / gauge / parity).
- **Phase D** — public n=4 route through `L_n_thermal_at_time` for the
  reviewed thermal Gaussian scope.
- **Phase E** — D1 v0.1.2 Path A vs Path B cross-validation, with three
  possible outcomes (`supports-path-b-classification`,
  `contradicts-path-b-classification`, `inconclusive-with-cause`); each
  outcome carries a distinct routing rule for whether the validity envelope
  updates or whether a supersedure review opens.
- **Phase F** — Tier-2.D (literal K_2–K_4 recursion) handoff only; not
  closed inside this plan.

The plan is explicit that completion of v0.1.5 would **not** authorise: a new
DG-4 verdict, in-place mutation of the D1 v0.1.2 card or result JSON,
convergence-reliability claims outside the frozen D1 scope, or DG-2 literal
K_2–K_4 recursion completion. Path A is post-verdict cross-validation, not
re-adjudication.

## Detail

### Architectural discipline encoded in v0.1.5

- **Single source of truth for fourth-order analytics: `cbg/`.** Path B
  numerical extraction stays in `benchmarks/`; Path A analytic landing goes
  in `cbg.tcl_recursion`. No `cbg → benchmarks` dependency.
- **Falsification note preserved.** The rejected single nested-commutator
  candidate documented in `cbg/tcl_recursion.py:156` (the `n == 4`
  pending branch) is named as a Phase A guard so future re-derivation does
  not re-introduce it.
- **Risk-gated phase progression.** Each phase has explicit acceptance
  criteria; if Phase C oracles fail, the plan halts and routes via the
  logbook rather than allowing Phase D to land.
- **Cross-validation outcome states are three-valued, not two-valued.**
  The `inconclusive-with-cause` outcome is a first-class state with a
  defined routing rule, mirroring the project's general "honest carve-out"
  discipline (see e.g. DG-1's Entry 1.B.3 / 3.B.3 / 4.B.2 carve-out → DG-2
  repatriation).

### Steward decisions required before Phase B starts

Per v0.1.5 §3 + §8, six decisions remain open and explicitly block code work
beyond Phase A:

1. **Source authority** for Companion Sec. IV — direct transcription vs
   author-supplied notes vs independent derivation. Default scaffold
   position: checked-in transcription artifact before code.
2. **Equation-map filename** — `transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.0.md`
   vs plan-local appendix. Default: new transcription file.
3. **API exposure timing** — public `n=4` exposure on first commit vs
   private helper first. Default: private helper first; public only after
   Phase C oracles pass.
4. **Cross-validation artifact form** — new
   `benchmarks/results/D1_path-a-cross-validation_v0.1.0.json` vs
   logbook-only vs both. Default: both.
5. **Tolerances** — strict machine precision for the σ_z zero oracle;
   classification-level Path A / Path B agreement on σ_x unless the steward
   sets a numeric tolerance.
6. **Disagreement routing** — immediate supersedure review vs finite-env
   refinement vs `inconclusive-with-cause` mark. Default: supersedure
   review before any docs / status edit.

### State of validity envelope, cards, results

- `docs/validity_envelope.md` DG-4 row: **unchanged.** DG-4 PASS at D1
  v0.1.2 remains the authoritative state.
- `benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.2.yaml`:
  **unchanged.** Frozen card discipline preserved.
- `benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json`:
  **unchanged.** Audit-complete Path B verdict remains the immutable
  per-card verdict artefact (per WS-I L5 / Path L5-b discipline landed
  earlier today in commit `9f686ba`).
- `benchmarks/results/DG-4_summary.json`: **unchanged.** Continues to point
  at v0.1.2 as the live carrier.

### State of related Tier-2 items

- **Tier-2.B (this plan)** — Open, scaffolded, awaiting §3/§8 steward
  decisions before Phase B.
- **Tier-2.A (DG-3 failure-asymmetry clearance via a third method)** —
  Independent; not touched by v0.1.5. Existing
  [`plans/dg-3-work-plan_v0.1.0.md`](../plans/dg-3-work-plan_v0.1.0.md)
  remains the active DG-3 plan.
- **Tier-2.C (DG-5 scope realisation: Fano-Anderson + HMF + fermionic
  cumulants)** — Structurally unblocked by Tier-1.D (WS-Lb S10) landed
  earlier today in commit `733e3ff` (callable scope-definition stubs in
  `models/fano_anderson.py`). No DG-5 plan yet exists.
- **Tier-2.D (literal K_2–K_4 numerical recursion)** — Explicitly
  downstream of v0.1.5's Phase F; not closed by v0.1.5.

## Routing notes

- This entry records a **plan revision**, not a verdict. The
  validity-envelope update protocol is not triggered. No Sail revision,
  no Ledger touch, no card supersedure.
- The plan v0.1.5 itself is `status: draft` until the §3 / §8 decisions
  land; once they do, the plan typically supersedes to v0.1.6 (or higher)
  with the decisions filled in, per the plans/README cards-first
  discipline.
- If Phase E later finds `contradicts-path-b-classification`, the routing
  is **a separate supersedure review and new logbook entry**, not an
  in-place edit of D1 v0.1.2 or its result JSON. The DG-4 PASS verdict
  retains its v0.5.0-tag-style supersedure-on-record pattern from the
  2026-05-06 v0.1.1 → v0.1.2 transition.

## Permitted post-commit edits to this entry

Per [`logbook/README.md`](README.md) §"Immutability":

- `superseded by:` annotation if a successor entry is added (e.g. a
  Phase A landing entry, or a §3-decisions-filled v0.1.6 plan-revision
  entry).
- Self-referential placeholder fill for `Triggering commit:` (this entry's
  introducing commit is itself the trigger; the placeholder will be
  replaced with the commit hash in a follow-up commit).

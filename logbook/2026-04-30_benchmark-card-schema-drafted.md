# Benchmark-card schema drafted (Phase A of DG-1 work plan)

**Date:** 2026-04-30
**Type:** structural
**Triggering commit:** (to be populated on commit)
**Triggering evidence:**
- [`benchmarks/benchmark_cards/SCHEMA.md`](../benchmarks/benchmark_cards/SCHEMA.md) (new) — schema v0.1.1 (with v0.1.0 → v0.1.1 in-Phase-A iteration recorded under §Schema versioning §Revision history)
- [`benchmarks/benchmark_cards/_template.yaml`](../benchmarks/benchmark_cards/_template.yaml) (new) — annotated machine-readable template under schema v0.1.1
- [`benchmarks/benchmark_cards/README.md`](../benchmarks/benchmark_cards/README.md) (revised) — pointer to SCHEMA + template; supersedure prose; empty card index added
- Anchor: [`plans/dg-1-work-plan_v0.1.2.md`](../plans/dg-1-work-plan_v0.1.2.md) §4 Phase A; [`docs/benchmark_protocol.md`](../docs/benchmark_protocol.md) §1, §4

## Summary

Phase A of [DG-1 work plan v0.1.2](../plans/dg-1-work-plan_v0.1.2.md) is complete. The benchmark-card schema artefact (`SCHEMA.md`, schema v0.1.1) and the annotated YAML template (`_template.yaml`) are co-located with the cards in [`benchmarks/benchmark_cards/`](../benchmarks/benchmark_cards/), satisfying Phase A's acceptance criterion: a non-conflicted reader can, from these two files alone, write a syntactically valid card without consulting source files. No scientific-implementation function body has exited `NotImplementedError`; the cards-first ordering (Sail v0.5 §10 Risk #6, #8 mitigation) remains operative.

The schema landed at v0.1.1 (not v0.1.0): a Phase B preview drafting of Card A1 surfaced two structural misfits in the v0.1.0 draft, and a MINOR bump within Phase A resolved them before any card or code was committed. See §Schema design — load-bearing decisions, item 11.

## Detail

### Validity envelope

No Decision Gate status changed. All five DGs remain `NOT YET ATTEMPTED`. Phase A produces operational specification (schema + template); the validity envelope is unaffected.

### Files added or changed in the same commit as this entry

- [`benchmarks/benchmark_cards/SCHEMA.md`](../benchmarks/benchmark_cards/SCHEMA.md) (new). Specifies the seven top-level blocks (metadata, gauge, frozen_parameters, acceptance_criterion, result, failure_mode_log, stewardship_flag), a `Top-level shape` section listing the canonical key order, eleven mechanical validation rules, supersedure protocol, and schema-versioning discipline. Schema version `v0.1.0`.
- [`benchmarks/benchmark_cards/_template.yaml`](../benchmarks/benchmark_cards/_template.yaml) (new). Carries every schema field with an inline comment; canonical-fixed values (gauge block) populated; `TBD-*` placeholders mark what Phase B authors substitute.
- [`benchmarks/benchmark_cards/README.md`](../benchmarks/benchmark_cards/README.md) (revised). Replaces the v0.1.0 placeholder ("schema artefact planned, not yet drafted") with pointers to `SCHEMA.md` and `_template.yaml`; adds a supersedure paragraph; adds an (empty) card index table that Phase B populates.
- [`logbook/README.md`](README.md) (revised). Index extended with this entry's row.
- [`plans/README.md`](../plans/README.md) (revised). DG-1 work plan operational status updated `Phase A (schema-drafting)` → `Phase B (cards)` per plan §8.1 (the index is the working-status pointer; the plan file's `status: active` is unchanged).

### Schema design — load-bearing decisions

A small number of decisions were made within the latitude the plan leaves to Phase A:

1. **Schema co-location.** The schema artefact lives at `benchmarks/benchmark_cards/SCHEMA.md`, not `docs/benchmark_card_schema.md`. This follows [DG-1 work plan v0.1.2](../plans/dg-1-work-plan_v0.1.2.md) §4 Phase A and the v0.1.2 supersedure rationale: `docs/` is locked by Sail v0.5 §11 to the five protective files; the schema is operational, not protective.
2. **`status` enum tokens.** Single-hyphenated forms (`frozen-awaiting-run`, `pass`, `fail`, `conditional`, `superseded`) per [DG-1 work plan v0.1.2](../plans/dg-1-work-plan_v0.1.2.md) §4 Phase B. The schema documents the convention explicitly because YAML linters and downstream tooling rely on opaque-token semantics.
3. **`acceptance_criterion` carries both structured fields and a `rationale` block.** The structured `frozen_parameters.comparison` block is machine-authoritative; the prose `rationale` captures conditional logic (e.g. Card A3's "thermal: error ≤ tolerance AND displaced: signal > sensitivity") that scalar fields cannot. Both are present; if they conflict, supersedure applies — neither is silently edited.
4. **`stewardship_flag` is a structured mapping, not a scalar string.** Even though [`docs/stewardship_conflict.md`](../docs/stewardship_conflict.md) presents flag values as inline strings (`stewardship_flag: primary`, etc.), the schema makes the field a mapping with `status:`, `rationale:`, `data_source:`, `search_performed:` sub-fields so audit-trail requirements are mechanically checkable rather than embedded in free text. DG-1 cards set `status: unflagged` with empty conditional sub-fields.
5. **Two-phase card lifecycle.** The schema documents an explicit lifecycle in §Card lifecycle: Phase B commit (`status: frozen-awaiting-run`, empty `result`) → verdict commit (status and `result` populated, `commit_hash` left `""`) → self-referential follow-up commit (`commit_hash` filled) → optional successor-marker commit (`superseded_by` appended, `status: superseded`). Reframing immutability around the verdict commit (rather than the Phase B commit) resolves the apparent contradiction with the populated `result` block.
6. **`result.commit_hash` self-referential fill via follow-up commit, not amend.** The schema's §Card lifecycle and §Result block prescribe a separate follow-up commit whose message format is `cards: fill self-referential commit_hash placeholder for <card_id>`. This mirrors [`logbook/README.md`](README.md) §Immutability's self-referential placeholder rule. The plan v0.1.2 §4 Phase D's `git commit --amend` prescription is buggy on this point — amending changes the tree and therefore the hash, so the placeholder cannot resolve to its own commit's hash. The schema corrects to follow-up commit; a future plan supersedure (`v0.1.3`) will align the plan text.
7. **Filename includes version.** The pattern is `<card_id>_<short-tag>_v<version>.yaml` (e.g. `A3_pure-dephasing_v0.1.0.yaml`). The version is in the filename so that a superseding card (same `card_id`, same `<short-tag>`, higher `version`) coexists with its predecessor in the directory rather than colliding.
8. **Supersedure identity: same `card_id` + higher `version`.** A new `card_id` is reserved for a *new benchmark* (different DG target, model, or observable). Re-issuing the same benchmark with corrected parameters keeps `card_id` and bumps `version`. This resolves an earlier ambiguity in the v0.1.0 schema draft.
9. **Schema is itself versioned (`v0.1.0`), and the version is machine-recorded in cards.** Each card carries a `schema_version:` field declaring which dialect of `SCHEMA.md` it claims to satisfy. The runner's validation rule 12 rejects cards under unknown dialects. A schema bump never invalidates already-committed cards: cards retain the schema they were authored against; conflicts are resolved by full supersedure under §Supersedure with a `failure_mode_log` entry citing the schema bump.
10. **Template is parse-valid but not validation-valid.** [`_template.yaml`](../benchmarks/benchmark_cards/_template.yaml) intentionally fails validation rules 3, 8, 9, 10 via zero-valued thresholds and `TBD-*` placeholders, so a steward who attempts to commit the template unchanged hits a runner error. SCHEMA.md §Validation rules documents this exemption.
11. **Schema bumped v0.1.0 → v0.1.1 within Phase A.** A Phase B preview drafting of Card A1 surfaced two structural misfits in the v0.1.0 draft. (i) `frozen_parameters.model` presumed a single dynamical model with required `system_hamiltonian`, `coupling_operator`, `bath_type`; but Entry 1's claim is an *algebraic-map* check on multiple L specifications (canonical Lindblad with traceless jump operators; Markovian weak coupling; pseudo-Kraus form) — there is no single `system_hamiltonian`. (ii) `numerical.time_grid` was structurally required but Entry 1 is time-independent, so a degenerate single-point grid would have been a permanent rough edge. The bump adds a `model_kind:` discriminator (`dynamical` vs `algebraic_map`); under `algebraic_map`, `system_hamiltonian`/`coupling_operator`/`bath_type` and `numerical.time_grid` become optional, and a `test_cases:` list is recognized with at-minimum `name`/`description`/`expected_outcome`/`reference` per entry (validation rules 13–16). MINOR bump (not PATCH) because new fields and validation rules are added; non-breaking because `model_kind: dynamical` matches the v0.1.0 shape exactly. Bundled into Phase A so the schema arrives in one piece rather than requiring an in-progress revision during Phase B; the in-Phase-A iteration is itself a deliberate audit-trail entry under SCHEMA.md §Schema versioning §Revision history. This is the cards-first ordering working as designed: the schema gets exercised by a card preview before the schema is committed and before code is written.

### What was *not* done at Phase A

No scientific-implementation module body has exited `NotImplementedError`. No card files have been added to `benchmarks/benchmark_cards/` (Phase B). No code in `reporting/benchmark_card.py` has been written (Phase C). The cards-first ordering remains intact: a future steward can audit, from `git log --diff-filter=A -- cbg/` against `git log --diff-filter=A -- benchmarks/benchmark_cards/A1_*.yaml benchmarks/benchmark_cards/A3_*.yaml benchmarks/benchmark_cards/A4_*.yaml`, that no CBG-construction function existed at HEAD before the cards' frozen-parameter blocks did.

### Naming reconciliation with [`logbook/2026-04-29_repo-init.md`](2026-04-29_repo-init.md)

The repo-init logbook anticipated this entry under the working name `benchmark-protocol-schema-drafted`. The [`logbook/2026-04-29_sail-v0.5-bump.md`](2026-04-29_sail-v0.5-bump.md) Routing notes corrected the form to `benchmark-card-schema-drafted` per [DG-1 work plan v0.1.2](../plans/dg-1-work-plan_v0.1.2.md) §4 Phase A. This entry adopts the corrected form. The repo-init logbook is immutable and is not amended; the plan-side and successor-logbook-side names govern.

### Stewardship-conflict flag carried forward

No change. The triple-flagging discipline operationalised in [`docs/stewardship_conflict.md`](../docs/stewardship_conflict.md) is not invoked by Phase A: schema authoring is structural-scaffolding work, not Tier 4 trapped-ion benchmarking. The schema *encodes* the flag-propagation discipline by making `stewardship_flag` a required block on every card.

## Routing notes

This entry does not bear on the Ledger or the Sail. No Council deliberation is required. The next anticipated logbook entries:

1. `dg-1-cards-frozen` (optional but recommended per [DG-1 work plan v0.1.2](../plans/dg-1-work-plan_v0.1.2.md) §4 Phase B) — when the three DG-1 benchmark cards (`A1`, `A3`, `A4`) are committed in `benchmarks/benchmark_cards/`. This is the moment Risk #8 mitigation becomes auditable.
2. `dg-1-pass` or `dg-1-fail-with-cause` — when DG-1 reaches a verdict (Phase D).

The `Triggering commit:` field above is the documented self-referential placeholder per [`logbook/README.md`](README.md) §Immutability. It will be filled with this commit's SHA-1 in a follow-up commit whose message reads `logbook: fill self-referential triggering-commit placeholder for benchmark-card-schema-drafted`.

---

*Logbook entry. Immutable once committed.*

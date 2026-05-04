# `logbook/` — Immutable repository event log

The logbook is the append-only record of repository events: initialisation, version bumps, Decision Gate passes (and downgrades), Sail revisions, Ledger imports, structural changes, and significant discussion outcomes.

## Conventions

### File naming

```
logbook/YYYY-MM-DD_<short-tag>.md
```

- `YYYY-MM-DD` is the ISO date of the event in the steward's local timezone (Europe/Berlin).
- `<short-tag>` is a kebab-case tag describing the event. Examples: `repo-init`, `dg-1-pass`, `sail-v0.5-bump`, `ledger-v0.5-imported`, `dg-3-readiness-pass`.
- One file per event. Do not bundle multiple events into a single file even if they share a date.

### Content structure

Each entry contains, at minimum:

```markdown
# <Title>

**Date:** YYYY-MM-DD
**Type:** <one of: initialisation, dg-pass, dg-downgrade, sail-bump, ledger-import,
              structural, discussion-outcome, conflict-flag, other>
**Triggering commit:** <hash, populated after commit>
**Triggering evidence:** <files, cards, tests, or external references>

## Summary

(One paragraph stating what happened.)

## Detail

(Any further detail. Specifically: which DG was affected, what the validity-envelope
change is, any cause labels assigned, any stewardship flags applied or propagated.)

## Routing notes

(If the event has implications for the Ledger or Sail, state the routing here.
Do NOT modify the Ledger or Sail from logbook entries; document the route only.)
```

### Immutability

Once committed, a logbook entry is immutable. Corrections take the form of a *new* entry that supersedes the old one, with an explicit `supersedes: YYYY-MM-DD_old-tag.md` field in its header. The old entry remains in the repository, with a `superseded by:` annotation appended.

Two narrow categories of post-commit edit are permitted:

1. **`superseded by:` annotation** — appended when a successor entry is added (per the supersedure rule above).
2. **Self-referential placeholder fills** — where an entry's `Triggering commit:` field carries the explicit placeholder `(to be populated on commit)` *and* the entry's introducing commit is itself the trigger (typical of sail-bumps, plan-revision logs, and other entries whose subject is the commit they live in). The placeholder may be replaced with the introducing commit's hash in a follow-up commit. The follow-up commit message must state `logbook: fill self-referential triggering-commit placeholder for <entry-tag>` and touch only that field. Any other text edit to a committed entry continues to require supersedure.

Both exceptions are bookkeeping completions of explicit gaps, not substantive revisions. They mirror the Ledger's discipline at the repository layer (the Ledger permits typo-level corrections under Council mandate; the logbook permits these two structural completions under steward discipline).

### What does *not* go in the logbook

- Routine commits (those go in commit messages and PR descriptions).
- Discussion that has not produced an outcome (that goes in issues).
- Minor documentation typo fixes (commit message suffices).
- Anything that belongs in the Ledger or Sail (those have their own change procedures; the logbook may *reference* such changes but does not *enact* them).

## Index

| Date | Tag | Type | Summary |
|---|---|---|---|
| 2026-04-29 | `repo-init` | initialisation | Repository scaffold v0.1.0; Sail v0.4 active; CL-2026-005 v0.4 vendored |
| 2026-04-29 | `public-site-added` | structural | Root `index.html` added as a static public landing page |
| 2026-04-29 | `sail-v0.5-bump` | sail-bump | Cardinality-fix supersedure: Sail v0.5 names all five `docs/` files non-optional, aligning Sail wording with already-enforced behaviour; no Ledger impact |
| 2026-04-30 | `benchmark-card-schema-drafted` | structural | Phase A of DG-1 work plan v0.1.2: `benchmarks/benchmark_cards/SCHEMA.md` (schema v0.1.1) + `_template.yaml` drafted; v0.1.1 bump within Phase A added `model_kind` discriminator after Card A1 preview surfaced misfits; cards-first ordering remains intact |
| 2026-04-30 | `dg-1-cards-frozen` | structural | Phase B of DG-1 work plan v0.1.2: Cards A1, A3, A4 committed with `status: frozen-awaiting-run`; cards-first / Risk #6/#8 mitigation now mechanically auditable via `git log --diff-filter=A`; schema bumped to v0.1.2 mid-Phase-B after A3 preview surfaced bath_state-sweep gap |
| 2026-04-30 | `dg-1-pass` | dg-pass | DG-1 PASSED — Cards A1 v0.1.1, A3 v0.1.1, A4 v0.1.1 reproduce CL-2026-005 v0.4 Entries 1, 3, 4 (unambiguous sub-cases) at machine precision; Entries 1.B.3, 3.B.3, 4.B.2 deferred to DG-2 per plan v0.1.4 §1.1; validity envelope NOT YET ATTEMPTED → PASS; tag `v0.2.0` pending |
| 2026-05-01 | `hayden-sorce-transcription-initiated` | structural | Source-transcription surface added; Hayden-Sorce 2022 pseudo-Kraus formula transcribed for the Entry 1.B.3 DG-2 unblocking path; no code/card/DG status change |
| 2026-05-01 | `dg-2-b1-card-frozen` | structural | DG-2 Card B1 v0.1.0 frozen against the (pre-commit hardened) Hayden-Sorce transcription; three HPTA pseudo-Kraus fixtures freeze the diagonal half of Entry 1.B.3; no runner handlers yet (cards-first), no DG status change |
| 2026-05-01 | `dg-2-b1-pass` | structural | DG-2 Card B1 v0.1.0 PASS — diagonal pseudo-Kraus runner confirms Entry 1.B.3 at machine precision; three test_cases all error=0.0, HPTA residuals below 1e-14; does not constitute full DG-2 PASS |
| 2026-05-01 | `hayden-sorce-transcription-v0.1.1-bumped` | structural | Transcription v0.1.0 → v0.1.1: §4b adds off-diagonal pseudo-Kraus generalization (Letter-derived consequence, source-content unchanged); §7a adds off-diagonal candidate fixture; opens admissible path for off-diagonal Entry 1.B.3 / Entry 1.D card; no code change, no card freeze, no DG status change |
| 2026-05-01 | `dg-2-b2-card-frozen` | structural | DG-2 Card B2 v0.1.0 frozen against transcription v0.1.1; three off-diagonal HPTA + Hermitian-omega fixtures freeze the off-diagonal half of Entry 1.B.3 + Entry 1.D; new card surface (pseudo_kraus_offdiag_operators / pseudo_kraus_offdiag_omega); no runner handlers yet (cards-first), no DG status change |
| 2026-05-01 | `dg-2-b3-card-frozen` | structural | DG-2 Card B3 v0.1.0 frozen — cross-basis structural-identity check (Entry 1.A basis-independence; Sail v0.5 §9 DG-2 universal default); three test_cases reuse A1 / B1 frozen fixtures and assert K agreement under matrix_unit vs su_d_generator (d=2 normalized Pauli) bases; no runner handlers, no su_d_generator builder yet (cards-first), no DG status change |
| 2026-05-04 | `dg-2-b3-pass` | structural | DG-2 Card B3 v0.1.0 PASS — cross-basis structural-identity runner confirms Entry 1.A basis-independence at machine precision; three test_cases all error <= 1.57e-16 under matrix_unit vs su_d_generator (d=2); su_d_generator_basis stub filled, basis-independence handler factory added; does not constitute full DG-2 PASS |
| 2026-05-04 | `dg-2-b2-pass` | structural | DG-2 Card B2 v0.1.0 PASS — off-diagonal pseudo-Kraus runner confirms Entry 1.B.3 off-diagonal half + Entry 1.D at error = 0.0 across all three β=0.5 fixtures; Hermiticity-of-omega + HPTA gates enforced; 3 of 4 DG-2 sub-claims now PASS, only Council-gated coherent-displacement track remains |
| 2026-05-04 | `dg-2-partial-envelope` | dg-pass | Validity envelope updated to DG-2 PARTIAL (3 of 4 sub-claims PASS) — Entry 1.A basis-independence + Entry 1.B.3 diagonal + Entry 1.B.3 off-diagonal/Entry 1.D verified via Cards B1+B2+B3; Entries 3.B.3, 4.B.2 remain Council-gated; DG-1 row's stale Entry 1.B.3 deferral removed; citation of Entries 1.A, 1.B.3, 1.D now supported at v0.2.0+ with attribution to Hayden-Sorce gauge and d=2 basis-independence scope |
| 2026-05-04 | `cbg-appendix-d-transcription-populated` | structural | Colla-Breuer-Gasbarri Appendix-D-routed transcription populated and classified underdetermined: source material contains spin-system parity algebra but no displacement-profile convention; Act 2 remains required over §3.1-§3.4 |
| 2026-05-04 | `dg-2-b4-conv-registry-card-frozen` | structural | DG-2 Card B4-conv-registry v0.1.0 frozen — first card under Council Act 2 (c)-discipline; four test_cases tag the four cleared displacement profiles (delta-omega_c, delta-omega_S, sqrt-J, gaussian) for Entry 3.B.3 (pure-dephasing); cbg/displacement_profiles.py module added with REGISTERED_PROFILES; reporting/benchmark_card.py _DISPLACEMENT_PROFILES wired; runner extension for coherent-displaced bath_state.family deferred to verdict commit (cards-first); 21 new tests; no DG status change |
| 2026-05-04 | `dg-2-b5-conv-registry-card-frozen` | structural | DG-2 Card B5-conv-registry v0.1.0 frozen — σ_x sibling of B4 under the same Council-cleared profile registry; four test_cases tag the same four cleared displacement profiles for Entry 4.B.2 (eigenbasis rotation under σ_x coupling); verdict criterion is absolute Euclidean error on (σ_x, σ_y) transverse vector of K(t), distinguishing from A4 v0.1.1's thermal "zero rotation" check; runner handlers shared with B4 verdict commit (cards-first); 3 new tests; no DG status change |
| 2026-05-04 | `dg-2-b4-conv-registry-pass` | structural | DG-2 Card B4-conv-registry v0.1.0 PASS — first card under post-Act-2 (c)-discipline reaches verdict; cbg.cumulants.D_bar_1 dispatches on the cleared profile registry; cbg.tcl_recursion.K_total_displaced_on_grid added; _run_dynamical carve-out lifted; four (pure_dephasing, displaced_bath_*) handlers registered; all four profiles PASS at machine precision (≤ 8.9e-16) by the parity-class theorem of Eq. (A.39); B5 still pending v0.2.0 supersedure (prediction-text correction) before its verdict; envelope unchanged at DG-2 PARTIAL 3/4 |
| 2026-05-04 | `dg-2-b5-conv-registry-v020-superseded-frozen` | structural | DG-2 Card B5-conv-registry v0.1.0 superseded by v0.2.0 same-day (Schrödinger-picture prediction correction); the v0.1.0 acceptance criterion mistakenly used the interaction-picture rotating-vector form D̄_1(t)·(cos(ωt), -sin(ωt)) for the predicted transverse channel, but Companion Eq. (28) at n=1 has no A_I(τ) integral — Schrödinger-picture K_1 = D̄_1(t)·σ_x is constant-direction with zero σ_y component; v0.2.0 prediction is (b_pred, c_pred) = (D̄_1(t), 0); steward-side correction (no Council deliberation, registry unchanged); v0.1.0 retained at HEAD with status: superseded |
| 2026-05-04 | `dg-2-b5-conv-registry-pass` | structural | DG-2 Card B5-conv-registry v0.2.0 PASS — joint B4/B5 closure achieved; new _dyn_handler_sigma_x_displaced registered under (spin_boson_sigma_x, displaced_bath_*); all four cleared profiles return error = 0.0 EXACTLY (single-source-of-truth pattern: same D̄_1 array drives both K_1 computation and predicted σ_x channel; σ_y zero by Eq. (A.43)-(A.45) parity); all four DG-2 sub-claim families now PASS; envelope update follows atomically per §Update protocol |
| 2026-05-04 | `dg-2-pass-envelope` | dg-pass | Validity envelope updated to DG-2 PASS — 4 of 4 sub-claims PASS under Council Act 2 cleared registry; B1 + B2 + B3 + B4-conv-registry + B5-conv-registry v0.2.0 collectively verify Entries 1.A, 1.B.3 (both halves) + 1.D, 3.B.3 (under registry), 4.B.2 (under registry); citation of Entries 3.B.3 / 4.B.2 supported with explicit profile naming requirement; K_2-K_4 numerical recursion at order ≥ 4 remains the only unattempted DG-2-internal milestone |

(This index is updated atomically when new entries are added.)

---

*Last updated: 2026-05-04 (DG-2 PASS — validity envelope updated). CC-BY-4.0 (see ../LICENSE-docs).*

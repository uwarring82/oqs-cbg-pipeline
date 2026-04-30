# DG-1 cards frozen (Phase B of DG-1 work plan)

**Date:** 2026-04-30
**Type:** structural
**Triggering commit:** (to be populated on commit)
**Triggering evidence:**
- [`benchmarks/benchmark_cards/A1_closed-form-K_v0.1.0.yaml`](../benchmarks/benchmark_cards/A1_closed-form-K_v0.1.0.yaml) (committed 2026-04-30 at 252e2f1; CL-2026-005 v0.4 Entry 1)
- [`benchmarks/benchmark_cards/A3_pure-dephasing_v0.1.0.yaml`](../benchmarks/benchmark_cards/A3_pure-dephasing_v0.1.0.yaml) (committed 2026-04-30 at dbef635; CL-2026-005 v0.4 Entry 3)
- [`benchmarks/benchmark_cards/A4_sigma-x-thermal_v0.1.0.yaml`](../benchmarks/benchmark_cards/A4_sigma-x-thermal_v0.1.0.yaml) (this commit; CL-2026-005 v0.4 Entry 4)
- Anchor: [`plans/dg-1-work-plan_v0.1.2.md`](../plans/dg-1-work-plan_v0.1.2.md) §4 Phase B; [`benchmarks/benchmark_cards/SCHEMA.md`](../benchmarks/benchmark_cards/SCHEMA.md) v0.1.2

## Summary

Phase B of [DG-1 work plan v0.1.2](../plans/dg-1-work-plan_v0.1.2.md) is complete. Three benchmark cards — one per Ledger Entry — are committed at HEAD with `status: frozen-awaiting-run`. Each card has its `frozen_parameters` and `acceptance_criterion` blocks fully populated; each card's `result` block is empty per Phase B convention. No scientific-implementation function body has exited `NotImplementedError`; the cards-first ordering (Sail v0.5 §10 Risk #6, #8 mitigation) remains intact and is now mechanically auditable.

## Detail

### Validity envelope

No Decision Gate status changed. All five DGs remain `NOT YET ATTEMPTED`. Phase B produces frozen test specifications only; the PASS/FAIL verdict for DG-1 is decided in Phase D after the runner ([`reporting/benchmark_card.py`](../reporting/), Phase C) is implemented and the cards are executed.

### Cards committed

| Card ID | Ledger Entry | Model | model_kind | N_card | Test cases |
|---|---|---|---|---|---|
| A1 | CL-2026-005 v0.4 Entry 1 (operational K(t) form) | `closed_form_algebraic` | `algebraic_map` | 0 | canonical Lindblad with traceless jumps; Markovian weak coupling with Lamb shift; diagonal pseudo-Kraus |
| A3 | CL-2026-005 v0.4 Entry 3 (pure-dephasing structural result) | `pure_dephasing` | `dynamical` | 2 | thermal bath; coherently-displaced bath |
| A4 | CL-2026-005 v0.4 Entry 4 (orthogonal-coupling thermal-bath result) | `spin_boson_sigma_x` | `dynamical` | 2 | thermal bath; coherently-displaced bath |

Cards A3 and A4 share the same physical setup (H_S = (ω/2)σ_z, ohmic bosonic linear coupling at α = 0.05, ω_c = 10 ω-units; same bath_state cases at T = 0.5 thermal and α_disp = 1.0 displaced; same time grid t ∈ [0, 20/ω], 200 uniform points; same N_card = 2) and differ only in `coupling_operator` (σ_z vs. σ_x). The matched-pair design lets a future audit isolate the effect of coupling-orientation geometry without confounding from bath-physics differences.

### Files in this commit

- [`benchmarks/benchmark_cards/A4_sigma-x-thermal_v0.1.0.yaml`](../benchmarks/benchmark_cards/A4_sigma-x-thermal_v0.1.0.yaml) (new)
- [`benchmarks/benchmark_cards/README.md`](../benchmarks/benchmark_cards/README.md) (revised: A4 row added; Phase B closure note)
- [`logbook/README.md`](README.md) (revised: index row for this entry)
- [`plans/README.md`](../plans/README.md) (revised: DG-1 plan operational status `Phase B (card-drafting)` → `Phase C (module implementation)`)
- This logbook entry.

### Files NOT in this commit (referenced but committed earlier)

- A1 and A3 (committed earlier at 252e2f1 and dbef635 respectively).
- [`benchmarks/benchmark_cards/SCHEMA.md`](../benchmarks/benchmark_cards/SCHEMA.md) at v0.1.2 (current HEAD). Phase A drafted v0.1.0 → v0.1.1; Phase B drafting of A3 surfaced the v0.1.1 → v0.1.2 generalization. The full revision history lives under SCHEMA.md §Schema versioning §Revision history; the Phase A logbook entry [2026-04-30_benchmark-card-schema-drafted](2026-04-30_benchmark-card-schema-drafted.md) records the v0.1.0 → v0.1.1 iteration; the [v0.1.2 commit](dbef635) records the v0.1.1 → v0.1.2 iteration in its commit message.

### Risk #6 / Risk #8 mitigation now auditable

The cards-first ordering is now mechanically verifiable from `git log` alone, without recourse to side-channel notes. A future steward (including a non-conflicted future steward) can run

```
git log --diff-filter=A -- cbg/
git log --diff-filter=A -- benchmarks/benchmark_cards/A1_*.yaml \
                            benchmarks/benchmark_cards/A3_*.yaml \
                            benchmarks/benchmark_cards/A4_*.yaml
```

and confirm that no CBG-construction function existed at HEAD before the three cards' frozen-parameter blocks did. The first command lists CBG module additions ([cbg/__init__.py](../cbg/__init__.py), [cbg/diagnostics.py](../cbg/diagnostics.py), [cbg/basis.py](../cbg/basis.py), [cbg/effective_hamiltonian.py](../cbg/effective_hamiltonian.py), [cbg/cumulants.py](../cbg/cumulants.py), [cbg/bath_correlations.py](../cbg/bath_correlations.py), [cbg/tcl_recursion.py](../cbg/tcl_recursion.py)); the latter additions are scaffolding (import-time protective-doc checks, failure-mode constants, structural_constraints tuples) not scientific implementation, per plan §1's "scientific-implementation module body" qualifier. The second command lists the three card additions, all of which are at or before this commit. From this commit forward, any new commit to a function body inside `cbg/` that exits `NotImplementedError` and executes the CBG construction is provenance-traceable to the cards that motivated it.

### Schema iteration during Phase A/B (audit trail)

Schema versions touched cards over the combined Phase A/B span:

- **v0.1.0** — drafted in working tree during Phase A; superseded within Phase A before reaching HEAD; never authored cards.
- **v0.1.1** — reached HEAD at [0b9590a](0b9590a) (Phase A commit). Card A1 authored under it.
- **v0.1.2** — reached HEAD at [dbef635](dbef635) (bundled with Card A3 commit). Cards A3 and A4 authored under it; Card A1 continues to validate unchanged under v0.1.2 (the test_cases generalization is additive).

Both in-Phase iterations (v0.1.0 → v0.1.1 surfaced by Card A1 preview; v0.1.1 → v0.1.2 surfaced by Card A3 preview) are cards-first ordering working as designed: the schema gets exercised by a card before the schema is committed and before scientific-implementation code is written. Each iteration is recorded under SCHEMA.md §Schema versioning §Revision history with the surfacing card and the bump rationale.

### Stewardship-conflict flag carried forward

No change. All three DG-1 cards carry `stewardship_flag.status: unflagged` per [`docs/stewardship_conflict.md`](../docs/stewardship_conflict.md): DG-1 verifies Tier 1 theory-internal predictions, not Tier 4 trapped-ion benchmarks; the steward conflict on Entry 6 does not propagate.

## Routing notes

This entry does not bear on the Ledger or the Sail. No Council deliberation is required. The next anticipated logbook entries:

1. **`dg-1-pass`** or **`dg-1-fail-with-cause`** — when DG-1 reaches a verdict in Phase D. The Phase D logbook entry will quote the three cards' commit hashes via `git log --diff-filter=A -- benchmarks/benchmark_cards/A1_*.yaml ...` (per plan §4 Phase B "Phase-B commit hash recording") and update [`docs/validity_envelope.md`](../docs/validity_envelope.md) atomically with the verdict commit.

The `Triggering commit:` field above is the documented self-referential placeholder per [`logbook/README.md`](README.md) §Immutability. It will be filled with this commit's SHA-1 in a follow-up commit whose message reads `logbook: fill self-referential triggering-commit placeholder for dg-1-cards-frozen`.

---

*Logbook entry. Immutable once committed.*

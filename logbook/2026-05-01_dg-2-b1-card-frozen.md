# DG-2 Benchmark Card B1 frozen — pseudo-Kraus reduction to Hayden-Sorce 2022

**Date:** 2026-05-01
**Type:** structural
**Triggering commit:** (to be populated on commit)
**Triggering evidence:** `benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml`; `transcriptions/hayden-sorce-2022_pseudokraus_v0.1.0.md` (hardened pre-commit; §4a structural cross-check and §7 algebraic-HPTA notes added in the same drafting episode); `benchmarks/benchmark_cards/README.md` index update

## Summary

Card B1 v0.1.0 is committed at `status: frozen-awaiting-run` against the Hayden-Sorce 2022 pseudo-Kraus transcription. It is the first DG-2 benchmark card. It freezes three HPTA pseudo-Kraus fixtures (σ_z, σ_x, all-traceless) with closed-form expected `K` derived from the transcribed Hayden-Sorce formula, plus a per-fixture HPTA precondition that the runner must validate before evaluating the K comparison. SCHEMA.md v0.1.2 validation passes (all 16 rules); gauge-annotation block is canonical.

## Detail

**Scope and Ledger anchor.** B1 verifies the diagonal-pseudo-Kraus half of CL-2026-005 v0.4 Entry 1.B.3 — the half that was deferred from DG-1 (Card A1 v0.1.1 `failure_mode_log[0]`) for absence of a transcribed Hayden-Sorce 2022 closed form. The off-diagonal half of Entry 1.B.3 (the "generalises to off-diagonal" claim, also touching Entry 1.D) is *not* in B1's scope: transcription v0.1.0 covers only the diagonal expression. Coherent-displacement gaps for Entries 3.B.3 and 4.B.2 are unrelated to Entry 1.B.3 and remain gated on the second DG-2 unblocker (Council-cleared displacement convention).

**Three test cases freeze the fixtures, no runner support yet.** Per cards-first discipline, B1 lands as `frozen-awaiting-run`: the runner's `_TEST_CASE_HANDLERS` registry has no handler for the three new test_case names, so an attempted run currently raises `TestCaseHandlerNotFoundError`. That is the intended pre-implementation state. Implementing the handlers (and any pseudo-Kraus parser for the symbolic `pseudo_kraus_operators` / `pseudo_kraus_coefficients` fields) is a separate work step strictly after this commit; the freeze prevents retroactive fixture edits during that implementation.

**Pre-implementation numerical sanity checks** (steward-side, prior to the freeze) confirm the math is sound: HPTA residual at machine precision (~3·10⁻¹⁶) for both nonzero fixtures, K from `cbg.effective_hamiltonian.K_from_generator` exactly matches the transcribed `H_HS` formula (||·||_F = 0.0) for all three cases, HPTA-violating fixtures are clearly distinguishable (residual ~0.35), and the a=0 / b=0 boundary correctly degenerates to L ≡ 0. These checks are pre-freeze evidence that the fixtures are well-posed; they are not the card's verdict (which awaits the implemented runner handlers).

**Transcription hardening (pre-commit).** In the same drafting episode that produced B1, the Hayden-Sorce 2022 pseudo-Kraus transcription v0.1.0 received two pre-commit hardening edits, made before its first commit (the file was untracked at the time of the edits, so the in-place revision is not a supersedure — both `transcriptions/README.md` and the file's frontmatter retain `version: v0.1.0`):

1. **New §4a "Structural cross-check against Letter Eq. (6)"** with an explicit derivation showing that the transcribed `H_HS` formula and the basis-independent Letter Eq. (6) form are algebraically identical on pseudo-Kraus inputs in the matrix-unit basis. This makes the load-bearing point for any future card explicit: a comparison of `K_from_generator` against `H_HS` verifies *implementation correctness* (basis-summation pipeline numerically matches the trace-based formula), not the source claim itself.
2. **§7 expansion** noting that the candidate fixture's HPTA precondition holds as an *algebraic* identity (`(I - iaσ_z)(I + iaσ_z) = (1+a²)I`), not merely numerically; adding the σ_x analog as a Pauli-orientation cross-check; and flagging the `a = 0` boundary as degenerate.

These additions strengthen the audit trail for B1 without changing the source-derived formula in §4 or §5. They are operational scaffolding under the transcription-layer authority limit (`transcriptions/README.md` §Authority), not new scientific claims.

## Routing notes

This event freezes a DG-2 benchmark card; it does not pass DG-2, does not modify the validity envelope, and does not alter CL-2026-005, the Sail, or any DG status. DG-2 advances to PASS only when the implemented runner produces a verdict commit on this card (and the analogous cards covering the remaining DG-2 deferrals: off-diagonal pseudo-Kraus, plus Entries 3.B.3 / 4.B.2 once the displacement-convention gap clears).

The next admissible work step is implementation of the runner handlers for B1's three test_case names in `reporting.benchmark_card._TEST_CASE_HANDLERS`, plus whatever symbolic-operator parsing infrastructure the new `pseudo_kraus_operators` / `pseudo_kraus_coefficients` card fields require. That step is bounded by B1's frozen acceptance criterion: handlers must implement the comparison defined by `acceptance_criterion.rationale`, not extend it.

No Council deliberation is required. No stewardship flag attaches.

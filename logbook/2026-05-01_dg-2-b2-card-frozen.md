# DG-2 Benchmark Card B2 frozen — off-diagonal pseudo-Kraus reduction

**Date:** 2026-05-01
**Type:** structural
**Triggering commit:** (to be populated on commit)
**Triggering evidence:** `benchmarks/benchmark_cards/B2_pseudo-kraus-offdiagonal_v0.1.0.yaml`; `transcriptions/hayden-sorce-2022_pseudokraus_v0.1.1.md` §4b (off-diagonal direct formula) and §7a (worked off-diagonal fixture); `benchmarks/benchmark_cards/README.md` index update

## Summary

Card B2 v0.1.0 is committed at `status: frozen-awaiting-run` against transcription v0.1.1. It is the second DG-2 benchmark card and the first to exercise off-diagonal pseudo-Kraus structure (Hermitian coefficient matrix `omega` with non-zero off-diagonal entries). Three test cases freeze HPTA + Hermitian-`omega` fixtures with closed-form expected `K`: a canonical off-diagonal `sigma_z` fixture (`K = beta sigma_z`), a `sigma_x` Pauli-orientation analog (`K = -beta sigma_x`), and a degenerate diagonal-only `omega` sub-case (`K = 0`). SCHEMA.md v0.1.2 validation passes (all 16 rules); gauge-annotation block is canonical.

## Detail

**Scope and Ledger anchor.** B2 verifies the off-diagonal half of CL-2026-005 v0.4 Entry 1.B.3 ("the new formula generalises the prior result to the off-diagonal `omega_{ij}` case") and the corresponding generalization claim in Entry 1.D. Hayden-Sorce 2022's source content gives the canonical-Hamiltonian closed form in single-index / diagonal pseudo-Kraus form (transcription §4 / §5); the Letter's contribution is that the basis-independent recipe Letter Eq. (6) absorbs off-diagonal pseudo-Kraus inputs without requiring a prior eigendecomposition of `omega`. Transcription §4b records the Letter-derived direct off-diagonal expression; B2's three test cases verify that `K_from_generator` (matrix-unit basis sum) reproduces this expression on representative fixtures.

The diagonal half of Entry 1.B.3 is *not* re-tested here — that is Card B1 v0.1.0's territory (PASS, 2026-05-01) and stays anchored to transcription v0.1.0 per SCHEMA.md §Card lifecycle.

**Three test cases freeze the off-diagonal fixtures.** The pattern mirrors B1's three-case structure:

  1. `offdiag_omega_imaginary_sigma_z` — V_1 = I, V_2 = sigma_z, omega = [[1, i*beta], [-i*beta, -1]], beta = 0.5; expected K = 0.5 sigma_z. The canonical fixture from transcription §7a, with the per-term derivation table cited inline.
  2. `offdiag_omega_imaginary_sigma_x` — V_1 = sigma_x, V_2 = I, same omega structure, beta = 0.5; expected K = -0.5 sigma_x. Pauli-orientation cross-check — confirms the off-diagonal handler does not silently prefer the sigma_z axis. The minus sign relative to the first case is structural (Tr(V_1) = 0, Tr(V_2) = 2 swap relative to fixture 1).
  3. `offdiag_omega_diagonal_only` — V_1 = I, V_2 = sigma_z, omega = diag(1, -1) (off-diagonal entries zero); expected K = 0. Degeneracy / consistency check: the off-diagonal handler must collapse correctly when omega's off-diagonal entries vanish. Parallels B1's `pseudo_kraus_traceless_jumps` in spirit (purely-degenerate input ⇒ K = 0, useful for catching structural-contribution bugs in the handler).

**Card surface (additive over B1).** B2 introduces two new card-level fields:

  - `pseudo_kraus_offdiag_operators`: ordered list of V_i symbolic strings, parsed against the d=2 Pauli + I namespace using the same AST-restricted operator parser already implemented for B1.
  - `pseudo_kraus_offdiag_omega`: 2D list (n × n where n = number of V_i), entries are symbolic strings parsed as complex scalars under parameter substitution. Must be Hermitian (`omega[j][i]` equals `conj(omega[i][j])`); diagonal entries are real.

Both fields reuse B1's `parameters` mechanism for named scalars (here, just `beta`).

**Acceptance criterion (per case)** requires *three* gates, in order:

  1. Hermiticity of `omega`: `||omega - omega^dagger||_F <= 1.0e-14`.
  2. HPTA: `||sum_{i,j} omega_{ij} V_j^dagger V_i||_F <= 1.0e-14`.
  3. K comparison: `||K_computed - K_expected||_F / max(||K_expected||_F, 1) <= 1.0e-10`.

All three frozen fixtures satisfy gates (1) and (2) as algebraic identities; gate (3) is the acceptance threshold proper. Structurally identical to B1's two-gate (HPTA + K) acceptance, with Hermiticity-of-omega added as a precondition that does not arise in B1's single-index gamma form (real coefficients are trivially Hermitian as a 1×1 / vector).

**Pre-implementation numerical sanity** (steward-side, prior to the freeze) confirms the math: HPTA residuals at exactly 0.0 for all three fixtures (algebraic identity holds in floating-point because the simple algebra evaluates without round-off); K errors vs §4b expected at exactly 0.0 for fixtures 1 and 2; K = 0.0 exactly for fixture 3. These are pre-freeze evidence that the fixtures are well-posed; they are not the card's verdict (which awaits the implemented runner handlers).

**No runner support yet.** Per cards-first discipline, B2 lands as `frozen-awaiting-run`: the runner's `_TEST_CASE_HANDLERS` registry has no handler for B2's three test_case names, so an attempted run currently raises `TestCaseHandlerNotFoundError` — confirmed at freeze time via `reporting.benchmark_card._TEST_CASE_HANDLERS` membership check. That is the intended pre-implementation state. Implementation of the handlers (and the small omega-string parser extension; the V_i parser is already in place from B1 work) is a separate, bounded work step.

## Routing notes

This event freezes a DG-2 benchmark card; it does not pass DG-2, does not modify the validity envelope, and does not alter CL-2026-005, the Sail, or any DG status. Card B1 v0.1.0's PASS verdict is unaffected — B2 is additive coverage, not a B1 supersedure.

The next admissible work step is the runner-extension equivalent of the B1 wiring commit: add an off-diagonal pseudo-Kraus handler factory to `reporting.benchmark_card`, register handlers for B2's three test_case names, extend the symbolic-operator parser (or add a thin sibling) for complex-scalar omega entries, plus a tests-side update (loading B2, verifying PASS verdict, per-case error checks, Hermiticity-of-omega and HPTA gate behaviour). That step is bounded by B2's frozen acceptance criterion: handlers must implement the three gates described in `acceptance_criterion.rationale`, not extend them.

After runner support lands, the verdict-commit + self-referential commit_hash fill sequence applies (mirrors B1 lifecycle).

DG-2 progress map after this freeze:

1. **Diagonal half of Entry 1.B.3** — closed: Card B1 v0.1.0 PASS (2026-05-01).
2. **Off-diagonal half of Entry 1.B.3 / Entry 1.D** — frozen here: Card B2 v0.1.0 awaiting runner + verdict.
3. **Cross-basis structural-identity check** — orthogonal track; implementable now, no transcription dependency.
4. **Coherent-displacement gap (Entries 3.B.3, 4.B.2)** — orthogonal track; remains gated on Council-cleared displacement convention.

No Council deliberation is required. No stewardship flag attaches.

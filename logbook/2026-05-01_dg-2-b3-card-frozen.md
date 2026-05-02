# DG-2 Benchmark Card B3 frozen — cross-basis structural-identity for K_from_generator

**Date:** 2026-05-01
**Type:** structural
**Triggering commit:** (to be populated on commit)
**Triggering evidence:** `benchmarks/benchmark_cards/B3_cross-basis-structural-identity_v0.1.0.yaml`; `cbg/effective_hamiltonian.py` module docstring (DG-2 universal-default check); `cbg/basis.py` `su_d_generator_basis` stub explicitly tagged DG-2 territory; `benchmarks/benchmark_cards/A1_closed-form-K_v0.1.1.yaml` and `B1_pseudo-kraus-diagonal_v0.1.0.yaml` for the source fixtures B3 reuses; `benchmarks/benchmark_cards/README.md` index update

## Summary

Card B3 v0.1.0 is committed at `status: frozen-awaiting-run`. It is the third DG-2 benchmark card and the first to operationalise the DG-2 universal-default structural-identity check named in Sail v0.5 §9 (basis-independence of `cbg.effective_hamiltonian.K_from_generator` per Entry 1.A). Three test cases reuse known-good frozen fixtures (A1 v0.1.1's two Lindblad fixtures plus B1 v0.1.0's σ_z pseudo-Kraus fixture) and assert that K computed under the matrix-unit basis equals K computed under the su(d)-generator basis (for d = 2: the normalized Pauli basis {I, σ_x, σ_y, σ_z} / √2). SCHEMA.md v0.1.2 validation passes (all 16 rules); gauge-annotation block is canonical.

## Detail

**Scope and Ledger anchor.** B3 verifies CL-2026-005 v0.4 Entry 1.A's central claim — that `K = (1/2id) Σ_α [F_α†, L[F_α]]` yields the same operator K for any complete Hilbert-Schmidt-orthonormal operator basis `{F_α}`. The DG-1 cards (A1, A3, A4) and the diagonal / off-diagonal pseudo-Kraus DG-2 cards (B1 PASS, B2 frozen) all evaluate K under the matrix-unit basis only — they verify K's value, not its basis-independence. Sail v0.5 §9 names cross-basis verification as the DG-2 universal-default structural-identity check; the `cbg.effective_hamiltonian` module docstring and the `cbg.basis.su_d_generator_basis` stub both flag this as DG-2 territory. B3 closes that gap for d = 2.

**Three test cases reuse known-good fixtures.**

  1. `basis_independence_pseudo_kraus_sigma_z` — re-states B1 v0.1.0's `pseudo_kraus_diagonal_sigma_z` fixture (V_1 = I + 1j*a*σ_z, V_2 = √(1+a²)*I, γ = (1, -1), a = 0.5; HPTA holds as algebraic identity; common K = -0.5*σ_z per B1 PASS).
  2. `basis_independence_lindblad_traceless` — re-states A1 v0.1.1's `canonical_lindblad_traceless` fixture (H = (ω/2)σ_z, jumps √γ_∓ σ_∓; common K = (ω/2)σ_z per A1 PASS). Lindblad form with traceless jumps is HPTA by construction.
  3. `basis_independence_lindblad_lamb_shift` — re-states A1 v0.1.1's `markovian_weak_coupling_lamb_shift` fixture (combined Lamb-shifted H, single jump √γ σ_-; common K = ((ω + 2δ_LS)/2)σ_z per A1 PASS). Lindblad form (HPTA automatic).

Re-stating rather than cross-referencing keeps B3 self-contained: A1 and B1 are content-immutable post-verdict per SCHEMA.md §Card lifecycle, but a hypothetical future supersedure of either would not silently propagate into B3's frozen content. Each B3 test case explicitly cites its source-fixture card by filename in `reference`.

**Card surface (additive over A1 / B1).** Each test case adds one new field, `comparison_basis: "su_d_generator"`, naming the alternate basis to compare against the matrix-unit reference under which `K_from_generator` is canonically evaluated. The fixture-defining fields (pseudo_kraus_operators / pseudo_kraus_coefficients for case 1; hamiltonian_term / jump_operators for cases 2 and 3) match A1 / B1's shapes verbatim, so the existing AST-restricted operator parser and Lindblad-generator builder are reused without extension.

**Acceptance criterion (per case)** requires two gates:

  1. HPTA precondition (pseudo-Kraus case only): `||Σ_j γ_j E_j† E_j||_F ≤ 1.0e-14`. Identical to B1's HPTA gate; satisfied as algebraic identity by the inherited fixture.
  2. Cross-basis structural identity: `||K(matrix_unit) − K(comparison_basis)||_F / max(||K(matrix_unit)||_F, 1) ≤ 1.0e-10`. The K comparison is between the two basis evaluations of `K_from_generator`, *not* between K and a reference value. This is deliberate: B3 tests basis-independence in isolation, so a regression in the basis-summation path or in the su(d)-generator basis builder cannot be masked by a coincident regression in fixture evaluation. The K values themselves stay verified by A1 and B1.

**Pre-implementation status.** `cbg.basis.su_d_generator_basis` is currently a NotImplementedError stub explicitly tagged "DG-2 territory; not exercised by DG-1 cards". For d = 2, the implementation is one-shot: return `[I, σ_x, σ_y, σ_z] / √2` as a list of complex ndarrays. The stub's docstring already commits to this shape via "{1/√d, σ_i/√d}". B3's wiring step is bounded: fill the stub for d = 2, add a basis-comparison handler factory in `reporting.benchmark_card`, register handlers for B3's three test_case names. No new operator parsing infrastructure is required — A1 / B1's parsers handle all three fixture surfaces unchanged.

**No runner support yet.** Per cards-first discipline, B3 lands as `frozen-awaiting-run`: the runner's `_TEST_CASE_HANDLERS` registry has no handler for B3's three test_case names (confirmed at freeze time via membership check). An attempted run currently raises `TestCaseHandlerNotFoundError`. The su(d)-generator basis builder is also not yet implemented. Both are deliberate pre-implementation state.

## Routing notes

This event freezes a DG-2 benchmark card; it does not pass DG-2, does not modify the validity envelope, and does not alter CL-2026-005, the Sail, or any DG status. Card A1 v0.1.1, B1 v0.1.0, and B2 v0.1.0 are unaffected — B3 is additive coverage of the universal-default structural-identity check, not a supersedure of any prior card.

DG-2 progress map after this freeze:

1. **Diagonal half of Entry 1.B.3** — closed: Card B1 v0.1.0 PASS (2026-05-01).
2. **Off-diagonal half of Entry 1.B.3 / Entry 1.D** — frozen: Card B2 v0.1.0 awaiting runner + verdict.
3. **Universal-default structural identity (Entry 1.A basis-independence)** — frozen here: Card B3 v0.1.0 awaiting runner + verdict.
4. **Coherent-displacement gap (Entries 3.B.3, 4.B.2)** — orthogonal track; remains gated on Council-cleared displacement convention.

The next admissible work step on the B3 track is bounded: fill `cbg.basis.su_d_generator_basis(2)`, add a basis-comparison handler factory to `reporting.benchmark_card`, register handlers for B3's three test_case names, add tests, then verdict commit + self-referential commit_hash fill (mirroring the B1 lifecycle). The wiring is independent of the B2 wiring track and can run in either order.

After both B2 and B3 verdicts land, three of the four DG-2 sub-claims will be PASS or honestly verified, with only the Council-gated coherent-displacement track remaining. That state would justify a "DG-2 PARTIAL: 3 of 4 sub-claims" envelope update analogous to DG-1's honest-deferral pattern, pending the Council clearance.

No Council deliberation is required for this freeze. No stewardship flag attaches.

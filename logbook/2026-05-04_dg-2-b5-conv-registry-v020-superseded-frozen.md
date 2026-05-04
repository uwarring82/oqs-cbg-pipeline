# DG-2 Card B5-conv-registry v0.2.0 frozen — Schrödinger-picture prediction correction

**Date:** 2026-05-04
**Type:** structural
**Triggering commit:** (to be populated on commit)
**Triggering evidence:**
- [`benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml`](../benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml) (status: `frozen-awaiting-run`; supersedes v0.1.0)
- [`benchmarks/benchmark_cards/B5-conv-registry_v0.1.0.yaml`](../benchmarks/benchmark_cards/B5-conv-registry_v0.1.0.yaml) (status: `superseded`; superseded_by → v0.2.0)
- [`benchmarks/benchmark_cards/README.md`](../benchmarks/benchmark_cards/README.md) index update
- [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py) load tests updated for v0.2.0 + v0.1.0 supersedure
- Anchor: B4-conv-registry verdict commit [`62e44d0`](62e44d0) (2026-05-04) which established the canonical Schrödinger-picture L_1^S construction in `cbg.tcl_recursion.K_total_displaced_on_grid`.

## Summary

Card B5-conv-registry v0.1.0 (frozen 2026-05-04 at commit [`a7eae74`](a7eae74)) is superseded by v0.2.0 same-day on a card-design correction. The v0.1.0 acceptance criterion referenced an interaction-picture predicted transverse vector `(b_pred, c_pred) = D̄_1(t) · (cos(ωt), -sin(ωt))` that does not match what the Schrödinger-picture runner computes. Companion Eq. (28) at n = 1 has no integral over `A_I(τ)`; the displacement enters only through `D̄_1(t)` as a scalar prefactor on the (Schrödinger-picture) commutator `[A, X]`. For traceless `A = σ_x`, this extracts via Letter Eq. (6) to `K_1(t) = D̄_1(t) · σ_x` — a CONSTANT transverse direction along σ_x with zero σ_y component at order ≤ N_card = 2 (parity-class theorem of Letter end-matter Eq. (A.43)–(A.45) sends K_2 to the diagonal subspace). v0.2.0 corrects the prediction to `(b_pred, c_pred) = (D̄_1(t), 0)`, making B5 structurally analogous to B4-conv-registry v0.1.0 (B4: σ_z shift = 2 D̄_1(t); B5: σ_x coefficient = D̄_1(t), σ_y = 0).

## Detail

### What changed at v0.2.0

- **`expected_outcome` per fixture**: rewritten to state `b(t) = D̄_1(t)`, `c(t) = 0` directly (rather than the rotating `(cos(ωt), -sin(ωt))` form).
- **`acceptance_criterion.rationale`**: rewritten to define `b_predicted(t) := D̄_1(t).real`, `c_predicted(t) := 0`, and the verdict gate as `max_t sqrt((b - b_pred)² + c²) ≤ 1.0e-4`. The two channels (σ_x and σ_y) are split as independent checks for clarity.
- **`comparison.target_observable`**: updated to "K_perp(t) = (b(t), c(t)) with predicted (D̄_1(t), 0)".
- **`failure_mode_log[0]`**: added with the full supersedure rationale (the prediction error, the Companion Eq. (28) reference, the cards-first audit note that no v0.1.0 verdict was ever attempted).
- **`stewardship_flag.rationale`**: extended to record the supersedure context; the Council Act 2 (c)-clearance + per-fixture parameter-disclosure context is unchanged.
- **`supersedes`**: added pointing back to v0.1.0.

### What did NOT change

- Per-fixture parameter values: matched verbatim to v0.1.0 (and to B4 v0.1.0). Same four cleared profiles (`delta-omega_c`, `delta-omega_S`, `sqrt-J`, `gaussian`).
- System-side block (model, coupling, spectral density, time grid): verbatim.
- Council-clearance context (subsidiary briefing v0.3.0; Act 2 verdict; (c)-discipline + §6.1 registry-clearance-gate): unchanged. The §6.1 gate is not engaged — no profile additions or removals.
- `coupling_operator: "sigma_x"` and `model: "spin_boson_sigma_x"`: unchanged.
- threshold `1.0e-4`: unchanged.

### Why the v0.1.0 prediction was wrong

In the standard projection-operator TCL derivation:

  L_1^I[X](t) = -i D̄_1(t) [A_I(t), X]    (interaction picture)
  L_1^S[X](t) = -i D̄_1(t) [A,      X]    (Schrödinger picture)

The two are related by `L_1^S[X] = U L_1^I[U† X U] U†` with `U = e^{-iH_S t}`, and the unitary cancels: `U A_I(t) U† = U U† A U U† = A`. So in Schrödinger picture, L_1 carries `A` (not `A_I(t)`). The runner's existing `L_2_thermal_at_time` uses this same convention (outer commutator with `A`, inner with `A_I(τ)`) — i.e. Schrödinger-picture L_t.

When `A = σ_x` (traceless), `K_from_generator` applied to `L_1^S[X] = -i D̄_1(t) [σ_x, X]` returns `K_1(t) = D̄_1(t) · σ_x`. The extraction is via Letter Eq. (6); the result is exact for d = 2 because the generic identity `K(L_H')` returns the traceless part of `H'` for `L_H'[X] = -i [H', X]`.

The v0.1.0 prediction text mistakenly wrote `K_1(t) = D̄_1(t) · A_I(t) = D̄_1(t) · (σ_x cos(ωt) - σ_y sin(ωt))`, conflating `A_I(t)` (which rotates) with `A` (which doesn't). The error was caught at the B4 verdict commit (`62e44d0`) — verifying B4's correct σ_z prediction made it clear B5 v0.1.0 was inconsistent with the same physics.

### Cards-first audit

- B5 v0.1.0 was frozen at commit [`a7eae74`](a7eae74) on 2026-05-04 at `frozen-awaiting-run`. No verdict was attempted between freeze and supersedure (its handlers were never registered; running it hit `TestCaseHandlerNotFoundError`). No verdict-trail invalidation arises.
- v0.2.0 lands also at `frozen-awaiting-run` on 2026-05-04. Per cards-first discipline, this commit lands the corrected card BEFORE the σ_x-specific dynamical handler is wired. The verdict commit (separate, immediately following) registers `_dyn_handler_sigma_x_displaced` and runs B5 v0.2.0 to PASS.
- The supersedure mechanism (v0.1.0 → v0.2.0 with `supersedes` / `superseded_by` cross-references; both files retained at HEAD; failure_mode_log entry on v0.2.0) follows the SCHEMA.md §Card lifecycle precedent established by A1 v0.1.0 → v0.1.1, A3 v0.1.0 → v0.1.1, A4 v0.1.0 → v0.1.1.

### Routing

- This is a **steward-side card-design correction**, NOT a Council-level convention change.
- The §6.1 registry-clearance-gate is not engaged: the four cleared profiles (subsidiary briefing v0.3.0 §3.1–§3.4) are unchanged.
- The Steward-conflict surface (§4.3 handling (c) discipline) is unchanged: the Steward does not select a single convention; the supersedure corrects internal prediction text, not a convention choice.
- No Council deliberation is required.

### Files in this commit

- [`benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml`](../benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml) (new)
- [`benchmarks/benchmark_cards/B5-conv-registry_v0.1.0.yaml`](../benchmarks/benchmark_cards/B5-conv-registry_v0.1.0.yaml): `status: frozen-awaiting-run` → `status: superseded`; `superseded_by` added.
- [`benchmarks/benchmark_cards/README.md`](../benchmarks/benchmark_cards/README.md): card-index points to v0.2.0; superseded-cards table gains a B5 v0.1.0 row.
- [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py): `B5_PATH` now points to v0.2.0; new test for v0.1.0 supersedure metadata; load assertions updated.
- [`logbook/2026-05-04_dg-2-b5-conv-registry-v020-superseded-frozen.md`](2026-05-04_dg-2-b5-conv-registry-v020-superseded-frozen.md): this entry.
- [`logbook/README.md`](README.md): index row added.

### Test envelope

322 pass post-this-commit (the v0.2.0 freeze adds 1 new test — the v0.1.0 supersedure-metadata assertion — and updates the existing `test_load_card_b5_succeeds` to assert v0.2.0; the carve-out test continues to assert `TestCaseHandlerNotFoundError` since v0.2.0's handlers are not yet registered).

## Routing notes

This event freezes a corrected DG-2 benchmark card; it does not pass DG-2, does not modify the validity envelope, and does not alter CL-2026-005, the Sail, or any DG status. The validity envelope holds at DG-2 PARTIAL — 3 of 4 sub-claims PASS (2026-05-04). Movement contingent on B5 v0.2.0's verdict landing.

The next admissible work step is the **B5 verdict commit**: register `_dyn_handler_sigma_x_displaced` under `(spin_boson_sigma_x, displaced_bath_*)` keys; the handler computes `b(t)`, `c(t)`, and the predicted `(D̄_1(t), 0)` vector (reusing `cbg.cumulants.D_bar_1` for the predicted σ_x channel — same single-source-of-truth pattern that made B4's verdict land at machine precision). Run B5 v0.2.0 to verdict; produce per-profile evidence; populate result.

No Council deliberation is required. No stewardship flag attaches beyond the standing co-author flag captured in `stewardship_flag.rationale`.

---

*Logbook entry. Immutable once committed.*

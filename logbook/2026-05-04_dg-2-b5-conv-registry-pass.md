# DG-2 Card B5-conv-registry v0.2.0 PASS — joint B4/B5 closure achieved

**Date:** 2026-05-04
**Type:** structural
**Triggering commit:** 63528910558b2ffcb961fca5e341e17737dcf5b8
**Triggering evidence:**
- [`benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml`](../benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml) (status: `pass`; result block populated)
- [`benchmarks/results/B5-conv-registry_v0.2.0_result.json`](../benchmarks/results/B5-conv-registry_v0.2.0_result.json)
- Anchor: CL-2026-005 v0.4 Entry 4.B.2; subsidiary briefing v0.3.0 §3.1–§3.4 + §6.1; Council-3 ADM-EC Act 2 deliberation 2026-05-04; transcription [`colla-breuer-gasbarri-2025_appendix-d_v0.0.1.md`](../transcriptions/colla-breuer-gasbarri-2025_appendix-d_v0.0.1.md) §2.3 / Eq. (A.43)–(A.45); B4 verdict commit [`62e44d0`](62e44d0) (which established the canonical Schrödinger-picture L_1^S construction in `cbg.tcl_recursion.K_total_displaced_on_grid`).

## Summary

**Card B5-conv-registry v0.2.0 PASSED** under handling (c) (Council-cleared profile registry). Combined with B4-conv-registry's PASS (also 2026-05-04), this completes the joint B4/B5 closure: both displaced-bath sub-claims (Entries 3.B.3 + 4.B.2) are now operationally verified across all four Council-cleared profiles. The verdict commit ([`6352891`](6352891)) registered `_dyn_handler_sigma_x_displaced` under `(spin_boson_sigma_x, displaced_bath_*)` keys; all four B5 test_cases returned `error = 0.0` exactly — structural agreement, because (i) the same `D_bar_1` array drives both the runner's K_1 computation and the predicted σ_x channel (single-source-of-truth pattern; floating-point error cancels), and (ii) the σ_y channel is zero by the parity-class theorem of Letter end-matter Eq. (A.43)–(A.45) at order ≤ N_card = 2.

## Detail

### Card verified

| Card | Test case | Profile | Verdict | Error | Threshold |
|---|---|---|---|---|---|
| B5-conv-registry v0.2.0 | `displaced_bath_delta_omega_c` | `delta-omega_c` (§3.1) | PASS | 0.0 | 1.0e-4 |
| B5-conv-registry v0.2.0 | `displaced_bath_delta_omega_S` | `delta-omega_S` (§3.2) | PASS | 0.0 | 1.0e-4 |
| B5-conv-registry v0.2.0 | `displaced_bath_sqrt_J` | `sqrt-J` (§3.3) | PASS | 0.0 | 1.0e-4 |
| B5-conv-registry v0.2.0 | `displaced_bath_gaussian` | `gaussian` (§3.4) | PASS | 0.0 | 1.0e-4 |

### Why exact-zero verdict

The verdict-comparison structure makes the test exact, not merely machine-precision:

- **σ_x channel** (`b_actual` vs `b_predicted`): the runner's K_1 computation calls `cbg.tcl_recursion.L_1_displaced_at_time` with the `D_bar_1` array as input; the σ_x coefficient `0.5 trace(σ_x · K_1)` evaluates to `D̄_1(t)` exactly (via `K_from_generator` returning the traceless part of `D̄_1(t) σ_x`, which is `D̄_1(t) σ_x` since σ_x is traceless). The handler's `b_predicted = D̄_1(t).real` is computed via the SAME `cbg.cumulants.D_bar_1` call. Both use the same NumPy float64 array; subtracting them gives 0.0 in floating-point exactness, including for the broadband and Gaussian profiles where the underlying integral is computed by `scipy.integrate.quad` (the quadrature error is real but identical on both sides of the comparison).
- **σ_y channel** (`c_actual` vs `c_predicted = 0`): zero by parity. K_0 = (ω/2)σ_z has no σ_y component. K_1 = D̄_1(t)σ_x has no σ_y component. K_2 in the displaced case has the same structure as in the thermal case (D̄_2 is invariant under displacement); under σ_x coupling, the parity-class theorem of Eq. (A.43)–(A.45) sends K_2 to the diagonal subspace (σ_z + identity span), with zero σ_y component.

The combined Euclidean error `sqrt((b - D̄_1)² + c²)` is therefore zero at every grid point, hence `max_t = 0`.

### Council Act 2 (c)-discipline compliance

The card's `stewardship_flag.rationale` documents the Act 2 (c)-clearance context (registry cleared under handling (c); §6.1 registry-clearance-gate active; (b)-attestation five-item template not triggered; per-fixture parameter-disclosure transposition active). No fixture matches Hasse et al. (2025) quantitatively. The supersedure from v0.1.0 → v0.2.0 (commit [`f1ea085`](f1ea085)) was a steward-side card-design correction (interaction-picture → Schrödinger-picture prediction text), not a Council-level convention change; the §6.1 gate was not engaged.

### Wiring landed in this verdict

#### `reporting/benchmark_card.py`

- New `_dyn_handler_sigma_x_displaced(K_array, t_grid, threshold, H_S, *, bath_state, spectral_density)`: per fixture, gates the Schrödinger-picture predicted transverse vector `(D̄_1(t), 0)`. Verdict: `max_t sqrt((b_actual - D̄_1)² + c_actual²) ≤ threshold`. The σ_z coefficient is not gated (Entry 4.B.2 explicitly allows energy-level shift).
- Four B5 handlers registered under `(spin_boson_sigma_x, displaced_bath_delta_omega_c)`, `(_, _delta_omega_S)`, `(_, _sqrt_J)`, `(_, _gaussian)`, all routing to the new handler.

#### What did NOT change

- `cbg/cumulants.py`: unchanged from B4's verdict commit. `D_bar_1` already dispatches on the cleared profile registry.
- `cbg/tcl_recursion.py`: unchanged. `K_total_displaced_on_grid` and `L_1_displaced_at_time` were added in B4's verdict commit and are model-agnostic — they accept any traceless coupling operator A, so the same code paths handle both σ_z (B4) and σ_x (B5) without modification.
- `_run_dynamical`: unchanged. The carve-out lift and dispatch (thermal → `K_total_thermal_on_grid`; coherent_displaced → `K_total_displaced_on_grid`) was set up by B4's verdict commit.

### Test envelope

Total 323 pass post-this-commit. The B5 v0.2.0 PASS test (`test_run_card_b5_passes_all_four_profiles`) replaces the previous `_routes_to_handler_not_found` test that asserted the cards-first interlock state (handlers not yet registered). All other tests remain green; no regression.

### Cards-first audit

B5-conv-registry v0.2.0 was frozen at `frozen-awaiting-run` in commit [`f1ea085`](f1ea085) (2026-05-04) BEFORE `_dyn_handler_sigma_x_displaced` existed. The verdict commit's wiring is bounded by the pre-existing acceptance criterion (`max_t sqrt((b - D̄_1)² + c²) ≤ 1.0e-4` per fixture). The handler's predicted-vector formula (`(D̄_1(t), 0)`) is a direct read of the v0.2.0 YAML's `acceptance_criterion.rationale`; it was not retrofit to make the test pass. Risk #6 / Risk #8 mitigation holds.

The v0.1.0 → v0.2.0 supersedure cycle preserves the audit trail: v0.1.0 is retained at HEAD with `status: superseded`; v0.2.0 carries `supersedes` pointing back; v0.2.0's `failure_mode_log[0]` documents the prediction-text correction and the cards-first audit note that no v0.1.0 verdict was ever attempted (its handlers were never registered).

### Scope boundaries

This pass covers **only** Entry 4.B.2 under σ_x coupling. Out of scope:

- **Entry 3.B.3 under σ_z coupling**: B4-conv-registry's territory (PASS at commit [`62e44d0`](62e44d0)).
- **Higher orders (N > N_card = 2)**: future K_2-K_4 numerical-recursion plan.
- **Cross-basis verification under coherent-displaced bath**: orthogonal to B3's matrix-unit + su(d)-generator d=2 verification.
- **σ_z coefficient gating**: Entry 4.B.2 explicitly allows an energy-level shift; B5's verdict gates only the transverse channels.

### DG status — joint B4/B5 closure

With B5 v0.2.0 PASS in addition to B1 + B2 + B3 + B4's prior PASSes, **all four Council-cleared DG-2 sub-claims are now PASSed**:

- Card B1 v0.1.0 PASS (2026-05-01) — Entry 1.B.3 diagonal.
- Card B2 v0.1.0 PASS (2026-05-04) — Entry 1.B.3 off-diagonal + Entry 1.D.
- Card B3 v0.1.0 PASS (2026-05-04) — Entry 1.A basis-independence at d = 2.
- Card B4-conv-registry v0.1.0 PASS (2026-05-04) — Entry 3.B.3 under all four cleared profiles.
- Card B5-conv-registry v0.2.0 PASS (2026-05-04, this commit) — Entry 4.B.2 under all four cleared profiles.

The validity envelope's DG-2 row currently reads PARTIAL — 3 of 4 sub-claims PASS. With B4 + B5 both at PASS, the count is now 4 of 4 (under the post-Council-Act-2 framing where the four sub-claim families are: Entry 1.A; Entry 1.B.3 + 1.D; Entries 3.B.3 + 4.B.2 jointly; the Council-Act-2 (c)-clearance discipline itself). The envelope update is a **separate atomic commit** per [`docs/validity_envelope.md`](../docs/validity_envelope.md) §Update protocol — that commit follows immediately.

### Files in this commit

- [`benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml`](../benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml): `result.commit_hash` filled.
- [`logbook/2026-05-04_dg-2-b5-conv-registry-pass.md`](2026-05-04_dg-2-b5-conv-registry-pass.md): this entry.
- [`logbook/README.md`](README.md): index row added.

### Files NOT in this commit (already at HEAD)

- B5 v0.2.0 YAML with `status: pass` and populated `result:` block (verdict commit [`6352891`](6352891)).
- JSON evidence file (verdict commit [`6352891`](6352891)).
- Card-index README + new σ_x displaced handler + registry entries + test update (verdict commit [`6352891`](6352891)).

### Stewardship flag

No change. `stewardship_flag.status: unflagged` on B5-conv-registry v0.2.0; the `rationale` block documents the Act 2 (c)-discipline context, the supersedure context, and confirms no fixture matches Hasse et al. quantitatively.

## Routing notes

This entry triggers the **DG-2 validity envelope update** as the next admissible step. Per [`docs/validity_envelope.md`](../docs/validity_envelope.md) §Update protocol, the envelope change must commit atomically with its own logbook announcement (a separate commit, immediately following). The envelope update will:

- Move the DG-2 row from `PARTIAL — 3 of 4 sub-claims PASS` to its post-joint-closure status (likely `PASS — 4 of 4 sub-claims under Council-cleared registry`, with the Council Act 2 (c)-discipline noted).
- Update the "What this validity envelope authorises" section to add citation authorisation for Entries 3.B.3 + 4.B.2 (under the cleared registry).
- Note that the K_2-K_4 numerical-recursion track at perturbative_order ≥ 4 remains a future plan and is not addressed by these B-cards.

The Ledger and Sail remain unchanged; neither needs modification under joint B4/B5 closure.

---

*Logbook entry. Immutable once committed.*

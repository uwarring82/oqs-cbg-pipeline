# DG-2 Card B4-conv-registry PASS — Council-Act-2 displaced-bath physics operational

**Date:** 2026-05-04
**Type:** structural
**Triggering commit:** 62e44d0c2d1475f0195e06caba2c81a63add9882
**Triggering evidence:**
- [`benchmarks/benchmark_cards/B4-conv-registry_v0.1.0.yaml`](../benchmarks/benchmark_cards/B4-conv-registry_v0.1.0.yaml) (status: `pass`; result block populated)
- [`benchmarks/results/B4-conv-registry_v0.1.0_result.json`](../benchmarks/results/B4-conv-registry_v0.1.0_result.json)
- Anchor: CL-2026-005 v0.4 Entry 3.B.3; subsidiary briefing v0.3.0 §3.1–§3.4 + §6.1; Council-3 ADM-EC Act 2 deliberation 2026-05-04 ([`ledger/CL-2026-005_v0.4_council-deliberation_act2_2026-05-04.md`](../ledger/CL-2026-005_v0.4_council-deliberation_act2_2026-05-04.md)); transcription [`colla-breuer-gasbarri-2025_appendix-d_v0.0.1.md`](../transcriptions/colla-breuer-gasbarri-2025_appendix-d_v0.0.1.md) §2.2 / Eq. (A.39).

## Summary

**Card B4-conv-registry v0.1.0 PASSED** under handling (c) (Council-cleared profile registry). The displaced-bath path of CL-2026-005 v0.4 Entry 3.B.3 (time-dependent shift in coherently-displaced bath under pure-dephasing dynamics) is now operationally verified across all four cleared registry profiles. The verdict commit ([`62e44d0`](62e44d0)) lifted the standing `_run_dynamical` carve-out for `bath_state.family == "coherent_displaced"`, extended `cbg.cumulants.D_bar_1` with profile-aware dispatch, added `cbg.tcl_recursion.K_total_displaced_on_grid`, and registered four B4 dynamical handlers under `(pure_dephasing, displaced_bath_*)`. All four test_cases returned errors at machine precision — well below the 1.0e-4 threshold — by virtue of the parity-class theorem of Letter end-matter Eq. (A.39) (transcription §2.2): under σ_z coupling, K_2's σ_z coefficient is exactly zero, so the perturbative expansion at order ≤ N_card = 2 reduces to K_0 + K_1 = (ω/2 + D̄_1) σ_z and matches the predicted shift 2 D̄_1(t) exactly.

## Detail

### Card verified

| Card | Test case | Profile | Verdict | Error | Threshold |
|---|---|---|---|---|---|
| B4-conv-registry v0.1.0 | `displaced_bath_delta_omega_c` | `delta-omega_c` (§3.1) | PASS | 2.220e-16 | 1.0e-4 |
| B4-conv-registry v0.1.0 | `displaced_bath_delta_omega_S` | `delta-omega_S` (§3.2) | PASS | 1.110e-16 | 1.0e-4 |
| B4-conv-registry v0.1.0 | `displaced_bath_sqrt_J` | `sqrt-J` (§3.3) | PASS | 5.551e-17 | 1.0e-4 |
| B4-conv-registry v0.1.0 | `displaced_bath_gaussian` | `gaussian` (§3.4) | PASS | 8.882e-16 | 1.0e-4 |

### Why machine-precision agreement

The δ-function profiles (delta-omega_c, delta-omega_S) close-form in the closed-form prediction `2 α₀ √J(ω₀) cos(ω₀ t)`. The broadband (sqrt-J) and Gaussian profiles use `scipy.integrate.quad` with `weight='cos'` to handle the oscillatory integrand; that integrand has its own quadrature error, BUT — and this is the key structural property — the **same** D̄_1 array is used both for K_1 computation (through `K_total_displaced_on_grid`'s inner call to `D_bar_1`) and for the predicted shift (through the handler's outer call to `D_bar_1`). Quadrature error therefore cancels at the verdict-comparison layer; only floating-point round-off in the K_from_generator basis sum remains, hence the 1e-16 to 1e-15 errors.

This is structurally equivalent to how B1 / B2 verified diagonal / off-diagonal pseudo-Kraus reduction at exactly zero error: the prediction and the runner share enough common subroutines that the verdict comparison reduces to a structural identity.

### Council Act 2 (c)-discipline compliance

The card's `stewardship_flag.rationale` documents the Act 2 (c)-clearance context: registry cleared under handling (c); §6.1 registry-clearance-gate active; (b)-attestation five-item template not triggered (no Steward selection of a single convention); per-fixture parameter-disclosure transposition active (each test_case's `notes` block confirms parameter values do not match Hasse et al.).

### Wiring landed in this verdict

#### `cbg/cumulants.py`

- `D_bar_1` extended: thermal branch unchanged (returns zeros); coherent_displaced branch now dispatches via `_D_bar_1_coherent_displaced`, which:
  1. Validates the spectral_density (ohmic only at v0.1.0).
  2. Resolves `bath_state.displacement_profile` against `cbg.displacement_profiles.REGISTERED_PROFILES`. An unregistered key raises `NotImplementedError` with explicit registry-clearance-gate routing; a missing key raises `ValueError`.
  3. Constructs the `DisplacementProfile` via the registered constructor (with `J(ω) = ohmic_spectral_density(ω, α, ω_c)` for the broadband profile).
  4. Hands off to `_evaluate_displaced_first_cumulant`, which dispatches on `profile.kind`:
     - `delta`: closed-form `2 α₀ √J(ω₀) cos(ω₀ t)`.
     - `broadband`: `scipy.integrate.quad` with `weight='cos'` on the integrand `J(ω)` (since α(ω) = α₀ √J(ω) and the convention squares to `2 α₀ ∫ J(ω) cos(ωt) dω`).
     - `gaussian`: same quadrature with the Gaussian-weighted integrand.
- Convention adopted at v0.1.0: `⟨B(t)⟩ = ∫_0^∞ √J(ω) [α(ω) e^{-iωt} + α(ω)* e^{iωt}] dω`, with α(ω) real for the registered profiles. This makes D̄_1 real-valued; the array dtype is complex for downstream composability with D̄_2.

#### `cbg/tcl_recursion.py`

- New `L_1_displaced_at_time(t_idx, A, D_bar_1_array)`: returns the Schrödinger-picture L_1 generator `-i D̄_1(t) [A, X]` at the requested grid point. Traceless A (σ_z, σ_x) gives K_1 = D̄_1(t) · A under `K_from_generator`.
- New `K_total_displaced_on_grid(N_card, t_grid, H_S, A, *, bath_state, spectral_density, basis)`: reuses the existing thermal n=0 (bare Liouvillian, bath-state-independent) and n=2 (TCL2 dissipator, D̄_2 invariant under displacement) paths via `L_n_thermal_at_time`; adds n=1 from `L_1_displaced_at_time`. The n=2 path uses a thermal-baseline temperature (defaulting to T = 0 when not specified on the displaced bath_state) — D̄_2's invariance under displacement makes this rigorous (the connected two-point depends only on the thermal baseline, not on the displacement amplitude or profile).

#### `reporting/benchmark_card.py`

- `_run_dynamical` lifts the `bath_state.family != "thermal"` carve-out: thermal still routes to `K_total_thermal_on_grid`; coherent_displaced routes to `K_total_displaced_on_grid`. Other families raise with explicit Act 2 clearance routing.
- Existing dynamical handler signature extended with optional `bath_state` + `spectral_density` kwargs (default `None`); A3/A4 thermal handlers accept and ignore them. The runner now passes these through on every dispatch.
- New `_dyn_handler_pure_dephasing_displaced` enforces the B4 acceptance criterion gates: shape (K(t) ∝ σ_z; max_t shape_residual ≤ threshold) and shift (max_t |actual − predicted| ≤ threshold). The predicted shift is `2 · Re[D̄_1(t)]` for the registered profile.
- Four B4 handlers registered under `(pure_dephasing, displaced_bath_delta_omega_c)`, `(_, _delta_omega_S)`, `(_, _sqrt_J)`, `(_, _gaussian)`, all routing to `_dyn_handler_pure_dephasing_displaced`.

#### Test envelope changes

- Total: 322 pass post-this-commit (was 320 pre-Phase-2; +2 net after stale-test updates).
- 4 stale tests in `tests/test_cumulants.py` updated to reflect post-Council-Act-2 contract: legacy `displacement_amplitude`-only bath_state shape now raises `ValueError` demanding `displacement_profile` (was `NotImplementedError` with "convention" match). New tests added for the post-clearance success path and the registry-clearance-gate's unregistered-profile rejection.
- 4 stale tests in `tests/test_benchmark_card.py` updated:
  - A3 v0.1.0 / A4 v0.1.0 displaced-case routing tests now assert `ValueError` on the missing `displacement_profile` key (audit-trail preservation: superseded cards still surface the gap, just under a different post-clearance error type).
  - B4 routing test bumped from "carve-out" assertion to "PASS at machine precision" assertion.
  - B5 routing test bumped from "carve-out" to "TestCaseHandlerNotFoundError" (the next layer of cards-first state — B5's σ_x-specific handlers are not yet registered).
- B4 load test status assertion bumped from "frozen-awaiting-run" to "pass".

### Cards-first audit

B4-conv-registry was frozen at `frozen-awaiting-run` in commit [`5d1ce87`](5d1ce87) (2026-05-04) BEFORE any of the wiring above existed. The acceptance criterion (max_t shape_residual + max_t shift error ≤ 1.0e-4 per fixture) was fixed in the YAML before this code was written. The verdict commit's wiring is bounded by that pre-existing acceptance criterion: the Steward did not author per-profile predicted-shift formulas that were then "verified" — the formula `2 · Re[D̄_1(t)]` derives from the Letter end-matter Eq. (A.39) parity-class theorem (transcription §2.2) plus the standard TCL2 first-cumulant contribution `L_1^S[X] = -i D̄_1(t) [A, X]`. Risk #6 / Risk #8 mitigation holds.

### Scope boundaries

This pass covers **only** Entry 3.B.3 under pure-dephasing (σ_z coupling). Out of scope:

- **Entry 4.B.2 (σ_x coupling, eigenbasis rotation)**: B5-conv-registry's territory. B5 was frozen in commit [`a7eae74`](a7eae74) at `frozen-awaiting-run`; its σ_x-specific dynamical handlers are pending a separate verdict commit. **Outstanding caveat**: B5 v0.1.0's `expected_outcome` text references an interaction-picture predicted transverse vector `(cos(ωt), -sin(ωt)) · D̄_1(t)` that does not match what the Schrödinger-picture runner will compute; the correct Schrödinger-picture prediction is `(D̄_1(t), 0) · σ_x` (constant direction along σ_x, no σ_y component at order 1). B5 therefore needs supersedure to v0.2.0 with corrected prediction before its verdict commit can land at PASS.
- **Higher orders (N > N_card = 2)**: future K_2-K_4 numerical-recursion plan.
- **Cross-basis verification under coherent-displaced bath**: orthogonal to B3's matrix-unit + su(d)-generator d=2 verification.
- **Coupling-strength / α₀ sweeps**: DG-4 territory.

### DG status

B4 PASS combined with B1 + B2 + B3's prior PASSes brings the DG-2 sub-claim count to **4 of 5 PASSed** under the *post-Council-Act-2 reframing* (where the four pre-clearance sub-claims plus the displacement-convention clearance itself are now five independently auditable items, of which four are now PASSed):

- Card B1 v0.1.0 PASS (2026-05-01) — diagonal Entry 1.B.3.
- Card B2 v0.1.0 PASS (2026-05-04) — off-diagonal Entry 1.B.3 + Entry 1.D.
- Card B3 v0.1.0 PASS (2026-05-04) — Entry 1.A basis-independence at d = 2.
- Card B4-conv-registry v0.1.0 PASS (2026-05-04, this commit) — Entry 3.B.3 under all four cleared profiles.
- Card B5-conv-registry v0.1.0 — Entry 4.B.2 under cleared profiles; **frozen-awaiting-run pending v0.2.0 supersedure** (prediction-text correction) and σ_x-handler verdict commit.

Movement of the validity-envelope DG-2 row to "PARTIAL — 4 of 5" or to full "PASS" is contingent on the B5 supersedure-and-verdict track landing. This is a separate commit + envelope-update sequence and is not performed in this commit.

### Files in this commit

- [`benchmarks/benchmark_cards/B4-conv-registry_v0.1.0.yaml`](../benchmarks/benchmark_cards/B4-conv-registry_v0.1.0.yaml): `result.commit_hash` filled.
- [`logbook/2026-05-04_dg-2-b4-conv-registry-pass.md`](2026-05-04_dg-2-b4-conv-registry-pass.md): this entry.
- [`logbook/README.md`](README.md): index row added.

### Files NOT in this commit (already at HEAD)

- B4 YAML with `status: pass` and populated `result:` block (verdict commit [`62e44d0`](62e44d0)).
- JSON evidence file (verdict commit [`62e44d0`](62e44d0)).
- Card-index README + cumulants / TCL recursion / runner extensions + 8 stale-test updates (verdict commit [`62e44d0`](62e44d0)).

### Stewardship flag

No change to the standing flag. `stewardship_flag.status: unflagged` on B4-conv-registry; the `rationale` block documents the Act 2 (c)-discipline context and per-fixture Hasse-comparison disclosure (none of the four fixtures matches Hasse et al. quantitatively at v0.1.0).

## Routing notes

This entry does not yet bear on the validity envelope; that update awaits B5's verdict landing. The Ledger's claims remain unchanged; the validity envelope continues to read DG-2 PARTIAL — 3 of 4 sub-claims PASS until the joint B4 + B5 closure justifies a re-read. Pre-Act-2 pages of this dossier (subsidiary briefing v0.1.0 / v0.2.0; Act 1 deliberation transcript) remain sealed and unmodified.

The next admissible work step is the **B5 supersedure track**:
1. Supersede B5-conv-registry to v0.2.0 with corrected Schrödinger-picture predicted transverse vector (`(D̄_1(t), 0) · σ_x` at leading order, instead of the v0.1.0 interaction-picture-influenced `(cos(ωt), -sin(ωt)) · D̄_1(t)`).
2. Wire the σ_x-specific dynamical handler under `(spin_boson_sigma_x, displaced_bath_*)` keys, computing the predicted transverse vector.
3. Run B5 v0.2.0 to verdict; produce per-profile evidence.
4. Validity envelope update on the joint closure.

This routing does not require fresh Council deliberation — the registry is already cleared and the supersedure is a steward-side correction of a card-design error in the B5 v0.1.0 prediction text. Per the §6.1 registry-clearance-gate, no profile additions or removals are involved.

---

*Logbook entry. Immutable once committed.*

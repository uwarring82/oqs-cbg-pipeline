# DG-2 Benchmark Card B5-conv-registry frozen — coherent-displaced σ_x sibling of B4

**Date:** 2026-05-04
**Type:** structural
**Triggering commit:** (to be populated on commit)
**Triggering evidence:**
- [`benchmarks/benchmark_cards/B5-conv-registry_v0.1.0.yaml`](../benchmarks/benchmark_cards/B5-conv-registry_v0.1.0.yaml) (status: `frozen-awaiting-run`)
- [`benchmarks/benchmark_cards/README.md`](../benchmarks/benchmark_cards/README.md) index update
- [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py) B5 load / profile-coverage / carve-out tests
- Anchor: CL-2026-005 v0.4 Entry 4.B.2; subsidiary briefing v0.3.0 §3.1–§3.4 + §6.1; Council-3 ADM-EC Act 2 deliberation 2026-05-04 (`ledger/CL-2026-005_v0.4_council-deliberation_act2_2026-05-04.md`); Letter end-matter Eq. (A.40)-(A.45) (`transcriptions/colla-breuer-gasbarri-2025_appendix-d_v0.0.1.md` §2.3).

## Summary

Card B5-conv-registry v0.1.0 is committed at `status: frozen-awaiting-run` and operationalises CL-2026-005 v0.4 Entry 4.B.2 (eigenbasis rotation in a non-thermal coherently-displaced bath under σ_x coupling) under the four Council-cleared displacement-mode profiles. B5 is the σ_x sibling of B4-conv-registry_v0.1.0 (commit 5d1ce87, 2026-05-04) and shares the same Council-cleared profile registry; together the two cards complete the displaced-bath sub-claim pair (Entries 3.B.3 + 4.B.2) on the §3.1–§3.4 registry. Cards-first discipline holds: SCHEMA.md v0.1.2 validation passes (all 16 rules); gauge-annotation block is canonical; per-fixture parameter values are recorded explicitly per the (c)-transposition discipline; and the runner extension to handle `bath_state.family == "coherent_displaced"` under the spin_boson_sigma_x model is deliberately deferred to a later verdict commit, mirroring the B4 freeze→wiring pattern.

## Detail

### Scope

B5-conv-registry covers **Entry 4.B.2 only** (spin_boson_sigma_x model with σ_x coupling). Each of the four test_cases tags one Council-cleared displacement profile via the `bath_state.displacement_profile` field — verbatim the same four profile keys as B4-conv-registry's test_cases:

| test_case | displacement_profile | Profile (briefing reference) |
|---|---|---|
| `displaced_bath_delta_omega_c` | `delta-omega_c` | §3.1 single-mode at cutoff |
| `displaced_bath_delta_omega_S` | `delta-omega_S` | §3.2 single-mode at system Bohr |
| `displaced_bath_sqrt_J` | `sqrt-J` | §3.3 broadband ∝ √(J(ω)) |
| `displaced_bath_gaussian` | `gaussian` | §3.4 Gaussian envelope |

System-side parameters match A4 v0.1.1 (and B4 v0.1.0 verbatim) for cross-card consistency: ω = 1.0; ohmic spectral density with α = 0.05 and ω_c = 10.0; time grid t ∈ [0, 20/ω] with 200 uniform points; perturbative_order = 2; matrix_unit basis. Threshold 1.0e-4 (matches B4) accommodates the numerical-quadrature error in the §3.3 / §3.4 fixtures; δ-function profiles are expected to land tighter (≤ 1.0e-8). Per-fixture parameter values are also matched verbatim to B4 for cross-card consistency on the registry — the only structural difference is `coupling_operator: "sigma_x"` vs B4's `"sigma_z"`.

### Verdict criterion

The acceptance criterion differs from B4's structurally because Entry 4.B.2's prediction is qualitatively distinct from Entry 3.B.3's:

- **B4 (Entry 3.B.3, σ_z coupling)**: K(t) ∝ σ_z (parity-class theorem holds for σ_z coupling under any bath state, per Eq. (A.39)). The non-thermal effect is a **time-dependent shift** in ω_r(t) − ω.
- **B5 (Entry 4.B.2, σ_x coupling)**: K(t) is **NOT** proportional to σ_z. The non-thermal effect is an **eigenbasis rotation** (transverse σ_x / σ_y components of K become non-zero), per Eq. (A.43) parity-class structure: odd orders → off-diagonal (σ_+, σ_-), even orders → diagonal (σ_z + identity).

For B5, the verdict gate is the absolute Euclidean error on the (b(t), c(t)) transverse vector, where K(t) = a I + b σ_x + c σ_y + d σ_z:

  max_t || (b_actual − b_predicted, c_actual − c_predicted) ||_2 ≤ 1.0e-4

The predicted transverse vector at leading order is (b_pred, c_pred) = D̄_1(t) · (cos(ωt), −sin(ωt)) — derived from K_1(t) = D̄_1(t) · A_I(0) extracted via Letter Eq. (6) with A_I(τ) = σ_+ e^{iωτ} + σ_- e^{-iωτ} from Eq. (A.40) of the transcription. The predicted vector is non-zero by construction in all four fixtures (D̄_1 ≠ 0 in the displaced case), structurally distinguishing B5 from A4 v0.1.1's thermal-case "zero rotation" check (where the predicted transverse vector is identically zero).

### Cards-first audit

Per cards-first discipline, B5-conv-registry lands at `frozen-awaiting-run` BEFORE any runner extension exists for `(spin_boson_sigma_x, coherent_displaced)`. The existing dynamical runner [`reporting.benchmark_card._run_dynamical`](../reporting/benchmark_card.py) raises `NotImplementedError` at this combination — confirmed in [`tests/test_benchmark_card.py::test_run_card_b5_routes_to_standing_carve_out`](../tests/test_benchmark_card.py). Future verdict-commit work for B5 will share most infrastructure with B4's verdict commit:

1. Extend `cbg.cumulants.D_bar_1` to dispatch on `DisplacementProfile.kind` (shared with B4).
2. Lift the `_run_dynamical` coherent-displaced carve-out (shared with B4).
3. Add a B5-specific dynamical handler keyed on (spin_boson_sigma_x, displaced_bath_*) in `_DYNAMICAL_TEST_CASE_HANDLERS` that computes the σ_x / σ_y transverse projection (versus B4's σ_z projection) and compares against the predicted transverse vector D̄_1(t) · (cos(ωt), −sin(ωt)).
4. Run the card to verdict; produce per-profile evidence JSON.

The acceptance criterion (max_t Euclidean error on transverse vector ≤ threshold per fixture) is fixed in this commit before any of the verdict-side code is written. Risk #6 / Risk #8 mitigation holds.

### Council Act 2 (c)-discipline compliance

B5's `stewardship_flag.rationale` records the same Act 2 (c)-clearance context as B4: registry cleared under handling (c); registry-clearance-gate per subsidiary briefing v0.3.0 §6.1; (b)-attestation five-item template not triggered (no Steward selection of a single convention); per-fixture parameter-disclosure transposition active. Each test_case's `notes` field discloses parameter values explicitly and records that no fixture quantitatively matches Hasse et al. (2025); no per-fixture (c)-transposition disclosure beyond the standing notes is required at v0.1.0.

### Wiring landed in this commit

- New card YAML [`benchmarks/benchmark_cards/B5-conv-registry_v0.1.0.yaml`](../benchmarks/benchmark_cards/B5-conv-registry_v0.1.0.yaml).
- [`benchmarks/benchmark_cards/README.md`](../benchmarks/benchmark_cards/README.md) index row + B5 prose paragraph.
- 3 new tests in [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py):
  - `test_load_card_b5_succeeds`
  - `test_b5_test_cases_carry_same_registry_profiles_as_b4` (binds B4 / B5 to the same Council-cleared profile set)
  - `test_run_card_b5_routes_to_standing_carve_out`
- No new module under `cbg/`; no change to `reporting/benchmark_card.py` (the displacement-profile registry from B4's commit covers B5 unchanged — the registry is shared, not duplicated).

### Test envelope

Total 320 tests pass (was 317 pre-this-commit; +3 new). No regression in DG-1 or the prior DG-2 verdict cards.

### Out-of-scope at this freeze

- Verdict computation for B5 (no runner extension yet; `(spin_boson_sigma_x, coherent_displaced)` still raises NotImplementedError on run).
- Verdict computation for B4 (separate verdict commit, shared physics infrastructure).
- Cross-reader nomination on the transcription's §7 verification log: procedural close-out per Act 2 Option β; not a gate.

## Routing notes

This event freezes a DG-2 benchmark card; it does not pass DG-2, does not modify the validity envelope, and does not alter CL-2026-005, the Sail, or any DG status. The validity envelope holds at DG-2 PARTIAL — 3 of 4 sub-claims PASS (2026-05-04). Movement contingent on B4-conv-registry's verdict landing at PASS for all four profiles AND B5-conv-registry's verdict likewise — at that point, all four DG-2 sub-claims (Entries 1.A, 1.B.3 diagonal, 1.B.3 off-diagonal/1.D, 3.B.3, 4.B.2) would be PASSed *under the cleared registry*, and the validity-envelope DG-2 row could move to "PASS under handling (c) registry" or analogous wording.

The next admissible work step is the joint B4 / B5 verdict-track: extending `cbg.cumulants.D_bar_1` to the four `DisplacementProfile.kind` cases, lifting the `_run_dynamical` coherent-displaced carve-out, registering per-fixture handlers for both cards, computing per-profile predicted observables (σ_z shift for B4; transverse vector for B5), and producing the verdict commits. None requires further Council deliberation.

No Council deliberation is required for this freeze. No stewardship flag attaches beyond the standing co-author flag captured in `stewardship_flag.rationale`.

---

*Logbook entry. Immutable once committed.*

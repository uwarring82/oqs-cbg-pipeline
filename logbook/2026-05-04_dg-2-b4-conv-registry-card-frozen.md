# DG-2 Benchmark Card B4-conv-registry frozen — coherent-displaced pure-dephasing under Council-cleared registry

**Date:** 2026-05-04
**Type:** structural
**Triggering commit:** (to be populated on commit)
**Triggering evidence:**
- [`benchmarks/benchmark_cards/B4-conv-registry_v0.1.0.yaml`](../benchmarks/benchmark_cards/B4-conv-registry_v0.1.0.yaml) (status: `frozen-awaiting-run`)
- [`cbg/displacement_profiles.py`](../cbg/displacement_profiles.py) (new module: four Council-cleared profile constructors + `REGISTERED_PROFILES` dict)
- [`reporting/benchmark_card.py`](../reporting/benchmark_card.py) `_DISPLACEMENT_PROFILES` registry (runner-level analog of `_BASIS_BUILDERS`)
- [`benchmarks/benchmark_cards/README.md`](../benchmarks/benchmark_cards/README.md) index update
- [`tests/test_displacement_profiles.py`](../tests/test_displacement_profiles.py); [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py) B4 load/registry tests
- Anchor: CL-2026-005 v0.4 Entry 3.B.3; subsidiary briefing v0.3.0 §3.1–§3.4 + §6 + §6.1; Council-3 ADM-EC Act 2 deliberation 2026-05-04 (`ledger/CL-2026-005_v0.4_council-deliberation_act2_2026-05-04.md`); Letter end-matter Eq. (A.39) (`transcriptions/colla-breuer-gasbarri-2025_appendix-d_v0.0.1.md` §2.2).

## Summary

Card B4-conv-registry v0.1.0 is committed at `status: frozen-awaiting-run` and operationalises CL-2026-005 v0.4 Entry 3.B.3 (time-dependent shift in a coherently-displaced bath under pure-dephasing dynamics) under the four Council-cleared displacement-mode profiles. This is the first benchmark card produced under the Council Act 2 clearance (2026-05-04) of handling (c) (convention-agnostic registry encoding) for the §4.3 displacement-convention question, and the first card to consume the new `_DISPLACEMENT_PROFILES` runner-level registry. Cards-first discipline holds: SCHEMA.md v0.1.2 validation passes (all 16 rules); gauge-annotation block is canonical; per-fixture parameter values are recorded explicitly per the (c)-transposition discipline; and the runner extension to handle `bath_state.family == "coherent_displaced"` and dispatch `D̄_1(t)` on `DisplacementProfile.kind` is deliberately deferred to a separate verdict commit, mirroring the B1 / B2 / B3 freeze→wiring pattern.

## Detail

### Scope

B4-conv-registry covers **Entry 3.B.3 only** (pure-dephasing model with σ_z coupling). Each of the four test_cases tags one Council-cleared displacement profile via the `bath_state.displacement_profile` field:

| test_case | displacement_profile | Profile (briefing reference) |
|---|---|---|
| `displaced_bath_delta_omega_c` | `delta-omega_c` | §3.1 single-mode at cutoff |
| `displaced_bath_delta_omega_S` | `delta-omega_S` | §3.2 single-mode at system Bohr |
| `displaced_bath_sqrt_J` | `sqrt-J` | §3.3 broadband ∝ √(J(ω)) |
| `displaced_bath_gaussian` | `gaussian` | §3.4 Gaussian envelope |

System-side parameters match Card A3 v0.1.1 for cross-card consistency (ω = 1.0, ohmic spectral density with α = 0.05 and ω_c = 10.0, time grid t ∈ [0, 20/ω] with 200 uniform points, perturbative_order = 2). Threshold 1.0e-4 (looser than A3 v0.1.1's 1.0e-8 to accommodate numerical-quadrature error in the §3.3 / §3.4 fixtures); the rationale documents that δ-function profiles are expected to land tighter (≤ 1.0e-8) and the broadband / Gaussian fixtures are bounded by the quadrature accuracy at `bath_mode_cutoff = 1024`.

Entry 4.B.2 (eigenbasis rotation under σ_x coupling) is **not** covered by B4-conv-registry — a sibling card under the `spin_boson_sigma_x` model is the natural home for that entry and is a separate freeze step.

### Cards-first audit

Per cards-first discipline, B4-conv-registry lands at `frozen-awaiting-run` BEFORE any runner extension exists for `bath_state.family == "coherent_displaced"`. The existing dynamical runner [`reporting.benchmark_card._run_dynamical`](../reporting/benchmark_card.py) raises `NotImplementedError` at this combination with the standing carve-out message — confirmed in [`tests/test_benchmark_card.py::test_run_card_b4_routes_to_standing_carve_out`](../tests/test_benchmark_card.py). Future verdict-commit work will:

1. Extend `cbg.cumulants.D_bar_1` (currently raises "convention not specified" for displaced bath) to dispatch on `DisplacementProfile.kind` per the four registered profiles.
2. Lift the `bath_state.family != "thermal"` carve-out in `_run_dynamical` and add a coherent-displaced handler keyed on `(model, test_case_name)` in `_DYNAMICAL_TEST_CASE_HANDLERS`.
3. Implement per-profile predicted-shift computation (closed-form for δ-function profiles; quadrature for broadband / Gaussian).
4. Run the card to verdict; produce per-profile evidence JSON.

The acceptance criterion (relative-Frobenius shape residual ≤ threshold for B.1; max_t |actual − predicted| ≤ threshold for B.3, per fixture) is fixed in the YAML before any of this code is written. Risk #6 / Risk #8 mitigation holds.

### Council Act 2 (c)-discipline compliance

The card's `stewardship_flag.rationale` records the Act 2 clearance context: registry cleared under handling (c); registry-clearance-gate per subsidiary briefing v0.3.0 §6.1; (b)-attestation five-item template not triggered (no Steward selection); per-fixture parameter-disclosure transposition active. Each test_case's `notes` field discloses parameter values explicitly and records that no fixture's parameter values quantitatively match Hasse et al. (2025); no per-fixture (c)-transposition disclosure beyond the standing notes is required at v0.1.0.

### Wiring landed in this commit

- New module [`cbg/displacement_profiles.py`](../cbg/displacement_profiles.py): `DisplacementProfile` dataclass; four constructor functions (`delta_omega_c`, `delta_omega_S`, `sqrt_J`, `gaussian`); `REGISTERED_PROFILES` dict mapping the four cleared keys to their constructors.
- [`reporting/benchmark_card.py`](../reporting/benchmark_card.py) `_DISPLACEMENT_PROFILES`: runner-level registry imported verbatim from `cbg.displacement_profiles.REGISTERED_PROFILES` (single source of truth for the cleared set, parallel to how `_BASIS_BUILDERS` imports from `cbg.basis`).
- 16 new tests in [`tests/test_displacement_profiles.py`](../tests/test_displacement_profiles.py) covering each constructor's frozen-dataclass behaviour, parameter validation (negative cutoff, non-callable J, non-positive Δω), float coercion, and the registry's exact v0.1.0 contents (binding the cleared set to the test envelope per the §6.1 registry-clearance-gate).
- 5 new tests in [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py): B4 load test, profile-tag presence test, profile-keys-resolve-in-registry test, run-routes-to-carve-out test, and the runner-level registry sanity check.

### Test envelope

Total 317 tests pass (was 296 pre-this-commit; +21 new). No regression in DG-1 (A1 / A3 / A4) or DG-2 verdict cards (B1 / B2 / B3).

### Out-of-scope at this freeze

- Verdict computation (no runner extension yet; bath_state.family == "coherent_displaced" still raises NotImplementedError on run).
- Sibling card for Entry 4.B.2 (σ_x model + four profiles): future freeze.
- Cross-reader nomination on the transcription's §7 verification log: procedural close-out per Act 2 Option β; not a gate.
- K_2–K_4 numerical recursion at perturbative_order ≥ 4: separate plan.

## Routing notes

This event freezes a DG-2 benchmark card; it does not pass DG-2, does not modify the validity envelope, and does not alter CL-2026-005, the Sail, or any DG status. The validity envelope holds at DG-2 PARTIAL — 3 of 4 sub-claims PASS (2026-05-04). Movement to "DG-2 PARTIAL — 4 of 4 sub-claims PASS under cleared registry" (or analogous wording) is contingent on B4-conv-registry's verdict landing at PASS for all four profiles AND a sibling card for Entry 4.B.2 reaching PASS — a multi-step path.

The next admissible work step is the runner-extension verdict track: extending `cbg.cumulants.D_bar_1` to the four `DisplacementProfile.kind` cases, lifting the `_run_dynamical` coherent-displaced carve-out, registering per-fixture handlers, computing per-profile predicted shifts (closed-form / quadrature), and producing the verdict commit. None of this requires further Council deliberation under the standing operational discipline (Act 2 verdicts §Implementation forward agenda).

No Council deliberation is required for this freeze. No stewardship flag attaches beyond the standing co-author flag captured in `stewardship_flag.rationale`. No cross-read of the Letter Appendix D transcription is required for this freeze (the cards-first freeze does not depend on the transcription's POPULATED state being cross-read; the cross-read remains a procedural close-out per Act 2).

---

*Logbook entry. Immutable once committed.*

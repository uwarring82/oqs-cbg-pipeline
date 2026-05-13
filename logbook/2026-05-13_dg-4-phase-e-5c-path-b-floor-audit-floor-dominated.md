# DG-4 Phase E Track 5.C — Path B floor audit lands `floor-dominated`

**Date:** 2026-05-13
**Type:** audit-result / phase-e-routing-change
**Triggering commit:** _(self-referential; to be filled post-merge per [`logbook/README.md`](README.md) §Immutability exception 2)_

**Triggering evidence:**
- Frozen 5.C card v0.1.0: [`transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-5c-path-b-floor-audit-card_v0.1.0.md`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-5c-path-b-floor-audit-card_v0.1.0.md) (frozen at commit `bbdc237`).
- Audit driver + tests: [`benchmarks/path_b_floor_audit.py`](../benchmarks/path_b_floor_audit.py) and [`tests/test_path_b_floor_audit.py`](../tests/test_path_b_floor_audit.py) (gate-wiring commit `ced5276`; this entry's commit adds the timeout wrapper + `d_joint^2.2` recalibration).
- Audit result payload: [`benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json`](../benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json).
- Phase E pilot card v0.1.0 (the upstream record this audit serves): [`transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-pilot-card_v0.1.0.md`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-pilot-card_v0.1.0.md).
- D1 v0.1.2 baseline (the audit's reference): [`benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json`](../benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json).
- 2026-05-06 Path B σ_z zero-oracle pilot (where the σ_z floor was first characterised): [`2026-05-06_dg-4-path-b-pilot-result.md`](2026-05-06_dg-4-path-b-pilot-result.md).

## Summary

The Phase E Track 5.C audit, scoped by the frozen v0.1.0 card and executed against the D1 v0.1.2 σ_x thermal fixture, lands cause label **`floor-dominated`** per the card §4.3 ladder. The audit evaluated 9 of 10 one-axis-at-a-time configurations (the tenth, `(8, 3)`, preflight-skipped at d_joint = 13122); maximum drift against the production anchor `coefficient_ratio = 47.4227` was **24.16%** at the `(6, 3)` Hilbert-tightening witness. Three Hilbert witnesses were evaluated `((4, 4)`, `(4, 5)`, `(6, 3))`, comfortably satisfying the §5.3 minimum of one. All fit residuals remained in the 3-7 × 10⁻⁵ range, well below the 10⁻³ degraded threshold.

The dominant finding is that the three truncation knobs pull the Path B `coefficient_ratio` in **mutually inconsistent directions**: `omega_max_factor ↑` and `n_levels_per_mode ↑` both drive the ratio downward, while `n_bath_modes ↑` drives it upward by 24%. No single tightening direction recovers a stable estimate, which rules out both `truncation-converged` and `borderline` and forces the §4.4 routing consequence: **Phase E cannot be classified against Path B as the analytic-comparison reference.** The D1 v0.1.2 PASS verdict is unchanged; the envelope is not modified; Phase F remains blocked.

A second-order finding: the v0.1.0 driver's initial `d_joint³` preflight scaling proved 2.5–3× pessimistic. A direct measurement against the anchor (6.95 s) and (4, 4) (74 s) fixes the exponent at ≈ 2.07 (used as 2.2 with safety pad); the production-run commit lands this recalibration as a constant `PREFLIGHT_D_JOINT_EXPONENT = 2.2`. Without that fix, the v0.1.0 audit landed only one Hilbert witness on its first run, on `(4, 4)` only; the recalibrated re-run produced three Hilbert witnesses at the same 30-min budget.

## Detail

### Audit configuration

- Anchor: `(n_bath_modes = 4, n_levels_per_mode = 3, omega_max_factor = 30)` (centre of D1 v0.1.2 production perturbation set `{20, 30, 40}`).
- Fixture: D1 v0.1.2 baseline — `spin_boson_sigma_x` thermal Ohmic bath at `temperature = 0.5`, `cutoff_frequency = 10`, `omega = 1`, time grid `linspace(0, 20, 200)`.
- Richardson fit α grid: production `(0.01, 0.015, 0.02, 0.025, 0.03)` — one fit per truncation configuration, α-independent `coefficient_ratio` extracted.
- Per-point wall-time budget: 30 min (default); preflight skip threshold = budget × 2.0 = 60 min.
- Total audit runtime: 33.2 min wall, 9 evaluated + 1 preflight-skipped (no timeouts triggered).

### Drift table — omega_max_factor axis at `(4, 3)`

| `omega_max_factor` | `coefficient_ratio` | drift vs anchor 47.4227 |
|---:|---:|---:|
| 10 | 50.229 | +5.93% |
| 20 | 49.681 | +4.77% |
| **30 (anchor)** | **47.423** | 0 |
| 40 | 46.307 | −2.35% |
| 80 | 41.996 | −11.43% |
| 160 | 36.486 | **−23.06%** |

Monotone, no sign of stabilisation across a 16× sweep range. At `omega_max_factor = 10` and `20` the ratio sits *above* the production anchor; at 40, 80, and 160 it sits *below*. The crossover is consistent with the high-frequency tail of `J(ω)` contributing to ⟨‖L_2^dis‖⟩ faster than to ⟨‖L_4^dis‖⟩ as the cutoff grows.

### Drift table — Hilbert axes at `omega_max_factor = 30`

| config | d_joint | `coefficient_ratio` | drift vs anchor | direction |
|---|---:|---:|---:|---|
| **(4, 3) anchor** | 162 | **47.423** | 0 | — |
| (4, 4) | 512 | 42.970 | **−9.39%** | down |
| (4, 5) | 1250 | 40.971 | **−13.60%** | down (still moving; `Δ = −2.0` per Fock level) |
| **(6, 3)** | **1458** | **58.880** | **+24.16%** | **up — opposite direction to the other two axes** |
| (8, 3) | 13122 | — | — | preflight-skipped (predicted ~44 h; remains intractable under any reasonable audit budget) |

The two `n_levels_per_mode` Hilbert points (4 → 5 → ?) show a 2-unit-per-Fock-level decrease in the ratio, with no sign of stabilisation; extrapolating naively to `n_levels_per_mode = 6` would predict a ratio near 38. The single `n_bath_modes` Hilbert point at `(6, 3)` sits 24% *above* the anchor — a direction opposite to both `omega_max_factor ↑` and `n_levels_per_mode ↑`.

### Cause-label derivation under card §4.3

- **`truncation-converged`** requires max drift ≤ 5% AND ≥ 1 non-degraded Hilbert witness. Max drift is 24.16% — fails the bound by ~5×.
- **`borderline`** requires max drift > 5% **but bounded (stabilises at the tightest evaluated truncation)** AND ≥ 1 Hilbert witness. The `omega_max_factor` axis at 160 is still moving (slope −5.5/octave between 80 and 160). The `n_levels_per_mode` axis at 5 is still moving (slope −2.0/level). The `n_bath_modes` axis at 6 is a single point with no second sample on that axis to assess local stabilisation, but the +24% magnitude itself signals strong sensitivity. No axis stabilises in the evaluated window.
- **`floor-dominated`** requires max drift > 5% AND still moving at the tightest tractable truncation, Hilbert axis included. Both conditions hold: max drift is 24% and the `(6, 3)` Hilbert witness is the tightest tractable point on the `n_bath_modes` axis with a +24% shift.

The card §4.3 ladder strictly yields **`floor-dominated`**.

### Process finding — `d_joint^2.2` empirical scaling

The v0.1.0 driver's initial preflight prediction used `d_joint³` scaling, which would correspond to matrix-exponential-dominated cost (O(d³) per timestep). The actual `exact_finite_env.propagate` uses `scipy_dop853` adaptive Runge-Kutta, which is matrix-vector per step (O(d²)); the empirical exponent across the anchor (6.95 s at d_joint = 162) and `(4, 4)` (74.3 s at d_joint = 512) is ≈ 2.07. The production-run commit lands `PREFLIGHT_D_JOINT_EXPONENT = 2.2` as a slightly-padded module constant.

Impact: under the same 30-min budget × 2.0 preflight factor, the recalibrated predictor lets `(4, 5)` (predicted 896 s, actual 752 s) and `(6, 3)` (predicted 1257 s, actual 1119 s) clear the preflight threshold instead of being skipped. The cubic guess would have left only `(4, 4)` evaluated — insufficient evidence to distinguish `floor-dominated` from a less load-bearing `borderline` call. Recording this as a process lesson: when a preflight estimator drives a §5.3-style witness requirement, calibrate empirically against at least one off-anchor evaluation before issuing a cause label.

### What this changes

- **Phase E cause label**: `floor-dominated` per card v0.1.0 §4.3.
- **Phase E routing**: per card v0.1.0 §4.4 and work plan v0.1.5 §4 Phase E, the `floor-dominated` outcome means **Tracks 5.A (finer Path A grid) and 5.B (higher-order Path A quadrature) cannot close Phase E against Path B as the analytic reference** — they would converge toward a Path B value that itself is not stable. Phase E's path forward is one of:
  1. Drive Path A to convergence (5.A or 5.B) and treat the converged Path A value as the *analytic ground truth*, with Path B documented as a finite-environment approximation only — i.e. Phase E classification becomes a single-sided convergence claim, not a Path A / Path B agreement claim.
  2. Open DG-3 Tier-2.A (HEOM / TEMPO third method) and use that as Path B's reference; this is the route the 5.C card §4.4 routing matrix cites as the canonical `floor-dominated` escalation.
  3. Leave Phase E permanently as `unclassified-pilot` and accept that the D1 v0.1.2 verdict carries Path B's documented finite-env uncertainty.
- **Audit driver upgrade**: timeout wrapper + `d_joint^2.2` calibration land alongside this entry's logbook record. The `evaluate_point_with_timeout` function provides the §6 R1 hard process timeout that beats the preflight estimator; the `use_timeout` parameter on `run_audit` controls whether dispatched points run in-process (tests) or in a multiprocessing child (production).

### What this does NOT change

- **D1 v0.1.2 PASS verdict** is unchanged. The audit was an audit, not a verdict supersedure; it characterises Path B's finite-env floor at the production fixture without modifying the v0.1.2 verdict, card, or result JSON.
- **DG-4 envelope row** is not modified. Per work plan v0.1.5 §5 acceptance 6 and card v0.1.0 §4.4, the `floor-dominated` outcome routes Phase E's path forward but does not in itself trigger an envelope change.
- **CL-2026-005 v0.4 Entry 2** scope-limited qualifier is unchanged.
- **The v0.1.0 5.C card** is content-immutable post-freeze; this entry's audit *executes* the frozen card, it does not modify the card.
- **The Phase E pilot card v0.1.0** is content-immutable; the `frozen-unclassified-pilot` state stands.
- **Work plan v0.1.5** is unchanged. The §4 Phase E routing table's `inconclusive-with-cause` state does NOT apply here — that state is for the work plan's three-state classification set, and this audit explicitly declines to issue a work-plan-state classification. The `floor-dominated` label lives in the 5.C card's vocabulary, not the work plan's.

## Routing notes

- **Phase F remains blocked.** The 5.C audit does not classify the Phase E cross-validation under the work plan v0.1.5 three-state set; it identifies a fundamental issue with using Path B as the cross-validation reference at the D1 fixture. Selection between the three §4.4-routed paths above is a steward decision out of scope of this entry.
- **Tracks 5.A / 5.B remain scientifically interesting but no longer suffice for Phase E classification on their own.** Both can still proceed (Path A convergence is independently valuable), but landing them no longer closes Phase E against Path B — the steward should record this routing change when initiating either track.
- **DG-3 Tier-2.A (third reference method) gains additional motivation.** Beyond its existing role of lifting the DG-3 row from RUNNER-COMPLETE → PASS, a third method now also serves as the Path B replacement that Phase E needs. This may make Tier-2.A selection (HEOM vs TEMPO vs MCTDH vs pseudomode) a steward priority sooner than the 2026-05-11 next-tasks scoping anticipated.
- The Phase E pilot card's `frozen-unclassified-pilot` state is unchanged by this audit; the pilot card recorded the audit was needed and pinned the follow-up plan, and this entry is the recorded outcome of that follow-up.
- The 5.C card's `triggering_commit` was `bbdc237`; this entry's commit hash will become the recorded execution commit for the card.

## Permitted post-commit edits to this entry

Per [`logbook/README.md`](README.md) §"Immutability":

- `superseded by:` annotation if a successor entry is added (e.g., a `v0.1.1` audit result if the steward chooses to re-run with a tighter Hilbert grid or different fixture).
- Self-referential placeholder fill for `Triggering commit:` (this entry's introducing commit is itself the trigger; the placeholder will be replaced with the commit hash in a follow-up commit).

Any substantive text edit requires supersedure under the normal logbook discipline.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

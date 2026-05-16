# DG-3 Phase D reconnaissance — C1/C2 v0.2.0 verdict blocked: gating pair unsatisfiable (cause `finite-env-correlator-floor`)

**Date:** 2026-05-16
**Type:** experimental-result / dg-3-route-block
**Triggering commit:** _(self-referential; to be populated on commit per [`logbook/README.md`](README.md) §Immutability exception 2)_

**Triggering evidence:**
- Active cards [`C1 v0.2.0`](../benchmarks/benchmark_cards/C1_cross-method-pure-dephasing_v0.2.0.yaml), [`C2 v0.2.0`](../benchmarks/benchmark_cards/C2_cross-method-spin-boson_v0.2.0.yaml) (`frozen-awaiting-run`; `comparison.gating_pair = [exact_finite_env, heom_reference]`, threshold `1.0e-6`).
- DG-3 work plan [`v0.1.1`](../plans/dg-3-work-plan_v0.1.1.md) §4 Phase D and §§2.2–2.3; §2.3 records TEMPO (OQuPy) as the documented fallback third method.
- Phase B module [`benchmarks/heom_reference.py`](../benchmarks/heom_reference.py); finite-env reference [`benchmarks/exact_finite_env.py`](../benchmarks/exact_finite_env.py) `_build_spin_joint`; bath correlator [`cbg/bath_correlations.py`](../cbg/bath_correlations.py) `bath_two_point_thermal`.
- Predecessor DG-3 handler-wiring entries (2026-05-05): [`dg-3-c2-displaced-handler-wired`](2026-05-05_dg-3-c2-displaced-handler-wired.md) and siblings (all four baseline-pair fixtures runner-reachable; no verdict).
- Phase D.0 / D.1 diagnostic scripts were **throwaway** (not committed; resided in `/tmp`). Their numerical findings are reproduced verbatim in the Detail section below so this entry is self-contained.
- Parallel precedent: [`dg-4-phase-e-5c-path-b-floor-audit-floor-dominated`](2026-05-13_dg-4-phase-e-5c-path-b-floor-audit-floor-dominated.md) (a reference method not faithful enough at the production fixture).

## Summary

Before running C1/C2 v0.2.0 to a frozen Phase D verdict, a bounded two-stage reconnaissance (Phase D.0 convergence sweep, Phase D.1 correlator-convention audit) was performed. It established that the frozen gating pair `(exact_finite_env, heom_reference)` at threshold `1.0e-6` is **physically unsatisfiable for structural finite-bath reasons**, not because of a code, convention, or HEOM-truncation defect. Running the frozen 200-point verdict would therefore produce a misattributed clean FAIL. **No DG-3 PASS or failure-asymmetry clearance is claimed; the v0.2.0 cards are NOT mutated** (they remain valuable as the frozen artifact that exposed the bad gate); no code/card/runner change accompanies this entry — it is a checkpoint record plus minimal status-surface drift-prevention.

## Detail

### Phase D.0 — convergence sweep (C1/C2 v0.2.0, reduced grid)

Sweeping the HEOM knobs on both cards:

- `max_depth` 3 → 8: `exact|heom` flat (C1 0.2240 → 0.2242; C2 0.3303 constant).
- `cf_target_rmse` 5e-3 → 1e-4: flat.
- `n_pts_correlator` 1024 → 4096: negligible (C1 0.2242 → 0.2206; C2 0.3303 → 0.3291).

HEOM is internally converged at the default `max_depth=3`; brute-force hierarchy depth is ruled out. Sweeping `exact_finite_env`'s bath instead, the `exact|heom` gap stays pinned in the O(0.2–0.3) band and is **non-monotone / increasing** with mode count for C1 — `exact_finite_env` is the non-converged method and does not approach HEOM.

### Phase D.1 — correlator-convention audit

Reconstructed the discrete two-point correlator that `exact_finite_env` actually propagates (same log-spaced mode grid, `g_k = √(J(ω_k)·Δω_k)`, Fock-truncated per-mode thermal state) and compared it to `cbg.bath_correlations.bath_two_point_thermal` (HEOM's source) over the HEOM fit window `t ∈ [0, 3.0]` at the shared C1/C2 bath parameters (α=0.05, ω_c=10, T=0.5; the σ_z/σ_x difference is system-side and does not enter the bath correlator).

1. **cbg correlator is trustworthy.** `C_cbg` vs an independent quadrature of `∫₀^∞ J(ω)[coth(ω/2T)cos − i sin]dω`: relL2 = 5.5e-8; `C(0) = 5.038309` both ways. No normalization surprise on the cbg/HEOM side.
2. **No convention bug.** Across all mode counts the best-fit real scale `c ≈ 0.98–1.03` while the post-rescale residual stays equal to the raw relL2 (large). A constant/sign/factor mismatch would collapse the rescaled residual; it does not. The discretization convention is the *correct* Riemann sum of cbg's integral.
3. **Fock truncation negligible.** `C_disc_trunc` vs `C_disc_ideal` at the default 8-mode grid: n_levels=4 → relL2 7.9e-4; n_levels=8 → 2.5e-5 — three to four orders below the grid error. Bath-state construction is fine.
4. **The floor is `exact_finite_env` mode-discretization, non-convergent in the feasible regime.** `C_disc_ideal` vs `C_cbg` relL2: 4 modes 4.15, 8 modes 2.71, 16 modes 1.66, 32 modes 0.96, 64 modes 0.33 — convergence ≈ O(1/n_modes). Reaching the card's 1e-6 tolerance would need ~10⁶ modes; dense joint-Hilbert diagonalization caps at ~6–8 modes (4ⁿ bath dimension). At the tractable mode count the bath `exact_finite_env` feeds the dynamics is **270–415 % wrong** relative to the continuous bath HEOM solves, which fully explains the Phase D.0 O(0.2–0.3) dynamics floor upstream at the correlator level.

### Cause label and interpretation

Cause: **`finite-env-correlator-floor`** — the C1/C2 v0.2.0 gating pair is structurally unsatisfiable at the frozen threshold. Nothing is buggy: `exact_finite_env` correctly implements its declared `finite-system` failure-mode class (a coarse finite bath with a mode-density approximation of the continuum). The flaw is the v0.2.0 **card design**: gating a continuous-bath HEOM solve against a ≤8-mode finite bath at 1e-6 cannot pass. This mirrors the DG-4 Phase E Track 5.C `floor-dominated` finding (chosen reference not faithful enough at the production fixture).

### Explicit non-claims

- No DG-3 PASS. No failure-asymmetry clearance. The validity-envelope DG-3 status is unchanged in substance (still NOT CLEARED); only a blocking-cause annotation is added.
- The frozen C1/C2 v0.2.0 cards are **not** mutated. Per [`benchmarks/benchmark_cards/SCHEMA.md`](../benchmarks/benchmark_cards/SCHEMA.md) §Supersedure, any change to a frozen card is by new-version supersedure only; that will happen when v0.3.0 exists, not in this checkpoint.
- No code, card, or runner change accompanies this entry. The diagnostic scripts were throwaway and are not committed.

## Routing notes

Recommended next work item (steward-gated; **not** enacted by this entry): promote **TEMPO (OQuPy)** — the DG-3 work plan v0.1.1 §2.3 documented fallback — as HEOM's gating partner. HEOM (hierarchy-truncation class) vs TEMPO (process-tensor class) are both faithful continuous-bath solvers from non-overlapping failure-mode classes and can plausibly agree to tight tolerance. Retain `exact_finite_env` and `qutip_reference` as non-gating auxiliary trajectories, with `exact_finite_env` explicitly documented as a coarse finite-bath approximation. This requires a `C1/C2 v0.3.0` card revision (normal supersedure of the v0.2.0 cards) plus a new `benchmarks/oqupy_reference.py` module — Phase C-scale work.

Weaker alternatives recorded for completeness: post-hoc threshold loosening on v0.2.0 is barred by Sail §4 without supersedure + `failure_mode_log` and would not constitute meaningful cross-method validation; gating `qutip_reference` vs `heom_reference` (Markov vs non-Markovian) is even less able to reach 1e-6.

This is a discussion/experimental outcome, not a verdict. No Ledger or Sail change. DG-4 D1 v0.1.2 PASS unchanged; DG-4 work plan v0.1.5 unchanged. Superseded by execution when the route triggers the C1/C2 v0.3.0 + `oqupy_reference` work item.

## Permitted post-commit edits to this entry

Per [`logbook/README.md`](README.md) §Immutability:

1. `superseded by:` annotation when a successor entry is added (e.g. the C1/C2 v0.3.0 + `oqupy_reference` landing entry, or a steward decision entry selecting a different route).
2. Self-referential `Triggering commit:` placeholder fill — this entry's introducing commit is itself the trigger; the placeholder may be replaced with the commit hash in a follow-up commit whose message states `logbook: fill self-referential triggering-commit placeholder for dg-3-phase-d-recon-gating-pair-blocked`.

Any other text edit requires supersedure under the normal logbook discipline.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

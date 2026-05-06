# DG-4 Phase B.2 — K_3 wired (thermal Gaussian); K_4 deferred

**Date:** 2026-05-06
**Type:** structural
**Triggering commit:** _placeholder_
**Triggering evidence:**
- [`cbg/tcl_recursion.py`](../cbg/tcl_recursion.py): `L_n_thermal_at_time` extended with the n=3 branch (returns the zero superoperator for any system coupling under a thermal Gaussian bath); `K_n_thermal_on_grid` now accepts n=3; `K_total_thermal_on_grid` cap raised from 2 to 3; the `L_n` shim accepts n=3. n=4 raises a structured `NotImplementedError` naming the missing pieces.
- [`tests/test_tcl_recursion.py`](../tests/test_tcl_recursion.py): 6 new tests covering K_3 = 0 on A3 / A4 fixtures, the L_n_thermal_at_time n=3 zero-superop contract, the n=4 / n=5 deferral guards, the K_total N_card=3 equivalence to N_card=2, and the K_total N_card=4 deferral.
- DG-4 work plan v0.1.2 §3 Phase B.2 (partial).

## Summary

Phase B.2 of the DG-4 work plan (v0.1.2) lands the n=3 piece. For thermal Gaussian baths the analytic result is `L_3 = 0` for any system coupling — D̄_1 = D̄_3 = 0 forces every contribution at this order to vanish — and Phase B.2 wires that explicitly: `L_n_thermal_at_time(n=3, ...)` returns the zero superoperator, `K_n_thermal_on_grid(n=3, ...)` returns zeros at every grid time, and `K_total_thermal_on_grid(N_card=3, ...)` matches `N_card=2` exactly.

The n=4 piece — where the convergence-detection signal for D1 v0.1.1 actually lives — is **deferred** to a focused follow-up commit. The deferral path (`NotImplementedError`) is structured: the error message names the two physical regimes (zero for σ_z by Feynman-Vernon Gaussian-bath exactness; non-zero for σ_x via the (2,2) Wick contractions of D̄_2 mediated by the Λ_t-inversion subtraction `L_4 = ∂_t Λ_4 - L_2 ∘ Λ_2`) and points at the implementation gap.

This is **not** a verdict commit. D1 v0.1.0 remains `frozen-awaiting-run` behind the runner refusal path; D1 v0.1.1 (Phase A.bis) cannot freeze its acceptance metric until L_4 lands and the pilot check confirms the metric is well-defined.

## Detail

### What the n=3 branch does

`L_n_thermal_at_time(3, ...)` returns `lambda X: np.zeros((d, d), dtype=complex)`. The accompanying inline derivation in the code:

> The TCL recursion at order 3 is a single triple-time integral weighted by the third generalised cumulant D̄_3, plus product terms involving D̄_1 from the Λ_t-inversion bookkeeping. For a thermal Gaussian bath, D̄_3 = 0 by Gaussianity (verified to machine precision in cbg.cumulants Phase B.1, `test_D_bar_thermal_n3_all_left_*`); D̄_1 = 0 by zero-mean (Phase B.0 odd-order vanishing). Both contributions therefore vanish, and `L_3[X] = 0` identically for any system coupling A.

This is the K_n-level falsification witness Phase B.2 was designed to surface: combined with the Phase B.1 `D̄_3 = 0` witness, it confirms the entire pinned-convention chain (B.0 → B.1 → B.2 at order 3) is internally consistent.

### What the n=4 branch does

`L_n_thermal_at_time(4, ...)` raises `NotImplementedError` with a structured message:

> n=4 is the next deferred piece of Phase B.2. For thermal Gaussian baths, L_4 = 0 when [A, A_I(τ)] = 0 (A = σ_z) and is non-zero when [A, A_I(τ)] ≠ 0 (A = σ_x). Implementing the fourth-order TCL formula or the Λ_t-inversion machinery is the remaining gating piece.

The two-regime distinction matters for D1 v0.1.1:

- For A = σ_z the commutator structure degenerates and L_4 = 0 by Feynman-Vernon Gaussian-bath exactness — this is the source of the original DG-4 work plan v0.1.0's metric flaw, which v0.1.2 addresses by switching D1's model to σ_x.
- For A = σ_x the commutator structure does not degenerate; L_4 is non-zero and is the leading-order convergence-detection signal that D1 v0.1.1's `‖L_n^dissipator‖` ratio is designed to measure.

### Tests

Six new tests; one prior test reframed:

- `test_K_3_thermal_pure_dephasing_is_zero` — A3 fixture, K_3 = 0.
- `test_K_3_thermal_sigma_x_is_zero` — A4 fixture, K_3 = 0 (parity, independent of the σ_z Feynman-Vernon argument).
- `test_K_total_N_card_3_succeeds_post_phase_b2` — K_total at N_card=3 matches N_card=2 in σ_x thermal.
- `test_K_total_N_card_4_raises_pending_recursion` — N_card=4 still gated.
- `test_L_n_thermal_at_time_n_3_returns_zero_post_phase_b2` — direct check that the n=3 superop is zero on σ_x and σ_z inputs.
- `test_L_n_thermal_at_time_n_4_raises_pending_recursion`, `test_L_n_thermal_at_time_n_5_raises_out_of_scope` — deferral guards.
- `test_L_n_shim_n_3_returns_zero_post_phase_b2`, `test_L_n_shim_n_4_raises_pending_recursion` — same coverage on the shim path.

Pre-existing tests `test_K_total_N_card_3_raises_pending_recursion` and `test_L_n_shim_n_3_raises_pending_recursion` are reframed to assert the new "n=3 returns zero" contract; the deferral guard moves to n=4.

Full suite: 430 passed (was 424; +6 net new tests).

### What is NOT implemented yet

- `L_4` for thermal Gaussian. Two physical regimes (σ_z = 0; σ_x ≠ 0); see the n=4 branch's inline note for the implementation roadmap.
- All non-thermal paths at n >= 3 (coherent-displaced, etc.). Out of scope for D1 v0.1.1's chosen fixture.
- `K_total_thermal_on_grid` does not iterate over n=4 (`N_card > 3` still raises).

### What this changes for the validity envelope

DG-4 row transitions from "SCOPED — runner refusal path wired; sweep runner not yet implemented" to **"SCOPED — Phase B partial: B.0, B.1, B.2 (n=3) implemented; n=4 + sweep runner pending"**. DG status itself unchanged (still SCOPED). What is mechanically auditable now: the cumulant + TCL machinery up to order 3 is wired and convention-witnessed; the only remaining piece for D1 v0.1.1's metric to be evaluable is the n=4 implementation.

DG-2 row carries an unchanged **footnote**: the K_2-K_4 numerical-recursion milestone is **partially** unblocked by Phase B.2 (n=3 lands), and will be fully unblocked once n=4 lands.

## Routing

Three independent threads remain:

1. **Phase B.2 (n=4)** — the gating piece for D1 v0.1.1's pilot check. Substantial: requires either the explicit fourth-order TCL formula or Λ_t-inversion machinery.
2. **Phase B.4** — knob-threading for `quad_limit` / `upper_cutoff_factor`. Independent of B.2 (n=4).
3. **Phase A.bis** (D1 v0.1.1 supersedure) — depends on B.2 (n=4) plus B.3 (L_n^dissipator extraction) for the pilot check.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

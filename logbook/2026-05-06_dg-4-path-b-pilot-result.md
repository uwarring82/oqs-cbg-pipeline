# DG-4 Path B pilot — σ_x thermal `‖L_4^dis‖` is non-zero (numerical, with finite-env floor)

**Date:** 2026-05-06
**Type:** experimental-result
**Triggering commit:** aa09a32
**Triggering evidence:**
- Path B scaffold: [`benchmarks/numerical_tcl_extraction.py`](../benchmarks/numerical_tcl_extraction.py) (commit `b35ba05`).
- Auxiliary work plan: [`plans/dg-4-path-b-richardson-extraction_v0.1.0.md`](../plans/dg-4-path-b-richardson-extraction_v0.1.0.md).
- Active DG-4 work plan: [`plans/dg-4-work-plan_v0.1.4.md`](../plans/dg-4-work-plan_v0.1.4.md) §3 Phase A.bis pilot check.
- Test suite: `.venv/bin/pytest -q tests/test_numerical_tcl_extraction.py` → 8 passed.

## Summary

The DG-4 work plan v0.1.4 §3 Phase A.bis pilot check — confirm both `‖L_2^dis‖ > 0` AND `‖L_4^dis‖ > 0` in the σ_x thermal Gaussian model at the planned baseline coupling — is now **empirically alive but partial**. The L_2 piece was already confirmed by Phase B.3 (commit `b699950`, `test_L_2_dissipator_sigma_x_thermal_is_nonzero`). The L_4 piece, deferred from analytic Phase B.2 (n=4) pending the Companion-paper formula, has now been measured numerically via the Path B Richardson extraction scaffold.

**Result**: at the C1/C2 baseline coupling `α² = 0.05`, σ_x thermal gives `‖L_4^dis‖` averaged over time ≈ `6.21e-1`, ~27× above the σ_z thermal zero-oracle floor of `‖L_4^dis‖_residual ≈ 2.32e-2`. The signal is well-separated from the finite-env extraction floor, confirming that the v0.1.4 metric design is empirically valid in the chosen fixture.

**Caveat**: this is a numerical pilot result with a finite-env extraction floor of ~few × 10⁻². It is **not** equivalent to analytic Phase B.2 (n=4) completion. D1 v0.1.1 verdict commits should treat the floor as a documented uncertainty band, not as machine-precision agreement.

## Detail

### Pilot configuration

- Reference method: `benchmarks.exact_finite_env` with `n_bath_modes=4`, `n_levels_per_mode=3`.
- Time grid: `t ∈ [0, 3]`, 61 points.
- Picture: interaction-picture extraction via the zero-coupling map (Λ_t at α=0 is the bare H_S evolution, used as the reference for subtraction).
- Fit amplitudes (fit parameter is interaction *amplitude* α, with `coupling_strength = α²` in the model_spec): `α ∈ {0.01, 0.015, 0.02, 0.025, 0.03}` — 5 points spanning the small-coupling regime where the Richardson polynomial fit is well-conditioned.
- Polynomial fit: `Λ_t(α) = Λ_0 + α² Λ_2 + α⁴ Λ_4 + O(α⁶)` (even-order fit, parity-aware).
- Synthesis: `L_4 = ∂_t Λ_4 − L_2 ∘ Λ_2` per the Path B plan §3 specification, with `L_2 = ∂_t Λ_2`.

### Numerical results

**σ_x thermal (the signal case):**
- Fit relative residual: `5.16e-6` (well-conditioned; the polynomial captures Λ_t(α) to within numerical noise).
- `‖L_4^dis‖` coefficient (the α⁴ scale-free piece, units of 1/time): avg over t = `2.483e+02`, max = `7.029e+02`.
- At card baseline `coupling_strength = 0.05` (so α² = 0.05, α⁴ = 2.5e-3): contribution avg over t = `6.208e-01`, max = `1.757e+00`.
- Parity-aware ratio estimate at baseline: `r_4 = ⟨‖L_4^dis‖⟩ / ⟨‖L_2^dis‖⟩ ≈ 4.89e-01` — well below the convergence-failure threshold of 1.0. **Implication**: at the baseline coupling, the perturbative expansion is still convergent; the convergence-failure boundary `α_crit` lies at a *higher* coupling strength, exactly as D1 v0.1.1 was designed to find.

**σ_z thermal (the zero-oracle control):**
- Fit relative residual: `1.60e-6` (same fit quality as σ_x).
- `‖L_4^dis‖` residual at baseline: avg = `2.319e-02`, max not separately recorded.
- Residual ratio at baseline: `r_4_residual ≈ 2.09e-02`.

**Signal-to-floor ratio**:
- σ_x signal `6.21e-01` ÷ σ_z floor `2.32e-02` ≈ **26.8** at α² = 0.05. The σ_z analytic answer is exactly 0 (Feynman-Vernon), so the σ_z residual is the finite-env extraction floor at the chosen `(n_bath_modes, n_levels_per_mode)` truncation. The σ_x result is well above this floor by more than an order of magnitude — the metric design is empirically valid at this fixture.

### Interpretation

- **The v0.1.4 metric design (parity-aware `r_4 = ‖L_4^dis‖ / ‖L_2^dis‖`) survives the pilot.** The L_4 piece is non-zero in σ_x thermal, the L_2 piece was already confirmed non-zero in Phase B.3, and the ratio is well-defined at the baseline coupling.
- **At the baseline coupling, `r_4 ≈ 0.49` is below the convergence-failure threshold.** This means a coupling-strength sweep starting at α = 0.05 needs to extend to higher α before any candidate `convergence failure` is found. D1 v0.1.0's frozen sweep range is `0.05 → 1.0` log-uniform; this is consistent with finding `α_crit` somewhere in that range.
- **The σ_z zero-oracle finite-env floor is ~2 × 10⁻² in this configuration**, which sets a lower bound on the signal-to-noise of the Path B extraction. With `n_bath_modes=4, n_levels_per_mode=3`, the floor would shrink with larger truncation but the cost grows exponentially. For D1 v0.1.1 verdicts, the floor should be recorded in `result.notes` as an explicit uncertainty band.
- **Path A (Companion Sec. IV) remains the preferred analytic deliverable.** Path B gives a numerical signal with finite-env truncation noise; an analytic L_4 implementation (when available) would deliver machine-precision evaluation and avoid the floor entirely. Until then, the cross-validation strategy is: if Path A lands, the Path B and Path A values should agree at small α to within the Path B finite-env floor.

### What this changes

- DG-4 work plan v0.1.4 §3 Phase A.bis pilot text's conditional ("if `‖L_4^dis‖ = 0` numerically … Phase A.bis must consider a different model") is now **resolved**: σ_x thermal is the right model.
- D1 v0.1.1 supersedure (Phase A.bis) is now empirically unblocked. The σ_x model + parity-aware metric is confirmed to produce a non-zero L_4 signal at the planned coupling regime.
- Phase D admissibility is **not** changed: the analytic Phase B.2 (n=4) deferral remains; verdict commits via Path B alone would carry the finite-env floor as a documented uncertainty.

### What this does NOT change

- Plan v0.1.4 itself (no metric or scope edit needed; the pilot result fits the existing acceptance criteria framing).
- The structured n=4 deferral at [`cbg/tcl_recursion.py:156`](../cbg/tcl_recursion.py): the analytic L_4 in `cbg.tcl_recursion` remains pending. Path B is benchmark-side scaffold, not a `cbg.tcl_recursion` core API replacement.
- The DG-4 row in `docs/validity_envelope.md` status (still "SCOPED — Phase B partial").

## Status updates

- `docs/validity_envelope.md` DG-4 row narrative is updated with a one-sentence mention of this pilot result (the structural status itself is unchanged).
- This logbook entry indexed in `logbook/README.md`.

## Routing

The Path B pilot's main load-bearing result is empirical confirmation that D1 v0.1.1's metric design works. Three productive next moves:

1. **Phase A.bis (D1 v0.1.0 → v0.1.1 supersedure)** is now drafting-ready. The card can freeze the σ_x model + parity-aware r_4 metric + (`upper_cutoff_factor`, `omega_c`) reproducibility set per plan v0.1.4.
2. **Path A (Companion Sec. IV)** is still the preferred analytic deliverable. Whoever can put the Companion fourth-order expression in front of us unblocks the analytic Phase B.2 (n=4) commit; cross-validation against Path B at small α is the natural acceptance gate.
3. **Tighter Path B truncation** (e.g. `n_bath_modes=6, n_levels_per_mode=4` or higher) would shrink the finite-env floor and improve the signal-to-noise of the Path B extraction. Useful if analytic Path A is not on the immediate horizon.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

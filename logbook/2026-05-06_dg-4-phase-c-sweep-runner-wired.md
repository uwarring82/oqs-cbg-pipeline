# DG-4 Phase C — sweep runner wired (Path B numerical L_4 source)

**Date:** 2026-05-06
**Type:** structural
**Triggering commit:** 55b1064
**Triggering evidence:**
- New runner branch [`reporting/benchmark_card.py:_run_dg4_sweep`](../reporting/benchmark_card.py).
- New helper [`benchmarks/numerical_tcl_extraction.py:path_b_dissipator_norm_coefficients`](../benchmarks/numerical_tcl_extraction.py).
- New tests in [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py): seven DG-4 sweep tests covering dispatch, classification, alpha_crit interpolation, notes content, and the structural refusal paths for non-σ_x / non-thermal cards.
- DG-4 work plan v0.1.4 §3 Phase C.
- D1 v0.1.1 frozen card.
- Path B pilot result `2026-05-06_dg-4-path-b-pilot-result.md`.

## Summary

Phase C of the DG-4 work plan v0.1.4 is complete. `run_card(D1 v0.1.1)` now routes through `_run_dg4_sweep` and produces a structured `CardResult` with verdict, per-α classifications, and an interpolated `α_crit` (when a boundary exists). The runner consumes Path B (Richardson numerical extraction via `benchmarks/exact_finite_env`) as the L_4 source; the analytic Path A (Companion Sec. IV) is not yet available, and the runner notes carry the documented finite-env extraction floor as an explicit uncertainty band.

The previous `_refuse_dg4_sweep` path is retained as a structured fallback — it fires when the card's coupling operator or bath state falls outside Path B's current scope (σ_x + thermal Gaussian only). The exception class `DG4SweepRunnerNotImplementedError` continues to subclass `NotImplementedError`.

This is **not** a Phase D verdict commit. Phase D would land a populated `result:` block on D1 v0.1.1; this commit only wires the runner to the point where verdict computation is mechanically available.

## Detail

### What landed

**`benchmarks/numerical_tcl_extraction.py:path_b_dissipator_norm_coefficients`**
- One-shot Path B orchestrator: tomography → polynomial fit (with closed-system baseline) → Λ_2, Λ_4 coefficients → L_2, L_4 generators → per-t Liouville-Frobenius dissipator norm with K_n extracted via Letter Eq. (6).
- Returns a `DissipatorNormCoefficients` dataclass with `l2_per_t`, `l4_per_t`, `l2_avg`, `l4_avg`, and `fit_relative_residual`.
- The "coefficients" are α-independent (Taylor coefficients of the perturbative expansion); the runner scales them per-α via `r_4(α²) = α² · (l4_avg / l2_avg)`.
- Added `_liouville_dissipator_frobenius_norms` private helper that builds the d²×d² Liouville matrix of `L_n + i [K_n, ·]` per the v0.1.4 sign convention and takes the Frobenius norm.

**`reporting/benchmark_card.py:_run_dg4_sweep`**
- Validates the card carries a `frozen_parameters.sweep` block, σ_x coupling, thermal bath state. Non-σ_x / non-thermal cards raise `DG4SweepRunnerNotImplementedError` with structured messages.
- Reads optional Path B overrides from `frozen_parameters.numerical.path_b` (alpha_values, n_bath_modes, n_levels_per_mode); defaults match the production pilot configuration.
- Runs **one** Path B fit at the baseline model spec — sufficient for the entire α-sweep because L_n are α-independent coefficients.
- Iterates the swept α² grid (via `_build_dg4_sweep_grid`, supporting `log_uniform` and `uniform` schemes per SCHEMA.md v0.1.3 Rule 17) and computes `r_4(α²)` for each.
- For each α with `r_4 > 1` (failing-candidate), runs **four** additional Path B fits at the perturbed configurations (`upper_cutoff_factor ∈ {20, 40}` via the runner-side allow-list; `omega_c ∈ {9, 11}` via direct model-spec mutation at `bath_spectral_density.cutoff_frequency`). Total Path B work: 1 (baseline) + 0 or 4 (only if any failing-candidate exists).
- Classifies each α as `passing`, `convergence_failure` (r_4 > 1 stable under all four perturbations), `truncation_artefact` (r_4 > 1 unstable under at least one), or `metric-undefined` (zero-denominator).
- Interpolates `α_crit` linearly in `log(α²)` between the last passing α and the first convergence-failure α.
- Verdict logic per DG-4 work plan v0.1.4 §4:
  - **PASS** iff at least one α is `convergence_failure`.
  - **CONDITIONAL** iff at least one α is failing-candidate but all reclassify to `truncation_artefact`.
  - **FAIL** iff no α gives r_4 > 1 baseline (cause: `no-failure-found-in-frozen-range`; per Risk #8, response is supersedure D2 with extended range).
- Returns a `CardResult` with a single `TestCaseResult` named `dg4_failure_envelope_sweep`, plus `result.notes` containing baseline coefficients, fit residual, per-α classifications, α_crit (when defined), and the explicit Path-B-floor caveat.

**Dispatch update**: `run_card` now calls `_run_dg4_sweep(card)` for `dg_target == "DG-4"` cards (was: raised `_refuse_dg4_sweep`).

### What is NOT changed

- `cbg.tcl_recursion` analytic L_4 path — still raises the structured n=4 deferral with three routing paths recorded at [`cbg/tcl_recursion.py:156`](../cbg/tcl_recursion.py). Path B is benchmark-side scaffold and the runner consumes it directly; the cbg core remains pure of benchmarks dependencies.
- `_refuse_dg4_sweep` helper and `DG4SweepRunnerNotImplementedError` exception — retained as fallbacks for non-σ_x / non-thermal / non-sweep cards. They fire from inside `_run_dg4_sweep` when the card spec falls outside the current scope.
- D1 v0.1.1 result block — the card remains `frozen-awaiting-run`. Phase D would populate the verdict in a separate commit.

### Empirical readout (reduced fixture, smoke test)

Reduced D1 v0.1.1 (4-point sweep, `alpha_values=(0.01, 0.02, 0.03)`, `n_bath_modes=2`, `n_levels_per_mode=2`, `t ∈ [0, 1]`, 11 grid points):

| Quantity | Value |
|---|---|
| Runtime | ~40 ms |
| Baseline fit relative residual | 2.03e-7 |
| Baseline `‖L_2^dis‖_avg` | 9.72e+00 |
| Baseline `‖L_4^dis‖_avg` | 6.15e+01 |
| Coefficient ratio L_4/L_2 | 6.32 |
| Per-α classifications | passing=2, convergence_failure=2 |
| Interpolated α_crit | 1.49e-1 |
| Verdict | PASS |

The reduced-fixture coefficient ratio (~6.3) is lower than the pilot's full-fixture ratio (~9.8); the difference is the n_bath_modes=2 vs 4 truncation. The classification structure is sound.

### Production-fixture cost estimate

At full pilot resolution (D1 v0.1.1 frozen defaults: 20-point sweep, `alpha_values=(0.01, 0.015, 0.02, 0.025, 0.03)`, n_bath_modes=4, n_levels_per_mode=3, t ∈ [0, 20], 200 grid points), each Path B fit takes ~30 s. Worst-case (any failing candidate triggers all 4 reproducibility re-runs) total: 5 × 30 s = 150 s ≈ 2.5 min. Tractable for Phase D verdict commits.

### Tests (7 new, 2 reframed)

- `test_run_card_d1_runs_dg4_sweep_to_verdict` (replaces `..._raises_dg4_sweep_error`) — positive smoke: runner returns a CardResult with one of {PASS, FAIL, CONDITIONAL}.
- `test_run_card_d1_dispatches_to_dg4_runner_not_dynamical` (replaces `..._refusal_takes_precedence_over_dynamical_dispatch`) — verifies DG-4 dispatch fires before the dynamical handler (D1 has no test_cases; KeyError would prove dispatch broken).
- `test_run_card_d1_notes_record_path_b_floor_caveat` — verdict notes explicitly call out the Path B finite-env uncertainty.
- `test_run_card_d1_alpha_crit_interpolation_when_boundary_present` — when verdict is PASS, notes contain an `alpha_crit` entry.
- `test_dg4_sweep_runner_refuses_non_sigma_x_with_clear_error` — Path B scope guard for σ_y / σ_z couplings.
- `test_dg4_sweep_runner_refuses_non_thermal_with_clear_error` — Path B scope guard for coherent-displaced bath.
- (Existing `test_dg4_sweep_runner_error_subclasses_not_implemented` retained.)

Verified:
- Targeted DG-4 sweep slice: 7 passed.
- Full suite: 461 passed under .venv (Python 3.13). 0 failures.

## What this changes for the validity envelope

DG-4 row narrative: D1 v0.1.1 is now structurally runnable; Phase C is complete. The DG status itself remains SCOPED (no PASS verdict). Phase D admissibility now depends on the L_4 source quality — Path B is operational with documented finite-env floor; analytic Path A would deliver machine-precision evaluation and is the preferred path for a clean verdict commit.

## Routing

Three productive next moves:

1. **Phase D pilot run** — execute `run_card(D1 v0.1.1)` at full resolution (no fixture overrides) and record the verdict in a Phase D commit. The verdict carries the Path B finite-env floor as a documented uncertainty band.
2. **Path A landing** — transcribe the Companion Sec. IV fourth-order TCL expression and add `cbg.tcl_recursion.L_n_thermal_at_time(n=4)`. Cross-validate against Path B at small α; once they agree, switch the runner to consume cbg analytic by default.
3. **Stop here** — Phase C is structurally complete. D1 v0.1.1 is runnable; verdict is a separate decision.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

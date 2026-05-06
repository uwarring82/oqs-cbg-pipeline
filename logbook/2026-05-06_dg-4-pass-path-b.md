# DG-4 PASS — Path B numerical failure-envelope verdict

**Date:** 2026-05-06
**Type:** dg-pass
**Triggering commit:** d7ca897fbf5a3594400675061b7926b84c9552af
**Triggering evidence:**
- Card [D1 v0.1.1](../benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.1.yaml).
- Result artefact [D1_failure-envelope-convergence_v0.1.1_result.json](../benchmarks/results/D1_failure-envelope-convergence_v0.1.1_result.json).
- Decision-gate summary [DG-4_summary.json](../benchmarks/results/DG-4_summary.json).
- DG-4 work plan [v0.1.4](../plans/dg-4-work-plan_v0.1.4.md) §4 verdict logic.
- Phase C runner [`reporting.benchmark_card._run_dg4_sweep`](../reporting/benchmark_card.py).

## Summary

DG-4 is marked PASS on a Path B numerical verdict. A full frozen run of `run_card(D1 v0.1.1)` identified a cause-labelled `convergence_failure` regime in the σ_x thermal fixture: all 20 frozen `coupling_strength` sweep points from 0.05 to 1.0 classified as `convergence_failure` under the parity-aware `r_4 = <‖L_4^dis‖>_t / <‖L_2^dis‖>_t` metric. The Path B route verifies stability under the operational `omega_c` model-spec perturbations; the runner-threaded `upper_cutoff_factor` perturbations are recorded as a Path-B-specific limitation because `exact_finite_env` does not consume that knob.

## Detail

The Phase D run used the benchmark-side Path B numerical Richardson extraction for the L_4 source. It ran from `2026-05-06T19:44:36+00:00` to `2026-05-06T19:45:12+00:00` at runner version `0.1.0`.

Baseline Path B readout:

| Quantity | Value |
|---|---:|
| Fit relative residual | `4.744e-05` |
| `<‖L_2^dis‖>_t` | `4.218e+01` |
| `<‖L_4^dis‖>_t` | `1.962e+03` |
| Coefficient ratio | `4.651e+01` |
| Maximum baseline `r_4` | `4.651260562533e+01` |

The PASS condition is the DG-4 asymmetry: DG-4 passes by finding at least one reproducible, cause-labelled failure regime. Here every swept point classifies as `convergence_failure`, so there is no interpolated `alpha_crit` inside the frozen range. The boundary is below the first swept value, `coupling_strength = 0.05`, under this Path B run.

Reproducibility caveat specific to Path B: `omega_c` perturbations are operational because they mutate `model.bath_spectral_density.cutoff_frequency` before the exact finite-environment build. `upper_cutoff_factor` perturbations are threaded by `_run_dg4_sweep` through the quadrature path, but the current `exact_finite_env` Path B extraction does not consume continuum quadrature controls. The verdict therefore carries the upper-cutoff check as a recorded limitation until analytic Path A or a quadrature-consuming extraction path lands.

This verdict does not claim analytic order-4 recursion completion. `cbg.tcl_recursion.L_n_thermal_at_time(n=4)` remains intentionally deferred behind the structured Path A/B/C wall. The D1 verdict is therefore a numerical-L_4 failure-envelope result carrying the documented Path B finite-env extraction floor from the 2026-05-06 σ_z thermal zero-oracle pilot. Analytic Path A (Companion Sec. IV closed form) remains preferred for machine-precision L_4 evaluation and future cross-validation.

## Routing notes

The validity envelope is updated to record DG-4 PASS with the Path B numerical caveat. CL-2026-005 v0.4 Entry 2 remains scope-limited for analytic recursion, but the open convergence question now has a repository-local failure-envelope witness: the σ_x thermal D1 sweep identifies convergence breakdown rather than supporting arbitrary-range convergence.

The D1 card's `result.commit_hash` remains empty in the verdict commit per `SCHEMA.md` §Card lifecycle; a follow-up self-referential commit should fill it with this verdict commit's hash. A repository tag bump may follow the same release discipline used for prior Decision Gate passes.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

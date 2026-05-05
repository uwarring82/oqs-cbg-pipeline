# DG-3 Phase C runner wired — partial implementation, no verdict

**Date:** 2026-05-05
**Type:** structural
**Triggering commit:** 8b66dcb6d025cd8df291a896c6f8740743cce498
**Triggering evidence:**
- [`reporting/benchmark_card.py`](../reporting/benchmark_card.py): DG-3 `_run_cross_method` branch and `_CROSS_METHOD_TEST_CASE_HANDLERS` registry added.
- [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py): C1/C2 load, handler-registration, C1 thermal clean-FAIL, deferred-handler, and trajectory-shape tests added.
- [`benchmarks/exact_finite_env.py`](../benchmarks/exact_finite_env.py) and [`benchmarks/qutip_reference.py`](../benchmarks/qutip_reference.py): Phase B reference methods consumed by the C1 thermal runner path.
- `pytest` under `.venv/bin/python` 3.13.7: 368 passed, 1 QuTiP optional-matplotlib warning.
- Frozen C1 thermal single-case run: `inter_method_relative_frobenius = 0.548376892921` against threshold `1.0e-6`, therefore FAIL.

## Summary

Phase C of the DG-3 work plan is partially complete. The benchmark-card runner now has a dedicated DG-3 cross-method branch that compares reduced-density-matrix trajectories from `exact_finite_env` and `qutip_reference`. The implemented scope is deliberately narrow: C1 `pure_dephasing` with `thermal_bath_cross_method` runs both methods cleanly and returns a FAIL verdict at the frozen threshold. That FAIL is informative, not a runner failure: the finite-bath reference shows recurrence structure while the QuTiP reference is Markovian.

This is not a DG-3 verdict entry. Full C1 and C2 verdict blocks are not admissible yet because C1's displaced fixture and both C2 fixtures still route to explicit deferred handlers.

## Detail

### What changed

- `run_card` now routes `dg_target: DG-3` cards into `_run_cross_method` before the legacy algebraic/dynamical dispatch.
- `_run_cross_method` builds the frozen time grid, merges each test case's `bath_state` into the model spec, validates both returned trajectories, and computes the card-defined `inter_method_relative_frobenius` metric.
- `_CROSS_METHOD_TEST_CASE_HANDLERS` records every frozen C1/C2 test-case key explicitly. Only `(pure_dephasing, thermal_bath_cross_method)` is implemented. The deferred entries raise `NotImplementedError` with a pointer to the next handler to implement.
- The existing TCL structural runner for A3/A4/B4/B5 is unchanged.

### Phase D reachability check

Running the full frozen cards at this state gives:

| Card | Current result |
|---|---|
| C1 v0.1.0 | Runs the thermal case, then raises `NotImplementedError` at `displaced_bath_delta_omega_c_cross_method`. |
| C2 v0.1.0 | Raises `NotImplementedError` at `thermal_bath_cross_method`. |

Therefore no C1/C2 `result:` blocks are populated in this commit, and the DG-3 row remains below PASS.

### Status update

The validity envelope and benchmark protocol now record the more precise state:

- DG-3 is no longer merely "scoped awaiting implementation".
- DG-3 is **partial implementation**: C1 thermal is implemented and runner-wired; full frozen-card coverage is incomplete.
- No implementation-ready PASS and no failure-asymmetry-cleared PASS are claimed.

## Routing notes

Next admissible DG-3 implementation work is to complete the deferred handlers in cards-first order:

1. C1 `displaced_bath_delta_omega_c_cross_method`.
2. C2 `thermal_bath_cross_method`.
3. C2 `displaced_bath_delta_omega_c_cross_method`.

Only after full C1 and C2 run to `CardResult` objects should Phase D populate card result blocks and update the validity envelope to a verdict state.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

# DG-4 Phase B.0 — thermal Gaussian n_point_ordered, n in {3, 4}

**Date:** 2026-05-06
**Type:** structural
**Triggering commit:** a2e7380 (initial implementation) + 33eeeb5 (Hermiticity-reflection witness)
**Triggering evidence:**
- [`cbg/bath_correlations.py`](../cbg/bath_correlations.py) `n_point_ordered`: thermal Gaussian Wick-factorisation path replacing the prior `NotImplementedError` stub.
- [`tests/test_bath_correlations.py`](../tests/test_bath_correlations.py): 7 new B.0 tests across the two commits.
- DG-4 work plan v0.1.2 §3 Phase B.0.

## Summary

Phase B.0 of the DG-4 work plan (v0.1.2) is complete. The leaf module — raw ordered n-point bath correlations for thermal Gaussian baths at total order n in {3, 4} — replaces the longstanding NotImplementedError stub. Implementation is by Wick factorisation against the existing connected two-point correlator, so n=3 returns zero (zero-mean Gaussian odd-order), and n=4 returns the sum over the three pair partitions of `two_point` evaluations.

The flattening convention `times = tau_args + tuple(reversed(s_args))` is pinned at this commit and is the operator-order interface the higher-order TCL recursion (B.1, B.2) consumes.

## Detail

### What landed in commit `a2e7380` — initial B.0

- `n_point_ordered(tau_args, s_args, bath_state, B_op=None, *, spectral_density)` replaces the prior stub.
- Scope:
  - Bath state: `family == "thermal"` only; coherent-displaced and other states route to `NotImplementedError` with a deferral message.
  - Total order: `n in {3, 4}` only; orders outside this set route to `NotImplementedError`.
  - Spectral density: required keyword; consumed via the existing `two_point` path.
  - Explicit `B_op` finite-bath traces: not implemented; pass `None` (only the Wick spectral-density path is in scope).
- Implementation:
  - For odd `n_total`, return `0+0j` (zero-mean Gaussian odd-order).
  - For `n_total == 4`, sum over the three pair partitions returned by a private `_wick_pairings` helper; each pairing's term is the product of two_point() values at the paired times.
- Convention witnesses (commit `a2e7380`):
  - `test_n_point_ordered_thermal_n3_vanishes`: odd-order zero.
  - `test_n_point_ordered_thermal_n4_wick_all_left`: matches the explicit three-pairing sum at all-left times.
  - `test_n_point_ordered_thermal_n4_mixed_left_right_ordering`: mixed (τ, s) flattens to the same value as the equivalent all-left ordering, confirming `tau_args + reversed(s_args)`.
  - Plus four scope-guard tests.

### What landed in commit `33eeeb5` — Hermiticity reflection

- `test_n_point_ordered_thermal_n4_hermitian_reflection`: for Hermitian B, `D(t_1, ..., t_4)* = D(t_4, ..., t_1)`. Independent of any future recursion; verifies the convention at the leaf layer alone.

### Convention witness coverage at end of B.0

Three witnesses on the pinned `tau_args + reversed(s_args)` convention:

| Witness | Layer | Check |
|---|---|---|
| All-left Wick sum | B.0 | n=4 raw matches the explicit three-pairing two-point sum |
| Mixed L/R consistency | B.0 | n=4 mixed equals same-times all-left |
| Hermiticity reflection | B.0 | `D(t_1..t_4)* = D(t_4..t_1)` |

The strongest convention witness — `D̄_3 = D̄_4 = 0` for Gaussian thermal once the recursion is wired — was reserved for B.1.

## Status updates

- DG-4 row in `docs/validity_envelope.md`: progress recorded in the consolidated B.2 envelope update (logbook entry `2026-05-06_dg-4-phase-b2-tcl-order-3.md`).
- No card-level changes; D1 v0.1.0 remains `frozen-awaiting-run` behind the runner refusal path.

## Routing

Phase B.0 unblocks Phase B.1's leaf inputs at orders 3 and 4. B.1 lands separately (logbook entry `2026-05-06_dg-4-phase-b1-cumulant-recursion.md`); B.0 has no further work pending.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholders above were populated at the original commit time. CC-BY-4.0 (see ../LICENSE-docs).*

# DG-4 Phase B.1 — D̄ mixed L/R + thermal Gaussian n in {3, 4}

**Date:** 2026-05-06
**Type:** structural
**Triggering commit:** edae5cf
**Triggering evidence:**
- [`cbg/cumulants.py`](../cbg/cumulants.py) `D_bar`: extended dispatch with mixed-left/right n=2 and thermal Gaussian n in {3, 4} via set-partition / Möbius-inversion closed form.
- [`tests/test_cumulants.py`](../tests/test_cumulants.py): 4 new B.1 tests including the `D̄_3 = 0` and `D̄_4 = 0` falsification witnesses.
- DG-4 work plan v0.1.2 §3 Phase B.1.

## Summary

Phase B.1 of the DG-4 work plan (v0.1.2) is complete. The generic `D_bar` dispatch now consumes B.0's flattened operator order for total order n in {3, 4} on thermal Gaussian baths, plus the previously-rejected mixed-left/right n=2 path. The strongest convention witness — `D̄_3 = D̄_4 = 0` to machine precision for thermal Gaussian — fires.

Implementation is by the **set-partition / Möbius-inversion closed form**:

    D̄(t_1, ..., t_n) = Σ_π (-1)^{|π| - 1} (|π| - 1)! · ∏_{B ∈ π} m(B)

where `m(B)` is the raw ordered moment of the block. This is mathematically equivalent to Letter Eq. (17) / Companion Eq. (27)'s recursive subtraction `D̄_n = D_n - Σ D̄_l ⊗ D̄_{n-l}` (Möbius inversion is the closed-form solution of that recursion); the closed form avoids double-bookkeeping of partial cumulants the recursion would otherwise build along the way.

## Detail

### Block evaluation

- `len(B) = 1`: forwards to `D_bar_1` (zero for thermal Gaussian).
- `len(B) = 2`: forwards to `cbg.bath_correlations.two_point`.
- `len(B) in {3, 4}`: forwards to `cbg.bath_correlations.n_point_ordered` (Phase B.0).

### Helpers added

- `_flatten_mixed_order(tau_args, s_args)` — pins the convention in one place and is the canonical entry to B.0's flattening.
- `_D_bar_scalar_from_flat_times` — scalar dispatch over n in {1, 2, 3, 4}; routes n=1 / n=2 to the existing array helpers and n in {3, 4} to the joint-cumulant computation.
- `_joint_cumulant_from_raw_moments` — the set-partition sum.
- `_raw_ordered_moment` — dispatches block size to the right leaf module.
- `_set_partitions` — small recursive generator over set partitions.

### Scope guards (preserved)

- `n=0` raises `ValueError`.
- `n=1` mixed/right-only path raises (caller should use `D_bar_1`).
- `spectral_density` required for `n >= 2`.
- `bath_state` required.
- `n in {3, 4}` requires `bath_state.family == "thermal"`.
- `n > 4` raises `NotImplementedError` naming Phase B.1's scope.

### Falsification tests (all passing)

- `test_D_bar_thermal_n3_all_left_vanishes_by_gaussianity`: `D̄_3 = 0` to machine precision. The strongest convention witness — any flattening sign/order bug in B.0 would surface as a non-zero residual here. It does not.
- `test_D_bar_thermal_n4_all_left_vanishes_by_gaussianity`: same, n=4.
- `test_D_bar_thermal_n4_mixed_left_right_vanishes_by_gaussianity`: same, n=4 with non-empty `s_args`.

### New leaf coverage

- `test_D_bar_mixed_n2_thermal_matches_pairwise_correlator`: confirms the previously-rejected mixed n=2 path now gives the expected `⟨B(τ) B(s)⟩` value (with τ in the left position and s in the right, per `tau_args + reversed(s_args)` at n=2).
- Scope-guard rejections for n > 4 and non-thermal n >= 3.

### Convention status

Phase B.1's `D̄_3 = D̄_4 = 0` witnesses join Phase B.0's three witnesses to give end-to-end confirmation that the pinned `tau_args + reversed(s_args)` convention is internally consistent through the recursion. The cumulant machinery is ready for Phase B.2's K_n consumer.

## Status updates

- DG-4 row in `docs/validity_envelope.md`: consolidated update lands with the Phase B.2 logbook entry.

## Routing

Phase B.1 unblocks Phase B.2 (K_3, K_4 wiring through `K_n_thermal_on_grid`). B.2 lands separately (logbook entry `2026-05-06_dg-4-phase-b2-tcl-order-3.md`); B.1 has no further work pending.

---

*Logbook entry. Immutable once committed. CC-BY-4.0 (see ../LICENSE-docs).*

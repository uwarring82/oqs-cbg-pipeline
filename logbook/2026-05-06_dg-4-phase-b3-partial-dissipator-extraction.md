# DG-4 Phase B.3 partial — L_n^dissipator extraction for n ∈ {0, 1, 2, 3}

**Date:** 2026-05-06
**Type:** structural
**Triggering commit:** _placeholder_
**Triggering evidence:**
- [`cbg/tcl_recursion.py`](../cbg/tcl_recursion.py): two new public functions — `L_n_dissipator_thermal_at_time` (callable form) and `L_n_dissipator_norm_thermal_on_grid` (per-t HS norm). Inline derivation block documents the convention `L_n^dissipator(t) := L_n(t) + i [K_n(t), · ]` with the explicit unitary-recovery oracle.
- [`tests/test_tcl_recursion.py`](../tests/test_tcl_recursion.py): 8 new B.3 tests covering the unitary-recovery oracle, A3/A4 fixture behaviour, n=4 deferral propagation, Phase B.4 knob-threading consistency, and at_time/on_grid round-trip.
- DG-4 work plan v0.1.3 §3 Phase B.3.

## Summary

Phase B.3 of the DG-4 work plan (v0.1.3) is **partial**: the L_n^dissipator extraction is wired for n ∈ {0, 1, 2, 3}, satisfying the Risk R8 unitary-recovery oracle to machine precision. n = 4 is gated by L_n_thermal_at_time(n=4) and propagates the same three-route deferral.

The convention adopted (matching cbg.effective_hamiltonian's `L[X] = -i[K, X] + dissipator`):

    L_n^dissipator(t) := L_n(t) + i [K_n(t), · ]

For a purely unitary L_n with K_n = H, the dissipator residual `L_n + i[K_n, ·] = -i[H,·] + i[H,·] = 0` exactly. This is the strong correctness gate Risk R8 of the work plan named: any sign error in the dissipator extraction would produce `2 × Hamiltonian-part` rather than vanish, and would be caught at the n=0 oracle test.

## Detail

### What landed

- `L_n_dissipator_thermal_at_time(n, t_idx, t_grid, H_S, A, *, bath_state, spectral_density, basis=None, upper_cutoff_factor=30.0, quad_limit=200, K_n_array=None, D_bar_2_array=None) -> Callable[[X], X]`. Returns a closure that applies the dissipator superop at a single grid time. Optional precomputed `K_n_array` and `D_bar_2_array` kwargs let callers amortise the K_n / D̄_2 cost when iterating across many t_idx values.
- `L_n_dissipator_norm_thermal_on_grid(n, t_grid, ..., upper_cutoff_factor, quad_limit) -> ndarray(n_t,)`. Precomputes K_n once across the grid, then per-t builds the d²×d² Liouville matrix in the matrix-unit basis and returns its Frobenius (= HS) norm. This is the per-t scalar D1 v0.1.1's convergence-ratio metric `r_n = ⟨‖L_n^dissipator‖⟩_t / ⟨‖L_{n−1}^dissipator‖⟩_t` consumes.
- Phase B.4 knob-threading propagates: both new functions accept `upper_cutoff_factor` and `quad_limit` and forward them into `K_n_thermal_on_grid` and `D_bar_2`.

### Empirical confirmation across all four orders

Smoke-tested at `(α=0.05, ω_c=10, T=0.5, t ∈ [0, 5])`:

| n | model | ‖L_n^dissipator‖ (max over grid) | expected |
|---|---|---|---|
| 0 | σ_z | `0.000e+00` | exactly 0 (unitary-recovery oracle) |
| 1 | σ_x | `0.000e+00` | exactly 0 (L_1 = 0 + K_1 = 0 thermal) |
| 2 | σ_z | `6.923e+00` | non-zero (pure dephasing dissipator dominates; K_2 = 0 by parity) |
| 2 | σ_x | `6.948e+00` | non-zero (energy relaxation + dephasing; K_2 ∝ σ_z subtracted) |
| 3 | σ_x | `0.000e+00` | exactly 0 (L_3 = 0 + K_3 = 0 thermal) |

The n=0 row is the strong falsification: any sign error in the dissipator-extraction convention (e.g. v0.1.1's `L_n - i[K_n,·]`) would produce `2 × ‖H_S‖_HS = 2.0` here instead of 0. The exact zero confirms the convention `L_n + i[K_n,·]` is correct as adopted by plan v0.1.3.

### Tests (8 new)

- `test_L_0_dissipator_unitary_recovery_oracle` — Risk R8 falsification gate; ‖L_0^dissipator‖ = 0 to machine precision.
- `test_L_1_dissipator_thermal_is_zero`, `test_L_3_dissipator_thermal_is_zero` — both pieces zero ⇒ dissipator zero.
- `test_L_2_dissipator_pure_dephasing_thermal_is_nonzero` — A3 fixture: `‖L_2^dis‖[0] = 0` (zero-length integral) and `‖L_2^dis‖[-1] > 1e-2`.
- `test_L_2_dissipator_sigma_x_thermal_is_nonzero` — A4 fixture: same.
- `test_L_n_dissipator_n_4_raises_pending` — n=4 deferral propagation.
- `test_L_n_dissipator_threads_quadrature_kwargs` — Phase B.4 knob-threading.
- `test_L_n_dissipator_at_time_returns_callable_matching_norm` — at_time / on_grid round-trip consistency.

### What is NOT implemented yet

- L_n^dissipator at n = 4. Gated by L_n_thermal_at_time(n=4); see the source-side falsification note at [`cbg/tcl_recursion.py:156`](../cbg/tcl_recursion.py) for the three routing paths (Companion Sec. IV / numerical Λ_t Richardson extraction / HEOM).
- Coherent-displaced bath path. The thermal path is sufficient for D1 v0.1.1's planned σ_x + thermal fixture; a displaced extension would track the existing K_total_displaced_on_grid pattern but is out of scope for this plan revision.

### What this changes for D1 v0.1.1 readiness

Phase B.3 (n ∈ {0, 1, 2, 3}) is sufficient to support the **denominator** of D1 v0.1.1's convergence ratio at order n_card ∈ {1, 2, 3} (each of which is zero or well-behaved). The **numerator** at n = 4 — the actual convergence-detection signal — still requires the L_n_thermal_at_time(n=4) follow-up. The Phase A.bis pilot check (confirming `‖L_3^dissipator‖ > 0` numerically in the σ_x model) is therefore not yet runnable: B.3 gives `‖L_3^dissipator‖ = 0` thermal Gaussian by construction (Phase B.2 result). The pilot check needs n = 4: confirming `‖L_4^dissipator‖ > 0` for σ_x thermal, which is the non-trivial Bloch-Redfield-correction signal.

So Phase A.bis is still gated on the L_4 path. Phase B.3 partial is useful infrastructure but not by itself unblocking.

## Routing

Two independent threads remain:

1. **L_n_thermal_at_time(n=4)** — the gating piece. Three routing paths recorded at [`cbg/tcl_recursion.py:156`](../cbg/tcl_recursion.py) and DG-4 work plan v0.1.3 §3 Phase B.2: Path A (Companion Sec. IV closed-form), Path B (numerical Λ_t Richardson extraction via benchmarks/exact_finite_env, kept behind a named extraction module), Path C (HEOM/TEMPO/pseudomode in its own work plan). Phase B.3 (n=4) follows automatically from any of the three.
2. **Phase A.bis (D1 v0.1.0 → v0.1.1 supersedure)** — depends on the L_4 path being chosen and the pilot check being runnable.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

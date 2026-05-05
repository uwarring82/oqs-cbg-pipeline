# DG-3 C2 thermal handler wired — full C1 + C2 thermal reachable

**Date:** 2026-05-05
**Type:** structural
**Triggering commit:** 45489d7
**Triggering evidence:**
- [`benchmarks/exact_finite_env.py`](../benchmarks/exact_finite_env.py): `build_spin_boson_sigma_x_thermal_total` builder (parallel to the pure-dephasing thermal builder, σ_x in the joint interaction).
- [`benchmarks/qutip_reference.py`](../benchmarks/qutip_reference.py): `_propagate_spin_boson_sigma_x_thermal` handler with σ_-/σ_+ secular Lindblad and rates `S(±ω_S)` numerically integrated from `cbg.bath_correlations.bath_two_point_thermal`.
- [`reporting/benchmark_card.py`](../reporting/benchmark_card.py): `_cross_handler_spin_boson_sigma_x_thermal` registered in `_CROSS_METHOD_TEST_CASE_HANDLERS`, replacing the previous deferred entry.
- [`tests/test_exact_finite_env.py`](../tests/test_exact_finite_env.py), [`tests/test_qutip_reference.py`](../tests/test_qutip_reference.py), [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py): 12 net new tests covering the σ_x builder, the σ_x QuTiP handler (incl. detailed-balance approach to Boltzmann), and the runner end-to-end.
- `pytest` under `.venv/bin/python` 3.13.7: 395 passed.
- Frozen C2 thermal single-case run: `inter_method_relative_frobenius ≈ 0.538 > 1.0e-6`, therefore clean FAIL.

## Summary

The next deferred handler in cards-first order is now implemented: C2 `thermal_bath_cross_method` (the σ_x-coupling thermal-bath fixture). Three of the four C1+C2 fixtures now run end-to-end through `_run_cross_method`. The only remaining deferred handler is C2 `displaced_bath_delta_omega_c_cross_method`, which couples the σ_x energy-relaxation channel to a coherently-displaced bath; it remains the single gate before full Phase D reachability of the frozen C1+C2 cards.

This is **not** a verdict commit. The C2 thermal FAIL (`error ≈ 0.538`) is qualitatively larger than the C1 thermal FAIL (`≈ 0.293`) because the σ_x case probes the bath spectrum at the system Bohr frequency ±ω_S = ±1, where the discrete finite-bath truncation has a stronger effect than the σ_z case's S(0) channel. As before, the FAIL is structural Markov-vs-exact mismatch, consistent with the cross-method test working as designed but not yet failure-asymmetry-cleared.

## Detail

### exact_finite_env: parallel builder for σ_x

`build_spin_boson_sigma_x_thermal_total` mirrors `build_pure_dephasing_thermal_total` in every respect except the joint interaction:

    H_int = σ_x ⊗ Σ_k g_k (a_k + a_k†)

The bath discretisation, thermal initial state, Hilbert-space layout, and partial-trace convention are identical. Because `[H_S, σ_x] ≠ 0`, the system experiences both energy relaxation toward Boltzmann equilibrium AND coherence loss — unlike the σ_z (pure-dephasing) case where σ_z populations are conserved. A `# Refactor opportunity` comment on the new builder marks the obvious factoring of `_build_spin_thermal_joint(coupling_op_array, ...)` for a future commit; the duplication is kept to minimise this commit's diff and risk.

### qutip_reference: σ_-/σ_+ secular Lindblad

Under the secular master equation, σ_x decomposes into spectral components `A_{+ω_S} = σ_-` (lowers energy by ω_S) and `A_{-ω_S} = σ_+` (raises energy). The corresponding Lindblad coefficients are the bath spectrum at ±ω_S:

    γ_- = S(+ω_S)     (downward; c_- = √γ_- σ_-)
    γ_+ = S(-ω_S)     (upward;  c_+ = √γ_+ σ_+)

Both rates are computed numerically by Simpson integration of `cbg.bath_correlations.bath_two_point_thermal`:

    S(ω) = 2 Re[∫_0^∞ C(t) e^{iωt} dt]
         = 2 ∫_0^∞ (Re[C(t)] cos(ωt) - Im[C(t)] sin(ωt)) dt

Sourcing `S(±ω_S)` from cbg rather than from a closed-form ohmic spectrum keeps the bath-correlation single-source-of-truth discipline intact. Detailed balance `γ_+/γ_- = exp(-ω_S/T)` is satisfied to numerical precision; the long-time qutip_reference state for the C2 thermal parameters reaches `P(↑) ≈ 0.1189` against the canonical Boltzmann target `1/(1+e^2) ≈ 0.1192`.

### Cross-method runner registry

The previously-deferred entry

    ("spin_boson_sigma_x", "thermal_bath_cross_method"): _deferred_cross_method_handler(...)

is replaced with `_cross_handler_spin_boson_sigma_x_thermal`, which wires the two reference-module handlers and emits notes naming the σ_x channel and the σ_-/σ_+ collapse mechanism.

### Reachability

| Card | Fixture | State |
|---|---|---|
| C1 v0.1.0 | thermal_bath_cross_method | runs (FAIL ≈ 0.293) |
| C1 v0.1.0 | displaced_bath_delta_omega_c_cross_method | runs (FAIL ≈ 0.309) |
| C2 v0.1.0 | thermal_bath_cross_method | runs (FAIL ≈ 0.538) — **this commit** |
| C2 v0.1.0 | displaced_bath_delta_omega_c_cross_method | NotImplementedError (deferred) |

## Routing notes

Next admissible DG-3 implementation work, in cards-first order:

1. C2 `displaced_bath_delta_omega_c_cross_method` (σ_x coupling, displaced bath).

After full C2 reachability, the natural next step is *not* a verdict commit but rather a third reference method from a non-overlapping failure-mode class (HEOM, TEMPO, MCTDH, or pseudomode/chain-mapping), per Sail v0.5 §5 Tier 3 — failure-asymmetry clearance is the missing element for an informative DG-3 PASS.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

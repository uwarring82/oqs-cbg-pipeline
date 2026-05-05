# DG-3 C2 displaced handler wired — full C1+C2 runner reachability

**Date:** 2026-05-05
**Type:** structural
**Triggering commit:** 82ee614
**Triggering evidence:**
- [`benchmarks/exact_finite_env.py`](../benchmarks/exact_finite_env.py): `build_spin_boson_sigma_x_displaced_total` (parallel to the σ_z displaced builder, σ_x in the joint interaction).
- [`benchmarks/qutip_reference.py`](../benchmarks/qutip_reference.py): `_propagate_spin_boson_sigma_x_displaced_delta_omega_c` handler combining σ_-/σ_+ secular Lindblad (rates from cbg) with a time-dependent σ_x classical drive ⟨B(t)⟩ σ_x.
- [`reporting/benchmark_card.py`](../reporting/benchmark_card.py): `_cross_handler_spin_boson_sigma_x_displaced_delta_omega_c` registered in `_CROSS_METHOD_TEST_CASE_HANDLERS`, replacing the last deferred entry.
- [`tests/test_exact_finite_env.py`](../tests/test_exact_finite_env.py), [`tests/test_qutip_reference.py`](../tests/test_qutip_reference.py), [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py): 12 net new tests — including a full-card-reaches-verdict integration test for C2.
- `pytest` under `.venv/bin/python` 3.13.7: 407 passed.
- Frozen C2 displaced single-case run: `inter_method_relative_frobenius ≈ 0.526 > 1.0e-6`, therefore clean FAIL.

## Summary

The last deferred handler in cards-first order is now implemented: C2 `displaced_bath_delta_omega_c_cross_method`. **All four C1+C2 fixtures are now runner-reachable** through `_run_cross_method`. No `NotImplementedError` paths remain for the frozen test cases of either DG-3 card.

This is **not** a verdict commit. The four fixtures all produce structural Markov-vs-exact mismatches well above the frozen 1.0e-6 threshold:

| Card | Fixture | error |
|---|---|---|
| C1 | thermal_bath_cross_method | 0.293 |
| C1 | displaced_bath_delta_omega_c_cross_method | 0.309 |
| C2 | thermal_bath_cross_method | 0.538 |
| C2 | displaced_bath_delta_omega_c_cross_method | 0.526 |

The σ_x cases (~0.5) show larger gaps than σ_z (~0.3) because σ_x couples to ±ω_S transitions where finite-bath truncation has a stronger effect than σ_z's S(0) channel. Phase D verdict admissibility for both cards now requires either (i) convergence in the finite-bath truncation or (ii) a third reference method from a non-overlapping failure-mode class per Sail v0.5 §5 Tier 3 — neither of which is provided in this commit.

## Detail

### exact_finite_env: σ_x displaced builder

`build_spin_boson_sigma_x_displaced_total` is the third Phase B/C copy of the discrete-finite-bath thermal-joint construction — same mode-snapping discretisation, same α_disp = α₀ / √(Δω_c) calibration of the discrete coherent displacement, same Fock-truncated `D(α) = exp(α a† − α* a)` on the resonant mode. The only structural difference from the σ_z displaced builder is the joint interaction:

    H_int = sigma_x ⊗ Σ_k g_k (a_k + a_k†).

A `# Refactor opportunity` comment marks the now-three-copies duplication; the obvious factoring is `_build_spin_displaced_joint(coupling_op_array, ...)` and is deferred to a clean-up commit so this commit's diff stays minimal.

### qutip_reference: σ_-/σ_+ Lindblad + σ_x coherent drive

For σ_x coupling, displacement contributes a coherent classical drive on the system's coupling operator:

    H_drive(t) = ⟨B(t)⟩ σ_x = 2 α₀ √J(ω_c) cos(ω_c t) σ_x.

Connected statistics are unchanged by displacement, so the dissipator carries the same σ_-/σ_+ collapse operators with rates `γ_± = S(±ω_S)` numerically integrated from `cbg.bath_correlations` as the σ_x thermal handler. The QuTiP master equation is

    dρ/dt = -i[H_S + ⟨B(t)⟩ σ_x, ρ] + γ_- D[σ_-]ρ + γ_+ D[σ_+]ρ,

encoded as a list-Hamiltonian with a string-coefficient time dependence on σ_x. For C2's parameters (ω_c=10, ω_S=1, α=0.05, T=0.5, α₀=1), the drive is far off-resonant from ω_S, so its effect in the rotating frame is small but observable; the C2 displaced trajectory differs from C2 thermal by O(10⁻²) in `P(↑)`, which is enough for the inter-method comparison to reach a comparable error scale to the thermal case.

### Cross-method runner registry

The previously-deferred entry

    ("spin_boson_sigma_x", "displaced_bath_delta_omega_c_cross_method"):
        _deferred_cross_method_handler(...)

is replaced with `_cross_handler_spin_boson_sigma_x_displaced_delta_omega_c`. Every key in the registry now maps to a real handler.

### Reachability

| Card | Fixture | State |
|---|---|---|
| C1 v0.1.0 | thermal_bath_cross_method | runs (FAIL ≈ 0.293) |
| C1 v0.1.0 | displaced_bath_delta_omega_c_cross_method | runs (FAIL ≈ 0.309) |
| C2 v0.1.0 | thermal_bath_cross_method | runs (FAIL ≈ 0.538) |
| C2 v0.1.0 | displaced_bath_delta_omega_c_cross_method | runs (FAIL ≈ 0.526) — **this commit** |

Full-card integration test (`test_run_card_c2_full_card_reaches_verdict`) verifies that `bc.run_card(C2)` succeeds end-to-end without any test case raising.

## Routing notes

DG-3 implementation work is now complete in cards-first scope: all frozen C1/C2 test cases have explicit handlers and run to clean FAIL verdicts. The next admissible work is **failure-asymmetry clearance** per Sail v0.5 §5 Tier 3 — adding a third reference method from a non-overlapping failure-mode class (HEOM, TEMPO, MCTDH, or pseudomode/chain-mapping). Without such a method, the present FAILs remain structural Markov-vs-exact diagnostics rather than informative DG-3 verdict signals.

A separate, smaller follow-up is the `_build_spin_thermal_joint` and `_build_spin_displaced_joint` refactor flagged in the σ_x builders' docstrings — this is repository hygiene and does not change behaviour.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

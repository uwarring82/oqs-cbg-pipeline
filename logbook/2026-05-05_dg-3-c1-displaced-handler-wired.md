# DG-3 C1 displaced delta-omega_c handler wired — full C1 runner reachable

**Date:** 2026-05-05
**Type:** structural
**Triggering commit:** b34143d
**Triggering evidence:**
- [`benchmarks/exact_finite_env.py`](../benchmarks/exact_finite_env.py): `build_pure_dephasing_displaced_total` builder for the discrete coherent-displacement fixture.
- [`benchmarks/qutip_reference.py`](../benchmarks/qutip_reference.py): `_propagate_pure_dephasing_displaced_delta_omega_c` handler with time-dependent Lamb-shift Hamiltonian.
- [`reporting/benchmark_card.py`](../reporting/benchmark_card.py): `_cross_handler_pure_dephasing_displaced_delta_omega_c` registered in `_CROSS_METHOD_TEST_CASE_HANDLERS`, replacing the deferred entry.
- [`tests/test_exact_finite_env.py`](../tests/test_exact_finite_env.py), [`tests/test_qutip_reference.py`](../tests/test_qutip_reference.py), [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py): 15 net new tests covering the displaced builder, displaced QuTiP handler, and the runner end-to-end.
- `pytest` under `.venv/bin/python` 3.13.7: 383 passed.
- Frozen C1 displaced single-case run: `inter_method_relative_frobenius ≈ 0.309 > 1.0e-6`, therefore clean FAIL.

## Summary

The next deferred handler in cards-first order is now implemented: C1 `displaced_bath_delta_omega_c_cross_method`. Both reference modules have a registered handler for the Council-cleared `delta-omega_c` displacement profile, and the cross-method runner registry no longer raises `NotImplementedError` for that case. Both C1 fixtures (thermal and displaced delta-omega_c) run end-to-end and return clean FAIL verdicts at the frozen 1.0e-6 threshold.

This is **not** a verdict commit. The full C1 card cannot land a Phase D verdict block until the verdict is informative — at the current finite-bath / Markov-mismatch error level (`~0.3`), a FAIL is structural rather than diagnostic. Phase D admissibility remains gated on a third method from a non-overlapping failure-mode class (per Sail v0.5 §5 Tier 3) or convergence in the finite-bath truncation toward the Markov reference.

C2 handlers remain explicit deferred routes; the next admissible Phase B/C work is the `spin_boson_sigma_x × thermal_bath_cross_method` handler.

## Detail

### Convention for the discrete-finite-bath displacement

The Council-cleared continuous convention (cbg.cumulants `_evaluate_displaced_first_cumulant`) for the `delta-omega_c` profile is

    ⟨B(t)⟩ = 2 α₀ √J(ω_c) cos(ω_c t).

The exact_finite_env discretisation forces one bath mode at exactly ω_c (the displacement-profile centre). The discrete first cumulant on that resonant mode k_c is

    ⟨B(t)⟩_discrete = 2 g_{k_c} α_disp cos(ω_{k_c} t),

where g_{k_c} = √(J(ω_c) Δω_{k_c}) is the discretisation coupling. Matching the continuous convention pins

    α_disp = α₀ / √(Δω_{k_c}),

i.e. the discrete coherent-state amplitude is the continuous α₀ divided by the square root of the discretisation width at the resonant mode. The displacement is realised as `D(α_disp) ρ_thermal(ω_{k_c}) D(α_disp)†` on the truncated Fock space, with `D(α) = exp(α a† − α* a)` evaluated via `scipy.linalg.expm`.

### qutip_reference: time-dependent Lamb shift

Connected bath statistics are invariant under a coherent displacement, so the Markov dephasing rate γ_M is identical to the thermal handler. The displacement enters the master equation as a time-dependent Lamb shift on H_S:

    H_eff(t) = (ω/2 + ⟨B(t)⟩) σ_z = (ω/2 + 2 α₀ √J(ω_c) cos(ω_c t)) σ_z.

QuTiP integrates this via a list-Hamiltonian with a string-coefficient time dependence `lamb_amp * cos(omega_disp * t)`, plus the same √(γ_M / 2) σ_z collapse operator as the thermal handler.

### Cross-method runner registry

The previously-deferred entry

    ("pure_dephasing", "displaced_bath_delta_omega_c_cross_method"): _deferred_cross_method_handler(...)

is replaced with `_cross_handler_pure_dephasing_displaced_delta_omega_c`, which wires the two reference-module handlers and emits notes naming the profile and the Lamb-shift mechanism.

### Reachability of C1 verdict blocks

Running the full frozen C1 card (with the time grid reduced to keep the finite-environment reference quick) now gives:

    verdict: FAIL
      thermal_bath_cross_method:                error ≈ 0.293  (threshold 1.0e-6)
      displaced_bath_delta_omega_c_cross_method: error ≈ 0.309  (threshold 1.0e-6)

C1 is therefore *runner-complete* in the sense that no test case raises and the verdict is well-defined. Phase D admissibility additionally requires the FAIL to be *informative* (sub-threshold or with a documented cause-label per Sail v0.5 §9 DG-3); the present FAIL is structural Markov-vs-exact mismatch and does not yet meet that bar.

## Routing notes

Next admissible DG-3 implementation work, in cards-first order:

1. C2 `thermal_bath_cross_method` (`spin_boson_sigma_x` σ_x coupling, thermal bath).
2. C2 `displaced_bath_delta_omega_c_cross_method` (σ_x coupling, displaced bath).

After full C2 reachability, the natural next step is *not* a verdict commit but rather a third reference method from a non-overlapping class (HEOM, TEMPO, MCTDH, or pseudomode/chain-mapping) per Sail v0.5 §5 Tier 3. Without that, C1/C2 verdicts remain Markov-vs-exact diagnostics rather than failure-asymmetry-cleared findings.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

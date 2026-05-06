# `benchmark_cards/`

Benchmark cards live here. Each card is a YAML file with frozen-parameter,
acceptance-criterion, result, failure-mode-log, and stewardship-flag blocks.

## Card schema

The canonical schema is [`SCHEMA.md`](SCHEMA.md) (this directory). A
machine-readable, fully-annotated example is [`_template.yaml`](_template.yaml).
Together they are sufficient to author a syntactically valid card without
consulting source files.

The schema derives from two protocol sections in
[`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md):

- §1 (gauge annotation) — transcribed into the `gauge:` block.
- §4 (parameter freezing) — transcribed into the `frozen_parameters:` block.

The schema lives here, not in `docs/`, because `docs/` is locked by
Sail v0.5 §11 to the five protective documents. The schema is operational
specification, not protective scaffolding.

## Supersedure

No card may be silently edited or deleted post-result. Superseded cards are
retained with a `superseded_by:` annotation; new cards are added as new files.
A `failure_mode_log` entry on the new card explains what changed and why.
See [`SCHEMA.md`](SCHEMA.md) §Supersedure and
[`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md) §4.3.

## Card index

| Card ID | DG | Ledger anchor | Status | File |
|---|---|---|---|---|
| A1 | DG-1 | CL-2026-005 v0.4 Entry 1 (B.1, B.2; B.3 deferred to DG-2) | **pass** (2026-04-30) | [A1_closed-form-K_v0.1.1.yaml](A1_closed-form-K_v0.1.1.yaml) |
| A3 | DG-1 | CL-2026-005 v0.4 Entry 3 (B.1, B.2 thermal; B.3 deferred to DG-2) | **pass** (2026-04-30) | [A3_pure-dephasing_v0.1.1.yaml](A3_pure-dephasing_v0.1.1.yaml) |
| A4 | DG-1 | CL-2026-005 v0.4 Entry 4 (B.1 thermal; B.2 deferred to DG-2) | **pass** (2026-04-30) | [A4_sigma-x-thermal_v0.1.1.yaml](A4_sigma-x-thermal_v0.1.1.yaml) |
| B1 | DG-2 | CL-2026-005 v0.4 Entry 1.B.3 (diagonal pseudo-Kraus reduction) | **pass** (2026-05-01) | [B1_pseudo-kraus-diagonal_v0.1.0.yaml](B1_pseudo-kraus-diagonal_v0.1.0.yaml) |
| B2 | DG-2 | CL-2026-005 v0.4 Entry 1.B.3 (off-diagonal half), Entry 1.D | **pass** (2026-05-04) | [B2_pseudo-kraus-offdiagonal_v0.1.0.yaml](B2_pseudo-kraus-offdiagonal_v0.1.0.yaml) |
| B3 | DG-2 | CL-2026-005 v0.4 Entry 1.A (basis-independence) | **pass** (2026-05-04) | [B3_cross-basis-structural-identity_v0.1.0.yaml](B3_cross-basis-structural-identity_v0.1.0.yaml) |
| B4-conv-registry | DG-2 | CL-2026-005 v0.4 Entry 3.B.3 (time-dependent shift; coherent-displaced bath, pure-dephasing) | **pass** (2026-05-04) | [B4-conv-registry_v0.1.0.yaml](B4-conv-registry_v0.1.0.yaml) |
| B5-conv-registry | DG-2 | CL-2026-005 v0.4 Entry 4.B.2 (eigenbasis rotation; coherent-displaced bath, σ_x coupling) | **pass** (2026-05-04) | [B5-conv-registry_v0.2.0.yaml](B5-conv-registry_v0.2.0.yaml) |
| C1 | DG-3 | CL-2026-005 v0.4 Entry 3 (cross-method corroboration) | frozen-awaiting-run | [C1_cross-method-pure-dephasing_v0.1.0.yaml](C1_cross-method-pure-dephasing_v0.1.0.yaml) |
| C2 | DG-3 | CL-2026-005 v0.4 Entry 4 (cross-method corroboration) | frozen-awaiting-run | [C2_cross-method-spin-boson_v0.1.0.yaml](C2_cross-method-spin-boson_v0.1.0.yaml) |
| D1 | DG-4 | CL-2026-005 v0.4 Entry 2 (recursive-series convergence; scope-limited) | **pass** (Path B numerical, 2026-05-06) | [D1_failure-envelope-convergence_v0.1.1.yaml](D1_failure-envelope-convergence_v0.1.1.yaml) |
| E1 | DG-5 | CL-2026-005 v0.4 Entries 6–7 (thermodynamic discriminant scope) | scope-definition | [E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml](E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml) |

The three DG-1 cards reached the **PASS** verdict per [DG-1 work plan v0.1.4](../../plans/dg-1-work-plan_v0.1.4.md) §4 Phase D; see [logbook/2026-04-30_dg-1-pass.md](../../logbook/2026-04-30_dg-1-pass.md) for the verdict logbook entry and [benchmarks/results/](../results/) for the JSON evidence artefacts.

Card B1 is the first DG-2 card and reached **pass** at runner version 0.1.0. All three pseudo-Kraus test_cases returned error = 0.0 (machine precision) with HPTA residuals well below the 1.0e-14 absolute bound.

Card B2 is the second DG-2 card and reached **pass** at runner version 0.1.0. All three off-diagonal pseudo-Kraus test_cases returned error = 0.0 (machine precision) with both Hermiticity-of-omega and HPTA preconditions satisfied as algebraic identities (residuals 0.0 exactly). B2 introduces the off-diagonal pseudo-Kraus card surface (`pseudo_kraus_offdiag_operators` + `pseudo_kraus_offdiag_omega`) per transcription [v0.1.1 §4b / §7a](../../transcriptions/hayden-sorce-2022_pseudokraus_v0.1.1.md); the wiring in [`reporting/benchmark_card.py`](../../reporting/benchmark_card.py) reuses B1's AST-restricted operator parser for `V_i` and adds a parameters-only scalar parser (`_eval_complex_scalar_expression`) for `omega_{ij}` entries.

Card B3 is the third DG-2 card and reached **pass** at runner version 0.1.0. B3 covers the [Sail v0.5](../../docs/) §9 DG-2 universal-default structural-identity check — basis-independence of `K_from_generator` per Entry 1.A. Its three test cases reuse known-good frozen fixtures from A1 v0.1.1 and B1 v0.1.0, and assert that K computed under the matrix-unit basis equals K computed under the su(d)-generator basis ({I, σ_x, σ_y, σ_z} / √2 for d = 2). All three test_cases returned errors at machine precision (1.57e-16, 1.57e-16, 0.0), well below the 1.0e-10 relative-Frobenius threshold; the pseudo-Kraus case's HPTA residual is 3.14e-16, well below 1.0e-14.

Card B4-conv-registry is the fourth DG-2 card and reached **pass** at runner version 0.1.0 across all four Council-cleared profiles. The verdict commit landed [`cbg/cumulants.py`](../../cbg/cumulants.py) `D_bar_1` dispatch on the registry; [`cbg/tcl_recursion.py`](../../cbg/tcl_recursion.py) `K_total_displaced_on_grid` (reusing the thermal n=0 / n=2 path; D̄_2 is invariant under displacement); and the [`reporting/benchmark_card.py`](../../reporting/benchmark_card.py) carve-out lift + four B4 dynamical handlers under (pure_dephasing, displaced_bath_*). All four test_cases returned errors at machine precision (≤ 8.9e-16, well below the 1.0e-4 threshold) — structural agreement, because under σ_z coupling the parity-class theorem of Letter end-matter Eq. (A.39) makes K_2's σ_z coefficient exactly zero, so the perturbative expansion at order ≤ N_card = 2 reduces to K_0 + K_1 = (ω/2 + D̄_1) σ_z and matches the predicted shift 2 D̄_1(t) exactly.

Card B5-conv-registry v0.2.0 is the σ_x sibling of B4-conv-registry under the same Council-cleared profile registry, and reached **pass** at runner version 0.1.0 across all four cleared profiles. The verdict commit registered the σ_x-specific `_dyn_handler_sigma_x_displaced` under (spin_boson_sigma_x, displaced_bath_*) keys, reusing the displaced-bath TCL recursion that landed with B4's verdict commit. All four test_cases returned errors at exactly 0.0 — structurally exact agreement, because the same D̄_1 array drives both the runner's K_1 computation and the predicted σ_x channel (single-source-of-truth pattern; floating-point error cancels), and the σ_y channel is zero by the parity-class theorem of Letter end-matter Eq. (A.43)-(A.45) at order ≤ N_card = 2. The v0.1.0 predecessor card is retained at HEAD with `status: superseded` per SCHEMA.md §Card lifecycle (see superseded-cards table below).

Card D1 v0.1.1 is the active DG-4 failure-envelope card after Phase A.bis supersedure and reached **pass** at runner version 0.1.0. It switches the target model from pure_dephasing to spin_boson_sigma_x, adopts the parity-aware even-order ratio `r_4 = <||L_4^dis||>_t / <||L_2^dis||>_t`, and freezes the reproducibility perturbation set (`upper_cutoff_factor` via numerical quadrature, `omega_c` via model-spec mutation). The Phase D run used Path B numerical Richardson extraction for the L_4 source and classified all 20 frozen `coupling_strength` sweep points as `convergence_failure`; no `alpha_crit` is bracketed because the first swept point already fails. The verdict carries the documented finite-env extraction floor caveat, plus the Path-B-specific limitation that `upper_cutoff_factor` is threaded but not consumed by `exact_finite_env`; `omega_c` is the operational reproducibility mutation in the current Path B route. It is not analytic n=4 completion. The v0.1.0 predecessor is retained with `status: superseded`.

The index is updated atomically when cards are committed, when their `status` field changes per [SCHEMA.md](SCHEMA.md) §Card lifecycle, or when a successor card is added.

### Superseded cards (retained for audit)

| Card ID | Version | Superseded by | Date | Reason |
|---|---|---|---|---|
| A1 | v0.1.0 | [v0.1.1](A1_closed-form-K_v0.1.1.yaml) | 2026-04-30 | Entry 1.B.3 (pseudo-Kraus) deferred to DG-2; Hayden–Sorce 2022 closed form not transcribed. See A1 v0.1.1 `failure_mode_log[0]`. |
| A3 | v0.1.0 | [v0.1.1](A3_pure-dephasing_v0.1.1.yaml) | 2026-04-30 | Entry 3.B.3 (time-dependent shift in non-thermal bath) deferred to DG-2; displacement convention on multi-mode bath under-specified. See A3 v0.1.1 `failure_mode_log[0]`. |
| A4 | v0.1.0 | [v0.1.1](A4_sigma-x-thermal_v0.1.1.yaml) | 2026-04-30 | Entry 4.B.2 (eigenbasis rotation in non-thermal bath) deferred to DG-2; same displacement-convention gap as A3. See A4 v0.1.1 `failure_mode_log[0]`. |
| B5-conv-registry | v0.1.0 | [v0.2.0](B5-conv-registry_v0.2.0.yaml) | 2026-05-04 | Card-design correction: v0.1.0's predicted transverse vector used the interaction-picture form `D̄_1(t)·(cos(ωt), -sin(ωt))`, but the Schrödinger-picture runner computes `K_1(t) = D̄_1(t)·σ_x` (constant direction, zero σ_y component at order ≤ N_card = 2 by parity-class theorem). v0.2.0 corrects the prediction to `(D̄_1(t), 0)`. Card-internal correction; no Council deliberation, no convention change. See B5 v0.2.0 `failure_mode_log[0]`. |
| D1 | v0.1.0 | [v0.1.1](D1_failure-envelope-convergence_v0.1.1.yaml) | 2026-05-06 | DG-4 Phase A.bis correction: pure_dephasing thermal is TCL-2 exact and cannot expose the intended order-4 convergence failure; adjacent-order ratios are parity-blind in the σ_x thermal fixture. v0.1.1 switches to spin_boson_sigma_x, parity-aware `r_4`, and operational reproducibility perturbations. |

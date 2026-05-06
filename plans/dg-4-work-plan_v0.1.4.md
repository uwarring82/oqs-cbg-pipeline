---
plan_id: dg-4-work-plan
version: v0.1.4
date: 2026-05-06
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§9 (DG-4), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entry 2 (recursive-series convergence; COMPATIBLE, scope-limited)
anchor_envelope: docs/validity_envelope.md DG-4 row (SCOPED — Phase B partial → target PASS)
status: draft
supersedes: dg-4-work-plan_v0.1.3.md
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Work Plan — Failure-envelope identification

## Supersedure note

v0.1.4 supersedes v0.1.3 to address two issues surfaced by review of Phase B.3 (commit `b699950`). The empirical finding behind v0.1.3 (quad_limit no-op, omega_c substitute) and all earlier corrections remain in place. v0.1.4 fixes:

1. **Adjacent-order ratio is undefined for the σ_x thermal fixture.** v0.1.3 §1.1 specified `r_n = ⟨‖L_n^dissipator‖⟩_t / ⟨‖L_{n−1}^dissipator‖⟩_t`. Phase B.3 (commit `b699950`) confirmed numerically that `‖L_3^dissipator‖ = 0` for σ_x thermal, by parity (Letter App. D odd-order vanishing) plus thermal Gaussian D̄_3 = 0. Under v0.1.3 §3 Phase C's zero-denominator policy, the planned `r_4 = ‖L_4^dis‖ / ‖L_3^dis‖` would be marked `metric-undefined`, **not** `convergence failure`, so the metric cannot fire even after L_4 lands. v0.1.4 switches to a **parity-aware even-order ratio**:

       r_n^{even} := ⟨‖L_n^dissipator‖⟩_t / ⟨‖L_{n−2}^dissipator‖⟩_t   for n ∈ {2, 4, 6, ...}

   The convergence-failure classification at order 4 is now `r_4 = ‖L_4^dis‖ / ‖L_2^dis‖ > 1` — the natural "next-leading even-order correction exceeds the leading even-order term" signal. For small α the perturbative scaling is `‖L_n^dis‖ ∝ α^n`, so `r_4 = α² × O(1)` and `r_4 < 1` in the convergent regime; the boundary `α_crit` where `r_4` crosses 1 is the same physical quantity D1 v0.1.0/1/2/3 sought. The pilot check (Phase A.bis) updates accordingly: confirm `‖L_2^dis‖ > 0` AND `‖L_4^dis‖ > 0` in the σ_x thermal model at α = 0.05 (both leading even-order terms must be non-zero for the ratio to be well-defined).

2. **`omega_c` perturbation placement.** v0.1.3 §3 Phase A.bis suggested putting both `upper_cutoff_factor` and `omega_c` perturbations in the ad-hoc `frozen_parameters.numerical.quadrature` extras block. But the runner-side allow-list `reporting.benchmark_card._quadrature_kwargs` (Phase B.4) only forwards two known keys — `upper_cutoff_factor` and `quad_limit`. If D1 v0.1.1's reproducibility spec encoded `omega_c` under `numerical.quadrature.omega_c`, that perturbation would silently no-op (the runner would drop it). v0.1.4 clarifies the placement separately for the two knobs:

   - **`upper_cutoff_factor` ∈ {20, 30, 40}**: a quadrature control. Perturbations encoded under `frozen_parameters.numerical.quadrature.upper_cutoff_factor` (the allow-listed extras block; consumed by `_quadrature_kwargs`).
   - **`omega_c` ∈ {9.0, 10.0, 11.0}**: a model parameter. Perturbations encoded by mutating `frozen_parameters.model.bath_spectral_density.cutoff_frequency` directly. The Phase C runner is responsible for cloning the model spec with the perturbed value at each reproducibility re-run; this is *not* a quadrature-allow-list concern.

The §1 Objective and §2 Scope shape are unchanged from v0.1.3; the substantive edits are concentrated in §1.1 (second + third bullets), §1.2 (example verdict), §3 Phase A.bis (the D1 v0.1.1 spec), §3 Phase C (per-α reproducibility check spec), §4 (acceptance criteria), §5 R7 (parity-vanishing of odd L_n^dis recorded), and §5 R9 (new: ratio-metric parity-awareness).

## 1. Objective

Pass DG-4 as defined in Sail v0.5 §9:

> *Pass if at least one reproducible, cause-labelled regime is identified in which the implementation fails or yields ambiguous output.*

DG-4 is the only Decision Gate where **PASS requires a failure to occur**. It operationalises CL-2026-005 v0.4 Entry 2's open convergence question by demanding evidence that the implementation *actually exhibits* breakdown in some regime, not merely that breakdown is possible in principle.

This plan operationalises that objective in **benchmark-cards-first** ordering. Card D1 v0.1.0 is frozen; Phase A.bis below supersedes it to D1 v0.1.1 with a model switch (`pure_dephasing` → `spin_boson_sigma_x`), a metric switch to the **parity-aware even-order ratio** `‖L_n^dissipator‖ / ‖L_{n−2}^dissipator‖`, and the v0.1.3 reproducibility-perturbation set (`upper_cutoff_factor`, `omega_c`) with the v0.1.4 placement clarification. Phases B–D operationalise the corrected card.

### 1.1 Cards-first context

D1 v0.1.0 freezes a `coupling_strength` sweep over the pure-dephasing model and targets cause label `convergence failure`. Three of its design choices need re-freezing in Phase A.bis:

- **Model.** v0.1.0 uses `pure_dephasing` (A = σ_z). For thermal Gaussian baths, this model has TCL-2 exact reduced dynamics: `L_n = 0` for all `n ≥ 3` by Gaussianity, and `L_1 = 0` because thermal `D̄_1 = 0`. The convergence-ratio metric is therefore identically zero for `n ≥ 3` regardless of which observable (`K_n` or `L_n^dissipator`) or which adjacent / next-leading variant of the ratio is chosen. D1 v0.1.1 will switch to `spin_boson_sigma_x` (A = σ_x), which inherits the parameter scaffold from cards A4 v0.1.1 and B5-conv-registry v0.2.0 (parallel to A3/B4 inheritance) and where `[H_S, A] ≠ 0` keeps the **even-order** TCL series non-trivial at every order (odd orders still vanish by Letter App. D parity).
- **Convergence metric (v0.1.4 update — parity-aware).** With the σ_x model, `‖L_n^dissipator‖` is non-zero for *even* n and zero for *odd* n (parity + Gaussian). Phase B.3 (commit `b699950`) verified `‖L_3^dis‖ = 0` numerically. The metric is the time-averaged Frobenius norm of the dissipator part of L_n, computed under the repository's sign convention `L[X] = -i[H, X] + dissipator` so that

      L_n^dissipator(t) := L_n(t) + i [K_n(t), · ]

  with the **parity-aware ratio**:

      r_n^{even} := ⟨‖L_n^dissipator‖⟩_t / ⟨‖L_{n−2}^dissipator‖⟩_t   for n ∈ {2, 4, 6, ...}

  D1 v0.1.1 evaluates `r_4 = ⟨‖L_4^dis‖⟩ / ⟨‖L_2^dis‖⟩` at every swept α. The convergence-failure classification at order 4 is `r_4 > 1.0` AND stable under the v0.1.3 reproducibility-perturbation set. The `r_2 = ⟨‖L_2^dis‖⟩ / ⟨‖L_0^dis‖⟩` is undefined (`L_0^dis = 0` by the unitary-recovery oracle, Phase B.3 R8); the metric is meaningful only at orders n ≥ 4. `r_6` and higher would extend the same parity-aware structure if Phase B reaches order 6.
- **Reproducibility-perturbation knobs (v0.1.3 + v0.1.4 placement clarification).** Two genuinely-perturbative knobs:
  - **`upper_cutoff_factor`** (default 30, perturb to 20 / 40). Quadrature control. Perturbations encoded under `frozen_parameters.numerical.quadrature.upper_cutoff_factor` — the runner-side allow-list block consumed by `_quadrature_kwargs` (Phase B.4 commit `c7e9999`).
  - **`omega_c`** (default 10.0, perturb to 9.0 / 11.0). Model parameter (the ohmic spectral-density cutoff). Perturbations encoded by mutating `frozen_parameters.model.bath_spectral_density.cutoff_frequency` directly at each reproducibility re-run; this is *not* a quadrature-allow-list concern. The Phase C runner clones the model spec with the perturbed value before re-evaluating r_4.
  - **Dropped from the load-bearing set:** `quad_limit` (no-op witness for production-like tuples; v0.1.3 finding). May be retained as a documented null-result witness in `result.notes`.
  - v0.1.0's `bath_mode_cutoff` and `integration_tolerance` remain dropped (non-operational on the CBG path).

D1 v0.1.0's status reverts to `superseded` in Phase A.bis. The supersedure is steward-side: all three changes are runner-discovery / mathematical-physics findings, not Ledger-bearing facts.

### 1.2 PASS-on-failure asymmetry from DG-1/2/3

DG-1, DG-2, and DG-3 PASS when their cards' acceptance criteria are met. DG-4 PASSES when D1 v0.1.1 produces a verdict like:

> "α_crit ≈ 0.42 ± 0.05 (interpolated boundary between last α with `r_4^{even} < 1` and first α with `r_4^{even} > 1`); cause label `convergence failure` confirmed reproducible under upper_cutoff_factor ±10 (30 → 20 / 40) and ω_c ±1 (10 → 9 / 11) perturbation."

A verdict like "no α in the swept range produced r_4 > 1" is **not** a DG-4 PASS. The cards-first / Risk #8 discipline requires *supersedure* (D2 with extended range), not in-place range-tightening. See Risk R3.

## 2. Scope

### 2.1 In scope

- **Phase A.bis:** supersede D1 v0.1.0 → D1 v0.1.1 with the σ_x model, the parity-aware even-order metric, and the v0.1.4 reproducibility-perturbation placement. Includes a small pilot check (see §3 Phase A.bis) confirming both `‖L_2^dis‖ > 0` and `‖L_4^dis‖ > 0` in the chosen model.
- **Phase B:** four-sub-phase TCL-recursion extension (B.0 → B.4 below). Status: B.0, B.1, B.2 (n=3), B.3 (n ∈ {0,1,2,3}), B.4 landed; B.2 (n=4) and B.3 (n=4) pending the L_4 path resolution.
- **Phase C:** sweep-block-aware runner branch consuming `frozen_parameters.sweep`, with parity-aware ratio computation and the two-pathway reproducibility re-run (quadrature-allow-list mutation for `upper_cutoff_factor`, model-spec mutation for `omega_c`).
- Cause-label assignment per the Sail v0.5 §9 taxonomy.
- Boundary `α_crit` interpolation (linear in `log α`).
- Phase D verdict commit.

### 2.2 Out of scope

- Other cause labels (#3 `projection ambiguity`, #5 `benchmark disagreement`): require cross-method data — DG-3 territory; future cards.
- Cause label #2 `TCL singularity`: logged as a runner observation in `result.notes` if `‖Λ_t − id‖ ≥ 1` is detected, but does NOT gate D1's PASS verdict (R5).
- Multi-parameter sweeps; models other than `spin_boson_sigma_x`; re-classification of CL-2026-005 v0.4 Entry 2.
- Higher-order even ratios `r_6`, `r_8`: out of scope until Phase B reaches order 6.

### 2.3 Explicit non-claims

Same as v0.1.3; DG-4 PASS does not establish that α_crit is theory-intrinsic, that lower orders are convergent for all α below it, or that finite-bath truncations in DG-3 handlers are converged at α ≤ α_crit.

## 3. Phases

### Phase A — Card drafting (already complete)

D1 v0.1.0 frozen 2026-05-05. Note: superseded by Phase A.bis below.

### Phase A.bis — Supersede D1 v0.1.0 → D1 v0.1.1

- Draft `D1_failure-envelope-convergence_v0.1.1.yaml` with:
  - `model: "spin_boson_sigma_x"` (changed from `pure_dephasing`).
  - `frozen_parameters.model.coupling_operator: "sigma_x"`.
  - `frozen_parameters.model.system_hamiltonian: "(omega / 2) * sigma_z"` (unchanged).
  - Parameter inheritance: bath_spectral_density and time_grid from A4 v0.1.1; perturbative_order, basis, integration_tolerance, solver from D1 v0.1.0. `bath_mode_cutoff` is dropped (non-operational on the CBG path).
  - `comparison.target_observable: "parity-aware even-order convergence ratio r_n = ||L_n^dissipator|| / ||L_{n-2}^dissipator|| for n ∈ {4, 6, ...}"` with `L_n^dissipator := L_n + i [K_n, ·]`. D1 v0.1.1 evaluates **only `r_4`** at v0.1.1; `r_6` and higher would land in a successor card after Phase B reaches order 6.
  - `comparison.error_metric: "convergence_ratio_parity_aware"` (renamed from v0.1.3's `convergence_ratio` to make the parity-aware variant explicit).
  - **Reproducibility specification (v0.1.4 placement clarification):**
    - `upper_cutoff_factor` ±10 perturbation: encoded under `frozen_parameters.numerical.quadrature.upper_cutoff_factor` (sweep `30 → 20 / 40`); consumed by `reporting.benchmark_card._quadrature_kwargs`.
    - `omega_c` ±1 perturbation: encoded as a model-spec mutation pattern documented in `result.notes` and in the Phase C runner. The card freezes the baseline `omega_c = 10.0`; the runner clones `frozen_parameters.model.bath_spectral_density.cutoff_frequency = 9.0 / 11.0` for the two reproducibility re-runs. **Not** placed under `numerical.quadrature` (which would silently no-op via the allow-list).
  - `failure_mode_log` entry citing v0.1.0/.2/.3/.4's deficiencies and refinements as the supersedure reasons; `predecessor_card_id: D1`, `predecessor_version: v0.1.0`.
- Annotate D1 v0.1.0 with `superseded_by: D1_failure-envelope-convergence_v0.1.1.yaml` and `status: superseded`.
- **Pilot check (v0.1.4 update):** before D1 v0.1.1 lands, a small numerical experiment confirming that, in the σ_x + thermal Gaussian model at α = 0.05, **both** `‖L_2^dis‖_t` AND `‖L_4^dis‖_t` are strictly positive at typical `t > 0`. The L_2 part is already known to be non-zero (Phase B.3 test `test_L_2_dissipator_sigma_x_thermal_is_nonzero`); the L_4 part is the gating piece, runnable only after the L_4 path resolves. If `‖L_4^dis‖ = 0` numerically in the σ_x thermal fixture, D1 v0.1.1 fails its design assumption and Phase A.bis must consider a different model or non-Gaussian bath.
- **Schema/docs minor follow-up** (not in this commit; flagged for a future SCHEMA.md v0.1.4 bump): formalise `frozen_parameters.numerical.quadrature` as a sub-block with `upper_cutoff_factor` and `quad_limit` as the only allowed keys. Currently accepted as extras by the permissive validator. v0.1.4 of this plan does NOT block on the schema bump.

### Phase B — TCL recursion at orders 3 and 4

Status (commit-tagged):

- **B.0 — Raw ordered n-point correlations.** Implemented (commits `a2e7380`, `33eeeb5`).
- **B.1 — Extend D̄ recursion to mixed left/right indices and n ≥ 3.** Implemented (commit `edae5cf`).
- **B.2 — K_3, K_4 wired through K_n_thermal_on_grid.** Partial (commit `ca3471b`): n=3 lands; n=4 deferred. Three concrete routes recorded at [`cbg/tcl_recursion.py:156`](../cbg/tcl_recursion.py).
- **B.3 — L_n^dissipator extraction.** Partial (commit `b699950`): n ∈ {0, 1, 2, 3} lands with the unitary-recovery oracle (R8) firing at exact zero for n=0 and the σ_x thermal pilot signal `‖L_2^dis‖ > 0` (gate component 1 of Phase A.bis pilot). n=4 propagates the L_4 path. Norm convention clarification: see logbook follow-up entry `2026-05-06_dg-4-phase-b3-norm-convention-clarification.md` (the original entry stated a wrong-sign counterfactual of 2.0 rather than the correct Liouville-Frobenius value 2√2 ≈ 2.828).
- **B.4 — Knob-threading for reproducibility checks.** Implemented (commit `c7e9999`). Threads `upper_cutoff_factor` and `quad_limit` through the bath / cumulant / TCL / runner layers via an allow-list helper. Empirical finding (v0.1.3): `quad_limit` is a no-op witness; `upper_cutoff_factor` is genuinely perturbative.

### Phase C — Sweep runner wiring

- Add `_run_dg4_sweep(card)` in `reporting/benchmark_card.py`. Dispatch from `run_card` BEFORE `_refuse_dg4_sweep` (and remove the refusal path once tests pass).
- The sweep runner:
  - Iterates over swept α values per `frozen_parameters.sweep.sweep_range`.
  - For each α, builds a `model_spec` with the swept value injected at `model.bath_spectral_density.coupling_strength`.
  - Evaluates K_n and L_n^dissipator at orders 0–4 via Phase B.
  - Computes the **parity-aware ratio** `r_4 = ⟨‖L_4^dis‖⟩_t / ⟨‖L_2^dis‖⟩_t`.
  - **Zero-denominator policy:** if `‖L_2^dis‖ < ε_machine × ‖L_2^dis‖_max-over-sweep`, mark the α as `metric-undefined` and exclude from convergence-failure classification. (At the chosen σ_x model this should never fire — `L_2^dis` is uniformly the dominant Bloch-Redfield term — but the policy is retained as a defensive guard.)
  - Tags each α as `passing`, `failing-candidate`, or `metric-undefined`.
- Per-α reproducibility checks (v0.1.4 placement-clarified):
  1. **`upper_cutoff_factor` perturbation**: re-evaluate `r_4` at `upper_cutoff_factor = 20` and `40`, passing through the `_quadrature_kwargs` allow-list block.
  2. **`omega_c` perturbation**: clone the model spec with `bath_spectral_density.cutoff_frequency = 9.0` and `11.0` respectively; re-evaluate `r_4` under each cloned spec. Mutation is at the model level (NOT in the `numerical.quadrature` block).
- Reclassify `failing-candidate` α as `convergence failure` (stable under all four perturbations) or `truncation artefact` (unstable under at least one).
- Λ_t-singularity observations recorded in `result.notes` only (R5).

### Phase D — Verdict

- Run D1 v0.1.1 end-to-end via the Phase C runner.
- Populate `result.verdict`, `result.evidence`, `result.runner_version`, `result.notes`.
- Logbook entry; validity-envelope update; self-referential `commit_hash` follow-up.
- Repository tag (`v0.5.0` on PASS; appropriate dev bump otherwise).

## 4. Acceptance criteria

PASS for DG-4 requires D1 v0.1.1 to verdict to PASS, which requires:

1. The Phase C runner runs to completion across the full swept range without raising.
2. At least one α in the range is classified `convergence failure` (i.e. `r_4 = ⟨‖L_4^dis‖⟩ / ⟨‖L_2^dis‖⟩ > 1` AND stable under the v0.1.4 reproducibility perturbations: `upper_cutoff_factor` ±10 (via `_quadrature_kwargs`) AND `omega_c` ±1 (via model-spec mutation)).
3. The cause label, the per-α `r_4` values, and the boundary `α_crit` interpolation are all recorded in `result.notes`.

A FAIL verdict is admissible iff the runner runs to completion AND no α is classified `convergence failure`. The result must report `verdict: FAIL` with cause `no-failure-found-in-frozen-range` AND a routing note: per Risk R3, the response is supersedure (D2 with extended range), not in-place range-tightening of D1.

CONDITIONAL is admissible iff all candidate α values are classified `truncation artefact` rather than `convergence failure`; the `result.notes` must explain the reproducibility-knob coverage gap.

**TCL singularity at D1 v0.1.1 is observational, not gating.** A future card (with Λ_t reconstruction) targets it as a primary cause label.

## 5. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **R1: Phase B is large.** | **Largely mitigated:** B.0, B.1, B.2 (n=3), B.3 (n ∈ {0,1,2,3}), B.4 are landed (commits `a2e7380`, `33eeeb5`, `edae5cf`, `ca3471b`, `b699950`, `c7e9999`). B.2 (n=4) and B.3 (n=4) deferred per source-side falsification at [`cbg/tcl_recursion.py:156`](../cbg/tcl_recursion.py); both gated on the same L_4 path resolution. |
| **R2: Reproducibility-check cost.** Each `failing-candidate` α is re-run under the v0.1.4 perturbation set — twice for `upper_cutoff_factor` and twice for `omega_c` — so up to 4 perturbed re-runs per failing α. | Cache K_n / L_n arrays where the model spec is unchanged (only `quadrature` perturbations); for `omega_c` perturbations the bath kernel must be recomputed. Document the cost; consider a `--quick` mode for development. |
| **R3: PASS-by-supersedure temptation.** | §4 *explicitly* allows a FAIL with cause `no-failure-found-in-frozen-range`. Response is a *new card* D2, not a silent edit of D1. |
| **R4: Truncation-artefact dominance.** | The v0.1.4 perturbation set — `upper_cutoff_factor` and `omega_c` — both genuinely change the bath spectrum. Artefact-classification under either is a meaningful signal that the truncation is too coarse and the response is a new card D3 with tighter defaults. |
| **R5: TCL singularity is observational only at D1 v0.1.1.** | TCL singularity recorded in `result.notes` only; D1 PASS gates only on `convergence failure`. A future card with Λ_t reconstruction targets it as a primary PASS path. |
| **R6: Reproducibility-knob operationality (empirically refined in v0.1.3).** | Confirmed in commit `c7e9999`. The v0.1.3 perturbation set (`upper_cutoff_factor`, `omega_c`) is the load-bearing pair; `quad_limit` may be retained as a null-result witness. v0.1.4 adds the *placement clarification*: `omega_c` perturbations are model-spec mutations (NOT routed through `numerical.quadrature`). |
| **R7: K_n is identically zero in pure-dephasing thermal — and so is L_n for n ≥ 3.** Plus, in any thermal Gaussian + bilinear-coupling model, **L_n^dissipator is identically zero for odd n** (parity + Gaussian D̄_3 = 0; verified at n=3 by Phase B.3 commit `b699950`). | v0.1.2's Phase A.bis switched D1's *model* to `spin_boson_sigma_x`. v0.1.4 additionally switches the metric to a *parity-aware even-order ratio* (R9) so the odd-order zeros are bypassed structurally rather than triggering the zero-denominator policy. |
| **R8: Dissipator-extraction sign.** | v0.1.2 corrected to `L_n^dissipator := L_n + i [K_n, ·]`. Phase B.3 (commit `b699950`) wired the unit test on the unitary-recovery oracle: ‖L_0^dissipator‖ = 0 to machine precision; an opposite sign would give the Liouville-Frobenius residual `2√2 ≈ 2.828` (NOT 2.0; see logbook clarification entry `2026-05-06_dg-4-phase-b3-norm-convention-clarification.md`). |
| **R9 (NEW in v0.1.4): Adjacent-order ratio is parity-blind.** v0.1.3's `r_n = ‖L_n^dis‖ / ‖L_{n−1}^dis‖` would mark D1 v0.1.1's σ_x thermal fixture as `metric-undefined` because `L_{odd}^dis = 0` by parity. The metric never fires even after L_4 lands. | v0.1.4 adopts the **parity-aware even-order ratio** `r_n^{even} := ‖L_n^dis‖ / ‖L_{n−2}^dis‖` for n ∈ {2, 4, 6, …}. D1 v0.1.1 evaluates `r_4` only; `r_2` is undefined (L_0^dis = 0 by R8 oracle); `r_6` and higher require Phase B at order 6. |

## 6. Dependencies

- DG-1 PASS (completed 2026-04-30, tag `v0.2.0`).
- DG-2 structural sub-claims PASS (completed 2026-05-04). Phase B unblocks the canonical-unfilled "literal K_2–K_4 numerical recursion" milestone partially — n=3 lands at Phase B.2; n=4 remains pending.
- D1 v0.1.1 supersedure (Phase A.bis): must land before Phase C consumes the new model and metric. Phase B.0 / B.1 / B.3 (n ≤ 3) / B.4 are independent and have already landed.
- Currently stubbed pieces this plan still needs:
  - `cbg.tcl_recursion.K_n_thermal_on_grid` at n=4 (B.2 deferred; three routing paths recorded at [`cbg/tcl_recursion.py:156`](../cbg/tcl_recursion.py)).
  - `cbg.tcl_recursion.L_n_dissipator_*` at n=4 (B.3 partial extends automatically once B.2 n=4 lands).
- Currently stubbed but **deferred to a future card**:
  - `cbg.diagnostics.tcl_invertibility_distance` (Λ_t reconstruction). D1 v0.1.1 records `‖Λ_t − id‖ ≥ 1` in `result.notes` only when this becomes available; until then the field is omitted.
- SCHEMA.md v0.1.3 (sweep block specified). Possible future v0.1.4 patch: define `numerical.quadrature` formally with `upper_cutoff_factor` and `quad_limit` as the only allowed keys (currently accepted as permissive extras).
- `reporting.benchmark_card._refuse_dg4_sweep` (the present runner refusal path; replaced by `_run_dg4_sweep` when Phase C lands).

---

*Plan version: v0.1.4. Drafted 2026-05-06. Supersedes v0.1.3 to address: (1) the parity-blindness of the adjacent-order ratio in σ_x thermal (Phase B.3 finding `‖L_3^dis‖ = 0`); (2) the placement ambiguity of the `omega_c` perturbation (model-spec mutation, NOT routed through `numerical.quadrature`). CC-BY-4.0 (see ../LICENSE-docs).*

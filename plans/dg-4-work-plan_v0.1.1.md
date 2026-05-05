---
plan_id: dg-4-work-plan
version: v0.1.1
date: 2026-05-05
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§9 (DG-4), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entry 2 (recursive-series convergence; COMPATIBLE, scope-limited)
anchor_envelope: docs/validity_envelope.md DG-4 row (SCOPED — runner refusal path wired → target PASS)
status: draft
supersedes: dg-4-work-plan_v0.1.0.md
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Work Plan — Failure-envelope identification

## Supersedure note

v0.1.1 supersedes v0.1.0 to address five structural deficiencies surfaced by review of the v0.1.0 commit (`23c4057`). The deficiencies were:

1. **Reproducibility-tolerance unit mismatch** (v0.1.0 §3 Phase C said "10× to 1e-11"; D1 v0.1.0 freezes "10% tightening"). The plan is now consistent with the frozen card; runner must consume the card's value verbatim.
2. **Reproducibility perturbations not operational.** The CBG path uses `scipy.integrate.quad` for bath correlations and does not consume `bath_mode_cutoff`; `integration_tolerance` is not threaded through `D̄_2`, `bath_two_point_thermal_array`, or the trapezoidal TCL integration. v0.1.0 silently presumed both knobs were active. v0.1.1 introduces Phase B.4 to make a defined set of perturbation knobs operational, and recommends D1 supersedure (Phase A.bis) to freeze knobs that are *actually* perturbable.
3. **K_n weak-probe in pure-dephasing thermal.** For A = σ_z and a thermal Gaussian bath, the Letter App. D parity-class theorem gives K_{2m} = 0; thermal D̄_1 = 0 forces K_{2m+1} = 0 too. So K_n = 0 for all n ≥ 1, and the convergence-ratio metric `r_n = ⟨‖K_n‖⟩ / ⟨‖K_{n−1}‖⟩` becomes 0/0 (numerical noise). v0.1.0 missed this. v0.1.1 recommends D1 supersedure to use the *dissipator part* of L_n (which carries the actual dephasing physics in this model) instead of K_n, OR alternatively to switch to the σ_x model where K_n is non-trivial; Phase A.bis decides between the two.
4. **TCL-singularity route ambiguity.** v0.1.0 said D1 targets `convergence failure` (§4) but R5 allowed PASS with cause `TCL singularity`. Also `cbg.diagnostics.tcl_invertibility_distance` is stubbed, so D1 cannot in fact detect a TCL singularity at runner-time. v0.1.1 removes the R5 PASS allowance: TCL singularity is logged in `result.notes` as a *runner observation* but does not gate D1's PASS verdict. Λ_t reconstruction belongs to a separate cause-label card (D2 or later) once `tcl_invertibility_distance` is implemented.
5. **Phase B missing leaf layer.** v0.1.0's Phase B jumped to D̄_3, D̄_4 directly. The recursion in Letter Eq. (17) requires raw ordered n-point bath correlations (`cbg.bath_correlations.n_point_ordered`, currently stubbed) AND `cbg.cumulants.D_bar` extension to mixed left/right indices and n ≥ 3 (also stubbed). v0.1.1 adds Phase B.0 (raw correlations) explicitly before B.1 (extended D̄ recursion).

The §1 Objective and §2 Scope are otherwise unchanged from v0.1.0; the substantive edits are concentrated in §3 Phases, §4 Acceptance criteria, §5 Risks, and §6 Dependencies.

## 1. Objective

Pass DG-4 as defined in Sail v0.5 §9:

> *Pass if at least one reproducible, cause-labelled regime is identified in which the implementation fails or yields ambiguous output.*

DG-4 is the only Decision Gate where **PASS requires a failure to occur**. It operationalises CL-2026-005 v0.4 Entry 2's open convergence question by demanding evidence that the implementation *actually exhibits* breakdown in some regime, not merely that breakdown is possible in principle. A passed DG-4 narrows the validity envelope; a stuck-on-PASS implementation that never finds a failure regime fails DG-4 by virtue of being insufficiently probed.

This plan operationalises that objective in **benchmark-cards-first** ordering, extending the discipline established in DG-1, DG-2, and DG-3. Card D1 v0.1.0 is frozen (`benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.0.yaml`); Phase A.bis below supersedes it to D1 v0.1.1 to fix the K_n weak-probe deficiency, and Phases B–D operationalise the corrected card.

### 1.1 Cards-first context

D1 v0.1.0 freezes a `coupling_strength` sweep (0.05 → 1.0 log-uniform, 20 points) over the pure-dephasing model and targets cause label `convergence failure`. Two of its design choices are problematic at this point in the implementation effort and will be re-frozen by D1 v0.1.1 in Phase A.bis:

- **Convergence metric.** v0.1.0 specifies `r_n = ⟨‖K_n‖⟩ / ⟨‖K_{n−1}‖⟩`. For A = σ_z + thermal Gaussian bath, all K_n with n ≥ 1 are zero (parity + odd-cumulant vanishing), so r_n is 0/0. D1 v0.1.1 will replace ‖K_n‖ with the *dissipator part* of L_n — the non-Hamiltonian piece of the TCL generator that carries the actual dephasing rate. The recommended form is

      L_n^dissipator(t) := L_n(t) - i [K_n(t), · ]

  with `r_n = ⟨‖L_n^dissipator‖⟩_t / ⟨‖L_{n−1}^dissipator‖⟩_t`. The alternative — switching to the σ_x model — is documented in §3 Phase A.bis but rejected as the primary path because (a) it breaks A3/B4 parameter inheritance and (b) σ_x dynamics conflate energy relaxation with dephasing, blurring the convergence question.
- **Reproducibility-perturbation knobs.** v0.1.0 freezes `bath_mode_cutoff` ±1 and `integration_tolerance` 10% tightening. Neither is operational on the CBG path. D1 v0.1.1 will replace these with knobs that ARE operational: `bath_two_point_thermal.quad_limit` (default 200, perturb to 100 / 400) and `bath_two_point_thermal.upper_cutoff_factor` (default 30, perturb to 20 / 40). These are quadrature-truncation knobs that genuinely change the computed correlator.

D1 v0.1.0's status reverts to `superseded` in Phase A.bis. The supersedure is steward-side (no Council deliberation): both deficiencies are runner-discovery findings, not Ledger-bearing facts.

### 1.2 PASS-on-failure asymmetry from DG-1/2/3

DG-1, DG-2, and DG-3 PASS when their cards' acceptance criteria are met. DG-4 PASSES when D1 v0.1.1 produces a verdict like:

> "α_crit ≈ 0.42 ± 0.05 (interpolated boundary between last α with `r_3 < 1` and first α with `r_3 > 1`); cause label `convergence failure` confirmed reproducible under quad_limit ±100 and upper_cutoff_factor ±10 perturbation."

A verdict like "no α in the swept range produced r_n > 1" is **not** a DG-4 PASS. The cards-first / Risk #8 discipline requires *supersedure* (D2 with extended range), not in-place range-tightening. See Risk R3.

## 2. Scope

### 2.1 In scope

- **Phase A.bis:** supersede D1 v0.1.0 → D1 v0.1.1 with the L_n^dissipator metric and operational reproducibility-perturbation knobs.
- **Phase B:** the four-sub-phase TCL-recursion extension (B.0 → B.4 below).
- **Phase C:** sweep-block-aware runner branch consuming `frozen_parameters.sweep`. New private helper `_run_dg4_sweep` in `reporting/benchmark_card.py`, dispatched from `run_card` *before* the present `_refuse_dg4_sweep` (which is removed when Phase C lands and tests pass).
- Reproducibility-check infrastructure: the runner re-executes D1 with perturbed `quad_limit` and `upper_cutoff_factor` to support per-α classification.
- Cause-label assignment per the §1.1 taxonomy (one of the five Sail v0.5 §9 labels), written into `result.notes`.
- Boundary `α_crit` interpolation (linear in `log α`) when both passing and failing α exist in the swept range.
- Phase D verdict commit: populate D1 v0.1.1's `result` block, fill `commit_hash` self-referentially, update `docs/validity_envelope.md`, write `logbook/YYYY-MM-DD_dg-4-{pass,fail-with-cause}.md`, repository tag.

### 2.2 Out of scope

- Other cause labels (#3 `projection ambiguity`, #5 `benchmark disagreement`): require cross-method data — DG-3 territory — and would be future failure-envelope cards (D3, D4, …).
- **Cause label #2 `TCL singularity`:** logged as a runner observation in `result.notes` if `‖Λ_t − id‖ ≥ 1` is detected at runtime, but does NOT gate D1's PASS verdict (see §5 R5). Implementing Λ_t reconstruction and a singularity-targeted card is a separate work item.
- Multi-parameter sweeps (e.g. α × T): future cards.
- Models other than `pure_dephasing`: future cards.
- Re-classification of CL-2026-005 v0.4 Entry 2: D1's verdict feeds the validity envelope, not the Ledger. Council route only.

### 2.3 Explicit non-claims

DG-4 PASS does **not** establish:

- That α_crit is a property of the analytical theory rather than the implementation under D1 v0.1.1's frozen scaffold.
- That smaller perturbative orders are convergent for *all* α ≤ α_crit. The verdict is about the order at which divergence first appears under the L_n^dissipator metric.
- That the discrete finite-bath truncation in any DG-3 cross-method handler is converged at α ≤ α_crit. The two questions (perturbative-series convergence vs. finite-bath truncation) are independent.

## 3. Phases

### Phase A — Card drafting (already complete)

D1 v0.1.0 frozen 2026-05-05. Note: superseded by Phase A.bis below.

### Phase A.bis — Supersede D1 v0.1.0 → D1 v0.1.1

- Draft `D1_failure-envelope-convergence_v0.1.1.yaml` with:
  - `comparison.target_observable: "L_n^dissipator(t) norm ratio ||L_n^dissipator|| / ||L_{n-1}^dissipator||"`.
  - `comparison.error_metric: "convergence_ratio"` (unchanged label; semantics now over L_n^dissipator).
  - Reproducibility specification: perturb `quad_limit` by ±100 (200 → 100 / 400) AND `upper_cutoff_factor` by ±10 (30 → 20 / 40). Drop `bath_mode_cutoff` and `integration_tolerance` from the perturbation list (they are non-operational on the CBG path).
  - `failure_mode_log` entry citing v0.1.0's two deficiencies (K_n parity + non-operational knobs) as the supersedure reason; `predecessor_card_id: D1`, `predecessor_version: v0.1.0`.
- Annotate D1 v0.1.0 with `superseded_by: D1_failure-envelope-convergence_v0.1.1.yaml` and `status: superseded`.

**Alternative considered (and rejected):** switch the model from `pure_dephasing` to `spin_boson_sigma_x`. Rejected because (a) it breaks A3/B4 parameter inheritance, complicating the cross-card audit trail, and (b) σ_x couples to ±ω_S transitions and conflates energy relaxation with dephasing, making the convergence question harder to interpret. The L_n^dissipator path keeps the same model and isolates the convergence question to the dissipator's perturbative growth.

### Phase B — TCL recursion at orders 3 and 4

Decomposed into four sub-phases to keep each commit reviewable:

- **B.0 — Raw ordered n-point correlations.** Implement `cbg.bath_correlations.n_point_ordered` for `n ∈ {3, 4}` on thermal Gaussian baths. Currently stubbed; the recursion in Letter Eq. (17) / Companion Eq. (27) requires these as the leaf inputs. For Gaussian baths, n-point correlations factor into products of two-point correlators by Wick's theorem; B.0 implements this contraction.
- **B.1 — Extend D̄ recursion to mixed left/right indices and n ≥ 3.** The current `D_bar` rejects mixed indices and `n ≥ 3` (multiple `NotImplementedError` raises in `cbg/cumulants.py`). Implement `D̄(τ_1^k, s_1^{n−k}) = D − Σ_{l,r} D̄(τ_1^l, s_1^r) D̄(τ_{l+1}^k, s_{r+1}^{n−k})` for `n ∈ {3, 4}`.
- **B.2 — K_3, K_4 wired through K_n_thermal_on_grid.** Extend `cbg.tcl_recursion.K_n_thermal_on_grid` to support `n ∈ {3, 4}`. Verify against existing DG-1/2 fixtures: K_3 and K_4 should be identically zero on A3/A4 thermal fixtures by parity (this is the cross-check that motivates D1's metric switch in Phase A.bis).
- **B.3 — L_n dissipator extraction.** Compute `L_n^dissipator = L_n − i [K_n, ·]` per the convention in §1.1. Lives in `cbg.tcl_recursion` next to the K_n path.
- **B.4 — Knob-threading for reproducibility checks.** Thread `quad_limit` and `upper_cutoff_factor` from the model_spec (or a dedicated runner-options block) through `bath_two_point_thermal`, `bath_two_point_thermal_array`, and the TCL recursion. Without this, the Phase C runner cannot perform D1 v0.1.1's reproducibility perturbations.

### Phase C — Sweep runner wiring

- Add `_run_dg4_sweep(card)` in `reporting/benchmark_card.py`. Dispatch from `run_card` BEFORE `_refuse_dg4_sweep` (and remove the refusal path once tests pass).
- The sweep runner:
  - Iterates over swept α values per `frozen_parameters.sweep.sweep_range`.
  - For each α, builds a `model_spec` with the swept value injected at `model.bath_spectral_density.coupling_strength`.
  - Evaluates K_n and L_n^dissipator at orders 0–4 via Phase B's extended recursion.
  - Computes `r_n = ⟨‖L_n^dissipator‖⟩ / ⟨‖L_{n−1}^dissipator‖⟩`.
  - **Zero-denominator policy:** if `‖L_{n−1}^dissipator‖ < ε_machine × ‖L_0^dissipator‖`, mark the α as `metric-undefined` and exclude it from the convergence-failure classification. (This guards against any residual parity-driven cancellation.)
  - Tags each α as `passing`, `failing-candidate`, or `metric-undefined`.
- For each `failing-candidate` α, run reproducibility checks under perturbed `quad_limit` (100, 400) and `upper_cutoff_factor` (20, 40) per D1 v0.1.1's frozen rule. Reclassify per §5 R6 below.
- If `‖Λ_t − id‖ ≥ 1` is detected (via `cbg.diagnostics.tcl_invertibility_distance` once that lands), record it in `result.notes` but do not change the per-α classification — TCL singularity is observation-only at D1 v0.1.1.

### Phase D — Verdict

- Run D1 v0.1.1 end-to-end via the Phase C runner.
- Populate `result.verdict`, `result.evidence`, `result.runner_version`, `result.notes` (cause-label classification per α, α_crit interpolation, reproducibility-check outcomes, any TCL-singularity observations).
- Logbook entry; validity-envelope update; self-referential `commit_hash` follow-up.
- Repository tag (`v0.5.0` on PASS; appropriate dev bump otherwise).

## 4. Acceptance criteria

PASS for DG-4 requires D1 v0.1.1 to verdict to PASS, which requires:

1. The Phase C runner runs to completion across the full swept range without raising.
2. At least one α in the range is classified `convergence failure` (i.e. `r_n > 1` AND stable under reproducibility perturbation per D1 v0.1.1's frozen specification).
3. The cause label, the per-α `r_n` values, and the boundary `α_crit` interpolation are all recorded in `result.notes`.

A FAIL verdict is admissible iff the runner runs to completion AND no α is classified `convergence failure`. The result must report `verdict: FAIL` with cause `no-failure-found-in-frozen-range` AND a routing note: per Risk R3, the response is supersedure (D2 with extended range), not in-place range-tightening of D1.

CONDITIONAL is admissible iff all candidate α values are classified `truncation artefact` rather than `convergence failure`; the `result.notes` must explain the reproducibility-knob coverage gap.

**TCL singularity at D1 v0.1.1 is observational, not gating.** A run that hits `‖Λ_t − id‖ ≥ 1` for some α records it in `result.notes` but classifies that α according to its convergence-ratio outcome (or `metric-undefined` if both ratios collapse). DG-4 PASS via TCL singularity is a future-card concern (R5).

## 5. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **R1: Phase B is large.** Extending TCL recursion to orders 3 and 4 is also the canonical-unfilled DG-2 milestone. The bookkeeping for the generalised-cumulant recursion at higher orders is non-trivial, and three of the four leaf modules (`n_point_ordered`, mixed-index `D_bar`, n ≥ 3 `D_bar`) are currently stubbed. | Decompose into B.0 → B.4 (see §3 Phase B). Land each sub-commit independently with stand-alone tests. B.0 and B.1 are independent of D1 and can land before Phase A.bis. |
| **R2: Reproducibility-check cost.** Each `failing-candidate` α is re-run twice for `quad_limit` and twice for `upper_cutoff_factor` — up to ~80 K_n + L_n evaluations at order 4 across the 20-α sweep. | Cache K_n / L_n arrays; document the cost in the runner; consider a `--quick` mode (CONDITIONAL verdict only) for development iteration. |
| **R3: PASS-by-supersedure temptation.** If the swept range yields no `convergence failure`, the temptation is to extend the range *in place* and re-run. This is a Risk #8 violation. | The acceptance criterion in §4 *explicitly* allows a FAIL with cause `no-failure-found-in-frozen-range`. The response is a *new card* D2 with an extended range, not a silent edit of D1. The Phase D verdict commit must include a routing note if this path is taken. |
| **R4: Truncation-artefact dominance.** If most candidate α values reclassify as truncation artefacts under the reproducibility check, D1 lands CONDITIONAL with no informative DG-4 finding. | Quad knobs (`quad_limit`, `upper_cutoff_factor`) are the operational ones; if their perturbations dominate, the response is a new card D3 with tighter quadrature defaults and a `failure_mode_log` entry citing the artefact dominance. |
| **R5: TCL singularity is observational only at D1 v0.1.1.** Plan v0.1.0 erroneously allowed PASS with cause `TCL singularity`, but `cbg.diagnostics.tcl_invertibility_distance` is stubbed and Λ_t reconstruction would itself be substantial work. v0.1.1 demotes TCL singularity to a *recorded observation* in `result.notes`; D1 PASS gates only on `convergence failure`. | A future card (D2 or later) — accompanied by a Λ_t reconstruction implementation and its own work-plan revision — can target cause label `TCL singularity` as a primary PASS path. Until then, D1 does not gate on it. |
| **R6: Reproducibility-knob operationality.** D1 v0.1.0's perturbation knobs (`bath_mode_cutoff`, `integration_tolerance`) are not threaded through the CBG code paths and silently no-op. v0.1.1 fixes this by (a) Phase A.bis re-freezing D1 to use `quad_limit` and `upper_cutoff_factor` (which ARE operational once Phase B.4 threads them), and (b) Phase B.4 making them runner-consumable. | Phase B.4 must include a smoke test that perturbing `quad_limit` from 200 to 100 actually changes the computed `bath_two_point_thermal` value at a representative `(t, alpha, omega_c, T)` tuple. If the change is below numerical noise, the knob is still effectively non-operational and a different perturbation (e.g. `omega_c` itself) must be considered. |
| **R7: K_n is identically zero in pure-dephasing thermal.** Surfaced by review of v0.1.0; the parity-class theorem (Letter App. D) plus thermal D̄_1 = 0 forces K_n = 0 for all n ≥ 1. v0.1.1's L_n^dissipator metric resolves this for the σ_z model. | Phase B.2 includes the explicit cross-check that K_n = 0 on A3/A4 fixtures for n ≥ 1 — this serves both as a recursion-correctness test and as the empirical confirmation of the v0.1.0 metric flaw. |

## 6. Dependencies

- DG-1 PASS (completed 2026-04-30, tag `v0.2.0`).
- DG-2 structural sub-claims PASS (completed 2026-05-04). The DG-2 "literal K_2–K_4 numerical recursion" milestone is *unblocked by Phase B*; B.2's commit message should also update `docs/validity_envelope.md` DG-2 row.
- D1 v0.1.1 supersedure (Phase A.bis): must land before Phase C consumes the new metric and reproducibility knobs. Phase B.0 and B.1 are independent and can land first.
- Currently stubbed pieces that this plan delivers:
  - `cbg.bath_correlations.n_point_ordered` (B.0).
  - `cbg.cumulants.D_bar` extension to mixed left/right indices and n ≥ 3 (B.1).
  - `cbg.tcl_recursion.K_n_thermal_on_grid` at n ∈ {3, 4} (B.2).
  - L_n^dissipator extraction in `cbg.tcl_recursion` (B.3).
  - Knob-threading for `quad_limit` / `upper_cutoff_factor` (B.4).
- Currently stubbed but **deferred to a future card** (not in this plan):
  - `cbg.diagnostics.tcl_invertibility_distance` (Λ_t reconstruction). D1 v0.1.1 records `‖Λ_t − id‖ ≥ 1` in `result.notes` only when this becomes available; until then the field is omitted.
- SCHEMA.md v0.1.3 (sweep block already specified; no further schema work needed for D1 v0.1.x).
- `reporting.benchmark_card._refuse_dg4_sweep` (the present runner refusal path; replaced by `_run_dg4_sweep` when Phase C lands).

---

*Plan version: v0.1.1. Drafted 2026-05-05. Supersedes v0.1.0 per the structural deficiencies enumerated in the Supersedure note above. CC-BY-4.0 (see ../LICENSE-docs).*

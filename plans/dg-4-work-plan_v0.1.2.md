---
plan_id: dg-4-work-plan
version: v0.1.2
date: 2026-05-05
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§9 (DG-4), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entry 2 (recursive-series convergence; COMPATIBLE, scope-limited)
anchor_envelope: docs/validity_envelope.md DG-4 row (SCOPED — runner refusal path wired → target PASS)
status: draft
supersedes: dg-4-work-plan_v0.1.1.md
superseded_by: dg-4-work-plan_v0.1.3.md
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Work Plan — Failure-envelope identification

## Supersedure note

v0.1.2 supersedes v0.1.1 to address two follow-up issues surfaced by review of the v0.1.1 commit (`e85fd70`). The five v0.1.0 deficiencies remain addressed; v0.1.2 fixes:

1. **Dissipator-extraction sign error.** v0.1.1 §1.1 and §3 Phase B.3 defined `L_n^dissipator := L_n - i[K_n, ·]`. The repository convention is `L[X] = -i[K, X] + dissipator` (see [`cbg/effective_hamiltonian.py:82`](../cbg/effective_hamiltonian.py) and the unitary-recovery test at [`tests/test_effective_hamiltonian.py:59`](../tests/test_effective_hamiltonian.py)). The dissipator residual is therefore `L_n^dissipator := L_n + i[K_n, ·]`, with the opposite sign on the commutator subtraction. v0.1.1's sign would have produced 2 × the Hamiltonian piece on the LHS rather than a vanishing residual when the generator is purely unitary.
2. **Pure-dephasing thermal is TCL-2 exact.** v0.1.1 recommended switching the convergence-ratio metric from `‖K_n‖` to `‖L_n^dissipator‖`, on the assumption that `L_n` would be non-trivial where `K_n` vanished by parity. That assumption is wrong: for σ_z coupling to a thermal Gaussian bath, the entire TCL series truncates at order 2 (Feynman-Vernon influence-functional exactness for bilinear coupling to a Gaussian bath), so `L_n = 0` identically for `n ≥ 3`. The metric is undefined for the same fundamental reason whether it is over `K_n` or `L_n^dissipator`. v0.1.2 therefore changes Phase A.bis to switch D1's *model* to `spin_boson_sigma_x` (σ_x coupling), where `[H_S, A] ≠ 0` keeps the TCL series non-trivial at all orders and the convergence-ratio metric is meaningful.

The §1 Objective and §2 Scope shape are unchanged from v0.1.1; the substantive edits are concentrated in the Supersedure note above, §3 Phase A.bis, and the Risk R7 / R8 reframing.

## 1. Objective

Pass DG-4 as defined in Sail v0.5 §9:

> *Pass if at least one reproducible, cause-labelled regime is identified in which the implementation fails or yields ambiguous output.*

DG-4 is the only Decision Gate where **PASS requires a failure to occur**. It operationalises CL-2026-005 v0.4 Entry 2's open convergence question by demanding evidence that the implementation *actually exhibits* breakdown in some regime, not merely that breakdown is possible in principle.

This plan operationalises that objective in **benchmark-cards-first** ordering. Card D1 v0.1.0 is frozen; Phase A.bis below supersedes it to D1 v0.1.1 with both a model switch (`pure_dephasing` → `spin_boson_sigma_x`) and a metric switch (`‖K_n‖` → `‖L_n^dissipator‖` with the correct sign), and Phases B–D operationalise the corrected card.

### 1.1 Cards-first context

D1 v0.1.0 freezes a `coupling_strength` sweep over the pure-dephasing model and targets cause label `convergence failure`. Three of its design choices need re-freezing in Phase A.bis:

- **Model.** v0.1.0 uses `pure_dephasing` (A = σ_z). For thermal Gaussian baths, this model has TCL-2 exact reduced dynamics: `L_n = 0` for all `n ≥ 3` by Gaussianity, and `L_1 = 0` because thermal `D̄_1 = 0`. The convergence-ratio metric `r_n = ⟨‖L_n‖⟩ / ⟨‖L_{n−1}‖⟩` is therefore identically `0/0` for `n ≥ 3` regardless of which observable (`K_n` or `L_n^dissipator`) is chosen. D1 v0.1.1 will switch to `spin_boson_sigma_x` (A = σ_x), which inherits the parameter scaffold from cards A4 v0.1.1 and B5-conv-registry v0.2.0 (parallel to A3/B4 inheritance) and where `[H_S, A] ≠ 0` keeps the TCL series non-trivial at every order.
- **Convergence metric.** The metric is the time-averaged Frobenius norm of the *dissipator part* of L_n, defined with the repository's sign convention `L[X] = -i[H, X] + dissipator`:

      L_n^dissipator(t) := L_n(t) + i [K_n(t), · ]

  with `r_n = ⟨‖L_n^dissipator‖⟩_t / ⟨‖L_{n−1}^dissipator‖⟩_t`. The sign is such that for a purely unitary L_n, `L_n^dissipator = 0` exactly. v0.1.1's sign (`L_n - i[K_n,·]`) was the opposite and would have produced `2 × Hamiltonian-part` rather than the dissipator residual.
- **Reproducibility-perturbation knobs.** Same as v0.1.1: `bath_two_point_thermal.quad_limit` (default 200, perturb to 100 / 400) and `bath_two_point_thermal.upper_cutoff_factor` (default 30, perturb to 20 / 40). v0.1.0's `bath_mode_cutoff` and `integration_tolerance` are dropped from the perturbation list (non-operational on the CBG path).

D1 v0.1.0's status reverts to `superseded` in Phase A.bis. The supersedure is steward-side: all three changes are runner-discovery / mathematical-physics findings, not Ledger-bearing facts.

### 1.2 PASS-on-failure asymmetry from DG-1/2/3

DG-1, DG-2, and DG-3 PASS when their cards' acceptance criteria are met. DG-4 PASSES when D1 v0.1.1 produces a verdict like:

> "α_crit ≈ 0.42 ± 0.05 (interpolated boundary between last α with `r_3 < 1` and first α with `r_3 > 1`); cause label `convergence failure` confirmed reproducible under quad_limit ±100 and upper_cutoff_factor ±10 perturbation."

A verdict like "no α in the swept range produced r_n > 1" is **not** a DG-4 PASS. The cards-first / Risk #8 discipline requires *supersedure* (D2 with extended range), not in-place range-tightening. See Risk R3.

## 2. Scope

### 2.1 In scope

- **Phase A.bis:** supersede D1 v0.1.0 → D1 v0.1.1 with the σ_x model, the L_n^dissipator metric (correct sign), and operational reproducibility-perturbation knobs. Includes a small pilot check (see §3 Phase A.bis) confirming the metric is non-trivial in the chosen model.
- **Phase B:** four-sub-phase TCL-recursion extension (B.0 → B.4 below).
- **Phase C:** sweep-block-aware runner branch consuming `frozen_parameters.sweep`. New private helper `_run_dg4_sweep` in `reporting/benchmark_card.py`, dispatched from `run_card` *before* the present `_refuse_dg4_sweep` (which is removed when Phase C lands).
- Reproducibility checks per D1 v0.1.1's frozen rule.
- Cause-label assignment per the Sail v0.5 §9 taxonomy (one of the five labels), written into `result.notes`.
- Boundary `α_crit` interpolation (linear in `log α`).
- Phase D verdict commit.

### 2.2 Out of scope

- Other cause labels (#3 `projection ambiguity`, #5 `benchmark disagreement`): require cross-method data — DG-3 territory; future cards.
- Cause label #2 `TCL singularity`: logged as a runner observation in `result.notes` if `‖Λ_t − id‖ ≥ 1` is detected, but does NOT gate D1's PASS verdict (R5).
- Multi-parameter sweeps; models other than `spin_boson_sigma_x`; re-classification of CL-2026-005 v0.4 Entry 2.

### 2.3 Explicit non-claims

Same as v0.1.1; DG-4 PASS does not establish that α_crit is theory-intrinsic, that lower orders are convergent for all α below it, or that finite-bath truncations in DG-3 handlers are converged at α ≤ α_crit.

## 3. Phases

### Phase A — Card drafting (already complete)

D1 v0.1.0 frozen 2026-05-05. Note: superseded by Phase A.bis below.

### Phase A.bis — Supersede D1 v0.1.0 → D1 v0.1.1

- Draft `D1_failure-envelope-convergence_v0.1.1.yaml` with:
  - `model: "spin_boson_sigma_x"` (changed from `pure_dephasing`).
  - `frozen_parameters.model.coupling_operator: "sigma_x"`.
  - `frozen_parameters.model.system_hamiltonian: "(omega / 2) * sigma_z"` (unchanged; the σ_x coupling acts on this same bare system Hamiltonian).
  - Parameter inheritance: bath_spectral_density and time_grid from A4 v0.1.1; perturbative_order, basis, bath_mode_cutoff, integration_tolerance, solver from D1 v0.1.0 (the parts that didn't depend on the model).
  - `comparison.target_observable: "L_n^dissipator(t) norm ratio ||L_n^dissipator|| / ||L_{n-1}^dissipator||"` with `L_n^dissipator := L_n + i [K_n, ·]`.
  - `comparison.error_metric: "convergence_ratio"`.
  - Reproducibility specification: perturb `quad_limit` by ±100 (200 → 100, 400) AND `upper_cutoff_factor` by ±10 (30 → 20, 40). Drop `bath_mode_cutoff` and `integration_tolerance` from the perturbation list.
  - `failure_mode_log` entry citing v0.1.0's three flagged deficiencies (model-induced TCL-2 exactness, K_n parity-vanishing, non-operational knobs) as the supersedure reason; `predecessor_card_id: D1`, `predecessor_version: v0.1.0`.
- Annotate D1 v0.1.0 with `superseded_by: D1_failure-envelope-convergence_v0.1.1.yaml` and `status: superseded`.
- **Pilot check** (lands in the same commit or as a stand-alone follow-up before Phase C consumes the metric): a small numerical experiment confirming that, in the σ_x + thermal Gaussian model at α = 0.05 (the lower end of the swept range), `‖L_3^dissipator‖_t > 0` to numerical precision. The check uses Phase B.3 once that lands; if `L_3^dissipator = 0` numerically, the pilot fails and Phase A.bis must consider a different model (e.g. coherent-displaced bath, or non-Gaussian bath state). The pilot may be folded into Phase B.2 / B.3's commit message as a "metric well-defined" observation.
- **Schema/docs minor follow-up** (not in this commit; flagged for a future SCHEMA.md v0.1.4 bump): if `quad_limit` and `upper_cutoff_factor` go into `frozen_parameters.numerical`, consider naming the block (e.g. `numerical.quadrature`) for forward compatibility. The runner's `validate_card_data` is permissive on extras today, but the schema prose does not currently define a quadrature sub-block. v0.1.2 of this plan does NOT block on the schema bump; D1 v0.1.1 may carry the perturbation knobs under an ad-hoc `numerical.quadrature` extras key with an inline comment, and the schema bump can land later.

### Phase B — TCL recursion at orders 3 and 4

Decomposed identically to v0.1.1:

- **B.0 — Raw ordered n-point correlations.** Implement `cbg.bath_correlations.n_point_ordered` for `n ∈ {3, 4}` on thermal Gaussian baths. For Gaussian baths the n-point correlations factor by Wick's theorem; B.0 implements this contraction.
- **B.1 — Extend D̄ recursion to mixed left/right indices and n ≥ 3.** Currently `D_bar` rejects mixed indices and `n ≥ 3`. Implement Letter Eq. (17) recursion for `n ∈ {3, 4}`.
- **B.2 — K_3, K_4 wired through K_n_thermal_on_grid.** Verify against existing DG-1/2 fixtures: K_3 and K_4 should be identically zero on A3/A4 thermal fixtures by parity (this is the cross-check that motivates Phase A.bis's σ_x model switch).
- **B.3 — L_n dissipator extraction.** Compute `L_n^dissipator = L_n + i [K_n, ·]` per the corrected sign convention. Lives in `cbg.tcl_recursion` next to the K_n path.
- **B.4 — Knob-threading for reproducibility checks.** Thread `quad_limit` and `upper_cutoff_factor` from the model_spec (or a dedicated runner-options block) through `bath_two_point_thermal`, `bath_two_point_thermal_array`, and the TCL recursion. Includes a smoke test (per Risk R6) confirming that perturbing `quad_limit` from 200 to 100 actually changes the computed correlator at a representative tuple.

### Phase C — Sweep runner wiring

- Add `_run_dg4_sweep(card)` in `reporting/benchmark_card.py`. Dispatch from `run_card` BEFORE `_refuse_dg4_sweep` (and remove the refusal path once tests pass).
- The sweep runner:
  - Iterates over swept α values per `frozen_parameters.sweep.sweep_range`.
  - For each α, builds a `model_spec` with the swept value injected at `model.bath_spectral_density.coupling_strength`.
  - Evaluates K_n and L_n^dissipator at orders 0–4 via Phase B.
  - Computes `r_n = ⟨‖L_n^dissipator‖⟩ / ⟨‖L_{n−1}^dissipator‖⟩`.
  - **Zero-denominator policy:** if `‖L_{n−1}^dissipator‖ < ε_machine × ‖L_2^dissipator‖`, mark the α as `metric-undefined` and exclude from convergence-failure classification.
  - Tags each α as `passing`, `failing-candidate`, or `metric-undefined`.
- Per-α reproducibility checks under perturbed `quad_limit` (100, 400) and `upper_cutoff_factor` (20, 40); reclassify per §5 R6.
- Λ_t-singularity observations recorded in `result.notes` only (R5).

### Phase D — Verdict

- Run D1 v0.1.1 end-to-end via the Phase C runner.
- Populate `result.verdict`, `result.evidence`, `result.runner_version`, `result.notes`.
- Logbook entry; validity-envelope update; self-referential `commit_hash` follow-up.
- Repository tag (`v0.5.0` on PASS; appropriate dev bump otherwise).

## 4. Acceptance criteria

PASS for DG-4 requires D1 v0.1.1 to verdict to PASS, which requires:

1. The Phase C runner runs to completion across the full swept range without raising.
2. At least one α in the range is classified `convergence failure` (i.e. `r_n > 1` AND stable under reproducibility perturbation per D1 v0.1.1's frozen specification).
3. The cause label, the per-α `r_n` values, and the boundary `α_crit` interpolation are all recorded in `result.notes`.

A FAIL verdict is admissible iff the runner runs to completion AND no α is classified `convergence failure`. The result must report `verdict: FAIL` with cause `no-failure-found-in-frozen-range` AND a routing note: per Risk R3, the response is supersedure (D2 with extended range), not in-place range-tightening of D1.

CONDITIONAL is admissible iff all candidate α values are classified `truncation artefact` rather than `convergence failure`; the `result.notes` must explain the reproducibility-knob coverage gap.

**TCL singularity at D1 v0.1.1 is observational, not gating.** A future card (with Λ_t reconstruction) targets it as a primary cause label.

## 5. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **R1: Phase B is large.** Three of four leaf modules (`n_point_ordered`, mixed-index `D_bar`, n ≥ 3 `D_bar`) are stubbed; bookkeeping for higher-order generalised cumulants is non-trivial. | Decompose into B.0 → B.4 (see §3 Phase B). Land each sub-commit independently with stand-alone tests. B.0 and B.1 are independent of D1 and can land before Phase A.bis. |
| **R2: Reproducibility-check cost.** Each `failing-candidate` α is re-run twice for `quad_limit` and twice for `upper_cutoff_factor` — up to ~80 K_n + L_n evaluations at order 4 across the 20-α sweep. | Cache K_n / L_n arrays; document the cost; consider a `--quick` mode (CONDITIONAL verdict only) for development. |
| **R3: PASS-by-supersedure temptation.** If the swept range yields no `convergence failure`, the temptation is to extend the range *in place*. Risk #8 violation. | §4 *explicitly* allows a FAIL with cause `no-failure-found-in-frozen-range`. Response is a *new card* D2, not a silent edit of D1. |
| **R4: Truncation-artefact dominance.** Most candidates reclassify as artefacts under the reproducibility check. | Quad knobs are the operational ones; if their perturbations dominate, response is a new card D3 with tighter quadrature defaults. |
| **R5: TCL singularity is observational only at D1 v0.1.1.** Plan v0.1.0 erroneously allowed PASS with cause TCL singularity, but `cbg.diagnostics.tcl_invertibility_distance` is stubbed and Λ_t reconstruction is itself substantial work. | TCL singularity recorded in `result.notes` only; D1 PASS gates only on `convergence failure`. A future card (D2 or later) — accompanied by a Λ_t reconstruction implementation — can target this label as a primary PASS path. |
| **R6: Reproducibility-knob operationality.** D1 v0.1.0's perturbation knobs (`bath_mode_cutoff`, `integration_tolerance`) are not threaded through the CBG code paths. v0.1.2 fixes this by Phase A.bis (re-freezing D1 to use `quad_limit` and `upper_cutoff_factor`) plus Phase B.4 (threading them). | Phase B.4 must include a smoke test that perturbing `quad_limit` from 200 to 100 actually changes the computed `bath_two_point_thermal` value at a representative tuple. If the change is below numerical noise, the knob is still effectively non-operational and a different perturbation (e.g. `omega_c` itself) must be considered. |
| **R7: K_n is identically zero in pure-dephasing thermal — and so is L_n for n ≥ 3.** Surfaced by review of v0.1.0 (K_n) and v0.1.1 (L_n^dissipator); the parity-class theorem + thermal D̄_1 = 0 + Gaussian Feynman-Vernon exactness force *all* perturbative orders ≥ 3 to vanish in the σ_z model with thermal Gaussian bath, regardless of which observable (K_n or L_n^dissipator) is chosen. | v0.1.2's Phase A.bis switches D1's *model* to `spin_boson_sigma_x`. For σ_x coupling, [H_S, σ_x] ≠ 0 keeps the perturbative series non-trivial: TCL-2 is *not* exact for σ_x + Gaussian bath (Bloch-Redfield is the order-2 *approximation*, not the exact result), so L_3, L_4 carry finite contributions. Phase A.bis includes the pilot check that confirms ‖L_3^dissipator‖ > 0 numerically before D1 v0.1.1 lands. |
| **R8: Dissipator-extraction sign.** v0.1.1 used `L_n - i[K_n, ·]`, which under the repository convention `L[X] = -i[H, X] + dissipator` produces `2 × Hamiltonian-part` instead of the dissipator residual. Surfaced by review of v0.1.1. | v0.1.2 corrects to `L_n^dissipator := L_n + i [K_n, ·]`. Phase B.3's commit must include a unit test on a known-pure-unitary L: `L_n^dissipator` equals zero to machine precision when L is `-i[H, ·]` and K is `H`. |

## 6. Dependencies

- DG-1 PASS (completed 2026-04-30, tag `v0.2.0`).
- DG-2 structural sub-claims PASS (completed 2026-05-04). Phase B unblocks the canonical-unfilled "literal K_2–K_4 numerical recursion" milestone.
- D1 v0.1.1 supersedure (Phase A.bis): must land before Phase C consumes the new model and metric. Phase B.0 and B.1 are independent and can land first.
- Currently stubbed pieces this plan delivers:
  - `cbg.bath_correlations.n_point_ordered` (B.0).
  - `cbg.cumulants.D_bar` extension to mixed left/right indices and n ≥ 3 (B.1).
  - `cbg.tcl_recursion.K_n_thermal_on_grid` at n ∈ {3, 4} (B.2).
  - L_n^dissipator extraction in `cbg.tcl_recursion` with the corrected sign (B.3).
  - Knob-threading for `quad_limit` / `upper_cutoff_factor` (B.4).
- Currently stubbed but **deferred to a future card**:
  - `cbg.diagnostics.tcl_invertibility_distance` (Λ_t reconstruction). D1 v0.1.1 records `‖Λ_t − id‖ ≥ 1` in `result.notes` only when this becomes available; until then the field is omitted.
- SCHEMA.md v0.1.3 (sweep block specified). Possible future v0.1.4 patch: define a `numerical.quadrature` sub-block to formally validate `quad_limit` / `upper_cutoff_factor` (currently accepted as extras by the permissive validator; flagged in §3 Phase A.bis).
- `reporting.benchmark_card._refuse_dg4_sweep` (the present runner refusal path; replaced by `_run_dg4_sweep` when Phase C lands).

---

*Plan version: v0.1.2. Drafted 2026-05-05. Supersedes v0.1.1 per the two issues enumerated in the Supersedure note above. CC-BY-4.0 (see ../LICENSE-docs).*

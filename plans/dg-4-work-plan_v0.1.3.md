---
plan_id: dg-4-work-plan
version: v0.1.3
date: 2026-05-06
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§9 (DG-4), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entry 2 (recursive-series convergence; COMPATIBLE, scope-limited)
anchor_envelope: docs/validity_envelope.md DG-4 row (SCOPED — Phase B partial → target PASS)
status: draft
supersedes: dg-4-work-plan_v0.1.2.md
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Work Plan — Failure-envelope identification

## Supersedure note

v0.1.3 supersedes v0.1.2 to record an empirical finding from Phase B.4 implementation (commit `c7e9999`) that bears on D1 v0.1.1's frozen reproducibility-perturbation set. The two v0.1.2 fixes (dissipator-extraction sign; σ_x model switch) and all five v0.1.0 deficiencies remain addressed. v0.1.3 narrows the load-bearing perturbation set:

- **`quad_limit` is a no-op witness for production-like tuples.** Direct measurement at `(α=0.05, ω_c=10, T=0.5)` and t-grid points typical of the C1 fixture shows that `scipy.integrate.quad` with `weight='cos'/'sin'` converges in well under 100 subintervals for the ohmic correlator. `quad_limit ∈ {100, 200, 400}` therefore gives bit-identical correlator values, and any "perturbation under quad_limit" check is degenerate. Risk R6 of v0.1.2 named exactly this case and prescribed substitution; this is R6 firing.
- **`upper_cutoff_factor` is genuinely perturbative** at the planned values `{20, 30, 40}` (visibly changes the correlator integrand support).
- **`omega_c` substitute.** A natural replacement perturbation that genuinely changes the spectrum is `omega_c` itself (e.g. `10 → 9 / 11`). This is *not* changing the spectral-density family or the model; it is an admissible runner-side perturbation under the same SCHEMA.md v0.1.3 sweep / reproducibility framing.

Phase A.bis's drafting of D1 v0.1.1 should freeze the load-bearing reproducibility perturbations as **{`upper_cutoff_factor`, `omega_c`}**, with `quad_limit` either dropped entirely or kept as an explicit null-result witness in `result.notes` (recording that the planned 100/200/400 sweep produced bit-identical values, confirming the SciPy-converges-fast regime).

The §1 Objective and §2 Scope shape are unchanged from v0.1.2; the substantive edits are in the Supersedure note above, §1.1 (third bullet), §1.2 (example verdict), §3 Phase A.bis (the D1 v0.1.1 spec), §3 Phase C (per-α reproducibility-check counts), and §5 R6 (empirical confirmation of the v0.1.2 risk).

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
- **Reproducibility-perturbation knobs (v0.1.3 update).** The load-bearing perturbations for D1 v0.1.1 are:
    - `bath_two_point_thermal.upper_cutoff_factor` (default 30, perturb to 20 / 40). Genuinely perturbative; verified post-Phase B.4 against a representative `(α, ω_c, T)` tuple.
    - `bath_spectral_density.cutoff_frequency` (`ω_c`; default 10.0, perturb to 9.0 / 11.0). Substitute for v0.1.2's `quad_limit`. Genuinely changes the bath spectrum (J(ω) = α ω exp(-ω/ω_c) shifts), so a stable convergence-failure classification under this perturbation is a meaningful witness.
  - **Dropped from the load-bearing set:** `quad_limit`. v0.1.2 originally specified `quad_limit ∈ {100, 200, 400}` as a perturbation, but Phase B.4 implementation showed that `scipy.integrate.quad` with `weight='cos'/'sin'` converges in well under 100 subintervals for production-like tuples, so the three values give bit-identical correlator values. D1 v0.1.1 may either (i) drop the knob entirely or (ii) keep it as a documented null-result witness (frozen sweep `100 / 200 / 400` recorded in `result.notes` with the expected outcome "bit-identical → SciPy-converges-fast regime"); either choice satisfies the Risk #8 record-keeping discipline.
  - v0.1.0's `bath_mode_cutoff` and `integration_tolerance` remain dropped from the perturbation list (non-operational on the CBG path).

D1 v0.1.0's status reverts to `superseded` in Phase A.bis. The supersedure is steward-side: all three changes are runner-discovery / mathematical-physics findings, not Ledger-bearing facts.

### 1.2 PASS-on-failure asymmetry from DG-1/2/3

DG-1, DG-2, and DG-3 PASS when their cards' acceptance criteria are met. DG-4 PASSES when D1 v0.1.1 produces a verdict like:

> "α_crit ≈ 0.42 ± 0.05 (interpolated boundary between last α with `r_3 < 1` and first α with `r_3 > 1`); cause label `convergence failure` confirmed reproducible under upper_cutoff_factor ±10 (30 → 20 / 40) and ω_c ±1 (10 → 9 / 11) perturbation."

A verdict like "no α in the swept range produced r_n > 1" is **not** a DG-4 PASS. The cards-first / Risk #8 discipline requires *supersedure* (D2 with extended range), not in-place range-tightening. See Risk R3.

## 2. Scope

### 2.1 In scope

- **Phase A.bis:** supersede D1 v0.1.0 → D1 v0.1.1 with the σ_x model, the L_n^dissipator metric (correct sign), and the v0.1.3 load-bearing reproducibility-perturbation knobs (`upper_cutoff_factor`, `omega_c`). Includes a small pilot check (see §3 Phase A.bis) confirming the metric is non-trivial in the chosen model.
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

Same as v0.1.2; DG-4 PASS does not establish that α_crit is theory-intrinsic, that lower orders are convergent for all α below it, or that finite-bath truncations in DG-3 handlers are converged at α ≤ α_crit.

## 3. Phases

### Phase A — Card drafting (already complete)

D1 v0.1.0 frozen 2026-05-05. Note: superseded by Phase A.bis below.

### Phase A.bis — Supersede D1 v0.1.0 → D1 v0.1.1

- Draft `D1_failure-envelope-convergence_v0.1.1.yaml` with:
  - `model: "spin_boson_sigma_x"` (changed from `pure_dephasing`).
  - `frozen_parameters.model.coupling_operator: "sigma_x"`.
  - `frozen_parameters.model.system_hamiltonian: "(omega / 2) * sigma_z"` (unchanged; the σ_x coupling acts on this same bare system Hamiltonian).
  - Parameter inheritance: bath_spectral_density and time_grid from A4 v0.1.1; perturbative_order, basis, integration_tolerance, solver from D1 v0.1.0 (the parts that didn't depend on the model). `bath_mode_cutoff` is dropped from the inheritance set (it is non-operational on the CBG path; see R6).
  - `comparison.target_observable: "L_n^dissipator(t) norm ratio ||L_n^dissipator|| / ||L_{n-1}^dissipator||"` with `L_n^dissipator := L_n + i [K_n, ·]`.
  - `comparison.error_metric: "convergence_ratio"`.
  - **Reproducibility specification (v0.1.3):** perturb `upper_cutoff_factor` by ±10 (30 → 20, 40) AND `omega_c` (the ohmic cutoff frequency) by ±1 (10 → 9, 11). Drop `bath_mode_cutoff`, `integration_tolerance`, and `quad_limit` from the load-bearing perturbation list; if `quad_limit` is retained, it is a null-result witness (sweep `100 / 200 / 400` documented in `result.notes` with the expected outcome "bit-identical").
  - `failure_mode_log` entry citing v0.1.0's three flagged deficiencies (model-induced TCL-2 exactness, K_n parity-vanishing, non-operational knobs) and v0.1.2's two refinements (dissipator sign, model switch) and v0.1.3's empirical narrowing of the perturbation set as the supersedure reasons; `predecessor_card_id: D1`, `predecessor_version: v0.1.0`.
- Annotate D1 v0.1.0 with `superseded_by: D1_failure-envelope-convergence_v0.1.1.yaml` and `status: superseded`.
- **Pilot check** (lands in the same commit or as a stand-alone follow-up before Phase C consumes the metric): a small numerical experiment confirming that, in the σ_x + thermal Gaussian model at α = 0.05 (the lower end of the swept range), `‖L_3^dissipator‖_t > 0` to numerical precision. The check uses Phase B.3 once that lands; if `L_3^dissipator = 0` numerically, the pilot fails and Phase A.bis must consider a different model. The pilot may be folded into Phase B.2 / B.3's commit message as a "metric well-defined" observation.
- **Schema/docs minor follow-up** (not in this commit; flagged for a future SCHEMA.md v0.1.4 bump): if `upper_cutoff_factor` and `omega_c`-perturbation knobs go into `frozen_parameters.numerical.quadrature` (the ad-hoc extras block accepted by Phase B.4's runner allow-list at [`reporting/benchmark_card.py`](../reporting/benchmark_card.py) `_quadrature_kwargs`), consider naming the block formally for forward compatibility. The runner's `validate_card_data` is permissive on extras today; v0.1.3 of this plan does NOT block on the schema bump.

### Phase B — TCL recursion at orders 3 and 4

Decomposed identically to v0.1.2:

- **B.0 — Raw ordered n-point correlations.** Implemented (commit `a2e7380`, `33eeeb5`).
- **B.1 — Extend D̄ recursion to mixed left/right indices and n ≥ 3.** Implemented (commit `edae5cf`).
- **B.2 — K_3, K_4 wired through K_n_thermal_on_grid.** Partial (commit `ca3471b`): n=3 lands; n=4 deferred. Three concrete routes to a correct L_4 (Path A: Companion Sec. IV closed-form; Path B: numerical Λ_t Richardson extraction via `benchmarks/exact_finite_env`, kept behind a named extraction module; Path C: HEOM/TEMPO/pseudomode third-method extraction in its own work plan). See the source-side falsification note at [`cbg/tcl_recursion.py:156`](../cbg/tcl_recursion.py).
- **B.3 — L_n dissipator extraction.** Compute `L_n^dissipator = L_n + i [K_n, ·]` per the corrected sign convention. Lives in `cbg.tcl_recursion` next to the K_n path. **Phase B.3 partial (n ∈ {0, 1, 2, 3})** is independent of B.2 (n=4) and can land first; B.3 (n=4) follows the L_4 path resolution.
- **B.4 — Knob-threading for reproducibility checks.** Implemented (commit `c7e9999`). Threads `upper_cutoff_factor` and `quad_limit` through the bath / cumulant / TCL / runner layers via an allow-list helper (`reporting.benchmark_card._quadrature_kwargs`). Empirical finding folded into v0.1.3 §1.1: `quad_limit` is a no-op witness for production-like tuples; `upper_cutoff_factor` is genuinely perturbative.

### Phase C — Sweep runner wiring

- Add `_run_dg4_sweep(card)` in `reporting/benchmark_card.py`. Dispatch from `run_card` BEFORE `_refuse_dg4_sweep` (and remove the refusal path once tests pass).
- The sweep runner:
  - Iterates over swept α values per `frozen_parameters.sweep.sweep_range`.
  - For each α, builds a `model_spec` with the swept value injected at `model.bath_spectral_density.coupling_strength`.
  - Evaluates K_n and L_n^dissipator at orders 0–4 via Phase B.
  - Computes `r_n = ⟨‖L_n^dissipator‖⟩ / ⟨‖L_{n−1}^dissipator‖⟩`.
  - **Zero-denominator policy:** if `‖L_{n−1}^dissipator‖ < ε_machine × ‖L_2^dissipator‖`, mark the α as `metric-undefined` and exclude from convergence-failure classification.
  - Tags each α as `passing`, `failing-candidate`, or `metric-undefined`.
- Per-α reproducibility checks (v0.1.3 perturbation set): re-evaluate `r_n` under perturbed `upper_cutoff_factor` (20, 40) AND perturbed `omega_c` (9, 11); reclassify per §5 R6.
- Λ_t-singularity observations recorded in `result.notes` only (R5).

### Phase D — Verdict

- Run D1 v0.1.1 end-to-end via the Phase C runner.
- Populate `result.verdict`, `result.evidence`, `result.runner_version`, `result.notes`.
- Logbook entry; validity-envelope update; self-referential `commit_hash` follow-up.
- Repository tag (`v0.5.0` on PASS; appropriate dev bump otherwise).

## 4. Acceptance criteria

PASS for DG-4 requires D1 v0.1.1 to verdict to PASS, which requires:

1. The Phase C runner runs to completion across the full swept range without raising.
2. At least one α in the range is classified `convergence failure` (i.e. `r_n > 1` AND stable under the v0.1.3 reproducibility perturbations: `upper_cutoff_factor` ±10 AND `omega_c` ±1).
3. The cause label, the per-α `r_n` values, and the boundary `α_crit` interpolation are all recorded in `result.notes`.

A FAIL verdict is admissible iff the runner runs to completion AND no α is classified `convergence failure`. The result must report `verdict: FAIL` with cause `no-failure-found-in-frozen-range` AND a routing note: per Risk R3, the response is supersedure (D2 with extended range), not in-place range-tightening of D1.

CONDITIONAL is admissible iff all candidate α values are classified `truncation artefact` rather than `convergence failure`; the `result.notes` must explain the reproducibility-knob coverage gap.

**TCL singularity at D1 v0.1.1 is observational, not gating.** A future card (with Λ_t reconstruction) targets it as a primary cause label.

## 5. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **R1: Phase B is large.** Three of four leaf modules (`n_point_ordered`, mixed-index `D_bar`, n ≥ 3 `D_bar`) were stubbed; bookkeeping for higher-order generalised cumulants is non-trivial. | **Largely mitigated:** B.0, B.1, B.2 (n=3), B.4 are landed (commits `a2e7380`, `33eeeb5`, `edae5cf`, `ca3471b`, `c7e9999`). B.2 (n=4) deferred per source-side falsification at [`cbg/tcl_recursion.py:156`](../cbg/tcl_recursion.py); B.3 (n=4) follows. |
| **R2: Reproducibility-check cost.** Each `failing-candidate` α is re-run under the v0.1.3 perturbation set — twice for `upper_cutoff_factor` and twice for `omega_c` — so up to 4 perturbed re-runs per failing α (down from 4 in v0.1.2's `quad_limit` + `upper_cutoff_factor` set). | Cache K_n / L_n arrays; document the cost; consider a `--quick` mode (CONDITIONAL verdict only) for development. |
| **R3: PASS-by-supersedure temptation.** If the swept range yields no `convergence failure`, the temptation is to extend the range *in place*. Risk #8 violation. | §4 *explicitly* allows a FAIL with cause `no-failure-found-in-frozen-range`. Response is a *new card* D2, not a silent edit of D1. |
| **R4: Truncation-artefact dominance.** Most candidates reclassify as artefacts under the reproducibility check. | The v0.1.3 perturbation set — `upper_cutoff_factor` and `omega_c` — both genuinely change the bath spectrum, so artefact-classification under either perturbation is a meaningful signal that the truncation is too coarse and the response is a new card D3 with tighter defaults. |
| **R5: TCL singularity is observational only at D1 v0.1.1.** Plan v0.1.0 erroneously allowed PASS with cause TCL singularity, but `cbg.diagnostics.tcl_invertibility_distance` is stubbed and Λ_t reconstruction is itself substantial work. | TCL singularity recorded in `result.notes` only; D1 PASS gates only on `convergence failure`. A future card (D2 or later) — accompanied by a Λ_t reconstruction implementation — can target this label as a primary PASS path. |
| **R6: Reproducibility-knob operationality (empirically refined in v0.1.3).** v0.1.0's perturbation knobs (`bath_mode_cutoff`, `integration_tolerance`) are not threaded through the CBG code paths. v0.1.2 substituted `quad_limit` and `upper_cutoff_factor`, threaded by Phase B.4 (commit `c7e9999`). **Phase B.4 implementation revealed that `quad_limit ∈ {100, 200, 400}` is a no-op witness** for production-like tuples (`α=0.05, ω_c=10, T=0.5` and t-grid points typical of C1): SciPy's adaptive quadrature with `weight='cos'/'sin'` converges in well under 100 subintervals, so the three values give bit-identical correlator outputs. v0.1.3 therefore drops `quad_limit` from the load-bearing set and adds `omega_c` ±1 as a substitute that genuinely changes the spectrum. | Empirically confirmed in commit `c7e9999`. The v0.1.3 perturbation set (`upper_cutoff_factor`, `omega_c`) is the load-bearing pair; `quad_limit` may be retained as a null-result witness in `result.notes` documenting that the planned 100/200/400 sweep was bit-identical. |
| **R7: K_n is identically zero in pure-dephasing thermal — and so is L_n for n ≥ 3.** Surfaced by review of v0.1.0 (K_n) and v0.1.1 (L_n^dissipator); the parity-class theorem + thermal D̄_1 = 0 + Gaussian Feynman-Vernon exactness force *all* perturbative orders ≥ 3 to vanish in the σ_z model with thermal Gaussian bath, regardless of which observable (K_n or L_n^dissipator) is chosen. | v0.1.2's Phase A.bis switches D1's *model* to `spin_boson_sigma_x`. For σ_x coupling, [H_S, σ_x] ≠ 0 keeps the perturbative series non-trivial: TCL-2 is *not* exact for σ_x + Gaussian bath, so L_3, L_4 carry finite contributions. Phase A.bis includes the pilot check that confirms ‖L_3^dissipator‖ > 0 numerically before D1 v0.1.1 lands. |
| **R8: Dissipator-extraction sign.** v0.1.1 used `L_n - i[K_n, ·]`, which under the repository convention `L[X] = -i[H, X] + dissipator` produces `2 × Hamiltonian-part` instead of the dissipator residual. Surfaced by review of v0.1.1. | v0.1.2 corrects to `L_n^dissipator := L_n + i [K_n, ·]`. Phase B.3's commit must include a unit test on a known-pure-unitary L: `L_n^dissipator` equals zero to machine precision when L is `-i[H, ·]` and K is `H`. |

## 6. Dependencies

- DG-1 PASS (completed 2026-04-30, tag `v0.2.0`).
- DG-2 structural sub-claims PASS (completed 2026-05-04). Phase B unblocks the canonical-unfilled "literal K_2–K_4 numerical recursion" milestone partially — n=3 lands at Phase B.2; n=4 remains pending.
- D1 v0.1.1 supersedure (Phase A.bis): must land before Phase C consumes the new model and metric. Phase B.0 / B.1 / B.4 are independent and have already landed; Phase B.3 (partial) is also independent and can land before A.bis.
- Currently stubbed pieces this plan still needs:
  - `cbg.tcl_recursion.K_n_thermal_on_grid` at n=4 (B.2 deferred; three routing paths recorded at [`cbg/tcl_recursion.py:156`](../cbg/tcl_recursion.py)).
  - `cbg.tcl_recursion` L_n^dissipator extraction with the corrected sign and the unitary-recovery unit test (B.3 partial: n ∈ {0, 1, 2, 3} can land; n=4 follows L_4).
- Currently stubbed but **deferred to a future card**:
  - `cbg.diagnostics.tcl_invertibility_distance` (Λ_t reconstruction). D1 v0.1.1 records `‖Λ_t − id‖ ≥ 1` in `result.notes` only when this becomes available; until then the field is omitted.
- SCHEMA.md v0.1.3 (sweep block specified). Possible future v0.1.4 patch: define a `numerical.quadrature` sub-block to formally validate `upper_cutoff_factor` / `omega_c`-perturbation knobs (currently accepted as extras by the permissive validator; flagged in §3 Phase A.bis).
- `reporting.benchmark_card._refuse_dg4_sweep` (the present runner refusal path; replaced by `_run_dg4_sweep` when Phase C lands).

---

*Plan version: v0.1.3. Drafted 2026-05-06. Supersedes v0.1.2 per the empirical narrowing of the load-bearing reproducibility-perturbation set, surfaced by Phase B.4 implementation. CC-BY-4.0 (see ../LICENSE-docs).*

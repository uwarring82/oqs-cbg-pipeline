---
plan_id: dg-4-work-plan
version: v0.1.0
date: 2026-05-05
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§9 (DG-4), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entry 2 (recursive-series convergence; COMPATIBLE, scope-limited)
anchor_envelope: docs/validity_envelope.md DG-4 row (SCOPED — runner refusal path wired → target PASS)
status: draft
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Work Plan — Failure-envelope identification

## 1. Objective

Pass DG-4 as defined in Sail v0.5 §9:

> *Pass if at least one reproducible, cause-labelled regime is identified in which the implementation fails or yields ambiguous output.*

DG-4 is the only Decision Gate where **PASS requires a failure to occur**. It operationalises CL-2026-005 v0.4 Entry 2's open convergence question (Constraint C: "convergence of the perturbative series depends on system parameters, and singularities in the exact TCL generator can arise in specific regimes") by demanding evidence that the implementation *actually exhibits* breakdown in some regime, not merely that breakdown is possible in principle. A passed DG-4 narrows the validity envelope; a stuck-on-PASS implementation that never finds a failure regime fails DG-4 by virtue of being insufficiently probed.

This plan operationalises that objective in **benchmark-cards-first** ordering, extending the discipline established in the DG-1, DG-2, and DG-3 work plans. Card D1 v0.1.0 is already frozen (`benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.0.yaml`, status `frozen-awaiting-run`); Phases B–D below operationalise it.

### 1.1 Cards-first context

D1 v0.1.0 is the canonical Phase A artefact. It freezes:

- **Sweep parameter:** `coupling_strength` (ohmic α), swept log-uniformly from 0.05 to 1.0 over 20 points (`frozen_parameters.sweep`, SCHEMA.md v0.1.3 Rule 17).
- **Perturbative orders:** N_card = 4. The convergence-ratio metric `r_n = ⟨‖K_n‖⟩_t / ⟨‖K_{n−1}‖⟩_t` is evaluated at every swept α for n ∈ {1, 2, 3, 4}.
- **Failure regime definition:** an α is classified as a *convergence failure* when r_3 > 1.0 OR r_4 > 1.0 (the perturbative series ceases to decrease in norm at order 3 or 4).
- **Reproducibility requirement:** classification must be stable under a ±1 grid-point perturbation in `bath_mode_cutoff` (1023 / 1025) AND a 10% tightening of `integration_tolerance`. Unstable classifications are *truncation artefacts*, not convergence failures.
- **Cause-label taxonomy** (Sail v0.5 §9 DG-4):
  1. `convergence failure` (r_n > 1, stable under truncation perturbation).
  2. `TCL singularity` (`‖Λ_t − id‖ ≥ 1`).
  3. `projection ambiguity` (multi-method comparison reveals projection-scheme-dependent results — DG-3 territory; not gated by D1).
  4. `truncation artefact` (r_n > 1 but unstable under truncation perturbation).
  5. `benchmark disagreement` (DG-3 cross-method test fails — also not gated by D1).

D1 targets cause label **#1 (convergence failure)**. The other four labels are out of scope for D1 v0.1.0 and would be addressed by future failure-envelope cards.

### 1.2 Asymmetry from DG-1/2/3

DG-1, DG-2, and DG-3 PASS when their cards' acceptance criteria are met (errors below thresholds, structural identities satisfied, or cross-method agreement). DG-4 PASSES when D1 produces a verdict like:

> "α_crit ≈ 0.42 ± 0.05 (interpolated boundary between last α with r_3 < 1 and first α with r_3 > 1); cause label `convergence failure` confirmed reproducible under ±1 grid-point bath_mode_cutoff perturbation and 10% integration_tolerance tightening."

A verdict like "no α in the swept range produced r_n > 1" is **not** a DG-4 PASS. It indicates the swept range was too narrow, and the cards-first / Risk #8 discipline requires *supersedure* (D2 with extended range), not in-place range-tightening. See Risk R3.

## 2. Scope

### 2.1 In scope

- **Phase B:** extend `cbg.tcl_recursion` to perturbative_order ∈ {3, 4}. This delivers, as a side effect, the canonical-unfilled DG-2 milestone "literal K_2–K_4 numerical recursion at perturbative_order ≥ 4" (per `docs/validity_envelope.md` DG-2 row; tracked separately in §6 below).
- **Phase C:** sweep-block-aware runner branch consuming `frozen_parameters.sweep`. New private helper `_run_dg4_sweep` in `reporting/benchmark_card.py`, dispatched from `run_card` *before* the present `_refuse_dg4_sweep` (which is replaced when the real runner lands).
- Reproducibility-check infrastructure: the runner must be able to re-execute D1 under perturbed `bath_mode_cutoff` and `integration_tolerance` to support the per-α classification.
- Cause-label assignment per the §1.1 taxonomy, written into `result.notes`.
- Boundary interpolation: when both *passing* (r_n < 1) and *failing* (r_n > 1) α values exist in the swept range, the boundary `α_crit` is interpolated (linear in `log(α)`) and reported in `result.notes`.
- Phase D verdict commit: populate D1's `result` block, fill `commit_hash` self-referentially (per `benchmarks/benchmark_cards/SCHEMA.md` §Card lifecycle), update `docs/validity_envelope.md` DG-4 row, and write a `logbook/YYYY-MM-DD_dg-4-{pass,fail-with-cause}.md` entry.
- Repository tag bump (`v0.5.0` on PASS, or appropriate dev bump on partial progress).

### 2.2 Out of scope

- **Other cause labels.** D1 targets label #1 (`convergence failure`) only. Labels #2 (`TCL singularity`) and #4 (`truncation artefact`) appear *as outcomes* of D1's classification logic but are not separately gated by this plan. Labels #3 (`projection ambiguity`) and #5 (`benchmark disagreement`) require cross-method data and are DG-3 territory; future failure-envelope cards (D2, D3, …) would address them.
- **Multi-parameter sweeps.** D1 sweeps `coupling_strength` only. Sweeps in other parameters (temperature, displacement amplitude, time-grid step) are explicitly out of scope for D1 v0.1.0 and would be future cards.
- **Models other than `pure_dephasing`.** `spin_boson_sigma_x` and other models could carry their own DG-4 cards; not in this plan.
- **Re-entry into Entry 2's classification.** D1's verdict feeds the validity envelope; it does NOT unilaterally re-classify CL-2026-005 v0.4 Entry 2. The Council deliberation route remains the only way to alter Entry 2's `COMPATIBLE, scope-limited` label.

### 2.3 Explicit non-claims

DG-4 PASS does **not** establish:

- That the breakdown α_crit is a property of the analytical theory rather than a property of the implementation. It is an *implementation* finding under the frozen parameter scaffold of D1.
- That smaller perturbative orders (n ≤ 2) are convergent for *all* α ≤ α_crit. The verdict is about the order at which divergence first appears under the D1 metric.
- That the discrete finite-bath truncation in any DG-3 cross-method handler is converged at α ≤ α_crit. The two questions (perturbative-series convergence vs. finite-bath truncation) are independent.

## 3. Phases

### Phase A — Card drafting (already complete)

D1 v0.1.0 was frozen 2026-05-05 (`logbook/2026-05-05_dg-3-4-5-scoping.md` and the SCHEMA.md v0.1.3 bump for the sweep block). No further Phase A work.

### Phase B — TCL recursion at orders 3 and 4

- Extend `cbg.tcl_recursion.K_n_thermal_on_grid` to support `n ∈ {3, 4}`. Currently the docstring states "n: int; one of 0, 1, 2 in the currently implemented thermal path" — this restriction is the gating gap.
- Implement the higher-order generalised cumulants `D̄_3`, `D̄_4` via the recursion in Letter Eq. (17) / Companion Eq. (27): `D̄(τ_1^k, s_1^{n−k}) = D − Σ_{l,r} D̄(τ_1^l, s_1^r) D̄(τ_{l+1}^k, s_{r+1}^{n−k})`.
- Verify the new orders against existing DG-1/DG-2 fixtures: K_3 and K_4 should evaluate to zero (or be proportional to σ_z by parity) on the A3 / A4 thermal fixtures, since the parity-class theorem still applies. Add tests.
- This is the canonical-unfilled DG-2 milestone per `docs/validity_envelope.md` DG-2 row. A side-effect commit message should mention the DG-2 unblocking.

### Phase C — Sweep runner wiring

- Add `_run_dg4_sweep(card)` in `reporting/benchmark_card.py`. Dispatch from `run_card` BEFORE the existing `_refuse_dg4_sweep` (and remove the refusal path once the real runner is wired and tested).
- The sweep runner:
  - Iterates over the swept α values per the card's `frozen_parameters.sweep.sweep_range`.
  - For each α, builds a `model_spec` with the swept value injected at `model.bath_spectral_density.coupling_strength`.
  - Evaluates K_0, K_1, K_2, K_3, K_4 via Phase B's extended recursion.
  - Computes `r_n = ⟨‖K_n‖⟩_t / ⟨‖K_{n−1}‖⟩_t` for each order.
  - Tags each α as `passing` (r_3 < 1 AND r_4 < 1) or `failing-candidate` (r_3 > 1 OR r_4 > 1).
- For each `failing-candidate` α, run a reproducibility check: re-evaluate r_n with `bath_mode_cutoff` perturbed by ±1 (1023, 1025) AND with `integration_tolerance.relative` tightened by 10× (`1e-11`). Reclassify as:
  - `convergence failure` if r_n > 1 in all three perturbed runs.
  - `truncation artefact` if r_n flips below 1 in any perturbed run.
- If any handler hits a TCL singularity (`‖Λ_t − id‖ ≥ 1`), mark that α with cause label `TCL singularity` and short-circuit the rest of D1's classification for that α.

### Phase D — Verdict

- Run D1 v0.1.0 end-to-end via the Phase C runner.
- Populate `result.verdict`, `result.evidence` (paths to numerical outputs, plot files, log files), `result.runner_version`, and `result.notes` (cause-label classification per α; α_crit interpolation; reproducibility-check outcomes).
- Write `logbook/YYYY-MM-DD_dg-4-{pass,fail-with-cause}.md`.
- Atomically update `docs/validity_envelope.md` DG-4 row.
- Self-referential `commit_hash` follow-up commit per SCHEMA.md §Card lifecycle.
- Repository tag (`v0.5.0` on PASS, dev bump on partial progress or FAIL).

## 4. Acceptance criteria

PASS for DG-4 requires D1 v0.1.0 to verdict to PASS, which requires:

1. The Phase C runner runs to completion across the full swept range without raising.
2. At least one α in the range is classified `convergence failure` (i.e. r_3 > 1 OR r_4 > 1 with stability under reproducibility perturbation).
3. The cause label is recorded in `result.notes` together with the boundary α_crit interpolation.

A FAIL verdict is admissible iff:

- The runner runs to completion.
- No α in the range is classified `convergence failure`.
- The result is reported as `verdict: FAIL` with cause `no-failure-found-in-frozen-range` AND a routing note: per Risk R3, the response is supersedure (D2 with extended range), not in-place range-tightening of D1.

Conditional verdicts (CONDITIONAL) are admissible if all candidate α values are classified `truncation artefact` rather than `convergence failure`. The `result.notes` must explain that the bath_mode_cutoff is too coarse to discriminate.

## 5. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **R1: Phase B is large.** Extending TCL recursion to orders 3 and 4 is the canonical-unfilled DG-2 milestone; it has not been attempted because of the bookkeeping complexity of the generalised-cumulant recursion at higher orders. | Decompose Phase B into sub-commits: (B.1) D̄_3, D̄_4 evaluators with stand-alone tests; (B.2) K_3, K_4 evaluators wired through `K_n_thermal_on_grid`; (B.3) integration tests on A3/A4 fixtures (K_3, K_4 should respect parity). Land each sub-commit before Phase C starts. |
| **R2: Reproducibility-check cost.** Each `failing-candidate` α is re-run twice (perturbed bath_mode_cutoff) plus once at tightened tolerance. With 20 swept α, this is up to ~80 K_n evaluations at order 4, which is substantial. | Cache K_n arrays where possible; document the cost in the runner; consider a `--quick` mode that skips the reproducibility checks (CONDITIONAL verdict only) for development iteration. |
| **R3: PASS-by-supersedure temptation.** If the swept range yields no `convergence failure` at any α, the temptation is to extend the range *in place* and re-run. This is a Risk #8 violation. | The acceptance criterion in §4 *explicitly* allows a FAIL with cause `no-failure-found-in-frozen-range`. The response is a *new card* D2 with an extended range, not a silent edit of D1. The Phase D verdict commit must include a routing note if this path is taken. |
| **R4: Truncation-artefact dominance.** If most candidate α values are reclassified as truncation artefacts under the reproducibility check, the card lands CONDITIONAL with no informative DG-4 finding. | The bath_mode_cutoff frozen at 1024 (per A3/B4 inheritance) is generous; if it proves too coarse, the response is a new card D3 with `bath_mode_cutoff: 4096` (or higher) and a `failure_mode_log` entry citing the truncation-artefact dominance in D1's verdict. |
| **R5: TCL-singularity prevalence.** If most α land on `TCL singularity` (`‖Λ_t − id‖ ≥ 1`), the convergence-ratio metric is never reached, and the failure-envelope question moves into a different cause-label regime. | TCL singularity is itself a valid DG-4 cause label (#2). The verdict can be PASS with cause label `TCL singularity` rather than `convergence failure`, provided the singularity is reproducible under the perturbation check. The card's `result.notes` must distinguish the two. |

## 6. Dependencies

- DG-1 PASS (completed 2026-04-30, tag `v0.2.0`).
- DG-2 structural sub-claims PASS (completed 2026-05-04). Note: the DG-2 "literal K_2–K_4 numerical recursion at perturbative_order ≥ 4" milestone is *unblocked by Phase B of this plan*; it has been deferred precisely because it was not needed for the DG-2 structural-identity cards (B1–B5). Phase B's sub-commit landing K_3, K_4 should also update `docs/validity_envelope.md` DG-2 row to remove the residual "scope-limited" qualifier on Entry 2 once the structural identities can be exhibited at order ≥ 4.
- `cbg.cumulants.D_bar_2` (available; DG-1 Phase C.7).
- `cbg.tcl_recursion.K_total_thermal_on_grid` (available for orders ≤ 2).
- `numerical/time_grid.py` integration utilities (available; used in DG-1/2/3).
- SCHEMA.md v0.1.3 (the sweep block is already specified; no further schema work needed for D1 v0.1.0).
- `reporting.benchmark_card._refuse_dg4_sweep` (the present runner refusal path; replaced by `_run_dg4_sweep` when Phase C lands).

---

*Plan version: v0.1.0. Drafted 2026-05-05. CC-BY-4.0 (see ../LICENSE-docs).*

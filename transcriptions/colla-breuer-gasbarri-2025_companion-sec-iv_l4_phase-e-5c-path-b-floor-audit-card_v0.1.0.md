---
artifact_id: cbg-companion-sec-iv-l4-phase-e-5c-path-b-floor-audit-card
version: v0.1.0
date: 2026-05-13
type: verification-card / audit (scope-definition)
status: frozen — implementation may proceed
parent_phase_e_pilot_card: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-pilot-card_v0.1.0.md
parent_path_b_pilot_logbook: logbook/2026-05-06_dg-4-path-b-pilot-result.md
target_artifact: benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json
anchor_plan: plans/dg-4-work-plan_v0.1.5.md §"Deferred tracks (post-pilot)" 5.C
release_gate: NONE — this card does NOT issue a Phase E classification
reviewer: Codex (GPT-5 local steward review)
review_date: 2026-05-13
review_state: frozen
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Phase E Track 5.C card — Path B finite-env floor audit at the D1 σ_x fixture

> **Status: frozen (2026-05-13).** This card scopes Track 5.C from the
> Phase E pilot card §5.C: an independent characterisation of Path B's
> finite-environment extraction floor **at the D1 v0.1.2 σ_x thermal
> fixture** (currently characterised only at the small-coupling σ_z
> zero-oracle fixture per the 2026-05-06 pilot). It does **not** issue
> a Phase E classification, does **not** modify the D1 v0.1.2 verdict,
> and does **not** convene Council-3. The audit is a precondition for
> a clean Phase E verdict when combined with Path A convergence
> evidence from Tracks 5.A or 5.B.

## 0. Provenance and role

This card consumes:

- the Phase E pilot card v0.1.0 (`749bd85`) §5.C, which named this
  audit as a "complement or alternative" to Tracks 5.A / 5.B;
- the 2026-05-06 σ_z thermal zero-oracle pilot
  ([`logbook/2026-05-06_dg-4-path-b-pilot-result.md`](../logbook/2026-05-06_dg-4-path-b-pilot-result.md)),
  which characterised the floor at the small-coupling σ_z fixture as
  `‖L_4^dis‖_avg ≈ 2.32e-2` for `(n_bath_modes=4, n_levels_per_mode=3,
  omega_max_factor≈4)`;
- the D1 v0.1.2 audit payload
  ([`benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json`](../benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json)),
  whose `coefficient_ratio ≈ 47.4` at α²=1.0 is the Path B baseline
  this audit perturbs around;
- the Path B implementation at `benchmarks/numerical_tcl_extraction.py`
  (`path_b_dissipator_norm_coefficients`) and the runner threading at
  [`reporting/benchmark_card.py:1722`](../reporting/benchmark_card.py#L1722)
  (`upper_cutoff_factor → omega_max_factor`).

This is a **scope-definition card**. Implementation and result JSON
land in successor commits gated by steward freeze of this card.

## 1. Purpose

### 1.1 What this card does

- Frames a single scientific question:
  **Is the D1 v0.1.2 Path B `coefficient_ratio ≈ 47.4` tight against
  the analytic value, or does it drift significantly as the
  finite-env truncation tightens?**
- Pins the audit parameter grid (truncation knobs, fixture points,
  acceptance ladder).
- Pins the result artefact format and the routing rules for each
  possible outcome.

### 1.2 What this card does not do

- It does **not** classify the Phase E cross-validation as
  supports / contradicts / inconclusive. Phase E remains unclassified
  per the Phase E pilot card.
- It does **not** retract or modify the D1 v0.1.2 PASS verdict.
- It does **not** modify the Path B implementation in
  `benchmarks/numerical_tcl_extraction.py` other than additive
  audit-time helpers if needed.
- It does **not** convene Council-3. The audit feeds a future Phase E
  classification card; Council-3 routing is governed by the work plan
  §4 Phase E table on that card, not on this one.

## 2. Hypothesis

The Phase E pilot revealed a Path A vs Path B disagreement of ~30× in
the α-normalised coefficient ratio at N=41 on the D1 σ_x thermal
fixture (Path A: 14.15; Path B: 47.4). The Phase E pilot card §5.C
records the contributing hypothesis:

> "If Path B's σ_x finite-env floor is order-unity at the D1 fixture,
> the Path B coefficient_ratio = 47.4 may itself be at the floor and
> not a tight estimate of the analytic value."

This audit tests that hypothesis directly by varying the three
truncation knobs available in the Path B finite-env builder and
measuring the resulting drift in the production-fixture
`coefficient_ratio`.

## 3. Scope

### 3.1 In scope

- Production fixture: D1 v0.1.2 baseline (`model = spin_boson_sigma_x`,
  `bath_state.family = thermal`, `temperature = 0.5`, `omega_c = 10.0`,
  `omega = 1.0`, time grid `linspace(0, 20, 200)`).
- **Grid topology: one-axis-at-a-time, anchored at the production
  configuration `(n_bath_modes = 4, n_levels_per_mode = 3,
  omega_max_factor = 30)`.** Each lever below is swept in isolation
  while the other two are held at the anchor. Cross-term audit points
  (e.g., `(n_bath_modes = 6, n_levels_per_mode = 4)`) are **optional**
  and dependent on compute budget; the audit acceptance does NOT
  require a Cartesian product, only that each axis is exercised
  independently and the Hilbert-tightening witness requirement of §5
  is met.
- Audit lever 1 — `omega_max_factor` (high-frequency tail). Sweep:
  `{10, 20, 30, 40, 80, 160}`. Includes the production anchor
  `omega_max_factor = 30` (centre of the D1 v0.1.2 production
  perturbation set `{20, 30, 40}`); extends the production
  perturbation downward to `10` and upward to `80` / `160`.
- Audit lever 2 — `n_bath_modes` (number of discrete bath modes).
  Sweep: `{4 (anchor), 6, 8}` if compute permits at the higher
  values; the joint Hilbert space scales as `n_levels_per_mode ^
  n_bath_modes`.
- Audit lever 3 — `n_levels_per_mode` (Fock truncation per mode).
  Sweep: `{3 (anchor), 4, 5}` likewise gated by compute.
- Richardson fit α grid: production `alpha_values = (0.01, 0.015, 0.02,
  0.025, 0.03)` per [`reporting/benchmark_card.py:1401`](../reporting/benchmark_card.py#L1401).
  The fit yields α-independent `L_2`, `L_4` coefficients and the
  α-independent `coefficient_ratio = ⟨‖L_4^dis‖⟩ / ⟨‖L_2^dis‖⟩`. **Each
  truncation configuration is one Richardson fit, not multiple.**
- Reported `r_4` ladder: the per-α metric
  `r_4(α²) = α² · coefficient_ratio` is reported at
  `α² ∈ {0.05, 0.5, 1.0}` (low-coupling / mid-range / max of the
  production sweep range), derived from the single fit at that
  truncation configuration. These reporting points carry no extra
  compute cost.
- Fit shape: Richardson polynomial `Λ_t(α) = Λ_0 + α² Λ_2 + α⁴ Λ_4 +
  O(α⁶)` (unchanged from production).
- Reproducibility: each audit point persists a full result row
  (truncation knobs + Richardson fit residual + extracted `L_2`,
  `L_4` coefficients + averaged dissipator norms + α-independent
  coefficient ratio + the three reported `r_4(α²)` values).

### 3.2 Out of scope

- Modifying D1 v0.1.2 card parameters or its result JSON.
- Issuing any Phase E classification.
- Implementing Path A higher-order quadrature (Track 5.B).
- Running Path A at higher N (Track 5.A).
- Higher orders (`n ≥ 5`) or non-thermal/displaced fixtures.
- Modifying the production runner's threading of
  `upper_cutoff_factor → omega_max_factor` — this audit calls
  `path_b_dissipator_norm_coefficients` directly with the chosen
  truncation, not through the production sweep runner.

### 3.3 Explicit non-claims

Completion of this audit would authorise saying:

- "At the D1 v0.1.2 σ_x fixture, the Path B `coefficient_ratio` drifts
  by ≤ X% across the truncation sweep" (X% measured directly), with
  a stated cause label for the residual sensitivity (floor-dominated /
  truncation-converged / borderline).

It would not authorise:

- a Phase E classification verdict;
- modification of the D1 v0.1.2 PASS;
- a generalisation of the floor characterisation outside the D1 σ_x
  fixture.

## 4. Methodology

### 4.1 Driver

A new `benchmarks/path_b_floor_audit.py` script (no `cbg/` changes; no
runner changes) that:

1. Iterates over the one-axis-at-a-time truncation grid in §3.1.
2. For each point, calls
   `numerical_tcl_extraction.path_b_dissipator_norm_coefficients` with
   the explicit truncation kwargs (overriding the production defaults).
3. Records the production α-grid Richardson fit output:
   `‖L_2^dis‖_avg`, `‖L_4^dis‖_avg`,
   `coefficient_ratio = L_4/L_2`, the derived `r_4(α²)` ladder,
   fit residual, and wall time.
4. Emits a single JSON artefact
   `benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json` with
   the full table + summary statistics.

### 4.2 Compute envelope

Approximate per-point cost is dominated by the joint Hilbert dimension
`d_joint = 2 × n_levels_per_mode ^ n_bath_modes` and the time grid:

| Knob configuration | d_joint | Indicative cost vs production |
|---|---:|---|
| `(4, 3)` production | 162 | 1× |
| `(4, 4)` | 512 | ~30× |
| `(4, 5)` | 1250 | ~150× |
| `(6, 3)` | 1458 | ~200× |
| `(6, 4)` | 8192 | ~6000× (likely intractable in audit) |

The `omega_max_factor` sweep is free wrt Hilbert dimension; only the
discretisation of `J(ω)` over `n_bath_modes` modes changes. The audit
should produce the full 6-point `omega_max_factor` sweep at the anchor
`(4, 3)` first; the Hilbert-tightening axes (`n_bath_modes`,
`n_levels_per_mode`) are conditional on bench-time feasibility (the
audit script should declare a wall-time budget per point and skip +
log truncations that exceed it). **At least one non-degraded
Hilbert-tightening point is required by §5 acceptance** — the
`omega_max_factor` sweep alone is necessary but not sufficient.

### 4.3 Acceptance ladder

**Drift definition.** "Drift" is the relative change in the
α-independent `coefficient_ratio` between the production anchor
`(n_bath_modes = 4, n_levels_per_mode = 3, omega_max_factor = 30)` and
each non-degraded evaluated audit point — i.e.
`drift = |ratio_point − ratio_anchor| / ratio_anchor`. Degraded points
(R2 fit-conditioning filter, R3 aliasing filter) and skipped points
(R1 wall-time budget) are excluded from the drift maximum. **Maximum
drift over the non-degraded evaluated points** is the cause-label
input.

| Result | Cause label | Interpretation |
|---|---|---|
| Max drift ≤ 5% AND ≥ 1 non-degraded Hilbert-tightening point evaluated | `truncation-converged` | Path B 47.4 is tight; the Phase E disagreement is dominantly a Path A issue. Path A convergence (Track 5.A or 5.B) is the live blocker for Phase E. |
| Max drift > 5% but bounded (stabilises at the tightest evaluated truncation) AND ≥ 1 non-degraded Hilbert-tightening point evaluated | `borderline` | Path B 47.4 is partially floor-driven; the audit reports the converged value and its uncertainty band. Path A convergence work in 5.A/5.B should target the converged Path B value, not 47.4. |
| Max drift > 5% AND still moving at the tightest tractable truncation (Hilbert axis included) | `floor-dominated` | Path B 47.4 is not a stable estimate of the analytic value at D1. Phase E classification must wait on a fundamentally different Path B (e.g., HEOM / TEMPO via DG-3 Tier-2.A) or on Path A convergence with no Path B reference target. |

If §5's Hilbert-tightening witness requirement is not met (zero
non-degraded Hilbert-tightening points produced), the audit is
**incomplete** and no cause label is issued; the steward extends the
compute budget or relaxes the wall-time skip threshold and re-runs.
The `omega_max_factor` sweep alone is never sufficient to claim
`truncation-converged`.

### 4.4 Routing matrix

| Cause label | Live verdict change | Steward action |
|---|---|---|
| `truncation-converged` | None | Initiate Track 5.A (Path A at N=81) targeting Path B's 47.4. |
| `borderline` | None | Initiate Track 5.A targeting the audit's converged value; record the band as Phase E precondition. |
| `floor-dominated` | None | Open a successor scoping entry: Phase E may need DG-3 Tier-2.A (third reference method) as a precondition, not just Path A convergence. |

In **none** of the three outcomes does this card alter the D1 v0.1.2
PASS verdict or the Phase E unclassified-pilot state. The card is
diagnostic only.

## 5. Acceptance criteria

This audit is **complete** when:

1. The script `benchmarks/path_b_floor_audit.py` is checked in,
   runnable from a clean `.venv`, and gated by a pytest entry
   (smoke test on the `(4, 3, omega_max_factor=10)` corner only).
2. The result JSON
   `benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json`
   exists, contains the full audit table, and is referenced from a
   logbook entry.
3. **Hilbert-tightening witness requirement.** The audit produces at
   least one non-degraded evaluated point on a Hilbert-tightening axis
   — i.e. at least one of (`n_bath_modes ∈ {6, 8}` with
   `n_levels_per_mode = 3, omega_max_factor = 30`) or
   (`n_levels_per_mode ∈ {4, 5}` with `n_bath_modes = 4,
   omega_max_factor = 30`). If the compute budget prevents this, the
   audit is INCOMPLETE; the steward extends the budget, relaxes the
   wall-time skip threshold in §6 R1, or both, before re-running. The
   `omega_max_factor` sweep alone does not satisfy this criterion.
4. A cause label from §4.3 is recorded in the result JSON's `notes`
   field and in the logbook entry — or, if §5.3 is not met, the
   logbook entry explicitly records the audit as INCOMPLETE.
5. Quality gates pass on the script + smoke test:
   - `ruff check`;
   - `black --check .`;
   - `mypy benchmarks/`;
   - `pytest -q`.
6. No edits to: D1 v0.1.2 card, D1 v0.1.2 result JSON, validity
   envelope DG-4 row, work plan v0.1.5 §4 Phase E, Phase E pilot
   card.

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **R1: Compute budget exceeded.** Higher truncations may be intractable on the audit machine. | Declare a per-point wall-time budget (default scaffold: 30 min); skip + log infeasible points. **Add a preflight estimator that predicts wall time from `d_joint` and skips ahead of dispatch when the prediction exceeds budget, in addition to a hard process timeout for points that beat the estimator.** The audit acceptance does NOT require the full grid (§5.3 only requires one non-degraded Hilbert-tightening point). |
| **R2: Richardson fit conditioning degrades at tighter Hilbert truncations.** The fit α grid is fixed at the production `alpha_values = (0.01, 0.015, 0.02, 0.025, 0.03)` for every audit point, so per-α extrapolation uncertainty (the α²=1.0 reporting case) is a production concern, not a floor-audit concern; the floor-audit signal lives in the α-independent `coefficient_ratio` which is the fit output directly. The remaining R2 mode is that wider Hilbert truncations may degrade the small-α fit itself (e.g., O(α⁶) tails becoming significant relative to the α² and α⁴ coefficients at larger d_joint). | Persist `relative_residual_norm` at every point. If `relative_residual_norm > 1e-3`, mark the point as fit-degraded; exclude from the drift maximum in §4.3. |
| **R3: `omega_max_factor` sweep introduces aliasing.** Geometric discretisation at high `omega_max_factor` and low `n_bath_modes` may push the resonant `ω_S = 1.0` mode into a poorly-resolved bin. | The audit reports the per-point `omega_modes` array as part of the result JSON for post-hoc inspection. |
| **R4: Steward sign-off lag.** The audit script must wait on this card freeze before merging. | Until freeze, the script lives on a branch (or is held back from main) and the result JSON is not written. |

## 7. Dependencies

- D1 v0.1.2 PASS remains the live verdict.
- Path B implementation (`path_b_dissipator_norm_coefficients`) is
  unchanged.
- `exact_finite_env._build_spin_joint` already accepts
  `n_bath_modes`, `n_levels_per_mode`, `omega_max_factor` as parameters
  — no API change needed.
- This audit does NOT depend on Path A (`cbg.tcl_recursion.L_n_thermal_at_time(n=4)`)
  and can run independently of Tracks 5.A / 5.B.

## 8. Steward decisions before implementation

Required steward sign-offs on this card before any implementation
commit lands:

- [x] Confirm the audit-grid parameter ranges in §3.1:
      `omega_max_factor ∈ {10, 20, 30, 40, 80, 160}` (anchored at
      production `30`); `n_bath_modes ∈ {4, 6, 8}` conditional on
      compute; `n_levels_per_mode ∈ {3, 4, 5}` conditional on compute;
      one-axis-at-a-time topology anchored at
      `(n_bath_modes = 4, n_levels_per_mode = 3, omega_max_factor = 30)`;
      Richardson fit α grid fixed at production
      `(0.01, 0.015, 0.02, 0.025, 0.03)`; reported
      `r_4(α²) = α² · coefficient_ratio` at `α² ∈ {0.05, 0.5, 1.0}`
      derived from the single per-point fit.
- [x] Confirm the §5.3 Hilbert-tightening witness requirement
      (at least one non-degraded point on a `n_bath_modes` or
      `n_levels_per_mode` axis; the `omega_max_factor` sweep alone is
      insufficient for `truncation-converged`).
- [x] Confirm the §4.3 drift definition (relative change in the
      α-independent `coefficient_ratio` against the production anchor
      `omega_max_factor = 30`, computed over non-degraded evaluated
      points) and the 5% boundary for `truncation-converged` vs
      `borderline`.
- [x] Confirm the result-JSON artefact path
      `benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json`.
- [x] Confirm the per-point wall-time budget and skip mechanism
      (default scaffold: 30 min per point; preflight `d_joint`-based
      estimator + hard process timeout per §6 R1).
- [x] Confirm the routing matrix in §4.4 (in particular the
      `floor-dominated` → DG-3 Tier-2.A escalation path).

## 9. Out-of-scope reminders

- **Phase F Tier-2.D handoff**: cannot proceed until a Phase E verdict
  is issued; this audit does not issue one.
- **Path A convergence**: Track 5.A / 5.B work, separate from this
  audit; sequencing is a steward decision after this card's cause
  label is recorded.
- **Cross-method validation (DG-3 Tier-2.A)**: only invoked in the
  `floor-dominated` cause-label branch; that escalation requires its
  own plan revision.

## 10. Steward freeze sign-off

> I have reviewed the revised 5.C audit card after the three freeze
> blockers were addressed. The production `omega_max_factor = 30`
> anchor is now explicit, the audit is scoped as a one-axis-at-a-time
> truncation study with optional compute-gated cross-terms, and the
> production Richardson α grid is separated cleanly from the derived
> `r_4(α²)` reporting ladder.
>
> I approve the audit grid (§3.1), the Hilbert-tightening witness
> requirement (§5.3), the drift definition and 5% cause-label boundary
> (§4.3), the result-artefact path, the per-point compute budget and
> skip mechanism, and the routing matrix (§4.4). This card freezes
> from `v0.1.0-draft` to `v0.1.0`; implementation may proceed under
> this scope.
>
> Reviewer: Codex (GPT-5 local steward review)  Date: 2026-05-13
>
> Version at freeze: v0.1.0 (release state: frozen)

## Appendix — change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1.0-draft | 2026-05-13 | Initial draft scoping Track 5.C from the Phase E pilot card §5.C. Pins the audit grid (3 truncation knobs × 3 α points), cause-label ladder (truncation-converged / borderline / floor-dominated), routing matrix, and compute-budget mechanism. Awaiting steward freeze. | Steward-directed scaffold (Claude Opus 4.7). |
| v0.1.0-draft (revision 1) | 2026-05-13 | Three steward freeze-blockers addressed: (1) §3.1 `omega_max_factor` set includes the production anchor `30` (`{10, 20, 30, 40, 80, 160}`); (2) §3.1 α-grid rewritten — Richardson fit α grid is the production `(0.01, 0.015, 0.02, 0.025, 0.03)` for every truncation point yielding one α-independent `coefficient_ratio`, with `r_4(α²) = α² · coefficient_ratio` reported at `α² ∈ {0.05, 0.5, 1.0}` as derived values at no extra compute cost; (3) §3.1 grid topology declared one-axis-at-a-time anchored at `(4, 3, omega_max_factor = 30)` with cross-terms optional, §5.3 adds an explicit Hilbert-tightening witness requirement (omega_max_factor sweep alone insufficient for `truncation-converged`), §4.3 drift redefined against the production anchor over non-degraded evaluated points. R2 risk reframed (production fit α grid is fixed; extrapolation uncertainty is a production-side concern). R1 risk extended with preflight `d_joint` estimator + hard process timeout. §8 steward-decisions list mirrors the revised ranges and adds a Hilbert-tightening confirmation row. Awaiting steward countersignature in §10. | Steward freeze blockers (Ulrich Warring); revisions executed by Claude Opus 4.7. |
| v0.1.0 | 2026-05-13 | Frozen after steward review. Countersignature confirms the revised grid, production α-fit handling, Hilbert-tightening witness requirement, drift threshold, artefact path, wall-time budget, skip mechanism, and routing matrix. Minor freeze-time wording cleanup in §4.1 aligns the driver description with the revised single-fit-per-truncation design. | Codex (GPT-5 local steward review). |

---

*Verification card version: v0.1.0 (frozen 2026-05-13). Scopes the
Phase E Track 5.C Path B floor audit at the D1 σ_x fixture. Does NOT
issue a Phase E classification. Implementation may proceed under this
card. CC-BY-4.0 (see ../LICENSE-docs).*

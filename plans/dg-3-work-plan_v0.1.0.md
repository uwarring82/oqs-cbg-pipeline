---
plan_id: dg-3-work-plan
version: v0.1.0
date: 2026-05-05
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§5 (Tier 3), 9 (DG-3), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entries 1–7 (COMPATIBLE); Entry 7 (UNDERDETERMINED)
anchor_envelope: docs/validity_envelope.md DG-3 row (NOT YET ATTEMPTED → target implementation-ready PASS; failure-asymmetry clearance aspirational)
status: draft
superseded_by: dg-3-work-plan_v0.1.1.md
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-3 Work Plan — Cross-Method Validation

## 1. Objective

Pass DG-3 as defined in Sail v0.5 §9:

> *Pass if benchmark comparisons against at least two independent established methods are implemented, with at least one pair drawn from non-overlapping failure-mode families.*

This plan operationalises that objective in **benchmark-cards-first** ordering, extending the discipline established in the DG-1 work plan (v0.1.4). Two benchmark cards (`C1`, `C2`) are drafted and frozen *before* the cross-method reference implementations (`benchmarks/exact_finite_env.py`, `benchmarks/qutip_reference.py`) are completed. The ordering mitigates Sail v0.5 §10 Risk #6 (*"building a codebase before defining benchmark cards"*) and Risk #8 (*"overfitting the pipeline to known solvable models"*).

### 1.1 Two-level pass structure

Sail v0.5 §9 DG-3 distinguishes two properties that must be tracked separately:

- **Implementation-ready pass**: the methods are implemented, callable, and produce output for the model under test. This is the **minimum** DG-3 pass.
- **Failure-asymmetry-cleared pass**: the pair satisfies the non-overlapping failure-mode rule of `docs/benchmark_protocol.md` §2. This is **aspirational** at v0.3.0.dev0.

This plan targets the **implementation-ready pass** as the primary milestone. The baseline pair (`exact_finite_env.py` + `qutip_reference.py`) belongs to different failure-mode classes (*finite-system* vs *solver-default*), so once implemented they **would** satisfy the pairing rule. However, Sail v0.5 §5 Tier 3 notes that these two methods may share correlated truncation/solver assumptions in certain regimes. Full failure-asymmetry clearance is therefore deferred to a future plan revision that adds a third method from a genuinely non-overlapping class (HEOM, TEMPO, MCTDH, or pseudomode/chain-mapping).

### 1.2 Model selection

Only two models currently expose the full callable API (`hamiltonian`, `coupling_operator`, `system_arrays_from_spec`) required to drive a dynamical benchmark card:

- `models/pure_dephasing.py` (DG-1/DG-2 validated)
- `models/spin_boson_sigma_x.py` (DG-1/DG-2 validated)

`models/jaynes_cummings.py` and `models/fano_anderson.py` are deep stubs (no callable API). DG-3 cards must target the two validated models. A future plan revision can extend to additional models once their APIs and cards are drafted.

### 1.3 Card-parameter inheritance

To maximise cross-card comparability, DG-3 cards inherit frozen parameters from their DG-1/DG-2 siblings on a per-case basis:

- **Card C1** (pure_dephasing): the `thermal_bath_cross_method` test case inherits `bath_spectral_density`, `time_grid`, and integration tolerances from **Card A3 v0.1.1**; the `displaced_bath_delta_omega_c_cross_method` test case inherits its `bath_state` and `displacement_profile` from **Card B4-conv-registry v0.1.0**. (A3 v0.1.1 does not carry a displaced case — it was removed in the A3 v0.1.0 → v0.1.1 supersedure per the DG-2 deferral.)
- **Card C2** (spin_boson_sigma_x): same per-case split, with **Card A4 v0.1.1** supplying the thermal anchor and **Card B5-conv-registry v0.2.0** supplying the displaced anchor.

The inherited parameters are **not** silently edited; they are re-frozen in the new card with an explicit `failure_mode_log` entry citing the predecessor card. This preserves the audit trail required by `docs/benchmark_protocol.md` §4.

## 2. Scope

### 2.1 In scope

- Two DG-3 benchmark cards (`C1`, `C2`), one per validated model, each with a frozen-parameter block and an empty result block.
- Implementation of the baseline cross-method pair:
  - `benchmarks/exact_finite_env.py` — exact propagation of system + finite environment via diagonalisation or matrix exponential.
  - `benchmarks/qutip_reference.py` — QuTiP-based master-equation reference (Lindblad or Bloch–Redfield solver dispatch).
- Runner extensions in `reporting/benchmark_card.py` to support cross-method comparison:
  - A new `_run_cross_method` branch or extension of `_run_dynamical` that compares two method outputs against a tolerance.
  - New test-case handler registration for DG-3 cases.
- `docs/benchmark_protocol.md` §3 update: mark baseline pair as **IMPLEMENTED** and **CLEARED** (pending actual implementation).
- DG-3 verdict logbook entry (`logbook/YYYY-MM-DD_dg-3-{pass,fail-with-cause}.md`).
- Validity-envelope update (`docs/validity_envelope.md`) on verdict.
- Repository tag `v0.4.0` on implementation-ready PASS, or appropriate dev bump on partial progress.

### 2.2 Out of scope

- HEOM, TEMPO, MCTDH, or pseudomode/chain-mapping implementations: aspirational for failure-asymmetry clearance, not required for the implementation-ready pass.
- `models/jaynes_cummings.py` and `models/fano_anderson.py` callable API: deferred to DG-2/DG-5 plan revisions.
- DG-4 failure-envelope identification: separate work plan.
- DG-5 thermodynamic discriminant: separate work plan; routes via Council deliberation.
- Higher-order recursion (K_2–K_4 literal numerical recursion): DG-2 territory, tracked separately.

### 2.3 Explicit non-claims

DG-3 PASS does **not** establish:
- That the CBG construction is correct in regimes beyond those exercised by Cards C1, C2.
- That the baseline pair's agreement is free from coincident-truncation artefacts (failure-asymmetry clearance requires a third method).
- That alternative gauges (HMF, polaron, Mori) are adjudicated (DG-5 territory).

## 3. Phases

### Phase A — Card drafting (this commit)

- Draft `C1_cross-method-pure-dephasing_v0.1.0.yaml` and `C2_cross-method-spin-boson_v0.1.0.yaml`.
- Validate cards against SCHEMA.md v0.1.2.
- Freeze cards with `status: frozen-awaiting-run`.

### Phase B — Method implementation

- Implement `exact_finite_env.propagate`:
  - Input: `H_total` (system + bath Hamiltonian as dense or sparse matrix), `rho_initial` (full system+bath density matrix), `t_grid` (time points).
  - Output: `rho_system_t` (reduced density matrix at each time point).
  - Strategy: diagonalise `H_total`, evolve each eigenstate, trace out bath at each time step.
  - Bath size: start with 4–8 modes (small enough for exact diagonalisation, large enough to show non-trivial dynamics).
- Implement `qutip_reference.reference_propagate`:
  - Input: `model_spec` (dict from benchmark card `frozen_parameters.model`), `t_grid`, optional `solver_options`.
  - Output: `rho_system_t` (reduced density matrix at each time point).
  - Strategy: construct QuTiP `Qobj` Hamiltonian and collapse operators from `model_spec`, dispatch to `mesolve` or `brmesolve`, return expectation values or full state.
  - **Warning**: bath correlations must be sourced from `cbg.bath_correlations`, not from QuTiP defaults.

### Phase C — Runner wiring

- Extend `reporting/benchmark_card.py` with cross-method comparison logic.
- Register DG-3 test-case handlers.
- Validate that Phase B implementations satisfy the frozen parameters of Cards C1 and C2.

### Phase D — Verdict

- Run Cards C1 and C2.
- Populate result blocks.
- Commit verdict.
- Fill self-referential commit_hash placeholders.
- Update validity envelope and logbook.

## 4. Acceptance criteria

### Card C1 (pure_dephasing)

PASS iff, for the frozen parameter set inherited from A3/B4:

1. `exact_finite_env.propagate` and `qutip_reference.reference_propagate` both run to completion without raising.
2. Both methods return reduced density matrices `rho_exact(t)` and `rho_qutip(t)` at every point of the frozen time grid.
3. The inter-method discrepancy
   ```
   max_t ||rho_exact(t) - rho_qutip(t)||_F / max(||rho_exact(t)||_F, ||rho_qutip(t)||_F)
   ```
   is ≤ the frozen threshold (1.0e-6) for the thermal bath case.

### Card C2 (spin_boson_sigma_x)

Same structure as C1, applied to the `spin_boson_sigma_x` model with parameters inherited from A4/B5.

## 5. Risks and mitigations

| Risk | Mitigation |
|---|---|
| QuTiP dependency is heavy and may fail on CI | Pin QuTiP version in `pyproject.toml`; use `pip install -e ".[dev]"` which already declares `qutip>=4.7`. |
| Exact diagonalisation is exponentially costly in bath size | Keep bath mode count small (4–8 modes) for baseline pair; document the truncation in `frozen_parameters.truncation.bath_mode_cutoff`. |
| The two methods agree by coincidence (shared assumptions) | Documented as a known limitation; failure-asymmetry clearance deferred to third method. |
| Cross-method comparison requires schema changes | Keep schema changes minimal; if a new `model_kind` is needed, bump SCHEMA.md minor version and retain backward compatibility. |

## 6. Dependencies

- DG-1 PASS (completed 2026-04-30, tag v0.2.0).
- DG-2 structural sub-claims PASS (completed 2026-05-04).
- `models/pure_dephasing.py` and `models/spin_boson_sigma_x.py` callable API (available).
- `cbg.tcl_recursion.K_total_thermal_on_grid` and `K_total_displaced_on_grid` (available for orders ≤ 2).

---

*Plan version: v0.1.0. Drafted 2026-05-05. CC-BY-4.0 (see ../LICENSE-docs).*

# Benchmark Protocol — `oqs-cbg-pipeline`

**Layer:** Repository protective scaffolding
**Anchor:** Sail v0.5 §11 (four explicit content requirements)
**Last updated:** 2026-05-13 (Phase E Track 5.C Path B floor audit landed `floor-dominated`; D1 v0.1.2 PASS unchanged. Prior verdict update: 2026-05-06 DG-4 PASS at D1 v0.1.2 via picture-fixed Path B numerical L_4; supersedes the v0.1.1 verdict downgraded on review the same day.)

---

This document specifies the protocols required by Sail v0.5 §11:

1. Coordinate-choice annotation template (Sail §4 output discipline).
2. Failure-mode starter taxonomy for Tier 3 methods (Sail §5).
3. DG-3 readiness vs. failure-asymmetry-clearance status tracking (Sail §9).
4. DG-4 status tracking (Sail §9).
5. DG-5 status tracking (Sail §9).
6. Parameter-freezing protocol enforcing Risk #8 mitigation (Sail §10).

## 1. Coordinate-choice annotation template

Every plot, table, or report that exhibits K(t) — or any quantity derived from it — must carry the following annotation, either as a figure caption, table footer, or report footnote:

```
K(t) is computed under the Hayden–Sorce minimal-dissipation gauge.
The displayed quantity is a coordinate-dependent representation of the
coherent part of the TCL generator, not a directly measured Hamiltonian.
Comparisons with quantities computed under other gauges (e.g. Hamiltonian
of mean force, polaron, Mori) require explicit gauge alignment.
```

For machine-readable contexts (benchmark cards, JSON exports), the equivalent annotation is:

```yaml
gauge: hayden-sorce-minimal-dissipation
coordinate_dependent: true
direct_observable: false
gauge_alignment_required_for_comparison: [hmf, polaron, mori]
```

The annotation template itself is versioned. Future updates (e.g. when DG-5 outputs introduce alternative gauge results) will increment this template's version, but the requirement that *some* annotation be present never lapses.

## 2. Failure-mode starter taxonomy

The Tier 3 failure-asymmetry requirement (Sail v0.5 §5 Tier 3) requires that benchmark pairs draw from non-overlapping failure-mode classes. The following starter taxonomy is provided so that implementers do not have to reconstruct it from the literature:

| Method | Primary failure modes | Class | Notes |
|---|---|---|---|
| HEOM (hierarchical equations of motion) | Hierarchy truncation; fitting of bath spectral density into Drude–Lorentz peaks; numerical instability at large hierarchy depth | Hierarchy-truncation class | Tanimura, Y., *J. Chem. Phys.* **153**, 020901 (2020) |
| TEMPO / process tensor | Memory-cutoff parameter; bond-dimension truncation in MPS representation; convergence in time-step | Memory-cutoff class | Strathearn et al., *Nat. Commun.* **9**, 3322 (2018) |
| MCTDH (multi-configuration time-dependent Hartree) | Single-particle basis truncation; configuration-space truncation; convergence in basis size | Basis-truncation class | Beck et al., *Phys. Rep.* **324**, 1 (2000) |
| Exact diagonalisation (finite environment) | Finite-bath size; recurrence times; mode-density approximation of continuous bath | Finite-system class | Standard textbook |
| QuTiP master-equation solvers | Solver assumptions (Lindblad, Bloch–Redfield) embedded in solver choice; secular approximations; Born–Markov defaults | Solver-default class | Johansson et al., *Comp. Phys. Commun.* **184**, 1234 (2013) |
| Pseudomode / chain-mapping | Number of pseudomodes; chain-length truncation; auxiliary Lindblad rates | Auxiliary-system class | Tamascelli et al., *PRL* **120**, 030402 (2018) |

**Failure-asymmetry pairing rule.** A Tier 3 benchmark pair satisfies the failure-asymmetry requirement if and only if the two methods come from *different* classes in this taxonomy. For example, exact-diagonalisation (finite-system class) + HEOM (hierarchy-truncation class) satisfies the rule; QuTiP master-equation (solver-default class) + exact-diagonalisation (finite-system class) also satisfies; QuTiP + QuTiP-with-different-solver does not.

This taxonomy will be revised as the repository's experience with each method matures. Any revision is logged in `logbook/`.

## 3. DG-3 status tracking

Per Sail v0.5 §9, two distinct properties must be tracked separately for any DG-3-relevant method pair:

- **Implementation readiness**: the methods are implemented, callable, and produce output for the model under test.
- **Failure-asymmetry clearance**: the pair satisfies the rule of §2 above.

Current status (mirrors `validity_envelope.md`):

| Triple | Implementation readiness | Failure-asymmetry clearance |
|---|---|---|
| `exact_finite_env.py` + `qutip_reference.py` + `heom_reference.py` | COMPLETE for the C1/C2 v0.2.0 thermal fixtures (triple-method dispatch); baseline pair runner-reachable for the C1/C2 v0.1.0 displaced fixtures retained for reproduction | NOT CLEARED — Phase D verdict on C1/C2 v0.2.0 is **blocked** (cause `finite-env-correlator-floor`; Phase D.0/D.1 recon 2026-05-16). The three method classes are non-overlapping per §2, but the frozen gating pair `(exact_finite_env, heom_reference)` @1e-6 is physically unsatisfiable: `exact_finite_env`'s discrete bath correlator converges only ≈ O(1/n_modes) vs the continuous bath HEOM solves. Recommended route (steward-gated): TEMPO/OQuPy as HEOM's gating partner via C1/C2 v0.3.0. See logbook [`2026-05-16_dg-3-phase-d-recon-gating-pair-blocked`](../logbook/2026-05-16_dg-3-phase-d-recon-gating-pair-blocked.md). |

DG-3 *implementation-ready pass* requires only the first column. DG-3 *failure-asymmetry-cleared pass* requires both. Reports must explicitly state which level of pass is being claimed.

### 3.1. Benchmark cards

Active DG-3 cards (frozen):

| Card | Model | Methods compared | Status |
|---|---|---|---|
| C1 v0.2.0 | pure_dephasing | exact_finite_env + qutip_reference + heom_reference (gating pair: `[exact_finite_env, heom_reference]`) | frozen-awaiting-run; thermal-only triple-method (displaced fixture deferred to a future C1 v0.3.0) |
| C2 v0.2.0 | spin_boson_sigma_x | exact_finite_env + qutip_reference + heom_reference (same gating pair) | frozen-awaiting-run; thermal-only triple-method |

Superseded predecessors (retained for audit and reproduction of the baseline-pair runner reachability):

| Card | Model | Methods compared | Status |
|---|---|---|---|
| C1 v0.1.0 | pure_dephasing | exact_finite_env + qutip_reference | superseded by C1 v0.2.0; both fixtures run to clean FAIL on the pair branch (thermal: `error ≈ 0.293`; displaced delta-omega_c: `error ≈ 0.309`; threshold 1.0e-6) |
| C2 v0.1.0 | spin_boson_sigma_x | exact_finite_env + qutip_reference | superseded by C2 v0.2.0; both fixtures run to clean FAIL (thermal: `error ≈ 0.538`; displaced delta-omega_c: `error ≈ 0.526`; threshold 1.0e-6) |

Cards inherit frozen parameters from their DG-1/DG-2 siblings (A3/B4 and A4/B5) to preserve cross-card comparability. The runner has a DG-3 cross-method comparison branch (`reporting.benchmark_card._run_cross_method`) that detects `comparison.third_method` and dispatches to the triple-handler registry `_CROSS_METHOD_TRIPLE_HANDLERS` for C1/C2 v0.2.0; the pair-handler path remains active for the v0.1.0 superseded surface. **No `NotImplementedError` paths are reachable on the frozen C1/C2 test fixtures.** (The underlying benchmark modules retain `NotImplementedError` paths for non-frozen parameter combinations; those paths are out of scope for the C1/C2 frozen surface.) HEOM is added via QuTiP 5's in-tree `qutip.solver.heom.HEOMSolver` (BSD-3, reached via the `qutip>=5.2` dependency floor); bath correlations are sourced from `cbg.bath_correlations.bath_two_point_thermal` and fitted to a multi-exponential expansion via QuTiP's CF NLSQ fitter so the bath spectrum is *cbg-owned*, not QuTiP-default. Phase D verdict on C1/C2 v0.2.0 is **blocked** (cause `finite-env-correlator-floor`; Phase D.0/D.1 reconnaissance 2026-05-16): the frozen gating pair `(exact_finite_env, heom_reference)` cannot reach 1e-6 because `exact_finite_env`'s discrete bath correlator converges only ≈ O(1/n_modes) toward the continuous bath HEOM solves (~10⁶ modes needed, ~8 feasible); HEOM is internally converged and cbg is correct (no convention bug). The v0.2.0 cards remain frozen and unmutated; the recommended route (steward decision pending) is to supersede them with C1/C2 v0.3.0 gating HEOM vs TEMPO (OQuPy), per DG-3 work plan v0.1.1 §2.3. See logbook [`2026-05-16_dg-3-phase-d-recon-gating-pair-blocked`](../logbook/2026-05-16_dg-3-phase-d-recon-gating-pair-blocked.md).

## 4. DG-4 status tracking

Per Sail v0.5 §9 DG-4, the repository must identify at least one reproducible, cause-labelled failure regime. The five mandatory cause labels are:

1. `convergence failure`
2. `TCL singularity`
3. `projection ambiguity`
4. `truncation artefact`
5. `benchmark disagreement`

One DG-4 failure-envelope card is frozen:

| Card | Model | Sweep parameter | Target cause label | Status |
|---|---|---|---|---|
| D1 v0.1.2 | spin_boson_sigma_x | coupling_strength (0.05 → 1.0, log-uniform, 20 points) | convergence failure via parity-aware `r_4(α²) = α² · <||L_4^dis||>_t / <||L_2^dis||>_t` | **pass** (picture-fixed Path B numerical L_4; all 20 points `convergence_failure`; all four reproducibility perturbations operational; max baseline `r_4 ≈ 47.42` at α² = 1.0; min perturbed coefficient ratio `≈ 41.47`) |
| D1 v0.1.1 | spin_boson_sigma_x | (same) | (same) | superseded by v0.1.2 (2026-05-06; original PASS verdict at tag `v0.5.0` downgraded on review for two HIGH-severity defects in Path B; see below) |

The v0.1.0 predecessor targeted pure_dephasing and is superseded: thermal pure dephasing is TCL-2 exact, so no order-4 convergence signal can appear. D1 v0.1.1 adopted the σ_x thermal model and the parity-aware even-order dissipator ratio specified by DG-4 work plan v0.1.4.

As of 2026-05-06, `run_card(D1 v0.1.2)` routes through `reporting.benchmark_card._run_dg4_sweep` and returns PASS. The full frozen run classified all 20 `coupling_strength` values from 0.05 to 1.0 as `convergence_failure`, with stability across all four reproducibility perturbations (`upper_cutoff_factor ∈ {20, 40}` via the runner threading the value into `omega_max_factor`, and `omega_c ∈ {9, 11}` via direct model-spec mutation). No `α_crit` is interpolated inside the frozen range because the first swept point already fails; under this Path B run the boundary lies below `coupling_strength = 0.05`. The audit-complete result JSON at [`benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json`](../benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json) persists per-α + per-α-per-perturbation `r_4` plus per-perturbation Path B fit residuals.

### v0.1.1 supersedure history

D1 v0.1.1 ran a PASS verdict on 2026-05-06 (tag `v0.5.0`), which was **superseded on review** the same day for two HIGH-severity defects:

1. **Path B picture/baseline extraction was in the wrong frame.** [`benchmarks/numerical_tcl_extraction.py`](../benchmarks/numerical_tcl_extraction.py) under v0.1.1 computed `L_2 = dΛ_2/dt` and `L_4 = dΛ_4/dt - L_2 Λ_2` — the order-4 expansion of `L_t = Λ̇_t Λ_t⁻¹` only when the closed-system map `Λ_0` is the identity. For σ_x thermal at `H_S = (ω/2) σ_z`, the omitted `Λ_0⁻¹` similarity and `L_0 Λ_n Λ_0⁻¹` correction terms are nonzero, so the extracted `‖L_n^dis‖` was not picture-invariant. Fixed in v0.1.2 via `transform_to_interaction_picture` applied to the fit coefficients before order-4 extraction.

2. **PASS predicate trivially satisfied for two of four perturbations.** Under v0.1.1, the runner threaded `upper_cutoff_factor` into a `numerical_overrides` annotation on the model_spec but never reached the finite-env builder; `r_4_perturbed == r_4_baseline` for those two perturbations. Fixed in v0.1.2 via `_path_b_evaluate` threading the knob into the builder's `omega_max_factor` kwarg.

A MEDIUM audit-completeness gap was also recorded — per-α + per-α-per-perturbation `r_4` not persisted in the result JSON; only aggregate counts. Fixed in v0.1.2 via `CardResult.dg4_sweep_data` + `write_dg4_result_json`.

The supersedure is recorded in [`logbook/2026-05-06_dg-4-pass-path-b-superseded.md`](../logbook/2026-05-06_dg-4-pass-path-b-superseded.md); the v0.1.2 verdict log is at [`logbook/2026-05-06_dg-4-pass-path-b-v012.md`](../logbook/2026-05-06_dg-4-pass-path-b-v012.md). The `v0.5.0` git tag is left as immutable history of the v0.1.1 commit; v0.1.2 is the live verdict.

Path A (Companion Sec. IV analytic) remains the preferred deliverable for machine-precision L_4 evaluation and follows the v0.1.2 verdict. The Phase E Track 5.C Path B floor audit (2026-05-13; frozen card v0.1.0 at `bbdc237`, executed at commit `b4bda20`; result JSON at [`benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json`](../benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json)) characterised Path B's reference at the D1 production fixture and landed cause label **`floor-dominated`**: the production `coefficient_ratio = 47.4` shifts by **24%** under truncation tightening across `omega_max_factor`, `n_levels_per_mode`, and `n_bath_modes`, with the three axes pulling in **mutually inconsistent directions**. Per 5.C card §4.4, this rules out using Path B as the analytic-comparison reference for a Phase E classification verdict; Phase E routing now requires Path A as single-sided ground truth, DG-3 Tier-2.A (third method) as Path B's replacement, or a permanent `unclassified-pilot` state. The D1 v0.1.2 PASS verdict is unchanged.

## 5. DG-5 status tracking

Per Sail v0.5 §9 DG-5, the repository must demonstrate numerically distinguishable predictions between the minimal-dissipation K(t) and a competing thermodynamic framework in one solvable model. One scope-definition card is frozen:

| Card | Model | Competing framework | Observable | Status |
|---|---|---|---|---|
| E1 | fano_anderson | Hamiltonian of mean force (HMF) | impurity_occupation_dynamics | frozen-awaiting-run (scope definition) |

Card E1 preconditions are not yet met:
- `models/fano_anderson.py` has no callable API.
- No HMF reference implementation exists in the repository.
- `cbg.bath_correlations` does not support fermionic baths.

DG-5 outputs route via fresh Council deliberation per Sail §9; they do not unilaterally modify the Ledger. `run_card(E1)` raises `ScopeDefinitionNotRunnableError` (a `NotImplementedError` subclass) that surfaces the recorded preconditions from the card's `failure_mode_log` / `result.notes` rather than failing with a generic missing-model-factory message.

## 6. Parameter-freezing protocol (Risk #8 mitigation)

Per Sail v0.5 §10 Risk #8, every parameter choice that affects Tier 1–3 outcomes must be set *before* benchmarking and recorded in the benchmark card. This document specifies the operational protocol:

### 6.1. Parameters that must be frozen

The following parameters must be frozen before any benchmark run:

- **Model parameters**: Hamiltonian coefficients, system–environment partition, coupling operators, bath state, temperature, spectral density.
- **Truncation parameters**: bath cutoff, basis size, hierarchy depth (HEOM), bond dimension (TEMPO), pseudomode count.
- **Numerical parameters**: time-grid step size, integration tolerance, perturbative order, gauge choice.
- **Comparison parameters**: target observable, error metric, agreement threshold, projection scheme (for non-TCL methods, per Sail §2 representation commitment).

### 6.2. Recording protocol

Each benchmark card carries a `frozen_parameters:` block at the top, populated *before* the benchmark is run. The block is committed to the repository. The benchmark is then run, and the result (PASS / FAIL / CONDITIONAL) is appended.

### 6.3. Post-hoc adjustments

If a parameter is changed *after* the initial run — for any reason, including a discovered bug — this is *not* silent revision. The card is retained with its original verdict; a *new* card is created with the new parameter set, *and* a `failure_mode_log` entry is added explaining what changed and why. The original card is annotated `superseded by <new-card-id>`. No card is ever silently deleted or edited post-result.

### 6.4. Parameter-sweep distinction

A *parameter sweep* (e.g. running the same benchmark over a range of bath cutoffs to verify convergence) is *not* a post-hoc adjustment. Sweeps are part of the frozen design: the sweep range is itself a frozen parameter, declared before the run. A sweep that reveals divergence at one end of the range is a DG-4 failure-envelope finding, not a justification for tightening the range and re-running.

### 6.5. Audit

A future steward (including a non-conflicted future steward) must be able to reconstruct, from the recorded benchmark cards alone, which parameters were frozen for each run, when they were frozen, and what the resulting verdict was. The reconstruction must not require access to internal communications, side-channel notes, or the original implementer's recollection.

---

*This document is non-optional per Sail v0.5 §11. It must exist at HEAD before any benchmark card is committed.*

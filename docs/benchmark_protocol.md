# Benchmark Protocol — `oqs-cbg-pipeline`

**Layer:** Repository protective scaffolding
**Anchor:** Sail v0.5 §11 (four explicit content requirements)
**Last updated:** 2026-05-06 (DG-4 Phase B partial — TCL thermal-Gaussian recursion wired through n=3; n=4 deferred)

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

| Pair | Implementation readiness | Failure-asymmetry clearance |
|---|---|---|
| `exact_finite_env.py` + `qutip_reference.py` | COMPLETE for all four C1+C2 fixtures | NOT CLEARED at DG level; method classes are distinct (`finite-system` vs `solver-default`), but third-method clearance from a non-overlapping class (HEOM, TEMPO, MCTDH, pseudomode/chain-mapping) remains deferred |

DG-3 *implementation-ready pass* requires only the first column. DG-3 *failure-asymmetry-cleared pass* requires both. Reports must explicitly state which level of pass is being claimed.

### 3.1. Benchmark cards

Two DG-3 cross-method cards are frozen:

| Card | Model | Methods compared | Status |
|---|---|---|---|
| C1 | pure_dephasing | exact_finite_env vs qutip_reference | frozen-awaiting-run; both fixtures run to clean FAIL (thermal: `error ≈ 0.293`; displaced delta-omega_c: `error ≈ 0.309`; threshold 1.0e-6) |
| C2 | spin_boson_sigma_x | exact_finite_env vs qutip_reference | frozen-awaiting-run; both fixtures run to clean FAIL (thermal: `error ≈ 0.538`; displaced delta-omega_c: `error ≈ 0.526`; threshold 1.0e-6) |

Cards inherit frozen parameters from their DG-1/DG-2 siblings (A3/B4 and A4/B5) to preserve cross-card comparability. The runner now has a DG-3 cross-method comparison branch (`reporting.benchmark_card._run_cross_method`) with handlers registered for **all four** C1+C2 fixtures. Phase D verdict commits for both C1 and C2 are structurally reachable; their admissibility requires either convergence in the finite-bath truncation or a third reference method from a non-overlapping failure-mode class (Sail v0.5 §5 Tier 3). **No `NotImplementedError` paths remain for C1/C2 frozen test cases.**

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
| D1 | pure_dephasing | coupling_strength (0.05 → 1.0, log-uniform, 20 points) | convergence failure | frozen-awaiting-run |

The runner does not yet support parameter sweeps; `run_card(D1)` raises `DG4SweepRunnerNotImplementedError` naming the two missing pieces. As of 2026-05-06, DG-4 work plan v0.1.2 Phase B has landed B.0, B.1, and B.2 (n=3) — `cbg.tcl_recursion` is wired through perturbative_order = 3 on the thermal-Gaussian path, with K_3 = 0 verified on A3/A4 fixtures. The two remaining gates before D1 v0.1.1 can be evaluated are (i) Phase B.2 (n=4) — the convergence-detection signal, where σ_z gives 0 by Feynman-Vernon and σ_x gives the leading non-trivial higher-order TCL contribution — and (ii) the sweep-block-aware runner branch consuming `frozen_parameters.sweep` per SCHEMA.md v0.1.3 Rule 17. The card defines the sweep range frozen *before* any run, per the parameter-freezing protocol §6.

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

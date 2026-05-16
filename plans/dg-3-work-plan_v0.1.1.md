---
plan_id: dg-3-work-plan
version: v0.1.1
date: 2026-05-15
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§5 (Tier 3), 9 (DG-3), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entries 1–7 (COMPATIBLE); Entry 7 (UNDERDETERMINED)
anchor_envelope: docs/validity_envelope.md DG-3 row (FULL RUNNER REACHABILITY — all four C1+C2 fixtures runner-wired 2026-05-05; failure-asymmetry clearance still gated on a third method)
status: draft
supersedes: dg-3-work-plan_v0.1.0.md
superseded_by: dg-3-work-plan_v0.1.2.md
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-3 Work Plan — Tier-2.A Third-Method Selection (HEOM primary, TEMPO fallback)

## 1. Objective

Pass DG-3 as defined in Sail v0.5 §9:

> *Pass if benchmark comparisons against at least two independent established methods are implemented, with at least one pair drawn from non-overlapping failure-mode families.*

### 1.1 What changed since v0.1.0

The v0.1.0 plan targeted the **implementation-ready pass** — i.e. wiring the baseline pair (`benchmarks/exact_finite_env.py` + `benchmarks/qutip_reference.py`) into a runnable cross-method comparison. That work has now landed (Phase A–C completed under v0.1.0, recorded in [validity_envelope.md DG-3 row](../docs/validity_envelope.md) as **FULL RUNNER REACHABILITY** on 2026-05-05): all four C1+C2 fixtures are runner-wired through `reporting.benchmark_card._run_cross_method`, no `NotImplementedError` paths are reachable on the frozen fixtures, and the baseline pair runs to clean FAIL at the frozen 1.0e-6 threshold with Markov-vs-exact gaps of ~0.3 (σ_z) and ~0.5 (σ_x).

The remaining DG-3 blocker is **failure-asymmetry clearance** per Sail v0.5 §5 Tier 3: the baseline pair's two methods belong to distinct failure-mode classes (*finite-system* vs *solver-default*), but Sail §5 Tier 3 explicitly flags that they may share correlated truncation/solver assumptions in certain regimes. Full clearance requires a **third method from a genuinely non-overlapping class** (HEOM, TEMPO, MCTDH, or pseudomode/chain-mapping).

The 2026-05-13 routing-fork recommendation ([logbook/2026-05-13_dg-4-routing-fork-recommendation.md](../logbook/2026-05-13_dg-4-routing-fork-recommendation.md)) further established that the same third method is **two-for-one**: it both lifts DG-3 from RUNNER-COMPLETE → PASS and provides the Path B replacement that DG-4 Phase E now needs after the 5.C `floor-dominated` audit.

v0.1.1 therefore re-scopes the DG-3 work plan to a **Tier-2.A third-method selection plan**. The baseline-pair implementation text from v0.1.0 (Phases A–C, acceptance criteria for C1/C2 under the two-method comparison) moves to §7 historical context; the active scope is selecting, scaffolding, and integrating the third method.

### 1.2 Tier-2.A scope (active)

This plan covers:

1. **Selection** of the preferred third-method family with rationale (§2).
2. **Module-boundary** definition: a new top-level `benchmarks/<third-method>_reference.py` module per chosen family, kept separate from `benchmarks/qutip_reference.py` so the hierarchy-truncation / process-tensor / etc. failure class remains auditable as a distinct artefact.
3. **Card revision** strategy: a successor pair (`C1 v0.2.0`, `C2 v0.2.0`) extending the cross-method comparison to a triple, with the third-method threshold and per-fixture acceptance criteria frozen on the same A3/A4/B4/B5 parameter inheritance pattern as v0.1.0.
4. **Phase ordering** for integration, runner-wiring, and verdict.

Out of scope (deferred or covered elsewhere): the baseline-pair runner wiring (done under v0.1.0), DG-4 Path A convergence (Tracks 5.A / 5.B of the DG-4 v0.1.5 plan), DG-5 thermodynamic discriminant.

## 2. Third-method family selection

### 2.1 Accessibility audit (2026-05-15)

| Method | Reference package | Latest version | Last activity | Licence | Python-native | Verdict |
|---|---|---|---|---|---|---|
| **HEOM** | QuTiP 5 (in-tree, `qutip.solver.heom.HEOMSolver`) | 5.2.3 | Released 2026-01-26 | BSD-3 | yes | **Selected** |
| **TEMPO** | OQuPy | 0.5.0 (pkg release 2024-06-24) | Last commit on `main` 2026-03-01 | Apache-2.0 | yes | **Fallback** |
| **Pseudomode** | QuTiP `mesolve` + auxiliary Lindblad modes (no dedicated package) | — | — | — | yes (implementer-built) | **Note: viable third option** if both HEOM and TEMPO are blocked |
| **MCTDH** | Heidelberg MCTDH / QuantICs | — | — | gated (Heidelberg) / open (QuantICs) | no (Fortran) | Not recommended |

Local verification 2026-05-15 in `.venv` (`qutip 5.2.3`): `from qutip.solver.heom import HEOMSolver` imports cleanly. (Note: the import path is `qutip.solver.heom`, not `qutip.solver.heomsolver`; the package layout exposes `HEOMSolver` as a class under the `heom` submodule, per the QuTiP 5.2 source docs at [`qutip/solver/heom/bofin_solvers.html`](https://qutip.readthedocs.io/en/v5.2.3/_modules/qutip/solver/heom/bofin_solvers.html).)

### 2.2 Selected: HEOM via QuTiP 5 in-tree solver

Rationale:

- **Failure-mode class**: *bath-hierarchy truncation*. Distinct from both the *finite-system* class (`exact_finite_env`) and the *solver-default* class (`qutip_reference`'s Lindblad/Bloch–Redfield dispatch). Adding HEOM therefore produces a genuine non-overlapping triple and satisfies Sail v0.5 §5 Tier 3.
- **No new top-level dependency**. The standalone `qutip-bofin` repository ([tehruhn/bofin](https://github.com/tehruhn/bofin)) is explicitly unmaintained, with its README redirecting to "a more stable version of this package … incorporated directly into QuTiP with greater functionality." The integrated solver lives at `qutip.solver.heom.HEOMSolver` in QuTiP 5.2.3. Reaching it requires tightening the existing `pyproject.toml` floor from `qutip>=4.7` to `qutip>=5.2`; no second-party dependency is added.
- **Python-native**, BSD-3 licensed, and ships with documented spin-boson examples ([`qutip.org/docs/latest/guide/guide-heom.html`](https://qutip.org/docs/latest/guide/guide-heom.html)).

### 2.3 Fallback: TEMPO via OQuPy

If HEOM encounters an unforeseen blocker (e.g. upstream regression at the C1/C2 fixture regime, or a non-trivial mismatch with the Hayden–Sorce gauge convention), TEMPO via OQuPy is the next selection. OQuPy 0.5.0 is Apache-2.0, Python-native, actively maintained (last commit 2026-03-01), and represents a different failure-mode class (*process-tensor / MPS-bond-dimension truncation*) that is also non-overlapping with both the baseline pair and HEOM. Switching to TEMPO would re-target this plan onto `benchmarks/oqupy_reference.py` rather than `benchmarks/heom_reference.py`; no other structural change is required.

### 2.4 Note on pseudomode as further fallback

Pseudomode is implementable as a technique on top of QuTiP `mesolve` with auxiliary Lindblad modes but is not packaged with documentation comparable to OQuPy or QuTiP-HEOM. If both HEOM and TEMPO are blocked, pseudomode remains a suitable third option: its failure-mode class (*Lorentzian-fit residual on the bath spectrum*) is non-overlapping with the baseline pair, HEOM, and TEMPO. Scoping it would require the implementer to build the auxiliary-mode scaffolding from primary literature; the module would land as `benchmarks/pseudomode_reference.py` with its own failure-mode class banner mirroring the convention in `benchmarks/qutip_reference.py:1-32`.

### 2.5 MCTDH explicitly not recommended

Heidelberg MCTDH is free for academic use but registration-gated (not OSI-open); the open QuantICs alternative is Fortran-based with a steep learning curve and does not integrate cleanly with the Python-native benchmark-card runner. Neither matches the accessibility bar set by the other three options.

## 3. Module-boundary discipline

The third method **must** land as its own top-level module under `benchmarks/`, not as an extension of `benchmarks/qutip_reference.py`. Rationale: `qutip_reference.py` is documented at [benchmarks/qutip_reference.py:1-32](../benchmarks/qutip_reference.py#L1-L32) as the **solver-default** failure-mode class. The HEOM integration belongs to the **bath-hierarchy truncation** class. Co-locating the two would blur the failure-mode-class auditability that Sail v0.5 §5 Tier 3 relies on. This plan therefore adopts a **one module per failure-mode class** convention for `benchmarks/*_reference.py`, derived from (but not currently explicit in) the [`docs/benchmark_protocol.md`](../docs/benchmark_protocol.md) §2 taxonomy + §2 failure-asymmetry pairing rule. If the convention proves useful, a subsequent revision of `docs/benchmark_protocol.md` §2 can promote it to a protocol clause; until then it is recorded here as the operating convention of this plan.

Concretely, the selected option lands as:

- `benchmarks/heom_reference.py` — new module, failure-mode class = `bath-hierarchy-truncation`.
  - Imports `from qutip.solver.heom import HEOMSolver`.
  - Bath correlations sourced from `cbg.bath_correlations` (same discipline as `qutip_reference.py:12-14`).
  - Public function: `heom_propagate(model_spec, t_grid, solver_options=None) -> np.ndarray`, mirroring the signature of `qutip_reference.reference_propagate`.
  - Internal dispatch by `(system_hamiltonian, coupling_operator, bath_state.family, displacement_profile)` mirroring the `_HANDLERS` registry at [benchmarks/qutip_reference.py:423-443](../benchmarks/qutip_reference.py#L423-L443).
  - Handler set at v0.1.0 of the module: minimum two fixtures (C1 thermal `pure_dephasing × thermal`, C2 thermal `pure_dephasing × σ_x × thermal`). Displaced-bath fixtures deferred to a v0.1.1 of the module unless the cards require them at the first verdict.

The runner-side change to `reporting/benchmark_card.py` is an extension of `_run_cross_method` to support a third-method tolerance pair, not a second runner branch. Schema (`SCHEMA.md`) may need a minor bump to add a `third_method` key under `frozen_parameters.cross_method`; the schema bump is scoped under Phase B below.

## 4. Phases

### Phase A — Decision-record and dependency floor (this commit)

- This plan revision (`dg-3-work-plan_v0.1.1.md`) records the HEOM selection with rationale and audit (§2).
- The accompanying commit also updates [plans/README.md](README.md) to move DG-3 canonical version from v0.1.0 to v0.1.1.
- Tighten `pyproject.toml` floor `qutip>=4.7` → `qutip>=5.2`. Verify the existing test suite still passes against QuTiP 5.2.3 in the development venv before committing.

### Phase B — Module and schema scaffolding

- Create `benchmarks/heom_reference.py` with module-docstring failure-mode banner (mirroring `benchmarks/qutip_reference.py:3-32`).
- Implement `heom_propagate` and a minimum-viable handler set (C1 thermal + C2 thermal at first; displaced handlers deferred unless the v0.2.0 cards require them).
- Schema bump if needed: add `frozen_parameters.cross_method.third_method` field under SCHEMA.md (minor version bump; backward-compatible — absent field = baseline-pair-only card, present field = triple-method card).
- Tests under `tests/test_heom_reference.py`: import smoke test, one-shot propagation on a small bath at the C1 thermal fixture, assertion that the returned shape and dtype match `qutip_reference._propagate_pure_dephasing_thermal` at the same fixture.

### Phase C — Card revision and runner extension

- Draft `C1_cross-method-pure-dephasing_v0.2.0.yaml` and `C2_cross-method-spin-boson_v0.2.0.yaml`, each adding a `third_method: heom` block with its own per-fixture frozen threshold. v0.1.0 cards are retained with `status: superseded` and a `superseded_by:` pointer to v0.2.0; failure_mode_log entries cite the v0.1.0 verdict.
- Extend `reporting.benchmark_card._run_cross_method` to dispatch to a registered third-method propagate function and compute the three-way pairwise discrepancy tensor (or the two relevant pairs against `exact_finite_env`, depending on what the cards specify).
- Register DG-3 v0.2.0 card handlers; ensure the v0.1.0 cards remain reproducible from history.

### Phase D — Run and verdict

- Run Cards C1 v0.2.0 and C2 v0.2.0.
- Populate result blocks.
- Commit verdict.
- Fill self-referential commit_hash placeholders.
- Update `docs/validity_envelope.md` DG-3 row to reflect either PASS (failure-asymmetry cleared) or partial progress with a precise cause label.
- Update `docs/benchmark_protocol.md` §3 to mark the chosen third method as **IMPLEMENTED** and the new triple as **CLEARED** (pending actual outcomes).
- Logbook entry: `logbook/YYYY-MM-DD_dg-3-{pass,fail-with-cause}.md`.
- Repository tag bump on PASS.

## 5. Acceptance criteria

### 5.1 Tier-2.A scoping pass (this plan revision)

This v0.1.1 revision itself PASSes when:

1. The plan is committed and indexed (with `plans/README.md` moved to v0.1.1 canonical).
2. The `qutip>=5.2` floor is in place and `pytest` passes locally against it.

### 5.2 DG-3 failure-asymmetry clearance PASS (downstream verdict — gated by Phases B–D)

DG-3 PASS at the failure-asymmetry-cleared level (Sail v0.5 §9, Tier 3) iff, for each of Cards C1 v0.2.0 and C2 v0.2.0:

1. `exact_finite_env.propagate`, `qutip_reference.reference_propagate`, and `heom_reference.heom_propagate` all run to completion without raising on the frozen fixtures.
2. All three methods return reduced density matrices at every point of the frozen time grid.
3. The pairwise discrepancies that the v0.2.0 card explicitly designates as gating (typically `exact_finite_env` vs `heom_reference`, since these are the two methods most expected to converge to the same value in the chosen regime) are below the frozen threshold.

The frozen pairwise thresholds and the choice of which pair gates the verdict are recorded in Cards C1 v0.2.0 and C2 v0.2.0; this plan does not pre-empt that decision.

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| QuTiP 5.2 floor breaks downstream usage of QuTiP 4.7 API in the existing baseline pair | Run the full test suite at the proposed floor before committing the bump; the change list documented in QuTiP 5 release notes is conservative for `mesolve`/`brmesolve` callers, but verify locally. |
| HEOM correlation-fit (Matsubara expansion) introduces its own truncation parameter that overlaps with `exact_finite_env` mode-count truncation | Document the HEOM truncation parameter explicitly in `benchmarks/heom_reference.py`'s docstring failure-mode banner; the bath-hierarchy-truncation class is conceptually distinct from finite-mode truncation even when both control discretisation of the bath. The v0.2.0 cards must freeze HEOM truncation depth separately from the finite-env mode count. |
| HEOM is too slow at the C1/C2 fixtures' time grids for routine runs | Allow HEOM to run on a coarsened sub-grid declared in the v0.2.0 cards if needed, with interpolation back to the comparison grid. Document the interpolation step in the card's failure_mode_log. |
| HEOM upstream regression between QuTiP 5.2.3 and a future floor bump | Pin the floor at `qutip==5.2.x` if regression patterns appear during Phase B; lift later under explicit review. |
| Selected third-method package becomes unmaintained or licence-restricted | Fall back to TEMPO (OQuPy 0.5.0, last commit 2026-03-01) per §2.3, or to pseudomode per §2.4. The fallback ordering is recorded in §2 and does not require a plan revision unless re-targeted. |
| Schema bump for `third_method` field breaks card readers in older tools | Minor SCHEMA.md bump with backward compatibility (absent field = baseline-pair-only). Confirm `benchmarks/SCHEMA.md` parser accepts both shapes before Phase C. |

## 7. Historical context — baseline-pair text from v0.1.0 (superseded scope)

The v0.1.0 plan's Phases A, B, C and the original Cards C1 v0.1.0 / C2 v0.1.0 acceptance criteria are retained in [`dg-3-work-plan_v0.1.0.md`](dg-3-work-plan_v0.1.0.md) and are not reproduced here. Their execution is recorded in:

- `benchmarks/benchmark_cards/C1_cross-method-pure-dephasing_v0.1.0.yaml` (frozen-awaiting-run; baseline-pair fixtures wired)
- `benchmarks/benchmark_cards/C2_cross-method-spin-boson_v0.1.0.yaml` (frozen-awaiting-run; baseline-pair fixtures wired)
- `benchmarks/exact_finite_env.py`, `benchmarks/qutip_reference.py` (implemented)
- `reporting.benchmark_card._run_cross_method` (implemented)
- `tests/test_benchmark_card.py` DG-3 runner tests (passing)
- `docs/validity_envelope.md` DG-3 row (FULL RUNNER REACHABILITY 2026-05-05)

The v0.1.0 cards are not modified by this plan; they remain the canonical record of the implementation-ready milestone. The v0.2.0 cards drafted under Phase C of this plan supersede them only for the failure-asymmetry-cleared verdict.

## 8. Dependencies

- DG-1 PASS (completed 2026-04-30, tag v0.2.0).
- DG-2 structural sub-claims PASS (completed 2026-05-04).
- DG-3 baseline-pair runner wiring (completed 2026-05-05 under v0.1.0).
- `models/pure_dephasing.py` and `models/spin_boson_sigma_x.py` callable API (available).
- `cbg.tcl_recursion.K_total_thermal_on_grid` and `K_total_displaced_on_grid` (available for orders ≤ 2; n=4 thermal-Gaussian route exposed 2026-05-13).
- QuTiP 5.2.3 in the development venv (verified 2026-05-15: `from qutip.solver.heom import HEOMSolver` imports cleanly).

## 9. Changelog

- **v0.1.1 (2026-05-15)**: Re-scoped from baseline-pair implementation plan to **Tier-2.A third-method selection plan**, reflecting that the baseline-pair runner wiring landed under v0.1.0 (validity envelope DG-3 row 2026-05-05). Selected **HEOM via QuTiP 5 in-tree `qutip.solver.heom.HEOMSolver`** as the third method (BSD-3, no new top-level dependency, distinct *bath-hierarchy-truncation* failure-mode class). **TEMPO via OQuPy 0.5.0** recorded as fallback; **pseudomode** noted as further fallback if both blocked. Required separate module boundary `benchmarks/heom_reference.py` per `docs/benchmark_protocol.md` §2; explicitly forbids extending `benchmarks/qutip_reference.py` to keep the solver-default failure-mode class auditable. New phase structure (A: decision-record + dependency floor; B: module + schema scaffolding; C: card revision C1/C2 v0.2.0 + runner extension; D: run and verdict). Old baseline-pair scope moved to §7 historical context. Linked to the 2026-05-13 DG-4 routing-fork recommendation which independently selected this work as the two-for-one DG-3 + DG-4 Phase E Path B replacement move.
- **v0.1.0 (2026-05-05)**: Initial draft. Implementation-ready pass for the baseline pair `exact_finite_env` + `qutip_reference`. Cards C1 v0.1.0 and C2 v0.1.0 frozen. Phases A–C executed under v0.1.0; superseded by v0.1.1 for the failure-asymmetry-cleared verdict.

---

*Plan version: v0.1.1. Drafted 2026-05-15. CC-BY-4.0 (see ../LICENSE-docs).*

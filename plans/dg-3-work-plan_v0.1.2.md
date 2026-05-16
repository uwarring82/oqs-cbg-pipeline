---
plan_id: dg-3-work-plan
version: v0.1.2
date: 2026-05-16
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§5 (Tier 3), 9 (DG-3), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entries 1–7 (COMPATIBLE); Entry 7 (UNDERDETERMINED)
anchor_envelope: docs/validity_envelope.md DG-3 row (TRIPLE-METHOD CARDS FROZEN; Phase D verdict BLOCKED — cause `finite-env-correlator-floor`, Phase D.0/D.1 recon 2026-05-16; route = HEOM-vs-TEMPO gating via C1/C2 v0.3.0)
status: draft
supersedes: dg-3-work-plan_v0.1.1.md
superseded_by: dg-3-work-plan_v0.1.3.md
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-3 Work Plan — HEOM-vs-TEMPO Gating Pair (v0.2.0 finite-env gate blocked; route to v0.3.0)

## 1. Objective

Pass DG-3 as defined in Sail v0.5 §9:

> *Pass if benchmark comparisons against at least two independent established methods are implemented, with at least one pair drawn from non-overlapping failure-mode families.*

### 1.1 What changed since v0.1.0

The v0.1.0 plan targeted the **implementation-ready pass** — wiring the baseline pair (`benchmarks/exact_finite_env.py` + `benchmarks/qutip_reference.py`) into a runnable cross-method comparison. That work landed (Phase A–C under v0.1.0; validity-envelope DG-3 row "FULL RUNNER REACHABILITY" 2026-05-05): all four C1+C2 v0.1.0 fixtures runner-wired through `reporting.benchmark_card._run_cross_method`, clean FAIL at 1.0e-6 with Markov-vs-exact gaps ~0.3 (σ_z) / ~0.5 (σ_x).

The remaining DG-3 blocker is **failure-asymmetry clearance** per Sail v0.5 §5 Tier 3: a third method from a genuinely non-overlapping class is required. v0.1.1 selected **HEOM via QuTiP 5 in-tree `qutip.solver.heom.HEOMSolver`** and landed it (Phase A/B/C: `benchmarks/heom_reference.py`, schema v0.1.4, C1/C2 v0.2.0 triple-method cards).

### 1.2 What v0.1.2 corrects (Phase D.0/D.1 reconnaissance outcome)

Before running C1/C2 v0.2.0 to a frozen verdict, a bounded Phase D.0 convergence sweep + Phase D.1 correlator-convention audit were performed (logbook [`2026-05-16_dg-3-phase-d-recon-gating-pair-blocked`](../logbook/2026-05-16_dg-3-phase-d-recon-gating-pair-blocked.md)). Findings:

- HEOM is internally converged at default `max_depth=3` (depth / `cf_target_rmse` / `n_pts_correlator` sweeps flat); HEOM is **not** the blocker and is a faithful continuous-bath solver.
- `cbg.bath_correlations` is correct (matches independent quadrature to 5.5e-8); no convention bug (best-fit rescale leaves the residual unchanged); Fock truncation negligible (~8e-4).
- The C1/C2 v0.2.0 gating pair `(exact_finite_env, heom_reference)` @1e-6 is **physically unsatisfiable** (cause `finite-env-correlator-floor`): `exact_finite_env`'s discrete two-point correlator converges to the continuous bath only ≈ O(1/n_modes) (relL2 4.15 @4 modes → 0.33 @64 modes; ~10⁶ modes needed, ~6–8 feasible by dense joint-Hilbert diagonalization). At any tractable mode count the bath it feeds the dynamics is 270–415 % wrong relative to the continuum HEOM solves.

**Consequence — this supersedes the v0.1.1 §2.3 sentence "*no other structural change is required*".** That sentence assumed TEMPO would merely *replace* HEOM as the third method, still gated against `exact_finite_env`. Phase D.1 proved the floor is `exact_finite_env`'s coarse discretization **independent of the partner**: gating `exact_finite_env` against *any* continuous-bath solver (HEOM or TEMPO) hits the same floor. The valid gate is therefore **HEOM vs TEMPO/OQuPy** — two faithful continuous-bath solvers from non-overlapping failure-mode classes — which **is** a structural change (a four-method card + a schema generalization). v0.1.2 records this corrected route. The C1/C2 v0.2.0 cards remain frozen and unmutated (they are the auditable artifact that exposed the bad gate); the correction lands via a normal C1/C2 **v0.3.0** supersedure.

### 1.3 Tier-2.A scope (active under v0.1.2)

1. Plan-surface correction (this revision): supersede the v0.1.1 §2.3 framing; fix the route to HEOM-vs-TEMPO gating.
2. Schema **v0.1.5**: generalize the cross-method comparison block to a `methods` list (§2.6), backward compatible with v0.1.4 (absent `methods` ⇒ existing pair/triple semantics).
3. New module `benchmarks/oqupy_reference.py` (TEMPO via OQuPy; failure-mode class `process-tensor-bond-dimension`).
4. C1/C2 **v0.3.0** four-method cards (Option A) superseding v0.2.0; gating pair `[heom_reference, oqupy_reference]`; `exact_finite_env` + `qutip_reference` retained as non-gating auxiliary trajectories.
5. Runner extension to a registered N-method dispatch; run and verdict.

Out of scope: DG-4 Path A convergence (DG-4 v0.1.5 Tracks 5.A/5.B), DG-5; pseudomode/MCTDH (further fallbacks only, §2.4/§2.5).

## 2. Third-method family selection

### 2.1 Accessibility audit (2026-05-15, OQuPy metadata re-confirmed 2026-05-16)

| Method | Reference package | Latest version | Last activity | Licence | Python-native | Verdict |
|---|---|---|---|---|---|---|
| **HEOM** | QuTiP 5 (in-tree, `qutip.solver.heom.HEOMSolver`) | 5.2.3 | Released 2026-01-26 | BSD-3 | yes | **Landed (Phase A/B/C); converged, faithful** |
| **TEMPO** | OQuPy | 0.5.0 (PyPI release 2024-06-24; Python `>=3.10`) | Last commit on `main` 2026-03-01 | Apache-2.0 | yes | **Promoted to HEOM's gating partner (v0.3.0)** |
| **Pseudomode** | QuTiP `mesolve` + auxiliary Lindblad modes | — | — | — | yes (implementer-built) | Further fallback if HEOM-vs-TEMPO is blocked |
| **MCTDH** | Heidelberg MCTDH / QuantICs | — | — | gated / open | no (Fortran) | Not recommended |

Local verification 2026-05-15 (`.venv`, `qutip 5.2.3`): `from qutip.solver.heom import HEOMSolver` imports cleanly. OQuPy is **not yet installed** in `.venv` (not in `pyproject.toml`); adding `oqupy>=0.5` is the dependency decision recorded in §2.6 and is to be enacted only in the spec/dependency commit (not by ad-hoc install). OQuPy 0.5.0 PyPI metadata (Apache-2.0, Python `>=3.10`) matches this repo's `requires-python >=3.10`.

### 2.2 HEOM — landed, converged, retained as a gating method

HEOM (failure-mode class *bath-hierarchy-truncation*) is implemented at `benchmarks/heom_reference.py`, reached via the `qutip>=5.2` floor (Phase A). Phase D.0 established it is internally converged at `max_depth=3` and is a faithful continuous-bath solver. It is retained as **one half of the v0.3.0 gating pair** — not gated against `exact_finite_env` (see §1.2 / §2.3).

### 2.3 TEMPO via OQuPy — promoted to HEOM's gating partner (corrects v0.1.1 §2.3)

**This subsection supersedes v0.1.1 §2.3 in full.** The v0.1.1 sentence "*Switching to TEMPO would re-target this plan onto `benchmarks/oqupy_reference.py` rather than `benchmarks/heom_reference.py`; no other structural change is required*" is **obsolete and withdrawn**: it presupposed `exact_finite_env` as the gating partner, which Phase D.1 disproved.

Corrected position: TEMPO via OQuPy is promoted **not as a replacement for HEOM but as HEOM's gating partner**. HEOM (*bath-hierarchy-truncation*) and TEMPO (*process-tensor / MPS-bond-dimension truncation*) are both faithful continuous-bath solvers from genuinely non-overlapping failure-mode classes; gating them against each other is the scientifically valid DG-3 Tier-3 check. `exact_finite_env` (finite-system class) and `qutip_reference` (solver-default class) are **retained in the v0.3.0 cards as non-gating auxiliary trajectories** so the finite-bath floor and the Markov reference remain visible in every result without controlling the verdict (Option A; steward decision 2026-05-16).

OQuPy 0.5.0: Apache-2.0, Python-native, Python `>=3.10`, PyPI release 2024-06-24, last `main` commit 2026-03-01. Sources: [PyPI oqupy](https://pypi.org/project/oqupy/), [OQuPy install docs](https://oqupy.readthedocs.io/en/latest/pages/install.html).

### 2.4 Pseudomode — further fallback only

Unchanged from v0.1.1 §2.4: implementable on QuTiP `mesolve` with auxiliary Lindblad modes (*Lorentzian-fit residual* class), non-overlapping with the baseline pair, HEOM, and TEMPO. Invoked only if the HEOM-vs-TEMPO gate is itself blocked. Would land as `benchmarks/pseudomode_reference.py` with its own failure-mode banner.

### 2.5 MCTDH — explicitly not recommended

Unchanged from v0.1.1 §2.5: Heidelberg MCTDH registration-gated (not OSI-open); QuantICs Fortran-based with a steep learning curve; neither integrates cleanly with the Python-native runner.

### 2.6 v0.3.0 card architecture (Option A; general `methods` list — schema v0.1.5)

Steward decision 2026-05-16: **Option A** (four-method card) with a **general `methods` list**, not a one-off `fourth_method`. Schema v0.1.5 generalizes `frozen_parameters.comparison`:

```yaml
comparison:
  methods:
    - exact_finite_env
    - qutip_reference
    - heom_reference
    - oqupy_reference
  method_modules:
    heom_reference: benchmarks.heom_reference
    oqupy_reference: benchmarks.oqupy_reference
  gating_pair:
    - heom_reference
    - oqupy_reference
  heom_options: { ... }     # frozen HEOM knobs (as C1/C2 v0.2.0)
  oqupy_options: { ... }    # frozen TEMPO knobs: dt, dkmax, epsrel, end-time
```

Backward compatibility (mandatory): **absent `methods`** ⇒ existing v0.1.4 pair/triple semantics (the C1/C2 v0.1.0 pair cards and v0.2.0 triple cards continue to validate and run unchanged). `exact_finite_env` and `qutip_reference` are implicit built-in methods (no `method_modules` entry required); only third-party modules are listed under `method_modules`. Rule 19 generalizes: when `methods` is present, `gating_pair` ⊂ `methods`, every non-built-in method has a `method_modules` entry, and a `<method>_options` mapping may be frozen per method.

## 3. Module-boundary discipline

Unchanged in principle from v0.1.1 §3 (one module per failure-mode class). The v0.3.0 route adds a second new module alongside `benchmarks/heom_reference.py`:

- `benchmarks/oqupy_reference.py` — new module, failure-mode class `process-tensor-bond-dimension`.
  - Imports OQuPy (`import oqupy`); uses the TEMPO / process-tensor API.
  - Bath correlations sourced from `cbg.bath_correlations` via OQuPy's custom-correlation path (`oqupy.CustomCorrelations` / custom SD), **never** OQuPy spectral-density defaults — same discipline as `benchmarks/heom_reference.py:12-21` and `benchmarks/qutip_reference.py:12-14`.
  - Public function `oqupy_propagate(model_spec, t_grid, solver_options=None) -> np.ndarray`, mirroring `heom_reference.heom_propagate`.
  - Frozen `oqupy_options` knobs (pinned against the installed OQuPy 0.5.0 API during the module phase): time step `dt`, memory cutoff `dkmax`, bond-dimension/SVD tolerance `epsrel`, end time. Thermal-only handler set first (C1 thermal, C2 thermal), mirroring `heom_reference` v0.1.0-of-module scope.

## 4. Phases

### Phase A–C — landed under v0.1.1 (HEOM track)

- **A** (commit `672db39`): v0.1.1 decision-record + `qutip>=4.7 → >=5.2` floor.
- **B** (commit `f30c627`): `benchmarks/heom_reference.py` + 12 smoke tests.
- **C** (commit `0b750b2`): schema v0.1.4 (Rule 19), C1/C2 v0.2.0 triple-method cards, `_run_cross_method` third-method branch + `_CROSS_METHOD_TRIPLE_HANDLERS`, C1/C2 v0.1.0 atomic supersedure.

### Phase D.0/D.1 — reconnaissance (landed; v0.2.0 gate found blocked)

Convergence sweep + correlator-convention audit (commit `d41ff66`, logbook 2026-05-16). Outcome: cause `finite-env-correlator-floor`; C1/C2 v0.2.0 gating pair unsatisfiable; route corrected (this revision). No frozen verdict run; no DG-3 PASS; v0.2.0 cards unmutated.

### Phase E — plan-surface correction + schema v0.1.5 (this commit + next)

- This revision (`dg-3-work-plan_v0.1.2.md`) supersedes v0.1.1; `plans/README.md` index moved to v0.1.2; v0.1.1 gets the `superseded_by:` annotation.
- Next: schema **v0.1.5** (`methods` list generalization, §2.6; backward compatible) + add `oqupy>=0.5` to `pyproject.toml`. Verify the existing suite still passes (OQuPy import optional until the module lands).

### Phase F — `benchmarks/oqupy_reference.py`

- Implement `oqupy_propagate` + thermal handler set (C1, C2); cbg-sourced correlations; failure-mode banner.
- Tests `tests/test_oqupy_reference.py`: import smoke, shape/dtype, trace/Hermiticity, populations invariant, explicit rejection of unsupported configs (mirrors `tests/test_heom_reference.py`).

### Phase G — C1/C2 v0.3.0 cards + runner N-method dispatch

- Draft `C1/C2 *_v0.3.0.yaml` (Option A; `methods` list; `gating_pair=[heom_reference, oqupy_reference]`; `heom_options`/`oqupy_options` frozen). v0.2.0 cards retained `status: superseded` + `superseded_by:` (atomic, per SCHEMA §Supersedure); failure_mode_log cites the Phase D.1 logbook entry.
- Extend `_run_cross_method` to a registered N-method dispatch driven by `comparison.methods`; compute all pairwise discrepancies; gate on `gating_pair`; record non-gating pairs in `result.notes`.

### Phase H — run and verdict

- Run C1/C2 v0.3.0; populate result blocks; commit verdict; fill self-referential `commit_hash`; update `docs/validity_envelope.md` + `docs/benchmark_protocol.md` §3; logbook entry; repository tag bump on PASS.

## 5. Acceptance criteria

### 5.1 Plan-surface correction pass (this revision)

PASSes when v0.1.2 is committed and indexed (`plans/README.md` canonical → v0.1.2; v0.1.1 `superseded_by:` appended), with the v0.1.1 §2.3 obsolete sentence explicitly superseded by §2.3 here.

### 5.2 DG-3 failure-asymmetry clearance PASS (downstream, gated by Phases E–H)

DG-3 PASS at the failure-asymmetry-cleared level iff, for each of Cards C1 v0.3.0 and C2 v0.3.0:

1. All four methods (`exact_finite_env`, `qutip_reference`, `heom_reference`, `oqupy_reference`) run to completion on the frozen fixtures.
2. All return reduced density matrices at every frozen-grid point.
3. The **gating pair** `(heom_reference, oqupy_reference)` inter-method discrepancy is ≤ the frozen threshold. The non-gating pairs (including the `exact_finite_env` finite-bath floor) are recorded as auxiliary evidence and do **not** gate.

Frozen thresholds and the gating pair are recorded in the v0.3.0 cards.

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| HEOM and TEMPO share a *hidden* correlated assumption (both consume the same cbg correlator fit) | They differ in the dominant truncation (hierarchy depth vs MPS bond dimension) and in how the correlator enters (exponential expansion vs influence functional). Document both failure-mode banners explicitly; freeze `heom_options` and `oqupy_options` independently. If they agree only because of a shared cbg-fit artefact, the Phase D.1-style correlator audit is the diagnostic. |
| OQuPy 0.5.0 API drift vs the documented surface | Pin `oqupy>=0.5,<0.6` initially; pin the exact `oqupy_options` knob names against the installed version during Phase F; lift the ceiling under explicit review. |
| OQuPy not installable in CI | OQuPy is pure-Python, Apache-2.0, Python `>=3.10` (matches `requires-python`); add to the `[dev]`/runtime deps and confirm CI install before Phase G. |
| TEMPO too slow at the frozen 200-point grid | Allow a coarsened OQuPy sub-grid declared in the v0.3.0 card with interpolation back to the comparison grid; document in failure_mode_log (same mitigation pattern as the HEOM risk in v0.1.1 §6). |
| Schema v0.1.5 `methods` list breaks v0.1.4 readers | Strict backward compatibility: absent `methods` ⇒ v0.1.4 semantics; v0.1.0 pair cards and v0.2.0 triple cards must continue to validate and run unchanged (regression-tested before Phase G). |
| `exact_finite_env` finite-bath floor misread as a DG-3 failure | v0.3.0 cards document it explicitly as a non-gating auxiliary trajectory; `acceptance_criterion.rationale` states the gating pair is HEOM-vs-TEMPO only. |

## 7. Historical context

- v0.1.0 baseline-pair scope: see [`dg-3-work-plan_v0.1.0.md`](dg-3-work-plan_v0.1.0.md).
- v0.1.1 HEOM-selection scope and the (now superseded) §2.3 fallback framing: see [`dg-3-work-plan_v0.1.1.md`](dg-3-work-plan_v0.1.1.md). The v0.1.1 §2.3 sentence "no other structural change is required" is explicitly withdrawn by §2.3 here.
- C1/C2 v0.1.0 (pair) and v0.2.0 (triple) cards remain at HEAD with `status: superseded` / `frozen-awaiting-run` respectively; the v0.2.0 cards are the auditable artifact that exposed the `finite-env-correlator-floor`. Phase D.0/D.1 evidence: logbook [`2026-05-16_dg-3-phase-d-recon-gating-pair-blocked`](../logbook/2026-05-16_dg-3-phase-d-recon-gating-pair-blocked.md).

## 8. Dependencies

- DG-1 PASS (2026-04-30, tag v0.2.0); DG-2 structural sub-claims PASS (2026-05-04).
- DG-3 baseline-pair runner wiring (v0.1.0) + HEOM track (v0.1.1 Phase A/B/C, commits `672db39`, `f30c627`, `0b750b2`).
- `models/pure_dephasing.py`, `models/spin_boson_sigma_x.py` callable API (available).
- QuTiP 5.2.3 in `.venv` (HEOM verified 2026-05-15).
- **New:** `oqupy>=0.5` (Apache-2.0, Python `>=3.10`) — to be added to `pyproject.toml` in the Phase E spec/dependency commit; not yet installed.

## 9. Changelog

- **v0.1.2 (2026-05-16)**: Plan-surface correction superseding v0.1.1. Records the Phase D.0/D.1 reconnaissance outcome (cause `finite-env-correlator-floor`; C1/C2 v0.2.0 gating pair physically unsatisfiable) and **explicitly supersedes the v0.1.1 §2.3 sentence "no other structural change is required"** (§2.3 here). Corrected route: TEMPO via OQuPy promoted to HEOM's **gating partner** (not a replacement); valid gate is HEOM-vs-TEMPO (two faithful continuous-bath solvers, non-overlapping classes). Records the steward Option-A decision: four-method C1/C2 v0.3.0 cards with a general `methods` list (schema v0.1.5, backward compatible), `exact_finite_env`/`qutip_reference` retained as non-gating auxiliary trajectories. Adds `oqupy>=0.5` as a planned dependency (Apache-2.0, Python `>=3.10`; spec/dependency-commit only). New phase structure: A–C landed (HEOM), D.0/D.1 recon (blocked), E (this correction + schema v0.1.5), F (`oqupy_reference`), G (v0.3.0 cards + N-method runner), H (run/verdict). v0.2.0 cards remain frozen and unmutated.
- **v0.1.1 (2026-05-15)**: Tier-2.A third-method selection plan; HEOM via QuTiP 5 in-tree solver selected; TEMPO/pseudomode as fallback; module-boundary discipline; phases A–D. Superseded by v0.1.2 (the §2.3 "no other structural change is required" framing was invalidated by the Phase D.1 finding).
- **v0.1.0 (2026-05-05)**: Initial draft; baseline-pair implementation-ready pass; C1/C2 v0.1.0 frozen.

---

*Plan version: v0.1.2. Drafted 2026-05-16. CC-BY-4.0 (see ../LICENSE-docs).*

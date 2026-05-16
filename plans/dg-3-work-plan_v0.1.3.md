---
plan_id: dg-3-work-plan
version: v0.1.3
date: 2026-05-16
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§5 (Tier 3), 9 (DG-3), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entries 1–7 (COMPATIBLE); Entry 7 (UNDERDETERMINED)
anchor_envelope: docs/validity_envelope.md DG-3 row (v0.2.0 finite-env gate blocked; v0.3.0 OQuPy route blocked by numpy<2; route = HEOM-vs-pseudomode via C1/C2 v0.4.0)
status: draft
supersedes: dg-3-work-plan_v0.1.2.md
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-3 Work Plan — HEOM-vs-Pseudomode Gating Pair (OQuPy route blocked by numpy<2)

## 1. Objective

Pass DG-3 as defined in Sail v0.5 §9:

> *Pass if benchmark comparisons against at least two independent established methods are implemented, with at least one pair drawn from non-overlapping failure-mode families.*

### 1.1 What changed since v0.1.0

v0.1.0 landed the baseline pair (`exact_finite_env` + `qutip_reference`), Phase A–C (validity-envelope DG-3 "FULL RUNNER REACHABILITY" 2026-05-05). v0.1.1 selected and landed **HEOM via QuTiP 5 in-tree `qutip.solver.heom.HEOMSolver`** (Phase A/B/C: `benchmarks/heom_reference.py`, schema v0.1.4, C1/C2 v0.2.0 triple cards).

### 1.2 The v0.2.0 finite-env gate is unsatisfiable (Phase D.0/D.1; unchanged from v0.1.2)

Phase D.0 convergence sweep + D.1 correlator-convention audit (logbook [`2026-05-16_dg-3-phase-d-recon-gating-pair-blocked`](../logbook/2026-05-16_dg-3-phase-d-recon-gating-pair-blocked.md)) proved the C1/C2 v0.2.0 gating pair `(exact_finite_env, heom_reference)` @1e-6 physically unsatisfiable (cause `finite-env-correlator-floor`; `exact_finite_env`'s discrete correlator converges only ≈ O(1/n_modes)). HEOM is internally converged and faithful; cbg is correct; no convention bug. The valid DG-3 Tier-3 gate must be between **two faithful continuous-bath solvers** from non-overlapping failure-mode classes. v0.1.2 set that gate to HEOM-vs-TEMPO(OQuPy) via a four-method C1/C2 v0.3.0 card; schema v0.1.5 + the v0.3.0 `scope-definition` cards landed under Phase E (commit `1b4c21d`).

### 1.3 What v0.1.3 corrects — the OQuPy route is blocked by a hard numpy conflict

Phase F step 1 (refresh/install `oqupy>=0.5,<0.6`) **failed on a hard, mutually-exclusive dependency conflict**, not a transient build issue (logbook [`2026-05-16_dg-3-oqupy-numpy2-dependency-blocked`](../logbook/2026-05-16_dg-3-oqupy-numpy2-dependency-blocked.md)):

- OQuPy **0.5.0 is the latest PyPI release** (versions: 0.5.0, 0.4.0, 0.3.x, 0.2.0) and its wheel metadata **hard-pins `numpy<2.0,>=1.18`**.
- This repo runs **numpy 2.4.4** (scipy 1.17.1, qutip 5.2.3). HEOM — the *other* gating method — is validated on that numpy-2 / qutip-5.2 stack; the 560-test suite runs on numpy 2.x. The `qutip>=5.2` floor remains the in-tree HEOM floor, not an OQuPy compatibility bridge.
- `pip install 'oqupy>=0.5,<0.6'` forces a numpy downgrade (it tried to source-build numpy 1.26.4, which also fails under clang 21). Even a successful build would break HEOM/qutip-5.2 and the suite.

The two intended gating methods **cannot coexist in one environment**. A subprocess/isolated-env bridge is technically possible but would turn DG-3 into an environment-orchestration project and add a new failure surface exactly where a *clean* reference comparison is needed (steward judgement 2026-05-16). **Decision: withdraw the OQuPy route as active; promote pseudomode.** The OQuPy route is retained only as a documented, blocked option (re-openable iff upstream OQuPy ships numpy-2 support). This supersedes the v0.1.2 §2.3 "TEMPO promoted to HEOM's gating partner" framing.

> **⚠ URGENT REMEDIATION (Phase F.0, included in this revision).** The Phase E commit `1b4c21d` declared `oqupy>=0.5,<0.6` as a **hard runtime dependency** in `pyproject.toml`. It is uninstallable on the numpy-2 stack, so `pip install -e .` / `pip install -e ".[dev]"` fails for fresh checkouts at that commit. This plan revision's commit includes the `pyproject.toml` remediation: remove `oqupy` from runtime dependencies (retain OQuPy only as documented prose, not a declared dependency). See §4 Phase F.0.

### 1.4 Active scope under v0.1.3

1. Plan-surface correction (this revision): withdraw OQuPy as active; select pseudomode; record the numpy conflict.
2. **Phase F.0 (included):** `pyproject.toml` — drop the uninstallable `oqupy>=0.5,<0.6` hard dependency; update README dependency prose; short logbook reference. No executable module/runner code.
3. New module `benchmarks/pseudomode_reference.py` (pseudomode via QuTiP `mesolve`; failure-mode class *auxiliary-system / pseudomode-count + Lorentzian-fit-residual*); **no new third-party dependency** (QuTiP is already a dependency; numpy-2-native).
4. C1/C2 **v0.4.0** four-method cards superseding v0.3.0; gating pair `[heom_reference, pseudomode_reference]`; `exact_finite_env` + `qutip_reference` retained as non-gating auxiliary. (Steward 2026-05-16: the gating-method-family change is a structural revision → **v0.4.0**, not a v0.3.1 knob bump.)
5. Runner N-method dispatch (Phase G) + run/verdict (Phase H), unchanged in shape from v0.1.2.

Out of scope: DG-4 Path A; DG-5; MCTDH (§2.5); OQuPy unless upstream numpy-2 support lands (§2.3).

## 2. Third-method family selection

### 2.1 Accessibility audit (updated 2026-05-16 after the Phase F-step-1 OQuPy install attempt)

| Method | Reference package | Status | Failure-mode class | Verdict |
|---|---|---|---|---|
| **HEOM** | QuTiP 5 in-tree `qutip.solver.heom.HEOMSolver` (5.2.3, numpy-2) | Landed (Phase A/B/C); converged, faithful | bath-hierarchy-truncation | **Gating method (retained)** |
| **Pseudomode** | QuTiP `mesolve` + auxiliary Lindblad modes (no new dependency) | Implementable; numpy-2-native | auxiliary-system / pseudomode-count + Lorentzian-fit-residual | **SELECTED — HEOM's gating partner** |
| **TEMPO** | OQuPy 0.5.0 (latest; hard-pins `numpy<2.0`) | **BLOCKED** — incompatible with numpy-2 / qutip-5.2 (HEOM) | process-tensor / MPS-bond-dimension | Withdrawn; re-openable iff upstream numpy-2 support lands |
| **MCTDH** | Heidelberg MCTDH / QuantICs | gated / Fortran | basis-truncation | Not recommended |

### 2.2 HEOM — landed, converged, retained as a gating method

Unchanged from v0.1.2 §2.2. HEOM (*bath-hierarchy-truncation*) at `benchmarks/heom_reference.py`, internally converged at `max_depth=3`, faithful continuous-bath solver. Retained as **one half of the v0.4.0 gating pair**.

### 2.3 TEMPO via OQuPy — withdrawn (blocked by numpy<2), retained as a documented dormant option

**This subsection supersedes v0.1.2 §2.3.** OQuPy 0.5.0 (latest release) hard-pins `numpy<2.0,>=1.18`; this repo's HEOM gating method is validated on the numpy-2 / qutip-5.2 stack. OQuPy would require an in-process downgrade below numpy 2, so the two cannot coexist in this Python environment; an isolated-env/subprocess bridge is rejected as disproportionate (steward judgement — it converts DG-3 into environment orchestration and adds a new failure surface). OQuPy is therefore **not an active gating candidate**. It is retained only as a dormant option: re-openable *iff* a future OQuPy release/commit drops the `numpy<2` pin (the v0.1.2 §2.1 audit noted last `main` commit 2026-03-01; no numpy-2 release exists as of 2026-05-16). No `benchmarks/oqupy_reference.py` will be written under this plan; the `oqupy` dependency declared in Phase E is to be removed (§4 Phase F.0).

### 2.4 Pseudomode — promoted to HEOM's gating partner

**This subsection supersedes v0.1.2 §2.4** (which listed pseudomode as "further fallback only"). Pseudomode is now the **selected gating partner for HEOM**:

- **No environment conflict / no new dependency.** Implemented on QuTiP `mesolve` (already a dependency; numpy-2-native). The blocker that withdrew OQuPy does not apply.
- **Genuinely non-overlapping failure-mode class.** Pseudomode's dominant truncations — number of pseudomodes, auxiliary Lindblad rates, and the rational/Lorentzian fit of the bath correlation/spectral function — are distinct from HEOM's hierarchy-depth truncation (`docs/benchmark_protocol.md` §2 taxonomy: *Pseudomode / chain-mapping → auxiliary-system class*). HEOM-vs-pseudomode is a scientifically valid DG-3 Tier-3 gate of two faithful continuous-bath solvers.
- **cbg-sourced bath input.** The pseudomode construction must fit its Lorentzian/auxiliary parameters to the **cbg** bath correlation function (`cbg.bath_correlations.bath_two_point_thermal`), never to QuTiP spectral-density defaults — same discipline as `benchmarks/heom_reference.py:12-21` and `benchmarks/qutip_reference.py:12-14`. The fit residual is an explicit, documented truncation knob (non-overlap with HEOM's hierarchy depth is what makes the gate meaningful).

### 2.5 MCTDH — explicitly not recommended

Unchanged from v0.1.2 §2.5.

### 2.6 v0.4.0 card architecture (Option A retained; pseudomode replaces oqupy)

Option A (four-method card, general `methods` list, schema v0.1.5 — already landed under Phase E) is retained; only the third-party gating method changes from `oqupy_reference` to `pseudomode_reference`:

```yaml
comparison:
  methods:
    - exact_finite_env
    - qutip_reference
    - heom_reference
    - pseudomode_reference
  method_modules:
    heom_reference: benchmarks.heom_reference
    pseudomode_reference: benchmarks.pseudomode_reference
  gating_pair:
    - heom_reference
    - pseudomode_reference
  heom_options: { ... }           # frozen HEOM knobs (as C1/C2 v0.2.0/v0.3.0)
  pseudomode_options: { ... }     # frozen knobs: n_pseudomodes, Lorentzian-fit
                                  # params/residual target, mesolve atol/rtol
```

Schema v0.1.5 already supports this shape (the `methods`/`method_modules`/options-stem machinery is method-agnostic; `pseudomode_reference` → `pseudomode_options` by the `*_reference → *_options` stem convention). **No schema bump is required** — v0.1.5 is sufficient. The card supersedure is **v0.3.0 → v0.4.0** (steward 2026-05-16: replacing the gating method family is a structural revision, not a v0.3.1 knob change); v0.3.0 (`scope-definition`) is retained at HEAD with `status: superseded` + `superseded_by:` set atomically when v0.4.0 lands (SCHEMA §Supersedure).

## 3. Module-boundary discipline

Unchanged in principle (one module per failure-mode class). The active third module is now:

- `benchmarks/pseudomode_reference.py` — new module, failure-mode class `pseudomode-auxiliary-system`.
  - Imports `qutip` (already a dependency; no new top-level dependency, no numpy conflict).
  - Bath input fitted to `cbg.bath_correlations` (Lorentzian/rational fit of the cbg correlator), **never** QuTiP spectral defaults.
  - Public function `pseudomode_propagate(model_spec, t_grid, solver_options=None) -> np.ndarray`, mirroring `heom_reference.heom_propagate`.
  - Frozen `pseudomode_options` knobs (pinned during the module phase): number of pseudomodes, Lorentzian-fit parameters / fit-residual target, auxiliary Lindblad-rate construction, `mesolve` atol/rtol. Thermal-only handler set first (C1, C2), mirroring `heom_reference` v0.1.0-of-module scope.

`benchmarks/oqupy_reference.py` is **not** created under this plan (§2.3).

## 4. Phases

### Phase A–C — landed under v0.1.1 (HEOM track)

Unchanged: A `672db39`, B `f30c627`, C `0b750b2`.

### Phase D.0/D.1 — reconnaissance (landed; v0.2.0 gate blocked)

Unchanged: commit `d41ff66`; cause `finite-env-correlator-floor`.

### Phase E — schema v0.1.5 + C1/C2 v0.3.0 scope-definition + oqupy dep (landed; partly to be reverted)

Commit `1b4c21d`: schema v0.1.4 → v0.1.5 (N-method `methods` form), C1/C2 v0.3.0 `scope-definition` cards (gating `[heom_reference, oqupy_reference]`), C1/C2 v0.2.0 atomically superseded, **`oqupy>=0.5,<0.6` declared in `pyproject.toml`**. The schema-v0.1.5 / N-method-form / Option-A four-method-card scaffolding **remains valid** (method-agnostic); only the OQuPy-specific dependency and the v0.3.0 gating method are superseded by this revision.

### Phase F.0 — pyproject remediation (included in this revision; no executable code)

- Remove `oqupy>=0.5,<0.6` from `pyproject.toml` runtime dependencies (it is uninstallable on numpy-2 and breaks `pip install -e .` for every fresh checkout at Phase E commit `1b4c21d`).
- Update `README.md` dependency prose: drop OQuPy from the dependency list; note OQuPy/TEMPO is a dormant blocked option (numpy<2), pseudomode is the active partner.
- Logbook reference (the OQuPy-blocker entry committed with this plan revision). Verify `pip install -e ".[dev]"` succeeds and `pytest` is green after the dependency removal.

### Phase F — `benchmarks/pseudomode_reference.py`

- Implement `pseudomode_propagate` + thermal handler set (C1, C2); cbg-fitted bath; failure-mode banner.
- Tests `tests/test_pseudomode_reference.py`: import smoke, shape/dtype, trace/Hermiticity, populations invariant, explicit rejection of unsupported configs (mirrors `tests/test_heom_reference.py`).

### Phase G — C1/C2 v0.4.0 cards + runner N-method dispatch

- Draft `C1/C2 *_v0.4.0.yaml` (Option A; `methods` with `pseudomode_reference`; `gating_pair=[heom_reference, pseudomode_reference]`; `heom_options`/`pseudomode_options` frozen). v0.3.0 cards retained `status: superseded` + `superseded_by:` (atomic, SCHEMA §Supersedure); failure_mode_log cites this plan + the OQuPy-blocker logbook entry. v0.4.0 lands as `scope-definition` until the runner exists, transitioning to `frozen-awaiting-run` per the same discipline as v0.3.0.
- Extend `_run_cross_method` to the registered N-method dispatch driven by `comparison.methods`; add `v0.1.5` to `KNOWN_SCHEMA_VERSIONS`; enforce generalised Rule 19; gate on `gating_pair`; record non-gating pairs in `result.notes`.

### Phase H — run and verdict

Unchanged in shape from v0.1.2 §4 Phase H (run C1/C2 v0.4.0; verdict; surface + logbook updates; tag bump on PASS).

## 5. Acceptance criteria

### 5.1 Plan-surface correction pass (this revision)

PASSes when v0.1.3 is committed and indexed (`plans/README.md` canonical → v0.1.3; v0.1.2 `superseded_by:` appended), with the v0.1.2 §2.3 OQuPy-gating framing explicitly superseded by §§2.3–2.4 here, and the OQuPy numpy<2 blocker recorded in the logbook.

### 5.2 DG-3 failure-asymmetry clearance PASS (downstream, gated by Phases F.0–H)

For each of Cards C1 v0.4.0 and C2 v0.4.0: all four methods run to completion; the **gating pair** `(heom_reference, pseudomode_reference)` inter-method discrepancy is ≤ the frozen threshold; non-gating pairs (incl. the `exact_finite_env` finite-bath floor) are recorded but do not gate. Frozen thresholds and the gating pair are recorded in the v0.4.0 cards.

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **(Realised) OQuPy `numpy<2` ⟂ qutip-5.2 numpy-2 (HEOM).** | Route withdrawn; pseudomode selected (§2.3/§2.4). OQuPy retained as a dormant blocked option only. |
| **(Realised) `pyproject.toml` declares an uninstallable `oqupy` hard dep at Phase E commit `1b4c21d`.** | Phase F.0 in this revision removes it; verify `pip install -e ".[dev]"` + `pytest`. |
| HEOM and pseudomode share a hidden correlated assumption (both consume the cbg correlator) | They differ in dominant truncation (hierarchy depth vs pseudomode count + Lorentzian-fit residual) and in how the correlator enters (exponential expansion vs rational-pole auxiliary modes). Freeze `heom_options` and `pseudomode_options` independently; a Phase D.1-style correlator/fit audit is the diagnostic if they agree only by a shared cbg-fit artefact. |
| Pseudomode Lorentzian fit of an ohmic cbg correlator is poor (ohmic ≠ sum-of-Lorentzians) | Treat fit residual as an explicit frozen knob; document in the card; if the residual floor prevents a 1e-6 gate, that routes to a steward threshold decision via v0.4.1 supersedure (not post-hoc loosening; Sail §4) — same pattern as the v0.3.0 threshold open-question. |
| Schema/runner: `methods` form not yet enforced/dispatched | Already scoped (Phase G): add `v0.1.5` to `KNOWN_SCHEMA_VERSIONS`, enforce generalised Rule 19, N-method dispatch. v0.4.0 stays `scope-definition` until then. |
| `exact_finite_env` finite-bath floor misread as DG-3 failure | v0.4.0 cards document it as non-gating auxiliary; `acceptance_criterion.rationale` states the gate is HEOM-vs-pseudomode only. |

## 7. Historical context

- v0.1.0 baseline pair; v0.1.1 HEOM selection; v0.1.2 HEOM-vs-TEMPO route (the §2.3 OQuPy-gating framing is withdrawn by §§2.3–2.4 here). See [`dg-3-work-plan_v0.1.0.md`](dg-3-work-plan_v0.1.0.md), [`v0.1.1`](dg-3-work-plan_v0.1.1.md), [`v0.1.2`](dg-3-work-plan_v0.1.2.md).
- C1/C2 v0.1.0 (pair), v0.2.0 (triple, `superseded`), v0.3.0 (`scope-definition`, gating OQuPy) remain at HEAD for audit. v0.3.0 will be superseded by v0.4.0 (pseudomode) under Phase G.
- Evidence: Phase D.0/D.1 logbook [`2026-05-16_dg-3-phase-d-recon-gating-pair-blocked`](../logbook/2026-05-16_dg-3-phase-d-recon-gating-pair-blocked.md); OQuPy blocker logbook [`2026-05-16_dg-3-oqupy-numpy2-dependency-blocked`](../logbook/2026-05-16_dg-3-oqupy-numpy2-dependency-blocked.md).

## 8. Dependencies

- DG-1 PASS (tag v0.2.0); DG-2 structural sub-claims PASS.
- HEOM track landed (v0.1.1 A/B/C, commits `672db39`, `f30c627`, `0b750b2`); schema v0.1.5 + v0.3.0 scaffolding landed (Phase E `1b4c21d`).
- QuTiP 5.2.3 in `.venv` (numpy 2.4.4) — covers **both** HEOM and the planned pseudomode module (QuTiP `mesolve`). **No new third-party dependency** is introduced by the pseudomode route.
- **Removed:** `oqupy>=0.5,<0.6` (declared under Phase E; uninstallable on numpy-2; dropped in Phase F.0 of this revision).

## 9. Changelog

- **v0.1.3 (2026-05-16)**: Plan-surface correction superseding v0.1.2. Phase F step 1 found OQuPy 0.5.0 (latest) hard-pins `numpy<2.0`, mutually exclusive with this repo's validated numpy-2 / qutip-5.2 HEOM stack (logbook `2026-05-16_dg-3-oqupy-numpy2-dependency-blocked`). **Withdraws the OQuPy/TEMPO gating route** (retained only as a dormant option, re-openable iff upstream numpy-2 support lands) and **promotes pseudomode** (QuTiP `mesolve`; no new dependency; numpy-2-native; non-overlapping *auxiliary-system* class) as HEOM's gating partner. Includes **Phase F.0**: removes the now-uninstallable `oqupy>=0.5,<0.6` hard dependency committed under Phase E (`1b4c21d`) and updates README dependency prose. Card supersedure retargeted to **C1/C2 v0.4.0** (steward: gating-method-family change is structural, not a v0.3.1 knob bump); schema v0.1.5 / Option-A four-method scaffolding is method-agnostic and **retained (no schema bump)**. Phase structure: A–E landed, F.0 included, F (`pseudomode_reference`), G (v0.4.0 cards + N-method runner), H (verdict).
- **v0.1.2 (2026-05-16)**: HEOM-vs-TEMPO route; superseded the v0.1.1 §2.3 framing after Phase D.0/D.1. Superseded by v0.1.3 (OQuPy blocked by numpy<2).
- **v0.1.1 (2026-05-15)**: Tier-2.A HEOM selection. Superseded by v0.1.2.
- **v0.1.0 (2026-05-05)**: Initial draft; baseline-pair implementation-ready pass.

---

*Plan version: v0.1.3. Drafted 2026-05-16. CC-BY-4.0 (see ../LICENSE-docs).*

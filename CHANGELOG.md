# Changelog

All notable changes to `oqs-cbg-pipeline` are recorded here. The authoritative
record of scientific status and Decision Gate verdicts is
[`docs/validity_envelope.md`](docs/validity_envelope.md); per-event detail and
self-referential commit hashes live in [`logbook/`](logbook/). This file gives
a flat, user-facing summary of the same information.

The project follows [Semantic Versioning](https://semver.org/) for its public
Python API and tracks Decision Gate transitions in the validity envelope.
Anchor: Sail v0.5; Ledger CL-2026-005 v0.4.

**On version semantics.** Bracketed section headers below track *git tags* that
anchor Decision Gate verdict immutability — they are not Python package
releases. Package metadata in [`pyproject.toml`](pyproject.toml) and
[`CITATION.cff`](CITATION.cff) remains at `0.3.0.dev0` until a deliberate
package release is made. The DG-anchoring tags are `v0.2.0` (DG-1 PASS) and
`v0.5.0` (DG-4 v0.1.1 PASS verdict, subsequently superseded on review).

## [Unreleased]

### Added
- DG-4 PASS at D1 v0.1.2 (2026-05-06; verdict commit `6f88787`) via
  picture-fixed Path B numerical L_4 extraction. All 20 frozen
  `coupling_strength` sweep points classify as `convergence_failure` under
  the parity-aware `r_4(α²) = α² · ⟨‖L_4^dis‖⟩_t / ⟨‖L_2^dis‖⟩_t` metric,
  with stability across all four reproducibility perturbations
  (`upper_cutoff_factor ∈ {20, 40}`, `omega_c ∈ {9, 11}`); maximum baseline
  `r_4 ≈ 47.42` at α² = 1.0; minimum perturbed coefficient ratio `≈ 41.47`. See
  [`logbook/2026-05-06_dg-4-pass-path-b-v012.md`](logbook/2026-05-06_dg-4-pass-path-b-v012.md).
- `benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.2.yaml`
  superseding v0.1.1; structurally identical (same model, metric, sweep,
  perturbation set) but consumes the v0.1.1 supersedure repair commits.
- `benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json`
  audit-complete: per-α + per-α-per-perturbation `r_4` plus per-perturbation
  Path B fit residuals + dissipator-norm coefficients persisted.
- Three v0.1.1 supersedure repair commits consumed by v0.1.2:
  - `d67b453`: `benchmarks.numerical_tcl_extraction.transform_to_interaction_picture`
    + `adjoint_unitary_superoperator` helpers, `path_b_dissipator_norm_coefficients`
    now requires `system_hamiltonian` and applies the IP transform before
    order-4 extraction. Six new regression tests pin picture invariance and
    that direct-Schrödinger extraction disagrees with picture-aware extraction
    by >10% under `H_S ≠ 0`.
  - `a908cd6`: `reporting.benchmark_card._path_b_evaluate` threads
    `numerical.quadrature.upper_cutoff_factor` into the finite-env builder
    as `omega_max_factor`. New regression test
    `test_dg4_path_b_upper_cutoff_factor_is_operational` pins that the
    perturbation now produces a non-trivial coefficient delta.
  - `5441467`: `CardResult.dg4_sweep_data` field, `_build_dg4_sweep_data`
    helper, and `write_dg4_result_json(card, result, output_path)` writer
    persist the audit-complete sweep table to disk. Three new tests pin
    the audit shape, round-trip through the writer, and refusal on non-DG-4
    results.

- Review-resolution sweep (2026-05-08 → 2026-05-11) per
  [`reviews/work-package_review-resolution_v0.1.0.md`](reviews/work-package_review-resolution_v0.1.0.md),
  consolidating 35+ issues from three review rounds (Kimi, Gemini,
  Claude, Codex, anonymous structural). All HIGH (H1–H4), MEDIUM
  (M0–M7), and structural/LOW (S1–S14 / L1–L7) issues closed across
  workstreams WS-A through WS-Lc plus follow-up patches WS-A2 / WS-D2 /
  WS-E2 / WS-H2. Notable Tier-1 landings:
  - WS-I L5 (`9f686ba`): immutable summary JSONs; `benchmarks/results/README.md`
    index file added (Path L5-b chosen).
  - WS-Lb S6 (`509c3c1`): `# SPDX-License-Identifier: MIT` headers on all
    `*.py` files (41 touched).
  - WS-Lb S8 (`a78b203` + `cf7d66c`): Python 3.13 in CI matrix and
    `pyproject.toml` classifiers (two-step: CI row first, classifier after
    green).
  - WS-Lb S10 (`733e3ff`): callable refusal stubs in `models.fano_anderson`
    and `models.jaynes_cummings` (Path S10-a); `ScopeDefinitionNotRunnableError`
    raised on call, not import.
  - WS-Lb S13 (`80971e0`): `.github/ISSUE_TEMPLATE/bug_report.md`,
    `.github/ISSUE_TEMPLATE/dg-status-change.md`,
    `.github/PULL_REQUEST_TEMPLATE.md` added with cards-first /
    validity-envelope / DG-cause-label discipline encoded.
- DG-4 work plan v0.1.5 (Path A analytic L_4 cross-validation, post-
  verdict Tier-2.B) frozen via Council-3 ADM-EC deliberation 2026-05-11
  (`e3ac79c`); six edits merged, no vetoes, no rc-read issues. See
  [`plans/dg-4-work-plan_v0.1.5.md`](plans/dg-4-work-plan_v0.1.5.md) and
  [`logbook/2026-05-11_dg-4-work-plan-v015-frozen-via-council-3.md`](logbook/2026-05-11_dg-4-work-plan-v015-frozen-via-council-3.md).
- DG-4 v0.1.5 **Phase A** (`24c771e`): Companion Sec. IV L_4 transcription
  v0.1.1 released at
  [`transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md`](transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md);
  two post-release docs-cleanup passes (`17c7ace`, `3c43eac`) addressed
  eight findings.
- DG-4 v0.1.5 **Phase B** (`ae20806`, `becccf9`, errata `0d900ec`):
  small-grid Companion-identity verification card v0.1.1 and
  `cbg.tcl_recursion._D_bar_4_companion` + `_D_companion_raw_n{2,4}`
  helpers; 22 small-grid tests passing
  ([`tests/test_n4_small_grid_verification.py`](tests/test_n4_small_grid_verification.py)).
  Companion D̄ at n=4 differs from standard set-partition cumulants —
  the B.1 cumulant path would silently zero L_4 and is rejected as a
  falsification record.
- DG-4 v0.1.5 **Phase C** (`49b92d5`, `6732924`, `e414448`, `3e50e94`,
  `0d900ec`): physics-oracles card v0.1.3 (errata) and
  `cbg.tcl_recursion._L_4_thermal_at_time_apply` (+ `_no_guard`
  diagnostic); 19 physics-oracle tests passing
  ([`tests/test_n4_physics_oracles.py`](tests/test_n4_physics_oracles.py)).
  σ_z zero oracle is gated via the `[H_S, A] = 0` Feynman–Vernon guard
  (Part A) with a non-gating O(h¹) convergence diagnostic (Part B);
  cube → outer-simplex domain fix re-pinned the Part B reference table.
- DG-4 v0.1.5 **Phase D** (`2959925`, `f599751`, `6cb0ea6`): public-route
  card v0.1.0 and `cbg.tcl_recursion.L_n_thermal_at_time(n=4)` exposed
  for the supported thermal Gaussian scope, propagating through
  `L_n_superoperator_thermal_at_time`, `L_n_dissipator_thermal_at_time`,
  `L_n_dissipator_norm_thermal_on_grid`, and `K_total_thermal_on_grid`
  for `N_card > 4`. Four deferral tests flipped to callable; six new
  unsupported-scope + guard-exact-zero gates added; 47/47 regression
  tests passing ([`tests/test_tcl_recursion.py`](tests/test_tcl_recursion.py)).
  Stale-deferral references swept across docs/.
- DG-4 v0.1.5 **Phase E** (`749bd85`): Path A vs Path B cross-validation
  pilot frozen as `frozen-unclassified-pilot` — a fourth state outside
  the work plan's three-state acceptance set. An analytical convention
  audit confirmed no normalization/definition mismatch between paths;
  the remaining magnitude disagreement at N≤41 (Path A: 1.07 → 1.24 →
  14.15; Path B: 47.42) is dual-side numerical resolution (Path A
  quadrature not converged at O(h¹) on N≤41; Path B finite-env
  extraction floor from the 2026-05-06 σ_z pilot). No classification
  verdict issued; D1 v0.1.2 PASS unchanged; Phase F blocked. Deferred
  tracks 5.A (finer-grid Path A: N=81 ≈ 50 min, N=161 ≈ 25–30 h due to
  O(N⁵) L_4 assembly), 5.B (higher-order quadrature), and 5.C (Path B
  floor audit) recorded for future steward selection. See
  [`transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-pilot-card_v0.1.0.md`](transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-pilot-card_v0.1.0.md)
  and
  [`logbook/2026-05-13_dg-4-v015-phases-a-e-completion-plus-phase-e-pilot.md`](logbook/2026-05-13_dg-4-v015-phases-a-e-completion-plus-phase-e-pilot.md).

### Changed
- DG-4 row in `docs/validity_envelope.md`, `docs/benchmark_protocol.md` §4,
  `README.md`, `index.html`, `docs-site/`, `examples/README.md`,
  `docs/endorsement_marker.md`, `project_dg2_blockers.md`, and
  `examples/dg4_walkthrough.ipynb` rolled forward from "v0.1.1 verdict
  superseded; v0.1.2 supersedure pending" to "DG-4 PASS at D1 v0.1.2".
- DG-2 row in `docs/validity_envelope.md` carries a 2026-05-13
  implementation-stage note that the reviewed thermal-Gaussian n=4 public
  route (Phase D) reduces the old "n=4 not implemented" gap but does
  **not** by itself authorise DG-2 Entry 2 closure: the scope is thermal
  Gaussian only, non-thermal/displaced n=4 remains out of scope, and no
  DG-2 card has yet converted this public route into an Entry-2-wide
  K_2-K_4 recursion verdict.
- Landing page and status surfaces refreshed (`2bf830d`) to reflect the
  post-verdict DG-4 Path A artefact chain.
- DG-4 Phase E Track 5.C **frozen card v0.1.0** (`bbdc237`): scopes the
  Path B finite-env floor audit at the D1 σ_x fixture; one-axis-at-a-time
  topology anchored at `(n_bath_modes = 4, n_levels_per_mode = 3,
  omega_max_factor = 30)`; cause-label ladder `truncation-converged` /
  `borderline` / `floor-dominated`; routing matrix; §5.3 Hilbert-witness
  acceptance criterion; §6 R1 preflight estimator + hard process
  timeout. Replaces the v0.1.0-draft after three steward freeze blockers
  resolved (production cutoff anchor `30` added to omega sweep,
  single-Richardson-fit-per-truncation language, one-axis-at-a-time
  topology + Hilbert-witness requirement made explicit).
- DG-4 Phase E Track 5.C **audit driver + smoke gate** (`ced5276`):
  `benchmarks/path_b_floor_audit.py` and
  `tests/test_path_b_floor_audit.py` (7 tests; ~1 s) — `TruncationConfig`
  / `FloorAuditPoint` dataclasses, `predict_wall_time_seconds()`
  preflight estimator, `iter_audit_grid()`, `evaluate_point()`,
  `run_audit()` driver, JSON writer, `_compute_summary()` cause-label
  eligibility helper, CLI entry point. Card §5.1 smoke test runs the
  `(4, 3, omega_max_factor=10)` corner end-to-end on a reduced grid.
- DG-4 Phase E Track 5.C **production run + cause label** (`b4bda20`):
  hard process timeout wrapper (`evaluate_point_with_timeout`) via
  `multiprocessing.Process` (`spawn` + grace-then-kill); preflight
  exponent recalibrated to `PREFLIGHT_D_JOINT_EXPONENT = 2.2` (the
  initial cubic guess was 2.5–3× pessimistic because
  `exact_finite_env.propagate` is matrix-vector per RK step, not
  matrix-matrix); 9 of 10 grid configs evaluated (one preflight-skipped
  at `d_joint = 13122`); three Hilbert witnesses `(4, 4)`, `(4, 5)`,
  `(6, 3)`; **max drift 24.16%** at `(6, 3)` Hilbert witness. Cause
  label: **`floor-dominated`**. Path B at the D1 production fixture is
  not a stable cross-validation reference: the three truncation knobs
  (`omega_max_factor`, `n_levels_per_mode`, `n_bath_modes`) drive
  `coefficient_ratio` in mutually inconsistent directions (omega and
  Fock both down; mode count up by 24%). Per 5.C card §4.4 routing,
  Phase E now requires Path A as single-sided ground truth, DG-3
  Tier-2.A (HEOM / TEMPO third method) as Path B's replacement, or a
  permanent `unclassified-pilot` state. **D1 v0.1.2 PASS verdict is
  unchanged.** Result JSON
  [`benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json`](benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json);
  logbook entry
  [`2026-05-13_dg-4-phase-e-5c-path-b-floor-audit-floor-dominated.md`](logbook/2026-05-13_dg-4-phase-e-5c-path-b-floor-audit-floor-dominated.md).

## [v0.5.0 git tag] — 2026-05-06

DG-4 v0.1.1 PASS verdict via Path B numerical L_4 extraction. **Superseded
on review** the same day for two HIGH-severity defects in the Path B
extraction (picture / `Λ_0⁻¹` similarity error, and trivial PASS predicate
for two of four perturbations). See
[`logbook/2026-05-06_dg-4-pass-path-b.md`](logbook/2026-05-06_dg-4-pass-path-b.md)
(original verdict) and
[`logbook/2026-05-06_dg-4-pass-path-b-superseded.md`](logbook/2026-05-06_dg-4-pass-path-b-superseded.md)
(supersedure citation). The repaired DG-4 PASS landed at D1 v0.1.2 the
same day (verdict commit `6f88787`); see Unreleased section above. The
`v0.5.0` git tag is left as immutable history of the v0.1.1 commit.

### Added
- DG-4 failure-envelope card
  [`D1 v0.1.1`](benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.1.yaml):
  spin-boson σ_x thermal model with the parity-aware even-order ratio
  `r_4 = ⟨‖L_4^dis‖⟩_t / ⟨‖L_2^dis‖⟩_t`. Supersedes D1 v0.1.0 (pure-dephasing
  thermal, which is TCL-2 exact and cannot expose order-4 convergence
  failure).
- `benchmarks/numerical_tcl_extraction.py` — Path B numerical Richardson
  extraction of TCL generator coefficients via polynomial fit
  `Λ_t(α) = Λ_0 + α² Λ_2 + α⁴ Λ_4 + O(α⁶)` against finite-environment
  tomography (`benchmarks.exact_finite_env`). Provides
  `path_b_dissipator_norm_coefficients` consumed by the DG-4 sweep runner.
- `reporting.benchmark_card._run_dg4_sweep` — Phase C sweep runner that
  consumes the Path B numerical L_4 source, evaluates `r_4` on the frozen
  `coupling_strength` sweep, applies the reproducibility perturbations
  (`upper_cutoff_factor`, `omega_c`), interpolates `α_crit` if a transition
  exists in range, and emits the cause-labelled DG-4 verdict.
- `cbg.tcl_recursion`: `L_n_dissipator_thermal_at_time` and
  `L_n_dissipator_norm_thermal_on_grid` for `n ∈ {0, 1, 2, 3}` (Phase B.3
  parity-aware norm primitives). The `n = 3` case returns the zero
  superoperator by Gaussian-Wick parity. The analytic `n = 4` case remains
  intentionally deferred behind a structured Path A / B / C wall.
- DG-4 status row in the validity envelope and benchmark protocol §4.
- Logbook entry
  [`2026-05-06_dg-4-pass-path-b.md`](logbook/2026-05-06_dg-4-pass-path-b.md).

### Changed
- Repository status badge and Decision Gate matrix updated across `README.md`,
  `index.html`, and `docs-site/`.
- `docs/benchmark_protocol.md` §4 updated to record D1 v0.1.1 PASS with the
  Path B numerical caveat.

### Notes
- Path B carries a documented finite-environment extraction floor (~few × 1e-2
  at default truncation) from the 2026-05-06 σ_z thermal zero-oracle pilot.
  Analytic Path A (Companion Sec. IV closed form for L_4) remains preferred
  for machine-precision evaluation and pending.
- Reproducibility caveat: `omega_c` perturbations are operational under
  model-spec mutation; `upper_cutoff_factor` perturbations are runner-threaded
  but not consumed by the current `exact_finite_env` Path B extraction.

## [v0.3.0.dev0 / v0.2.0 git tag] — 2026-05-04

DG-1 PASS (2026-04-30, tag `v0.2.0`) and DG-2 structural sub-claims PASS
(2026-05-04) under the Council-cleared displacement-profile registry. The
literal fourth-order K_2-K_4 recursion remains pending. See
[`docs/validity_envelope.md`](docs/validity_envelope.md) for the full
authorisation table.

### Changed
- `cbg.__version__` now reads from package metadata (`importlib.metadata`),
  removing the prior hardcoded literal so it cannot drift from `pyproject.toml`.
- The import-time protective-docs check skips when no `docs/` tree is adjacent
  to the package (i.e., the package is pip-installed without a repo checkout),
  removing the `RuntimeWarning` for downstream reusers. CI still enforces the
  same check strictly on the repository.

### Added
- `examples/` directory with two runnable Jupyter notebooks demonstrating the
  passed Decision Gate verdicts end-to-end:
  `dg1_walkthrough.ipynb` (Cards A1, A3) and `dg2_structural.ipynb`
  (Cards B3, B4 under the `delta-omega_S` displacement profile).
  Both execute cleanly under `nbclient`; numerics agree with the frozen card
  results at machine precision.
- `[tool.black]`, `[tool.ruff]`, and `[tool.mypy]` configuration in
  `pyproject.toml` (declared dev tools now have shared defaults; not enforced
  in CI).
- `Installation` and `Quickstart` sections in `README.md`.
- This `CHANGELOG.md`.

## [v0.2.0 git tag] — 2026-05-04

Tag bumped at the DG-2 structural-sub-claims PASS commit (DG-1 PASS verdict
also anchored under this tag). See
[`logbook/2026-05-04_dg-2-pass-envelope.md`](logbook/2026-05-04_dg-2-pass-envelope.md).

## [v0.1.0 git tag] — 2026-04-30

Tagged at DG-1 PASS. See
[`logbook/2026-04-30_dg-1-pass.md`](logbook/2026-04-30_dg-1-pass.md).

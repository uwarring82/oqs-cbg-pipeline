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

### Changed
- DG-4 row in `docs/validity_envelope.md`, `docs/benchmark_protocol.md` §4,
  `README.md`, `index.html`, `docs-site/`, `examples/README.md`,
  `docs/endorsement_marker.md`, `project_dg2_blockers.md`, and
  `examples/dg4_walkthrough.ipynb` rolled forward from "v0.1.1 verdict
  superseded; v0.1.2 supersedure pending" to "DG-4 PASS at D1 v0.1.2".

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

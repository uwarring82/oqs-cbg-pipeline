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

### Changed
- DG-4 v0.1.1 PASS verdict recorded under tag `v0.5.0` was **superseded on
  review** on 2026-05-06 the same day. Two HIGH-severity defects: (i) Path B
  applies the interaction-picture order-4 formula `L_2 = Λ̇_2`,
  `L_4 = Λ̇_4 - L_2 Λ_2` to raw Schrödinger-picture maps without the
  `Λ_0⁻¹` similarity and the `L_0 Λ_n Λ_0⁻¹` correction, which is wrong
  whenever `H_S ≠ 0`; (ii) the runner's "stable under all four perturbations"
  PASS predicate is trivially satisfied for `upper_cutoff_factor ∈ {20, 40}`
  because the current Path B path does not consume that knob. MEDIUM audit
  gap: per-α + per-perturbation `r_4` not persisted in the result JSON.
  See [`logbook/2026-05-06_dg-4-pass-path-b-superseded.md`](logbook/2026-05-06_dg-4-pass-path-b-superseded.md).
- `docs/validity_envelope.md`, `docs/benchmark_protocol.md` §4, `README.md`,
  `index.html`, `docs-site/`, `examples/README.md`, `docs/endorsement_marker.md`,
  `project_dg2_blockers.md`, and `examples/dg4_walkthrough.ipynb` rolled back
  to "DG-4 v0.1.1 PASS verdict superseded; v0.1.2 supersedure pending Path B
  picture repair + operational `omega_max_factor` + audit-complete result JSON".
- The `v0.5.0` git tag is left as immutable history (the verdict it anchored
  remains in the repository on the record); only the verdict's authorisation
  is downgraded.

### Pending (D1 v0.1.2 supersedure)
- Repair Path B order-4 extraction: implement the general
  `L_n = Λ̇_n Λ_0⁻¹ - L_0 Λ_n Λ_0⁻¹ + …` formula or transform raw maps to
  the interaction picture before extraction. Add a regression test on a
  fixture with `H_S ≠ 0` checking dissipator-norm picture invariance.
- Thread `upper_cutoff_factor` into `exact_finite_env`'s `omega_max_factor`
  so the perturbation is operational under Path B.
- Persist per-α baseline and per-α-per-perturbation `r_4` plus
  per-perturbation Path B fit residuals in the result JSON.
- Freeze D1 v0.1.2 superseding v0.1.1 and re-run.

## [v0.5.0 git tag] — 2026-05-06

DG-4 v0.1.1 PASS verdict via Path B numerical L_4 extraction (subsequently
**superseded on review** the same day; see Unreleased section above and
[`logbook/2026-05-06_dg-4-pass-path-b-superseded.md`](logbook/2026-05-06_dg-4-pass-path-b-superseded.md)).
The original verdict log is at
[`logbook/2026-05-06_dg-4-pass-path-b.md`](logbook/2026-05-06_dg-4-pass-path-b.md).

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

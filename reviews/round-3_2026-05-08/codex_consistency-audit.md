# Repository Consistency Audit - 2026-05-08

Reviewer: Codex
Repository: `oqs-cbg-pipeline`
Branch / HEAD reviewed: `main` / `c1f3806`
Scope: repository-wide consistency review across code, tests, CI config, docs, benchmark cards/results, rendered site assets, metadata, examples, and review notes.

This is a flag-only review. No code, docs, card, or metadata fixes were made. This file is the only artifact added by this audit.

Two untracked review notes were already present when this report was created and were left untouched:

- `reviews/consistency_review_2026-05-08.md`
- `reviews/repo_inconsistencies_flagged.md`

## Verification Snapshot

- `pytest`: `471 passed, 2 warnings in 55.33s`.
- `ruff`: fails on the CI scope with 8 diagnostics.
- `black --check`: fails; 8 tracked Python files would be reformatted.
- `mypy cbg/ models/ numerical/ benchmarks/ reporting/`: fails with 6 errors in 3 files.
- `sphinx-build -b html -E` into a temp directory: succeeds with 15 warnings / docutils issues.
- `jupyter nbconvert --to notebook --execute` on the examples: fails on `examples/dg1_walkthrough.ipynb` with `ModuleNotFoundError: No module named 'cbg'`.
- Tracked JSON/YAML syntax parse: OK.
- Rendered worked-example HTML files exist at `api/examples/dg1_walkthrough.html` through `api/examples/dg4_walkthrough.html`.

## Findings

### HIGH - CI quality gates are configured but currently fail

`.github/workflows/tests.yml:48-70` runs Black, Ruff, and MyPy in the `code-quality` job. Local runs with the same tool family fail, while pytest passes. That means the test suite is green but the repo is not CI-clean.

Observed failures:

- Ruff: 8 diagnostics, including import ordering in `benchmarks/exact_finite_env.py` and `tests/test_exact_finite_env.py`, stale Python-version guards in `cbg/__init__.py` and `conftest.py`, E402 imports in `cbg/__init__.py`, an F541 f-string in `reporting/benchmark_card.py:1815`, and a UP032 string-formatting issue in `tests/test_benchmark_card.py:1089`.
- Black: 8 files would be reformatted: `docs-site/conf.py`, `benchmarks/qutip_reference.py`, `benchmarks/exact_finite_env.py`, `benchmarks/numerical_tcl_extraction.py`, `tests/test_numerical_tcl_extraction.py`, `tests/test_exact_finite_env.py`, `tests/test_benchmark_card.py`, and `reporting/benchmark_card.py`.
- MyPy CI scope: 6 errors in `benchmarks/qutip_reference.py`, `benchmarks/numerical_tcl_extraction.py`, and `reporting/benchmark_card.py`.

Related inconsistency: `CONTRIBUTING.md` tells contributors to run the quality tools, and CI enforces them, but the current tree does not satisfy them.

### HIGH - DG-4 live status is v0.1.2, but several surfaces still point at v0.1.1

The apparent authoritative state is `docs/validity_envelope.md:22` and `docs/benchmark_protocol.md:98-103`: DG-4 is live at D1 v0.1.2, with v0.1.1 superseded after review.

Stale or contradictory surfaces:

- `benchmarks/results/DG-4_summary.json:12-24` still summarizes D1 v0.1.1, points evidence to `D1_failure-envelope-convergence_v0.1.1_result.json`, and says `upper_cutoff_factor` perturbations are not operational.
- `benchmarks/benchmark_cards/README.md:45` points D1 to `D1_failure-envelope-convergence_v0.1.1.yaml`.
- `benchmarks/benchmark_cards/README.md:60` calls D1 v0.1.1 the active DG-4 card and says `upper_cutoff_factor` is threaded but not consumed.
- `benchmarks/benchmark_cards/README.md:72` records supersedure from v0.1.0 to v0.1.1, but not from v0.1.1 to v0.1.2.
- `plans/README.md:55`, `plans/README.md:61`, and `plans/README.md:78` still describe the DG-4 verdict as D1 v0.1.1.
- `reporting/benchmark_card.py:150-159` says the DG-4 sweep runner is not yet implemented and names D1 v0.1.1, even though `_run_dg4_sweep` exists and v0.1.2 is the live verdict.
- `reporting/benchmark_card.py:1447`, `benchmarks/numerical_tcl_extraction.py:382`, and several `cbg/tcl_recursion.py` comments/docstrings still call the fixture or metric D1 v0.1.1.

This is not just prose drift: the summary JSON is a machine-readable result index, so downstream readers could resolve the wrong card/result pair.

### HIGH - FAIR and citation metadata are stale relative to DG-4

The machine-readable metadata still describes a pre-DG-4 state:

- `CITATION.cff:7-13` mentions DG-1 and DG-2, but no DG-4 PASS.
- `CITATION.cff:21` has `date-released: 2026-05-04`.
- `codemeta.json:5-7` has the same stale description/date.
- `.zenodo.json:3` omits DG-4.
- `.zenodo.json:40` says "DG-4 failure-envelope work" remains pending.

This conflicts with `docs/validity_envelope.md:22` and the landing page, which both state DG-4 PASS at D1 v0.1.2 on 2026-05-06.

### MEDIUM - DG-4 metric text alternates between scaled and unscaled definitions

The runner computes the scaled quantity:

- `reporting/benchmark_card.py:1421`: `r_4(alpha**2) = alpha**2 * (<||L_4^dis||>_t / <||L_2^dis||>_t)`.
- `reporting/benchmark_card.py:1747`: `_scaled_ratio` uses the same definition.
- `benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.2.yaml:277` says `r_4 = coupling_strength * coefficient_ratio`.
- `examples/README.md:12` also includes the `alpha^2` factor.

Other public prose omits the scaling factor and defines `r_4` as only the coefficient ratio:

- `docs/validity_envelope.md:22`
- `docs/benchmark_protocol.md:98`
- `README.md:116`
- `docs-site/index.md:34`
- `index.html:152` and `index.html:186`
- `benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.2.yaml:110`, `:155`, `:186`

The current full-run headline numbers remain above threshold either way, but the name `r_4` is being used for two different quantities. That is a real interpretive risk because the frozen sweep variable is `coupling_strength`.

### MEDIUM - Worked-example surfaces are not all synchronized

The landing page and Sphinx intro now show four worked examples, but older surfaces still describe two or blur PASS versus non-PASS examples:

- `README.md:83-86` says "Two runnable Jupyter notebooks" and lists only DG-1 and DG-2.
- `examples/README.md:28-29` gives noninteractive execution commands only for DG-1 and DG-2, while `docs-site/examples.md:71-74` includes all four notebooks.
- `examples/README.md:4` says each notebook anchors a passed Decision Gate, but `examples/README.md:11` correctly says DG-3 is runner-complete and does not have a PASS.
- `examples/README.md:34` calls the notebooks "demonstrations of passed Decision Gate verdicts"; the landing page uses the more accurate "passed (or partially passed)" phrasing at `index.html:205`.
- `README.md:85`, `README.md:86`, `index.html:207`, and `index.html:208` list cards A1/A3 and B3/B4, while the authoritative DG rows use A1/A3/A4 and B3/B4-conv-registry/B5-conv-registry where appropriate.

The rendered Sphinx worked-example index itself does link the four notebook HTML pages correctly:

- `api/examples.html:383` -> `examples/dg1_walkthrough.html`
- `api/examples.html:389` -> `examples/dg2_structural.html`
- `api/examples.html:396` -> `examples/dg3_cross_method.html`
- `api/examples.html:404` -> `examples/dg4_walkthrough.html`

### MEDIUM - DG-4 example prose mixes reduced-fixture behavior with full frozen-run behavior

The authoritative full frozen run says all 20 swept points fail and no `alpha_crit` is bracketed:

- `docs/benchmark_protocol.md:103`
- `docs/validity_envelope.md:22`

Some example summaries describe threshold crossing only in the "upper sweep range":

- `examples/README.md:12`
- `docs-site/examples.md:52-53`
- rendered `api/examples.html:407-408`

`examples/dg4_walkthrough.ipynb:15` explains that the notebook uses a reduced fixture whose upper half fails, while the full frozen run has all 20 points fail. The shorter index prose does not carry that distinction, so it can read as contradicting the live D1 v0.1.2 verdict.

Also, `examples/dg4_walkthrough.ipynb:90` says "Card D1 v0.1.1 freezes...", but the code loads `D1_failure-envelope-convergence_v0.1.2.yaml` at line 122 and the output at line 110 prints `card_id = D1 v0.1.2`.

### MEDIUM - Notebook execution instructions are not reproducible in this checkout

The docs recommend populating outputs with commands like:

`jupyter nbconvert --to notebook --execute --inplace examples/<nb>.ipynb`

In this environment, `.venv/bin/jupyter nbconvert --to notebook --execute ... examples/dg1_walkthrough.ipynb` fails immediately with `ModuleNotFoundError: No module named 'cbg'`.

The package import itself works under `.venv/bin/python`, so this appears to be a kernel/path issue. The active kernelspec at `.venv/share/jupyter/kernels/python3/kernel.json` uses:

```json
"argv": ["python", "-m", "ipykernel_launcher", "-f", "{connection_file}"]
```

not an absolute `.venv/bin/python`. That makes the documented execution path fragile.

Notebook output state is also mixed:

- `examples/dg1_walkthrough.ipynb`: 5 code cells, 0 with outputs/execution counts.
- `examples/dg2_structural.ipynb`: 4 code cells, 0 with outputs/execution counts.
- `examples/dg3_cross_method.ipynb`: 4 code cells, 4 with outputs/execution counts.
- `examples/dg4_walkthrough.ipynb`: 6 code cells, 6 with outputs/execution counts.

### MEDIUM - Sphinx build succeeds but emits doc warnings that could become release blockers

The temp Sphinx build completed, but emitted 15 warnings/docutils issues. Main categories:

- Definition/field-list blank-line warnings in `cbg/tcl_recursion.py`.
- Block quote blank-line warning in `cbg/bath_correlations.py`.
- Undefined substitution warnings involving bra-ket text in `cbg/effective_hamiltonian.py` and `cbg/basis.py`.
- Unexpected indentation warnings in `models/pure_dephasing.py`, `models/spin_boson_sigma_x.py`, `numerical/tensor_ops.py`, and `numerical/time_grid.py`.
- Duplicate object descriptions for `numerical.time_grid.TimeGrid.times`, `n_points`, and `scheme`.

This is currently non-fatal because the docs command does not use `-W`, but it is inconsistent with a clean docs-build expectation.

### MEDIUM - Card schema version references are mixed

`benchmarks/benchmark_cards/SCHEMA.md:5` says the schema version is v0.1.3, and the changelog at `SCHEMA.md:387` describes v0.1.3 as the current revision. Other places still present v0.1.2 as current or active:

- `benchmarks/benchmark_cards/SCHEMA.md:376` says "The current version is v0.1.2".
- `benchmarks/benchmark_cards/_template.yaml:4` and `:43` claim schema v0.1.2.
- `benchmarks/results/DG-1_summary.json:8` records `SCHEMA.md (v0.1.2)`.
- `scripts/run_dg1_verdict.py:22` and `:132` reference v0.1.2.
- `docs-site/reporting.md:3` says implementation of the SCHEMA.md v0.1.2 lifecycle.
- `index.html:195` links to "card schema (SCHEMA.md v0.1.2)".

Some historical card references can legitimately remain at the card's authored schema version. The inconsistency is that central docs and the template still present v0.1.2 as the live schema while the schema file header says v0.1.3.

### MEDIUM - Existing review notes are stale relative to current repo state

`reviews/FAIR_review_2026-05-04.md` is now internally stale:

- `:7` says 368 tests pass; current run has 471.
- `:53` says 323 tests pass; current run has 471.
- `:98` says Black/Ruff/MyPy all pass; current runs fail.
- `:152` and `:169` say CI does not enforce Black/Ruff/MyPy; `.github/workflows/tests.yml:48-70` does enforce them.
- `:171` says there are no examples/notebooks; `examples/` and rendered `api/examples/*.html` now exist.

The file is historical, but it is in the active `reviews/` folder and reads partly as current assessment.

### LOW - Local workspace residue is present

Ignored or untracked local residue is present on disk:

- Python cache directories and `.pyc` files for both CPython 3.9 and 3.13 across `cbg/`, `models/`, `numerical/`, `benchmarks/`, `reporting/`, and `tests/`.
- Empty local directory `api/_static 2`.

This does not affect tracked release content, but it is noise for repo hygiene and can confuse manual tree scans.

## Not Flagged

- The core test suite itself is healthy: `471 passed`.
- Tracked JSON/YAML files parse successfully.
- The Sphinx left toctree contains the worked examples entry via `docs-site/index.md:50-55`.
- Rendered notebook pages exist under `api/examples/`.
- The raw HTML links in `docs-site/examples.md` render correctly in the current `api/examples.html`; I did not find the earlier MyST rewrite issue in the current rendered file.

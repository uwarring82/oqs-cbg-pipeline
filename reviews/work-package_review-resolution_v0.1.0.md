# Work Package — Review-Resolution v0.1.0

**Author:** Steward (drafted from Rounds 1–3 review evidence)
**Drafted:** 2026-05-08
**Revised:** 2026-05-08 (post-review revisions integrating steward + second-reviewer feedback on the v0.1.0 first draft)
**Status:** draft, awaiting steward triage and sequencing
**Inputs:**
- [`round-1_2026-05-04/kimi_fair-review.md`](round-1_2026-05-04/kimi_fair-review.md)
- [`round-2_2026-05-06/gemini_inconsistency-flags.md`](round-2_2026-05-06/gemini_inconsistency-flags.md)
- [`round-3_2026-05-08/claude_consistency-review.md`](round-3_2026-05-08/claude_consistency-review.md)
- [`round-3_2026-05-08/codex_consistency-audit.md`](round-3_2026-05-08/codex_consistency-audit.md)
- [`round-3_2026-05-08/anonymous_structural-review.md`](round-3_2026-05-08/anonymous_structural-review.md)

---

## 1. Purpose

Three review rounds (Kimi 2026-05-04, Gemini 2026-05-06, Claude+Codex+anonymous
2026-05-08) collectively surface **35+ distinct issues** in documentation
drift, FAIR-metadata staleness, post-supersedure rollforward gaps,
CI-quality-gate failures, formula/labeling inconsistencies, and structural /
packaging hygiene. **None currently invalidates a recorded DG verdict; most
are documentation, metadata, or tooling drift** relative to the authoritative
`docs/validity_envelope.md`. A subset (H4, M4, M5, S10, S11, S12) are
tooling, build, or runtime surfaces — those are not "documentation drift"
and the workstreams below treat them accordingly.

This work package consolidates those issues into actionable workstreams,
proposes acceptance criteria, and sequences the work. It is intentionally
written without surprising scope creep: each item maps to a specific quoted
finding from the source reviews.

## 2. Issue inventory

Issues are grouped by severity (Codex / Claude classifications adopted as
primary; Gemini items folded into the same scheme).

### HIGH — verdict-adjacent or CI-blocking

| ID | Title | Source(s) | Surface |
|---|---|---|---|
| **H1** | `DG-4_summary.json` still cites D1 v0.1.1 | Gemini §1; Claude #2; Codex HIGH "DG-4 live status" | `benchmarks/results/DG-4_summary.json:13-24` |
| **H2** | FAIR metadata omits DG-4 PASS | Claude #1; Codex HIGH "FAIR and citation metadata" | `.zenodo.json:3,40`; `codemeta.json:5-7`; `CITATION.cff:7-13,21` |
| **H3** | DG-4 v0.1.1 references scattered across cards-README, plans-README, runner code, recursion comments | Codex HIGH "DG-4 live status" | `benchmarks/benchmark_cards/README.md:45,60,72`; `plans/README.md:55,61,78`; `reporting/benchmark_card.py:150-159,1447`; `benchmarks/numerical_tcl_extraction.py:382`; comments in `cbg/tcl_recursion.py` |
| **H4** | CI quality gates currently fail (ruff 8, black 8, mypy 6) | Codex HIGH "CI quality gates" | `.github/workflows/tests.yml:48-70` is enforcing; tree fails locally |

(H5 reclassified to **M0** in the MEDIUM table below — user-facing but neither verdict-adjacent nor CI-blocking.)

### MEDIUM — interpretive risk or release-blocker drift

| ID | Title | Source(s) | Surface |
|---|---|---|---|
| **M0** | `README.md` says "Two notebooks", ships four | Claude #3; Codex MEDIUM "Worked-example surfaces" | `README.md:83-86` *(reclassified from H5; user-facing but not verdict-adjacent or CI-blocking)* |
| **M1** | `r_4` defined two ways (with vs. without α² prefactor) | Claude #4; Codex MEDIUM "DG-4 metric text" | Many locations; see Codex §"DG-4 metric text" |
| **M2** | Card schema version drift (header says v0.1.3; many surfaces still say v0.1.2) | Codex MEDIUM "Card schema version" | `SCHEMA.md:5,376,387`; `_template.yaml:4,43`; `DG-1_summary.json:8`; `scripts/run_dg1_verdict.py:22,132`; `docs-site/reporting.md:3`; `index.html:195` |
| **M3** | DG-4 example prose mixes reduced-fixture vs full-frozen-run behavior; notebook self-labels v0.1.1 while loading v0.1.2 | Codex MEDIUM "DG-4 example prose" | `examples/dg4_walkthrough.ipynb:15,90,110,122`; `examples/README.md:12`; `docs-site/examples.md:52-53`; `api/examples.html:407-408` |
| **M4** | `nbconvert --execute` fails (kernelspec uses bare `python`, not `.venv/bin/python`) | Codex MEDIUM "Notebook execution" | `.venv/share/jupyter/kernels/python3/kernel.json` |
| **M5** | Sphinx build emits 15 warnings (definition lists, bra-ket substitutions, indentation, duplicate object descriptions) | Codex MEDIUM "Sphinx build warnings" | `cbg/tcl_recursion.py`, `cbg/bath_correlations.py`, `cbg/effective_hamiltonian.py`, `cbg/basis.py`, `models/pure_dephasing.py`, `models/spin_boson_sigma_x.py`, `numerical/tensor_ops.py`, `numerical/time_grid.py` |
| **M6** | `MEMORY.md` links non-existent `feedback_cards_first_discipline.md` | Claude #5 | `MEMORY.md:2` |
| **M7** | "B4" / "B5" short-name vs. `B4-conv-registry` / `B5-conv-registry` filenames | Claude #6; Codex MEDIUM | `README.md:86`; `examples/README.md:10` |

### LOW — copy nits, hygiene

| ID | Title | Source(s) | Surface |
|---|---|---|---|
| **L1** | DG-2 status label varies ("PARTIAL" vs "STRUCTURAL SUB-CLAIMS PASS") | Claude #7 | `validity_envelope.md`, `README.md:114`, `index.html:176`, `docs-site/index.md:32` |
| **L2** | DG-1 demo notebook listing omits A4 | Claude #8 | `README.md:85`; `examples/README.md:9` |
| **L3** | `CITATION.cff` / `codemeta.json` release-date pinned 2026-05-04 (predates DG-4) | Claude #9 (subsumed by H2 if treated together) | — |
| **L4** | PhD tutorial HTML v0.2 vintage 2026-04-30, no staleness caveat | Claude #10 | `README.md:90` |
| **L5** | `DG-1_summary.json` has no field documenting Entry 1.B.3 / 3.B.3 / 4.B.2 repatriation | Claude #11 | `benchmarks/results/DG-1_summary.json` |
| **L6** | Hayden–Sorce transcription v0.1.0 retained alongside v0.1.1, no in-file "superseded" marker checked | Claude #12 | `transcriptions/hayden-sorce-2022_pseudokraus_v0.1.0.md` |
| **L7** | Local workspace residue (pyc files for both py3.9 and py3.13; empty `api/_static 2`) | Codex LOW "Local workspace residue"; Anonymous #1 | — |

### Round-3 anonymous structural review (additional MEDIUM/LOW)

| ID | Title | Source | Surface |
|---|---|---|---|
| **S1** | Card naming: `B4-conv-registry` / `B5-conv-registry` use kebab-case while every other card embeds hyphens inside an underscore-separated short-tag (e.g. `A1_closed-form-K`) | Anonymous #2 | `benchmarks/benchmark_cards/B[45]-conv-registry_v*.yaml` and matching result JSONs |
| **S2** | `docs-site/conf.py:4` `release = "v0.2.0+dev"` is two milestones stale (last tag is `v0.5.0`; package is `0.3.0.dev0`); the stale string is baked into served HTML in `api/` | Anonymous #3 | `docs-site/conf.py:4`; `api/index.html` `<title>` and meta tags |
| **S3** | Script executable-bit asymmetry: `scripts/build_docs.sh` is `+x`, `scripts/run_dg1_verdict.py` is not (and has no shebang) | Anonymous #4 | `scripts/` |
| **S4** | `tests/__init__.py` is 0 bytes (every other package init carries a docstring) | Anonymous #5, #13 | `tests/__init__.py` |
| **S5** | No `__all__` in any of the six top-level packages; `from cbg import *` would currently leak deleted-but-revivable underscore names | Anonymous #6 | All `__init__.py` files |
| **S6** | No SPDX or license headers in any source file despite the dual-licensing discipline (MIT code / CC-BY docs) | Anonymous #7 | All `*.py` |
| **S7** | CI lint scope (`tests/` included) vs `pyproject.toml` package list (`tests/` excluded) — two sources of truth that disagree on package boundary | Anonymous #8 | `.github/workflows/tests.yml:62-68`; `pyproject.toml:46` |
| **S8** | Python 3.13 not in classifiers / CI matrix (currently 3.10–3.12 only) | Anonymous #9 | `pyproject.toml`; `.github/workflows/tests.yml` |
| **S9** | `CONTRIBUTING.md:53` tells contributors to run ruff + black; omits mypy (which CI enforces) | Anonymous #10 | `CONTRIBUTING.md:53` |
| **S10** | Stub model files: `models/fano_anderson.py` (38 lines, 0 funcs/classes) and `models/jaynes_cummings.py` (29 lines, 0 funcs/classes); E1 card references the Fano-Anderson model with no callable API | Anonymous #11 | `models/fano_anderson.py`, `models/jaynes_cummings.py` |
| **S11** | `NotImplementedError` paths still present in `benchmarks/exact_finite_env.py` (×2) and `benchmarks/qutip_reference.py` (×5); validity envelope's "no NotImplementedError paths remain for C1/C2 frozen test cases" is true only for the *frozen* test cases | Anonymous #12 | the two benchmark modules |
| **S12** | `scripts/run_dg1_verdict.py` manually injects `sys.path` to bypass `pip install -e .`; contradicts README's documented install path | Anonymous #15 | `scripts/run_dg1_verdict.py:36-42` |
| **S13** | No `.github/ISSUE_TEMPLATE/`, no `.github/PULL_REQUEST_TEMPLATE.md`, no `CODEOWNERS` despite a detailed `CONTRIBUTING.md` | Anonymous #16 | `.github/` |
| **S14** | `oqs_cbg_pipeline.egg-info/` present in working tree (correctly ignored, but visual clutter for contributors) | Anonymous #18 | working-tree only |

### Round-1 / Round-2 items now de-prioritised by archival

| ID | Title | Source | Disposition |
|---|---|---|---|
| **A1** | Kimi FAIR review (Round 1) is internally stale and self-contradictory (test counts, CI enforcement, exact_finite_env status) | Gemini §2 A/B/C; Codex MEDIUM "Existing review notes are stale" | Round 1 review is now archived under `round-1_2026-05-04/`; archived reviews are point-in-time and not edited. **No action.** Mitigation: this `README.md` index makes the staleness explicit. |
| **A2** | Tag-vs-package SemVer drift (`v0.5.0` tag vs `0.3.0.dev0` package) | Gemini §3 | CHANGELOG already documents this as intentional (tags anchor verdicts, not releases). **No action**; possibly add a one-line clarifier in `pyproject.toml` description. |
| **A3** | `dg-1-work-plan_v0.1.3.md` retains `status: active` per design ("no in-place transition") | Gemini §4 | Documented design decision per plan §8.1. **No action.** |
| **A4** | Logbook entry "v0.1.2 supersedure pending Path B repair" reads as contradicting CHANGELOG's "landed" state | Gemini §5 | Logbook is append-only point-in-time; CHANGELOG reflects end-of-day state. **No action**; both are correct in their own frame. |

## 3. Workstreams

Issues regrouped by which surface gets touched. Each workstream is a small,
auditable commit (or a small series). Acceptance criteria are stated so each
workstream's PR can declare completion explicitly.

### WS-A — DG-4 v0.1.1 → v0.1.2 rollforward (consumes H1, H3; partial M3)

**Scope.** A grep-and-update pass to bring every "v0.1.1" reference to
v0.1.2, EXCEPT historical surfaces (CHANGELOG, logbook, superseded YAMLs,
git-tag prose) where v0.1.1 is correctly preserved as history.

**Targets:**
- `benchmarks/results/DG-4_summary.json` — `card_version`, `card_path`,
  `evidence`; rewrite `summary` and `limitations` to match v0.1.2 (the
  `upper_cutoff_factor` operationality limitation is now obsolete).
- `benchmarks/benchmark_cards/README.md` lines 45, 60, 72.
- `plans/README.md` lines 55, 61, 78.
- `reporting/benchmark_card.py` module-docstring lines 150-159; the
  "DG-4 sweep runner not yet implemented" comment is now false; line 1447
  metric-name reference.
- `benchmarks/numerical_tcl_extraction.py:382`.
- `cbg/tcl_recursion.py` D1-fixture comments/docstrings.
- `examples/dg4_walkthrough.ipynb:90` ("Card D1 v0.1.1 freezes…").

**Acceptance criteria.**
1. `git grep -n 'D1 v0.1.1'` and
   `git grep -n 'D1_failure-envelope-convergence_v0.1.1'` return only the
   historical surfaces (CHANGELOG, logbook, superseded card YAML,
   supersedure log) — never live runner code, live result JSON, live
   notebook, live plans-README, or live cards-README.
2. **Regression test passes.** `pytest tests/test_benchmark_card.py -k dg4`
   completes with exit code 0; the existing
   `test_dg4_path_b_upper_cutoff_factor_is_operational` and the v0.1.2
   audit-shape regression tests continue to pass with the rewritten
   `DG-4_summary.json`. This guards against accidentally degrading the
   v0.1.2 verdict surface while editing summary metadata.

**File-collision note.** WS-A and WS-D both touch
`reporting/benchmark_card.py` and `benchmarks/numerical_tcl_extraction.py`.
Land WS-D first (clean lint baseline), then rebase the WS-A branch onto
the post-WS-D `main`. See §4.

### WS-B — FAIR metadata roll-forward (consumes H2, L3)

**Scope.** Single edit pass to the three FAIR files, lifting status to the
2026-05-06 / DG-4 PASS state. The wording can be reused verbatim from
`docs/validity_envelope.md:43-58` ("Authorised uses").

**Targets:**
- `.zenodo.json` — description (line 3), notes (line 40), `version` if a
  bump is decided (see decision below).
- `codemeta.json` — description (line 5), `datePublished` (line 7).
- `CITATION.cff` — abstract (lines 7-13), `date-released` (line 21).

**Decision required.**
- Roll `date-released` / `datePublished` to 2026-05-06? Or keep at the
  2026-05-04 release event of the `0.3.0.dev0` metadata version and add
  prose making explicit that the FAIR record reflects the *metadata*
  release date, not the latest verdict? Recommendation: **bump dates
  forward** to 2026-05-06 since the description text changes anyway.
- Bump `version` from `0.3.0.dev0`? Recommendation: **no** — Codex's A2
  notes the tag-vs-package distinction is intentional; bumping
  `0.3.0.dev0` would break the documented convention.

**Acceptance criterion.** All three FAIR files mention DG-4 PASS at
D1 v0.1.2 (2026-05-06). Description text matches the validity envelope's
DG-4 row in substance.

### WS-C — README + examples surface alignment (consumes M0, M3 doc-side, M7, L2, L4)

**Scope.** Update README and `examples/README.md` to match the actual
four-notebook layout and authoritative card naming.

**Targets:**
- `README.md:83-86` — replace "Two runnable Jupyter notebooks" with the
  four-notebook listing; mirror `examples/README.md`'s correct version.
  Use full card names: `B4-conv-registry`, `B5-conv-registry`.
  Add A4 to the DG-1 line.
- `README.md:90` — add staleness caveat to the PhD tutorial link
  ("dated 2026-04-30; pre-DG-2 / pre-DG-4 — for theoretical orientation
  only").
- `examples/README.md:9` — add A4 to DG-1 row; rename "B4" / "B5" to
  full names; reconcile DG-4 row prose with `dg4_walkthrough.ipynb`.
- `examples/README.md:28-29` — extend the `nbconvert --execute` example
  block to all four notebooks, OR remove (see WS-H).
- `examples/dg4_walkthrough.ipynb:15,90,110,122` — sync notebook prose to
  v0.1.2; clarify reduced-fixture vs frozen-run distinction.

**Acceptance criterion.** README and `examples/README.md` agree on (a) the
notebook count, (b) the card name format, and (c) DG-1's three-card
roster. `dg4_walkthrough.ipynb` has no internal "v0.1.1" references.

### WS-D — CI quality gates back to green (consumes H4)

**Scope.** Make `ruff` / `black --check` / `mypy` pass on the CI scope.
**Sequencing rule:** establish a green quality baseline first, then rerun
the full quality gate after each subsequent content workstream lands.
Several content workstreams (notably WS-A, WS-E, WS-G) edit files that
already trip the gates; running WS-D first prevents the formatting noise
from contaminating their diffs.

**Targets** (per Codex enumeration):
- Ruff (8 diagnostics): import ordering in `benchmarks/exact_finite_env.py`
  and `tests/test_exact_finite_env.py`; stale py-version guards in
  `cbg/__init__.py`, `conftest.py`; E402 in `cbg/__init__.py`; F541 at
  `reporting/benchmark_card.py:1815`; UP032 at
  `tests/test_benchmark_card.py:1089`.
- Black (8 files): `docs-site/conf.py`, `benchmarks/qutip_reference.py`,
  `benchmarks/exact_finite_env.py`, `benchmarks/numerical_tcl_extraction.py`,
  `tests/test_numerical_tcl_extraction.py`, `tests/test_exact_finite_env.py`,
  `tests/test_benchmark_card.py`, `reporting/benchmark_card.py`.
- MyPy (6 errors): `benchmarks/qutip_reference.py`,
  `benchmarks/numerical_tcl_extraction.py`, `reporting/benchmark_card.py`.

**Acceptance criterion.** `ruff check`, `black --check`, and `mypy` over
the CI-configured scope all return exit code 0. CI's `code-quality` job
goes green on a fresh push.

### WS-E — `r_4` formula reconciliation (consumes M1)

**Scope.** Pick one definition of `r_4` and propagate.

**Decision required.**
- **Option A (preferred):** Adopt the runner's definition
  `r_4(α²) = α² · ⟨‖L_4^dis‖⟩_t / ⟨‖L_2^dis‖⟩_t`. Update validity envelope,
  benchmark protocol, README, CHANGELOG, index.html, docs-site, and the
  D1 v0.1.2 card's headline-formula lines (110, 155, 186) to include the
  α² factor.
- **Option B:** Rename the unscaled quantity `coefficient_ratio` and
  reserve `r_4` for the scaled quantity. Update the runner's docstrings
  to match if needed.

Recommendation: **Option A**. The runner is authoritative and changing
prose is cheaper than renaming a programmatic quantity.

**Acceptance criteria.**
1. `git grep -n 'r_4 = '` returns only formulas with the α² (or
   coupling-strength) prefactor for live surfaces; historical
   CHANGELOG/logbook entries keep their original wording.
2. **Numerical-stability check.** Re-run `_run_dg4_sweep` against
   D1 v0.1.2's frozen sweep and confirm the per-α `r_4_baseline` values
   match the persisted result JSON
   `benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json`
   to within the existing tolerance. WS-E only changes prose; if the
   numbers shift, the change has overshot scope and must be reverted.

### WS-F — Card schema version reconciliation (consumes M2)

**Context.** `SCHEMA.md` already records v0.1.3 in its frontmatter
(`:5`) and has a v0.1.3 changelog entry (`:387`, drafted 2026-05-05,
adding `frozen_parameters.sweep:` for DG-4 and the `scope-definition`
status value). The bump is therefore intentional and substantive (D1
sweep specification + E1 scope-definition status both depend on it).
The inconsistency is **not** "is the bump intentional"; it is that the
body prose (`SCHEMA.md:376`), `_template.yaml`, and several pointers
elsewhere in the tree still call v0.1.2 the current version.

**Scope.** Propagate v0.1.3 consistently across all *current* surfaces;
leave already-frozen card YAMLs unchanged at their authored
schema_version (this is explicit per `SCHEMA.md`'s grandfathering rule
that "a card under schema v0.1.2 continues to exist unchanged after the
schema bumps to a future v0.1.3").

**Targets:**
- `SCHEMA.md:376` — replace "The current version is v0.1.2" with v0.1.3.
- `_template.yaml:4,43` — bump schema reference (the template is for
  *new* cards, which adopt the live schema).
- `scripts/run_dg1_verdict.py:22,132` — bump.
- `docs-site/reporting.md:3` — bump.
- `index.html:195` — bump.
- `DG-1_summary.json:8` — **leave at v0.1.2** (historical pin: the DG-1
  cards were authored under v0.1.2). Add a one-line note to that effect
  in `benchmarks/results/README.md` (create if absent) or in the
  validity envelope.

**Decision required.** **The decision is no longer "add a changelog
entry" — the entry exists.** The remaining decision is binary:
*propagate v0.1.3 consistently across current surfaces* (recommended),
*or revert SCHEMA.md's frontmatter/changelog to v0.1.2 if the live tree
is intentionally pinned at v0.1.2*.

**Acceptance criterion.** `SCHEMA.md`'s header version, body's "current
version" prose, and the `_template.yaml`/`scripts`/`docs-site`/`index.html`
references all agree.

### WS-G — Sphinx build cleanup (consumes M5)

**Scope.** Resolve the 15 docstring warnings emitted by `sphinx-build -b html`.
Defer until after WS-A–C since those workstreams may also touch the same
docstrings (notably in `cbg/tcl_recursion.py`). Then run with `-W` in CI.

**Targets:** docstring formatting in `cbg/tcl_recursion.py`,
`cbg/bath_correlations.py`, `cbg/effective_hamiltonian.py`, `cbg/basis.py`,
`models/pure_dephasing.py`, `models/spin_boson_sigma_x.py`,
`numerical/tensor_ops.py`, `numerical/time_grid.py`. Resolve duplicate
object descriptions for `numerical.time_grid.TimeGrid.times` /
`n_points` / `scheme` (likely a `:noindex:` issue in autodoc).

**Acceptance criterion.** `sphinx-build -W -b html docs-site /tmp/out`
exits 0.

### WS-H — Notebook execution reproducibility (consumes M4)

**Scope.** Make `jupyter nbconvert --execute examples/<nb>.ipynb` succeed
from a fresh `[dev]` install. The Codex finding traces to a kernelspec
(`.venv/share/jupyter/kernels/python3/kernel.json`) whose `argv` uses bare
`python` instead of `sys.executable`, but **`.venv/` is local environment
state, not a repo artifact** — the workstream targets only repo-owned
docs and build behavior.

**Targets (repo-owned only):**
- `examples/README.md` — document the supported execution path explicitly
  (e.g., `python -m jupyter nbconvert --to notebook --execute --inplace
  examples/<nb>.ipynb`, which uses the active interpreter rather than
  whatever `python` resolves to in PATH). Or document a one-time kernel
  registration: `python -m ipykernel install --user --name oqs-cbg
  --display-name "Python (oqs-cbg-pipeline)"` and then nbconvert with
  `--ExecutePreprocessor.kernel_name=oqs-cbg`.
- `scripts/build_docs.sh` — if it executes notebooks during the docs
  build, set `PATH` / pin the interpreter explicitly (`"$VENV/bin/python"
  -m jupyter nbconvert …`), so the build behavior is independent of
  whichever kernelspec a contributor's local Jupyter happens to register.
- `CONTRIBUTING.md` — note the `python -m jupyter` form as the supported
  invocation (one-line update; ties into WS-La S9).

**Out of scope (explicitly):** any edit to `.venv/`, `~/.jupyter/`, or
the user's local kernelspec. Those are environment state; the workstream
fixes the **repo's documented execution path** so any compliant
environment can reproduce.

**Acceptance criterion.** From a fresh `git clone` + `pip install -e
".[dev]"` + `pip install jupyter`, the documented invocation form (one
line, copy-pastable from `examples/README.md`) runs `jupyter nbconvert
--execute` on each of the four notebooks and exits with code 0 and no
uncaught Python exceptions. (Cell-output identity to a frozen reference
is **not** required at this scope; that would require a checked-in
reference output set, which is a separate decision.)

### WS-I — Status label / link / repatriation nits (consumes L1, L5, M6)

**Scope.** Three small fixes — **but L5 needs a steward decision before
execution** (see below).

- **L1 (in scope):** Pick "PARTIAL" as the canonical DG-2 status label;
  update README, index.html, docs-site to use it; validity envelope
  already uses it.
- **L5 (decision required, do not execute as written in v0.1.0 draft):**
  The v0.1.0 draft proposed adding a `repatriated_sub_claims` field to
  `benchmarks/results/DG-1_summary.json`. **This may conflict with the
  project's audit-trail discipline.** A result JSON anchored to a
  Decision Gate verdict commit is plausibly *immutable* in the same
  spirit as logbook entries and frozen card YAMLs. The decision is:
  - **Path L5-a:** If summary JSONs are mutable indexes (i.e., they
    aggregate links and can be refreshed without disturbing the verdict's
    immutability), add the `repatriated_sub_claims` field directly. This
    requires confirming the pattern in `SCHEMA.md` or another governance
    doc.
  - **Path L5-b (preferred default):** Treat summary JSONs as
    point-in-time verdict artefacts and record the repatriation note
    elsewhere. Two natural homes: (i) `docs/validity_envelope.md`'s
    DG-1 row already mentions the repatriation prose-side, and could
    be linked from `DG-1_summary.json` via an *index-style* file
    `benchmarks/results/README.md` listing each result and its
    cross-references; or (ii) the existing `logbook/` entry that closed
    DG-1 already records the carve-out.
  Until the steward chooses, leave `DG-1_summary.json` untouched.
- **M6 (in scope):** Either delete the `MEMORY.md:2` link, or place a
  copy of `feedback_cards_first_discipline.md` at repo root. Recommend
  the former — that file is user-level agent memory and is not part of
  the repo's tracked corpus.

**Acceptance criterion.** L1 and M6 land as line-level edits; L5 lands
as either (a) a documented `summary JSON immutability` policy plus the
field addition, or (b) a `benchmarks/results/README.md` index file with
the repatriation note. Either path is acceptable; silent mutation of the
summary JSON is not.

### WS-J — Repo hygiene (consumes L6, L7, S14)

**Scope.** Repo-tracked cleanup only, no semantic change.

- **L6 (in scope, auditable commit):** Add a `status: superseded_by_v0.1.1`
  header line to `transcriptions/hayden-sorce-2022_pseudokraus_v0.1.0.md`
  (or delete the v0.1.0 file if the project's discipline is to retain only
  the latest transcription; check `transcriptions/README.md` first).
- **L7 part-1 (in scope):** Remove the spurious empty directory `api/_static 2/`
  if it is tracked, and add a `.gitignore` rule preventing it from
  reappearing if the build process re-creates it.
- **L7 part-2 (out of scope — local cleanup only):** Removing `__pycache__/`
  and stale `.pyc` files for both py3.9 and py3.13 is **manual / local**,
  not an auditable commit. The project's `.gitignore` already excludes
  these. Contributors run `find . -name '__pycache__' -exec rm -rf {} +`
  on their own machines as needed; this work package does **not**
  prescribe `git clean -fdX` (destructive, non-auditable, and may
  remove the contributor's untracked work in adjacent dirs).
- **S14 (out of scope — local only):** `oqs_cbg_pipeline.egg-info/` is
  correctly ignored. Optional follow-up: add a one-line note in
  `CONTRIBUTING.md` warning contributors that `pip install -e .` creates
  an untracked `egg-info` dir (this overlaps with WS-La S12).

**Acceptance criterion.** `git status` from a fresh clone shows no
empty/duplicated directories under `api/`; the v0.1.0 transcription
either deleted or carrying an in-file supersedure marker.

### WS-K — Sphinx release string + naming/conventions (consumes S1, S2)

**Scope.** Two small docs-site fixes that are conceptually independent of
the rest.

- **S2 (Sphinx release string):** Update `docs-site/conf.py:4` from
  `release = "v0.2.0+dev"` to track the package's `__version__`. Naive
  `from importlib.metadata import version; release =
  version("oqs-cbg-pipeline")` **will fail** if the docs are built
  without a `pip install -e .` (e.g., a fresh sphinx-only build).
  Use a robust fallback chain instead:

  ```python
  # docs-site/conf.py
  try:
      from importlib.metadata import version as _v
      release = _v("oqs-cbg-pipeline")
  except Exception:
      try:
          from cbg import __version__ as release  # in-tree fallback
      except Exception:
          # Last-resort fallback: parse pyproject.toml
          import tomllib, pathlib
          _pp = pathlib.Path(__file__).parent.parent / "pyproject.toml"
          release = tomllib.loads(_pp.read_text())["project"]["version"]
  ```

  Then rebuild `api/` so the served HTML's `<title>` / meta tags refresh.

- **S1 (naming convention):** Decide whether to rename `B4-conv-registry`
  / `B5-conv-registry` to a snake-tag form like `B4_conv-registry`. The
  rename is **risky** because the cards are referenced by exact filename
  in validity envelope, CHANGELOG, logbook, plans, README, index.html,
  benchmark protocol, and example notebooks (≥10 files), and would create
  supersedure-record ambiguity. **Recommend not renaming**; instead amend
  `SCHEMA.md` to make the de-facto naming rule explicit. Draft amendment
  text for the §"File layout and naming" section:

  > **Filename pattern.** `<card_id>_<short-tag>_v<MAJOR.MINOR.PATCH>.yaml`
  >
  > - `<card_id>` and `v<version>` are separated from `<short-tag>` by
  >   underscores `_`.
  > - `<short-tag>` is itself a hyphen-separated kebab-case slug
  >   (e.g. `closed-form-K`, `cross-basis-structural-identity`,
  >   `conv-registry`). **Hyphens within the short-tag are required**;
  >   underscores within the short-tag are reserved as the field
  >   separator and must not appear inside the slug.
  > - Examples (canonical): `A1_closed-form-K_v0.1.1.yaml`,
  >   `B3_cross-basis-structural-identity_v0.1.0.yaml`,
  >   `B4-conv-registry_v0.1.0.yaml` *(legacy: see note)*.
  >
  > *Legacy note.* Cards `B4-conv-registry` and `B5-conv-registry`
  > predate the explicit underscore-separator rule and embed the
  > `<card_id>` directly into the kebab slug. They are retained at
  > their original filenames per the supersedure-record stability
  > rule; new cards must follow the canonical pattern above.

**Acceptance criterion.** (a) Sphinx-built `api/index.html` carries a
release string that matches `pyproject.toml`'s `version` under both
`pip install -e .`-installed and uninstalled docs builds; (b)
`SCHEMA.md` carries the filename-pattern amendment above (or a
steward-revised equivalent). No file rename in `benchmarks/benchmark_cards/`.

### WS-L (split) — Packaging & contribution discipline

The v0.1.0 draft bundled S3–S13 into a single "WS-L" workstream. That is
a junk drawer: it mixes one-line hygiene fixes with policy decisions
(SPDX, Py3.13 support, stub-model architecture). Splitting along the
nature of the change, with the more interactive items separated:

#### WS-La — Trivial hygiene (consumes S3, S4, S9, S12, S14)

**Scope.** Single PR batching no-decision-needed one-liners.

- **S3:** `scripts/run_dg1_verdict.py` is documented in README as
  `python scripts/run_dg1_verdict.py`. Leave executable bit off; **no
  action**, but record this disposition.
- **S4:** Add a one-line docstring (e.g. `"""Test suite."""`) to
  `tests/__init__.py`.
- **S9:** Add `mypy` to the tool list in `CONTRIBUTING.md:53` (currently
  mentions only ruff + black). One-line edit.
- **S12:** `scripts/run_dg1_verdict.py` manually injects `sys.path`. Add
  a header comment to the script documenting this as the supported
  "checkout-and-run" path; flag the `pip install -e .` form as the
  preferred path. **No code change**, only a docstring/comment update.
- **S14:** Add a one-line note in `CONTRIBUTING.md` warning contributors
  that `pip install -e .` creates an untracked `oqs_cbg_pipeline.egg-info/`.

**Acceptance criterion.** Single PR; all five items batched; no policy
decisions surface.

#### WS-Lb — Policy decisions (consumes S6, S8, S10, S13)

**Scope.** Each item needs a steward decision and lands as its own PR
so the rationale is atomic in git history.

- **S6 (SPDX-header policy).** Recommended yes; add `# SPDX-License-Identifier:
  MIT` to all `*.py` files under `cbg/`, `models/`, `numerical/`,
  `benchmarks/`, `reporting/`, `tests/`, `scripts/`. Decision before
  execution.
- **S8 (Python 3.13 support).** Recommended: add a 3.13 row to
  `.github/workflows/tests.yml` first; promote to a `pyproject.toml`
  classifier only after a green run. Decision before execution.
- **S10 (stub model files).** **Do NOT raise `ScopeDefinitionNotRunnableError`
  on import** — that would break `from models import fano_anderson`,
  Sphinx autodoc, and any CI step that imports the `models` package as
  a whole. Two safe alternatives:
  - **Path S10-a (preferred):** Add explicit stub functions to
    `models/fano_anderson.py` and `models/jaynes_cummings.py` (e.g.
    `def make_model(*args, **kwargs): raise ScopeDefinitionNotRunnableError(...)`)
    plus a top-of-module docstring marking the scope-definition state.
    Imports succeed; calls fail with the appropriate error.
  - **Path S10-b:** Leave the modules as docstring-only and update the
    relevant card / validity envelope prose to reference the
    docstring-as-scope-definition discipline.
  Decision before execution.
- **S13 (GitHub templates).** Add `.github/ISSUE_TEMPLATE/bug_report.md`,
  `.github/ISSUE_TEMPLATE/dg-status-change.md`, and
  `.github/PULL_REQUEST_TEMPLATE.md` with the project's required
  metadata. Decision required only on the *content* of the templates;
  recommended yes by default.

**Acceptance criterion.** Four PRs (one per S* item); each carries its
own decision rationale in the commit message.

#### WS-Lc — Packaging alignment (consumes S5, S7, S11)

**Scope.** Three items that touch package boundaries / public API
surface and interact, so they should land together.

- **S5 (`__all__` declarations).** Add `__all__` lists to the six
  package `__init__.py` files. The `cbg/__init__.py` case is sensitive:
  several private names (`_sys`, `_pkg_version`, `_PNF`, `_os`,
  `_warnings`, `_repo_root`, `_docs_dir`) are explicitly `del`-ed but
  `__all__` makes the export contract explicit and survives future
  refactors.
- **S7 (`pyproject.toml` vs CI lint scope).** `pyproject.toml`'s
  `packages = [...]` excludes `tests/` (correct: it is not an installable
  package). CI lints `tests/` (also correct). The "inconsistency" is
  cosmetic; document it explicitly in `CONTRIBUTING.md` (one paragraph)
  rather than restructuring.
- **S11 (`NotImplementedError` wording).** Tighten the validity
  envelope's wording: "no `NotImplementedError` paths remain for the
  frozen C1/C2 test fixtures" (current) → "no `NotImplementedError`
  paths are reachable on the frozen C1/C2 test fixtures; the underlying
  benchmark modules retain `NotImplementedError` paths for non-frozen
  parameter combinations".

**Acceptance criterion.** Single PR; the public-surface diff (`__all__`
exports) is reviewed line-by-line; validity envelope wording change
is the only DG-doc edit in this PR (so the diff is clean).

## 4. Sequencing

Recommended order:

1. **WS-D** (CI quality gates) — establish a green quality baseline first.
2. **WS-A** (DG-4 rollforward) — unblocks reading; rebase onto post-WS-D
   `main` to avoid lint-formatting noise in the diff.
3. **WS-B** (FAIR metadata) — single small commit, can ship same day as
   WS-A.
4. **WS-C** (README + examples) — depends on WS-A's notebook prose changes.
5. **WS-E** (r_4 formula) — independent; can interleave with WS-C.
6. **WS-F** (schema version) — depends on a steward decision (see §6).
7. **WS-I** (status label / link / repatriation) — L1 + M6 are quick
   wins; L5 lands only after the steward chooses Path L5-a or L5-b.
8. **WS-K** (Sphinx release string + naming convention amendment) — quick
   win; independent of doc-content changes.
9. **WS-La** (trivial hygiene: S3, S4, S9, S12, S14) — quick win.
10. **WS-G** (Sphinx warnings) — benefits from WS-A–C touching the same
    docstrings.
11. **WS-H** (notebook execution path) — independent; can land any time.
12. **WS-Lc** (packaging alignment: S5, S7, S11) — single PR, public-API
    sensitive.
13. **WS-Lb** (policy decisions: S6, S8, S10, S13) — four separate PRs
    after the four steward decisions land.
14. **WS-J** (hygiene: L6, L7-tracked, S14-doc) — last; trivial.

**Cross-workstream file collisions.** The following files appear in more
than one workstream; the sequencing above is designed to prevent rebase
storms, but spell out explicitly:

| File | Touched by | Rebase guidance |
|---|---|---|
| `reporting/benchmark_card.py` | WS-D (lint), WS-A (v0.1.1 refs) | Land WS-D first; rebase WS-A. |
| `benchmarks/numerical_tcl_extraction.py` | WS-D (lint), WS-A (v0.1.1 refs) | Same. |
| `cbg/tcl_recursion.py` | WS-A (D1 fixture comments), WS-G (Sphinx blank-line warnings) | Land WS-A first; WS-G picks up the post-WS-A docstring state. |
| `cbg/__init__.py` | WS-D (E402, version-guard ruff), WS-Lc (S5 `__all__`) | Land WS-D first; WS-Lc adds `__all__` on top of clean lint. |
| `examples/README.md` | WS-C (notebook listing), WS-H (execution path), WS-La S9 (mypy in tool list — wait, that's CONTRIBUTING.md, no collision) | Land WS-C first; WS-H amends. |
| `CONTRIBUTING.md` | WS-La (S9 mypy + S12 + S14), WS-H (S9 invocation) | Bundle the CONTRIBUTING.md edits in WS-La; WS-H references the same line. |
| `docs/validity_envelope.md` | WS-Lc (S11 wording), WS-I (DG-2 label L1) | Single edit in WS-Lc + WS-I; coordinate as one PR if landed near each other. |

After every content workstream merges, **rerun `ruff` / `black --check`
/ `mypy` / `pytest` / `sphinx-build`** as a check that the WS-D baseline
is preserved. Any regression triggers an immediate revert per §5.

WS-A, WS-B, WS-C, WS-D, WS-E, WS-F, WS-G, WS-H, WS-I, WS-J, WS-K, WS-La,
WS-Lc are each a single commit (or two if a mid-flight decision is
needed). WS-Lb is four PRs (one per S* item). Total: ~14–18 commits
across ~13 PRs.

## 5. Out of scope / declined

| ID | Reason |
|---|---|
| **A1** (Kimi FAIR review staleness) | Round 1 is now archived under `round-1_2026-05-04/`; archived reviews are point-in-time evidence, not edited retroactively. The new `reviews/README.md` index makes the staleness explicit, which is the appropriate mitigation. |
| **A2** (tag-vs-package SemVer drift) | Documented design decision in CHANGELOG; CHANGELOG line 13–18 already explains the convention. **Optional follow-up:** add a one-line clarifier to `pyproject.toml`'s `description` field. |
| **A3** (`dg-1-work-plan_v0.1.3.md` `status: active`) | Documented design decision per plan §8.1 ("no in-place transition of status"). |
| **A4** (logbook v0.1.2-pending vs CHANGELOG landed) | Logbook is append-only point-in-time; CHANGELOG reflects end-of-day. Both correct in their own frame. |
| Tutorial HTML rewrite (L4) | The tutorial is for theoretical orientation, not validation status. A staleness caveat in `README.md:90` (handled in WS-C) is sufficient; a full content refresh is a separate, larger project. |

## 6. Open decisions for the steward

Before the listed workstreams can land, the following decisions are
required:

1. **WS-B:** Bump `date-released` / `datePublished` to 2026-05-06?
   *(Recommended yes.)*
2. **WS-E:** Adopt the runner's `r_4(α²) = α² · ratio` definition in
   prose? *(Recommended yes.)*
3. **WS-F:** Propagate schema v0.1.3 across current surfaces, or revert
   `SCHEMA.md`'s frontmatter/changelog to v0.1.2? *(Recommended: propagate.
   The v0.1.3 changelog entry already exists at SCHEMA.md:387; the bump
   is intentional and substantive.)*
4. **WS-I L5:** Are summary JSONs (`benchmarks/results/DG-N_summary.json`)
   mutable indexes or immutable verdict artefacts? *(Recommended: treat
   as immutable; route the DG-1 repatriation note via a new
   `benchmarks/results/README.md` index file — Path L5-b.)*
5. **WS-K (S1):** Rename `B[45]-conv-registry` cards for filename
   consistency, or amend `SCHEMA.md` instead? *(Recommended: amend
   `SCHEMA.md` — draft text supplied in WS-K. Renaming touches ≥10 files
   and creates supersedure-record ambiguity.)*
6. **WS-Lb (S6):** SPDX-header policy — add to all source files, or
   document a decision not to? *(Recommended: add
   `# SPDX-License-Identifier: MIT` headers; small one-time cost, large
   clarity payoff for downstream re-users.)*
7. **WS-Lb (S8):** Python 3.13 support — claim or not? *(Recommended:
   add a 3.13 row to the CI matrix first; promote to a `pyproject.toml`
   classifier only after a green run.)*
8. **WS-Lb (S10):** Stub model files — mark scope-definition via Path
   S10-a (callable stubs that raise `ScopeDefinitionNotRunnableError`)
   or Path S10-b (docstring-only)? *(Recommended: Path S10-a — explicit
   stub APIs that raise when called. Do **not** raise on import; that
   would break Sphinx autodoc, `from models import *`, and any CI step
   that imports the `models` package as a whole.)*

## 7. Rollback policy

Each workstream's default failure response is **revert + fresh
workstream**, not fix-forward. This mirrors the project's supersedure
discipline:

- If a regression surfaces in CI, a downstream consumer flags a broken
  link, or the validity-envelope re-read shows that a workstream's edit
  contradicted authoritative state: **revert the merge commit on
  `main`**, then open a new branch / PR with a corrected scope.
- Do not layer a "fix-up" commit on top of a faulty workstream. A clean
  revert + re-do preserves git-blame traceability against the source
  review evidence.
- Verdict-adjacent workstreams (WS-A, WS-B, WS-E) have an explicit
  regression test in their acceptance criteria. If the regression test
  fails post-merge, revert immediately; do not branch a hotfix on
  top.
- Logbook discipline: a reverted workstream is not "removed from
  history". Add a one-line entry to `logbook/` recording the revert
  with timestamp and reason, so the audit trail captures the
  fix-revert-redo cycle.

The exception to this rule is **WS-D** (CI quality gates). Because
WS-D's job is to make tooling pass, "fix-forward" is the natural mode:
if a follow-up tool diagnostic surfaces, fix it on the same branch
rather than reverting the lint baseline.

## 8. Acceptance for the package as a whole

This work package is **complete** when:

- All HIGH issues (H1–H4) are closed (commit hashes recorded against
  each in the issue table above, in a follow-up edit to this file).
- All MEDIUM issues (M0–M7) are closed or explicitly deferred with a
  written rationale.
- All structural issues (S1–S14) and LOW issues (L1–L7) are either
  closed or recorded as deferred under WS-La / WS-Lb / WS-Lc / WS-J / §5.
- Round-1 / round-2 archived items (A1–A4) carry their no-action
  dispositions per §5.
- WS-D's green baseline holds at HEAD: `ruff` / `black --check` /
  `mypy` / `pytest` / `sphinx-build` all exit 0.
- A short note is appended to `CHANGELOG.md` under `[Unreleased]`
  referencing this work package and the resolved issues.

Once those conditions hold, this file's `status:` is bumped to
`closed` and a v0.2.0 of the work package is opened only if a new round
of reviews surfaces fresh issues.

---

*Drafted from review evidence; no actions taken. The steward triages,
sequences, and executes.*

# Consistency Review of `oqs-cbg-pipeline`

**Date:** 2026-05-08
**Reviewer:** Claude Code (read-only consistency sweep)
**Scope:** Cross-document consistency of metadata, DG-status claims, version
references, formula expressions, benchmark-card / result-JSON pairing, and
internal links. **No actions taken** — flags only.
**Authoritative reference for DG status:** [`docs/validity_envelope.md`](../docs/validity_envelope.md)
(Last updated 2026-05-06: DG-1 PASS, DG-2 structural sub-claims PASS,
DG-3 RUNNER-COMPLETE / no PASS, DG-4 PASS at D1 v0.1.2, DG-5 SCOPED).

---

## Summary

Twelve issues flagged. Severity is relative to the project's own discipline
(cards-first; documentation rolled forward atomically with verdicts). Nothing
here changes any verdict; everything is in human-facing copy or stale
metadata that has not been rolled forward to match `validity_envelope.md`.

| # | Severity | Area | One-line summary |
|---|---|---|---|
| 1 | **HIGH** | FAIR metadata | `.zenodo.json`, `codemeta.json`, `CITATION.cff` still describe status as pre-DG-4: omit DG-4 PASS entirely. |
| 2 | **HIGH** | DG-4 verdict artefact | [`benchmarks/results/DG-4_summary.json`](../benchmarks/results/DG-4_summary.json) still cites `card_version: "v0.1.1"` after the supersedure to v0.1.2. |
| 3 | **HIGH** | README accuracy | [`README.md:83`](../README.md) says "Two runnable Jupyter notebooks" but `examples/` ships **four** (`dg1_walkthrough`, `dg2_structural`, `dg3_cross_method`, `dg4_walkthrough`). |
| 4 | **MEDIUM** | Formula consistency | The DG-4 metric `r_4` is written **with α² prefactor** in the runner code and `examples/README.md`, but **without α²** in nearly every prose document and in three places inside the D1 v0.1.2 card itself. |
| 5 | **MEDIUM** | Memory index | `MEMORY.md:2` links `feedback_cards_first_discipline.md` at repo root; that file does not exist at repo root (it lives only in the user-level memory directory). |
| 6 | **MEDIUM** | Card naming | `README.md:86` and `examples/README.md:10` refer to "Card B4" and "Card B5"; the actual files and the validity envelope name them `B4-conv-registry` / `B5-conv-registry`. |
| 7 | **LOW** | DG-2 row caption | `README.md:114` shows DG-2 status as "STRUCTURAL SUB-CLAIMS PASS …; literal K_2-K_4 fourth-order recursion pending"; `index.html:176` uses "PARTIAL: structural sub-claims PASS …"; `docs-site/index.md:32` uses "**PARTIAL**". The validity envelope itself uses "**PARTIAL**". Wording converges on the same fact but the label differs. |
| 8 | **LOW** | DG-1 row & A4 | `validity_envelope.md:19` lists Cards A1, A3, A4 but the DG-1 evidence statement names Entries 1.B.1, 1.B.2, 3.B.1, 3.B.2, 4.B.1; `examples/README.md:9` lists only "A1, A3" for the DG-1 demo notebook — no mention of A4 or σ_x thermal. |
| 9 | **LOW** | CITATION.cff release date | `CITATION.cff:21` `date-released: 2026-05-04`; `codemeta.json:7` `datePublished: "2026-05-04"`. Last verdict landed 2026-05-06 (DG-4 v0.1.2). Either roll forward or document why the release-date is intentionally pinned to v0.2.0/v0.3.0.dev0. |
| 10 | **LOW** | tutorial version | `cbg-tutorial-for-phd-students_v0.2.html` is dated by filename only; pre-DG-2/DG-4. README links to it without a "may be stale" caveat. Consider noting in `README.md:90`. |
| 11 | **LOW** | DG-1_summary.json missing card-list completeness | [`benchmarks/results/DG-1_summary.json`](../benchmarks/results/DG-1_summary.json) lists A1/A3/A4 cards but has no `ledger_anchor` cross-link to the structural-identity sub-claims that were repatriated to DG-2 (DG-1 row in validity_envelope explicitly notes this repatriation). The summary JSON is silent about repatriated entries. |
| 12 | **LOW** | docs-site footer / paths | `docs-site/index.md:64` links Hayden–Sorce transcription **v0.1.1**; the directory contains both v0.1.0 and v0.1.1 — confirmed correct. (Flagging only that v0.1.0 is retained alongside; status of v0.1.0 is unmarked.) |

All other cross-references checked (logbook links, benchmark-card / result-JSON
pairings, paper DOIs, sail v0.4 vs v0.5 references, package version
`0.3.0.dev0` consistency in `pyproject.toml` / `CITATION.cff` / `codemeta.json`
/ `.zenodo.json` / `cbg.__init__`, README repository-layout vs `ls`,
`tests/test_imports.py` module names, and `cbg.__version__` exposure)
are **internally consistent**.

---

## Detailed findings

### #1 — FAIR metadata staleness (omit DG-4 PASS entirely)

The three machine-readable FAIR files all describe the project's status as
"DG-1 PASS; DG-2 structural sub-claims PASS; literal fourth-order K_2-K_4
recursive computation remains pending" with **no mention of DG-4**, and
`.zenodo.json` further says DG-4 is pending:

- [`.zenodo.json:3`](../.zenodo.json#L3) — description omits DG-4.
- [`.zenodo.json:40`](../.zenodo.json#L40) — `"notes"` explicitly states:
  *"DG-3 cross-method validation, DG-4 failure-envelope work, and DG-5
  thermodynamic discriminant remain pending."* This is wrong for DG-4 as of
  2026-05-06.
- [`codemeta.json:5`](../codemeta.json#L5) — description omits DG-4 PASS.
- [`CITATION.cff:7-13`](../CITATION.cff#L7-L13) — abstract omits DG-4 PASS.

`docs/validity_envelope.md` is the authoritative source and was updated
2026-05-06 to record DG-4 PASS. The three FAIR files appear to have been
last refreshed at the 2026-05-04 DG-2 milestone and were not rolled forward
when DG-4 PASSed.

### #2 — DG-4_summary.json still points at v0.1.1

[`benchmarks/results/DG-4_summary.json:13-16`](../benchmarks/results/DG-4_summary.json#L13-L16):

```
"card_version": "v0.1.1",
"card_path": "benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.1.yaml",
"verdict": "PASS",
"evidence": "benchmarks/results/D1_failure-envelope-convergence_v0.1.1_result.json",
```

The validity envelope, CHANGELOG, README, index.html, and
`docs/benchmark_protocol.md` all record v0.1.2 as the live verdict and
v0.1.1 as superseded. `D1_failure-envelope-convergence_v0.1.2_result.json`
exists in the same directory. The summary JSON's `card_version` field is
stale.

`limitations[1]` in the same file (line 24) also says
*"upper_cutoff_factor perturbations are not operational in the current
exact_finite_env Path B extraction"* — but the v0.1.2 supersedure repair
commit `a908cd6` made `upper_cutoff_factor` operational via
`omega_max_factor` threading. The limitation as stated is true only of v0.1.1.

### #3 — README undercounts notebook examples

[`README.md:83-86`](../README.md#L83-L86):

> *Two runnable Jupyter notebooks demonstrate the passed Decision Gate
> verdicts end-to-end:*
> - `examples/dg1_walkthrough.ipynb` …
> - `examples/dg2_structural.ipynb` …

But `examples/` contains four notebooks (also `dg3_cross_method.ipynb`,
`dg4_walkthrough.ipynb`), and `examples/README.md`, `index.html`, and the
`api/examples/*.html` build all advertise four. README's mini-listing is
stale.

Additionally, `README.md:86` labels the DG-2 demo as "DG-2 structural sub-claims
PASS (Cards B3, B4)" — see #6 for the B4 vs B4-conv-registry naming issue,
and note that `examples/README.md:10` lists the same notebook as exercising
"B3, B4" with the displacement profile `delta-omega_S` (the README only
says "one Council-cleared registry profile", which is fine, but the card
names should match).

### #4 — `r_4` formula written two different ways

The actual quantity computed by the runner is

```
r_4(α²) = α² · (⟨‖L_4^dis‖⟩_t / ⟨‖L_2^dis‖⟩_t)
```

(see [`reporting/benchmark_card.py:1421`](../reporting/benchmark_card.py#L1421)
and `_scaled_ratio` at line 1746).

But the **prose-form definition** in most documents drops the `α²` factor:

- [`docs/validity_envelope.md:22`](../docs/validity_envelope.md#L22) →
  `r_4 = <‖L_4^dis‖>_t / <‖L_2^dis‖>_t` (no α²)
- [`docs/benchmark_protocol.md:98`](../docs/benchmark_protocol.md#L98) →
  same, no α²
- [`README.md:116`](../README.md#L116) → no α²
- [`CHANGELOG.md:26-27`](../CHANGELOG.md#L26-L27) → no α²
- [`index.html:152`](../index.html) → no α²
- [`docs-site/index.md:34`](../docs-site/index.md#L34) → no α²
- [`benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.2.yaml:110,155,186`](../benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.2.yaml) → no α²

Only [`examples/README.md:12`](../examples/README.md#L12) writes
`r_4 = α² ⋅ ⟨‖L_4^dis‖⟩_t / ⟨‖L_2^dis‖⟩_t`, matching the runner.

The numbers (max baseline ≈ 47.42, min perturbed ≈ 41.47) are consistent
across all documents because at α = 1 the prefactor is 1, but the formula
labels disagree. The card YAML even disagrees with itself: the headline
formula at lines 110/155/186 omits α², while line 277 says
`r_4 = coupling_strength * coefficient_ratio`. Recommendation: pick one
definition (the runner's, with α²) and roll forward; or relabel the prose
quantity as "coefficient ratio" and reserve `r_4` for the runner's scaled
quantity.

### #5 — MEMORY.md links a file that isn't at repo root

[`MEMORY.md:2`](../MEMORY.md#L2):

```
- [Cards-first discipline](feedback_cards_first_discipline.md) — …
```

There is no `feedback_cards_first_discipline.md` in `/Users/uwarring/Documents/GitHub/oqs-cbg-pipeline/`.
The file exists in the user-level memory directory
(`~/.claude/projects/-Users-uwarring-…/memory/feedback_cards_first_discipline.md`)
but the relative link from MEMORY.md will not resolve.

`MEMORY.md:1` links `project_dg2_blockers.md` correctly — that file is at repo root.

### #6 — Card naming "B4" / "B5" vs "B4-conv-registry" / "B5-conv-registry"

`docs/validity_envelope.md` and `index.html` consistently use the full
filenames `B4-conv-registry` and `B5-conv-registry`. But:

- [`README.md:86`](../README.md#L86) → "Cards B3, B4"
- [`examples/README.md:10`](../examples/README.md#L10) → "B3 (cross-basis identity), B4 (displaced bath, profile `delta-omega_S`)"
- [`README.md:114-116`](../README.md#L114-L116) DG status table → consistent with full names? Check: the DG-2 row says only "**STRUCTURAL SUB-CLAIMS PASS**", no card names.

The B4/B5 short names are unambiguous (no other B4 / B5 exists), but
inconsistent with the repository's own filename convention.

### #7 — DG-2 status label varies

Three different wordings of the same status:

| File:line | Wording |
|---|---|
| `validity_envelope.md:20` | "**PARTIAL: structural sub-claims PASS; K_2-K_4 recursion pending**" |
| `README.md:114` | "**STRUCTURAL SUB-CLAIMS PASS** (2026-05-04); literal K_2-K_4 fourth-order recursion pending" |
| `index.html:176` | "PARTIAL: structural sub-claims PASS; K_2-K_4 recursion pending" |
| `docs-site/index.md:32` | "**PARTIAL** — structural sub-claims PASS …" |

Same fact, three labels. Validity envelope is authoritative; the others
should align (probably on "PARTIAL").

### #8 — DG-1 demo notebook lists only A1/A3, not A4

`examples/README.md:9` says the dg1_walkthrough demo exercises
"A1 (closed-form K), A3 (pure-dephasing thermal)". The DG-1 verdict (and
`DG-1_summary.json`) anchors on **three** cards: A1, A3, A4. README.md:85
makes the same omission. The notebook itself was not opened in this review;
flag is on the prose listing only.

### #9 — Release date pinned to 2026-05-04

`CITATION.cff:21` `date-released: 2026-05-04`; `codemeta.json:7`
`datePublished: "2026-05-04"`. Both predate the DG-4 PASS commit `6f88787`
on 2026-05-06. If these dates are intended to track the
`v0.3.0.dev0`/`v0.2.0` release event rather than the latest verdict, this
is fine but undocumented; if they're meant to track the latest published
verdict, they're stale.

### #10 — Tutorial vintage not flagged

`README.md:90` links `cbg-tutorial-for-phd-students_v0.2.html` with no
caveat. The file is dated 2026-04-30 (per `ls`) — pre-DG-2-PASS and
pre-DG-4-PASS. Readers may assume tutorial content reflects current DG
status. Not a hard inconsistency; flag for awareness.

### #11 — DG-1_summary.json silent about repatriated sub-claims

[`benchmarks/results/DG-1_summary.json`](../benchmarks/results/DG-1_summary.json)
lists `cards: [A1, A3, A4]` with `verdict: PASS`. The validity envelope's
DG-1 row explicitly notes that **Entries 1.B.3, 3.B.3, 4.B.2 were
repatriated from DG-1 to DG-2 and PASSed under the cleared registry**.
The summary JSON does not record this repatriation, so a downstream
consumer reading only `DG-1_summary.json` would not know about the
operationalisability carve-out. Compare to `DG-4_summary.json`, which has
a `limitations` field — `DG-1_summary.json` has no analogous
"repatriations" or "carve_outs" block.

### #12 — Hayden–Sorce transcription v0.1.0 retained alongside v0.1.1

`transcriptions/` contains both `hayden-sorce-2022_pseudokraus_v0.1.0.md`
and `hayden-sorce-2022_pseudokraus_v0.1.1.md`. `docs-site/index.md:64`
correctly links v0.1.1. v0.1.0 is unreferenced; not opened in this review,
status of v0.1.0 within the file (e.g. an internal "superseded" header)
not verified. Mild flag for symmetry with the cards' supersedure
discipline.

---

## Notes on what is consistent

For audit-trail completeness, the following were checked and found to be
internally consistent:

- All logbook entries linked from `docs/validity_envelope.md`,
  `CHANGELOG.md`, `README.md`, and `index.html` resolve to existing files
  in `logbook/`.
- All benchmark-card files referenced as "live verdict" by the validity
  envelope have a matching `_result.json` in `benchmarks/results/`.
- Superseded card YAMLs (`A1/A3/A4_v0.1.0`, `B5-conv-registry_v0.1.0`,
  `D1_v0.1.0`, `D1_v0.1.1`) all carry `status: "superseded"`.
  Frozen-awaiting-run cards (C1, C2) carry `status: "frozen-awaiting-run"`.
  E1 carries `status: "scope-definition"`.
- Paper DOIs (10.1103/n5nl-gn1y, 10.1103/9j8d-jxgd) match across
  README.md, CITATION.cff, codemeta.json, .zenodo.json, and `cbg/__init__.py`.
- Package version `0.3.0.dev0` matches across `pyproject.toml`,
  `CITATION.cff`, `codemeta.json`, `.zenodo.json`, and is consumed by
  `cbg/__init__.py` via `importlib.metadata.version("oqs-cbg-pipeline")`.
- `pyproject.toml` package list matches actual top-level packages
  (`cbg`, `models`, `numerical`, `benchmarks`, `reporting`).
- README "Repository layout" tree (lines 135–150) lists every actual
  top-level dir in the repo (no extras, no omissions of dirs the README
  describes as part of the project).
- `tests/test_imports.py` and `conftest.py` only reference modules that
  exist in `cbg/`, `models/`, `numerical/`, `benchmarks/`, `reporting/`.
- Sail v0.4 is retained as superseded per `sail/README.md:10`; v0.5 is
  the active document; no document outside `sail/` cites v0.4 as active.

---

*End of consistency review. No files modified.*

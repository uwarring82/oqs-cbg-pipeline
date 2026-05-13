# `reviews/`

External and automated review reports of `oqs-cbg-pipeline`. Each review is a
**point-in-time snapshot** of the repository's state on the reviewer's date —
they are not living documents and are not updated retroactively as the repo
moves on. The authoritative live state of the repository remains
[`docs/validity_envelope.md`](../docs/validity_envelope.md).

## Layout

Reviews are filed under `round-N_YYYY-MM-DD/` directories, where `N` is the
round ordinal and the date is the **reviewer's date** (which may differ from
the file's git-add date for reviews authored on one day and filed on
another). Within each round, files are named `<reviewer>_<scope>.md`.

```
reviews/
├── round-1_2026-05-04/
│   └── kimi_fair-review.md
├── round-2_2026-05-06/
│   └── gemini_inconsistency-flags.md
├── round-3_2026-05-08/
│   ├── claude_consistency-review.md
│   ├── codex_consistency-audit.md
│   └── anonymous_structural-review.md
└── work-package_review-resolution_v0.1.0.md
```

## Index

| Round | Date | Reviewer | Scope | Notes |
|---|---|---|---|---|
| 1 | 2026-05-04 (initial; updates through 2026-05-05) | Kimi Code CLI | FAIR compliance, governance, software-engineering hygiene | Tracks `0df8a1e` post-DG-2 metadata refresh and several follow-up commits. Now stale on test counts and CI-quality status — see Round 3 / Codex `:170-181`. |
| 2 | 2026-05-06 | Gemini Code Assist | Documentation drift, state contradictions, file inconsistencies | Authored on the day of the DG-4 v0.1.1 supersedure; flags the same stale `DG-4_summary.json` later re-flagged in Round 3. |
| 3 | 2026-05-08 | Claude Code (Opus 4.7) | Cross-document consistency sweep (metadata, DG status, formula, links) | 12 issues; high overlap with Codex audit. |
| 3 | 2026-05-08 | Codex | Repository-wide audit (CI quality gates, FAIR metadata, examples, schema, doc warnings) | Includes verification snapshot: pytest 471 passed; ruff/black/mypy currently fail on CI scope. |
| 3 | 2026-05-08 | anonymous (by reviewer request; steward-confirmed 2026-05-13) | Structural / code-level sweep (build artefacts, naming conventions, packaging hygiene, Sphinx release string, stub modules, license headers) | 18 issues, mostly LOW. Self-describes as a complement to the Claude consistency review. |

## Attribution note

The four named reviews (Kimi, Gemini, Claude, Codex) carry self-identifying
attribution in their headers. The Round-3 file `anonymous_structural-review.md`
is **anonymous by reviewer request** (steward-confirmed 2026-05-13); a
one-line `Attribution:` header in the file records this intent. Its findings
are treated as evidence-of-equal-weight to the named reviews.

## Resolution tracking

Issues raised across the three rounds are consolidated and triaged in
[`work-package_review-resolution_v0.1.0.md`](work-package_review-resolution_v0.1.0.md).
That work package is the live planning artifact; this directory's per-round
files are the immutable evidence. Resolution status is tracked in the work
package, not edited back into the original review files.

## What goes here vs. elsewhere

- **`reviews/`** — external assessments (automated agent reviews, reviewer
  reports, audit findings). Read-only after authoring.
- **`plans/`** — steward-authored work plans for Decision Gates. Versioned;
  the active plan is the highest-numbered file in each `dg-N-work-plan_*.md`
  series.
- **`logbook/`** — append-only repository event log (verdicts, supersedures,
  card freezes, deliberation outcomes).
- **`docs/`** — protective scaffolding (validity envelope, benchmark protocol,
  endorsement marker, do-not-cite-as, stewardship-conflict). Updated atomically
  with verdicts.

The review-resolution work package straddles `reviews/` and `plans/` in
spirit: it consolidates external findings (inputs from `reviews/`) into a
steward-actionable plan (output similar to `plans/`). It lives here because
its primary input is review evidence; if it grows into a multi-phase
implementation plan, it can be promoted to `plans/`.

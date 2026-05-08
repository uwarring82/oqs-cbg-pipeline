# Repository Inconsistency Review

**Date:** 2026-05-06 (Contextual)  
**Reviewer:** Gemini Code Assist  
**Focus:** Documentation drift, state contradictions, and file inconsistencies across the repository.

## 1. Stale DG-4 Summary JSON
**Files involved:** `benchmarks/results/DG-4_summary.json`, `CHANGELOG.md`, `logbook/2026-05-06_dg-4-pass-path-b-superseded.md`
* **Issue:** `DG-4_summary.json` still records an active `PASS` for `card_id: D1`, `card_version: v0.1.1`. However, the logbook explicitly downgraded and superseded this verdict due to two HIGH-severity defects (incorrect Path B picture extraction and trivially satisfied PASS predicates). 
* **Impact:** The summary JSON is aggregating a defective, superseded run. While `CHANGELOG.md` correctly reports that a repaired `v0.1.2` was subsequently passed on the same day, `DG-4_summary.json` has not been rolled forward to point to the `v0.1.2` evidence.

## 2. Internal Contradictions in the FAIR Review
**File involved:** `reviews/FAIR_review_2026-05-04.md`
* **Issue A (Test Counts):** The review states `368 tests passed` in the "DG-3 Phase C update" changelog section, but still claims `323 tests pass` in the "Coding-readiness pass" and bottom-line "What's solid" conclusion. The summary stats were not updated to reflect the new tests.
* **Issue B (Implementation Status):** Under the "DG-3 Phase C" section, `exact_finite_env.py` and `qutip_reference.py` are explicitly marked as "✅ Implemented". However, later in the document under "Still open — Low / Deferred", it states: "Complete benchmark reference implementations (`exact_finite_env.py`, `qutip_reference.py`)".
* **Issue C (CI Enforcement):** The review explicitly lists "Enforce `black` / `ruff` / `mypy` in CI" as "✅ Done (commit 821cfee)". However, in the earlier "Reusability" and "Interoperability" sections, it still flags "No CI enforcement of code quality" as an active failure. 
* **Impact:** The review document represents a living state but its structural sections were not fully reconciled after the steward's commit `0df8a1e` and subsequent updates.

## 3. Semantic Versioning Drift
**Files involved:** `CHANGELOG.md`, `logbook/2026-05-06_dg-4-pass-path-b-superseded.md`
* **Issue:** As accurately self-reported by the steward in the logbook, there is a divergence between the Git tag strategy and the Python package versioning. Git tags (`v0.2.0`, `v0.5.0`) are moving rapidly to anchor Decision Gate immutability, while the package metadata in `pyproject.toml` and `CITATION.cff` remains anchored at `0.3.0.dev0`.
* **Impact:** This is technically allowed per the repository's internal rules (tags anchor *verdicts*, not *releases*), but it creates a cognitive inconsistency for any external user relying on `CHANGELOG.md` SemVer headers vs the installable package version.

## 4. `dg-1-work-plan` Sub-Claim Consistency
**Files involved:** `plans/dg-1-work-plan_v0.1.3.md`, `plans/dg-1-work-plan_v0.1.4.md`
* **Issue:** Plan `v0.1.3` introduces an "Operationalisability carve-out" to defer `Entry 1.B.3` to DG-2. Plan `v0.1.4` extends this to `Entry 3.B.3` and `4.B.2` due to displacement-mode convention gaps. The files correctly use `superseded_by:` to maintain the chain of custody. 
* **Note:** The `status:` field remains `active` on the superseded `v0.1.3` plan rather than being changed to `superseded`. The steward documented this as a deliberate design choice (Section 8.1: "There is no in-place transition of status"), but it represents an architectural quirk where a file's active front-matter metadata intentionally contradicts its superseded reality.

## 5. Changelog / Logbook Alignment on v0.5.0 Downgrade
**Files involved:** `CHANGELOG.md`, `logbook/2026-05-06_dg-4-pass-path-b-superseded.md`
* **Issue:** The `CHANGELOG.md` efficiently merges the story of the v0.5.0 downgrade and the subsequent v0.1.2 fix into the `[Unreleased]` section. However, the logbook entry `2026-05-06_dg-4-pass-path-b-superseded.md` states: *"v0.1.2 supersedure pending Path B repair"*. 
* **Impact:** This is an artifact of the rapid same-day commits. The logbook entry acts as a point-in-time snapshot where the fix was "pending", whereas the Changelog reflects the end-of-day state where the fix was "landed". While historically accurate to the hour, it reads as a slight contradiction to a future auditor.
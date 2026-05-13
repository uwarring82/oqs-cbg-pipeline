---
artifact_id: cbg-companion-sec-iv-l4-n4-small-grid-verification-card
version: v0.1.1
date: 2026-05-13
type: verification-card / pre-code-oracle
status: frozen
supersedes: colla-breuer-gasbarri-2025_companion-sec-iv_l4_n4-small-grid-verification-card_v0.1.0.md
parent_transcription: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md
target_implementation: cbg/tcl_recursion.py — Phase B n=4 thermal Gaussian D̄ evaluator (commit `becccf9`)
anchor_plan: plans/dg-4-work-plan_v0.1.5.md §4 Phase B
release_gate: Companion §10 implementation reminder, item (b) — already met by commit `becccf9`
reviewer: Ulrich Warring
review_date: 2026-05-13
review_state: frozen-errata (clarifies §5.3 k=2 cross-grid claim wording)
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Phase B pre-code verification card — n=4 small-grid oracle for Companion Eqs. (69)–(73) (v0.1.1, errata)

> **Status: frozen (2026-05-13).** This v0.1.1 supersedes v0.1.0 as an
> **errata** revision to clarify §5.3 bullet 2's wording about the
> k=2 cross-grid relationship. v0.1.0's wording — "Mismatch between
> the two grids at k=2 would signal a sign-pattern error in
> Eq. (71)" — is potentially misleading because it reads as if it
> means **numerical** mismatch between the two grids' computed values.
> The intended meaning is **structural-form** mismatch (a different
> polynomial in `C(·, ·)` for one or both grids). The numerical values
> on Grid α and Grid β are NOT expected to be equal — they are complex
> conjugates of each other (for thermal Hermitian B on τ ↔ s-mirrored
> grids).
>
> v0.1.1 carries forward ALL other v0.1.0 content unchanged: the §2
> bath fixture, the §3 grids, the §4 substitution rules, the §5
> by-hand closed forms (the algebraic identities themselves), §6 API
> contract, §7 independent oracle, §8 secondary diagnostic, §9
> acceptance criterion, §10 implementation hand-off, §11 out-of-scope
> reminders, §12 steward freeze. Only §5.3 bullet 2's wording is
> updated below.

## 0. Provenance and role

This v0.1.1 errata revision consumes:

- the v0.1.0 small-grid card (commit `ae20806`) — the parent whose
  §5.3 bullet 2 wording is clarified by this revision;
- the v0.1.0 Phase B implementation experiment (commit `becccf9`)
  which produced the test `test_k2_closed_form_identical_across_grids`
  in `tests/test_n4_small_grid_verification.py`. The test correctly
  interprets v0.1.0 §5.3 bullet 2 as a structural-form claim and
  verifies each grid's closed form against its own grid's evaluation
  — but the v0.1.0 wording itself reads as a numerical-equality claim
  in isolation, which is at best misleading.

## 1. Purpose and scope

### 1.1 What this card does

- Carries forward ALL the v0.1.0 §2–§12 content unchanged.
- Replaces v0.1.0 §5.3 bullet 2's wording with a clearer statement
  that distinguishes structural-form identity (which holds) from
  numerical-value identity (which does NOT hold, by τ ↔ s mirror).

### 1.2 What this card does not do

- It does not change the §3 grids.
- It does not change the §5 by-hand closed forms.
- It does not change the §9 acceptance criterion (atol = rtol = 1e-10
  for primary vs independent oracle).
- It does not require any change to the implemented test (commit
  `becccf9` already interprets the §5.3 bullet 2 correctly per the
  v0.1.1 clarified wording).

## 2 – §5.2 (unchanged from v0.1.0)

Refer to v0.1.0 §2 (bath fixture: thermal ohmic α=0.1, ω_c=1.0,
T=1.0), §3 (two grids: Grid α with τ_1=t, Grid β with s_1=t), §4
(substitution rules: row-2.3 swap, Eq. (22) boundary delta, thermal
Gaussian Wick), §5 (by-hand closed forms for all 5 × 2 = 10
(case, grid) pairs), §5.1 (Grid α table), §5.2 (Grid β table).

## §5.3 Consistency checks built into the §5 closed forms (UPDATED wording)

v0.1.0 §5.3 had three bullets. Bullet 2 is updated in v0.1.1:

### v0.1.0 §5.3 bullet 2 — original wording (superseded)

> - `k = 2` produces the **same** survivor form at both grids
>   (`C(s_2, τ_1)·C(s_1, τ_2)`) despite different boundary-delta paths.
>   This is a coincidence of the symmetric Eq. (71) subtraction structure
>   at `k = 2`, not a generic τ ↔ s symmetry. Mismatch between the two
>   grids at `k = 2` would signal a sign-pattern error in Eq. (71).

### v0.1.1 §5.3 bullet 2 — clarified wording

> - `k = 2` produces the **same algebraic survivor form** at both
>   grids — namely the polynomial `C(s_2, τ_1)·C(s_1, τ_2)` in
>   `C(·, ·)` — despite different boundary-delta paths. This is a
>   coincidence of the symmetric Eq. (71) subtraction structure at
>   `k = 2`, not a generic τ ↔ s symmetry.
>
>   **Structural-form vs numerical-value distinction.** The two grids
>   have τ ↔ s-mirrored time tuples: Grid α has (τ_1, τ_2, s_1, s_2)
>   = (1.0, 0.7, 0.9, 0.6), and Grid β has the (τ_1, τ_2, s_1, s_2)
>   = (0.9, 0.6, 1.0, 0.7) (mirror image). Substituting these into
>   the shared survivor form `C(s_2, τ_1)·C(s_1, τ_2)` produces
>   complex-conjugate numerical values on the two grids (for thermal
>   Hermitian B, since `C(a, b)* = C(b, a)` and the (a, b) ↔ (b, a)
>   swap between grids implies complex conjugation).
>
>   **What constitutes "mismatch" at k=2.** A **numerical** mismatch
>   between the two grids is EXPECTED (the values are conjugates,
>   not equal). A **structural-form** mismatch — i.e., one grid's
>   primary oracle producing the survivor `C(s_2, τ_1)·C(s_1, τ_2)`
>   while the other grid's primary oracle produces a different
>   polynomial in `C(·, ·)` (e.g., a different Wick pairing
>   combination or a sign-flipped subtraction) — WOULD signal a
>   sign-pattern error in Eq. (71). The implemented test
>   `test_k2_closed_form_identical_across_grids` correctly verifies
>   each grid's primary oracle against its own grid's instance of
>   the shared survivor form: if either grid's evaluation diverges
>   from `C(s_2, τ_1)·C(s_1, τ_2)`, the test fails.

The v0.1.1 bullet 1 (k=0/k=4 trivially-zero cases must traverse the
full code path) and bullet 3 (k=0 ↔ k=4 and k=1 ↔ k=3 mirror-pair
algebraic structure) are unchanged from v0.1.0.

## §6 – §12 (unchanged from v0.1.0)

Refer to v0.1.0 §6 (primary oracle API contract), §7 (independent
oracle), §8 (secondary diagnostic), §9 (acceptance criterion at
atol = rtol = 1e-10), §10 (implementation hand-off), §11
(out-of-scope reminders), §12 (steward freeze sign-off).

## 7. Steward freeze sign-off

> I have drafted v0.1.1 as an errata revision to v0.1.0 to clarify
> §5.3 bullet 2's wording about the k=2 cross-grid relationship.
> The intended meaning was always **structural-form** identity (same
> polynomial in `C(·, ·)`) with **numerical-value** complex
> conjugation across the τ ↔ s-mirrored grids; v0.1.0's terser
> wording is potentially misleading when read in isolation. v0.1.1
> carries forward ALL other v0.1.0 content unchanged, including the
> §5 closed-form table, the §9 acceptance criterion, and the §10
> implementation hand-off. The implemented test (commit `becccf9`)
> already correctly interprets §5.3 bullet 2 per the v0.1.1 clarified
> wording; the test docstring was expanded for the same clarity in
> commit `3e50e94`. Per cards-first discipline, this file is
> content-immutable post-commit; v0.1.0 is retained as the
> predecessor.
>
> Reviewer: Ulrich Warring  Date: 2026-05-13
>
> Version at freeze: v0.1.1 (release state: frozen-errata)

## Appendix — change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1.0 | 2026-05-13 | Initial draft and freeze. (Commit `ae20806`.) | Local steward draft. |
| v0.1.1 | 2026-05-13 | **Errata supersedes v0.1.0.** Clarified §5.3 bullet 2 wording: distinguishes structural-form identity (`C(s_2, τ_1)·C(s_1, τ_2)` polynomial; holds on both grids) from numerical-value identity (does NOT hold; the two grids' values are complex conjugates for thermal Hermitian B). No other changes; §2–§4, §5 (incl. §5.1/§5.2 closed-form tables), §5.3 bullets 1 and 3, §6–§12 of v0.1.0 carried forward verbatim. The implemented test `test_k2_closed_form_identical_across_grids` (commit `becccf9`, with the docstring expanded in commit `3e50e94`) already interprets §5.3 bullet 2 per this v0.1.1 clarified wording. | Local steward errata revision. |

*Verification card version: v0.1.1 (frozen 2026-05-13, errata).
Supersedes v0.1.0 to clarify §5.3 bullet 2's structural-form vs
numerical-value wording. CC-BY-4.0.*

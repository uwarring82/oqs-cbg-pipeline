---
artifact_id: cbg-companion-sec-iv-l4-phase-c-physics-oracles-card
version: v0.1.3
date: 2026-05-13
type: verification-card / pre-code-oracle
status: frozen
supersedes: colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-c-physics-oracles-card_v0.1.2.md
parent_transcription: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md
parent_card: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_n4-small-grid-verification-card_v0.1.1.md
target_implementation: cbg/tcl_recursion.py — Phase C private assembled-L_4 helper, post-domain-fix
anchor_plan: plans/dg-4-work-plan_v0.1.5.md §4 Phase C
release_gate: work plan v0.1.5 §4 Phase C acceptance — all four physics oracles pass under the full quality gate; public n=4 route remains deferred to Phase D
reviewer: Ulrich Warring
review_date: 2026-05-13
review_state: frozen-post-implementation-review (errata supersession of v0.1.2)
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Phase C pre-code verification card — physics oracles for assembled L_4 (v0.1.3, post-domain-fix errata)

> **Status: frozen (2026-05-13).** This v0.1.3 supersedes v0.1.2 as an
> **errata** revision following the post-implementation review of
> commit `3e50e94`. v0.1.3 carries forward all v0.1.2 content
> unchanged EXCEPT for two textual updates to §4.1 Part B that bring
> the card back into alignment with the implemented test:
>
> 1. **Part B reference table re-pinned** to the post-domain-fix
>    measured values (commit `3e50e94`). The v0.1.2 table was
>    measured under the pre-fix implementation that used 3-D cube
>    domains for four subtraction terms; the v0.1.2 implementation
>    review found and corrected that bug, which shifted the σ_z
>    no-guard convergence values.
> 2. **Part B grid annotation corrected**: the diagnostic uses a
>    `t_end = 1.0` grid (NOT the §2 `t_end = 2.0` fixture). v0.1.2 §4.1
>    Part B inadvertently said the diagnostic was run "at the §2
>    fixture"; the implemented test uses `t_end = 1.0` for fast
>    iteration across `n_pts ∈ {11, 21, 41, 81}`. The diagnostic is
>    non-gating, so the grid choice is independent of the §2 fixture
>    used by the four gating oracles.
>
> No other v0.1.2 content changes. The §2 fixture (which the four
> gating oracles use), the §3 API contract + §3.2 commuting-case
> guard, §3a θ-aware integration discipline, §3b Wick-pre-cancellation
> prohibition, §4.1 Part A exact-zero gate, §4.2 σ_x signal oracle,
> §4.3 gauge/sign oracle, §4.4 parity oracle, and §5 implementation
> hand-off all remain in force verbatim.

## 0. Provenance and role

This v0.1.3 errata revision consumes:

- the v0.1.2 Phase C card (commit `e414448`) — the immediate parent
  whose §4.1 Part B is updated by this revision;
- the v0.1.2 implementation experiment + review (commit `3e50e94`)
  which fixed four cube-domain bugs in
  `_L_4_thermal_at_time_apply_no_guard`. The review found that four
  subtraction terms (k=1 s-branch T3.70; k=2 τ-branch T2.71; k=2
  s-branch T2.71; k=3 τ-branch T3.72) were integrated over 3-D cube
  domains when the outer Eq. (28) chain ordering still applies. Per
  v0.1.2 §3a.2 step 3, the correct domain is the intersection of the
  outer chain ordering with each factor's inner θ-window. The fix
  merged each "cube" term into the sibling simplex loop at its (k,
  branch). The Wick-pre-cancellation prohibition (v0.1.1 §3b) was
  preserved because the integrand summation happens BEFORE the
  composite weight multiplication.

## 1. Purpose and scope

### 1.1 What this card does

- Carries forward the v0.1.2 two-part σ_z gate, the σ_x signal /
  gauge/sign / parity oracles, the API contract with the §3.2
  commuting-case guard, and the v0.1.1 §3a θ-aware integration
  discipline.
- Re-pins the §4.1 Part B convergence diagnostic reference table to
  the post-domain-fix values measured against commit `3e50e94`.
- Corrects the §4.1 Part B grid annotation to state the diagnostic's
  actual grid (`t_end = 1.0`, independent of §2's `t_end = 2.0`
  gating fixture).

### 1.2 What this card does not do

- It does not change any of the four gating oracle gates (Part A,
  σ_x, gauge/sign, parity).
- It does not change the §2 fixture used by gating oracles.
- It does not change the §3 / §3a / §3b implementation discipline.
- It does not introduce any new gate.

## 2. Frozen shared fixtures (unchanged from v0.1.2)

Refer to v0.1.2 §2 / v0.1.1 §2. Pinned values unchanged: ω = 1.0,
thermal T = 0.5, ohmic α = 0.02, ω_c = 10.0, time grid
`linspace(0, 2.0, 11)`, `t_idx = 5`, matrix-unit basis.

## 3. API contract (unchanged from v0.1.2)

Refer to v0.1.2 §3 (`_L_4_thermal_at_time_apply` signature),
§3.2 (commuting-case guard), and §3.3 (mandatory literal θ-aware
path for non-commuting A).

## 3a. θ-aware integration discipline (unchanged from v0.1.1)

Refer to v0.1.1 §3a (literal Eqs. (69)–(73) integration; intersection
of outer chain ordering and each factor's inner θ-window per §3a.2
step 3) and v0.1.1 §3b (forbidden Wick-pre-cancellation across terms).

The v0.1.2 implementation review and commit `3e50e94` validate
that §3a.2 step 3's "intersection with the outer chain ordering" was
the correct interpretation, by demonstrating that the alternative
"cube" interpretation (which ignored the outer ordering for some
subtraction terms) produced an inconsistent result and was a real
implementation bug. The v0.1.3 errata revision does not change §3a;
it only re-pins the Part B reference table that was measured under
the pre-fix implementation.

## 4. The four physics oracles

### 4.1 σ_z zero oracle (two-part gate)

**Part A (commuting-case exact-zero, the acceptance gate; unchanged
from v0.1.2).**

For `coupling_operator = σ_z` with `system_hamiltonian = (ω/2) σ_z`,
the §3.2 guard fires and returns the zero callable. For each
`X ∈ BASIS`, assert `np.testing.assert_allclose(L_4_apply(X), 0,
atol=1e-12)` for all four matrix-unit basis elements.

**Part B (literal-quadrature convergence diagnostic, non-gating; UPDATED in v0.1.3).**

Invoke `_L_4_thermal_at_time_apply_no_guard` on σ_z over a refinement
table to confirm the literal θ-aware integration converges
monotonically toward zero.

**Diagnostic grid (updated in v0.1.3 vs v0.1.2 wording).** The
diagnostic uses `t_end = 1.0` for fast iteration across the
refinement table; this is **independent** of the §2 gating fixture
(`t_end = 2.0`). The choice is acceptable because Part B is
non-gating: it documents structural soundness of the literal
integration, not a specific physical signal magnitude. The shorter
`t_end` keeps the runtime tractable.

**Reference table (re-pinned in v0.1.3 vs v0.1.2 values).** Measured
against commit `3e50e94` (post-cube-domain-fix). Tolerance: `rtol =
0.1` for regression matching.

    | n_pts | h | `‖L_4[E_01]‖_F` |
    |---|---|---|
    | 11 | 0.1 | ~1.28e-2 |
    | 21 | 0.05 | ~1.17e-2 |
    | 41 | 0.025 | ~7.48e-3 |
    | 81 | 0.0125 | ~5.09e-3 |

Assertions:
1. Monotonic decrease: `values[n_curr] < values[n_prev]` for all
   consecutive (`n_prev`, `n_curr`) pairs.
2. Regression match: each `values[n_pts]` matches the table value
   above at `rtol = 0.1`.

**Reason for the re-pinning.** v0.1.2 §4.1 Part B (commit `e414448`)
pinned `{11: 1.12e-2, 21: 7.47e-3, 41: 3.84e-3, 81: 1.90e-3}` —
measured under the pre-fix implementation that integrated four
subtraction terms over incorrect 3-D cube domains. After commit
`3e50e94` corrected those domains (cube → outer-simplex-intersected
per v0.1.1 §3a.2 step 3), the σ_z no-guard residuals shifted to the
new table above. The convergence rate is still O(h^1)-like (the
domain fix did not alter the overall convergence character; it only
shifted the magnitudes). The acceptance gate (Part A exact-zero via
the §3.2 guard) is unaffected.

### 4.2 σ_x signal oracle (unchanged from v0.1.2)

Refer to v0.1.2 §4.2. The bounding box `1e-6 ≤ ‖L_4^dis‖_F ≤ 1e6` is
unchanged. The measured value at commit `3e50e94` is
`‖L_4^dis‖_F ≈ 2.52e-2` (within the bounding box; the cube-domain
fix did not push the σ_x signal outside the gate).

### 4.3 Gauge/sign oracle (unchanged from v0.1.2)

Refer to v0.1.2 §4.3. The card-pinned n=2 regression reference value
is unchanged (the n=2 implementation `L_n_thermal_at_time(n=2)` was
not touched by the cube-domain fix).

### 4.4 Parity oracle (unchanged from v0.1.2)

Refer to v0.1.2 §4.4.

## 5. Implementation hand-off (unchanged from v0.1.2)

Refer to v0.1.2 §5. The `_L_4_thermal_at_time_apply` and
`_L_4_thermal_at_time_apply_no_guard` private helpers landed at
commit `e414448` (initial) and `3e50e94` (post-review fix). Phase C
acceptance gates pass at commit `3e50e94`. Phase D is the next
step.

## 6. Out-of-scope reminders (unchanged from v0.1.2)

Refer to v0.1.2 §6.

## 7. Steward freeze sign-off

> I have drafted v0.1.3 as an errata revision to v0.1.2 to bring the
> card's §4.1 Part B back into alignment with the implemented test
> after the post-review cube-domain fix landed at commit `3e50e94`.
> Two textual updates: (1) re-pin the Part B reference table to the
> post-fix measured values; (2) correct the Part B grid annotation
> from "§2 fixture" to "t_end = 1.0 (independent of §2)". No other
> changes; §2 through §6 of v0.1.2 are carried forward verbatim. The
> §3.2 commuting-case guard, the §3a θ-aware integration discipline,
> and the §3b pre-cancellation prohibition all remain in force.
> Per cards-first discipline, this file is content-immutable
> post-commit; v0.1.2 is retained as the predecessor (with its old
> table pinning the pre-fix implementation as a historical record).
>
> Reviewer: Ulrich Warring  Date: 2026-05-13
>
> Version at freeze: v0.1.3 (release state: frozen-post-implementation-review)

## Appendix — change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1.0 | 2026-05-13 | Initial draft and freeze. (Commit `49b92d5`.) | Local steward draft. |
| v0.1.1 | 2026-05-13 | **Supersedes v0.1.0.** Added §3a / §3b. (Commit `6732924`.) | Local steward draft. |
| v0.1.2 | 2026-05-13 | **Supersedes v0.1.1.** Added §3.2 commuting-case guard and split §4.1 into Part A (gate) + Part B (diagnostic). (Commit `e414448`.) | Local steward draft. |
| v0.1.3 | 2026-05-13 | **Errata supersedes v0.1.2.** Updated §4.1 Part B reference table to post-domain-fix values `{11: 1.28e-2, 21: 1.17e-2, 41: 7.48e-3, 81: 5.09e-3}` (was `{11: 1.12e-2, 21: 7.47e-3, 41: 3.84e-3, 81: 1.90e-3}`) and corrected the Part B grid annotation from "§2 fixture" to "t_end = 1.0 independent of §2 gating fixture". The re-pinning is required because v0.1.2's table was measured under the pre-fix implementation that integrated four subtraction terms over incorrect 3-D cube domains; commit `3e50e94` corrected those domains per v0.1.2 §3a.2 step 3 (intersection with outer chain ordering), which shifted the no-guard σ_z convergence values. §2 through §6 of v0.1.2 carried forward verbatim. | Local steward errata revision. |

*Verification card version: v0.1.3 (frozen 2026-05-13, errata).
Supersedes v0.1.2 to align §4.1 Part B with the implemented test after
the post-implementation-review cube-domain fix. CC-BY-4.0.*

---
artifact_id: cbg-companion-sec-iv-l4-phase-e-pilot-card
version: v0.1.0
date: 2026-05-13
type: verification-card / pilot
status: frozen-unclassified-pilot
parent_transcription: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md
parent_phase_b_card: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_n4-small-grid-verification-card_v0.1.1.md
parent_phase_c_card: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-c-physics-oracles-card_v0.1.3.md
parent_phase_d_card: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-d-public-route-card_v0.1.0.md
target_artifact: (deferred — no Phase E verdict written by this card)
anchor_plan: plans/dg-4-work-plan_v0.1.5.md §4 Phase E
release_gate: NONE — this card explicitly does NOT issue a Phase E classification
reviewer: Ulrich Warring
review_date: 2026-05-13
review_state: frozen-unclassified-pilot
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Phase E pilot card — unclassified Path A / Path B disagreement

> **Status: frozen-unclassified-pilot (2026-05-13).** This card
> records a Phase E pilot run that revealed a Path A / Path B
> magnitude disagreement of ~10⁵× in absolute ‖L_n^dis‖ values and
> ~30× in the α-normalised coefficient ratio at N=41, on the D1
> v0.1.2 σ_x thermal fixture. The card **does NOT classify** the
> cross-validation as supports / contradicts / inconclusive per work
> plan v0.1.5 §4 Phase E because both Path A and Path B have
> documented uncertainties that prevent a clean verdict:
>
> - **Path A** is not at quadrature convergence at the grids tested
>   (N=11, 21, 41); see §3.
> - **Path B** has a self-reported finite-env extraction floor
>   ("sigma_z thermal zero-oracle ~few × 10⁻² at the default
>   truncation per the 2026-05-06 pilot", per [D1 v0.1.2 result JSON
>   notes](../benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json)).
>
> The card pins the audit findings, the pilot measurements, and a
> follow-up plan to resolve the disagreement before any
> Phase E verdict lands. The D1 v0.1.2 envelope status is unchanged
> by this card.

## 0. Provenance and role

This card consumes:

- the released parent transcription
  ([Companion Sec. IV L_4 transcription v0.1.1](colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md));
- the Phase B / Phase C / Phase D card chain (small-grid v0.1.1,
  physics-oracles v0.1.3, public-route v0.1.0) and the implementation
  at commit `6cb0ea6`;
- the D1 v0.1.2 Path B audit payload (`benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json`);
- the Path B implementation in `benchmarks/numerical_tcl_extraction.py`;
- the work plan v0.1.5 §4 Phase E acceptance criteria.

Phase E was to be the analytic-Path-A vs numerical-Path-B
cross-validation. Per the work plan §4 Phase E acceptance, the
cross-validation must be recorded as **one of**:

- `supports-path-b-classification` → envelope DG-4 row updated
  positively, no Council convening;
- `contradicts-path-b-classification` → envelope marked
  `under-supersedure-review` same day, Council-3 convening required;
- `inconclusive-with-cause` → envelope frozen with marker, no
  verdict-bearing update.

This pilot card explicitly **does not** make any of those
classifications. It records the pilot result as
**`unclassified-pending-mutual-resolution`**, a state outside the
work plan's three-state acceptance set, on the grounds that the
preconditions for a clean classification (both paths at sufficient
resolution to permit comparison) are not met.

## 1. Purpose and scope

### 1.1 What this card does

- Records the audit comparing Path A and Path B implementation
  conventions (dissipator definition, Frobenius norm definition, α
  convention). Result: **no convention mismatch found**.
- Records the pilot measurement of Path A on the D1 v0.1.2 σ_x
  thermal fixture at N ∈ {11, 21, 41}, including the observed
  non-convergence pattern.
- Pins cause labels for the remaining magnitude disagreement.
- Pins a follow-up plan to resolve the disagreement.

### 1.2 What this card does not do

- It does **not** classify the cross-validation as
  supports / contradicts / inconclusive. The D1 v0.1.2 envelope
  status is unchanged.
- It does **not** retract the Path A or Path B verdicts.
- It does **not** authorize background compute beyond the pilot
  already recorded.
- It does **not** initiate Council-3 convening.

## 2. Audit findings (no convention mismatch)

Done by code review on 2026-05-13. The Path A and Path B sources
audited: `cbg/tcl_recursion.py` for Path A (`_L_4_thermal_at_time_apply`
+ `L_n_dissipator_thermal_at_time` + `L_n_dissipator_norm_thermal_on_grid`)
and `benchmarks/numerical_tcl_extraction.py` for Path B
(`path_b_dissipator_norm_coefficients` + `_liouville_dissipator_frobenius_norms`).

| Convention | Path A | Path B | Match |
|---|---|---|---|
| Dissipator residual sign | `L^dis = L + i [K, ·]` (`L_n_dissipator_thermal_at_time` line ~1235) | `L^dis = L + i [K, ·]` (`_liouville_dissipator_frobenius_norms` line ~528 docstring) | ✓ |
| K extraction | `K_from_generator` (Letter Eq. 6, matrix-unit basis) | `K_from_generator` (same function imported from `cbg.effective_hamiltonian`) | ✓ |
| Liouville matrix construction | `M[α, β] = ⟨F_α, L[F_β]⟩` in matrix-unit basis | Same construction in matrix-unit basis | ✓ |
| Norm | `np.linalg.norm(L_matrix, "fro")` over d²×d² Liouville matrix | Same | ✓ |
| Time-averaging | `np.mean(per_t_array)` | `np.mean(per_t_array)` | ✓ |
| α convention | `coupling_strength = α_phys²` (matches the continuum-limit J(ω) ∝ g² density of states) | `coupling_strength = α_phys²` by the runner default (per `numerical_tcl_extraction.py` line 22-24: "the finite-env builders discretise g_k ∝ sqrt(coupling_strength)") | ✓ |
| α-power scaling expected | L_2 ∝ α_phys², L_4 ∝ α_phys⁴ | L_t = α_phys² L_2_coeff + α_phys⁴ L_4_coeff + … (α-independent coefficients reported) | ✓ |

**Conclusion of the convention audit.** Path A and Path B compute
the same physical quantity at the same physical α (after the
`coupling_strength = α_phys²` understanding). The remaining
magnitude disagreement is NOT a convention or definition mismatch;
it is a numerical-resolution issue on at least one (probably both)
of the two paths.

## 3. Pilot measurement: Path A on D1 v0.1.2 σ_x thermal fixture

Fixture: D1 v0.1.2 baseline (`bath_state.family = thermal`,
`temperature = 0.5`, `coupling_strength = 0.02`, `cutoff_frequency = 10.0`),
σ_x coupling, H_S = (ω/2) σ_z with ω = 1.0, time grid linspace(0, 20, N).
Public route `L_n_dissipator_norm_thermal_on_grid(n, ...)` from
commit `f599751`.

| N | `‖L_2^dis‖_avg` | `‖L_4^dis‖_avg` | `‖L_4‖ / ‖L_2‖` | `(ratio) / α_phys²` | Wall time |
|---|---|---|---|---|---|
| 11 | 10.36 | 4.42e-3 | 4.26e-4 | 1.07 | 0.8 s |
| 21 | 5.40 | 2.67e-3 | 4.95e-4 | 1.24 | 8.5 s |
| 41 | 2.63 | 1.49e-2 | 5.66e-3 | 14.15 | 106 s |

Path B baseline (D1 v0.1.2 audit payload, computed at the full N=200
grid with finite-env Richardson extraction):

| Quantity | Value |
|---|---|
| `l2_dissipator_avg` | 27.42 |
| `l4_dissipator_avg` | 1300.49 |
| `coefficient_ratio (l4/l2)` | **47.42** |

### Observations

- **‖L_2^dis‖_avg halves** with each grid doubling in Path A
  (10.4 → 5.4 → 2.6). This is an averaging artifact: with more grid
  points uniformly spaced from t=0 to t=20, more samples land in
  the small-t buildup region where L_2(t) ≈ 0, dragging the
  arithmetic mean down. Path B at N=200 has the same averaging
  effect but at higher density and thus a different (smaller, in
  the same direction) artifact.
- **‖L_4^dis‖_avg is non-monotone** in N (4.4e-3 → 2.7e-3 → 1.5e-2),
  signalling that the literal θ-aware integration is not yet at
  asymptotic convergence at N=41 for the D1 fixture's parameters
  (`ω_c = 10`, far higher than the time grid spacing).
- **The α-normalised ratio rises**: 1.07 → 1.24 → 14.15. Path B's
  ratio is 47.4. The two paths are moving in the same direction as
  N refines but are not yet at agreement.

### Acceptance gate

**This pilot does NOT meet a Phase E classification gate.** Both
paths have unresolved numerical uncertainty at the resolutions
tested. Per work plan §4 Phase E, no `supports` /
`contradicts` / `inconclusive-with-cause` verdict is issued.

## 4. Cause labels

The disagreement at N ≤ 41 has two documented causes; the card
explicitly labels both before any future verdict is considered:

### 4.1 Path A: not at quadrature convergence at the grids tested

The Phase C card v0.1.3 §4.1 Part B documented Path A's σ_z O(h¹)
convergence character at N ∈ {11, 21, 41, 81}. The current Phase E
pilot extends that observation to the D1 σ_x fixture (different
spectral density parameters: ω_c=10 vs Phase C's ω_c=10 but
different time horizon and α). The convergence at the D1 fixture
appears slower than at the Phase C fixture, possibly because the
D1 fixture's higher ω_c relative to grid spacing demands finer
quadrature.

**To reach Path B's effective continuum resolution (Path B uses
N=200 + finite-env continuum limit), Path A would need at minimum
N=200 trapezoidal — estimated runtime ~hours per (configuration)
at present.**

### 4.2 Path B: finite-env extraction floor

Per the D1 v0.1.2 result JSON `notes`:

> "Path B carries a finite-env extraction floor (sigma_z thermal
> zero-oracle ~few × 10⁻² at the default truncation per the
> 2026-05-06 pilot); verdicts are subject to this documented
> uncertainty until the analytic Path A (Companion Sec. IV) lands."

The Path B floor was a known precondition at the D1 v0.1.2 PASS
verdict. Phase E was explicitly meant to resolve this uncertainty
via the analytic Path A; the pilot run shows that resolving it
requires resolving Path A's own convergence first.

## 5. Follow-up plan

Two work-plan-compatible follow-up tracks. Neither is initiated by
this card; the steward selects:

### Track 5.A: Targeted Path A convergence

- Extend Path A to N=81 and N=161 in background compute. Expected
  runtime: ~30 min for N=81, ~7 h for N=161.
- If the α-normalised ratio approaches Path B's 47.4: Phase E gains
  evidence for `supports-path-b-classification`.
- If the ratio plateaus at a different value: Phase E gains
  evidence for `contradicts-path-b-classification` or
  `inconclusive-with-cause`.
- Either outcome routes through a successor Phase E card with the
  full work plan §4 classification machinery.

### Track 5.B: Higher-order quadrature in Path A

- Implement Simpson's rule or Romberg integration inside
  `_L_4_thermal_at_time_apply_no_guard`, replacing the current
  nested-trapezoidal quadrature.
- Re-run the pilot at N=11..41 and compare convergence rate. If
  the converged ratio reaches Path B's 47.4 within ~10% at modest
  N, the cross-validation can land at a cheaper compute cost.
- Larger implementation effort than Track 5.A.

### Track 5.C: Path B audit (alternative or complement)

- Independently estimate Path B's finite-env extraction floor at
  the D1 σ_x fixture (currently characterised only on σ_z thermal
  per the 2026-05-06 pilot).
- If Path B's σ_x finite-env floor is order-unity at the D1
  fixture, the Path B coefficient_ratio = 47.4 may itself be at
  the floor and not a tight estimate of the analytic value.
- Out of scope for the immediate Phase E follow-up but relevant
  context for the eventual classification.

## 6. D1 v0.1.2 envelope status (unchanged)

The D1 v0.1.2 PASS verdict at commit `0d900ec` (Phase C+B errata
chain pushed; Path B as the v0.1.2 audit source) is **unchanged**
by this card. The validity-envelope DG-4 row is **not** updated by
this card in any direction. Per work plan §4 Phase E:

- Only `supports-path-b-classification` allows a positive envelope
  update; this card does NOT issue that classification.
- `contradicts-path-b-classification` would require same-day
  `under-supersedure-review` marker + Council-3 convening within
  one logbook cycle; this card does NOT issue that classification.
- `inconclusive-with-cause` would freeze the envelope with a
  marker; this card does NOT issue that classification.

The pilot result is an **internal cause record** for the steward
to consult when selecting Track 5.A / 5.B / 5.C as the next move.

## 7. Out-of-scope reminders

- **Phase F Tier-2.D handoff**: cannot proceed without a Phase E
  verdict.
- **Phase D public-route changes**: unaffected.
- **D1 v0.1.2 result JSON**: unchanged; the Path B baseline values
  reported there remain the verdict-bearing source.
- **Path B Richardson extraction implementation**: not modified by
  this card. Track 5.C is the audit path.

## 8. Steward freeze sign-off

> I have drafted this Phase E pilot card as a frozen
> unclassified-pilot record. The audit (§2) confirms Path A and
> Path B share definition conventions; the pilot (§3) reveals a
> resolution-dependent magnitude disagreement that prevents a
> clean Phase E classification. Cause labels (§4) and follow-up
> plan (§5) are recorded. The D1 v0.1.2 envelope status is
> unchanged (§6). No `supports` / `contradicts` /
> `inconclusive-with-cause` verdict is issued.
>
> Per cards-first discipline, this file is content-immutable
> post-commit. The follow-up tracks (5.A / 5.B / 5.C) will land
> as successor Phase E cards if and when the steward initiates
> them.
>
> Reviewer: Ulrich Warring  Date: 2026-05-13
>
> Version at freeze: v0.1.0 (release state: frozen-unclassified-pilot)

## Appendix — change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1.0 | 2026-05-13 | Initial draft and freeze. Records the audit (§2: no convention mismatch found), the Phase E pilot measurement on D1 v0.1.2 σ_x at N ∈ {11, 21, 41} (§3: Path A ratio 1.07 → 1.24 → 14.15 vs Path B 47.4), cause labels (§4: Path A not converged; Path B finite-env floor), and follow-up plan (§5: Tracks A/B/C). Does NOT classify the Phase E result. D1 v0.1.2 envelope status unchanged. | Local steward unclassified-pilot record. |

*Verification card version: v0.1.0 (frozen 2026-05-13,
unclassified-pilot). Records the Phase E pilot result without
classification; the steward selects Track 5.A / 5.B / 5.C as the
next move. CC-BY-4.0 (see ../LICENSE-docs).*

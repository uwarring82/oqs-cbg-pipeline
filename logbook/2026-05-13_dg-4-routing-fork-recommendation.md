# DG-4 routing fork after Phase E Track 5.C — recommend DG-3 Tier-2.A as the two-for-one move

**Date:** 2026-05-13
**Type:** discussion-outcome (route prioritization; not a verdict)
**Triggering commit:** _(self-referential; to be filled post-merge per [`logbook/README.md`](README.md) §Immutability exception 2)_

**Triggering evidence:**
- 5.C floor audit cause-label entry: [`2026-05-13_dg-4-phase-e-5c-path-b-floor-audit-floor-dominated.md`](2026-05-13_dg-4-phase-e-5c-path-b-floor-audit-floor-dominated.md) (commit `b4bda20`).
- Frozen 5.C card: [`transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-5c-path-b-floor-audit-card_v0.1.0.md`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-5c-path-b-floor-audit-card_v0.1.0.md) (commit `bbdc237`), §4.4 routing matrix.
- Phase E pilot card: [`transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-pilot-card_v0.1.0.md`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-pilot-card_v0.1.0.md) (commit `749bd85`).
- DG-4 work plan v0.1.5 §4 Phase E routing table: [`plans/dg-4-work-plan_v0.1.5.md`](../plans/dg-4-work-plan_v0.1.5.md).
- DG-4 row + "next natural milestones" in validity envelope: [`docs/validity_envelope.md`](../docs/validity_envelope.md).
- Status-surface propagation commit `77e5128` ("docs: propagate Phase E 5.C floor-dominated finding across status surfaces").
- Scoping-entry precedent: [`2026-05-11_next-tasks-scoping.md`](2026-05-11_next-tasks-scoping.md) — the same forward-looking discussion-outcome shape used here.

## Summary

The Phase E Track 5.C Path B floor audit (landed 2026-05-13 at commit `b4bda20`, cause label `floor-dominated`, max drift 24.16% with axes pulling in mutually inconsistent directions) made the original "cross-check Path A against Path B at D1 and route through the three-state acceptance set (`supports` / `contradicts` / `inconclusive-with-cause`)" milestone **unreachable in its original form**: Path B at the D1 production fixture is not a stable analytic-comparison reference. The 5.C card §4.4 routing matrix offers three forward paths without choosing among them.

This entry records the steward's recommended prioritization: **option (ii) — DG-3 Tier-2.A third reference method — first**, as a two-for-one move. The same work that lifts DG-3 from RUNNER-COMPLETE → PASS via a third method (HEOM / TEMPO / MCTDH / pseudomode) also produces the Path B replacement that Phase E now needs. Path A convergence (Tracks 5.A / 5.B) continues as **supporting ground-truth work**, not as a Phase E closure path on its own. Option (iii) — permanent `unclassified-pilot` — is the fallback if neither lands within a steward-chosen horizon.

This is a discussion-outcome, not a verdict. No DG-status transition, no Sail revision, no Ledger touch. The D1 v0.1.2 PASS verdict is unchanged.

## Detail

### The three §4.4 forward paths (recap)

Per the 5.C card §4.4 routing matrix, the `floor-dominated` outcome allows three forward paths for Phase E:

| Option | Path | Phase E closure shape |
|---|---|---|
| **(i)** | Drive Path A to convergence via Tracks 5.A (finer grid; N=81 ≈ 50 min, N=161 ≈ 25–30 h due to O(N⁵) L_4 assembly) or 5.B (higher-order quadrature; implementation + Part B reference re-pin). Treat the converged Path A value as the analytic ground truth with Path B documented as a finite-environment approximation only. | Single-sided Path A convergence claim; **not** a Path A / Path B agreement claim. |
| **(ii)** | Open DG-3 Tier-2.A: add or integrate a third reference method from a non-overlapping failure-mode class (HEOM / TEMPO / MCTDH / pseudomode), and use that as the Path B replacement. | Cross-validation against the third method, with Path B re-classified as a finite-env baseline. |
| **(iii)** | Leave Phase E permanently as `frozen-unclassified-pilot` and accept that the D1 v0.1.2 verdict carries Path B's documented finite-env floor as a recorded uncertainty. | No closure; documented Phase E gap. |

The 5.C card did not pick among the three. This entry does the prioritization.

### Why DG-3 Tier-2.A (option ii) wins on cost-effectiveness

Three reasons:

1. **Two-for-one Decision Gate coverage.** A third method is the only path that simultaneously serves DG-3 (lifting it from RUNNER-COMPLETE → PASS) AND DG-4 (giving Phase E a stable reference to cross-validate Path B against). Options (i) and (iii) only address Phase E.

2. **Path A's analytic ground truth has its own convergence floor.** The Phase E pilot card §4.1 documented that Path A at N ≤ 41 is not at quadrature convergence; Track 5.A's N=161 extension is estimated at 25–30 h due to the O(N⁵) L_4 assembly cost, and Track 5.B's higher-order quadrature requires implementing Romberg / Gauss-Legendre on the nested simplex plus re-pinning the Part B reference table. Path A as "the ground truth" is a real engineering claim, not a free upgrade. Treating it as supporting work (in parallel with option ii) reduces the risk that a converged Path A still leaves Phase E open because Path B is unreliable.

3. **The work-package precedent.** The 2026-05-11 next-tasks scoping listed DG-3 Tier-2.A as a Tier-2 milestone that "lifts the validity envelope's DG-3 row from RUNNER-COMPLETE → PASS"; the 5.C audit now adds a second purpose for the same work, making it the highest-leverage Tier-2 item. Selecting it now also makes the DG-3 work-plan revision concrete (it needs a v0.1.1 with a specific third-method family chosen) instead of remaining a draft.

### Path A as supporting ground-truth work

Tracks 5.A and 5.B remain valuable and should not be stopped — they would:

- Confirm or contradict Path A's structural correctness at the σ_x thermal fixture (current pilot shows the analytic route converges in *form* but not in *value* at N ≤ 41).
- Provide a Path-A-anchored cross-check for the DG-3 third-method values once those land.
- Unblock DG-2's literal K_2-K_4 fourth-order recursion milestone, which depends on a converged analytic L_4.

What changes is the **framing**: Path A convergence on its own is no longer treated as sufficient to close Phase E, because the Path B reference it would be compared against is itself not stable. Phase E closure now requires the DG-3 third-method anchor (or the option-iii acceptance).

### What's deferred behind this route decision

- **DG-5 scope realisation** (Fano-Anderson dynamics + HMF reference + fermionic-bath cumulants): the largest Tier-2 scope. Deferred until DG-3 Tier-2.A makes meaningful progress, both because DG-5 itself depends on a competing-framework reference (HMF) that overlaps in spirit with DG-3's third-method requirement, and because the stewardship bandwidth implication of opening two large Tier-2 items in parallel is high.
- **Entry-2-wide K_2-K_4 recursion closure** (DG-2 Tier-2.D): was the natural DG-2 follow-up after a successful Phase E. Now that Phase E's cross-validation milestone is unreachable in its original form, Entry-2-wide closure also defers until either Path A produces converged values (via 5.A or 5.B) OR a third method gives an independent reference (via DG-3 Tier-2.A).
- **Tracks 5.A and 5.B execution decisions**: continue as supporting work; sequencing is a separate steward decision and does not block the DG-3 Tier-2.A initiation.

### What this does NOT change

- **D1 v0.1.2 PASS verdict** is unchanged. The 5.C audit did not retract or modify the v0.1.2 verdict, card, or result JSON. This entry does not either.
- **DG-4 row in the validity envelope** is unchanged. The DG-4 row already records the 5.C `floor-dominated` finding (commit `77e5128`); this entry adds prioritization context, not a status transition.
- **Phase E pilot card v0.1.0** `frozen-unclassified-pilot` state is unchanged.
- **5.C card v0.1.0** is content-immutable.
- **DG-4 work plan v0.1.5** is unchanged. The three §4.4 forward paths are recorded there; this entry does not modify the work plan, only prioritises among the options it already provides.
- **Phase F blocked status** is unchanged. This entry advances the routing decision; it does not unblock Phase F.

## Routing notes

- **If the steward initiates option (ii)**: the next concrete step is a DG-3 work-plan revision (`plans/dg-3-work-plan_v0.1.0.md` → `v0.1.1`) that selects a specific third-method family. The four candidate classes per Sail v0.5 §5 Tier 3 are HEOM (hierarchy-truncation class), TEMPO / process tensor (memory-cutoff class), MCTDH (basis-truncation class), and pseudomode / chain-mapping (auxiliary-system class). The selection is itself a steward decision and may benefit from a brief comparison scoping note.
- **If the steward initiates option (i) instead** (or as preceding supporting work): Tracks 5.A and/or 5.B initiate. The Phase E classification that emerges would be a single-sided convergence claim, not an agreement claim. This is permissible; it just requires the Phase E pilot card or a successor card to record the changed framing.
- **If neither initiates within a steward-chosen horizon**: option (iii) is the default — Phase E stays `frozen-unclassified-pilot`, the D1 v0.1.2 verdict's Path B finite-env floor stays as documented uncertainty, and Phase F remains blocked.
- This entry is **superseded by execution** — when the route decision triggers a downstream plan revision or card commit, a follow-up logbook entry (or a commit message referencing this entry) closes it.
- The 5.C card's `triggering_commit` is `bbdc237`; the 5.C audit's commit is `b4bda20`; the status-surface propagation commit is `77e5128`; this entry's commit hash will be the recorded routing-fork decision commit.

## Permitted post-commit edits to this entry

Per [`logbook/README.md`](README.md) §"Immutability":

- `superseded by:` annotation when a successor entry is added (e.g., a DG-3 work-plan revision logbook entry that opens option (ii), a Track-5.A / 5.B execution entry that opens option (i), or a steward acceptance entry that picks option (iii)).
- Self-referential placeholder fill for `Triggering commit:` (this entry's introducing commit is itself the trigger; the placeholder will be replaced with the commit hash in a follow-up commit).

Any substantive text edit requires supersedure under the normal logbook discipline.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

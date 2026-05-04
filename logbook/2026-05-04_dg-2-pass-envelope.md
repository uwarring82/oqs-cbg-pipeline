# DG-2 PASS — validity envelope updated (4 of 4 sub-claims verified under cleared registry)

**Date:** 2026-05-04
**Type:** dg-pass
**Triggering commit:** (to be populated on commit)
**Triggering evidence:**
- Card B1 v0.1.0 PASS (verdict commit `4502863`, 2026-05-01) — diagonal Entry 1.B.3
- Card B2 v0.1.0 PASS (verdict commit `9febfed`, 2026-05-04) — off-diagonal Entry 1.B.3 + Entry 1.D
- Card B3 v0.1.0 PASS (verdict commit `b46a4e4`, 2026-05-04) — Entry 1.A basis-independence
- Card B4-conv-registry v0.1.0 PASS (verdict commit `62e44d0`, 2026-05-04) — Entry 3.B.3 under cleared registry
- Card B5-conv-registry v0.2.0 PASS (verdict commit `6352891`, 2026-05-04) — Entry 4.B.2 under cleared registry
- Subsidiary briefing v0.3.0 + Act 1 + Act 2 deliberation transcripts (sealed)
- [`docs/validity_envelope.md`](../docs/validity_envelope.md) (this commit; DG-2 row updated to PASS)

## Summary

The validity envelope's DG-2 row transitions from **PARTIAL — 3 of 4 sub-claims PASS** to **PASS — 4 of 4 sub-claims under Council-cleared registry** as of 2026-05-04. With B5-conv-registry v0.2.0's verdict landing same-day (commit `6352891`), the joint B4 + B5 closure of Entries 3.B.3 + 4.B.2 under all four Council-cleared displacement profiles completes the DG-2 sub-claim set. Together with the prior PASSes of B1 (diagonal Entry 1.B.3), B2 (off-diagonal Entry 1.B.3 + Entry 1.D), and B3 (Entry 1.A basis-independence), the four DG-2 sub-claim families are now operationally verified at machine precision. The Ledger and Sail are unchanged; the envelope simply now records that all four sub-claims hold under the Council-cleared scope.

## Detail

### What changed in the envelope

1. **Header `Last updated` line**: `2026-05-04 (DG-2 PARTIAL — 3 of 4 sub-claims PASS; ...)` → `2026-05-04 (DG-2 PASS — 4 of 4 sub-claims PASS under Council Act 2 cleared registry; ...)`.

2. **DG-1 row, Validity-envelope-implication cell**: the operationalisability-carve-out parenthetical narrowed further. Previously v0.2.0 read "Entries 3.B.3, 4.B.2 remain deferred to DG-2"; now the carve-out paragraph reads that Entries 1.B.3, 3.B.3, 4.B.2 *all three* were repatriated to DG-2 and PASSed (the 1.B.3 repatriation happened earlier on 2026-05-01 via B1 + B2; the 3.B.3 / 4.B.2 repatriation completes here via B4 + B5). The DG-1 verdict itself is unchanged — DG-1 still PASSes the same five sub-claims (1.B.1, 1.B.2, 3.B.1, 3.B.2 thermal, 4.B.1 thermal); only the deferred-entries note is updated.

3. **DG-2 row, Status / Evidence / Implication cells**:
   - Status: `PARTIAL (3 of 4 sub-claims PASS)` → `**PASS — 4 of 4 sub-claims under Council-cleared registry** (2026-05-04)`.
   - Evidence: extended with B4-conv-registry v0.1.0 (verdict `62e44d0`) + B5-conv-registry v0.2.0 (verdict `6352891`) and their per-card PASS logbook entries.
   - Implication: enumerates the four sub-claim families (Entry 1.A, Entry 1.B.3 both halves + 1.D, Entries 3.B.3 + 4.B.2 jointly), records Entries 3.B.3 / 4.B.2 as verified *under the Council-cleared registry* (with the four profile keys named explicitly), introduces the citation requirement that DG-2 displaced-bath citations must name the registered profile, and notes that the K_2–K_4 *numerical recursion* at perturbative_order ≥ 4 remains unattempted (so Entry 2's "scope-limited" qualifier is partially-mitigated, not fully).

4. **"What this validity envelope authorises" section**:
   - Date stamp: `(2026-05-04, DG-1 PASS + DG-2 PARTIAL)` → `(2026-05-04, DG-1 PASS + DG-2 PASS under Council-cleared registry)`.
   - DG-2 authorised-citation bullet expanded into a sub-list covering all four sub-claim families. New explicit citation requirement: Entries 3.B.3 / 4.B.2 citations must name the registered displacement profile.
   - Reproduction sentence updated to note the single-source-of-truth pattern (B4 / B5 dynamical cards reuse `cbg.cumulants.D_bar_1` for both the runner's K_1 computation and the predicted-shift / predicted-transverse-vector handlers, giving exact-zero or machine-precision verdicts).
   - Architectural-scaffold demonstration mention extended to include the two-act Council deliberation discipline and the displacement-profile registry-clearance-gate (subsidiary briefing v0.3.0 §6.1).
   - Non-authorised list updated:
     - **Removed**: the carve-out for Entries 3.B.3 / 4.B.2 (now authorised under the cleared registry).
     - **Added**: explicit non-authorisation for Entries 3.B.3 / 4.B.2 *under non-cleared profiles*. The four cleared profiles are exhaustive of the v0.1.0 admissible set; ad-hoc additions require fresh Council clearance per the §6.1 registry-clearance-gate.
     - **Updated**: out-of-frozen-parameter carve-out broadened to include the dynamical-card cleared-registry scope (parameters per fixture: α₀ = 1.0; ω_d = 5.0, Δω = 2.0 for Gaussian).
   - "Natural milestones" sentence narrowed: full DG-2 closure is now achieved at the *structural-identity* layer; the remaining open milestone within DG-2 is the K_2–K_4 numerical recursion at perturbative_order ≥ 4.

### What did NOT change

- **Sail v0.5 §9 Decision Gate definitions**: untouched. The DG-2 description ("Fourth-order recursion (K_2–K_4 with structural-identity satisfaction)") is unchanged. PASS at this milestone reflects that the structural-identity portion has now been operationally verified under all four Council-cleared sub-claim families; the literal "fourth-order recursion" portion (K_2 through K_4 numerically computed at perturbative_order ≥ 4) remains a separate open milestone within DG-2 — the envelope's implication cell records this honestly.
- **Failure-asymmetry-clearance status table**: unchanged. DG-3 remains NOT YET ATTEMPTED.
- **Stewardship-conflict-bound annotations**: unchanged. No Tier 4 trapped-ion cards exist.
- **CL-2026-005 v0.4 (Ledger)**: untouched. The Ledger's claims are unchanged; the envelope simply now records additional repository evidence supporting Entries 1.A, 1.B.3 (both halves), 1.D, 3.B.3, and 4.B.2.
- **Sail v0.5**: untouched. No DG criteria revised.
- **DG-3, DG-4, DG-5 rows**: unchanged at NOT YET ATTEMPTED.
- **Subsidiary briefing v0.3.0 + Act 1 + Act 2 deliberation transcripts**: sealed and unchanged.
- **All five passed B-cards (B1 / B2 / B3 / B4 / B5 v0.2.0)**: unchanged at HEAD; their YAML files carry their respective PASS verdicts and self-referential commit_hash fills.

### Cards-first audit trail (DG-2)

All five DG-2 cards followed the cards-first / Risk #6 / Risk #8 mitigation pattern: frozen at `frozen-awaiting-run` BEFORE any runner code existed for their test_case names; verdict commits added handler implementations bounded by the cards' pre-existing acceptance criteria. The audit trail is mechanically reconstructable:

| Card | Frozen | Verdict commit | Self-ref hash + logbook |
|---|---|---|---|
| B1 v0.1.0 | `551c03e` (2026-05-01) | `4502863` | `efcb031` |
| B2 v0.1.0 | `cd364f3` (2026-05-01) | `9febfed` (bundled) | `0a5bf69` |
| B3 v0.1.0 | `eb39460` (2026-05-01) | `b46a4e4` (bundled) | `b42a353` |
| B4-conv-registry v0.1.0 | `5d1ce87` (2026-05-04) | `62e44d0` | `bed0854` |
| B5-conv-registry v0.1.0 → v0.2.0 | `a7eae74` (2026-05-04) → `f1ea085` (2026-05-04 supersedure) | `6352891` | `6247ae3` |

The B5 v0.1.0 → v0.2.0 same-day supersedure (commit `f1ea085`) corrected a prediction-text error in v0.1.0 (interaction-picture vs Schrödinger-picture form for the σ_x channel); v0.1.0 is retained at HEAD with `status: superseded` per SCHEMA.md §Card lifecycle. No verdict was attempted on v0.1.0 between freeze and supersedure; the audit trail is unbroken.

### DG status summary at HEAD

- **DG-1**: PASS (2026-04-30). Five sub-claims (1.B.1, 1.B.2, 3.B.1, 3.B.2 thermal, 4.B.1 thermal) at machine precision.
- **DG-2**: PASS — 4 of 4 sub-claims PASS under Council-cleared registry (2026-05-04). Entries 1.A, 1.B.3 (both halves) + 1.D, 3.B.3 (under registry), 4.B.2 (under registry) verified at machine precision.
- **DG-3**: NOT YET ATTEMPTED. No cross-method validation; implementation-readiness pair scaffolded only.
- **DG-4**: NOT YET ATTEMPTED. No failure regime identified.
- **DG-5**: NOT YET ATTEMPTED. CL-2026-005 v0.4 Entry 7 remains UNDERDETERMINED.

### Authorisation delta (citation impact)

- **Newly authorised at v0.2.0+** (post-this-update): citation of the repository for Entries **3.B.3** and **4.B.2** under any of the four Council-cleared displacement profiles, with explicit profile naming and Hayden-Sorce gauge attribution.
- **Still not authorised**: Entries 3.B.3 / 4.B.2 under non-cleared profiles (registry-clearance-gate); Entry 2 K_n at order ≥ 4 (not attempted); Entry 5 (parity-FDT, DG-2 recursive-perturbative layer); Entry 6 (Tier-4 stewardship-conflict-bound); Entry 7 (DG-5 territory); K(t) outside the cards' frozen-parameter regimes; cross-method (DG-3) and failure-regime (DG-4) claims.
- **DG-1 + B1 + B2 + B3 authorisations unchanged**.

## Routing notes

- **No Council deliberation required.** The PASS transition aggregates verdicts that have already landed under the cards-first discipline plus the Act-2-cleared (c)-discipline. The validity envelope simply now reports the aggregate state.
- **Ledger CL-2026-005 v0.4**: untouched. Its claims are unchanged.
- **Sail v0.5**: untouched. DG criteria unchanged.
- **Subsidiary briefing v0.3.0 + Act 1 / Act 2 transcripts**: sealed, unchanged. The (c)-discipline and §6.1 registry-clearance-gate continue to apply: any future expansion of the displacement-profile registry (additions or removals) requires fresh Council clearance and would re-open the Entries 3.B.3 / 4.B.2 authorisation scope.
- **Recursive K_2–K_4 numerical track (Entry 2 residual)**: not attempted; the structural-identity scaffolding (B1 / B2 / B3 / B4 / B5) is reusable for the higher-order recursion. That work is a separate plan and a future commit.
- **Cross-method (DG-3) and failure-envelope (DG-4) tracks**: unchanged.

The next admissible work step is at the steward's discretion: either (a) plan documents for the K_2–K_4 numerical recursion at perturbative_order ≥ 4 (which would mitigate Entry 2's residual "scope-limited" qualifier), or (b) preparation of DG-3 cross-method scaffolding (against a method from a non-overlapping failure-mode class). Neither requires Council deliberation under standing operational discipline.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above will be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

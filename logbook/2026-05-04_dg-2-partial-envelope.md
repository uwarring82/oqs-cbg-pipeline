# DG-2 PARTIAL — validity envelope updated (3 of 4 sub-claims PASS)

**Date:** 2026-05-04
**Type:** dg-pass (PARTIAL)
**Triggering commit:** 9e78353cf0754c1fab3aa16a7db0ee7248661b08
**Triggering evidence:**
- Card B1 v0.1.0 PASS (verdict commit `4502863`, 2026-05-01) — diagonal Entry 1.B.3
- Card B2 v0.1.0 PASS (verdict commit `9febfed`, 2026-05-04) — off-diagonal Entry 1.B.3 + Entry 1.D
- Card B3 v0.1.0 PASS (verdict commit `b46a4e4`, 2026-05-04) — Entry 1.A basis-independence
- [`docs/validity_envelope.md`](../docs/validity_envelope.md) (this commit; DG-2 row updated to PARTIAL, DG-1 row's stale Entry 1.B.3 deferral removed)
- Anchor: Sail v0.5 §9 Decision Gate framework; CL-2026-005 v0.4 Entries 1.A, 1.B.3, 1.D, 3.B.3, 4.B.2.

## Summary

The validity envelope's DG-2 row transitions from **NOT YET ATTEMPTED** to **PARTIAL (3 of 4 sub-claims PASS)** as of 2026-05-04. Three of the four DG-2 structural-identity sub-claims that the B-cards were designed around are now operationally verified at machine precision — Entry 1.A basis-independence (Card B3), Entry 1.B.3 diagonal half (Card B1), and Entry 1.B.3 off-diagonal half + Entry 1.D (Card B2). The fourth DG-2 sub-claim, the coherent-displacement track for Entries 3.B.3 + 4.B.2, remains Council-gated on the displacement-mode convention and is the only DG-2 deferral. The DG-1 row's deferral language has been narrowed to remove the now-stale Entry 1.B.3 carve-out (Entry 1.B.3 is no longer deferred — it has been repatriated to DG-2 and PASSed). This entry follows the [`docs/validity_envelope.md`](../docs/validity_envelope.md) §Update protocol requirement that envelope changes commit atomically with the logbook announcement.

## Detail

### What changed in the envelope

1. **Header `Last updated`** line: `2026-04-30 (DG-1 PASS; ...)` → `2026-05-04 (DG-2 PARTIAL — 3 of 4 sub-claims PASS; ...)`.

2. **DG-1 row, Validity-envelope-implication cell**: the deferral list narrowed from `Entries 1.B.3, 3.B.3, 4.B.2` to `Entries 3.B.3, 4.B.2`, and the parenthetical operationalisability rationale narrowed from "(Hayden–Sorce 2022 transcription + displacement convention not available)" to "(displacement-mode convention not yet Council-cleared)". Added a parenthetical note that Entry 1.B.3 was repatriated to DG-2 and PASSed on 2026-05-04, with a forward reference to the DG-2 row. The DG-1 verdict itself is unchanged — the cards still PASS the same five sub-claims (1.B.1, 1.B.2, 3.B.1, 3.B.2 thermal, 4.B.1 thermal); only the deferred-entries list shrank.

3. **DG-2 row, Status / Evidence / Implication cells**:
   - Status: `NOT YET ATTEMPTED` → `**PARTIAL (3 of 4 sub-claims PASS)** (2026-05-04)`.
   - Evidence: filled with B1 / B2 / B3 verdict commits (`4502863` / `9febfed` / `b46a4e4`), the per-card YAMLs, the [`benchmarks/results/`](../benchmarks/results/) JSON evidence directory, and the three per-card PASS logbook entries.
   - Implication: enumerates the three verified sub-claims with explicit Entry citations, flags the d = 2 / matrix-unit + su(d)-generator scope of the basis-independence verification, declares Entries 1.A / 1.B.3 (both halves) / 1.D citation **supported** at v0.2.0+, and carves out Entries 3.B.3 / 4.B.2 as the Council-gated remainder. Notes that the K_2–K_4 numerical recursion at perturbative_order ≥ 4 (the literal "fourth-order recursion" portion of the DG-2 description) is *not* attempted by the B-cards — those operate at perturbative_order = 0 (algebraic_map) — so CL-2026-005 v0.4 Entry 2's "scope-limited" qualifier remains *partially* unmitigated by repository evidence: the structural identities Entry 2 relies on (1.A, 1.B.3, 1.D) are now reproducible, but the recursive K_n computation at order 4 is not yet operational.

4. **"What this validity envelope authorises" section**:
   - Date stamp: `(2026-04-30, DG-1 PASS)` → `(2026-05-04, DG-1 PASS + DG-2 PARTIAL)`.
   - Added a new authorised-citation bullet for DG-2 sub-claims (Entries 1.A, 1.B.3 diagonal, 1.B.3 off-diagonal + 1.D) with explicit attribution to the Hayden–Sorce gauge and the d = 2 / matrix-unit + su(d)-generator basis-independence scope.
   - Reproduction sentence broadened to mention `pytest tests/test_benchmark_card.py` for DG-2 cards alongside the existing `python scripts/run_dg1_verdict.py` for DG-1.
   - Removed Entry 1.B.3 from the non-authorised list (it is now authorised). Entries 3.B.3 + 4.B.2 remain non-authorised, with the rationale narrowed to displacement-mode convention not Council-cleared. Entry 2's not-authorised explanation refined to reflect that the *structural identities* it invokes are now operational while the *K_n recursion at order 4* is not.
   - Out-of-frozen-parameter-regime carve-out broadened to include the DG-2 algebraic_map fixture scope (d = 2; n = 2 V_i; β / a / b = 0.5).
   - "Natural milestones" sentence updated: the next DG-2 work is full closure (3.B.3 + 4.B.2 Council clearance; K_2–K_4 numerical recursion with structural-identity stacking on top of the now-verified Entry 1.A / 1.B.3 / 1.D identities).

### What did NOT change

- **Sail v0.5 § 9 Decision Gate definitions**: untouched. The DG-2 description remains "Fourth-order recursion (K_2–K_4 with structural-identity satisfaction)"; only the *status* / *evidence* / *implication* triple changed. The PARTIAL state is honest about which slice of DG-2 is verified (the structural identities Entry 2 relies on) and which is not (the K_n numerical recursion at order ≥ 4).
- **Failure-asymmetry-clearance status table**: unchanged. DG-3 remains NOT YET ATTEMPTED; the implementation-readiness pair is still scaffolded-but-not-implemented.
- **Stewardship-conflict-bound annotations**: unchanged. No Tier 4 trapped-ion cards exist.
- **CL-2026-005 v0.4 (Ledger)**: not touched. The Ledger's claims are unchanged. The validity envelope simply now reports that more of those claims have been operationalised by repository evidence.
- **Sail v0.5**: not touched. No DG criteria were revised; only existing-criteria evidence was added.
- **DG-3, DG-4, DG-5 rows**: unchanged at NOT YET ATTEMPTED.

### Cards-first audit trail (DG-2)

All three B-cards were committed at `frozen-awaiting-run` before any runner code existed for their test-case names; the verdict commits added handler implementations bounded by the cards' pre-existing acceptance criteria. The audit trail is mechanically reconstructable:

| Card | Frozen | Runner wiring | Verdict | Self-ref hash + logbook |
|---|---|---|---|---|
| B1 v0.1.0 | `551c03e` (2026-05-01) | `62f5879` | `4502863` | `efcb031` |
| B2 v0.1.0 | `cd364f3` (2026-05-01) | (bundled) | `9febfed` | `0a5bf69` |
| B3 v0.1.0 | `eb39460` (2026-05-01) | (bundled) | `b46a4e4` | `b42a353` |

The cards-first / Risk #6 / Risk #8 mitigation pattern that DG-1 validated continues to hold for DG-2: each card's threshold, acceptance criterion, and per-case expected outcome was fixed in YAML before the implementing handler code was written, so no card was retroactively edited to make a runner pass.

### DG status summary at HEAD

- **DG-1**: PASS (2026-04-30). Five sub-claims (1.B.1, 1.B.2, 3.B.1, 3.B.2 thermal, 4.B.1 thermal) at machine precision.
- **DG-2**: PARTIAL — 3 of 4 sub-claims PASS (2026-05-04). Entries 1.A, 1.B.3 (both halves), 1.D verified at machine precision. Entries 3.B.3, 4.B.2 Council-gated. K_2–K_4 numerical recursion at order ≥ 4 not yet attempted.
- **DG-3**: NOT YET ATTEMPTED. No cross-method validation; implementation-readiness pair scaffolded only.
- **DG-4**: NOT YET ATTEMPTED. No failure regime identified.
- **DG-5**: NOT YET ATTEMPTED. CL-2026-005 v0.4 Entry 7 remains UNDERDETERMINED.

### Authorisation delta (citation impact)

- **Newly authorised at v0.2.0+** (post-this-update): citation of the repository for Entry 1.A basis-independence at d = 2; Entry 1.B.3 diagonal pseudo-Kraus reduction; Entry 1.B.3 off-diagonal half + Entry 1.D off-diagonal `omega_{ij}` generalisation.
- **Still not authorised**: Entries 3.B.3, 4.B.2 (Council-gated displacement convention); Entry 2 K_n at order 4 (not attempted); Entry 5 (parity-FDT, DG-2 recursive-perturbative layer); Entry 6 (Tier-4 stewardship-conflict-bound); Entry 7 (DG-5 territory). K(t) outside the cards' frozen-parameter regimes (DG-1 dynamical scope + DG-2 algebraic_map fixture scope). Cross-method (DG-3) and failure-regime (DG-4) claims.
- **DG-1 authorisations unchanged**.

## Routing notes

- **No Council deliberation required.** The PARTIAL transition aggregates verdicts that have already landed under the cards-first discipline. The validity envelope simply now reports the aggregate state.
- **Ledger CL-2026-005 v0.4**: untouched. Its claims are unchanged; the envelope now records additional repository evidence supporting Entries 1.A, 1.B.3 (both halves), and 1.D.
- **Sail v0.5**: untouched. DG criteria are unchanged.
- **Coherent-displacement track (Entries 3.B.3, 4.B.2)**: still gated on Council-cleared displacement-mode convention. No steward-actionable path to closure; this is the only outstanding DG-2 sub-claim.
- **Recursive K_2–K_4 numerical track**: not yet attempted. The structural-identity scaffolding (B1 / B2 / B3) is reusable for the higher-order recursion; that work is a separate plan.
- **Next admissible work**: either (a) author plan documents for the K_2–K_4 numerical recursion at perturbative_order = 4 (steward-actionable; would not on its own complete DG-2 but would mitigate Entry 2's "scope-limited" qualifier further), or (b) wait on Council clearance for the displacement-mode convention to attempt the 3.B.3 / 4.B.2 sub-claim. Both routes are admissible.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above will be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

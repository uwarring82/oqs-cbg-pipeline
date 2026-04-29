# Stewardship Conflict — `oqs-cbg-pipeline`

**Layer:** Repository protective scaffolding
**Anchor:** Sail v0.5 §5 Tier 4; CL-2026-005 v0.4 Entry 6; Council ratification G2 (session CL-2026-005-DEL-001).

## The conflict

The local steward of this repository (U. Warring) is also the steward of CL-2026-005 v0.4 *and* a co-author of the trapped-ion experimental paper invoked as the empirical anchor in CL-2026-005 Entry 6:

> Colla, Hasse, Palani, Schaetz, Breuer, Warring, *Nature Communications* **16**, 2502 (2025).

This is a structural conflict, not a defect: the conflict exists because the steward is genuinely connected to the work being measured. Council has ratified that the conflict is acceptably contained by triple-flagging discipline (Council ratification G2), and the present document operationalises that discipline at the repository level.

## Operational rules

### Rule 1 — Primary trapped-ion data: non-Warring-group sources

For Tier 4 (experimental-facing) benchmarks involving trapped-ion systems, *primary* benchmark cards must use data from research groups other than the Warring group. The list of qualifying groups should be reviewed annually; at the time of this document, it includes (non-exhaustively): NIST trapped-ion group, Innsbruck Blatt/Roos groups, Oxford Lucas group, ETH Home group, JQI/Maryland Monroe group, Sandia Mehta group, MPQ Garching, Sussex Hensinger group.

### Rule 2 — Secondary cross-checks: Warring-group data admissible with flag

Warring-group trapped-ion data may be used as a *secondary* cross-check, never as primary evidence for a DG pass. When such data are used:

- The benchmark card must carry the explicit annotation: `stewardship_flag: secondary, conservatively-read, no-DG-pass-on-this-data-alone`.
- The card's verdict must not depend on Warring-group data: removing those data and re-evaluating must not change the DG verdict.
- The flag propagates to any downstream artefact (plot, table, report, paper, talk) that uses the card.

### Rule 3 — Unmatched models: explicit annotation, hold verdict

For Tier 4 models where no independent (non-Warring-group) data exist, the Tier 4 verdict for that model is annotated:

> `stewardship-conflict-bound, awaiting independent replication`

The model may still be carried in the repository — the algebra and Tier 1–3 results stand on their own. But its Tier 4 verdict does *not* count toward DG-3 or DG-5 pass criteria, and is excluded from any aggregate validity-envelope report until independent replication is available.

### Rule 4 — Sticky propagation

The stewardship flag is *sticky*. Once a benchmark card carries the flag, every artefact derived from it inherits the flag verbatim. Removing the flag requires:

- Replacement of the underlying data with a non-Warring-group source, *or*
- A fresh Council deliberation that explicitly addresses the conflict in the new context.

No automated tool, no convenience refactor, and no editorial decision at the repository level may remove a stewardship flag.

## What this conflict does *not* contaminate

Per Council deliberation CL-2026-005-DEL-001 §5, the steward conflict on Entry 6 *does not propagate* to Entries 5 or 7. Concretely:

- Tier 1, Tier 2, Tier 3 benchmarks are *not* affected by the conflict — they are theory-internal or cross-method comparisons that do not depend on the Hasse et al. experimental paper.
- DG-1, DG-2, DG-3, DG-4 are *not* affected by the conflict.
- DG-5's discriminant venues (Fano–Anderson, Jaynes–Cummings) are *not* affected by the conflict — they are solvable models, not experimental implementations of trapped ions.

The conflict is bounded to Tier 4 trapped-ion benchmarks. Triple-flagging discipline contains it.

## Audit trail

Every benchmark card stamped `stewardship_flag: primary` must record the data source explicitly (paper, group, year, DOI). Every card stamped `secondary` must additionally record why a primary-eligible source was insufficient or unavailable. Every card stamped `stewardship-conflict-bound` must record the search performed to confirm absence of independent data.

The audit trail is part of the FAIR-Reusable layer of this repository: future stewards (including non-conflicted future stewards) must be able to reconstruct the conflict's bounds from the recorded annotations alone, without reading additional internal documents.

---

*This document is non-optional per Sail v0.5 §11. It must exist at HEAD before any code is committed to the repository.*

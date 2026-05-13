# `docs/` — Repository protective scaffolding

This directory contains the non-optional protective documents required by Sail v0.5 §11. None of these files may be omitted from the repository at any version. Code that runs without all five files present at HEAD is structurally non-compliant with the Sail's discipline and must not be released, archived, or cited.

## Contents

| File | Purpose | Source authority |
|---|---|---|
| `endorsement_marker.md` | Defines what the repository is and is not; states the unidirectional consumption rule | Sail v0.5 §0 |
| `stewardship_conflict.md` | Operationalises the steward-conflict triple-flagging at repository level | CL-2026-005 v0.4 Entry 6; G2 (DEL-001) |
| `do_not_cite_as.md` | Enumerates citation prohibitions and the sole supported conditional citation | G1 (DEL-001) |
| `validity_envelope.md` | Living record of current DG status and what each authorises | Sail v0.5 §9 |
| `benchmark_protocol.md` | Coordinate-choice annotations, failure-mode taxonomy, DG-3 tracking, parameter-freezing | Sail v0.5 §11 |

## Reading order for new contributors

1. `endorsement_marker.md` — what the repository is for.
2. `do_not_cite_as.md` — what may and may not be cited from it.
3. `stewardship_conflict.md` — why some Tier 4 results are flagged.
4. `validity_envelope.md` — what the repository can currently support.
5. `benchmark_protocol.md` — how to add a benchmark card without breaking discipline.

## Authority

These documents inherit their authority from Council-cleared Ledger entry CL-2026-005 v0.4 (session CL-2026-005-DEL-001) and from Sail v0.5 §§0, 4, 5, 9, 10, 11. They cannot be amended by repository action alone; substantive changes require either (a) Sail revision (steward action) or (b) fresh Council deliberation, depending on the change's scope. See `endorsement_marker.md` for the routing rule.

---

*Last updated: 2026-05-13 (Phase E Track 5.C Path B floor audit landed `floor-dominated`; D1 v0.1.2 PASS unchanged. Prior verdict update: 2026-05-06 DG-4 PASS at D1 v0.1.2 via picture-fixed Path B numerical L_4, supersedes the v0.1.1 verdict at tag `v0.5.0` downgraded on review the same day).*

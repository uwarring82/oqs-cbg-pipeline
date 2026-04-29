# `ledger/` — Vendored Council-cleared inputs

This directory contains a verbatim copy of the Council-cleared Breakwater Ledger entry that anchors this repository, plus its briefing and deliberation log. These files are **vendored** into the repository as stable, read-only inputs.

## Contents

| File | Authority |
|---|---|
| `CL-2026-005_v0.4.md` | Active immutable Ledger entry, Council-cleared 2026-04-29 |
| `CL-2026-005_v0.4_council-briefing.md` | Orientation document for the Council deliberation |
| `CL-2026-005_v0.4_council-deliberation_2026-04-29.md` | Immutable deliberation log, session CL-2026-005-DEL-001 |

## Vendoring rationale

Per FAIR principles (Findable, Accessible), the Ledger is included in the repository so that:

- A future reader who clones the repository in isolation can verify the anchor without external lookup.
- The exact text the repository was authored against is preserved against future Ledger amendments.
- Citation of the repository at a specific commit hash transitively pins the Ledger version.

## Read-only at this layer

These files are read-only at the repository layer. They must not be edited by repository action. If the upstream Ledger is amended (e.g. via a future Council re-deliberation following DG-5 outcomes), the repository imports the new version into a *new* file (e.g. `CL-2026-005_v0.5.md`) without overwriting the existing v0.4 file. The vendored history is preserved.

If a discrepancy is ever found between the vendored copy and the canonical Ledger source, the canonical source takes precedence and the vendored copy is corrected in a single dedicated commit with no other changes.

## Routing rule reminder

Per `docs/endorsement_marker.md`, the repository's relationship to the Ledger is unidirectional: Ledger informs repository; repository never modifies Ledger. Outputs of this repository that bear on the Ledger route via fresh Council deliberation, not via edits in this directory.

---

*Last updated: 2026-04-29 (repository initialisation).*

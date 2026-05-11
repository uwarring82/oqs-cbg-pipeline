---
name: DG status-change request
about: Propose a Decision-Gate status transition (verdict, downgrade, supersedure)
title: "[DG-?] "
labels: dg-status
---

<!--
This template is for proposing a change to docs/validity_envelope.md's
DG-status table. Examples:

- Reaching PASS on a previously-RUNNER-COMPLETE / SCOPED gate.
- Downgrading a passed gate after a defect surfaces.
- Adding a new card that supersedes a passed-card under the §6.3
  supersedure protocol from docs/benchmark_protocol.md.
- Repatriating sub-claims between gates (analogous to the DG-1 →
  DG-2 carve-out for Entries 1.B.3 / 3.B.3 / 4.B.2).

If you want to *report a bug* in a passed gate's surface, use the
bug-report template instead and check the "could affect a passed DG"
box; the steward will convert to this template if a status change is
warranted.
-->

## Decision Gate (required)

- [ ] DG-1
- [ ] DG-2
- [ ] DG-3
- [ ] DG-4
- [ ] DG-5

## Proposed transition (required)

| Field | Current | Proposed |
|---|---|---|
| Status (`docs/validity_envelope.md` DG row) | | |
| Triggering card(s) | | |
| Date | | |
| Triggering commit | | |

## Cards-first discipline check (required)

- [ ] The triggering card is **frozen** (the card's `status:` field is
  `frozen-awaiting-run` or `pass`, and its `frozen_parameters` and
  `acceptance_criterion` blocks were committed before the runner code
  that satisfies them).
- [ ] The card is **not** being silently edited post-verdict; any
  change to a card's content goes through supersedure (a new
  `<card_id>_<short-tag>_v<higher>.yaml` file with `supersedes:` set).
- [ ] If this is a verdict transition, the matching evidence
  artefact (`benchmarks/results/<card_filename>_result.json`) is
  either present, will be added in the same PR, or its absence is
  explained.

## Validity-envelope authorisation (required)

<!--
What does this transition authorise — and explicitly NOT authorise —
in terms of citation? Mirror the prose form used in
docs/validity_envelope.md's "What this validity envelope authorises"
section. Include any required attribution annotations (gauge,
displacement profile, schema version).
-->

## Routing notes (required)

- [ ] **Repository-internal change.** No Ledger or Sail impact; the
  validity envelope update is a steward action under
  docs/validity_envelope.md "Update protocol".
- [ ] **Ledger-routed change.** A new Council deliberation is needed
  per Sail v0.5 §9 + CL-2026-005 v0.4 procedures. Outline the routing
  here; do NOT modify the Ledger from this PR.
- [ ] **Sail-routed change.** A Sail revision is needed.

## Logbook entry plan (required)

The repository's discipline is "verdict commit → logbook entry → validity
envelope row update". Name the logbook entry you intend to add:

- File: `logbook/YYYY-MM-DD_<short-tag>.md`
- Type: `dg-pass` / `dg-downgrade` / `dg-scoping` / `discussion-outcome` / other

## Supersedure record (if applicable)

<!--
If this transition supersedes a prior verdict (like the
2026-05-06 DG-4 v0.1.1 → v0.1.2 same-day supersedure), name the
predecessor card and the supersedure logbook entry that records the
defect rationale.
-->

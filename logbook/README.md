# `logbook/` — Immutable repository event log

The logbook is the append-only record of repository events: initialisation, version bumps, Decision Gate passes (and downgrades), Sail revisions, Ledger imports, structural changes, and significant discussion outcomes.

## Conventions

### File naming

```
logbook/YYYY-MM-DD_<short-tag>.md
```

- `YYYY-MM-DD` is the ISO date of the event in the steward's local timezone (Europe/Berlin).
- `<short-tag>` is a kebab-case tag describing the event. Examples: `repo-init`, `dg-1-pass`, `sail-v0.5-bump`, `ledger-v0.5-imported`, `dg-3-readiness-pass`.
- One file per event. Do not bundle multiple events into a single file even if they share a date.

### Content structure

Each entry contains, at minimum:

```markdown
# <Title>

**Date:** YYYY-MM-DD
**Type:** <one of: initialisation, dg-pass, dg-downgrade, sail-bump, ledger-import,
              structural, discussion-outcome, conflict-flag, other>
**Triggering commit:** <hash, populated after commit>
**Triggering evidence:** <files, cards, tests, or external references>

## Summary

(One paragraph stating what happened.)

## Detail

(Any further detail. Specifically: which DG was affected, what the validity-envelope
change is, any cause labels assigned, any stewardship flags applied or propagated.)

## Routing notes

(If the event has implications for the Ledger or Sail, state the routing here.
Do NOT modify the Ledger or Sail from logbook entries; document the route only.)
```

### Immutability

Once committed, a logbook entry is immutable. Corrections take the form of a *new* entry that supersedes the old one, with an explicit `supersedes: YYYY-MM-DD_old-tag.md` field in its header. The old entry remains in the repository, with a `superseded by:` annotation appended (this annotation is the one and only edit ever permitted to a committed entry).

This mirrors the Ledger's discipline at the repository layer.

### What does *not* go in the logbook

- Routine commits (those go in commit messages and PR descriptions).
- Discussion that has not produced an outcome (that goes in issues).
- Minor documentation typo fixes (commit message suffices).
- Anything that belongs in the Ledger or Sail (those have their own change procedures; the logbook may *reference* such changes but does not *enact* them).

## Index

| Date | Tag | Type | Summary |
|---|---|---|---|
| 2026-04-29 | `repo-init` | initialisation | Repository scaffold v0.1.0; Sail v0.4 active; CL-2026-005 v0.4 vendored |
| 2026-04-29 | `public-site-added` | structural | Root `index.html` added as a static public landing page |

(This index is updated atomically when new entries are added.)

---

*Last updated: 2026-04-29. CC-BY-4.0 (see ../LICENSE-docs).*

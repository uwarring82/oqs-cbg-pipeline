# `plans/` — Steward-authored work plans

This directory holds **work plans**: steward-authored, revisable documents that operationalise a Sail-stipulated objective (e.g. a Decision Gate) into ordered, auditable tasks.

## Distinction from neighbouring surfaces

| Surface | Author | Mutability | Authority |
|---|---|---|---|
| `ledger/` | Council | Immutable once cleared | Council-cleared Breakwater entry |
| `sail/` | Steward | Revisable; substantive changes that bear on the Ledger route via Council | Programme-level direction |
| `plans/` (this) | Steward | Revisable freely; superseded plans retained, not deleted | Operational decomposition of Sail objectives |
| `logbook/` | Steward | Immutable once committed | Append-only event record |
| `docs/` | Steward | Revisable under §11 discipline | Protective scaffolding (5 non-optional files) |

A plan **does not** modify the Sail or Ledger. It schedules and orders work that is bounded by them. Plans are revised by **superseding revision**: a new file at a new version (`dg-1-work-plan_v0.1.1.md`, `dg-1-work-plan_v0.2.0.md`, …) is added, and the prior revision is retained with a `superseded by:` field appended to its front-matter. That `superseded by:` annotation is the only post-commit edit permitted to a plan file's content.

A plan's **status** (draft / active / superseded) is not tracked by editing the plan file; it is tracked in the index below. This keeps individual plan files content-immutable post-commit while letting the steward update the operational status pointer freely. The pattern mirrors the validity envelope's "living document, atomic-update protocol" and the logbook's "immutable entries + index table" structure.

## File naming

```
plans/<plan-id>_v<MAJOR>.<MINOR>.<PATCH>.md
```

`<plan-id>` is a kebab-case identifier (e.g. `dg-1-work-plan`). One plan per file. Version bumps follow the same MAJOR/MINOR/PATCH semantics used by the repository tag, scoped to the plan.

## Required front-matter

Each plan carries a YAML front-matter block with at least:

```yaml
---
plan_id: <id>
version: v<MAJOR>.<MINOR>.<PATCH>
date: YYYY-MM-DD
type: work-plan
anchor_sail: <sail filename + § references>
anchor_ledger: <ledger id + version + entry references>
anchor_envelope: <validity_envelope.md status references>
status: draft  # set at commit time; reflects status AS OF this commit. Operational status tracked in the index below, not by editing this field.
supersedes: <prior plan filename, if any>
superseded_by: <successor plan filename, if any — appended only when a successor exists; this is the only post-commit edit permitted>
license: CC-BY-4.0 (LICENSE-docs)
---
```

## Index (operational status — mutable)

This index is the canonical source of truth for *current* plan status. Updating a row in this table is permitted; editing a committed plan file's `status:` field is not.

| Plan | Canonical version | Operational status | Phase | Anchor |
|---|---|---|---|---|
| [DG-1 Work Plan](dg-1-work-plan_v0.1.4.md) | v0.1.4 | verdict-reached | **Verdict: PASS** (2026-04-30; tag `v0.2.0`) | Sail v0.5 §9 (DG-1); CL-2026-005 v0.4 Entries 1, 3, 4 (1.B.3, 3.B.3, 4.B.2 deferred to DG-2 per v0.1.4 §1.1 operationalisability carve-out). See [logbook/2026-04-30_dg-1-pass.md](../logbook/2026-04-30_dg-1-pass.md). |
| [DG-3 Work Plan](dg-3-work-plan_v0.1.0.md) | v0.1.0 | draft | Phase A: cards frozen; Phase B–D pending | Sail v0.5 §9 (DG-3); baseline pair implementation + cross-method runner wiring. Cards C1, C2 frozen. |
| [DG-4 Work Plan](dg-4-work-plan_v0.1.3.md) | v0.1.3 | draft | Phase A complete; B.0, B.1, B.2 (n=3), B.4 landed; Phase A.bis (D1 v0.1.1) + B.2 (n=4) + B.3 + Phase C–D pending | Sail v0.5 §9 (DG-4); CL-2026-005 v0.4 Entry 2 (recursive-series convergence; scope-limited). v0.1.3 supersedes v0.1.2 with an empirical narrowing of D1 v0.1.1's load-bearing reproducibility-perturbation set: Phase B.4 implementation (commit `c7e9999`) revealed that `quad_limit` is a no-op witness for production-like tuples (SciPy converges before 100 subintervals), so v0.1.3 drops it from the load-bearing set and adds `omega_c` ±1 as a substitute that genuinely changes the spectrum. This is Risk R6 firing as anticipated by v0.1.2. |

### Superseded plans (retained for audit)

| Plan | Version | Superseded by | Date |
|---|---|---|---|
| [DG-1 Work Plan v0.1.0](dg-1-work-plan_v0.1.0.md) | v0.1.0 | [v0.1.1](dg-1-work-plan_v0.1.1.md) | 2026-04-30 |
| [DG-1 Work Plan v0.1.1](dg-1-work-plan_v0.1.1.md) | v0.1.1 | [v0.1.2](dg-1-work-plan_v0.1.2.md) | 2026-04-30 |
| [DG-1 Work Plan v0.1.2](dg-1-work-plan_v0.1.2.md) | v0.1.2 | [v0.1.3](dg-1-work-plan_v0.1.3.md) | 2026-04-30 |
| [DG-1 Work Plan v0.1.3](dg-1-work-plan_v0.1.3.md) | v0.1.3 | [v0.1.4](dg-1-work-plan_v0.1.4.md) | 2026-04-30 |
| [DG-4 Work Plan v0.1.0](dg-4-work-plan_v0.1.0.md) | v0.1.0 | [v0.1.1](dg-4-work-plan_v0.1.1.md) | 2026-05-05 |
| [DG-4 Work Plan v0.1.1](dg-4-work-plan_v0.1.1.md) | v0.1.1 | [v0.1.2](dg-4-work-plan_v0.1.2.md) | 2026-05-05 |
| [DG-4 Work Plan v0.1.2](dg-4-work-plan_v0.1.2.md) | v0.1.2 | [v0.1.3](dg-4-work-plan_v0.1.3.md) | 2026-05-06 |

---

*Last updated: 2026-05-06 (DG-4 work plan v0.1.3 supersedes v0.1.2: empirical narrowing of D1 v0.1.1's load-bearing reproducibility-perturbation set after Phase B.4 implementation; quad_limit out, omega_c in). CC-BY-4.0 (see ../LICENSE-docs).*

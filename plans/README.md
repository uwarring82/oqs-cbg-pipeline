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
| [DG-3 Work Plan](dg-3-work-plan_v0.1.2.md) | v0.1.2 | draft; Phases A–C + D.0/D.1 recon landed; route corrected | HEOM-vs-TEMPO gating-pair plan, superseding v0.1.1 after Phase D.0/D.1 invalidated its §2.3 framing. **Phases A–C** (HEOM track) landed under v0.1.1: `qutip>=5.2` floor (`672db39`), `benchmarks/heom_reference.py` + 12 tests (`f30c627`), schema v0.1.4 + C1/C2 v0.2.0 triple cards + runner third-method branch + C1/C2 v0.1.0 supersedure (`0b750b2`). **Phase D.0/D.1 recon** (`d41ff66`, logbook [`2026-05-16_dg-3-phase-d-recon-gating-pair-blocked`](../logbook/2026-05-16_dg-3-phase-d-recon-gating-pair-blocked.md)): C1/C2 v0.2.0 gating pair `(exact_finite_env, heom_reference)` @1e-6 found physically unsatisfiable (cause `finite-env-correlator-floor`); HEOM converged/faithful, cbg correct, no convention bug. v0.1.2 corrects the route: gate **HEOM vs TEMPO/OQuPy** (two faithful continuous-bath solvers), Option-A four-method C1/C2 **v0.3.0** cards with a general `methods` list (schema **v0.1.5**, backward compatible), `exact_finite_env`/`qutip_reference` retained as non-gating auxiliary. **Phases E–H** (plan correction + schema v0.1.5 + `oqupy>=0.5` dep; `benchmarks/oqupy_reference.py`; v0.3.0 cards + N-method runner; run/verdict) pending. v0.2.0 cards remain frozen and unmutated. | Sail v0.5 §9 (DG-3 failure-asymmetry clearance per §5 Tier 3). Linked to the 2026-05-13 DG-4 routing-fork recommendation as the two-for-one DG-3 PASS + DG-4 Phase E Path B replacement move. |
| [DG-4 Work Plan](dg-4-work-plan_v0.1.5.md) | v0.1.5 | frozen (Council-3 cleared 2026-05-11); Phases A–D landed; Phase E pilot frozen-unclassified; Phase E Track 5.C executed `floor-dominated` 2026-05-13 | **Verdict remains PASS** via D1 v0.1.2 picture-fixed Path B numerical L_4 run (2026-05-06). v0.1.5 scaffolds Tier-2.B (DG-4 Path A) and is now substantially executed: Phase A transcription released ([`v0.1.1`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md)); Phase B small-grid verification card v0.1.1 + `_D_bar_4_companion` helper landed (22-test gate passes); Phase C physics-oracles card v0.1.3 + `_L_4_thermal_at_time_apply` landed (19-test gate passes; σ_z gated via the `[H_S, A] = 0` Feynman–Vernon guard); Phase D public-route card v0.1.0 + `L_n_thermal_at_time(n=4)` exposed with the n=4 dissipator / `K_total` cascade (47-test regression passes); Phase E pilot card v0.1.0 frozen as `unclassified-pilot` (commit `749bd85`). **Phase E Track 5.C Path B floor audit** (frozen card `bbdc237`, executed at commit `b4bda20`, surface-propagation commit `77e5128`) landed cause label `floor-dominated`: Path B at the D1 production fixture is not a stable analytic-comparison reference (24% drift under truncation tightening; axes pull in inconsistent directions). Phase E routing now requires Path A as single-sided ground truth (Tracks 5.A / 5.B), DG-3 Tier-2.A (third method) as Path B's replacement, or a permanent `unclassified-pilot` state; the steward routing recommendation prioritising DG-3 Tier-2.A is recorded in [`logbook/2026-05-13_dg-4-routing-fork-recommendation.md`](../logbook/2026-05-13_dg-4-routing-fork-recommendation.md). | Sail v0.5 §9 (DG-4); CL-2026-005 v0.4 Entry 2. v0.1.5 supersedes v0.1.4 for post-verdict Path A follow-up planning only; it does not reopen D1, mutate frozen card parameters, or change the live DG-4 verdict. The D1 v0.1.2 audit-complete Path B result remains [`benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json`](../benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json); the 5.C floor-audit payload is [`benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json`](../benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json). |

### Auxiliary route plans

| Plan | Version | Operational status | Parent | Purpose |
|---|---|---|---|---|
| [DG-4 Path B Richardson Extraction](dg-4-path-b-richardson-extraction_v0.1.0.md) | v0.1.0 | consumed-by-verdict | DG-4 work plan v0.1.4 Phase B.2 Path B | Numerical `Lambda_t` reconstruction and even-alpha Richardson extraction via `benchmarks/exact_finite_env`; benchmark-side only, not a replacement for analytic `cbg.tcl_recursion` order-4 recursion. D1 v0.1.2 (and its superseded predecessor v0.1.1) used this path for the 2026-05-06 DG-4 PASS verdict. The v0.1.2 run added the interaction-picture transform before order-4 extraction (commit d67b453) and threaded `upper_cutoff_factor` into the finite-env builder's `omega_max_factor` (commit a908cd6), so all four reproducibility perturbations are now operational. |

### Superseded plans (retained for audit)

| Plan | Version | Superseded by | Date |
|---|---|---|---|
| [DG-1 Work Plan v0.1.0](dg-1-work-plan_v0.1.0.md) | v0.1.0 | [v0.1.1](dg-1-work-plan_v0.1.1.md) | 2026-04-30 |
| [DG-1 Work Plan v0.1.1](dg-1-work-plan_v0.1.1.md) | v0.1.1 | [v0.1.2](dg-1-work-plan_v0.1.2.md) | 2026-04-30 |
| [DG-1 Work Plan v0.1.2](dg-1-work-plan_v0.1.2.md) | v0.1.2 | [v0.1.3](dg-1-work-plan_v0.1.3.md) | 2026-04-30 |
| [DG-1 Work Plan v0.1.3](dg-1-work-plan_v0.1.3.md) | v0.1.3 | [v0.1.4](dg-1-work-plan_v0.1.4.md) | 2026-04-30 |
| [DG-3 Work Plan v0.1.0](dg-3-work-plan_v0.1.0.md) | v0.1.0 | [v0.1.1](dg-3-work-plan_v0.1.1.md) | 2026-05-15 |
| [DG-3 Work Plan v0.1.1](dg-3-work-plan_v0.1.1.md) | v0.1.1 | [v0.1.2](dg-3-work-plan_v0.1.2.md) | 2026-05-16 |
| [DG-4 Work Plan v0.1.0](dg-4-work-plan_v0.1.0.md) | v0.1.0 | [v0.1.1](dg-4-work-plan_v0.1.1.md) | 2026-05-05 |
| [DG-4 Work Plan v0.1.1](dg-4-work-plan_v0.1.1.md) | v0.1.1 | [v0.1.2](dg-4-work-plan_v0.1.2.md) | 2026-05-05 |
| [DG-4 Work Plan v0.1.2](dg-4-work-plan_v0.1.2.md) | v0.1.2 | [v0.1.3](dg-4-work-plan_v0.1.3.md) | 2026-05-06 |
| [DG-4 Work Plan v0.1.3](dg-4-work-plan_v0.1.3.md) | v0.1.3 | [v0.1.4](dg-4-work-plan_v0.1.4.md) | 2026-05-06 |
| [DG-4 Work Plan v0.1.4](dg-4-work-plan_v0.1.4.md) | v0.1.4 | [v0.1.5](dg-4-work-plan_v0.1.5.md) | 2026-05-11 |

---

*Last updated: 2026-05-16 (DG-3 work plan superseded v0.1.1 → v0.1.2: plan-surface correction after Phase D.0/D.1 recon found the C1/C2 v0.2.0 gating pair `(exact_finite_env, heom_reference)` @1e-6 physically unsatisfiable — cause `finite-env-correlator-floor`. v0.1.2 explicitly supersedes the v0.1.1 §2.3 "no other structural change is required" sentence; corrected route gates **HEOM vs TEMPO/OQuPy** via Option-A four-method C1/C2 v0.3.0 cards + general `methods` list (schema v0.1.5); `oqupy>=0.5` planned dependency. v0.2.0 cards remain frozen and unmutated; no DG-3 PASS. Prior: DG-3 work plan v0.1.1 Phases A–C landed: Phase A decision-record + qutip>=5.2 floor (commit `672db39`); Phase B `benchmarks/heom_reference.py` module + 12 smoke tests (commit `f30c627`); Phase C SCHEMA.md v0.1.4 + C1/C2 v0.2.0 triple-method thermal cards + runner extension + C1/C2 v0.1.0 atomic supersedure; Phase D.0/D.1 recon (commit `d41ff66`). DG-3 work plan revised v0.1.0 → v0.1.1: Tier-2.A third-method selection plan with **HEOM via QuTiP 5 in-tree `qutip.solver.heom.HEOMSolver`** selected, **TEMPO via OQuPy 0.5.0** recorded as fallback, pseudomode noted; baseline-pair runner wiring under v0.1.0 already landed per validity envelope DG-3 row 2026-05-05. DG-4 verdict remains D1 v0.1.2 PASS via picture-fixed Path B numerical L_4; active DG-4 follow-up plan is v0.1.5, **frozen** via Council-3 review on 2026-05-11; Phase A transcription artifact released as v0.1.1 on 2026-05-12; Phases B, C, and D landed 2026-05-13 with the public `L_n_thermal_at_time(n=4)` thermal-Gaussian route exposed and full regression suite passing; Phase E pilot card v0.1.0 frozen as `unclassified-pilot`; **Phase E Track 5.C Path B floor audit landed `floor-dominated` 2026-05-13** — Path B is not a stable cross-validation reference at the D1 production fixture; Phase E routing pivoted to Path A single-sided / DG-3 Tier-2.A / permanent `unclassified-pilot` per the steward routing-fork recommendation in [`logbook/2026-05-13_dg-4-routing-fork-recommendation.md`](../logbook/2026-05-13_dg-4-routing-fork-recommendation.md). DG-3 v0.1.2 is the active plan for the Tier-2.A route. D1 v0.1.2 PASS unchanged. CC-BY-4.0 (see ../LICENSE-docs).*

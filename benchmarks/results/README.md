# `benchmarks/results/` — Verdict result artefacts and DG-level summaries

This directory holds the **machine-readable evidence** for every passed (or
superseded) benchmark card and the DG-level summary aggregates.

Each `<card_id>_<short-tag>_v<version>_result.json` file is a **point-in-time
verdict artefact**: it captures the runner's output at the moment a card's
verdict commit landed and is **not subsequently edited**. This mirrors the
[`logbook/`](../../logbook/) discipline at the result-artefact layer:
supersedure produces a *new file* (the successor card's `_result.json`),
not an in-place edit of the predecessor.

The `DG-N_summary.json` files (e.g. `DG-1_summary.json`, `DG-4_summary.json`)
are top-level aggregates: they list which cards contributed to a Decision
Gate's verdict, point at each card's `_result.json`, and record any
DG-level caveats. They may be **refreshed in place** when a verdict
supersedure changes which card is the live carrier of a DG (e.g. the
2026-05-06 DG-4 v0.1.1 → v0.1.2 supersedure refreshed `DG-4_summary.json`
to point at `v0.1.2` rather than `v0.1.1`). They are *not* themselves
versioned; their authoritative history is the git log of this directory.

## Index

| File | Card or DG | Verdict status | Notes |
|---|---|---|---|
| [`A1_closed-form-K_v0.1.1_result.json`](A1_closed-form-K_v0.1.1_result.json) | A1 v0.1.1 (DG-1) | **PASS** (2026-04-30) | Frozen. |
| [`A3_pure-dephasing_v0.1.1_result.json`](A3_pure-dephasing_v0.1.1_result.json) | A3 v0.1.1 (DG-1) | **PASS** (2026-04-30) | Frozen. |
| [`A4_sigma-x-thermal_v0.1.1_result.json`](A4_sigma-x-thermal_v0.1.1_result.json) | A4 v0.1.1 (DG-1) | **PASS** (2026-04-30) | Frozen. |
| [`B1_pseudo-kraus-diagonal_v0.1.0_result.json`](B1_pseudo-kraus-diagonal_v0.1.0_result.json) | B1 v0.1.0 (DG-2) | **PASS** (2026-05-01) | Frozen. |
| [`B2_pseudo-kraus-offdiagonal_v0.1.0_result.json`](B2_pseudo-kraus-offdiagonal_v0.1.0_result.json) | B2 v0.1.0 (DG-2) | **PASS** (2026-05-04) | Frozen. |
| [`B3_cross-basis-structural-identity_v0.1.0_result.json`](B3_cross-basis-structural-identity_v0.1.0_result.json) | B3 v0.1.0 (DG-2) | **PASS** (2026-05-04) | Frozen. |
| [`B4-conv-registry_v0.1.0_result.json`](B4-conv-registry_v0.1.0_result.json) | B4-conv-registry v0.1.0 (DG-2) | **PASS** (2026-05-04) | Frozen. Verifies Entry 3.B.3 under all four Council-cleared profiles. |
| [`B5-conv-registry_v0.2.0_result.json`](B5-conv-registry_v0.2.0_result.json) | B5-conv-registry v0.2.0 (DG-2) | **PASS** (2026-05-04) | Frozen. v0.1.0 predecessor result was superseded same-day; only the v0.2.0 result is retained as the live verdict. |
| [`D1_failure-envelope-convergence_v0.1.1_result.json`](D1_failure-envelope-convergence_v0.1.1_result.json) | D1 v0.1.1 (DG-4) | **SUPERSEDED** (2026-05-06) | Retained for audit only. Verdict was tagged `v0.5.0` and downgraded the same day for two HIGH-severity Path B defects + one MEDIUM audit gap. See [`logbook/2026-05-06_dg-4-pass-path-b-superseded.md`](../../logbook/2026-05-06_dg-4-pass-path-b-superseded.md). |
| [`D1_failure-envelope-convergence_v0.1.2_result.json`](D1_failure-envelope-convergence_v0.1.2_result.json) | D1 v0.1.2 (DG-4) | **PASS** (2026-05-06) — **live DG-4 verdict** | Audit-complete: per-α + per-α-per-perturbation `r_4` persisted; picture-fixed Path B; all four reproducibility perturbations operational. |
| [`D1_path-b-floor-audit_v0.1.0_result.json`](D1_path-b-floor-audit_v0.1.0_result.json) | Phase E 5.C floor-audit card v0.1.0 (DG-4) | **AUDIT RESULT** (2026-05-13) — cause label `floor-dominated` | Phase E Track 5.C Path B finite-env floor audit at the D1 v0.1.2 σ_x fixture. 9 of 10 configs evaluated (one preflight-skipped at `d_joint = 13122`); three Hilbert witnesses `(4, 4)`, `(4, 5)`, `(6, 3)`; max drift **24.16%** at `(6, 3)`; the three truncation axes drive `coefficient_ratio` in mutually inconsistent directions. **Audit result artefact, not a verdict commit** — D1 v0.1.2 PASS unchanged; Phase E routing pivoted away from Path A / Path B agreement claim. See [`logbook/2026-05-13_dg-4-phase-e-5c-path-b-floor-audit-floor-dominated.md`](../../logbook/2026-05-13_dg-4-phase-e-5c-path-b-floor-audit-floor-dominated.md). |
| [`DG-1_summary.json`](DG-1_summary.json) | DG-1 aggregate | **PASS** (2026-04-30) | Lists A1 / A3 / A4. Schema anchor pinned at v0.1.2 (the schema in effect when DG-1 PASS landed); SCHEMA.md has since bumped to v0.1.3. |
| [`DG-4_summary.json`](DG-4_summary.json) | DG-4 aggregate | **PASS** (2026-05-06) | Points at D1 v0.1.2 (live) and records `supersedes: v0.1.1`. Includes a `v011_supersedure_record` block citing the three repair commits. |

## DG-1 sub-claim repatriation (recorded here per work-package §6 item 4 / Path L5-b)

The DG-1 verdict (2026-04-30) covers CL-2026-005 v0.4 **Entries 1, 3, 4
unambiguous sub-cases** at machine precision. Three displacement-dependent
sub-claims initially deferred from DG-1 per [`plans/dg-1-work-plan_v0.1.4.md`](../../plans/dg-1-work-plan_v0.1.4.md) §1.1 ("operationalisability carve-out") were **repatriated to DG-2** and
subsequently passed there:

| Originally part of | Now passes under | Card | Date |
|---|---|---|---|
| DG-1, Entry 1.B.3 (diagonal pseudo-Kraus) | DG-2 | [B1 v0.1.0](../benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml) | 2026-05-01 |
| DG-1, Entry 1.B.3 (off-diagonal) + Entry 1.D | DG-2 | [B2 v0.1.0](../benchmark_cards/B2_pseudo-kraus-offdiagonal_v0.1.0.yaml) | 2026-05-04 |
| DG-1, Entry 3.B.3 (time-dependent shift) | DG-2 | [B4-conv-registry v0.1.0](../benchmark_cards/B4-conv-registry_v0.1.0.yaml) | 2026-05-04 |
| DG-1, Entry 4.B.2 (eigenbasis rotation) | DG-2 | [B5-conv-registry v0.2.0](../benchmark_cards/B5-conv-registry_v0.2.0.yaml) | 2026-05-04 |

`DG-1_summary.json` itself was **intentionally not edited** to record this
repatriation, per the immutable-verdict-artefact discipline above. The
authoritative live record of the repatriation is
[`docs/validity_envelope.md`](../../docs/validity_envelope.md) DG-1 row,
which states it explicitly; this README is the index-side cross-reference.

## Conventions

### File naming

```
benchmarks/results/<card_filename_without_yaml>_result.json
benchmarks/results/DG-N_summary.json
```

The per-card result file's basename matches its source card 1:1
(`A1_closed-form-K_v0.1.1.yaml` → `A1_closed-form-K_v0.1.1_result.json`).

### Mutability discipline

| Surface | Mutability | Update mechanism |
|---|---|---|
| `<card_filename>_result.json` | Immutable point-in-time | Supersedure via a new card + new result file. |
| `DG-N_summary.json` | Mutable aggregate / index | In-place refresh when the live carrier card changes (e.g. v0.1.1 → v0.1.2 supersedure); the git log of this file is the authoritative refresh history. |
| This `README.md` | Mutable index | Updated when new result files land or when verdict status of an existing file changes (superseded, deprecated). |

The mutability distinction is the rationale for work-package §6 item 4
"Path L5-b". Adding fields to `DG-1_summary.json` (or any other
`DG-N_summary.json`) post-verdict to record information that wasn't
known at verdict time is **permitted** when the field is index-style
(pointers, repatriation links, supersedure records). It is **not
permitted** to retroactively change a verdict, its evidence path, or any
field that asserts the runner's output at verdict time. The per-card
result JSONs carry the immutable verdict; the summaries are how the
repository's *current understanding* of those verdicts is presented.

### What is NOT here

- Logbook entries about verdicts. Those live in [`logbook/`](../../logbook/).
- Card YAMLs. Those live in [`../benchmark_cards/`](../benchmark_cards/).
- DG-status prose for the public record. That lives in
  [`../../docs/validity_envelope.md`](../../docs/validity_envelope.md).

---

*Last updated: 2026-05-13 (Phase E Track 5.C Path B floor audit result JSON added; cause label `floor-dominated`; D1 v0.1.2 PASS unchanged). Prior update: 2026-05-11 (Path L5-b index file added under work package §6 item 4). CC-BY-4.0 (see ../../LICENSE-docs).*

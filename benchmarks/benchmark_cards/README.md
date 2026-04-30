# `benchmark_cards/`

Benchmark cards live here. Each card is a YAML file with frozen-parameter,
acceptance-criterion, result, failure-mode-log, and stewardship-flag blocks.

## Card schema

The canonical schema is [`SCHEMA.md`](SCHEMA.md) (this directory). A
machine-readable, fully-annotated example is [`_template.yaml`](_template.yaml).
Together they are sufficient to author a syntactically valid card without
consulting source files.

The schema derives from two protocol sections in
[`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md):

- §1 (gauge annotation) — transcribed into the `gauge:` block.
- §4 (parameter freezing) — transcribed into the `frozen_parameters:` block.

The schema lives here, not in `docs/`, because `docs/` is locked by
Sail v0.5 §11 to the five protective documents. The schema is operational
specification, not protective scaffolding.

## Supersedure

No card may be silently edited or deleted post-result. Superseded cards are
retained with a `superseded_by:` annotation; new cards are added as new files.
A `failure_mode_log` entry on the new card explains what changed and why.
See [`SCHEMA.md`](SCHEMA.md) §Supersedure and
[`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md) §4.3.

## Card index

| Card ID | DG | Ledger anchor | Status | File |
|---|---|---|---|---|
| A1 | DG-1 | CL-2026-005 v0.4 Entry 1 (B.1, B.2; B.3 deferred to DG-2) | frozen-awaiting-run | [A1_closed-form-K_v0.1.1.yaml](A1_closed-form-K_v0.1.1.yaml) |
| A3 | DG-1 | CL-2026-005 v0.4 Entry 3 (B.1, B.2 thermal; B.3 deferred to DG-2) | frozen-awaiting-run | [A3_pure-dephasing_v0.1.1.yaml](A3_pure-dephasing_v0.1.1.yaml) |
| A4 | DG-1 | CL-2026-005 v0.4 Entry 4 (B.1 thermal; B.2 deferred to DG-2) | frozen-awaiting-run | [A4_sigma-x-thermal_v0.1.1.yaml](A4_sigma-x-thermal_v0.1.1.yaml) |

The three DG-1 cards are now frozen per [DG-1 work plan v0.1.4](../../plans/dg-1-work-plan_v0.1.4.md) §4 Phase B. Verdicts populate in Phase D. The index is updated atomically when cards are committed, when their `status` field changes per [SCHEMA.md](SCHEMA.md) §Card lifecycle, or when a successor card is added.

### Superseded cards (retained for audit)

| Card ID | Version | Superseded by | Date | Reason |
|---|---|---|---|---|
| A1 | v0.1.0 | [v0.1.1](A1_closed-form-K_v0.1.1.yaml) | 2026-04-30 | Entry 1.B.3 (pseudo-Kraus) deferred to DG-2; Hayden–Sorce 2022 closed form not transcribed. See A1 v0.1.1 `failure_mode_log[0]`. |
| A3 | v0.1.0 | [v0.1.1](A3_pure-dephasing_v0.1.1.yaml) | 2026-04-30 | Entry 3.B.3 (time-dependent shift in non-thermal bath) deferred to DG-2; displacement convention on multi-mode bath under-specified. See A3 v0.1.1 `failure_mode_log[0]`. |
| A4 | v0.1.0 | [v0.1.1](A4_sigma-x-thermal_v0.1.1.yaml) | 2026-04-30 | Entry 4.B.2 (eigenbasis rotation in non-thermal bath) deferred to DG-2; same displacement-convention gap as A3. See A4 v0.1.1 `failure_mode_log[0]`. |

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
| A1 | DG-1 | CL-2026-005 v0.4 Entry 1 | frozen-awaiting-run | [A1_closed-form-K_v0.1.0.yaml](A1_closed-form-K_v0.1.0.yaml) |
| A3 | DG-1 | CL-2026-005 v0.4 Entry 3 | frozen-awaiting-run | [A3_pure-dephasing_v0.1.0.yaml](A3_pure-dephasing_v0.1.0.yaml) |
| A4 | DG-1 | CL-2026-005 v0.4 Entry 4 | frozen-awaiting-run | [A4_sigma-x-thermal_v0.1.0.yaml](A4_sigma-x-thermal_v0.1.0.yaml) |

The three DG-1 cards are now frozen per [DG-1 work plan v0.1.2](../../plans/dg-1-work-plan_v0.1.2.md) §4 Phase B. Verdicts populate in Phase D. The index is updated atomically when cards are committed (or when their `status` field changes per [SCHEMA.md](SCHEMA.md) §Card lifecycle).

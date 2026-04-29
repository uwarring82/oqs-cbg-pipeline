# `benchmark_cards/`

Benchmark cards live here. Each card is a YAML file with a frozen
parameter block, a result block, and a stewardship-flag block.

The card schema is defined in `docs/benchmark_protocol.md` §4
(parameter freezing) plus the schema artefact (planned, not yet drafted).

No card may be silently edited or deleted post-result. Superseded
cards are retained with a `superseded by <new-card-id>` annotation;
new cards are added as new files. See `docs/benchmark_protocol.md` §4.3.

At repository v0.1.0 (initialisation), no cards exist yet.

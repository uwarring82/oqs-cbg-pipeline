# `transcriptions/` - Source-derived operational transcriptions

This directory holds steward-authored transcriptions of external source material into the notation and audit discipline used by this repository.

Transcriptions are operational artefacts. They do not modify the Ledger, Sail, validity envelope, or benchmark cards by themselves. They exist so future benchmark cards and implementation work can cite a stable, repository-local transcription rather than relying on side-channel readings of external papers.

## Contents

| Transcription | Version | Status | Purpose |
|---|---|---|---|
| [Hayden-Sorce 2022 pseudo-Kraus formula](hayden-sorce-2022_pseudokraus_v0.1.1.md) | v0.1.1 | in-use (current) | Adds off-diagonal pseudo-Kraus coverage (§4b, §7a) to the v0.1.0 single-index/diagonal content, repatriating both halves of CL-2026-005 Entry 1.B.3 plus Entry 1.D's off-diagonal generalization claim into the DG-2 path. Source content unchanged from v0.1.0; off-diagonal expression is a Letter-derived consequence. |

### Superseded transcriptions (retained for audit)

| Transcription | Version | Superseded by | Date | Reason |
|---|---|---|---|---|
| [Hayden-Sorce 2022 pseudo-Kraus formula](hayden-sorce-2022_pseudokraus_v0.1.0.md) | v0.1.0 | [v0.1.1](hayden-sorce-2022_pseudokraus_v0.1.1.md) | 2026-05-01 | v0.1.0 covered only the diagonal / single-index pseudo-Kraus form. v0.1.1 extends to off-diagonal pseudo-Kraus (Hermitian coefficient matrix) for the Entry 1.D generalization claim. v0.1.0 remains anchored by frozen Card B1 v0.1.0 ([benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml](../benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml)) per SCHEMA.md §Card lifecycle. |

## Naming

```text
transcriptions/<source-slug>_<scope>_v<MAJOR>.<MINOR>.<PATCH>.md
```

Version bumps are superseding revisions: retain earlier files, add a new file, and mark the current version in this index.

## Authority

A transcription carries no independent scientific authority. Its authority is limited to the cited primary source and the repository-layer decision to use the transcription in cards or code. If a transcription changes a Ledger-bearing claim, the change routes through the relevant Sail/Ledger procedure; otherwise it remains steward-side operational scaffolding.

---

*Last updated: 2026-05-01. CC-BY-4.0 (see ../LICENSE-docs).*

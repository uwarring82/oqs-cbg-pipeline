# `transcriptions/` - Source-derived operational transcriptions

This directory holds steward-authored transcriptions of external source material into the notation and audit discipline used by this repository.

Transcriptions are operational artefacts. They do not modify the Ledger, Sail, validity envelope, or benchmark cards by themselves. They exist so future benchmark cards and implementation work can cite a stable, repository-local transcription rather than relying on side-channel readings of external papers.

## Contents

| Transcription | Version | Status | Purpose |
|---|---|---|---|
| [Hayden-Sorce 2022 pseudo-Kraus formula](hayden-sorce-2022_pseudokraus_v0.1.0.md) | v0.1.0 | in-use | Transcribes the finite-dimensional pseudo-Kraus expression for the canonical Hamiltonian needed to repatriate CL-2026-005 Entry 1.B.3 from DG-2 deferral. Cited by frozen DG-2 Card B1 ([benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml](../benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml)). |

## Naming

```text
transcriptions/<source-slug>_<scope>_v<MAJOR>.<MINOR>.<PATCH>.md
```

Version bumps are superseding revisions: retain earlier files, add a new file, and mark the current version in this index.

## Authority

A transcription carries no independent scientific authority. Its authority is limited to the cited primary source and the repository-layer decision to use the transcription in cards or code. If a transcription changes a Ledger-bearing claim, the change routes through the relevant Sail/Ledger procedure; otherwise it remains steward-side operational scaffolding.

---

*Last updated: 2026-05-01. CC-BY-4.0 (see ../LICENSE-docs).*

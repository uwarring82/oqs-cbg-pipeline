# `transcriptions/` - Source-derived operational transcriptions

This directory holds steward-authored transcriptions of external source material into the notation and audit discipline used by this repository.

Transcriptions are operational artefacts. They do not modify the Ledger, Sail, validity envelope, or benchmark cards by themselves. They exist so future benchmark cards and implementation work can cite a stable, repository-local transcription rather than relying on side-channel readings of external papers.

## Contents

| Transcription | Version | Status | Purpose |
|---|---|---|---|
| [Colla-Breuer-Gasbarri 2025 Companion Sec. IV L4 transcription](colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md) | v0.1.1 | released (current) | Releases the DG-4 Tier-2.B Phase A equation-map for Companion Sec. IV fourth-order TCL terms. Rows §2.3 and §2.8(b) are closed via the explicit chain-reversal-and-swap conversion from repo mixed-order Wick inputs to Companion Eq. (15); §10 is countersigned. Phase B code must still apply that conversion, use direct Eqs. (69)–(73) rather than B.1 standard cumulants, and complete the small-grid verification before code lands. |
| [Hayden-Sorce 2022 pseudo-Kraus formula](hayden-sorce-2022_pseudokraus_v0.1.1.md) | v0.1.1 | in-use (current) | Adds off-diagonal pseudo-Kraus coverage (§4b, §7a) to the v0.1.0 single-index/diagonal content, repatriating both halves of CL-2026-005 Entry 1.B.3 plus Entry 1.D's off-diagonal generalization claim into the DG-2 path. Source content unchanged from v0.1.0; off-diagonal expression is a Letter-derived consequence. |
| [Colla–Breuer–Gasbarri Letter Appendix D](colla-breuer-gasbarri-2025_appendix-d_v0.0.1.md) | v0.0.1 | POPULATED — underdetermined; awaiting Act 2 §4.3 handling selection over §3.1–§3.4 | Gates Council Act 2 deliberation on the displacement-mode convention for CL-2026-005 v0.4 Entries 3.B.3 + 4.B.2 per [subsidiary briefing v0.2.0](../ledger/CL-2026-005_v0.4_council-briefing_displacement-convention.md) §3.5. The Appendix-D-routed source material has been transcribed from the arXiv/APS Letter source; it contains spin-system parity algebra but no displacement-profile convention, so all §3.1–§3.4 candidates remain silent-compatible and Council Act 2 remains required. |

### Superseded transcriptions (retained for audit)

| Transcription | Version | Superseded by | Date | Reason |
|---|---|---|---|---|
| [Colla-Breuer-Gasbarri 2025 Companion Sec. IV L4 transcription](colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.0.md) | v0.1.0 | [v0.1.1](colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md) | 2026-05-12 | v0.1.0 was the pre-release Path-A draft scaffold. v0.1.1 closes the mixed-order Eq. (15) conversion via the chain-reversal-and-swap derivation, countersigns §10, and promotes the transcription to stable Phase-B-consumable status. v0.1.0 is retained as the pre-release predecessor. |
| [Hayden-Sorce 2022 pseudo-Kraus formula](hayden-sorce-2022_pseudokraus_v0.1.0.md) | v0.1.0 | [v0.1.1](hayden-sorce-2022_pseudokraus_v0.1.1.md) | 2026-05-01 | v0.1.0 covered only the diagonal / single-index pseudo-Kraus form. v0.1.1 extends to off-diagonal pseudo-Kraus (Hermitian coefficient matrix) for the Entry 1.D generalization claim. v0.1.0 remains anchored by frozen Card B1 v0.1.0 ([benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml](../benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml)) per SCHEMA.md §Card lifecycle. |

## Naming

```text
transcriptions/<source-slug>_<scope>_v<MAJOR>.<MINOR>.<PATCH>.md
```

Version bumps are superseding revisions: retain earlier files, add a new file, and mark the current version in this index.

## Authority

A transcription carries no independent scientific authority. Its authority is limited to the cited primary source and the repository-layer decision to use the transcription in cards or code. If a transcription changes a Ledger-bearing claim, the change routes through the relevant Sail/Ledger procedure; otherwise it remains steward-side operational scaffolding.

---

*Last updated: 2026-05-12 (Companion Sec. IV L4 transcription released at v0.1.1; v0.1.0 retained as superseded pre-release predecessor). CC-BY-4.0 (see ../LICENSE-docs).*

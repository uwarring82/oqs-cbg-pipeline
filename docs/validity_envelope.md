# Validity Envelope — `oqs-cbg-pipeline`

**Layer:** Repository protective scaffolding (living document)
**Anchor:** Sail v0.5 §9 (Decision Gates DG-1 through DG-5)
**Last updated:** 2026-04-30 (DG-1 PASS; see `logbook/2026-04-30_dg-1-pass.md`)

---

## What this document is

This is the *living* record of the repository's current validity envelope. It records, for each Decision Gate, whether that gate has been passed, what the evidence is, and what the gate's pass implies.

This document is updated atomically with every change in DG status. Changes are recorded with timestamp, commit hash, and the benchmark cards or test results that triggered the status change. The full history is preserved in version control.

## Decision Gate status table

| DG | Description | Status | Evidence | Validity-envelope implication |
|---|---|---|---|---|
| DG-1 | Formula implementation (Entries 1, 3, 4 reproduced numerically) | **PASS** (2026-04-30) | Cards [A1 v0.1.1](../benchmarks/benchmark_cards/A1_closed-form-K_v0.1.1.yaml), [A3 v0.1.1](../benchmarks/benchmark_cards/A3_pure-dephasing_v0.1.1.yaml), [A4 v0.1.1](../benchmarks/benchmark_cards/A4_sigma-x-thermal_v0.1.1.yaml) (verdict commit `44f94a9`); [`benchmarks/results/`](../benchmarks/results/); logbook entry [2026-04-30_dg-1-pass.md](../logbook/2026-04-30_dg-1-pass.md). | Entries 1.B.1, 1.B.2, 3.B.1, 3.B.2 (thermal), 4.B.1 (thermal) are numerically verified at machine precision (`error = 0.0`, well below the cards' acceptance thresholds). Citation of the repository for these specific sub-claims is **supported**, with explicit attribution to the Hayden–Sorce minimal-dissipation gauge per [`docs/benchmark_protocol.md`](benchmark_protocol.md) §1. Entries **1.B.3, 3.B.3, 4.B.2** are deferred to DG-2 per [plan v0.1.4 §1.1](../plans/dg-1-work-plan_v0.1.4.md) operationalisability carve-out (Hayden–Sorce 2022 transcription + displacement convention not available); citation of the repository for those sub-claims is *not* supported at v0.2.0. |
| DG-2 | Fourth-order recursion (K_2–K_4 with structural-identity satisfaction) | NOT YET ATTEMPTED | — | The recursive expansion has not been verified to fourth order in this repository. CL-2026-005 v0.4 Entry 2's "scope-limited" qualifier remains unmitigated by repository evidence. The Entries 1.B.3, 3.B.3, 4.B.2 deferred from DG-1 (per plan v0.1.4 §1.1) are natural repatriation targets for DG-2 once the missing prior-art transcriptions / displacement conventions are available. |
| DG-3 | Cross-method validation (≥2 methods, non-overlapping failure modes) | NOT YET ATTEMPTED | — | No cross-method comparison has been performed. Implementation-readiness pair (`exact_finite_env.py` + `qutip_reference.py`) is *scaffolded but not yet implemented*. |
| DG-4 | Failure envelope (≥1 reproducible, cause-labelled failure regime) | NOT YET ATTEMPTED | — | No failure regime has been identified by the repository. |
| DG-5 | Thermodynamic discriminant (≥1 distinguishable observable in solvable model) | NOT YET ATTEMPTED | — | CL-2026-005 v0.4 Entry 7 remains UNDERDETERMINED. The repository has not yet contributed evidence to the discriminant question. |

## Failure-asymmetry-clearance status (per Sail v0.5 DG-3 distinction)

| Pair | Implementation readiness | Failure-asymmetry clearance |
|---|---|---|
| `exact_finite_env.py` + `qutip_reference.py` | NOT YET IMPLEMENTED | NOT CLEARED (both methods may share finite-truncation/solver assumptions) |

Full failure-asymmetry clearance per Sail v0.5 §5 Tier 3 requires at least one additional method family from a non-overlapping failure-mode class (HEOM, TEMPO, MCTDH, pseudomode/chain-mapping). The current scaffold *does not provide* such a method. Plans for adding one are tracked in the logbook.

## Stewardship-conflict-bound annotations

| Model | Status | Notes |
|---|---|---|
| (none yet, since no Tier 4 cards exist) | — | — |

When Tier 4 trapped-ion benchmark cards are added, models without independent (non-Warring-group) data are tracked here per [`stewardship_conflict.md`](stewardship_conflict.md) Rule 3.

## What this validity envelope authorises

At the current status (2026-04-30, DG-1 PASS):

**Authorised uses of repository outputs:**

- **Citation of DG-1 verified sub-claims** of CL-2026-005 v0.4: specifically Entries 1.B.1 (canonical-Lindblad recovery), 1.B.2 (Markovian Lamb shift), 3.B.1 (no eigenbasis rotation in pure dephasing), 3.B.2 (thermal trivialisation; spin–boson exact result), 4.B.1 (parity-class theorem in thermal regime). Citations must include attribution to the Hayden–Sorce minimal-dissipation gauge per [`docs/benchmark_protocol.md`](benchmark_protocol.md) §1.
- Reproduction of these results from a clean checkout via `python scripts/run_dg1_verdict.py`; the verdict is deterministic and re-runnable at `error = 0.0` machine precision.
- Demonstration of the architectural scaffold (Sail v0.5, Ledger CL-2026-005 v0.4, plans/, schema, cards, logbook) as a worked example of the cards-first ordering discipline.

**Not authorised:**
- Citation of the repository for **Entries 1.B.3, 3.B.3, 4.B.2** — these sub-cases are deferred to DG-2 per [plan v0.1.4 §1.1](../plans/dg-1-work-plan_v0.1.4.md) operationalisability carve-out (the Hayden–Sorce 2022 closed form for 1.B.3, and the displacement-mode convention for 3.B.3 / 4.B.2, were not available at the time of the verdict).
- Citation of the repository for Entry 2 (recursive-series convergence; DG-2 territory), Entry 5 (parity-FDT decomposition; DG-2), Entry 6 (trapped-ion validation; permanent stewardship-conflict-bound), Entry 7 (thermodynamic interpretation; DG-5).
- Citation of any K(t) computation **outside** the DG-1 cards' frozen-parameter regime (α = 0.05, ω_c = 10, T = 0.5 in ω-units; t ∈ [0, 20/ω]; matrix-unit basis; perturbative_order ≤ 2). The validity envelope is bounded by the cards' authorisation scope.
- Cross-method validation against alternative open-quantum-systems methods (DG-3 territory; not attempted).
- Failure-envelope claims about regimes where the implementation might or might not fail (DG-4 territory).

This envelope expands as further Decision Gates pass. The next natural milestones are DG-2 (fourth-order recursion + structural-identity stacking + repatriation of the three operationalisability-deferred sub-claims) and DG-3 (cross-method validation against a method from a non-overlapping failure-mode class).

## Update protocol

1. A change in DG status is triggered by a benchmark card or test suite passing the DG-specific criteria documented in Sail v0.5 §9.
2. The triggering card or test result is committed to the repository before this document is updated.
3. This document is updated in the *same* commit as the status-change announcement in `logbook/`.
4. The commit message includes the DG identifier (e.g. `DG-1: pass`) and the triggering card or test reference.
5. A status downgrade (e.g. discovery that a previously-passed DG was satisfied by a faulty test) is treated identically: triggering evidence committed, then status updated, then logbook entry.

---

*This document is non-optional per Sail v0.5 §11. It must exist at HEAD throughout the repository's lifetime and must be updated atomically with every DG-status change.*

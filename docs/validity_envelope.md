# Validity Envelope — `oqs-cbg-pipeline`

**Layer:** Repository protective scaffolding (living document)
**Anchor:** Sail v0.4 §9 (Decision Gates DG-1 through DG-5)
**Last updated:** 2026-04-29 (repository initialisation)

---

## What this document is

This is the *living* record of the repository's current validity envelope. It records, for each Decision Gate, whether that gate has been passed, what the evidence is, and what the gate's pass implies.

This document is updated atomically with every change in DG status. Changes are recorded with timestamp, commit hash, and the benchmark cards or test results that triggered the status change. The full history is preserved in version control.

## Decision Gate status table

| DG | Description | Status | Evidence | Validity-envelope implication |
|---|---|---|---|---|
| DG-1 | Formula implementation (Entries 1, 3, 4 reproduced numerically) | NOT YET ATTEMPTED | — | None of Entries 1, 3, 4 has been numerically verified by this repository. Citation of the repository for these entries' numerical content is not supported. |
| DG-2 | Fourth-order recursion (K_2–K_4 with structural-identity satisfaction) | NOT YET ATTEMPTED | — | The recursive expansion has not been verified to fourth order in this repository. CL-2026-005 v0.4 Entry 2's "scope-limited" qualifier remains unmitigated by repository evidence. |
| DG-3 | Cross-method validation (≥2 methods, non-overlapping failure modes) | NOT YET ATTEMPTED | — | No cross-method comparison has been performed. Implementation-readiness pair (`exact_finite_env.py` + `qutip_reference.py`) is *scaffolded but not yet implemented*. |
| DG-4 | Failure envelope (≥1 reproducible, cause-labelled failure regime) | NOT YET ATTEMPTED | — | No failure regime has been identified by the repository. |
| DG-5 | Thermodynamic discriminant (≥1 distinguishable observable in solvable model) | NOT YET ATTEMPTED | — | CL-2026-005 v0.4 Entry 7 remains UNDERDETERMINED. The repository has not yet contributed evidence to the discriminant question. |

## Failure-asymmetry-clearance status (per Sail v0.4 DG-3 distinction)

| Pair | Implementation readiness | Failure-asymmetry clearance |
|---|---|---|
| `exact_finite_env.py` + `qutip_reference.py` | NOT YET IMPLEMENTED | NOT CLEARED (both methods may share finite-truncation/solver assumptions) |

Full failure-asymmetry clearance per Sail v0.4 §5 Tier 3 requires at least one additional method family from a non-overlapping failure-mode class (HEOM, TEMPO, MCTDH, pseudomode/chain-mapping). The current scaffold *does not provide* such a method. Plans for adding one are tracked in the logbook.

## Stewardship-conflict-bound annotations

| Model | Status | Notes |
|---|---|---|
| (none yet, since no Tier 4 cards exist) | — | — |

When Tier 4 trapped-ion benchmark cards are added, models without independent (non-Warring-group) data are tracked here per [`stewardship_conflict.md`](stewardship_conflict.md) Rule 3.

## What this validity envelope authorises

At the current status (2026-04-29, repository initialisation):

**Authorised uses of repository outputs:**
- None for scientific citation. The repository contains no scientific outputs at this version.
- Demonstration of the architectural scaffold (this document, Sail v0.4, Ledger v0.4) for review purposes.

**Not authorised:**
- Citation of any K(t) computation (none exists yet).
- Citation of any benchmark result (none exists yet).
- Citation of the repository as evidence for any claim about CBG framework validity (no evidence has been produced).

This envelope expands as Decision Gates pass. The next milestone is DG-1, which gates citation of repository numerical reproductions of CL-2026-005 v0.4 Entries 1, 3, 4.

## Update protocol

1. A change in DG status is triggered by a benchmark card or test suite passing the DG-specific criteria documented in Sail v0.4 §9.
2. The triggering card or test result is committed to the repository before this document is updated.
3. This document is updated in the *same* commit as the status-change announcement in `logbook/`.
4. The commit message includes the DG identifier (e.g. `DG-1: pass`) and the triggering card or test reference.
5. A status downgrade (e.g. discovery that a previously-passed DG was satisfied by a faulty test) is treated identically: triggering evidence committed, then status updated, then logbook entry.

---

*This document is non-optional per Sail v0.4 §11. It must exist at HEAD throughout the repository's lifetime and must be updated atomically with every DG-status change.*

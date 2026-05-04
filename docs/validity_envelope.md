# Validity Envelope — `oqs-cbg-pipeline`

**Layer:** Repository protective scaffolding (living document)
**Anchor:** Sail v0.5 §9 (Decision Gates DG-1 through DG-5)
**Last updated:** 2026-05-04 (DG-2 PASS — 4 of 4 sub-claims PASS under Council Act 2 cleared registry; see `logbook/2026-05-04_dg-2-pass-envelope.md`)

---

## What this document is

This is the *living* record of the repository's current validity envelope. It records, for each Decision Gate, whether that gate has been passed, what the evidence is, and what the gate's pass implies.

This document is updated atomically with every change in DG status. Changes are recorded with timestamp, commit hash, and the benchmark cards or test results that triggered the status change. The full history is preserved in version control.

## Decision Gate status table

| DG | Description | Status | Evidence | Validity-envelope implication |
|---|---|---|---|---|
| DG-1 | Formula implementation (Entries 1, 3, 4 reproduced numerically) | **PASS** (2026-04-30) | Cards [A1 v0.1.1](../benchmarks/benchmark_cards/A1_closed-form-K_v0.1.1.yaml), [A3 v0.1.1](../benchmarks/benchmark_cards/A3_pure-dephasing_v0.1.1.yaml), [A4 v0.1.1](../benchmarks/benchmark_cards/A4_sigma-x-thermal_v0.1.1.yaml) (verdict commit `44f94a9`); [`benchmarks/results/`](../benchmarks/results/); logbook entry [2026-04-30_dg-1-pass.md](../logbook/2026-04-30_dg-1-pass.md). | Entries 1.B.1, 1.B.2, 3.B.1, 3.B.2 (thermal), 4.B.1 (thermal) are numerically verified at machine precision (`error = 0.0`, well below the cards' acceptance thresholds). Citation of the repository for these specific sub-claims is **supported**, with explicit attribution to the Hayden–Sorce minimal-dissipation gauge per [`docs/benchmark_protocol.md`](benchmark_protocol.md) §1. (Entries 1.B.3, 3.B.3, 4.B.2, originally deferred from DG-1 per [plan v0.1.4 §1.1](../plans/dg-1-work-plan_v0.1.4.md) operationalisability carve-out, were repatriated to DG-2 and PASSed on 2026-05-04 under the Council Act 2 cleared registry — see DG-2 row.) |
| DG-2 | Fourth-order recursion (K_2–K_4 with structural-identity satisfaction) | **PASS — 4 of 4 sub-claims under Council-cleared registry** (2026-05-04) | Cards [B1 v0.1.0](../benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml) (verdict commit `4502863`), [B2 v0.1.0](../benchmarks/benchmark_cards/B2_pseudo-kraus-offdiagonal_v0.1.0.yaml) (verdict commit `9febfed`), [B3 v0.1.0](../benchmarks/benchmark_cards/B3_cross-basis-structural-identity_v0.1.0.yaml) (verdict commit `b46a4e4`), [B4-conv-registry v0.1.0](../benchmarks/benchmark_cards/B4-conv-registry_v0.1.0.yaml) (verdict commit `62e44d0`), [B5-conv-registry v0.2.0](../benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml) (verdict commit `6352891`); [`benchmarks/results/`](../benchmarks/results/); logbook entries [2026-05-01_dg-2-b1-pass.md](../logbook/2026-05-01_dg-2-b1-pass.md), [2026-05-04_dg-2-b2-pass.md](../logbook/2026-05-04_dg-2-b2-pass.md), [2026-05-04_dg-2-b3-pass.md](../logbook/2026-05-04_dg-2-b3-pass.md), [2026-05-04_dg-2-b4-conv-registry-pass.md](../logbook/2026-05-04_dg-2-b4-conv-registry-pass.md), [2026-05-04_dg-2-b5-conv-registry-pass.md](../logbook/2026-05-04_dg-2-b5-conv-registry-pass.md); subsidiary briefing v0.3.0 + Act 1 + Act 2 deliberation transcripts. | All four DG-2 structural-identity sub-claim families are operationally verified at machine precision: (i) **Entry 1.A** basis-independence of `K_from_generator` at d = 2 (matrix-unit basis vs su(d)-generator basis = normalized Pauli; Card B3); (ii) **Entry 1.B.3 diagonal** half — pseudo-Kraus reduction to Hayden–Sorce 2022 H_HS for diagonal coefficients (Card B1); (iii) **Entry 1.B.3 off-diagonal** half + **Entry 1.D** off-diagonal `omega_{ij}` generalisation claim (Card B2); (iv) **Entries 3.B.3 + 4.B.2** time-dependent shift (σ_z coupling) and eigenbasis rotation (σ_x coupling) under coherently-displaced bath, verified across the four Council-cleared displacement profiles (`delta-omega_c`, `delta-omega_S`, `sqrt-J`, `gaussian`; B4 + B5). Citation of the repository for Entries **1.A, 1.B.3 (both halves), 1.D, 3.B.3, 4.B.2** is now **supported**, with explicit attribution to the Hayden–Sorce minimal-dissipation gauge and the displacement-profile registry. Citations of Entries 3.B.3 / 4.B.2 must additionally name the registered displacement profile (one of the four cleared keys) under which the sub-claim is verified. The fourth-order recursion *proper* (K_2 through K_4 numerically computed at perturbative_order ≥ 4 with structural-identity stacking) has not been attempted; the verified sub-claims are at perturbative_order = 0 (algebraic-map cards: B1 / B2 / B3) or perturbative_order = 2 (dynamical cards: B4 / B5). CL-2026-005 v0.4 Entry 2's "scope-limited" qualifier therefore remains partially unmitigated: the structural identities Entry 2 relies on are now reproducible, but the recursive K_n computation at order 4 is not yet operational. The displacement-profile registry is Council-cleared per the §6.1 registry-clearance-gate (subsidiary briefing v0.3.0); registry additions or removals require fresh Council clearance and would trigger a re-read of the Entries 3.B.3 / 4.B.2 authorisation under the extended set. |
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

At the current status (2026-05-04, DG-1 PASS + DG-2 PASS under Council-cleared registry):

**Authorised uses of repository outputs:**

- **Citation of DG-1 verified sub-claims** of CL-2026-005 v0.4: specifically Entries 1.B.1 (canonical-Lindblad recovery), 1.B.2 (Markovian Lamb shift), 3.B.1 (no eigenbasis rotation in pure dephasing), 3.B.2 (thermal trivialisation; spin–boson exact result), 4.B.1 (parity-class theorem in thermal regime). Citations must include attribution to the Hayden–Sorce minimal-dissipation gauge per [`docs/benchmark_protocol.md`](benchmark_protocol.md) §1.
- **Citation of DG-2 verified sub-claims** of CL-2026-005 v0.4:
  - Entry 1.A (basis-independence of `K_from_generator` under change of complete Hilbert–Schmidt-orthonormal basis at d = 2; verified for the matrix-unit and normalized-Pauli bases via Card B3 v0.1.0).
  - Entry 1.B.3 *diagonal* half (pseudo-Kraus reduction to the Hayden–Sorce 2022 closed-form H_HS for diagonal coefficients; Card B1 v0.1.0).
  - Entry 1.B.3 *off-diagonal* half + Entry 1.D ("the new formula generalises the prior result to the off-diagonal `omega_{ij}` case"; Card B2 v0.1.0).
  - **Entry 3.B.3** (time-dependent shift in non-thermal coherently-displaced bath, pure-dephasing model; Card B4-conv-registry v0.1.0). The shift `ω_r(t) - ω = 2 D̄_1(t)` is verified at machine precision under each of the four Council-cleared displacement profiles.
  - **Entry 4.B.2** (eigenbasis rotation in non-thermal coherently-displaced bath, σ_x coupling model; Card B5-conv-registry v0.2.0). The transverse vector `(b(t), c(t)) = (D̄_1(t), 0)` is verified at exact-zero error under each of the four Council-cleared displacement profiles.
  Citations of Entries 3.B.3 / 4.B.2 **must additionally name the registered displacement profile** under which the sub-claim is verified — one of `delta-omega_c` (§3.1 single-mode at cutoff), `delta-omega_S` (§3.2 single-mode at system Bohr), `sqrt-J` (§3.3 broadband ∝ √(J(ω))), `gaussian` (§3.4 Gaussian envelope at (ω_d, Δω)), per the Council Act 2 (2026-05-04) clearance under handling (c) (subsidiary briefing v0.3.0 §3.1–§3.4 + §6.1). All citations of DG-2 sub-claims must include attribution to the Hayden–Sorce minimal-dissipation gauge and, where the basis-independence claim is material, the d = 2 / matrix-unit + su(d)-generator scope.
- Reproduction of these results from a clean checkout via `python scripts/run_dg1_verdict.py` (DG-1 cards) and `pytest tests/test_benchmark_card.py` (DG-2 cards); both are deterministic and re-runnable at machine precision. The DG-2 dynamical cards (B4 / B5) achieve exact-zero or machine-precision verdicts via the single-source-of-truth pattern in which the runner's K_1 computation and the predicted-shift / predicted-transverse-vector handlers consume the same `cbg.cumulants.D_bar_1` array.
- Demonstration of the architectural scaffold (Sail v0.5, Ledger CL-2026-005 v0.4, plans/, schema, cards, logbook, two-act Council deliberation discipline, displacement-profile registry-clearance-gate) as a worked example of the cards-first ordering combined with the (c)-discipline conflict-mitigation pattern.

**Not authorised:**
- Citation of the repository for Entry 2 (recursive-series convergence at fourth order; the structural identities Entry 2 invokes are now operationally verified via B1 / B2 / B3 / B4 / B5, but the K_2–K_4 numerical recursion at perturbative_order ≥ 4 has not been attempted), Entry 5 (parity-FDT decomposition; DG-2 territory at the recursive-perturbative layer), Entry 6 (trapped-ion validation; permanent stewardship-conflict-bound), Entry 7 (thermodynamic interpretation; DG-5).
- Citation of Entries 3.B.3 / 4.B.2 *under a displacement profile NOT in the Council-cleared registry*. The four cleared profiles are exhaustive of the v0.1.0 admissible set; any non-listed profile (including profiles transcribed from successor papers, profiles parameterised differently from the four registered constructors, or ad-hoc Steward-discretion choices) requires fresh Council clearance per the subsidiary briefing v0.3.0 §6.1 registry-clearance-gate before it can underwrite citation.
- Citation of any K(t) computation **outside** the DG-1 cards' frozen-parameter regime (α = 0.05, ω_c = 10, T = 0.5 in ω-units; t ∈ [0, 20/ω]; matrix-unit basis; perturbative_order ≤ 2) for the thermal sub-claims, or **outside** the DG-2 algebraic_map cards' frozen-fixture scope (d = 2; n = 2 V_i operators for off-diagonal pseudo-Kraus; β = 0.5 / a = 0.5 / b = 0.5 fixture parameters; matrix-unit + su(d)-generator bases) for the structural-identity sub-claims, or **outside** the DG-2 dynamical-card cleared-registry scope (α = 0.05, ω_c = 10, ω_S = 1.0 in ω-units; α₀ = 1.0 displacement amplitude; ω_d = 5.0, Δω = 2.0 for the Gaussian profile; t ∈ [0, 20/ω]; perturbative_order = 2) for Entries 3.B.3 / 4.B.2. The validity envelope is bounded by the cards' authorisation scope; the Council Act 2 (c)-discipline binds Entries 3.B.3 / 4.B.2 to the *specific cleared registry*, not the broader physical-convention space.
- Cross-method validation against alternative open-quantum-systems methods (DG-3 territory; not attempted).
- Failure-envelope claims about regimes where the implementation might or might not fail (DG-4 territory).

This envelope expands as further Decision Gates pass. The next natural milestones are: the K_2–K_4 numerical recursion at perturbative_order ≥ 4 with structural-identity stacking on top of the now-verified Entry 1.A basis-independence and Entries 1.B.3 / 1.D pseudo-Kraus identities (which would mitigate the residual "scope-limited" qualifier on Entry 2), and DG-3 (cross-method validation against a method from a non-overlapping failure-mode class).

## Update protocol

1. A change in DG status is triggered by a benchmark card or test suite passing the DG-specific criteria documented in Sail v0.5 §9.
2. The triggering card or test result is committed to the repository before this document is updated.
3. This document is updated in the *same* commit as the status-change announcement in `logbook/`.
4. The commit message includes the DG identifier (e.g. `DG-1: pass`) and the triggering card or test reference.
5. A status downgrade (e.g. discovery that a previously-passed DG was satisfied by a faulty test) is treated identically: triggering evidence committed, then status updated, then logbook entry.

---

*This document is non-optional per Sail v0.5 §11. It must exist at HEAD throughout the repository's lifetime and must be updated atomically with every DG-status change.*

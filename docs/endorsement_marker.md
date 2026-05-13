# Endorsement Marker — `oqs-cbg-pipeline`

**Layer:** Sail-internal repository
**Anchor:** [Sail v0.5](../sail/sail-cbg-pipeline_v0.5.md), which itself anchors to [CL-2026-005 v0.4](../ledger/CL-2026-005_v0.4.md) (Council-cleared 2026-04-29, session CL-2026-005-DEL-001)
**Steward:** U. Warring (Physikalisches Institut, Albert-Ludwigs-Universität Freiburg)

## What this repository is

This repository implements the numerical pipeline scoped by the Sail "Towards a Decision-Forcing Numerical Pipeline for Non-Markovian Open Quantum Dynamics" (v0.5). It is a Sail-internal artefact. It is *not* a Ledger entry, *not* a coastline, and *not* a validation claim about the underlying Colla–Breuer–Gasbarri (CBG) framework.

## What this repository is not

- It is *not* an endorsement of the minimal-dissipation effective Hamiltonian K(t) as the unique physical Hamiltonian of a strongly-coupled open quantum system. K(t) is a coordinate-dependent object under a chosen gauge. See [`do_not_cite_as.md`](do_not_cite_as.md).
- It is *not* an adjudication between competing strong-coupling thermodynamic frameworks (Hayden–Sorce minimal-dissipation, Hamiltonian of mean force, polaron, Mori). Adjudication is the discriminant question for CL-2026-005 Entry 7 and is *out of scope* for unilateral repository action.
- It is *not* a substitute for fresh Council deliberation when its outputs bear on Ledger entries. See "Unidirectional consumption rule" below.

## Unidirectional consumption rule

The repository consumes [CL-2026-005 v0.4](../ledger/CL-2026-005_v0.4.md) as a stable input. Findings produced here that bear on the Ledger — notably any DG-5 outcomes affecting Entry 7's UNDERDETERMINED classification — are routed via fresh Council deliberation, not via repository revision.

The relationship is:

```
Council-cleared Ledger  ──►  Sail  ──►  Repository
                                          │
                                          ▼
                                   discriminant report
                                          │
                                          ▼
                              fresh Council deliberation
                                          │
                                          ▼
                              (possibly) revised Ledger
```

The repository never modifies the Ledger directly. The arrow is one-way at every layer except via Council deliberation.

## Inherited protective measures

This repository inherits, verbatim, two Council-ratified protective measures from CL-2026-005 v0.4 (session CL-2026-005-DEL-001):

- **(G1)** The "Do not cite as" guard, expanded in [`do_not_cite_as.md`](do_not_cite_as.md).
- **(G2)** Continued steward-conflict triple-flagging on Entry 6, operationalised here in [`stewardship_conflict.md`](stewardship_conflict.md).

Code that runs without all five protective documents (`endorsement_marker.md`, `stewardship_conflict.md`, `do_not_cite_as.md`, `validity_envelope.md`, `benchmark_protocol.md`) being present at HEAD is structurally non-compliant with the Sail's discipline and must not be released, archived, or cited. The first three are inherited from CL-2026-005 v0.4 (G1 + G2); the latter two are mandated by Sail v0.5 §11 as operational scaffolding.

## Scope

The repository's scope is determined by the Sail's Decision Gates DG-1 through DG-5 (Sail §9). The repository's outputs at any given time are valid only within the validity envelope established by those gates' status, recorded in [`validity_envelope.md`](validity_envelope.md).

## Citation

If you use any output of this repository, cite the underlying papers (Colla, Breuer, Gasbarri, Phys. Rev. A **112**, L050203 (2025) and Phys. Rev. A **112**, 052222 (2025)) and the repository version. Do not cite the repository as evidence for any claim outside the validity envelope of the relevant Decision Gates' status. See [`do_not_cite_as.md`](do_not_cite_as.md) for the full guard.

---

*Repository version: post-`v0.5.0` (metadata 0.3.0.dev0). Not production-ready. DG-1 PASS (2026-04-30, tag `v0.2.0`); DG-2 structural sub-claims PASS (2026-05-04); DG-4 PASS at D1 v0.1.2 (2026-05-06; picture-fixed Path B numerical L_4; supersedes the v0.1.1 verdict at tag `v0.5.0` that was downgraded on review the same day); post-verdict thermal-Gaussian n=4 public route landed 2026-05-13; Phase E Track 5.C Path B floor audit landed `floor-dominated` 2026-05-13 (D1 v0.1.2 PASS unchanged, Phase E routing pivoted away from Path A / Path B agreement claim). DG-3 runner-complete; DG-5 scope-definition. Outputs are bounded by the live status in [`validity_envelope.md`](validity_envelope.md).*

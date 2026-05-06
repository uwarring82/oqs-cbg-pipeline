# Do Not Cite As — `oqs-cbg-pipeline`

**Layer:** Repository protective scaffolding
**Anchor:** Council ratification G1 (CL-2026-005 v0.4, session CL-2026-005-DEL-001), inherited verbatim from CL-2026-005 v0.4 §"Do not cite as" and Sail v0.5 §0.

---

## The guard

This repository, its outputs, its plots, its benchmark cards, and its archived results **must not be cited as** evidence that the minimal-dissipation Hamiltonian K(t) is the unique physical Hamiltonian of a strongly-coupled open quantum system.

The repository supports only the following conditional claim:

> *Given the Hayden–Sorce minimal-dissipation gauge, the Colla–Breuer–Gasbarri construction provides a basis-independent expression and a recursive TCL expansion with structural consequences itemised in CL-2026-005 v0.4 Entries 1–5; this repository implements that construction numerically and benchmarks it against independent methods within the validity envelope established by the current status of Decision Gates DG-1 through DG-5.*

That is the upper bound of what may be cited. Statements stronger than this are not supported by this repository, regardless of how cleanly the numerics agree with experiment, how stable the perturbative series appears, or how attractive the thermodynamic interpretation is.

## Specific prohibitions

The following uses are explicitly disallowed, by inheritance from CL-2026-005 v0.4 G1 and from Sail v0.5 §0:

1. **Reification.** Do not cite K(t) computed by this repository as "the physical Hamiltonian" of the open system. K(t) is a coordinate-dependent object under a chosen gauge.
2. **Framework adjudication.** Do not cite agreement between this repository's K(t) and any specific experimental observation as evidence that the Hayden–Sorce gauge is preferable to the Hamiltonian of mean force, polaron-transformed, Mori-projector, or other gauges. Adjudication is the discriminant question for CL-2026-005 Entry 7 and proceeds only via fresh Council deliberation.
3. **Universal validity.** Do not cite this repository as evidence that the CBG perturbative pipeline is convergent or reliable in arbitrary strong-coupling regimes. CL-2026-005 Entry 2 is COMPATIBLE *scope-limited*; DG-4 records a finite Path B numerical failure-envelope witness, not an analytic convergence guarantee.
4. **Trapped-ion empirical claims absent stewardship-conflict flag.** Do not cite Tier 4 trapped-ion benchmarks without the stewardship-conflict flag attached. See [`stewardship_conflict.md`](stewardship_conflict.md).
5. **DG-5 thermodynamic interpretation absent Council re-deliberation.** Do not cite DG-5 outputs as having transitioned CL-2026-005 Entry 7 from UNDERDETERMINED to COMPATIBLE or INCONSISTENT. Only fresh Council deliberation can effect that transition.

## What may be cited

The following uses are appropriate:

- **Method citation.** "Numerical implementation of the Colla–Breuer–Gasbarri recursive effective-Hamiltonian construction, as described in [Sail v0.5]." This cites the *implementation*, not a physical claim.
- **Algebraic results.** Tier 1 verifications (CL-2026-005 v0.4 Entries 1, 3, 4 reproduced numerically). These are theorem-level and well-supported.
- **Constructive results within stated scope.** Tier 2 fourth-order recursion outputs, when cited with the structural-identity check that confirmed them and the convergence-diagnostic envelope.
- **Cross-method comparison results.** Tier 3 benchmark cards, when cited with the failure-asymmetry-clearance status (per Sail v0.5 DG-3 distinction between *implementation readiness* and *failure-asymmetry clearance*).
- **Failure-mode reports.** DG-4 failure-envelope identifications, with cause labels.
- **Discriminant reports** (DG-5), explicitly framed as *input to* a Council deliberation, not as a deliberation outcome.

## Format for citations

When citing this repository:

```
oqs-cbg-pipeline (version X.Y.Z), implementation of the Colla–Breuer–Gasbarri
minimal-dissipation effective-Hamiltonian framework. Steward: U. Warring.
Validity envelope per docs/validity_envelope.md as of commit <hash>.
Anchored to CL-2026-005 v0.4 (Council-cleared 2026-04-29).
DOI: <Zenodo DOI once minted>.
```

Citing without the validity-envelope reference and the Ledger anchor is a partial citation and does not transfer the protective scope.

---

*This document is non-optional per Sail v0.5 §11. It must exist at HEAD before any code is committed to the repository.*

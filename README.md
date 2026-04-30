# `oqs-cbg-pipeline`

**Numerical pipeline for the Colla–Breuer–Gasbarri minimal-dissipation effective-Hamiltonian construction in non-Markovian open quantum systems.**

[![Status](https://img.shields.io/badge/status-scaffold--v0.1.0-orange)](docs/validity_envelope.md)
[![Sail](https://img.shields.io/badge/sail-v0.5-blue)](sail/sail-cbg-pipeline_v0.5.md)
[![Ledger](https://img.shields.io/badge/ledger-CL--2026--005%20v0.4%20cleared-green)](ledger/CL-2026-005_v0.4.md)
[![Code license](https://img.shields.io/badge/code%20license-MIT-blue)](LICENSE)
[![Docs license](https://img.shields.io/badge/docs%20license-CC--BY--4.0-blue)](LICENSE-docs)

---

## What this is

A Sail-internal repository implementing the construction of:

> A. Colla, H.-P. Breuer, G. Gasbarri,
> *Unveiling coherent dynamics in non-Markovian open quantum systems: Exact expression and recursive perturbation expansion*,
> **Phys. Rev. A 112, L050203 (2025)**. DOI: [10.1103/n5nl-gn1y](https://doi.org/10.1103/n5nl-gn1y)
>
> A. Colla, H.-P. Breuer, G. Gasbarri,
> *Recursive perturbation approach to time-convolutionless master equations: Explicit construction of generalized Lindblad generators for arbitrary open systems*,
> **Phys. Rev. A 112, 052222 (2025)**. DOI: [10.1103/9j8d-jxgd](https://doi.org/10.1103/9j8d-jxgd)

The pipeline computes the minimal-dissipation effective Hamiltonian K(t), its perturbative expansion K_n(t), and the canonical TCL generator at every order; benchmarks against independent open-system methods; and forces decisions about the validity envelope of the construction.

A static public landing page for the repository is tracked at [`index.html`](index.html).

## What this is *not*

- **Not** a claim that K(t) is the unique physical Hamiltonian of an open system. K(t) is a coordinate-dependent object under the Hayden–Sorce minimal-dissipation gauge. See [`docs/do_not_cite_as.md`](docs/do_not_cite_as.md).
- **Not** an adjudication between competing strong-coupling thermodynamic frameworks. That question is the discriminant for CL-2026-005 Entry 7 and is reserved for fresh Council deliberation.
- **Not** production-ready. At v0.1.0, no Decision Gate has been passed; module bodies are stubs. See [`docs/validity_envelope.md`](docs/validity_envelope.md) for the live status.

## Anchor chain

```
Two peer-reviewed papers (Phys. Rev. A 112, 2025)
        │
        ▼
CL-2026-005 v0.4   (Council-cleared 2026-04-29, immutable)
        │
        ▼
Sail v0.5          (programme-setting, local stewardship)
        │
        ▼
This repository    (numerical implementation, scaffold v0.1.0)
```

Every layer consumes the layer above unidirectionally. The repository never modifies the Ledger; outputs that bear on the Ledger route via fresh Council deliberation. See [`docs/endorsement_marker.md`](docs/endorsement_marker.md).

## Decision Gate status

| DG | Description | Status |
|---|---|---|
| DG-1 | Formula implementation (CL-2026-005 Entries 1, 3, 4 reproduced) | NOT YET ATTEMPTED |
| DG-2 | Fourth-order recursion + structural identity | NOT YET ATTEMPTED |
| DG-3 | Cross-method validation (≥2 methods, non-overlapping failures) | NOT YET ATTEMPTED |
| DG-4 | Failure envelope (cause-labelled, reproducible) | NOT YET ATTEMPTED |
| DG-5 | Thermodynamic discriminant (distinguishable observable) | NOT YET ATTEMPTED |

Live status: [`docs/validity_envelope.md`](docs/validity_envelope.md).

## Reading order

1. [`docs/endorsement_marker.md`](docs/endorsement_marker.md) — what the repository is for.
2. [`docs/do_not_cite_as.md`](docs/do_not_cite_as.md) — what may and may not be cited.
3. [`docs/stewardship_conflict.md`](docs/stewardship_conflict.md) — why some Tier 4 results are flagged.
4. [`sail/sail-cbg-pipeline_v0.5.md`](sail/sail-cbg-pipeline_v0.5.md) — the active programme.
5. [`ledger/CL-2026-005_v0.4.md`](ledger/CL-2026-005_v0.4.md) — the Council-cleared anchor.
6. [`docs/validity_envelope.md`](docs/validity_envelope.md) — current DG status.
7. [`docs/benchmark_protocol.md`](docs/benchmark_protocol.md) — coordinate annotations, failure-mode taxonomy, parameter freezing.
8. [`plans/README.md`](plans/README.md) and the active DG plan (currently [`plans/dg-1-work-plan_v0.1.0.md`](plans/dg-1-work-plan_v0.1.0.md)) — operational decomposition of the next Decision Gate.
9. Module docstrings in `cbg/`, `models/`, `numerical/`, `benchmarks/`, `reporting/`.

## Repository layout

```
oqs-cbg-pipeline/
├── index.html        # static public landing page
├── docs/             # protective scaffolding (non-optional, gates code)
├── ledger/           # vendored CL-2026-005 v0.4 + briefing + deliberation log
├── sail/             # active Sail v0.5
├── cbg/              # CBG construction (basis, K, recursion, cumulants, bath, diag)
├── models/           # microscopic open-system models with declared structural constraints
├── numerical/        # time-grid integration; deliberately separate from cbg/bath_correlations
├── benchmarks/       # cross-method references; benchmark_cards/ holds YAML cards
├── reporting/        # benchmark-card I/O and validity-envelope reporting
├── plans/            # steward-authored revisable work plans (DG-1 onwards)
├── tests/            # smoke tests (no scientific tests pre-DG-1)
├── logbook/          # immutable repository event log
└── .github/          # CI workflows
```

## Citation

To cite the repository at a specific commit:

```
oqs-cbg-pipeline (v0.1.0, commit <hash>), implementation of the
Colla–Breuer–Gasbarri minimal-dissipation effective-Hamiltonian framework.
Steward: U. Warring (Albert-Ludwigs-Universität Freiburg).
Validity envelope per docs/validity_envelope.md as of commit <hash>.
Anchored to CL-2026-005 v0.4 (Council-cleared 2026-04-29).
DOI: <Zenodo DOI to be minted at first non-trivial release>.
```

A machine-readable citation is in [`CITATION.cff`](CITATION.cff). FAIR metadata is in [`codemeta.json`](codemeta.json) and [`.zenodo.json`](.zenodo.json).

**Citation prohibitions** are enumerated in [`docs/do_not_cite_as.md`](docs/do_not_cite_as.md). Citing the repository without the validity-envelope reference and the Ledger anchor is a partial citation and does not transfer the protective scope.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Contributions to scientific layers must respect the Sail's discipline (parameter-freezing, coordinate-choice annotations, stewardship flags, DG cause labels). Contributions to protective scaffolding require either a Sail revision (steward action) or a fresh Council deliberation (depending on scope).

## License

- Code: [MIT](LICENSE).
- Documentation, Ledger artefacts, Sail, logbook, and benchmark cards: [CC-BY-4.0](LICENSE-docs).

The dual licensing reflects FAIR-Reusable practice: code that may be modified and reused, documentation that must be cited but may be redistributed.

## Steward

U. Warring, Physikalisches Institut, Albert-Ludwigs-Universität Freiburg. ORCID to be added at first non-trivial release.

The steward holds a structural conflict on CL-2026-005 Entry 6 (co-authorship of the cited experimental paper). The conflict is operationalised at the repository level in [`docs/stewardship_conflict.md`](docs/stewardship_conflict.md).

---

*Repository version: v0.1.0. Initialised 2026-04-29. Sail v0.5. Ledger CL-2026-005 v0.4. No Decision Gate has yet been passed at this version.*

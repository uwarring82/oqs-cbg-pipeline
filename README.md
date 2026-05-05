# `oqs-cbg-pipeline`

**Numerical pipeline for the Colla–Breuer–Gasbarri minimal-dissipation effective-Hamiltonian construction in non-Markovian open quantum systems.**

[![Status](https://img.shields.io/badge/status-DG--1%20PASS%20%7C%20DG--2%20structural%20PASS-green)](docs/validity_envelope.md)
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

The implemented surface computes the minimal-dissipation effective Hamiltonian K(t) from TCL generators, runs the frozen DG-1 and DG-2 structural benchmark cards, and records exactly which sub-claims are supported inside the validity envelope. Full fourth-order recursive K_n(t) computation, cross-method validation, failure-envelope discovery, and thermodynamic-discriminant work remain future milestones.

A static public landing page for the repository is tracked at [`index.html`](index.html).

## What this is *not*

- **Not** a claim that K(t) is the unique physical Hamiltonian of an open system. K(t) is a coordinate-dependent object under the Hayden–Sorce minimal-dissipation gauge. See [`docs/do_not_cite_as.md`](docs/do_not_cite_as.md).
- **Not** an adjudication between competing strong-coupling thermodynamic frameworks. That question is the discriminant for CL-2026-005 Entry 7 and is reserved for fresh Council deliberation.
- **Not** production-ready. DG-1 has passed, and DG-2 structural sub-claims have passed under the Council-cleared displacement-profile registry, but the literal fourth-order K_2-K_4 recursion, DG-3 cross-method validation, DG-4 failure-envelope work, and DG-5 thermodynamic discriminant have not been completed. See [`docs/validity_envelope.md`](docs/validity_envelope.md) for the live status.

## Installation

Requires Python ≥ 3.10. From a repository checkout:

```bash
git clone https://github.com/uwarring82/oqs-cbg-pipeline.git
cd oqs-cbg-pipeline
pip install -e ".[dev]"
```

The `[dev]` extra installs `pytest`, `pytest-cov`, `black`, `ruff`, and `mypy`. The `[docs]` extra installs the Sphinx toolchain. The package depends on `numpy`, `scipy`, `qutip ≥ 4.7`, and `pyyaml`; QuTiP requires a C/C++ toolchain on systems where wheels are not available.

## Quickstart

Verify the install and inspect the package's anchor metadata:

```python
import cbg

print(cbg.__version__)              # package version (PEP 440)
print(cbg.__sail_version__)         # active Sail revision
print(cbg.__ledger_anchor__)        # Council-cleared Ledger entry
```

Construct the minimal-dissipation effective Hamiltonian K from a TCL generator L using Letter Eq. (6):

```python
import numpy as np
from cbg.basis import matrix_unit_basis
from cbg.effective_hamiltonian import K_from_generator

# Toy generator: L[X] = -i [H, X] for a chosen system Hamiltonian H.
H = 0.5 * np.array([[1, 0], [0, -1]], dtype=complex)  # (omega/2) sigma_z

def L(X):
    return -1j * (H @ X - X @ H)

basis = matrix_unit_basis(d=2)
K = K_from_generator(L, basis)
print(K)  # Hermitian effective Hamiltonian; for traceless H, recovers H.
```

Run the smoke tests:

```bash
pytest tests/ -v
```

For a guided introduction aimed at PhD students, open [`cbg-tutorial-for-phd-students_v0.2.html`](cbg-tutorial-for-phd-students_v0.2.html). For the full validated surface and the structural-identity benchmark cards that anchor each Decision Gate, see [`benchmarks/benchmark_cards/`](benchmarks/benchmark_cards/) and [`docs/validity_envelope.md`](docs/validity_envelope.md).

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
This repository    (numerical implementation, bounded by validity envelope)
```

Every layer consumes the layer above unidirectionally. The repository never modifies the Ledger; outputs that bear on the Ledger route via fresh Council deliberation. See [`docs/endorsement_marker.md`](docs/endorsement_marker.md).

## Decision Gate status

| DG | Description | Status |
|---|---|---|
| DG-1 | Formula implementation (CL-2026-005 Entries 1, 3, 4 reproduced) | **PASS** (2026-04-30) |
| DG-2 | Structural identities and displaced-bath registry checks | **STRUCTURAL SUB-CLAIMS PASS** (2026-05-04); literal K_2-K_4 fourth-order recursion pending |
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
8. [`plans/README.md`](plans/README.md) — operational decomposition of Decision Gate work.
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
oqs-cbg-pipeline (0.3.0.dev0, commit <hash>), implementation of the
Colla–Breuer–Gasbarri minimal-dissipation effective-Hamiltonian framework.
Steward: U. Warring (Albert-Ludwigs-Universität Freiburg).
Validity envelope per docs/validity_envelope.md as of commit <hash>.
Anchored to CL-2026-005 v0.4 (Council-cleared 2026-04-29).
DOI: <Zenodo DOI once minted>.
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

*Repository metadata version: 0.3.0.dev0. Initialised 2026-04-29. Sail v0.5. Ledger CL-2026-005 v0.4. DG-1 PASS; DG-2 structural sub-claims PASS; literal K_2-K_4 fourth-order recursion pending.*

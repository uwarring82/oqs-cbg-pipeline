# `oqs-cbg-pipeline`

**Numerical pipeline for the Colla–Breuer–Gasbarri minimal-dissipation effective-Hamiltonian construction in non-Markovian open quantum systems.**

[![Status](https://img.shields.io/badge/status-DG--1%20PASS%20%7C%20DG--2%20structural%20PASS%20%7C%20DG--4%20PASS%20%28v0.1.2%29-green)](docs/validity_envelope.md)
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

The implemented surface computes the minimal-dissipation effective Hamiltonian K(t) from TCL generators, runs the frozen DG-1 and DG-2 structural benchmark cards, runs the picture-fixed Path B DG-4 failure-envelope sweep on D1 v0.1.2 (PASS, 2026-05-06; supersedes the v0.5.0-tagged v0.1.1 verdict that was downgraded on review the same day), and records exactly which sub-claims are supported inside the validity envelope.

Current HEAD is a post-verdict development stage. The DG verdict table has not changed since the DG-4 D1 v0.1.2 PASS, but the analytic fourth-order thermal-Gaussian route has advanced: the Companion Sec. IV L_4 transcription is released at v0.1.1, the n=4 small-grid and physics-oracle cards are current, and the public thermal-Gaussian n=4 route is exposed through `cbg.tcl_recursion.L_n_thermal_at_time(n=4)`, `K_n_thermal_on_grid(n=4)`, `K_total_thermal_on_grid(N_card=4)`, the n=4 dissipator helpers, and the `L_n` shim. This does **not** retroactively change the D1 verdict source: D1 v0.1.2 remains a Path B numerical failure-envelope verdict. The Phase E Track 5.C Path B floor audit (2026-05-13) landed `floor-dominated` — Path B at the D1 production fixture shifts by 24% under truncation tightening, with the three truncation axes pulling in inconsistent directions, so a direct Path A / Path B cross-validation milestone is no longer reachable; Phase E routing now requires Path A as single-sided ground truth, DG-3 Tier-2.A (third method) as Path B's replacement, or a permanent `unclassified-pilot` state. DG-3 failure-asymmetry clearance and DG-5 thermodynamic-discriminant work remain future milestones.

A static public landing page for the repository is tracked at [`index.html`](index.html).

## What this is *not*

- **Not** a claim that K(t) is the unique physical Hamiltonian of an open system. K(t) is a coordinate-dependent object under the Hayden–Sorce minimal-dissipation gauge. See [`docs/do_not_cite_as.md`](docs/do_not_cite_as.md).
- **Not** an adjudication between competing strong-coupling thermodynamic frameworks. That question is the discriminant for CL-2026-005 Entry 7 and is reserved for fresh Council deliberation.
- **Not** production-ready. DG-1 has passed, DG-2 structural sub-claims have passed under the Council-cleared displacement-profile registry, and DG-4 has passed at D1 v0.1.2 (2026-05-06) via picture-fixed Path B numerical L_4 extraction with all four reproducibility perturbations operational and the result JSON audit-complete. (The v0.1.1 PASS verdict tagged `v0.5.0` earlier on the same day was superseded on review; v0.1.2 is the live verdict.) The thermal-Gaussian n=4 public route now exists in `cbg.tcl_recursion`, and the Phase E 5.C Path B floor audit (2026-05-13) characterised that route's reference: Path B at the D1 production fixture is `floor-dominated`, so Phase E routing now requires Path A as single-sided ground truth, DG-3 Tier-2.A (third method) as Path B's replacement, or a permanent `unclassified-pilot` state. Entry-2-wide K_2-K_4 recursion closure, DG-3 failure-asymmetry clearance, and the DG-5 thermodynamic discriminant have not been completed. See [`docs/validity_envelope.md`](docs/validity_envelope.md) for the live status.

## Installation

Requires Python ≥ 3.10. The project is tested across Python 3.10-3.13 in current metadata. From a repository checkout:

```bash
git clone https://github.com/uwarring82/oqs-cbg-pipeline.git
cd oqs-cbg-pipeline
pip install -e ".[dev]"
```

The `[dev]` extra installs `pytest`, `pytest-cov`, `black`, `ruff`, and `mypy`. The `[docs]` extra installs the Sphinx toolchain. The package depends on `numpy`, `scipy`, `qutip ≥ 5.2`, and `pyyaml`; QuTiP requires a C/C++ toolchain on systems where wheels are not available. The `qutip ≥ 5.2` floor provides the in-tree `qutip.solver.heom.HEOMSolver` (HEOM). OQuPy/TEMPO is not a declared dependency: DG-3 Phase F step 1 found OQuPy 0.5.0 pins `numpy<2.0`, incompatible with the repository's numpy-2 / QuTiP-5.2 stack. The active DG-3 route is now HEOM vs pseudomode per [plans/dg-3-work-plan_v0.1.3.md](plans/dg-3-work-plan_v0.1.3.md); OQuPy is dormant unless upstream numpy-2 support lands.

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

Four runnable Jupyter notebooks demonstrate the passed (or partially passed) Decision Gate verdicts end-to-end:

- [`examples/dg1_walkthrough.ipynb`](examples/dg1_walkthrough.ipynb) — DG-1 PASS (Cards A1, A3, A4): closed-form K, pure-dephasing K(t), and the σ_x thermal fixture.
- [`examples/dg2_structural.ipynb`](examples/dg2_structural.ipynb) — DG-2 structural sub-claims PASS (Cards B3, B4-conv-registry): basis-independence on a dissipative generator, and the coherently-displaced bath under one Council-cleared registry profile.
- [`examples/dg3_cross_method.ipynb`](examples/dg3_cross_method.ipynb) — DG-3 RUNNER-COMPLETE (Cards C1, C2): runner reachable on all four C1+C2 fixtures; both currently FAIL convergence in finite-bath truncation, demonstrating the failure-asymmetry-clearance gap.
- [`examples/dg4_walkthrough.ipynb`](examples/dg4_walkthrough.ipynb) — DG-4 PASS at D1 v0.1.2 (Card D1 v0.1.2): picture-fixed Path B numerical L_4 extraction; reduced fixture for fast walkthrough, full frozen run reports `verdict = PASS` with max baseline `r_4 ≈ 47.42`.

See [`examples/README.md`](examples/README.md) for the index.

For the post-verdict n=4 analytic implementation route, start with the released Companion Sec. IV transcription and its derived cards in [`transcriptions/README.md`](transcriptions/README.md). That surface is code-facing and oracle-tested for the thermal-Gaussian scope; it is not itself a new DG verdict.

For a guided introduction aimed at PhD students, open [`cbg-tutorial-for-phd-students_v0.2.html`](cbg-tutorial-for-phd-students_v0.2.html). *Note: the tutorial dates from 2026-04-30, predates DG-2 / DG-4 PASS, and is for theoretical orientation only — refer to [`docs/validity_envelope.md`](docs/validity_envelope.md) for current verdict status.* For the full validated surface and the structural-identity benchmark cards that anchor each Decision Gate, see [`benchmarks/benchmark_cards/`](benchmarks/benchmark_cards/) and [`docs/validity_envelope.md`](docs/validity_envelope.md).

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
| DG-2 | Structural identities and displaced-bath registry checks | **PARTIAL**: structural sub-claims PASS (2026-05-04); thermal-Gaussian n=4 code route now present, but Entry-2-wide K_2-K_4 recursion closure is not yet authorised |
| DG-3 | Cross-method validation (≥2 methods, non-overlapping failures) | RUNNER REACHABLE; failure-asymmetry clearance pending |
| DG-4 | Failure envelope (cause-labelled, reproducible) | **PASS** at D1 v0.1.2 (2026-05-06; picture-fixed Path B numerical L_4; supersedes the v0.5.0-tagged v0.1.1 verdict that was downgraded on review the same day). Post-verdict analytic n=4 thermal-Gaussian public route landed 2026-05-13; Phase E 5.C Path B floor audit landed `floor-dominated` 2026-05-13 — Path B is not a stable cross-validation reference at the D1 production fixture, and Phase E routing pivots to Path A single-sided or DG-3 Tier-2.A; D1 v0.1.2 PASS verdict unchanged. |
| DG-5 | Thermodynamic discriminant (distinguishable observable) | SCOPED: E1 refusal path and callable model stubs exist; Fano-Anderson dynamics, HMF reference, and fermionic-bath support remain unimplemented |

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
├── transcriptions/   # source-derived operational transcriptions and derived cards
├── reviews/          # external/internal review packets and resolution work packages
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

*Repository metadata version: 0.3.0.dev0. Initialised 2026-04-29. Sail v0.5. Ledger CL-2026-005 v0.4. DG-1 PASS (tag `v0.2.0`); DG-2 structural sub-claims PASS / Entry-2-wide recursion closure still unauthorised; DG-3 runner-complete (no PASS); DG-4 PASS at D1 v0.1.2 (2026-05-06; picture-fixed Path B; supersedes the v0.5.0-tagged v0.1.1 PASS verdict that was downgraded on review the same day); post-verdict thermal-Gaussian n=4 public route landed 2026-05-13; Phase E 5.C Path B floor audit landed `floor-dominated` 2026-05-13 — D1 PASS unchanged, Phase E routing pivoted; DG-5 scope-definition with callable refusal stubs.*

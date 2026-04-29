# Contributing to `oqs-cbg-pipeline`

Thank you for considering a contribution. This repository operates under specific Sail discipline. Please read the protective documents in `docs/` before opening a pull request.

## Reading order before contributing

1. [`docs/endorsement_marker.md`](docs/endorsement_marker.md)
2. [`docs/do_not_cite_as.md`](docs/do_not_cite_as.md)
3. [`docs/stewardship_conflict.md`](docs/stewardship_conflict.md)
4. [`sail/sail-cbg-pipeline_v0.5.md`](sail/sail-cbg-pipeline_v0.5.md), especially §§4, 9, 10, 11.
5. [`docs/benchmark_protocol.md`](docs/benchmark_protocol.md).

Contributions that violate the Sail's discipline will be requested to revise; not as criticism, but because the discipline is the load-bearing element that gives outputs their citation scope.

## What contributions are welcome

| Layer | Welcome contributions | Routing |
|---|---|---|
| Code (`cbg/`, `models/`, `numerical/`, `benchmarks/`, `reporting/`) | Module implementations, bug fixes, performance improvements, test coverage | Pull request, steward review |
| Tests (`tests/`) | New scientific tests as DGs pass; new structural tests | Pull request, steward review |
| Benchmark cards (`benchmarks/benchmark_cards/`) | New cards for new models or methods, with frozen parameters | Pull request, steward review; cards must satisfy `docs/benchmark_protocol.md` §4 |
| Logbook entries (`logbook/`) | Append-only event records | Direct commit by steward; pull requests welcomed for proposed entries |
| Documentation in `docs/` | Clarifications, typo fixes | Pull request, steward review |
| Substantive changes to `docs/endorsement_marker.md`, `docs/do_not_cite_as.md`, `docs/stewardship_conflict.md` | Sail revision required | Open an issue first; substantive change requires Sail bump |
| Changes to vendored Ledger artefacts in `ledger/` | NOT ACCEPTED at repository layer | Route via Council deliberation; vendored copies update only when upstream Ledger updates |
| Changes to vendored Sail in `sail/` | Sail revision required | Steward action; not a repository pull request |

## Pull request checklist

- [ ] I have read `docs/endorsement_marker.md` and `docs/do_not_cite_as.md`.
- [ ] I have not modified the vendored Ledger artefacts in `ledger/`.
- [ ] If I added a benchmark card: parameters are frozen *before* the run; the card carries the appropriate `stewardship_flag`; coordinate-choice annotation is present per `docs/benchmark_protocol.md` §1.
- [ ] If I added or modified code: new tests cover the change; existing tests pass.
- [ ] If I claim a Decision Gate has passed: I have updated `docs/validity_envelope.md` atomically with the change, and added a `logbook/` entry.
- [ ] My PR description states which DG the change targets (or "structural / non-DG").

## DG-relevant contribution guidance

A pull request that claims to pass a Decision Gate must:

1. Provide the benchmark cards or tests that constitute the evidence.
2. Atomically update `docs/validity_envelope.md` in the same commit as the evidence.
3. Add a logbook entry in `logbook/YYYY-MM-DD_<short-tag>.md` describing the gate, the evidence, and any caveats.
4. For DG-3: explicitly state whether the claim is for *implementation readiness* or *failure-asymmetry clearance* (these are distinct per Sail v0.5 §9 DG-3 and `docs/benchmark_protocol.md` §3).
5. For DG-4: include the cause label (one of the five in `cbg/diagnostics.py`).
6. For DG-5: NOT a unilateral repository change. A DG-5 pass produces a *discriminant report* that is filed as input to a fresh Council deliberation; the repository pull request only adds the report as evidence and updates `docs/validity_envelope.md` to "DG-5 evidence filed; awaiting Council deliberation".

## Coding style

- Python 3.10+ idioms.
- Type hints on public functions.
- Docstrings: NumPy style. Anchor every module to its Sail/Ledger reference in the module docstring.
- Run `ruff` and `black` before committing.

## Conduct

This project follows a light, harbour-style code of conduct: be constructive, attribute generously, refuse to flatten substantive disagreement into consensus, and remember that maps are not territory.

---

*Last updated: 2026-04-29. This file is licensed CC-BY-4.0 (see LICENSE-docs).*

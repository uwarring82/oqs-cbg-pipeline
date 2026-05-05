# Changelog

All notable changes to `oqs-cbg-pipeline` are recorded here. The authoritative
record of scientific status and Decision Gate verdicts is
[`docs/validity_envelope.md`](docs/validity_envelope.md); per-event detail and
self-referential commit hashes live in [`logbook/`](logbook/). This file gives
a flat, user-facing summary of the same information.

The project follows [Semantic Versioning](https://semver.org/) for its public
Python API and tracks Decision Gate transitions in the validity envelope.
Anchor: Sail v0.5; Ledger CL-2026-005 v0.4.

## [Unreleased]

### Changed
- `cbg.__version__` now reads from package metadata (`importlib.metadata`),
  removing the prior hardcoded literal so it cannot drift from `pyproject.toml`.
- The import-time protective-docs check skips when no `docs/` tree is adjacent
  to the package (i.e., the package is pip-installed without a repo checkout),
  removing the `RuntimeWarning` for downstream reusers. CI still enforces the
  same check strictly on the repository.

### Added
- `[tool.black]`, `[tool.ruff]`, and `[tool.mypy]` configuration in
  `pyproject.toml` (declared dev tools now have shared defaults; not enforced
  in CI).
- `Installation` and `Quickstart` sections in `README.md`.
- This `CHANGELOG.md`.

## [0.3.0.dev0] — 2026-05-04

DG-1 PASS (2026-04-30) and DG-2 structural sub-claims PASS (2026-05-04) under
the Council-cleared displacement-profile registry. The literal fourth-order
K_2-K_4 recursion remains pending. See
[`docs/validity_envelope.md`](docs/validity_envelope.md) for the full
authorisation table.

## [0.2.0] — 2026-05-04

Tagged at the DG-2 structural-sub-claims PASS commit. See
[`logbook/2026-05-04_dg-2-pass-envelope.md`](logbook/2026-05-04_dg-2-pass-envelope.md).

## [0.1.0] — 2026-04-30

Tagged at DG-1 PASS. See
[`logbook/2026-04-30_dg-1-pass.md`](logbook/2026-04-30_dg-1-pass.md).

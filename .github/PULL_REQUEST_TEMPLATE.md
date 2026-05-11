<!--
Thanks for the contribution. Please fill in the sections below before
requesting review. The "required" sections are load-bearing; the rest
are helpful but not blocking. See CONTRIBUTING.md for the project's
cards-first / parameter-freezing discipline, the dual-licensing
policy, and the quality-gate expectations.
-->

## Summary (required)

<!-- One paragraph: what does this PR change and why? -->

## Scope (required — check exactly the categories that apply)

- [ ] Bug fix in code, tests, or scaffolding
- [ ] New benchmark card (frozen-awaiting-run; cards-first discipline)
- [ ] Verdict commit (run-result fills a card's empty `result` block)
- [ ] Documentation only (READMEs, docs/, docs-site/, examples/)
- [ ] Tooling / CI / packaging (`.github/`, `pyproject.toml`, `scripts/`)
- [ ] Logbook entry (append-only repository event log)
- [ ] Supersedure (new card / plan / transcription version superseding an earlier one)
- [ ] Other (describe)

## Validity-envelope impact (required)

- [ ] **None.** No row in `docs/validity_envelope.md` changes.
- [ ] **DG row updated** in the same PR. Cite the row; also link the
  matching logbook entry (one of `logbook/YYYY-MM-DD_<short-tag>.md`).
- [ ] **Could affect a passed DG.** Name the DG and the card whose
  verdict could be invalidated. **A confirmed regression in a
  passed-card surface routes via the supersedure-and-downgrade
  protocol** (Sail v0.5 §9; see logbook entries
  `2026-05-06_dg-4-pass-path-b-superseded.md` and
  `2026-05-06_dg-4-pass-path-b-v012.md` for the canonical worked
  example).

## Cards-first / parameter-freezing discipline (required for any card-touching PR)

- [ ] No frozen card's `frozen_parameters` block, `acceptance_criterion`,
  or other-than-result fields are mutated in place. (Supersedure goes
  via a new `<card_id>_<short-tag>_v<higher>.yaml` file with
  `supersedes:` set.)
- [ ] **Exception**: definitional clarifications (e.g. formula labels
  that match the runner's actual computation) treated under
  benchmark_cards/SCHEMA.md / docs/benchmark_protocol.md §6.3. State
  here why this is a clarification and not a parameter mutation.

## Gauge & profile annotations (required if outputs cite K(t) or DG-2 displaced sub-claims)

- [ ] Outputs claiming agreement with K(t) annotate the
  Hayden–Sorce minimal-dissipation gauge per
  `docs/benchmark_protocol.md` §1.
- [ ] Outputs claiming Entries 3.B.3 / 4.B.2 name the registered
  displacement profile (one of `delta-omega_c`, `delta-omega_S`,
  `sqrt-J`, `gaussian`).

## Quality gates (required)

- [ ] `pytest tests/ -q` passes.
- [ ] `python -m ruff check .` passes.
- [ ] `python -m black --check cbg/ models/ numerical/ benchmarks/ reporting/ tests/ docs-site/ scripts/ conftest.py` passes.
- [ ] `python -m mypy cbg/ models/ numerical/ benchmarks/ reporting/` passes.
- [ ] `sphinx-build -W -b html -E docs-site /tmp/out` passes (only required for doc-touching PRs).

## Licensing (required for new files)

- [ ] New `*.py` files carry `# SPDX-License-Identifier: MIT` on the
  first line.
- [ ] New documentation files inherit CC-BY-4.0 via `LICENSE-docs`
  (no per-file SPDX required for docs unless the file mixes content
  with a different license).

## Linked issue / logbook (optional)

Closes #
Logbook entry:

---
name: Bug report
about: Report a defect in the numerical surface, benchmark runner, or supporting tooling
title: "[BUG] "
labels: bug
---

<!--
Thanks for filing a bug. Please fill in the sections below. The
sections marked "required" are load-bearing for triage; the rest are
helpful but not blocking.
-->

## Summary (required)

<!-- One paragraph: what behaviour did you see, what did you expect? -->

## How to reproduce (required)

<!--
Minimal steps. Prefer a copy-pasteable code block that imports cbg /
reporting / models / numerical / benchmarks and reaches the defect in
≤ 30 lines. If the bug surfaces only via a benchmark card or example
notebook, cite the card filename and the specific test_case / sweep
point that fails.
-->

```python
# Minimal reproducer
```

## Environment (required for non-trivial bugs)

- `cbg.__version__` (the package version, not the git tag):
- Python version (`python --version`):
- Operating system / architecture:
- QuTiP version (`pip show qutip`) — only if QuTiP is in the trace:
- Are you in an editable install (`pip install -e .`) or a release install?

## Validity-envelope impact (required)

<!--
Pick one. The triage path depends on it.
-->

- [ ] **Does not affect any passed Decision Gate.** The bug is in
  tooling, scaffolding, examples, docs, or scope-definition surface
  (E1, stub model APIs, etc.).
- [ ] **Could affect a passed Decision Gate.** Name the DG (DG-1,
  DG-2 sub-claims, DG-4 at D1 v0.1.2) and the card(s) whose verdict
  could be invalidated. **A confirmed defect in a passed DG triggers
  the supersedure-and-downgrade protocol from Sail v0.5 §9 + the
  logbook supersedure discipline; the steward will route accordingly.**

## DG cause label (required if the bug surfaces during a DG run)

<!--
If the bug surfaces while running a benchmark card, pick the
DG-4-taxonomy cause label that best matches (per docs/benchmark_protocol.md §4):
-->

- [ ] `convergence_failure`
- [ ] `tcl_singularity`
- [ ] `projection_ambiguity`
- [ ] `truncation_artefact`
- [ ] `benchmark_disagreement`
- [ ] Not applicable (bug is outside a card run)

## Suggested fix (optional)

<!--
If you have a proposal, sketch it here. The steward may take it as-is,
request changes, or route it via a separate supersedure / fresh
Council deliberation depending on its scope per Sail v0.5 §9.
-->

# `reporting` — Benchmark-card schema, loader, validator, runner

Implementation of the SCHEMA.md v0.1.3 card lifecycle: load YAML cards,
validate against the schema rules (16 from v0.1.2 + Rule 17
`frozen_parameters.sweep:` for DG-4 sweep cards + Rule 18
`scope-definition` notes from v0.1.3), run them via the appropriate
handler dispatch (algebraic-map vs. dynamical vs. DG-4 sweep vs.
scope-definition refusal), populate the result block, and serialise
evidence.

The runner enforces the canonical Hayden–Sorce minimal-dissipation gauge
block before any K-from-generator computation; tampering aborts with
`GaugeAnnotationError`. Test-case handlers are registered in two
side-by-side registries — `_TEST_CASE_HANDLERS` for algebraic-map cards
(A1, B1, frozen B2/B3) and `_DYNAMICAL_TEST_CASE_HANDLERS` for dynamical
cards (A3, A4, future B-series). Adding a new test_case name requires
registering its handler explicitly; missing handlers raise
`TestCaseHandlerNotFoundError` rather than silently no-oping, which is
how cards-first / Risk #6 / Risk #8 mitigation is mechanically enforced.

## `reporting.benchmark_card`

```{eval-rst}
.. automodule:: reporting.benchmark_card
   :members:
```

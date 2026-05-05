# D1 (DG-4) and E1 (DG-5 scope-definition) runner refusal paths wired

**Date:** 2026-05-05
**Type:** structural
**Triggering commit:** 0c01cbd
**Triggering evidence:**
- [`reporting/benchmark_card.py`](../reporting/benchmark_card.py): two new `NotImplementedError` subclasses (`ScopeDefinitionNotRunnableError`, `DG4SweepRunnerNotImplementedError`) plus dedicated refusal branches `_refuse_scope_definition` and `_refuse_dg4_sweep` invoked from `run_card`.
- [`tests/test_benchmark_card.py`](../tests/test_benchmark_card.py): 6 new tests covering exception hierarchy, message content (card id, DG label, surfaced preconditions / sweep summary, missing-pieces description), and dispatch-precedence (refusal must fire before downstream dispatch).
- `pytest` under `.venv/bin/python` 3.13.7: 413 passed.

## Summary

Before this commit, calling `run_card(D1)` raised a `KeyError: 'test_cases'` from the dynamical handler (because D1 has no `test_cases`, only a `frozen_parameters.sweep:` block), and `run_card(E1)` raised a generic `NotImplementedError: no model factory registered for 'fano_anderson'` from the same handler. Both errors were opaque — they pointed at internal-runner missteps rather than at the actual reason the cards aren't runnable.

This commit replaces both with dedicated refusal paths that emit clear, actionable diagnostics. The cards remain not-runnable; the change is in the *quality of the refusal*, not in what the cards compute.

## Detail

### `ScopeDefinitionNotRunnableError`

Raised when `run_card` is called on any card whose `status` field is `scope-definition` (SCHEMA.md v0.1.3 Rule 18). The error message surfaces the unmet preconditions recorded in the card's `failure_mode_log` and/or `result.notes`. For E1, those preconditions are:

- `models/fano_anderson.py` has no callable API.
- No HMF reference implementation exists in the repository.
- `cbg.bath_correlations` does not support fermionic baths.

The exception is a `NotImplementedError` subclass so callers that catch the broader exception still see the refusal.

### `DG4SweepRunnerNotImplementedError`

Raised when `run_card` is called on any `dg_target: DG-4` card. The error message includes a one-line summary of the card's frozen sweep block (parameter name, range, scheme) and names the two missing pieces required for a real DG-4 runner:

1. `cbg.tcl_recursion` at perturbative_order ≥ 3 — the canonical-unfilled DG-2 milestone per `docs/validity_envelope.md`. D1 needs orders {0, 1, 2, 3, 4} to evaluate the convergence-ratio metric `r_n = ⟨‖K_n‖⟩ / ⟨‖K_{n−1}‖⟩` defined in the card's acceptance criterion.
2. A sweep-block-aware runner branch consuming `frozen_parameters.sweep` (SCHEMA.md v0.1.3 Rule 17). Both pieces would need to land before D1 becomes runnable.

The exception is a `NotImplementedError` subclass.

### Dispatch precedence

`run_card`'s dispatch order now begins with the two refusal checks before falling through to the existing DG-3 cross-method, algebraic_map, and dynamical branches:

```python
verify_gauge_annotation(card)
if card.status == "scope-definition":
    _refuse_scope_definition(card)  # raises
if card.dg_target == "DG-4":
    _refuse_dg4_sweep(card)  # raises
if card.dg_target == "DG-3":
    return _run_cross_method(card)
if card.model_kind == "algebraic_map":
    return _run_algebraic_map(card)
if card.model_kind == "dynamical":
    return _run_dynamical(card)
```

Tests `test_run_card_d1_refusal_takes_precedence_over_dynamical_dispatch` and `test_run_card_e1_refusal_takes_precedence_over_model_factory` lock in the precedence so a future refactor cannot regress to opaque downstream errors.

## What this changes for the validity envelope

The DG-4 and DG-5 rows transition from "frozen card awaiting implementation" to "runner refusal path wired; \<implementation\> not yet implemented". The DG status itself does not change — both gates remain SCOPED. What is now mechanically auditable is that the runner's behaviour for these cards is *defined and informative*, not *accidental*.

## Routing notes

The natural next pieces of work are the actual implementations rather than further refusal-path polish:

1. **D1 / DG-4**: extend `cbg.tcl_recursion` to perturbative_order ≥ 3, then add a `_run_dg4_sweep` runner branch consuming `frozen_parameters.sweep`.
2. **E1 / DG-5**: implement the Fano-Anderson model API (`hamiltonian`, `coupling_operator`, `system_arrays_from_spec`), add fermionic-bath support to `cbg.bath_correlations`, and supersede E1 with a `frozen-awaiting-run` successor once the HMF reference is in place.

Both are substantial enough to warrant their own work-plan revisions. The refusal paths landed here keep the runner contract clean while those work plans are drafted.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

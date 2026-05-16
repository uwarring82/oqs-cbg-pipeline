# DG-3 Phase E — schema v0.1.5 + C1/C2 v0.3.0 scope-definition cards (HEOM-vs-TEMPO gate)

**Date:** 2026-05-16
**Type:** structural
**Triggering commit:** _(self-referential; to be populated on commit per [`logbook/README.md`](README.md) §Immutability exception 2)_

**Triggering evidence:**
- DG-3 work plan [`v0.1.2`](../plans/dg-3-work-plan_v0.1.2.md) §§2.3, 2.6 Phase E (route authority; pushed `cf3ce54`).
- Phase D.0/D.1 blocking finding: logbook [`2026-05-16_dg-3-phase-d-recon-gating-pair-blocked`](2026-05-16_dg-3-phase-d-recon-gating-pair-blocked.md) (commit `d41ff66`).
- `benchmarks/benchmark_cards/SCHEMA.md` v0.1.5; new cards [`C1 v0.3.0`](../benchmarks/benchmark_cards/C1_cross-method-pure-dephasing_v0.3.0.yaml), [`C2 v0.3.0`](../benchmarks/benchmark_cards/C2_cross-method-spin-boson_v0.3.0.yaml); superseded [`C1 v0.2.0`](../benchmarks/benchmark_cards/C1_cross-method-pure-dephasing_v0.2.0.yaml), [`C2 v0.2.0`](../benchmarks/benchmark_cards/C2_cross-method-spin-boson_v0.2.0.yaml).

## Summary

DG-3 work plan v0.1.2 Phase E (cards/spec-first) landed: schema bumped v0.1.4 → **v0.1.5** (generalised N-method `methods`/`method_modules` form; Rule 19 rewritten as a 3-branch mutually-exclusive shape with the `*_reference → *_options` options-stem convention; backward compatible — v0.1.4 `third_method` cards validate unchanged). `oqupy>=0.5,<0.6` declared in `pyproject.toml` (Apache-2.0, Python ≥3.10; **not yet installed** — realised at Phase F). C1/C2 **v0.3.0** four-method cards drafted and committed as **`scope-definition`** (Option A: gating pair `[heom_reference, oqupy_reference]`; `exact_finite_env`/`qutip_reference` retained as non-gating auxiliary), atomically superseding C1/C2 v0.2.0. No DG-3 verdict; no runner/module code.

## Detail

- The v0.3.0 gate `(heom_reference, oqupy_reference)` replaces the v0.2.0 gate `(exact_finite_env, heom_reference)` proven physically unsatisfiable by Phase D.1 (`finite-env-correlator-floor`). Both gating methods are faithful continuous-bath solvers from non-overlapping failure-mode classes (bath-hierarchy-truncation vs process-tensor / MPS-bond-dimension).
- v0.3.0 is `scope-definition` (SCHEMA §Status values; Rule 18 preconditions in `result.notes`): `benchmarks/oqupy_reference.py`, the N-method runner dispatch, `KNOWN_SCHEMA_VERSIONS` ⊇ `v0.1.5`, and generalised-Rule-19 enforcement do not yet exist. Transition to `frozen-awaiting-run` is via a v0.3.1 supersedure once Phase F/G satisfy them (and re-freeze Phase-F-validated `oqupy_options`).
- C1/C2 v0.2.0 set `status: superseded` + `superseded_by:` atomically in the same commit (SCHEMA §Supersedure); v0.2.0 retained at HEAD as the artifact that exposed the bad gate. Cards-index README index/superseded tables updated; `README.md` dependency docs updated (OQuPy + v0.1.2 route). Quality gate: `pytest` 560 passed; `git diff --check` clean.

## Routing notes

Next: DG-3 work plan v0.1.2 **Phase F** (`benchmarks/oqupy_reference.py` + tests; install `oqupy`; validate/re-freeze `oqupy_options`) then **Phase G** (schema v0.1.5 in `KNOWN_SCHEMA_VERSIONS`, generalised Rule 19 enforcement, N-method runner dispatch, v0.3.0 → v0.3.1 transition to `frozen-awaiting-run`), then **Phase H** (run + verdict). No Ledger or Sail change. DG-4 D1 v0.1.2 PASS unchanged. Superseded by execution when Phase F lands.

## Permitted post-commit edits to this entry

Per [`logbook/README.md`](README.md) §Immutability: (1) `superseded by:` annotation when a successor entry is added; (2) self-referential `Triggering commit:` placeholder fill (follow-up commit message `logbook: fill self-referential triggering-commit placeholder for dg-3-phase-e-schema-v015-cards-v030`). Any other text edit requires supersedure.

---

*Logbook entry. Immutable once committed.*

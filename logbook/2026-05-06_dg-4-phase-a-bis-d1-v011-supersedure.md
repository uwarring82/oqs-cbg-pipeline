# DG-4 Phase A.bis — D1 v0.1.1 supersedure frozen

**Date:** 2026-05-06
**Type:** structural
**Triggering commit:** (to be populated on commit)
**Triggering evidence:**
- Card [`D1_failure-envelope-convergence_v0.1.1.yaml`](../benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.1.yaml) added.
- Card [`D1_failure-envelope-convergence_v0.1.0.yaml`](../benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.0.yaml) marked `status: superseded`.
- Active DG-4 work plan [`dg-4-work-plan_v0.1.4.md`](../plans/dg-4-work-plan_v0.1.4.md) §3 Phase A.bis.
- Path B pilot result [`2026-05-06_dg-4-path-b-pilot-result.md`](2026-05-06_dg-4-path-b-pilot-result.md).
- Tests: `.venv/bin/pytest -q tests/test_benchmark_card.py tests/test_imports.py`.

## Summary

DG-4 Phase A.bis is complete: D1 v0.1.0 has been superseded by D1 v0.1.1. The active D1 card now targets the σ_x thermal model and the parity-aware even-order dissipator ratio

```text
r_4 = <||L_4^dissipator||>_t / <||L_2^dissipator||>_t
```

with the v0.1.4 operational reproducibility perturbations: `upper_cutoff_factor` via the numerical quadrature allow-list and `omega_c` via direct model-spec mutation. No DG-4 verdict is claimed; the card remains `frozen-awaiting-run` behind the DG-4 sweep-runner refusal path.

## Detail

D1 v0.1.0 targeted pure_dephasing and a K_n adjacent-order growth metric. Phase B work and the v0.1.4 work-plan review established that this cannot produce the intended convergence-failure signal:

- pure_dephasing thermal Gaussian is TCL-2 exact, so `L_n` and `L_n^dissipator` vanish for `n >= 3`;
- σ_x thermal still has odd-order zeros by parity, so adjacent-order ratios are parity-blind and become metric-undefined;
- the original reproducibility perturbations (`bath_mode_cutoff`, `integration_tolerance`) were non-operational on the CBG recursion path.

D1 v0.1.1 freezes the corrected target:

- model: `spin_boson_sigma_x`, thermal bath, ohmic spectral density with swept `coupling_strength` from `0.05` to `1.0` over 20 log-uniform points;
- metric: `convergence_ratio_parity_aware`, evaluating only `r_4` at this card version;
- denominator policy: zero `L_2^dis` marks a point `metric-undefined` rather than convergence failure;
- reproducibility perturbations: `upper_cutoff_factor = 20 / 40` and `omega_c = 9 / 11`;
- cause-label discipline: stable `r_4 > 1` gives `convergence_failure`, instability gives `truncation_artefact`, and `TCL_singularity` remains observational only for this card.

The Path B numerical pilot is cited as design evidence only. It confirmed `||L_4^dis|| > 0` in σ_x thermal, but it does not complete analytic Phase B.2/B.3 at n=4.

## Routing

The next DG-4 implementation step is Phase C runner work, gated on a trusted order-4 `L_4` source:

- Path A (Companion Sec. IV closed form) remains preferred.
- Path B numerical extraction may support exploratory or Path-B-only verdict work only if result notes carry the finite-env floor as an uncertainty band.
- `reporting.benchmark_card.run_card(D1 v0.1.1)` still raises `DG4SweepRunnerNotImplementedError` until the order-4 source and sweep-aware branch land.

No Ledger or Sail edit is implied by this card supersedure.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

# `examples/`

Runnable demonstrations of the validated surface of `oqs-cbg-pipeline`.
Each notebook exercises the cards that anchor a passed Decision Gate
verdict in [`docs/validity_envelope.md`](../docs/validity_envelope.md).

| Notebook | Decision Gate | Cards demonstrated | Expected outcome |
|---|---|---|---|
| [`dg1_walkthrough.ipynb`](dg1_walkthrough.ipynb) | DG-1 PASS (2026-04-30; tag `v0.2.0`) | A1 (closed-form K), A3 (pure-dephasing thermal) | Algebraic K = H_S exactly; pure-dephasing K(t) ∝ σ_z at machine precision |
| [`dg2_structural.ipynb`](dg2_structural.ipynb) | DG-2 structural sub-claims PASS (2026-05-04) | B3 (cross-basis identity), B4 (displaced bath, profile `delta-omega_S`) | Basis-independence at machine precision on a dissipative L; displaced-bath K(t) recovers thermal K as α₀ → 0 |
| [`dg3_cross_method.ipynb`](dg3_cross_method.ipynb) | DG-3 RUNNER-COMPLETE; failure-asymmetry-cleared PASS pending | C1 (pure-dephasing), C2 (spin-boson σ_x) | Runner reachable on all four C1+C2 fixtures; both cards return clean FAIL at the frozen `1.0e-6` agreement threshold (~10⁻¹ disagreement under finite-bath truncation). Demonstrates the failure-asymmetry-clearance gap, not a PASS. |
| [`dg4_walkthrough.ipynb`](dg4_walkthrough.ipynb) | DG-4 PASS at D1 v0.1.2 (2026-05-06) via picture-fixed Path B numerical L_4 | D1 v0.1.2 (σ_x thermal, parity-aware r_4) | Picture-fixed Path B extraction recovers `<‖L_4^dis‖>_t` and `<‖L_2^dis‖>_t`; the parity-aware ratio `r_4 = α² ⋅ ⟨‖L_4^dis‖⟩_t / ⟨‖L_2^dis‖⟩_t` exceeds threshold 1.0 in the upper sweep range and `run_card` returns `verdict = PASS` with all four reproducibility perturbations operational. Path B carries a documented finite-env extraction floor; analytic Path A pending. v0.1.2 supersedes the v0.5.0-tagged v0.1.1 verdict that was downgraded on review the same day. |

## Running

From a repository checkout with the package installed:

```bash
pip install -e ".[dev]"
pip install jupyter        # only needed if not already installed

jupyter notebook examples/
```

Or non-interactively (no GUI), executing in place:

```bash
jupyter nbconvert --to notebook --execute --inplace examples/dg1_walkthrough.ipynb
jupyter nbconvert --to notebook --execute --inplace examples/dg2_structural.ipynb
```

## Scope

These notebooks are **demonstrations of passed Decision Gate verdicts**,
not tutorials on the underlying theory. For the theoretical background,
read the two anchoring papers (linked from the top-level
[`README.md`](../README.md)) and the PhD-student tutorial
[`cbg-tutorial-for-phd-students_v0.2.html`](../cbg-tutorial-for-phd-students_v0.2.html).
For the frozen verdict numbers and acceptance thresholds, see the
benchmark cards in [`benchmarks/benchmark_cards/`](../benchmarks/benchmark_cards/)
and their results in [`benchmarks/results/`](../benchmarks/results/).

All numerical outputs in these notebooks are coordinate-dependent under the
Hayden–Sorce minimal-dissipation gauge. See
[`docs/do_not_cite_as.md`](../docs/do_not_cite_as.md) for citation discipline.

# Worked examples

Runnable demonstrations of the validated surface of `oqs-cbg-pipeline`.
Each notebook exercises the cards that anchor a passed Decision Gate
verdict in the
[validity envelope](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/docs/validity_envelope.md).

:::{admonition} Demonstrations, not tutorials
:class: note

These notebooks are demonstrations of passed (or partially passed)
Decision Gate verdicts, not tutorials on the underlying theory. For
theoretical background, see the two
<a href="../index.html">seed papers</a> and the entry-level
<a href="../cbg-tutorial-for-phd-students_v0.2.html">PhD-student tutorial</a>.
For the frozen verdict numbers and acceptance thresholds, see the
[benchmark cards](https://github.com/uwarring82/oqs-cbg-pipeline/tree/main/benchmarks/benchmark_cards)
and their
[results](https://github.com/uwarring82/oqs-cbg-pipeline/tree/main/benchmarks/results).
:::

## Available notebooks

<a href="examples/dg1_walkthrough.html"><code>dg1_walkthrough</code></a>
: **DG-1 PASS** (2026-04-30; tag `v0.2.0`) — cards A1 (closed-form K) and
  A3 (pure-dephasing thermal). Shows that the algebraic K equals H_S
  exactly and that the pure-dephasing K(t) is proportional to σ_z at
  machine precision.
  ([source on GitHub](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/examples/dg1_walkthrough.ipynb))

<a href="examples/dg2_structural.html"><code>dg2_structural</code></a>
: **DG-2 structural sub-claims PASS** (2026-05-04) — cards B3
  (cross-basis identity) and B4 (displaced bath, profile
  `delta-omega_S`). Shows basis-independence at machine precision on a
  dissipative L, and that the displaced-bath K(t) recovers the thermal
  K as α₀ → 0.
  ([source on GitHub](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/examples/dg2_structural.ipynb))

<a href="examples/dg3_cross_method.html"><code>dg3_cross_method</code></a>
: **DG-3 RUNNER-COMPLETE; failure-asymmetry-cleared PASS pending** —
  cards C1 (pure-dephasing) and C2 (spin-boson σ_x). Demonstrates the
  failure-asymmetry-clearance gap, *not* a PASS: the runner is reachable
  on all four C1+C2 fixtures, and both cards return clean FAIL at the
  frozen `1.0e-6` agreement threshold (~10⁻¹ disagreement under
  finite-bath truncation).
  ([source on GitHub](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/examples/dg3_cross_method.ipynb))

<a href="examples/dg4_walkthrough.html"><code>dg4_walkthrough</code></a>
: **DG-4 PASS at D1 v0.1.2** (2026-05-06) via picture-fixed Path B
  numerical L_4 — card D1 v0.1.2 (σ_x thermal, parity-aware r_4). The
  parity-aware ratio
  `r_4 = α² ⋅ ⟨‖L_4^dis‖⟩_t / ⟨‖L_2^dis‖⟩_t` exceeds threshold 1.0 in
  the upper sweep range, and `run_card` returns `verdict = PASS` with
  all four reproducibility perturbations operational. Path B carries a
  documented finite-env extraction floor; analytic Path A pending.
  v0.1.2 supersedes the v0.5.0-tagged v0.1.1 verdict that was downgraded
  on review the same day.
  ([source on GitHub](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/examples/dg4_walkthrough.ipynb))

## Running locally

The rendered HTML reflects the on-disk state of each notebook at build
time; some notebooks are committed without outputs to keep diffs clean.
To populate every cell with live outputs, re-execute the notebooks
before rebuilding the docs:

```bash
pip install -e ".[dev,docs]"
pip install jupyter

jupyter nbconvert --to notebook --execute --inplace examples/dg1_walkthrough.ipynb
jupyter nbconvert --to notebook --execute --inplace examples/dg2_structural.ipynb
jupyter nbconvert --to notebook --execute --inplace examples/dg3_cross_method.ipynb
jupyter nbconvert --to notebook --execute --inplace examples/dg4_walkthrough.ipynb

scripts/build_docs.sh
```

Or open them interactively:

```bash
jupyter notebook examples/
```

## Citation discipline

All numerical outputs in these notebooks are coordinate-dependent under
the Hayden–Sorce minimal-dissipation gauge. See
[`docs/do_not_cite_as.md`](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/docs/do_not_cite_as.md)
for citation rules.

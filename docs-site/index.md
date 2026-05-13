# oqs-cbg-pipeline — API documentation

Auto-generated reference for the open numerical companion to the
**Colla–Breuer–Gasbarri** minimal-dissipation effective-Hamiltonian
framework for non-Markovian open quantum systems
([Phys. Rev. A **112**, L050203 (2025)](https://doi.org/10.1103/n5nl-gn1y);
[Phys. Rev. A **112**, 052222 (2025)](https://doi.org/10.1103/9j8d-jxgd)).

For a warmer project overview, citation policy, conflict-of-interest disclosures,
and the concise status table, see the <a href="../index.html">main landing page</a>.
(The link uses raw HTML to bypass Sphinx's download-internal handling for
sibling-directory files; on GitHub Pages it resolves to the hand-curated
landing page at the repo root.)

:::{admonition} Authority limit
:class: warning

These pages are auto-generated from in-source docstrings. They describe
**how** the implementation works, not **what** it has been verified to
reproduce. Verification status is the responsibility of the
[validity envelope](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/docs/validity_envelope.md)
and the [benchmark cards](https://github.com/uwarring82/oqs-cbg-pipeline/tree/main/benchmarks/benchmark_cards).
A function being documented here does **not** imply its outputs have
passed any Decision Gate.
:::

## Where to start

If you are new to the repository, start with the hand-curated
<a href="../index.html">landing page</a>, then use these API pages to
inspect the implementation details behind the benchmark cards. The
worked examples are the best executable entry point; the module reference
is for checking signatures, docstrings, and supported scopes.

## Current implementation stage

The live DG verdicts remain DG-1 PASS, DG-2 structural-sub-claims PASS
with Entry-2-wide recursion closure still unauthorised, and DG-4 PASS at
D1 v0.1.2 via picture-fixed Path B numerical L_4. Since that verdict,
the post-verdict analytic thermal-Gaussian n=4 route has landed:
`L_n_thermal_at_time(n=4)`, `K_n_thermal_on_grid(n=4)`,
`K_total_thermal_on_grid(N_card=4)`, the n=4 dissipator helpers, and
the `L_n` shim route through the reviewed Phase B/C helpers.

That implementation advance is code-facing, not a new verdict. D1 v0.1.2
remains the live DG-4 failure-envelope artifact. The Phase E Track 5.C
Path B floor audit (2026-05-13) characterised Path B's reference at the
D1 production fixture and landed cause label `floor-dominated`: the
production `coefficient_ratio = 47.4` shifts by 24% under truncation
tightening across `omega_max_factor`, `n_levels_per_mode`, and
`n_bath_modes`, with axes pulling in mutually inconsistent directions.
Phase E routing now requires either Path A as single-sided ground truth
(Tracks 5.A / 5.B), DG-3 Tier-2.A (HEOM / TEMPO third method) as Path
B's replacement, or a permanent `unclassified-pilot` state. The D1
v0.1.2 PASS verdict is unchanged.

## Packages

The implementation is split across four top-level packages:

```{toctree}
:maxdepth: 2

cbg
models
numerical
reporting
```

## Worked examples

```{toctree}
:maxdepth: 1

examples
```

## Quick links

- [Source on GitHub](https://github.com/uwarring82/oqs-cbg-pipeline)
- [Benchmark cards](https://github.com/uwarring82/oqs-cbg-pipeline/tree/main/benchmarks/benchmark_cards) — frozen verification artifacts
- [Validity envelope](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/docs/validity_envelope.md) — authoritative DG status
- [Transcriptions](https://github.com/uwarring82/oqs-cbg-pipeline/tree/main/transcriptions) — source-derived operational transcriptions and n=4 derived cards
- [Subsidiary Council briefing v0.3.0](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/ledger/CL-2026-005_v0.4_council-briefing_displacement-convention.md) — Council-cleared displacement-profile registry (handling (c))
- [Hayden–Sorce transcription v0.1.1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/transcriptions/hayden-sorce-2022_pseudokraus_v0.1.1.md)
- [Colla–Breuer–Gasbarri Appendix-D-routed transcription v0.0.1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/transcriptions/colla-breuer-gasbarri-2025_appendix-d_v0.0.1.md)
- [Logbook](https://github.com/uwarring82/oqs-cbg-pipeline/tree/main/logbook) — append-only repository event log
- [DG-1 work plan v0.1.4](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/plans/dg-1-work-plan_v0.1.4.md)

## Decision-Gate Status Snapshot

| Gate | Status | Anchor |
|---|---|---|
| DG-1 | **PASS** (2026-04-30; tag `v0.2.0`) | Cards [A1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/A1_closed-form-K_v0.1.1.yaml), [A3](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/A3_pure-dephasing_v0.1.1.yaml), [A4](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/A4_sigma-x-thermal_v0.1.1.yaml). |
| DG-2 | **PARTIAL** — structural sub-claims PASS; Entry-2-wide recursion closure not yet authorised | Cards [B1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml), [B2](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/B2_pseudo-kraus-offdiagonal_v0.1.0.yaml), [B3](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/B3_cross-basis-structural-identity_v0.1.0.yaml), [B4-conv-registry](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/B4-conv-registry_v0.1.0.yaml), and [B5-conv-registry v0.2.0](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml). The thermal-Gaussian n=4 public route exists, but no DG-2 K_2-K_4 recursion card has closed Entry 2. |
| DG-3 | RUNNER-COMPLETE; failure-asymmetry clearance pending | Cards [C1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/C1_cross-method-pure-dephasing_v0.1.0.yaml) + [C2](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/C2_cross-method-spin-boson_v0.1.0.yaml) are reachable on all four thermal + displaced fixtures and currently clean-FAIL under finite-bath truncation. A PASS needs convergence or a third non-overlapping method. |
| DG-4 | **PASS** at D1 v0.1.2 (2026-05-06) | [D1 v0.1.2](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.2.yaml) identifies the σ_x thermal convergence-failure envelope with max baseline `r_4 ≈ 47.42`. The verdict source remains picture-fixed Path B numerical L_4. Phase E 5.C audit (2026-05-13) landed `floor-dominated`: Path B at the D1 production fixture is not a stable cross-validation reference (24% drift under truncation tightening); Phase E routing pivots to Path A single-sided or DG-3 Tier-2.A. PASS verdict unchanged. |
| DG-5 | SCOPE-DEFINITION | [E1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml) records the Fano-Anderson / HMF discriminant scope. Callable refusal stubs exist; realised dynamics, HMF reference, and fermionic-bath support remain unimplemented. |

## Building these pages

```bash
scripts/build_docs.sh
```

The wrapper creates a local `.venv/` if needed, installs the documentation
dependencies declared in `pyproject.toml` under `[project.optional-dependencies] docs`,
and runs `sphinx-build` to write HTML into `api/` at the repository root.
The output is committed to `main`; refreshing the docs is a discrete commit
event for audit-trail purposes.

# oqs-cbg-pipeline — API documentation

Auto-generated reference for the open numerical companion to the
**Colla–Breuer–Gasbarri** minimal-dissipation effective-Hamiltonian
framework for non-Markovian open quantum systems
([Phys. Rev. A **112**, L050203 (2025)](https://doi.org/10.1103/n5nl-gn1y);
[Phys. Rev. A **112**, 052222 (2025)](https://doi.org/10.1103/9j8d-jxgd)).

For project background, citation policy, conflict-of-interest disclosures,
and the authoritative status, see the <a href="../index.html">main landing page</a>.
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

## Decision-Gate status snapshot

| Gate | Status | Anchor |
|---|---|---|
| DG-1 | **PASS** (2026-04-30; tag `v0.2.0`) | Cards [A1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/A1_closed-form-K_v0.1.1.yaml), [A3](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/A3_pure-dephasing_v0.1.1.yaml), [A4](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/A4_sigma-x-thermal_v0.1.1.yaml) |
| DG-2 | **PARTIAL** — structural sub-claims PASS under Council-cleared registry; K_2-K_4 recursion pending (2026-05-04) | [B1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml) (Entry 1.B.3 diagonal); [B2](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/B2_pseudo-kraus-offdiagonal_v0.1.0.yaml) (Entry 1.B.3 off-diagonal + Entry 1.D); [B3](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/B3_cross-basis-structural-identity_v0.1.0.yaml) (Entry 1.A basis-independence); [B4-conv-registry](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/B4-conv-registry_v0.1.0.yaml) (Entry 3.B.3) + [B5-conv-registry v0.2.0](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/B5-conv-registry_v0.2.0.yaml) (Entry 4.B.2), each under all four Council-cleared displacement profiles. Literal K_2-K_4 numerical recursion at order >= 4 = future plan. |
| DG-3 | RUNNER-COMPLETE; failure-asymmetry clearance pending | Cards [C1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/C1_cross-method-pure-dephasing_v0.1.0.yaml) (pure-dephasing) + [C2](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/C2_cross-method-spin-boson_v0.1.0.yaml) (spin-boson σ_x) reachable on all four thermal + displaced fixtures via `_run_cross_method`; both currently FAIL convergence in finite-bath truncation. Failure-asymmetry-cleared PASS requires either bath-convergence under the cleared registry or a third reference method from a non-overlapping failure-mode class. |
| DG-4 | **PASS** at D1 v0.1.2 (2026-05-06) | Card [D1 v0.1.2](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.2.yaml) — spin-boson σ_x thermal, parity-aware ratio `r_4(α²) = α² · ⟨‖L_4^dis‖⟩_t / ⟨‖L_2^dis‖⟩_t`. All 20 swept `coupling_strength` points classify `convergence_failure` with stability across all four perturbations (`upper_cutoff_factor ∈ {20, 40}`, `omega_c ∈ {9, 11}`); max baseline `r_4 ≈ 47.42`. v0.1.2 supersedes the v0.5.0-tagged v0.1.1 verdict that was superseded on review the same day; consumes Path B picture fix + operational `omega_max_factor` + audit-complete result JSON. Path A analytic L_4 cross-validation remains pending. See [v0.1.2 verdict log](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/logbook/2026-05-06_dg-4-pass-path-b-v012.md). |
| DG-5 | SCOPE-DEFINITION (preconditions unmet) | Card [E1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/benchmarks/benchmark_cards/E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml) — Fano–Anderson + Hamiltonian of mean force discriminant. `run_card(E1)` raises `ScopeDefinitionNotRunnableError` listing missing preconditions (model factory, HMF reference, fermionic-bath support). |

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
- [Subsidiary Council briefing v0.3.0](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/ledger/CL-2026-005_v0.4_council-briefing_displacement-convention.md) — Council-cleared displacement-profile registry (handling (c))
- [Hayden–Sorce transcription v0.1.1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/transcriptions/hayden-sorce-2022_pseudokraus_v0.1.1.md)
- [Colla–Breuer–Gasbarri Appendix-D-routed transcription v0.0.1](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/transcriptions/colla-breuer-gasbarri-2025_appendix-d_v0.0.1.md)
- [Logbook](https://github.com/uwarring82/oqs-cbg-pipeline/tree/main/logbook) — append-only repository event log
- [DG-1 work plan v0.1.4](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/plans/dg-1-work-plan_v0.1.4.md)

## Building these pages

```bash
scripts/build_docs.sh
```

The wrapper creates a local `.venv/` if needed, installs the documentation
dependencies declared in `pyproject.toml` under `[project.optional-dependencies] docs`,
and runs `sphinx-build` to write HTML into `api/` at the repository root.
The output is committed to `main`; refreshing the docs is a discrete commit
event for audit-trail purposes.

# DG-4 PASS (Path B numerical L_4) — superseded on review

**Date:** 2026-05-06
**Type:** dg-downgrade
**Triggering commit:** 018c188
**Triggering evidence:**
- Reviewer findings on the DG-4 v0.5.0 documentation rollout, recorded in this conversation's review pass.
- Path B extraction code: [`benchmarks/numerical_tcl_extraction.py`](../benchmarks/numerical_tcl_extraction.py).
- DG-4 sweep runner: [`reporting/benchmark_card.py`](../reporting/benchmark_card.py) `_run_dg4_sweep` and `_path_b_evaluate`.
- Card: [D1 v0.1.1](../benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.1.yaml).
- Result artefact: [D1_failure-envelope-convergence_v0.1.1_result.json](../benchmarks/results/D1_failure-envelope-convergence_v0.1.1_result.json).
- Predecessor logbook entry being superseded: [2026-05-06_dg-4-pass-path-b.md](2026-05-06_dg-4-pass-path-b.md).

**Supersedes:** `2026-05-06_dg-4-pass-path-b.md`

## Summary

The DG-4 PASS verdict recorded on 2026-05-06 (D1 v0.1.1, Path B numerical L_4 extraction, repo tag `v0.5.0`) is superseded on the record. Reviewer-side analysis surfaced two HIGH-severity defects that jointly mean the verdict's PASS predicate is not numerically defensible: (i) the Path B extraction applies the interaction-picture order-4 formula to raw Schrödinger-picture map coefficients without the `Λ_0⁻¹` similarity and the `L_0` correction, which is wrong whenever `H_S ≠ 0`; and (ii) the runner's stability-under-all-four-perturbations PASS predicate is satisfied trivially because two of the four perturbations (`upper_cutoff_factor = 20, 40`) are not consumed by the current `exact_finite_env` Path B extraction. A MEDIUM audit-completeness gap and a LOW version-semantics drift were also recorded.

The superseded verdict remains in the repository at HEAD; downstream documentation is rolled back to "DG-4 verdict superseded; pending v0.1.2 re-run with repaired Path B." DG-4 row in [`docs/validity_envelope.md`](../docs/validity_envelope.md) reverts to "RUNNER-COMPLETE; v0.1.1 verdict superseded; v0.1.2 supersedure pending."

## Detail

### HIGH-1. Path B extracts `L_2`, `L_4` in the wrong picture

[`benchmarks/numerical_tcl_extraction.py:224`](../benchmarks/numerical_tcl_extraction.py) computes

```python
L2 = dLambda2_dt
L4 = dLambda4_dt - L2 @ Lambda2
```

This is the order-4 expansion of `L_t = Λ̇_t Λ_t⁻¹` *only when `Λ_0 = id`* (interaction picture, or `H_S = 0`). The Path B pipeline at [`numerical_tcl_extraction.py:336`](../benchmarks/numerical_tcl_extraction.py) reconstructs raw Schrödinger-picture maps via `reconstruct_schrodinger_maps_from_exact_env` and at [`numerical_tcl_extraction.py:363`](../benchmarks/numerical_tcl_extraction.py) only subtracts the closed-system baseline `Λ_0(t)` as the polynomial-fit baseline; it does not apply `Λ_0⁻¹` to the extracted maps and does not include the `L_0 Λ_n Λ_0⁻¹` correction terms.

Derivation. With `L_t = Λ̇_t Λ_t⁻¹` and `Λ_t = Λ_0 + α² Λ_2 + α⁴ Λ_4 + O(α⁶)`, expanding `Λ_t⁻¹` gives `Λ_t⁻¹ = Λ_0⁻¹ - α² Λ_0⁻¹ Λ_2 Λ_0⁻¹ + O(α⁴)`. Collecting orders:

- `L_2_correct = Λ̇_2 Λ_0⁻¹ - L_0 Λ_2 Λ_0⁻¹`,
- `L_4_correct = Λ̇_4 Λ_0⁻¹ - L_0 Λ_4 Λ_0⁻¹ - L_2_correct Λ_2 Λ_0⁻¹` (and an `Λ̇_2 Λ_0⁻¹ Λ_2 Λ_0⁻¹` cross-term that cancels into `L_2_correct Λ_2 Λ_0⁻¹`).

The code's formula `L_2_code = Λ̇_2` differs from `L_2_correct` by the omitted `Λ_0⁻¹` similarity and the `L_0 Λ_2 Λ_0⁻¹` correction. For σ_x thermal at `H_S = (ω/2) σ_z` with `ω = 1`, neither term vanishes, and the Frobenius norm of the extracted `L_n^dis = L_n + i[K_n, ·]` is not the picture-invariant quantity the metric is supposed to be. The Hayden–Sorce K extraction is gauge-defined; under the *correct* extraction, picture change acts on `L_t` by Liouville-unitary similarity plus the `-i[H_S, ·]` shift, K transforms covariantly, and `‖L_n^dis‖_F` is preserved. The current code does the wrong extraction in the wrong frame; norm invariance is not in evidence.

### HIGH-2. PASS predicate trivially satisfied for two of four perturbations

The D1 v0.1.1 frozen card requires every failing candidate to be re-run under all four perturbations including `upper_cutoff_factor ∈ {20, 40}` ([D1 card line 169](../benchmarks/benchmark_cards/D1_failure-envelope-convergence_v0.1.1.yaml)). The runner's PASS predicate at [`reporting/benchmark_card.py:1424`](../reporting/benchmark_card.py) and `_classify` loop at [`reporting/benchmark_card.py:1508`](../reporting/benchmark_card.py) requires `r_4 > 1` to be stable under *all* perturbations.

But `_path_b_evaluate` at [`reporting/benchmark_card.py:1593`](../reporting/benchmark_card.py) explicitly records that `exact_finite_env` ignores the threaded `quadrature_kwargs`. With the perturbation a no-op, `r_4_perturbed == r_4_baseline`, so `_is_failing_candidate(r_4_perturbed)` is trivially true whenever `_is_failing_candidate(r_4_baseline)` is. Two of the four perturbations therefore add zero independent evidence; the predicate's "stable under all four" requirement is not actually being tested.

The result artefact at [D1_failure-envelope-convergence_v0.1.1_result.json line 38](../benchmarks/results/D1_failure-envelope-convergence_v0.1.1_result.json) does mark both `upper_cutoff_factor` checks as `operational_in_path_b: false` while still recording `verdict: PASS`. Recording this honestly as a caveat does not satisfy the frozen card's PASS predicate.

### MEDIUM. Audit-completeness gap in result artefact

`_run_dg4_sweep` constructs per-α `r_4_baseline` and per-α-per-perturbation `r_4` values in memory at [`reporting/benchmark_card.py:1467`](../reporting/benchmark_card.py) and [`reporting/benchmark_card.py:1487`](../reporting/benchmark_card.py), but the verdict notes only carry aggregate counts at [`reporting/benchmark_card.py:1719`](../reporting/benchmark_card.py); the result JSON at [D1_failure-envelope-convergence_v0.1.1_result.json line 33](../benchmarks/results/D1_failure-envelope-convergence_v0.1.1_result.json) likewise stores counts and booleans but not the actual per-α numbers, the perturbed coefficients, or the perturbation residuals. A cause-labelled DG-4 verdict requires a reproducibility-complete audit trail; the per-α sweep table and per-perturbation coefficients should be persisted.

### LOW. Version semantics drift

[CHANGELOG.md line 9 / line 15](../CHANGELOG.md) introduces `[0.5.0] — 2026-05-06` under a SemVer statement. Package metadata at [pyproject.toml line 7](../pyproject.toml) and [CITATION.cff line 20](../CITATION.cff) remain `0.3.0.dev0`. The repository's discipline (matching the v0.2.0 DG-1 PASS pattern) is that DG-PASS git tags anchor verdict immutability without bumping package metadata; the CHANGELOG should make that explicit, or pyproject + CITATION should bump.

## Validity-envelope routing

DG-4 row in [`docs/validity_envelope.md`](../docs/validity_envelope.md) is reverted to:

> RUNNER-COMPLETE on D1 v0.1.1; the 2026-05-06 v0.5.0-tagged PASS verdict is **SUPERSEDED on review** for two HIGH-severity defects (Path B picture/baseline extraction; PASS-predicate triviality on two of four perturbations) and one MEDIUM audit-completeness gap. v0.1.2 supersedure pending Path B repair (interaction-picture transformation + operational `omega_max_factor`) and audit completeness (per-α + per-perturbation `r_4` persisted).

The v0.5.0 git tag is not retracted (tags are immutable history; that is the point of the tag); the verdict it anchors is downgraded on the record.

## Routing notes

This entry is not a Sail revision and not a Ledger amendment. The CL-2026-005 v0.4 Entry 2 status (COMPATIBLE *scope-limited* on convergence) is unaffected by the supersedure: the prior DG-4 PASS authorised reporting a Path B numerical *failure-envelope witness* under the v0.1.1 frozen scope; with the verdict superseded, that authorisation lapses until v0.1.2 lands.

The supersedure decision is steward-side and does not require fresh Council deliberation. The repair work is implementation work within the DG-4 work plan v0.1.4's Phase D scope; it does not bump the work plan.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

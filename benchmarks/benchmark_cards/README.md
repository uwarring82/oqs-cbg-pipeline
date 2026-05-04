# `benchmark_cards/`

Benchmark cards live here. Each card is a YAML file with frozen-parameter,
acceptance-criterion, result, failure-mode-log, and stewardship-flag blocks.

## Card schema

The canonical schema is [`SCHEMA.md`](SCHEMA.md) (this directory). A
machine-readable, fully-annotated example is [`_template.yaml`](_template.yaml).
Together they are sufficient to author a syntactically valid card without
consulting source files.

The schema derives from two protocol sections in
[`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md):

- §1 (gauge annotation) — transcribed into the `gauge:` block.
- §4 (parameter freezing) — transcribed into the `frozen_parameters:` block.

The schema lives here, not in `docs/`, because `docs/` is locked by
Sail v0.5 §11 to the five protective documents. The schema is operational
specification, not protective scaffolding.

## Supersedure

No card may be silently edited or deleted post-result. Superseded cards are
retained with a `superseded_by:` annotation; new cards are added as new files.
A `failure_mode_log` entry on the new card explains what changed and why.
See [`SCHEMA.md`](SCHEMA.md) §Supersedure and
[`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md) §4.3.

## Card index

| Card ID | DG | Ledger anchor | Status | File |
|---|---|---|---|---|
| A1 | DG-1 | CL-2026-005 v0.4 Entry 1 (B.1, B.2; B.3 deferred to DG-2) | **pass** (2026-04-30) | [A1_closed-form-K_v0.1.1.yaml](A1_closed-form-K_v0.1.1.yaml) |
| A3 | DG-1 | CL-2026-005 v0.4 Entry 3 (B.1, B.2 thermal; B.3 deferred to DG-2) | **pass** (2026-04-30) | [A3_pure-dephasing_v0.1.1.yaml](A3_pure-dephasing_v0.1.1.yaml) |
| A4 | DG-1 | CL-2026-005 v0.4 Entry 4 (B.1 thermal; B.2 deferred to DG-2) | **pass** (2026-04-30) | [A4_sigma-x-thermal_v0.1.1.yaml](A4_sigma-x-thermal_v0.1.1.yaml) |
| B1 | DG-2 | CL-2026-005 v0.4 Entry 1.B.3 (diagonal pseudo-Kraus reduction) | **pass** (2026-05-01) | [B1_pseudo-kraus-diagonal_v0.1.0.yaml](B1_pseudo-kraus-diagonal_v0.1.0.yaml) |
| B2 | DG-2 | CL-2026-005 v0.4 Entry 1.B.3 (off-diagonal half), Entry 1.D | **pass** (2026-05-04) | [B2_pseudo-kraus-offdiagonal_v0.1.0.yaml](B2_pseudo-kraus-offdiagonal_v0.1.0.yaml) |
| B3 | DG-2 | CL-2026-005 v0.4 Entry 1.A (basis-independence) | **pass** (2026-05-04) | [B3_cross-basis-structural-identity_v0.1.0.yaml](B3_cross-basis-structural-identity_v0.1.0.yaml) |
| B4-conv-registry | DG-2 | CL-2026-005 v0.4 Entry 3.B.3 (time-dependent shift; coherent-displaced bath, pure-dephasing) | **frozen-awaiting-run** (2026-05-04) | [B4-conv-registry_v0.1.0.yaml](B4-conv-registry_v0.1.0.yaml) |
| B5-conv-registry | DG-2 | CL-2026-005 v0.4 Entry 4.B.2 (eigenbasis rotation; coherent-displaced bath, σ_x coupling) | **frozen-awaiting-run** (2026-05-04) | [B5-conv-registry_v0.1.0.yaml](B5-conv-registry_v0.1.0.yaml) |

The three DG-1 cards reached the **PASS** verdict per [DG-1 work plan v0.1.4](../../plans/dg-1-work-plan_v0.1.4.md) §4 Phase D; see [logbook/2026-04-30_dg-1-pass.md](../../logbook/2026-04-30_dg-1-pass.md) for the verdict logbook entry and [benchmarks/results/](../results/) for the JSON evidence artefacts.

Card B1 is the first DG-2 card and reached **pass** at runner version 0.1.0. All three pseudo-Kraus test_cases returned error = 0.0 (machine precision) with HPTA residuals well below the 1.0e-14 absolute bound.

Card B2 is the second DG-2 card and reached **pass** at runner version 0.1.0. All three off-diagonal pseudo-Kraus test_cases returned error = 0.0 (machine precision) with both Hermiticity-of-omega and HPTA preconditions satisfied as algebraic identities (residuals 0.0 exactly). B2 introduces the off-diagonal pseudo-Kraus card surface (`pseudo_kraus_offdiag_operators` + `pseudo_kraus_offdiag_omega`) per transcription [v0.1.1 §4b / §7a](../../transcriptions/hayden-sorce-2022_pseudokraus_v0.1.1.md); the wiring in [`reporting/benchmark_card.py`](../../reporting/benchmark_card.py) reuses B1's AST-restricted operator parser for `V_i` and adds a parameters-only scalar parser (`_eval_complex_scalar_expression`) for `omega_{ij}` entries.

Card B3 is the third DG-2 card and reached **pass** at runner version 0.1.0. B3 covers the [Sail v0.5](../../docs/) §9 DG-2 universal-default structural-identity check — basis-independence of `K_from_generator` per Entry 1.A. Its three test cases reuse known-good frozen fixtures from A1 v0.1.1 and B1 v0.1.0, and assert that K computed under the matrix-unit basis equals K computed under the su(d)-generator basis ({I, σ_x, σ_y, σ_z} / √2 for d = 2). All three test_cases returned errors at machine precision (1.57e-16, 1.57e-16, 0.0), well below the 1.0e-10 relative-Frobenius threshold; the pseudo-Kraus case's HPTA residual is 3.14e-16, well below 1.0e-14.

Card B4-conv-registry is the fourth DG-2 card and is **frozen-awaiting-run**: SCHEMA.md v0.1.2 validation passes (all 16 rules), the gauge-annotation block is canonical, and the four test_cases tag the Council-cleared displacement-mode profiles per the [subsidiary briefing v0.3.0](../../ledger/CL-2026-005_v0.4_council-briefing_displacement-convention.md) §3.1–§3.4 + §6.1 (Council Act 2, 2026-05-04, transcript at [CL-2026-005_v0.4_council-deliberation_act2_2026-05-04.md](../../ledger/CL-2026-005_v0.4_council-deliberation_act2_2026-05-04.md)). The runner-level `_DISPLACEMENT_PROFILES` registry in [`reporting/benchmark_card.py`](../../reporting/benchmark_card.py) is wired (importing from [`cbg/displacement_profiles.py`](../../cbg/displacement_profiles.py)), but the dynamical-runner extension to handle `bath_state.family == "coherent_displaced"` and the per-profile `D̄_1(t)` dispatch in [`cbg/cumulants.py`](../../cbg/cumulants.py) are deliberately scoped after the freeze, per cards-first discipline. The card covers Entry 3.B.3 only (pure-dephasing).

Card B5-conv-registry is the σ_x sibling of B4-conv-registry under the same Council-cleared profile registry. **frozen-awaiting-run**: SCHEMA.md v0.1.2 validation passes; gauge block canonical; the same four test_cases tag the four registry profiles. B5 covers Entry 4.B.2 (eigenbasis rotation in non-thermal bath under σ_x coupling) and reuses the displacement-profile registry shared with B4. Verdict criterion is the absolute Euclidean error on the (σ_x, σ_y) transverse vector of K(t) per profile, distinguishing B5's "non-zero predicted rotation" from A4 v0.1.1's "zero rotation in the thermal case". Per cards-first discipline, B5's runner handlers and the displaced-bath TCL recursion are scoped after the freeze (jointly with B4's verdict commit, since the underlying physics is shared).

The index is updated atomically when cards are committed, when their `status` field changes per [SCHEMA.md](SCHEMA.md) §Card lifecycle, or when a successor card is added.

### Superseded cards (retained for audit)

| Card ID | Version | Superseded by | Date | Reason |
|---|---|---|---|---|
| A1 | v0.1.0 | [v0.1.1](A1_closed-form-K_v0.1.1.yaml) | 2026-04-30 | Entry 1.B.3 (pseudo-Kraus) deferred to DG-2; Hayden–Sorce 2022 closed form not transcribed. See A1 v0.1.1 `failure_mode_log[0]`. |
| A3 | v0.1.0 | [v0.1.1](A3_pure-dephasing_v0.1.1.yaml) | 2026-04-30 | Entry 3.B.3 (time-dependent shift in non-thermal bath) deferred to DG-2; displacement convention on multi-mode bath under-specified. See A3 v0.1.1 `failure_mode_log[0]`. |
| A4 | v0.1.0 | [v0.1.1](A4_sigma-x-thermal_v0.1.1.yaml) | 2026-04-30 | Entry 4.B.2 (eigenbasis rotation in non-thermal bath) deferred to DG-2; same displacement-convention gap as A3. See A4 v0.1.1 `failure_mode_log[0]`. |

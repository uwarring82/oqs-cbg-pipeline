---
plan_id: dg-4-work-plan
version: v0.1.5
date: 2026-05-11
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§9 (DG-4), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entry 2 (recursive-series convergence; COMPATIBLE, scope-limited)
anchor_envelope: docs/validity_envelope.md DG-4 row (PASS at D1 v0.1.2; Path A analytic L_4 cross-validation remains a next natural milestone)
status: draft
supersedes: dg-4-work-plan_v0.1.4.md
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Work Plan - Path A analytic L_4 cross-validation

## Supersedure note

v0.1.5 supersedes v0.1.4 as a **post-verdict Tier-2.B plan revision**. The DG-4
PASS at D1 v0.1.2 is unchanged: the live verdict remains the picture-fixed
Path B numerical Richardson extraction recorded in
`benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json`.

This revision does not reopen Card D1, mutate frozen card parameters, or claim
analytic fourth-order completion. It turns the Path A follow-up named in
v0.1.4 and in the validity envelope into a steward-authored execution scaffold:
transcribe the Companion Sec. IV analytic fourth-order TCL expression, implement
it in the core `cbg.tcl_recursion` route, and cross-check the existing D1
v0.1.2 Path B failure-envelope verdict against that paper-bearing expression.

If Path A materially contradicts the Path B verdict, the response is a
separate supersedure review and logbook entry, not an in-place edit of the D1
card or result JSON.

## 1. Objective

Implement and validate the **Path A analytic L_4 source** for the thermal
Gaussian TCL recursion at order 4.

The immediate goals are:

1. Add a reviewed transcription / equation map for the Companion Sec. IV
   fourth-order TCL expression.
2. Implement the analytic `L_4` route in `cbg.tcl_recursion`, keeping `cbg/`
   independent of benchmark-side Path B extraction code.
3. Extend the existing dissipator-norm APIs so the D1 sigma_x thermal fixture
   can evaluate the parity-aware D1 metric from the analytic source:
   `coefficient_ratio = <||L_4^dis||>_t / <||L_2^dis||>_t`, with the runner
   reporting `r_4(alpha^2) = alpha^2 * coefficient_ratio` at each swept
   `coupling_strength = alpha^2`.
4. Compare analytic Path A against the existing D1 v0.1.2 Path B audit payload
   and record whether it supports, contradicts, or is inconclusive relative to
   the live DG-4 failure-envelope claim.
5. Prepare the downstream Tier-2.D literal `K_2`-through-`K_4` recursion work;
   do not claim that milestone inside this plan.

## 2. Scope

### 2.1 In scope

- A transcription artifact under `transcriptions/` or equivalent source-note
  file that maps the Companion Sec. IV equations to repository symbols and sign
  conventions.
- Analytic `n == 4` support for thermal Gaussian baths in
  `cbg.tcl_recursion.L_n_thermal_at_time`.
- Propagation of the n=4 route through:
  - `L_n_superoperator_thermal_at_time`;
  - `L_n_dissipator_thermal_at_time`;
  - `L_n_dissipator_norm_thermal_on_grid`;
  - any `K_n` / `K_total` helper that is mechanically unblocked by a reviewed
    `L_4` source.
- Tests pinning:
  - pure-dephasing sigma_z thermal `L_4 = 0` as the Feynman-Vernon Gaussian
    exactness oracle;
  - sigma_x thermal `L_4^dis` is finite and non-zero on the D1 fixture;
  - Path A and Path B agree at the classification level on the D1 v0.1.2
    failure-envelope scope, subject to the documented Path B finite-env floor.
- A cross-validation note or result artifact that is explicitly labelled
  post-verdict evidence, not a new DG-4 verdict.

### 2.2 Out of scope

- Editing D1 v0.1.2 frozen card parameters or the D1 v0.1.2 result JSON.
- Replacing the existing DG-4 PASS verdict.
- HEOM, TEMPO, MCTDH, pseudomode, or chain-mapping extraction routes. Those are
  Path C / DG-3-family method work, not this Path A plan.
- Non-thermal, coherently displaced, or non-Gaussian fourth-order formulas.
- Higher orders (`n >= 5`) and parity-aware ratios beyond `r_4`.
- DG-5 thermodynamic-discriminant work.
- Declaring the residual CL-2026-005 Entry 2 "literal K_2-K_4 recursion"
  qualifier closed. Tier-2.D is downstream of this plan and needs its own
  acceptance criteria.

### 2.3 Explicit non-claims

Completion of this plan would authorise saying that D1 v0.1.2 has been
cross-checked against an analytic Path A `L_4` implementation, within the
scope and tolerance recorded in the cross-validation artifact.

It would not authorise:

- convergence reliability claims outside the frozen D1 scope;
- analytic completion for displaced or non-thermal baths;
- a new DG-4 verdict unless a separate verdict/supersedure process is opened;
- DG-2 literal `K_2`-through-`K_4` recursion completion.

## 3. Steward decisions before implementation

These decisions must be filled in by the steward before Phase B or later code
work starts.

| Decision | Options | Default scaffold position |
|---|---|---|
| Source authority | Companion Sec. IV direct transcription; author-supplied notes; independent derivation checked against the paper. | Use a checked-in transcription artifact before code. |
| Equation-map file | New `transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.0.md`; or a plan-local appendix. | Prefer new transcription file so tests can cite it. |
| API exposure | Route `n == 4` directly through `L_n_thermal_at_time`; or land private helper first and expose only after tests. | Private helper first; expose after oracles pass. |
| Cross-validation artifact | New `benchmarks/results/D1_path-a-cross-validation_v0.1.0.json`; logbook table only; or both. | Prefer separate result JSON plus logbook summary. |
| Tolerances | Strict machine precision for sigma_z zero; bounded relative agreement with Path B for sigma_x; classification-level agreement only. | Use strict zero oracle; use classification-level Path A/Path B agreement unless steward sets numeric tolerance. |
| Routing on disagreement | Immediate supersedure review; more finite-env refinement; or mark inconclusive. | If classification differs, open supersedure review before any docs/status edit. |

## 4. Phases

### Phase A - Transcription and sign-convention gate

- Add the Companion Sec. IV equation map under `transcriptions/` or an
  explicitly named plan appendix.
- Map every symbol needed for `L_4` to repository objects:
  - left/right action convention;
  - interaction-picture versus Schrodinger-picture placement;
  - bath two-point function `C(t, s)` and conjugate pairing;
  - Lambda-inversion subtraction term `L_4 = d_t Lambda_4 - L_2 Lambda_2`;
  - dissipator extraction sign `L_n^dis := L_n + i [K_n, .]`.
- Record the rejected single nested-commutator candidate from
  `cbg/tcl_recursion.py` as a falsification note so it is not reintroduced.

**Phase A acceptance:** the transcription exists, includes equation numbers or
stable anchors, and is reviewed before implementation begins.

### Phase B - Algebraic implementation scaffold

- Implement a private analytic helper for the thermal Gaussian n=4 expression
  in `cbg.tcl_recursion`.
- Keep all benchmark-side Path B code out of `cbg/`; no imports from
  `benchmarks/` are allowed in the core implementation.
- Thread existing quadrature controls (`upper_cutoff_factor`, `quad_limit`) in
  the same style as the n=2 route.
- Preserve current `NotImplementedError` behavior for unsupported scopes:
  non-thermal, displaced, and `n >= 5`.
- Do not expose `L_n_thermal_at_time(n=4)` as supported until the Phase C
  oracles pass.

**Phase B acceptance:** the private helper can be imported, has unit tests for
input-shape and sign-convention guards, and does not change public n=4 support
yet unless Phase C lands in the same PR.

### Phase C - Physics oracles

Add tests that exercise the analytic route without depending on the Path B
fit:

1. **Sigma_z zero oracle:** pure-dephasing thermal `L_4` is exactly zero, or
   zero to a tolerance chosen in §3, across a representative time grid.
2. **Sigma_x signal oracle:** spin_boson_sigma_x thermal `L_4^dis` is finite
   and non-zero on the D1 baseline fixture.
3. **Gauge/sign oracle:** the unitary-recovery oracle still gives
   `L_0^dis = 0`, and the n=2 dissipator route remains unchanged.
4. **Parity oracle:** odd thermal Gaussian dissipator terms remain zero at n=1
   and n=3, so the even-order `r_4` metric remains the intended route.

**Phase C acceptance:** all oracles pass under the full quality gate. If any
oracle fails, stop and add a logbook routing note; do not continue to Phase D.

### Phase D - Public n=4 route

- Route `L_n_thermal_at_time(n=4)` to the analytic helper for the supported
  thermal Gaussian scope.
- Allow `L_n_superoperator_thermal_at_time(n=4)` and
  `L_n_dissipator_norm_thermal_on_grid(n=4)` to use the same source.
- Update tests that currently assert the n=4 deferral so they now assert:
  - supported thermal Gaussian n=4 returns a callable / norm array;
  - unsupported scopes continue to raise clear `NotImplementedError` messages.

**Phase D acceptance:** public n=4 support is available only for the reviewed
thermal Gaussian scope, and all previous n<=3 tests remain green.

### Phase E - D1 v0.1.2 Path A / Path B cross-validation

- Re-evaluate the D1 v0.1.2 frozen sigma_x thermal fixture using analytic
  Path A `L_4`.
- Compare against the existing Path B audit payload:
  - per-alpha classification (`passing`, `convergence_failure`,
    `truncation_artefact`);
  - maximum baseline `r_4`;
  - minimum perturbed `r_4` or coefficient ratio;
  - cause-label stability under `upper_cutoff_factor` and `omega_c`
    perturbations.
- Write the chosen cross-validation artifact from §3.
- Add a logbook entry summarising the comparison.

**Phase E acceptance:** the cross-validation is recorded as one of:

- `supports-path-b-classification`;
- `contradicts-path-b-classification`;
- `inconclusive-with-cause`.

Only the first state allows a validity-envelope follow-up saying Path A
cross-validation has landed. The second state routes to a supersedure review.
The third state records the cause, freezes any validity-envelope update, and
routes to steward review before Phase F / Tier-2.D handoff.

### Phase F - Downstream Tier-2.D handoff

If Phase E supports the Path B classification, draft the next plan revision or
standalone plan for literal `K_2`-through-`K_4` numerical recursion.

This phase is a handoff only. It does not close Tier-2.D.

## 5. Acceptance criteria for v0.1.5

This plan revision is complete when:

1. The Companion Sec. IV L_4 transcription / equation map is checked in and
   cited by tests or implementation comments.
2. `cbg.tcl_recursion.L_n_thermal_at_time(n=4)` works for the supported
   thermal Gaussian scope and still refuses unsupported scopes clearly.
3. `L_n_dissipator_norm_thermal_on_grid(n=4)` returns finite values on the
   D1 sigma_x thermal fixture.
4. The sigma_z zero oracle and sigma_x signal oracle pass.
5. A Path A / Path B cross-validation artifact is written without mutating the
   D1 v0.1.2 card or result JSON.
6. The validity envelope is updated only if the cross-validation state is
   `supports-path-b-classification`; otherwise a supersedure or inconclusive
   routing note is recorded first.
7. Quality gates pass:
   - `ruff check`;
   - `black --check .`;
   - `mypy cbg/ models/ numerical/ benchmarks/ reporting/ scripts/`;
   - `pytest -q`;
   - `sphinx-build -W -b html -E docs-site <tmpdir>`.

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **R1: Transcription error.** | Require a checked-in equation map and a steward re-read before code. Keep equation anchors in implementation comments only where they disambiguate signs or picture. |
| **R2: Left/right action or complex-conjugate pairing mistake.** | Preserve the known falsification note from `cbg/tcl_recursion.py`; add sigma_z zero and unitary-recovery tests before exposing n=4 publicly. |
| **R3: Path A / Path B mismatch.** | Treat disagreement as a scientific routing event. Do not patch the verdict in place; open a supersedure review or mark inconclusive with cause. |
| **R4: Computational cost of the analytic expression.** | Start with correctness-first implementation on small grids; cache repeated bath kernels; only optimise after oracles pass. |
| **R5: Overclaiming analytic completion.** | This plan is Path A cross-validation for DG-4. Literal `K_2`-through-`K_4` recursion remains Tier-2.D until a separate plan closes it. |
| **R6: Architecture drift.** | Keep Path A in `cbg/`; keep Path B in `benchmarks/`; no `cbg -> benchmarks` dependency. |

## 7. Dependencies

- DG-4 D1 v0.1.2 PASS remains the live verdict.
- Path B numerical extraction remains available through
  `benchmarks.numerical_tcl_extraction` and
  `reporting.benchmark_card._run_dg4_sweep`.
- Current n=4 deferral lives in `cbg.tcl_recursion.L_n_thermal_at_time`.
- Existing transcription coverage is incomplete for this plan: `transcriptions/`
  currently contains Letter Appendix D and Hayden-Sorce notes, but not the
  Companion Sec. IV L_4 expression.
- Tier-2.D literal recursion depends on the Path A result from this plan.

## 8. Scaffold TODOs for the steward

- [ ] Choose and record the exact source authority for Companion Sec. IV.
- [ ] Name the transcription artifact path.
- [ ] Fill the tolerance table for the sigma_z zero oracle and Path A / Path B
      comparison.
- [ ] Decide whether the cross-validation artifact is JSON, logbook-only, or
      both.
- [ ] Decide whether a successful Phase E updates only the validity envelope or
      also `docs/benchmark_protocol.md`.
- [ ] Decide whether to open Tier-2.D as `dg-2-work-plan` follow-up or as a
      separate recursion plan after Phase E.

---

*Plan version: v0.1.5. Drafted 2026-05-11 as a Tier-2.B scaffold for DG-4 Path A
analytic L_4 cross-validation. Supersedes v0.1.4 for post-verdict Path A
follow-up planning only; it does not change the D1 v0.1.2 verdict. CC-BY-4.0
(see ../LICENSE-docs).*

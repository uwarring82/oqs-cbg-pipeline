---
plan_id: dg-4-path-b-richardson-extraction
version: v0.1.0
date: 2026-05-06
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§5 (Tier 3), 9 (DG-4), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entry 2 (recursive-series convergence; COMPATIBLE, scope-limited)
anchor_envelope: docs/validity_envelope.md DG-4 row (SCOPED — Phase B partial; L_4 path unresolved)
status: draft
supports: dg-4-work-plan_v0.1.4.md Phase B.2 Path B
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Path B Work Plan — Numerical TCL extraction

## 1. Objective

Provide the bounded numerical route for the DG-4 `L_4` blocker recorded in
`cbg.tcl_recursion.L_n_thermal_at_time(n=4)`: reconstruct reduced dynamical
maps from `benchmarks/exact_finite_env`, fit the even-amplitude expansion, and
extract a numerical order-4 TCL generator by

```text
Lambda_t(lambda) = Lambda_0(t) + lambda^2 Lambda_2(t) + lambda^4 Lambda_4(t) + O(lambda^6)
L_2(t) = d_t Lambda_2(t)
L_4(t) = d_t Lambda_4(t) - L_2(t) Lambda_2(t)
```

Here `lambda` is the interaction-amplitude extraction parameter. The repository
model specs expose the ohmic spectral-density key `coupling_strength`, and
`benchmarks.exact_finite_env` discretises mode couplings as
`g_k proportional to sqrt(coupling_strength)`. Therefore the Path B runner
sets `coupling_strength = lambda^2` by default when it wants an even-power fit
in `lambda`. A direct fit in the card's `coupling_strength` would instead use
powers `{1, 2}` and must be labelled separately.

This is explicitly **Path B**, not the canonical analytic recursion. Its
outputs may unblock exploratory pilot checks for D1 v0.1.1, but they do not
replace the paper-bearing `cbg.tcl_recursion` implementation that Path A would
provide.

## 2. Scope

### 2.1 In scope

- A benchmark-side module, `benchmarks/numerical_tcl_extraction.py`, with:
  - process-tomography reconstruction of raw Schrodinger-picture maps from
    `benchmarks.exact_finite_env` builders;
  - least-squares Richardson extraction of even amplitude-order coefficients
    (`Lambda_2`, `Lambda_4`);
  - finite-difference reconstruction of `L_2` and `L_4`;
  - small diagnostics exposing fit residuals and matrix rank.
- Unit tests for the algebraic pieces using synthetic maps with known
  coefficients.
- A documented interface boundary: `cbg/` must not import this module.

### 2.2 Out of scope

- Promoting the numerical `L_4` into `cbg.tcl_recursion`.
- Declaring DG-4 PASS or freezing D1 v0.1.1.
- Treating finite-bath results as a canonical closed-form formula.
- HEOM/TEMPO/pseudomode infrastructure. That remains Path C and needs its own
  work plan.

### 2.3 Non-claims

This plan does not claim that a finite bath at any chosen truncation has the
same convergence boundary as the continuum ohmic model. It provides a
controlled extraction path with visible residuals and validation oracles so the
steward can decide whether Path B is useful evidence or only a development
probe.

## 3. Phases

### Phase B-PB.0 — Scaffold and algebraic tests

- Add `benchmarks/numerical_tcl_extraction.py`.
- Implement generic helpers:
  - `reconstruct_superoperator_from_basis_outputs`;
  - `fit_even_alpha_series`;
  - `finite_difference_time_derivative`;
  - `extract_tcl_generators_order4`.
- Add synthetic tests:
  - exact recovery of known `Lambda_2`, `Lambda_4`;
  - exact recovery of `L_4 = d_t Lambda_4 - L_2 Lambda_2` on a polynomial time
    fixture;
  - input-shape and rank-deficiency guards.

### Phase B-PB.1 — Exact finite-env tomography adapter

- Implement `reconstruct_schrodinger_maps_from_exact_env(builder, model_spec,
  t_grid, ...)`.
- Use the matrix-unit basis as linear tomography inputs. These inputs need not
  be physical density matrices; `exact_finite_env.propagate` is linear in the
  joint initial operator.
- Keep the output explicitly named as raw Schrodinger-picture maps. Consumers
  must either pass a closed-system baseline into the fit or transform to the
  interaction picture before applying the expansion.

### Phase B-PB.2 — Alpha-grid extraction runner

- Add a small orchestration helper that:
  - clones the frozen model spec;
  - mutates `bath_spectral_density.coupling_strength = lambda^2` over a chosen
    extraction-amplitude grid by default;
  - reconstructs maps for each alpha;
  - fits even orders `{2, 4}` against a supplied baseline.
- Emit residual and conditioning diagnostics. A rank-deficient or visibly
  ill-conditioned fit is a hard failure for the run, not a DG-4 signal.

### Phase B-PB.3 — Physics validation oracles

Before Path B can feed the DG-4 D1 pilot, require:

1. **Alpha-zero / closed-baseline oracle:** after removing the closed-system
   baseline, the fitted interaction-picture correction is numerically zero at
   alpha = 0.
2. **Pure-dephasing thermal oracle:** in the sigma_z thermal Gaussian fixture,
   the extracted `L_4` must vanish within a tolerance that tightens under
   finite-bath refinement. This is the Feynman-Vernon Gaussian exactness gate.
3. **Sigma_x signal oracle:** in the sigma_x thermal fixture, the extracted
   dissipator norm for `L_4` is non-zero at representative `t > 0`.
4. **Finite-bath refinement probe:** repeat at at least two `(n_bath_modes,
   n_levels_per_mode)` settings. A stable sign / order-of-magnitude signal is
   required before the result is used in D1 v0.1.1 planning.

### Phase B-PB.4 — DG-4 integration decision

If the oracles pass, Path B may provide a development-only `L_4` estimate for
the D1 v0.1.1 pilot. The result must be labelled `numerical-extraction` in
notes and must not be recorded as the analytic Phase B.2 completion. If the
oracles fail, route back to Path A or Path C.

## 4. Acceptance criteria

This auxiliary plan is complete when:

1. The module and synthetic tests land.
2. The exact finite-env tomography adapter reconstructs well-conditioned maps
   on a small fixture.
3. The pure-dephasing thermal `L_4 = 0` oracle is demonstrated under at least
   one finite-bath setting and improves under refinement.
4. The sigma_x thermal `L_4` pilot either shows a stable non-zero signal or
   records a clear no-go result.

Completion of this plan is **not** DG-4 PASS. It only resolves whether Path B
is strong enough to support Phase A.bis / D1 v0.1.1 pilot work.

## 5. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **PB-R1: Finite-bath artefact mistaken for continuum `L_4`.** | Require the sigma_z zero oracle and finite-bath refinement probes before any D1 pilot use. |
| **PB-R2: Fit conditioning hides lambda^6 contamination.** | Use more lambda samples than coefficients, report rank / singular values / residual norms, and keep lambda values small enough for the even expansion. |
| **PB-R3: Time differentiation amplifies noise.** | Start with smooth time grids, use central finite differences, and report sensitivity to grid refinement before freezing any result. |
| **PB-R4: Schrodinger-vs-interaction picture mismatch.** | The adapter names raw Schrodinger-picture maps explicitly. Consumers must remove or provide the closed-system baseline before fitting. |
| **PB-R5: Architecture drift (`cbg` depending on `benchmarks`).** | Keep all Path B code in `benchmarks/`; `cbg.tcl_recursion` continues to raise for n=4 until Path A or an explicitly accepted analytic route lands. |

## 6. Routing

- **Path A remains preferred** if Companion Sec. IV or an equivalent
  transcription becomes available.
- **Path B is the current no-paper-access move**: useful for a pilot and for
  falsifying candidate formulas, but labelled numerical extraction.
- **Path C remains separate** and should be planned as a new reference-method
  effort, not as an in-place DG-4 Phase B patch.

---

*Plan version: v0.1.0. Drafted 2026-05-06 as an auxiliary route plan supporting
DG-4 work plan v0.1.4 Phase B.2 Path B. CC-BY-4.0 (see ../LICENSE-docs).*

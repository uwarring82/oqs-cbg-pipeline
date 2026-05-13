---
artifact_id: cbg-companion-sec-iv-l4-phase-c-physics-oracles-card
version: v0.1.1
date: 2026-05-13
type: verification-card / pre-code-oracle
status: frozen
supersedes: colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-c-physics-oracles-card_v0.1.0.md
parent_transcription: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md
parent_card: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_n4-small-grid-verification-card_v0.1.0.md
target_implementation: cbg/tcl_recursion.py — Phase C private assembled-L_4 helper (re-implementation per v0.1.1)
anchor_plan: plans/dg-4-work-plan_v0.1.5.md §4 Phase C
release_gate: work plan v0.1.5 §4 Phase C acceptance — all four physics oracles pass under the full quality gate; public n=4 route remains deferred to Phase D
reviewer: Ulrich Warring
review_date: 2026-05-13
review_state: frozen-pre-implementation (corrects v0.1.0 θ-window scope omission)
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Phase C pre-code verification card — physics oracles for assembled L_4 (v0.1.1, θ-aware)

> **Status: frozen (2026-05-13).** This v0.1.1 supersedes v0.1.0 to
> correct the θ-window scope omission. The shared fixtures (§2), API
> contract (§3), and four oracle gates (§4) are carried forward
> unchanged. The added content is §3a (θ-aware literal-Eq. integration
> rules) and §3b (forbidden-anti-pattern: Wick-pre-cancellation across
> terms with mismatched θ windows). The §4.1 σ_z zero oracle gate at
> `atol = 1e-10` is retained — but the v0.1.0 boundary-collapsed
> survivor-form path is now explicitly forbidden, since it gave a
> non-converging ~1e-2 residual on the σ_z off-diagonal cancellation
> (audit: commit 49b92d5 + the v0.1.0 implementation experiment
> documented below).

## 0. Provenance and role

This v0.1.1 successor consumes everything v0.1.0 consumed, plus the
v0.1.0 implementation post-mortem:

- the verbatim-transcribed Companion Eqs. (15), (16), (17), (22), (28),
  (43), (45), (69)–(73) from the released parent transcription
  ([Companion Sec. IV L_4 transcription v0.1.1](colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md)),
  with particular attention to **Eqs. (15) and (22)**: each `D` factor
  in the recursion expansion of Eq. (27) carries its **own** θ-window
  per Eq. (15), not a single shared outer θ. Eq. (22) confirms the
  boundary delta convention `∫_0^t dτ δ_{τ,t} f(τ) = f(t)` (verified
  against local VoR PDF, 2026-05-13);
- the closed-by-steward row-2.3 chain-reversal-and-swap rule;
- the §2.8 Phase B `_D_bar_4_companion` private helper (commit `becccf9`),
  pinned by the small-grid card v0.1.0 (commit `ae20806`);
- the v0.1.0 Phase C card (commit `49b92d5`);
- **the v0.1.0 implementation experiment (transient, not committed)**
  which produced a non-converging σ_z off-diagonal residual ≈ −0.0169
  in the `h → 0` limit. Audit per §3b below.
- the work plan v0.1.5 §4 Phase C four-oracle gate.

The structural change from v0.1.0 to v0.1.1 is:

- **v0.1.0 implicitly invited** a "boundary-collapsed survivor form"
  implementation that pre-cancels Wick pairings against Eq. (69)–(73)
  subtraction terms before integration.
- **v0.1.1 explicitly forbids** this pre-cancellation and **pins the
  literal θ-aware term-by-term integration** of Eqs. (69)–(73), with
  each `Ḋ` × `D̄`/`D` factor product carrying its own Eq. (15) θ-window
  and its own boundary delta.

## 1. Purpose and scope

### 1.1 What this card does

- Operationalises work plan v0.1.5 §4 Phase C as four executable
  oracle gates against an assembled-L_4 private helper, with
  implementation-facing details (API, fixtures, time grid, basis,
  tolerances, and the **θ-aware integration discipline**) pinned.
- Provides a frozen, citable target for the Phase C implementation
  re-write following v0.1.0's failed survivor-form attempt.

### 1.2 What this card does not do

- It does not change the §2 fixtures, §3 API contract, or §4 oracle
  gates — those are carried forward unchanged from v0.1.0.
- It does not unbind the public `L_n_thermal_at_time(n=4)` route.
- It does not authorise any change to D1 v0.1.2 frozen parameters
  or the released v0.1.1 transcription.

### 1.3 Carry-forward from v0.1.0

All of v0.1.0's:
- §2 frozen fixtures (D1-baseline-style: σ_x/σ_z, ω=1.0, ω_c=10.0,
  T=0.5, α=0.02, time grid `linspace(0, 2.0, 11)`, `t_idx=5`,
  matrix-unit basis);
- §3 API contract for `_L_4_thermal_at_time_apply(t_idx, t_grid, H_S,
  A, *, bath_state, spectral_density, ...)`;
- §4 oracle gates (σ_z zero at `atol=1e-10`, σ_x signal `1e-6 ≤
  ‖L_4^dis‖_F ≤ 1e6`, L_0^dis=0 + n=2 regression at `atol=rtol=1e-12`,
  L_1=L_3=0 at `atol=1e-12`);
- §5 implementation hand-off (test file at
  `tests/test_n4_physics_oracles.py`);
- §6 out-of-scope reminders;

are carried forward verbatim. The diff vs. v0.1.0 is the addition of
**§3a (θ-aware integration discipline)** and **§3b (forbidden
anti-pattern: Wick-pre-cancellation)** below.

## 2. Frozen shared fixtures (unchanged from v0.1.0)

Refer to v0.1.0 §2. Pinned values:

```yaml
omega: 1.0
bath_state: {family: thermal, temperature: 0.5}
spectral_density:
  family: ohmic
  coupling_strength: 0.02
  cutoff_frequency: 10.0
quadrature_controls:
  upper_cutoff_factor: 30.0
  quad_limit: 200
time_grid:
  t_start: 0.0
  t_end: 2.0
  n_points: 11
t_idx_oracle: 5
basis: matrix_unit
```

## 3. API contract (unchanged from v0.1.0)

Refer to v0.1.0 §3 for the `_L_4_thermal_at_time_apply` signature.
Repeated here:

```python
def _L_4_thermal_at_time_apply(
    t_idx: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> Callable[[np.ndarray], np.ndarray]:
    """L_4[X] at t = t_grid[t_idx] for thermal Gaussian bath."""
```

## 3a. θ-aware literal-Eq. (69)–(73) integration discipline (new in v0.1.1)

### 3a.1 The principle

Companion Eq. (28) at `n = 4` reads:

```math
\mathcal{L}_4[X] = (i)^4 \sum_{k=0}^{4} (-)^k
  \int_0^t \mathrm{d}\boldsymbol{\tau}_1^k \, \mathrm{d}\boldsymbol{s}_1^{4-k}
  \; \bar{\mathcal{D}}(\boldsymbol{\tau}_1^k, \boldsymbol{s}_1^{4-k})
  \; A(\boldsymbol{\tau}_1^k) \, X \, A^\dagger(\boldsymbol{s}_1^{4-k})
```

where the integration measure `dτ_1^k ds_1^{4-k}` is the iterated
nested-simplex measure per **Eq. (17)** — i.e. each τ-chain and each
s-chain carries the descending θ-ordering of **Eq. (16)** internally.

Each generalized cumulant `D̄(τ_1^k, s_1^{4-k})` from Eqs. (69)–(73)
**factors** into terms of the form:

```math
\bar{\mathcal{D}}_k = \dot{D}(\text{full chain}) - \sum_i \dot{D}(\text{partial chain}_i^L) \cdot D(\text{partial chain}_i^R)
```

**Each factor** `Ḋ(...)` or `D(...)` carries its own θ-window via
Eq. (15):

```math
D(\boldsymbol{\tau}_1^k, \boldsymbol{s}_1^{n-k})
  = \operatorname{Tr}_E\{ B^R(\boldsymbol{s}_1^{n-k}) \circ B^L(\boldsymbol{\tau}_1^k) [\rho_E] \}
  \; \theta_{\boldsymbol{\tau}_1^k} \; \theta_{\boldsymbol{s}_1^{n-k}}
```

i.e. each `D` is **identically zero** outside its OWN factor's
descending θ-region for its OWN argument tuple. When the recursion
factorises `Ḋ × D` (e.g. Eq. 70 Term 2: `Ḋ(τ_1, s_1) D(s_2^3)`), the
SECOND factor `D(s_2^3)` is zero unless `s_2 > s_3 > … > s_{n-k}` —
**but** the FIRST factor `Ḋ(τ_1, s_1)` has a SHORTER chain with a
WEAKER (or empty) θ-constraint on its OWN arguments, in particular
no constraint between `s_1` and `s_2`.

**Consequence.** Different terms in a single Eq. (69)–(73) integrate
over **different effective domains** in the outer Eq. (28) measure.
A Wick pairing in the full-chain `Ḋ(τ_1^k, s_1^{n-k})` term and an
algebraically-similar product in a subtraction term are only
"equal" on the **overlap** of their θ-domains; outside the overlap,
the subtraction term still contributes and the full-chain term does
not.

### 3a.2 The implementation discipline

For each k ∈ {0, 1, 2, 3, 4}, the Phase C implementation MUST:

1. **Enumerate Eqs. (69)–(73) verbatim**, term by term. The
   surface-level expressions from the parent transcription §4.2:
    - Eq. (69) k=0: `D̄(s_1^4) = Ḋ(s_1^4) − Ḋ(s_1^2) D(s_3^4)`
    - Eq. (70) k=1: `D̄(τ_1, s_1^3) = Ḋ(τ_1, s_1^3) − Ḋ(τ_1, s_1) D(s_2^3) − Ḋ(s_1^2) D(τ_1, s_3)`
    - Eq. (71) k=2: `D̄(τ_1^2, s_1^2) = Ḋ(τ_1^2, s_1^2) − Ḋ(τ_1, s_1) D(τ_2, s_2) − Ḋ(s_1^2) D(τ_1^2) − Ḋ(τ_1^2) D(s_1^2)`
    - Eq. (72) k=3: `D̄(τ_1^3, s_1) = Ḋ(τ_1^3, s_1) − Ḋ(τ_1, s_1) D(τ_2^3) − Ḋ(τ_1^2) D(τ_3, s_1)`
    - Eq. (73) k=4: `D̄(τ_1^4) = Ḋ(τ_1^4) − Ḋ(τ_1^2) D(τ_3^4)`

2. For each term, expand each `Ḋ(arguments)` per Eq. (22) into
   `D(arguments) × (δ_{τ_1, t} + δ_{s_1, t})` (where `τ_1`/`s_1` refer
   to the chain-largest times **of that factor's argument tuple**,
   not the outer chain).

3. For each `(k, term, boundary-delta-choice)`, derive the
   **post-collapse integration domain** as the intersection of:
   - the outer Eq. (28) τ-chain ordering `t > τ_1 > … > τ_k > 0`
     (with the relevant τ_1 collapsed to `t` if `δ_{τ_1, t}` fires
     for the OUTER τ_1);
   - the outer Eq. (28) s-chain ordering `t > s_1 > … > s_{4-k} > 0`
     (analogously for s_1);
   - **the θ-window of each `D` factor in the term** per Eq. (15)
     — typically only the SUB-chain ordering of that factor's
     arguments.

4. **Apply Wick's theorem inside each raw `D` factor INDIVIDUALLY**
   (parent artifact §4.4: three bosonic pairings of the 4-point and
   the trivial 2-point). **DO NOT pre-cancel Wick pairings across
   different terms of the same Eq. (69)–(73).** That cross-term
   cancellation is only algebraically valid on the overlap of the
   θ-domains, which differ.

5. Integrate each `(k, term, boundary-delta-choice)` contribution on
   its **own** 3-D domain (after the single boundary-delta
   collapse), using a quadrature rule that respects the simplex /
   non-simplex shape correctly (e.g. nested 1-D trapezoidal on
   simplex factors; standard 1-D trapezoidal on free axes).

6. Sum all `(k, term, boundary-delta-choice)` contributions
   weighted by the Eq. (28) `(-)^k` factor and the per-term sign
   from Eqs. (69)–(73), multiplied by the operator chain
   `A(τ_1^k) X A^†(s_1^{n-k})` per Eqs. (10), (11) at the post-
   collapse times (boundary times equal `t`, free times are the
   integration variables).

### 3a.3 The Phase B helper's role under v0.1.1

`_D_bar_4_companion(tau_args, s_args, *, t, …)` remains the
**pointwise verifier** at fully-θ-saturated grid configurations
(all-inner-descending, with the boundary delta of the corresponding
side firing). It is **not** the full L_4 integrand evaluator — it
returns a single scalar at a single point in time, having pre-
cancelled internal contributions because all its constituent `D`
factors are evaluated on the same (descending) argument tuple. The
helper's own correctness is unaffected; it is used for spot-check
testing only, not for assembly.

## 3b. Forbidden anti-pattern: Wick-pre-cancellation across terms

The v0.1.0 implementation experiment computed boundary-collapsed
"survivor forms" for each `(k, branch)` by pre-cancelling Wick
pairings between the full-chain `Ḋ(τ_1^k, s_1^{n-k})` Wick expansion
and the subtraction terms `Ḋ × D` of Eqs. (69)–(73). For example,
at `k = 1` τ-branch:

```text
Eq. (70) τ-branch (δ_{τ_1, t} = 1, δ_{s_1, t} = 0):
  Term 1: D(t, s_1, s_2, s_3) → Wick gives 3 pairings.
  Term 2: -D(t, s_1) × D(s_2, s_3) = -C(s_1, t) × C(s_3, s_2).

  Survivor (after pre-cancellation against Term 2):
    D̄_τ_k1 = C(s_3, s_1) C(s_2, t) + C(s_3, t) C(s_2, s_1)
    [Wick pairing 1 cancels Term 2]
```

**This pre-cancellation is INVALID.** Term 2's `D(s_2, s_3)` carries
θ-window `θ_{s_2^2} = θ(s_2 > s_3)` from Eq. (15), with no
constraint relating `s_1` to `s_2`. Term 1's full Wick `D(t, s_1,
s_2, s_3)` carries `θ_{s_1^3} = θ(s_1 > s_2 > s_3)`. The pre-
cancellation between Term 1's first Wick pairing and Term 2
assumes both are integrated on the SAME outer simplex; in fact
Term 2 has the LARGER domain `{s_1 ∈ [0, t], s_2 > s_3 ∈ [0, t]}`,
which includes the region `s_2 > s_1` that Term 1 does not.

**The v0.1.0 experiment demonstrated this empirically**: with the
σ_z zero oracle (`A = σ_z`, `[A, A_I] = 0`, Feynman-Vernon
truncation predicts `L_4 = 0`), the boundary-collapsed survivor-form
implementation produced `‖L_4[E_01]‖_F ≈ 0.0169` in the `h → 0`
limit (verified at `n ∈ {6, 11, 21, 41}` grid resolutions; the
residual converged to a non-zero plateau rather than decreasing as
`O(h²)`). Diagonal X (`E_00`, `E_11`) passed at machine zero
through accidental sign alternation. Off-diagonal X (`E_01`, `E_10`)
revealed the structural error.

**Phase C v0.1.1 implementations MUST NOT** apply Wick pre-
cancellation across the Eqs. (69)–(73) sub-terms. Each subterm is
integrated **literally** on its own θ-domain, as described in §3a.

## 4. The four physics oracles (unchanged from v0.1.0)

Refer to v0.1.0 §4 for the σ_z zero, σ_x signal, gauge/sign
(L_0^dis = 0 + n=2 regression marker with card-pinned reference
value `[[0, -0.26338525879711916 + 0.04707234985666798j], [+0.26338525879711916 - 0.04707234985666798j, 0]]`),
and parity (L_1 = L_3 = 0) oracle gates and tolerances. The
**§4.1 σ_z zero oracle gate remains at `atol = 1e-10`** —
steward-tightenable per work plan §3, but the v0.1.1 implementation
MUST hit it via the §3a literal θ-aware integration, not by
loosening.

The v0.1.0 §4.1 "trapezoidal-on-N=11 quadrature limit" escalation
clause is hereby **retracted**: the σ_z residual at the
`h → 0` limit is not a trapezoidal quadrature issue, it is a
structural derivation issue from the pre-cancellation. With the §3a
discipline, σ_z `atol = 1e-10` is expected to be achievable on a
trapezoidal N=11 internal grid (since the integrand sums to zero
algebraically when computed correctly, and trapezoidal preserves
algebraic identities to its quadrature precision).

## 5. Implementation hand-off (refined from v0.1.0)

When the steward starts Phase C coding against v0.1.1:

1. **Discard the boundary-collapsed survivor-form draft.** It is
   irrecoverable as a path to `atol = 1e-10` σ_z zero. The bug is
   structural, not numerical.

2. Re-implement `_L_4_thermal_at_time_apply` as a literal sum over
   `(k, term, branch)` triples per §3a, with each contribution
   integrated on its own 3-D domain. The natural enumeration is:

    ```text
    for k in {0, 1, 2, 3, 4}:
        for term in Eqs. (69)-(73) at this k:
            for branch in {τ_1=t, s_1=t} where the term's Ḋ fires:
                compute integrand on the term's own θ-domain
                accumulate weighted contribution
    ```

3. For each `(k, term, branch)` triple, the integrand has the
   structure: `±` × `D(boundary_collapsed_args)` × `D(other_factor_args)`
   × `operator_chain`. Apply Wick to each `D` factor **separately**.

4. Use nested 1-D trapezoidal for simplex factors (factors of the
   form `θ_{s_a^b}`) and standard 1-D trapezoidal for free axes.
   The 3-D domain decomposes naturally into simplex × free-axis
   factors that are computed independently.

5. Update `tests/test_n4_physics_oracles.py` (no changes required —
   the test file references v0.1.0 by version, and v0.1.1 carries
   forward the same oracle gates; the test cite should be updated
   to v0.1.1 in the docstring after the implementation lands).

6. Run the full quality gate per work plan v0.1.5 §5 acceptance
   criterion 7.

7. On all-pass at `atol = 1e-10` for σ_z and the bounding box for
   σ_x: proceed to Phase D.

8. **If σ_z still fails at `atol = 1e-10`** under §3a literal
   integration: the failure is now genuinely a quadrature issue
   (since structural correctness is enforced by §3a), and the
   work plan §3 "steward-tightenable" carve-out activates. A
   successor v0.1.2 card would then loosen σ_z atol to a measured
   value. **But this should not be needed**, since the literal
   integration should give exact algebraic cancellation up to
   trapezoidal error on each domain.

## 6. Out-of-scope reminders (unchanged from v0.1.0)

Refer to v0.1.0 §6.

## 7. Steward freeze sign-off

> I have drafted v0.1.1 to correct the θ-window scope omission in
> v0.1.0. The shared fixtures (§2), API contract (§3), and four
> oracle gates (§4) are carried forward verbatim. The added content
> is §3a (θ-aware literal-Eq. integration discipline) and §3b
> (forbidden anti-pattern: Wick-pre-cancellation across terms with
> mismatched θ windows). The §4.1 σ_z zero oracle at `atol = 1e-10`
> is retained; the v0.1.0 "trapezoidal quadrature limit" escalation
> clause is retracted, since the residual was a structural derivation
> error, not a numerical quadrature error. Per cards-first
> discipline, this file is content-immutable post-commit.
>
> Reviewer: Ulrich Warring  Date: 2026-05-13
>
> Version at freeze: v0.1.1 (release state: frozen-pre-implementation)

## Appendix — change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1.0 | 2026-05-13 | Initial draft and freeze. Pinned API contract, shared fixtures, four oracle gates, implementation hand-off, out-of-scope reminders, steward freeze sign-off. Included a "trapezoidal-on-N=11 quadrature limit" escalation clause for the σ_z zero oracle. | Local steward draft; cards-first discipline. (Commit `49b92d5`.) |
| v0.1.1 | 2026-05-13 | **Supersedes v0.1.0.** Added §3a (θ-aware literal-Eq. (69)–(73) integration discipline) and §3b (forbidden anti-pattern: Wick-pre-cancellation across terms with mismatched θ windows). The v0.1.0 implementation experiment, which pre-cancelled Wick pairings against subtraction terms before integration, produced a non-converging σ_z off-diagonal residual ≈ −0.0169 in the `h → 0` limit; the audit (steward + local VoR PDF) identified the root cause as Eq. (15) θ-windows mismatched between terms, NOT a quadrature error. v0.1.1 retracts v0.1.0's "trapezoidal quadrature limit" escalation clause for σ_z and pins the literal θ-aware approach as the required implementation route. §2 (fixtures), §3 (API contract), §4 (oracle gates), §5 (hand-off), §6 (out-of-scope) carried forward unchanged. Card-pinned n=2 regression reference value retained verbatim. | Local steward draft; cards-first discipline. |

*Verification card version: v0.1.1 (frozen 2026-05-13). Supersedes
v0.1.0 to pin the θ-aware literal-Eq. (69)–(73) integration as the
required Phase C implementation route. Operationalises work plan
v0.1.5 §4 Phase C as four executable oracle gates against an
assembled-L_4 private helper that consumes the Phase B
`_D_bar_4_companion` (commit `becccf9`) and the D1 v0.1.2 baseline-
style bath fixture. Public n=4 exposure remains deferred to Phase D.
CC-BY-4.0 (see ../LICENSE-docs).*

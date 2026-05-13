---
artifact_id: cbg-companion-sec-iv-l4-n4-small-grid-verification-card
version: v0.1.0
date: 2026-05-13
type: verification-card / pre-code-oracle
status: frozen
parent_transcription: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md
target_implementation: cbg/tcl_recursion.py — Phase B n=4 thermal Gaussian D̄ evaluator (not yet implemented)
anchor_plan: plans/dg-4-work-plan_v0.1.5.md §4 Phase B
release_gate: Companion §10 implementation reminder, item (b): "small-grid verification of the direct Eq. (69)–(73) formulas using the row-2.3 chain-reversal-and-swap at mixed order"
reviewer: Ulrich Warring
review_date: 2026-05-13
review_state: frozen-pre-implementation
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Phase B pre-code verification card — n=4 small-grid oracle for Companion Eqs. (69)–(73)

> **Status: frozen (2026-05-13).** This card pins the by-hand
> table-expanded reference values that the Phase B n=4 direct evaluator
> must reproduce, on two small fixed time grids, at strict numerical
> equality. The card lands **before** the Phase B private helper exists.
> Per the cards-first discipline, this file is content-immutable
> post-commit; revisions are by superseding successor at a new version.

## 0. Provenance and role

This card operationalises the §2.8 small-grid verification gate carried
forward by the released v0.1.1 transcription artifact
([Companion Sec. IV L_4 transcription v0.1.1](colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md)).
That artifact's §10 sign-off explicitly defers the small-grid check to
the implementation-side guard:

> "Before Phase B code lands, the steward must still: ... (b) sign off
> a small-grid verification of the direct Eq. (69)–(73) formulas using
> the row-2.3 chain-reversal-and-swap at mixed order."

This card freezes:

1. A fixed bath fixture (spectral density + state) under which `C(a, b)`
   is reproducibly computable.
2. Two fixed time grids that independently exercise the τ-side and
   s-side boundary deltas of `Ḋ` (Companion Eq. 22).
3. The substitution rules (Eq. 22 boundary delta; row-2.3 swap; thermal
   Gaussian 4-point Wick split).
4. By-hand closed-form expected values for each of the five mixed-order
   cumulants `D̄(τ_1^k, s_1^{n−k})` at `n = 4`, `k ∈ {0, 1, 2, 3, 4}`,
   evaluated on each grid. These are the **independent oracle**.
5. The primary-oracle API contract that Phase B's direct evaluator must
   satisfy.
6. A strict numerical-equality acceptance criterion.
7. A secondary supporting diagnostic that is explicitly **not** the
   acceptance gate.

## 1. Purpose and scope

### 1.1 What this card does

- Provides a frozen, citable oracle for the Phase B n=4 direct
  evaluator before any implementation code is written.
- Makes the by-hand reference values reproducible: pinning the bath
  fixture is sufficient to evaluate every `C(a, b)` in §5 numerically.
- Routes the Phase B test (`tests/test_n4_small_grid_verification.py`,
  to be added in Phase B) to a single, unambiguous acceptance gate.

### 1.2 What this card does not do

- It does not implement the evaluator. The Phase B helper lives in
  `cbg.tcl_recursion` and is the subject under test, not part of the
  oracle.
- It does not derive Eqs. (69)–(73); those are transcribed verbatim in
  the parent artifact §4.2.
- It does not bind the bath fixture choice for any other downstream
  test or benchmark. The fixture below is local to this card.
- It does not authorise any change to the released v0.1.1 transcription
  artifact or to D1 v0.1.2 frozen parameters.

### 1.3 What "small grid" means here

Two time tuples, each of length 5 (one outer evaluation time `t` plus
two chains of length 4). The grids are chosen to make the boundary
delta `δ_{τ_1, t}` or `δ_{s_1, t}` of `Ḋ` (Eq. 22) fire on exactly one
side per grid. This isolates each side's contribution to the
substitution rule and gives independent checks of all five formulas.

## 2. Frozen bath fixture

For numerical reproducibility of `C(a, b) := ⟨B(a) B(b)⟩` at the grid
times:

```yaml
bath_state:
  family: thermal
  temperature: 1.0
spectral_density:
  family: ohmic
  coupling_strength: 0.1     # α
  cutoff_frequency: 1.0      # ω_c
quadrature_controls:
  upper_cutoff_factor: 30.0
  quad_limit: 200
```

These are the existing `cbg.bath_correlations.two_point` defaults for
quadrature, with α and ω_c chosen at a representative ohmic scale and
temperature `T = 1.0` (in the same units as ω_c). `C(a, b)` is
evaluated through `cbg.bath_correlations.two_point(a, b, …)` at this
fixture; the function depends on `a − b` by stationarity, so the grid
values are what determine the numerical values of `C`.

**Stationarity convention.** Because `two_point` returns `C(t1 − t2)`,
the operator order in `⟨B(a) B(b)⟩` is preserved by always calling
`two_point(a, b, …)` with `a` as the leftmost operator's time and `b`
as the rightmost. The card's `C(a, b)` notation matches this call
order verbatim.

## 3. Frozen time grids

Outer evaluation time: `t = 1.0` (fixed across both grids).

### Grid α — τ-side boundary fires

| Variable | Value |
|---|---|
| `τ_1` | `1.0` |
| `τ_2` | `0.7` |
| `τ_3` | `0.4` |
| `τ_4` | `0.2` |
| `s_1` | `0.9` |
| `s_2` | `0.6` |
| `s_3` | `0.3` |
| `s_4` | `0.1` |

Boundary indicators at Grid α:

- `δ_{τ_1, t} = 1` (since `τ_1 = 1.0 = t`).
- `δ_{s_1, t} = 0` (since `s_1 = 0.9 ≠ t`).

Both chains are strictly descending and satisfy Eq. (17) ordering on
their own side (`t > τ_2 > τ_3 > τ_4` and `t > s_1 > s_2 > s_3 > s_4`,
with `τ_1 = t` saturating).

### Grid β — s-side boundary fires (τ ↔ s mirror of Grid α)

| Variable | Value |
|---|---|
| `τ_1` | `0.9` |
| `τ_2` | `0.6` |
| `τ_3` | `0.3` |
| `τ_4` | `0.1` |
| `s_1` | `1.0` |
| `s_2` | `0.7` |
| `s_3` | `0.4` |
| `s_4` | `0.2` |

Boundary indicators at Grid β:

- `δ_{τ_1, t} = 0` (since `τ_1 = 0.9 ≠ t`).
- `δ_{s_1, t} = 1` (since `s_1 = 1.0 = t`).

**Why two grids.** Grid α exercises every formula whose subtraction
chain runs through `δ_{τ_1, t}` (full check of Eqs. 70–73, k=0 case
trivially zero). Grid β exercises every formula whose subtraction
chain runs through `δ_{s_1, t}` (full check of Eqs. 69–71, k=4 case
trivially zero). The two grids are τ ↔ s mirrors of each other; the
by-hand expectations are **not** trivially mirror-symmetric because
the row-2.3 swap is not τ ↔ s symmetric in operator order.

## 4. Substitution rules used by the by-hand reference

The §5 closed forms are obtained by applying, in order:

### 4.1 Row-2.3 chain-reversal-and-swap rule (parent artifact row 2.3)

```text
D_companion(τ_1^k, s_1^{n−k})
  = n_point_ordered(
        tau_args = tuple(reversed(s_args_companion)),
        s_args   = tuple(reversed(tau_args_companion)),
        bath_state, spectral_density, ...
    )
```

After `n_point_ordered`'s flattening `times = tau_args + reversed(s_args)`,
the operator order delivered to the trace is:

```text
⟨ B(s_{n−k}) B(s_{n−k−1}) ... B(s_1) B(τ_1) B(τ_2) ... B(τ_k) ⟩
```

Concretely at `n = 4`:

| Case `k` | Companion arguments | Operator-order trace |
|---|---|---|
| `k = 4` | `(τ_1, τ_2, τ_3, τ_4); ()` | `⟨B(τ_1) B(τ_2) B(τ_3) B(τ_4)⟩` |
| `k = 3` | `(τ_1, τ_2, τ_3); (s_1)` | `⟨B(s_1) B(τ_1) B(τ_2) B(τ_3)⟩` |
| `k = 2` | `(τ_1, τ_2); (s_1, s_2)` | `⟨B(s_2) B(s_1) B(τ_1) B(τ_2)⟩` |
| `k = 1` | `(τ_1); (s_1, s_2, s_3)` | `⟨B(s_3) B(s_2) B(s_1) B(τ_1)⟩` |
| `k = 0` | `(); (s_1, s_2, s_3, s_4)` | `⟨B(s_4) B(s_3) B(s_2) B(s_1)⟩` |

The lower-order pieces (`D(τ_1^2)`, `D(s_1^2)`, `D(τ_1, s_1)`,
`D(τ_2, s_2)`, `D(τ_2^3)`, `D(τ_3, s_1)`, `D(s_2^3)`, `D(τ_1, s_3)`,
`D(s_3^4)`) entering the subtractions in Eqs. (69)–(73) are evaluated
by the same row-2.3 swap rule at their respective `(k, n − k)`, which
specialises to:

| Lower-order piece | Operator-order trace | Equivalent `C(·, ·)` |
|---|---|---|
| `D(τ_a, τ_b)` (pure-left, `n=2, k=2`) | `⟨B(τ_a) B(τ_b)⟩` | `C(τ_a, τ_b)` |
| `D(s_a, s_b)` (pure-right, `n=2, k=0`) | `⟨B(s_b) B(s_a)⟩` | `C(s_b, s_a)` |
| `D(τ_a, s_b)` (mixed, `n=2, k=1`) | `⟨B(s_b) B(τ_a)⟩` | `C(s_b, τ_a)` |

### 4.2 Boundary-delta rule for `Ḋ` (Companion Eq. 22)

```text
Ḋ(τ_1^k, s_1^{n−k}) = D(τ_1^k, s_1^{n−k}) · (δ_{τ_1, t} + δ_{s_1, t}),
```

with the convention that `δ_{τ_1, t}` is taken as `0` when `k = 0`
(empty τ-chain), and likewise `δ_{s_1, t}` is taken as `0` when
`k = n` (empty s-chain). Discrete Kronecker semantics apply at the
fixed grid times.

### 4.3 Thermal Gaussian 4-point Wick split (parent artifact §4.4)

For a thermal Gaussian bath with `⟨B(t)⟩ = 0`:

```text
⟨B(u_1) B(u_2) B(u_3) B(u_4)⟩
  = C(u_1, u_2) C(u_3, u_4)
  + C(u_1, u_3) C(u_2, u_4)
  + C(u_1, u_4) C(u_2, u_3).
```

Each pairing preserves the original left-to-right time order inside
its `C` factor. This rule is applied to the raw 4-point inside the
Companion-operator-order trace from §4.1 — i.e. to
`(u_1, u_2, u_3, u_4) = (s_{n−k}, ..., s_1, τ_1, ..., τ_k)`.

### 4.4 θ-window note

The two chosen grids put each side's chain in strict descending order
(`t > τ_2 > τ_3 > τ_4`; `t > s_1 > s_2 > s_3 > s_4` at Grid α and the
mirror at Grid β), so all θ-window indicators evaluate to `1` at the
grid points. The §4.4 procedural rule from the parent artifact is
**not** stress-tested by this card; this card stress-tests the
algebraic structure of Eqs. (69)–(73) and the row-2.3 swap at mixed
order. The θ-window cross-check is left to a follow-up card (out of
this card's scope; see §11).

## 5. By-hand table-expanded reference values

Closed forms below are obtained by applying §4.1–§4.3 to the
verbatim-transcribed Eqs. (69)–(73) from the parent artifact §4.2 and
substituting the boundary-delta values from §3.

The forms are written as polynomials in `C(·, ·)` so the Phase B test
can hand-enumerate them in plain Python (no symbolic engine).
Numerical values follow once `C(a, b)` is evaluated at the §2 fixture.

### 5.1 Grid α (τ_1 = t = 1.0; δ_{τ_1,t} = 1; δ_{s_1,t} = 0)

| Case | Companion eq. | Closed form on Grid α |
|---|---|---|
| `k = 0` — `D̄(s_1^4)` | Eq. (69) | `0` (both `Ḋ(s_1^4)` and `Ḋ(s_1^2)` are zero since `δ_{s_1,t}=0` and the τ-chain is empty) |
| `k = 1` — `D̄(τ_1, s_1^3)` | Eq. (70) | `C(s_3, s_1)·C(s_2, τ_1) + C(s_3, τ_1)·C(s_2, s_1)` |
| `k = 2` — `D̄(τ_1^2, s_1^2)` | Eq. (71) | `C(s_2, τ_1)·C(s_1, τ_2)` |
| `k = 3` — `D̄(τ_1^3, s_1)` | Eq. (72) | `C(s_1, τ_2)·C(τ_1, τ_3)` |
| `k = 4` — `D̄(τ_1^4)` | Eq. (73) | `C(τ_1, τ_3)·C(τ_2, τ_4) + C(τ_1, τ_4)·C(τ_2, τ_3)` |

**Derivation trace (for audit).**

- `k = 0` (Eq. 69): `Ḋ(s_1^4) = δ_{s_1,t}·D(s_1^4) = 0`;
  `Ḋ(s_1^2) = δ_{s_1,t}·C(s_2,s_1) = 0`. Hence `D̄ = 0 − 0 = 0`.
- `k = 1` (Eq. 70): `D(τ_1, s_1^3) = ⟨B(s_3)B(s_2)B(s_1)B(τ_1)⟩
  = C(s_3,s_2)·C(s_1,τ_1) + C(s_3,s_1)·C(s_2,τ_1) + C(s_3,τ_1)·C(s_2,s_1)`.
  `Ḋ(τ_1, s_1^3) = (1+0)·D = D`. Subtractions:
  `Ḋ(τ_1, s_1)·D(s_2^3) = 1·C(s_1,τ_1)·C(s_3,s_2)` cancels the first
  pairing; `Ḋ(s_1^2)·D(τ_1, s_3) = 0`. Survivors: pairings 2 and 3.
- `k = 2` (Eq. 71): `D(τ_1^2, s_1^2) = ⟨B(s_2)B(s_1)B(τ_1)B(τ_2)⟩
  = C(s_2,s_1)·C(τ_1,τ_2) + C(s_2,τ_1)·C(s_1,τ_2) + C(s_2,τ_2)·C(s_1,τ_1)`.
  `Ḋ(τ_1^2, s_1^2) = (1+0)·D = D`. Subtractions:
  `Ḋ(τ_1, s_1)·D(τ_2, s_2) = 1·C(s_1,τ_1)·C(s_2,τ_2)` cancels pairing 3;
  `Ḋ(s_1^2)·D(τ_1^2) = 0`;
  `Ḋ(τ_1^2)·D(s_1^2) = 1·C(τ_1,τ_2)·C(s_2,s_1)` cancels pairing 1.
  Survivor: pairing 2.
- `k = 3` (Eq. 72): `D(τ_1^3, s_1) = ⟨B(s_1)B(τ_1)B(τ_2)B(τ_3)⟩
  = C(s_1,τ_1)·C(τ_2,τ_3) + C(s_1,τ_2)·C(τ_1,τ_3) + C(s_1,τ_3)·C(τ_1,τ_2)`.
  `Ḋ(τ_1^3, s_1) = (1+0)·D = D`. Subtractions:
  `Ḋ(τ_1, s_1)·D(τ_2^3) = 1·C(s_1,τ_1)·C(τ_2,τ_3)` cancels pairing 1;
  `Ḋ(τ_1^2)·D(τ_3, s_1) = 1·C(τ_1,τ_2)·C(s_1,τ_3)` cancels pairing 3.
  Survivor: pairing 2.
- `k = 4` (Eq. 73): `D(τ_1^4) = ⟨B(τ_1)B(τ_2)B(τ_3)B(τ_4)⟩
  = C(τ_1,τ_2)·C(τ_3,τ_4) + C(τ_1,τ_3)·C(τ_2,τ_4) + C(τ_1,τ_4)·C(τ_2,τ_3)`.
  `Ḋ(τ_1^4) = 1·D = D`. Subtraction:
  `Ḋ(τ_1^2)·D(τ_3^4) = 1·C(τ_1,τ_2)·C(τ_3,τ_4)` cancels pairing 1.
  Survivors: pairings 2 and 3.

### 5.2 Grid β (s_1 = t = 1.0; δ_{τ_1,t} = 0; δ_{s_1,t} = 1)

| Case | Companion eq. | Closed form on Grid β |
|---|---|---|
| `k = 0` — `D̄(s_1^4)` | Eq. (69) | `C(s_4, s_2)·C(s_3, s_1) + C(s_4, s_1)·C(s_3, s_2)` |
| `k = 1` — `D̄(τ_1, s_1^3)` | Eq. (70) | `C(s_3, s_1)·C(s_2, τ_1)` |
| `k = 2` — `D̄(τ_1^2, s_1^2)` | Eq. (71) | `C(s_2, τ_1)·C(s_1, τ_2)` |
| `k = 3` — `D̄(τ_1^3, s_1)` | Eq. (72) | `C(s_1, τ_2)·C(τ_1, τ_3) + C(s_1, τ_3)·C(τ_1, τ_2)` |
| `k = 4` — `D̄(τ_1^4)` | Eq. (73) | `0` (both `Ḋ(τ_1^4)` and `Ḋ(τ_1^2)` are zero since `δ_{τ_1,t}=0` and the s-chain is empty) |

**Derivation trace (for audit).**

- `k = 0` (Eq. 69): `Ḋ(s_1^4) = δ_{s_1,t}·D(s_1^4) = 1·D`;
  `Ḋ(s_1^2) = δ_{s_1,t}·C(s_2,s_1) = C(s_2,s_1)`.
  `D(s_1^4) = ⟨B(s_4)B(s_3)B(s_2)B(s_1)⟩
   = C(s_4,s_3)·C(s_2,s_1) + C(s_4,s_2)·C(s_3,s_1) + C(s_4,s_1)·C(s_3,s_2)`.
  Subtraction `Ḋ(s_1^2)·D(s_3^4) = C(s_2,s_1)·C(s_4,s_3)` cancels
  pairing 1. Survivors: pairings 2 and 3.
- `k = 1` (Eq. 70): `D(τ_1, s_1^3) = ⟨B(s_3)B(s_2)B(s_1)B(τ_1)⟩` (as
  in §5.1 k=1). `Ḋ(τ_1, s_1^3) = (0+1)·D = D`. Subtractions:
  `Ḋ(τ_1, s_1)·D(s_2^3) = (0+1)·C(s_1,τ_1)·C(s_3,s_2)` cancels pairing 1;
  `Ḋ(s_1^2)·D(τ_1, s_3) = 1·C(s_2,s_1)·C(s_3,τ_1)` cancels pairing 3.
  Survivor: pairing 2.
- `k = 2` (Eq. 71): As in §5.1 k=2. `Ḋ(τ_1^2, s_1^2) = (0+1)·D = D`.
  Subtractions: `Ḋ(τ_1, s_1)·D(τ_2, s_2) = (0+1)·C(s_1,τ_1)·C(s_2,τ_2)`
  cancels pairing 3; `Ḋ(s_1^2)·D(τ_1^2) = 1·C(s_2,s_1)·C(τ_1,τ_2)`
  cancels pairing 1; `Ḋ(τ_1^2)·D(s_1^2) = 0`. Survivor: pairing 2.
  (Same survivor structure as Grid α.)
- `k = 3` (Eq. 72): As in §5.1 k=3. `Ḋ(τ_1^3, s_1) = (0+1)·D = D`.
  Subtractions: `Ḋ(τ_1, s_1)·D(τ_2^3) = (0+1)·C(s_1,τ_1)·C(τ_2,τ_3)`
  cancels pairing 1; `Ḋ(τ_1^2)·D(τ_3, s_1) = 0`. Survivors: pairings 2
  and 3.
- `k = 4` (Eq. 73): `Ḋ(τ_1^4) = δ_{τ_1,t}·D(τ_1^4) = 0`;
  `Ḋ(τ_1^2) = 0`. Hence `D̄ = 0 − 0 = 0`.

### 5.3 Consistency checks built into the §5 closed forms

- `k = 0` at Grid α and `k = 4` at Grid β are both **identically zero**
  by the boundary-delta rule. The Phase B evaluator must return
  numerical zero (within the §9 tolerance) at both, not by short-circuit
  on `k`, but by the same Eq. (69)/(73) code path that produces the
  nontrivial mirror result on the other grid.
- `k = 2` produces the **same** survivor form at both grids
  (`C(s_2, τ_1)·C(s_1, τ_2)`) despite different boundary-delta paths.
  This is a coincidence of the symmetric Eq. (71) subtraction structure
  at `k = 2`, not a generic τ ↔ s symmetry. Mismatch between the two
  grids at `k = 2` would signal a sign-pattern error in Eq. (71).
- The `k = 0` ↔ `k = 4` and `k = 1` ↔ `k = 3` pairs are mirror images
  under τ ↔ s relabeling (Grid α ↔ Grid β), but only when the row-2.3
  swap is applied symmetrically on both sides of the relabeling. Any
  asymmetry in the survivor pairings between mirror-grid case pairs is
  a structural sign that the swap is being applied to only one side.

## 6. Primary oracle — Phase B direct evaluator (API contract)

The Phase B helper to be implemented in `cbg.tcl_recursion` must expose
a callable with the following contract:

```python
def _D_bar_4_companion(
    tau_args: tuple[float, ...],
    s_args: tuple[float, ...],
    *,
    t: float,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> complex:
    """
    Companion D̄(τ_1^k, s_1^{n−k}) at total order n = 4, evaluated
    directly from Eqs. (69)-(73).

    Implements:
      - Row-2.3 chain-reversal-and-swap on internal `n_point_ordered`
        calls for the raw D leaves.
      - Eq. (22) boundary delta (δ_{τ_1, t} + δ_{s_1, t}), with the
        empty-chain convention.
      - Explicit subtractions of lower-order raw correlators per the
        case-specific formula (Eq. 69, 70, 71, 72, or 73 dispatched on
        len(tau_args)).
      - MUST NOT call cbg.cumulants._joint_cumulant_from_raw_moments
        (B.1 path) for any of the five cases. Reusing B.1 would silently
        return ≈ 0 for thermal Gaussian; see parent artifact row 2.8.
    """
```

The signature is **not yet implemented**; this card is the spec the
implementation must satisfy. The exact name (private helper vs. public
method) is a Phase B implementation decision; the contract above is the
gate.

### 6.1 Routing on case dispatch

`k := len(tau_args)`; the cases dispatch as:

| `k` | Companion eq. | Mixed-order shape |
|---|---|---|
| `4` | (73) | `(τ_1, τ_2, τ_3, τ_4); ()` |
| `3` | (72) | `(τ_1, τ_2, τ_3); (s_1)` |
| `2` | (71) | `(τ_1, τ_2); (s_1, s_2)` |
| `1` | (70) | `(τ_1); (s_1, s_2, s_3)` |
| `0` | (69) | `(); (s_1, s_2, s_3, s_4)` |

`k ∉ {0, 1, 2, 3, 4}` MUST raise `NotImplementedError` (Phase B scope is
n=4 only; n>=5 is out of scope for v0.1.5 of the work plan).

## 7. Independent oracle — the §5 closed-form table

The §5 closed forms are the **acceptance oracle**. The Phase B test
hand-enumerates each closed form in plain Python (multiplying complex
`C(a, b)` values evaluated by `cbg.bath_correlations.two_point` at the
§2 fixture and the §3 grid times) and compares against the primary
oracle's return value at each of the 5 × 2 = 10 (case, grid) pairs.

### 7.1 Why this is the gate, not the secondary diagnostic

The §5 table is derived algebraically from:

- the verbatim-transcribed Eqs. (69)–(73) (parent artifact §4.2);
- the closed-by-steward row-2.3 swap rule (parent artifact row 2.3);
- the boundary-delta rule of Eq. (22) (parent artifact §3 symbol map);
- the thermal Gaussian 4-point Wick split (parent artifact §4.4).

Each of these four inputs is independently auditable against the
Companion paper. A "Wick-output minus same-formula subtractions"
diagnostic, by contrast, only checks the plumbing — it consumes the
same Eq. (69)–(73) subtraction terms that the primary evaluator
produces, so it cannot detect a sign-pattern error in the subtraction
structure itself. The §5 table is independent of the primary evaluator
in the algebraic sense; the diagnostic is not.

## 8. Secondary supporting diagnostic (not the gate)

For Phase B debugging convenience, the test may **additionally**
compute, at each (case, grid) pair:

- The raw `n_point_ordered(tau_args=…, s_args=…, …)` call with the
  Companion-side `(tau_args, s_args)` passed through the row-2.3 swap
  (i.e., the `D` leaf the primary evaluator uses internally).
- The same `D` leaf computed by direct Wick enumeration in plain Python
  using `cbg.bath_correlations.two_point`.

These two values must agree at the §9 tolerance. **This check is
supporting evidence on the row-2.3 plumbing only**; it does not
exercise the subtraction structure of Eqs. (69)–(73), and a passing
secondary check alone does NOT satisfy the gate. The acceptance gate is
§9 applied to the §5–§6 comparison.

## 9. Acceptance criterion

For every `(case k, grid g)` pair with `k ∈ {0, 1, 2, 3, 4}` and
`g ∈ {α, β}`:

```python
np.testing.assert_allclose(
    primary_oracle_value,
    independent_oracle_value,
    atol=1e-10,
    rtol=1e-10,
)
```

- The tolerances are **strict** machine-precision-class; any larger
  tolerance must be justified in a successor card revision with a
  recorded reason (e.g., demonstrated quadrature-noise floor under
  the chosen `(upper_cutoff_factor, quad_limit)`).
- The complex argument of each value must agree to the same tolerance
  on both real and imaginary parts (default `assert_allclose` behaviour
  on complex arrays).
- The two trivially-zero cases (`k = 0` at Grid α and `k = 4` at Grid β)
  must satisfy `abs(primary_oracle_value) <= 1e-10` (absolute), since
  the relative comparison is degenerate at zero.

If any (case, grid) pair fails the gate, Phase B must **stop** and open
a logbook routing note before proceeding to Phase C oracles. Do not
relax the tolerance in place; the tolerance is part of the frozen card.

## 10. Implementation hand-off to Phase B

When the steward starts Phase B coding:

1. Implement the §6 contract as a private helper in
   `cbg.tcl_recursion` (default scaffold position per work plan
   v0.1.5 §3).
2. Add `tests/test_n4_small_grid_verification.py` that:
   - imports the §2 fixture and §3 grids verbatim;
   - calls the primary oracle at each of the 10 (case, grid) pairs;
   - hand-enumerates the §5 closed forms using
     `cbg.bath_correlations.two_point` to produce the independent
     oracle values;
   - applies `np.testing.assert_allclose` with the §9 tolerances;
   - optionally includes the §8 secondary diagnostic as separate
     non-gating assertions (clearly labelled).
3. Cite this card by version in the test file's module docstring:
   `"Verification card: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_n4-small-grid-verification-card_v0.1.0.md"`.
4. Run `.venv/bin/pytest -q tests/test_n4_small_grid_verification.py`.
   On all-pass: proceed to Phase C oracles (work plan §4). On any
   failure: stop and route per §9 closing sentence.

## 11. Out-of-scope reminders

This card explicitly does **not** cover:

- **θ-window stress.** Both grids put each chain in strict descending
  order; the parent artifact's §4.4 θ-aware combination rule for
  `f̄`/`ḡ` is not exercised. A follow-up card covers θ-window edge
  cases (e.g., grid points where descending order is violated, or
  where two times coincide); that card is not a v0.1.5 release
  blocker — it is a Phase C/E follow-up.
- **K_4 assembly.** Phase B's helper produces `D̄_4` only. The
  downstream `K_4` assembly (Eq. 74 with bath coefficients
  `f̄`/`ḡ` from Eqs. 75/76 and operator blocks `X̄`/`Ȳ` from
  Eqs. 77/78) is verified by Phase C/E oracles, not by this card.
- **σ_z zero oracle and σ_x signal oracle.** Those are the Phase C
  physics oracles per work plan §4 Phase C — they exercise the full
  `L_4` route, not just the D̄ evaluator. This card sits **upstream**
  of those oracles.
- **Path A / Path B cross-validation.** That is the Phase E artifact
  per work plan §4 Phase E.
- **Non-thermal or non-Gaussian baths.** Out of scope of DG-4 v0.1.5;
  the §6 contract documents the supported scope.
- **`n >= 5`.** Out of scope per parent artifact §1.2.

## 12. Steward freeze sign-off

> I have drafted the small-grid verification card as the gate that
> turns the released Companion Sec. IV L_4 transcription (v0.1.1) into
> "safe to code" for Phase B. The bath fixture, time grids, by-hand
> closed-form reference values, primary-oracle API contract, secondary
> diagnostic, and strict numerical-equality acceptance criterion are
> frozen at this version. Per cards-first discipline, this file is
> content-immutable post-commit; any revision is by superseding
> successor at a new version.
>
> Reviewer: Ulrich Warring  Date: 2026-05-13
>
> Version at freeze: v0.1.0 (release state: frozen-pre-implementation)
>
> Phase B may begin coding against the §6 contract once this card is
> committed. The §9 acceptance criterion is the only gate this card
> imposes.

## Appendix — change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1.0 | 2026-05-13 | Initial draft and freeze. Pinned bath fixture (§2), two time grids (§3), substitution rules (§4), by-hand closed forms for all 5 × 2 = 10 (case, grid) pairs (§5), primary-oracle API contract (§6), independent-oracle gate (§7), secondary diagnostic (§8), strict atol=1e-10 rtol=1e-10 acceptance (§9), Phase B hand-off (§10), out-of-scope reminders (§11), and steward freeze sign-off (§12). Derivation traces audited for each of the 10 closed forms against the verbatim Eqs. (69)–(73) transcribed in the parent v0.1.1 artifact §4.2 plus the closed-by-steward row-2.3 swap rule. | Local steward draft; cards-first discipline. |

*Verification card version: v0.1.0 (frozen 2026-05-13). Operationalises
the §2.8 small-grid verification gate carried forward by the released
Companion Sec. IV L_4 transcription v0.1.1. Phase B coding is
authorised against the §6 contract under the §9 acceptance criterion.
CC-BY-4.0 (see ../LICENSE-docs).*

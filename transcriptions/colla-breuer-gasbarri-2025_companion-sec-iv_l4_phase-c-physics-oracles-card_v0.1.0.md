---
artifact_id: cbg-companion-sec-iv-l4-phase-c-physics-oracles-card
version: v0.1.0
date: 2026-05-13
type: verification-card / pre-code-oracle
status: frozen
parent_transcription: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md
parent_card: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_n4-small-grid-verification-card_v0.1.0.md
target_implementation: cbg/tcl_recursion.py — Phase C private assembled-L_4 helper (not yet implemented)
anchor_plan: plans/dg-4-work-plan_v0.1.5.md §4 Phase C
release_gate: work plan v0.1.5 §4 Phase C acceptance — all four physics oracles pass under the full quality gate; public n=4 route remains deferred to Phase D
reviewer: Ulrich Warring
review_date: 2026-05-13
review_state: frozen-pre-implementation
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Phase C pre-code verification card — physics oracles for assembled L_4

> **Status: frozen (2026-05-13).** This card pins the executable
> oracle details for Phase C: the API contract for the assembled-L_4
> private helper, the four physics oracles named by work plan v0.1.5
> §4 Phase C (σ_z zero, σ_x signal, gauge/sign, parity), and the
> acceptance criteria. It lands **before** Phase C implementation
> code exists. Per cards-first discipline, this file is
> content-immutable post-commit; revisions are by superseding
> successor at a new version.

## 0. Provenance and role

This card consumes:

- the verbatim-transcribed Companion Eqs. (28), (43), (45), (69)-(73)
  from the released parent transcription
  ([Companion Sec. IV L_4 transcription v0.1.1](colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md));
- the closed-by-steward row-2.3 chain-reversal-and-swap rule;
- the §2.8 Phase B `_D_bar_4_companion` private helper, frozen against
  the n=4 small-grid verification card
  ([v0.1.0](colla-breuer-gasbarri-2025_companion-sec-iv_l4_n4-small-grid-verification-card_v0.1.0.md))
  and landed at commit `becccf9`;
- the work plan v0.1.5 §4 Phase C four-oracle gate
  ([dg-4-work-plan_v0.1.5.md](../plans/dg-4-work-plan_v0.1.5.md)).

This card freezes:

1. The API contract for the assembled-L_4 private helper
   `_L_4_thermal_at_time_apply` in `cbg.tcl_recursion`.
2. The shared system, bath, time-grid, and basis fixtures used by all
   four oracles. The bath fixture is the D1 v0.1.2 baseline-style
   (the same `(ω_c, T, ω)` triple), distinct from the small-grid
   card's fresh local fixture and reused here because the σ_x signal
   oracle is anchored to "the D1 baseline fixture" by work plan §4.
3. The σ_z zero oracle gate at `atol = 1e-10` over a representative
   matrix-unit basis (steward-tightenable per work plan §3).
4. The σ_x signal oracle gate as a structural finite + non-zero
   bounding box with a conservatively chosen lower bound; the actual
   numerical value of the first run is recorded as a regression note
   in the logbook, not pinned in this card.
5. The gauge/sign oracle (L_0^dis = 0, n=2 dissipator unchanged) and
   parity oracle (L_1 = L_3 = 0) at machine-zero tolerance.
6. The explicit Phase C ↔ Phase D scope boundary: this card pins the
   **private** assembled-L_4 helper and the four oracles consume it
   privately; the public `L_n_thermal_at_time(n=4)` route remains a
   `NotImplementedError` until Phase D lands.

## 1. Purpose and scope

### 1.1 What this card does

- Operationalises work plan v0.1.5 §4 Phase C as four executable
  oracle gates, with all implementation-facing details pinned (API
  shape, fixtures, time grid, basis, tolerances).
- Provides a frozen, citable target the Phase C implementation must
  hit before Phase D code exposes the public route.
- Maintains the cards-first discipline boundary between the algebraic
  D̄ verifier (Phase B; small-grid card) and the operator-valued L_4
  assembly (Phase C; this card).

### 1.2 What this card does not do

- It does not implement the assembled-L_4 helper. The Phase C code
  lives in `cbg.tcl_recursion` and is the subject under test, not
  part of this oracle.
- It does not unbind the public `L_n_thermal_at_time(n=4)`
  `NotImplementedError`. That deferral remains in force until Phase D
  lands; the four oracles in §4 consume the private helper only.
- It does not specify the **quadrature** rule for the simplex
  integrals. Trapezoidal-on-uniform-grid is the n=2 precedent
  in `L_n_thermal_at_time(n=2)`, but the Phase C implementation may
  choose a different rule (e.g., Simpson, Gauss-Legendre, adaptive)
  if needed to satisfy §4.1's `atol = 1e-10` σ_z zero gate within
  reasonable resources. The card pins the **gate**; the
  implementation chooses the **route**.
- It does not commit to K_4 / L_4^dis decomposition beyond what is
  needed by §4.2 (σ_x signal oracle). The σ_x oracle composes the
  existing `cbg.effective_hamiltonian.K_from_generator` against the
  new `_L_4_thermal_at_time_apply` callable to extract K_4 and form
  L_4^dis = L_4 + i [K_4, ·]; no new K_4-specific helper is required
  by Phase C.
- It does not cross-validate against Path B numerical extraction.
  That is the Phase E artifact per work plan §4 Phase E.
- It does not authorise any change to D1 v0.1.2 frozen parameters,
  the v0.1.2 result JSON, or the released v0.1.1 transcription.

## 2. Frozen shared fixtures

All four oracles consume the same fixtures unless explicitly noted in
§4.x.

### 2.1 System

```yaml
system_dimension: 2
system_hamiltonian: "(omega / 2) * sigma_z"
omega: 1.0
basis: matrix_unit  # the four E_ij of d=2; identical to A4/B4 cards
```

The coupling operator `A` is oracle-specific:

- σ_z zero oracle (§4.1): `coupling_operator = sigma_z`.
- σ_x signal oracle (§4.2): `coupling_operator = sigma_x`.
- Gauge/sign oracle (§4.3): `coupling_operator = sigma_x` (D1-baseline-style);
  the L_0^dis = 0 check is coupling-independent but uses the same
  fixture for consistency.
- Parity oracle (§4.4): `coupling_operator = sigma_x` (same reason).

### 2.2 Bath (D1 v0.1.2 baseline-style)

```yaml
bath_state:
  family: thermal
  temperature: 0.5      # T (in units of omega)
spectral_density:
  family: ohmic
  coupling_strength: 0.02   # alpha, the middle of the D1 sweep {0.01..0.03}
  cutoff_frequency: 10.0    # omega_c
quadrature_controls:
  upper_cutoff_factor: 30.0
  quad_limit: 200
```

`alpha = 0.02` is pinned for the σ_x signal oracle's numerical
evaluation; the σ_z, gauge/sign, and parity oracles are structural
(algebraic-zero) and their results are coupling-independent in
character, but `alpha = 0.02` is used uniformly so the bath two-point
`C(a, b)` is reproducible across all four oracles.

### 2.3 Time grid

```yaml
time_grid:
  t_start: 0.0
  t_end: 2.0          # in units of 1/omega, deliberately small per work plan §6 R4
  n_points: 11        # uniform; dt = 0.2
  scheme: uniform
```

Each oracle evaluates `_L_4_thermal_at_time_apply` at a designated
`t_idx` index into this grid (see §3 and §4.x). The small grid is
deliberate — Phase C is testing structure (zero/non-zero, sign,
parity), not quantitative D1 agreement. Quantitative agreement is the
Phase E artifact.

> **Note on σ_z zero oracle quadrature.** The σ_z `atol = 1e-10` gate
> is an algebraic-identity check on a sum of independently-quadratured
> simplex integrals. Trapezoidal on N=11 may not preserve the
> cancellation at 1e-10. The implementation is permitted, and may
> need, to use a finer grid or higher-order quadrature **inside the
> helper** while still being called at the §2.3 N=11 grid's
> evaluation index. If the implementation cannot hit `atol = 1e-10`
> without exorbitant resources, escalate via a successor card
> revision (do not silently loosen the tolerance in the test).

### 2.4 Test basis (matrix unit)

```python
from cbg.basis import matrix_unit_basis
BASIS = matrix_unit_basis(2)   # [E_00, E_01, E_10, E_11], each (2, 2) complex
```

Oracle assertions are made over `X ∈ BASIS` (all four matrix units).

### 2.5 Evaluation index

```yaml
t_idx_oracle: 5     # t = t_grid[5] = 1.0; mid-grid, away from t=0 boundary
```

A single `t_idx` is sufficient for each oracle; the assertions are
structural and do not need a sweep across the time grid for Phase C
acceptance. Phase E will sweep.

## 3. API contract — assembled-L_4 private helper

The Phase C helper to be implemented in `cbg.tcl_recursion` must
expose a callable with the following contract:

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
    """
    Return a callable that computes L_4[X] at t = t_grid[t_idx] for
    a thermal Gaussian bath, assembled from Companion Eq. (28) at n=4.

    Implements:
      sum_{k=0}^{4} (-1)^k * integral over the k-simplex × (4-k)-simplex
          in [0, t] of D̄(τ_1^k, s_1^{n-k})
          * A(τ_1^k) X A^†(s_1^{n-k})
      where:
        - A(τ_1^k) := A_I(τ_1) A_I(τ_2) ... A_I(τ_k)         (Eq. 10)
        - A^†(s_1^{n-k}) := A_I(s_{n-k}) ... A_I(s_1)         (Eq. 11, reversed)
        - A_I(τ) := cbg.tcl_recursion.interaction_picture(H_S, A, τ)
        - D̄(τ_1^k, s_1^{n-k}) is the Phase B private helper
          cbg.tcl_recursion._D_bar_4_companion with outer time
          t = t_grid[t_idx].

    The implementation MUST:
      - call cbg.tcl_recursion._D_bar_4_companion for every D̄ leaf
        (i.e., the Phase B helper, not the B.1 standard-cumulant path);
      - integrate over the k-simplex × (4-k)-simplex on the descending
        sub-grid t_grid[:t_idx+1], honouring the θ-ordering of Eq. (17);
      - return a callable apply(X) -> L_4[X] consistent with the n=2
        precedent in L_n_thermal_at_time(n=2);
      - choose any quadrature rule it likes; trapezoidal is permitted
        but not required.

    The implementation MUST NOT:
      - mutate the public L_n_thermal_at_time(n=4) NotImplementedError;
      - introduce a route_version parameter (deferred per work plan
        v0.1.5 §3);
      - reuse cbg.cumulants._joint_cumulant_from_raw_moments (B.1).

    Returns
    -------
    Callable[(d, d) ndarray] -> (d, d) ndarray
        Apply function L_4[X].
    """
```

### 3.1 Naming and routing

- The exact name `_L_4_thermal_at_time_apply` is recommended for
  symmetry with `L_n_thermal_at_time(n=2)`'s internal `L_2_apply`
  closure but is not mandatory. If the implementation chooses a
  different private name, it must be documented in the Phase C
  implementation commit message.
- The public `L_n_thermal_at_time(n=4)` route continues to raise
  `NotImplementedError`. Phase D will route that public entry through
  the private helper.

## 4. The four physics oracles

### 4.1 σ_z zero oracle (work plan §4 Phase C, bullet 1)

**Setup.** Use the §2 fixture with `coupling_operator = sigma_z`. With
A = σ_z and H_S = (ω/2) σ_z, `A_I(τ) = e^{iωσ_z τ/2} σ_z e^{-iωσ_z τ/2}
= σ_z` (commutes), so `[A, A_I(τ)] = 0` for all τ. The entire TCL
series truncates at order 2 by Feynman-Vernon Gaussian-bath exactness
(see `cbg/tcl_recursion.py` n=4 falsification note), so the algebraic
answer is L_4[X] = 0 for every X.

**Test.** For each `X ∈ BASIS` (the four matrix units), compute
`L_4_apply(X)` via the §3 helper at `t_idx = 5` (t = 1.0). Assert:

```python
np.testing.assert_allclose(L_4_apply(X), 0.0, atol=1e-10)
```

for all four X. The tolerance is **strict** per work plan v0.1.5 §3
("Strict zero oracle for sigma_z … steward-tightenable"). If
trapezoidal-on-N=11 cannot reach `1e-10`, the implementation should
internally refine to higher-order or finer quadrature while preserving
the §2.3 outer grid; if even that fails, escalate via successor card
revision rather than loosening the test.

**What this gate exercises.** The non-trivial algebraic cancellation
`Σ_k (-1)^k I_k = 0` (diagonal X) and `Σ_k I_k = 0` (off-diagonal X)
among the five integrated D̄_k pieces. A sign error in any one of
Eqs. (69)-(73), or in the (-1)^k factor of Eq. (28), or in the
operator-chain `A(τ_1^k) X A^†(s_1^{n-k})` construction, will break
this gate before Phase D code lands.

### 4.2 σ_x signal oracle (work plan §4 Phase C, bullet 2)

**Setup.** Use the §2 fixture with `coupling_operator = sigma_x`. With
A = σ_x and H_S = (ω/2) σ_z, `A_I(τ) = σ_x cos(ωτ) + σ_y sin(ωτ)` —
`[A, A_I(τ)] ≠ 0` in general, so L_4 is structurally non-zero.

**Test.** Build the assembled L_4 superoperator over BASIS:

```python
from cbg.effective_hamiltonian import K_from_generator
L_4_apply = _L_4_thermal_at_time_apply(t_idx=5, ...)
K_4 = K_from_generator(L_4_apply, basis=BASIS)
def L_4_dis_apply(X):
    return L_4_apply(X) + 1j * (K_4 @ X - X @ K_4)
# Build superoperator matrix of L_4_dis_apply over BASIS, take Frobenius norm.
L_4_dis_super = build_superoperator(L_4_dis_apply, BASIS)
norm = np.linalg.norm(L_4_dis_super, "fro")
```

Assert:

```python
assert np.isfinite(norm), "L_4^dis has non-finite entries"
assert 1e-6 <= norm <= 1e6, (
    f"||L_4^dis||_F = {norm:.3e} is outside the structural bounding box"
)
```

**Lower-bound rationale.** At `(α, ω_c, T, t_max) = (0.02, 10.0, 0.5, 2.0)`,
the expected scale of `||L_4||_F` is roughly `|C|^2 × t^4 / (k! (4-k)!)`
summed over k, with `|C|^2 ~ α^2 ω_c^2 / (πβ)^2 ~ 10^{-2}` and
`t^4 / 24 ~ 0.67`, giving a structural signal of order `10^{-3}` to
`10^{-2}`. The lower bound `1e-6` is **four to three orders of
magnitude** below the expected scale — well above machine zero
(~1e-16) and any plausible quadrature noise floor, but well below the
physical signal. It is a **structural** non-zero check, not a
quantitative-magnitude check.

**Upper-bound rationale.** `1e6` catches accidental overflow / sign
inversion blowups. Any value > 1e6 indicates a unit or factor error,
not the physical signal.

**Regression note (not gated by this card).** On the first run, the
test should log the achieved `norm` value to the test output (via
`print` or `pytest -s -v`); the value should also be recorded in the
Phase C completion logbook entry as a regression baseline for future
successor cards. The card itself does not pin a specific number, only
the bounding box.

### 4.3 Gauge/sign oracle (work plan §4 Phase C, bullet 3)

This oracle splits into two structural checks:

**4.3.a — L_0 dissipator vanishes.** For `n = 0`, the zeroth-order
generator is purely Hamiltonian: `L_0[X] = -i [H_S, X]`. The
zeroth-order effective Hamiltonian satisfies `K_0 = H_S`, so the
dissipator is `L_0^dis[X] := L_0[X] + i [K_0, X] = -i[H_S,X] + i[H_S,X] = 0`.

For each `X ∈ BASIS`:

```python
L_0_apply = L_n_thermal_at_time(n=0, t_idx=5, t_grid=..., ...)
K_0 = K_from_generator(L_0_apply, basis=BASIS)
L_0_dis = L_0_apply(X) + 1j * (K_0 @ X - X @ K_0)
np.testing.assert_allclose(L_0_dis, 0.0, atol=1e-12)
```

**4.3.b — n=2 dissipator regression.** The Phase C implementation
must not change `L_n_thermal_at_time(n=2)` output. Verify by computing
`L_2_apply(E_01)` (an arbitrary representative basis element) at the
§2 fixture and asserting it matches the **card-pinned pre-Phase-C
reference value** below at machine precision:

```python
# Compute L_2[E_01] at t_idx=5 with the same §2 fixture
L_2_apply = L_n_thermal_at_time(
    n=2, t_idx=5, t_grid=t_grid,
    system_hamiltonian=H_S, coupling_operator=A_sigma_x,
    D_bar_2_array=D_bar_2_array,
)
val = L_2_apply(BASIS[1])  # E_01

# Card-pinned pre-Phase-C reference (measured at this card's freeze
# under the §2 fixture; commit `ae20806` is the upstream baseline).
L_2_E01_REFERENCE = np.array(
    [
        [-0.0 - 0.0j, -0.26338525879711916 + 0.04707234985666798j],
        [ 0.26338525879711916 - 0.04707234985666798j, -0.0 - 0.0j],
    ],
    dtype=complex,
)
np.testing.assert_allclose(val, L_2_E01_REFERENCE, atol=1e-12, rtol=1e-12)
```

The reference is **card-pinned**: any divergence of the Phase C
implementation from this value at `atol = rtol = 1e-12` is a
regression on n=2 behaviour and must block Phase C acceptance. The
value was measured against the §2 fixture (σ_x coupling, ω = 1.0,
ohmic with α = 0.02, ω_c = 10.0, thermal T = 0.5, time grid
`np.linspace(0, 2.0, 11)`, evaluated at `t_idx = 5` ⇒ `t = 1.0`,
matrix-unit basis, default quadrature controls) at this card's
freeze, with the upstream code at commit `ae20806` (the Phase B
small-grid-card freeze, prior to any Phase B helper landing). The
Phase B helper landing at commit `becccf9` did not modify
`L_n_thermal_at_time(n=2)`, so this reference is also the
post-Phase-B value.

**Tolerance** for both 4.3.a and 4.3.b: `atol = 1e-12, rtol = 1e-12`
(tighter than the σ_z zero oracle because both involve simpler
algebraic identities with no n=4 simplex quadrature).

### 4.4 Parity oracle (work plan §4 Phase C, bullet 4)

**Setup.** Use the §2 fixture with `coupling_operator = sigma_x`. For
thermal Gaussian baths with `⟨B⟩ = 0`, the odd generalized cumulants
vanish: `D̄_1 = 0` (Phase B.0 zero-mean), `D̄_3 = 0` (Phase B.1
Gaussianity). Consequently `L_1 = L_3 = 0` identically.

The existing `cbg.tcl_recursion.L_n_thermal_at_time` already returns
the zero callable for `n = 1` (line 132-136) and `n = 3`
(line 138-155). The Phase C parity oracle asserts that these zeros
are preserved after Phase C code lands. (The n=4 helper's
zero / non-zero structure is exercised by §4.1 σ_z zero and §4.2 σ_x
signal, not duplicated here.)

For each `X ∈ BASIS`:

```python
L_1_apply = L_n_thermal_at_time(n=1, t_idx=5, ...)
L_3_apply = L_n_thermal_at_time(n=3, t_idx=5, ...)
np.testing.assert_allclose(L_1_apply(X), 0.0, atol=1e-12)
np.testing.assert_allclose(L_3_apply(X), 0.0, atol=1e-12)
```

**Tolerance.** `atol = 1e-12` (machine-zero-class; the existing
implementation returns numpy.zeros exactly, so machine zero is
achievable).

**Note.** The parity oracle is a **regression** check on existing
behaviour, not a new physics gate. Its inclusion in Phase C ensures
that the Phase C code touching `cbg.tcl_recursion` does not
accidentally break the n=1/n=3 thermal Gaussian shortcuts.

## 5. Implementation hand-off to Phase C

When the steward starts Phase C coding:

1. Implement `_L_4_thermal_at_time_apply` as a private helper in
   `cbg.tcl_recursion` per the §3 contract. Place it in the same
   "Companion D̄ at n=4 (DG-4 Phase B, thermal Gaussian)" section as
   `_D_bar_4_companion` (the Phase B helper), since it consumes that
   helper directly.
2. Add `tests/test_n4_physics_oracles.py` that:
   - Imports the §2 fixture verbatim;
   - Implements the four oracle test cases of §4.1, §4.2, §4.3.a,
     §4.3.b, §4.4 against the §3 helper and the existing
     `cbg.effective_hamiltonian.K_from_generator` and
     `cbg.tcl_recursion.L_n_thermal_at_time` (n ∈ {0, 1, 2, 3});
   - Cites this card by version in the module docstring:
     `"Verification card: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-c-physics-oracles-card_v0.1.0.md"`;
   - Logs the §4.2 measured `||L_4^dis||_F` value to test output for
     the regression note.
3. Run the full quality gate per work plan v0.1.5 §5 acceptance
   criterion 7 (`ruff check`, `black --check .`, `mypy cbg/ models/
   numerical/ benchmarks/ reporting/ scripts/`, `pytest -q`,
   `sphinx-build -W -b html -E docs-site <tmpdir>`).
4. On all-pass: proceed to Phase D (public n=4 route exposure).
   On any failure of §4.1 at `atol = 1e-10`: stop and open a logbook
   routing note; consider successor card revision to loosen tolerance
   only if the implementation has demonstrated that the algebraic
   cancellation is genuine but the quadrature-error floor is the
   binding constraint.

## 6. Out-of-scope reminders

This card explicitly does **not** cover:

- **Public n=4 route.** `L_n_thermal_at_time(n=4)` continues to raise
  `NotImplementedError`. Public exposure is Phase D.
- **`L_n_dissipator_norm_thermal_on_grid(n=4)`.** This is a Phase D
  public route. Phase C uses the private helper plus
  `K_from_generator` ad hoc inside the test, not a new public
  surface.
- **Path A / Path B cross-validation.** Phase E.
- **Tier-2.D literal K_2-K_4 recursion.** Out of scope per work plan
  v0.1.5 §1.1.
- **Non-thermal or non-Gaussian baths.** Out of scope of DG-4 v0.1.5;
  the §3 contract documents the supported scope.
- **θ-window stress at n=4 mixed-order.** The σ_z zero oracle test
  uses the §2.3 strictly-descending grid; θ-window edge cases (grid
  points where descending order is violated or where two times
  coincide) remain a follow-up card per the small-grid card §11.
- **f̄ / ḡ bath coefficients and K_4 master formula (Eqs. 74-78).**
  Phase C tests K_4 only indirectly via `K_from_generator(L_4_apply, ...)`
  — i.e., extraction from the assembled L_4 via Letter Eq. (6),
  not from the Companion's explicit Eqs. (74)-(78) master formula.
  A separate card may cover the Eq. (74) master formula as an
  independent cross-check in a future Phase F-or-equivalent revision.

## 7. Steward freeze sign-off

> I have drafted the Phase C physics-oracles card as the gate that
> turns the §6-contract-implementing assembled-L_4 private helper
> into "safe to expose publicly" for Phase D. The API contract, four
> oracle gates with their tolerances and bounding boxes, fixtures,
> time grid, test basis, and implementation hand-off are frozen at
> this version. The σ_z zero oracle at `atol = 1e-10` is pinned per
> work plan v0.1.5 §3 with the steward-tightenable carve-out; the
> σ_x signal oracle is a structural finite-and-non-zero gate with
> first-run measurement logged for future regression; the gauge/sign
> and parity oracles are machine-zero structural checks. Per
> cards-first discipline, this file is content-immutable
> post-commit; any revision is by superseding successor at a new
> version.
>
> Reviewer: Ulrich Warring  Date: 2026-05-13
>
> Version at freeze: v0.1.0 (release state: frozen-pre-implementation)
>
> Phase C may begin coding against the §3 contract once this card is
> committed. The §4 oracle gates are the only gates this card
> imposes. Public n=4 exposure remains Phase D.

## Appendix — change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1.0 | 2026-05-13 | Initial draft and freeze. Pinned API contract for `_L_4_thermal_at_time_apply` (§3); shared fixtures (system, D1-baseline-style bath, time grid, basis; §2); four oracle gates (σ_z zero at atol=1e-10, σ_x signal as structural finite+non-zero bounding box `1e-6 ≤ ||L_4^dis||_F ≤ 1e6` with first-run measurement logged for regression, gauge/sign with L_0^dis=0 plus a **card-pinned** n=2 reference value `L_2[BASIS[1]] = [[0, -0.26338525879711916 + 0.04707234985666798j], [0.26338525879711916 - 0.04707234985666798j, 0]]` measured against the §2 fixture under upstream commit `ae20806`, parity for L_1=L_3=0; all §4); implementation hand-off (§5); out-of-scope reminders (§6); and steward freeze sign-off (§7). Documented the σ_z `atol=1e-10` quadrature reality: trapezoidal-on-N=11 may not preserve the algebraic cancellation at the strict tolerance, and the implementation is permitted to choose finer/higher-order internal quadrature while still being called at the §2.3 outer grid index; escalation route is successor card revision, not silent loosening. | Local steward draft; cards-first discipline. |

*Verification card version: v0.1.0 (frozen 2026-05-13). Operationalises
work plan v0.1.5 §4 Phase C as four executable oracle gates against an
assembled-L_4 private helper that consumes the released v0.1.1
transcription, the small-grid-verified `_D_bar_4_companion` Phase B
helper (commit `becccf9`), and the D1 v0.1.2 baseline-style bath
fixture. Public n=4 exposure remains deferred to Phase D.
CC-BY-4.0 (see ../LICENSE-docs).*

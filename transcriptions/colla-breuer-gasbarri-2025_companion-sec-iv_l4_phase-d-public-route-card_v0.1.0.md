---
artifact_id: cbg-companion-sec-iv-l4-phase-d-public-route-card
version: v0.1.0
date: 2026-05-13
type: verification-card / pre-code-public-exposure
status: frozen
parent_transcription: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md
parent_phase_b_card: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_n4-small-grid-verification-card_v0.1.1.md
parent_phase_c_card: transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-c-physics-oracles-card_v0.1.3.md
target_implementation: cbg/tcl_recursion.py — public n=4 thermal Gaussian routing through `_L_4_thermal_at_time_apply`
anchor_plan: plans/dg-4-work-plan_v0.1.5.md §4 Phase D
release_gate: work plan v0.1.5 §4 Phase D acceptance — "public n=4 support is available only for the reviewed thermal Gaussian scope, and all previous n≤3 tests remain green"
reviewer: Ulrich Warring
review_date: 2026-05-13
review_state: frozen-pre-implementation
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-4 Phase D pre-code verification card — public n=4 route for thermal Gaussian scope

> **Status: frozen (2026-05-13).** This card pins the public-API
> exposure of the Phase B `_D_bar_4_companion` and Phase C
> `_L_4_thermal_at_time_apply` private helpers, for the **reviewed
> thermal Gaussian scope only**. Unsupported scopes (non-thermal
> baths, displaced baths, `n ≥ 5`) MUST continue to raise clear
> `NotImplementedError` messages.

## 0. Provenance and role

This card consumes:

- the released parent transcription
  ([Companion Sec. IV L_4 transcription v0.1.1](colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md));
- the Phase B small-grid card v0.1.1 (errata-current) and the
  Phase B helper `_D_bar_4_companion` (commit `becccf9`, 22-test
  acceptance gate passes);
- the Phase C physics-oracles card v0.1.3 (errata-current) and the
  Phase C helpers `_L_4_thermal_at_time_apply` (with §3.2
  commuting-case guard) and `_L_4_thermal_at_time_apply_no_guard`
  (commits `e414448` initial + `3e50e94` cube-domain fix);
- the work plan v0.1.5 §4 Phase D acceptance criterion.

Phase D is the public-API-exposure step. It does not change any
private helper or any algorithm; it only opens the public routes
that currently raise `NotImplementedError` for `n=4` so that the
reviewed thermal Gaussian scope flows through the Phase B+C private
implementation.

The work plan v0.1.5 §4 Phase D explicitly requires the Phase D
diff to keep the private-helper landing (Phase B+C, already merged)
and the public-route exposure (this card's implementation)
**visible as separable concerns**. Since the Phase B/C content is
already on `main`, the Phase D implementation is its own commit;
mechanical revertability of the public exposure is preserved.

## 1. Purpose and scope

### 1.1 What this card does

- Pins the **routing rules**: for `n=4` and `bath_state.family ==
  "thermal"`, the public `L_n_thermal_at_time(n=4, ...)` /
  `K_n_thermal_on_grid(n=4, ...)` /
  `L_n_dissipator_thermal_at_time(n=4, ...)` /
  `L_n_dissipator_norm_thermal_on_grid(n=4, ...)` /
  `K_total_thermal_on_grid(N_card=4, ...)` / `L_n(n=4, ...)` shim
  paths route through the Phase C `_L_4_thermal_at_time_apply`
  helper (which itself applies the §3.2 commuting-case guard before
  the expensive integration).
- Pins the **signature extensions**: `L_n_thermal_at_time` and the
  `L_n` shim grow optional `bath_state`, `spectral_density`,
  `upper_cutoff_factor`, `quad_limit` keyword arguments (required
  at `n=4`, ignored at `n ∈ {0, 1, 2, 3}`). All existing callers
  remain backward-compatible.
- Pins the **unsupported-scope error gates**: non-thermal bath
  states (e.g., `coherent_displaced`) and `n ≥ 5` continue to raise
  `NotImplementedError` with clear messages.
- Pins the **test updates**: the four current `n=4` deferral tests
  in `tests/test_tcl_recursion.py` are flipped from "raises" to
  "returns a callable / norm array"; a new explicit non-thermal-`n=4`
  raise test is added.

### 1.2 What this card does not do

- It does not change any private helper (Phase B+C content is
  unchanged).
- It does not change the §2 fixture, §3 API contract, §3a θ-aware
  discipline, §3b pre-cancellation prohibition, or any of the four
  Phase C oracle gates.
- It does not extend the supported scope beyond thermal Gaussian
  `n=4`. Non-thermal / displaced / `n ≥ 5` continue to raise.
- It does not authorise any change to D1 v0.1.2 frozen parameters
  or to any released transcription / card.
- It does not run any Phase E cross-validation between Path A
  (analytic, via the new public route) and Path B (numerical, via
  `benchmarks/numerical_tcl_extraction`). Phase E is the next step
  after Phase D lands.

## 2. Signature extensions

### 2.1 `L_n_thermal_at_time` grows four optional kwargs

```python
def L_n_thermal_at_time(
    n: int,
    t_idx: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    D_bar_2_array: np.ndarray | None = None,
    *,
    # NEW in Phase D — required at n=4, ignored at n ∈ {0, 1, 2, 3}:
    bath_state: dict[str, Any] | None = None,
    spectral_density: dict[str, Any] | None = None,
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> Callable[[np.ndarray], np.ndarray]:
    ...
```

- For `n ∈ {0, 1, 2, 3}`: the new kwargs are ignored. Existing
  callers (which do not pass them) remain backward-compatible.
- For `n = 4`: `bath_state` and `spectral_density` are required;
  passing `None` for either raises `ValueError` with a clear
  message naming the required kwargs.
- For `n ≥ 5`: raise `NotImplementedError` with the existing
  out-of-scope message.

### 2.2 `L_n(n=4, **kwargs)` shim signature

The `L_n` generic shim already accepts `**kwargs`. It must:
- For `n=4` with `bath_state.family == "thermal"`: route to
  `L_n_thermal_at_time(n=4, ...)` with the required Phase D kwargs
  forwarded.
- For `n=4` with `bath_state.family != "thermal"`: raise
  `NotImplementedError` pointing at `K_total_displaced_on_grid`.
- For `n ≥ 5`: continue to raise the existing out-of-scope message.

### 2.3 Downstream functions: no signature change

`K_n_thermal_on_grid`, `L_n_dissipator_thermal_at_time`,
`L_n_dissipator_norm_thermal_on_grid`, and `K_total_thermal_on_grid`
already accept `bath_state` and `spectral_density` as required
keyword arguments. Their internals (which call
`L_n_thermal_at_time`) must forward those kwargs at `n=4` so the
routing reaches `_L_4_thermal_at_time_apply`. No public signature
change is needed.

## 3. Routing rules

| Function | `n` | `bath_state.family` | Behaviour |
|---|---|---|---|
| `L_n_thermal_at_time` | `0..3` | `thermal` | Existing path (unchanged from Phase B/C) |
| `L_n_thermal_at_time` | `4` | `thermal` | **NEW**: route to `_L_4_thermal_at_time_apply` with `(t_idx, t_grid, H_S, A, bath_state, spectral_density, upper_cutoff_factor, quad_limit)` |
| `L_n_thermal_at_time` | `4` | not present or `bath_state=None` | Raise `ValueError("L_n_thermal_at_time: n=4 requires bath_state and spectral_density kwargs (Phase D contract)")` |
| `L_n_thermal_at_time` | `4` | `coherent_displaced` etc. | Raise `NotImplementedError` pointing at the displaced-bath entry point |
| `L_n_thermal_at_time` | `≥5` | any | Raise `NotImplementedError` with the existing out-of-scope message |
| `K_n_thermal_on_grid` | `4` | `thermal` | Loop over `t_idx`, call `L_n_thermal_at_time(4, t_idx, ..., bath_state=..., spectral_density=...)`, apply `K_from_generator` |
| `K_n_thermal_on_grid` | `≥5` | any | Raise `NotImplementedError` |
| `L_n_dissipator_thermal_at_time` | `4` | `thermal` | Forward `bath_state`/`spectral_density` to `L_n_thermal_at_time(n=4, ...)`; compute `K_n` via `K_n_thermal_on_grid(4, ...)`; dissipator residual `L_n + i [K_n, ·]` returned as before |
| `L_n_dissipator_norm_thermal_on_grid` | `4` | `thermal` | Existing wrapper around `L_n_dissipator_thermal_at_time`; works once that route is open |
| `K_total_thermal_on_grid` | `N_card=4` | `thermal` | Existing summation; lift the `N_card > 3` gate to `N_card > 4` so `N_card=4` flows through |
| `K_total_thermal_on_grid` | `N_card≥5` | any | Raise `NotImplementedError` (existing message reused, threshold raised to >4) |
| `L_n` shim | `4` | `thermal` | Route to `L_n_thermal_at_time(n=4, ...)` |
| `L_n` shim | `4` | not thermal | Raise pointing at displaced entry point |
| `L_n` shim | `≥5` | any | Raise (existing out-of-scope message) |

## 4. Error message conventions

For unsupported scopes, error messages must satisfy the existing
test matchers:

- `match="n=4|deferred"` is **retired** — there is no longer a
  deferral at `n=4` for thermal Gaussian. The Phase D test rewrite
  removes this matcher from `n=4` thermal Gaussian gates.
- `match="out of scope|not implemented"` is **retained** for `n ≥ 5`.
- `match="K_total_displaced_on_grid"` is **retained** for non-thermal
  routing.
- `match="bath_state|spectral_density"` is **introduced** for the
  `n=4`-without-required-kwargs error.

## 5. Test gate updates

The following four `tests/test_tcl_recursion.py` tests are flipped
from "n=4 raises pending" to "n=4 thermal returns a result", and
two new tests are added:

### 5.1 Flipped from deferral to functional

- `test_L_n_thermal_at_time_n_4_raises_pending_recursion` → rename
  to `test_L_n_thermal_at_time_n_4_thermal_returns_callable`.
  Assertion: `L_n_thermal_at_time(4, ..., bath_state=thermal,
  spectral_density=ohmic, ...)` returns a callable that, when
  applied to a basis element, returns a finite (d, d) complex
  ndarray.
- `test_L_n_dissipator_n_4_raises_pending` → rename to
  `test_L_n_dissipator_norm_n_4_thermal_returns_finite_array`.
  Assertion: returns a finite (n_t,) real array.
- `test_K_total_N_card_4_raises_pending_recursion` → rename to
  `test_K_total_thermal_on_grid_N_card_4_thermal_returns_finite_array`.
  Assertion: returns a finite (n_t, d, d) complex array.
- `test_L_n_shim_n_4_raises_pending_recursion` → rename to
  `test_L_n_shim_n_4_thermal_returns_callable`.
  Assertion: routes through `L_n_thermal_at_time(n=4)` and matches
  the direct call output to machine precision.

### 5.2 New tests for unsupported scopes at n=4

- `test_L_n_thermal_at_time_n_4_without_bath_kwargs_raises_value_error`:
  calling `L_n_thermal_at_time(4, ..., D_bar_2_array=None)` without
  `bath_state`/`spectral_density` raises `ValueError` matching
  `bath_state|spectral_density`.
- `test_L_n_thermal_at_time_n_4_non_thermal_raises`: calling with
  `bath_state.family = "coherent_displaced"` raises
  `NotImplementedError` matching `K_total_displaced_on_grid`.

### 5.3 Retained existing tests (unchanged)

- `test_L_n_thermal_at_time_n_5_raises_out_of_scope`: `n=5` still
  raises with the existing matcher.
- All n ∈ {0, 1, 2, 3} tests are unchanged and MUST remain green
  (work plan v0.1.5 §4 Phase D acceptance: "all previous n≤3 tests
  remain green").
- `test_K_n_non_thermal_points_to_displaced_entry_point`: non-thermal
  routing at the K_n level is unchanged.

### 5.4 σ_x signal cross-check (NEW, optional)

A new test in `tests/test_n4_physics_oracles.py` (or a new
`tests/test_n4_public_route.py`) MAY assert that the public
`L_n_dissipator_norm_thermal_on_grid(4, ...)` value at the §2
gating fixture is consistent with the Phase C §4.2 σ_x signal
oracle's `‖L_4^dis‖_F` measurement (commit `3e50e94`: ~2.52e-2).
This is a "same-source consistency" check between the private and
public routes; it does NOT introduce a new physics gate.

## 6. Out-of-scope reminders

This card explicitly does NOT cover:

- **Phase E Path A / Path B cross-validation.** That is the next
  step after Phase D lands.
- **Non-thermal `n=4` support.** Out of DG-4 v0.1.5 scope; non-thermal
  baths remain a `NotImplementedError` at `n=4`.
- **`n ≥ 5` support.** Out of DG-4 v0.1.5 scope.
- **`route_version` parameter on `L_n_thermal_at_time`.** Per work
  plan v0.1.5 §3, this is deferred to a future revision that lands
  a second analytic or numerical route for n=4 thermal Gaussian
  (likely Tier-2.D or Path C). Phase D does not introduce this
  parameter.
- **Any change to Phase B/C private helpers or their cards.** Phase D
  is purely a public-route exposure; the private path is unchanged
  from commit `3e50e94` (Phase C review fix) + commit `0d900ec`
  (card erratum chain).

## 7. Steward freeze sign-off

> I have drafted Phase D as a public-route-exposure card. The scope
> is the reviewed thermal Gaussian n=4 path; non-thermal /
> displaced / n≥5 scopes continue to raise `NotImplementedError`
> with clear messages. The implementation is a routing change
> (with one signature extension to `L_n_thermal_at_time` adding
> optional bath kwargs) plus four test flips and two new tests for
> the unsupported-scope error gates. No private helper, algorithm,
> or fixture changes. Per cards-first discipline, this file is
> content-immutable post-commit; revisions are by superseding
> successor at a new version.
>
> Reviewer: Ulrich Warring  Date: 2026-05-13
>
> Version at freeze: v0.1.0 (release state: frozen-pre-implementation)
>
> Phase D may begin coding against the §3 routing rules and §5 test
> gate updates once this card is committed. Phase E cross-validation
> (work plan v0.1.5 §4 Phase E) is the next step after Phase D lands.

## Appendix — change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1.0 | 2026-05-13 | Initial draft and freeze. Pins the public-route exposure rules for n=4 thermal Gaussian: `L_n_thermal_at_time(n=4)` routes to `_L_4_thermal_at_time_apply` (Phase C helper, commits `e414448` + `3e50e94`); `K_n_thermal_on_grid(n=4)`, `L_n_dissipator_*(n=4)`, `K_total_thermal_on_grid(N_card=4)`, and the `L_n` shim all propagate. Signature extension: `L_n_thermal_at_time` and the `L_n` shim grow optional `bath_state`/`spectral_density`/`upper_cutoff_factor`/`quad_limit` kwargs (required at n=4). Unsupported scopes (non-thermal, displaced, n≥5) continue to raise. Four `n=4` deferral tests flipped from "raises pending" to "returns callable / norm array"; two new tests added for the unsupported-scope error gates at n=4. | Local steward draft; cards-first discipline. |

*Verification card version: v0.1.0 (frozen 2026-05-13). Pins the
public-route exposure of the Phase B+C private helpers for the
reviewed thermal Gaussian n=4 scope. Phase E cross-validation is
the next step. CC-BY-4.0 (see ../LICENSE-docs).*

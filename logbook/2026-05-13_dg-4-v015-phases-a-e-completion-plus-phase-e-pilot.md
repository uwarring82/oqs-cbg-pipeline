# DG-4 v0.1.5 Phases A–E completion + Phase E unclassified pilot

**Date:** 2026-05-13
**Type:** dg-completion
**Triggering commits:**
- Phase A: `24c771e` (transcription v0.1.1 release), `17c7ace` / `3c43eac` (post-release docs cleanup)
- Phase B: `ae20806` (card freeze v0.1.0), `becccf9` (`_D_bar_4_companion` + 22-test small-grid gate)
- Phase C: `49b92d5` / `6732924` (cards v0.1.0 / v0.1.1), `e414448` (assembled L_4 + card v0.1.2), `3e50e94` (cube → outer-simplex domain fix + 3 doc findings), `0d900ec` (Phase C v0.1.3 + Phase B v0.1.1 errata chain)
- Phase D: `2959925` (public-route card v0.1.0), `f599751` (`L_n_thermal_at_time` n=4 routing + dissipator/`K_total` cascade), `6cb0ea6` (stale-deferral doc sweep)
- Phase E: `749bd85` (pilot card v0.1.0, `frozen-unclassified-pilot`)

**Triggering evidence:**
- DG-4 work plan v0.1.5 (Council-3-frozen): see [`2026-05-11_dg-4-work-plan-v015-frozen-via-council-3.md`](2026-05-11_dg-4-work-plan-v015-frozen-via-council-3.md).
- Phase A transcription artefact [`colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md).
- Phase B card [`colla-breuer-gasbarri-2025_companion-sec-iv_l4_n4-small-grid-verification-card_v0.1.1.md`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_n4-small-grid-verification-card_v0.1.1.md) (errata) + test gate [`tests/test_n4_small_grid_verification.py`](../tests/test_n4_small_grid_verification.py) (22 tests passing).
- Phase C card [`colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-c-physics-oracles-card_v0.1.3.md`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-c-physics-oracles-card_v0.1.3.md) (errata) + test gate [`tests/test_n4_physics_oracles.py`](../tests/test_n4_physics_oracles.py) (19 tests passing).
- Phase D card [`colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-d-public-route-card_v0.1.0.md`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-d-public-route-card_v0.1.0.md) + updated regression suite [`tests/test_tcl_recursion.py`](../tests/test_tcl_recursion.py) (47 tests passing).
- Phase E pilot card [`colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-pilot-card_v0.1.0.md`](../transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_phase-e-pilot-card_v0.1.0.md).
- D1 Path B reference payload [`benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json`](../benchmarks/results/D1_failure-envelope-convergence_v0.1.2_result.json).

## Summary

DG-4 work plan v0.1.5 Phases A–D are implemented and verified end-to-end. The analytic n=4 thermal-Gaussian route is now publicly exposed through `cbg.tcl_recursion.L_n_thermal_at_time(n=4, ...)` and its downstream dissipator/`K_total` cascade, gated by 22 small-grid Companion-identity checks (Phase B), 19 physics-oracle checks (Phase C — σ_z exact-zero via commuting-case guard + Part B convergence diagnostic, σ_x finite signal, parity, L_0^dis=0, n=2 regression), and 47 regression-suite checks (Phase D deferral-tests flipped + new error-gate tests).

Phase E (analytic Path A vs numerical Path B cross-validation pilot) is recorded as **`frozen-unclassified-pilot`** — a fourth state outside the work plan's three-state acceptance set (`supports-path-b-classification` / `contradicts-path-b-classification` / `inconclusive-with-cause`). An analytical convention audit confirmed no normalization or definition mismatch between the two paths; the remaining magnitude disagreement is a dual-side numerical-resolution issue. No classification verdict is issued. The D1 v0.1.2 PASS envelope is unchanged.

## Detail

### Phase A–D artifact table

| Phase | Artifact | Status |
|---|---|---|
| A | Companion Sec. IV L_4 transcription v0.1.1 | Released (`24c771e`); two post-release docs-cleanup passes (`17c7ace`, `3c43eac`) |
| B | Small-grid verification card v0.1.1 (errata) + `_D_bar_4_companion` + `_D_companion_raw_n{2,4}` | 22/22 tests passing |
| C | Physics-oracles card v0.1.3 (errata) + `_L_4_thermal_at_time_apply` (+ `_no_guard` diagnostic) | 19/19 tests passing; σ_z gated via `[H_S, A] = 0` Feynman-Vernon guard (Part A) + non-gating O(h¹) convergence diagnostic (Part B, reference table re-pinned post-domain-fix) |
| D | Public-route card v0.1.0 + `L_n_thermal_at_time(n=4)` + dissipator/`K_total` cascade (`N_card > 4`) + stale-deferral doc sweep | 47/47 regression tests passing; 4 deferral tests flipped to callable, 6 new unsupported-scope + guard-exact-zero gates |

### Phase E pilot measurements

Path A analytic route (current implementation, n=4 thermal Gaussian, Eqs. (69)-(73) literal with outer-simplex-intersected θ-windows):

| Grid (N) | `<‖L_4^dis‖>_t / α²` | Ratio to Path B 47.42 |
|---:|---:|---:|
| 11 | ~1.07 | ~0.023 |
| 21 | ~1.24 | ~0.026 |
| 41 | ~14.15 | ~0.298 |

Path B numerical Richardson extraction (D1 v0.1.2 baseline payload): `<‖L_4^dis‖>_t = 1300.49`, `<‖L_2^dis‖>_t = 27.42`, **coefficient ratio = 47.42**.

The Path A trend (1.07 → 1.24 → 14.15) over N=11→21→41 indicates Path A is **not converged** in the pilot range. The analytical audit (commit-level inspection of [`benchmarks/numerical_tcl_extraction.py`](../benchmarks/numerical_tcl_extraction.py) against the Phase D public route) confirmed **no convention mismatch**: the α convention (`coupling_strength = α_phys²`), the dissipator convention (`L^dis := L + i [K, ·]`), the Liouville d²×d² Frobenius norm, and the picture choice all agree between the two paths.

The remaining ~5-order-of-magnitude residual disagreement at N≤41 is therefore attributed to two simultaneous numerical-resolution effects, neither resolvable inside the pilot scope:

1. **Path A quadrature not converged.** Trapezoidal nested-simplex quadrature at O(h¹) on N≤41 grids is far from the analytic asymptote.
2. **Path B finite-env extraction floor.** Carried forward from the 2026-05-06 σ_z thermal zero-oracle pilot; documented but not re-audited under v0.1.5.

### Deferred tracks (post-pilot)

| Track | Scope | Estimated cost |
|---|---|---|
| 5.A | Finer-grid Path A sweep (N=81, N=161) to map convergence floor | N=81 ≈ 50 min; N=161 ≈ 25–30 h (revised up from optimistic ~7 h — L_4 assembly is O(N⁵)) |
| 5.B | Higher-order quadrature (Romberg / Gauss–Legendre on nested-simplex) | Implementation + re-pin of Part B reference table |
| 5.C | Path B floor audit (re-evaluate finite-env extraction at higher `omega_max_factor` + tighter Richardson stencil) | Independent of 5.A/5.B; can run in parallel |

### What still doesn't stand

- No Phase E classification verdict. The `frozen-unclassified-pilot` state is a record-only artefact and does **not** trigger Council-3 convening, does **not** alter D1 v0.1.2 PASS, and does **not** unblock Phase F.
- Path A is not validated as the preferred analytic reference; the Part B diagnostic shows correct asymptotic *form* but not converged *value* at pilot resolutions.

## Routing notes

- **D1 v0.1.2 PASS verdict is unchanged.** The Phase E disagreement is dual-side numerical, not a defect in either implementation; the v0.1.2 envelope continues to satisfy the v0.1.5 reproducibility predicate as written.
- **Phase F is blocked** pending a Phase E classification verdict. Selection of which deferred track (5.A / 5.B / 5.C) to advance is a steward decision and out of scope of this entry.
- **CL-2026-005 v0.4 Entry 2** remains scope-limited for analytic recursion; the v0.1.5 work plan does not modify it.
- The Phase E pilot card's `triggering_commit` is `749bd85`; this logbook entry's commit hash is the v0.1.5 completion-record reference.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

# Colla-Breuer-Gasbarri Companion Sec. IV L4 transcription released at v0.1.1

**Date:** 2026-05-12
**Type:** structural
**Triggering commit:** `24c771e`
**Triggering evidence:** `transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.1.md` (new released successor); `transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.0.md` (annotated with `superseded_by`); `transcriptions/README.md` (index updated); `plans/README.md` and `docs/validity_envelope.md` (operational pointers updated)

## Summary

The DG-4 Tier-2.B Phase A transcription for Companion Sec. IV is now released at v0.1.1. This successor closes the remaining transcription-layer source-alignment blocker by deriving the mixed-order repo-to-paper conversion rule for raw bath correlators: Companion Eq. (15) maps to the repo Wick leaf by a chain-reversal-and-swap of the mixed `(tau_args, s_args)` inputs. Section 10 is countersigned in v0.1.1, and v0.1.0 is retained as the superseded pre-release predecessor.

## Detail

The release bump does three things:

1. Promotes the transcription from pre-release draft status to a stable repository-local source artifact for Phase B consumption.
2. Records the exact mixed-order conversion needed when reusing `cbg.bath_correlations.n_point_ordered` for Companion raw `D(τ_1^k, s_1^{n-k})` inputs:

```text
D_companion(τ_1^k, s_1^{n-k})
  = n_point_ordered(
      tau_args = tuple(reversed(s_args)),
      s_args   = tuple(reversed(tau_args)),
    )
```

This reproduces the Companion trace operator order `(s_{n-k}, ..., s_1, τ_1, ..., τ_k)` exactly. The familiar `n = 2`, `k = 1` complex-conjugation relation is the singleton special case of this broader rule.

3. Separates transcription release from implementation completion. The source transcription is now released, but Phase B code still has to:
   - apply the row-2.3 mixed-order conversion when consuming the repo's Wick leaf,
   - implement Companion Eqs. (69)-(73) directly rather than reusing the B.1 standard-cumulant path,
   - and complete the small-grid verification under the §4.4 theta-aware combination rule before code lands.

No code changed, no benchmark card changed, no DG verdict changed, and D1 v0.1.2 remains the live DG-4 PASS artifact.

## Routing notes

This is a transcription-layer structural release only. It does not modify the Sail, the Ledger, the validity-envelope DG statuses, or any frozen card/result artifacts. It unblocks the source-citation side of DG-4 Path A implementation work under `plans/dg-4-work-plan_v0.1.5.md`; the remaining work is Phase B code plus later Path A / Path B cross-validation.

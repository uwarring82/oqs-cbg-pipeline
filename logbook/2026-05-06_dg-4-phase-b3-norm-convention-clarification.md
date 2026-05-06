# DG-4 Phase B.3 — norm-convention clarification (supersedes original Phase B.3 partial entry)

**Date:** 2026-05-06
**Type:** structural-correction
**Supersedes:** [`2026-05-06_dg-4-phase-b3-partial-dissipator-extraction.md`](2026-05-06_dg-4-phase-b3-partial-dissipator-extraction.md)
**Triggering commit:** _placeholder_
**Triggering evidence:**
- Numerical verification (this entry) of the wrong-sign Liouville-Frobenius residual.

## Scope of this correction

This entry corrects exactly one numerical claim in the original Phase B.3 partial logbook entry. The original entry's main content — the convention `L_n^dissipator := L_n + i [K_n, ·]`, the unitary-recovery oracle (Risk R8), the empirical 5-row table of ‖L_n^dissipator‖ values across (n, model) pairs, the test inventory, and the routing notes — is **all unchanged and still correct**. Only the parenthetical wrong-sign counterfactual number is wrong.

## What the original entry said

Quoting the original:

> The n=0 row is the strong falsification: an opposite sign would give 2 × ‖H_S‖_HS = 2.0 here instead of 0.

This conflates three distinct norm conventions. The implementation uses the Frobenius norm of the d²×d² Liouville-representation matrix in the matrix-unit basis (`np.linalg.norm(L_matrix, ord='fro')` at [`cbg/tcl_recursion.py`](../cbg/tcl_recursion.py) `L_n_dissipator_norm_thermal_on_grid`). For `H_S = (ω/2) σ_z` with `ω = 1`:

| Norm convention | Numerical value |
|---|---|
| **Frobenius of the Liouville matrix** (the suite-measured norm) | **2√2 ≈ 2.828** |
| Spectral (operator) norm of the Liouville matrix | 2.000 |
| 2 · ‖H_S‖_F (Hilbert-Schmidt of the operator H_S) | √2 ≈ 1.414 |

The original entry's "2.0" matches the *spectral* norm of the Liouville matrix, not the Frobenius norm the suite actually computes.

## Numerical check

```
||L_0||_Frobenius (Liouville) = 1.4142135623730951
||L_0||_spectral  (Liouville) = 1.0
||H_S||_Frobenius             = 0.7071067811865476

wrong-sign counterfactual L_0_wrong = -2i[H_S, ·]:
  ||L_0_wrong||_F   (Liouville) = 2.8284271247461903   ← what the suite measures
  ||L_0_wrong||_spec(Liouville) = 2.0
  2 · ||H_S||_F                 = 1.4142135623730951
```

(Run via `.venv/bin/python` against the implemented basis and superop construction; verifiable directly from the matrix-unit Liouville representation.)

## Correct counterfactual

The accurate sentence is:

> The n=0 row is the strong falsification: an opposite sign would give the Liouville-Frobenius residual ‖L_0^wrong‖_F = 2 · ‖L_0‖_F = 2√2 ≈ **2.828** here instead of 0.

The factor-of-2 enhancement comes from the wrong-sign superoperator being literally twice the correct unitary generator: `L_0^wrong = -i[H_S,·] - i[H_S,·] = -2i[H_S,·]`. The Frobenius norm of a superop scales linearly with the superop, so the wrong-sign residual is exactly `2 × ‖L_0‖_F`. For our H_S = σ_z/2, `‖L_0‖_F = √2` and the residual is `2√2`.

## What is unaffected

- The implementation. The B.3 code is correct; only the logbook explanatory text was wrong.
- The unitary-recovery oracle test (`test_L_0_dissipator_unitary_recovery_oracle`) still fires at exact zero. The test asserts the *correct* sign convention; the wrong-sign value is never actually evaluated by the suite — the wrong-sign discussion is purely counterfactual / pedagogical.
- All five rows of the original entry's empirical confirmation table.
- The convention statement, the API description, the test inventory, and the routing notes for the L_4 deferral.
- The DG-4 work plan v0.1.4's Risk R8 narrative, which is updated separately to cite the corrected number.

## Routing

This is a documentation-only correction. No code changes. The original entry is annotated `superseded by:` per logbook supersedure discipline. Future readers should treat both entries as the authoritative record of Phase B.3 partial: the original for the substance, this entry for the corrected explanatory number.

---

*Logbook entry. Immutable once committed. The `Triggering commit` placeholder above may be filled self-referentially in a follow-up commit per [`logbook/README.md`](README.md) §Immutability exception 2.*

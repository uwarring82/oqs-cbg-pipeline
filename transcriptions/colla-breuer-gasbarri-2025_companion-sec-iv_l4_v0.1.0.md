---
artifact_id: transcription-cbg-companion-sec-iv-l4
version: v0.1.0
date: 2026-05-11
type: transcription / equation-map
status: scaffold (steward fill-in required before Phase B)
source_authority: TBD-by-steward
source_doi: TBD-by-steward
source_arxiv_version: TBD-by-steward
source_section: "Colla, Breuer, Gasbarri (2025), Companion paper, Section IV (TCL fourth-order analytic expression)"
target_implementation: cbg/tcl_recursion.py — analytic helper for thermal Gaussian n=4
anchor_plan: plans/dg-4-work-plan_v0.1.5.md §4 Phase A
anchor_ledger: ledger/CL-2026-005_v0.4.md Entry 2 (recursive-series convergence; COMPATIBLE, scope-limited)
reviewer: TBD-by-steward
review_date: TBD-by-steward
review_state: scaffold-not-yet-reviewed
release_state: pre-release-until-source-pinned
license: CC-BY-4.0 (LICENSE-docs)
---

# Companion Sec. IV — analytic L_4 transcription and equation map

> **Status: scaffold.** This file establishes the structural infrastructure
> for transcribing the Companion paper's Section IV analytic fourth-order
> TCL expression into a form citable by `cbg/tcl_recursion.py` and by the
> Phase C oracles. The equation slots below are explicitly marked
> `[TRANSCRIBE FROM PAPER]`. No implementation work (Phase B onward) should
> begin until every such slot is filled and the file has been re-read by
> the steward against the source.

## 0. Provenance and review block

| Field | Value | Status |
|---|---|---|
| Source paper | Colla, Breuer, Gasbarri (2025) — Companion | TBD-by-steward |
| Source DOI | `10.xxxx/...` | TBD-by-steward |
| Source arXiv version | `arXiv:xxxx.xxxxxvN`, dated `YYYY-MM-DD` | TBD-by-steward |
| Source section | Section IV — analytic fourth-order TCL | Pinned |
| Equation numbers transcribed | `(IV.x)`, `(IV.y)`, ... | TBD-by-steward |
| Sign-convention review pass | Steward checklist §2 below | Not yet completed |
| Reviewer | Ulrich Warring (or named delegate) | TBD-by-steward |
| Review date | `YYYY-MM-DD` | TBD-by-steward |

**Pre-release marker.** While `source_doi` or `source_arxiv_version` are
TBD, this artifact is `pre-release` and **must not be cited as a stable
reference** by tests or implementation comments. Promotion to release state
requires both fields pinned and the §2 sign-convention checklist signed off.

## 1. Purpose and scope

### 1.1 What this artifact does

This transcription provides a one-to-one equation map between the Companion
Sec. IV analytic fourth-order TCL expression and the repository symbols
used in `cbg/tcl_recursion.py`. The map covers:

- the operator generators `L_n` and their dissipator parts `L_n^dis`;
- the Lambda subtractor sequence `Lambda_n` and its time derivative;
- the bath two-point correlation function `C(t, s)` and its conjugate;
- the unitary-correction Hamiltonians `K_n`;
- the picture (interaction vs Schrödinger) in which each object is defined;
- the left/right action conventions used by `superoperator.py`.

### 1.2 What this artifact does not do

- It does not derive Sec. IV; it transcribes and maps it.
- It does not extend Sec. IV beyond the thermal Gaussian scope.
- It does not commit to higher orders (`n >= 5`).
- It does not authorise any change to D1 v0.1.2 frozen parameters or the
  D1 v0.1.2 result JSON.

## 2. Sign-convention checklist (must be signed off before Phase B)

Each row below must be filled in from the Companion paper before any
implementation work. Where the Companion paper differs from the
repository's convention, the difference must be explicitly recorded as a
**conversion rule**, not silently absorbed.

| # | Convention | Companion value | Repository value | Conversion rule | Status |
|---|---|---|---|---|---|
| 2.1 | Picture for `L_n` definition | `[TRANSCRIBE: interaction or Schrödinger?]` | Interaction-picture (per existing n=2 implementation) | `[TRANSCRIBE: identity or rotation by H_S]` | Open |
| 2.2 | Left/right action convention on system density matrix | `[TRANSCRIBE: A — σ vs σ — A; column-major vs row-major superop layout]` | `superoperator.py` uses `[TRANSCRIBE: existing convention name]` | `[TRANSCRIBE: identity or transpose]` | Open |
| 2.3 | Sign of bath two-point function `C(t, s)` | `C(t, s) = ⟨B(t) B(s)⟩` or its complex conjugate? | `[TRANSCRIBE: existing repo convention from n=2 route]` | `[TRANSCRIBE: identity or conjugation]` | Open |
| 2.4 | Time ordering in nested integrals | `[TRANSCRIBE: t ≥ s_1 ≥ s_2 ≥ ... or other]` | `[TRANSCRIBE: existing repo convention]` | `[TRANSCRIBE]` | Open |
| 2.5 | Dissipator extraction sign | Implicit in Companion; pinned at repository level | `L_n^dis := L_n + i [K_n, ·]` | Repository convention is authoritative | **Pinned (repository convention)** |
| 2.6 | Lambda-inversion subtraction structure | `[TRANSCRIBE: explicit Sec. IV equation number]` | `L_4 = d_t Λ_4 — L_2 Λ_2` | Identity if Companion uses same form; otherwise transcribe Companion form and record subtractor algebra in §5 | Open |
| 2.7 | Hermiticity / Hermitian-adjoint conventions | `[TRANSCRIBE]` | `[TRANSCRIBE existing]` | `[TRANSCRIBE]` | Open |
| 2.8 | Ordering of bath operators in 4-point correlator (Wick contractions) | `[TRANSCRIBE: which pairing convention?]` | n=2 route uses 2-point only; n=4 introduces the 4-point Wick split for the first time | **New for n=4; must be transcribed explicitly** | Open |

**Steward sign-off line for §2:**

> I have checked rows 2.1 through 2.8 against the Companion paper version
> pinned in §0 and recorded any conversion rules needed to reconcile its
> conventions with the repository.
>
> Reviewer: _________________________  Date: ____________

**Guardian note.** Row 2.8 is the new sign-convention surface introduced
at n=4. The rejected single nested-commutator candidate (see §6) was
defeated precisely by mishandling the 4-point Wick pairing. This row must
be re-read by the steward before code lands.

## 3. Symbol map (Companion — repository)

Every Companion symbol used in the Sec. IV L_4 expression must appear in
this table with its repository counterpart. Where no repository counterpart
exists yet, the table records what would need to be added.

| Companion symbol | Companion meaning | Repository symbol | Repository location | Notes |
|---|---|---|---|---|
| `[TRANSCRIBE]` | Coupling operator on system side | `A` (or `system_coupling_operator`) | `models/spin_boson.py` | Existing |
| `[TRANSCRIBE]` | Bath two-point correlator | `C` | `cbg/bath_correlations.py` | Existing for n=2 route |
| `[TRANSCRIBE]` | Lambda_2 subtractor | `Lambda_2` | `cbg/tcl_recursion.py` | Existing |
| `[TRANSCRIBE]` | Lambda_4 subtractor | `Lambda_4` | `cbg/tcl_recursion.py` | **To be added** in Phase B |
| `[TRANSCRIBE]` | K_2 unitary correction | `K_2` | `cbg/tcl_recursion.py` | Existing |
| `[TRANSCRIBE]` | K_4 unitary correction | `K_4` | `cbg/tcl_recursion.py` | **To be added if mechanically unblocked by L_4**; otherwise deferred to Tier-2.D |
| `[TRANSCRIBE]` | 4-point bath Wick split factor | `_wick_4pt_split` (proposed private name) | `cbg/tcl_recursion.py` | **New for n=4** |
| `[TRANSCRIBE]` | ... | ... | ... | ... |

> **Fill instruction.** Add one row per distinct Companion symbol used in
> the Sec. IV L_4 expression. If the Companion paper uses the same symbol
> in two different contexts (e.g. operator vs scalar coefficient),
> transcribe them as two separate rows.

## 4. Equation transcription slots

### 4.1 Master expression

> **Steward fill-in.** Transcribe the Companion paper's Sec. IV L_4
> master expression verbatim into the block below, using LaTeX-style
> notation in fenced code. Annotate each Companion symbol that appears
> with a reference to the §3 symbol map.

```text
[TRANSCRIBE FROM PAPER: Companion Sec. IV master equation for L_4]

Equation reference: (IV.x)

L_4(t) = ...
```

**Companion equation anchor:** `(IV.x)` — `[TRANSCRIBE exact equation number]`.

### 4.2 Lambda_4 expression

```text
[TRANSCRIBE FROM PAPER: Sec. IV Lambda_4 definition]

Equation reference: (IV.y)

Lambda_4(t) = ...
```

**Companion equation anchor:** `(IV.y)` — `[TRANSCRIBE exact equation number]`.

### 4.3 d_t Lambda_4

```text
[TRANSCRIBE FROM PAPER, or DERIVE FROM 4.2:
 d_t Lambda_4(t) = ... ]

If derived rather than transcribed, annotate the derivation step in §5.
```

### 4.4 4-point bath correlator split

```text
[TRANSCRIBE FROM PAPER: Sec. IV Wick decomposition of
 ⟨B(t_1) B(t_2) B(t_3) B(t_4)⟩_thermal into 2-point pairings]

Equation reference: (IV.z)

⟨B(t_1) B(t_2) B(t_3) B(t_4)⟩ = C(t_1, t_2) C(t_3, t_4)
                              + C(t_1, t_3) C(t_2, t_4)
                              + C(t_1, t_4) C(t_2, t_3)
```

> Confirm that the above is the Companion convention. Some references
> include a Wick sign factor for fermionic baths; the thermal Gaussian
> bosonic case here should have all three pairings with `+1` coefficient.
> **Record the Companion paper's explicit form regardless.**

## 5. Lambda-inversion subtraction — repository form

The repository implements

```text
L_4 := d_t Lambda_4 — L_2 Lambda_2
```

with the right-hand side evaluated at time `t`. The Companion paper either
states this identity directly in Sec. IV or implies it through the
generator-inversion construction. The steward must record which:

- [ ] **Case A:** Companion states the subtraction identity directly.
      Citation: `(IV.w)`. No further reconciliation needed.
- [ ] **Case B:** Companion uses a different but algebraically equivalent
      form. Citation: `(IV.w)`. Reconciliation algebra recorded below.
- [ ] **Case C:** Companion form differs and is not obviously equivalent.
      **Stop — escalate to Council-3 before Phase B begins.**

**Case B reconciliation (if applicable):**

```text
[TRANSCRIBE Companion form, then show algebraic steps reducing it to the
 repository form L_4 = d_t Lambda_4 — L_2 Lambda_2.]
```

## 6. Falsification note — rejected single nested-commutator candidate

The current `cbg/tcl_recursion.py` carries a comment recording a defeated
candidate expression for `L_4` of the schematic form

```text
L_4_candidate(t) ?= ∫∫∫ [A, [A_{s_1}, [A_{s_2}, [A_{s_3}, · ]]]]
                      × C(t, s_1) C(s_2, s_3) ds_1 ds_2 ds_3
                      (single Wick pairing, single nested commutator chain)
```

This candidate is **rejected** because it:

1. Uses only one of the three Wick pairings required by the 4-point
   bosonic Gaussian correlator (see §4.4);
2. Fails the σ_z zero oracle (it returns non-zero values for pure
   dephasing where the Feynman–Vernon exactness theorem requires `L_4 = 0`);
3. Conflates the nested-commutator structure of `L_2` with what is in fact
   a sum over Wick pairings at n=4.

> **Steward instruction.** Do **not** reintroduce any expression that
> reduces, in the thermal Gaussian case, to a single Wick pairing. The
> σ_z zero oracle (Phase C oracle 1) is the falsification gate for this
> class of error.

**Repository anchor:** the falsification note in `cbg/tcl_recursion.py`
must reference this transcription's §6 by stable anchor, not by version
number, so that future revisions of this transcription do not break the
reference.

## 7. Oracle reference points (for Phase C)

This section records, in transcription terms, the four physics oracles
defined in plan §4 Phase C. The steward should verify that the transcribed
expression in §4 has the structural properties required by each oracle
**before** code is written.

### 7.1 Oracle 1 — σ_z zero oracle

**Statement.** For the pure-dephasing thermal Gaussian model with coupling
operator `A = σ_z`, the transcribed `L_4` must vanish identically (or to
machine precision) at every time `t`.

**Why.** Pure dephasing with a Gaussian bath is exactly solvable via
Feynman–Vernon influence functional; all higher-order TCL generators
beyond `L_2` vanish.

**Transcription check.** Inspect the transcribed master expression in
§4.1. Confirm that when `A` commutes with itself (which is trivially the
case for σ_z with itself, but more importantly when `[A, [A, ·]] = 0`
in the relevant operator algebra), every term in §4.1 carries a vanishing
nested commutator. This is a **paper-level** sanity check independent of
code.

| Check | Result |
|---|---|
| All terms in §4.1 carry at least one outer commutator with `A`? | TBD-by-steward |
| Pairing structure of §4.4 preserves σ_z cancellation? | TBD-by-steward |

### 7.2 Oracle 2 — σ_x signal oracle

**Statement.** For the spin-boson model with `A = σ_x` on the D1 baseline
fixture, the transcribed `L_4^dis` must be finite and non-zero on a
representative time grid.

**Why.** This is the regime where Path B v0.1.2 found a non-trivial
failure envelope; if Path A also produced zero here, the cross-validation
would be vacuous.

**Transcription check.** Confirm that the transcribed `L_4` does **not**
identically vanish under non-commuting `A`.

### 7.3 Oracle 3 — Gauge/sign oracle

**Statement.** `L_0^dis = 0` is preserved, and the existing n=2 dissipator
route is unchanged.

**Transcription check.** The new Phase B code must not alter any n<=3
behaviour. The transcription itself has nothing to add here; this is a
Phase B/C regression-test concern.

### 7.4 Oracle 4 — Parity oracle

**Statement.** Odd thermal Gaussian dissipator terms remain zero at n=1
and n=3, so the even-order `r_4` metric remains the intended route.

**Transcription check.** Confirm that the Companion paper's odd-order
generators vanish for the thermal Gaussian bath, or transcribe explicitly
the conditions under which they do.

## 8. Implementation handoff to Phase B

When §§0–7 above are complete and signed off, Phase B is unblocked. The
hand-off boundary is:

- Phase A produces this transcription artifact, frozen at v0.1.0.
- Phase B consumes the transcription as a fixed reference and produces
  the private analytic helper in `cbg/tcl_recursion.py`.

**Phase B implementation comments must cite this artifact by stable
anchor** (`transcriptions/colla-breuer-gasbarri-2025_companion-sec-iv_l4_v0.1.0.md`
§ X.Y) rather than by paragraph quotation, both to keep code lean and to
preserve clear provenance flow.

## 9. Out-of-scope reminders for the transcriber

This transcription is **only** for the analytic fourth-order TCL
expression of the Companion Sec. IV in the thermal Gaussian regime. The
transcriber should **not** extend the artifact to:

- non-thermal initial bath states;
- coherently displaced bath states;
- non-Gaussian baths (anharmonic, structured-mode);
- higher orders `n >= 5`;
- HEOM, TEMPO, MCTDH, pseudomode, or chain-mapping comparisons (those are
  Path C, separate plan);
- literal `K_2`-through-`K_4` recursion completion (Tier-2.D, separate
  plan).

If any of these surfaces during transcription, record the surfacing as a
logbook note and continue with the in-scope transcription only.

## 10. Steward final sign-off block

> I have transcribed the Companion Sec. IV analytic L_4 expression into
> §§3–4 of this artifact, recorded all sign-convention conversions in §2,
> noted the Lambda-inversion case in §5, preserved the falsification note
> in §6, and verified the paper-level oracle conditions in §7. The source
> DOI and arXiv version are pinned in §0. This artifact is hereby promoted
> from `scaffold` to `released` state for Phase B consumption.
>
> Reviewer: _________________________  Date: ____________
>
> Version at sign-off: v0.1.0 (release state: released)

## Appendix — change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1.0 | 2026-05-11 | Scaffold drafted alongside `dg-4-work-plan_v0.1.5` freeze. All equation slots marked TBD-by-steward. | Council-3 (Guardian/Integrator/Architect) deliberation product |

---

*Transcription artifact version: v0.1.0 (scaffold). Drafted 2026-05-11 as
the Phase A artifact for `dg-4-work-plan_v0.1.5`. This is a steward fill-
in document: all `[TRANSCRIBE FROM PAPER]` slots and all TBD-by-steward
fields must be completed and the §2 and §10 sign-off blocks signed before
Phase B implementation begins. CC-BY-4.0 (see ../LICENSE-docs).*

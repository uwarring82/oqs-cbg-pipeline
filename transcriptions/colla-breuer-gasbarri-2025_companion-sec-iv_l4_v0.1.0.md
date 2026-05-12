---
artifact_id: transcription-cbg-companion-sec-iv-l4
version: v0.1.0
date: 2026-05-12
type: transcription / equation-map
status: in-progress-transcription (first-pass fill-in 2026-05-12; steward sign-off pending)
source_authority: APS Version-of-Record PDF (Phys. Rev. A 112, 052222), local copy filed under scratch/sources/ (gitignored)
source_doi: 10.1103/9j8d-jxgd
source_arxiv_version: not-used-as-controlling-identifier (VoR DOI 10.1103/9j8d-jxgd controls; Letter companion preprint is arXiv:2506.04097, informational only)
source_section: "Colla, Breuer, Gasbarri (2025), Companion paper, Section IV (TCL fourth-order analytic expression)"
target_implementation: cbg/tcl_recursion.py — analytic helper for thermal Gaussian n=4
anchor_plan: plans/dg-4-work-plan_v0.1.5.md §4 Phase A
anchor_ledger: ledger/CL-2026-005_v0.4.md Entry 2 (recursive-series convergence; COMPATIBLE, scope-limited)
reviewer: TBD-by-steward
review_date: TBD-by-steward
review_state: first-pass-fill-in-pending-steward-readthrough
release_state: pre-release-until-steward-signoff
license: CC-BY-4.0 (LICENSE-docs)
---

# Companion Sec. IV — analytic L_4 transcription and equation map

> **Status: first-pass fill-in (2026-05-12).** Bibliographic record pinned;
> §§3–4 equation transcription drafted from the Version-of-Record PDF;
> §2 sign-convention rows populated where the paper is unambiguous and
> marked `Open` where the steward must read the source directly (in
> particular the 4-point bath structure, which Sec. IV does not write
> out explicitly under Wick's theorem). No implementation work (Phase B
> onward) should begin until every `Open` row in §2 is closed and the
> §10 sign-off is countersigned.

## 0. Provenance and review block

| Field | Value | Status |
|---|---|---|
| Source paper | Colla, Breuer, Gasbarri — "Recursive perturbation approach to time-convolutionless master equations: Explicit construction of generalized Lindblad generators for arbitrary open systems" | Pinned |
| Source journal reference | *Phys. Rev. A* **112**, 052222 (2025); received 9 May 2025; accepted 3 November 2025; published 24 November 2025. | Pinned |
| Source DOI | `10.1103/9j8d-jxgd` | Pinned |
| Source arXiv version | **Not used as a controlling identifier.** The VoR DOI above controls. For informational reference only, the Letter companion preprint is `arXiv:2506.04097`; the Companion paper's own arXiv identifier (if it has a distinct one) is not required for this transcription and is intentionally not pinned. | Not-controlling (informational) |
| Source PDF local copy | `scratch/sources/colla-breuer-gasbarri-2025_companion_PRA-112-052222.pdf` (gitignored; not redistributed). Letter copy: `scratch/sources/colla-breuer-gasbarri-2025_letter_PRA-112-L050203.pdf`. | Pinned |
| Source license | CC-BY-4.0 (APS, "Published by the American Physical Society under the terms of the Creative Commons Attribution 4.0 International license."). | Pinned |
| Source section | Section IV — "Explicit Expansion up to Fourth Order" (article pages 052222-6 to 052222-8). Subsections IV.A First order; IV.B Second order; IV.C Third order; IV.D Fourth order. Also relevant: Sec. III.B–III.C (canonical generalized-Lindblad form, perturbative `K(t)` expansion). | Pinned |
| Equation numbers verbatim-transcribed into §4 | (28) [`L_n` operator form]; (43) [canonical Lindblad dissipator]; (45), (46), (47)–(49) [`K_n` master + parity split]; (27) [cumulant recursion]; (69)–(73) [n=4 cumulants]; (74)–(78) [`K_4` and its bath/system blocks]. | Pinned |
| Equation numbers consulted / relevant but **not** verbatim-transcribed | (5)–(6) [Φ_t Taylor expansion]; (8)–(11) [left/right superop product notation]; (15)–(18) [bath cumulant definitions, time-ordering θ, Hermiticity]; (20)–(26) [generator series, μ-coefficient bookkeeping, theta-window rule of notation]; (50)–(53) [n=1: cumulants, `K_1`, `L_1`]; (54)–(59) [n=2: cumulants, `K_2`]; (60)–(68) [n=3: cumulants, `K_3`, coefficients f/g]. | Pinned-as-consulted-only (the corresponding repository routes are implemented at n ≤ 3 and verified to be either zero or matching n=2 path; full verbatim transcription is out of Phase A scope for n ≤ 3). |
| Sign-convention review pass | Steward checklist §2 below | Rows 2.1–2.5, 2.7 Pinned; row 2.6 Pinned-as-Case-B; row 2.8 **Draft-complete** (2026-05-12) pending steward grid-verification of the B.0 flattening convention and the direct Eq. (69)–(73) implementation before Phase B code lands |
| Reviewer | Ulrich Warring (or named delegate) | TBD-by-steward |
| Review date | `YYYY-MM-DD` | TBD-by-steward |

**Pre-release marker.** While the §2 sign-convention checklist `Open` rows
remain unsigned and §10 is uncountersigned, this artifact is
`pre-release` and **must not be cited as a stable reference** by tests or
implementation comments. Promotion to released state requires every §2
row marked `Pinned` or `Closed-by-steward`, plus a countersigned §10.

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
| 2.1 | Picture for `L_n` definition | **Interaction picture.** Sec. II.A: "We move into the interaction picture by evolving the bipartite system under the free local evolution given by `H_S` and `H_E`. We denote the interaction picture Hamiltonian of system and environment by `H̃_t = λ A_t ⊗ B_t` ..." All `L_n` of Eq. (28) and `K_n` of Eq. (45) are written in the interaction picture. | Interaction picture (per existing n=2 implementation in `cbg/tcl_recursion.py`). | Identity (no rotation). The Schrödinger-picture observable `K_S(t)` discussed at Sec. III.C "common case" (e.g. `K_2^S` form) is **already** the interaction-picture answer with the trivial undoing of free evolution at the final time; the repository's `K_n` returns are interaction-picture by construction. | **Pinned** (first-pass fill-in 2026-05-12) |
| 2.2 | Left/right action convention on system density matrix | `X^L[ρ] = X ρ`, `X^R[ρ] = ρ X` (Eq. 3 verbatim). Composition convention: `A^{L/R}(t_1^k)[·] = A^{L/R}_{t_1} ∘ A^{L/R}_{t_2} ∘ ... ∘ A^{L/R}_{t_k}[·]` (Eq. 8), so left-superop products carry the same time ordering as left-multiplications. The right-superop product reads the times in the **same** order but its action `ρ ↦ ρ A_{t_1} A_{t_2} ... A_{t_k}` therefore applies operators in **right-to-left** order on `ρ`. | Repository n=2 route uses `A @ A_I(s−t) @ X` (left action) and `X @ A_I(s−t) @ A` (right action) in `cbg/tcl_recursion.py:L_2_apply`. This matches Eq. (3). | Identity. | **Pinned** (first-pass fill-in 2026-05-12) |
| 2.3 | Sign of bath two-point function `C(t, s)` | Eq. (15) verbatim: `D(τ_1^k, s_1^{n−k}) = Tr_E{ B^R(s_1^{n−k}) ∘ B^L(τ_1^k) [ρ_E] } θ_{τ_1^k} θ_{s_1^{n−k}}`. For the simplest case `n=2`, `k=1`: `D(τ_1, s_1) = ⟨B(s_1) B(τ_1)⟩ θ_{τ_1} θ_{s_1}` (right-acting B applied last under the trace, then left-acting B). Note the **Hermiticity** identity Eq. (18): `D*(τ_1^k, s_1^{n−k}) = D(s_1^{n−k}, τ_1^k)`. | Repository n=2 stores `D̄_2(t, s) = C(t − s)` (stationary baseline) and pairs `C` with the left commutator branch, `C*` with the right commutator branch. Repository signature `cbg.cumulants.D_bar_2` matches the connected two-point with the same time-argument ordering as Eq. (15) at `n=2`, `k=1`. | **Verify-on-readthrough** (repo's stationary `C(t−s)` matches Eq. (15) provided the bath state is stationary; the connected-cumulant subtraction at higher `n` is what `D̄` encodes, see §3 and §4.2). | First-pass-Pinned; **steward to verify the `C` vs `C*` pairing at the right-acting branch survives unchanged at n=4** |
| 2.4 | Time ordering in nested integrals | Eq. (16) verbatim: `θ_{τ_1^n} = 1 if τ_1 > τ_2 > ... > τ_n, 0 otherwise`. Convention Eq. (17): `∫_0^t dτ_1^n θ_{τ_1^n} = ∫_0^t dτ_1 ∫_0^{τ_1} dτ_2 ... ∫_0^{τ_{n−1}} dτ_n`. The vectors `τ_1^k` and `s_1^{n−k}` are **separately** time-ordered (no cross-ordering between τ's and s's), so each side carries its own descending chain. The two chains are stitched together by the `D̄` cumulants. | Repository convention: explicit nested-integral form, with `t ≥ s_1 ≥ s_2 ≥ ...` realised by descending grid loops in `cbg.tcl_recursion`. | Identity, after recognising that the repository's "s, u" labels at n=2 map to `s_1`, `τ_1` at `k=1`. | **Pinned** (first-pass fill-in 2026-05-12) |
| 2.5 | Dissipator extraction sign | Implicit in Companion via Eq. (43): the dissipator is the second `{...}` block of `L_n[X]`, so `L_n^dis = L_n − (Hamiltonian-commutator part)`. Equivalently `L_n^dis := L_n + i [K_n, ·]`. | `L_n^dis := L_n + i [K_n, ·]` in `cbg/tcl_recursion.py:L_n_dissipator_thermal_at_time`. | Identity. | **Pinned** (repository convention; matches Companion Eq. (43)) |
| 2.6 | Lambda-inversion subtraction structure | **Companion uses Case B (algebraically equivalent but bookkept differently).** Sec. II.C, Eq. (20) verbatim: `L_n = (−i)^n ∑_{q=0}^{n−1} (−1)^q ∑_{(m_0+...+m_q=n)} ∑_{k_0=0}^{m_0} ... ∑_{k_q=0}^{m_q} μ̇^{k_0}_{m_0} μ^{k_1}_{m_1} ... μ^{k_q}_{m_q}`. This is the `̇Φ_t ∘ Φ_t^{−1}` expansion in λ. After reorganisation into Eq. (23) and the cumulant recursion Eq. (27), the same subtraction structure that the repository writes as `L_4 = ∂_t Λ_4 − L_2 ∘ Λ_2` is absorbed into the `D̄(τ_1^k, s_1^{n−k})` generalized cumulants. | Repository writes `L_4 = ∂_t Λ_4 − L_2 ∘ Λ_2`. | **Case B.** Identity at the operator level; the algebraic reconciliation is recorded in §5 below. The repository may continue to bookkeep via `Λ_n` provided every term that the Companion's `D̄` recursion subtracts is also subtracted by the `Λ_n` route; the §5 reconciliation block enumerates the matching. | First-pass-Pinned-as-Case-B; **steward to confirm the §5 reconciliation block is complete** |
| 2.7 | Hermiticity / Hermitian-adjoint conventions | Sec. II.A assumes `A† = A`, `B† = B` ("for simplicity and clarity. However, the calculations can be easily extended to a more general interaction of the form `λ ∑_i A_i,t ⊗ B_i,t`"). Eq. (18) gives the cumulant identity `D*(τ_1^k, s_1^{n−k}) = D(s_1^{n−k}, τ_1^k)`. Hermiticity preservation of the generator: Eq. (33). | Repository carries `A = A†`, `B = B†` as a precondition; Hermiticity-of-omega gate enforced in the off-diagonal pseudo-Kraus runner (cf. memory). | Identity for the `A`, `B` Hermiticity precondition. The cumulant identity Eq. (18) is the §4.4 input to the Hermiticity check on `K_n`. | **Pinned** (first-pass fill-in 2026-05-12) |
| 2.8 | Ordering of bath operators in 4-point correlator (Wick contractions) | **Sec. IV does NOT explicitly write Wick's theorem for the 4-point bath correlator.** Sec. IV.D computes the `n = 4` cumulants (Eqs. 69–73) using the recursion Eq. (27), **not** an explicit Wick split. The 4-point bath quantities `D(τ_1^4)`, `D(τ_1^3, s_1)`, `D(τ_1^2, s_1^2)`, `D(τ_1, s_1^3)`, `D(s_1^4)` are treated as **given inputs** (n-point environmental correlators with the time ordering inherited from Eq. (15)). For a **thermal Gaussian** bath, Wick's theorem applies independently — but this is **not** a Companion equation; it is a model-level fact about the bath. | **n=4 repository routes: B.0 raw correlator is correct; B.1 standard-cumulant path must NOT be reused for Companion n=4.** `cbg.bath_correlations.n_point_ordered` (DG-4 Phase B.0) evaluates the raw thermal Gaussian 4-point correlator `D` by Wick factorisation into the existing two-point `C(t_i, t_j)` with the three bosonic pairings at `+1` coefficient (see `tests/test_bath_correlations.py:test_n_point_ordered_thermal_n4_wick_all_left`). The flattening convention `times = tau_args + reversed(s_args)` matches Companion Eq. (15)'s left-then-right operator ordering. However, `cbg.cumulants._joint_cumulant_from_raw_moments` (B.1) computes standard statistical cumulants via set partitions, which vanish for thermal Gaussian at n ≥ 3; the Companion's `D̄` at n=4 is **not** the standard statistical cumulant. Companion Eqs. (69)–(73) use `Ḋ` (time-derivative with boundary delta, Eq. 22) and explicit subtractions of lower-order raw correlators, giving non-zero `D̄` even for Gaussian baths. | **Conversion rule: repository-side Wick input is correct; Companion-side `D̄` recursion is distinct from the repository's standard-cumulant path.** Phase B must implement Eqs. (69)–(73) directly, reusing `n_point_ordered` for the raw `D` leaves but **not** reusing `_joint_cumulant_from_raw_moments` for the n=4 `D̄`. The explicit subtraction formulas encode the boundary-time delta structure (`Ḋ`) that the standard set-partition cumulant formula omits. The θ-aware procedural rule in §4.4 governs how the raw 4-point and disconnected subtractions are combined inside their distinct θ-windows. | **Draft-complete** (2026-05-12). Repository Phase B.0 raw-correlator path is the correct Wick input. Phase B must implement Companion Eqs. (69)–(73) explicitly; the B.1 standard-cumulant path gives zero for n=4 thermal Gaussian and is not equivalent to the Companion's `Ḋ`-based generalized cumulant. Steward must verify the flattening convention and the explicit-formula implementation on a small test grid before Phase B code lands. |

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
| `λ` | Coupling parameter for the interaction Hamiltonian `H_t = H_{S,t} + H_{E,t} + λ A_t^S ⊗ B_t^S` (Eq. 1). | `coupling_strength` / `α` (Path B sweep variable; `α²` in D1 v0.1.2 fixture) | `benchmarks/...` and `cbg/` (implicit via per-order scaling) | Repository scales `r_4(α²) = α² · ⟨‖L_4^dis‖⟩_t / ⟨‖L_2^dis‖⟩_t`. The Companion `λ`-power expansion and the repository `α`-power expansion are the same series. |
| `A` (= `A_t` in interaction picture) | System-side coupling operator on Hilbert space `H_S`. Hermitian (`A† = A`) by Sec. II.A simplifying assumption. | `coupling_operator` (and `A` locally) | `models/spin_boson.py`; `cbg/tcl_recursion.py:L_2_apply` | Existing. |
| `A(t_1^m)` = `A_{t_1} · A_{t_2} · ... · A_{t_m}` | Product of interaction-picture coupling operators at descending times (Eq. 10). | Pre-computed `A_I_array[s_idx]` chain | `cbg.tcl_recursion.interaction_picture` (single time); chain product is **new for n ≥ 3**. | Eq. (11) defines the reversed-order product `A†(t_1^m) = A_{t_m} · ... · A_{t_1}`. |
| `A^{L/R}(t_1^k)[·]` | Left/right superop composition over k times (Eq. 8). | Left action `A @ X`, right action `X @ A` | `cbg/tcl_recursion.py:L_2_apply` (n=2) | Already pinned by §2.2. |
| `B`, `B_t` | Bath-side coupling operator, Hermitian (`B† = B`). Sec. II.A. | `bath_coupling_operator` / implicit (only correlators enter the code) | `cbg/bath_correlations.py` | The repository never instantiates `B` explicitly; only its correlators `⟨B(t)B(s)⟩` (n=2) enter via spectral density. |
| `D(τ_1^k, s_1^{n−k})` | Raw n-point bath correlator with time ordering, Eq. (15). For thermal Gaussian: zero unless `n` is even and the operators pair up via Wick. | (none — raw, never computed alone in the repo) | conceptually a precondition input | The repo's `cbg.cumulants.D_bar_2` is the *connected* (= cumulant) two-point, i.e. it already implements the n=2 case of Eq. (27). |
| `D̄(τ_1^k, s_1^{n−k})` | Generalized (connected) cumulant of order n, defined by Eqs. (24)/(27). Eq. (17): for thermal Gaussian (`⟨B⟩ = 0`), `D̄(τ_1^k, s_1^{n−k}) = Ḋ(τ_1^k, s_1^{n−k})` at `n = 2, 3` (Sec. IV.D opening paragraph). | `D_bar_2` at n=2; **new at n=4** | `cbg.cumulants.D_bar_2`; new `D_bar_4_thermal_*` helpers to be added in Phase B | At n=4 the cumulants Eqs. (69)–(73) introduce **subtractor** terms `−Ḋ(τ_1^2) D(τ_3^4)` etc. — these are the analogue of the `Λ_2`-inversion correction in the repository's `Λ`-bookkeeping. |
| `Ḋ(τ_1^k, s_1^{n−k})` | Time derivative of the raw correlator: `Ḋ(τ_1^k, s_1^{n−k}) = D(τ_1^k, s_1^{n−k}) (δ_{τ_1,t} + δ_{s_1,t})` (Eq. 22). | (implicit — built into the cumulant-evaluation pipeline) | `cbg.cumulants` | The `δ` is the boundary-time pin: only the **largest** time in each chain (`τ_1` or `s_1`) carries the derivative. |
| `θ_{τ_1^n}`, `θ_{s_1^{n−k}}` | Discrete time-ordering indicators (Eq. 16). | Implicit nested-loop ordering in the repo. | `cbg.tcl_recursion` integral loops | Already pinned by §2.4. |
| `μ_n[ρ_S]`, `μ_n^k[ρ_S]` | Taylor coefficient of the reduced dynamical map (Eqs. 6, 13). | (not directly used) | — | Intermediate; the `L_n` formula Eq. (28) bypasses `μ_n` once `D̄` is in hand. |
| `Λ_n` (repository symbol, **not** Companion) | The propagator inversion subtractor implicit in `L_t = ̇Φ_t ∘ Φ_t^{−1}`. | `Lambda_2` (existing), `Lambda_4` (new) | `cbg.tcl_recursion` | The Companion paper does **not** name `Λ_n`; the repository carries `Λ_n` as bookkeeping. See §5 reconciliation. |
| `L_n[X]` | n-th order generator term (Eq. 28). | `L_n_thermal_at_time(n, ...)` | `cbg.tcl_recursion.L_n_thermal_at_time` | Existing for n ∈ {0,1,2,3}; n=4 deferred. |
| `L_n^k` | Sub-term of `L_n` with `k` left-acting operators (Eq. 23). | (private partition) | — | Useful for the parity decomposition at the `K_n` level (Eqs. 48–49). |
| `K(t) = ∑_n λ^n K_n` | Effective Hamiltonian, perturbative expansion (Eq. 44). | `K_total_thermal_on_grid` | `cbg.tcl_recursion.K_total_thermal_on_grid` | Existing. |
| `K_n` | n-th order contribution to the effective Hamiltonian (Eq. 45). | `K_n_thermal_on_grid(n, ...)` | `cbg.tcl_recursion.K_n_thermal_on_grid` | Existing for n ∈ {0,1,2,3}; **K_4 is the next mechanically-unblocked piece** once L_4 is available. |
| `K_n^k` | Partial contribution to `K_n` with k left-acting A's, Eq. (46). | (private partition for `K_4` if used) | — | Eq. (47) recombines: `K_n = −(+i)^n/(2i) ∑_k [K_n^k − (−)^n H.c.]`. |
| `𝔸(τ_1^k, s_1^{n−k}) := ⟨A(s_1^{n−k})†⟩_{1/d} A(τ_1^k)` | Trace-shifted operator product entering the **K_n master formula** Eq. (45)/(46). `⟨·⟩_{1/d}` denotes the maximally-mixed-state average, i.e. `⟨X⟩_{1/d} := Tr(X)/d`. | Helper (proposed) `_A_block_with_traced_right` | new in `cbg.tcl_recursion` (Phase B) | The `⟨A(s_1^{n−k})†⟩_{1/d}` factor is a **scalar** (trace over the system-dim Hilbert space); `A(τ_1^k)` is the operator chain. For trace-less `A` (the standard σ_z / σ_x cases) every chain of **odd** length traces to zero; this is the structural lever behind the spin-system parity result of Sec. III.C / Letter App. D. |
| `Ā(τ_1^k)` := `A(τ_1^k) − ⟨A(τ_1^k)⟩_{1/d} 𝟙` | Trace-less projection of the operator chain (defined just below Eq. 43). | (proposed) `_A_traceless` | new in `cbg.tcl_recursion` (Phase B) | Enters the **dissipator** Eq. (43); ensures the Lindblad jump operators are traceless ("minimal dissipation" principle). |
| `K_n^S(t)` | Schrödinger-picture effective Hamiltonian contribution at order n. Sec. IV.A: `K_1^S(t) = ⟨B_t⟩ A`. | `K_n_schrodinger_*` (does not exist) | — | The repository currently exposes the **interaction-picture** `K_n`. The Schrödinger-picture rotation `K_n^S = U(t) K_n U†(t)` is a trivial post-processing if needed. |
| `f(t, t_1, t_2)`, `g(t, t_1, t_2)` | Third-order bath-correlator coefficients (Eqs. 65–66). | (n=3 returns zero for thermal Gaussian) | — | Vanish identically for thermal Gaussian (all odd cumulants are zero). |
| `f̄(t, t_1, t_2, t_3)`, `ḡ(t, t_1, t_2, t_3)` | Fourth-order bath coefficients (Eqs. 75–76). | (new) `_K4_bath_coeff_f`, `_K4_bath_coeff_g` | new in `cbg.tcl_recursion` (Phase B) | Built from the 4-point bath cumulants under thermal Gaussian Wick (see §4.4 and §2.8). |
| `X(t, t_1, t_2)`, `Y(t, t_1, t_2)`; `X̄(...)`, `Ȳ(...)` | System-operator structures (Eqs. 67–68, 77–78). | (new for n=4) | new in `cbg.tcl_recursion` (Phase B) | The structure `A_t A_{t_1} A_{t_2} A_{t_3} − ⟨A_t A_{t_1} A_{t_2} A_{t_3}⟩_{1/d}` is **not** a single nested commutator — this is the structural difference that defeated the rejected single-commutator candidate (see §6). |
| `H.c.` | Hermitian conjugate of the preceding expression. | `.conj().T` post-processing | — | Pinned. |

> **Fill instruction.** This table is complete for the Sec. IV symbols up
> to fourth order (`K_4` in Eq. 74). If Phase B introduces additional
> private helpers, add rows here rather than introducing new shorthand
> in code comments.

## 4. Equation transcription slots

### 4.1 Master expression for `K_n` (Eq. 45, Sec. III.C) and for `L_n[X]` (Eq. 28, Sec. II.C)

> **Important orientation note.** The Companion paper does **not** present
> a single closed-form "`L_4`" formula. Section IV.D computes the
> fourth-order **K_4** contribution (Eq. 74), with the fourth-order
> generalized cumulants `D̄` listed as Eqs. (69)–(73). The full `L_4[X]`
> follows from these `D̄`s inserted into the universal **n-th-order**
> formula Eq. (28) (operator form) or Eq. (43) (canonical Lindblad form).
> The transcription below records both: the universal `L_n[X]` formula
> (which specialises to `L_4[X]` by setting `n = 4`) and the four
> specialised fourth-order cumulants.

**Companion Eq. (28) — universal n-th-order operator form (Sec. II.C):**

```math
\mathcal{L}_n[X]
= (i)^n \sum_{k=0}^{n} (-)^k
  \int_0^t d\boldsymbol{\tau}_1^k \, d\boldsymbol{s}_1^{n-k}
  \; \bar{\mathcal{D}}(\boldsymbol{\tau}_1^k, \boldsymbol{s}_1^{n-k})
  \; A(\boldsymbol{\tau}_1^k) \, X \, A^\dagger(\boldsymbol{s}_1^{n-k})
\tag{28}
```

with `A(τ_1^k) = A_{τ_1} A_{τ_2} ... A_{τ_k}` (Eq. 10) and
`A†(s_1^{n−k}) = A_{s_{n−k}} A_{s_{n−k−1}} ... A_{s_1}` (Eq. 11) —
note the **reversed time order** in the right-acting product, induced
by the Hermitian conjugate sign chain in Eqs. (8)–(11).

**Companion Eq. (43) — canonical Lindblad form (Sec. III.B):**

```math
\mathcal{L}_n[X]
= \sum_{k=0}^{n} (-)^k \int_0^t d\boldsymbol{\tau}_1^k \, d\boldsymbol{s}_1^{n-k}
  \Bigg\{
    -i \Big[
      \operatorname{Im}\!\big\{(i)^n \bar{\mathcal{D}}(\boldsymbol{\tau}_1^k, \boldsymbol{s}_1^{n-k})\big\}
      \big\langle A(\boldsymbol{\tau}_1^k)\big\rangle_{1/d}
      A^\dagger(\boldsymbol{s}_1^{n-k}),\; X
    \Big] \\
   \quad + i^n\, \bar{\mathcal{D}}(\boldsymbol{\tau}_1^k, \boldsymbol{s}_1^{n-k})
     \Big(
       \bar{A}(\boldsymbol{\tau}_1^k)\, X\, \bar{A}^\dagger(\boldsymbol{s}_1^{n-k})
       - \tfrac{1}{2}\big\{\bar{A}^\dagger(\boldsymbol{s}_1^{n-k}) \bar{A}(\boldsymbol{\tau}_1^k),\; X\big\}
     \Big)
  \Bigg\}\;,
\tag{43}
```

with `Ā := A − ⟨A⟩_{1/d} 𝟙` (defined just below Eq. 43).

**Companion Eq. (45) — `K_n` master formula:**

```math
K_n = -\frac{(+i)^n}{2i} \sum_{k=0}^{n} (-)^k
  \int_0^t d\boldsymbol{\tau}_1^k \, d\boldsymbol{s}_1^{n-k}
  \; \bar{\mathcal{D}}(\boldsymbol{\tau}_1^k, \boldsymbol{s}_1^{n-k})
  \; \mathbb{A}(\boldsymbol{\tau}_1^k, \boldsymbol{s}_1^{n-k})
  - (-)^n \,\mathrm{H.c.}
\tag{45}
```

where the operator block is

```math
\mathbb{A}(\boldsymbol{\tau}_1^k, \boldsymbol{s}_1^{n-k})
:= \big\langle A(\boldsymbol{s}_1^{n-k})^\dagger \big\rangle_{1/d} \, A(\boldsymbol{\tau}_1^k)
```

(see Eq. 45 setup, "for later convenience, we have defined the
operator").

**Companion Eqs. (47)–(49) — parity decomposition of `K_n`:**

```math
K_n = -\frac{(+i)^n}{2i} \sum_{k=0}^{n} \big[K_n^k - (-)^n \mathrm{H.c.}\big],
\tag{47}
```

```math
K_{2m} = (-1)^{m+1} \sum_{k=0}^{2m} \operatorname{Im}\!\big[K_{2m}^k\big],
\tag{48}
```

```math
K_{2m+1} = (-1)^{m+1} \sum_{k=0}^{2m+1} \operatorname{Re}\!\big[K_{2m+1}^k\big],
\tag{49}
```

with the partial block

```math
K_n^k := (-)^k \int_0^t d\boldsymbol{\tau}_1^k \, d\boldsymbol{s}_1^{n-k}
  \; \bar{\mathcal{D}}(\boldsymbol{\tau}_1^k, \boldsymbol{s}_1^{n-k})
  \; \mathbb{A}(\boldsymbol{\tau}_1^k, \boldsymbol{s}_1^{n-k}).
\tag{46}
```

**Companion equation anchors:** Eqs. (28), (43), (45), (46), (47), (48),
(49) of *Phys. Rev. A* **112**, 052222 (2025).

### 4.2 Fourth-order generalized cumulants (Eqs. 69–73, Sec. IV.D)

Sec. IV.D opens by assuming `⟨B_t⟩ = 0` (so first-order disappears and
`D̄(τ_1^k, s_1^{n−k}) = Ḋ(τ_1^k, s_1^{n−k})` at `n = 2, 3`). The
fourth-order cumulants from the recursion Eq. (27) are then:

```math
\bar{\mathcal{D}}(\boldsymbol{s}_1^4)
= \dot{D}(\boldsymbol{s}_1^4) - \dot{D}(\boldsymbol{s}_1^2)\,D(\boldsymbol{s}_3^4),
\tag{69}
```

```math
\bar{\mathcal{D}}(\tau_1, \boldsymbol{s}_1^3)
= \dot{D}(\tau_1, \boldsymbol{s}_1^3)
  - \dot{D}(\tau_1, s_1)\,D(\boldsymbol{s}_2^3)
  - \dot{D}(\boldsymbol{s}_1^2)\,D(\tau_1, s_3),
\tag{70}
```

```math
\bar{\mathcal{D}}(\boldsymbol{\tau}_1^2, \boldsymbol{s}_1^2)
= \dot{D}(\boldsymbol{\tau}_1^2, \boldsymbol{s}_1^2)
  - \dot{D}(\tau_1, s_1)\,D(\tau_2, s_2)
  - \dot{D}(\boldsymbol{s}_1^2)\,D(\boldsymbol{\tau}_1^2)
  - \dot{D}(\boldsymbol{\tau}_1^2)\,D(\boldsymbol{s}_1^2),
\tag{71}
```

```math
\bar{\mathcal{D}}(\boldsymbol{\tau}_1^3, s_1)
= \dot{D}(\boldsymbol{\tau}_1^3, s_1)
  - \dot{D}(\tau_1, s_1)\,D(\boldsymbol{\tau}_2^3)
  - \dot{D}(\boldsymbol{\tau}_1^2)\,D(\tau_3, s_1),
\tag{72}
```

```math
\bar{\mathcal{D}}(\boldsymbol{\tau}_1^4)
= \dot{D}(\boldsymbol{\tau}_1^4) - \dot{D}(\boldsymbol{\tau}_1^2)\,D(\boldsymbol{\tau}_3^4).
\tag{73}
```

**These five cumulants are the n=4 inputs to Eq. (28) / Eq. (43) / Eq. (45).**
Setting `n = 4` in Eq. (28) and summing `k = 0, 1, 2, 3, 4` reads each
cumulant against its `A(τ_1^k) X A†(s_1^{n−k})` block. The repository's
Phase B implementation must thread all five `D̄` evaluators through the
n=4 routes.

**Companion equation anchors:** Eqs. (69), (70), (71), (72), (73).

### 4.3 Fourth-order `K_4` Hamiltonian contribution (Eq. 74, Sec. IV.D)

Inserting Eqs. (69)–(73) into Eq. (45) at `n = 4` gives

```math
K_4 = -\frac{1}{2i}
  \int_0^t dt_1 \, dt_2 \, dt_3
  \Big[\;
    \bar{f}(t, t_1, t_2, t_3)\,\bar{X}(t, t_1, t_2, t_3)
    - \bar{g}(t, t_1, t_2, t_3)\,\bar{Y}(t, t_1, t_2, t_3)
    - \mathrm{H.c.}
  \;\Big],
\tag{74}
```

with the bath coefficients

```math
\bar{f}(t, t_1, t_2, t_3)
= \big\langle B_t B_{t_1} B_{t_2} B_{t_3}\big\rangle \theta_{t_1^3}
  - \big\langle B_t B_{t_1}\big\rangle\big\langle B_{t_2} B_{t_3}\big\rangle \theta_{t_2^3},
\tag{75}
```

```math
\bar{g}(t, t_1, t_2, t_3)
= \big\langle B_{t_1} B_t B_{t_2} B_{t_3}\big\rangle \theta_{t_2^3}
  - \big\langle B_{t_1} B_t\big\rangle\big\langle B_{t_2} B_{t_3}\big\rangle \theta_{t_2^3}
  - \big\langle B_t B_{t_2}\big\rangle\big\langle B_{t_1} B_{t_3}\big\rangle,
\tag{76}
```

and the system-operator blocks

```math
\bar{X}(t, t_1, t_2, t_3)
= A_t A_{t_1} A_{t_2} A_{t_3}
  - \big\langle A_t A_{t_1} A_{t_2} A_{t_3}\big\rangle_{1/d}
  - A_{t_1} A_{t_2} A_{t_3}\big\langle A_t\big\rangle_{1/d}
  + A_t \big\langle A_{t_1} A_{t_2} A_{t_3}\big\rangle_{1/d},
\tag{77}
```

```math
\bar{Y}(t, t_1, t_2, t_3)
= A_t A_{t_2} A_{t_3}\big\langle A_{t_1}\big\rangle_{1/d}
  - A_{t_1}\big\langle A_t A_{t_2} A_{t_3}\big\rangle_{1/d}.
\tag{78}
```

**Companion equation anchors:** Eqs. (74), (75), (76), (77), (78).

> **Sec. IV.D simplification note (verbatim quote, post-Eq. 78):**
> "The latter will slightly simplify under the assumption that `Tr A = 0`.
> The calculation of the coefficients (69)–(73) was made significantly
> easier through the use of the recursive formula, in particular because
> the simplification of lower-order coefficients can be quickly carried
> through to higher orders."
>
> Repository D1 fixtures use `A = σ_z` (`Tr A = 0`) and `A = σ_x`
> (`Tr A = 0`); the `Tr A = 0` simplification applies. Implementation
> may zero out the `⟨A_t⟩_{1/d}` factors at the entry point.

### 4.4 4-point bath correlator structure (model-side assumption, **not** Sec. IV)

> **Critical sign-convention surface — see §2.8.** The Companion Sec. IV
> does **not** Wick-factorize the raw 4-point correlator
> `⟨B_{t_1} B_{t_2} B_{t_3} B_{t_4}⟩` into pairs. Eqs. (75)–(76) carry
> the raw 4-point correlator `⟨B B B B⟩` and the disconnected 2×2
> product `⟨B B⟩⟨B B⟩` as **separate** terms — that subtraction is
> precisely what makes `D̄_n` *connected*.
>
> For a **thermal Gaussian** bath the additional model-level fact is
> Wick's theorem:

```math
\big\langle B_{t_1} B_{t_2} B_{t_3} B_{t_4}\big\rangle_{\text{thermal Gaussian}}
=
  \big\langle B_{t_1} B_{t_2}\big\rangle \big\langle B_{t_3} B_{t_4}\big\rangle
+ \big\langle B_{t_1} B_{t_3}\big\rangle \big\langle B_{t_2} B_{t_4}\big\rangle
+ \big\langle B_{t_1} B_{t_4}\big\rangle \big\langle B_{t_2} B_{t_3}\big\rangle.
\tag{not-in-Companion-Sec-IV}
```

> This is the **bosonic** 4-point Wick split (all three pairings with
> `+1` coefficient). It is the input the repository must feed into
> Eqs. (75)–(76). **The Companion paper does not invoke Wick here**;
> the repository adds Wick as a separate, model-side thermal-Gaussian
> assumption. The Sec. II.A statement of initial factorization
> (`ρ_{SE}(0) = ρ_S ⊗ ρ_E`) is **not** sufficient to imply Wick — Wick is
> a property of the bath state's Gaussianity, separate from initial
> system-bath factorization.
>
> Steward must confirm before code lands:
> 1. **No Companion equation in Sec. IV is being treated as if it
>    implements the Wick split.** The Wick split is a separate, model-
>    side identity belonging at the `cbg.bath_correlations` boundary,
>    not inside `cbg.tcl_recursion`.
> 2. **All three pairings have `+1` coefficient** (bosonic). If the
>    repository ever generalises to a fermionic bath, the third
>    pairing acquires a sign.
> 3. **Disconnected subtraction — θ-aware implementation rule:**
>    Eqs. (75) and (76) carry both a raw 4-point term and one or more
>    disconnected `⟨B B⟩ ⟨B B⟩` subtractions, with **distinct θ-window
>    factors on the connected vs. disconnected pieces** (e.g. `θ_{t_1^3}`
>    on the raw 4-point in Eq. (75) vs. `θ_{t_2^3}` on its disconnected
>    subtraction; analogous mismatches in Eq. (76)). This θ-window
>    mismatch makes it **incorrect** to characterise the post-Wick
>    structure of `f̄` or `ḡ` as a simple count of surviving pairings
>    over a single time region — the surviving and subtracted pieces
>    live on different time-ordering sub-regions.
>
>    **Safe implementation rule for Phase B:**
>
>    1. Apply Wick's theorem to the **raw 4-point term only** (the first
>       term in Eq. (75) and the first term in Eq. (76)), writing it as
>       the sum of three two-point pairings, **inside its own θ-window**.
>    2. Keep the disconnected `⟨B B⟩ ⟨B B⟩` subtraction terms of
>       Eqs. (75)/(76) **exactly as written**, **with their own
>       θ-windows preserved**.
>    3. Do **not** algebraically pre-cancel pairings across the
>       connected/disconnected split; the θ-windows generally do not
>       permit such cancellation pointwise.
>    4. After integration over the time variables, equivalent
>       simplifications may emerge, but they must be derived from the
>       integrated expression, not assumed term-by-term.
>
>    **What this rule explicitly forbids:** a uniform "two-out-of-three
>    pairings survive" or "one-out-of-three pairings survives"
>    simplification at the integrand level. Both `f̄` and `ḡ` carry
>    integrand-level structure that depends on the relative θ-region of
>    the four time arguments; the count of "surviving pairings" only
>    becomes meaningful after the integration carves out a definite
>    time region.
>
>    **What the steward must record before code lands:** the fully
>    θ-aware expanded formulas for `f̄` and `ḡ` after Wick is applied to
>    the raw 4-point — one expression per θ-region needed. If the
>    repository prefers, equivalently, to keep `f̄` and `ḡ` in the
>    literal Eq. (75)/(76) form (raw 4-point + disconnected subtraction,
>    each with its own θ) and apply Wick only at the integrand-evaluator
>    boundary, that is also acceptable and is the lower-risk
>    implementation path.

## 5. Lambda-inversion subtraction — repository form

The repository implements

```text
L_4 := d_t Lambda_4 — L_2 Lambda_2
```

with the right-hand side evaluated at time `t`. The Companion paper does
not write this identity in this notation; the steward classification is:

- [ ] **Case A:** Companion states the subtraction identity directly.
- [x] **Case B:** Companion uses a different but algebraically equivalent
      form. Citations: Eq. (20) (the `L_n = ̇Φ_t ∘ Φ_t^{−1}` Taylor expansion
      in `λ`), Eq. (27) (the recursive cumulant subtraction). Reconciliation
      algebra recorded below.
- [ ] **Case C:** Companion form differs and is not obviously equivalent.

**Case B reconciliation.** The repository's `Λ_n` bookkeeping and the
Companion's generalized-cumulant recursion express the same operator
identity. The bridging argument below is **schematic** — combinatorial
ranges and signs are sketched for orientation, not source-exact in
Companion notation. The source-exact statements are Companion Eq. (20)
verbatim and the recursion Eq. (27) verbatim (transcribed in §4); the
recommendation at the end of this section is to bypass this bridge in
implementation by evaluating Eqs. (69)–(73) directly.

The dynamical map's expansion `Φ_t = 𝟙 + ∑_{n≥1} (−iλ)^n μ_n` (Eq. 5)
inverts as a formal series

```text
[schematic]
Φ_t^{-1} = 𝟙 + ∑_{q≥1} (−1)^q [(Φ_t − 𝟙)]^q
        = 𝟙 + ∑_{q≥1} (−1)^q ∑_{m_1,...,m_q ≥ 1} (−iλ)^{m_1+...+m_q}
              μ_{m_1} μ_{m_2} ... μ_{m_q}.
```

Then `L_t = ̇Φ_t ∘ Φ_t^{−1}` gives, at order `λ^n`, schematically,

```text
[schematic — Companion Eq. (20) is the source-exact form]
L_n = (−i)^n ∑_{q=0}^{n−1} (−1)^q
        ∑_{m_0+m_1+...+m_q = n}
        μ̇_{m_0} μ_{m_1} ... μ_{m_q}.
```

Picking off the left-acting count `k` across each chain (Companion
Eq. 23) and collecting bath-correlator factors yields the cumulant
recursion Companion Eq. (27) verbatim:

```text
[Companion Eq. (27) verbatim]
D̄(τ_1^k, s_1^{n−k}) = Ḋ(τ_1^k, s_1^{n−k})
                      − ∑_{l=0}^{k} ∑_{r=0}^{n−k}
                         D̄(τ_1^l, s_1^r) · D(τ_{l+1}^k, s_{r+1}^{n−k}).
```

(Per Companion Eq. (26) "rule of notation," some terms in the double
sum drop out when one of `b_1 < a_1` or `b_2 < a_2`; see Eq. (26).
This drop-out structure must not be elided in implementation.)

Identifying (schematically) `Λ_n ↔ μ_n` and `∂_t Λ_n ↔ μ̇_n`, the
repository identity `L_4 = ∂_t Λ_4 − L_2 ∘ Λ_2` matches the `n = 4`
specialisation of Companion Eq. (20) **after** the lower-`n` `L`'s have
been re-expressed in `μ̇, μ` form.

For **thermal Gaussian** baths with `⟨B_t⟩ = 0`, all odd-order
contributions involving `μ̇_1`, `μ_1`, `μ_3`, `μ̇_3` vanish (Companion
Sec. IV.A; thermal-Gaussian zero-mean). The surviving fourth-order
contributions reduce to `μ̇_4` and `μ̇_2 μ_2` analogues, matching the
repository's `L_4 = ∂_t Λ_4 − L_2 ∘ Λ_2` under the same odd-vanishing.

**Conclusion (Case B).** The repository may continue to bookkeep via
`Λ_n` provided the n=4 implementation either (i) computes `μ̇_4` and
`μ̇_2 μ_2` directly and subtracts, or (ii) computes each `D̄` of
Eqs. (69)–(73) directly. Approaches (i) and (ii) are algebraically
identical for thermal Gaussian baths. Approach (ii) is paper-bearing
and self-validating against the Companion equation numbers; approach (i)
requires the steward to maintain the `Λ_n` ↔ `μ_n` translation table.

**Recommendation for Phase B.** Implement approach (ii) — directly
evaluate Eqs. (69)–(73) — to minimise the reconciliation surface.

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
beyond `L_2` vanish. The **Letter** (PRA 112, L050203 (2025)) documents
this explicitly: Letter Eq. (21) gives the exact second-order dephasing
TCL master equation

```math
\dot{\rho}_S(t) = -i\!\left[\tfrac{\omega}{2}\sigma_z,\, \rho_S(t)\right]
  + \gamma(t)\!\left[\sigma_z \rho_S(t) \sigma_z - \rho_S(t)\right],
\tag{Letter 21}
```

with the surrounding text noting that this is "already exact at second
order" (Letter cites Doll, Zueco, Wubs, Kohler, Hänggi, *Chem. Phys.*
2008). Hence no `L_n` for `n ≥ 3` contributes to the dephasing TCL
generator.

> **Citation correction note (2026-05-12 review pass).** An earlier draft
> cited "Companion Eq. (21)" for this fact. Companion Eq. (21) is the
> definition of `μ̇_n^k`, not a dephasing master equation. The
> authoritative anchor is Letter Eq. (21) above.

**Transcription check.** Inspect the transcribed master expression in
§4.1 and the fourth-order expression in §4.3. For `A = σ_z`:

1. **Interaction-picture operator chain is constant:** `[H_S, σ_z] = 0`
   (since `H_S = (ω/2) σ_z` in the standard convention), so
   `A_t = σ_z ∀ t`. The chain `A_t A_{t_1} A_{t_2} A_{t_3} = σ_z^4 = 𝟙`.

2. **Letter App. D / §4.1–4.3 specialisation:** From Letter Eq. (D1)
   (transcribed in `transcriptions/colla-breuer-gasbarri-2025_appendix-d_v0.0.1.md`
   Eq. (A.39)), `𝔸(τ_1^k, s_1^{n−k}) = ⟨σ_z^{n−k}⟩_{1/d} σ_z^k`. For
   `n = 4`:
   - `n` even, `k` even (`k ∈ {0, 2, 4}`): `𝔸 = ⟨σ_z^{4−k}⟩_{1/d} σ_z^k`
     equals `𝟙` (since `Tr(σ_z^{even})/2 = 1` and `σ_z^{even} = 𝟙`).
   - `n` even, `k` odd: `𝔸 = 0` (since `Tr(σ_z^{odd}) = 0`).
   So **only** `k ∈ {0, 2, 4}` contribute, and the contributions are
   proportional to the **identity** operator.

3. **`K_4` consequence:** A `K_n` proportional to `𝟙` is dynamically
   irrelevant — `[𝟙, ·] = 0`, so identity contributions to the
   Hamiltonian generate no evolution. Equivalently, the Hamiltonian
   gauge fixes `K_n` up to a multiple of `𝟙`; the "traceless"
   convention (Hayden–Sorce minimal-dissipation; Letter Eq. (4)–(6) +
   Companion Sec. III.A) simply chooses the representative
   `K_n − Tr(K_n)/d · 𝟙`. Either statement gives `K_4 = 0` (traceless
   part) for `A = σ_z`. **Letter App. D Eq. (A.39) is the explicit
   `n = 4` row.** Note: this argument is Hamiltonian-side; do **not**
   conflate it with Eq. (43)'s `Ā = A − ⟨A⟩_{1/d} 𝟙` trace-shift,
   which is the dissipator-side construction of traceless Lindblad
   jump operators.

4. **`L_4^dis` consequence:** Eq. (43) dissipator carries
   `Ā(τ_1^k) X Ā(s_1^{n−k})† − (1/2){...}`. With `Ā = σ_z − Tr(σ_z)/2 · 𝟙
   = σ_z` (already traceless), the dissipator structure persists; the
   `L_4` cancellation must come from the cumulant structure itself, not
   the trace shift. Specifically, in the dephasing spin-boson model
   (Eq. 20), all `L_n` for `n ≥ 3` vanish because the exact TCL
   generator is already second-order exact (Eq. 21). This is a model-
   level result that the analytic `L_4` must reproduce.

| Check | Result |
|---|---|
| All terms in §4.3 carry at least one outer commutator with `A`? | **Verified via Letter App. D Eq. (A.39):** for `A = σ_z`, every operator-block evaluation is proportional to `𝟙` (after `Tr σ_z = 0` accounting), hence drops out of `K_4`. The dissipator side (Eq. 43) inherits the `Ā = σ_z` traceless structure, but the `L_4` cancellation is a **bath-side** cancellation among the three Wick pairings in §4.4 combined with the cumulant subtractions of Eqs. (69)–(73). |
| Pairing structure of §4.4 preserves σ_z cancellation? | **First-pass argument:** For `A = σ_z`, the system-operator chain in Eq. (28) reduces to `σ_z^k X σ_z^{n−k}`, which has a closed-form action. The required `L_4 = 0` for the dephasing model is the structural test for the Wick + cumulant combination — equivalent to the bath kernel `f̄`-evaluated-on-the-anti-symmetric-time-region having the right cancellation. **Steward must verify this on the transcribed §4.3/§4.4 expressions before code lands.** |

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
> in §6, and verified the paper-level oracle conditions in §7. The
> controlling source identifier is the APS Version-of-Record DOI
> (`10.1103/9j8d-jxgd`), pinned in §0. The companion arXiv identifier is
> not used as a controlling identifier by this artifact; any arXiv anchor
> is informational only. This artifact is hereby promoted from
> `scaffold` to `released` state for Phase B consumption.
>
> Reviewer: _________________________  Date: ____________
>
> Version at sign-off: v0.1.0 (release state: released)
>
> **Pre-release condition reminder.** Before this block is countersigned,
> the §2 row 2.8 (Wick split) must be marked `Closed-by-steward` (or
> equivalent) and the §4.4 θ-aware implementation rule must have been
> read by the steward. The artifact's controlling source is the VoR DOI
> pinned in §0; no arXiv-version pinning is required for release.

## Appendix — change log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1.0 | 2026-05-11 | Scaffold drafted alongside `dg-4-work-plan_v0.1.5` freeze. All equation slots marked TBD-by-steward. | Council-3 (Guardian/Integrator/Architect) deliberation product |
| v0.1.0 | 2026-05-12 | First-pass transcription fill-in from the APS Version-of-Record PDF (filed locally under `scratch/sources/`, gitignored). Pinned source DOI `10.1103/9j8d-jxgd` and bibliographic block (§0). Filled §2 rows 2.1–2.5, 2.7 from Companion Sec. II.A, II.C, III.B (Pinned); pre-filled 2.6 as Case B with reconciliation in §5; left 2.8 explicitly Open (Wick split is model-side, not paper-side). Expanded §3 symbol map to cover every Sec. IV symbol used through Eq. (78). Transcribed verbatim into §4: Eqs. (28) [`L_n` operator form], (43) [canonical Lindblad], (45)–(49) [`K_n` master + parity], (69)–(73) [n=4 cumulants], (74)–(78) [`K_4`]. Recorded §5 Λ-inversion reconciliation (Case B; recommended Phase B approach = direct Eq. 69–73 evaluation). Strengthened §7.1 σ_z oracle with Letter App. D Eq. (A.39) specialisation. **Status: status remains `scaffold`/`in-progress-transcription`; steward sign-off in §10 still required.** | Local steward draft (U. Warring's working session); not yet countersigned. |
| v0.1.0 | 2026-05-12 | **§2.8 fill-in (Open → Draft-complete).** Steward populated row 2.8 with three substantive additions: (a) **Repository value** explicitly cites `cbg.bath_correlations.n_point_ordered` (B.0) as the correct Wick-input path with flattening convention `times = tau_args + reversed(s_args)` matching Companion Eq. (15)'s left-then-right ordering; (b) **Critical finding** that `cbg.cumulants._joint_cumulant_from_raw_moments` (B.1) computes standard statistical cumulants (vanishing for thermal Gaussian at n ≥ 3) and is **not** equivalent to the Companion's n=4 `D̄`, which is built from `Ḋ`'s boundary-time delta (Eq. 22) plus the explicit lower-order subtractions of Eq. (27)/(73); (c) **Conversion rule** that Phase B must implement Eqs. (69)–(73) directly, reusing `n_point_ordered` for the raw `D` leaves but **not** reusing `_joint_cumulant_from_raw_moments` for the n=4 `D̄`. The B.1 mismatch is evidenced by `tests/test_cumulants.py:test_D_bar_n4_thermal_vanishes` (B.1 returns ≈ 0 for the all-τ four-time tuple), whereas Companion Eq. (73) gives `D̄(τ_1^4) = [C(τ_1,τ_3) C(τ_2,τ_4) + C(τ_1,τ_4) C(τ_2,τ_3)] δ_{τ_1,t}` after the first Wick pairing cancels against the subtraction term — non-zero in general. Aligned the §0 sign-convention review pass row and the trailing artifact-summary footer to record the Draft-complete state. §10 sign-off remains Open. | Local steward §2.8 fill-in session. |
| v0.1.0 | 2026-05-12 | Steward review fix-pass #2 against the local VoR PDF (3 findings). **§4.4 disconnected-subtraction:** Removed the "2 survive for `f̄`, 1 for `ḡ`" pointwise count and replaced with a θ-aware procedural rule that keeps Eqs. (75)/(76) literal and applies Wick only to the raw 4-point term, inside its own θ-window, with the disconnected subtractions preserved as-written. Steward must record fully θ-aware expanded formulas (or use the literal-form route) before code lands. **§0 provenance:** Split the "Equation numbers transcribed" row into "verbatim-transcribed into §4" (Eqs. (27), (28), (43), (45)–(49), (69)–(78)) and "consulted / relevant but not verbatim-transcribed" (Eqs. (5)–(6), (8)–(11), (15)–(18), (20)–(26), (50)–(68)), to match the actual §4 contents. **§0 + §10 arXiv-pinning:** Made the VoR DOI `10.1103/9j8d-jxgd` the sole controlling source identifier; rewrote the §10 sign-off to drop the arXiv-version-pinned claim; aligned the frontmatter `source_arxiv_version` field to "not-used-as-controlling-identifier". Status unchanged. | Local steward fix-pass #2 after second VoR PDF spot-check review. |
| v0.1.0 | 2026-05-12 | Steward review fix-pass against the local VoR PDF (5 findings). **Item 1 (High):** Corrected §4.4 disconnected-subtraction note — the count of surviving Wick pairings under Eqs. (75)/(76) is **asymmetric**: 2 survive for `f̄` (one subtraction), 1 survives for `ḡ` (two subtractions). Removed the incorrect "two-out-of-three pairings survive" generalisation; flagged the `θ`-window mismatch between connected and disconnected pieces for steward re-derivation. *(Subsequently superseded by fix-pass #2, which replaced the pointwise count with a θ-aware procedural rule.)* **Item 2 (Medium):** Corrected §7.1 citation — the exact second-order dephasing TCL master equation is **Letter** Eq. (21), not Companion Eq. (21) (Companion Eq. (21) is the `μ̇_n^k` definition). Inline citation-correction note added. **Item 3 (Medium):** Re-attributed the §7.1 `K_4 = 0` mechanism — identity contributions to `K_n` are dynamically irrelevant (Hamiltonian gauge / traceless projection), distinct from Eq. (43)'s dissipator-side `Ā = A − ⟨A⟩_{1/d} 𝟙`. **Item 4 (Low):** Reworded §4.4 — Companion does **not** invoke Wick implicitly; initial system-bath factorization does not imply Wick. **Item 5 (Low):** Labelled the §5 displayed recursion as schematic and pointed to Companion Eq. (20)/(27) as the source-exact form; added the Companion Eq. (26) "rule of notation" drop-out caveat. **Status unchanged:** still `in-progress-transcription`; §2.8 still Open; §10 still uncountersigned. | Local steward fix-pass after VoR PDF spot-check review. |

---

*Transcription artifact version: v0.1.0 (in-progress-transcription;
first-pass fill-in 2026-05-12, fix-pass 2026-05-12, fix-pass #2
2026-05-12, §2.8 fill-in 2026-05-12). Drafted 2026-05-11 as the Phase A
artifact for `dg-4-work-plan_v0.1.5`. The 2026-05-12 first-pass populated
§0 bibliographic block from the APS Version-of-Record, filled §2 rows
where the paper is unambiguous (leaving row 2.8 explicitly Open as the
model-side Wick split), expanded §3 to a complete symbol table for
Sec. IV, transcribed Eqs. (28), (43), (45)–(49), (69)–(78) verbatim into
§4, recorded the Λ-inversion reconciliation as Case B in §5, and
strengthened the §7.1 σ_z oracle check. Fix-pass #1 corrected the §7.1
dephasing exactness citation to Letter Eq. (21) and recorded an
asymmetric pairing-count note in §4.4 that was subsequently superseded.
Fix-pass #2 replaced that §4.4 note with a θ-aware procedural rule
that forbids pointwise pairing-count simplifications, split the §0
provenance row to match actual §4 contents, and dropped the §10 arXiv-
version-pinned claim so the VoR DOI is the sole controlling source. The
§2.8 fill-in (steward, 2026-05-12) moved row 2.8 from Open to Draft-
complete, recording that `cbg.bath_correlations.n_point_ordered` (B.0)
is the correct Wick-input path and that
`cbg.cumulants._joint_cumulant_from_raw_moments` (B.1, standard
statistical cumulants) must **not** be reused for the Companion's
n=4 `D̄` because `D̄` carries `Ḋ`'s boundary-time delta plus Eq. (27)'s
explicit lower-order subtractions, which the standard set-partition
cumulant omits. The §10 steward sign-off remains Open pending grid-
verification of the §2.8 conversion rule and of the §4.4 θ-aware
procedural rule; Phase B implementation must not begin until §10 is
countersigned. CC-BY-4.0 (see ../LICENSE-docs).*

---
artefact: Primary-source transcription
source_paper: Colla, Breuer, Gasbarri — "Unveiling coherent dynamics in non-Markovian open quantum systems: exact expression and recursive perturbation expansion"
source_journal: "Phys. Rev. A 112, L050203 (2025)"
source_doi: "10.1103/n5nl-gn1y"
source_section: End matter, "Contributions to K in spin systems" (Ledger/briefing route name: Appendix D)
source_pages: "Phys. Rev. A article pages L050203-7–L050203-8; arXiv PDF pp. 7–8"
relates_to: CL-2026-005 v0.4 Entries 3.B.3 + 4.B.2; subsidiary briefing v0.2.0 §3.5
authorises: none directly; gates Act 2 selection before any B4-conv-<X>_v0.1.0 card
prepared_by: Local steward (U. Warring)
date: 2026-05-04
status: POPULATED — underdetermined; awaiting Act 2 §4.3 handling selection over candidate set §3.1–§3.4
precedent: transcriptions/hayden-sorce-2022_pseudokraus_v0.1.1.md (gated B1 v0.1.0 / B2 v0.1.0)
---

# Endorsement Marker

This is a **primary-source transcription**, not a coastline, not a sail, and not a Ledger entry. It records the verbatim notation of the Letter source material routed by CL-2026-005 as "Appendix D" (Colla, Breuer, Gasbarri) as faithfully as the typesetting of this repository permits, with explicit `[steward note]` blocks where verbatim transcription is impossible (figures, embedded LaTeX with non-standard macros, etc.). It carries no veto power and asserts no novel claim. The transcription is the input to a future Act 2 Council-3 ADM-EC deliberation; it does not itself perform that deliberation.

Any disagreement between this transcription and the Letter as published is resolved in favour of the Letter; this file is a working copy for repository-internal use only and is not redistributed.

# Steward conflict notice

The transcribing steward (U. Warring) is a co-author on Colla, Hasse, Palani, Schaetz, Breuer, Warring, *Nat. Commun.* 16, 2502 (2025), the trapped-ion experimental paper cited as the empirical anchor of CL-2026-005 v0.4 Entry 6, and is not a co-author of the Letter being transcribed here. The Letter authors (Colla, Breuer, Gasbarri) are however the same theory team the steward collaborates with on the open-quantum-systems track. The conflict is therefore standing-Entry-6-tier, not the sharper Entry-3.B.3 / 4.B.2 convention-selection tier.

For the *transcription act itself* the conflict is structurally inert: transcription is a non-discretionary copying operation; the steward is not selecting, weighting, or interpreting. Any interpretive notes are tagged `[steward note]` and are explicitly out of scope for the transcription's authority. The conflict re-fires at Act 2 because the classification below is "underdetermined" — see §6 routing.

# 1. Bibliographic record

- **Authors.** Colla, A.; Breuer, H.-P.; Gasbarri, G.
- **Title.** _Unveiling coherent dynamics in non-Markovian open quantum systems: exact expression and recursive perturbation expansion_
- **Reference.** _Phys. Rev. A_ **112**, L050203 (2025).
- **DOI.** `10.1103/n5nl-gn1y`
- **arXiv.** `2506.04097v1` (`arXiv:2506.04097 [quant-ph]`, submitted 2025-06-04)
- **Source version used.** arXiv TeX source `effectiveHamiltonian.tex` from `2506.04097v1`, cross-checked against the arXiv PDF rendered from that source. The bibliographic reference above uses the APS Version-of-Record metadata.
- **Source license.** CC-BY-4.0, per arXiv license link and APS/Crossref Version-of-Record metadata.
- **Appendix-D-routed pages.** Phys. Rev. A article pages L050203-7–L050203-8; arXiv PDF pp. 7–8.
- **Equation numbering.** The arXiv/APS source used here labels the end-matter equations as Eq. (A.39)–Eq. (A.45), not Eq. (D.N). CL-2026-005 and the subsidiary briefing call this material "Appendix D"; this file preserves the source equation labels and records the route-name mismatch explicitly.

# 2. Verbatim transcription of Appendix D

`[steward note: source-section naming]` The Letter source available as arXiv `2506.04097v1` does not contain a section literally titled "Appendix D". After `\appendix*` it uses the unnumbered section title "end matter"; the relevant Ledger-routed material is the subsection "Contributions to K in spin systems", with subsubsections "Pure decoherence" and "Unbiased spin system". The transcription below records that source material and preserves the source equation labels Eq. (A.39)–Eq. (A.45).

`[steward note: macro substitution]` The source TeX uses the local macro `\Xcal{\mathbb{A}}{1}{k}{1}{n-k}` for `\mathbb{A}(\boldsymbol{\tau}_{1}^{k}, \boldsymbol{s}_{1}^{n-k})`, `\Xcal{\mathbb{A}_1}{1}{k}{1}{n-k}` for `\mathbb{A}_1(\boldsymbol{\tau}_{1}^{k}, \boldsymbol{s}_{1}^{n-k})`, and `\Xcal{\mathbb{A}_2}{1}{k}{1}{n-k}` for `\mathbb{A}_2(\boldsymbol{\tau}_{1}^{k}, \boldsymbol{s}_{1}^{n-k})`. This file expands those macros for readability. The source TeX macro `\one` is rendered as `\mathbb{1}`.

## 2.1 Contributions to `K` in spin systems

## 2.2 Pure decoherence

> Suppose that `A = σ_z`, so that `A(t) ≡ A` `∀ t`, namely a situation of pure decoherence of the spin. Then we have `\mathbb{A}(\boldsymbol{\tau}_{1}^{k}, \boldsymbol{s}_{1}^{n-k}) = \langle \sigma_z^{n-k}\rangle_{1/d} \sigma_z^{k}`, which is easily found depending on the parity of `n` and `k`:

```math
\mathbb{A}(\boldsymbol{\tau}_{1}^{k}, \boldsymbol{s}_{1}^{n-k})
=
\begin{cases}
    \sigma_z & \text{($n$ odd, $k$ odd)} \\
    \mathbb{1} & \text{($n$ even, $k$ even)}  \\
    0 & \text{elsewhere}
\end{cases}\; .
\tag{A.39}
```

> This means that there are no even order terms in the effective Hamiltonian -- as the final Hamiltonian is always traceless and any term proportional to the identity will vanish -- and that any odd order term will give a contribution proportional to `σ_z`. Thus, we conclude that for a spin under pure decoherence, the effective Hamiltonian is in general of the form `K(t) = \frac{\omega(t)}{2}\sigma_z`.

## 2.3 Unbiased spin system

> Suppose now that the interaction term is orthogonal to `σ_z`. For example, take `A = σ_x`. Then `A(t) = σ_+ e^{i\omega t} + σ_- e^{-i\omega t}`, and the terms `A(\boldsymbol{t}_1^m)` have a different structure depending on the parity of `m`. For odd `m`:

```math
A(\boldsymbol{t}_1^m)
= \sigma_+ e^{i\phi(\boldsymbol{t}_1^m)}
+ \sigma_- e^{-i\phi(\boldsymbol{t}_1^m)}\;,
\tag{A.40}
```

> while for even `m`:

```math
\begin{aligned}
A(\boldsymbol{t}_1^m)
&= \ket{1}\bra{1} e^{i\phi(\boldsymbol{t}_1^m)}
  + \ket{0}\bra{0} e^{-i\phi(\boldsymbol{t}_1^m)}\\
&= \mathbb{1}\, \cos(\phi(\boldsymbol{t}_{1}^{m}))
  + i\sigma_z\, \sin(\phi(\boldsymbol{t}_{1}^{m}))
\;,
\end{aligned}
\tag{A.41}
```

> where the phases are defined as

```math
\phi(\boldsymbol{t}_1^m):= - \omega \sum_{j=1}^m (-1)^j t_j \; .
\tag{A.42}
```

> This leads to

```math
\mathbb{A}(\boldsymbol{\tau}_{1}^{k}, \boldsymbol{s}_{1}^{n-k})
=
\begin{cases}
    \mathbb{A}_1(\boldsymbol{\tau}_{1}^{k}, \boldsymbol{s}_{1}^{n-k})
      & \text{($n$ odd, $k$ odd)} \\
    \mathbb{A}_2(\boldsymbol{\tau}_{1}^{k}, \boldsymbol{s}_{1}^{n-k})
      & \text{($n$ even, $k$ even)}  \\
    0 & \text{elsewhere}
\end{cases}\; ,
\tag{A.43}
```

> with

```math
\mathbb{A}_1(\boldsymbol{\tau}_{1}^{k}, \boldsymbol{s}_{1}^{n-k})
=
\cos(\phi(\boldsymbol{s}_1^{n-k}))
\left[\sigma_+ e^{i\phi(\boldsymbol{\tau}_1^k)}
+ \sigma_- e^{-i\phi(\boldsymbol{\tau}_1^k)}\right]
\tag{A.44}
```

```math
\mathbb{A}_2(\boldsymbol{\tau}_{1}^{k}, \boldsymbol{s}_{1}^{n-k})
=
\cos(\phi(\boldsymbol{s}_1^{n-k}))
\left[\mathbb{1} + i \sin(\phi(\boldsymbol{\tau}_1^{k}))\sigma_z \right]
\tag{A.45}
```

> From the above it is clear that even orders give contributions on the diagonal of `K`, thus maintaining a structure proportional to `σ_z`, while odd orders give only contributions on off-diagonals of the effective Hamiltonian, thus changing its eigenbasis.

`[steward note: convention relevance]` The transcribed source subsection is system-side parity algebra. It does not define a coherent-displacement amplitude, a mode profile, a spectral-density-matched displacement, or any parameter equivalent to `α(ω)`, `ω_c`, `ω_d`, or `Δω`.

# 3. Notational glossary

The following symbols appear in the Appendix-D-routed source material, or were expected by the scaffold because of the Council Act 1 convention question. Symbols absent from the source subsection are recorded as absent because that absence is classification-bearing.

| Symbol | Letter definition (verbatim) | Letter location | Notes |
|---|---|---|---|
| `α(ω)` | Not present in the Appendix-D-routed source material; no definition given. | — | Classification-bearing absence. |
| `D̄_1(t)` | Not present in the Appendix-D-routed source material; no one-point ordered cumulant is defined there. | — | The main text discusses the first-order contribution through `\langle B(t)\rangle`, but no displacement-mode profile is specified. |
| `D̄_3(t)` | Not present in the Appendix-D-routed source material; no third-order ordered cumulant is defined there. | — | Classification-bearing absence. |
| `J(ω)` | Not present in the Appendix-D-routed source material. | — | No spectral density is invoked in the transcribed subsection. |
| `ω_c` | Not present in the Appendix-D-routed source material. | — | No cutoff-frequency displacement convention is given. |
| `ω` | `H_S = \frac{\omega}{2}\sigma_z` | Main text "Spin systems"; used in Eq. (A.42) | System Bohr/free-spin frequency in the Letter's notation. |
| `A(t)` | `A(t) = \sigma_+ e^{i\omega t} + \sigma_- e^{-i\omega t}` | Eq. (A.40) lead-in | For the `A = σ_x` unbiased spin example. |
| `\mathbb{A}(\boldsymbol{\tau}_{1}^{k}, \boldsymbol{s}_{1}^{n-k})` | `\langle A(\boldsymbol{s}_{1}^{n-k})^{\dagger}\rangle_{1/d}  A(\boldsymbol{\tau}_{1}^{k})` | Main text Eq. (15) lead-in; specialized in Eq. (A.39), Eq. (A.43) | Macro-expanded from source TeX. |
| `\phi(\boldsymbol{t}_1^m)` | `- \omega \sum_{j=1}^m (-1)^j t_j` | Eq. (A.42) | Phase used for products of `A(t)` in the `A = σ_x` example. |
| `\sigma_\pm` | Not explicitly defined in the transcribed subsection. | Eq. (A.40) | Standard spin raising/lowering notation; no convention choice for displacement follows from it. |

The glossary is purely a finding aid; the verbatim transcription in §2 is authoritative.

# 4. Classification of the displacement-mode convention

This section records whether and how Appendix D pins the displacement-mode convention required by CL-2026-005 v0.4 Entries 3.B.3 + 4.B.2. The classification is the *only* steward judgment required at this stage; selection of a convention (if needed) is reserved for Council Act 2.

## 4.1 Classification outcome

Exactly one of the three branches below is checked:

- [ ] **Pinned.** Appendix D specifies the displacement-mode convention unambiguously. The pinned convention is recorded in §4.2.
- [x] **Underdetermined.** Appendix D is consistent with one or more of subsidiary-briefing §3.1–§3.4 (and possibly other physically natural conventions) but does not single one out. The compatible candidates are recorded in §4.3.
- [ ] **Ambiguous-with-no-fit.** Appendix D's notation is itself ambiguous AND none of subsidiary-briefing §3.1–§3.4 captures the intended construction. The ambiguity is recorded in §4.4 and §3.6 of the subsidiary briefing fires.

Steward classification: the transcribed material determines the parity structure of `K_n` for pure decoherence (`A = σ_z`) and unbiased spin coupling (`A = σ_x`), but it does not define the bath displacement mode/profile. Therefore it cannot fix the numerical content of `D̄_1`, `D̄_3`, or any coherent-displacement B4 fixture.

## 4.2 If "pinned": the pinned convention

Not applicable. §4.1 outcome is "underdetermined"; no pinned convention is recorded.

Card name fixed by this outcome: none.

§4.3 Council handling at Act 2 is not moot under this outcome.

## 4.3 If "underdetermined": compatible candidates

Appendix-D-routed source material is silent on the displacement profile. Since it gives no equation involving `α(ω)` or a comparable spectral-mode amplitude, it does not support or rule out any of the §3.1–§3.4 candidate conventions. They remain compatible only in the weak sense that nothing in the transcribed subsection contradicts them.

| Candidate | Compatible with Appendix D? | Letter equation(s) supporting / ruling out | Notes |
|---|---|---|---|
| §3.1 single-mode at ω_c | Silent-compatible | None; Eq. (A.39)–Eq. (A.45) contain no `α(ω)`, `ω_c`, or bath-mode profile. | Requires Council Act 2 selection if chosen. |
| §3.2 single-mode at ω_S | Silent-compatible | None; Eq. (A.39)–Eq. (A.45) contain no `α(ω)` or bath-mode profile. Eq. (A.42) defines the system frequency `ω` only through spin dynamics. | Requires Council Act 2 selection if chosen. |
| §3.3 broadband ∝ √J(ω) | Silent-compatible | None; Eq. (A.39)–Eq. (A.45) contain no `J(ω)` or spectral-density dependence. | Requires Council Act 2 selection if chosen. |
| §3.4 Gaussian envelope (ω_d, Δω) | Silent-compatible | None; Eq. (A.39)–Eq. (A.45) contain no displacement center or bandwidth. | Requires Council Act 2 selection if chosen. |
| Additional convention | None surfaced | — | No extra displacement convention appears in the transcribed source material. |

Act 2 agenda under this outcome: §4.3 handling selection (a / b / c, no Steward-proposed default) over the compatible-candidate set.

## 4.4 If "ambiguous-with-no-fit": ambiguity record

Not applicable. §4.1 outcome is "underdetermined", not "ambiguous-with-no-fit". The problem is absence/silence about the displacement profile, not an internally ambiguous notation that rules out §3.1–§3.4.

Routing per subsidiary briefing §3.6 fires under this outcome:
- [ ] Letter-clarification consultation (recommended first move; Colla as natural primary contact via the standing open-quantum-systems collaboration).
- [ ] Successor-paper consultation (only if a successor with explicit convention has since published).
- [ ] Open hold (fallback if neither above produces a determinate convention; validity envelope holds at DG-2 PARTIAL — 3 of 4 sub-claims PASS).

§3.6 routing does not fire at this stage.

# 5. Connection to subsidiary briefing §3 candidates

This section is a **reading aid only**, not part of the verbatim transcription. It records the steward's mapping between Appendix D's notation and the §3.1–§3.4 candidate conventions, for the Council's convenience at Act 2. Any disagreement between this section and the verbatim §2 transcription is resolved in favour of §2.

| Subsidiary-briefing §3 candidate | Mapping into Appendix D notation | Steward judgment of fit |
|---|---|---|
| §3.1 `α(ω) = α_0 δ(ω − ω_c)` | No Appendix-D-routed expression; `α(ω)` and `ω_c` absent. | Admissible only as an external convention; not pinned by this source. |
| §3.2 `α(ω) = α_0 δ(ω − ω_S)` | No Appendix-D-routed expression; `α(ω)` absent. The Letter's `ω` is the system frequency in Eq. (A.42), but no bath displacement at that frequency is specified. | Admissible only as an external convention; not pinned by this source. |
| §3.3 `α(ω) ∝ √(J(ω))` | No Appendix-D-routed expression; `α(ω)` and `J(ω)` absent. | Admissible only as an external convention; not pinned by this source. |
| §3.4 `α(ω) = α_0 exp(−(ω − ω_d)²/(2 Δω²))` | No Appendix-D-routed expression; `α(ω)`, `ω_d`, and `Δω` absent. | Admissible only as an external convention; not pinned by this source. |

# 6. Routing record (post-classification)

Once §4.1 is resolved, the steward updates the artefact header `status:` field from `SCAFFOLD — not yet populated` to one of:

- `POPULATED — pinned; awaiting Act 2 ratification of convention <X>`
- `POPULATED — underdetermined; awaiting Act 2 §4.3 handling selection over candidate set <Y>`
- `POPULATED — ambiguous-with-no-fit; §3.6 routing initiated, branch <Z>`

and circulates the populated transcription with a one-paragraph cover note to the Council, naming the proposed Act 2 agenda under the classification outcome.

**Current routing state (2026-05-04).** Header status updated to `POPULATED — underdetermined; awaiting Act 2 §4.3 handling selection over candidate set §3.1–§3.4`.

**Cover note for Council circulation.** The Appendix-D-routed Letter source material has now been transcribed from the arXiv/APS source. It contains the spin-system parity algebra for pure decoherence and unbiased `A = σ_x` coupling, but it does not define any coherent-displacement spectral profile or any notation equivalent to `α(ω)`, `J(ω)`, `ω_c`, `ω_d`, or `Δω`. The classification is therefore **underdetermined**: all four subsidiary-briefing §3.1–§3.4 candidate conventions remain silent-compatible, none is pinned, no additional candidate surfaced, and §3.6 ambiguous-with-no-fit routing does not fire. Proposed Act 2 agenda: Council performs the deferred §4.3 handling selection (a / b / c, no Steward-proposed default) over the §3.1–§3.4 candidate set, with the standing conflict notice and anti-bias requirements unchanged.

# 7. Verification log

| Date | Steward | Action | Notes |
|---|---|---|---|
| 2026-05-04 | U. Warring | Scaffold drafted | This file at SCAFFOLD status |
| 2026-05-04 | U. Warring | Verbatim transcription performed | §2 populated from arXiv `2506.04097v1` TeX/PDF source; source-section naming mismatch recorded |
| 2026-05-04 | U. Warring | Classification recorded | §4.1 checked "underdetermined"; §4.3 candidate table populated |
| _<YYYY-MM-DD>_ | _<initials>_ | Cross-read against Letter (independent pass, ideally a non-author) | _<diff/no-diff against §2>_ |
| 2026-05-04 | U. Warring | Circulation cover note drafted | §6 cover note names Act 2 agenda; independent cross-read still recommended before formal Council circulation |

A second-pair-of-eyes cross-read on the verbatim §2 transcription is **strongly recommended** before circulation, on standing-conflict grounds: it is the lightest available form of redundancy against transcription drift in the steward's hand, costs little, and pre-empts any Guardian objection at Act 2 that the underlying record was prepared single-handedly under conflict.

# 8. Revision history

| Version | Status | Trigger | Net change |
|---|---|---|---|
| v0.0.1 | SCAFFOLD — not yet populated | Steward unblocking move 2026-05-04 (Council Act 1 cleared 2026-05-04) | Initial scaffold drafted, mirroring `transcriptions/hayden-sorce-2022.md` template structure; sections §1–§7 set up empty for population from the Letter |
| v0.0.1-populated | POPULATED — underdetermined; awaiting Act 2 §4.3 handling selection over candidate set §3.1–§3.4 | Steward population pass 2026-05-04 following commit `d67cb8c` scaffold | §1 bibliographic record filled; §2 transcribed Appendix-D-routed end-matter subsection "Contributions to K in spin systems"; §3 glossary records absence of displacement-profile notation; §4.1 classification checked "underdetermined"; §4.3 candidate table marks §3.1–§3.4 silent-compatible; §5 mapping populated; §6 cover note drafted |

---

*End of populated Appendix-D-routed transcription for CL-2026-005 v0.4 Entries 3.B.3 + 4.B.2. Classification: underdetermined; Act 2 selection remains Council-gated.*

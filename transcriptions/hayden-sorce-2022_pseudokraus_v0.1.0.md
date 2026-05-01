---
transcription_id: hayden-sorce-2022-pseudokraus
version: v0.1.0
date: 2026-05-01
type: source-transcription
source_title: "A canonical Hamiltonian for open quantum systems"
source_authors: "Patrick Hayden; Jonathan Sorce"
source_publication: "Journal of Physics A: Mathematical and Theoretical 55, 225302 (2022)"
source_doi: "https://doi.org/10.1088/1751-8121/ac65c2"
source_arxiv: "https://arxiv.org/abs/2108.08316"
source_version_used: "arXiv:2108.08316v4, 2022-05-11"
repo_anchor: "CL-2026-005 v0.4 Entry 1.B.3; benchmarks/benchmark_cards/A1_closed-form-K_v0.1.1.yaml failure_mode_log[0]; benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml (frozen against this version)"
status: initiated
license: CC-BY-4.0 (LICENSE-docs)
superseded_by: hayden-sorce-2022_pseudokraus_v0.1.1.md
---

# Hayden-Sorce 2022 pseudo-Kraus transcription

## 1. Purpose

This transcription initiates the DG-2 unblocking path for CL-2026-005 v0.4 Entry 1.B.3: the check that the repository's basis-independent formula for `K` reduces to the diagonal pseudo-Kraus formula in Hayden-Sorce 2022.

The scope is deliberately narrow:

- transcribe the finite-dimensional pseudo-Kraus formula for the canonical Hamiltonian;
- map source symbols to repository notation;
- record mechanical preconditions future cards must freeze;
- provide a candidate fixture shape for later card drafting.

This file does **not** pass DG-2, does **not** update the validity envelope, and does **not** alter any already-committed DG-1 card. It creates the repository-local source artefact that future DG-2 cards may cite.

## 2. Source identity

Primary source:

Patrick Hayden and Jonathan Sorce, "A canonical Hamiltonian for open quantum systems", *Journal of Physics A: Mathematical and Theoretical* **55**, 225302 (2022), DOI `10.1088/1751-8121/ac65c2`; arXiv `2108.08316`.

The repository's Ledger citation at `ledger/CL-2026-005_v0.4.md` identifies this source as *J. Phys. A* **55**, 225302 (2022). Some DG-1 operational artefacts historically refer to "Communications Physics 5, 92 (2022)"; this transcription uses the primary-source bibliographic metadata above and treats the Communications Physics wording as a historical repository metadata error, not as a second source.

Source sections used:

- Section 2.2: pseudo-Kraus decomposition of a Hermiticity-preserving superoperator.
- Section 3.2: canonical Hamiltonian as the orthogonal projection of a quantum master equation onto Hamiltonian superoperators.
- Section 3.3: expression of the canonical Hamiltonian and dissipator in pseudo-Kraus form.

## 3. Preconditions

Let `H` be a finite-dimensional Hilbert space with dimension `d`.

The source formula applies to a superoperator `L` that is:

- Hermiticity-preserving: `L(M)^\dagger = L(M^\dagger)`;
- trace-annihilating: `Tr(L(M)) = 0`;
- written in pseudo-Kraus form with real coefficients:

```math
L(\rho) = \sum_j \gamma_j E_j \rho E_j^\dagger,
\qquad \gamma_j \in \mathbb{R}.
```

Trace annihilation is not optional. In pseudo-Kraus variables it imposes:

```math
\sum_j \gamma_j E_j^\dagger E_j = 0.
```

Future benchmark cards must check this condition mechanically before comparing Hamiltonians. A raw expression of the form `sum_j gamma_j E_j rho E_j^\dagger` is not a valid quantum master-equation generator unless this constraint is satisfied.

## 4. Transcribed formula

For an HPTA pseudo-Kraus decomposition satisfying the preconditions above, the Hayden-Sorce canonical Hamiltonian is:

```math
H_{\mathrm{HS}}[L]
  =
  \frac{1}{2 i d}
  \sum_j \gamma_j
  \left(
    \operatorname{Tr}(E_j) E_j^\dagger
    -
    \operatorname{Tr}(E_j^\dagger) E_j
  \right).
```

The associated canonical dissipator is:

```math
D_{\mathrm{HS}}(\rho) = L(\rho) + i[H_{\mathrm{HS}}, \rho].
```

Equivalently, after shifting each pseudo-Kraus operator to its traceless part,

```math
L_j = E_j - \frac{\operatorname{Tr}(E_j)}{d} I,
```

the dissipator can be written in Lindblad form with traceless jump operators:

```math
D_{\mathrm{HS}}(\rho)
  =
  \sum_j \gamma_j
  \left(
    L_j \rho L_j^\dagger
    -
    \frac{1}{2}\{L_j^\dagger L_j, \rho\}
  \right).
```

The Hamiltonian is defined up to addition of a scalar multiple of the identity; this repository follows the source convention that the canonical Hamiltonian is traceless. The transcribed formula returns a traceless operator by construction: each summand `Tr(E_j) E_j^\dagger - Tr(E_j^\dagger) E_j` has trace `Tr(E_j) Tr(E_j^\dagger) - Tr(E_j^\dagger) Tr(E_j) = 0`.

## 4a. Structural cross-check against Letter Eq. (6)

The transcribed formula in §4 and the Letter Eq. (6) basis-independent expression `K = (1/2id) Σ_α [F_α^\dagger, L[F_α]]` are different basis-projections of the same canonical-Hamiltonian projection on `htp(H)`. They therefore agree on every HPTA generator, including pseudo-Kraus inputs. A direct algebraic check in the matrix-unit basis `F_{j,k} = |j\rangle\langle k|` makes this explicit:

```math
K
  = \frac{1}{2 i d}
    \sum_{j,k} \bigl[\,|k\rangle\langle j|,\; L[\,|j\rangle\langle k|\,]\,\bigr]
  = \frac{1}{2 i d}
    \sum_\alpha \gamma_\alpha
    \sum_{j,k}
    \bigl(\,|k\rangle\langle j| E_\alpha |j\rangle\langle k| E_\alpha^\dagger
         - E_\alpha |j\rangle\langle k| E_\alpha^\dagger |k\rangle\langle j|\,\bigr).
```

Collapsing the inner sums via the resolutions of identity `Σ_j |j\rangle\langle j| = Σ_k |k\rangle\langle k| = I` gives `Σ_{j,k} |k\rangle\langle j| E_\alpha |j\rangle\langle k| = Tr(E_\alpha) I` (folded into `|k\rangle\langle k|` after the inner contraction) and similarly for the second term, leaving

```math
K = \frac{1}{2 i d}
    \sum_\alpha \gamma_\alpha
    \bigl(\operatorname{Tr}(E_\alpha) E_\alpha^\dagger
         - \operatorname{Tr}(E_\alpha^\dagger) E_\alpha\bigr)
  = H_{\mathrm{HS}}[L].
```

**Consequence for benchmark-card design.** A future card that compares `cbg.effective_hamiltonian.K_from_generator(L_pseudo_kraus, matrix_unit_basis)` against `H_HS` from §4 is verifying *implementation correctness* (the matrix-unit summation and the trace-based formula agree numerically), not the source claim itself. The cross-check above shows the two paths are algebraically identical; the card's verdict therefore tests the basis-summation pipeline. Independent verification of Hayden-Sorce 2022's source claim is out of scope for this transcription and would require either (a) an alternative derivation of the canonical-Hamiltonian projection from first principles, or (b) a comparison against an external implementation citing the same source.

## 5. Diagonal pseudo-Kraus specialization

For the diagonal pseudo-Kraus case relevant to CL-2026-005 Entry 1.B.3, write:

```math
L(\rho) = \sum_i \omega_i V_i \rho V_i^\dagger,
\qquad \omega_i \in \mathbb{R},
```

with the HPTA constraint:

```math
\sum_i \omega_i V_i^\dagger V_i = 0.
```

Then the transcribed Hayden-Sorce expression is:

```math
H_{\mathrm{HS}}^{\mathrm{diag}}
  =
  \frac{1}{2 i d}
  \sum_i \omega_i
  \left(
    \operatorname{Tr}(V_i) V_i^\dagger
    -
    \operatorname{Tr}(V_i^\dagger) V_i
  \right).
```

Immediate consequences for the old DG-1 deferral:

- If every `V_i` is traceless, this expression gives zero.
- A nonzero comparison requires at least one pseudo-Kraus operator with a nonzero trace and nontrivial anti-Hermitian scalar overlap.
- The speculative DG-1 placeholder expectation proportional to `(omega_11 - omega_22) sigma_z` is not a valid card expectation unless the concrete `V_i`, `omega_i`, and HPTA constraint imply it.

## 6. Repository symbol map

| Source symbol | Repository meaning |
|---|---|
| `d` | `frozen_parameters.model.system_dimension` |
| `L` | generator callable consumed by `cbg.effective_hamiltonian.K_from_generator` |
| `E_j` / `V_i` | future card field for pseudo-Kraus operators |
| `gamma_j` / `omega_i` | future card field for real pseudo-Kraus coefficients |
| `H_HS[L]` | expected `K` for a Hayden-Sorce pseudo-Kraus benchmark case |
| `sum gamma_j E_j^\dagger E_j = 0` | required HPTA validation precondition |

The existing `K_from_generator` implementation evaluates the Colla-Breuer-Gasbarri basis expression for `K`. A future DG-2 card can compare its output against `H_HS^{diag}` for fixtures satisfying the HPTA constraint.

## 7. Candidate fixture shape, not yet frozen

The following qubit fixture is suitable as a seed for a future card, but is **not frozen by this transcription**:

```math
E_1 = I + i a \sigma_z,\qquad \gamma_1 = 1,
```

```math
E_2 = \sqrt{1 + a^2}\, I,\qquad \gamma_2 = -1,
```

with real nonzero `a` and `d = 2`.

The HPTA precondition holds as an *algebraic* identity (not merely numerically): `(I - i a \sigma_z)(I + i a \sigma_z) = I + a^2 \sigma_z^2 = (1 + a^2) I`, so

```math
\gamma_1 E_1^\dagger E_1 + \gamma_2 E_2^\dagger E_2
  = (1 + a^2) I - (1 + a^2) I = 0,
```

independent of the value of `a`. The transcribed formula then gives:

```math
H_{\mathrm{HS}} = -a \sigma_z.
```

A `\sigma_x` analog with the same structure (`E_1 = I + i b \sigma_x`, `E_2 = \sqrt{1 + b^2} I`, real nonzero `b`) gives `H_{\mathrm{HS}} = -b \sigma_x` by the same construction, since `\sigma_x^2 = I`. This second fixture is useful as a Pauli-orientation cross-check: a correct implementation must produce the rotated-axis result without preferring `\sigma_z`.

The boundary case `a = 0` is degenerate: `E_1 = E_2 = I`, so `L \equiv 0` and `H_HS = 0` trivially. A meaningful test requires `a \neq 0`.

A DG-2 benchmark card may either adopt these fixtures or choose different ones. Per cards-first discipline, that choice must be frozen in the card before implementation work starts.

## 8. DG-2 routing

This transcription resolves only the Hayden-Sorce 2022 prior-art formula gap for Entry 1.B.3. It does not resolve the coherent-displacement convention gap for Entries 3.B.3 and 4.B.2.

Next admissible steps:

1. Draft a DG-2 benchmark card for the pseudo-Kraus reduction, with a frozen HPTA pseudo-Kraus fixture and expected `H_HS`.
2. Add mechanical validation that the fixture satisfies `sum gamma_j E_j^\dagger E_j = 0` before the comparison is evaluated.
3. Only after the card is frozen, implement any missing parser/fixture support needed to run it.

No Council deliberation is required for this transcription itself. If later work changes the Ledger-bearing interpretation of Entry 1.B.3 rather than merely operationalising its already-cleared source comparison, that later work must be routed separately.

---

*End of transcription v0.1.0. Initiated 2026-05-01 under repository-layer stewardship.*

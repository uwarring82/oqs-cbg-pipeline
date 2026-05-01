---
transcription_id: hayden-sorce-2022-pseudokraus
version: v0.1.1
date: 2026-05-01
type: source-transcription
source_title: "A canonical Hamiltonian for open quantum systems"
source_authors: "Patrick Hayden; Jonathan Sorce"
source_publication: "Journal of Physics A: Mathematical and Theoretical 55, 225302 (2022)"
source_doi: "https://doi.org/10.1088/1751-8121/ac65c2"
source_arxiv: "https://arxiv.org/abs/2108.08316"
source_version_used: "arXiv:2108.08316v4, 2022-05-11"
repo_anchor: "CL-2026-005 v0.4 Entry 1.B.3 (diagonal + off-diagonal halves); Entry 1.D (off-diagonal generalization claim); benchmarks/benchmark_cards/A1_closed-form-K_v0.1.1.yaml failure_mode_log[0]; benchmarks/benchmark_cards/B1_pseudo-kraus-diagonal_v0.1.0.yaml (frozen against v0.1.0)"
status: in-use
license: CC-BY-4.0 (LICENSE-docs)
supersedes: hayden-sorce-2022_pseudokraus_v0.1.0.md
---

# Hayden-Sorce 2022 pseudo-Kraus transcription

## 1. Purpose

This transcription operationalises the DG-2 path for CL-2026-005 v0.4 Entry 1.B.3 (both halves) and the off-diagonal generalization claim in Entry 1.D: the check that the repository's basis-independent expression for `K` (Letter Eq. (6)) reduces to the diagonal Hayden-Sorce 2022 closed form on diagonal pseudo-Kraus inputs, and absorbs the off-diagonal pseudo-Kraus form without separate treatment.

Scope:

- Transcribe the finite-dimensional Hayden-Sorce canonical-Hamiltonian formula in its source-faithful single-index pseudo-Kraus form (§4).
- Record the structural cross-check against Letter Eq. (6) (§4a).
- **Extend to off-diagonal pseudo-Kraus form (§4b).** This is a Letter-derived consequence — algebraically equivalent to §4 after diagonalizing the Hermitian coefficient matrix — recorded here so cards constructed natively in off-diagonal form can cite a stable repository expression rather than an in-card eigendecomposition.
- Provide candidate fixtures: the diagonal/single-index form (§7) and the off-diagonal form (§7a).

This file does **not** pass DG-2, does **not** update the validity envelope, and does **not** alter any committed card. It is a v0.1.0 → v0.1.1 superseding revision per the transcription-layer protocol (`transcriptions/README.md` §Naming): the v0.1.0 file is retained, this file is added, and the index is updated to mark v0.1.1 as the current version. Card B1 v0.1.0 (PASS, 2026-05-01) was frozen against v0.1.0; under SCHEMA.md §Card lifecycle, B1 is content-immutable and is not retroactively re-anchored to v0.1.1.

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

## 4. Transcribed formula (single-index pseudo-Kraus form)

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

## 4b. Off-diagonal pseudo-Kraus generalization (Letter-derived consequence)

A pseudo-Kraus generator may also be written natively with a Hermitian coefficient matrix `omega` rather than a real diagonal vector `gamma`:

```math
L(\rho) = \sum_{i,j} \omega_{ij} V_i \rho V_j^\dagger,
\qquad \omega_{ji} = \omega_{ij}^{\ast}\ \text{(Hermitian)}.
```

Hermiticity preservation requires `omega` Hermitian (so off-diagonal entries are complex conjugates and diagonal entries are real); trace annihilation requires

```math
\sum_{i,j} \omega_{ij} V_j^\dagger V_i = 0.
```

The §4 single-index form `L(rho) = sum_alpha gamma_alpha E_alpha rho E_alpha^dagger` is the special case obtained by eigendecomposing `omega = U D U^dagger`: the eigenvalues `D_{αα}` become `gamma_alpha`, and the corresponding linear combinations of `V_i` become `E_alpha`. The diagonal pseudo-Kraus form (§5) is the further restriction `omega_{ij} = delta_{ij} omega_{ii}`.

Applying Letter Eq. (6) directly to off-diagonal pseudo-Kraus `L`, the matrix-unit basis sum factorizes (analogous to §4a) into

```math
H_{\mathrm{HS}}^{\mathrm{off\text{-}diag}}[L]
  =
  \frac{1}{2 i d}
  \sum_{i,j} \omega_{ij}
  \left(
    \operatorname{Tr}(V_i) V_j^\dagger
    -
    \operatorname{Tr}(V_j^\dagger) V_i
  \right).
```

**Authority status of this expression.** §4b is a *Letter-derived consequence*, not new Hayden-Sorce 2022 source content. It is algebraically equivalent to §4 after diagonalizing `omega` — every off-diagonal pseudo-Kraus `L` admits a single-index reformulation, so §4 already covers the underlying mathematical content via eigendecomposition. §4b is recorded for *operational* convenience: cards constructed natively in off-diagonal form (e.g., V_1, V_2 a fixed Pauli pair plus a Hermitian `omega` with non-zero off-diagonal entries) can cite the §4b expression directly rather than embedding an in-card eigendecomposition step that would obscure the audit trail.

The "Letter generalises the prior result to the off-diagonal case" claim in CL-2026-005 v0.4 Entry 1.B.3 / Entry 1.D is best read operationally: the basis-independent Letter Eq. (6) does not require a prior eigendecomposition of `omega`, so off-diagonal pseudo-Kraus `L` evaluates directly. Hayden-Sorce 2022's source content gives the closed form in single-index / diagonal form (§4 / §5); the Letter's contribution is the basis-independent recipe that absorbs the off-diagonal case without separate treatment.

**Hermiticity and tracelessness of `H_HS^off-diag`** follow from `omega` Hermitian:

- *Hermiticity.* Taking `dagger` of the integrand and relabeling `i ↔ j` reproduces the negative of the integrand under `omega_{ji}^* = omega_{ij}`; multiplied by `1/(2id)` (with `omega` Hermitian implying real-valued contractions in the trace), the result is Hermitian.
- *Tracelessness.* `Tr(Tr(V_i) V_j^dagger - Tr(V_j^dagger) V_i) = Tr(V_i) Tr(V_j^dagger) - Tr(V_j^dagger) Tr(V_i) = 0` term-by-term.

A direct algebraic derivation in the matrix-unit basis closes the cross-check: starting from `Σ_{k,l} [|l⟩⟨k|, L[|k⟩⟨l|]]` for the off-diagonal `L`, the inner contractions reduce as in §4a but with the index pair `(i, j)` retained, giving the §4b expression after dividing by `2id`. This mirrors §4a; no new identity is invoked.

## 5. Diagonal pseudo-Kraus specialization

For the diagonal pseudo-Kraus case, write:

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
| `E_j` (single-index) | future card field for pseudo-Kraus operators (B1 form) |
| `gamma_j` (single-index) | future card field for real pseudo-Kraus coefficients (B1 form) |
| `V_i`, `V_j` (off-diagonal) | future card field for off-diagonal pseudo-Kraus operators |
| `omega_{ij}` (off-diagonal) | future card field for the Hermitian off-diagonal coefficient matrix |
| `H_HS[L]` / `H_HS^{off-diag}[L]` | expected `K` for the corresponding pseudo-Kraus benchmark case |
| `sum gamma_j E_j^\dagger E_j = 0` (single-index) | required HPTA validation precondition |
| `sum_{i,j} omega_{ij} V_j^\dagger V_i = 0` (off-diagonal) | required HPTA validation precondition |

The existing `K_from_generator` implementation evaluates the Colla-Breuer-Gasbarri basis expression for `K` and is independent of the input pseudo-Kraus representation: it consumes only the callable `L`. A future DG-2 off-diagonal card therefore reuses the same runner contract as B1 — what changes is the card-level operator/coefficient surface (V_i list + omega matrix instead of E_j list + gamma vector) and the corresponding handler that builds `L` from those fields.

## 7. Candidate fixture (single-index, σ_z form), not yet frozen

The following qubit fixture is suitable as a seed for a single-index/diagonal card; it was adopted by Card B1 v0.1.0 (PASS, 2026-05-01):

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

## 7a. Candidate fixture (off-diagonal form), not yet frozen

The following qubit fixture exercises §4b directly — a Hermitian `omega` with nonzero (purely imaginary) off-diagonal entries:

```math
V_1 = I,\qquad V_2 = \sigma_z,\qquad d = 2,
```

```math
\omega = \begin{pmatrix} 1 & i \beta \\ -i \beta & -1 \end{pmatrix},
```

with real nonzero `beta`. The matrix is Hermitian by construction (real diagonal; off-diagonal entries are complex conjugates).

The HPTA precondition holds as an algebraic identity, independent of `beta`:

```math
\sum_{i,j} \omega_{ij} V_j^\dagger V_i
  = \omega_{11} I + \omega_{12} \sigma_z + \omega_{21} \sigma_z + \omega_{22} I
  = (1 + (-1)) I + (i \beta + (- i \beta)) \sigma_z = 0.
```

(Uses `V_1^\dagger V_1 = I`, `V_1^\dagger V_2 = V_2^\dagger V_1 = \sigma_z` since `V_1 = I` and `V_2 = \sigma_z` is Hermitian, and `V_2^\dagger V_2 = \sigma_z^2 = I`.)

The transcribed off-diagonal formula then gives:

```math
H_{\mathrm{HS}}^{\mathrm{off\text{-}diag}}
  =
  \frac{1}{2 i d}
  \sum_{i,j} \omega_{ij} \left(\operatorname{Tr}(V_i) V_j^\dagger - \operatorname{Tr}(V_j^\dagger) V_i\right)
  =
  \beta\, \sigma_z,
```

with the per-term contributions:

| `(i,j)` | `omega_{ij}` | `Tr(V_i)` | `Tr(V_j^dagger)` | summand |
|---|---|---|---|---|
| (1,1) | 1 | 2 | 2 | `2 I - 2 I = 0` |
| (1,2) | `i beta` | 2 | 0 | `i beta · 2 sigma_z = 2 i beta sigma_z` |
| (2,1) | `-i beta` | 0 | 2 | `-i beta · (- 2 sigma_z) = 2 i beta sigma_z` |
| (2,2) | -1 | 0 | 0 | `0` |

Sum: `4 i beta sigma_z`; multiplied by `1 / (2 i d) = 1 / (4 i)`, giving `H_HS^off-diag = beta sigma_z`.

A `sigma_x` analog (`V_1 = sigma_x, V_2 = I, omega = same Hermitian matrix with `beta` real`) gives `H_HS^off-diag = -beta sigma_x` by symmetric construction (HPTA holds because `sigma_x^2 = I`, with the same imaginary-off-diagonal Hermiticity pattern).

The diagonal sub-case `omega_{12} = omega_{21} = 0` collapses to `omega_{11} V_1 \rho V_1^\dagger + omega_{22} V_2 \rho V_2^\dagger`. With `V_1 = I` (cancels term-wise) and `V_2 = sigma_z` (traceless), the transcribed formula gives zero — a useful sanity-check sub-fixture for any future B-series card.

A DG-2 benchmark card may either adopt this fixture or choose a different off-diagonal HPTA fixture. Per cards-first discipline, that choice must be frozen in the card before implementation work starts.

## 8. DG-2 routing

This transcription resolves the Hayden-Sorce 2022 prior-art formula gap for Entry 1.B.3 (both diagonal and off-diagonal halves) and for Entry 1.D's "the new formula generalises the prior result to the off-diagonal case" claim. It does not resolve the coherent-displacement convention gap for Entries 3.B.3 and 4.B.2.

DG-2 progress map after v0.1.1:

1. **Diagonal half of Entry 1.B.3** — covered by Card B1 v0.1.0 (PASS, 2026-05-01) frozen against transcription v0.1.0. Re-anchoring B1 to v0.1.1 is **not** required: §4 / §5 / §7 content is unchanged from v0.1.0, and B1's frozen fixtures cite §4 / §5 / §7 only. (Rule of thumb: cards frozen against vN.M remain anchored to vN.M; vN.(M+1) is the source for *future* cards.)
2. **Off-diagonal half of Entry 1.B.3 / Entry 1.D** — admissible next card (provisional id B2): freeze an off-diagonal HPTA fixture (§7a or alternative) with expected `H_HS^off-diag` (§4b), enforce HPTA mechanically, and compare against `K_from_generator` output. The runner extension required is bounded: the card surface adds `pseudo_kraus_offdiag_operators` (V_i list) and `pseudo_kraus_offdiag_omega` (Hermitian matrix), and a new handler reuses the existing AST-restricted symbolic-operator parser plus a small numerics block for `omega`.
3. **Cross-basis structural-identity check** — DG-2 universal-default per Sail v0.5 §9 DG-2; orthogonal to this transcription (operates on the K_from_generator basis, not on the pseudo-Kraus representation). Implementable independently.
4. **Coherent-displacement gap (Entries 3.B.3, 4.B.2)** — orthogonal to this transcription; remains gated on the second DG-2 unblocker (Council-cleared displacement convention).

No Council deliberation is required for this transcription bump. The bump remains within the transcription-layer authority limit (`transcriptions/README.md` §Authority): §4b is a Letter-derived consequence, not a new scientific claim, and is recorded as such in this file's authority statement.

---

*End of transcription v0.1.1. Bumped 2026-05-01 under repository-layer stewardship; supersedes v0.1.0 by adding off-diagonal pseudo-Kraus coverage. Source content (§2, §3, §4, §5) is unchanged from v0.1.0; new content (§4b, §7a) is Letter-derived consequence and DG-2 routing.*

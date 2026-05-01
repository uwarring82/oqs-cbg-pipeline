# Hayden-Sorce 2022 transcription bumped to v0.1.1 — off-diagonal pseudo-Kraus coverage

**Date:** 2026-05-01
**Type:** structural
**Triggering commit:** (to be populated on commit)
**Triggering evidence:** `transcriptions/hayden-sorce-2022_pseudokraus_v0.1.1.md` (new); `transcriptions/hayden-sorce-2022_pseudokraus_v0.1.0.md` (annotated with `superseded_by`); `transcriptions/README.md` (index updated to mark v0.1.1 as current and v0.1.0 as superseded); Hayden and Sorce, *J. Phys. A* **55**, 225302 (2022), DOI `10.1088/1751-8121/ac65c2`, arXiv `2108.08316`

## Summary

Transcription v0.1.1 supersedes v0.1.0 by adding §4b (off-diagonal pseudo-Kraus generalization, derived from Letter Eq. (6)) and §7a (off-diagonal candidate fixture: V_1 = I, V_2 = σ_z, Hermitian ω with imaginary off-diagonal entries → H_HS^off-diag = β σ_z). Source content (§2 source identity, §3 preconditions, §4 single-index transcribed formula, §5 diagonal specialization) is unchanged from v0.1.0; the new content is a Letter-derived consequence with an explicit authority qualifier. v0.1.0 is retained per the transcription-layer protocol (`transcriptions/README.md` §Naming) and remains anchored by frozen Card B1 v0.1.0 (PASS, 2026-05-01).

## Detail

**Scope of the bump.** v0.1.1 covers what v0.1.0 already covered — the source-faithful single-index pseudo-Kraus form — plus the off-diagonal extension needed for the second half of CL-2026-005 v0.4 Entry 1.B.3 ("the new formula generalises the prior result to the off-diagonal case") and Entry 1.D. The off-diagonal direct expression is recorded as

```
H_HS^off-diag[L] = (1/2id) Σ_{i,j} ω_{ij} (Tr(V_i) V_j^dagger - Tr(V_j^dagger) V_i),
```

derived in §4b by direct application of Letter Eq. (6) to off-diagonal pseudo-Kraus L (HPTA: ω Hermitian, Σ_{i,j} ω_{ij} V_j^dagger V_i = 0). The expression is algebraically equivalent to §4 after eigendecomposing ω, so source-faithfulness is unaffected — it is a notational variant suited to natively off-diagonal fixtures.

**Authority status.** §4b is explicitly tagged as a Letter-derived consequence within the transcription's authority limits (`transcriptions/README.md` §Authority). The transcription does not claim §4b is in Hayden-Sorce 2022's source content; it claims §4b follows from Letter Eq. (6) and is algebraically equivalent to the source-faithful §4. This distinction matters for any future card that cites §4b: the citation chain runs *Letter Eq. (6) → §4b derivation*, not *Hayden-Sorce 2022 → §4b*.

**Pre-commit numerical sanity** (steward-side, prior to the bump) confirms the off-diagonal fixture in §7a evaluates as claimed: HPTA residual at machine zero (the constraint holds as an algebraic identity), `K_from_generator(L_off-diag, matrix_unit_basis) - β σ_z = 0` exactly at β = 0.5; same for a σ_x-analog fixture (V_1 = σ_x, V_2 = I, β = 0.3) giving K = -0.3 σ_x. These are pre-bump evidence that the formula is well-posed; they are not the verdict of any benchmark card.

**Card B1 v0.1.0 is not re-anchored.** Per SCHEMA.md §Card lifecycle, B1 is content-immutable post-verdict. B1's frozen fixtures cite §4 / §5 / §7 only, all of which are unchanged from v0.1.0 to v0.1.1. The transcription-layer convention (recorded in v0.1.1 §8) is: cards frozen against `vN.M` remain anchored to `vN.M`; `vN.(M+1)` is the source for *future* cards. No B1 supersedure is required or appropriate.

**v0.1.0 annotation.** v0.1.0's frontmatter receives a `superseded_by: hayden-sorce-2022_pseudokraus_v0.1.1.md` field as a one-line bookkeeping completion, mirroring the analogous discipline on cards (SCHEMA.md `superseded_by:`) and the logbook (`superseded by:` annotation). The transcription's body content is not edited. The README index lists both versions, with v0.1.1 marked as current and v0.1.0 in a separate "Superseded transcriptions" subsection.

## Routing notes

This bump operationalises the "off-diagonal pseudo-Kraus" track of the three-track DG-2 plan:

1. **Off-diagonal pseudo-Kraus (this track)** — transcription bump complete; next steps are a card freeze (provisional id B2) against §7a or alternative off-diagonal fixture, then a runner extension (additive: new card surface fields `pseudo_kraus_offdiag_operators` + `pseudo_kraus_offdiag_omega`, new handler reusing the AST-restricted operator parser, no change to existing B1 / A1 paths).
2. **Cross-basis structural-identity check** — orthogonal to this transcription; implementable independently.
3. **Coherent-displacement convention (Entries 3.B.3, 4.B.2)** — orthogonal; remains gated on the second DG-2 unblocker (Council clearance).

This is a repository-layer operational artefact under transcription-layer authority. It does not modify CL-2026-005, the Sail, or the validity envelope. No code changed; no card froze; no DG status changed; no Council deliberation required.

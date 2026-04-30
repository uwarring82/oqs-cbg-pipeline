---
plan_id: dg-1-work-plan
version: v0.1.2
date: 2026-04-30
type: work-plan
anchor_sail: sail/sail-cbg-pipeline_v0.5.md §§4, 5, 9 (DG-1), 10 (Risks #6, #8), 11
anchor_ledger: ledger/CL-2026-005_v0.4.md Entries 1, 3, 4 (COMPATIBLE)
anchor_envelope: docs/validity_envelope.md DG-1 row (NOT YET ATTEMPTED → target PASS)
status: active
supersedes: dg-1-work-plan_v0.1.1.md
license: CC-BY-4.0 (LICENSE-docs)
---

# DG-1 Work Plan — Numerical reproduction of CL-2026-005 v0.4 Entries 1, 3, 4

## 1. Objective

Pass DG-1 as defined in Sail v0.5 §9:

> *Pass if Entries 1, 3, and 4 of CL-2026-005 are reproduced numerically.*

This plan operationalises that objective in **benchmark-cards-first** ordering: a benchmark-card YAML schema is drafted, three filled cards (one per Entry) are committed with frozen parameters *before any scientific-implementation module body exits `NotImplementedError`*, implementation work is then derived from the cards, and DG-1 is decided by running the pipeline against the cards' acceptance criteria. The ordering is a direct mitigation of Sail v0.5 §10 Risk #6 (*"building a codebase before defining benchmark cards"*) and Risk #8 (*"overfitting the pipeline to known solvable models"*).

The qualifier "scientific-implementation module body" matters: the v0.1.0 scaffold already contains executable Python that is *not* scientific implementation — package import-time protective-doc checks ([cbg/__init__.py:34-53](../cbg/__init__.py#L34-L53)), failure-mode label constants ([cbg/diagnostics.py:26-38](../cbg/diagnostics.py#L26-L38)), and `structural_constraints` tuples in `models/`. Those are scaffolding, not science, and are exempt from the cards-first rule. The rule applies to functions whose body would execute the CBG construction.

DG-1 does **not** require structural-identity stacking (that is DG-2), nor cross-method validation (DG-3), nor failure-envelope characterisation (DG-4), nor thermodynamic-discriminant computation (DG-5). The acceptance criterion is *numerical reproduction* of each Entry's predicted result against an analytical or paper-cited reference, within a tolerance frozen in the card.

### 1.1 Reading of "reproduced numerically"

Sail §9 DG-1 says only "*Pass if Entries 1, 3, and 4 of CL-2026-005 are reproduced numerically.*" That sentence is ambiguous on two axes: *which sub-claims* (just the headline structural result, or every *Predictions / consequences* sub-claim B.1, B.2, B.3 in each Entry?) and *to what order* (the headline result for Entries 3 and 4 is "at all orders"; reproducing it numerically requires a perturbative cap).

This plan adopts a **bounded-maximalist** reading on both axes:

- **Sub-claims:** every B-prediction listed for each Entry in CL-2026-005 v0.4 is targeted by its card. A minimalist reading that reproduced only the trivial sub-case (e.g. K(t) = (ω/2) σ_z under a thermal bath, without ever exercising the contrasting non-thermal case where the time-dependent shift appears) would weaken the validity envelope relative to the Ledger's actual content.
- **Order:** each card freezes a finite perturbative cap *N_card* (Phase B) and verifies the B-predictions *up to that cap*. The Ledger's "at all orders" structural claims (notably Entry 4's "K(t) ∝ σ_z at all orders" and Entry 3's "K_2m = 0 at all orders") are not directly numerically verifiable; what DG-1 verifies is that the claim **holds at every computed order ≤ N_card**. The all-order character of the analytical proof is acknowledged but not gated by DG-1; gating it would require either symbolic verification (out of scope) or unbounded numerical search (intractable).

The bounded-maximalist reading is what a non-conflicted reader would treat as the operational meaning of "reproduced numerically": every B-prediction is exercised, every order *for which the pipeline computes K_n* satisfies the predicted structure, and the cap *N_card* is recorded explicitly in the card's `frozen_parameters:` block. A future steward who finds the structure violated at order *N_card + 1* would log a DG-2 finding (or a DG-4 failure-envelope finding, depending on cause), not retroactively invalidate the DG-1 PASS — the envelope's authorisation scope is bounded by the cap.

### 1.2 Minimum perturbative order

DG-1 cards execute the TCL recursion at the **minimum order N_card** sufficient to exercise every B-prediction in the corresponding Entry. The defaults this plan prescribes (cards may freeze higher caps if the steward judges fit, but not lower):

- **Card A1 (Entry 1):** N_card = 0. Entry 1's claim is a closed-form algebraic expression for K from L (Letter Eqs. (6)–(7)); no perturbative recursion is needed. The three B-predictions (canonical-Lindblad recovery, Markovian Lamb shift, pseudo-Kraus reduction) are each direct evaluations of the closed form.
- **Card A3 (Entry 3):** N_card = 2. Entry 3.B.1 (K(t) = (ω_r(t)/2) σ_z) is a structural statement; Entry 3.B.2 (thermal-bath trivialisation to (ω/2) σ_z, no renormalisation) holds trivially at every order; Entry 3.B.3 (time-dependent shift for non-thermal bath) is a second-order observable. N_card = 2 lets all three be exercised without entering DG-2 territory.
- **Card A4 (Entry 4):** N_card = 2. Same structure: Entry 4.B.1 (no eigenbasis rotation for thermal bath) holds at every order; Entry 4.B.2 (eigenbasis rotation for non-thermal bath, where odd cumulants are nonzero) is a second-order observable per Letter Eqs. (D.4)–(D.6).

Higher-order recursion (N ≥ 3) is DG-2 territory. Modules `cbg/cumulants.py` and `cbg/tcl_recursion.py` are implemented only along the code paths Cards A3/A4 exercise at orders ≤ 2; higher-order paths remain stubbed and raise `NotImplementedError`.

The cards' acceptance criteria record N_card as a frozen parameter and verify the B-predictions order-by-order *up to N_card*. A card whose order-cap is later raised (e.g. to N_card = 4 in DG-2 work) is a *new card* per the supersedure discipline; the DG-1 card with N_card = 2 is retained as historical record.

## 2. Scope

### 2.1 In scope

- Benchmark-card YAML schema artefact (`benchmarks/benchmark_cards/SCHEMA.md` and an example `.yaml` template `benchmarks/benchmark_cards/_template.yaml`).
- Three DG-1 benchmark cards (`A1`, `A3`, `A4`), one per Ledger Entry, each with a frozen-parameter block and an empty result block.
- Implementation of the modules each card depends on:
  - `cbg/basis.py`, `cbg/effective_hamiltonian.py`, `cbg/cumulants.py` (low-order paths only), `cbg/bath_correlations.py`, `cbg/tcl_recursion.py` (low-order paths only)
  - `models/pure_dephasing.py`, `models/spin_boson_sigma_x.py`
  - `numerical/time_grid.py`, `numerical/tensor_ops.py`
  - `reporting/benchmark_card.py` (card loader, runner, result-block writer, and gauge-annotation enforcement on emitted artefacts)

  `cbg/diagnostics.py` is **not** implemented at DG-1: its sole non-trivial deliverable (basis-independence cross-check) is the universal-default DG-2 structural-identity check per Sail §9 DG-2. Computing K(t) in two distinct bases and asserting agreement is the *operation* DG-2 gates; relabelling it a "smoke check" at DG-1 would either duplicate DG-2 or erode the gate distinction. DG-1 cards therefore evaluate K(t) in a single canonical basis (matrix-unit) and verify against an analytical reference; cross-basis verification is deferred to DG-2.
- DG-1 verdict logbook entry (`logbook/YYYY-MM-DD_dg-1-{pass,fail-with-cause}.md`).
- Validity-envelope update (`docs/validity_envelope.md`) on verdict.
- Repository tag `v0.2.0` on PASS, or no tag on FAIL.

### 2.2 Out of scope

- Entry 2 (recursive perturbative series, scope-limited): convergence is open per Ledger constraints; full reproduction belongs to DG-2.
- Entry 5 (parity structure, FDT): DG-2 territory at higher orders. Entry 5's second-order FDT decomposition concerns the *parity structure* of K_2 and is naturally adjacent to Cards A3/A4 (which evaluate K_n for spin-bath models at orders ≤ 2), not Card A1 (which is the closed-form algebraic check at order 0). Even at second order, however, Entry 5's discriminant content — identifying the FDT structure within K_2 rather than merely computing K_2 — is reserved for DG-2 and not gated by DG-1. DG-1 cards do not assert anything about Entry 5.
- Entry 6 (trapped-ion validation): empirical, with self-reference flag; not reproducible by this repository at any DG.
- Entry 7 (thermodynamic interpretation): DG-5 territory; routes via fresh Council deliberation.
- Models `models/jaynes_cummings.py` and `models/fano_anderson.py`: DG-2/DG-5 venues.
- Cross-method benchmarking via `benchmarks/exact_finite_env.py` and `benchmarks/qutip_reference.py`: DG-3 territory; stubs remain `NotImplementedError` at DG-1.

### 2.3 Explicit non-claims

DG-1 PASS does **not** establish:
- That the CBG construction is correct in regimes beyond those exercised by Cards A1, A3, A4.
- That the implementation is free of numerically-stable-but-wrong errors (DG-2 catches that class).
- That the Hayden–Sorce gauge is the right gauge (DG-5 territory; gauge annotation per `docs/benchmark_protocol.md` §1 is mandatory regardless).

### 2.4 Lacunae in this plan revision (intentional)

The following are deliberately left under-specified at v0.1.0; they are populated when Phase B authors the actual cards, not retrofitted into this plan:

- Concrete frozen-parameter values for Cards A3 and A4 (perturbative order, time grid, integration tolerance, spectral cutoff, bath temperature, displacement amplitude). The values shown in §4 are illustrative scaffolding only.
- The exact analytical-reference expressions Cards A1, A3, A4 compare against (the Ledger Entries cite the equations; the cards must transcribe them with explicit symbol-mapping).
- The tolerance values (10⁻¹⁰ for A1 is illustrative; A3, A4 tolerances depend on the chosen integration scheme).

A future plan revision (`dg-1-work-plan_v0.1.1.md`) populates these once Phase A's schema is finalised, *if* the values turn out to depend on schema decisions; otherwise the cards themselves are the canonical record and no plan revision is required.

## 3. Approach: benchmark-cards-first

```
        Phase A                Phase B                Phase C                Phase D
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │ Card schema  │ ───▶ │ 3 DG-1 cards │ ───▶ │ Module impl  │ ───▶ │ Run + verdict│
   │ + template   │      │ frozen-param │      │ derived from │      │ + envelope   │
   │              │      │ blocks       │      │ cards        │      │ + tag/log    │
   └──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
       (no code)            (no code)            (cards drive)         (no new code)
```

The hard rule: **no scientific-implementation function body exits `NotImplementedError` until the three cards are committed.** Scaffolding code that already exists at HEAD (import-time protective-doc checks, failure-mode label constants, model `structural_constraints` tuples — see §1) is exempt: it does not execute the CBG construction. This keeps Risk #8 mitigation operative — a future steward can audit, from `git log --diff-filter=A -- cbg/` against `git log -- benchmarks/benchmark_cards/`, that no CBG-construction function existed at HEAD before the cards' frozen-parameter blocks did.

## 4. Phases

### Phase A — Benchmark-card schema (no code)

**Inputs.** `docs/benchmark_protocol.md` §1 (gauge annotation), §4 (parameter freezing).

**Outputs.**

1. `benchmarks/benchmark_cards/SCHEMA.md` — human-readable specification of the card schema, with field definitions, required vs optional, and validation rules. Co-located with the cards themselves rather than in `docs/`, since `docs/` is reserved for the five protective-scaffolding files named in Sail v0.5 §11; the schema is operational specification, not protective scaffolding.
2. `benchmarks/benchmark_cards/_template.yaml` — machine-readable template carrying the schema by example, including:
   - Top-level metadata (`card_id`, `version`, `date`, `dg_target`, `ledger_entry`, `model`, `status`).
   - `gauge:` block (per `docs/benchmark_protocol.md` §1 machine-readable annotation).
   - `frozen_parameters:` block (model, truncation, numerical, comparison sub-blocks per `docs/benchmark_protocol.md` §4.1).
   - `acceptance_criterion:` block (reference, observable, error metric, threshold, projection scheme if any).
   - `result:` block (empty at draft time; populated post-run with `verdict`, `evidence`, `commit_hash`, `runner_version`).
   - `failure_mode_log:` block (empty at draft time; appended on revisions per `docs/benchmark_protocol.md` §4.3).
   - `stewardship_flag:` block (carries forward Entry-level flags; for DG-1 cards, all three Entries are unflagged, but the field is present and explicit).

**Acceptance criterion (Phase A).** A non-conflicted reader can, from the schema document and template alone, write a syntactically valid card without consulting source files.

**Logbook entry on completion.** `logbook/YYYY-MM-DD_benchmark-card-schema-drafted.md`. The repo-init logbook anticipates this entry under the working name `benchmark-protocol-schema-drafted` ([logbook/2026-04-29_repo-init.md:64](../logbook/2026-04-29_repo-init.md#L64)); this plan adopts the more accurate `card-schema` form, since the artefact is a *new* schema document for benchmark cards, not a revision of the existing `docs/benchmark_protocol.md`. The repo-init logbook's "next anticipated entries" list is anticipatory and non-binding; an in-place correction of an immutable logbook entry is not permitted, and a superseding logbook entry is not warranted for a non-load-bearing naming preference. The plan-side name governs.

The repo-init logbook also lists `dg-1-attempt-began` *before* the schema-drafted entry. This plan reverses that order: schema-drafted comes before any attempt, since the cards-first ordering makes "attempt" a notion only after Phase B is committed.

### Phase B — Three DG-1 benchmark cards (no code)

Each card is a standalone YAML file in `benchmarks/benchmark_cards/`, populated through the `frozen_parameters` and `acceptance_criterion` blocks; the `result` block is left empty until Phase D.

#### Card A1 — Entry 1: operational K(t) form

- **Anchor.** CL-2026-005 v0.4 Entry 1; Letter Eqs. (6)–(7).
- **Reproduction targets** (per Entry 1.B):
  1. Canonical Lindblad input with traceless jump operators → K returns the original Hamiltonian term.
  2. Markovian weak-coupling generator → K reproduces standard Lamb shift.
  3. Pseudo-Kraus representation L[X] = Σ_i ω_ii V_i X V_i† → K reduces to the diagonal Hayden–Sorce 2022 expression.
- **Frozen parameters** (illustrative scaffolding only — actual values are populated in the YAML card during Phase B; see §2.4):
  - System dimension d ∈ {2, 3} (small enough to evaluate the basis-independent sum directly).
  - Hilbert–Schmidt operator basis: matrix-unit basis {|j⟩⟨k|} (single basis; cross-basis verification is DG-2 territory and is not exercised here).
  - Tolerance: relative Frobenius-norm error vs analytical reference, threshold ≤ 10⁻¹⁰.
- **Modules touched.** `cbg/basis.py`, `cbg/effective_hamiltonian.py`, `numerical/tensor_ops.py`.
- **Reporting.** Card-level report carries the gauge annotation per `docs/benchmark_protocol.md` §1.

#### Card A3 — Entry 3: pure dephasing structural result

- **Anchor.** CL-2026-005 v0.4 Entry 3; Letter Eq. (19), Letter Appendix D.
- **Reproduction targets** (per Entry 3.B):
  1. K(t) = (ω_r(t)/2) σ_z (no environment-induced eigenbasis rotation).
  2. For thermal bosonic bath (Fock-diagonal initial state): K(t) = (ω/2) σ_z exactly, no renormalisation, recovering the standard spin–boson exact result (Łuczka 1990; Doll et al. 2008; Leggett et al. 1987).
  3. Time-dependent shift when odd-order bath cumulants are nonzero (e.g. coherently-displaced bath): demonstrated as a sweep showing nonzero ω_r(t) − ω.
- **Frozen parameters** (illustrative scaffolding only — see §2.4):
  - H_S = (ω/2) σ_z; A = σ_z; bath: linearly-coupled bosonic, ohmic spectral density, finite cutoff; bath state: thermal at temperature T (target ½) and a coherently-displaced state (target 3).
  - Perturbative order: minimum order needed to demonstrate B-predictions (expected: order 0 for the thermal trivial case; order ≤ 2 for the non-thermal contrast case).
  - Time grid, integration tolerance, spectral cutoff: populated in card during Phase B.
  - Acceptance: ω_r(t) − ω = 0 within tolerance for thermal case (target 2); ω_r(t) − ω ≠ 0 within sensitivity for displaced case (target 3); K(t) ∝ σ_z at machine precision (target 1).
- **Modules touched.** `models/pure_dephasing.py`, `cbg/effective_hamiltonian.py`, `cbg/cumulants.py` (orders ≤ 2 only), `cbg/bath_correlations.py`, `cbg/tcl_recursion.py` (orders ≤ 2 only), `numerical/time_grid.py`.

#### Card A4 — Entry 4: σ_x thermal-bath result

- **Anchor.** CL-2026-005 v0.4 Entry 4; Letter Eqs. (D.4)–(D.6); Letter Eq. (22).
- **Reproduction targets** (per Entry 4.B):
  1. K(t) ∝ σ_z (no eigenbasis rotation) for thermal bosonic bath with orthogonal coupling A = σ_x.
  2. Eigenbasis rotation when odd-order bath cumulants are nonzero (e.g. coherent displacement, non-equilibrium preparation): demonstrated as a sweep.
- **Frozen parameters** (illustrative scaffolding only — see §2.4):
  - H_S = (ω/2) σ_z; A = σ_x; bath: thermal bosonic, ohmic, finite cutoff; non-thermal comparison state for target 2.
  - Perturbative order: minimum order needed to demonstrate B-predictions (expected: order ≤ 2; the parity-class result of Letter Eqs. (D.4)–(D.6) is a second-order statement).
  - Time grid, integration tolerance, spectral cutoff: populated in card during Phase B.
  - Acceptance: rotation angle θ(t) of K(t)'s eigenbasis relative to σ_z basis ≤ tolerance for thermal case; θ(t) > sensitivity threshold for non-thermal case.
- **Modules touched.** `models/spin_boson_sigma_x.py`, `cbg/effective_hamiltonian.py`, `cbg/cumulants.py` (orders ≤ 2 only), `cbg/bath_correlations.py`, `cbg/tcl_recursion.py` (orders ≤ 2 only), `numerical/time_grid.py`.

**Acceptance criterion (Phase B).** Three card files committed, each with top-level `status: frozen-awaiting-run` (single hyphenated token; this is the YAML key value the Phase A schema enumerates). No card has a populated `result:` block. Validation at this phase is by hand-inspection plus a third-party YAML linter (`yamllint`); schema-conformance via `reporting/benchmark_card.py` happens in Phase C — Phase B does *not* depend on Phase C tooling existing.

**Phase-B commit hash recording.** The Phase B commit hash is *not* recorded in a separate tracking file. It is the natural output of `git log --diff-filter=A -- benchmarks/benchmark_cards/A1_*.yaml benchmarks/benchmark_cards/A3_*.yaml benchmarks/benchmark_cards/A4_*.yaml`. The Phase D logbook entry runs that command and quotes the resulting hashes; no out-of-band tracking is required, satisfying the "no out-of-band knowledge" criterion in §5 (FAIR — Reusable).

**Logbook entry on completion.** Optional: `logbook/YYYY-MM-DD_dg-1-cards-frozen.md` (recommended, since this is the moment that Risk #8 mitigation becomes auditable).

### Phase C — Module implementation (cards drive)

Implement only what the three cards require, in the order their dependencies fall out:

| Order | Module | Driven by |
|---|---|---|
| C.1 | `cbg/basis.py` (matrix-unit basis only) | Card A1 |
| C.2 | `numerical/tensor_ops.py` | Card A1 |
| C.3 | `cbg/effective_hamiltonian.py` (operational form only, single-basis evaluation) | Card A1 |
| C.4 | `reporting/benchmark_card.py` (loader, runner, result-block writer, gauge-annotation enforcement) | All three cards |
| C.5 | `numerical/time_grid.py` | Cards A3, A4 |
| C.6 | `cbg/bath_correlations.py` | Cards A3, A4 |
| C.7 | `cbg/cumulants.py` (orders ≤ 2 only) | Cards A3, A4 |
| C.8 | `cbg/tcl_recursion.py` (orders ≤ 2 only) | Cards A3, A4 |
| C.9 | `models/pure_dephasing.py` | Card A3 |
| C.10 | `models/spin_boson_sigma_x.py` | Card A4 |

`cbg/tcl_recursion.py` and `cbg/cumulants.py` are implemented *only at the orders the cards require*. Higher-order code paths remain stubbed and are DG-2 territory. `cbg/diagnostics.py` is **not** implemented at DG-1 (see §2.1: cross-basis verification is the DG-2 universal-default check).

`reporting/benchmark_card.py` is promoted to early in Phase C (C.4) because all three cards depend on it for runner dispatch and gauge-annotation enforcement; deferring it to last would force re-running every card after the runner lands. The gauge-annotation-enforcement scope listed here matches the §2.1 in-scope description.

`tests/test_imports.py` continues to verify structural compliance; additional smoke tests are added per module as implementation lands, but no DG-2 structural-identity tests are introduced here.

**Acceptance criterion (Phase C).** All three cards can be loaded by `reporting/benchmark_card.py` and dispatched to a runnable pipeline; no module touched by a card still raises `NotImplementedError` at any code path the card exercises; gauge annotation is mechanically attached to all card-emitted artefacts; CI green.

### Phase D — Run, verdict, validity-envelope, tag

The validity envelope's update protocol ([docs/validity_envelope.md:56-62](../docs/validity_envelope.md#L56-L62)) requires that (i) the triggering evidence is committed *before* the envelope is updated, and (ii) the envelope update lands in the *same* commit as the logbook status-change entry. The plan operationalises this as **two sequential commits**:

**Commit D.1 — Run results.** Populate each card's `result:` block with `verdict ∈ {PASS, FAIL, CONDITIONAL}`, evidence (numerical outputs, plot paths), and `runner_version`. The `commit_hash` field of each card's `result:` block is left empty in the working tree, then filled by the steward to the actual D.1 commit hash via `git commit --amend` immediately after the initial commit creates the hash. (This amend is permitted: D.1 is a verdict commit that has not yet been pushed; once pushed, the cards are immutable. The amend is the only way to satisfy the YAML-self-reference without a tracking file.)

**Commit D.2 — Logbook entry + envelope update, atomically.** Write logbook entry `logbook/YYYY-MM-DD_dg-1-{pass,fail-with-cause}.md` per `logbook/README.md` conventions; its `Triggering commit:` field references the D.1 hash. Update `docs/validity_envelope.md` DG-1 row in the same commit: `NOT YET ATTEMPTED` → `PASS` (with evidence pointers to D.1) or `FAIL` (with cause label and pointers). Per the envelope's protocol step 4, the commit message includes the DG identifier — this plan prescribes the format `DG-1: <pass|fail-with-cause> — Cards A1, A3, A4 reproduced` (or for FAIL, the cause-label per Sail §9 DG-4 cause-label discipline). The format is a plan-level prescription, not a quote from the envelope; the envelope only requires *some* DG identifier in the message.

**Tag D.3 (PASS only).** Tag `v0.2.0` annotated against the D.2 commit, with message `DG-1: pass — repository validity envelope expanded to cover Entries 1, 3, 4`. **No tag is created on FAIL.**

The tag message intentionally differs from the D.2 commit message ("Cards A1, A3, A4 reproduced"). The commit message records *what was done in this commit* (run results landed; envelope updated; logbook entry written). The tag message records *what the tag means at the validity-envelope layer* (the envelope's authorisation scope expanded to cover three Ledger Entries at the frozen N_card cap). Both messages are canonical for their respective consumers — `git log` for commit messages, `git tag -n` and Zenodo deposition metadata for tag messages.

**Verdict computation.**
- **DG-1 PASS** if all three cards verdict = PASS.
- **DG-1 FAIL-WITH-CAUSE** otherwise; cause label drawn from the Sail §9 DG-4 taxonomy (convergence_failure / tcl_singularity / projection_ambiguity / truncation_artefact / benchmark_disagreement) or, if none fits, recorded as a new failure mode with explicit text.

**Acceptance criterion (Phase D).** A future, non-conflicted steward can, from the public repo at HEAD, reconstruct the Phase A schema, the Phase B frozen cards, the Phase C implementation history, and the Phase D verdict + envelope state, without recourse to side-channel notes. On PASS this set includes the `v0.2.0` tag; on FAIL the set is artefact-complete *without* the tag.

## 5. FAIR alignment

The plan, the schema artefact, the cards, and the result artefacts are designed to satisfy the FAIR principles (Wilkinson et al. 2016) at every stage of execution.

### F — Findable

- The plan lives at a stable path (`plans/dg-1-work-plan_v0.1.0.md`); subsequent revisions are new files (`v0.1.1`, `v0.2.0`, …) with `supersedes:`/`superseded_by:` cross-links, not in-place content edits.
- The plan, schema, and cards are indexed: [plans/README.md](../plans/README.md) (operational status), [benchmarks/benchmark_cards/README.md](../benchmarks/benchmark_cards/README.md) (will be extended in Phase A with a pointer to `SCHEMA.md` and `_template.yaml`, and in Phase B with a card index). [docs/README.md](../docs/README.md) is *not* extended — its scope is locked to the five protective files per Sail v0.5 §11.
- Every artefact carries rich front-matter metadata (id, version, date, anchors, status-as-of-commit), making each searchable by attribute, not just by filename.
- The repository's top-level `README.md`, `CITATION.cff`, `codemeta.json`, `.zenodo.json` provide cross-discovery from external indexes once an archival snapshot is minted (after DG-1 PASS, the `v0.2.0` git tag is the natural Zenodo anchor).

### A — Accessible

- The repository is public on GitHub (`https://github.com/uwarring82/oqs-cbg-pipeline`), retrievable over HTTPS without authentication.
- All plan, schema, card, and result artefacts are plain text (Markdown, YAML); no proprietary binary formats are introduced.
- License: code under `LICENSE` (MIT or repository-default; verify in `LICENSE`), documentation under `LICENSE-docs` (CC-BY-4.0). The plan inherits CC-BY-4.0 explicitly via its front-matter `license:` field.
- Once the v0.2.0 archival snapshot is minted, the Zenodo deposition (per `.zenodo.json`) provides a persistent DOI that does not depend on GitHub's continued availability.

### I — Interoperable

- Cards use YAML, a widely supported, machine-readable format with an explicit schema document.
- Cross-references use stable, repository-relative paths (`sail/...`, `ledger/...`, `benchmarks/benchmark_cards/...`), not fragile URLs.
- Vocabulary aligns with Sail and Ledger anchors (§-numbered Sail sections, Entry-numbered Ledger references), enabling unambiguous cross-walks between the protective layer and the operational layer.
- The gauge-annotation block (per `docs/benchmark_protocol.md` §1) is structured with explicit fields (`gauge`, `coordinate_dependent`, `direct_observable`, `gauge_alignment_required_for_comparison`), so a downstream tool can verify gauge-consistency mechanically rather than by prose inspection.

### R — Reusable

- Provenance is explicit at every layer: the plan anchors to Sail v0.5 and CL-2026-005 v0.4; the schema anchors to `docs/benchmark_protocol.md`; cards anchor to specific Ledger Entries; results anchor to commit hashes and runner versions.
- Versioning is explicit and consistent across plan (semver), schema (versioned in front-matter), cards (version field), and repository (git tags).
- The parameter-freezing protocol (per `docs/benchmark_protocol.md` §4) ensures that any third party can reproduce a result by checking out the commit referenced in the card's `result:` block and re-running with the card's `frozen_parameters:` block — no out-of-band knowledge is required.
- License clarity (CC-BY-4.0 docs, code license per LICENSE) permits redistribution and adaptation with attribution; this is consistent with the repository's `do_not_cite_as.md` constraint, which restricts *interpretive citation*, not *technical reuse*.
- Stewardship-conflict propagation: although DG-1's three Entries are unflagged, the `stewardship_flag:` field is present on every card to ensure that flag-propagation discipline (per `docs/stewardship_conflict.md`) is mechanically enforced and audit-traceable.

## 6. Risks and deviations

Inherited from Sail v0.5 §10 with mitigations specific to DG-1:

| Sail Risk | Concrete DG-1 manifestation | Mitigation in this plan |
|---|---|---|
| #1 (gauge reification) | Treating K(t) as the "physical Hamiltonian" in card output | Mandatory gauge annotation on every card-emitted artefact (Phase A schema enforces; Phase C `reporting/benchmark_card.py` checks at write time) |
| #5 (hiding failures behind smooth plots) | Plot-level smoothing masking divergence in Card A3/A4 sweeps | Cards specify the *raw* observable + tolerance, not a plotted-then-eyeballed quantity |
| #6 (codebase before cards) | Implementing modules before cards exist | Phase B hard rule (§3): no scientific-implementation function exits `NotImplementedError` until the three cards are committed |
| #8 (overfitting to solvable models) | Tuning truncation/cutoff/step until known results match | Frozen-parameter discipline (Phase B); post-hoc adjustment requires a new card with `failure_mode_log` entry, never silent revision (per `docs/benchmark_protocol.md` §4.3) |

Risks #2, #3, #4, #7 are not load-bearing on DG-1 (they apply at DG-2 and beyond) but the plan does not weaken them.

### Deviation policy

If during Phase C an Entry's reproduction proves infeasible at the frozen parameters, the card is **not** silently retuned. Two paths are permitted:

- **Path 1 (preferred).** A new card supersedes the original, with the original retained and annotated `superseded by <new-card-id>`. The plan version increments (`v0.1.0` → `v0.1.1` if the structure is unchanged; `v0.2.0` if the approach changes).
- **Path 2 (failure verdict).** The original card is run, the result is `FAIL`, and DG-1 is verdicted FAIL-WITH-CAUSE per Phase D. This is not a setback — it is exactly the kind of evidence the validity envelope is designed to record.

## 7. Dependencies

- `docs/benchmark_protocol.md` (already at HEAD; v0.1.0 baseline).
- `docs/validity_envelope.md` (already at HEAD; will be edited by Phase D).
- `docs/stewardship_conflict.md`, `docs/do_not_cite_as.md`, `docs/endorsement_marker.md` (already at HEAD; not edited by this plan).
- `sail/sail-cbg-pipeline_v0.4.md` (already at HEAD; not edited by this plan).
- `ledger/CL-2026-005_v0.4.md` (already at HEAD; immutable; consulted, never edited).
- `LICENSE-docs` (CC-BY-4.0; covers plan, schema, cards-as-prose, logbook entries).

No external services are required for DG-1 PASS. (The Zenodo deposition referenced under FAIR-Accessible is an *optional* archival step post-PASS, not a prerequisite.)

## 8. Estimated effort and sequencing

This plan is intentionally not time-bound (Risk #8 mitigation: time pressure encourages overfitting). A coarse sequencing for the steward's planning, assuming Card A1 is implemented first (least dependencies) before A3/A4 (which share `cbg/cumulants.py`, `cbg/tcl_recursion.py`, `cbg/bath_correlations.py`, `numerical/time_grid.py`):

1. Phase A (schema + template): 1 working session.
2. Phase B (three cards): 1–2 working sessions.
3. Phase C (module implementation):
   - C.1–C.4 (Card A1 chain + runner): ~1 session, dominated by `cbg/effective_hamiltonian.py` and `cbg/basis.py`.
   - C.5–C.10 (Cards A3/A4 chain): ~2–4 sessions, dominated by `cbg/cumulants.py` (orders ≤ 2) and `cbg/bath_correlations.py`. `cbg/tcl_recursion.py` is exercised but its DG-1 surface is small (orders ≤ 2 only); the module is dominant in *DG-2* effort, not DG-1.
4. Phase D (run + verdict + envelope + tag): 1 working session, plus iteration if FAIL.

### 8.1 Plan status field

The `status:` field in the front-matter is set at commit time and reflects the plan's status *as of that commit*. The current revision (`v0.1.0`) is committed at `status: draft`. There is no in-place transition to `active`: post-commit, the file is content-immutable per `plans/README.md`. The plan's *operational* status (which version is canonical-current and at which phase) is tracked in the `plans/README.md` index, not in the individual plan files. This separates the audit-stable record (the file) from the working-status pointer (the index), which is the pattern used by the validity envelope and the logbook index.

### 8.2 Version-namespace discipline

The plan version (`v0.1.0`, `v0.1.1`, …) shares numeric form with the repository tag (`v0.1.0`, `v0.2.0`, …) but **not** namespace. To prevent ambiguous reference:

- A bare `v0.2.0` always refers to the **repository tag** (the convention used by git, GitHub, and Zenodo).
- Plan revisions are referred to by full filename (`dg-1-work-plan_v0.2.0.md`) or by qualified phrase ("plan v0.2.0" / "plan revision v0.2.0").
- It is permissible (and likely) for plan version and repo tag version to drift independently: a mid-execution plan revision to `dg-1-work-plan_v0.2.0.md` does not imply repo tag `v0.2.0`, and conversely a DG-1 PASS tagging the repo at `v0.2.0` does not bump the plan version.

## 9. Acceptance criterion (whole plan)

DG-1 verdict is recorded — PASS or FAIL-WITH-CAUSE — in three artefacts that exist on **both** verdict paths, plus one tag artefact that exists **only on PASS**:

| Artefact | PASS | FAIL-WITH-CAUSE |
|---|---|---|
| Three cards' `result:` blocks (`benchmarks/benchmark_cards/A1*.yaml`, `A3*.yaml`, `A4*.yaml`) | required | required |
| Logbook entry `logbook/YYYY-MM-DD_dg-1-{pass,fail-with-cause}.md` | required | required |
| `docs/validity_envelope.md` DG-1 row updated | required | required |
| Annotated git tag `v0.2.0` | required | **not created** |

The plan itself is acceptance-criterion-satisfying when the path-appropriate set of artefacts exists at HEAD with mutually consistent commit hashes (per the two-commit pattern in §4 Phase D).

## 10. Routing notes

This plan does not modify the Sail and does not modify the Ledger. It schedules and orders steward work that is bounded by both. If during execution any finding bears on CL-2026-005 (e.g. discovers an inconsistency in an Entry that this plan was meant to merely reproduce), the routing rule is: **do not edit the Ledger; route via fresh Council deliberation per Sail v0.5 §0 and §9 DG-5.** A repository-level finding that bears on the Ledger triggers a logbook `discussion-outcome` entry and a Council convocation request, never a direct edit.

If during execution any finding bears on the Sail (e.g. the §11 minimal-implementation scaffold proves structurally inadequate for one of the cards), the routing rule is: **steward authors a Sail revision, with substantive Ledger-bearing content routed via Council per §0.** The plan itself may be revised freely.

---

## Revision history

- **v0.1.0 (2026-04-29).** Initial draft. Established four-phase benchmark-cards-first ordering, DG-1/DG-2 boundary (no `cbg/diagnostics.py` cross-basis check at DG-1), maximalist sub-claim reading, two-commit Phase D pattern, version-namespace discipline, lacunae section, FAIR alignment.
- **v0.1.1 (2026-04-30).** Steward supersedure following second-pass audit:
  - **Bounded-maximalist reading (§1.1).** Maximalist sub-claim reading retained; explicit perturbative cap *N_card* added per card. Reproduction is "every B-prediction at every order ≤ N_card", not "every B-prediction at all orders". The Ledger's "at all orders" structural claims are acknowledged as analytical proofs that DG-1 verifies up to N_card; unbounded numerical verification is intractable, symbolic verification is out of scope. The cap is recorded as a frozen parameter in each card.
  - **N_card defaults (§1.2).** Per-card minimum: A1 = 0 (closed-form algebraic), A3 = 2 (parity-driven structure observable at second order), A4 = 2 (eigenbasis-rotation observable at second order). Higher caps are explicitly DG-2 territory.
  - **Entry 5 boundary (§2.2).** Removed the suggestion that Card A1 might "incidentally exercise" Entry 5. Card A1 is the order-0 closed-form check; Entry 5's parity-FDT content lives near A3/A4, and even there is reserved for DG-2.
  - **Tag-vs-commit message rationale (§4 Phase D).** Added one-paragraph rationale for why the tag and commit messages differ.
  - **Anchor bump (front matter).** Sail anchor v0.4 → v0.5; `supersedes:` field set to `dg-1-work-plan_v0.1.0.md`.
- **v0.1.2 (2026-04-30, this revision).** Steward supersedure to relocate the schema artefact and engage the plan:
  - **Schema location.** `docs/benchmark_card_schema.md` → `benchmarks/benchmark_cards/SCHEMA.md`. `docs/` is locked to the five protective-scaffolding files per Sail v0.5 §11; the schema is operational specification, not protective. Co-locating with the cards themselves keeps the operational artefacts together. Phase A logbook entry (`benchmark-card-schema-drafted`) records the same rationale.
  - **Operational status engaged.** Front-matter `status:` set to `active` (was `draft` in v0.1.0 / v0.1.1). Plans index updated to mark v0.1.2 as active / Phase A.
  - **Anchor bump (front matter).** `supersedes:` set to `dg-1-work-plan_v0.1.1.md`. No other substantive content changes.

---

*End of DG-1 Work Plan v0.1.2. Steward-authored; revisable. No Council clearance required. CC-BY-4.0 (LICENSE-docs).*

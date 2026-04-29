# Sail — Towards a Decision-Forcing Numerical Pipeline for Non-Markovian Open Quantum Dynamics

**Version:** v0.5 (Cardinality-fix; supersedes v0.4)
**Layer:** Sail
**Status:** Draft scaffold (Sails do not require Council clearance; local stewardship discipline applies)
**Anchor:** CL-2026-005 v0.4 (active immutable Ledger entry, Council-cleared 2026-04-29)
**Steward:** U. Warring
**Purpose:** Motivate and structure a numerical programme based on the Colla–Breuer–Gasbarri (CBG) recursive effective-Hamiltonian framework, benchmarked against established open-system methods, with explicit decision gates that determine the validity envelope of the construction.

---

## 0. Endorsement Marker

This Sail is an interpretive and programme-setting document. It is not a Ledger entry, not a coastline, and not a validation claim. It uses CL-2026-005 v0.4 as a stable input but does not promote any Ledger classification beyond its stated scope.

This Sail does not modify any Ledger entry. Findings that bear on CL-2026-005 — notably any DG-5 outcomes affecting Entry 7's UNDERDETERMINED classification — are routed via a fresh Council deliberation, not via Sail revision. The Sail's relationship to the Ledger is unidirectional consumption: the Ledger informs the Sail; the Sail does not edit the Ledger.

The Sail inherits the Council-cleared protective measures from CL-2026-005 v0.4: the "Do not cite as" guard (G1) and the steward-conflict triple-flagging on Entry 6. Both are reflected in §5 Tier 4 and in the repository scaffold (§11).

The term "Decision-Forcing" in the title refers to validity-envelope determination — i.e. the pipeline forces decisions about *when* the CBG construction is reliable, *when* it breaks down, and *how* it compares with established methods. It does *not* mean "decisively superior to alternative frameworks". Framework adjudication is out of scope per CL-2026-005 Entry 7.

---

## 1. Opening thesis

Once the minimal-dissipation gauge is chosen, the Colla–Breuer–Gasbarri construction turns the residual ambiguity in the coherent/dissipative split of a time-convolutionless (TCL) generator into a constructive computational target: the coherent part K(t) becomes calculable order by order, and the canonical Lindblad form is preserved at every order.

The next challenge is numerical. Can this recipe be turned into a robust, benchmarked platform that tells us when the effective-Hamiltonian description is reliable, when it breaks down, and how it compares with established methods? The answer matters precisely because the gauge choice is *not* a physics claim — it is a coordinate choice — and a numerical pipeline is the right instrument for mapping the territory in which that coordinate is most useful.

---

## 2. Motivation

Non-Markovian open quantum systems sit between three difficult regimes:

1. weak-coupling master equations, where analytic control is high but applicability is limited;
2. numerically exact methods, where reliability is high but cost grows rapidly;
3. effective reduced descriptions, where interpretation is useful but gauge choices matter.

A decision-forcing numerical platform should not merely compute trajectories. It should expose the coherent/dissipative split, track gauge dependence, identify TCL singularities, and benchmark approximation quality against independent methods.

*Representation commitment.* The pipeline adopts the TCL representation as its primary coordinate system. Comparisons with non-TCL methods (HEOM, TEMPO, process-tensor approaches, MCTDH) are performed via explicit projection into this representation, rather than by assuming representation equivalence. Where projection is non-trivial or requires approximation, the projection scheme is itself part of the benchmark protocol and must be recorded in the benchmark card.

---

## 3. Scientific opportunity

The CBG framework offers three numerical handles:

- a basis-independent expression for K(t) (CL-2026-005 Entry 1, COMPATIBLE);
- a recursive perturbative construction of K_n and the canonical TCL generator (Entry 2, COMPATIBLE scope-limited);
- structural constraints — parity rules, no-rotation results, second-order FDT structure (Entries 3, 4, 5).

These are unusually good ingredients for a benchmarkable code architecture because they give both outputs and internal consistency checks. Each Ledger entry is a place where the code can verify itself against an independently-derived structural result.

---

## 4. Core aim

Develop a numerical pipeline that takes microscopic open-system models and produces:

- TCL generator terms L_n(t);
- minimal-dissipation effective Hamiltonian terms K_n(t);
- canonical dissipative components;
- convergence diagnostics;
- gauge-conditional observables;
- comparisons with independent reference methods.

*Output discipline.* All outputs are coordinate-dependent objects under the chosen gauge. Any interpretation as a physical observable requires an explicit mapping to experimentally accessible quantities; the pipeline produces K(t) as a numerical artefact of the coordinate choice, not as a measured Hamiltonian. Reports must distinguish between *computed* and *observable* quantities throughout, and any plot or table presenting K(t) carries a coordinate-choice annotation by default.

---

## 5. Required benchmark hierarchy

### Tier 1 — Algebraic sanity checks

Use models where the answer is structurally known:

- pure dephasing with A = σ_z (CL-2026-005 Entry 3);
- unbiased spin–boson with A = σ_x and thermal bath (Entry 4);
- weak-coupling Lamb-shift recovery (Entry 1 consistency check);
- pseudo-Kraus reduction to Hayden–Sorce 2022 (Entry 1 prior-art check).

Goal: verify formula implementation.

### Tier 2 — Perturbative convergence checks

Compare K_2, K_3, K_4 against:

- exact TCL where available (Jaynes–Cummings, pure-dephasing spin–boson, Fano–Anderson);
- direct reduced-dynamics reconstruction;
- short-time expansions;
- known singularity structures (Vacchini & Breuer, PRA 81, 042103 (2010)).

Goal: determine when the recursive expansion is numerically meaningful (CL-2026-005 Entry 2's "scope-limited" caveat made operational).

### Tier 3 — Cross-method benchmarks

Compare with established methods:

- HEOM;
- TEMPO / process tensor methods;
- MCTDH;
- pseudomode / chain-mapping approaches;
- QuTiP-based master-equation solvers;
- exact diagonalisation for small environments.

Goal: separate CBG-specific insight from method artefacts.

*Failure-asymmetry requirement.* Benchmarking must include at least one pair of methods with known non-overlapping failure modes, to avoid agreement-by-coincident truncation. HEOM truncation bias, TEMPO memory cutoff, MCTDH basis truncation, and exact-diagonalisation finite-bath errors fail in qualitatively different regimes; a Tier 3 verdict drawn from only one of these failure classes is structurally weaker than one drawn from two with non-overlapping failure modes.

### Tier 4 — Experimental-facing models

Apply to systems with measurable coherent renormalisation:

- trapped-ion spin–motion coupling;
- Jaynes–Cummings / Rabi-type models;
- spin–boson finite-temperature benchmarks;
- Fano–Anderson thermodynamic comparison (the natural DG-5 venue).

Goal: connect K(t) to operational signatures without reifying it as unique.

*Steward-conflict inheritance.* The Sail's local steward (U. Warring) is also the steward of CL-2026-005 and a co-author of Colla, Hasse, Palani, Schaetz, Breuer, Warring (Nat. Commun. **16**, 2502 (2025)) — the trapped-ion experiment cited in CL-2026-005 Entry 6. The Entry 6 triple-flagging discipline is inherited verbatim by Tier 4 with the following operational rule:

- *Primary* trapped-ion benchmarking uses non-Warring-group data wherever such data exist.
- *Secondary* trapped-ion benchmarking against Warring-group data is admissible only as a cross-check, conservatively read, with the sticky flag carried into every benchmark card that uses such data.
- Where independent data are unavailable for a given model, the benchmark card records the absence explicitly and the Tier 4 verdict for that model is annotated "stewardship-conflict-bound, awaiting independent replication".

This rule is non-negotiable and is reflected in the repository's `docs/stewardship_conflict.md` file (§11). The flag propagates to any downstream artefact that uses Tier 4 results.

---

## 6. Pipeline architecture

### Input layer

- microscopic Hamiltonian;
- system/environment split;
- coupling operators;
- bath state;
- truncation parameters;
- perturbative order;
- gauge choice (Hayden–Sorce minimal-dissipation by default; alternative gauges as comparison option for DG-5);
- observable set.

### Symbolic layer

- operator algebra;
- cumulant recursion (CBG Companion Eqs. (17), (27));
- parity classification (Letter Eqs. (23)–(24));
- trace/traceless decomposition;
- basis-independent K(t) checks (Letter Eqs. (6)–(7)).

### Numerical layer

- time-grid integration;
- tensor contractions;
- environment correlation functions;
- finite-bath exact propagation;
- stability and convergence diagnostics.

### Benchmark layer

- reference-method interface;
- error metrics;
- convergence plots;
- singularity detection;
- gauge-comparison reports.

### Reporting layer

- reproducible benchmark cards;
- model manifests;
- validity-envelope summaries;
- failure-mode logs.

---

## 7. Key diagnostics

The platform should report:

- norm of successive perturbative orders;
- distance to TCL non-invertibility;
- trace preservation and Hermiticity preservation;
- positivity / CP violations of truncated generators;
- K(t) stability under basis changes (Entry 1 sanity check at runtime);
- sensitivity to bath truncation;
- comparison error against numerically exact methods;
- gauge-dependence where competing effective Hamiltonians are available (DG-5 substrate).

---

## 8. Benchmarking philosophy

The goal is not to prove that the CBG construction is universally superior. The goal is to determine its validity envelope.

A successful platform should be able to say:

- here the method agrees with exact numerics;
- here it gives the right coherent structure but poor dissipative accuracy;
- here the perturbative hierarchy fails;
- here another framework gives a different thermodynamic reading;
- here the gauge choice matters operationally.

Note the structural alignment with the Three-Probe Frequency Experiment philosophy (CL-2026-004 pending): repetition reduces variance; only kernel rotation increases robustness. Cross-method benchmarking (Tier 3) and gauge comparison (DG-5) are kernel-rotation moves in this sense — they do not merely accumulate evidence; they expose dimensions along which evidence is or is not informative.

---

## 9. Decision gates

### DG-1 — Formula implementation

Pass if Entries 1, 3, and 4 of CL-2026-005 are reproduced numerically.

### DG-2 — Fourth-order recursion

Pass if K_2–K_4 are computed reproducibly for at least one non-Gaussian bath and one finite-dimensional environment, *and* satisfy at least one non-trivial structural constraint at each computed order. The basis-independence check per Letter Eqs. (6)–(7) is universally applicable across all model classes and serves as the default. Model-appropriate additional checks — for example, parity rule per Letter Eqs. (23)–(24) for spin systems, vanishing pattern per Letter Appendix D for symmetric couplings, fermion-number conservation for Fano–Anderson, RWA-consistency for Jaynes–Cummings — are specified per benchmark card and stack on top of the universal default. Reproducibility alone is insufficient: a numerically wrong but stable implementation can pass reproducibility while violating structural identities, and DG-2 must catch that case.

### DG-3 — Cross-method validation

Pass if benchmark comparisons against at least two independent established methods are implemented, with at least one pair drawn from non-overlapping failure-mode families (per the Tier 3 failure-asymmetry requirement). The mandatory baseline pair for the v0.4 scaffold is `exact_finite_env.py` + `qutip_reference.py`; additional methods (HEOM, TEMPO, MCTDH, pseudomode/chain-mapping) are aspirational extensions and may be added as the platform matures. The benchmark protocol document (`docs/benchmark_protocol.md`) records which methods are baseline and which are aspirational at any given pipeline version.

*Implementation readiness vs. failure-asymmetry clearance.* The baseline pair satisfies DG-3 *implementation readiness* — it is sufficient to start the pipeline, run benchmarks, and produce comparison reports. It does *not* in general satisfy *failure-asymmetry clearance*: depending on implementation, `exact_finite_env.py` and `qutip_reference.py` may share finite-truncation and solver assumptions that fail in correlated regimes. Full failure-asymmetry clearance per the §5 Tier 3 rule requires at least one additional method family from a non-overlapping failure-mode class (most naturally HEOM or TEMPO, once available). The benchmark protocol document records the current clearance level for each pipeline version, so that downstream reports can correctly distinguish "implementation-ready" from "clearance-passed" comparisons.

### DG-4 — Failure envelope

Pass if the platform can identify at least one regime where the CBG perturbative pipeline fails or becomes ambiguous.

*Cause-label discipline.* Each identified failure regime must be recorded with an explicit cause label drawn from the following taxonomy: *convergence failure* (perturbative norm of K_n grows or fails to settle); *TCL singularity* (proximity to or crossing of ∥Λ_t − id∥ ≥ 1); *projection ambiguity* (non-TCL method comparison ill-defined under the chosen projection scheme); *truncation artefact* (bath cutoff, basis cutoff, or time-grid step dependence beyond stated tolerance); *benchmark disagreement* (cross-method inconsistency exceeding stated uncertainty under failure-asymmetry-cleared comparison). Each failure regime must be reproducible: re-running the pipeline at the same parameter set must produce the same failure label. Unlabelled or non-reproducible failures do not count toward DG-4 pass.

### DG-5 — Thermodynamic discriminant

Pass if Entry 7's discriminant is run in one solvable model, preferably Fano–Anderson or Jaynes–Cummings, *and* the run identifies at least one thermodynamic observable (work extraction, efficiency, heat current, or work–heat partition) where the minimal-dissipation K(t) and a competing framework (e.g. Hamiltonian of mean force, polaron, Mori) yield numerically distinguishable predictions in the same model parameter regime. Side-by-side computation of K(t) and K_HMF in a regime where the two predictions agree is *not* a DG-5 pass: the Ledger's discriminant condition requires demonstrable divergence between frameworks under identical model conditions.

*Ledger feedback-loop routing.* DG-5 outcomes feed back to CL-2026-005 only via a fresh Council deliberation; the Sail does not modify the Ledger. A successful DG-5 generates a discriminant report that is filed as input to a re-deliberation session for CL-2026-005. The re-deliberation may transition Entry 7 from UNDERDETERMINED to COMPATIBLE or INCONSISTENT, depending on the result; until that session is convened and concluded, Entry 7's classification stands.

*Self-contained statement.* The no-Ledger-edit rule is independent of any external reference: the Sail does not edit the Ledger, full stop. Council ratification G2 — recorded in CL-2026-005-DEL-001 — confirms that re-deliberation may proceed under continued steward-conflict triple-flagging, but the no-edit rule does not depend on a reader having access to that record.

---

## 10. Risks

- treating K(t) as the unique physical Hamiltonian rather than a gauge-conditional object;
- over-trusting perturbative convergence in strong coupling;
- confusing agreement with one experiment for general validation;
- benchmarking only against weak-coupling methods;
- hiding failures behind smooth plots;
- building a codebase before defining benchmark cards;
- bypassing Council deliberation for Sail outputs that bear on Ledger entries — the Sail's relationship to CL-2026-005 is unidirectional consumption; outputs that would alter the Ledger must route through fresh Council deliberation per DG-5;
- overfitting the pipeline to known solvable models — i.e. tuning truncation, bath discretisation, integration step size, or other internal parameters until known results are reproduced, while masking failure in regimes where independent benchmarks are unavailable. Mitigation: every parameter choice that affects Tier 1–3 outcomes must be set *before* benchmarking begins and recorded in the benchmark card; post hoc parameter adjustments are flagged and require explicit justification in the failure-mode log.

---

## 11. Minimal first implementation

Start with a small, inspectable repository:

```text
oqs-cbg-pipeline/
  models/
    pure_dephasing.py
    spin_boson_sigma_x.py
    jaynes_cummings.py
    fano_anderson.py
  cbg/
    basis.py
    tcl_recursion.py
    effective_hamiltonian.py
    cumulants.py
    bath_correlations.py
    diagnostics.py
  benchmarks/
    exact_finite_env.py
    qutip_reference.py
    benchmark_cards/
  docs/
    endorsement_marker.md
    stewardship_conflict.md
    do_not_cite_as.md
    validity_envelope.md
    benchmark_protocol.md
```

The five top-level `docs/` files — `endorsement_marker.md`, `stewardship_conflict.md`, `do_not_cite_as.md`, `validity_envelope.md`, and `benchmark_protocol.md` — are non-optional and must exist as separate files at HEAD throughout the repository's lifetime. The first three are the protective scaffolding inherited from CL-2026-005 v0.4 and from this Sail's §0. The latter two are operational scaffolding that this Sail mandates for its own discipline (`validity_envelope.md` as the living DG-status record per §9; `benchmark_protocol.md` as the four-protocol document below). Code that runs without all five is structurally non-compliant with the Sail's discipline and must not be released, archived, or cited.

`docs/benchmark_protocol.md` must include at minimum: (i) a *coordinate-choice annotation template* satisfying §4's output-discipline requirement, so that all K(t) plots and tables across benchmark cards carry uniform annotations; (ii) a *starter failure-mode taxonomy* for the Tier 3 methods listed in §5 (HEOM truncation bias, TEMPO memory cutoff, MCTDH basis truncation, exact-diagonalisation finite-bath errors, QuTiP solver-default assumptions, pseudomode/chain-mapping cutoff effects), so that implementers do not have to reconstruct it from the literature; (iii) the current implementation-readiness vs. failure-asymmetry-clearance status of the baseline pair (per DG-3); (iv) the parameter-freezing protocol enforcing Risk #8 mitigation at the code level.

`docs/validity_envelope.md` is updated atomically with every DG status change per its own §"Update protocol"; updates land in the same commit as the corresponding `logbook/` status-change entry.

The `cbg/bath_correlations.py` module holds the bath correlation functions and their generalised cumulants (CBG Companion Eqs. (15) and (24)) on which the recursive cumulants D̄(τ_1^k, s_1^{n-k}) are built. It is *not* a Nakajima–Zwanzig memory kernel: the TCL representation is time-local at every order, and the non-Markovian character lives in the time-dependence of L_t, not in a kernel convolution. The module is physically separated from standard time-grid integration to prevent accidental importation of Markovian solver defaults from libraries like QuTiP, and to isolate the bath-correlation structure that distinguishes the CBG construction from weak-coupling master-equation approaches. Time-grid integration belongs in the numerical layer (called from within `tcl_recursion.py` and `effective_hamiltonian.py`); bath-correlation evaluation belongs in `bath_correlations.py`; the two are not interchangeable and must not be merged. (Should a future extension require Nakajima–Zwanzig-style kernels, those would live in a separate `nz_kernels.py` module, not here.)

---

## 12. Revision log

- **v0.1 (initial scaffold)** — programme-setting document with §§0–11; "Decisive" in title; basic Endorsement Marker; trapped-ion benchmarking listed in Tier 4 without flag; no DG-5 routing rule; Risk list of six items; repo scaffold without `endorsement_marker.md` or `stewardship_conflict.md`.
- **v0.2 (intermediate, 2026-04-29)** — Guardian-pass refinements after CL-2026-005 v0.4 activation:
  - Title: "Decisive" → "Decision-Forcing"; "Decision-Forcing" glossed in §0 to mean validity-envelope determination, not framework competition.
  - §0 Endorsement Marker extended: explicit rule that the Sail does not modify the Ledger; findings bearing on CL-2026-005 route via fresh Council deliberation.
  - §1 opening thesis rewritten so the gauge-conditionality precedes the constructive claim (mirroring CL-2026-005 v0.4 framing-claim language).
  - §5 Tier 4: steward-conflict inheritance paragraph added with the primary/secondary data rule and the "stewardship-conflict-bound, awaiting independent replication" annotation for unmatched models.
  - §9 DG-5: Ledger feedback-loop routing rule added; references Council ratification G2 from CL-2026-005-DEL-001.
  - §10 Risks: seventh risk added (bypassing Council for Ledger-bearing Sail outputs).
  - §11: `endorsement_marker.md` and `stewardship_conflict.md` added to repo scaffold; `fano_anderson.py` added to models (DG-5 venue); code fence closed.
  - Anchor specificity: `CL-2026-005` → `CL-2026-005 v0.4` to record Council-cleared status.

- **v0.3 (intermediate, 2026-04-29)** — composite-review refinements after Verifier + Scout + Architect read of v0.2; ten distinct items applied:
  - §2 *representation commitment*: TCL adopted as primary coordinate system; comparisons with non-TCL methods require explicit projection, with the projection scheme recorded in the benchmark card.
  - §4 *output discipline*: K(t) is a coordinate-dependent output, not a measured Hamiltonian; reports distinguish *computed* vs. *observable* quantities throughout, and K(t) plots/tables carry coordinate-choice annotations by default.
  - §5 Tier 3 *failure-asymmetry requirement*: benchmarking must draw on at least one pair of methods with non-overlapping failure modes (HEOM truncation, TEMPO memory cutoff, MCTDH basis truncation, finite-bath errors), to avoid agreement-by-coincident-truncation.
  - §9 DG-2 tightened: reproducibility alone is insufficient; structural-identity satisfaction (parity rule, vanishing pattern, or basis-independence) required at each computed order to catch numerically-stable-but-wrong implementations.
  - §9 DG-3 mandatory baseline pair specified (`exact_finite_env.py` + `qutip_reference.py`); other methods marked aspirational; pair-selection logged in `docs/benchmark_protocol.md`.
  - §9 DG-5 sharpened: pass requires demonstrable divergence in at least one thermodynamic observable between frameworks under identical model conditions, not merely side-by-side computation; trivial agreement does not satisfy the Ledger's discriminant condition.
  - §9 DG-5 routing rule made self-contained: no-Ledger-edit rule does not depend on availability of the cited deliberation record (CL-2026-005-DEL-001); G2 ratification is referenced but the rule stands without it.
  - §10 Risks: eighth risk added (overfitting the pipeline to known solvable models), with explicit mitigation rule on parameter-choice freezing before benchmarking.
  - §11 repository scaffold: `cbg/memory_kernel.py` added per Architect to physically separate non-Markovian memory-retardation logic from standard time-grid integration; explanatory note added to prevent accidental QuTiP-default importation.
  - Header version bumped; final-line stamp updated.

- **v0.4 (intermediate, 2026-04-29)** — pre-freeze polish after Steward + Architect + Scout read of v0.3; six items applied:
  - Revision-log labels cleaned: v0.2 and v0.3 entries had both stale-claimed "this revision" status; both now correctly labelled "intermediate", with v0.4 the unique current revision.
  - DG-2 broadened: structural-constraint requirement now allows model-appropriate checks (parity, vanishing pattern, fermion-number conservation, RWA-consistency) stacking on top of the universal basis-independence default; addresses the Fano–Anderson and Jaynes–Cummings symmetry-pattern coverage gap.
  - DG-3 distinguishes *implementation readiness* from *failure-asymmetry clearance*: the baseline pair satisfies readiness but may not satisfy clearance if the two methods share truncation/solver assumptions; full clearance requires at least one additional method family.
  - DG-4 strengthened with cause-label discipline (convergence failure / TCL singularity / projection ambiguity / truncation artefact / benchmark disagreement) and reproducibility requirement; unlabelled or non-reproducible failures do not count toward DG-4 pass.
  - `cbg/memory_kernel.py` renamed to `cbg/bath_correlations.py`: TCL is time-local, the file holds bath correlation functions and their cumulants (CBG Companion Eqs. (15), (24)), not Nakajima–Zwanzig memory kernels. The Markovian-default-isolation rationale (per Architect v0.3 review) is preserved; future NZ-kernel extensions, if needed, would live in a separate `nz_kernels.py`.
  - §11 expanded: `docs/benchmark_protocol.md` requirements explicitly enumerated (coordinate-choice annotation template, failure-mode starter taxonomy, DG-3 readiness/clearance status, parameter-freezing protocol enforcing Risk #8 at the code level).

- **v0.5 (this revision, 2026-04-29)** — cardinality-fix pass following audit of repository v0.1.0 and the DG-1 work plan:
  - §11 protective-doc cardinality reconciled: v0.4 §11 named *three* top-level `docs/` files as "non-optional" (`endorsement_marker.md`, `stewardship_conflict.md`, `do_not_cite_as.md`) and separately required `docs/benchmark_protocol.md` to "include at minimum" certain content and `docs/validity_envelope.md` to exist (per §9). The repository's tests (`tests/test_imports.py`), CI (`.github/workflows/tests.yml`), and `docs/README.md` already treated all five as the protective set; `cbg/__init__.py` and `docs/endorsement_marker.md` still said "three". v0.5 makes the cardinality explicit and uniform: all five are non-optional protective documents at HEAD throughout the repository's lifetime. The substantive set of files required is unchanged from v0.4 — only the `non-optional` label is broadened to match enforcement.
  - The change is non-load-bearing on CL-2026-005: it does not touch any Ledger entry, Tier 4 stewardship discipline, or DG-5 routing rule. No Council deliberation is required (per §0, the Sail does not modify the Ledger, and this revision does not bear on the Ledger).
  - Companion edits land in the same logbook event (`logbook/2026-04-29_sail-v0.5-bump.md`): `cbg/__init__.py` widens its protective-doc check from three to five; `docs/endorsement_marker.md` updates "these three" to "these five"; `tests/test_imports.py` docstring corrected from "three" to "five"; Sail-version anchors in `docs/`, `pyproject.toml`, `README.md`, and module docstrings bumped from v0.4 to v0.5.

---

*End of Sail v0.5. Sail-layer artefact under local stewardship; no Council clearance required. Subject to revision at the steward's discretion; substantive changes that bear on CL-2026-005 must route via fresh Council deliberation per §0 and §9 DG-5.*

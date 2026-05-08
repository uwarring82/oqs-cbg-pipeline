# Benchmark-card schema — `oqs-cbg-pipeline`

**Layer:** Repository operational specification (co-located with cards)
**Anchor:** Sail v0.5 §11 (parameter-freezing protocol mandate); [`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md) §1 (gauge annotation), §4 (parameter freezing); [DG-1 work plan v0.1.2](../../plans/dg-1-work-plan_v0.1.2.md) §4 Phase A
**Schema version:** v0.1.3
**Last updated:** 2026-05-05

---

## What this document is

This document specifies the schema that every benchmark card (every `*.yaml` file in this directory other than [`_template.yaml`](_template.yaml)) must satisfy. It is the **canonical reference** for card structure: a non-conflicted reader should be able, from this document and [`_template.yaml`](_template.yaml) alone, to write a syntactically valid card without consulting the repository's source files.

The schema is **operational specification**, not protective scaffolding. It is co-located with the cards rather than placed in [`docs/`](../../docs/), because [`docs/`](../../docs/) is locked by Sail v0.5 §11 to the five protective documents (`endorsement_marker.md`, `stewardship_conflict.md`, `do_not_cite_as.md`, `validity_envelope.md`, `benchmark_protocol.md`).

The protocols it derives from — gauge annotation and parameter freezing — live in [`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md). This file *transcribes* their requirements into a concrete card structure; if the protocol document changes, this schema follows under its own version bump.

## File layout and naming

A benchmark card is a single YAML file in this directory. The filename is:

```
benchmarks/benchmark_cards/<card_id>_<short-tag>_v<version>.yaml
```

- `<card_id>` is a short identifier of the form `A<n>` (DG-1), `B<n>` (DG-2), `C<n>` (DG-3), `D<n>` (DG-4), `E<n>` (DG-5), where `<n>` is an integer drawn from the corresponding Decision Gate's plan. DG-1 cards (per [DG-1 work plan v0.1.2](../../plans/dg-1-work-plan_v0.1.2.md) §4 Phase B) are `A1`, `A3`, `A4`.
- `<short-tag>` is a kebab-case tag describing the model or scenario (e.g. `closed-form-K`, `pure-dephasing`, `sigma-x-thermal`).
- `<version>` is the card's `version` field with the leading `v` retained (e.g. `v0.1.0`).
- Examples: `A1_closed-form-K_v0.1.0.yaml`, `A3_pure-dephasing_v0.1.0.yaml`, `A4_sigma-x-thermal_v0.1.0.yaml`.

The version is included in the filename so a superseding card (same `card_id`, same `<short-tag>`, higher `version`) can coexist with its predecessor in the same directory. One card per file. Cards are never silently edited or deleted post-verdict; supersedure is by *new file*, with the prior file's `superseded_by:` field appended ([`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md) §4.3). See §[Supersedure](#supersedure) below.

## Top-level shape

A card is a single YAML mapping with the following top-level keys, in this order:

```yaml
schema_version:       # this card's schema dialect, e.g. "v0.1.0"
card_id:
version:
date:
dg_target:
ledger_entry:
model:
status:
supersedes:           # optional
superseded_by:        # optional, appended only when a successor exists
license:

gauge:                # mapping (see §Gauge block)
frozen_parameters:    # mapping with four required sub-blocks (see §Frozen-parameters block)
acceptance_criterion: # mapping (see §Acceptance-criterion block)
result:               # mapping; empty values at draft time (see §Result block)
failure_mode_log:     # list; empty list at draft time (see §Failure-mode log)
stewardship_flag:     # mapping (see §Stewardship-flag block)
```

The order is conventional rather than load-bearing for parsers, but required for human auditability: a steward scanning the file should reach the schema declaration first, the gauge annotation and frozen parameters next, and the result block last.

## Field reference

### Top-level metadata

| Field | Type | Required | Specification |
|---|---|---|---|
| `schema_version` | string | yes | Semver of the schema dialect this card claims to satisfy (e.g. `v0.1.0`). Records, machine-readably, which version of [`SCHEMA.md`](SCHEMA.md) the card was authored against. The runner ([`reporting/benchmark_card.py`](../../reporting/), Phase C) is responsible for accepting cards under any schema version it knows. See §[Schema versioning](#schema-versioning). |
| `card_id` | string | yes | Matches `^[A-E][0-9]+$`. Stable across the card's lifetime, **including** across version bumps and supersedure of the same benchmark. A *new* `card_id` is used only for a *new benchmark* (different DG target, model, or observable). Supersedure of an existing benchmark keeps `card_id` and increments `version` (see §[Supersedure](#supersedure)). |
| `version` | string | yes | Semver of the form `v<MAJOR>.<MINOR>.<PATCH>` (e.g. `v0.1.0`). Increments on supersedure of *this* card. Unrelated to repository tag, plan version, or `schema_version`. |
| `date` | string | yes | ISO-8601 date `YYYY-MM-DD` of the card's first commit at the current `version` (steward local timezone, Europe/Berlin). |
| `dg_target` | string | yes | One of `DG-1`, `DG-2`, `DG-3`, `DG-4`, `DG-5`. The Decision Gate the card contributes to. |
| `ledger_entry` | string | yes | Anchor of the form `<ledger-id> v<version> Entry <N>` (e.g. `CL-2026-005 v0.4 Entry 1`). |
| `model` | string | yes | Identifier of the system–environment model (e.g. `pure_dephasing`, `spin_boson_sigma_x`, `closed_form_algebraic`). For models implemented in [`models/`](../../models/), the model name matches the module file's basename. |
| `status` | string | yes | One of `frozen-awaiting-run`, `pass`, `fail`, `conditional`, `superseded`, `scope-definition`. The single-hyphenated tokens are intentional: parsers must accept them as opaque enum values, not as compound descriptors. See §[Status values](#status-values). |
| `supersedes` | string | optional | Filename of the card this card replaces (e.g. `A3_pure-dephasing_v0.1.0.yaml`). Absent on first-issue cards. |
| `superseded_by` | string | optional | Filename of the card that replaces this card. Appended only when a successor exists. One of the narrow post-Phase-D edits permitted; see §[Supersedure](#supersedure). |
| `license` | string | yes | Card prose is documentation; license is `CC-BY-4.0 (LICENSE-docs)`. |

#### Status values

- **`frozen-awaiting-run`** — card committed with `frozen_parameters` and `acceptance_criterion` populated; `result` empty. The state at end of [DG-1 work plan v0.1.2](../../plans/dg-1-work-plan_v0.1.2.md) Phase B.
- **`pass`** / **`fail`** / **`conditional`** — verdict reached. The card's `result.verdict` field carries the matching upper-case form (`PASS`, `FAIL`, `CONDITIONAL`); the top-level `status` mirrors it in lower-case for filename/display consistency.
- **`superseded`** — a successor card has replaced this one. The verdict (if any) is retained as historical record; `superseded_by:` is populated.
- **`scope-definition`** — a design-target card whose preconditions are not yet met (e.g. the model API is stubbed, a competing-framework reference is not yet implemented, or a required runner branch does not exist). The card freezes the *intended* parameter scaffold and acceptance criterion so that future implementation work is bounded and auditable. `result` is empty (as with `frozen-awaiting-run`). A scope-definition card transitions to `frozen-awaiting-run` once its preconditions are satisfied; that transition requires supersedure (new version with updated `failure_mode_log`).

The token `frozen-awaiting-run` is a single hyphenated identifier. It is **not** "`frozen, awaiting run`" or "`frozen awaiting run`"; YAML linters and downstream tools rely on the single-token form.

### Gauge block

Per [`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md) §1, every card-emitted artefact carries the Hayden–Sorce minimal-dissipation gauge annotation. The card transcribes the machine-readable form verbatim:

```yaml
gauge:
  gauge: hayden-sorce-minimal-dissipation
  coordinate_dependent: true
  direct_observable: false
  gauge_alignment_required_for_comparison:
    - hmf
    - polaron
    - mori
```

| Field | Type | Required | Specification |
|---|---|---|---|
| `gauge.gauge` | string | yes | Currently fixed at `hayden-sorce-minimal-dissipation`. Future DG-5 outputs may introduce alternative gauge values; when they do, this schema will bump under §[Schema versioning](#schema-versioning). |
| `gauge.coordinate_dependent` | boolean | yes | Always `true` for K(t)-bearing cards. |
| `gauge.direct_observable` | boolean | yes | Always `false` for K(t)-bearing cards. |
| `gauge.gauge_alignment_required_for_comparison` | list[string] | yes | Identifiers of gauges with which comparison requires explicit alignment. Default set: `[hmf, polaron, mori]`. |

The runner ([`reporting/benchmark_card.py`](../../reporting/), planned for Phase C) verifies that this block is present and well-formed before emitting any artefact derived from the card.

### Frozen-parameters block

Per [`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md) §4.1, four sub-blocks are required. The schema fixes the sub-block names; their *contents* are model- and DG-specific.

```yaml
frozen_parameters:
  model:        # mapping
  truncation:   # mapping
  numerical:    # mapping
  comparison:   # mapping
```

#### `frozen_parameters.model`

Hamiltonian coefficients, system–environment partition, coupling operators, bath state, temperature, spectral density. The required field set depends on `model_kind`:

| Field | Type | Required | Notes |
|---|---|---|---|
| `model_kind` | string | yes | One of `dynamical`, `algebraic_map`. Discriminates the verification style. `dynamical`: a system–bath model with time-dependent K(t) (Cards A3, A4 and DG-2+ cards). `algebraic_map`: a single-instant verification of a closed-form transformation (Card A1: L → K under Letter Eqs. (6)–(7)). See §[Algebraic-map cards](#algebraic-map-cards). |
| `system_dimension` | integer | yes | `d` of the system Hilbert space. Required for both `model_kind` values. |
| `system_hamiltonian` | string | conditional | Required when `model_kind == dynamical`. Symbolic expression (e.g. `(omega/2) * sigma_z`). For `algebraic_map`, the system Hamiltonian (if any) is per-test-case under `test_cases:`. |
| `coupling_operator` | string | conditional | Required when `model_kind == dynamical`. Symbolic expression (e.g. `sigma_z`, `sigma_x`). For `algebraic_map`, jump operators are per-test-case. |
| `bath_type` | string | conditional | Required when `model_kind == dynamical`. One of `bosonic_linear`, `bosonic_displaced`, `fermionic`, `none`. For `algebraic_map`, omit (no dynamical bath). |
| `bath_spectral_density` | mapping | conditional | Required when `bath_type ≠ none`. Sub-fields: `family` (e.g. `ohmic`, `drude_lorentz`), `cutoff_frequency`, `coupling_strength`. |
| `bath_state` | mapping | conditional | Required at model level when `bath_type ≠ none` AND no per-case `bath_state` is supplied in `test_cases`. When `test_cases` provides per-case `bath_state`, the per-case value takes precedence and the model-level field may be omitted. Sub-fields: `family` (e.g. `thermal`, `coherent_displaced`), `temperature` (kelvin or dimensionless `omega`-units; declare units explicitly), `displacement_amplitude` (if applicable). |
| `test_cases` | list[mapping] | conditional | Required when `model_kind == algebraic_map`. Optional when `model_kind == dynamical` (used for parameter sweeps; see §[Test cases for dynamical cards](#test-cases-for-dynamical-cards)). Each entry has at minimum `name`, `description`, `expected_outcome`, `reference`; for dynamical cards, may carry per-case overrides of model-level fields (typically `bath_state`). |

Cards may add model-specific fields beyond this minimum; the runner does not reject extra fields under `model`.

##### Algebraic-map cards

A card with `model_kind: algebraic_map` verifies a closed-form algebraic transformation at a single instant — typically a map from an input object (a Lindbladian L, a Kraus representation, …) to an output object (the effective Hamiltonian K, a generator term, …) — rather than a dynamical evolution. The canonical DG-1 instance is Card A1: Letter Eqs. (6)–(7) define a closed-form recipe taking any L to its K, and the card exercises that recipe on three representative L specifications (canonical Lindblad with traceless jump operators; Markovian weak-coupling generator; pseudo-Kraus form).

For algebraic-map cards:

- The model sub-block omits `system_hamiltonian`, `coupling_operator`, `bath_type`, `bath_spectral_density`, `bath_state`. Each sub-test fixes its own input objects under `test_cases[i]`.
- A non-empty `test_cases:` list is required. Each entry is a mapping with at minimum:
  - `name` (string) — kebab-case identifier of the sub-test (e.g. `canonical_lindblad_traceless`).
  - `description` (string) — one-line plain-language statement of what the sub-test verifies.
  - `expected_outcome` (string) — symbolic or prose expression of what the map should return.
  - `reference` (string) — anchor to the Letter equation, paper, or Ledger sub-claim (e.g. `Letter Eq. (6); CL-2026-005 v0.4 Entry 1.B.1`).
  - Additional model-specific fields (`hamiltonian_term`, `jump_operators`, numerical parameters) are permitted; the runner does not reject extras.
- `frozen_parameters.numerical.time_grid` is optional (the verification is at a single instant; see §[`frozen_parameters.numerical`](#frozen_parametersnumerical)).
- `frozen_parameters.truncation.bath_mode_cutoff` is omitted (no bath).
- `frozen_parameters.truncation.perturbative_order` is `0` for closed-form algebraic checks per [DG-1 work plan v0.1.2](../../plans/dg-1-work-plan_v0.1.2.md) §1.2.

PASS for an algebraic-map card requires every `test_cases[i]` to satisfy the card-level error metric and threshold. The `acceptance_criterion.rationale` block enumerates the per-test-case PASS conditions and any conditional logic.

##### Test cases for dynamical cards

A `dynamical` card may also use `test_cases:` to encode a *parameter sweep* — running the same physical model under multiple variants of a swept parameter, with each variant testing a different B-prediction. Cards A3 and A4 use this pattern: `system_hamiltonian`, `coupling_operator`, `bath_type`, `bath_spectral_density`, `truncation`, `numerical`, and `comparison` are fixed at the model/card level; the bath state varies per test case (thermal vs. coherently displaced), and each case's `expected_outcome` describes which B-predictions hold under that bath state.

For a dynamical card with `test_cases`:

- Each `test_cases[i]` entry has the same minimum fields as in algebraic-map cards (`name`, `description`, `expected_outcome`, `reference`) and may carry per-case overrides for any model-level field. The most common override is `bath_state:`; in principle any of the model-block fields may be overridden.
- Per-case fields take precedence over model-level when both are present; model-level fields apply when not overridden.
- When a card provides per-case `bath_state` for every entry, the model-level `bath_state` may be omitted (relaxation of validation rule 14a).
- Per-case acceptance metrics may differ from the card-level `comparison.error_metric` and `comparison.threshold` — for example, B.2 verifies a derived quantity is *zero* within tolerance, while B.3 verifies it is *nonzero* above a sensitivity threshold. The card-level `acceptance_criterion.rationale` enumerates the per-case PASS conditions in plain language; per-case structured fields (e.g. `expected_metric:`, `expected_threshold:`) are permitted as extras and resolved by the Phase C runner.

PASS for a dynamical card with `test_cases` requires every entry to satisfy its per-case conditions as enumerated in `acceptance_criterion.rationale`. A dynamical card without `test_cases` is a single-test card; its acceptance is set entirely by the card-level `comparison` block and `acceptance_criterion`.

#### `frozen_parameters.truncation`

| Field | Type | Required | Notes |
|---|---|---|---|
| `perturbative_order` | integer | yes | The frozen *N_card* for this card. DG-1 defaults per [DG-1 work plan v0.1.2](../../plans/dg-1-work-plan_v0.1.2.md) §1.2: A1 = 0, A3 = 2, A4 = 2. |
| `basis` | string | yes | Operator basis identifier (e.g. `matrix_unit`, `pauli`). |
| `bath_mode_cutoff` | integer | conditional | Required when `model.bath_type ≠ none`. Number of bath modes retained. |
| `hierarchy_depth` | integer | optional | HEOM-specific; absent for non-HEOM cards. |
| `bond_dimension` | integer | optional | TEMPO/MPS-specific; absent otherwise. |
| `pseudomode_count` | integer | optional | Pseudomode/chain-mapping-specific; absent otherwise. |

#### `frozen_parameters.numerical`

| Field | Type | Required | Notes |
|---|---|---|---|
| `time_grid` | mapping | conditional | Required when `model_kind == dynamical`; optional when `model_kind == algebraic_map` (no time evolution). Sub-fields when present: `t_start`, `t_end`, `n_points`, `scheme` (`uniform`, `chebyshev`, `log`, …). |
| `integration_tolerance` | mapping | yes | Sub-fields: `relative` (e.g. `1e-12`), `absolute` (e.g. `1e-14`). For `algebraic_map`, these set the comparison tolerance for the symbolic-to-numeric reduction (e.g. residual after evaluating the closed form). |
| `solver` | string | yes | Identifier of the numerical solver (e.g. `scipy_dop853`, `analytical`). For closed-form / algebraic-map cards, `analytical`. |

#### `frozen_parameters.comparison`

| Field | Type | Required | Notes |
|---|---|---|---|
| `reference` | string | yes | Citation key or expression for the analytical/literature reference. Use stable identifiers (e.g. `Letter Eq. (6)`, `Hayden_Sorce_2022`). |
| `target_observable` | string | yes | Observable being compared (e.g. `K(t)`, `omega_r(t)`, `eigenbasis_rotation_angle`). |
| `error_metric` | string | yes | Identifier of the error metric (e.g. `relative_frobenius`, `absolute_l2`, `relative_max`). |
| `threshold` | number | yes | Pass threshold under the named metric (e.g. `1.0e-10`). |
| `projection_scheme` | string | optional | Required for non-TCL methods (Sail §2 representation commitment); absent for native TCL outputs. |

#### `frozen_parameters.sweep` (optional)

Present on failure-envelope and convergence-study cards (DG-4). The sweep range is frozen *before* the run; post-hoc range tightening is prohibited by [`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md) §4.

```yaml
sweep:
  parameter_name: "coupling_strength"
  parameter_path: "model.bath_spectral_density.coupling_strength"
  sweep_range:
    start: 0.05
    end: 1.0
    n_points: 20
    scheme: "log_uniform"   # one of: uniform, log_uniform, chebyshev, log
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `parameter_name` | string | yes | Human-readable name of the swept parameter. |
| `parameter_path` | string | yes | Dot-notation path into `frozen_parameters` locating the swept field (e.g. `model.bath_spectral_density.coupling_strength`). |
| `sweep_range` | mapping | yes | Sub-fields: `start` (number), `end` (number), `n_points` (positive integer), `scheme` (`uniform`, `log_uniform`, `chebyshev`, `log`, …). |

### Acceptance-criterion block

The acceptance-criterion block is a *human-readable* restatement of the comparison rule, in addition to the structured `frozen_parameters.comparison` fields. It exists because the structured fields cannot capture, e.g., the conditional sweep logic for Card A3 ("zero shift in thermal case AND nonzero shift in displaced case").

```yaml
acceptance_criterion:
  reference: ""     # citation key or symbolic expression
  observable: ""    # what is computed
  error_metric: ""  # how the comparison is performed
  threshold: 0.0    # numerical pass threshold
  projection_scheme: null  # optional; null when not applicable
  rationale: |
    Multi-line prose stating, in plain language, what "PASS" means for this card.
    Refer to specific Ledger sub-claims by their B-prediction index (e.g. "B.1", "B.2").
    Reference the corresponding Letter equations by their numbering.
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `reference` | string | yes | Mirrors `frozen_parameters.comparison.reference`. |
| `observable` | string | yes | Mirrors `frozen_parameters.comparison.target_observable`. |
| `error_metric` | string | yes | Mirrors `frozen_parameters.comparison.error_metric`. |
| `threshold` | number | yes | Mirrors `frozen_parameters.comparison.threshold`. |
| `projection_scheme` | string \| null | optional | Mirrors `frozen_parameters.comparison.projection_scheme`. Use `null` (YAML scalar) when absent. |
| `rationale` | string (block) | yes | Plain-language statement of pass conditions, including any conditional logic that the structured fields cannot capture. |

The structured `frozen_parameters.comparison` block is the **machine-authoritative** version. The `acceptance_criterion` block is the **human-authoritative** version. If they conflict, the supersedure protocol applies — neither is silently edited.

### Result block

At draft (Phase B commit), this block is present with empty/null values. It is populated in Phase D ([DG-1 work plan v0.1.2](../../plans/dg-1-work-plan_v0.1.2.md) §4 Phase D, Commit D.1). See §[Card lifecycle](#card-lifecycle) for the precise edits permitted between phases.

```yaml
result:
  verdict: null         # one of PASS, FAIL, CONDITIONAL once populated
  evidence: []          # list of paths, one per artefact
  commit_hash: ""       # the verdict commit's SHA-1; filled by a follow-up commit (see below)
  runner_version: ""    # version string of reporting/benchmark_card.py at run time
  notes: ""             # optional free text
```

| Field | Type | Required | Specification |
|---|---|---|---|
| `verdict` | string \| null | yes (key present); null at draft | Once populated: one of `PASS`, `FAIL`, `CONDITIONAL` (upper case). The top-level `status` is updated to mirror in lower case. |
| `evidence` | list[string] | yes (key present); empty list at draft | Repository-relative paths to numerical outputs, plot files, log files. All listed files must exist in the same commit as the populated `result` block (the verdict commit). |
| `commit_hash` | string | yes (key present); empty string at draft | The full SHA-1 of the verdict commit. Cannot be set in the verdict commit itself (a commit hash is a function of the tree, so writing the hash into a tracked file changes the hash). Instead, the verdict commit lands with `commit_hash: ""`, and a *follow-up commit* fills the placeholder with the verdict commit's hash. This mirrors [`logbook/README.md`](../../logbook/README.md) §Immutability's self-referential placeholder discipline. The follow-up commit's message format is `cards: fill self-referential commit_hash placeholder for <card_id>` and it touches only that field. |
| `runner_version` | string | yes (key present); empty string at draft | Semver string of [`reporting/benchmark_card.py`](../../reporting/) at the time of the run. |
| `notes` | string | optional | Free text. Useful for `CONDITIONAL` verdicts to record the conditioning. |

### Failure-mode log

Per [`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md) §4.3, post-hoc parameter changes are *never* silent revisions. They are recorded as new cards plus a `failure_mode_log` entry on the new card explaining what changed and why.

```yaml
failure_mode_log: []   # list of mappings; empty at first-issue draft

# When populated (only on superseding cards), each entry has the shape:
# - date: 2026-MM-DD
#   change: "increased perturbative_order from 2 to 4"
#   reason: "convergence test of A3_v0.1.0 revealed truncation artefact at N=2"
#   predecessor_card_id: "A3"
#   predecessor_version: "v0.1.0"
```

| Field (per entry) | Type | Required | Specification |
|---|---|---|---|
| `date` | string | yes | ISO-8601 date of the supersedure. |
| `change` | string | yes | Plain-language description of what was modified. |
| `reason` | string | yes | Why the change was needed; reference to evidence (commit hash, run output) where applicable. |
| `predecessor_card_id` | string | yes | The `card_id` of the card being superseded. |
| `predecessor_version` | string | yes | The `version` of the card being superseded. |

A first-issue card has `failure_mode_log: []`. The log is append-only on the *current* card.

### Stewardship-flag block

Per [`docs/stewardship_conflict.md`](../../docs/stewardship_conflict.md), every card carries an explicit stewardship flag, even when unflagged. For DG-1 cards (Tier 1, theory-internal), all entries are unflagged; the field is present and explicit so flag-propagation discipline is mechanically enforceable.

```yaml
stewardship_flag:
  status: unflagged     # one of: unflagged, primary, secondary, stewardship-conflict-bound
  rationale: ""         # required when status != unflagged
  data_source: ""       # required when status in {primary, secondary}; format: "<paper>; <group>; <year>; <DOI>"
  search_performed: ""  # required when status == stewardship-conflict-bound; describes the search confirming absence of independent data
```

| Field | Type | Required | Specification |
|---|---|---|---|
| `status` | string | yes | Enum: `unflagged`, `primary`, `secondary`, `stewardship-conflict-bound`. The string forms match [`docs/stewardship_conflict.md`](../../docs/stewardship_conflict.md) Rules 1–3. |
| `rationale` | string | conditional | Required when `status ≠ unflagged`. Plain-language explanation of why the flag applies. |
| `data_source` | string | conditional | Required when `status ∈ {primary, secondary}`. Citation of the underlying experimental data. |
| `search_performed` | string | conditional | Required when `status = stewardship-conflict-bound`. Per [`docs/stewardship_conflict.md`](../../docs/stewardship_conflict.md) §Audit trail. |

The flag is sticky ([`docs/stewardship_conflict.md`](../../docs/stewardship_conflict.md) Rule 4): once attached, it propagates verbatim to every downstream artefact. Removal requires a fresh Council deliberation or replacement of the underlying data.

## Validation rules

The following are mechanically checkable. The runner ([`reporting/benchmark_card.py`](../../reporting/), Phase C) enforces them at load time; at Phase B (cards-first), validation is by hand-inspection plus a third-party YAML linter (`yamllint`).

These rules apply to **committed cards**. They do *not* apply to [`_template.yaml`](_template.yaml), which carries `TBD-*` and zero-valued placeholders that intentionally fail rules 3, 8, 9, 10. The template is exempt because it is parse-valid only — it must not be a valid card, or stewards would risk committing the template unchanged.

1. **All required top-level keys present** (per §[Top-level shape](#top-level-shape)), including `schema_version`.
2. **`status` is one of the enumerated values.**
3. **`status ∈ {frozen-awaiting-run, scope-definition}` ⇒ `result.verdict` is `null`, `result.evidence` is `[]`, `result.commit_hash` is `""`, `result.runner_version` is `""`.**
4. **`status ∈ {pass, fail, conditional}` ⇒ `result.verdict ∈ {PASS, FAIL, CONDITIONAL}` matching `status` (case-folded), `result.runner_version` is non-empty, every path in `result.evidence` exists in the same commit. `result.commit_hash` is either the empty string `""` (between the verdict commit and the self-referential follow-up commit) or a 40-character hex string (after the follow-up).**
5. **`status: superseded` ⇒ `superseded_by` is populated.**
6. **`gauge` block matches the verbatim form in §[Gauge block](#gauge-block)** (no value substitutions permitted at DG-1; alternative gauges are a future schema bump).
7. **`frozen_parameters` has the four required sub-blocks** (`model`, `truncation`, `numerical`, `comparison`), each non-empty.
8. **`frozen_parameters.truncation.perturbative_order` is a non-negative integer.**
9. **`acceptance_criterion.threshold` is a positive number.**
10. **`stewardship_flag.status` is one of the enumerated values; conditional fields are populated when their preconditions hold.**
11. **`license` field equals `CC-BY-4.0 (LICENSE-docs)`** (cards inherit documentation licensing).
12. **`schema_version` matches a schema dialect the runner knows.** Cards under unknown schema versions are rejected with a clear error pointing at this section.
13. **`frozen_parameters.model.model_kind` is one of `dynamical`, `algebraic_map`.**
14. **`model_kind == dynamical` ⇒ `system_hamiltonian`, `coupling_operator`, `bath_type` are required at model level; `numerical.time_grid` is required.**
14a. **When `bath_type ≠ none`, `bath_state` is required at model level OR in every entry of `test_cases`** (per-case `bath_state` takes precedence over model-level when both are present).
15. **When `test_cases` is present (under any `model_kind`), each entry has at minimum `name`, `description`, `expected_outcome`, `reference`.**
15a. **`model_kind == algebraic_map` ⇒ `test_cases` is required and non-empty; `system_hamiltonian`/`coupling_operator`/`bath_type` are absent or empty.**
16. **`numerical.time_grid` is required when `model_kind == dynamical`** (this is the dynamical-side restatement of rule 14, reiterated under `numerical` for runner-implementation clarity).
17. **`frozen_parameters.sweep` is optional. When present, `sweep.parameter_name`, `sweep.parameter_path`, and `sweep.sweep_range` are required, and `sweep.sweep_range.scheme` is one of the enumerated values.**
18. **`status: scope-definition` ⇒ the card carries explicit `failure_mode_log` or `result.notes` recording the preconditions that are not yet met.**

## Card lifecycle

A card's content is mutated only at the four enumerated commit-points below: two structural commits (Phase B, verdict), one self-referential bookkeeping commit (`commit_hash` fill), and one optional successor-marker commit (`superseded_by` annotation). Every other change requires [supersedure](#supersedure).

**Phase B commit (frozen-awaiting-run).** The card is committed with `status: frozen-awaiting-run`. All of `schema_version`, top-level metadata, `gauge`, `frozen_parameters`, `acceptance_criterion`, `failure_mode_log` (typically `[]`), and `stewardship_flag` are fully populated. The `result` block carries empty/null values per §[Result block](#result-block).

**Verdict commit (Phase D Commit D.1).** Between Phase B and the verdict commit, the card is content-immutable: any change to a frozen field requires supersedure. The verdict commit may modify *only* the following fields, atomically, in a single commit:

- `status`: `frozen-awaiting-run` → one of `pass`, `fail`, `conditional`
- `result.verdict`: `null` → `PASS` | `FAIL` | `CONDITIONAL` (matching `status`, case-folded)
- `result.evidence`: `[]` → list of repo-relative paths
- `result.runner_version`: `""` → semver string
- `result.notes`: optional free text

The verdict commit's message includes the DG identifier per [DG-1 work plan v0.1.2](../../plans/dg-1-work-plan_v0.1.2.md) §4 Phase D. `result.commit_hash` remains `""` in the verdict commit itself.

**Self-referential follow-up commit (`commit_hash` fill).** A separate commit, immediately after the verdict commit, fills `result.commit_hash` with the verdict commit's SHA-1. Its message format is `cards: fill self-referential commit_hash placeholder for <card_id>` and it touches only that field (or, where multiple cards share a verdict commit, the matching field on each).

**Successor-marker commit (`superseded_by` annotation).** When a new card supersedes this one, the prior card's `superseded_by:` field is appended in the same commit that introduces the successor. After this commit, the prior card's `status` is set to `superseded`.

After these four commit-points (Phase B, verdict, self-referential fill, optional successor-marker), the card is content-immutable.

## Supersedure

A *content* change to any field other than the lifecycle transitions enumerated in §[Card lifecycle](#card-lifecycle) requires supersedure: a *new* card file with the same `card_id` and an incremented `version`, plus a `failure_mode_log` entry on the new card explaining what changed and why ([`docs/benchmark_protocol.md`](../../docs/benchmark_protocol.md) §4.3).

The `superseded_by:` annotation on the prior card and the corresponding `failure_mode_log` entry on the new card are added in the **same commit**, atomically. The prior card's `status` is updated to `superseded` in the same commit. Neither is left dangling.

`card_id` does *not* change under supersedure. A new `card_id` is reserved for a *new benchmark* — different DG target, different model, different observable. Re-issuing the same benchmark with corrected parameters keeps `card_id` and bumps `version`; the filename pattern (§[File layout and naming](#file-layout-and-naming)) carries the version, so predecessor and successor coexist in the directory.

## Schema versioning

This schema is itself versioned. The current version is `v0.1.3` (drafted 2026-05-05; surfaced by Phase B drafting of Cards D1 and E1; see Revision history below). The v0.1.2 baseline (drafted 2026-04-30, [DG-1 work plan v0.1.2](../../plans/dg-1-work-plan_v0.1.2.md) Phase A/Phase B boundary) remains the schema under which the DG-1 cards (A1, A3, A4) and the DG-2 cards (B1–B5) were authored, and those cards continue to validate unchanged under v0.1.3 per the supersedure-stability rule below.

Subsequent revisions follow the same supersedure discipline as other repository documents: substantive changes increment `MINOR`; clarifications and typo fixes increment `PATCH`; structural reworks that break existing cards' validity increment `MAJOR`. The schema's *current* version is recorded in this file's front-matter (`Schema version:`); the version a *card* claims to satisfy is recorded in the card's machine-readable `schema_version:` field (see §[Top-level metadata](#top-level-metadata)). The two are independent: a card under schema `v0.1.2` continues to exist unchanged after the schema bumps to `v0.1.3` (the DG-1 / DG-2 cards exemplify this), and would similarly survive a future bump to `v0.2.0`.

A schema bump never invalidates already-committed cards: cards retain the schema they were authored against, recorded in their `schema_version` field. The runner is responsible for accepting cards under any schema version it knows (validation rule 12); conflicts are resolved by re-issuing the card under the new schema (full supersedure under §[Supersedure](#supersedure), with a `failure_mode_log` entry citing the schema bump as the reason).

### Revision history

- **v0.1.0 (2026-04-30, drafted, never committed).** Initial Phase A draft. Single `frozen_parameters.model` shape presuming a dynamical system–bath model with required `system_hamiltonian`, `coupling_operator`, `bath_type`; `numerical.time_grid` unconditionally required. Superseded by v0.1.1 within Phase A; never reached HEAD.
- **v0.1.1 (2026-04-30, superseded by v0.1.2 within Phase A/B).** Added `model_kind:` discriminator (`dynamical` vs `algebraic_map`). Under `algebraic_map`: `system_hamiltonian`/`coupling_operator`/`bath_type` and `numerical.time_grid` become optional, and a `test_cases:` list is recognized with at-minimum `name`/`description`/`expected_outcome`/`reference` per entry. Validation rules 13–16 added. Surfaced by Phase B preview drafting of Card A1: Letter Eqs. (6)–(7) define an algebraic-map check on multiple L specifications, not a dynamical evolution. MINOR bump (not PATCH) because new fields and validation rules are added; non-breaking because `model_kind: dynamical` matches the v0.1.0 shape exactly. Reached HEAD; Card A1 was authored under v0.1.1.
- **v0.1.2 (2026-04-30, superseded by v0.1.3).** Generalized `test_cases:` to be optionally usable under `model_kind: dynamical` for parameter sweeps (a single physical model run under multiple variants of a swept parameter, typically `bath_state`, with each variant testing a different B-prediction). Relaxed `bath_state` requirement: when `test_cases` provides per-case `bath_state` for every entry, the model-level field may be omitted. Validation rules 14a, 15a added; rule 14 narrowed (model-level requirements) and rule 15 generalized (applies to test_cases under any `model_kind`). Added §Test cases for dynamical cards subsection. Surfaced by Phase B preview drafting of Card A3: Entry 3.B targets two distinct bath states (thermal vs. coherently displaced) under one card, exercising B.1 in both cases, B.2 in thermal, B.3 in displaced. MINOR bump because new fields, new subsection, and new validation rules are added; non-breaking because v0.1.1 cards (Card A1, `model_kind: algebraic_map` with `test_cases`) continue to validate unchanged under v0.1.2 (the test_cases generalization is additive). Same cards-first-surfaces-schema-issues pattern as v0.1.0 → v0.1.1.
- **v0.1.3 (2026-05-05, this revision).** Added `frozen_parameters.sweep:` block for DG-4 failure-envelope and convergence-study cards (Rule 17). Added `scope-definition` status value for cards whose preconditions are not yet met (e.g. model API is stubbed, competing-framework reference missing). Expanded Rule 2 (status enum), Rule 3 (empty-result precondition), and added Rule 18 (scope-definition notes requirement). Surfaced by Phase B drafting of Cards D1 (coupling-strength sweep) and E1 (Fano-Anderson scope definition): D1 needed a machine-readable sweep specification, and E1 needed a status that distinguished "intentionally not runnable" from "frozen awaiting implementation". MINOR bump because new fields, new status value, and new validation rules are added; non-breaking because v0.1.2 cards (no sweep block, status `frozen-awaiting-run`) continue to validate unchanged under v0.1.3 (the additions are additive). Same cards-first-surfaces-schema-issues pattern as prior bumps.

## Worked example pointer

A parse-valid (but intentionally not validation-valid; see §[Validation rules](#validation-rules)) card skeleton is at [`_template.yaml`](_template.yaml). Phase B will instantiate three cards (`A1`, `A3`, `A4`) per [DG-1 work plan v0.1.2](../../plans/dg-1-work-plan_v0.1.2.md) §4 Phase B; once committed, those cards become the canonical worked examples.

---

*This document is operational specification, not protective scaffolding. CC-BY-4.0 (see [`../../LICENSE-docs`](../../LICENSE-docs)).*

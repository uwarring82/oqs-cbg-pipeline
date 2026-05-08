"""
reporting.benchmark_card — Loader, validator, runner, and result-block writer.

DG-1 Phase C.4 per the work plan; extended in Phase C.10 to wire the
dynamical-card runner. Provides the infrastructure that Cards A1, A3,
A4 depend on:

    load_card(path)           — Read a YAML card and validate it against
                                SCHEMA.md v0.1.3.
    validate_card_data(data)  — Validate an already-parsed card dict
                                against the 18 schema rules.
    verify_gauge_annotation   — Enforce the canonical Hayden–Sorce
                                minimal-dissipation gauge block.
    run_card(card)            — Dispatch by DG target / model_kind.
                                algebraic_map cards (A1, B1–B3) run via
                                Letter Eq. (6) on registered handlers;
                                structural dynamical cards (A3, A4, B4,
                                B5) run via the TCL2 paths through
                                cbg.tcl_recursion; DG-3 dynamical cards
                                run through the cross-method reference
                                branch.
    populate_result           — Mutate the in-memory card with the
                                verdict + metadata. Disk serialisation
                                is deferred (Phase D verdict commit needs
                                a comment-preserving YAML library).

Test-case handlers live in explicit registries — _TEST_CASE_HANDLERS for
algebraic_map cards (keyed by test_cases[i].name),
_DYNAMICAL_TEST_CASE_HANDLERS for TCL structural dynamical cards, and
_CROSS_METHOD_TEST_CASE_HANDLERS for DG-3 reference-method comparisons
(the last two keyed by (card.model, test_cases[i].name)). New test cases
require new entries; the registries make the runner-side support surface
explicit and auditable.

Anchor: SCHEMA.md v0.1.3; DG-1 work plan v0.1.4 §4 Phase C rows C.4 and C.10.
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn

import numpy as np
import yaml

from benchmarks import exact_finite_env, qutip_reference
from cbg.basis import matrix_unit_basis, su_d_generator_basis, verify_orthonormality
from cbg.cumulants import D_bar_1 as _cumulants_D_bar_1
from cbg.displacement_profiles import REGISTERED_PROFILES as _CBG_REGISTERED_PROFILES
from cbg.effective_hamiltonian import K_from_generator
from cbg.tcl_recursion import K_total_displaced_on_grid, K_total_thermal_on_grid
from models import pure_dephasing, spin_boson_sigma_x
from numerical.tensor_ops import anticommutator, commutator
from numerical.time_grid import build_time_grid

__version__ = "0.1.0"  # Recorded in card.result.runner_version


# ─── Schema constants (SCHEMA.md v0.1.3) ─────────────────────────────────────

CANONICAL_GAUGE_BLOCK: dict[str, Any] = {
    "gauge": "hayden-sorce-minimal-dissipation",
    "coordinate_dependent": True,
    "direct_observable": False,
    "gauge_alignment_required_for_comparison": ["hmf", "polaron", "mori"],
}

# Schema versions the runner knows how to validate. v0.1.1 was the first
# version to reach HEAD (Card A1 v0.1.0 was authored under it); v0.1.2
# brought test_cases to dynamical cards (Cards A3, A4, A1 v0.1.1, B1–B5);
# v0.1.3 added the optional `frozen_parameters.sweep:` block (Rule 17)
# for DG-4 failure-envelope cards (D1) and the `scope-definition` status
# (Rule 18) for design-target cards whose preconditions are not yet met
# (E1: Fano-Anderson scope definition). Per SCHEMA.md §Schema versioning,
# "cards retain the schema they were authored against"; the runner
# accepts any known version. The v0.1.3 rule set is a non-breaking
# superset of v0.1.2 (additions are additive; v0.1.2 cards continue
# to validate unchanged).
KNOWN_SCHEMA_VERSIONS: tuple[str, ...] = ("v0.1.1", "v0.1.2", "v0.1.3")

VALID_STATUS = {
    "frozen-awaiting-run",
    "pass",
    "fail",
    "conditional",
    "superseded",
    "scope-definition",  # SCHEMA.md v0.1.3 (Rule 18): design-target card
}
VALID_MODEL_KIND = {"dynamical", "algebraic_map"}
VALID_STEWARDSHIP_FLAG = {"unflagged", "primary", "secondary", "stewardship-conflict-bound"}
VALID_DG_TARGET = {"DG-1", "DG-2", "DG-3", "DG-4", "DG-5"}
VALID_SWEEP_SCHEMES = {"uniform", "log_uniform", "chebyshev", "log"}
EMPTY_RESULT_STATUSES = {"frozen-awaiting-run", "scope-definition"}

REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = (
    "schema_version",
    "card_id",
    "version",
    "date",
    "dg_target",
    "ledger_entry",
    "model",
    "status",
    "license",
    "gauge",
    "frozen_parameters",
    "acceptance_criterion",
    "result",
    "failure_mode_log",
    "stewardship_flag",
)

REQUIRED_FROZEN_PARAMETERS_SUBBLOCKS: tuple[str, ...] = (
    "model",
    "truncation",
    "numerical",
    "comparison",
)


# ─── Exceptions ──────────────────────────────────────────────────────────────


class SchemaValidationError(ValueError):
    """A card YAML violates one of the SCHEMA.md v0.1.3 validation rules."""


class GaugeAnnotationError(ValueError):
    """A card's gauge block does not match the canonical Hayden–Sorce form."""


class ScopeDefinitionNotRunnableError(NotImplementedError):
    """Raised when ``run_card`` is called on a ``status: scope-definition`` card.

    Scope-definition cards (SCHEMA.md v0.1.3 Rule 18) are design-target
    cards whose preconditions are not yet met (e.g. model API stubbed,
    competing-framework reference missing). They freeze the *intended*
    parameter scaffold and acceptance criterion so future implementation
    work is bounded and auditable, but they are intentionally not
    runnable: attempting to run one indicates a workflow mistake (the
    card must transition to ``frozen-awaiting-run`` first via
    supersedure) rather than a runner bug.
    """


class DG4SweepRunnerNotImplementedError(NotImplementedError):
    """Raised when ``run_card`` is asked to run a DG-4 sweep card.

    The DG-4 failure-envelope runner is not yet implemented. It would
    require (i) a trusted order-4 L_4 source (analytic Path A preferred;
    benchmark-side Path B numerical extraction only with an uncertainty
    note) and (ii) wiring the ``frozen_parameters.sweep`` block
    (SCHEMA.md v0.1.3 Rule 17) into the runner. Card D1 v0.1.1 will
    become runnable when both pieces land.
    """


class TestCaseHandlerNotFoundError(LookupError):
    """No runner handler is registered for a card's test_case name."""


# ─── Card data structure ─────────────────────────────────────────────────────


@dataclass
class BenchmarkCard:
    """In-memory representation of a benchmark card.

    Constructed by load_card(); typically not instantiated directly. The
    raw YAML mapping is preserved in the dataclass fields; convenience
    properties surface frequently-accessed nested values.
    """

    schema_version: str
    card_id: str
    version: str
    date: str
    dg_target: str
    ledger_entry: str
    model: str
    status: str
    license: str
    gauge: dict[str, Any]
    frozen_parameters: dict[str, Any]
    acceptance_criterion: dict[str, Any]
    result: dict[str, Any]
    failure_mode_log: list[dict[str, Any]]
    stewardship_flag: dict[str, Any]
    supersedes: str | None = None
    superseded_by: str | None = None
    source_path: Path | None = None

    @property
    def model_kind(self) -> str:
        return self.frozen_parameters["model"]["model_kind"]

    @property
    def system_dimension(self) -> int:
        return self.frozen_parameters["model"]["system_dimension"]

    @property
    def threshold(self) -> float:
        return float(self.acceptance_criterion["threshold"])

    @property
    def basis_name(self) -> str:
        return self.frozen_parameters["truncation"]["basis"]


# ─── Run-result data structures ──────────────────────────────────────────────


@dataclass
class TestCaseResult:
    name: str
    passed: bool
    error: float
    threshold: float
    notes: str = ""
    hpta_residual: float | None = (
        None  # populated for pseudo-Kraus handlers; None for Lindblad-form handlers
    )
    hpta_threshold: float | None = None  # absolute Frobenius bound; None when no HPTA gate applies
    hermiticity_residual: float | None = (
        None  # populated for off-diagonal pseudo-Kraus (B2); None elsewhere
    )
    hermiticity_threshold: float | None = (
        None  # absolute Frobenius bound; None when no Hermiticity gate applies
    )


@dataclass
class CardResult:
    card_id: str
    verdict: str  # "PASS" | "FAIL" | "CONDITIONAL"
    test_case_results: list[TestCaseResult]
    runner_version: str
    notes: str = ""
    # DG-4 audit-completeness payload. Populated only by ``_run_dg4_sweep``.
    # Persists the full sweep table (per-alpha r_4 baseline + per-perturbation
    # r_4, per-perturbation Path B fit residuals and dissipator-norm
    # coefficients) so the result JSON written from this CardResult is
    # reproducibility-complete (DG-4 work plan v0.1.4 audit requirement).
    dg4_sweep_data: dict[str, Any] | None = None


# ─── Loader ──────────────────────────────────────────────────────────────────


def load_card(path: Path | str) -> BenchmarkCard:
    """Load and validate a benchmark card YAML file.

    Validates against SCHEMA.md v0.1.3 (18 rules); raises SchemaValidationError
    on any rule violation. The returned BenchmarkCard tracks its source_path
    so the runner can resolve relative evidence paths later.
    """
    path = Path(path)
    with open(path) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise SchemaValidationError(
            f"{path}: top-level YAML must be a mapping; got {type(data).__name__}"
        )
    validate_card_data(data)
    card = _data_to_card(data)
    card.source_path = path
    return card


def _data_to_card(data: dict[str, Any]) -> BenchmarkCard:
    return BenchmarkCard(
        schema_version=data["schema_version"],
        card_id=data["card_id"],
        version=data["version"],
        date=data["date"],
        dg_target=data["dg_target"],
        ledger_entry=data["ledger_entry"],
        model=data["model"],
        status=data["status"],
        license=data["license"],
        gauge=data["gauge"],
        frozen_parameters=data["frozen_parameters"],
        acceptance_criterion=data["acceptance_criterion"],
        result=data["result"],
        failure_mode_log=data.get("failure_mode_log", []),
        stewardship_flag=data["stewardship_flag"],
        supersedes=data.get("supersedes"),
        superseded_by=data.get("superseded_by"),
    )


# ─── Validator (SCHEMA.md v0.1.3 rules 1–18) ─────────────────────────────────


def validate_card_data(data: dict[str, Any]) -> None:
    """Validate a parsed card dict against SCHEMA.md v0.1.3.

    Implements all 18 validation rules. Raises SchemaValidationError with
    a "rule N: ..." prefix identifying the failing rule. Iteration order
    mirrors the schema's rule numbering for auditability.
    """
    # Rule 1: required top-level keys
    missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in data]
    if missing:
        raise SchemaValidationError(f"rule 1: missing required keys {missing}")

    # Rule 12: schema_version known to runner
    if data["schema_version"] not in KNOWN_SCHEMA_VERSIONS:
        raise SchemaValidationError(
            f"rule 12: schema_version {data['schema_version']!r} not in known "
            f"versions {KNOWN_SCHEMA_VERSIONS}; runner upgrade needed"
        )

    # Rule 11: license
    if data["license"] != "CC-BY-4.0 (LICENSE-docs)":
        raise SchemaValidationError(
            f"rule 11: license must equal 'CC-BY-4.0 (LICENSE-docs)'; " f"got {data['license']!r}"
        )

    # Rule 2: status enum
    if data["status"] not in VALID_STATUS:
        raise SchemaValidationError(
            f"rule 2: status {data['status']!r} not in {sorted(VALID_STATUS)}"
        )

    # Rule 5: superseded ⇒ superseded_by populated
    if data["status"] == "superseded" and not data.get("superseded_by"):
        raise SchemaValidationError(
            "rule 5: status 'superseded' requires superseded_by to be populated"
        )

    # Rule 3: frozen-awaiting-run | scope-definition ⇒ result block empty
    # (commit_hash and runner_version "", verdict null, evidence []). Note
    # that result.notes MAY be non-empty under scope-definition (Rule 18
    # accepts notes as a valid place to record unmet preconditions).
    r = data["result"]
    if data["status"] in EMPTY_RESULT_STATUSES:
        if r.get("verdict") is not None:
            raise SchemaValidationError(
                f"rule 3: status {data['status']!r} requires result.verdict null"
            )
        if r.get("evidence") != []:
            raise SchemaValidationError(
                f"rule 3: status {data['status']!r} requires result.evidence []"
            )
        if r.get("commit_hash") != "":
            raise SchemaValidationError(
                f"rule 3: status {data['status']!r} requires result.commit_hash ''"
            )
        if r.get("runner_version") != "":
            raise SchemaValidationError(
                f"rule 3: status {data['status']!r} requires result.runner_version ''"
            )

    # Rule 4: pass/fail/conditional ⇒ verdict matches
    if data["status"] in {"pass", "fail", "conditional"}:
        verdict = (r.get("verdict") or "").lower()
        if verdict != data["status"]:
            raise SchemaValidationError(
                f"rule 4: status {data['status']!r} requires "
                f"result.verdict {data['status'].upper()!r} (case-folded match); "
                f"got verdict={r.get('verdict')!r}"
            )
        if not r.get("runner_version"):
            raise SchemaValidationError("rule 4: result.runner_version must be non-empty")
        ch = r.get("commit_hash", "")
        if ch and not (len(ch) == 40 and all(c in "0123456789abcdef" for c in ch.lower())):
            raise SchemaValidationError(
                f"rule 4: result.commit_hash must be empty or a 40-char hex string; got {ch!r}"
            )

    # Rule 6: gauge block verbatim
    if data["gauge"] != CANONICAL_GAUGE_BLOCK:
        raise SchemaValidationError(
            "rule 6: gauge block does not match the canonical "
            "Hayden–Sorce minimal-dissipation form (see SCHEMA.md §Gauge block). "
            f"Expected {CANONICAL_GAUGE_BLOCK}; got {data['gauge']}"
        )

    # Rule 7: frozen_parameters has four required sub-blocks, each non-empty
    fp = data["frozen_parameters"]
    if not isinstance(fp, dict):
        raise SchemaValidationError("rule 7: frozen_parameters must be a mapping")
    for sub in REQUIRED_FROZEN_PARAMETERS_SUBBLOCKS:
        if sub not in fp or not fp[sub]:
            raise SchemaValidationError(f"rule 7: frozen_parameters.{sub} required and non-empty")

    # Rule 13: model.model_kind enum
    mk = fp["model"].get("model_kind")
    if mk not in VALID_MODEL_KIND:
        raise SchemaValidationError(
            f"rule 13: frozen_parameters.model.model_kind {mk!r} not in "
            f"{sorted(VALID_MODEL_KIND)}"
        )

    # Rules 14, 14a, 16: dynamical preconditions
    if mk == "dynamical":
        for f in ("system_hamiltonian", "coupling_operator", "bath_type"):
            if not fp["model"].get(f):
                raise SchemaValidationError(
                    f"rule 14: model_kind == dynamical requires model.{f} " f"at model level"
                )
        if not fp["numerical"].get("time_grid"):
            raise SchemaValidationError(
                "rule 16: model_kind == dynamical requires numerical.time_grid"
            )
        # Rule 14a: bath_type != none ⇒ bath_state at model level OR per-case
        if fp["model"]["bath_type"] != "none":
            test_cases = fp["model"].get("test_cases") or []
            model_level_bs = fp["model"].get("bath_state")
            if model_level_bs:
                pass
            elif test_cases and all(c.get("bath_state") for c in test_cases):
                pass
            else:
                raise SchemaValidationError(
                    "rule 14a: bath_type != 'none' requires bath_state at model "
                    "level OR in every entry of test_cases"
                )

    # Rule 15a: algebraic_map ⇒ test_cases required and non-empty
    if mk == "algebraic_map":
        tc = fp["model"].get("test_cases")
        if not tc:
            raise SchemaValidationError(
                "rule 15a: model_kind == algebraic_map requires non-empty test_cases"
            )
        for forbidden in ("system_hamiltonian", "coupling_operator", "bath_type"):
            v = fp["model"].get(forbidden)
            if v:
                raise SchemaValidationError(
                    f"rule 15a: model_kind == algebraic_map requires "
                    f"model.{forbidden} to be absent or empty; got {v!r}"
                )

    # Rule 15: every test_cases entry has minimum fields
    test_cases = fp["model"].get("test_cases") or []
    for i, case in enumerate(test_cases):
        for f in ("name", "description", "expected_outcome", "reference"):
            if not case.get(f):
                raise SchemaValidationError(f"rule 15: test_cases[{i}].{f} required and non-empty")

    # Rule 8: perturbative_order non-negative integer
    po = fp["truncation"].get("perturbative_order")
    if not isinstance(po, int) or isinstance(po, bool) or po < 0:
        raise SchemaValidationError(
            f"rule 8: frozen_parameters.truncation.perturbative_order must be "
            f"a non-negative integer; got {po!r}"
        )

    # Rule 9: threshold positive
    thr = data["acceptance_criterion"].get("threshold")
    if not isinstance(thr, (int, float)) or isinstance(thr, bool) or thr <= 0:
        raise SchemaValidationError(
            f"rule 9: acceptance_criterion.threshold must be a positive number; " f"got {thr!r}"
        )

    # Rule 10: stewardship_flag.status enum + conditional fields
    sf = data["stewardship_flag"]
    sf_status = sf.get("status")
    if sf_status not in VALID_STEWARDSHIP_FLAG:
        raise SchemaValidationError(
            f"rule 10: stewardship_flag.status {sf_status!r} not in "
            f"{sorted(VALID_STEWARDSHIP_FLAG)}"
        )
    if sf_status != "unflagged" and not sf.get("rationale"):
        raise SchemaValidationError(
            f"rule 10: stewardship_flag.status {sf_status!r} requires non-empty rationale"
        )
    if sf_status in {"primary", "secondary"} and not sf.get("data_source"):
        raise SchemaValidationError(
            f"rule 10: stewardship_flag.status {sf_status!r} requires non-empty data_source"
        )
    if sf_status == "stewardship-conflict-bound" and not sf.get("search_performed"):
        raise SchemaValidationError(
            "rule 10: stewardship_flag.status 'stewardship-conflict-bound' "
            "requires non-empty search_performed"
        )

    # Rule 17: frozen_parameters.sweep is optional. When present:
    # parameter_name, parameter_path, sweep_range required; sweep_range
    # has start, end, n_points, scheme; scheme is in the enum.
    sweep = fp.get("sweep")
    if sweep is not None:
        if not isinstance(sweep, dict):
            raise SchemaValidationError("rule 17: frozen_parameters.sweep must be a mapping")
        for f in ("parameter_name", "parameter_path", "sweep_range"):
            if not sweep.get(f):
                raise SchemaValidationError(
                    f"rule 17: frozen_parameters.sweep.{f} required and non-empty"
                )
        sr = sweep["sweep_range"]
        if not isinstance(sr, dict):
            raise SchemaValidationError(
                "rule 17: frozen_parameters.sweep.sweep_range must be a mapping"
            )
        for f in ("start", "end", "n_points", "scheme"):
            if f not in sr:
                raise SchemaValidationError(
                    f"rule 17: frozen_parameters.sweep.sweep_range.{f} required"
                )
        if not isinstance(sr["start"], (int, float)) or isinstance(sr["start"], bool):
            raise SchemaValidationError(
                f"rule 17: sweep.sweep_range.start must be a number; got {sr['start']!r}"
            )
        if not isinstance(sr["end"], (int, float)) or isinstance(sr["end"], bool):
            raise SchemaValidationError(
                f"rule 17: sweep.sweep_range.end must be a number; got {sr['end']!r}"
            )
        if (
            not isinstance(sr["n_points"], int)
            or isinstance(sr["n_points"], bool)
            or sr["n_points"] <= 0
        ):
            raise SchemaValidationError(
                f"rule 17: sweep.sweep_range.n_points must be a positive integer; "
                f"got {sr['n_points']!r}"
            )
        if sr["scheme"] not in VALID_SWEEP_SCHEMES:
            raise SchemaValidationError(
                f"rule 17: sweep.sweep_range.scheme {sr['scheme']!r} not in "
                f"{sorted(VALID_SWEEP_SCHEMES)}"
            )

    # Rule 18: status 'scope-definition' ⇒ unmet preconditions recorded
    # in either failure_mode_log (non-empty) or result.notes (non-empty).
    if data["status"] == "scope-definition":
        has_log = bool(data.get("failure_mode_log"))
        has_notes = bool(r.get("notes"))
        if not (has_log or has_notes):
            raise SchemaValidationError(
                "rule 18: status 'scope-definition' requires unmet preconditions "
                "recorded in failure_mode_log (non-empty) or result.notes (non-empty)"
            )


# ─── Gauge-annotation enforcement ────────────────────────────────────────────


def verify_gauge_annotation(card: BenchmarkCard) -> None:
    """Verify the card's gauge block matches the canonical form.

    Called at the start of run_card(); duplicates rule 6 from
    validate_card_data(), but separates the gauge check so that downstream
    artefact emitters (plots, tables, exports) can call it independently.
    """
    if card.gauge != CANONICAL_GAUGE_BLOCK:
        raise GaugeAnnotationError(
            f"Card {card.card_id} v{card.version}: gauge block does not match "
            f"the canonical Hayden–Sorce minimal-dissipation form. "
            f"Expected {CANONICAL_GAUGE_BLOCK}; got {card.gauge}. "
            "See docs/benchmark_protocol.md §1."
        )


# ─── Test-case handlers (algebraic_map cards) ────────────────────────────────

# Pauli matrices — used by both the algebraic-map Lindblad handlers
# (sigma_z, sigma_minus, sigma_plus) and the dynamical-card derived
# observables (sigma_x, sigma_y, sigma_z).
_SIGMA_X = np.array([[0, 1], [1, 0]], dtype=complex)
_SIGMA_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_SIGMA_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_SIGMA_MINUS = np.array([[0, 1], [0, 0]], dtype=complex)  # |0><1|
_SIGMA_PLUS = np.array([[0, 0], [1, 0]], dtype=complex)  # |1><0|


def _build_lindblad_generator(
    H: np.ndarray,
    jump_operators: list[np.ndarray],
) -> Callable[[np.ndarray], np.ndarray]:
    """Construct L[X] = -i[H, X] + Σ_i (V_i X V_i† - 0.5 {V_i†V_i, X})."""

    def L(X: np.ndarray) -> np.ndarray:
        out = -1j * commutator(H, X)
        for V in jump_operators:
            V_dag = V.conj().T
            out += V @ X @ V_dag
            out -= 0.5 * anticommutator(V_dag @ V, X)
        return out

    return L


def _handler_canonical_lindblad_traceless(
    case: dict[str, Any],
    d: int,
) -> tuple[
    Callable[[np.ndarray], np.ndarray],
    np.ndarray,
    float | None,
    float | None,
]:
    """Card A1 v0.1.1 test_case canonical_lindblad_traceless (Entry 1.B.1).

    H = (omega/2)*sigma_z (traceless); jumps sqrt(gamma_*) * sigma_∓.
    Expected K = H per the dissipator-with-traceless-jumps property.
    Operates only at d=2.

    Returns (L, K_expected, None, None). The trailing Nones signal that
    no HPTA precondition gate and no Hermiticity-of-omega gate apply —
    Lindblad form with traceless jumps is HPTA by construction, and the
    handler does not carry an omega coefficient matrix.
    """
    if d != 2:
        raise NotImplementedError(
            f"canonical_lindblad_traceless handler: only d=2 supported "
            f"at DG-1 (Card A1 v0.1.1); got d={d}"
        )
    p = case["parameters"]
    omega = p["omega"]
    gamma_minus = p["gamma_minus"]
    gamma_plus = p["gamma_plus"]
    H = 0.5 * omega * _SIGMA_Z
    jumps = [
        np.sqrt(gamma_minus) * _SIGMA_MINUS,
        np.sqrt(gamma_plus) * _SIGMA_PLUS,
    ]
    L = _build_lindblad_generator(H, jumps)
    return L, H, None, None


def _handler_markovian_weak_coupling_lamb_shift(
    case: dict[str, Any],
    d: int,
) -> tuple[
    Callable[[np.ndarray], np.ndarray],
    np.ndarray,
    float | None,
    float | None,
]:
    """Card A1 v0.1.1 test_case markovian_weak_coupling_lamb_shift (Entry 1.B.2).

    H = ((omega + 2*delta_LS)/2)*sigma_z (system + Lamb shift, combined);
    single jump sqrt(gamma) * sigma_-. Expected K = H (the combined
    coherent term recovered).
    Operates only at d=2.

    Returns (L, K_expected, None, None). See canonical_lindblad_traceless
    above for why the trailing Nones.
    """
    if d != 2:
        raise NotImplementedError(
            f"markovian_weak_coupling_lamb_shift handler: only d=2 "
            f"supported at DG-1 (Card A1 v0.1.1); got d={d}"
        )
    p = case["parameters"]
    omega = p["omega"]
    delta_LS = p["delta_LS"]
    gamma = p["gamma"]
    H = 0.5 * (omega + 2.0 * delta_LS) * _SIGMA_Z
    jumps = [np.sqrt(gamma) * _SIGMA_MINUS]
    L = _build_lindblad_generator(H, jumps)
    return L, H, None, None


# ─── Symbolic-operator parser (pseudo-Kraus handlers, B1) ───────────────────
#
# Card B1's pseudo_kraus_operators field carries symbolic strings like
# "I + 1j * a * sigma_z" or "sqrt(1 + b**2) * I". The parser evaluates
# these against a restricted namespace: the d=2 Pauli operators plus
# sqrt and 1j, augmented with the card's per-case `parameters` dict.
# AST-level whitelisting rejects attribute access, subscripting, and
# calls to anything other than sqrt — so a card cannot smuggle a Python
# expression that reads files, imports modules, or otherwise escapes
# the namespace.
#
# Adding a new dimension or a new symbolic identifier requires extending
# _OPERATOR_NAMESPACE_BUILDERS or _ALLOWED_FUNCTION_NAMES below.

_OPERATOR_NAMESPACE_BUILDERS: dict[int, Callable[[], dict[str, Any]]] = {
    2: lambda: {
        "I": np.eye(2, dtype=complex),
        "sigma_x": _SIGMA_X,
        "sigma_y": _SIGMA_Y,
        "sigma_z": _SIGMA_Z,
        "sigma_minus": _SIGMA_MINUS,
        "sigma_plus": _SIGMA_PLUS,
    },
}

_ALLOWED_FUNCTION_NAMES = frozenset({"sqrt"})

# Whitelist of AST node types permitted in a symbolic-operator expression.
# Any node outside this set raises during _eval_operator_expression.
_ALLOWED_AST_NODES: tuple[type, ...] = (
    ast.Expression,
    ast.Constant,  # numeric / complex literals (0.5, 1.0, 1j)
    ast.Name,  # identifiers — bound by the namespace
    ast.Load,  # context for Name reads
    ast.UnaryOp,
    ast.USub,
    ast.UAdd,
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.MatMult,
    ast.Call,  # only sqrt(...) — verified semantically below
)


def _eval_operator_expression(
    expr: str,
    parameters: dict[str, Any],
    d: int,
) -> np.ndarray:
    """Evaluate a symbolic-operator expression in a restricted namespace.

    Parameters
    ----------
    expr : str
        Symbolic expression. Identifiers must come from the d-dimensional
        operator namespace (I, sigma_x, sigma_y, sigma_z, sigma_minus,
        sigma_plus at d=2), the allowed function set ({sqrt}), or the
        ``parameters`` dict. Numeric and complex literals (e.g. 1j) are
        permitted.
    parameters : dict
        Per-case named parameters (e.g. {"a": 0.5}). Keys must not shadow
        the operator namespace or the allowed function names.
    d : int
        Hilbert-space dimension. Currently only d=2 is registered.

    Returns
    -------
    np.ndarray
        The d×d (or scalar-promoted) operator matrix.

    Raises
    ------
    NotImplementedError
        If d is not in _OPERATOR_NAMESPACE_BUILDERS.
    ValueError
        If the expression contains forbidden AST nodes, calls to
        functions other than sqrt, or parameter names shadowing
        namespace identifiers.

    Examples
    --------
    >>> _eval_operator_expression("I + 1j * a * sigma_z", {"a": 0.5}, 2)
    array([[1.+0.5j, 0.+0.j ], [0.+0.j , 1.-0.5j]])
    """
    if d not in _OPERATOR_NAMESPACE_BUILDERS:
        raise NotImplementedError(
            f"_eval_operator_expression: no operator namespace registered for "
            f"d={d}; known dimensions: {sorted(_OPERATOR_NAMESPACE_BUILDERS.keys())}"
        )
    namespace = _OPERATOR_NAMESPACE_BUILDERS[d]()
    reserved = set(namespace) | _ALLOWED_FUNCTION_NAMES
    for pname in parameters:
        if pname in reserved:
            raise ValueError(
                f"_eval_operator_expression: parameter name {pname!r} shadows a "
                f"reserved identifier (operators or function names); rename in "
                f"the card's parameters block"
            )
    namespace.update(parameters)
    namespace["sqrt"] = np.sqrt

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"_eval_operator_expression: cannot parse expression {expr!r}: {e}") from e

    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST_NODES):
            raise ValueError(
                f"_eval_operator_expression: forbidden AST node "
                f"{type(node).__name__} in expression {expr!r}"
            )
        if isinstance(node, ast.Call):
            if not (isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCTION_NAMES):
                raise ValueError(
                    f"_eval_operator_expression: only calls to "
                    f"{sorted(_ALLOWED_FUNCTION_NAMES)} are permitted; "
                    f"got call in expression {expr!r}"
                )
        if isinstance(node, ast.Name) and node.id not in namespace:
            raise ValueError(
                f"_eval_operator_expression: unknown identifier {node.id!r} "
                f"in expression {expr!r}; available: {sorted(namespace.keys())}"
            )

    return eval(  # noqa: S307 — restricted namespace + AST whitelist enforced above
        compile(tree, "<operator-expression>", "eval"),
        {"__builtins__": {}},
        namespace,
    )


# ─── Pseudo-Kraus generator builder + handler factory (B1) ──────────────────


def _build_pseudo_kraus_generator(
    operators: list[np.ndarray],
    coefficients: list[float],
) -> Callable[[np.ndarray], np.ndarray]:
    """Build L(rho) = sum_j gamma_j E_j rho E_j^dagger.

    Caller is responsible for HPTA: real coefficients and
    sum_j gamma_j E_j^dagger E_j = 0. This function does not validate.
    """

    def L(rho: np.ndarray) -> np.ndarray:
        out = np.zeros_like(rho, dtype=complex)
        for E, g in zip(operators, coefficients, strict=False):
            out += g * (E @ rho @ E.conj().T)
        return out

    return L


def _hpta_residual(
    operators: list[np.ndarray],
    coefficients: list[float],
) -> float:
    """Absolute Frobenius norm of sum_j gamma_j E_j^dagger E_j."""
    acc = np.zeros_like(operators[0], dtype=complex)
    for E, g in zip(operators, coefficients, strict=False):
        acc += g * (E.conj().T @ E)
    return float(np.linalg.norm(acc, ord="fro"))


def _make_pseudo_kraus_handler(
    expected_K: Callable[[dict[str, Any]], np.ndarray],
) -> Callable[
    [dict[str, Any], int],
    tuple[
        Callable[[np.ndarray], np.ndarray],
        np.ndarray,
        float,
        float | None,
    ],
]:
    """Return a handler for a pseudo-Kraus algebraic_map test_case.

    The returned handler:
      1. Parses ``case["pseudo_kraus_operators"]`` against the d=2
         operator namespace augmented with ``case["parameters"]``.
      2. Reads ``case["pseudo_kraus_coefficients"]`` as real floats.
      3. Builds L(rho) = sum_j gamma_j E_j rho E_j^dagger.
      4. Computes the HPTA residual ||sum_j gamma_j E_j^dagger E_j||_F.
      5. Calls ``expected_K(case)`` to obtain K_expected for this case.

    Returns (L, K_expected, hpta_residual, None). The trailing None is
    the Hermiticity-of-omega slot — diagonal pseudo-Kraus has real
    coefficients (the 1×1 / vector form is trivially Hermitian, and the
    runner has no omega matrix to gate on).
    """

    def handler(
        case: dict[str, Any],
        d: int,
    ) -> tuple[
        Callable[[np.ndarray], np.ndarray],
        np.ndarray,
        float,
        float | None,
    ]:
        if d != 2:
            raise NotImplementedError(
                f"pseudo-Kraus handler: only d=2 supported (Card B1 v0.1.0); " f"got d={d}"
            )
        params = case.get("parameters") or {}
        op_exprs = case["pseudo_kraus_operators"]
        coeff_list = case["pseudo_kraus_coefficients"]
        operators = [_eval_operator_expression(e, params, d) for e in op_exprs]
        coefficients = [float(g) for g in coeff_list]
        L = _build_pseudo_kraus_generator(operators, coefficients)
        residual = _hpta_residual(operators, coefficients)
        K_expected = expected_K(case)
        return L, K_expected, residual, None

    return handler


# Per-test-case K_expected closures. Kept as small named functions so the
# handler factory's parameterisation stays readable in the registry below.


def _expected_K_pseudo_kraus_diagonal_sigma_z(case: dict[str, Any]) -> np.ndarray:
    """K = -a * sigma_z; transcription §7 evaluated at the case's a."""
    a = float(case["parameters"]["a"])
    return -a * _SIGMA_Z


def _expected_K_pseudo_kraus_diagonal_sigma_x(case: dict[str, Any]) -> np.ndarray:
    """K = -b * sigma_x; sigma_x analog of transcription §7 at the case's b."""
    b = float(case["parameters"]["b"])
    return -b * _SIGMA_X


def _expected_K_pseudo_kraus_traceless_jumps(case: dict[str, Any]) -> np.ndarray:
    """K = 0; transcription §5 'every V_i traceless => H_HS = 0'."""
    return np.zeros((2, 2), dtype=complex)


# ─── Off-diagonal pseudo-Kraus support (B2) ─────────────────────────────────
#
# Card B2's pseudo_kraus_offdiag_omega field carries a 2D list of symbolic
# strings (e.g. "1.0", "1j * beta", "-1j * beta") that must reduce to
# complex scalars under the case's parameters. The same AST whitelist as
# B1's operator parser applies (Constant / Name / numeric BinOp / UnaryOp /
# sqrt(...)), but the namespace excludes operator identifiers — an omega
# entry must be scalar-typed, so I / sigma_x / ... in scope would be a
# category error. _eval_complex_scalar_expression enforces the scalar
# discipline by stripping the operator namespace before evaluation.


def _eval_complex_scalar_expression(
    expr: str,
    parameters: dict[str, Any],
) -> complex:
    """Evaluate a complex-scalar expression in a parameters-only namespace.

    Used by B2's pseudo_kraus_offdiag_omega entries (and any future card
    surface that needs scalar coefficients without operator identifiers
    in scope). Reuses the AST whitelist from _eval_operator_expression
    but keeps the namespace narrow: only the case's `parameters`, the
    `sqrt` builtin, and numeric / complex literals.

    Parameters
    ----------
    expr : str
        Symbolic scalar expression. Identifiers must come from the
        ``parameters`` dict; ``sqrt`` is the only allowed function call;
        numeric and complex literals (e.g. 1j, -1.0) are permitted.
    parameters : dict
        Per-case named parameters.

    Returns
    -------
    complex
        The evaluated scalar, coerced to complex.

    Raises
    ------
    ValueError
        If the expression contains forbidden AST nodes, calls to
        functions other than sqrt, parameter names shadowing sqrt, or
        identifiers not in ``parameters``.
    """
    namespace: dict[str, Any] = dict(parameters)
    for pname in parameters:
        if pname in _ALLOWED_FUNCTION_NAMES:
            raise ValueError(
                f"_eval_complex_scalar_expression: parameter name {pname!r} "
                f"shadows a reserved function name; rename in the card's "
                f"parameters block"
            )
    namespace["sqrt"] = np.sqrt

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(
            f"_eval_complex_scalar_expression: cannot parse expression " f"{expr!r}: {e}"
        ) from e

    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST_NODES):
            raise ValueError(
                f"_eval_complex_scalar_expression: forbidden AST node "
                f"{type(node).__name__} in expression {expr!r}"
            )
        if isinstance(node, ast.Call):
            if not (isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCTION_NAMES):
                raise ValueError(
                    f"_eval_complex_scalar_expression: only calls to "
                    f"{sorted(_ALLOWED_FUNCTION_NAMES)} are permitted; "
                    f"got call in expression {expr!r}"
                )
        if isinstance(node, ast.Name) and node.id not in namespace:
            raise ValueError(
                f"_eval_complex_scalar_expression: unknown identifier "
                f"{node.id!r} in expression {expr!r}; available: "
                f"{sorted(namespace.keys())}"
            )

    value = eval(  # noqa: S307 — restricted namespace + AST whitelist enforced above
        compile(tree, "<scalar-expression>", "eval"),
        {"__builtins__": {}},
        namespace,
    )
    return complex(value)


def _parse_offdiag_omega(
    rows: list[list[str]],
    parameters: dict[str, Any],
) -> np.ndarray:
    """Parse a 2D list of complex-scalar string expressions into an n×n array.

    Validates that the input is square (rows of equal length); the
    Hermiticity check happens at the runner level via _hermiticity_residual.
    """
    n = len(rows)
    omega = np.zeros((n, n), dtype=complex)
    for i, row in enumerate(rows):
        if len(row) != n:
            raise ValueError(
                f"_parse_offdiag_omega: row {i} has length {len(row)}; "
                f"expected square matrix of size {n}×{n}"
            )
        for j, entry in enumerate(row):
            omega[i, j] = _eval_complex_scalar_expression(entry, parameters)
    return omega


def _hermiticity_residual(omega: np.ndarray) -> float:
    """Absolute Frobenius norm of omega - omega^dagger."""
    return float(np.linalg.norm(omega - omega.conj().T, ord="fro"))


def _build_offdiag_pseudo_kraus_generator(
    operators: list[np.ndarray],
    omega: np.ndarray,
) -> Callable[[np.ndarray], np.ndarray]:
    """Build L(rho) = sum_{i,j} omega_{ij} V_i rho V_j^dagger.

    Caller is responsible for Hermiticity of omega and HPTA
    (sum_{i,j} omega_{ij} V_j^dagger V_i = 0). This function does not
    validate; the runner gates on those preconditions before evaluating
    the K comparison.
    """
    n = len(operators)

    def L(rho: np.ndarray) -> np.ndarray:
        out = np.zeros_like(rho, dtype=complex)
        for i in range(n):
            V_i = operators[i]
            for j in range(n):
                V_j_dag = operators[j].conj().T
                out += omega[i, j] * (V_i @ rho @ V_j_dag)
        return out

    return L


def _offdiag_hpta_residual(
    operators: list[np.ndarray],
    omega: np.ndarray,
) -> float:
    """Absolute Frobenius norm of sum_{i,j} omega_{ij} V_j^dagger V_i."""
    n = len(operators)
    d = operators[0].shape[0]
    acc = np.zeros((d, d), dtype=complex)
    for i in range(n):
        V_i = operators[i]
        for j in range(n):
            V_j_dag = operators[j].conj().T
            acc += omega[i, j] * (V_j_dag @ V_i)
    return float(np.linalg.norm(acc, ord="fro"))


def _make_offdiag_pseudo_kraus_handler(
    expected_K: Callable[[dict[str, Any]], np.ndarray],
) -> Callable[
    [dict[str, Any], int],
    tuple[
        Callable[[np.ndarray], np.ndarray],
        np.ndarray,
        float,
        float,
    ],
]:
    """Return a handler for an off-diagonal pseudo-Kraus algebraic_map test_case.

    The returned handler:
      1. Parses ``case["pseudo_kraus_offdiag_operators"]`` against the
         d=2 operator namespace augmented with ``case["parameters"]``.
      2. Parses ``case["pseudo_kraus_offdiag_omega"]`` (2D list of
         strings) against the parameters-only scalar namespace.
      3. Computes the Hermiticity residual ||omega - omega^dagger||_F.
      4. Builds L(rho) = sum_{i,j} omega_{ij} V_i rho V_j^dagger.
      5. Computes the HPTA residual ||sum_{i,j} omega_{ij} V_j^dagger V_i||_F.
      6. Calls ``expected_K(case)`` to obtain K_expected for this case.

    Returns (L, K_expected, hpta_residual, hermiticity_residual).
    """

    def handler(
        case: dict[str, Any],
        d: int,
    ) -> tuple[
        Callable[[np.ndarray], np.ndarray],
        np.ndarray,
        float,
        float,
    ]:
        if d != 2:
            raise NotImplementedError(
                f"off-diagonal pseudo-Kraus handler: only d=2 supported "
                f"(Card B2 v0.1.0); got d={d}"
            )
        params = case.get("parameters") or {}
        op_exprs = case["pseudo_kraus_offdiag_operators"]
        omega_rows = case["pseudo_kraus_offdiag_omega"]
        operators = [_eval_operator_expression(e, params, d) for e in op_exprs]
        omega = _parse_offdiag_omega(omega_rows, params)
        if omega.shape[0] != len(operators):
            raise ValueError(
                f"off-diagonal pseudo-Kraus handler: omega is "
                f"{omega.shape[0]}×{omega.shape[0]} but {len(operators)} "
                f"V_i operators were provided; sizes must match"
            )
        hermiticity = _hermiticity_residual(omega)
        L = _build_offdiag_pseudo_kraus_generator(operators, omega)
        hpta = _offdiag_hpta_residual(operators, omega)
        K_expected = expected_K(case)
        return L, K_expected, hpta, hermiticity

    return handler


# Per-test-case K_expected closures for B2, derived from transcription §4b:
#
#   H_HS^off-diag = (1/2id) sum_{i,j} omega_{ij}
#                          (Tr(V_i) V_j^dagger - Tr(V_j^dagger) V_i)
#
# Each fixture's per-term derivation is recorded in the YAML's
# expected_outcome and §7a; here we encode the closed-form result.


def _expected_K_offdiag_omega_imaginary_sigma_z(case: dict[str, Any]) -> np.ndarray:
    """K = beta * sigma_z; transcription §7a worked fixture at the case's beta."""
    beta = float(case["parameters"]["beta"])
    return beta * _SIGMA_Z


def _expected_K_offdiag_omega_imaginary_sigma_x(case: dict[str, Any]) -> np.ndarray:
    """K = -beta * sigma_x; sigma_x analog of §7a at the case's beta."""
    beta = float(case["parameters"]["beta"])
    return -beta * _SIGMA_X


def _expected_K_offdiag_omega_diagonal_only(case: dict[str, Any]) -> np.ndarray:
    """K = 0; degenerate sub-case where omega's off-diagonal entries vanish
    and the V_i pair (I, sigma_z) gives Tr-cancellation in the (1,1) summand
    and a traceless-V in the (2,2) summand."""
    return np.zeros((2, 2), dtype=complex)


# ─── Basis-builder registry (cross-basis runner, B3) ────────────────────────
#
# Card B3 v0.1.0's per-case `comparison_basis` field names a Hilbert–Schmidt
# orthonormal basis to compare against the matrix-unit reference. The runner
# resolves the name through this registry; adding a new comparison_basis
# value (e.g. "hermitian_basis") requires registering its builder here.

_BASIS_BUILDERS: dict[str, Callable[[int], list[np.ndarray]]] = {
    "matrix_unit": matrix_unit_basis,
    "su_d_generator": su_d_generator_basis,
}


# ─── Displacement-profile registry (Council Act 2 cleared, 2026-05-04) ──────
#
# The displacement-mode profiles α(ω) for the coherent-displaced bath state
# appearing in CL-2026-005 v0.4 Entries 3.B.3 + 4.B.2 are Council-cleared
# under handling (c) of the subsidiary briefing v0.3.0 §4.3 (deliberation
# transcript: ledger/CL-2026-005_v0.4_council-deliberation_act2_2026-05-04.md).
# The four cleared profile keys at v0.1.0 are:
#
#   delta-omega_c      single-mode at bath cutoff ω_c          (§3.1)
#   delta-omega_S      single-mode at system Bohr ω_S          (§3.2)
#   sqrt-J             broadband ∝ √(J(ω))                     (§3.3)
#   gaussian           Gaussian envelope (ω_d, Δω)             (§3.4)
#
# Adding or removing entries requires fresh Council clearance per the
# subsidiary briefing v0.3.0 §6.1 registry-clearance-gate; the registry is
# not open to ad-hoc Steward-discretion modifications.
#
# This runner-level registry imports the constructors verbatim from
# cbg.displacement_profiles.REGISTERED_PROFILES to maintain a single source
# of truth for the cleared set. The B4-conv-registry_v0.1.0 card's
# per-test-case ``displacement_profile`` field resolves through this dict.

_DISPLACEMENT_PROFILES: dict[str, Callable[..., Any]] = dict(_CBG_REGISTERED_PROFILES)


# ─── Basis-independence handler factory (B3) ────────────────────────────────
#
# B3's three test_cases reuse known-good fixtures from A1 / B1 — see
# B3 v0.1.0 YAML `frozen_parameters.model.test_cases[i].reference`. Each B3
# handler delegates fixture-to-L construction to the corresponding A1 / B1
# handler, then discards the K_expected slot: B3 verifies basis-independence
# of K_from_generator on the generated L, not the value of K (that is owned
# by A1 / B1 and already PASS).
#
# A B3 handler returns (L, None, hpta_residual_or_None). The None in the
# K_expected slot signals to the runner that the case carries a
# `comparison_basis` and must use the cross-basis comparison branch.


def _make_basis_independence_handler(
    base_handler: Callable[
        [dict[str, Any], int],
        tuple[
            Callable[[np.ndarray], np.ndarray],
            np.ndarray,
            float | None,
            float | None,
        ],
    ],
) -> Callable[
    [dict[str, Any], int],
    tuple[
        Callable[[np.ndarray], np.ndarray],
        None,
        float | None,
        float | None,
    ],
]:
    """Wrap an A1 / B1 handler to drop K_expected for B3 cross-basis use.

    The wrapped handler builds L identically to the source-card handler
    (so the parser / Lindblad-builder logic is reused unchanged) and
    returns (L, None, hpta_residual, hermiticity_residual). The None in
    the second slot is the runner's signal to switch to the cross-basis
    comparison branch; the trailing slots pass through whatever the
    source handler surfaced.
    """

    def handler(
        case: dict[str, Any],
        d: int,
    ) -> tuple[
        Callable[[np.ndarray], np.ndarray],
        None,
        float | None,
        float | None,
    ]:
        L, _K_expected, hpta_residual, hermiticity_residual = base_handler(case, d)
        return L, None, hpta_residual, hermiticity_residual

    return handler


# Registry: test_case name → handler. Adding a new test_case to a card
# requires registering its handler here. Handlers return a 4-tuple:
# (L, K_expected_or_None, hpta_residual_or_None, hermiticity_residual_or_None).
#   - Lindblad-form (A1): (L, K, None, None)
#   - Diagonal pseudo-Kraus (B1): (L, K, hpta, None)
#   - Off-diagonal pseudo-Kraus (B2): (L, K, hpta, hermiticity)
#   - Basis-independence (B3): (L, None, hpta_or_None, hermiticity_or_None)
# K_expected = None is the runner's signal to take the cross-basis comparison
# branch (B3); the trailing residual slots gate the runner's precondition
# checks.
_TEST_CASE_HANDLERS: dict[
    str,
    Callable[
        [dict[str, Any], int],
        tuple[
            Callable[[np.ndarray], np.ndarray],
            np.ndarray | None,
            float | None,
            float | None,
        ],
    ],
] = {
    "canonical_lindblad_traceless": _handler_canonical_lindblad_traceless,
    "markovian_weak_coupling_lamb_shift": _handler_markovian_weak_coupling_lamb_shift,
    "pseudo_kraus_diagonal_sigma_z": _make_pseudo_kraus_handler(
        _expected_K_pseudo_kraus_diagonal_sigma_z
    ),
    "pseudo_kraus_diagonal_sigma_x": _make_pseudo_kraus_handler(
        _expected_K_pseudo_kraus_diagonal_sigma_x
    ),
    "pseudo_kraus_traceless_jumps": _make_pseudo_kraus_handler(
        _expected_K_pseudo_kraus_traceless_jumps
    ),
    "offdiag_omega_imaginary_sigma_z": _make_offdiag_pseudo_kraus_handler(
        _expected_K_offdiag_omega_imaginary_sigma_z
    ),
    "offdiag_omega_imaginary_sigma_x": _make_offdiag_pseudo_kraus_handler(
        _expected_K_offdiag_omega_imaginary_sigma_x
    ),
    "offdiag_omega_diagonal_only": _make_offdiag_pseudo_kraus_handler(
        _expected_K_offdiag_omega_diagonal_only
    ),
    "basis_independence_pseudo_kraus_sigma_z": _make_basis_independence_handler(
        _make_pseudo_kraus_handler(_expected_K_pseudo_kraus_diagonal_sigma_z)
    ),
    "basis_independence_lindblad_traceless": _make_basis_independence_handler(
        _handler_canonical_lindblad_traceless
    ),
    "basis_independence_lindblad_lamb_shift": _make_basis_independence_handler(
        _handler_markovian_weak_coupling_lamb_shift
    ),
}


# ─── Runner ──────────────────────────────────────────────────────────────────


def run_card(card: BenchmarkCard) -> CardResult:
    """Run a benchmark card to verdict.

    Dispatches by DG target / model_kind. DG-3 cards use the dedicated
    cross-method branch; algebraic_map cards run end-to-end using
    cbg.basis + cbg.effective_hamiltonian + numerical.tensor_ops; other
    dynamical cards use the TCL structural-identity runner.

    Verifies the gauge annotation before any computation; raises
    GaugeAnnotationError if the canonical block has been tampered with.
    """
    verify_gauge_annotation(card)
    if card.status == "scope-definition":
        _refuse_scope_definition(card)  # raises ScopeDefinitionNotRunnableError
    if card.dg_target == "DG-4":
        return _run_dg4_sweep(card)
    if card.dg_target == "DG-3":
        return _run_cross_method(card)
    if card.model_kind == "algebraic_map":
        return _run_algebraic_map(card)
    if card.model_kind == "dynamical":
        return _run_dynamical(card)
    # Unreachable given rule 13 validation, but defensive:
    raise SchemaValidationError(f"run_card: unknown model_kind {card.model_kind!r}")


def _refuse_scope_definition(card: BenchmarkCard) -> None:
    """Raise a clear ScopeDefinitionNotRunnableError citing the card's preconditions.

    Reads the unmet preconditions from the card's ``failure_mode_log`` and
    ``result.notes`` (Rule 18 requires at least one of those to be
    populated) and folds them into the error message so callers see the
    specific reason this card is intentionally not runnable.
    """
    preconditions: list[str] = []
    for entry in card.failure_mode_log or []:
        change = (entry.get("change") or "").strip()
        reason = (entry.get("reason") or "").strip()
        if change or reason:
            preconditions.append(
                f"failure_mode_log entry {entry.get('date', '?')}: "
                f"change={change!r}; reason={reason!r}"
            )
    notes = (card.result.get("notes") or "").strip() if card.result else ""
    if notes:
        preconditions.append(f"result.notes: {notes!r}")
    detail = "\n  - ".join(preconditions) if preconditions else "(no detail recorded)"
    raise ScopeDefinitionNotRunnableError(
        f"run_card: card {card.card_id} {card.version} has "
        f"status='scope-definition' (SCHEMA.md v0.1.3 Rule 18). "
        f"Scope-definition cards are not runnable until their "
        f"preconditions are met and the card is superseded by a "
        f"frozen-awaiting-run successor. Recorded preconditions:\n"
        f"  - {detail}"
    )


def _refuse_dg4_sweep(card: BenchmarkCard) -> NoReturn:
    """Raise a clear DG4SweepRunnerNotImplementedError describing the gap.

    The DG-4 sweep runner is not yet implemented. The error message names
    the two prerequisite pieces (TCL recursion at orders ≥ 3, and the
    sweep-block-aware runner branch) so the path forward is auditable.
    """
    fp = card.frozen_parameters
    sweep = fp.get("sweep") if isinstance(fp, dict) else None
    sweep_summary = ""
    if isinstance(sweep, dict):
        param = sweep.get("parameter_name", "?")
        rng = sweep.get("sweep_range", {})
        sweep_summary = (
            f" Sweep: {param} from {rng.get('start')} to {rng.get('end')} "
            f"({rng.get('n_points')} points, {rng.get('scheme')})."
        )
    raise DG4SweepRunnerNotImplementedError(
        f"run_card: card {card.card_id} {card.version} (dg_target=DG-4) "
        f"requires the DG-4 failure-envelope sweep runner, which is not "
        f"yet implemented.{sweep_summary} Two pieces are missing: (i) "
        f"a trusted order-4 L_4 source for the parity-aware "
        f"r_4 = ||L_4^dis|| / ||L_2^dis|| metric (analytic Path A "
        f"preferred; Path B numerical extraction must carry its finite-env "
        f"floor in result.notes), and (ii) a sweep-block-aware runner "
        f"branch consuming frozen_parameters.sweep (SCHEMA.md v0.1.3 "
        f"Rule 17). Card becomes runnable when both land."
    )


# ─── DG-4 failure-envelope sweep runner (Phase C) ───────────────────────────


# Path B Richardson-extraction defaults (matches DG-4 work plan v0.1.4 Phase C
# and the 2026-05-06 Path B pilot configuration). The runner reads any
# overrides from card.frozen_parameters.numerical.path_b.* extras; defaults
# below are production-quality (the pilot's well-conditioned configuration).
_DG4_PATH_B_DEFAULTS: dict[str, Any] = {
    "alpha_values": (0.01, 0.015, 0.02, 0.025, 0.03),
    "n_bath_modes": 4,
    "n_levels_per_mode": 3,
}

# Reproducibility-perturbation set per DG-4 work plan v0.1.4 §3 Phase C.
# upper_cutoff_factor lives on the runner-side numerical.quadrature allow-list
# (Phase B.4 _quadrature_kwargs); omega_c is a model-spec mutation at
# bath_spectral_density.cutoff_frequency (NOT routed through the allow-list).
_DG4_REPRO_PERTURBATIONS: tuple[dict[str, Any], ...] = (
    {
        "name": "upper_cutoff_factor=20",
        "kind": "quadrature",
        "key": "upper_cutoff_factor",
        "value": 20.0,
    },
    {
        "name": "upper_cutoff_factor=40",
        "kind": "quadrature",
        "key": "upper_cutoff_factor",
        "value": 40.0,
    },
    {"name": "omega_c=9.0", "kind": "model_spec", "key": "cutoff_frequency", "value": 9.0},
    {"name": "omega_c=11.0", "kind": "model_spec", "key": "cutoff_frequency", "value": 11.0},
)


def _run_dg4_sweep(card: BenchmarkCard) -> CardResult:
    """DG-4 failure-envelope sweep runner (Phase C of DG-4 work plan v0.1.4).

    Iterates over the frozen sweep of ``coupling_strength`` and evaluates the
    parity-aware even-order ratio

        r_4(alpha**2) = alpha**2 * (<||L_4^dis||>_t / <||L_2^dis||>_t)

    via Path B numerical Richardson extraction (`benchmarks.numerical_tcl_extraction`
    `path_b_dissipator_norm_coefficients`). Per-failing-candidate-alpha
    reproducibility re-runs use the v0.1.4 perturbation set:
    ``upper_cutoff_factor`` via the runner-side numerical-quadrature allow-list,
    and ``omega_c`` (= ``bath_spectral_density.cutoff_frequency``) via direct
    model-spec mutation.

    Verdict logic:
      - PASS iff at least one alpha is classified ``convergence_failure``
        (r_4 > 1 baseline AND r_4 > 1 stable under all four perturbations).
      - CONDITIONAL iff at least one alpha is failing-candidate but all
        reclassify to ``truncation_artefact`` under at least one perturbation.
      - FAIL iff no alpha gives r_4 > 1 baseline (cause:
        ``no-failure-found-in-frozen-range`` per Risk #8 discipline).

    Path B carries a finite-env extraction floor; the floor magnitude is
    reported in ``result.notes`` so verdicts can carry the documented
    uncertainty band.
    """
    fp = card.frozen_parameters
    sweep = fp.get("sweep") if isinstance(fp, dict) else None
    if not isinstance(sweep, dict):
        _refuse_dg4_sweep(card)  # raises with a structured message

    # Path B currently supports only sigma_x + thermal (the D1 v0.1.1 fixture).
    model = fp["model"]
    coupling_op = (model.get("coupling_operator") or "").strip()
    bath_state = model.get("bath_state") or {}
    if coupling_op != "sigma_x":
        raise DG4SweepRunnerNotImplementedError(
            f"_run_dg4_sweep: Path B currently supports only "
            f"coupling_operator='sigma_x'; got {coupling_op!r}. The analytic "
            f"Path A (Companion Sec. IV) extension would unblock other "
            f"couplings."
        )
    if bath_state.get("family") != "thermal":
        raise DG4SweepRunnerNotImplementedError(
            f"_run_dg4_sweep: Path B currently supports only thermal Gaussian "
            f"bath_state; got {bath_state.get('family')!r}."
        )

    path_b_params = _resolve_path_b_params(fp)
    t_grid_arr = build_time_grid(fp["numerical"]["time_grid"]).times
    base_model_spec = _model_spec_for_dg4(fp)
    quadrature_kwargs = _quadrature_kwargs(fp)

    # 1. Baseline coefficients (one Path B fit covers the entire alpha-sweep,
    # since L_n are Taylor coefficients and r_4(alpha**2) scales linearly).
    baseline = _path_b_evaluate(base_model_spec, t_grid_arr, path_b_params, quadrature_kwargs)

    # 2. Per-alpha baseline r_4.
    alpha_sq_grid = _build_dg4_sweep_grid(sweep)
    per_alpha: list[dict[str, Any]] = []
    for alpha_sq in alpha_sq_grid:
        r_4 = _scaled_ratio(alpha_sq, baseline.l4_avg, baseline.l2_avg)
        per_alpha.append(
            {
                "alpha_sq": float(alpha_sq),
                "r_4_baseline": r_4,
                "classification": None,
                "perturbed": {},
            }
        )

    # 3. Reproducibility re-runs (only if at least one alpha is failing-candidate).
    failing_indices = [
        i for i, entry in enumerate(per_alpha) if _is_failing_candidate(entry["r_4_baseline"])
    ]
    perturbed_coeffs: dict[str, Any] = {}
    if failing_indices:
        for perturbation in _DG4_REPRO_PERTURBATIONS:
            perturbed_model_spec, perturbed_quad_kwargs = _apply_dg4_perturbation(
                base_model_spec, quadrature_kwargs, perturbation
            )
            perturbed_coeffs[perturbation["name"]] = _path_b_evaluate(
                perturbed_model_spec,
                t_grid_arr,
                path_b_params,
                perturbed_quad_kwargs,
            )

    # 4. Classify each alpha.
    for entry in per_alpha:
        r_4_baseline = entry["r_4_baseline"]
        if not np.isfinite(r_4_baseline):
            entry["classification"] = "metric-undefined"
            continue
        if not _is_failing_candidate(r_4_baseline):
            entry["classification"] = "passing"
            continue
        # Failing candidate: check stability under all four perturbations.
        all_failing_under_perturbations = True
        for name, coeffs in perturbed_coeffs.items():
            r_4_perturbed = _scaled_ratio(entry["alpha_sq"], coeffs.l4_avg, coeffs.l2_avg)
            entry["perturbed"][name] = r_4_perturbed
            if not _is_failing_candidate(r_4_perturbed):
                all_failing_under_perturbations = False
        entry["classification"] = (
            "convergence_failure" if all_failing_under_perturbations else "truncation_artefact"
        )

    # 5. alpha_crit interpolation (linear in log(alpha**2)).
    alpha_crit = _interpolate_alpha_crit(per_alpha)

    # 6. Verdict.
    classifications = [e["classification"] for e in per_alpha]
    has_convergence_failure = any(c == "convergence_failure" for c in classifications)
    has_truncation_artefact = any(c == "truncation_artefact" for c in classifications)
    if has_convergence_failure:
        verdict = "PASS"
    elif has_truncation_artefact:
        verdict = "CONDITIONAL"
    else:
        verdict = "FAIL"

    notes = _format_dg4_sweep_notes(
        card=card,
        per_alpha=per_alpha,
        alpha_crit=alpha_crit,
        baseline_coeffs=baseline,
        perturbed_coeffs=perturbed_coeffs,
        path_b_params=path_b_params,
    )

    test_case_results: list[TestCaseResult] = [
        TestCaseResult(
            name="dg4_failure_envelope_sweep",
            passed=has_convergence_failure,
            error=float(
                max(
                    (e["r_4_baseline"] for e in per_alpha if np.isfinite(e["r_4_baseline"])),
                    default=0.0,
                )
            ),
            threshold=card.threshold,
            notes=notes,
        )
    ]

    sweep_data = _build_dg4_sweep_data(
        path_b_params=path_b_params,
        baseline_coeffs=baseline,
        perturbed_coeffs=perturbed_coeffs,
        per_alpha=per_alpha,
        alpha_crit=alpha_crit,
    )

    return CardResult(
        card_id=card.card_id,
        verdict=verdict,
        test_case_results=test_case_results,
        runner_version=__version__,
        notes=notes,
        dg4_sweep_data=sweep_data,
    )


def _coefficients_to_dict(coeffs: Any) -> dict[str, float]:
    """Serialise a DissipatorNormCoefficients dataclass to a plain dict.

    Drops the per-time arrays (l2_per_t, l4_per_t) — those are large and
    not needed for audit reconstruction; the runtime invariant is that
    ``l2_avg = mean(l2_per_t)`` and likewise for l4.
    """
    return {
        "fit_relative_residual": float(coeffs.fit_relative_residual),
        "l2_dissipator_avg": float(coeffs.l2_avg),
        "l4_dissipator_avg": float(coeffs.l4_avg),
        "coefficient_ratio": float(coeffs.l4_avg / max(coeffs.l2_avg, 1e-300)),
    }


def _build_dg4_sweep_data(
    *,
    path_b_params: dict[str, Any],
    baseline_coeffs: Any,
    perturbed_coeffs: Mapping[str, Any],
    per_alpha: list[dict[str, Any]],
    alpha_crit: float | None,
) -> dict[str, Any]:
    """Assemble the audit-complete DG-4 sweep payload (v0.1.2 supersedure).

    Persists per-alpha r_4_baseline, per-alpha-per-perturbation r_4, and
    per-perturbation Path B fit residuals + dissipator-norm coefficients,
    so the verdict's evidence is reproducibility-complete from the
    artefact alone.
    """
    counts = {
        c: 0
        for c in (
            "passing",
            "convergence_failure",
            "truncation_artefact",
            "metric-undefined",
        )
    }
    for entry in per_alpha:
        cls = entry["classification"]
        counts[cls] = counts.get(cls, 0) + 1

    perturbation_records: list[dict[str, Any]] = []
    for spec in _DG4_REPRO_PERTURBATIONS:
        name = spec["name"]
        coeffs = perturbed_coeffs.get(name)
        rec: dict[str, Any] = {
            "name": name,
            "kind": spec["kind"],
            "key": spec["key"],
            "value": spec["value"],
            "operational_in_path_b": True,
            "evaluated": coeffs is not None,
        }
        if coeffs is not None:
            rec.update(_coefficients_to_dict(coeffs))
        perturbation_records.append(rec)

    return {
        "path_b_params": {
            "alpha_values": [float(a) for a in path_b_params["alpha_values"]],
            "n_bath_modes": int(path_b_params["n_bath_modes"]),
            "n_levels_per_mode": int(path_b_params["n_levels_per_mode"]),
        },
        "baseline": _coefficients_to_dict(baseline_coeffs),
        "per_alpha": [
            {
                "alpha_sq": float(entry["alpha_sq"]),
                "r_4_baseline": (
                    float(entry["r_4_baseline"]) if np.isfinite(entry["r_4_baseline"]) else None
                ),
                "classification": entry["classification"],
                "perturbed_r_4": {name: float(value) for name, value in entry["perturbed"].items()},
            }
            for entry in per_alpha
        ],
        "perturbations": perturbation_records,
        "alpha_crit": float(alpha_crit) if alpha_crit is not None else None,
        "classification_counts": counts,
        "max_baseline_r4": float(
            max(
                (e["r_4_baseline"] for e in per_alpha if np.isfinite(e["r_4_baseline"])),
                default=0.0,
            )
        ),
    }


def _resolve_path_b_params(frozen_parameters: Mapping[str, Any]) -> dict[str, Any]:
    """Read optional path-B overrides from frozen_parameters.numerical.path_b.

    Defaults match _DG4_PATH_B_DEFAULTS (the pilot configuration). Card-level
    overrides allow tests to inject reduced fixtures without redefining the
    frozen sweep range.
    """
    numerical = frozen_parameters.get("numerical") or {}
    overrides = numerical.get("path_b") or {}
    out = dict(_DG4_PATH_B_DEFAULTS)
    if "alpha_values" in overrides:
        out["alpha_values"] = tuple(float(a) for a in overrides["alpha_values"])
    if "n_bath_modes" in overrides:
        out["n_bath_modes"] = int(overrides["n_bath_modes"])
    if "n_levels_per_mode" in overrides:
        out["n_levels_per_mode"] = int(overrides["n_levels_per_mode"])
    return out


def _model_spec_for_dg4(frozen_parameters: Mapping[str, Any]) -> dict[str, Any]:
    """Extract a flat model_spec dict for Path B from frozen_parameters.model."""
    return deepcopy(dict(frozen_parameters["model"]))


def _path_b_evaluate(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    path_b_params: dict[str, Any],
    quadrature_kwargs: dict[str, Any],
) -> Any:
    """Run Path B Richardson extraction once at the given model_spec.

    Returns a DissipatorNormCoefficients with l2_avg, l4_avg, etc. Path B
    requires the system Hamiltonian H_S to perform the Schrödinger ->
    interaction picture transformation that the order-4 extractor depends
    on; H_S is built from the model_spec via the spin-boson sigma_x
    factory.

    The card-level ``numerical.quadrature.upper_cutoff_factor`` is threaded
    into the finite-environment builder as ``omega_max_factor``, so the
    DG-4 reproducibility perturbation on this knob is operational under
    Path B (per the v0.1.2 supersedure repair).
    """
    from benchmarks import exact_finite_env, numerical_tcl_extraction
    from models import spin_boson_sigma_x

    spec_with_quad = deepcopy(model_spec)
    H_S, _A = spin_boson_sigma_x.system_arrays_from_spec(spec_with_quad)

    builder_kwargs: dict[str, Any] = {
        "n_bath_modes": path_b_params["n_bath_modes"],
        "n_levels_per_mode": path_b_params["n_levels_per_mode"],
    }
    if "upper_cutoff_factor" in quadrature_kwargs:
        builder_kwargs["omega_max_factor"] = float(quadrature_kwargs["upper_cutoff_factor"])

    alpha_values = list(path_b_params["alpha_values"])
    return numerical_tcl_extraction.path_b_dissipator_norm_coefficients(
        exact_finite_env.build_spin_boson_sigma_x_thermal_total,
        spec_with_quad,
        t_grid.tolist(),
        alpha_values,
        builder_kwargs=builder_kwargs,
        system_hamiltonian=H_S,
    )


def _build_dg4_sweep_grid(sweep: Mapping[str, Any]) -> np.ndarray:
    """Build the alpha-squared (== coupling_strength) grid from the card sweep block."""
    sweep_range = sweep["sweep_range"]
    start = float(sweep_range["start"])
    end = float(sweep_range["end"])
    n_points = int(sweep_range["n_points"])
    scheme = sweep_range["scheme"]
    if scheme == "log_uniform":
        return np.geomspace(start, end, n_points)
    if scheme == "uniform":
        return np.linspace(start, end, n_points)
    raise NotImplementedError(
        f"_build_dg4_sweep_grid: scheme {scheme!r} not yet supported by the "
        f"DG-4 sweep runner; v0.1.0 D1 cards use 'log_uniform' or 'uniform'."
    )


def _scaled_ratio(alpha_sq: float, l4_avg: float, l2_avg: float) -> float:
    """Compute r_4(alpha**2) = alpha**2 * (l4_avg / l2_avg) with a zero-denom guard."""
    eps = float(np.finfo(float).eps)
    if l2_avg <= eps:
        return float("inf")
    return float(alpha_sq) * float(l4_avg) / float(l2_avg)


def _is_failing_candidate(r_4: float) -> bool:
    return np.isfinite(r_4) and r_4 > 1.0


def _apply_dg4_perturbation(
    base_model_spec: dict[str, Any],
    base_quadrature_kwargs: dict[str, Any],
    perturbation: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply a v0.1.4 reproducibility perturbation to the model spec / quad kwargs."""
    if perturbation["kind"] == "model_spec":
        spec = deepcopy(base_model_spec)
        spec.setdefault("bath_spectral_density", {})[perturbation["key"]] = perturbation["value"]
        return spec, dict(base_quadrature_kwargs)
    if perturbation["kind"] == "quadrature":
        kwargs = dict(base_quadrature_kwargs)
        kwargs[perturbation["key"]] = perturbation["value"]
        return deepcopy(base_model_spec), kwargs
    raise ValueError(f"_apply_dg4_perturbation: unknown perturbation kind {perturbation['kind']!r}")


def _interpolate_alpha_crit(per_alpha: list[dict[str, Any]]) -> float | None:
    """Linear interpolation of alpha_crit in log(alpha**2) between last passing
    and first convergence-failure alpha. Returns None if no boundary exists."""
    last_pass_idx: int | None = None
    first_failure_idx: int | None = None
    for i, entry in enumerate(per_alpha):
        if entry["classification"] == "passing":
            last_pass_idx = i
        elif entry["classification"] == "convergence_failure" and last_pass_idx is not None:
            first_failure_idx = i
            break
    if last_pass_idx is None or first_failure_idx is None:
        return None
    a_pass = per_alpha[last_pass_idx]["alpha_sq"]
    a_fail = per_alpha[first_failure_idx]["alpha_sq"]
    r_pass = per_alpha[last_pass_idx]["r_4_baseline"]
    r_fail = per_alpha[first_failure_idx]["r_4_baseline"]
    log_a_pass = np.log(a_pass)
    log_a_fail = np.log(a_fail)
    # Solve r(log_a) = 1 by linear interpolation.
    if r_fail == r_pass:
        return float(np.exp(0.5 * (log_a_pass + log_a_fail)))
    frac = (1.0 - r_pass) / (r_fail - r_pass)
    return float(np.exp(log_a_pass + frac * (log_a_fail - log_a_pass)))


def _format_dg4_sweep_notes(
    *,
    card: BenchmarkCard,
    per_alpha: list[dict[str, Any]],
    alpha_crit: float | None,
    baseline_coeffs: Any,
    perturbed_coeffs: Mapping[str, Any],
    path_b_params: dict[str, Any],
) -> str:
    """Format result.notes string for a DG-4 sweep run."""
    lines = [
        f"DG-4 sweep runner: card {card.card_id} {card.version}.",
        "L_4 source: Path B numerical Richardson extraction.",
        f"Path B params: alpha_values={path_b_params['alpha_values']}, "
        f"n_bath_modes={path_b_params['n_bath_modes']}, "
        f"n_levels_per_mode={path_b_params['n_levels_per_mode']}.",
        f"Baseline fit relative residual: {baseline_coeffs.fit_relative_residual:.3e}.",
        f"Baseline ||L_2^dis||_avg = {baseline_coeffs.l2_avg:.3e}, "
        f"||L_4^dis||_avg = {baseline_coeffs.l4_avg:.3e}, "
        f"coefficient ratio = {baseline_coeffs.l4_avg/max(baseline_coeffs.l2_avg, 1e-300):.3e}.",
    ]
    if alpha_crit is not None:
        lines.append(f"alpha_crit (interpolated, log-linear): {alpha_crit:.4e}.")
    classifications = {
        c: 0
        for c in (
            "passing",
            "convergence_failure",
            "truncation_artefact",
            "metric-undefined",
        )
    }
    for entry in per_alpha:
        classifications[entry["classification"]] = (
            classifications.get(entry["classification"], 0) + 1
        )
    lines.append(
        "Per-alpha classifications: "
        + ", ".join(f"{c}={n}" for c, n in classifications.items() if n > 0)
        + "."
    )
    lines.append(
        "Path B carries a finite-env extraction floor (sigma_z thermal "
        "zero-oracle ~few * 1e-2 at the default truncation per the "
        "2026-05-06 pilot); verdicts are subject to this documented "
        "uncertainty until the analytic Path A (Companion Sec. IV) lands."
    )
    return "\n".join(lines)


def _run_algebraic_map(card: BenchmarkCard) -> CardResult:
    """Run an algebraic_map card by iterating over test_cases.

    For each test_case, dispatches to the registered handler to obtain
    (L, K_expected), computes K via cbg.effective_hamiltonian.K_from_generator
    using a freshly-constructed matrix-unit basis, and compares the result
    by relative Frobenius norm against the card's threshold.
    """
    if card.basis_name != "matrix_unit":
        raise NotImplementedError(
            f"basis {card.basis_name!r}: only 'matrix_unit' is supported at "
            f"DG-1; cross-basis verification is the DG-2 universal-default "
            f"structural-identity check per Sail v0.5 §9 DG-2"
        )

    d = card.system_dimension
    basis = matrix_unit_basis(d)
    if not verify_orthonormality(basis):
        raise RuntimeError(
            f"matrix_unit_basis(d={d}) failed orthonormality precondition; "
            f"this should never happen — runner aborting"
        )

    threshold = card.threshold
    abs_tol = float(card.frozen_parameters["numerical"]["integration_tolerance"]["absolute"])
    test_cases = card.frozen_parameters["model"]["test_cases"]
    test_case_results: list[TestCaseResult] = []

    for case in test_cases:
        name = case["name"]
        if name not in _TEST_CASE_HANDLERS:
            raise TestCaseHandlerNotFoundError(
                f"No runner handler registered for test_case {name!r}. "
                f"Known handlers: {sorted(_TEST_CASE_HANDLERS.keys())}. "
                f"To support a new test_case name, register a handler in "
                f"reporting.benchmark_card._TEST_CASE_HANDLERS."
            )
        handler = _TEST_CASE_HANDLERS[name]
        L, K_expected, hpta_residual, hermiticity_residual = handler(case, d)

        # Hermiticity-of-omega precondition gate — applies only to handlers
        # that surface a non-None residual (off-diagonal pseudo-Kraus B2
        # cases). Checked first because Hermiticity is the structural
        # precondition for HPTA itself: a non-Hermitian omega makes the
        # HPTA residual ill-typed (it can be non-zero anti-Hermitian) and
        # the K comparison downstream meaningless. Short-circuit with a
        # clear diagnostic.
        if hermiticity_residual is not None and hermiticity_residual > abs_tol:
            test_case_results.append(
                TestCaseResult(
                    name=name,
                    passed=False,
                    error=hermiticity_residual,
                    threshold=abs_tol,
                    notes=(
                        f"Hermiticity precondition failed: "
                        f"||omega - omega^dagger||_F = {hermiticity_residual:.3e} "
                        f"> absolute tolerance {abs_tol:.3e}. "
                        f"HPTA and K comparison skipped."
                    ),
                    hpta_residual=hpta_residual,
                    hpta_threshold=abs_tol if hpta_residual is not None else None,
                    hermiticity_residual=hermiticity_residual,
                    hermiticity_threshold=abs_tol,
                )
            )
            continue

        # HPTA precondition gate — applies only to handlers that surface a
        # non-None residual (pseudo-Kraus B1 / B2 cases). The threshold is
        # numerical.integration_tolerance.absolute, the same bound the card
        # cites in acceptance_criterion.rationale. A failure here means the
        # fixture is not a valid pseudo-Kraus generator and the K comparison
        # downstream would be meaningless; short-circuit with a clear
        # diagnostic instead.
        if hpta_residual is not None and hpta_residual > abs_tol:
            test_case_results.append(
                TestCaseResult(
                    name=name,
                    passed=False,
                    error=hpta_residual,
                    threshold=abs_tol,
                    notes=(
                        f"HPTA precondition failed: "
                        f"||sum_j gamma_j E_j^dagger E_j||_F = {hpta_residual:.3e} "
                        f"> absolute tolerance {abs_tol:.3e}. K comparison skipped."
                    ),
                    hpta_residual=hpta_residual,
                    hpta_threshold=abs_tol,
                    hermiticity_residual=hermiticity_residual,
                    hermiticity_threshold=abs_tol if hermiticity_residual is not None else None,
                )
            )
            continue

        K_computed = K_from_generator(L, basis)

        comparison_basis_name = case.get("comparison_basis")
        if comparison_basis_name is not None:
            # Cross-basis structural-identity branch (B3 v0.1.0): compare K
            # under the matrix-unit reference against K under the named
            # alternate basis. The handler must have surfaced K_expected = None
            # to land here (the basis-independence factory enforces that).
            if K_expected is not None:
                raise RuntimeError(
                    f"_run_algebraic_map: test_case {name!r} has comparison_basis "
                    f"{comparison_basis_name!r} but its handler returned a non-None "
                    f"K_expected; cross-basis cases must surface K_expected = None"
                )
            alt_builder = _BASIS_BUILDERS.get(comparison_basis_name)
            if alt_builder is None:
                raise SchemaValidationError(
                    f"_run_algebraic_map: test_case {name!r} requests "
                    f"comparison_basis {comparison_basis_name!r}; no builder "
                    f"registered. Known: {sorted(_BASIS_BUILDERS.keys())}"
                )
            alt_basis = alt_builder(d)
            if not verify_orthonormality(alt_basis):
                raise RuntimeError(
                    f"comparison_basis {comparison_basis_name!r} (d={d}) failed "
                    f"orthonormality precondition; cross-basis comparison is "
                    f"meaningless against a non-orthonormal basis"
                )
            K_alt = K_from_generator(L, alt_basis)
            diff_norm = float(np.linalg.norm(K_computed - K_alt, ord="fro"))
            ref_norm = float(np.linalg.norm(K_computed, ord="fro"))
            error = diff_norm / max(ref_norm, 1.0)
        else:
            # K-value branch (A1, B1): compare K_computed against K_expected.
            assert K_expected is not None
            diff_norm = float(np.linalg.norm(K_computed - K_expected, ord="fro"))
            ref_norm = float(np.linalg.norm(K_expected, ord="fro"))
            if ref_norm > 0.0:
                error = diff_norm / ref_norm
            else:
                # If K_expected is zero, fall back to absolute Frobenius norm
                error = diff_norm

        test_case_results.append(
            TestCaseResult(
                name=name,
                passed=error <= threshold,
                error=error,
                threshold=threshold,
                hpta_residual=hpta_residual,
                hpta_threshold=abs_tol if hpta_residual is not None else None,
                hermiticity_residual=hermiticity_residual,
                hermiticity_threshold=abs_tol if hermiticity_residual is not None else None,
            )
        )

    all_passed = all(r.passed for r in test_case_results)
    verdict = "PASS" if all_passed else "FAIL"
    return CardResult(
        card_id=card.card_id,
        verdict=verdict,
        test_case_results=test_case_results,
        runner_version=__version__,
    )


# ─── Dynamical-card runner (Cards A3, A4 thermal-only at DG-1) ──────────────

# Model-factory registry: card.model -> (model_spec dict) -> (H_S, A) ndarrays.
_MODEL_FACTORIES: dict[str, Callable[[dict[str, Any]], tuple[np.ndarray, np.ndarray]]] = {
    "pure_dephasing": pure_dephasing.system_arrays_from_spec,
    "spin_boson_sigma_x": spin_boson_sigma_x.system_arrays_from_spec,
}


def _dyn_handler_pure_dephasing_thermal(
    K_array: np.ndarray,
    t_grid: np.ndarray,
    threshold: float,
    H_S: np.ndarray,
    bath_state: dict[str, Any] | None = None,
    spectral_density: dict[str, Any] | None = None,
) -> tuple[bool, float]:
    """Card A3 v0.1.1 thermal_bath PASS condition.

    Verifies Entry 3.B.1 (K(t) ∝ sigma_z; max_t shape_residual <= threshold)
    AND Entry 3.B.2 (no renormalisation: max_t |omega_r(t) - omega| <= threshold).

    omega is extracted from H_S = (omega/2) sigma_z by reading the [0,0]
    entry — this assumes the canonical pure-dephasing H_S form, which is
    enforced by models.pure_dephasing.system_arrays_from_spec validation.

    Returns (passed, error) where error = max(max_shape_residual, max_shift).
    """
    omega = float(2.0 * H_S[0, 0].real)
    max_shape_residual = 0.0
    max_shift = 0.0
    for K_t in K_array:
        # Project onto sigma_z: 0.5 * trace(sigma_z K) sigma_z
        coeff = 0.5 * np.trace(_SIGMA_Z @ K_t).real
        proj = coeff * _SIGMA_Z
        diff_norm = float(np.linalg.norm(K_t - proj, ord="fro"))
        K_norm = float(np.linalg.norm(K_t, ord="fro"))
        shape_residual = diff_norm / K_norm if K_norm > 0 else 0.0
        max_shape_residual = max(max_shape_residual, shape_residual)
        # omega_r(t) = trace(sigma_z K(t)); shift = omega_r - omega
        omega_r = float(np.trace(_SIGMA_Z @ K_t).real)
        max_shift = max(max_shift, abs(omega_r - omega))
    error = max(max_shape_residual, max_shift)
    return error <= threshold, error


def _dyn_handler_sigma_x_thermal(
    K_array: np.ndarray,
    t_grid: np.ndarray,
    threshold: float,
    H_S: np.ndarray,
    bath_state: dict[str, Any] | None = None,
    spectral_density: dict[str, Any] | None = None,
) -> tuple[bool, float]:
    """Card A4 v0.1.1 thermal_bath PASS condition.

    Verifies Entry 4.B.1 (no eigenbasis rotation; max_t transverse_norm
    <= threshold). The transverse_norm is the magnitude of the sigma_x +
    sigma_y components of K(t); zero (within tolerance) means K is
    proportional to sigma_z, i.e. eigenbasis aligned with H_S's eigenbasis.

    Energy-level shift is explicitly NOT gated (Entry 4.B.1 allows it);
    only the rotation is constrained.

    Returns (passed, max_transverse_norm).
    """
    max_transverse = 0.0
    for K_t in K_array:
        b = 0.5 * np.trace(_SIGMA_X @ K_t)
        c = 0.5 * np.trace(_SIGMA_Y @ K_t)
        transverse = float(np.sqrt(abs(b) ** 2 + abs(c) ** 2))
        max_transverse = max(max_transverse, transverse)
    return max_transverse <= threshold, max_transverse


# ─── Coherent-displaced dynamical handlers (Council Act 2 cleared, 2026-05-04) ─
#
# B4-conv-registry v0.1.0 verifies CL-2026-005 v0.4 Entry 3.B.3 under the
# four cleared displacement profiles. Per the parity-class theorem of Letter
# end-matter Eq. (A.39) (transcription §2.2): under σ_z coupling, K(t) is
# proportional to σ_z under any bath state. The non-thermal signature is
# the time-dependent shift ω_r(t) − ω, which under the perturbative
# expansion at N_card = 2 is exactly K_1(t)'s σ_z coefficient times 2 —
# i.e. 2 D̄_1(t) — because K_2 contributes only the identity term that is
# stripped by the K_from_generator traceless projection.
#
# Verdict gate: max_t |shift_actual(t) − shift_predicted(t)| ≤ threshold
# AND max_t shape_residual(t) ≤ threshold (K(t) ∝ σ_z preserved).


def _dyn_handler_pure_dephasing_displaced(
    K_array: np.ndarray,
    t_grid: np.ndarray,
    threshold: float,
    H_S: np.ndarray,
    bath_state: dict[str, Any] | None = None,
    spectral_density: dict[str, Any] | None = None,
) -> tuple[bool, float]:
    """Card B4-conv-registry v0.1.0 displaced-pure-dephasing PASS condition.

    Per fixture (one of four cleared profiles), gates BOTH:
      (1) shape: K(t) ∝ σ_z (parity-class theorem holds for σ_z coupling
          under any bath state). max_t shape_residual ≤ threshold.
      (2) shift: max_t |omega_r(t) - omega - shift_predicted(t)| ≤ threshold,
          where shift_predicted(t) = 2 · D̄_1(t).real for the registered
          profile.

    Returns (passed, max(shape_residual, shift_error)).
    """
    if bath_state is None or spectral_density is None:
        raise ValueError(
            "_dyn_handler_pure_dephasing_displaced: bath_state + " "spectral_density are required"
        )

    omega = float(2.0 * H_S[0, 0].real)
    shift_predicted = 2.0 * np.real(
        _cumulants_D_bar_1(
            np.asarray(t_grid, dtype=float),
            bath_state=bath_state,
            spectral_density=spectral_density,
        )
    )
    max_shape_residual = 0.0
    max_shift_err = 0.0
    for i, K_t in enumerate(K_array):
        # B.1: K(t) ∝ σ_z (shape residual)
        coeff = 0.5 * np.trace(_SIGMA_Z @ K_t).real
        proj = coeff * _SIGMA_Z
        diff_norm = float(np.linalg.norm(K_t - proj, ord="fro"))
        K_norm = float(np.linalg.norm(K_t, ord="fro"))
        shape_residual = diff_norm / K_norm if K_norm > 0 else 0.0
        max_shape_residual = max(max_shape_residual, shape_residual)
        # B.3: actual shift versus predicted shift
        omega_r = float(np.trace(_SIGMA_Z @ K_t).real)
        shift_actual = omega_r - omega
        max_shift_err = max(max_shift_err, abs(shift_actual - shift_predicted[i]))
    error = max(max_shape_residual, max_shift_err)
    return error <= threshold, error


# ─── B5-conv-registry v0.2.0 σ_x displaced handler ────────────────────────────
#
# Schrödinger-picture L_1^S[X](t) = -i D̄_1(t) [σ_x, X] extracts via Letter
# Eq. (6) to K_1(t) = D̄_1(t) · σ_x — a constant-direction transverse
# contribution along σ_x with zero σ_y component at order ≤ N_card = 2
# (parity-class theorem of Letter end-matter Eq. (A.43)-(A.45) sends K_2
# to the diagonal subspace; σ_y component is exactly zero in the displaced
# case at this order). Predicted: (b_pred, c_pred) = (D̄_1(t), 0).


def _dyn_handler_sigma_x_displaced(
    K_array: np.ndarray,
    t_grid: np.ndarray,
    threshold: float,
    H_S: np.ndarray,
    bath_state: dict[str, Any] | None = None,
    spectral_density: dict[str, Any] | None = None,
) -> tuple[bool, float]:
    """Card B5-conv-registry v0.2.0 displaced-σ_x PASS condition.

    Per fixture (one of four cleared profiles), gates the Schrödinger-
    picture predicted transverse vector (D̄_1(t), 0):
      b_actual(t) := 0.5 trace(σ_x · K(t))   should equal D̄_1(t)
      c_actual(t) := 0.5 trace(σ_y · K(t))   should equal 0
      transverse_error(t) := sqrt((b_actual - D̄_1)² + c_actual²)
    Verdict: max_t transverse_error(t) ≤ threshold.

    The σ_z coefficient d(t) is NOT gated — Entry 4.B.2 explicitly allows
    an energy-level shift; only the transverse channels are constrained.

    The same D̄_1 array is consumed by both the runner's K_1 computation
    (via cbg.tcl_recursion.K_total_displaced_on_grid → L_1_displaced_at_time)
    and the predicted σ_x channel here, so quadrature error in the
    broadband / Gaussian profiles cancels at the verdict-comparison
    layer (parallels B4's structural-precision pattern).

    Returns (passed, max_transverse_error).
    """
    if bath_state is None or spectral_density is None:
        raise ValueError(
            "_dyn_handler_sigma_x_displaced: bath_state + spectral_density " "are required"
        )

    b_predicted = np.real(
        _cumulants_D_bar_1(
            np.asarray(t_grid, dtype=float),
            bath_state=bath_state,
            spectral_density=spectral_density,
        )
    )
    max_transverse_err = 0.0
    for i, K_t in enumerate(K_array):
        b_actual = 0.5 * np.trace(_SIGMA_X @ K_t).real
        c_actual = 0.5 * np.trace(_SIGMA_Y @ K_t).real
        transverse_err = float(np.sqrt((b_actual - b_predicted[i]) ** 2 + c_actual**2))
        max_transverse_err = max(max_transverse_err, transverse_err)
    return max_transverse_err <= threshold, max_transverse_err


# Dynamical test-case handler registry: keyed by (card.model, test_case_name).
# The model qualifier in the key is what distinguishes A3.thermal_bath from
# A4.thermal_bath (both have the same test_case name but different physics).
# DG-2 (post-Council-Act-2) extends the registry with the four B4-conv-registry
# fixtures under pure_dephasing AND the four B5-conv-registry v0.2.0 fixtures
# under spin_boson_sigma_x — one per cleared displacement profile in each.
_DYNAMICAL_TEST_CASE_HANDLERS: dict[
    tuple[str, str],
    Callable[..., tuple[bool, float]],
] = {
    ("pure_dephasing", "thermal_bath"): _dyn_handler_pure_dephasing_thermal,
    ("spin_boson_sigma_x", "thermal_bath"): _dyn_handler_sigma_x_thermal,
    ("pure_dephasing", "displaced_bath_delta_omega_c"): _dyn_handler_pure_dephasing_displaced,
    ("pure_dephasing", "displaced_bath_delta_omega_S"): _dyn_handler_pure_dephasing_displaced,
    ("pure_dephasing", "displaced_bath_sqrt_J"): _dyn_handler_pure_dephasing_displaced,
    ("pure_dephasing", "displaced_bath_gaussian"): _dyn_handler_pure_dephasing_displaced,
    ("spin_boson_sigma_x", "displaced_bath_delta_omega_c"): _dyn_handler_sigma_x_displaced,
    ("spin_boson_sigma_x", "displaced_bath_delta_omega_S"): _dyn_handler_sigma_x_displaced,
    ("spin_boson_sigma_x", "displaced_bath_sqrt_J"): _dyn_handler_sigma_x_displaced,
    ("spin_boson_sigma_x", "displaced_bath_gaussian"): _dyn_handler_sigma_x_displaced,
}


# ─── DG-3 cross-method runner (Cards C1, C2) ────────────────────────────────

CrossMethodHandler = Callable[
    [dict[str, Any], np.ndarray, dict[str, Any], dict[str, Any]],
    tuple[np.ndarray, np.ndarray, str],
]


def _cross_method_model_spec(
    card_model_spec: dict[str, Any],
    case: dict[str, Any],
) -> dict[str, Any]:
    """Merge model-level card fields with a per-case bath_state.

    C1/C2 keep ``bath_state`` under each test_case so thermal and displaced
    fixtures can coexist. The reference modules expect a single model_spec
    mapping with ``bath_state`` at top level, matching the Phase B module
    tests.
    """
    model_spec = {k: v for k, v in card_model_spec.items() if k != "test_cases"}
    model_spec["bath_state"] = case["bath_state"]
    return model_spec


def _inter_method_relative_frobenius(
    rho_a: np.ndarray,
    rho_b: np.ndarray,
) -> float:
    """Card C1/C2 inter-method relative Frobenius error.

    error = max_t ||rho_a(t) - rho_b(t)||_F
            / max(||rho_a(t)||_F, ||rho_b(t)||_F, eps)
    """
    rho_a = np.asarray(rho_a, dtype=complex)
    rho_b = np.asarray(rho_b, dtype=complex)
    if rho_a.shape != rho_b.shape:
        raise ValueError(
            "_inter_method_relative_frobenius: trajectory shape mismatch; "
            f"got {rho_a.shape} and {rho_b.shape}"
        )
    if rho_a.ndim != 3 or rho_a.shape[1] != rho_a.shape[2]:
        raise ValueError(
            "_inter_method_relative_frobenius: expected shape "
            f"(n_times, d, d); got {rho_a.shape}"
        )
    diff = rho_a - rho_b
    n_times = rho_a.shape[0]
    diff_norm = np.linalg.norm(diff.reshape(n_times, -1), axis=1)
    norm_a = np.linalg.norm(rho_a.reshape(n_times, -1), axis=1)
    norm_b = np.linalg.norm(rho_b.reshape(n_times, -1), axis=1)
    denom = np.maximum(np.maximum(norm_a, norm_b), np.finfo(float).eps)
    return float(np.max(diff_norm / denom))


def _validate_density_trajectory(
    *,
    method_name: str,
    case_name: str,
    rho_t: np.ndarray,
    n_times: int,
    system_dimension: int,
) -> None:
    """Validate the common reduced-density-matrix trajectory contract."""
    expected_shape = (n_times, system_dimension, system_dimension)
    if rho_t.shape != expected_shape:
        raise ValueError(
            f"{method_name} returned shape {rho_t.shape} for {case_name!r}; "
            f"expected {expected_shape}"
        )
    if not np.all(np.isfinite(rho_t)):
        raise ValueError(f"{method_name} returned non-finite values for {case_name!r}")


def _cross_handler_pure_dephasing_thermal(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    _numerical: dict[str, Any],
    _truncation: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, str]:
    """C1 thermal-bath cross-method handler.

    Runs the Phase B finite-system reference against the Phase B QuTiP
    Markov reference on the same merged model specification. The exact
    helper defaults intentionally encode the Phase B scope: 4 log-spaced
    bosonic modes with 4 Fock levels per mode (joint dimension 512).
    """
    H_total, rho_initial, system_dim, bath_dim = (
        exact_finite_env.build_pure_dephasing_thermal_total(model_spec)
    )
    rho_exact = exact_finite_env.propagate(
        H_total,
        rho_initial,
        t_grid,
        system_dim=system_dim,
        bath_dim=bath_dim,
    )
    rho_qutip = qutip_reference.reference_propagate(model_spec, t_grid)
    notes = (
        "exact_finite_env finite-system reference "
        f"(system_dim={system_dim}, bath_dim={bath_dim}); "
        "qutip_reference solver-default Markov reference."
    )
    return rho_exact, rho_qutip, notes


def _deferred_cross_method_handler(reason: str) -> CrossMethodHandler:
    """Return a handler that fail-closes with the Phase B deferred-scope route."""

    def handler(
        _model_spec: dict[str, Any],
        _t_grid: np.ndarray,
        _numerical: dict[str, Any],
        _truncation: dict[str, Any],
    ) -> tuple[np.ndarray, np.ndarray, str]:
        raise NotImplementedError(
            f"_run_cross_method: {reason}. Next deferred handler: implement "
            "matching support in benchmarks.exact_finite_env and "
            "benchmarks.qutip_reference, then register it in "
            "reporting.benchmark_card._CROSS_METHOD_TEST_CASE_HANDLERS."
        )

    return handler


def _cross_handler_spin_boson_sigma_x_thermal(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    _numerical: dict[str, Any],
    _truncation: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, str]:
    """C2 thermal-bath cross-method handler.

    Builds the σ_x finite-system reference (full unitary on the joint
    system+bath Hilbert space, no rotating-wave approximation) against
    the QuTiP secular Lindblad reference (σ_-/σ_+ collapse operators
    with rates S(±ω_S) sourced from cbg.bath_correlations). Belongs to
    the same finite-system × solver-default failure-mode pairing as
    the C1 handlers; the qualitative differences from the σ_z case
    are (i) energy relaxation toward Boltzmann equilibrium and (ii)
    the relevant bath spectral frequencies are ±ω_S rather than 0.
    """
    H_total, rho_initial, system_dim, bath_dim = (
        exact_finite_env.build_spin_boson_sigma_x_thermal_total(model_spec)
    )
    rho_exact = exact_finite_env.propagate(
        H_total,
        rho_initial,
        t_grid,
        system_dim=system_dim,
        bath_dim=bath_dim,
    )
    rho_qutip = qutip_reference.reference_propagate(model_spec, t_grid)
    notes = (
        "exact_finite_env finite-system reference for σ_x coupling "
        f"(system_dim={system_dim}, bath_dim={bath_dim}); "
        "qutip_reference solver-default secular Lindblad with σ_-/σ_+ "
        "collapse operators at S(±ω_S)."
    )
    return rho_exact, rho_qutip, notes


def _cross_handler_spin_boson_sigma_x_displaced_delta_omega_c(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    _numerical: dict[str, Any],
    _truncation: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, str]:
    """C2 displaced delta-omega_c cross-method handler.

    Combines the σ_x finite-system reference under coherent-displaced bath
    (mode at ω_c displaced; same α_disp calibration as the σ_z displaced
    builder) with the QuTiP secular Lindblad reference for σ_x — same
    σ_-/σ_+ rates as the C2 thermal handler (connected stats invariant
    under displacement) plus a time-dependent σ_x drive ⟨B(t)⟩ σ_x.
    """
    H_total, rho_initial, system_dim, bath_dim = (
        exact_finite_env.build_spin_boson_sigma_x_displaced_total(model_spec)
    )
    rho_exact = exact_finite_env.propagate(
        H_total,
        rho_initial,
        t_grid,
        system_dim=system_dim,
        bath_dim=bath_dim,
    )
    rho_qutip = qutip_reference.reference_propagate(model_spec, t_grid)
    notes = (
        "exact_finite_env finite-system σ_x reference with coherent "
        f"displacement (system_dim={system_dim}, bath_dim={bath_dim}, "
        "profile=delta-omega_c); qutip_reference σ_-/σ_+ secular "
        "Lindblad with time-dependent σ_x drive."
    )
    return rho_exact, rho_qutip, notes


def _cross_handler_pure_dephasing_displaced_delta_omega_c(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    _numerical: dict[str, Any],
    _truncation: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, str]:
    """C1 displaced delta-omega_c cross-method handler.

    Builds the coherent-displaced finite-system reference (mode at ω_c
    coherently displaced by α_disp = α_0 / √Δω_c per the discrete-finite-
    bath analogue of the cbg.cumulants delta-omega_c convention) against
    the QuTiP Markov reference with a time-dependent Lamb-shift
    Hamiltonian H_eff(t) = (ω/2 + ⟨B(t)⟩) σ_z.
    """
    H_total, rho_initial, system_dim, bath_dim = (
        exact_finite_env.build_pure_dephasing_displaced_total(model_spec)
    )
    rho_exact = exact_finite_env.propagate(
        H_total,
        rho_initial,
        t_grid,
        system_dim=system_dim,
        bath_dim=bath_dim,
    )
    rho_qutip = qutip_reference.reference_propagate(model_spec, t_grid)
    notes = (
        "exact_finite_env finite-system reference with coherent displacement "
        f"(system_dim={system_dim}, bath_dim={bath_dim}, profile=delta-omega_c); "
        "qutip_reference Markov reference with time-dependent Lamb shift."
    )
    return rho_exact, rho_qutip, notes


_CROSS_METHOD_TEST_CASE_HANDLERS: dict[tuple[str, str], CrossMethodHandler] = {
    ("pure_dephasing", "thermal_bath_cross_method"): _cross_handler_pure_dephasing_thermal,
    (
        "pure_dephasing",
        "displaced_bath_delta_omega_c_cross_method",
    ): _cross_handler_pure_dephasing_displaced_delta_omega_c,
    (
        "spin_boson_sigma_x",
        "thermal_bath_cross_method",
    ): _cross_handler_spin_boson_sigma_x_thermal,
    (
        "spin_boson_sigma_x",
        "displaced_bath_delta_omega_c_cross_method",
    ): _cross_handler_spin_boson_sigma_x_displaced_delta_omega_c,
}


def _run_cross_method(card: BenchmarkCard) -> CardResult:
    """Run a DG-3 cross-method card by comparing two reference trajectories."""
    if card.model_kind != "dynamical":
        raise NotImplementedError(
            f"_run_cross_method: DG-3 runner currently supports only "
            f"model_kind='dynamical'; got {card.model_kind!r}"
        )

    comparison = card.frozen_parameters["comparison"]
    metric = comparison.get("error_metric")
    if metric != "inter_method_relative_frobenius":
        raise NotImplementedError(
            f"_run_cross_method: error_metric {metric!r} not supported. "
            "Known: 'inter_method_relative_frobenius'."
        )

    fp = card.frozen_parameters
    grid = build_time_grid(fp["numerical"]["time_grid"])
    threshold = card.threshold
    system_dimension = card.system_dimension
    test_case_results: list[TestCaseResult] = []

    for case in fp["model"]["test_cases"]:
        name = case["name"]
        handler_key = (card.model, name)
        handler = _CROSS_METHOD_TEST_CASE_HANDLERS.get(handler_key)
        if handler is None:
            raise TestCaseHandlerNotFoundError(
                f"_run_cross_method: no handler registered for "
                f"(model={card.model!r}, test_case={name!r}). "
                f"Known: {sorted(_CROSS_METHOD_TEST_CASE_HANDLERS.keys())}"
            )

        model_spec = _cross_method_model_spec(fp["model"], case)
        rho_exact, rho_qutip, notes = handler(
            model_spec,
            grid.times,
            fp["numerical"],
            fp["truncation"],
        )
        _validate_density_trajectory(
            method_name="exact_finite_env",
            case_name=name,
            rho_t=rho_exact,
            n_times=grid.times.size,
            system_dimension=system_dimension,
        )
        _validate_density_trajectory(
            method_name="qutip_reference",
            case_name=name,
            rho_t=rho_qutip,
            n_times=grid.times.size,
            system_dimension=system_dimension,
        )
        error = _inter_method_relative_frobenius(rho_exact, rho_qutip)
        test_case_results.append(
            TestCaseResult(
                name=name,
                passed=error <= threshold,
                error=error,
                threshold=threshold,
                notes=notes,
            )
        )

    all_passed = all(r.passed for r in test_case_results)
    verdict = "PASS" if all_passed else "FAIL"
    return CardResult(
        card_id=card.card_id,
        verdict=verdict,
        test_case_results=test_case_results,
        runner_version=__version__,
        notes=(
            "DG-3 cross-method branch: exact_finite_env (finite-system) "
            "vs qutip_reference (solver-default)."
        ),
    )


def _run_dynamical(card: BenchmarkCard) -> CardResult:
    """Run a dynamical card.

    Pipeline:
        1. Build (H_S, A) from card.model via _MODEL_FACTORIES dispatch.
        2. Build the time grid from frozen_parameters.numerical.time_grid.
        3. For each test_case:
              a. Dispatch on the registered (model, test_case_name) handler.
              b. Compute K_total = K_0 + K_1 + ... + K_{N_card} on the grid
                 through the thermal or Council-cleared coherent-displaced
                 low-order entry point.
              c. Apply the per-(model, test_case_name) handler to derive
                 the verdict.
    """
    fp = card.frozen_parameters

    # 1. Model arrays
    model_factory = _MODEL_FACTORIES.get(card.model)
    if model_factory is None:
        raise NotImplementedError(
            f"_run_dynamical: no model factory registered for "
            f"card.model {card.model!r}. Known models: "
            f"{sorted(_MODEL_FACTORIES.keys())}"
        )
    H_S, A = model_factory(fp["model"])

    # 2. Time grid
    grid = build_time_grid(fp["numerical"]["time_grid"])

    # 3. Iterate test_cases
    sd = fp["model"]["bath_spectral_density"]
    N_card = fp["truncation"]["perturbative_order"]
    threshold = card.threshold
    quadrature_kwargs = _quadrature_kwargs(fp)

    test_case_results: list[TestCaseResult] = []
    for case in fp["model"]["test_cases"]:
        bs = case["bath_state"]
        bs_family = bs.get("family")
        if bs_family == "thermal":
            K_array = K_total_thermal_on_grid(
                N_card,
                grid.times,
                H_S,
                A,
                bath_state=bs,
                spectral_density=sd,
                **quadrature_kwargs,
            )
        elif bs_family == "coherent_displaced":
            # Council Act 2 (2026-05-04) lifted the standing carve-out under
            # handling (c) (convention-agnostic registry encoding); the
            # displaced K_total dispatches on the per-fixture
            # ``displacement_profile`` registry key.
            K_array = K_total_displaced_on_grid(
                N_card,
                grid.times,
                H_S,
                A,
                bath_state=bs,
                spectral_density=sd,
                **quadrature_kwargs,
            )
        else:
            raise NotImplementedError(
                f"_run_dynamical: bath_state.family {bs_family!r} not "
                f"supported. Known: 'thermal' (DG-1); 'coherent_displaced' "
                f"(Council Act 2 cleared 2026-05-04 under handling (c) — "
                f"see ledger/CL-2026-005_v0.4_council-deliberation_act2_"
                f"2026-05-04.md)."
            )

        handler_key = (card.model, case["name"])
        handler = _DYNAMICAL_TEST_CASE_HANDLERS.get(handler_key)
        if handler is None:
            raise TestCaseHandlerNotFoundError(
                f"_run_dynamical: no handler registered for "
                f"(model={card.model!r}, test_case={case['name']!r}). "
                f"Known: {sorted(_DYNAMICAL_TEST_CASE_HANDLERS.keys())}"
            )
        passed, error = handler(
            K_array,
            grid.times,
            threshold,
            H_S,
            bath_state=bs,
            spectral_density=sd,
        )
        test_case_results.append(
            TestCaseResult(
                name=case["name"],
                passed=passed,
                error=error,
                threshold=threshold,
            )
        )

    all_passed = all(r.passed for r in test_case_results)
    verdict = "PASS" if all_passed else "FAIL"
    return CardResult(
        card_id=card.card_id,
        verdict=verdict,
        test_case_results=test_case_results,
        runner_version=__version__,
    )


def _quadrature_kwargs(frozen_parameters: Mapping[str, Any]) -> dict[str, Any]:
    """Extract optional quadrature controls from frozen_parameters.numerical.

    DG-4 Phase B.4 accepts an ad-hoc ``numerical.quadrature`` extras block
    until SCHEMA.md formalises it. Unknown keys are ignored here so future
    numerical controls do not accidentally leak into cbg.tcl_recursion.
    """
    numerical = frozen_parameters.get("numerical") or {}
    quadrature = numerical.get("quadrature") or {}
    out: dict[str, Any] = {}
    if "upper_cutoff_factor" in quadrature:
        out["upper_cutoff_factor"] = quadrature["upper_cutoff_factor"]
    if "quad_limit" in quadrature:
        out["quad_limit"] = quadrature["quad_limit"]
    return out


# ─── DG-4 audit-complete result-JSON writer ─────────────────────────────────


def write_dg4_result_json(
    card: BenchmarkCard,
    run_result: CardResult,
    output_path: Path | str,
    *,
    run_window_utc: Mapping[str, str] | None = None,
    computed_at_utc: str | None = None,
    indent: int = 2,
) -> Path:
    """Write an audit-complete DG-4 result JSON artefact.

    Persists the full sweep table from ``run_result.dg4_sweep_data`` plus
    card-level metadata, so a reader can reconstruct the verdict from the
    artefact alone (DG-4 work plan v0.1.4 audit requirement, addressing
    the v0.1.1 supersedure's MEDIUM finding).

    Returns the path the JSON was written to.
    """
    import json

    if run_result.dg4_sweep_data is None:
        raise ValueError(
            "write_dg4_result_json: run_result has no dg4_sweep_data; "
            "this writer is for DG-4 sweep verdicts only."
        )
    sweep = run_result.dg4_sweep_data
    output_path = Path(output_path)

    payload: dict[str, Any] = {
        "card_id": card.card_id,
        "card_version": card.version,
        "card_path": (str(card.source_path) if getattr(card, "source_path", None) else None),
        "schema_version": card.schema_version,
        "ledger_entry": card.ledger_entry,
        "verdict": run_result.verdict,
        "runner_version": run_result.runner_version,
        "l4_source": "Path B numerical Richardson extraction (interaction-picture transformed)",
        "path_b_params": sweep["path_b_params"],
        "baseline": sweep["baseline"],
        "max_baseline_r4": sweep["max_baseline_r4"],
        "threshold": card.threshold,
        "frozen_sweep": _summarise_frozen_sweep(card),
        "alpha_crit": sweep["alpha_crit"],
        "classification_counts": sweep["classification_counts"],
        "per_alpha": sweep["per_alpha"],
        "perturbations": sweep["perturbations"],
        "test_case_results": [
            {
                "name": tcr.name,
                "passed": tcr.passed,
                "error": float(tcr.error),
                "threshold": float(tcr.threshold),
                "notes": tcr.notes,
            }
            for tcr in run_result.test_case_results
        ],
        "notes": run_result.notes,
    }
    if computed_at_utc is not None:
        payload["computed_at_utc"] = computed_at_utc
    if run_window_utc is not None:
        payload["run_window_utc"] = dict(run_window_utc)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=indent)
        f.write("\n")
    return output_path


def _summarise_frozen_sweep(card: BenchmarkCard) -> dict[str, Any]:
    """Extract the frozen sweep block summary for the result JSON."""
    sweep = (
        card.frozen_parameters.get("sweep") if isinstance(card.frozen_parameters, dict) else None
    )
    if not isinstance(sweep, dict):
        return {}
    sweep_range = sweep.get("sweep_range", {})
    return {
        "parameter_name": sweep.get("parameter_name"),
        "start": sweep_range.get("start"),
        "end": sweep_range.get("end"),
        "n_points": sweep_range.get("n_points"),
        "scheme": sweep_range.get("scheme"),
    }


# ─── Result-block writer (in-memory) ─────────────────────────────────────────


def populate_result(
    card: BenchmarkCard,
    run_result: CardResult,
    evidence_paths: list[str] | None = None,
    notes: str = "",
) -> None:
    """Populate the card's in-memory result block with the run verdict.

    Mutates `card` in place. Does NOT write to disk: comment-preserving
    YAML serialisation is a Phase D verdict-commit responsibility (the
    library choice — ruamel.yaml or in-place hand-edit — is out of scope
    for C.4 since no Phase D run has happened yet).

    Sets `commit_hash` to "" per SCHEMA.md §Card lifecycle: the verdict
    commit lands with commit_hash empty, and a follow-up commit fills
    it self-referentially.

    The card's top-level `status` field is updated to mirror the verdict
    case-folded ("PASS" → "pass", etc.) per SCHEMA.md §Status values.
    """
    if evidence_paths is None:
        evidence_paths = []

    card.result["verdict"] = run_result.verdict
    card.result["evidence"] = list(evidence_paths)
    card.result["commit_hash"] = ""
    card.result["runner_version"] = run_result.runner_version
    card.result["notes"] = notes

    verdict_to_status = {"PASS": "pass", "FAIL": "fail", "CONDITIONAL": "conditional"}
    if run_result.verdict in verdict_to_status:
        card.status = verdict_to_status[run_result.verdict]
    else:
        raise ValueError(
            f"populate_result: unknown verdict {run_result.verdict!r}; "
            f"expected one of {sorted(verdict_to_status.keys())}"
        )


# ─── Backward-compatibility shims ────────────────────────────────────────────


def validate_card(path: Path | str) -> None:
    """Validate a card YAML file at `path`. Thin wrapper over load_card.

    Retained for compatibility with the v0.1.0 stub signature. New code
    should call load_card() directly to also receive the parsed
    BenchmarkCard.
    """
    load_card(path)


def write_card(spec: Any, path: Path | str) -> None:
    """Disk serialisation of a card. Not implemented at DG-1 Phase C.4.

    Phase D verdict commits write the populated result block back to the
    card's YAML file. That requires a comment-preserving YAML library
    (ruamel.yaml is the standard choice) so the card's human-readable
    structure survives the round-trip; the library choice is deferred.
    """
    raise NotImplementedError(
        "write_card: comment-preserving YAML serialisation is deferred to "
        "Phase D verdict-commit work. Use populate_result() to mutate the "
        "in-memory card; serialise via ruamel.yaml or hand-edit when the "
        "Phase D commit lands."
    )

"""
reporting.benchmark_card — Loader, validator, runner, and result-block writer.

DG-1 Phase C.4 per the work plan; extended in Phase C.10 to wire the
dynamical-card runner. Provides the infrastructure that Cards A1, A3,
A4 depend on:

    load_card(path)           — Read a YAML card and validate it against
                                SCHEMA.md v0.1.2.
    validate_card_data(data)  — Validate an already-parsed card dict
                                against the 16 schema rules.
    verify_gauge_annotation   — Enforce the canonical Hayden–Sorce
                                minimal-dissipation gauge block.
    run_card(card)            — Dispatch by model_kind. algebraic_map
                                cards (A1) run via Letter Eq. (6) on
                                the registered test-case handlers;
                                dynamical cards (A3, A4) run via the
                                TCL2 thermal-bath path through
                                cbg.tcl_recursion (thermal-only at
                                DG-1; coherent_displaced is deferred to
                                DG-2 per plan v0.1.4 §1.1).
    populate_result           — Mutate the in-memory card with the
                                verdict + metadata. Disk serialisation
                                is deferred (Phase D verdict commit needs
                                a comment-preserving YAML library).

Test-case handlers live in two registries — _TEST_CASE_HANDLERS for
algebraic_map cards (keyed by test_cases[i].name) and
_DYNAMICAL_TEST_CASE_HANDLERS for dynamical cards (keyed by
(card.model, test_cases[i].name)). New test cases require new entries;
the registries make the runner-side support surface explicit and
auditable.

Anchor: SCHEMA.md v0.1.2; DG-1 work plan v0.1.4 §4 Phase C rows C.4 and C.10.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import yaml

from cbg.basis import matrix_unit_basis, su_d_generator_basis, verify_orthonormality
from cbg.displacement_profiles import REGISTERED_PROFILES as _CBG_REGISTERED_PROFILES
from cbg.effective_hamiltonian import K_from_generator
from cbg.tcl_recursion import K_total_thermal_on_grid
from models import pure_dephasing, spin_boson_sigma_x
from numerical.tensor_ops import anticommutator, commutator
from numerical.time_grid import build_time_grid


__version__ = "0.1.0"  # Recorded in card.result.runner_version


# ─── Schema constants (SCHEMA.md v0.1.2) ─────────────────────────────────────

CANONICAL_GAUGE_BLOCK: Dict[str, Any] = {
    "gauge": "hayden-sorce-minimal-dissipation",
    "coordinate_dependent": True,
    "direct_observable": False,
    "gauge_alignment_required_for_comparison": ["hmf", "polaron", "mori"],
}

# Schema versions the runner knows how to validate. v0.1.1 was the first
# version to reach HEAD (Card A1 v0.1.0 was authored under it); v0.1.2 is
# the additive generalization that brought test_cases to dynamical cards
# (Cards A3, A4, and Card A1 v0.1.1 were authored under v0.1.2). Per
# SCHEMA.md §Schema versioning, "cards retain the schema they were
# authored against"; the runner accepts any known version. Validation
# uses the v0.1.2 rule set, which is a non-breaking superset of v0.1.1
# (the model_kind discriminator and test_cases pattern were already in
# v0.1.1; v0.1.2 only relaxed the bath_state / test_cases requirements
# for dynamical cards).
KNOWN_SCHEMA_VERSIONS: Tuple[str, ...] = ("v0.1.1", "v0.1.2")

VALID_STATUS = {"frozen-awaiting-run", "pass", "fail", "conditional", "superseded"}
VALID_MODEL_KIND = {"dynamical", "algebraic_map"}
VALID_STEWARDSHIP_FLAG = {"unflagged", "primary", "secondary", "stewardship-conflict-bound"}
VALID_DG_TARGET = {"DG-1", "DG-2", "DG-3", "DG-4", "DG-5"}

REQUIRED_TOP_LEVEL_KEYS: Tuple[str, ...] = (
    "schema_version", "card_id", "version", "date", "dg_target",
    "ledger_entry", "model", "status", "license", "gauge",
    "frozen_parameters", "acceptance_criterion", "result",
    "failure_mode_log", "stewardship_flag",
)

REQUIRED_FROZEN_PARAMETERS_SUBBLOCKS: Tuple[str, ...] = (
    "model", "truncation", "numerical", "comparison",
)


# ─── Exceptions ──────────────────────────────────────────────────────────────


class SchemaValidationError(ValueError):
    """A card YAML violates one of the SCHEMA.md v0.1.2 validation rules."""


class GaugeAnnotationError(ValueError):
    """A card's gauge block does not match the canonical Hayden–Sorce form."""


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
    gauge: Dict[str, Any]
    frozen_parameters: Dict[str, Any]
    acceptance_criterion: Dict[str, Any]
    result: Dict[str, Any]
    failure_mode_log: List[Dict[str, Any]]
    stewardship_flag: Dict[str, Any]
    supersedes: Optional[str] = None
    superseded_by: Optional[str] = None
    source_path: Optional[Path] = None

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
    hpta_residual: Optional[float] = None  # populated for pseudo-Kraus handlers; None for Lindblad-form handlers
    hpta_threshold: Optional[float] = None  # absolute Frobenius bound; None when no HPTA gate applies
    hermiticity_residual: Optional[float] = None  # populated for off-diagonal pseudo-Kraus (B2); None elsewhere
    hermiticity_threshold: Optional[float] = None  # absolute Frobenius bound; None when no Hermiticity gate applies


@dataclass
class CardResult:
    card_id: str
    verdict: str  # "PASS" | "FAIL" | "CONDITIONAL"
    test_case_results: List[TestCaseResult]
    runner_version: str
    notes: str = ""


# ─── Loader ──────────────────────────────────────────────────────────────────


def load_card(path: Path | str) -> BenchmarkCard:
    """Load and validate a benchmark card YAML file.

    Validates against SCHEMA.md v0.1.2 (16 rules); raises SchemaValidationError
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


def _data_to_card(data: Dict[str, Any]) -> BenchmarkCard:
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


# ─── Validator (SCHEMA.md v0.1.2 rules 1–16) ─────────────────────────────────


def validate_card_data(data: Dict[str, Any]) -> None:
    """Validate a parsed card dict against SCHEMA.md v0.1.2.

    Implements all 16 validation rules. Raises SchemaValidationError with
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
            f"rule 11: license must equal 'CC-BY-4.0 (LICENSE-docs)'; "
            f"got {data['license']!r}"
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

    # Rule 3: frozen-awaiting-run ⇒ result block empty
    r = data["result"]
    if data["status"] == "frozen-awaiting-run":
        if r.get("verdict") is not None:
            raise SchemaValidationError(
                "rule 3: status 'frozen-awaiting-run' requires result.verdict null"
            )
        if r.get("evidence") != []:
            raise SchemaValidationError(
                "rule 3: status 'frozen-awaiting-run' requires result.evidence []"
            )
        if r.get("commit_hash") != "":
            raise SchemaValidationError(
                "rule 3: status 'frozen-awaiting-run' requires result.commit_hash ''"
            )
        if r.get("runner_version") != "":
            raise SchemaValidationError(
                "rule 3: status 'frozen-awaiting-run' requires result.runner_version ''"
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
            raise SchemaValidationError(
                f"rule 7: frozen_parameters.{sub} required and non-empty"
            )

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
                    f"rule 14: model_kind == dynamical requires model.{f} "
                    f"at model level"
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
                raise SchemaValidationError(
                    f"rule 15: test_cases[{i}].{f} required and non-empty"
                )

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
            f"rule 9: acceptance_criterion.threshold must be a positive number; "
            f"got {thr!r}"
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
_SIGMA_PLUS = np.array([[0, 0], [1, 0]], dtype=complex)   # |1><0|


def _build_lindblad_generator(
    H: np.ndarray,
    jump_operators: List[np.ndarray],
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
    case: Dict[str, Any], d: int,
) -> Tuple[
    Callable[[np.ndarray], np.ndarray], np.ndarray,
    Optional[float], Optional[float],
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
    case: Dict[str, Any], d: int,
) -> Tuple[
    Callable[[np.ndarray], np.ndarray], np.ndarray,
    Optional[float], Optional[float],
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

_OPERATOR_NAMESPACE_BUILDERS: Dict[int, Callable[[], Dict[str, Any]]] = {
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
_ALLOWED_AST_NODES: Tuple[type, ...] = (
    ast.Expression,
    ast.Constant,           # numeric / complex literals (0.5, 1.0, 1j)
    ast.Name,               # identifiers — bound by the namespace
    ast.Load,               # context for Name reads
    ast.UnaryOp, ast.USub, ast.UAdd,
    ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.MatMult,
    ast.Call,               # only sqrt(...) — verified semantically below
)


def _eval_operator_expression(
    expr: str, parameters: Dict[str, Any], d: int,
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
        raise ValueError(
            f"_eval_operator_expression: cannot parse expression {expr!r}: {e}"
        ) from e

    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST_NODES):
            raise ValueError(
                f"_eval_operator_expression: forbidden AST node "
                f"{type(node).__name__} in expression {expr!r}"
            )
        if isinstance(node, ast.Call):
            if not (isinstance(node.func, ast.Name)
                    and node.func.id in _ALLOWED_FUNCTION_NAMES):
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
    operators: List[np.ndarray], coefficients: List[float],
) -> Callable[[np.ndarray], np.ndarray]:
    """Build L(rho) = sum_j gamma_j E_j rho E_j^dagger.

    Caller is responsible for HPTA: real coefficients and
    sum_j gamma_j E_j^dagger E_j = 0. This function does not validate.
    """
    def L(rho: np.ndarray) -> np.ndarray:
        out = np.zeros_like(rho, dtype=complex)
        for E, g in zip(operators, coefficients):
            out += g * (E @ rho @ E.conj().T)
        return out
    return L


def _hpta_residual(
    operators: List[np.ndarray], coefficients: List[float],
) -> float:
    """Absolute Frobenius norm of sum_j gamma_j E_j^dagger E_j."""
    acc = np.zeros_like(operators[0], dtype=complex)
    for E, g in zip(operators, coefficients):
        acc += g * (E.conj().T @ E)
    return float(np.linalg.norm(acc, ord="fro"))


def _make_pseudo_kraus_handler(
    expected_K: Callable[[Dict[str, Any]], np.ndarray],
) -> Callable[
    [Dict[str, Any], int],
    Tuple[
        Callable[[np.ndarray], np.ndarray], np.ndarray,
        float, Optional[float],
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
        case: Dict[str, Any], d: int,
    ) -> Tuple[
        Callable[[np.ndarray], np.ndarray], np.ndarray,
        float, Optional[float],
    ]:
        if d != 2:
            raise NotImplementedError(
                f"pseudo-Kraus handler: only d=2 supported (Card B1 v0.1.0); "
                f"got d={d}"
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

def _expected_K_pseudo_kraus_diagonal_sigma_z(case: Dict[str, Any]) -> np.ndarray:
    """K = -a * sigma_z; transcription §7 evaluated at the case's a."""
    a = float(case["parameters"]["a"])
    return -a * _SIGMA_Z


def _expected_K_pseudo_kraus_diagonal_sigma_x(case: Dict[str, Any]) -> np.ndarray:
    """K = -b * sigma_x; sigma_x analog of transcription §7 at the case's b."""
    b = float(case["parameters"]["b"])
    return -b * _SIGMA_X


def _expected_K_pseudo_kraus_traceless_jumps(case: Dict[str, Any]) -> np.ndarray:
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
    expr: str, parameters: Dict[str, Any],
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
    namespace: Dict[str, Any] = dict(parameters)
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
            f"_eval_complex_scalar_expression: cannot parse expression "
            f"{expr!r}: {e}"
        ) from e

    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST_NODES):
            raise ValueError(
                f"_eval_complex_scalar_expression: forbidden AST node "
                f"{type(node).__name__} in expression {expr!r}"
            )
        if isinstance(node, ast.Call):
            if not (isinstance(node.func, ast.Name)
                    and node.func.id in _ALLOWED_FUNCTION_NAMES):
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
    rows: List[List[str]], parameters: Dict[str, Any],
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
    operators: List[np.ndarray], omega: np.ndarray,
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
    operators: List[np.ndarray], omega: np.ndarray,
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
    expected_K: Callable[[Dict[str, Any]], np.ndarray],
) -> Callable[
    [Dict[str, Any], int],
    Tuple[
        Callable[[np.ndarray], np.ndarray], np.ndarray,
        float, float,
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
        case: Dict[str, Any], d: int,
    ) -> Tuple[
        Callable[[np.ndarray], np.ndarray], np.ndarray,
        float, float,
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

def _expected_K_offdiag_omega_imaginary_sigma_z(case: Dict[str, Any]) -> np.ndarray:
    """K = beta * sigma_z; transcription §7a worked fixture at the case's beta."""
    beta = float(case["parameters"]["beta"])
    return beta * _SIGMA_Z


def _expected_K_offdiag_omega_imaginary_sigma_x(case: Dict[str, Any]) -> np.ndarray:
    """K = -beta * sigma_x; sigma_x analog of §7a at the case's beta."""
    beta = float(case["parameters"]["beta"])
    return -beta * _SIGMA_X


def _expected_K_offdiag_omega_diagonal_only(case: Dict[str, Any]) -> np.ndarray:
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

_BASIS_BUILDERS: Dict[str, Callable[[int], List[np.ndarray]]] = {
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

_DISPLACEMENT_PROFILES: Dict[str, Callable[..., Any]] = dict(_CBG_REGISTERED_PROFILES)


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
        [Dict[str, Any], int],
        Tuple[
            Callable[[np.ndarray], np.ndarray], np.ndarray,
            Optional[float], Optional[float],
        ],
    ],
) -> Callable[
    [Dict[str, Any], int],
    Tuple[
        Callable[[np.ndarray], np.ndarray], None,
        Optional[float], Optional[float],
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
        case: Dict[str, Any], d: int,
    ) -> Tuple[
        Callable[[np.ndarray], np.ndarray], None,
        Optional[float], Optional[float],
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
_TEST_CASE_HANDLERS: Dict[
    str,
    Callable[
        [Dict[str, Any], int],
        Tuple[
            Callable[[np.ndarray], np.ndarray],
            Optional[np.ndarray],
            Optional[float],
            Optional[float],
        ],
    ],
] = {
    "canonical_lindblad_traceless": _handler_canonical_lindblad_traceless,
    "markovian_weak_coupling_lamb_shift": _handler_markovian_weak_coupling_lamb_shift,
    "pseudo_kraus_diagonal_sigma_z":
        _make_pseudo_kraus_handler(_expected_K_pseudo_kraus_diagonal_sigma_z),
    "pseudo_kraus_diagonal_sigma_x":
        _make_pseudo_kraus_handler(_expected_K_pseudo_kraus_diagonal_sigma_x),
    "pseudo_kraus_traceless_jumps":
        _make_pseudo_kraus_handler(_expected_K_pseudo_kraus_traceless_jumps),
    "offdiag_omega_imaginary_sigma_z":
        _make_offdiag_pseudo_kraus_handler(_expected_K_offdiag_omega_imaginary_sigma_z),
    "offdiag_omega_imaginary_sigma_x":
        _make_offdiag_pseudo_kraus_handler(_expected_K_offdiag_omega_imaginary_sigma_x),
    "offdiag_omega_diagonal_only":
        _make_offdiag_pseudo_kraus_handler(_expected_K_offdiag_omega_diagonal_only),
    "basis_independence_pseudo_kraus_sigma_z":
        _make_basis_independence_handler(
            _make_pseudo_kraus_handler(_expected_K_pseudo_kraus_diagonal_sigma_z)
        ),
    "basis_independence_lindblad_traceless":
        _make_basis_independence_handler(_handler_canonical_lindblad_traceless),
    "basis_independence_lindblad_lamb_shift":
        _make_basis_independence_handler(_handler_markovian_weak_coupling_lamb_shift),
}


# ─── Runner ──────────────────────────────────────────────────────────────────


def run_card(card: BenchmarkCard) -> CardResult:
    """Run a benchmark card to verdict.

    Dispatches by model_kind. algebraic_map cards (A1) run end-to-end
    using cbg.basis + cbg.effective_hamiltonian + numerical.tensor_ops.
    dynamical cards (A3, A4) raise NotImplementedError pointing at the
    yet-unimplemented C.5–C.10 modules.

    Verifies the gauge annotation before any computation; raises
    GaugeAnnotationError if the canonical block has been tampered with.
    """
    verify_gauge_annotation(card)
    if card.model_kind == "algebraic_map":
        return _run_algebraic_map(card)
    if card.model_kind == "dynamical":
        return _run_dynamical(card)
    # Unreachable given rule 13 validation, but defensive:
    raise SchemaValidationError(
        f"run_card: unknown model_kind {card.model_kind!r}"
    )


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
    abs_tol = float(
        card.frozen_parameters["numerical"]["integration_tolerance"]["absolute"]
    )
    test_cases = card.frozen_parameters["model"]["test_cases"]
    test_case_results: List[TestCaseResult] = []

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
            test_case_results.append(TestCaseResult(
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
            ))
            continue

        # HPTA precondition gate — applies only to handlers that surface a
        # non-None residual (pseudo-Kraus B1 / B2 cases). The threshold is
        # numerical.integration_tolerance.absolute, the same bound the card
        # cites in acceptance_criterion.rationale. A failure here means the
        # fixture is not a valid pseudo-Kraus generator and the K comparison
        # downstream would be meaningless; short-circuit with a clear
        # diagnostic instead.
        if hpta_residual is not None and hpta_residual > abs_tol:
            test_case_results.append(TestCaseResult(
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
            ))
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
            diff_norm = float(np.linalg.norm(K_computed - K_expected, ord="fro"))
            ref_norm = float(np.linalg.norm(K_expected, ord="fro"))
            if ref_norm > 0.0:
                error = diff_norm / ref_norm
            else:
                # If K_expected is zero, fall back to absolute Frobenius norm
                error = diff_norm

        test_case_results.append(TestCaseResult(
            name=name,
            passed=error <= threshold,
            error=error,
            threshold=threshold,
            hpta_residual=hpta_residual,
            hpta_threshold=abs_tol if hpta_residual is not None else None,
            hermiticity_residual=hermiticity_residual,
            hermiticity_threshold=abs_tol if hermiticity_residual is not None else None,
        ))

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
_MODEL_FACTORIES: Dict[str, Callable[[Dict[str, Any]], Tuple[np.ndarray, np.ndarray]]] = {
    "pure_dephasing": pure_dephasing.system_arrays_from_spec,
    "spin_boson_sigma_x": spin_boson_sigma_x.system_arrays_from_spec,
}


def _dyn_handler_pure_dephasing_thermal(
    K_array: np.ndarray, t_grid: np.ndarray, threshold: float, H_S: np.ndarray,
) -> Tuple[bool, float]:
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
    K_array: np.ndarray, t_grid: np.ndarray, threshold: float, H_S: np.ndarray,
) -> Tuple[bool, float]:
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
        transverse = float(np.sqrt(abs(b)**2 + abs(c)**2))
        max_transverse = max(max_transverse, transverse)
    return max_transverse <= threshold, max_transverse


# Dynamical test-case handler registry: keyed by (card.model, test_case_name).
# The model qualifier in the key is what distinguishes A3.thermal_bath from
# A4.thermal_bath (both have the same test_case name but different physics).
_DYNAMICAL_TEST_CASE_HANDLERS: Dict[
    Tuple[str, str],
    Callable[[np.ndarray, np.ndarray, float, np.ndarray], Tuple[bool, float]],
] = {
    ("pure_dephasing", "thermal_bath"): _dyn_handler_pure_dephasing_thermal,
    ("spin_boson_sigma_x", "thermal_bath"): _dyn_handler_sigma_x_thermal,
}


def _run_dynamical(card: BenchmarkCard) -> CardResult:
    """Run a dynamical card. Thermal-only at DG-1.

    Pipeline:
        1. Build (H_S, A) from card.model via _MODEL_FACTORIES dispatch.
        2. Build the time grid from frozen_parameters.numerical.time_grid.
        3. For each test_case:
              a. Verify bath_state.family == "thermal" (others raise with
                 carve-out routing per plan v0.1.4 §1.1).
              b. Compute K_total = K_0 + K_1 + ... + K_{N_card} on the grid
                 via cbg.tcl_recursion.K_total_thermal_on_grid.
              c. Apply the per-(model, test_case_name) handler from
                 _DYNAMICAL_TEST_CASE_HANDLERS to derive the verdict.

    Coherent-displaced bath states are deferred to DG-2 per the
    operationalisability carve-out (Cards A3 v0.1.0 / A4 v0.1.0 had those
    cases; v0.1.1 cards retain only thermal_bath).
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

    test_case_results: List[TestCaseResult] = []
    for case in fp["model"]["test_cases"]:
        bs = case["bath_state"]
        bs_family = bs.get("family")
        if bs_family != "thermal":
            raise NotImplementedError(
                f"_run_dynamical: bath_state.family {bs_family!r} not "
                f"supported at DG-1. Cards A3 / A4 coherent_displaced "
                f"sub-cases (Entries 3.B.3, 4.B.2) are deferred to DG-2 "
                f"per DG-1 work plan v0.1.4 §1.1 operationalisability "
                f"carve-out (displacement convention not specified). "
                f"Only 'thermal' is supported at this version."
            )

        K_array = K_total_thermal_on_grid(
            N_card, grid.times, H_S, A,
            bath_state=bs, spectral_density=sd,
        )

        handler_key = (card.model, case["name"])
        handler = _DYNAMICAL_TEST_CASE_HANDLERS.get(handler_key)
        if handler is None:
            raise TestCaseHandlerNotFoundError(
                f"_run_dynamical: no handler registered for "
                f"(model={card.model!r}, test_case={case['name']!r}). "
                f"Known: {sorted(_DYNAMICAL_TEST_CASE_HANDLERS.keys())}"
            )
        passed, error = handler(K_array, grid.times, threshold, H_S)
        test_case_results.append(TestCaseResult(
            name=case["name"],
            passed=passed,
            error=error,
            threshold=threshold,
        ))

    all_passed = all(r.passed for r in test_case_results)
    verdict = "PASS" if all_passed else "FAIL"
    return CardResult(
        card_id=card.card_id,
        verdict=verdict,
        test_case_results=test_case_results,
        runner_version=__version__,
    )


# ─── Result-block writer (in-memory) ─────────────────────────────────────────


def populate_result(
    card: BenchmarkCard,
    run_result: CardResult,
    evidence_paths: Optional[List[str]] = None,
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

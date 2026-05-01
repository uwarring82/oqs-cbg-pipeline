"""Behaviour tests for reporting.benchmark_card (DG-1 Phase C.4).

Covers:
- Loader (load_card) on real Card A1 v0.1.1 + corrupted-YAML rejection.
- Validator (validate_card_data) for all 16 SCHEMA.md v0.1.2 rules,
  with one positive and at least one negative case per major rule.
- Gauge-annotation enforcement.
- Runner end-to-end on Card A1 v0.1.1 (both test_cases PASS).
- Runner dispatch: dynamical cards (A3, A4) raise with C.5–C.10 routing.
- Test-case handler registry: unknown name raises TestCaseHandlerNotFoundError.
- Result-block writer (populate_result) mutates in-memory correctly.
- Backward-compat shims (validate_card, write_card).

Test-fixture cards live at the canonical paths under
benchmarks/benchmark_cards/. Negative validation cases construct dicts
in-memory rather than mutating files on disk.
"""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest
import yaml

from reporting import benchmark_card as bc


REPO_ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO_ROOT / "benchmarks" / "benchmark_cards"

# Canonical-current cards (v0.1.1 across the board after the
# Card A3/A4 v0.1.0 → v0.1.1 supersedure that deferred displaced cases).
A1_PATH = CARDS_DIR / "A1_closed-form-K_v0.1.1.yaml"
A3_PATH = CARDS_DIR / "A3_pure-dephasing_v0.1.1.yaml"
A4_PATH = CARDS_DIR / "A4_sigma-x-thermal_v0.1.1.yaml"

# DG-2 cards.
B1_PATH = CARDS_DIR / "B1_pseudo-kraus-diagonal_v0.1.0.yaml"

# Superseded cards retained for audit-trail tests.
A1_V010_PATH = CARDS_DIR / "A1_closed-form-K_v0.1.0.yaml"
A3_V010_PATH = CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml"
A4_V010_PATH = CARDS_DIR / "A4_sigma-x-thermal_v0.1.0.yaml"


# ─── Helpers ────────────────────────────────────────────────────────────────


def _load_raw(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def a1_data() -> dict:
    """Fresh copy of Card A1 v0.1.1's parsed dict for in-memory mutation."""
    return copy.deepcopy(_load_raw(A1_PATH))


@pytest.fixture
def a3_data() -> dict:
    return copy.deepcopy(_load_raw(A3_PATH))


# ─── Loader ─────────────────────────────────────────────────────────────────


def test_load_card_a1_v011_succeeds():
    card = bc.load_card(A1_PATH)
    assert isinstance(card, bc.BenchmarkCard)
    assert card.card_id == "A1"
    assert card.version == "v0.1.1"
    assert card.schema_version == "v0.1.2"
    assert card.model_kind == "algebraic_map"
    assert card.source_path == A1_PATH


def test_load_card_a3_succeeds():
    card = bc.load_card(A3_PATH)
    assert card.card_id == "A3"
    assert card.version == "v0.1.1"
    assert card.model_kind == "dynamical"


def test_load_card_a4_succeeds():
    card = bc.load_card(A4_PATH)
    assert card.card_id == "A4"
    assert card.version == "v0.1.1"
    assert card.model_kind == "dynamical"


def test_load_card_superseded_a1_v010_succeeds():
    """Superseded cards must still load (audit trail). The validator
    accepts status: superseded with superseded_by populated."""
    card = bc.load_card(A1_V010_PATH)
    assert card.status == "superseded"
    assert card.superseded_by == "A1_closed-form-K_v0.1.1.yaml"


def test_load_card_superseded_a3_v010_succeeds():
    card = bc.load_card(A3_V010_PATH)
    assert card.status == "superseded"
    assert card.superseded_by == "A3_pure-dephasing_v0.1.1.yaml"


def test_load_card_superseded_a4_v010_succeeds():
    card = bc.load_card(A4_V010_PATH)
    assert card.status == "superseded"
    assert card.superseded_by == "A4_sigma-x-thermal_v0.1.1.yaml"


def test_load_card_string_path():
    """Path can be passed as str, not just Path."""
    card = bc.load_card(str(A1_PATH))
    assert card.card_id == "A1"


def test_load_card_corrupted_yaml_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("[ this is a list, not a mapping ]\n")
    with pytest.raises(bc.SchemaValidationError, match="must be a mapping"):
        bc.load_card(bad)


# ─── Validator: positive and negative per rule ──────────────────────────────


def test_validate_passes_on_a1(a1_data):
    bc.validate_card_data(a1_data)  # must not raise


def test_validate_passes_on_a3(a3_data):
    bc.validate_card_data(a3_data)


def test_rule1_missing_required_key_raises(a1_data):
    del a1_data["card_id"]
    with pytest.raises(bc.SchemaValidationError, match="rule 1"):
        bc.validate_card_data(a1_data)


def test_rule12_unknown_schema_version_raises(a1_data):
    a1_data["schema_version"] = "v9.9.9"
    with pytest.raises(bc.SchemaValidationError, match="rule 12"):
        bc.validate_card_data(a1_data)


def test_rule11_wrong_license_raises(a1_data):
    a1_data["license"] = "MIT"
    with pytest.raises(bc.SchemaValidationError, match="rule 11"):
        bc.validate_card_data(a1_data)


def test_rule2_unknown_status_raises(a1_data):
    a1_data["status"] = "running"
    with pytest.raises(bc.SchemaValidationError, match="rule 2"):
        bc.validate_card_data(a1_data)


def test_rule5_superseded_without_superseded_by_raises(a1_data):
    a1_data["status"] = "superseded"
    # supersedes is set, but superseded_by is not — rule 5 needs successor
    a1_data.pop("superseded_by", None)
    with pytest.raises(bc.SchemaValidationError, match="rule 5"):
        bc.validate_card_data(a1_data)


def test_rule3_frozen_awaiting_run_with_dirty_result_raises(a1_data):
    # Reset to frozen-awaiting-run baseline (the loaded card may already
    # carry a populated result block post-Phase D verdict commit), then
    # introduce a dirty-result violation.
    a1_data["status"] = "frozen-awaiting-run"
    a1_data["result"]["verdict"] = "PASS"  # dirty result while frozen-awaiting-run
    a1_data["result"]["runner_version"] = ""
    with pytest.raises(bc.SchemaValidationError, match="rule 3"):
        bc.validate_card_data(a1_data)


def test_rule4_pass_status_requires_matching_verdict(a1_data):
    a1_data["status"] = "pass"
    a1_data["result"]["verdict"] = "FAIL"  # mismatched
    a1_data["result"]["runner_version"] = "0.1.0"
    with pytest.raises(bc.SchemaValidationError, match="rule 4"):
        bc.validate_card_data(a1_data)


def test_rule4_pass_status_requires_runner_version(a1_data):
    a1_data["status"] = "pass"
    a1_data["result"]["verdict"] = "PASS"
    a1_data["result"]["runner_version"] = ""  # explicitly clear (post-D may have set it)
    with pytest.raises(bc.SchemaValidationError, match="rule 4"):
        bc.validate_card_data(a1_data)


def test_rule4_invalid_commit_hash_raises(a1_data):
    a1_data["status"] = "pass"
    a1_data["result"]["verdict"] = "PASS"
    a1_data["result"]["runner_version"] = "0.1.0"
    a1_data["result"]["commit_hash"] = "not-a-hex-string"
    with pytest.raises(bc.SchemaValidationError, match="rule 4"):
        bc.validate_card_data(a1_data)


def test_rule6_modified_gauge_block_raises(a1_data):
    a1_data["gauge"]["gauge"] = "polaron-frame"
    with pytest.raises(bc.SchemaValidationError, match="rule 6"):
        bc.validate_card_data(a1_data)


def test_rule6_missing_gauge_alignment_list_raises(a1_data):
    a1_data["gauge"]["gauge_alignment_required_for_comparison"] = ["hmf"]
    with pytest.raises(bc.SchemaValidationError, match="rule 6"):
        bc.validate_card_data(a1_data)


def test_rule7_missing_subblock_raises(a1_data):
    del a1_data["frozen_parameters"]["truncation"]
    with pytest.raises(bc.SchemaValidationError, match="rule 7"):
        bc.validate_card_data(a1_data)


def test_rule13_unknown_model_kind_raises(a1_data):
    a1_data["frozen_parameters"]["model"]["model_kind"] = "perturbative"
    with pytest.raises(bc.SchemaValidationError, match="rule 13"):
        bc.validate_card_data(a1_data)


def test_rule14_dynamical_missing_system_hamiltonian_raises(a3_data):
    a3_data["frozen_parameters"]["model"]["system_hamiltonian"] = ""
    with pytest.raises(bc.SchemaValidationError, match="rule 14"):
        bc.validate_card_data(a3_data)


def test_rule14a_bath_state_neither_at_model_nor_per_case_raises(a3_data):
    # A3 has per-case bath_state in every test_case; remove from one to break 14a
    a3_data["frozen_parameters"]["model"]["test_cases"][0].pop("bath_state")
    # And ensure model-level is also absent (which it already is for A3)
    with pytest.raises(bc.SchemaValidationError, match="rule 14a"):
        bc.validate_card_data(a3_data)


def test_rule14a_model_level_bath_state_satisfies(a3_data):
    """When model-level bath_state is present, per-case may be missing
    (rule 14a satisfied via model level)."""
    # Remove per-case bath_state from all test_cases
    for case in a3_data["frozen_parameters"]["model"]["test_cases"]:
        case.pop("bath_state", None)
    # Add model-level bath_state
    a3_data["frozen_parameters"]["model"]["bath_state"] = {
        "family": "thermal", "temperature": 0.5,
    }
    bc.validate_card_data(a3_data)  # must not raise


def test_rule15_test_case_missing_required_field_raises(a1_data):
    a1_data["frozen_parameters"]["model"]["test_cases"][0]["expected_outcome"] = ""
    with pytest.raises(bc.SchemaValidationError, match="rule 15"):
        bc.validate_card_data(a1_data)


def test_rule15a_algebraic_map_with_empty_test_cases_raises(a1_data):
    a1_data["frozen_parameters"]["model"]["test_cases"] = []
    with pytest.raises(bc.SchemaValidationError, match="rule 15a"):
        bc.validate_card_data(a1_data)


def test_rule15a_algebraic_map_with_system_hamiltonian_raises(a1_data):
    a1_data["frozen_parameters"]["model"]["system_hamiltonian"] = "something"
    with pytest.raises(bc.SchemaValidationError, match="rule 15a"):
        bc.validate_card_data(a1_data)


def test_rule16_dynamical_missing_time_grid_raises(a3_data):
    a3_data["frozen_parameters"]["numerical"]["time_grid"] = None
    with pytest.raises(bc.SchemaValidationError, match="rule (14|16)"):
        bc.validate_card_data(a3_data)


def test_rule8_negative_perturbative_order_raises(a1_data):
    a1_data["frozen_parameters"]["truncation"]["perturbative_order"] = -1
    with pytest.raises(bc.SchemaValidationError, match="rule 8"):
        bc.validate_card_data(a1_data)


def test_rule8_non_integer_perturbative_order_raises(a1_data):
    a1_data["frozen_parameters"]["truncation"]["perturbative_order"] = 1.5
    with pytest.raises(bc.SchemaValidationError, match="rule 8"):
        bc.validate_card_data(a1_data)


def test_rule9_zero_threshold_raises(a1_data):
    a1_data["acceptance_criterion"]["threshold"] = 0.0
    with pytest.raises(bc.SchemaValidationError, match="rule 9"):
        bc.validate_card_data(a1_data)


def test_rule9_negative_threshold_raises(a1_data):
    a1_data["acceptance_criterion"]["threshold"] = -1e-10
    with pytest.raises(bc.SchemaValidationError, match="rule 9"):
        bc.validate_card_data(a1_data)


def test_rule10_invalid_stewardship_status_raises(a1_data):
    a1_data["stewardship_flag"]["status"] = "questionable"
    with pytest.raises(bc.SchemaValidationError, match="rule 10"):
        bc.validate_card_data(a1_data)


def test_rule10_primary_without_data_source_raises(a1_data):
    a1_data["stewardship_flag"]["status"] = "primary"
    a1_data["stewardship_flag"]["rationale"] = "yes"
    a1_data["stewardship_flag"]["data_source"] = ""
    with pytest.raises(bc.SchemaValidationError, match="rule 10"):
        bc.validate_card_data(a1_data)


# ─── Gauge-annotation enforcement ───────────────────────────────────────────


def test_verify_gauge_annotation_passes_on_a1():
    card = bc.load_card(A1_PATH)
    bc.verify_gauge_annotation(card)  # must not raise


def test_verify_gauge_annotation_rejects_modified_gauge():
    card = bc.load_card(A1_PATH)
    card.gauge = {**card.gauge, "gauge": "polaron-frame"}
    with pytest.raises(bc.GaugeAnnotationError, match="canonical Hayden"):
        bc.verify_gauge_annotation(card)


# ─── Runner: end-to-end on Card A1 v0.1.1 ───────────────────────────────────


def test_run_card_a1_v011_passes_both_test_cases():
    """Card A1 v0.1.1's two test_cases run end-to-end and PASS."""
    card = bc.load_card(A1_PATH)
    result = bc.run_card(card)
    assert result.verdict == "PASS"
    assert len(result.test_case_results) == 2
    names = {r.name for r in result.test_case_results}
    assert names == {"canonical_lindblad_traceless", "markovian_weak_coupling_lamb_shift"}
    for tcr in result.test_case_results:
        assert tcr.passed
        assert tcr.error <= card.threshold
    assert result.runner_version == bc.__version__


def test_run_card_a1_canonical_lindblad_recovers_input_H():
    """The canonical_lindblad_traceless test_case is exact: error ≪ threshold."""
    card = bc.load_card(A1_PATH)
    result = bc.run_card(card)
    tcr = next(r for r in result.test_case_results if r.name == "canonical_lindblad_traceless")
    assert tcr.error < 1e-12  # well below the 1e-10 threshold


def test_run_card_a1_lamb_shift_recovers_combined_H():
    """The markovian_weak_coupling_lamb_shift case is also exact."""
    card = bc.load_card(A1_PATH)
    result = bc.run_card(card)
    tcr = next(r for r in result.test_case_results
               if r.name == "markovian_weak_coupling_lamb_shift")
    assert tcr.error < 1e-12


def test_run_card_a1_v010_pseudo_kraus_handler_missing(a1_data):
    """A1 v0.1.0 (superseded) has pseudo_kraus_diagonal — no handler exists.

    The runner should refuse to run a superseded card cleanly. Loading
    succeeds, but running it triggers the handler-not-found error since
    the pseudo_kraus_diagonal handler was deliberately not registered
    (Entry 1.B.3 deferred to DG-2)."""
    card = bc.load_card(A1_V010_PATH)
    # Status is 'superseded'; running it is a misuse, but if forced...
    # Actually, the runner doesn't check status — it just runs whatever
    # test_cases are present. The pseudo_kraus_diagonal handler is missing.
    with pytest.raises(bc.TestCaseHandlerNotFoundError, match="pseudo_kraus_diagonal"):
        bc.run_card(card)


# ─── Runner: dynamical cards (A3, A4) thermal-only ───────────────────────────


def test_run_card_a3_v011_passes_thermal_case():
    """Card A3 v0.1.1 (pure dephasing, thermal_bath) verdict = PASS.

    Verifies Entry 3.B.1 (K(t) ∝ sigma_z) + Entry 3.B.2 (no
    renormalisation; ω_r(t) = ω at all orders ≤ N_card = 2). End-to-end
    through cbg.tcl_recursion.K_total_thermal_on_grid.
    """
    card = bc.load_card(A3_PATH)
    result = bc.run_card(card)
    assert result.verdict == "PASS"
    assert len(result.test_case_results) == 1
    tcr = result.test_case_results[0]
    assert tcr.name == "thermal_bath"
    assert tcr.passed
    # The thermal trivialisation gives error well below threshold.
    assert tcr.error < 1e-10
    assert tcr.threshold == card.threshold


def test_run_card_a4_v011_passes_thermal_case():
    """Card A4 v0.1.1 (sigma_x, thermal_bath) verdict = PASS.

    Verifies Entry 4.B.1 (parity-class theorem; no eigenbasis rotation
    for thermal bath) at order ≤ N_card = 2.
    """
    card = bc.load_card(A4_PATH)
    result = bc.run_card(card)
    assert result.verdict == "PASS"
    assert len(result.test_case_results) == 1
    tcr = result.test_case_results[0]
    assert tcr.name == "thermal_bath"
    assert tcr.passed
    assert tcr.error < 1e-10
    assert tcr.threshold == card.threshold


def test_run_card_a3_v010_displaced_case_routes_to_dg2():
    """The superseded A3 v0.1.0 has a coherent_displaced test_case; running
    it surfaces the operationalisability carve-out via the routing message.

    Audit-trail test: confirms the runner correctly refuses to evaluate the
    deferred case rather than silently producing a misleading verdict."""
    card = bc.load_card(A3_V010_PATH)
    with pytest.raises(NotImplementedError, match="v0.1.4"):
        bc.run_card(card)


def test_run_card_a4_v010_displaced_case_routes_to_dg2():
    """A4 v0.1.0 displaced case routes to DG-2, parallel to A3 v0.1.0."""
    card = bc.load_card(A4_V010_PATH)
    with pytest.raises(NotImplementedError, match="v0.1.4"):
        bc.run_card(card)


def test_run_card_dynamical_uses_correct_runner_version():
    """The runner_version recorded on a dynamical CardResult matches
    reporting.benchmark_card.__version__."""
    card = bc.load_card(A3_PATH)
    result = bc.run_card(card)
    assert result.runner_version == bc.__version__


# ─── Runner: gauge tampering aborts before computation ──────────────────────


def test_run_card_with_tampered_gauge_aborts():
    card = bc.load_card(A1_PATH)
    card.gauge = {**card.gauge, "direct_observable": True}
    with pytest.raises(bc.GaugeAnnotationError):
        bc.run_card(card)


# ─── Result-block writer ────────────────────────────────────────────────────


def test_populate_result_pass_sets_status_pass():
    card = bc.load_card(A1_PATH)
    run_result = bc.run_card(card)  # PASS
    bc.populate_result(card, run_result, evidence_paths=["plots/A1.png"], notes="ok")
    assert card.result["verdict"] == "PASS"
    assert card.result["evidence"] == ["plots/A1.png"]
    assert card.result["commit_hash"] == ""  # filled in self-referential follow-up
    assert card.result["runner_version"] == bc.__version__
    assert card.result["notes"] == "ok"
    assert card.status == "pass"


def test_populate_result_fail_sets_status_fail():
    card = bc.load_card(A1_PATH)
    fake_run = bc.CardResult(
        card_id=card.card_id,
        verdict="FAIL",
        test_case_results=[],
        runner_version="0.1.0",
    )
    bc.populate_result(card, fake_run)
    assert card.result["verdict"] == "FAIL"
    assert card.status == "fail"


def test_populate_result_unknown_verdict_raises():
    card = bc.load_card(A1_PATH)
    fake_run = bc.CardResult(
        card_id=card.card_id, verdict="MAYBE",
        test_case_results=[], runner_version="0.1.0",
    )
    with pytest.raises(ValueError, match="unknown verdict"):
        bc.populate_result(card, fake_run)


# ─── Backward-compat shims ──────────────────────────────────────────────────


def test_validate_card_path_wrapper():
    bc.validate_card(A1_PATH)  # must not raise


def test_write_card_remains_stubbed_pending_phase_d():
    """write_card still raises NotImplementedError; comment-preserving
    YAML serialisation is deferred to Phase D verdict-commit work."""
    with pytest.raises(NotImplementedError, match="Phase D"):
        bc.write_card({}, "/tmp/nonexistent.yaml")


# ─── Test-case handler registry ─────────────────────────────────────────────


def test_test_case_handlers_cover_a1_v011_test_cases():
    """Every test_case name in Card A1 v0.1.1 has a registered handler."""
    card = bc.load_card(A1_PATH)
    for case in card.frozen_parameters["model"]["test_cases"]:
        assert case["name"] in bc._TEST_CASE_HANDLERS


def test_unknown_test_case_name_raises_handler_not_found(a1_data):
    """Adding an unknown test_case name surfaces a clear error."""
    a1_data["frozen_parameters"]["model"]["test_cases"].append({
        "name": "made_up_test",
        "description": "not a real test",
        "expected_outcome": "unknown",
        "reference": "no paper",
    })
    card = bc._data_to_card(a1_data)
    with pytest.raises(bc.TestCaseHandlerNotFoundError, match="made_up_test"):
        bc.run_card(card)


# ─── Symbolic-operator parser (B1 pseudo-Kraus support) ─────────────────────


def test_eval_operator_expression_parses_complex_combination():
    op = bc._eval_operator_expression("I + 1j * a * sigma_z", {"a": 0.5}, 2)
    expected = np.array([[1 + 0.5j, 0], [0, 1 - 0.5j]], dtype=complex)
    assert np.allclose(op, expected)


def test_eval_operator_expression_parses_sqrt_scaling():
    op = bc._eval_operator_expression("sqrt(1 + b**2) * I", {"b": 0.5}, 2)
    expected = np.sqrt(1.25) * np.eye(2, dtype=complex)
    assert np.allclose(op, expected)


def test_eval_operator_expression_handles_empty_parameters():
    op = bc._eval_operator_expression("sigma_x", {}, 2)
    assert np.allclose(op, bc._SIGMA_X)


def test_eval_operator_expression_rejects_unknown_identifier():
    with pytest.raises(ValueError, match="unknown identifier"):
        bc._eval_operator_expression("sigma_q", {}, 2)


def test_eval_operator_expression_rejects_attribute_access():
    """Attribute access (e.g. ``I.real``) must be rejected — closes a
    common eval-escape route."""
    with pytest.raises(ValueError, match="forbidden AST node|unknown identifier"):
        bc._eval_operator_expression("I.real", {}, 2)


def test_eval_operator_expression_rejects_non_sqrt_call():
    with pytest.raises(ValueError, match="only calls to|unknown identifier"):
        bc._eval_operator_expression("exp(1) * I", {}, 2)


def test_eval_operator_expression_rejects_parameter_shadowing_namespace():
    with pytest.raises(ValueError, match="shadows a reserved identifier"):
        bc._eval_operator_expression("I + a * sigma_z", {"I": 0.0, "a": 0.5}, 2)


def test_eval_operator_expression_rejects_unregistered_dimension():
    with pytest.raises(NotImplementedError, match="no operator namespace"):
        bc._eval_operator_expression("I", {}, 3)


def test_eval_operator_expression_rejects_syntax_error():
    with pytest.raises(ValueError, match="cannot parse"):
        bc._eval_operator_expression("I +", {}, 2)


# ─── B1 pseudo-Kraus runner end-to-end ──────────────────────────────────────


def test_load_card_b1_succeeds():
    card = bc.load_card(B1_PATH)
    assert card.card_id == "B1"
    assert card.dg_target == "DG-2"
    assert card.version == "v0.1.0"
    assert card.status == "frozen-awaiting-run"
    assert card.model_kind == "algebraic_map"


def test_run_card_b1_passes_all_three_test_cases():
    """Card B1 v0.1.0's three pseudo-Kraus test_cases all PASS at machine
    precision; HPTA residuals are well below the absolute tolerance."""
    card = bc.load_card(B1_PATH)
    result = bc.run_card(card)
    assert result.verdict == "PASS"
    assert len(result.test_case_results) == 3
    names = {r.name for r in result.test_case_results}
    assert names == {
        "pseudo_kraus_diagonal_sigma_z",
        "pseudo_kraus_diagonal_sigma_x",
        "pseudo_kraus_traceless_jumps",
    }
    for tcr in result.test_case_results:
        assert tcr.passed
        assert tcr.error <= card.threshold
        # All three fixtures satisfy HPTA as algebraic identities; numerical
        # residual is bounded by complex-arithmetic round-off (~3e-16) and
        # is well below the 1e-14 absolute threshold.
        assert tcr.hpta_residual is not None
        assert tcr.hpta_threshold is not None
        assert tcr.hpta_residual <= tcr.hpta_threshold


def test_run_card_b1_sigma_z_recovers_minus_half_sigma_z():
    """Diagnostic check: the σ_z fixture (a=0.5) reproduces K = -0.5 σ_z
    at exactly zero error (algebraic tautology of the matrix-unit
    summation against the trace-based H_HS formula)."""
    card = bc.load_card(B1_PATH)
    result = bc.run_card(card)
    tcr = next(r for r in result.test_case_results
               if r.name == "pseudo_kraus_diagonal_sigma_z")
    assert tcr.error == 0.0


def test_run_card_b1_sigma_x_recovers_minus_half_sigma_x():
    """The σ_x analog is structurally identical to the σ_z fixture and
    must also pass at exactly zero error — confirms the implementation
    is not silently axis-biased."""
    card = bc.load_card(B1_PATH)
    result = bc.run_card(card)
    tcr = next(r for r in result.test_case_results
               if r.name == "pseudo_kraus_diagonal_sigma_x")
    assert tcr.error == 0.0


def test_run_card_b1_traceless_gives_zero_K():
    """All-traceless jumps (σ_x with γ=1, σ_y with γ=-1) give K = 0
    per transcription §5; HPTA holds exactly (σ_x² = σ_y² = I)."""
    card = bc.load_card(B1_PATH)
    result = bc.run_card(card)
    tcr = next(r for r in result.test_case_results
               if r.name == "pseudo_kraus_traceless_jumps")
    assert tcr.error == 0.0
    assert tcr.hpta_residual == 0.0


def test_b1_test_case_handlers_all_registered():
    """Every test_case name in Card B1 v0.1.0 has a registered handler."""
    card = bc.load_card(B1_PATH)
    for case in card.frozen_parameters["model"]["test_cases"]:
        assert case["name"] in bc._TEST_CASE_HANDLERS


def test_run_card_b1_hpta_gate_short_circuits_on_violation():
    """Synthetic HPTA-violating fixture (E_2 = I instead of sqrt(1+a²)*I)
    triggers the HPTA precondition gate; the K comparison is skipped and
    the failure carries a diagnostic note plus the residual fields."""
    raw = _load_raw(B1_PATH)
    case = raw["frozen_parameters"]["model"]["test_cases"][0]
    # Break HPTA by removing the sqrt scaling on E_2; the fixture is no
    # longer a valid pseudo-Kraus generator.
    case["pseudo_kraus_operators"][1] = "I"
    card = bc._data_to_card(raw)
    # Bypass full validation (gauge etc. unchanged); call the algebraic-map
    # runner directly to focus the assertion on the HPTA gate.
    result = bc._run_algebraic_map(card)
    tcr = next(r for r in result.test_case_results
               if r.name == "pseudo_kraus_diagonal_sigma_z")
    assert not tcr.passed
    assert tcr.hpta_residual is not None
    assert tcr.hpta_residual > tcr.hpta_threshold
    assert "HPTA precondition failed" in tcr.notes


# ─── A1 regression: TestCaseResult.hpta_residual is None for Lindblad ───────


def test_a1_results_carry_no_hpta_fields():
    """A1's Lindblad-form handlers do not surface an HPTA residual; the
    new TestCaseResult fields remain None for these cases."""
    card = bc.load_card(A1_PATH)
    result = bc.run_card(card)
    for tcr in result.test_case_results:
        assert tcr.hpta_residual is None
        assert tcr.hpta_threshold is None

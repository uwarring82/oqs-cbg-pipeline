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
B2_PATH = CARDS_DIR / "B2_pseudo-kraus-offdiagonal_v0.1.0.yaml"
B3_PATH = CARDS_DIR / "B3_cross-basis-structural-identity_v0.1.0.yaml"
B4_PATH = CARDS_DIR / "B4-conv-registry_v0.1.0.yaml"
B5_V010_PATH = CARDS_DIR / "B5-conv-registry_v0.1.0.yaml"
B5_PATH = CARDS_DIR / "B5-conv-registry_v0.2.0.yaml"

# DG-3 cards.
C1_PATH = CARDS_DIR / "C1_cross-method-pure-dephasing_v0.1.0.yaml"
C2_PATH = CARDS_DIR / "C2_cross-method-spin-boson_v0.1.0.yaml"

# Superseded cards retained for audit-trail tests.
A1_V010_PATH = CARDS_DIR / "A1_closed-form-K_v0.1.0.yaml"
A3_V010_PATH = CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml"
A4_V010_PATH = CARDS_DIR / "A4_sigma-x-thermal_v0.1.0.yaml"


# ─── Helpers ────────────────────────────────────────────────────────────────


def _load_raw(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def _single_case_card(
    path: Path,
    case_name: str,
    *,
    t_end: float = 5.0,
    n_points: int = 41,
) -> bc.BenchmarkCard:
    """Return an in-memory single-case clone with a smaller time grid.

    The real C1/C2 cards freeze a 200-point grid for verdict work. Runner
    unit tests use the same card surface but a reduced grid to keep the
    finite-environment reference quick.
    """
    data = copy.deepcopy(_load_raw(path))
    cases = data["frozen_parameters"]["model"]["test_cases"]
    selected = [case for case in cases if case["name"] == case_name]
    assert len(selected) == 1
    data["frozen_parameters"]["model"]["test_cases"] = selected
    time_grid = data["frozen_parameters"]["numerical"]["time_grid"]
    time_grid["t_end"] = t_end
    time_grid["n_points"] = n_points
    bc.validate_card_data(data)
    return bc._data_to_card(data)


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


def test_load_card_c1_succeeds():
    card = bc.load_card(C1_PATH)
    assert card.card_id == "C1"
    assert card.dg_target == "DG-3"
    assert card.model == "pure_dephasing"
    assert card.model_kind == "dynamical"


def test_load_card_c2_succeeds():
    card = bc.load_card(C2_PATH)
    assert card.card_id == "C2"
    assert card.dg_target == "DG-3"
    assert card.model == "spin_boson_sigma_x"
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
        "family": "thermal",
        "temperature": 0.5,
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


# ─── SCHEMA.md v0.1.3 additions: Rules 17, 18, scope-definition status ──────


D1_PATH = CARDS_DIR / "D1_failure-envelope-convergence_v0.1.1.yaml"
D1_V010_PATH = CARDS_DIR / "D1_failure-envelope-convergence_v0.1.0.yaml"
E1_PATH = CARDS_DIR / "E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml"


@pytest.fixture
def d1_data() -> dict:
    """Fresh copy of Card D1 v0.1.1's parsed dict (carries sweep block)."""
    return copy.deepcopy(_load_raw(D1_PATH))


@pytest.fixture
def e1_data() -> dict:
    """Fresh copy of Card E1 v0.1.0's parsed dict (status: scope-definition)."""
    return copy.deepcopy(_load_raw(E1_PATH))


def test_known_schema_versions_includes_v013():
    assert "v0.1.3" in bc.KNOWN_SCHEMA_VERSIONS


def test_valid_status_includes_scope_definition():
    assert "scope-definition" in bc.VALID_STATUS


def test_load_card_d1_succeeds():
    card = bc.load_card(D1_PATH)
    assert card.card_id == "D1"
    assert card.version == "v0.1.1"
    assert card.schema_version == "v0.1.3"
    assert card.model == "spin_boson_sigma_x"


def test_load_card_d1_v010_superseded():
    card = bc.load_card(D1_V010_PATH)
    assert card.status == "superseded"
    assert card.superseded_by == "D1_failure-envelope-convergence_v0.1.1.yaml"


def test_d1_v011_freezes_parity_aware_metric_and_operational_perturbations():
    card = bc.load_card(D1_PATH)
    fp = card.frozen_parameters
    assert fp["model"]["coupling_operator"] == "sigma_x"
    assert "bath_mode_cutoff" not in fp["truncation"]
    assert fp["comparison"]["error_metric"] == "convergence_ratio_parity_aware"
    assert fp["numerical"]["quadrature"]["upper_cutoff_factor"] == 30.0
    perturbations = {p["name"]: p for p in fp["reproducibility"]["perturbations"]}
    assert perturbations["upper_cutoff_factor"]["pathway"] == "quadrature_kwargs_allow_list"
    assert perturbations["omega_c"]["target_path"] == (
        "model.bath_spectral_density.cutoff_frequency"
    )
    assert perturbations["omega_c"]["pathway"] == "model_spec_mutation"


def test_load_card_e1_succeeds():
    card = bc.load_card(E1_PATH)
    assert card.card_id == "E1"
    assert card.schema_version == "v0.1.3"
    assert card.status == "scope-definition"


def test_validate_passes_on_d1(d1_data):
    bc.validate_card_data(d1_data)  # must not raise


def test_validate_passes_on_e1(e1_data):
    bc.validate_card_data(e1_data)  # must not raise


def test_rule17_sweep_missing_parameter_name_raises(d1_data):
    d1_data["frozen_parameters"]["sweep"]["parameter_name"] = ""
    with pytest.raises(bc.SchemaValidationError, match="rule 17"):
        bc.validate_card_data(d1_data)


def test_rule17_sweep_missing_sweep_range_raises(d1_data):
    del d1_data["frozen_parameters"]["sweep"]["sweep_range"]
    with pytest.raises(bc.SchemaValidationError, match="rule 17"):
        bc.validate_card_data(d1_data)


def test_rule17_sweep_range_missing_n_points_raises(d1_data):
    del d1_data["frozen_parameters"]["sweep"]["sweep_range"]["n_points"]
    with pytest.raises(bc.SchemaValidationError, match="rule 17"):
        bc.validate_card_data(d1_data)


def test_rule17_sweep_range_zero_n_points_raises(d1_data):
    d1_data["frozen_parameters"]["sweep"]["sweep_range"]["n_points"] = 0
    with pytest.raises(bc.SchemaValidationError, match="rule 17"):
        bc.validate_card_data(d1_data)


def test_rule17_sweep_range_unknown_scheme_raises(d1_data):
    d1_data["frozen_parameters"]["sweep"]["sweep_range"]["scheme"] = "exponential"
    with pytest.raises(bc.SchemaValidationError, match="rule 17"):
        bc.validate_card_data(d1_data)


def test_rule17_sweep_range_non_numeric_start_raises(d1_data):
    d1_data["frozen_parameters"]["sweep"]["sweep_range"]["start"] = "low"
    with pytest.raises(bc.SchemaValidationError, match="rule 17"):
        bc.validate_card_data(d1_data)


def test_rule17_absent_sweep_block_is_fine_for_non_sweep_cards(a1_data):
    """A card without a sweep block must still validate (sweep is optional)."""
    a1_data["frozen_parameters"].pop("sweep", None)
    bc.validate_card_data(a1_data)  # must not raise


def test_rule18_scope_definition_without_log_or_notes_raises(e1_data):
    """Stripping both failure_mode_log AND result.notes triggers rule 18."""
    e1_data["failure_mode_log"] = []
    e1_data["result"]["notes"] = ""
    with pytest.raises(bc.SchemaValidationError, match="rule 18"):
        bc.validate_card_data(e1_data)


def test_rule18_scope_definition_with_only_failure_mode_log_satisfies(e1_data):
    """failure_mode_log alone is sufficient for rule 18 (notes may be empty)."""
    assert e1_data["failure_mode_log"]  # E1 carries one entry by construction
    e1_data["result"]["notes"] = ""
    bc.validate_card_data(e1_data)  # must not raise


def test_rule18_scope_definition_with_only_notes_satisfies(e1_data):
    """result.notes alone is sufficient for rule 18 (log may be empty)."""
    e1_data["failure_mode_log"] = []
    assert e1_data["result"]["notes"]  # E1 carries notes by construction
    bc.validate_card_data(e1_data)  # must not raise


def test_rule3_scope_definition_with_dirty_result_raises(e1_data):
    """status: scope-definition shares rule 3's empty-result precondition."""
    e1_data["result"]["verdict"] = "PASS"
    with pytest.raises(bc.SchemaValidationError, match="rule 3"):
        bc.validate_card_data(e1_data)


def test_rule3_scope_definition_with_runner_version_raises(e1_data):
    e1_data["result"]["runner_version"] = "0.1.0"
    with pytest.raises(bc.SchemaValidationError, match="rule 3"):
        bc.validate_card_data(e1_data)


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
    tcr = next(
        r for r in result.test_case_results if r.name == "markovian_weak_coupling_lamb_shift"
    )
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


def test_run_card_a3_v010_legacy_displaced_shape_now_rejected():
    """The superseded A3 v0.1.0 has a coherent_displaced test_case in the
    legacy shape (`displacement_amplitude` only, no `displacement_profile`).
    Pre-Council-Act-2 the runner raised NotImplementedError with the
    standing v0.1.4 carve-out message; post-Council-Act-2 (2026-05-04, this
    repo at this commit) the runner lifts the family carve-out and
    dispatches into D_bar_1, which raises ValueError on the missing
    displacement_profile key — surfacing the schema gap that A3 v0.1.0's
    supersedure to v0.1.1 was performed to address. The verdict-trail-
    preservation property holds: the superseded card still surfaces the
    gap that motivated its supersedure, just under a different (post-
    clearance) error type."""
    card = bc.load_card(A3_V010_PATH)
    with pytest.raises(ValueError, match="displacement_profile"):
        bc.run_card(card)


def test_run_card_a4_v010_legacy_displaced_shape_now_rejected():
    """A4 v0.1.0 displaced legacy shape rejected post-Council-Act-2,
    parallel to A3 v0.1.0."""
    card = bc.load_card(A4_V010_PATH)
    with pytest.raises(ValueError, match="displacement_profile"):
        bc.run_card(card)


def test_run_card_dynamical_uses_correct_runner_version():
    """The runner_version recorded on a dynamical CardResult matches
    reporting.benchmark_card.__version__."""
    card = bc.load_card(A3_PATH)
    result = bc.run_card(card)
    assert result.runner_version == bc.__version__


def test_run_card_dynamical_threads_quadrature_extras(monkeypatch):
    seen = {}

    def fake_K_total_thermal_on_grid(
        N_card,
        t_grid,
        system_hamiltonian,
        coupling_operator,
        *,
        bath_state,
        spectral_density,
        basis=None,
        upper_cutoff_factor=30.0,
        quad_limit=200,
    ):
        seen.update(
            {
                "N_card": N_card,
                "upper_cutoff_factor": upper_cutoff_factor,
                "quad_limit": quad_limit,
                "basis": basis,
            }
        )
        return np.repeat(np.asarray(system_hamiltonian)[None, :, :], len(t_grid), axis=0)

    monkeypatch.setattr(bc, "K_total_thermal_on_grid", fake_K_total_thermal_on_grid)

    card = bc.load_card(A3_PATH)
    card.frozen_parameters["numerical"]["quadrature"] = {
        "upper_cutoff_factor": 20.0,
        "quad_limit": 100,
        "ignored_future_key": "kept out of cbg.tcl_recursion",
    }
    result = bc.run_card(card)

    assert result.verdict == "PASS"
    assert seen == {
        "N_card": 2,
        "upper_cutoff_factor": 20.0,
        "quad_limit": 100,
        "basis": None,
    }


# ─── Runner: DG-3 cross-method cards ────────────────────────────────────────


def test_c1_c2_cross_method_test_cases_have_explicit_handlers():
    """Every frozen DG-3 test_case lands in the cross-method registry.

    Some handlers are intentionally deferred and raise NotImplementedError,
    but the registry entry itself is explicit so cards-first gaps surface
    with a specific route rather than a generic missing-handler error.
    """
    for path in (C1_PATH, C2_PATH):
        card = bc.load_card(path)
        for case in card.frozen_parameters["model"]["test_cases"]:
            assert (card.model, case["name"]) in bc._CROSS_METHOD_TEST_CASE_HANDLERS


def test_run_card_c1_thermal_scope_returns_fail_verdict():
    """C1 pure_dephasing × thermal_bath now runs both reference methods.

    The expected Phase C outcome is a clean FAIL: the finite-bath exact
    reference has recurrences, while the QuTiP reference is Markovian, so
    their inter-method discrepancy is far above C1's 1e-6 threshold.
    """
    card = _single_case_card(C1_PATH, "thermal_bath_cross_method")
    result = bc.run_card(card)
    assert result.verdict == "FAIL"
    assert result.runner_version == bc.__version__
    assert len(result.test_case_results) == 1
    tcr = result.test_case_results[0]
    assert tcr.name == "thermal_bath_cross_method"
    assert not tcr.passed
    assert tcr.error > card.threshold
    assert tcr.threshold == card.threshold
    assert "exact_finite_env finite-system" in tcr.notes
    assert "qutip_reference solver-default" in tcr.notes


def test_run_card_c1_displaced_runs_to_clean_fail():
    """C1 displaced delta-omega_c handler is wired (Phase C+1 commit). The
    finite-system reference uses a coherent displacement on the resonant
    bath mode while the QuTiP reference adds a time-dependent Lamb shift;
    both run to completion and return FAIL at the frozen 1.0e-6 threshold,
    consistent with the Markov-vs-exact mismatch."""
    card = _single_case_card(C1_PATH, "displaced_bath_delta_omega_c_cross_method")
    result = bc.run_card(card)
    assert result.verdict == "FAIL"
    assert result.runner_version == bc.__version__
    assert len(result.test_case_results) == 1
    tcr = result.test_case_results[0]
    assert tcr.name == "displaced_bath_delta_omega_c_cross_method"
    assert not tcr.passed
    assert tcr.error > card.threshold
    assert "delta-omega_c" in tcr.notes
    assert "Lamb shift" in tcr.notes


def test_run_card_c2_thermal_runs_to_clean_fail():
    """C2 thermal handler is wired (next-deferred commit). The σ_x finite
    reference and the σ_-/σ_+ secular Lindblad reference both run to
    completion and return FAIL at the frozen 1.0e-6 threshold, again
    consistent with the Markov-vs-exact mismatch."""
    card = _single_case_card(C2_PATH, "thermal_bath_cross_method")
    result = bc.run_card(card)
    assert result.verdict == "FAIL"
    assert result.runner_version == bc.__version__
    assert len(result.test_case_results) == 1
    tcr = result.test_case_results[0]
    assert tcr.name == "thermal_bath_cross_method"
    assert not tcr.passed
    assert tcr.error > card.threshold
    assert "σ_x" in tcr.notes or "sigma_x" in tcr.notes
    assert "σ_-" in tcr.notes or "sigma_-" in tcr.notes or "secular" in tcr.notes


def test_run_card_c2_displaced_runs_to_clean_fail():
    """C2 displaced delta-omega_c handler is wired (final C1+C2 deferred
    handler commit). The σ_x finite reference applies a coherent
    displacement to the resonant bath mode; the QuTiP reference combines
    σ_-/σ_+ secular Lindblad with a time-dependent σ_x drive ⟨B(t)⟩ σ_x.
    Both run to completion and return FAIL at the 1e-6 threshold."""
    card = _single_case_card(C2_PATH, "displaced_bath_delta_omega_c_cross_method")
    result = bc.run_card(card)
    assert result.verdict == "FAIL"
    assert result.runner_version == bc.__version__
    assert len(result.test_case_results) == 1
    tcr = result.test_case_results[0]
    assert tcr.name == "displaced_bath_delta_omega_c_cross_method"
    assert not tcr.passed
    assert tcr.error > card.threshold
    assert ("σ_x" in tcr.notes) or ("sigma_x" in tcr.notes)
    assert "delta-omega_c" in tcr.notes


def test_run_card_c2_full_card_reaches_verdict():
    """All four C1+C2 fixtures are now runner-reachable: C2 v0.1.0 runs
    both its test_cases without raising and returns an aggregate FAIL."""
    card = bc.load_card(C2_PATH)
    # Use a reduced grid to keep the finite-environment reference fast.
    card.frozen_parameters["numerical"]["time_grid"]["t_end"] = 5.0
    card.frozen_parameters["numerical"]["time_grid"]["n_points"] = 21
    result = bc.run_card(card)
    assert result.verdict == "FAIL"
    case_names = {tcr.name for tcr in result.test_case_results}
    assert case_names == {
        "thermal_bath_cross_method",
        "displaced_bath_delta_omega_c_cross_method",
    }


def test_cross_method_relative_frobenius_shape_mismatch_raises():
    a = np.zeros((2, 2, 2), dtype=complex)
    b = np.zeros((3, 2, 2), dtype=complex)
    with pytest.raises(ValueError, match="shape mismatch"):
        bc._inter_method_relative_frobenius(a, b)


# ─── Runner: refusal paths for D1 (DG-4) and E1 (scope-definition) ──────────


D1_PATH_FOR_RUN = CARDS_DIR / "D1_failure-envelope-convergence_v0.1.1.yaml"
E1_PATH_FOR_RUN = CARDS_DIR / "E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml"


def test_scope_definition_error_subclasses_not_implemented():
    """ScopeDefinitionNotRunnableError must be a NotImplementedError so
    callers that catch the broader exception still see scope-definition
    refusals."""
    assert issubclass(bc.ScopeDefinitionNotRunnableError, NotImplementedError)


def test_dg4_sweep_runner_error_subclasses_not_implemented():
    assert issubclass(bc.DG4SweepRunnerNotImplementedError, NotImplementedError)


def test_run_card_e1_raises_scope_definition_error():
    """run_card on a status='scope-definition' card raises a clean
    ScopeDefinitionNotRunnableError, not an opaque downstream error."""
    card = bc.load_card(E1_PATH_FOR_RUN)
    with pytest.raises(bc.ScopeDefinitionNotRunnableError) as exc_info:
        bc.run_card(card)
    msg = str(exc_info.value)
    # Message must name the card and surface the recorded preconditions.
    assert "E1" in msg
    assert "scope-definition" in msg
    # E1 carries a non-empty failure_mode_log entry; the message folds it in.
    assert "failure_mode_log" in msg or "result.notes" in msg


def _reduced_d1_v011_card(
    *,
    n_points_sweep: int = 4,
    t_end: float = 1.0,
    n_t: int = 11,
    alpha_values=(0.01, 0.02, 0.03),
    n_bath_modes: int = 2,
    n_levels_per_mode: int = 2,
) -> bc.BenchmarkCard:
    """Load D1 v0.1.1 with a reduced fixture for fast Phase C smoke tests.

    The frozen card targets n_bath_modes=4, n_levels=3, 20-point sweep.
    Production runs at full resolution take ~150s; tests override via the
    runner-side numerical.path_b extras block + a smaller sweep grid.
    """
    data = copy.deepcopy(_load_raw(D1_PATH_FOR_RUN))
    data["frozen_parameters"]["numerical"]["time_grid"]["t_end"] = t_end
    data["frozen_parameters"]["numerical"]["time_grid"]["n_points"] = n_t
    data["frozen_parameters"]["sweep"]["sweep_range"]["n_points"] = n_points_sweep
    data["frozen_parameters"]["numerical"]["path_b"] = {
        "alpha_values": list(alpha_values),
        "n_bath_modes": n_bath_modes,
        "n_levels_per_mode": n_levels_per_mode,
    }
    bc.validate_card_data(data)
    return bc._data_to_card(data)


def test_run_card_d1_runs_dg4_sweep_to_verdict():
    """Phase C of the DG-4 work plan v0.1.4: run_card on D1 v0.1.1
    routes through _run_dg4_sweep (no longer raises) and returns a
    CardResult with a structured DG-4 verdict.
    """
    card = _reduced_d1_v011_card()
    result = bc.run_card(card)
    assert result.card_id == "D1"
    assert result.verdict in {"PASS", "FAIL", "CONDITIONAL"}
    assert result.runner_version == bc.__version__
    assert len(result.test_case_results) == 1
    tcr = result.test_case_results[0]
    assert tcr.name == "dg4_failure_envelope_sweep"
    # Verdict-vs-passed parity: PASS iff the single test_case passed.
    assert tcr.passed == (result.verdict == "PASS")


def test_run_card_d1_dispatches_to_dg4_runner_not_dynamical():
    """D1 v0.1.1 has no test_cases (it carries a sweep block instead).
    If dispatch fell through to _run_dynamical, that would raise KeyError.
    The DG-4 branch must fire first."""
    card = _reduced_d1_v011_card()
    # If this raises KeyError, the DG-4 dispatch is broken.
    bc.run_card(card)


def test_run_card_d1_notes_record_path_b_floor_caveat():
    """Path B is benchmark-side numerical extraction with a documented
    finite-env floor; the verdict notes must call this out so verdicts
    carry the uncertainty band per DG-4 work plan v0.1.4 §3 Phase C."""
    card = _reduced_d1_v011_card()
    result = bc.run_card(card)
    assert "Path B" in result.notes
    assert "finite-env" in result.notes or "uncertainty" in result.notes


def test_run_card_d1_alpha_crit_interpolation_when_boundary_present():
    """When the sweep grid spans both passing (r_4 ≤ 1) and convergence-
    failure (r_4 > 1) regions, the runner reports an interpolated
    alpha_crit in result.notes."""
    card = _reduced_d1_v011_card()
    result = bc.run_card(card)
    if result.verdict == "PASS":
        assert "alpha_crit" in result.notes
    # FAIL or CONDITIONAL outcomes don't always have alpha_crit; only PASS
    # guarantees a boundary-interpolation entry.


def test_dg4_sweep_runner_refuses_non_sigma_x_with_clear_error():
    """The Path B helper currently supports only sigma_x + thermal. A DG-4
    card with a different coupling operator must raise the structured
    DG4SweepRunnerNotImplementedError, not silently produce a meaningless
    verdict."""
    card = _reduced_d1_v011_card()
    # Mutate the card in-memory to trigger the refusal branch.
    card.frozen_parameters["model"]["coupling_operator"] = "sigma_z"
    with pytest.raises(bc.DG4SweepRunnerNotImplementedError) as exc_info:
        bc.run_card(card)
    msg = str(exc_info.value)
    assert "sigma_x" in msg or "Path A" in msg


def test_dg4_sweep_runner_refuses_non_thermal_with_clear_error():
    """Path B Phase C wiring also requires thermal Gaussian; non-thermal
    bath states route to the structured deferral."""
    card = _reduced_d1_v011_card()
    card.frozen_parameters["model"]["bath_state"] = {
        "family": "coherent_displaced",
        "displacement_profile": "delta-omega_c",
        "parameters": {"alpha_0": 1.0, "omega_c": 10.0},
    }
    with pytest.raises(bc.DG4SweepRunnerNotImplementedError) as exc_info:
        bc.run_card(card)
    msg = str(exc_info.value)
    assert "thermal" in msg.lower()


def test_dg4_path_b_upper_cutoff_factor_is_operational():
    """v0.1.2 supersedure repair: the upper_cutoff_factor perturbation must
    now produce a non-trivial change in the Path B coefficients via the
    finite-env builder's omega_max_factor knob. A pure no-op (the v0.1.1
    bug) would give exactly equal baseline and perturbed coefficients,
    making the runner's "stable under all four perturbations" PASS
    predicate trivially satisfied. This test pins that the predicate is
    now genuinely tested."""
    card = _reduced_d1_v011_card()
    fp = card.frozen_parameters
    grid_times = bc.build_time_grid(fp["numerical"]["time_grid"]).times
    path_b_params = bc._resolve_path_b_params(fp)
    base_quad = bc._quadrature_kwargs(fp)
    base_model = bc._model_spec_for_dg4(fp)

    # Baseline run.
    baseline = bc._path_b_evaluate(base_model, grid_times, path_b_params, base_quad)

    # Perturb upper_cutoff_factor downward via _apply_dg4_perturbation.
    perturbation = {
        "name": "upper_cutoff_factor=20",
        "kind": "quadrature",
        "key": "upper_cutoff_factor",
        "value": 20.0,
    }
    perturbed_spec, perturbed_quad = bc._apply_dg4_perturbation(
        base_model, base_quad, perturbation
    )
    perturbed = bc._path_b_evaluate(perturbed_spec, grid_times, path_b_params, perturbed_quad)

    # The l_2 and l_4 coefficients must differ — a no-op perturbation would
    # give exactly equal floats. We require >= 1% relative deviation in at
    # least one of l2_avg / l4_avg, well above any expected numerical noise.
    base_l2, base_l4 = baseline.l2_avg, baseline.l4_avg
    pert_l2, pert_l4 = perturbed.l2_avg, perturbed.l4_avg
    rel_l2 = abs(pert_l2 - base_l2) / max(abs(base_l2), 1e-300)
    rel_l4 = abs(pert_l4 - base_l4) / max(abs(base_l4), 1e-300)
    assert max(rel_l2, rel_l4) > 1e-2, (
        "upper_cutoff_factor perturbation must produce a non-trivial change "
        "in Path B coefficients; got rel_l2={:.3e}, rel_l4={:.3e}".format(rel_l2, rel_l4)
    )


def test_run_card_e1_refusal_takes_precedence_over_model_factory():
    """E1's model 'fano_anderson' has no model factory; if the scope-
    definition refusal did not fire first, run_card would raise a generic
    NotImplementedError from the dynamical handler about the missing
    factory rather than the actionable preconditions."""
    card = bc.load_card(E1_PATH_FOR_RUN)
    with pytest.raises(bc.ScopeDefinitionNotRunnableError):
        bc.run_card(card)


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
        card_id=card.card_id,
        verdict="MAYBE",
        test_case_results=[],
        runner_version="0.1.0",
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
    a1_data["frozen_parameters"]["model"]["test_cases"].append(
        {
            "name": "made_up_test",
            "description": "not a real test",
            "expected_outcome": "unknown",
            "reference": "no paper",
        }
    )
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
    assert card.status == "pass"
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
    tcr = next(r for r in result.test_case_results if r.name == "pseudo_kraus_diagonal_sigma_z")
    assert tcr.error == 0.0


def test_run_card_b1_sigma_x_recovers_minus_half_sigma_x():
    """The σ_x analog is structurally identical to the σ_z fixture and
    must also pass at exactly zero error — confirms the implementation
    is not silently axis-biased."""
    card = bc.load_card(B1_PATH)
    result = bc.run_card(card)
    tcr = next(r for r in result.test_case_results if r.name == "pseudo_kraus_diagonal_sigma_x")
    assert tcr.error == 0.0


def test_run_card_b1_traceless_gives_zero_K():
    """All-traceless jumps (σ_x with γ=1, σ_y with γ=-1) give K = 0
    per transcription §5; HPTA holds exactly (σ_x² = σ_y² = I)."""
    card = bc.load_card(B1_PATH)
    result = bc.run_card(card)
    tcr = next(r for r in result.test_case_results if r.name == "pseudo_kraus_traceless_jumps")
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
    tcr = next(r for r in result.test_case_results if r.name == "pseudo_kraus_diagonal_sigma_z")
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


# ─── B2 off-diagonal pseudo-Kraus end-to-end ────────────────────────────────


def test_eval_complex_scalar_expression_parses_imaginary_param():
    """1j * beta with beta=0.5 evaluates to 0.5j."""
    val = bc._eval_complex_scalar_expression("1j * beta", {"beta": 0.5})
    assert val == 0.5j


def test_eval_complex_scalar_expression_parses_negation_and_conjugate_pair():
    """-1j * beta with beta=0.5 evaluates to -0.5j (the conjugate of 1j*beta)."""
    val = bc._eval_complex_scalar_expression("-1j * beta", {"beta": 0.5})
    assert val == -0.5j


def test_eval_complex_scalar_expression_handles_real_literal():
    val = bc._eval_complex_scalar_expression("1.0", {})
    assert val == complex(1.0)


def test_eval_complex_scalar_expression_rejects_operator_identifier():
    """The scalar parser must NOT have I / sigma_x in scope — those would
    be a category error in an omega entry."""
    with pytest.raises(ValueError, match="unknown identifier"):
        bc._eval_complex_scalar_expression("I", {})
    with pytest.raises(ValueError, match="unknown identifier"):
        bc._eval_complex_scalar_expression("sigma_z", {})


def test_eval_complex_scalar_expression_rejects_unknown_identifier():
    with pytest.raises(ValueError, match="unknown identifier"):
        bc._eval_complex_scalar_expression("missing_param", {})


def test_eval_complex_scalar_expression_rejects_attribute_access():
    with pytest.raises(ValueError, match="forbidden AST node|unknown identifier"):
        bc._eval_complex_scalar_expression("(1.0).real", {})


def test_eval_complex_scalar_expression_rejects_non_sqrt_call():
    with pytest.raises(ValueError, match="only calls to|unknown identifier"):
        bc._eval_complex_scalar_expression("exp(1)", {})


def test_parse_offdiag_omega_returns_hermitian_matrix_for_canonical_fixture():
    """The first B2 fixture's omega = [[1, iβ], [-iβ, -1]] is Hermitian
    (omega - omega^dagger == 0) for any real β."""
    omega = bc._parse_offdiag_omega([["1.0", "1j * beta"], ["-1j * beta", "-1.0"]], {"beta": 0.5})
    assert omega.shape == (2, 2)
    assert bc._hermiticity_residual(omega) == 0.0


def test_parse_offdiag_omega_rejects_non_square():
    with pytest.raises(ValueError, match="square matrix"):
        bc._parse_offdiag_omega([["1.0", "0.0"], ["0.0", "0.0", "0.0"]], {})


def test_hermiticity_residual_detects_non_hermitian_omega():
    """A real-asymmetric omega has non-zero Frobenius norm of omega - omega^dag."""
    omega = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=complex)
    res = bc._hermiticity_residual(omega)
    # ||omega - omega^T||_F = ||[[0, -1], [1, 0]]||_F = sqrt(2)
    assert res == pytest.approx(np.sqrt(2.0))


def test_load_card_b2_succeeds():
    card = bc.load_card(B2_PATH)
    assert card.card_id == "B2"
    assert card.dg_target == "DG-2"
    assert card.version == "v0.1.0"
    assert card.model_kind == "algebraic_map"


def test_run_card_b2_passes_all_three_test_cases():
    """Card B2 v0.1.0's three off-diagonal pseudo-Kraus test_cases all PASS
    at machine precision; both Hermiticity-of-omega and HPTA preconditions
    hold as algebraic identities (residual 0.0 exactly)."""
    card = bc.load_card(B2_PATH)
    result = bc.run_card(card)
    assert result.verdict == "PASS"
    assert len(result.test_case_results) == 3
    names = {r.name for r in result.test_case_results}
    assert names == {
        "offdiag_omega_imaginary_sigma_z",
        "offdiag_omega_imaginary_sigma_x",
        "offdiag_omega_diagonal_only",
    }
    for tcr in result.test_case_results:
        assert tcr.passed
        assert tcr.error <= card.threshold
        assert tcr.hpta_residual is not None
        assert tcr.hpta_threshold is not None
        assert tcr.hpta_residual <= tcr.hpta_threshold
        assert tcr.hermiticity_residual is not None
        assert tcr.hermiticity_threshold is not None
        assert tcr.hermiticity_residual <= tcr.hermiticity_threshold


def test_run_card_b2_sigma_z_recovers_beta_sigma_z():
    """The σ_z fixture (β=0.5) reproduces K = 0.5 σ_z at exactly zero error
    — algebraic tautology between matrix-unit basis sum and §4b H_HS^off-diag."""
    card = bc.load_card(B2_PATH)
    result = bc.run_card(card)
    tcr = next(r for r in result.test_case_results if r.name == "offdiag_omega_imaginary_sigma_z")
    assert tcr.error == 0.0


def test_run_card_b2_sigma_x_recovers_minus_beta_sigma_x():
    """The σ_x analog (β=0.5) reproduces K = -0.5 σ_x at exactly zero error
    — confirms the off-diagonal handler does not silently prefer σ_z."""
    card = bc.load_card(B2_PATH)
    result = bc.run_card(card)
    tcr = next(r for r in result.test_case_results if r.name == "offdiag_omega_imaginary_sigma_x")
    assert tcr.error == 0.0


def test_run_card_b2_diagonal_only_gives_zero_K():
    """omega = diag(1, -1) on (V_1=I, V_2=σ_z) collapses to K = 0 — the
    off-diagonal handler degenerates correctly when off-diagonal entries
    vanish."""
    card = bc.load_card(B2_PATH)
    result = bc.run_card(card)
    tcr = next(r for r in result.test_case_results if r.name == "offdiag_omega_diagonal_only")
    assert tcr.error == 0.0
    assert tcr.hpta_residual == 0.0
    assert tcr.hermiticity_residual == 0.0


def test_b2_test_case_handlers_all_registered():
    card = bc.load_card(B2_PATH)
    for case in card.frozen_parameters["model"]["test_cases"]:
        assert case["name"] in bc._TEST_CASE_HANDLERS


def test_run_card_b2_hermiticity_gate_short_circuits_on_violation():
    """A non-Hermitian omega triggers the Hermiticity precondition gate;
    HPTA and K comparison are skipped and the failure carries a diagnostic
    note plus the Hermiticity-residual fields."""
    raw = _load_raw(B2_PATH)
    case = raw["frozen_parameters"]["model"]["test_cases"][0]
    # Break Hermiticity by making omega_21 not the conjugate of omega_12.
    case["pseudo_kraus_offdiag_omega"] = [
        ["1.0", "1j * beta"],
        ["1j * beta", "-1.0"],  # should be -1j * beta to be Hermitian
    ]
    card = bc._data_to_card(raw)
    result = bc._run_algebraic_map(card)
    tcr = next(r for r in result.test_case_results if r.name == "offdiag_omega_imaginary_sigma_z")
    assert not tcr.passed
    assert tcr.hermiticity_residual is not None
    assert tcr.hermiticity_residual > tcr.hermiticity_threshold
    assert "Hermiticity precondition failed" in tcr.notes


def test_run_card_b2_hpta_gate_short_circuits_with_hermitian_omega_but_no_hpta():
    """A Hermitian omega that does NOT satisfy HPTA (sum_{ij} omega_{ij}
    V_j^dag V_i ≠ 0) triggers the HPTA gate after Hermiticity passes —
    confirming gate ordering and that a Hermitian-but-not-HPTA fixture is
    still rejected with a HPTA-specific diagnostic."""
    raw = _load_raw(B2_PATH)
    case = raw["frozen_parameters"]["model"]["test_cases"][0]
    # Replace omega with a Hermitian matrix that is NOT HPTA: diag(1, 1) on
    # (V_1=I, V_2=σ_z) gives sum = I + σ_z² = 2I ≠ 0.
    case["pseudo_kraus_offdiag_omega"] = [
        ["1.0", "0.0"],
        ["0.0", "1.0"],
    ]
    card = bc._data_to_card(raw)
    result = bc._run_algebraic_map(card)
    tcr = next(r for r in result.test_case_results if r.name == "offdiag_omega_imaginary_sigma_z")
    assert not tcr.passed
    # Hermiticity passed (diag is trivially Hermitian) — residual recorded.
    assert tcr.hermiticity_residual == 0.0
    # HPTA failed.
    assert tcr.hpta_residual is not None
    assert tcr.hpta_residual > tcr.hpta_threshold
    assert "HPTA precondition failed" in tcr.notes


# ─── B3 cross-basis structural identity end-to-end ───────────────────────────


def test_load_card_b3_succeeds():
    card = bc.load_card(B3_PATH)
    assert card.card_id == "B3"
    assert card.dg_target == "DG-2"
    assert card.version == "v0.1.0"
    assert card.status == "pass"
    assert card.model_kind == "algebraic_map"


def test_run_card_b3_passes_all_three_test_cases():
    """Card B3 v0.1.0's three cross-basis test_cases all PASS: K computed
    under the matrix-unit reference and under the su(d)-generator (normalized
    Pauli) basis agree to machine precision on each fixture."""
    card = bc.load_card(B3_PATH)
    result = bc.run_card(card)
    assert result.verdict == "PASS"
    assert len(result.test_case_results) == 3
    names = {r.name for r in result.test_case_results}
    assert names == {
        "basis_independence_pseudo_kraus_sigma_z",
        "basis_independence_lindblad_traceless",
        "basis_independence_lindblad_lamb_shift",
    }
    for tcr in result.test_case_results:
        assert tcr.passed
        assert tcr.error <= card.threshold
        # Cross-basis identity is exact in exact arithmetic; numerical
        # round-off is bounded by ~1e-15 for d=2.
        assert tcr.error < 1e-12


def test_run_card_b3_pseudo_kraus_carries_hpta_fields():
    """The pseudo-Kraus B3 case inherits B1's HPTA gate (algebraic identity);
    Lindblad-form B3 cases carry no HPTA residual."""
    card = bc.load_card(B3_PATH)
    result = bc.run_card(card)
    pk = next(
        r for r in result.test_case_results if r.name == "basis_independence_pseudo_kraus_sigma_z"
    )
    assert pk.hpta_residual is not None
    assert pk.hpta_threshold is not None
    assert pk.hpta_residual <= pk.hpta_threshold

    for name in ("basis_independence_lindblad_traceless", "basis_independence_lindblad_lamb_shift"):
        tcr = next(r for r in result.test_case_results if r.name == name)
        assert tcr.hpta_residual is None
        assert tcr.hpta_threshold is None


def test_b3_test_case_handlers_all_registered():
    """Every test_case name in Card B3 v0.1.0 has a registered handler."""
    card = bc.load_card(B3_PATH)
    for case in card.frozen_parameters["model"]["test_cases"]:
        assert case["name"] in bc._TEST_CASE_HANDLERS


def test_b3_basis_independence_handler_returns_none_K_expected():
    """B3 handlers must surface K_expected = None — the runner's signal to
    take the cross-basis comparison branch instead of comparing to a
    K-value reference."""
    card = bc.load_card(B3_PATH)
    d = card.system_dimension
    for case in card.frozen_parameters["model"]["test_cases"]:
        handler = bc._TEST_CASE_HANDLERS[case["name"]]
        L, K_expected, _hpta, _hermiticity = handler(case, d)
        assert callable(L)
        assert K_expected is None


def test_b3_unknown_comparison_basis_raises(monkeypatch=None):
    """A test_case requesting a comparison_basis with no registered builder
    surfaces a clear SchemaValidationError."""
    raw = _load_raw(B3_PATH)
    raw["frozen_parameters"]["model"]["test_cases"][0]["comparison_basis"] = "imaginary_basis"
    card = bc._data_to_card(raw)
    with pytest.raises(bc.SchemaValidationError, match="imaginary_basis"):
        bc._run_algebraic_map(card)


def test_b3_basis_builders_registry_contains_expected_keys():
    """Sanity check on the registry: matrix_unit + su_d_generator are wired."""
    assert "matrix_unit" in bc._BASIS_BUILDERS
    assert "su_d_generator" in bc._BASIS_BUILDERS


# ─── B4-conv-registry frozen-awaiting-run ────────────────────────────────────


def test_load_card_b4_succeeds():
    """Card B4-conv-registry v0.1.0 loads cleanly post-verdict."""
    card = bc.load_card(B4_PATH)
    assert card.card_id == "B4-conv-registry"
    assert card.dg_target == "DG-2"
    assert card.version == "v0.1.0"
    assert card.status == "pass"
    assert card.model == "pure_dephasing"
    assert card.model_kind == "dynamical"


def test_b4_test_cases_carry_displacement_profile_tags():
    """All four B4 test_cases tag a Council-cleared displacement profile."""
    card = bc.load_card(B4_PATH)
    cases = card.frozen_parameters["model"]["test_cases"]
    assert len(cases) == 4
    profile_keys = {case["bath_state"]["displacement_profile"] for case in cases}
    # The four Council-cleared keys at v0.1.0 (Act 2, 2026-05-04).
    assert profile_keys == {"delta-omega_c", "delta-omega_S", "sqrt-J", "gaussian"}


def test_b4_displacement_profile_keys_are_in_runner_registry():
    """Every B4 fixture's profile key must resolve in _DISPLACEMENT_PROFILES.

    Per the §6.1 registry-clearance-gate, this binds the card-level profile
    declarations to the runner-level cleared registry — a card cannot tag a
    profile that is not in the cleared set.
    """
    card = bc.load_card(B4_PATH)
    for case in card.frozen_parameters["model"]["test_cases"]:
        profile_key = case["bath_state"]["displacement_profile"]
        assert profile_key in bc._DISPLACEMENT_PROFILES, (
            f"Test case {case['name']!r} declares profile {profile_key!r} "
            f"which is not in the Council-cleared _DISPLACEMENT_PROFILES "
            f"registry. Known: {sorted(bc._DISPLACEMENT_PROFILES.keys())}"
        )


def test_run_card_b4_passes_all_four_profiles():
    """Post-verdict-commit: B4-conv-registry runs to PASS for all four
    Council-cleared profiles. Errors at machine precision because under
    σ_z coupling the parity-class theorem (Eq. (A.39)) makes K_2's σ_z
    contribution exactly zero, so the perturbative expansion at order
    ≤ N_card = 2 reduces to K_0 + K_1 = (ω/2 + D̄_1) σ_z, matching the
    predicted shift 2 D̄_1(t) exactly."""
    card = bc.load_card(B4_PATH)
    result = bc.run_card(card)
    assert result.verdict == "PASS"
    names = {tcr.name for tcr in result.test_case_results}
    assert names == {
        "displaced_bath_delta_omega_c",
        "displaced_bath_delta_omega_S",
        "displaced_bath_sqrt_J",
        "displaced_bath_gaussian",
    }
    for tcr in result.test_case_results:
        assert tcr.passed
        # All four profiles land at machine precision
        # (≤ 1e-12, well below the 1e-4 threshold).
        assert (
            tcr.error < 1e-12
        ), f"{tcr.name}: expected machine-precision error; got {tcr.error:.3e}"


def test_displacement_profiles_registry_has_act2_cleared_keys():
    """Sanity check on the runner-level registry: exactly the four Council
    Act 2 cleared keys at v0.1.0 (subsidiary briefing v0.3.0 §3.1–§3.4)."""
    assert set(bc._DISPLACEMENT_PROFILES.keys()) == {
        "delta-omega_c",
        "delta-omega_S",
        "sqrt-J",
        "gaussian",
    }


# ─── B5-conv-registry frozen-awaiting-run (σ_x sibling) ──────────────────────


def test_load_card_b5_succeeds():
    """Card B5-conv-registry v0.2.0 loads cleanly post-verdict
    (the v0.1.0 predecessor was superseded same-day for a card-design
    prediction-text correction)."""
    card = bc.load_card(B5_PATH)
    assert card.card_id == "B5-conv-registry"
    assert card.dg_target == "DG-2"
    assert card.version == "v0.2.0"
    assert card.status == "pass"
    assert card.model == "spin_boson_sigma_x"
    assert card.model_kind == "dynamical"
    assert card.supersedes == "B5-conv-registry_v0.1.0.yaml"


def test_load_card_b5_v010_superseded():
    """The v0.1.0 predecessor is retained at HEAD with status: superseded
    per SCHEMA.md §Card lifecycle."""
    card = bc.load_card(B5_V010_PATH)
    assert card.status == "superseded"
    assert card.superseded_by == "B5-conv-registry_v0.2.0.yaml"


def test_b5_test_cases_carry_same_registry_profiles_as_b4():
    """B5 must tag the SAME four cleared profiles as B4 (same Council-cleared
    registry; the σ_x sibling shares the registry surface)."""
    b4 = bc.load_card(B4_PATH)
    b5 = bc.load_card(B5_PATH)
    b4_profiles = {
        c["bath_state"]["displacement_profile"] for c in b4.frozen_parameters["model"]["test_cases"]
    }
    b5_profiles = {
        c["bath_state"]["displacement_profile"] for c in b5.frozen_parameters["model"]["test_cases"]
    }
    assert b4_profiles == b5_profiles


def test_run_card_b5_passes_all_four_profiles():
    """Post-verdict-commit: B5-conv-registry v0.2.0 runs to PASS for all
    four Council-cleared profiles. Errors at 0.0 exactly because the
    same D̄_1 array drives both the runner's K_1 computation and the
    predicted σ_x channel (single source of truth), so b_actual - b_pred
    = 0 floating-point-exactly; the σ_y channel is zero by the parity-
    class theorem of Eq. (A.43)-(A.45)."""
    card = bc.load_card(B5_PATH)
    result = bc.run_card(card)
    assert result.verdict == "PASS"
    names = {tcr.name for tcr in result.test_case_results}
    assert names == {
        "displaced_bath_delta_omega_c",
        "displaced_bath_delta_omega_S",
        "displaced_bath_sqrt_J",
        "displaced_bath_gaussian",
    }
    for tcr in result.test_case_results:
        assert tcr.passed
        assert (
            tcr.error == 0.0
        ), f"{tcr.name}: expected exact-zero structural error; got {tcr.error:.3e}"

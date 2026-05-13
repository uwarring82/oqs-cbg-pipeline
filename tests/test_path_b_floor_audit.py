# SPDX-License-Identifier: MIT
"""Tests for the DG-4 Phase E Track 5.C Path B floor-audit driver.

These tests exercise the gate-wiring of ``benchmarks.path_b_floor_audit``
(grid generation, preflight skip, summary computation, JSON writer).

The §5.1 smoke test from the frozen 5.C card v0.1.0 runs the
``(n_bath_modes=4, n_levels_per_mode=3, omega_max_factor=10)`` corner
through the Path B Richardson fit on a reduced grid (smaller time grid
and a 3-point alpha grid) so the test completes in seconds. Production
runs of the full audit use the production grids and are out of scope
for this commit.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from benchmarks import path_b_floor_audit as pbfa


def test_iter_audit_grid_yields_one_axis_at_a_time_topology():
    """Grid is anchor + 5 omega_max sweep + 2 n_bath + 2 n_levels = 10 points."""
    configs = list(pbfa.iter_audit_grid())
    assert len(configs) == 10

    anchor = configs[0]
    assert anchor.axis == "anchor"
    assert anchor.n_bath_modes == pbfa.ANCHOR_N_BATH_MODES
    assert anchor.n_levels_per_mode == pbfa.ANCHOR_N_LEVELS_PER_MODE
    assert anchor.omega_max_factor == pbfa.ANCHOR_OMEGA_MAX_FACTOR

    axes = [c.axis for c in configs]
    assert axes.count("anchor") == 1
    assert axes.count("omega_max_factor") == 5
    assert axes.count("n_bath_modes") == 2
    assert axes.count("n_levels_per_mode") == 2

    for cfg in configs:
        if cfg.axis == "omega_max_factor":
            assert cfg.n_bath_modes == pbfa.ANCHOR_N_BATH_MODES
            assert cfg.n_levels_per_mode == pbfa.ANCHOR_N_LEVELS_PER_MODE
            assert cfg.omega_max_factor != pbfa.ANCHOR_OMEGA_MAX_FACTOR
        elif cfg.axis == "n_bath_modes":
            assert cfg.n_levels_per_mode == pbfa.ANCHOR_N_LEVELS_PER_MODE
            assert cfg.omega_max_factor == pbfa.ANCHOR_OMEGA_MAX_FACTOR
            assert cfg.n_bath_modes != pbfa.ANCHOR_N_BATH_MODES
        elif cfg.axis == "n_levels_per_mode":
            assert cfg.n_bath_modes == pbfa.ANCHOR_N_BATH_MODES
            assert cfg.omega_max_factor == pbfa.ANCHOR_OMEGA_MAX_FACTOR
            assert cfg.n_levels_per_mode != pbfa.ANCHOR_N_LEVELS_PER_MODE


def test_predict_wall_time_seconds_scales_cubically_with_d_joint():
    anchor = pbfa.TruncationConfig(
        n_bath_modes=pbfa.ANCHOR_N_BATH_MODES,
        n_levels_per_mode=pbfa.ANCHOR_N_LEVELS_PER_MODE,
        omega_max_factor=pbfa.ANCHOR_OMEGA_MAX_FACTOR,
        axis="anchor",
    )
    bigger = pbfa.TruncationConfig(
        n_bath_modes=pbfa.ANCHOR_N_BATH_MODES,
        n_levels_per_mode=4,
        omega_max_factor=pbfa.ANCHOR_OMEGA_MAX_FACTOR,
        axis="n_levels_per_mode",
    )
    # d_joint goes 162 -> 512 → ratio (512/162)**3 ≈ 31.5×.
    ratio = pbfa.predict_wall_time_seconds(bigger) / pbfa.predict_wall_time_seconds(anchor)
    expected = (bigger.d_joint / anchor.d_joint) ** 3
    assert ratio == pytest.approx(expected, rel=1e-9)


def test_run_audit_skips_intractable_points_via_preflight(tmp_path: Path):
    """A budget of 1 s forces preflight skip for non-anchor (4, 3) cases too."""
    audit = pbfa.run_audit(
        per_point_budget_seconds=0.001,
        preflight_factor=1.0,
        output_path=tmp_path / "audit.json",
        dry_run=True,
    )
    # Every point is preflight-skipped (anchor's 60 s prediction > 0.001 budget).
    skipped = [p for p in audit["points"] if p["status"] == "skipped-preflight"]
    assert len(skipped) == len(audit["points"])
    assert audit["summary"]["anchor_status"] == "skipped-preflight"
    assert audit["summary"]["cause_label_eligible"] is False


def test_write_audit_json_round_trips(tmp_path: Path):
    """Writer serialises non-degraded audit dict to disk; reads back equal."""
    out = tmp_path / "subdir" / "audit.json"
    payload = {
        "schema": "D1_path-b-floor-audit_v0.1.0",
        "card_version": "v0.1.0",
        "points": [],
        "summary": {"cause_label_eligible": False},
    }
    pbfa.write_audit_json(payload, out)
    assert out.exists()
    assert json.loads(out.read_text(encoding="utf-8")) == payload


def test_summary_flags_missing_hilbert_witness_when_only_omega_sweep_runs():
    """truncation-converged requires at least one Hilbert-axis evaluated point."""
    cfg_anchor = pbfa.TruncationConfig(
        n_bath_modes=4, n_levels_per_mode=3, omega_max_factor=30.0, axis="anchor"
    )
    cfg_omega = pbfa.TruncationConfig(
        n_bath_modes=4, n_levels_per_mode=3, omega_max_factor=10.0, axis="omega_max_factor"
    )
    anchor_point = pbfa.FloorAuditPoint(
        config=cfg_anchor,
        status="evaluated",
        l2_avg=10.0,
        l4_avg=470.0,
        coefficient_ratio=47.0,
        fit_relative_residual=1e-6,
        r_4_ladder={"alpha_sq_0.05": 2.35, "alpha_sq_0.5": 23.5, "alpha_sq_1": 47.0},
        wall_time_seconds=1.0,
        predicted_wall_time_seconds=1.0,
        skip_reason=None,
        error=None,
    )
    omega_point = pbfa.FloorAuditPoint(
        config=cfg_omega,
        status="evaluated",
        l2_avg=10.0,
        l4_avg=475.0,
        coefficient_ratio=47.5,
        fit_relative_residual=1e-6,
        r_4_ladder={"alpha_sq_0.05": 2.375, "alpha_sq_0.5": 23.75, "alpha_sq_1": 47.5},
        wall_time_seconds=1.0,
        predicted_wall_time_seconds=1.0,
        skip_reason=None,
        error=None,
    )
    summary = pbfa._compute_summary([anchor_point, omega_point])
    assert summary["evaluated_count"] == 2
    assert summary["hilbert_witness_count"] == 0
    assert summary["cause_label_eligible"] is False
    # Drift = |47.5 - 47.0| / 47.0 ≈ 1.06%.
    assert summary["max_drift"] == pytest.approx(0.5 / 47.0, rel=1e-9)


def test_summary_recognises_hilbert_witness():
    """A non-degraded n_levels_per_mode point flips cause_label_eligible to True."""
    cfg_anchor = pbfa.TruncationConfig(
        n_bath_modes=4, n_levels_per_mode=3, omega_max_factor=30.0, axis="anchor"
    )
    cfg_hilbert = pbfa.TruncationConfig(
        n_bath_modes=4, n_levels_per_mode=4, omega_max_factor=30.0, axis="n_levels_per_mode"
    )
    anchor_point = pbfa.FloorAuditPoint(
        config=cfg_anchor,
        status="evaluated",
        l2_avg=10.0,
        l4_avg=470.0,
        coefficient_ratio=47.0,
        fit_relative_residual=1e-6,
        r_4_ladder={},
        wall_time_seconds=1.0,
        predicted_wall_time_seconds=1.0,
        skip_reason=None,
        error=None,
    )
    hilbert_point = pbfa.FloorAuditPoint(
        config=cfg_hilbert,
        status="evaluated",
        l2_avg=10.0,
        l4_avg=460.0,
        coefficient_ratio=46.0,
        fit_relative_residual=1e-6,
        r_4_ladder={},
        wall_time_seconds=1.0,
        predicted_wall_time_seconds=1.0,
        skip_reason=None,
        error=None,
    )
    summary = pbfa._compute_summary([anchor_point, hilbert_point])
    assert summary["hilbert_witness_count"] == 1
    assert summary["cause_label_eligible"] is True


def test_smoke_evaluate_point_at_card_section_5_1_corner():
    """§5.1 acceptance smoke test: (4, 3, omega_max_factor=10) corner is runnable.

    Uses a reduced time grid (21 points) and a 3-point alpha grid for
    test speed; the production audit uses ``D1_T_GRID`` (200 points) and
    ``PRODUCTION_ALPHA_VALUES`` (5 points). The smoke gate's only job is
    to prove the gate-wiring works end-to-end against the Path B API.
    """
    cfg = pbfa.TruncationConfig(
        n_bath_modes=4,
        n_levels_per_mode=3,
        omega_max_factor=10.0,
        axis="omega_max_factor",
    )
    point = pbfa.evaluate_point(
        cfg,
        t_grid=np.linspace(0.0, 5.0, 21),
        alpha_values=(0.01, 0.02, 0.03),
    )
    assert point.status in (
        "evaluated",
        "fit-degraded",
    ), f"smoke point failed: status={point.status}, error={point.error}"
    assert point.coefficient_ratio is not None
    assert np.isfinite(point.coefficient_ratio)
    assert point.l2_avg is not None and point.l2_avg > 0.0
    assert point.l4_avg is not None and point.l4_avg >= 0.0
    assert point.r_4_ladder is not None
    assert set(point.r_4_ladder.keys()) == {
        f"alpha_sq_{a2:g}" for a2 in pbfa.R_4_LADDER_ALPHA_SQUARED
    }

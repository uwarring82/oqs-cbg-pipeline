# SPDX-License-Identifier: MIT
"""benchmarks.path_b_floor_audit -- DG-4 Phase E Track 5.C audit driver.

Drives the Path B finite-environment extraction floor audit at the D1
v0.1.2 sigma_x thermal fixture, anchored at the production configuration
``(n_bath_modes=4, n_levels_per_mode=3, omega_max_factor=30)``.

One-axis-at-a-time topology per the frozen 5.C card v0.1.0 §3.1:
    - omega_max_factor sweep in {10, 20, 30, 40, 80, 160} at the (4, 3) anchor;
    - n_bath_modes sweep in {6, 8} at (n_levels_per_mode=3, omega_max_factor=30);
    - n_levels_per_mode sweep in {4, 5} at (n_bath_modes=4, omega_max_factor=30).

Each truncation point is one Richardson fit at the production alpha grid
``(0.01, 0.015, 0.02, 0.025, 0.03)`` yielding one alpha-independent
``coefficient_ratio = <||L_4^dis||> / <||L_2^dis||>``. The per-alpha
metric ``r_4(alpha**2) = alpha**2 * coefficient_ratio`` is reported at
``alpha**2 in {0.05, 0.5, 1.0}`` as a derived ladder at no extra compute
cost.

Per-point compute budget + d_joint-based preflight skip per the card's
R1 risk mitigation. A hard process timeout for points that beat the
preflight estimator is not implemented in this commit; it will land in
the production-run commit (see card §6 R1).

This module does not modify cbg/ or the production runner; it calls
``benchmarks.numerical_tcl_extraction.path_b_dissipator_norm_coefficients``
directly with explicit truncation kwargs. The result JSON path is
``benchmarks/results/D1_path-b-floor-audit_v0.1.0_result.json``.
"""

from __future__ import annotations

import argparse
import json
import time
from collections.abc import Iterator, Sequence
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np

from benchmarks import exact_finite_env, numerical_tcl_extraction
from models import spin_boson_sigma_x

# ─── Frozen audit configuration (5.C card v0.1.0 §3.1) ──────────────────────

ANCHOR_N_BATH_MODES = 4
ANCHOR_N_LEVELS_PER_MODE = 3
ANCHOR_OMEGA_MAX_FACTOR = 30.0

OMEGA_MAX_FACTOR_SWEEP: tuple[float, ...] = (10.0, 20.0, 30.0, 40.0, 80.0, 160.0)
N_BATH_MODES_SWEEP: tuple[int, ...] = (4, 6, 8)
N_LEVELS_PER_MODE_SWEEP: tuple[int, ...] = (3, 4, 5)

PRODUCTION_ALPHA_VALUES: tuple[float, ...] = (0.01, 0.015, 0.02, 0.025, 0.03)
R_4_LADDER_ALPHA_SQUARED: tuple[float, ...] = (0.05, 0.5, 1.0)
FIT_RESIDUAL_DEGRADED_THRESHOLD = 1.0e-3

D1_FIXTURE_MODEL_SPEC: dict[str, Any] = {
    "model_kind": "dynamical",
    "system_dimension": 2,
    "system_hamiltonian": "(omega / 2) * sigma_z",
    "coupling_operator": "sigma_x",
    "bath_type": "bosonic_linear",
    "bath_spectral_density": {
        "family": "ohmic",
        "cutoff_frequency": 10.0,
        # coupling_strength is set per-alpha by the Path B fit; the spec value
        # here is irrelevant to the alpha-power expansion's extracted coefficients.
        "coupling_strength": 0.0,
    },
    "bath_state": {
        "family": "thermal",
        "temperature": 0.5,
    },
    "omega": 1.0,
}

D1_T_GRID: np.ndarray = np.linspace(0.0, 20.0, 200)

RESULT_JSON_PATH: Path = (
    Path(__file__).resolve().parent / "results" / "D1_path-b-floor-audit_v0.1.0_result.json"
)

PER_POINT_BUDGET_SECONDS_DEFAULT = 30.0 * 60.0

# Anchor-calibrated d_joint^3 wall-time scaling. Anchor (4, 3) has
# d_joint = 162; production runner data shows a single Richardson fit
# completes in roughly tens of seconds on developer hardware. We calibrate
# pessimistically (60 s at anchor) so the preflight skip is conservative.
PREFLIGHT_ANCHOR_SECONDS = 60.0
PREFLIGHT_ANCHOR_D_JOINT = 2 * ANCHOR_N_LEVELS_PER_MODE**ANCHOR_N_BATH_MODES


PointStatus = Literal[
    "evaluated",
    "fit-degraded",
    "skipped-preflight",
    "errored",
]


@dataclass(frozen=True)
class TruncationConfig:
    n_bath_modes: int
    n_levels_per_mode: int
    omega_max_factor: float
    axis: str  # "anchor" | "omega_max_factor" | "n_bath_modes" | "n_levels_per_mode"

    @property
    def d_joint(self) -> int:
        return 2 * self.n_levels_per_mode**self.n_bath_modes


@dataclass
class FloorAuditPoint:
    config: TruncationConfig
    status: PointStatus
    l2_avg: float | None
    l4_avg: float | None
    coefficient_ratio: float | None
    fit_relative_residual: float | None
    r_4_ladder: dict[str, float] | None
    wall_time_seconds: float
    predicted_wall_time_seconds: float
    skip_reason: str | None
    error: str | None


def predict_wall_time_seconds(config: TruncationConfig) -> float:
    """Preflight wall-time estimator from ``d_joint``.

    Anchor-calibrated cubic scaling. The propagation step inside
    ``exact_finite_env`` is matrix-exp-dominated, so wall time grows
    roughly as ``d_joint**3`` times the number of forward simulations
    (``n_alpha * n_basis``). We hold the alpha grid and basis size fixed
    at production values so the only varying factor here is ``d_joint``.

    The estimate is intentionally conservative; the audit's R1 mitigation
    pairs this preflight with a hard process timeout (production-run
    commit) to catch points that beat the prediction but still exceed
    budget.
    """
    return PREFLIGHT_ANCHOR_SECONDS * (config.d_joint / PREFLIGHT_ANCHOR_D_JOINT) ** 3


def iter_audit_grid() -> Iterator[TruncationConfig]:
    """Yield the one-axis-at-a-time audit points in §3.1 order."""
    yield TruncationConfig(
        n_bath_modes=ANCHOR_N_BATH_MODES,
        n_levels_per_mode=ANCHOR_N_LEVELS_PER_MODE,
        omega_max_factor=ANCHOR_OMEGA_MAX_FACTOR,
        axis="anchor",
    )
    for omf in OMEGA_MAX_FACTOR_SWEEP:
        if omf == ANCHOR_OMEGA_MAX_FACTOR:
            continue
        yield TruncationConfig(
            n_bath_modes=ANCHOR_N_BATH_MODES,
            n_levels_per_mode=ANCHOR_N_LEVELS_PER_MODE,
            omega_max_factor=omf,
            axis="omega_max_factor",
        )
    for nbm in N_BATH_MODES_SWEEP:
        if nbm == ANCHOR_N_BATH_MODES:
            continue
        yield TruncationConfig(
            n_bath_modes=nbm,
            n_levels_per_mode=ANCHOR_N_LEVELS_PER_MODE,
            omega_max_factor=ANCHOR_OMEGA_MAX_FACTOR,
            axis="n_bath_modes",
        )
    for nlpm in N_LEVELS_PER_MODE_SWEEP:
        if nlpm == ANCHOR_N_LEVELS_PER_MODE:
            continue
        yield TruncationConfig(
            n_bath_modes=ANCHOR_N_BATH_MODES,
            n_levels_per_mode=nlpm,
            omega_max_factor=ANCHOR_OMEGA_MAX_FACTOR,
            axis="n_levels_per_mode",
        )


def evaluate_point(
    config: TruncationConfig,
    *,
    t_grid: np.ndarray | None = None,
    alpha_values: Sequence[float] | None = None,
) -> FloorAuditPoint:
    """Run one Richardson fit at the given truncation config.

    No timeout enforcement; the caller (``run_audit``) is responsible for
    preflight skip. The function never raises on Path-B numerical failure
    — errors are captured in ``FloorAuditPoint.error`` with status
    ``errored``.

    Parameters
    ----------
    config:
        Truncation knobs threaded into ``exact_finite_env`` via
        ``builder_kwargs``.
    t_grid:
        Time grid. Defaults to the D1 v0.1.2 production grid
        ``linspace(0, 20, 200)``.
    alpha_values:
        Richardson fit alpha grid. Defaults to the production tuple
        ``(0.01, 0.015, 0.02, 0.025, 0.03)``. Tests pass a reduced grid
        to keep the smoke run cheap.
    """
    if t_grid is None:
        t_grid = D1_T_GRID
    if alpha_values is None:
        alpha_values = PRODUCTION_ALPHA_VALUES

    predicted = predict_wall_time_seconds(config)
    spec = deepcopy(D1_FIXTURE_MODEL_SPEC)
    H_S, _A = spin_boson_sigma_x.system_arrays_from_spec(spec)

    t0 = time.perf_counter()
    try:
        result = numerical_tcl_extraction.path_b_dissipator_norm_coefficients(
            exact_finite_env.build_spin_boson_sigma_x_thermal_total,
            spec,
            list(map(float, t_grid)),
            list(alpha_values),
            builder_kwargs={
                "n_bath_modes": config.n_bath_modes,
                "n_levels_per_mode": config.n_levels_per_mode,
                "omega_max_factor": config.omega_max_factor,
            },
            system_hamiltonian=H_S,
        )
    except Exception as exc:  # noqa: BLE001 — surface any Path-B failure as a logged audit row
        return FloorAuditPoint(
            config=config,
            status="errored",
            l2_avg=None,
            l4_avg=None,
            coefficient_ratio=None,
            fit_relative_residual=None,
            r_4_ladder=None,
            wall_time_seconds=time.perf_counter() - t0,
            predicted_wall_time_seconds=predicted,
            skip_reason=None,
            error=f"{type(exc).__name__}: {exc}",
        )
    wall = time.perf_counter() - t0

    l2_avg = float(result.l2_avg)
    l4_avg = float(result.l4_avg)
    coefficient_ratio = l4_avg / l2_avg if l2_avg != 0.0 else float("nan")
    r_4_ladder = {
        f"alpha_sq_{a2:g}": float(a2 * coefficient_ratio) for a2 in R_4_LADDER_ALPHA_SQUARED
    }
    fit_resid = float(result.fit_relative_residual)
    status: PointStatus = (
        "fit-degraded" if fit_resid > FIT_RESIDUAL_DEGRADED_THRESHOLD else "evaluated"
    )
    return FloorAuditPoint(
        config=config,
        status=status,
        l2_avg=l2_avg,
        l4_avg=l4_avg,
        coefficient_ratio=float(coefficient_ratio),
        fit_relative_residual=fit_resid,
        r_4_ladder=r_4_ladder,
        wall_time_seconds=wall,
        predicted_wall_time_seconds=predicted,
        skip_reason=None,
        error=None,
    )


def run_audit(
    *,
    per_point_budget_seconds: float = PER_POINT_BUDGET_SECONDS_DEFAULT,
    preflight_factor: float = 2.0,
    t_grid: np.ndarray | None = None,
    alpha_values: Sequence[float] | None = None,
    output_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run the one-axis-at-a-time audit and return the result dict.

    Each point is preflight-checked against ``predict_wall_time_seconds``:
    if the prediction exceeds ``per_point_budget_seconds *
    preflight_factor`` the point is recorded with status
    ``skipped-preflight`` and not dispatched. Points that beat the
    preflight may still exceed the budget; the production-run commit
    wraps ``evaluate_point`` in a child-process timeout for that case.

    Parameters
    ----------
    per_point_budget_seconds:
        Hard wall-time budget per point (default 30 min; card §6 R1).
    preflight_factor:
        Predicted wall time > ``per_point_budget_seconds * preflight_factor``
        triggers a preflight skip. Default 2.0 — allows the prediction to
        be off by 2× before skipping.
    t_grid, alpha_values:
        Forwarded to ``evaluate_point``. Defaults are the production
        D1 v0.1.2 grids.
    output_path:
        Where to write the JSON artefact. Defaults to
        ``RESULT_JSON_PATH``.
    dry_run:
        If True, return the audit dict without writing.
    """
    if output_path is None:
        output_path = RESULT_JSON_PATH

    points: list[FloorAuditPoint] = []
    started_at = time.time()

    for config in iter_audit_grid():
        predicted = predict_wall_time_seconds(config)
        if predicted > per_point_budget_seconds * preflight_factor:
            points.append(
                FloorAuditPoint(
                    config=config,
                    status="skipped-preflight",
                    l2_avg=None,
                    l4_avg=None,
                    coefficient_ratio=None,
                    fit_relative_residual=None,
                    r_4_ladder=None,
                    wall_time_seconds=0.0,
                    predicted_wall_time_seconds=predicted,
                    skip_reason=(
                        f"predicted {predicted:.1f}s > budget*{preflight_factor} "
                        f"= {per_point_budget_seconds * preflight_factor:.1f}s"
                    ),
                    error=None,
                )
            )
            continue
        points.append(evaluate_point(config, t_grid=t_grid, alpha_values=alpha_values))

    summary = _compute_summary(points)
    audit: dict[str, Any] = {
        "schema": "D1_path-b-floor-audit_v0.1.0",
        "card_id": "cbg-companion-sec-iv-l4-phase-e-5c-path-b-floor-audit-card",
        "card_version": "v0.1.0",
        "fixture": {
            "card_anchor": "D1 v0.1.2",
            "model_spec": D1_FIXTURE_MODEL_SPEC,
            "t_grid": (
                {
                    "t_start": float(D1_T_GRID[0]),
                    "t_end": float(D1_T_GRID[-1]),
                    "n_points": int(D1_T_GRID.size),
                    "scheme": "uniform",
                }
                if t_grid is None
                else {"custom": True, "n_points": int(np.asarray(t_grid).size)}
            ),
            "alpha_values": (
                list(alpha_values) if alpha_values is not None else list(PRODUCTION_ALPHA_VALUES)
            ),
            "r_4_ladder_alpha_squared": list(R_4_LADDER_ALPHA_SQUARED),
        },
        "anchor": {
            "n_bath_modes": ANCHOR_N_BATH_MODES,
            "n_levels_per_mode": ANCHOR_N_LEVELS_PER_MODE,
            "omega_max_factor": ANCHOR_OMEGA_MAX_FACTOR,
        },
        "per_point_budget_seconds": per_point_budget_seconds,
        "preflight_factor": preflight_factor,
        "fit_residual_degraded_threshold": FIT_RESIDUAL_DEGRADED_THRESHOLD,
        "started_at_unix": started_at,
        "ended_at_unix": time.time(),
        "points": [_serialise_point(p) for p in points],
        "summary": summary,
    }

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_audit_json(audit, output_path)

    return audit


def _serialise_point(p: FloorAuditPoint) -> dict[str, Any]:
    payload = asdict(p)
    payload["config"]["d_joint"] = p.config.d_joint
    return payload


def write_audit_json(audit: dict[str, Any], path: Path) -> None:
    """Serialise the audit dict to ``path`` as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(audit, fh, indent=2, sort_keys=False)
        fh.write("\n")


def _compute_summary(points: list[FloorAuditPoint]) -> dict[str, Any]:
    """Compute drift maximum and cause-label eligibility.

    Drift is defined in card §4.3 as the relative change in the
    alpha-independent ``coefficient_ratio`` between the production
    anchor and each non-degraded evaluated audit point. Degraded
    (``fit-degraded``) and skipped points are excluded.
    """
    by_axis: dict[str, list[FloorAuditPoint]] = {}
    for p in points:
        by_axis.setdefault(p.config.axis, []).append(p)
    anchor_points = by_axis.get("anchor", [])
    if not anchor_points or anchor_points[0].status != "evaluated":
        return {
            "anchor_status": anchor_points[0].status if anchor_points else "missing",
            "anchor_coefficient_ratio": None,
            "max_drift": None,
            "max_drift_config": None,
            "evaluated_count": sum(1 for p in points if p.status == "evaluated"),
            "fit_degraded_count": sum(1 for p in points if p.status == "fit-degraded"),
            "skipped_preflight_count": sum(1 for p in points if p.status == "skipped-preflight"),
            "errored_count": sum(1 for p in points if p.status == "errored"),
            "hilbert_witness_count": 0,
            "cause_label_eligible": False,
            "notes": "anchor point not evaluated; no cause label is issuable",
        }
    anchor = anchor_points[0]
    assert anchor.coefficient_ratio is not None
    non_degraded_non_anchor = [
        p for p in points if p.status == "evaluated" and p.config.axis != "anchor"
    ]
    drifts: list[tuple[float, FloorAuditPoint]] = []
    for p in non_degraded_non_anchor:
        assert p.coefficient_ratio is not None
        drift = abs(p.coefficient_ratio - anchor.coefficient_ratio) / abs(anchor.coefficient_ratio)
        drifts.append((drift, p))

    max_drift_config: dict[str, Any] | None
    if drifts:
        max_drift, max_point = max(drifts, key=lambda x: x[0])
        max_drift_config = asdict(max_point.config)
        max_drift_config["d_joint"] = max_point.config.d_joint
    else:
        max_drift = 0.0
        max_drift_config = None

    hilbert_witness_count = sum(
        1 for p in non_degraded_non_anchor if p.config.axis in ("n_bath_modes", "n_levels_per_mode")
    )

    return {
        "anchor_status": "evaluated",
        "anchor_coefficient_ratio": anchor.coefficient_ratio,
        "max_drift": max_drift if drifts else None,
        "max_drift_config": max_drift_config,
        "evaluated_count": sum(1 for p in points if p.status == "evaluated"),
        "fit_degraded_count": sum(1 for p in points if p.status == "fit-degraded"),
        "skipped_preflight_count": sum(1 for p in points if p.status == "skipped-preflight"),
        "errored_count": sum(1 for p in points if p.status == "errored"),
        "hilbert_witness_count": hilbert_witness_count,
        "cause_label_eligible": hilbert_witness_count >= 1,
        "notes": (
            "Cause label per card §4.3 is the steward's call from this table; "
            "the driver does not auto-classify. The Hilbert-tightening witness "
            "requirement (§5.3) is satisfied iff hilbert_witness_count >= 1."
        ),
    }


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "DG-4 Phase E Track 5.C Path B floor audit driver. Runs the one-axis-"
            "at-a-time truncation grid against the D1 v0.1.2 sigma_x thermal "
            "fixture and writes the audit JSON."
        )
    )
    parser.add_argument(
        "--budget-seconds",
        type=float,
        default=PER_POINT_BUDGET_SECONDS_DEFAULT,
        help="per-point wall-time budget (default: 1800 s = 30 min)",
    )
    parser.add_argument(
        "--preflight-factor",
        type=float,
        default=2.0,
        help="preflight skip if predicted > budget * this factor (default: 2.0)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULT_JSON_PATH,
        help=f"output JSON path (default: {RESULT_JSON_PATH})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="run the grid but do not write the JSON artefact",
    )
    args = parser.parse_args()
    audit = run_audit(
        per_point_budget_seconds=args.budget_seconds,
        preflight_factor=args.preflight_factor,
        output_path=args.output,
        dry_run=args.dry_run,
    )
    print(json.dumps(audit["summary"], indent=2))


if __name__ == "__main__":
    _cli()

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

# Anchor-calibrated wall-time scaling. Anchor (4, 3) has d_joint = 162;
# a direct evaluate_point() call at the anchor on production grids
# completes in ~6.8 s on developer hardware (M-class laptop, 2026-05-13);
# (4, 4) at d_joint = 512 completes in ~73.6 s. Fitting these two points
# to a power law gives ``exponent = log(73.6/6.8) / log(512/162) ≈ 2.07``.
# We use 2.2 to slightly pad for run-to-run variance and the d_joint > 512
# extrapolation; the anchor seconds is padded to 10.0 for the same reason.
# The empirically lower-than-cubic exponent reflects ``exact_finite_env``'s
# adaptive Runge-Kutta propagation (scipy_dop853, O(d²) per step) rather
# than full matrix-exp (O(d³)). The 2026-05-13 v0.1.0 audit run discovered
# the d_joint³ initial guess was 2.5–3× pessimistic; the recalibration to
# d_joint^2.2 unlocks (4, 5) and (6, 3) as Hilbert-witness candidates at
# the default 30-min budget.
PREFLIGHT_ANCHOR_SECONDS = 10.0
PREFLIGHT_ANCHOR_D_JOINT = 2 * ANCHOR_N_LEVELS_PER_MODE**ANCHOR_N_BATH_MODES
PREFLIGHT_D_JOINT_EXPONENT = 2.2


PointStatus = Literal[
    "evaluated",
    "fit-degraded",
    "skipped-preflight",
    "skipped-timeout",
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

    Anchor-calibrated power-law scaling with exponent
    ``PREFLIGHT_D_JOINT_EXPONENT = 2.2``. The propagation step inside
    ``exact_finite_env`` uses scipy_dop853 adaptive Runge-Kutta, which is
    matrix-vector per step (O(d²)) rather than matrix-matrix (O(d³)); the
    fitted exponent across the v0.1.0 audit's anchor + (4, 4) Hilbert
    witness is ≈ 2.07, padded to 2.2 for safety. The alpha grid and basis
    size are held fixed at production values so ``d_joint`` is the only
    varying factor.

    The estimate is intentionally slightly conservative; the audit's R1
    mitigation pairs this preflight with a hard process timeout in
    ``evaluate_point_with_timeout`` to catch points that beat the
    prediction but still exceed budget.
    """
    return (
        PREFLIGHT_ANCHOR_SECONDS
        * (config.d_joint / PREFLIGHT_ANCHOR_D_JOINT) ** PREFLIGHT_D_JOINT_EXPONENT
    )


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


def _worker_evaluate_point(
    config: TruncationConfig,
    t_grid: np.ndarray | None,
    alpha_values: Sequence[float] | None,
    result_queue: Any,  # multiprocessing.Queue; weakly typed for spawn pickling
) -> None:
    """Subprocess entry point for ``evaluate_point_with_timeout``.

    Lives at module top level so it is picklable under the ``spawn`` start
    method (required on macOS / Windows; default on Python 3.14+ for Linux).
    """
    point = evaluate_point(config, t_grid=t_grid, alpha_values=alpha_values)
    result_queue.put(point)


def evaluate_point_with_timeout(
    config: TruncationConfig,
    *,
    timeout_seconds: float,
    t_grid: np.ndarray | None = None,
    alpha_values: Sequence[float] | None = None,
    grace_seconds: float = 5.0,
) -> FloorAuditPoint:
    """Run ``evaluate_point`` in a child process with a hard wall-clock timeout.

    Python signal-based timeouts cannot interrupt blocking C extension
    code in numpy / scipy, so the audit needs a separate-process timeout
    to bail on points that beat the preflight estimator but still run
    past the per-point budget (card §6 R1).

    Behaviour:
        - Spawns a child via ``multiprocessing.get_context("spawn")`` for
          a clean import state (no inherited globals from the parent).
        - Joins on the child up to ``timeout_seconds``.
        - If the child is still alive at timeout, calls ``terminate()``
          and joins for ``grace_seconds``; if still alive after that,
          calls ``kill()`` and joins indefinitely (kernel-level SIGKILL
          should not block).
        - Returns a ``FloorAuditPoint`` with status ``skipped-timeout``
          and a populated ``skip_reason`` in the timeout branch.
        - Surface unexpected child failures as ``errored`` rows with the
          exit code captured in ``error``.

    Parameters
    ----------
    config:
        Truncation knobs (same as ``evaluate_point``).
    timeout_seconds:
        Wall-clock budget for the child. Should equal the per-point
        budget chosen at audit-run time (typically
        ``per_point_budget_seconds``).
    t_grid, alpha_values:
        Forwarded to the child's ``evaluate_point`` call.
    grace_seconds:
        Time given for ``SIGTERM`` to clean up before escalating to
        ``SIGKILL`` (default 5 s).
    """
    import multiprocessing as mp

    predicted = predict_wall_time_seconds(config)
    ctx = mp.get_context("spawn")
    result_queue: Any = ctx.Queue()
    proc = ctx.Process(
        target=_worker_evaluate_point,
        args=(config, t_grid, alpha_values, result_queue),
    )
    t0 = time.perf_counter()
    proc.start()
    proc.join(timeout=timeout_seconds)

    if proc.is_alive():
        proc.terminate()
        proc.join(grace_seconds)
        if proc.is_alive():
            proc.kill()
            proc.join()
        wall = time.perf_counter() - t0
        return FloorAuditPoint(
            config=config,
            status="skipped-timeout",
            l2_avg=None,
            l4_avg=None,
            coefficient_ratio=None,
            fit_relative_residual=None,
            r_4_ladder=None,
            wall_time_seconds=wall,
            predicted_wall_time_seconds=predicted,
            skip_reason=(
                f"hard process timeout after {timeout_seconds:.1f} s "
                f"(actual wall {wall:.1f} s including grace)"
            ),
            error=None,
        )

    wall = time.perf_counter() - t0
    exit_code = proc.exitcode
    if exit_code != 0:
        return FloorAuditPoint(
            config=config,
            status="errored",
            l2_avg=None,
            l4_avg=None,
            coefficient_ratio=None,
            fit_relative_residual=None,
            r_4_ladder=None,
            wall_time_seconds=wall,
            predicted_wall_time_seconds=predicted,
            skip_reason=None,
            error=f"child process exited with code {exit_code} (no result posted)",
        )

    try:
        point = result_queue.get(timeout=10.0)
    except Exception as exc:  # queue.Empty or unexpected
        return FloorAuditPoint(
            config=config,
            status="errored",
            l2_avg=None,
            l4_avg=None,
            coefficient_ratio=None,
            fit_relative_residual=None,
            r_4_ladder=None,
            wall_time_seconds=wall,
            predicted_wall_time_seconds=predicted,
            skip_reason=None,
            error=f"child exited cleanly but result queue empty: {type(exc).__name__}: {exc}",
        )
    return point


def run_audit(
    *,
    per_point_budget_seconds: float = PER_POINT_BUDGET_SECONDS_DEFAULT,
    preflight_factor: float = 2.0,
    use_timeout: bool = True,
    t_grid: np.ndarray | None = None,
    alpha_values: Sequence[float] | None = None,
    output_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run the one-axis-at-a-time audit and return the result dict.

    Each point is preflight-checked against ``predict_wall_time_seconds``:
    if the prediction exceeds ``per_point_budget_seconds *
    preflight_factor`` the point is recorded with status
    ``skipped-preflight`` and not dispatched. Dispatched points that
    still exceed the per-point budget at runtime are killed by the
    process-level timeout in ``evaluate_point_with_timeout`` and recorded
    as ``skipped-timeout`` (only when ``use_timeout=True``).

    Parameters
    ----------
    per_point_budget_seconds:
        Hard wall-time budget per point (default 30 min; card §6 R1).
        When ``use_timeout=True`` this is also passed as the child-
        process timeout for dispatched points.
    preflight_factor:
        Predicted wall time > ``per_point_budget_seconds * preflight_factor``
        triggers a preflight skip. Default 2.0 — allows the prediction to
        be off by 2× before skipping.
    use_timeout:
        If True (default), dispatched points run through
        ``evaluate_point_with_timeout`` with ``timeout_seconds =
        per_point_budget_seconds``. If False, ``evaluate_point`` is
        called in-process (useful in tests that bypass multiprocessing
        overhead).
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
        if use_timeout:
            points.append(
                evaluate_point_with_timeout(
                    config,
                    timeout_seconds=per_point_budget_seconds,
                    t_grid=t_grid,
                    alpha_values=alpha_values,
                )
            )
        else:
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
            "skipped_timeout_count": sum(1 for p in points if p.status == "skipped-timeout"),
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
        "skipped_timeout_count": sum(1 for p in points if p.status == "skipped-timeout"),
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
    parser.add_argument(
        "--no-timeout",
        action="store_true",
        help=(
            "disable the multiprocessing per-point timeout; dispatched "
            "points run in-process (faster startup, no kill safety)"
        ),
    )
    args = parser.parse_args()
    audit = run_audit(
        per_point_budget_seconds=args.budget_seconds,
        preflight_factor=args.preflight_factor,
        use_timeout=not args.no_timeout,
        output_path=args.output,
        dry_run=args.dry_run,
    )
    print(json.dumps(audit["summary"], indent=2))


if __name__ == "__main__":
    _cli()

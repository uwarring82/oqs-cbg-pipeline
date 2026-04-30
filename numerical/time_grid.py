"""
numerical.time_grid — Time-grid construction and time-ordered integration.

Provides the time-grid layer Cards A3 and A4 depend on:

    build_time_grid(spec)              — Construct a TimeGrid from a card's
                                          frozen_parameters.numerical.time_grid
                                          spec dict (YAML form).
    TimeGrid                           — Dataclass wrapping the time array
                                          plus the spec metadata.
    integrate_with_ordering(integrand,
                            t_grid,
                            ordering)  — Cumulative time-ordered integral.
                                          Used by cbg.tcl_recursion (C.8) for
                                          the K_1 single-integral term and
                                          the K_2 nested-integral term.

Schemes implemented at DG-1 Phase C.5:
    - uniform (linspace; matches Cards A3/A4 frozen_parameters.numerical.scheme)

Schemes deferred to DG-2 (raise NotImplementedError with routing):
    - chebyshev  (non-uniform; faster convergence at the bath-cutoff scale)
    - log        (logarithmic spacing for memory-tail resolution)

Orderings implemented at DG-1 Phase C.5:
    - time_ordered (1D: ∫_0^t dτ f(τ); 2D: ∫_0^t dτ ∫_0^τ ds g(τ, s))

Orderings deferred to DG-2+ (raise NotImplementedError with routing):
    - anti_time_ordered, mixed orderings used in higher-order TCL terms

The 2D time-ordered integral is the natural integration domain for K_2
(Letter Eq. (16) order-2 term; companion paper Eq. (45) at n=2). C.8
exercises this code path for Cards A3/A4.

Anchor: SCHEMA.md v0.1.2; DG-1 work plan v0.1.3 §4 Phase C row C.5.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import numpy as np


# ─── Schemes / orderings ────────────────────────────────────────────────────

KNOWN_SCHEMES = ("uniform",)
KNOWN_ORDERINGS = ("time_ordered",)

# Schemes / orderings recognized but deferred to DG-2 (clear routing message
# rather than the generic "unknown" error).
DEFERRED_SCHEMES = {
    "chebyshev": "DG-2: non-uniform grid with Chebyshev nodes (better "
                 "convergence at the bath-cutoff scale)",
    "log": "DG-2: logarithmic spacing for memory-tail resolution",
}
DEFERRED_ORDERINGS = {
    "anti_time_ordered": "DG-2+: anti-time-ordered integration domain",
}


# ─── TimeGrid dataclass ─────────────────────────────────────────────────────


@dataclass
class TimeGrid:
    """An immutable-by-convention time grid plus its construction metadata.

    Attributes
    ----------
    times : ndarray
        The time-point array, shape (n_points,).
    t_start, t_end : float
        Endpoints of the grid (matched to the spec).
    n_points : int
        Number of points.
    scheme : str
        Construction scheme (e.g. "uniform").
    """
    times: np.ndarray
    t_start: float
    t_end: float
    n_points: int
    scheme: str

    @property
    def dt(self) -> float:
        """Step size for uniform grids; for non-uniform grids the value is
        the *mean* spacing — callers should not rely on it for dispatch."""
        if self.n_points <= 1:
            return 0.0
        return (self.t_end - self.t_start) / (self.n_points - 1)


# ─── Time-grid construction ─────────────────────────────────────────────────


REQUIRED_TIME_GRID_KEYS = ("t_start", "t_end", "n_points", "scheme")


def build_time_grid(spec: Dict[str, Any]) -> TimeGrid:
    """Construct a TimeGrid from a card's time_grid spec dict.

    Parameters
    ----------
    spec : dict
        The mapping under `frozen_parameters.numerical.time_grid` in a
        benchmark card. Required keys: t_start, t_end, n_points, scheme.

    Returns
    -------
    TimeGrid

    Raises
    ------
    ValueError
        If required keys are missing, t_end <= t_start, or n_points < 2.
    NotImplementedError
        If `scheme` is recognized as DG-2 territory.
    KeyError-style ValueError
        If `scheme` is unknown.
    """
    if not isinstance(spec, dict):
        raise ValueError(
            f"build_time_grid: spec must be a mapping; got {type(spec).__name__}"
        )
    missing = [k for k in REQUIRED_TIME_GRID_KEYS if k not in spec]
    if missing:
        raise ValueError(f"build_time_grid: missing required keys {missing}")

    t_start = float(spec["t_start"])
    t_end = float(spec["t_end"])
    n_points = spec["n_points"]
    scheme = spec["scheme"]

    if not isinstance(n_points, int) or isinstance(n_points, bool):
        raise ValueError(
            f"build_time_grid: n_points must be int; got {n_points!r}"
        )
    if n_points < 2:
        raise ValueError(
            f"build_time_grid: n_points must be >= 2; got {n_points}"
        )
    if t_end <= t_start:
        raise ValueError(
            f"build_time_grid: require t_end > t_start; got "
            f"t_start={t_start}, t_end={t_end}"
        )

    if scheme in DEFERRED_SCHEMES:
        raise NotImplementedError(
            f"build_time_grid: scheme {scheme!r} not implemented at DG-1. "
            f"{DEFERRED_SCHEMES[scheme]}"
        )
    if scheme not in KNOWN_SCHEMES:
        raise ValueError(
            f"build_time_grid: unknown scheme {scheme!r}; "
            f"known: {KNOWN_SCHEMES}; deferred: {tuple(DEFERRED_SCHEMES)}"
        )

    if scheme == "uniform":
        times = np.linspace(t_start, t_end, n_points)
    else:
        # Unreachable given the checks above; defensive.
        raise ValueError(f"build_time_grid: unhandled scheme {scheme!r}")

    return TimeGrid(
        times=times,
        t_start=t_start,
        t_end=t_end,
        n_points=n_points,
        scheme=scheme,
    )


# ─── Time-ordered integration ───────────────────────────────────────────────


def integrate_with_ordering(
    integrand: np.ndarray,
    t_grid: np.ndarray,
    ordering: str = "time_ordered",
) -> np.ndarray:
    """Cumulative time-ordered integral of an integrand sampled on `t_grid`.

    The output F has the same length as t_grid and represents the integral
    accumulated up to each t_grid[i].

    Dispatch by `integrand.ndim`:

    - **1D** (``integrand.shape == (n,)``): cumulative trapezoidal of the
      single-time integrand,

          F[i] = ∫_{t_grid[0]}^{t_grid[i]} integrand(τ) dτ        (Letter
                                                                  K_1 form)

    - **2D** (``integrand.shape == (n, n)``): cumulative trapezoidal of
      the time-ordered nested integral. ``integrand[j, k]`` is the
      integrand value at (τ = t_grid[j], s = t_grid[k]); only the
      lower-triangular part k ≤ j is used,

          F[i] = ∫_{t_grid[0]}^{t_grid[i]} dτ
                 ∫_{t_grid[0]}^{τ}        ds  integrand(τ, s)     (Letter
                                                                   K_2 form
                                                                   at order 2)

    Parameters
    ----------
    integrand : ndarray
        Pre-evaluated integrand sampled on ``t_grid``. Shape (n,) or (n, n).
        Complex dtype is supported (and is the typical case for K_n).
    t_grid : ndarray
        Time grid, shape (n,). Must be strictly monotonically increasing.
    ordering : str
        For DG-1, only ``"time_ordered"`` is implemented. Other orderings
        raise NotImplementedError with explicit DG-2+ routing.

    Returns
    -------
    F : ndarray
        Cumulative integral, shape (n,), dtype matching the integrand.
        F[0] = 0 (the integral over a zero-length interval).

    Raises
    ------
    NotImplementedError
        If ``ordering`` is recognized as DG-2+ territory.
    ValueError
        On unknown ``ordering``, shape mismatch, non-monotonic t_grid,
        or unsupported integrand ndim.
    """
    if ordering in DEFERRED_ORDERINGS:
        raise NotImplementedError(
            f"integrate_with_ordering: ordering {ordering!r} not implemented "
            f"at DG-1. {DEFERRED_ORDERINGS[ordering]}"
        )
    if ordering not in KNOWN_ORDERINGS:
        raise ValueError(
            f"integrate_with_ordering: unknown ordering {ordering!r}; "
            f"known: {KNOWN_ORDERINGS}; deferred: {tuple(DEFERRED_ORDERINGS)}"
        )

    integrand = np.asarray(integrand)
    t_grid = np.asarray(t_grid)

    if t_grid.ndim != 1:
        raise ValueError(
            f"integrate_with_ordering: t_grid must be 1D; got shape {t_grid.shape}"
        )
    n = t_grid.shape[0]
    if n < 2:
        raise ValueError(
            f"integrate_with_ordering: t_grid must have at least 2 points; got {n}"
        )
    if np.any(np.diff(t_grid) <= 0):
        raise ValueError(
            "integrate_with_ordering: t_grid must be strictly monotonically increasing"
        )

    if integrand.ndim == 1:
        if integrand.shape != (n,):
            raise ValueError(
                f"integrate_with_ordering: 1D integrand shape {integrand.shape} "
                f"does not match t_grid length ({n},)"
            )
        return _cumulative_trapezoid(integrand, t_grid)

    if integrand.ndim == 2:
        if integrand.shape != (n, n):
            raise ValueError(
                f"integrate_with_ordering: 2D integrand shape {integrand.shape} "
                f"does not match expected ({n}, {n})"
            )
        return _cumulative_time_ordered_double(integrand, t_grid)

    raise ValueError(
        f"integrate_with_ordering: integrand must be 1D or 2D; got ndim={integrand.ndim}"
    )


def _cumulative_trapezoid(f: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Cumulative trapezoidal rule:

        F[0] = 0
        F[i] = F[i-1] + 0.5 * (f[i-1] + f[i]) * (t[i] - t[i-1])     for i >= 1

    Returns an array the same length as t with the same dtype as f.
    """
    out = np.zeros_like(f)
    increments = 0.5 * (f[:-1] + f[1:]) * np.diff(t)
    out[1:] = np.cumsum(increments)
    return out


def _cumulative_time_ordered_double(g: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Cumulative double time-ordered integral:

        F[i] = ∫_{t[0]}^{t[i]} dτ ∫_{t[0]}^τ ds g(τ, s)

    Computed by first reducing the inner s-integral at each τ (using the
    trapezoidal rule on the lower-triangular part of `g`) to obtain
    G[j] = ∫_{t[0]}^{t[j]} ds g(t[j], s), then taking the cumulative
    trapezoidal of G over τ.

    The function is O(n^2) in the number of grid points; for the n=200
    DG-1 cards (A3, A4), this is ~40k operations and is fast enough for
    DG-1 acceptance times.
    """
    n = t.shape[0]
    # Inner integral G[j] = ∫_{t[0]}^{t[j]} ds g(t[j], s); j-th row,
    # truncated at the j-th column (lower triangle).
    G = np.zeros(n, dtype=g.dtype)
    for j in range(1, n):
        # Trapezoidal on g[j, 0:j+1] over t[0:j+1]
        row = g[j, : j + 1]
        ts = t[: j + 1]
        G[j] = np.trapezoid(row, ts) if hasattr(np, "trapezoid") else np.trapz(row, ts)
    # Outer cumulative trapezoidal over τ.
    return _cumulative_trapezoid(G, t)

# SPDX-License-Identifier: MIT
"""
cbg.bath_correlations — Bath spectral densities and connected n-point bath
correlation functions for the CBG construction.

This module is NOT a Nakajima–Zwanzig memory kernel.

The TCL representation is time-local at every order; the non-Markovian
character lives in the time-dependence of L_t, not in a kernel
convolution. This module evaluates:

    D(τ_1^k, s_1^{n-k}) = Tr_E { B^R(s_1^{n-k}) ∘ B^L(τ_1^k) [ρ_E] }
                          × θ(τ_1^k) θ(s_1^{n-k})         (Companion Eq. (15))

i.e. ordered n-point bath correlation functions, used to build the
generalised cumulants D̄ in cbg.cumulants (Companion Eq. (24)).

DG-1 scope (C.6):
    - Ohmic spectral density evaluator J(ω) = α ω exp(-ω/ω_c).
    - Two-point thermal connected correlator for bosonic linear coupling:

        C(t) = ⟨B(t) B(0)⟩_connected_thermal
             = ∫_0^∞ dω J(ω) [coth(ω / 2T) cos(ωt) - i sin(ωt)]

      This is also the connected two-point for *coherent-displaced* bath
      states: displacement leaves the connected (cumulant) part of any
      Gaussian state invariant; only the first cumulant ⟨B(t)⟩ shifts
      under displacement, and ⟨B(t)⟩ is *not* a connected two-point.
      The first-cumulant ⟨B(t)⟩ assembly from a card's
      `bath_state: coherent_displaced` spec is a model-layer
      responsibility (models/pure_dephasing.py, models/spin_boson_sigma_x.py).

DG-4 Phase B.0 scope (this module, 2026-05-05):
    - Raw ordered n-point correlations for n in {3, 4} on thermal
      Gaussian ohmic baths, using Wick factorisation into the existing
      two-point correlator.

DG-4 Phase B.4 scope (this module, 2026-05-06):
    - ``quad_limit`` and ``upper_cutoff_factor`` are threaded through
      the array, generic two-point, and n-point ordered entry points so
      D1 reproducibility perturbations can reach the quadrature leaf.

DG-2 / later scope (stubbed here):
    - Non-ohmic spectral densities (Drude–Lorentz, sub-/super-ohmic).
    - n-point ordered correlations beyond n = 4, explicit finite-bath
      operator traces, and non-Gaussian states.

The module is physically separated from time-grid integration to prevent
accidental importation of Markovian solver defaults from libraries like
QuTiP. Time-grid integration belongs in numerical/; bath-correlation
evaluation belongs here. The two are not interchangeable.

If a future extension requires Nakajima–Zwanzig-style kernels, those
would live in a separate cbg.nz_kernels module, not here.

Anchor: SCHEMA.md v0.1.2; DG-1 work plan v0.1.3 §4 Phase C row C.6.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import integrate

# ─── Spectral densities ─────────────────────────────────────────────────────


def ohmic_spectral_density(
    omega: np.ndarray | float,
    alpha: float,
    omega_c: float,
) -> np.ndarray:
    """Ohmic spectral density J(ω) = α ω exp(-ω/ω_c).

    Parameters
    ----------
    omega : array or scalar
        Frequencies at which to evaluate. Must be non-negative; the
        physical convention is J(ω) defined for ω ≥ 0.
    alpha : float
        Dimensionless coupling strength. Must be non-negative.
    omega_c : float
        Cutoff frequency (high-frequency exponential rolloff). Must be positive.

    Returns
    -------
    ndarray
        J(ω) of the same shape as `omega`, dtype float.

    Raises
    ------
    ValueError
        If alpha < 0, omega_c <= 0, or any omega < 0.
    """
    if alpha < 0.0:
        raise ValueError(f"ohmic_spectral_density: alpha must be >= 0; got {alpha}")
    if omega_c <= 0.0:
        raise ValueError(f"ohmic_spectral_density: omega_c must be > 0; got {omega_c}")
    omega = np.asarray(omega, dtype=float)
    if np.any(omega < 0.0):
        raise ValueError("ohmic_spectral_density: omega must be non-negative")
    return alpha * omega * np.exp(-omega / omega_c)


# ─── Two-point thermal connected correlator (bosonic linear coupling) ──────


def bath_two_point_thermal(
    t_diff: float,
    alpha: float,
    omega_c: float,
    temperature: float,
    *,
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> complex:
    """Connected two-point bath correlator C(t) = ⟨B(t) B(0)⟩_connected
    for an ohmic bath linearly coupled to the system.

    Implements

        C(t) = ∫_0^∞ dω J(ω) [coth(ω / 2T) cos(ωt) - i sin(ωt)]

    with J(ω) = α ω exp(-ω/ω_c). At T = 0, the integral has the closed
    form C(t) = α / (1/ω_c + it)²; this shortcut is used to avoid the
    coth divergence at ω → 0 when T = 0.

    For T > 0, the integral is evaluated numerically via
    scipy.integrate.quad on the real (cos · coth) and imaginary
    (-sin) parts separately. The integrable singularity at ω → 0
    (where J coth → 2αT) is bounded; quad handles it without endpoint
    refinement.

    Parameters
    ----------
    t_diff : float
        Time difference t (the correlator depends only on t_1 - t_2 by
        stationarity of the bath equilibrium).
    alpha, omega_c : float
        Spectral density parameters; see ohmic_spectral_density.
    temperature : float
        Bath temperature in the same units as ω (i.e. k_B T / ℏ if ω is
        in angular frequency units; or the dimensionless ratio T/ω_S if
        the system frequency sets the energy scale, as in Cards A3/A4).
        Must be non-negative. T = 0 takes the analytical-limit shortcut.
    upper_cutoff_factor : float, optional
        Numerical integration upper limit, expressed as a multiple of
        omega_c. Defaults to 30 (where exp(-30) ≈ 1e-13). Adjust upward
        only if the integrand has weight beyond this; ohmic exponential
        decay makes 30 conservative.
    quad_limit : int, optional
        Maximum number of subintervals scipy.integrate.quad uses.
        Defaults to 200; adequate for ohmic at T ≲ 10 ω_c.

    Returns
    -------
    complex
        C(t) as a Python complex scalar.

    Raises
    ------
    ValueError
        If alpha < 0, omega_c <= 0, or temperature < 0.
    """
    if alpha < 0.0:
        raise ValueError(f"bath_two_point_thermal: alpha must be >= 0; got {alpha}")
    if omega_c <= 0.0:
        raise ValueError(f"bath_two_point_thermal: omega_c must be > 0; got {omega_c}")
    if temperature < 0.0:
        raise ValueError(f"bath_two_point_thermal: temperature must be >= 0; got {temperature}")

    if temperature == 0.0:
        # Analytical T = 0 limit: C(t) = α / (1/ω_c + it)².
        denom = 1.0 / omega_c + 1j * t_diff
        return complex(alpha / (denom * denom))

    upper = upper_cutoff_factor * omega_c

    # coth(x) = (e^x + e^{-x}) / (e^x - e^{-x}) — but for numerical safety
    # at small x (near ω → 0), use 1 + 2/(e^{2x} - 1) which avoids the
    # 0/0 cancellation. coth(βω/2) = 1 + 2 / (exp(βω) - 1) where β = 1/T.
    beta = 1.0 / temperature

    def _real_amplitude(omega: float) -> float:
        # The non-oscillatory amplitude J(ω) coth(βω/2) (cos(ωt) factored
        # out into scipy.integrate.quad's weight='cos').
        if omega <= 0.0:
            return 0.0  # integrand vanishes at ω = 0 (ω · coth-factor → finite)
        bw = beta * omega
        # For very small T (large β), bw can exceed expm1's overflow bound.
        # In that regime coth → 1; bypass the expm1 call to avoid the
        # harmless overflow warning.
        if bw > 700.0:
            coth_factor = 1.0
        else:
            coth_factor = 1.0 + 2.0 / np.expm1(bw)
        return alpha * omega * np.exp(-omega / omega_c) * coth_factor

    def _imag_amplitude(omega: float) -> float:
        # The non-oscillatory amplitude -J(ω) (sin(ωt) factored out into
        # scipy.integrate.quad's weight='sin').
        if omega <= 0.0:
            return 0.0
        return -alpha * omega * np.exp(-omega / omega_c)

    # When t_diff = 0, weight='cos'/'sin' degenerates (sin(0)=0 means the
    # imag integral is exactly 0 with no quadrature needed; cos(0)=1
    # means the real integral reduces to plain quadrature on the amplitude).
    # scipy's quad with weight='cos' at wvar=0 should handle this, but we
    # shortcut for clarity.
    if t_diff == 0.0:
        real_part, _ = integrate.quad(_real_amplitude, 0.0, upper, limit=quad_limit)
        imag_part = 0.0
    else:
        # weight='cos' / weight='sin' integrate
        # ∫_0^upper amplitude(ω) cos(ω·t_diff) dω (or sin) analytically
        # in each quadrature subinterval. Far more accurate than naive
        # quadrature on the oscillatory product, and avoids spurious
        # IntegrationWarning ("integral is probably divergent or slowly
        # convergent") for grid points with t_diff at the cutoff scale.
        real_part, _ = integrate.quad(
            _real_amplitude,
            0.0,
            upper,
            weight="cos",
            wvar=t_diff,
            limit=quad_limit,
        )
        imag_part, _ = integrate.quad(
            _imag_amplitude,
            0.0,
            upper,
            weight="sin",
            wvar=t_diff,
            limit=quad_limit,
        )
    return complex(real_part, imag_part)


def bath_two_point_thermal_array(
    t_grid: np.ndarray,
    alpha: float,
    omega_c: float,
    temperature: float,
    *,
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> np.ndarray:
    """Tabulate C[j, k] = C(t_grid[j] - t_grid[k]) on a (n, n) grid.

    Exploits stationarity (the connected two-point depends only on
    t_1 - t_2) and Hermiticity (C(-t) = conj(C(t))) to evaluate
    C only on a 1D array of unique time differences and broadcast.

    Parameters
    ----------
    t_grid : ndarray, shape (n,)
        Time points at which to tabulate.
    alpha, omega_c, temperature : float
        See bath_two_point_thermal.
    upper_cutoff_factor, quad_limit : optional
        Quadrature controls forwarded to ``bath_two_point_thermal``.

    Returns
    -------
    ndarray, shape (n, n), dtype complex
        C[j, k] = C(t_grid[j] - t_grid[k]).
    """
    t_grid = np.asarray(t_grid, dtype=float)
    if t_grid.ndim != 1:
        raise ValueError(
            f"bath_two_point_thermal_array: t_grid must be 1D; " f"got shape {t_grid.shape}"
        )

    # Compute C on the unique non-negative time-difference grid; reuse
    # via Hermiticity for negative differences.
    n = t_grid.size
    diff = t_grid[:, None] - t_grid[None, :]  # shape (n, n); arbitrary signs

    unique_pos = np.unique(np.abs(diff))
    c_vals = np.array(
        [
            bath_two_point_thermal(
                float(t),
                alpha,
                omega_c,
                temperature,
                upper_cutoff_factor=upper_cutoff_factor,
                quad_limit=quad_limit,
            )
            for t in unique_pos
        ],
        dtype=complex,
    )
    # Map: |diff| → C(|diff|); for negative diff, conjugate.
    c_lookup = dict(zip(unique_pos, c_vals, strict=False))
    C = np.zeros((n, n), dtype=complex)
    for j in range(n):
        for k in range(n):
            d = diff[j, k]
            if d >= 0.0:
                C[j, k] = c_lookup[abs(d)]
            else:
                C[j, k] = np.conj(c_lookup[abs(d)])
    return C


# ─── Generic two-point dispatch ─────────────────────────────────────────────


def two_point(
    t1: float,
    t2: float,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> complex:
    """Connected two-point bath correlator at the requested bath state.

    Dispatches by (bath_state.family, spectral_density.family) to the
    appropriate evaluator. For DG-1, supports:

        - ("thermal", "ohmic"): bath_two_point_thermal
        - ("coherent_displaced", "ohmic"): same evaluator with the
          spec's `temperature` (the displacement leaves the connected
          two-point invariant; the first cumulant ⟨B(t)⟩ is a
          model-layer concern, not evaluated here).

    Parameters
    ----------
    t1, t2 : float
        Two time arguments. The correlator depends only on t1 - t2 by
        stationarity.
    bath_state : dict
        The card's per-case `bath_state` mapping. Required key: `family`.
        For thermal: also `temperature`. For coherent_displaced: also
        `temperature` (the vacuum baseline, typically 0 in DG-1 cards).
    spectral_density : dict
        The card's `bath_spectral_density` mapping. Required keys:
        `family`, plus family-specific parameters (for ohmic:
        `coupling_strength` (= alpha), `cutoff_frequency` (= omega_c)).
    upper_cutoff_factor, quad_limit : optional
        Quadrature controls forwarded to ``bath_two_point_thermal``.

    Returns
    -------
    complex
        C(t1 - t2) at the requested state.

    Raises
    ------
    NotImplementedError
        If the (bath_state.family, spectral_density.family) pair is not
        supported at DG-1.
    KeyError-style ValueError
        If required keys are missing.
    """
    bs_family = bath_state.get("family")
    sd_family = spectral_density.get("family")

    if sd_family != "ohmic":
        raise NotImplementedError(
            f"two_point: spectral_density.family {sd_family!r} not implemented "
            f"at DG-1. Only 'ohmic' is supported. (Drude-Lorentz, sub-ohmic, "
            f"super-ohmic → DG-2 territory.)"
        )

    if bs_family not in {"thermal", "coherent_displaced"}:
        raise NotImplementedError(
            f"two_point: bath_state.family {bs_family!r} not implemented at "
            f"DG-1. Supported: 'thermal', 'coherent_displaced' (the connected "
            f"two-point is identical to the thermal evaluator at the spec's "
            f"`temperature` — the displacement enters via the first cumulant, "
            f"which is a model-layer concern)."
        )

    alpha = float(spectral_density["coupling_strength"])
    omega_c = float(spectral_density["cutoff_frequency"])
    temperature = float(bath_state["temperature"])

    return bath_two_point_thermal(
        t1 - t2,
        alpha,
        omega_c,
        temperature,
        upper_cutoff_factor=upper_cutoff_factor,
        quad_limit=quad_limit,
    )


# ─── n-point ordered correlator (DG-2 territory) ────────────────────────────


def n_point_ordered(
    tau_args,
    s_args,
    bath_state,
    B_op=None,
    *,
    spectral_density: dict[str, Any] | None = None,
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> complex:
    """Ordered n-point bath correlation per Companion Eq. (15).

    Implements the DG-4 Phase B.0 leaf case for thermal Gaussian ohmic
    baths at total order n in {3, 4}. Thermal Gaussian baths have zero
    first cumulant, so odd raw correlations vanish. The n = 4 raw
    correlation is evaluated by Wick factorisation into the existing
    connected two-point correlator::

        D(t1, t2, t3, t4) =
            C(t1, t2) C(t3, t4)
          + C(t1, t3) C(t2, t4)
          + C(t1, t4) C(t2, t3)

    The flattened operator order used here is the left-acting sequence
    followed by the reversed right-acting sequence::

        times = tuple(tau_args) + tuple(reversed(s_args))

    This pins the mixed left/right convention for the B.1 cumulant
    recursion while preserving the existing all-left behaviour when
    ``s_args == ()``.

    Parameters
    ----------
    tau_args, s_args : sequence of float
        Left and right time arguments in Companion Eq. (15).
    bath_state : dict
        Currently requires ``family == "thermal"``.
    B_op : object, optional
        Retained for the historical stub signature. Explicit finite-bath
        operator traces are not implemented in this path; pass ``None``.
    spectral_density : dict, keyword-only
        Required ohmic spectral-density mapping consumed by ``two_point``.
    upper_cutoff_factor, quad_limit : optional
        Quadrature controls forwarded to the Wick-factorised two-point
        leaves.

    Returns
    -------
    complex
        Ordered raw bath correlation at the requested arguments.
    """
    tau_args = tuple(float(t) for t in tau_args)
    s_args = tuple(float(s) for s in s_args)
    n_total = len(tau_args) + len(s_args)

    if B_op is not None:
        raise NotImplementedError(
            "n_point_ordered: explicit B_op finite-bath traces are not "
            "implemented. Pass spectral_density for the thermal Gaussian "
            "ohmic Wick-factorised path."
        )
    if spectral_density is None:
        raise ValueError("n_point_ordered: spectral_density kwarg required")
    if bath_state.get("family") != "thermal":
        raise NotImplementedError(
            f"n_point_ordered: bath_state.family {bath_state.get('family')!r} "
            f"not implemented for n >= 3. DG-4 Phase B.0 supports only "
            f"thermal Gaussian baths."
        )
    if n_total not in {3, 4}:
        raise NotImplementedError(
            f"n_point_ordered: total order n={n_total} not implemented. "
            f"DG-4 Phase B.0 supports n in {{3, 4}} only."
        )

    if n_total % 2 == 1:
        return 0.0 + 0.0j

    times = tau_args + tuple(reversed(s_args))
    out = 0.0 + 0.0j
    for pairs in _wick_pairings(tuple(range(n_total))):
        term = 1.0 + 0.0j
        for i, j in pairs:
            term *= two_point(
                times[i],
                times[j],
                bath_state=bath_state,
                spectral_density=spectral_density,
                upper_cutoff_factor=upper_cutoff_factor,
                quad_limit=quad_limit,
            )
        out += term
    return complex(out)


def _wick_pairings(indices: tuple[int, ...]):
    """Yield all pair partitions of ``indices``.

    Small recursive helper for Wick factorisation. B.0 uses it at n = 4,
    where it yields the three standard pairings.
    """
    if not indices:
        yield ()
        return
    first = indices[0]
    rest = indices[1:]
    for pos, second in enumerate(rest):
        remaining = rest[:pos] + rest[pos + 1 :]
        for tail in _wick_pairings(remaining):
            yield ((first, second),) + tail

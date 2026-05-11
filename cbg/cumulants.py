# SPDX-License-Identifier: MIT
"""
cbg.cumulants — Generalised cumulants D̄(τ_1^k, s_1^{n-k}) for the TCL recursion.

Implements the recursion of Letter Eq. (17) and Companion Eq. (27):

    D̄(τ_1^k, s_1^{n-k}) = D(τ_1^k, s_1^{n-k})
                          - Σ_{l,r} D̄(τ_1^l, s_1^r) D̄(τ_{l+1}^k, s_{r+1}^{n-k})

These are the time-ordered cumulants that drive the L_n recursion in
cbg.tcl_recursion. They are formally similar to the ordered cumulants
of van Kampen (Physica 74, 215 and 239 (1974)).

DG-1 scope (this module, C.7):
    - D̄_1(t) array on a time grid: ⟨B(t)⟩ as a (n,) ndarray.
    - D̄_2(τ, s) array on a time grid: connected two-point as a
      (n, n) ndarray. For a Gaussian bath state this is the same as
      bath_correlations.bath_two_point_thermal_array at the spec's
      temperature; the displacement (if any) leaves the connected
      part invariant.
    - These are the canonical *time-ordered* (all-left) cumulants
      sufficient for K_1 and K_2 in Cards A3 and A4.

DG-4 Phase B.1 scope (this module, 2026-05-06):
    - Scalar generic D_bar(τ_1^k, s_1^{n-k}) supports mixed left/right
      indices at total order n = 2 and thermal Gaussian cumulants at
      n in {3, 4}. The mixed ordering follows cbg.bath_correlations'
      B.0 convention: times = tau_args + reversed(s_args).
    - Phase B.4 threads ``quad_limit`` and ``upper_cutoff_factor``
      through D_bar_2 and the scalar generic D_bar path.

DG-2 / later scope (stubbed here):
    - Cumulants for n > 4.
    - Cumulants of non-Gaussian bath states (where D̄_3 etc. don't
      automatically vanish).

Coherent-displacement convention gap (DG-1):
    Cards A3 and A4 specify per-case `bath_state.coherent_displaced`
    with `displacement_amplitude: 1.0` but no displacement-mode
    frequency or envelope. A coherent state on a multi-mode bath
    requires a basis choice that the cards don't pin. Consequently,
    D̄_1 for `bath_state.family == "coherent_displaced"` is stubbed
    here with a clear "convention not specified" routing message;
    its resolution is a model-layer concern (cbg.cumulants is
    physics-generic; cbg/models/{pure_dephasing, spin_boson_sigma_x}
    is the right place to encode the model-specific convention OR
    declare the displaced case deferred to DG-2 like Entry 1.B.3).

    The thermal case (D̄_1 = 0) and the connected D̄_2 (same for
    both Gaussian states) are unambiguous and are implemented here.

Anchor: SCHEMA.md v0.1.2; DG-1 work plan v0.1.3 §4 Phase C row C.7.
"""

from __future__ import annotations

from math import factorial
from typing import Any

import numpy as np
from scipy import integrate

from cbg.bath_correlations import (
    bath_two_point_thermal_array,
    n_point_ordered,
    ohmic_spectral_density,
    two_point,
)
from cbg.displacement_profiles import (
    REGISTERED_PROFILES,
    DisplacementProfile,
)

# ─── First generalised cumulant D̄_1(t) ─────────────────────────────────────


def D_bar_1(
    t_grid: np.ndarray,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any] | None = None,
) -> np.ndarray:
    """First generalised cumulant D̄_1(t) = ⟨B(t)⟩ on the time grid.

    Dispatches by ``bath_state.family``:
        - "thermal": returns a zero array of shape (n,) — thermal Gaussian
          bath states have ⟨B⟩ = 0 by symmetry.
        - "coherent_displaced": raises NotImplementedError. The
          displacement convention from `displacement_amplitude` to
          ⟨B(t)⟩ is a model-layer concern; see the module docstring.

    Parameters
    ----------
    t_grid : ndarray, shape (n,)
        Time-points at which to tabulate ⟨B(t)⟩.
    bath_state : dict
        The card's per-case bath_state mapping. Required key: family.
    spectral_density : dict | None
        Optional; included for signature parity with D_bar_2 and to allow
        future implementations to derive ⟨B(t)⟩ from the spectral density
        when a displacement convention is fixed. Ignored for thermal.

    Returns
    -------
    ndarray, shape (n,), dtype complex
        D̄_1(t_grid).

    Raises
    ------
    NotImplementedError
        For coherent_displaced bath state (convention not specified).
    NotImplementedError
        For other unsupported bath_state.family values.
    """
    t_grid = np.asarray(t_grid, dtype=float)
    if t_grid.ndim != 1:
        raise ValueError(f"D_bar_1: t_grid must be 1D; got shape {t_grid.shape}")

    family = bath_state.get("family")
    if family == "thermal":
        return np.zeros_like(t_grid, dtype=complex)
    if family == "coherent_displaced":
        return _D_bar_1_coherent_displaced(
            t_grid,
            bath_state=bath_state,
            spectral_density=spectral_density,
        )
    raise NotImplementedError(
        f"D_bar_1: bath_state.family {family!r} not implemented. "
        f"Supported: 'thermal' (zero by symmetry); 'coherent_displaced' "
        f"(dispatches on bath_state.displacement_profile via the "
        f"Council-Act-2-cleared registry per subsidiary briefing v0.3.0)."
    )


# ─── coherent-displaced D̄_1 dispatch (Council Act 2 cleared, 2026-05-04) ────


def _D_bar_1_coherent_displaced(
    t_grid: np.ndarray,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any] | None,
) -> np.ndarray:
    """⟨B(t)⟩ for a coherent-displaced bosonic bath under one of the four
    Council-cleared displacement-mode profiles (subsidiary briefing v0.3.0
    §3.1–§3.4; Council Act 2 verdict 2026-05-04 — see
    ``ledger/CL-2026-005_v0.4_council-deliberation_act2_2026-05-04.md``).

    Convention adopted at v0.1.0:

        ⟨B(t)⟩ = ∫_0^∞ dω √J(ω) [α(ω) e^{-iωt} + α(ω)* e^{+iωt}]

    where α(ω) is the spectral displacement profile from the cleared
    registry. For real α(ω), this reduces to

        ⟨B(t)⟩ = 2 ∫_0^∞ dω √J(ω) α(ω) cos(ωt)

    and is real-valued. The four profiles dispatch as:

      - delta-omega_c (kind="delta", omega=ω_c, amplitude=α₀):
            ⟨B(t)⟩ = 2 α₀ √J(ω_c) cos(ω_c t)
      - delta-omega_S (kind="delta", omega=ω_S, amplitude=α₀):
            ⟨B(t)⟩ = 2 α₀ √J(ω_S) cos(ω_S t)
      - sqrt-J (kind="broadband", α(ω) = α₀ √J(ω)):
            ⟨B(t)⟩ = 2 α₀ ∫ J(ω) cos(ωt) dω
      - gaussian (kind="gaussian", α(ω) = α₀ exp(−(ω−ω_d)²/(2Δω²))):
            ⟨B(t)⟩ = 2 α₀ ∫ √J(ω) exp(−(ω−ω_d)²/(2Δω²)) cos(ωt) dω

    The δ-function profiles evaluate at machine precision; the broadband
    and Gaussian profiles use scipy.integrate.quad with weight='cos' for
    accuracy on the oscillatory integrand. Quadrature accuracy bounds
    the verdict accuracy in the broadband / Gaussian fixtures.

    Parameters
    ----------
    t_grid : ndarray, shape (n,)
        Time-points at which to tabulate ⟨B(t)⟩.
    bath_state : dict
        Card per-case bath_state mapping. Required keys: family =
        "coherent_displaced"; displacement_profile (one of the cleared
        registry keys); parameters (profile-specific).
    spectral_density : dict
        Card bath_spectral_density mapping. Required keys: family =
        "ohmic"; coupling_strength (= α); cutoff_frequency (= ω_c).

    Returns
    -------
    ndarray, shape (n,), dtype complex
        ⟨B(t_grid)⟩.

    Raises
    ------
    NotImplementedError
        If displacement_profile is not in REGISTERED_PROFILES (the
        registry-clearance-gate per subsidiary briefing v0.3.0 §6.1) or
        if spectral_density.family is not "ohmic".
    ValueError
        If bath_state lacks displacement_profile, parameters, or the
        spectral_density block is missing.
    """
    if spectral_density is None:
        raise ValueError(
            "_D_bar_1_coherent_displaced: spectral_density is required "
            "for the coherent-displaced branch"
        )
    sd_family = spectral_density.get("family")
    if sd_family != "ohmic":
        raise NotImplementedError(
            f"_D_bar_1_coherent_displaced: spectral_density.family "
            f"{sd_family!r} not implemented; only 'ohmic' is supported "
            f"at v0.1.0."
        )

    profile_name = bath_state.get("displacement_profile")
    if profile_name is None:
        raise ValueError(
            "_D_bar_1_coherent_displaced: bath_state must carry "
            "'displacement_profile' (one of the Council-cleared registry "
            "keys per subsidiary briefing v0.3.0 §3.1–§3.4)"
        )
    if profile_name not in REGISTERED_PROFILES:
        raise NotImplementedError(
            f"_D_bar_1_coherent_displaced: displacement_profile "
            f"{profile_name!r} is not in the Council-cleared registry. "
            f"Known keys (subsidiary briefing v0.3.0 §3.1–§3.4): "
            f"{sorted(REGISTERED_PROFILES.keys())}. Adding new profiles "
            f"requires fresh Council clearance per the §6.1 registry-"
            f"clearance-gate."
        )

    params = bath_state.get("parameters") or {}
    alpha_sd = float(spectral_density["coupling_strength"])
    omega_c = float(spectral_density["cutoff_frequency"])

    # Build the DisplacementProfile via the registered constructor. For
    # sqrt-J the constructor takes a callable J built from the spec.
    if profile_name == "sqrt-J":

        def J(w: float) -> float:
            return float(ohmic_spectral_density(w, alpha_sd, omega_c))

        profile = REGISTERED_PROFILES[profile_name](
            alpha_0=params["alpha_0"],
            J=J,
        )
    else:
        profile = REGISTERED_PROFILES[profile_name](**params)

    return _evaluate_displaced_first_cumulant(
        t_grid,
        profile,
        alpha_sd=alpha_sd,
        omega_c=omega_c,
    )


# Numerical-quadrature upper limit (multiples of ω_c). Beyond this, the
# ohmic exp(-ω/ω_c) factor is below 1e-13; conservative for both broadband
# and gaussian (the latter has its own envelope cutoff).
_QUAD_UPPER_FACTOR = 30.0
_QUAD_LIMIT = 200


def _evaluate_displaced_first_cumulant(
    t_grid: np.ndarray,
    profile: DisplacementProfile,
    *,
    alpha_sd: float,
    omega_c: float,
) -> np.ndarray:
    """Compute ⟨B(t)⟩ on the time grid for a given DisplacementProfile.

    Dispatches on profile.kind. The two δ-function profiles evaluate in
    closed form (single-frequency cosine times √J at the centre); the
    broadband and gaussian profiles use scipy.integrate.quad with
    weight='cos' for oscillatory accuracy.
    """
    t_grid = np.asarray(t_grid, dtype=float)
    upper = _QUAD_UPPER_FACTOR * omega_c

    if profile.kind == "delta":
        omega_0 = profile.params["omega"]
        amplitude = profile.params["amplitude"]  # α₀
        J_at_omega_0 = float(ohmic_spectral_density(omega_0, alpha_sd, omega_c))
        prefactor = 2.0 * amplitude * np.sqrt(J_at_omega_0)
        return (prefactor * np.cos(omega_0 * t_grid)).astype(complex)

    if profile.kind == "broadband":
        # α(ω) = α_0 √J(ω); ⟨B(t)⟩ = 2 α_0 ∫ J(ω) cos(ωt) dω
        alpha_0 = profile.params["alpha_0"]

        def amplitude(omega: float) -> float:
            if omega <= 0.0:
                return 0.0
            return float(ohmic_spectral_density(omega, alpha_sd, omega_c))

        result = np.zeros_like(t_grid, dtype=complex)
        for i, t in enumerate(t_grid):
            if t == 0.0:
                integral, _ = integrate.quad(
                    amplitude,
                    0.0,
                    upper,
                    limit=_QUAD_LIMIT,
                )
            else:
                integral, _ = integrate.quad(
                    amplitude,
                    0.0,
                    upper,
                    weight="cos",
                    wvar=float(t),
                    limit=_QUAD_LIMIT,
                )
            result[i] = 2.0 * alpha_0 * integral
        return result

    if profile.kind == "gaussian":
        # α(ω) = α_0 exp(-(ω-ω_d)²/(2Δω²)); ⟨B(t)⟩ = 2 α_0 ∫ √J(ω) α(ω)/α_0 cos(ωt) dω
        alpha_0 = profile.params["alpha_0"]
        omega_d = profile.params["omega_d"]
        Delta_omega = profile.params["Delta_omega"]

        def amplitude(omega: float) -> float:
            if omega <= 0.0:
                return 0.0
            J_w = float(ohmic_spectral_density(omega, alpha_sd, omega_c))
            envelope = float(np.exp(-((omega - omega_d) ** 2) / (2.0 * Delta_omega**2)))
            return float(np.sqrt(J_w)) * envelope

        result = np.zeros_like(t_grid, dtype=complex)
        for i, t in enumerate(t_grid):
            if t == 0.0:
                integral, _ = integrate.quad(
                    amplitude,
                    0.0,
                    upper,
                    limit=_QUAD_LIMIT,
                )
            else:
                integral, _ = integrate.quad(
                    amplitude,
                    0.0,
                    upper,
                    weight="cos",
                    wvar=float(t),
                    limit=_QUAD_LIMIT,
                )
            result[i] = 2.0 * alpha_0 * integral
        return result

    raise NotImplementedError(
        f"_evaluate_displaced_first_cumulant: profile.kind {profile.kind!r} "
        f"not implemented. Known kinds: 'delta', 'broadband', 'gaussian'."
    )


# ─── Second generalised cumulant D̄_2(τ, s) ─────────────────────────────────


def D_bar_2(
    t_grid: np.ndarray,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> np.ndarray:
    """Second generalised cumulant D̄_2(τ, s) = ⟨B(τ) B(s)⟩_connected on
    the time grid.

    For a Gaussian bath state (thermal or coherent_displaced), the
    connected two-point is invariant under displacement: only D̄_1
    shifts under displacement, not D̄_2. The implementation therefore
    forwards to bath_correlations.bath_two_point_thermal_array at the
    spec's temperature for both bath_state.family values supported at
    DG-1.

    Parameters
    ----------
    t_grid : ndarray, shape (n,)
        Time-points.
    bath_state : dict
        The card's per-case bath_state mapping. Required keys: family,
        temperature.
    spectral_density : dict
        The card's bath_spectral_density mapping. Required keys: family
        ("ohmic" at DG-1), coupling_strength (= alpha), cutoff_frequency
        (= omega_c).
    upper_cutoff_factor, quad_limit : optional
        Quadrature controls forwarded to
        ``bath_correlations.bath_two_point_thermal_array``.

    Returns
    -------
    ndarray, shape (n, n), dtype complex
        D̄_2[j, k] = ⟨B(t_grid[j]) B(t_grid[k])⟩_connected.

    Raises
    ------
    NotImplementedError
        If spectral_density.family is not "ohmic" or bath_state.family
        is not in {"thermal", "coherent_displaced"}.
    """
    bs_family = bath_state.get("family")
    sd_family = spectral_density.get("family")

    if sd_family != "ohmic":
        raise NotImplementedError(
            f"D_bar_2: spectral_density.family {sd_family!r} not "
            f"implemented at DG-1; only 'ohmic' is supported."
        )
    if bs_family not in {"thermal", "coherent_displaced"}:
        raise NotImplementedError(
            f"D_bar_2: bath_state.family {bs_family!r} not implemented "
            f"at DG-1; only 'thermal' and 'coherent_displaced' are supported "
            f"(both use the same connected two-point evaluator)."
        )

    alpha = float(spectral_density["coupling_strength"])
    omega_c = float(spectral_density["cutoff_frequency"])
    temperature = float(bath_state["temperature"])

    return bath_two_point_thermal_array(
        t_grid,
        alpha,
        omega_c,
        temperature,
        upper_cutoff_factor=upper_cutoff_factor,
        quad_limit=quad_limit,
    )


# ─── Generic D_bar dispatch (existing-stub signature) ───────────────────────


def D_bar(tau_args, s_args, **kwargs):
    """Compute the generalised cumulant D̄(τ_1^k, s_1^{n-k}) by recursion.

    Implements the recursive subtraction of Letter Eq. (17) /
    Companion Eq. (27):

        D̄(τ_1^k, s_1^{n-k}) = D(τ_1^k, s_1^{n-k})
                              - Σ_{l,r} D̄(τ_1^l, s_1^r) ·
                                        D̄(τ_{l+1}^k, s_{r+1}^{n-k})

    DG-1 implemented the leaf cases for the canonical time-ordered
    cumulants used by Cards A3 and A4:

        - k=1, n-k=0 (single τ argument) → D̄_1 = D_1 = ⟨B(τ)⟩.
        - k=2, n-k=0 (two τ arguments)   → D̄_2 = D_2 - D_1 ⊗ D_1
                                                 = connected two-point.

    DG-4 Phase B.1 extends the scalar generic path to mixed left/right
    indices and to total order n in {3, 4} for thermal Gaussian baths.
    For n = 3 and n = 4 it evaluates the equivalent connected-cumulant
    set-partition expansion over B.0's flattened operator order:

        times = tuple(tau_args) + tuple(reversed(s_args))

    This is the leaf accepted by the higher-order TCL recursion and
    makes D̄_3 = D̄_4 = 0 for thermal Gaussian baths by Wick
    factorisation.

    For the canonical (all-left, time-ordered) DG-1 use cases, callers
    should prefer D_bar_1(t_grid, ...) and D_bar_2(t_grid, ...), which
    return precomputed (n,) and (n, n) arrays respectively. The
    array-form helpers compose efficiently with cbg.tcl_recursion.

    Parameters
    ----------
    tau_args : tuple of float
        Left-time arguments (τ_1, ..., τ_k).
    s_args : tuple of float
        Right-time arguments (s_1, ..., s_{n-k}).
    **kwargs
        bath_state, spectral_density (as for D_bar_1, D_bar_2), and
        optional quadrature controls ``upper_cutoff_factor`` and
        ``quad_limit``.

    Raises
    ------
    NotImplementedError
        For total order n > 4, or n ≥ 3 outside the thermal Gaussian
        B.1 path.
    """
    tau_args = tuple(float(t) for t in tau_args)
    s_args = tuple(float(s) for s in s_args)
    n_total = len(tau_args) + len(s_args)

    bath_state = kwargs.get("bath_state")
    spectral_density = kwargs.get("spectral_density")
    upper_cutoff_factor = float(kwargs.get("upper_cutoff_factor", 30.0))
    quad_limit = int(kwargs.get("quad_limit", 200))
    if bath_state is None:
        raise ValueError("D_bar: bath_state kwarg required")
    if n_total == 0:
        raise ValueError("D_bar: at least one time argument is required")

    if spectral_density is None and n_total >= 2:
        raise ValueError("D_bar: spectral_density kwarg required")

    # Preserve the historical DG-1 all-left n=1 return shape: D_bar_1
    # returns an array. The mixed/right-only scalar case below is needed
    # by the B.1 recursion.
    if n_total == 1 and len(s_args) == 0:
        return D_bar_1(
            np.asarray(tau_args, dtype=float),
            bath_state=bath_state,
            spectral_density=spectral_density,
        )

    times = _flatten_mixed_order(tau_args, s_args)
    return _D_bar_scalar_from_flat_times(
        times,
        bath_state=bath_state,
        spectral_density=spectral_density,
        upper_cutoff_factor=upper_cutoff_factor,
        quad_limit=quad_limit,
    )


def _flatten_mixed_order(
    tau_args: tuple[float, ...], s_args: tuple[float, ...]
) -> tuple[float, ...]:
    """Flatten mixed left/right arguments using the DG-4 B.0 convention."""
    return tau_args + tuple(reversed(s_args))


def _D_bar_scalar_from_flat_times(
    times: tuple[float, ...],
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> complex:
    """Scalar connected cumulant for already-flattened operator times."""
    n_total = len(times)
    if n_total == 1:
        return _D_bar_1_scalar(
            times[0],
            bath_state=bath_state,
            spectral_density=spectral_density,
        )
    if n_total == 2:
        arr = D_bar_2(
            np.asarray(times, dtype=float),
            bath_state=bath_state,
            spectral_density=spectral_density,
            upper_cutoff_factor=upper_cutoff_factor,
            quad_limit=quad_limit,
        )
        return complex(arr[0, 1])
    if n_total not in {3, 4}:
        raise NotImplementedError(
            f"D_bar: total order n={n_total} not implemented. "
            f"DG-4 Phase B.1 supports n in {{3, 4}} only beyond the "
            f"existing n <= 2 path."
        )
    if bath_state.get("family") != "thermal":
        raise NotImplementedError(
            f"D_bar: bath_state.family {bath_state.get('family')!r} "
            f"not implemented for n >= 3. DG-4 Phase B.1 supports only "
            f"thermal Gaussian baths."
        )
    return _joint_cumulant_from_raw_moments(
        times,
        bath_state=bath_state,
        spectral_density=spectral_density,
        upper_cutoff_factor=upper_cutoff_factor,
        quad_limit=quad_limit,
    )


def _D_bar_1_scalar(
    time: float,
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any] | None,
) -> complex:
    arr = D_bar_1(
        np.asarray([time], dtype=float),
        bath_state=bath_state,
        spectral_density=spectral_density,
    )
    return complex(np.asarray(arr, dtype=complex)[0])


def _joint_cumulant_from_raw_moments(
    times: tuple[float, ...],
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> complex:
    """Connected cumulant from raw ordered moments via set partitions."""
    out = 0.0 + 0.0j
    for partition in _set_partitions(tuple(range(len(times)))):
        n_blocks = len(partition)
        coefficient = ((-1) ** (n_blocks - 1)) * factorial(n_blocks - 1)
        term = 1.0 + 0.0j
        for block in partition:
            block_times = tuple(times[idx] for idx in block)
            term *= _raw_ordered_moment(
                block_times,
                bath_state=bath_state,
                spectral_density=spectral_density,
                upper_cutoff_factor=upper_cutoff_factor,
                quad_limit=quad_limit,
            )
        out += coefficient * term
    return complex(out)


def _raw_ordered_moment(
    times: tuple[float, ...],
    *,
    bath_state: dict[str, Any],
    spectral_density: dict[str, Any],
    upper_cutoff_factor: float = 30.0,
    quad_limit: int = 200,
) -> complex:
    """Raw ordered bath moment for one block of flattened operator times."""
    n_total = len(times)
    if n_total == 0:
        return 1.0 + 0.0j
    if n_total == 1:
        return _D_bar_1_scalar(
            times[0],
            bath_state=bath_state,
            spectral_density=spectral_density,
        )
    if n_total == 2:
        return two_point(
            times[0],
            times[1],
            bath_state=bath_state,
            spectral_density=spectral_density,
            upper_cutoff_factor=upper_cutoff_factor,
            quad_limit=quad_limit,
        )
    if n_total in {3, 4}:
        return n_point_ordered(
            times,
            (),
            bath_state,
            spectral_density=spectral_density,
            upper_cutoff_factor=upper_cutoff_factor,
            quad_limit=quad_limit,
        )
    raise NotImplementedError(f"_raw_ordered_moment: total order n={n_total} not implemented")


def _set_partitions(indices: tuple[int, ...]):
    """Yield set partitions of ``indices`` as tuples of ordered blocks."""
    if not indices:
        yield ()
        return

    first = indices[0]
    for tail_partition in _set_partitions(indices[1:]):
        yield ((first,),) + tail_partition
        for block_idx, block in enumerate(tail_partition):
            yield (
                tail_partition[:block_idx] + ((first,) + block,) + tail_partition[block_idx + 1 :]
            )

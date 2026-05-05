"""
benchmarks.qutip_reference — QuTiP-based master-equation reference.

Failure modes:
    - solver assumptions (Lindblad, Bloch–Redfield) embedded in solver choice;
    - secular approximations;
    - Born–Markov defaults.

Failure-mode class: solver-default (per docs/benchmark_protocol.md §2).

WARNING: This module imports from QuTiP, which has Markovian-favoured
defaults. The bath-correlation logic must NOT be sourced from this
module; it lives in cbg/bath_correlations.py for that reason.

Phase B implementation (DG-3 work plan v0.1.0): ``reference_propagate``
dispatches by ``(model, bath_state.family)`` to per-fixture handlers. At
v0.1.0 the only registered handler is the C1 thermal case
(``pure_dephasing × thermal``); all other configurations raise
``NotImplementedError`` with a pointer to the next deferred fixture.

The pure_dephasing × thermal handler builds a Lindblad master equation
via ``qutip.mesolve`` with a constant dephasing rate ``gamma_M``
extracted from ``cbg.bath_correlations.bath_two_point_thermal`` (the
zero-frequency component of the bath spectrum, ``2 ∫_0^∞ Re[C(t)] dt``).
This is intentionally a Markov-approximation reference — it shares no
truncation parameters with ``exact_finite_env.propagate``, so the two
methods belong to different failure-mode classes (solver-default vs
finite-system) per the Sail v0.5 §5 Tier 3 pairing rule.

Anchor: SCHEMA.md v0.1.3; Card C1 v0.1.0; DG-3 work plan v0.1.0 Phase B.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import integrate

from cbg.bath_correlations import bath_two_point_thermal, ohmic_spectral_density


def reference_propagate(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    solver_options: dict[str, Any] | None = None,
) -> np.ndarray:
    """Propagate the system reduced density matrix via a QuTiP solver.

    Dispatches by ``(model_spec.system_hamiltonian, coupling_operator,
    bath_state.family)`` to a per-fixture handler. The handlers each
    construct a QuTiP master equation with collapse operators whose
    rates are sourced from ``cbg.bath_correlations`` (never from QuTiP's
    own bath-default machinery).

    Parameters
    ----------
    model_spec : dict
        The card's ``frozen_parameters.model`` mapping. Required fields:
        - ``system_hamiltonian``, ``coupling_operator``, ``bath_type``;
        - ``bath_spectral_density`` (family, cutoff_frequency, coupling_strength);
        - ``bath_state`` (family, temperature, ...).
        Optional: ``parameters.omega`` (default 1.0 in omega-units).
    t_grid : ndarray, shape (n_times,)
        Time points at which to evaluate the reduced density matrix.
    solver_options : dict, optional
        Forwarded to ``qutip.mesolve`` as the ``options`` argument.

    Returns
    -------
    rho_system_t : ndarray, shape (n_times, system_dim, system_dim), dtype complex
        Reduced system density matrix at each grid time.

    Raises
    ------
    NotImplementedError
        If the (model, bath_state) combination is not yet wired. C1 thermal
        is the only fixture wired at Phase B v0.1.0; the displaced and
        sigma_x-coupling fixtures are next on the roadmap.
    ValueError
        If model_spec fields are missing or malformed.
    """
    import qutip  # local import: keeps the QuTiP surface contained.

    h_str = (model_spec.get("system_hamiltonian") or "").strip()
    a_str = (model_spec.get("coupling_operator") or "").strip()
    bs = model_spec.get("bath_state") or {}
    bs_family = bs.get("family")
    profile = bs.get("displacement_profile") if bs_family == "coherent_displaced" else None

    key = (h_str, a_str, bs_family, profile)
    handler = _HANDLERS.get(key)
    if handler is None:
        raise NotImplementedError(
            f"qutip_reference.reference_propagate: no handler registered for "
            f"(system_hamiltonian={h_str!r}, coupling_operator={a_str!r}, "
            f"bath_state.family={bs_family!r}, displacement_profile={profile!r}). "
            f"Registered: {sorted(_HANDLERS.keys())}"
        )
    return handler(model_spec, np.asarray(t_grid, dtype=float), solver_options, qutip)


def _propagate_pure_dephasing_thermal(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    solver_options: dict[str, Any] | None,
    qutip: Any,
) -> np.ndarray:
    """C1 thermal-bath fixture: pure dephasing under Markov-approximated Lindblad.

    Builds H_S = (omega/2) sigma_z, collapse operator c = sqrt(gamma_M / 2) sigma_z
    where gamma_M = 2 ∫_0^∞ Re[C(t)] dt is the zero-frequency bath spectrum
    sourced from cbg.bath_correlations.bath_two_point_thermal.

    Lindblad arithmetic for L = sigma_z: the off-diagonal coherence decays
    as |ρ_↑↓(t)| ∝ exp(-2 (gamma_M/2) t) = exp(-gamma_M t), matching the
    long-time slope of the exact non-Markovian dephasing function.
    """
    sd = model_spec.get("bath_spectral_density", {})
    bs = model_spec.get("bath_state", {})
    alpha = float(sd["coupling_strength"])
    omega_c = float(sd["cutoff_frequency"])
    temperature = float(bs["temperature"])
    omega = float(model_spec.get("parameters", {}).get("omega", 1.0))

    # gamma_M = 2 * integral_0^inf Re[C(t)] dt, sourced from cbg.bath_correlations.
    # Evaluate C(t) on a grid then integrate Re[C] via Simpson's rule. The
    # ohmic correlator decays on a timescale ~ 1/omega_c; integrate out to
    # ~ 30 / omega_c to capture the bulk.
    t_int = np.linspace(0.0, 30.0 / omega_c, 2048)
    re_C = np.array(
        [bath_two_point_thermal(t, alpha, omega_c, temperature).real for t in t_int]
    )
    gamma_M = 2.0 * float(integrate.simpson(re_C, t_int))

    # QuTiP setup.
    sigma_z = qutip.sigmaz()
    H_S = 0.5 * omega * sigma_z

    # |+⟩⟨+| initial state, matching benchmarks.exact_finite_env default.
    plus = (qutip.basis(2, 0) + qutip.basis(2, 1)).unit()
    rho0 = plus * plus.dag()

    # Lindblad collapse operator: c = sqrt(gamma_M / 2) sigma_z gives
    # off-diagonal decay rate gamma_M.
    c_ops = [np.sqrt(gamma_M / 2.0) * sigma_z]

    # mesolve. The QuTiP 5 API takes options as a dict.
    options = dict(solver_options) if solver_options else {}
    options.setdefault("store_states", True)
    options.setdefault("atol", 1e-12)
    options.setdefault("rtol", 1e-10)

    result = qutip.mesolve(H_S, rho0, list(t_grid), c_ops=c_ops, options=options)

    # Stack the QuTiP states into a (n_times, 2, 2) numpy array.
    rho_system_t = np.empty((t_grid.size, 2, 2), dtype=complex)
    for k, state in enumerate(result.states):
        rho_system_t[k] = np.asarray(state.full(), dtype=complex)
    return rho_system_t


def _propagate_pure_dephasing_displaced_delta_omega_c(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    solver_options: dict[str, Any] | None,
    qutip: Any,
) -> np.ndarray:
    """C1 displaced fixture (delta-omega_c profile): time-dependent Hamiltonian.

    Under the Council-cleared delta-omega_c convention (cbg.cumulants
    ``_evaluate_displaced_first_cumulant``), ⟨B(t)⟩ = 2 α₀ √J(ω_c) cos(ω_c t).
    Coherent displacement leaves the *connected* bath statistics invariant,
    so the Markov dephasing rate γ_M is identical to the thermal handler.
    The displacement enters the system master equation as a coherent
    time-dependent Lamb shift on top of H_S:

        H_eff(t) = (ω/2 + ⟨B(t)⟩) σ_z

    QuTiP integrates this via a list-Hamiltonian
    ``[H_S, [σ_z, ⟨B(t)⟩-coefficient(t)]]``; the collapse operator is
    unchanged from the thermal handler.
    """
    sd = model_spec.get("bath_spectral_density", {})
    bs = model_spec.get("bath_state", {})
    params = bs.get("parameters") or {}
    profile_name = bs.get("displacement_profile")
    if profile_name != "delta-omega_c":
        raise NotImplementedError(
            f"_propagate_pure_dephasing_displaced_delta_omega_c: only "
            f"'delta-omega_c' supported at v0.1.0; got {profile_name!r}"
        )
    if "alpha_0" not in params or "omega_c" not in params:
        raise ValueError(
            "_propagate_pure_dephasing_displaced_delta_omega_c: "
            "bath_state.parameters must carry alpha_0 and omega_c"
        )

    alpha = float(sd["coupling_strength"])
    omega_c = float(sd["cutoff_frequency"])
    temperature = float(bs.get("temperature", 0.5))
    omega = float(model_spec.get("parameters", {}).get("omega", 1.0))
    alpha_0 = float(params["alpha_0"])
    omega_disp = float(params["omega_c"])

    # Markov dephasing rate from cbg (connected stats — unchanged by displacement).
    t_int = np.linspace(0.0, 30.0 / omega_c, 2048)
    re_C = np.array(
        [bath_two_point_thermal(t, alpha, omega_c, temperature).real for t in t_int]
    )
    gamma_M = 2.0 * float(integrate.simpson(re_C, t_int))

    # Coherent Lamb-shift amplitude from cbg.cumulants delta-omega_c
    # convention: ⟨B(t)⟩ = 2 α₀ √J(ω_disp) cos(ω_disp t).
    sqrt_J = float(np.sqrt(ohmic_spectral_density(omega_disp, alpha, omega_c)))
    lamb_amp = 2.0 * alpha_0 * sqrt_J  # peak amplitude of ⟨B(t)⟩

    sigma_z = qutip.sigmaz()
    H_S = 0.5 * omega * sigma_z

    plus = (qutip.basis(2, 0) + qutip.basis(2, 1)).unit()
    rho0 = plus * plus.dag()
    c_ops = [np.sqrt(gamma_M / 2.0) * sigma_z]

    # QuTiP 5 string-coefficient time-dependent Hamiltonian: H = H_S + f(t) σ_z
    # with f(t) = lamb_amp · cos(omega_disp · t).
    H_t = [
        H_S,
        [sigma_z, "lamb_amp * cos(omega_disp * t)"],
    ]
    args = {"lamb_amp": lamb_amp, "omega_disp": omega_disp}

    options = dict(solver_options) if solver_options else {}
    options.setdefault("store_states", True)
    options.setdefault("atol", 1e-12)
    options.setdefault("rtol", 1e-10)

    result = qutip.mesolve(
        H_t, rho0, list(t_grid), c_ops=c_ops, args=args, options=options
    )

    rho_system_t = np.empty((t_grid.size, 2, 2), dtype=complex)
    for k, state in enumerate(result.states):
        rho_system_t[k] = np.asarray(state.full(), dtype=complex)
    return rho_system_t


def _propagate_spin_boson_sigma_x_thermal(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    solver_options: dict[str, Any] | None,
    qutip: Any,
) -> np.ndarray:
    """C2 thermal-bath fixture: σ_x coupling under Born-Markov-secular Lindblad.

    Unlike σ_z (pure dephasing) where the bath couples to the system's
    energy basis and only S(0) matters, σ_x couples to off-diagonal
    transitions, so the relevant bath spectrum frequencies are ±ω_S
    (the system Bohr frequency). The secular master equation has two
    Lindblad channels:

        c_- = √(γ(+ω_S)) σ_-     (relaxation; rate γ_- = S(+ω_S))
        c_+ = √(γ(-ω_S)) σ_+     (excitation; rate γ_+ = S(-ω_S))

    where S(ω) = ∫_{-∞}^∞ ⟨B(t)B(0)⟩ e^{iωt} dt is the bath spectrum,
    sourced from cbg.bath_correlations.bath_two_point_thermal (NOT
    from QuTiP defaults). For ohmic at T > 0:

        S(+ω_S) = 2π J(ω_S) (n(ω_S) + 1)
        S(-ω_S) = 2π J(ω_S) n(ω_S)

    so the long-time steady state is the canonical Boltzmann distribution
    P(↑)/P(↓) = γ_+/γ_- = exp(-ω_S/T).

    Implementation evaluates S(ω_S) and S(-ω_S) numerically by Simpson
    integration of cbg's correlator on a fine grid, avoiding any
    closed-form ohmic-spectrum dependence inside this module.
    """
    sd = model_spec.get("bath_spectral_density", {})
    bs = model_spec.get("bath_state", {})
    alpha = float(sd["coupling_strength"])
    omega_c = float(sd["cutoff_frequency"])
    temperature = float(bs["temperature"])
    omega = float(model_spec.get("parameters", {}).get("omega", 1.0))

    # Numerical bath spectrum at ±ω: S(ω) = 2 Re[∫_0^∞ C(t) e^{iωt} dt].
    t_int = np.linspace(0.0, 30.0 / omega_c, 4096)
    C_int = np.array(
        [bath_two_point_thermal(t, alpha, omega_c, temperature) for t in t_int]
    )
    re_C = C_int.real
    im_C = C_int.imag
    cos_w = np.cos(omega * t_int)
    sin_w = np.sin(omega * t_int)
    # S(+ω) = 2 ∫(re_C cos(ωt) - im_C sin(ωt)) dt
    # S(-ω) = 2 ∫(re_C cos(ωt) + im_C sin(ωt)) dt
    gamma_relax = 2.0 * float(integrate.simpson(re_C * cos_w - im_C * sin_w, t_int))
    gamma_excite = 2.0 * float(integrate.simpson(re_C * cos_w + im_C * sin_w, t_int))
    if gamma_relax < 0 or gamma_excite < 0:
        raise ValueError(
            f"_propagate_spin_boson_sigma_x_thermal: numerical spectrum "
            f"yielded negative rates (γ_-={gamma_relax}, γ_+={gamma_excite}); "
            f"check spectral-density parameters."
        )

    sigma_z = qutip.sigmaz()
    sigma_p = qutip.sigmap()
    sigma_m = qutip.sigmam()
    H_S = 0.5 * omega * sigma_z

    plus = (qutip.basis(2, 0) + qutip.basis(2, 1)).unit()
    rho0 = plus * plus.dag()

    c_ops = [
        np.sqrt(gamma_relax) * sigma_m,
        np.sqrt(gamma_excite) * sigma_p,
    ]

    options = dict(solver_options) if solver_options else {}
    options.setdefault("store_states", True)
    options.setdefault("atol", 1e-12)
    options.setdefault("rtol", 1e-10)

    result = qutip.mesolve(H_S, rho0, list(t_grid), c_ops=c_ops, options=options)

    rho_system_t = np.empty((t_grid.size, 2, 2), dtype=complex)
    for k, state in enumerate(result.states):
        rho_system_t[k] = np.asarray(state.full(), dtype=complex)
    return rho_system_t


def _propagate_spin_boson_sigma_x_displaced_delta_omega_c(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    solver_options: dict[str, Any] | None,
    qutip: Any,
) -> np.ndarray:
    """C2 displaced fixture: σ_x coupling under coherent-displaced bath.

    Combines two Phase B mechanisms already validated:
      - Connected-stats invariance under displacement: γ_± = S(±ω_S) are
        identical to the C2 thermal case (σ_-/σ_+ secular Lindblad).
      - Coherent-displacement Lamb-like drive: ⟨B(t)⟩ = 2 α₀ √J(ω_c)
        cos(ω_c t) acts as a time-dependent classical drive on the
        coupling operator. For σ_x coupling this is a coherent σ_x drive,
        not a σ_z Lamb shift.

    The total Hamiltonian seen by the system is

        H_eff(t) = (ω/2) σ_z + ⟨B(t)⟩ σ_x,

    encoded as a QuTiP list-Hamiltonian with a string-coefficient time
    dependence; the dissipator is the same σ_-/σ_+ pair as the σ_x
    thermal handler.
    """
    sd = model_spec.get("bath_spectral_density", {})
    bs = model_spec.get("bath_state", {})
    params = bs.get("parameters") or {}
    profile_name = bs.get("displacement_profile")
    if profile_name != "delta-omega_c":
        raise NotImplementedError(
            f"_propagate_spin_boson_sigma_x_displaced_delta_omega_c: "
            f"only 'delta-omega_c' supported at v0.1.0; got {profile_name!r}"
        )
    if "alpha_0" not in params or "omega_c" not in params:
        raise ValueError(
            "_propagate_spin_boson_sigma_x_displaced_delta_omega_c: "
            "bath_state.parameters must carry alpha_0 and omega_c"
        )

    alpha = float(sd["coupling_strength"])
    omega_c = float(sd["cutoff_frequency"])
    temperature = float(bs.get("temperature", 0.5))
    omega = float(model_spec.get("parameters", {}).get("omega", 1.0))
    alpha_0 = float(params["alpha_0"])
    omega_disp = float(params["omega_c"])

    # Same numerical S(±ω_S) extraction as the σ_x thermal handler
    # (connected stats invariant under displacement).
    t_int = np.linspace(0.0, 30.0 / omega_c, 4096)
    C_int = np.array(
        [bath_two_point_thermal(t, alpha, omega_c, temperature) for t in t_int]
    )
    cos_w = np.cos(omega * t_int)
    sin_w = np.sin(omega * t_int)
    gamma_relax = 2.0 * float(integrate.simpson(C_int.real * cos_w - C_int.imag * sin_w, t_int))
    gamma_excite = 2.0 * float(integrate.simpson(C_int.real * cos_w + C_int.imag * sin_w, t_int))
    if gamma_relax < 0 or gamma_excite < 0:
        raise ValueError(
            f"_propagate_spin_boson_sigma_x_displaced_delta_omega_c: numerical "
            f"spectrum yielded negative rates (γ_-={gamma_relax}, γ_+={gamma_excite})"
        )

    # Coherent-drive amplitude on σ_x at frequency ω_disp.
    sqrt_J = float(np.sqrt(ohmic_spectral_density(omega_disp, alpha, omega_c)))
    drive_amp = 2.0 * alpha_0 * sqrt_J

    sigma_z = qutip.sigmaz()
    sigma_x = qutip.sigmax()
    sigma_p = qutip.sigmap()
    sigma_m = qutip.sigmam()
    H_S = 0.5 * omega * sigma_z

    plus = (qutip.basis(2, 0) + qutip.basis(2, 1)).unit()
    rho0 = plus * plus.dag()
    c_ops = [
        np.sqrt(gamma_relax) * sigma_m,
        np.sqrt(gamma_excite) * sigma_p,
    ]

    H_t = [
        H_S,
        [sigma_x, "drive_amp * cos(omega_disp * t)"],
    ]
    args = {"drive_amp": drive_amp, "omega_disp": omega_disp}

    options = dict(solver_options) if solver_options else {}
    options.setdefault("store_states", True)
    options.setdefault("atol", 1e-12)
    options.setdefault("rtol", 1e-10)

    result = qutip.mesolve(
        H_t, rho0, list(t_grid), c_ops=c_ops, args=args, options=options
    )

    rho_system_t = np.empty((t_grid.size, 2, 2), dtype=complex)
    for k, state in enumerate(result.states):
        rho_system_t[k] = np.asarray(state.full(), dtype=complex)
    return rho_system_t


_HANDLERS: dict[tuple[str, str, str, str | None], Any] = {
    ("(omega / 2) * sigma_z", "sigma_z", "thermal", None): _propagate_pure_dephasing_thermal,
    (
        "(omega / 2) * sigma_z",
        "sigma_z",
        "coherent_displaced",
        "delta-omega_c",
    ): _propagate_pure_dephasing_displaced_delta_omega_c,
    (
        "(omega / 2) * sigma_z",
        "sigma_x",
        "thermal",
        None,
    ): _propagate_spin_boson_sigma_x_thermal,
    (
        "(omega / 2) * sigma_z",
        "sigma_x",
        "coherent_displaced",
        "delta-omega_c",
    ): _propagate_spin_boson_sigma_x_displaced_delta_omega_c,
}

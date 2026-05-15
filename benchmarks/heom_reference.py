# SPDX-License-Identifier: MIT
"""
benchmarks.heom_reference — Hierarchical-equations-of-motion reference.

Failure modes:
    - hierarchy truncation (max_depth);
    - multi-exponential fit residual on the bath correlation function
      (Correlation-Function NLSQ; Nr / Ni truncation, target RMSE);
    - numerical instability at large hierarchy depth.

Failure-mode class: bath-hierarchy-truncation (per docs/benchmark_protocol.md §2;
DG-3 work plan v0.1.1 §3 records the one-module-per-failure-mode-class
convention).

WARNING: This module sources bath correlations from
``cbg.bath_correlations.bath_two_point_thermal`` — never from QuTiP's
own bath-default machinery (Drude–Lorentz expansion, Matsubara hierarchy
parameters, etc.). The cbg correlator is sampled on a time grid and fed
to ``BosonicEnvironment.from_correlation_function`` + an exponential
``approximate("cf", ...)`` fit. The fit is the only QuTiP-side numerical
choice; the underlying physics is cbg's.

Phase B implementation (DG-3 work plan v0.1.1): ``heom_propagate``
dispatches by ``(model, coupling_operator, bath_state.family,
displacement_profile)`` to per-fixture handlers. At v0.1.0 of this module
only the C1 thermal (``pure_dephasing × σ_z × thermal``) and C2 thermal
(``spin_boson_sigma_x × σ_x × thermal``) handlers are registered; all
other configurations raise ``NotImplementedError``.

Anchor: SCHEMA.md v0.1.3; Cards C1, C2 v0.1.0; DG-3 work plan v0.1.1
§§2, 3, 4 Phase B.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from cbg.bath_correlations import bath_two_point_thermal

# ─── Frozen knobs for the v0.1.0 of this module ───────────────────────────────
# Exposed as defaults; overridable via the ``heom`` sub-dict of
# ``solver_options`` (see ``heom_propagate``).

_T_MAX_FACTOR = 30.0  # cbg correlator sampled on [0, T_MAX_FACTOR / omega_c]
_N_PTS_CORRELATOR = 1024
_CF_TARGET_RMSE = 5e-3
_CF_NR_MAX = 3
_CF_NI_MAX = 2
_MAX_DEPTH = 3


def heom_propagate(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    solver_options: dict[str, Any] | None = None,
) -> np.ndarray:
    """Propagate the system reduced density matrix via QuTiP's in-tree HEOM.

    Dispatches by ``(system_hamiltonian, coupling_operator, bath_state.family,
    displacement_profile)`` to a per-fixture handler. The handlers build the
    bath correlation function from ``cbg.bath_correlations``, fit a
    multi-exponential expansion via ``BosonicEnvironment.approximate("cf", ...)``,
    and construct a ``qutip.solver.heom.HEOMSolver`` with the chosen
    ``max_depth``.

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
        Forwarded under key ``"heom"`` to override the v0.1.0 defaults:
        ``t_max_factor``, ``n_pts_correlator``, ``cf_target_rmse``,
        ``cf_Nr_max``, ``cf_Ni_max``, ``max_depth``. All other keys are
        forwarded to ``HEOMSolver`` as its ``options`` argument.

    Returns
    -------
    rho_system_t : ndarray, shape (n_times, system_dim, system_dim), dtype complex
        Reduced system density matrix at each grid time.

    Raises
    ------
    NotImplementedError
        If the (model, bath_state) combination is not registered. At v0.1.0
        only ``(σ_z, thermal)`` and ``(σ_x, thermal)`` are wired; displaced
        and non-ohmic configurations are explicit deferrals.
    ValueError
        If model_spec fields are missing or malformed.
    """
    import qutip  # local import: keeps the QuTiP surface contained.

    _validate_v010_assumptions(model_spec)

    h_str: str = (model_spec.get("system_hamiltonian") or "").strip()
    a_str: str = (model_spec.get("coupling_operator") or "").strip()
    bs = model_spec.get("bath_state") or {}
    bs_family: str = bs.get("family") or ""
    profile: str | None = (
        bs.get("displacement_profile") if bs_family == "coherent_displaced" else None
    )

    key: tuple[str, str, str, str | None] = (h_str, a_str, bs_family, profile)
    handler = _HANDLERS.get(key)
    if handler is None:
        raise NotImplementedError(
            f"heom_reference.heom_propagate: no handler registered for "
            f"(system_hamiltonian={h_str!r}, coupling_operator={a_str!r}, "
            f"bath_state.family={bs_family!r}, displacement_profile={profile!r}). "
            f"Registered: {sorted(_HANDLERS.keys())}"
        )
    return handler(model_spec, np.asarray(t_grid, dtype=float), solver_options, qutip)


def _validate_v010_assumptions(model_spec: dict[str, Any]) -> None:
    """Refuse model specs whose model-wide knobs fall outside v0.1.0 scope.

    The shared bath-correlation path (``_build_exp_env_from_cbg``) is hard-wired
    to ``cbg.bath_correlations.bath_two_point_thermal`` (ohmic, bosonic-linear)
    on a 2-level system. Any spec that contradicts those assumptions is
    refused here, *before* dispatch, so the user never gets a silent
    misinterpretation (e.g. a Drude–Lorentz spec being propagated as ohmic).
    """
    sd_family = (model_spec.get("bath_spectral_density") or {}).get("family")
    if sd_family != "ohmic":
        raise NotImplementedError(
            f"heom_reference: only bath_spectral_density.family='ohmic' is "
            f"supported at v0.1.0; got {sd_family!r}. Other families require "
            f"their own cbg correlator and a dedicated handler."
        )
    bath_type = model_spec.get("bath_type")
    if bath_type != "bosonic_linear":
        raise NotImplementedError(
            f"heom_reference: only bath_type='bosonic_linear' is supported at "
            f"v0.1.0; got {bath_type!r}."
        )
    system_dim = model_spec.get("system_dimension", 2)
    if system_dim != 2:
        raise NotImplementedError(
            f"heom_reference: only system_dimension=2 is supported at v0.1.0; "
            f"got {system_dim!r}."
        )


# ─── Shared helper: cbg correlator → exponential bath ─────────────────────────


def _build_exp_env_from_cbg(model_spec: dict[str, Any], heom_opts: dict[str, Any]):
    """Sample ``cbg.bath_two_point_thermal`` and fit an exponential expansion.

    Returns the ``ExponentialBosonicEnvironment`` produced by QuTiP's
    correlation-function (CF) NLSQ fitter. The underlying correlator is
    cbg's; the fit only chooses the multi-exponential approximation
    parameters.
    """
    from qutip.core.environment import BosonicEnvironment

    sd = model_spec.get("bath_spectral_density", {})
    bs = model_spec.get("bath_state", {})
    alpha = float(sd["coupling_strength"])
    omega_c = float(sd["cutoff_frequency"])
    temperature = float(bs["temperature"])

    t_max_factor = float(heom_opts.get("t_max_factor", _T_MAX_FACTOR))
    n_pts = int(heom_opts.get("n_pts_correlator", _N_PTS_CORRELATOR))
    target_rmse = float(heom_opts.get("cf_target_rmse", _CF_TARGET_RMSE))
    nr_max = int(heom_opts.get("cf_Nr_max", _CF_NR_MAX))
    ni_max = int(heom_opts.get("cf_Ni_max", _CF_NI_MAX))

    tlist = np.linspace(0.0, t_max_factor / omega_c, n_pts)
    C = np.array([bath_two_point_thermal(t, alpha, omega_c, temperature) for t in tlist])

    env = BosonicEnvironment.from_correlation_function(C=C, tlist=tlist, T=temperature)
    approx, _info = env.approximate(
        "cf", tlist=tlist, target_rmse=target_rmse, Nr_max=nr_max, Ni_max=ni_max
    )
    return approx


def _run_heom(H_S, Q, env_exp, rho0, t_grid, heom_opts: dict[str, Any], qutip: Any) -> np.ndarray:
    """Build HEOMSolver, run, and stack the returned states into an ndarray."""
    from qutip.solver.heom import HEOMSolver

    max_depth = int(heom_opts.get("max_depth", _MAX_DEPTH))
    solver_kwargs = {
        k: v
        for k, v in heom_opts.items()
        if k
        not in {
            "t_max_factor",
            "n_pts_correlator",
            "cf_target_rmse",
            "cf_Nr_max",
            "cf_Ni_max",
            "max_depth",
        }
    }
    solver_kwargs.setdefault("progress_bar", "")
    solver_kwargs.setdefault("store_states", True)

    solver = HEOMSolver(H_S, (env_exp, Q), max_depth=max_depth, options=solver_kwargs)
    result = solver.run(rho0, list(t_grid))

    rho_system_t = np.empty((len(t_grid), 2, 2), dtype=complex)
    for k, state in enumerate(result.states):
        rho_system_t[k] = np.asarray(state.full(), dtype=complex)
    return rho_system_t


# ─── Handlers ─────────────────────────────────────────────────────────────────


def _propagate_pure_dephasing_thermal(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    solver_options: dict[str, Any] | None,
    qutip: Any,
) -> np.ndarray:
    """C1 thermal-bath fixture: pure dephasing under HEOM with σ_z coupling.

    H_S = (ω/2) σ_z, Q = σ_z. The cbg ohmic correlator is fitted as a
    multi-exponential and fed to HEOMSolver. Populations are conserved
    (pure dephasing); the off-diagonal coherence decays non-Markovianly
    via the full bath memory kernel encoded in the hierarchy.
    """
    omega = float(model_spec.get("parameters", {}).get("omega", 1.0))
    heom_opts = dict((solver_options or {}).get("heom") or {})

    env_exp = _build_exp_env_from_cbg(model_spec, heom_opts)

    sigma_z = qutip.sigmaz()
    H_S = 0.5 * omega * sigma_z
    Q = sigma_z

    plus = (qutip.basis(2, 0) + qutip.basis(2, 1)).unit()
    rho0 = plus * plus.dag()

    other_opts = {k: v for k, v in (solver_options or {}).items() if k != "heom"}
    merged = {**heom_opts, **other_opts}
    return _run_heom(H_S, Q, env_exp, rho0, t_grid, merged, qutip)


def _propagate_spin_boson_sigma_x_thermal(
    model_spec: dict[str, Any],
    t_grid: np.ndarray,
    solver_options: dict[str, Any] | None,
    qutip: Any,
) -> np.ndarray:
    """C2 thermal-bath fixture: σ_x coupling under HEOM.

    Same cbg correlator and fit as the C1 handler; only the coupling
    operator Q changes from σ_z to σ_x. σ_x couples to the system Bohr
    transitions, so populations relax toward the bath's thermal state
    (Boltzmann ratio P(↑)/P(↓) → exp(-ω/T) in the long-time limit, modulo
    the hierarchy-depth truncation error).
    """
    omega = float(model_spec.get("parameters", {}).get("omega", 1.0))
    heom_opts = dict((solver_options or {}).get("heom") or {})

    env_exp = _build_exp_env_from_cbg(model_spec, heom_opts)

    sigma_z = qutip.sigmaz()
    sigma_x = qutip.sigmax()
    H_S = 0.5 * omega * sigma_z
    Q = sigma_x

    plus = (qutip.basis(2, 0) + qutip.basis(2, 1)).unit()
    rho0 = plus * plus.dag()

    other_opts = {k: v for k, v in (solver_options or {}).items() if k != "heom"}
    merged = {**heom_opts, **other_opts}
    return _run_heom(H_S, Q, env_exp, rho0, t_grid, merged, qutip)


_HANDLERS: dict[tuple[str, str, str, str | None], Any] = {
    ("(omega / 2) * sigma_z", "sigma_z", "thermal", None): _propagate_pure_dephasing_thermal,
    ("(omega / 2) * sigma_z", "sigma_x", "thermal", None): _propagate_spin_boson_sigma_x_thermal,
}

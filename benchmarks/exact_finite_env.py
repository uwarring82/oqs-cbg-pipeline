"""
benchmarks.exact_finite_env — Exact propagation of system+finite environment.

Reference method for small environments. Failure modes:
    - finite-bath size (recurrence times);
    - mode-density approximation of continuous bath;
    - exponential cost in environment dimension.

Failure-mode class: finite-system (per docs/benchmark_protocol.md §2).

Phase B implementation (DG-3 work plan v0.1.0): the generic ``propagate``
routine eigendecomposes the joint system+bath Hamiltonian and partial-
traces over the bath at every time-grid point. A model-specific helper
``build_pure_dephasing_thermal_total`` constructs ``H_total`` and the
factorised initial state for the C1 (pure_dephasing × thermal_bath)
fixture by discretising the ohmic spectral density into a finite set
of independent-bosonic-mode oscillators with truncated Fock spaces.

Anchor: SCHEMA.md v0.1.3; Card C1 v0.1.0; DG-3 work plan v0.1.0 Phase B.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from cbg.bath_correlations import ohmic_spectral_density


def propagate(
    H_total: np.ndarray,
    rho_initial: np.ndarray,
    t_grid: np.ndarray,
    system_dim: int,
    bath_dim: int,
) -> np.ndarray:
    """Exact unitary evolution of the joint system+bath state, partial-traced.

    Eigendecomposes ``H_total = V D V†`` once and evolves
    ``rho_total(t) = V exp(-iDt) V† rho_total(0) V exp(+iDt) V†``
    at each grid time, then partial-traces over the bath subsystem (the
    second tensor factor of the joint Hilbert space) to return the
    reduced system density matrix.

    Parameters
    ----------
    H_total : ndarray, shape (system_dim * bath_dim, system_dim * bath_dim)
        Hermitian joint Hamiltonian. The convention is
        H_total = H_S ⊗ I_B + I_S ⊗ H_B + H_int with the system tensor
        factor first.
    rho_initial : ndarray, shape (system_dim * bath_dim, system_dim * bath_dim)
        Initial joint density matrix. Hermitian, positive semidefinite,
        unit-trace.
    t_grid : ndarray, shape (n_times,)
        Time points at which to evaluate the reduced density matrix.
    system_dim : int
        Hilbert-space dimension of the system subsystem (first tensor
        factor). For C1's qubit, system_dim == 2.
    bath_dim : int
        Hilbert-space dimension of the bath subsystem (second tensor
        factor). For C1's pure_dephasing thermal fixture, bath_dim is
        the product of per-mode level counts.

    Returns
    -------
    rho_system_t : ndarray, shape (n_times, system_dim, system_dim), dtype complex
        Reduced system density matrix at each grid time.

    Raises
    ------
    ValueError
        If shapes are inconsistent, system_dim * bath_dim does not match,
        or H_total is not square.
    """
    H_total = np.asarray(H_total, dtype=complex)
    rho_initial = np.asarray(rho_initial, dtype=complex)
    t_grid = np.asarray(t_grid, dtype=float)

    joint_dim = system_dim * bath_dim
    if H_total.shape != (joint_dim, joint_dim):
        raise ValueError(
            f"propagate: H_total must be ({joint_dim}, {joint_dim}); "
            f"got {H_total.shape} with system_dim={system_dim} bath_dim={bath_dim}"
        )
    if rho_initial.shape != (joint_dim, joint_dim):
        raise ValueError(
            f"propagate: rho_initial must be ({joint_dim}, {joint_dim}); "
            f"got {rho_initial.shape}"
        )
    if t_grid.ndim != 1:
        raise ValueError(f"propagate: t_grid must be 1D; got shape {t_grid.shape}")

    # Eigendecomposition of the joint Hamiltonian.
    eigvals, V = np.linalg.eigh(H_total)
    # Project rho_initial into the energy eigenbasis: rho_E = V† rho V.
    rho_E = V.conj().T @ rho_initial @ V

    n_times = t_grid.size
    rho_system_t = np.empty((n_times, system_dim, system_dim), dtype=complex)

    for k, t in enumerate(t_grid):
        # In the eigenbasis, U(t) is diagonal with entries exp(-i E_n t),
        # so rho_E(t)[m,n] = exp(-i (E_m - E_n) t) rho_E(0)[m,n].
        phase = np.exp(-1j * np.outer(eigvals, np.ones_like(eigvals)) * t)
        phase = phase * np.exp(+1j * np.outer(np.ones_like(eigvals), eigvals) * t)
        rho_E_t = rho_E * phase
        # Back to computational basis.
        rho_total_t = V @ rho_E_t @ V.conj().T
        # Partial trace over the bath (second tensor factor).
        rho_system_t[k] = _partial_trace_bath(rho_total_t, system_dim, bath_dim)

    return rho_system_t


def _partial_trace_bath(
    rho_joint: np.ndarray, system_dim: int, bath_dim: int
) -> np.ndarray:
    """Trace out the bath (second tensor factor) of a joint density matrix.

    Convention: ``rho_joint`` is indexed as ``rho[i_S * bath_dim + i_B, j_S * bath_dim + j_B]``,
    i.e. the system index varies slowly and the bath index varies quickly.
    This matches the result of ``np.kron(A_S, A_B)``.
    """
    return np.trace(
        rho_joint.reshape(system_dim, bath_dim, system_dim, bath_dim),
        axis1=1,
        axis2=3,
    )


# ─── Pure-dephasing thermal-bath helper (C1 thermal case) ───────────────────


def build_pure_dephasing_thermal_total(
    model_spec: dict[str, Any],
    *,
    n_bath_modes: int = 4,
    n_levels_per_mode: int = 4,
    omega_min_factor: float = 0.05,
    omega_max_factor: float = 4.0,
    initial_system_rho: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, int, int]:
    """Build (H_total, rho_initial, system_dim, bath_dim) for the C1 thermal case.

    Discretises the ohmic spectral density from ``model_spec`` into
    ``n_bath_modes`` independent bosonic modes at log-spaced frequencies,
    each with ``n_levels_per_mode`` Fock levels retained. The system is
    a qubit with ``H_S = (omega/2) sigma_z`` and ``A = sigma_z``; the
    interaction is ``H_int = sigma_z ⊗ sum_k g_k (a_k + a_k†)`` with
    discretisation couplings g_k = sqrt(J(ω_k) Δω_k).

    The initial state is factorised: ``rho_initial = rho_S(0) ⊗ rho_B(thermal)``
    where ``rho_B(thermal) = exp(-H_B / T) / Z`` (factorised across modes).

    Parameters
    ----------
    model_spec : dict
        Card's ``frozen_parameters.model`` mapping. Reads:
        - bath_spectral_density: family ('ohmic'), cutoff_frequency, coupling_strength.
        - bath_state.temperature (omega-units).
        - parameters.omega (system Bohr frequency, default 1.0).
    n_bath_modes : int, optional
        Number of discretised bath modes (default 4).
    n_levels_per_mode : int, optional
        Fock-space truncation per mode (default 4).
    omega_min_factor, omega_max_factor : float, optional
        Lower / upper bounds for the discretisation grid, expressed as
        multiples of ``omega_c``. Defaults capture the bulk of the ohmic
        weight (J(0.05 ω_c) ≈ 5e-2 of peak; J(4 ω_c) ≈ 7e-2 of peak).
    initial_system_rho : ndarray, optional
        2x2 initial system density matrix (default: |+⟩⟨+| superposition,
        which exhibits dephasing in the σ_z basis).

    Returns
    -------
    H_total : ndarray, shape (2 * bath_dim, 2 * bath_dim), Hermitian.
    rho_initial : ndarray, same shape, density matrix.
    system_dim : int (always 2).
    bath_dim : int (n_levels_per_mode ** n_bath_modes).

    Raises
    ------
    ValueError
        If model_spec describes an unsupported configuration (non-ohmic,
        non-thermal, non-pure-dephasing).
    """
    # Validate model_spec.
    sd = model_spec.get("bath_spectral_density", {})
    if sd.get("family") != "ohmic":
        raise ValueError(
            f"build_pure_dephasing_thermal_total: requires ohmic spectral "
            f"density; got {sd.get('family')!r}"
        )
    bs = model_spec.get("bath_state", {})
    if bs.get("family") != "thermal":
        raise ValueError(
            f"build_pure_dephasing_thermal_total: requires thermal bath_state; "
            f"got {bs.get('family')!r}"
        )

    alpha = float(sd["coupling_strength"])
    omega_c = float(sd["cutoff_frequency"])
    temperature = float(bs["temperature"])
    omega = float(model_spec.get("parameters", {}).get("omega", 1.0))

    if temperature <= 0.0:
        raise ValueError(
            "build_pure_dephasing_thermal_total: thermal-mode populations "
            "require temperature > 0 (T=0 ground state is a separate path)"
        )

    # Discretisation grid: log-uniform between omega_min and omega_max.
    omega_min = omega_min_factor * omega_c
    omega_max = omega_max_factor * omega_c
    omega_modes = np.geomspace(omega_min, omega_max, n_bath_modes)
    # Discretisation widths: piecewise log-spaced. Use geometric midpoints
    # for the boundary rule.
    log_edges = np.empty(n_bath_modes + 1)
    log_modes = np.log(omega_modes)
    log_edges[1:-1] = 0.5 * (log_modes[:-1] + log_modes[1:])
    log_edges[0] = log_modes[0] - 0.5 * (log_modes[1] - log_modes[0])
    log_edges[-1] = log_modes[-1] + 0.5 * (log_modes[-1] - log_modes[-2])
    domega_modes = np.exp(log_edges[1:]) - np.exp(log_edges[:-1])

    J_modes = ohmic_spectral_density(omega_modes, alpha, omega_c)
    g_modes = np.sqrt(J_modes * domega_modes)  # discretisation couplings

    # Build the bath operators in the truncated Fock space.
    # Per-mode operators (n_levels_per_mode × n_levels_per_mode):
    #   a_k = sum_{n} sqrt(n+1) |n⟩⟨n+1|
    #   a_k† = a_k.T
    n = n_levels_per_mode
    a_single = np.diag(np.sqrt(np.arange(1, n)), k=1)  # shape (n, n)
    adag_single = a_single.T
    n_single = adag_single @ a_single
    I_single = np.eye(n, dtype=complex)

    # Embed each per-mode operator into the full bath Hilbert space
    # (n^n_bath_modes dimensional) via Kronecker products. Build:
    #   H_B = sum_k omega_k a_k† a_k
    #   X_k = a_k + a_k†
    bath_dim = n**n_bath_modes
    H_B = np.zeros((bath_dim, bath_dim), dtype=complex)
    X_modes: list[np.ndarray] = []
    for k in range(n_bath_modes):
        # a_k embedded: kron(I, ..., I, a_single, I, ..., I) with a_single in slot k.
        ops_X = [I_single] * n_bath_modes
        ops_X[k] = a_single + adag_single
        X_k = _kron_chain(ops_X)
        X_modes.append(X_k)

        ops_n = [I_single] * n_bath_modes
        ops_n[k] = n_single
        n_k_full = _kron_chain(ops_n)
        H_B += omega_modes[k] * n_k_full

    # System operators on the joint Hilbert space.
    sigma_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    I_S = np.eye(2, dtype=complex)

    H_S = 0.5 * omega * sigma_z
    H_total = np.kron(H_S, np.eye(bath_dim, dtype=complex)) + np.kron(I_S, H_B)
    for k in range(n_bath_modes):
        H_total += g_modes[k] * np.kron(sigma_z, X_modes[k])

    # Initial bath state: factorised thermal across modes,
    # rho_B = ⊗_k exp(-omega_k a_k† a_k / T) / Z_k.
    levels = np.arange(n)
    per_mode_thermal: list[np.ndarray] = []
    for k in range(n_bath_modes):
        weights = np.exp(-omega_modes[k] * levels / temperature)
        weights /= weights.sum()
        per_mode_thermal.append(np.diag(weights).astype(complex))
    rho_B = _kron_chain(per_mode_thermal)

    if initial_system_rho is None:
        # |+⟩⟨+| in the σ_z basis: dephasing target.
        plus = np.array([[1.0], [1.0]], dtype=complex) / np.sqrt(2.0)
        initial_system_rho = plus @ plus.conj().T
    initial_system_rho = np.asarray(initial_system_rho, dtype=complex)
    if initial_system_rho.shape != (2, 2):
        raise ValueError(
            f"initial_system_rho must be (2, 2); got {initial_system_rho.shape}"
        )

    rho_initial = np.kron(initial_system_rho, rho_B)

    return H_total, rho_initial, 2, bath_dim


def _kron_chain(ops: list[np.ndarray]) -> np.ndarray:
    """Compute kron(ops[0], ops[1], ..., ops[-1])."""
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out

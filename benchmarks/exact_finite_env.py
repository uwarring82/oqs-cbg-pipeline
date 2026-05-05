"""
benchmarks.exact_finite_env — Exact propagation of system+finite environment.

Reference method for small environments. Failure modes:
    - finite-bath size (recurrence times);
    - mode-density approximation of continuous bath;
    - exponential cost in environment dimension.

Failure-mode class: finite-system (per docs/benchmark_protocol.md §2).

Implementation (DG-3 work plan v0.1.0, Phase B + C): the generic
``propagate`` routine eigendecomposes the joint system+bath Hamiltonian
and partial-traces over the bath at every time-grid point. A single
private helper ``_build_spin_joint`` constructs the joint Hilbert
space, the system+bath Hamiltonian, and the factorised initial state
for any 2-level system with a single Hermitian coupling operator and
an ohmic bosonic bath in either a thermal or coherently-displaced
state. The four C1/C2 fixtures are thin wrappers that validate their
spec and dispatch into the helper:

    Card    coupling   bath_state                  wrapper
    ----    --------   --------------------------  -------------------------------------
    C1 a    σ_z        thermal                     build_pure_dephasing_thermal_total
    C1 b    σ_z        displaced (delta-omega_c)   build_pure_dephasing_displaced_total
    C2 a    σ_x        thermal                     build_spin_boson_sigma_x_thermal_total
    C2 b    σ_x        displaced (delta-omega_c)   build_spin_boson_sigma_x_displaced_total

The displacement convention follows cbg.cumulants
``_evaluate_displaced_first_cumulant`` for the Council-cleared
delta-omega_c profile: the discretisation forces one bath mode at
ω_c and the discrete coherent-state amplitude is

    α_disp = α₀ √J(ω_c) / g_c = α₀ / √(Δω_c)

where g_c = √(J(ω_c) Δω_c) is the discretisation coupling at the
resonant mode. This pins ⟨B(t)⟩_discrete = 2 α₀ √J(ω_c) cos(ω_c t),
matching the continuous convention.

Anchor: SCHEMA.md v0.1.3; Cards C1, C2 v0.1.0; DG-3 work plan v0.1.0
Phase B + C.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.linalg import expm

from cbg.bath_correlations import ohmic_spectral_density


# ─── Generic propagation ────────────────────────────────────────────────────


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


def _kron_chain(ops: list[np.ndarray]) -> np.ndarray:
    """Compute kron(ops[0], ops[1], ..., ops[-1])."""
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out


# ─── Single-coupling-operator joint builder (private) ──────────────────────


_SIGMA_Z: np.ndarray = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
_SIGMA_X: np.ndarray = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)


def _build_spin_joint(
    *,
    coupling_op: np.ndarray,
    alpha: float,
    omega_c: float,
    omega: float,
    temperature: float,
    n_bath_modes: int,
    n_levels_per_mode: int,
    omega_min_factor: float,
    omega_max_factor: float,
    initial_system_rho: np.ndarray | None,
    displacement: dict[str, float] | None = None,
) -> tuple[np.ndarray, np.ndarray, int, int]:
    """Build the joint (H_total, rho_initial) for a 2-level system + ohmic bath.

    All four C1/C2 fixtures dispatch into this helper. The system is
    H_S = (omega/2) σ_z; the joint interaction is
    ``coupling_op ⊗ Σ_k g_k (a_k + a_k†)`` with g_k = √(J(ω_k) Δω_k);
    the bath state is factorised thermal across all modes, with the
    resonant mode optionally displaced by ``D(α_disp)`` for the
    Council-cleared delta-omega_c profile.

    Pre-conditions assumed validated by the caller:
        - ``coupling_op`` is a (2, 2) Hermitian matrix.
        - ``alpha >= 0``, ``omega_c > 0``, ``temperature > 0``.
        - ``displacement``, if not None, has keys ``alpha_0`` (real) and
          ``omega_disp`` (positive). The discretisation snaps the
          closest log-spaced mode to ``omega_disp`` so the discrete
          first cumulant matches the continuous convention exactly.

    The function does not validate the spec or the bath-state family;
    callers should check those before dispatching here.
    """
    n = n_levels_per_mode
    omega_min = omega_min_factor * omega_c
    omega_max = omega_max_factor * omega_c
    omega_modes = np.geomspace(omega_min, omega_max, n_bath_modes)

    snap_idx: int | None = None
    if displacement is not None:
        omega_disp = float(displacement["omega_disp"])
        snap_idx = int(np.argmin(np.abs(np.log(omega_modes) - np.log(omega_disp))))
        omega_modes[snap_idx] = omega_disp

    log_modes = np.log(omega_modes)
    log_edges = np.empty(n_bath_modes + 1)
    log_edges[1:-1] = 0.5 * (log_modes[:-1] + log_modes[1:])
    log_edges[0] = log_modes[0] - 0.5 * (log_modes[1] - log_modes[0])
    log_edges[-1] = log_modes[-1] + 0.5 * (log_modes[-1] - log_modes[-2])
    domega_modes = np.exp(log_edges[1:]) - np.exp(log_edges[:-1])

    J_modes = ohmic_spectral_density(omega_modes, alpha, omega_c)
    g_modes = np.sqrt(J_modes * domega_modes)

    a_single = np.diag(np.sqrt(np.arange(1, n)), k=1)
    adag_single = a_single.T
    n_single = adag_single @ a_single
    I_single = np.eye(n, dtype=complex)

    bath_dim = n**n_bath_modes
    H_B = np.zeros((bath_dim, bath_dim), dtype=complex)
    X_modes: list[np.ndarray] = []
    for k in range(n_bath_modes):
        ops_X = [I_single] * n_bath_modes
        ops_X[k] = a_single + adag_single
        X_modes.append(_kron_chain(ops_X))

        ops_n = [I_single] * n_bath_modes
        ops_n[k] = n_single
        H_B += omega_modes[k] * _kron_chain(ops_n)

    I_S = np.eye(2, dtype=complex)
    H_S = 0.5 * omega * _SIGMA_Z
    H_total = np.kron(H_S, np.eye(bath_dim, dtype=complex)) + np.kron(I_S, H_B)
    for k in range(n_bath_modes):
        H_total += g_modes[k] * np.kron(coupling_op, X_modes[k])

    # Coherent-displacement amplitude on the resonant mode (if any).
    alpha_disp: complex | None = None
    if displacement is not None:
        assert snap_idx is not None  # narrowed by the displacement branch above
        g_c = float(g_modes[snap_idx])
        if g_c <= 0.0:
            raise ValueError(
                f"_build_spin_joint: resonant-mode coupling g_c={g_c} non-positive"
            )
        alpha_0 = float(displacement["alpha_0"])
        alpha_disp_continuous = alpha_0 * float(
            np.sqrt(ohmic_spectral_density(displacement["omega_disp"], alpha, omega_c))
        )
        alpha_disp = alpha_disp_continuous / g_c

    levels = np.arange(n)
    per_mode_rho: list[np.ndarray] = []
    for k in range(n_bath_modes):
        weights = np.exp(-omega_modes[k] * levels / temperature)
        weights /= weights.sum()
        rho_mode = np.diag(weights).astype(complex)
        if displacement is not None and k == snap_idx:
            assert alpha_disp is not None
            generator = alpha_disp * adag_single - np.conj(alpha_disp) * a_single
            D = expm(generator)
            rho_mode = D @ rho_mode @ D.conj().T
        per_mode_rho.append(rho_mode)
    rho_B = _kron_chain(per_mode_rho)

    if initial_system_rho is None:
        plus = np.array([[1.0], [1.0]], dtype=complex) / np.sqrt(2.0)
        initial_system_rho = plus @ plus.conj().T
    initial_system_rho = np.asarray(initial_system_rho, dtype=complex)
    if initial_system_rho.shape != (2, 2):
        raise ValueError(
            f"initial_system_rho must be (2, 2); got {initial_system_rho.shape}"
        )

    rho_initial = np.kron(initial_system_rho, rho_B)
    return H_total, rho_initial, 2, bath_dim


# ─── Wrapper validation helpers ─────────────────────────────────────────────


def _read_thermal_spec(model_spec: dict[str, Any], func_name: str) -> tuple[float, float, float, float]:
    """Validate ohmic + thermal + T>0 and return (alpha, omega_c, omega, T).

    ``func_name`` is the public wrapper name; it appears in error messages
    so the caller can identify which builder rejected the spec.
    """
    sd = model_spec.get("bath_spectral_density", {})
    if sd.get("family") != "ohmic":
        raise ValueError(
            f"{func_name}: requires ohmic spectral density; got {sd.get('family')!r}"
        )
    bs = model_spec.get("bath_state", {})
    if bs.get("family") != "thermal":
        raise ValueError(
            f"{func_name}: requires thermal bath_state; got {bs.get('family')!r}"
        )
    alpha = float(sd["coupling_strength"])
    omega_c = float(sd["cutoff_frequency"])
    temperature = float(bs["temperature"])
    omega = float(model_spec.get("parameters", {}).get("omega", 1.0))
    if temperature <= 0.0:
        raise ValueError(
            f"{func_name}: thermal-mode populations require temperature > 0 "
            f"(T=0 ground state is a separate path)"
        )
    return alpha, omega_c, omega, temperature


def _read_displaced_spec(
    model_spec: dict[str, Any], func_name: str
) -> tuple[float, float, float, float, dict[str, float]]:
    """Validate ohmic + coherent_displaced + delta-omega_c + T>0.

    Returns (alpha, omega_c, omega, T, displacement_dict) with the
    displacement dict carrying ``alpha_0`` and ``omega_disp`` as floats.
    """
    sd = model_spec.get("bath_spectral_density", {})
    if sd.get("family") != "ohmic":
        raise ValueError(
            f"{func_name}: requires ohmic spectral density; got {sd.get('family')!r}"
        )
    bs = model_spec.get("bath_state", {})
    if bs.get("family") != "coherent_displaced":
        raise ValueError(
            f"{func_name}: requires coherent_displaced bath_state; "
            f"got {bs.get('family')!r}"
        )
    profile_name = bs.get("displacement_profile")
    if profile_name != "delta-omega_c":
        raise NotImplementedError(
            f"{func_name}: only displacement_profile 'delta-omega_c' is "
            f"implemented at v0.1.0; got {profile_name!r}. Other "
            f"Council-cleared profiles (delta-omega_S, sqrt-J, gaussian) "
            f"are next deferred."
        )
    params = bs.get("parameters") or {}
    if "alpha_0" not in params or "omega_c" not in params:
        raise ValueError(
            f"{func_name}: bath_state.parameters must carry alpha_0 and "
            f"omega_c for the delta-omega_c profile"
        )
    alpha = float(sd["coupling_strength"])
    omega_c_sd = float(sd["cutoff_frequency"])
    omega = float(model_spec.get("parameters", {}).get("omega", 1.0))
    temperature = float(bs.get("temperature", 0.5))
    if temperature <= 0.0:
        raise ValueError(
            f"{func_name}: requires temperature > 0 (displaced T=0 ground "
            f"state is a separate implementation path)"
        )
    displacement = {
        "alpha_0": float(params["alpha_0"]),
        "omega_disp": float(params["omega_c"]),
    }
    return alpha, omega_c_sd, omega, temperature, displacement


# ─── Public builders (thin wrappers around _build_spin_joint) ──────────────


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
    """
    alpha, omega_c, omega, temperature = _read_thermal_spec(
        model_spec, "build_pure_dephasing_thermal_total"
    )
    return _build_spin_joint(
        coupling_op=_SIGMA_Z,
        alpha=alpha,
        omega_c=omega_c,
        omega=omega,
        temperature=temperature,
        n_bath_modes=n_bath_modes,
        n_levels_per_mode=n_levels_per_mode,
        omega_min_factor=omega_min_factor,
        omega_max_factor=omega_max_factor,
        initial_system_rho=initial_system_rho,
        displacement=None,
    )


def build_spin_boson_sigma_x_thermal_total(
    model_spec: dict[str, Any],
    *,
    n_bath_modes: int = 4,
    n_levels_per_mode: int = 4,
    omega_min_factor: float = 0.05,
    omega_max_factor: float = 4.0,
    initial_system_rho: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, int, int]:
    """Build (H_total, rho_initial, system_dim, bath_dim) for the C2 thermal case.

    Identical contract to ``build_pure_dephasing_thermal_total`` but with
    σ_x in the joint interaction. Because [H_S, σ_x] ≠ 0, the σ_z
    populations of ρ_S(t) are NOT conserved — energy relaxation toward
    Boltzmann equilibrium plus coherence loss.
    """
    alpha, omega_c, omega, temperature = _read_thermal_spec(
        model_spec, "build_spin_boson_sigma_x_thermal_total"
    )
    return _build_spin_joint(
        coupling_op=_SIGMA_X,
        alpha=alpha,
        omega_c=omega_c,
        omega=omega,
        temperature=temperature,
        n_bath_modes=n_bath_modes,
        n_levels_per_mode=n_levels_per_mode,
        omega_min_factor=omega_min_factor,
        omega_max_factor=omega_max_factor,
        initial_system_rho=initial_system_rho,
        displacement=None,
    )


def build_pure_dephasing_displaced_total(
    model_spec: dict[str, Any],
    *,
    n_bath_modes: int = 4,
    n_levels_per_mode: int = 4,
    omega_min_factor: float = 0.05,
    omega_max_factor: float = 4.0,
    initial_system_rho: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, int, int]:
    """Build (H_total, rho_initial, system_dim, bath_dim) for the C1 displaced case.

    σ_z coupling under coherent-displaced bath at the Council-cleared
    delta-omega_c profile. The discretisation snaps one mode to ω_c
    and that mode is coherently displaced by

        α_disp = α₀ √J(ω_c) / g_c = α₀ / √(Δω_c)

    so the discrete first cumulant ⟨B(t)⟩_discrete = 2 g_c α_disp cos(ω_c t)
    matches the cbg.cumulants delta-omega_c convention 2 α₀ √J(ω_c) cos(ω_c t).

    Raises
    ------
    NotImplementedError
        If displacement_profile ≠ 'delta-omega_c' (other Council-cleared
        profiles are next deferred).
    ValueError
        For invalid spec (non-ohmic, non-displaced, missing parameters,
        T = 0, etc.).
    """
    alpha, omega_c, omega, temperature, displacement = _read_displaced_spec(
        model_spec, "build_pure_dephasing_displaced_total"
    )
    return _build_spin_joint(
        coupling_op=_SIGMA_Z,
        alpha=alpha,
        omega_c=omega_c,
        omega=omega,
        temperature=temperature,
        n_bath_modes=n_bath_modes,
        n_levels_per_mode=n_levels_per_mode,
        omega_min_factor=omega_min_factor,
        omega_max_factor=omega_max_factor,
        initial_system_rho=initial_system_rho,
        displacement=displacement,
    )


def build_spin_boson_sigma_x_displaced_total(
    model_spec: dict[str, Any],
    *,
    n_bath_modes: int = 4,
    n_levels_per_mode: int = 4,
    omega_min_factor: float = 0.05,
    omega_max_factor: float = 4.0,
    initial_system_rho: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, int, int]:
    """Build (H_total, rho_initial, system_dim, bath_dim) for the C2 displaced case.

    σ_x coupling under coherent-displaced bath (delta-omega_c). Same
    discrete-displacement calibration as the σ_z displaced builder; the
    coupling-operator change adds an effective time-dependent σ_x drive
    in addition to the energy-relaxation channel.
    """
    alpha, omega_c, omega, temperature, displacement = _read_displaced_spec(
        model_spec, "build_spin_boson_sigma_x_displaced_total"
    )
    return _build_spin_joint(
        coupling_op=_SIGMA_X,
        alpha=alpha,
        omega_c=omega_c,
        omega=omega,
        temperature=temperature,
        n_bath_modes=n_bath_modes,
        n_levels_per_mode=n_levels_per_mode,
        omega_min_factor=omega_min_factor,
        omega_max_factor=omega_max_factor,
        initial_system_rho=initial_system_rho,
        displacement=displacement,
    )

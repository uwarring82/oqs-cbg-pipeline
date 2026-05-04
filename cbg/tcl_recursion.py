"""
cbg.tcl_recursion — Recursive construction of the TCL generator L_t.

Implements the recursion described in Companion Eqs. (19)-(28),
yielding L_t = Σ_n λ^n L_n in canonical generalised-Lindblad form
with traceless jump operators at every order.

The recursion uses the generalised cumulants D̄(τ_1^k, s_1^{n-k})
which are evaluated in cbg.cumulants (NOT a Nakajima-Zwanzig
memory kernel — TCL is time-local; see bath_correlations.py docstring).

DG-1 scope (this module, C.8):
    - L_n at orders n in {0, 1, 2}, thermal Gaussian bath only
      (D̄_1 = 0; the displaced-bath case is deferred to DG-2 per the
      operationalisability carve-out in plan v0.1.4 §1.1).
    - L_0[X] = -i [H_S, X].
    - L_1[X] = 0 (thermal: ⟨B⟩ = 0).
    - L_2[X](t) = -∫_0^t du {C(t-u) [A, A_I(u-t) X]
                              + C(t-u)* [X A_I(u-t), A]}
      where C(τ) is the connected bath two-point at the spec's
      temperature (cbg.cumulants.D_bar_2) and A_I(τ) = e^{iH_S τ} A
      e^{-iH_S τ} is the interaction-picture coupling operator.
    - K_n_thermal_on_grid: extracts K_n(t) at every t in t_grid by
      applying Letter Eq. (6) to L_n[F_α](t) for each basis element
      F_α (cbg.basis + cbg.effective_hamiltonian.K_from_generator).
    - K_total_thermal_on_grid: sums K_0 + K_1 + ... + K_{N_card} at
      every t in t_grid; the runner-facing entry point.

DG-2 scope (stubbed):
    - L_n at orders n >= 3 (full Companion Eq. (28) recursion).
    - Non-thermal bath states (D̄_1 ≠ 0); requires the displacement
      convention deferred per plan v0.1.4 §1.1.
    - canonical_lindblad_form: full K + dissipator decomposition with
      traceless jump operators (Companion Eq. (43)). DG-1 cards only
      need K (via Letter Eq. (6) extraction); the dissipator side is
      DG-2.

Anchor: SCHEMA.md v0.1.2; DG-1 work plan v0.1.4 §4 Phase C row C.8.
"""

from __future__ import annotations

from typing import Callable, Dict, Any

import numpy as np
from scipy.linalg import expm

from cbg.basis import matrix_unit_basis
from cbg.cumulants import D_bar_1, D_bar_2
from cbg.effective_hamiltonian import K_from_generator


# ─── Interaction-picture helper ──────────────────────────────────────────────


def interaction_picture(H_S: np.ndarray, A: np.ndarray, tau: float) -> np.ndarray:
    """Compute A_I(τ) = e^{i H_S τ} A e^{-i H_S τ}.

    Used to evolve the system coupling operator A under H_S only (the
    interaction-picture transformation). Vectorising over `tau` is left
    to the caller.

    Parameters
    ----------
    H_S : ndarray
        System Hamiltonian, shape (d, d).
    A : ndarray
        System coupling operator, shape (d, d).
    tau : float
        Interaction-picture time argument; can be positive or negative.

    Returns
    -------
    ndarray, shape (d, d), dtype complex
    """
    U = expm(1j * np.asarray(H_S, dtype=complex) * tau)
    return U @ np.asarray(A, dtype=complex) @ U.conj().T


# ─── L_n at order n (thermal-only path) ──────────────────────────────────────


def L_n_thermal_at_time(
    n: int,
    t_idx: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    D_bar_2_array: np.ndarray | None = None,
) -> Callable[[np.ndarray], np.ndarray]:
    """Return a callable that computes L_n[X] at time t_grid[t_idx] for
    a thermal Gaussian bath.

    Implements:
        - n = 0: L_0[X] = -i [H_S, X] (the bare Liouvillian; not really
          a perturbative term, but supplied here so K_total_thermal can
          uniformly assemble K = K_0 + K_1 + K_2 + ... via Letter Eq. (6)).
        - n = 1: L_1[X] = 0 (thermal Gaussian bath has ⟨B⟩ = 0).
        - n = 2: L_2[X](t) = -∫_0^t du {C(t-u) [A, A_I(u-t) X] +
                                         C(t-u)* [X A_I(u-t), A]}
          via trapezoidal integration over s_grid = t_grid[: t_idx+1].
          The integrand is operator-valued; the trapezoidal rule is
          inlined for efficiency (avoids 4 separate scalar integrations
          per matrix entry).

    Parameters
    ----------
    n : int
        Perturbative order; one of 0, 1, 2 at DG-1.
    t_idx : int
        Index into t_grid at which to evaluate L_n.
    t_grid : ndarray, shape (n_t,)
        Time points; must satisfy t_grid[0] = 0 for the integral lower
        bound to be the physical t_start = 0 (the cards' convention).
    system_hamiltonian, coupling_operator : ndarray, shape (d, d)
        H_S and A.
    D_bar_2_array : ndarray, shape (n_t, n_t), dtype complex
        Precomputed connected two-point on the time grid; required for
        n = 2; ignored for n in {0, 1}. Use cbg.cumulants.D_bar_2 to
        construct.

    Returns
    -------
    callable
        L_n_apply : (X: (d, d) ndarray) -> (d, d) ndarray.

    Raises
    ------
    NotImplementedError
        For n >= 3 (DG-2 territory).
    ValueError
        For invalid arguments.
    """
    if n == 0:
        H_S = np.asarray(system_hamiltonian, dtype=complex)
        return lambda X: -1j * (H_S @ X - X @ H_S)

    if n == 1:
        # Thermal Gaussian bath: D̄_1 = 0 → L_1 = 0 identically.
        # (For non-thermal bath, L_1 would carry a ⟨B(t)⟩-driven term.
        # Deferred to DG-2 per plan v0.1.4 §1.1.)
        return lambda X: np.zeros_like(np.asarray(X, dtype=complex))

    if n == 2:
        if D_bar_2_array is None:
            raise ValueError(
                "L_n_thermal_at_time: n=2 requires D_bar_2_array (use "
                "cbg.cumulants.D_bar_2 to construct)"
            )

        H_S = np.asarray(system_hamiltonian, dtype=complex)
        A = np.asarray(coupling_operator, dtype=complex)
        t_grid = np.asarray(t_grid, dtype=float)
        D = np.asarray(D_bar_2_array, dtype=complex)

        if t_idx < 1:
            # Integration interval has zero length; L_2(t=t_grid[0]) = 0.
            d = A.shape[0]
            return lambda X: np.zeros((d, d), dtype=complex)

        # Pre-compute A_I(u - t) for each s in s_grid = t_grid[:t_idx+1].
        # u = s, u - t = s - t (≤ 0).
        s_grid = t_grid[: t_idx + 1]
        n_s = len(s_grid)
        t_at = t_grid[t_idx]
        A_I_array = np.zeros((n_s, *A.shape), dtype=complex)
        for s_idx in range(n_s):
            tau = s_grid[s_idx] - t_at  # ≤ 0
            A_I_array[s_idx] = interaction_picture(H_S, A, tau)

        # C(t - s) = D̄_2(t, s) (stationary; depends only on the difference).
        C_at = D[t_idx, : t_idx + 1]  # shape (n_s,)
        C_at_conj = np.conj(C_at)

        def L_2_apply(X: np.ndarray) -> np.ndarray:
            X = np.asarray(X, dtype=complex)
            d = X.shape[0]
            # Build integrand[s_idx] = C(t-s) [A, A_I(s-t) X]
            #                          + C(t-s)* [X A_I(s-t), A]
            integrand = np.zeros((n_s, d, d), dtype=complex)
            for s_idx in range(n_s):
                A_I_su = A_I_array[s_idx]
                # [A, A_I X] = A @ A_I @ X - A_I @ X @ A
                term1 = A @ A_I_su @ X - A_I_su @ X @ A
                # [X A_I, A] = X @ A_I @ A - A @ X @ A_I
                term2 = X @ A_I_su @ A - A @ X @ A_I_su
                integrand[s_idx] = C_at[s_idx] * term1 + C_at_conj[s_idx] * term2

            # Trapezoidal integral over s; result is (d, d).
            out = np.zeros((d, d), dtype=complex)
            for i in range(n_s - 1):
                ds = s_grid[i + 1] - s_grid[i]
                out += 0.5 * (integrand[i] + integrand[i + 1]) * ds
            return -out  # the leading minus sign in the TCL2 formula

        return L_2_apply

    raise NotImplementedError(
        f"L_n_thermal_at_time: n={n} not implemented at DG-1. K_n at "
        f"orders n >= 3 is DG-2 territory per Sail v0.5 §9 DG-2 and "
        f"DG-1 work plan v0.1.4 §1.2."
    )


# ─── K_n on the time grid (Letter Eq. (6) extraction) ───────────────────────


def K_n_thermal_on_grid(
    n: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    *,
    bath_state: Dict[str, Any],
    spectral_density: Dict[str, Any],
    basis: list | None = None,
) -> np.ndarray:
    """Compute K_n(t) at every t in t_grid for a thermal Gaussian bath.

    For each t_idx, applies Letter Eq. (6) — K = (1/(2id)) Σ_α [F_α†, L[F_α]] —
    to L_n_thermal_at_time(n, t_idx, ...) using the matrix-unit basis (or
    a caller-supplied HS-orthonormal basis).

    Parameters
    ----------
    n : int
        Perturbative order; one of 0, 1, 2 at DG-1.
    t_grid : ndarray, shape (n_t,)
        Time points.
    system_hamiltonian, coupling_operator : ndarray, shape (d, d)
        H_S and A.
    bath_state, spectral_density : dict
        Card per-case bath_state and bath_spectral_density mappings.
        Used only for n = 2 (where D̄_2 is built); ignored for n in {0, 1}.
    basis : list of (d, d) ndarrays, optional
        HS-orthonormal basis for Letter Eq. (6). Defaults to the
        matrix-unit basis at the system dimension d.

    Returns
    -------
    ndarray, shape (n_t, d, d), dtype complex
        K_n(t_grid).

    Raises
    ------
    NotImplementedError
        If bath_state.family is not "thermal" (non-thermal bath at orders
        ≥ 1 requires the displacement convention deferred per plan v0.1.4).
    """
    if n >= 1:
        family = bath_state.get("family")
        if family != "thermal":
            raise NotImplementedError(
                f"K_n_thermal_on_grid: bath_state.family {family!r} at "
                f"n={n} requires the displacement convention deferred to "
                f"DG-2 per DG-1 work plan v0.1.4 §1.1. Only 'thermal' is "
                f"supported at DG-1 (D̄_1 = 0 by Gaussian symmetry)."
            )

    H_S = np.asarray(system_hamiltonian, dtype=complex)
    A = np.asarray(coupling_operator, dtype=complex)
    t_grid = np.asarray(t_grid, dtype=float)
    d = H_S.shape[0]

    if basis is None:
        basis = matrix_unit_basis(d)

    # For n = 2, precompute the D̄_2 array once (reused across all t_idx).
    D = None
    if n == 2:
        D = D_bar_2(
            t_grid, bath_state=bath_state, spectral_density=spectral_density
        )

    K = np.zeros((len(t_grid), d, d), dtype=complex)
    for t_idx in range(len(t_grid)):
        L_n_apply = L_n_thermal_at_time(
            n, t_idx, t_grid, H_S, A, D_bar_2_array=D
        )
        K[t_idx] = K_from_generator(L_n_apply, basis)
    return K


# ─── Displaced-bath L_n / K_n / K_total (Council Act 2 cleared, 2026-05-04) ──
#
# The displaced-bath path is structurally similar to the thermal path: K_0
# (bare Liouvillian) and K_2 (TCL2 dissipator) are unchanged because D̄_2
# (the connected two-point) is invariant under coherent displacement. The
# only change is K_1, which is non-zero in the displaced case where
# D̄_1(t) ≠ 0:
#
#   L_1^S[X](t) = -i D̄_1(t) [A, X]    (Schrödinger picture)
#
# Applying Letter Eq. (6) to L_1^S gives K_1(t) = D̄_1(t) · (A − Tr(A)/d · I).
# For traceless A (σ_z, σ_x), K_1(t) = D̄_1(t) · A. The runner extracts
# K_1 via K_from_generator without bypassing the basis-summation pipeline
# — preserving the cards-first audit boundary.


def L_1_displaced_at_time(
    t_idx: int,
    coupling_operator: np.ndarray,
    D_bar_1_array: np.ndarray,
) -> Callable[[np.ndarray], np.ndarray]:
    """Schrödinger-picture L_1 generator at t_grid[t_idx] for a coherent-
    displaced bath.

    L_1^S[X](t) = -i D̄_1(t) [A, X]

    Parameters
    ----------
    t_idx : int
        Index into the time grid at which D̄_1 is evaluated.
    coupling_operator : ndarray
        System coupling operator A, shape (d, d).
    D_bar_1_array : ndarray
        Precomputed ⟨B(t)⟩ on the time grid; produced by
        cbg.cumulants.D_bar_1 with the case's bath_state and
        spectral_density.

    Returns
    -------
    callable (X: (d, d) ndarray) -> (d, d) ndarray
    """
    A = np.asarray(coupling_operator, dtype=complex)
    d_bar_1_t = complex(D_bar_1_array[t_idx])

    def L_1_apply(X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=complex)
        return -1j * d_bar_1_t * (A @ X - X @ A)

    return L_1_apply


def K_total_displaced_on_grid(
    N_card: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    *,
    bath_state: Dict[str, Any],
    spectral_density: Dict[str, Any],
    basis: list | None = None,
) -> np.ndarray:
    """Compute K(t) = Σ_{n=0}^{N_card} K_n(t) for a coherent-displaced bath.

    Reuses ``L_n_thermal_at_time`` for n = 0 (bare Liouvillian, bath-state-
    independent) and n = 2 (TCL2 dissipator, D̄_2 invariant under
    displacement). For n = 1, dispatches to ``L_1_displaced_at_time``
    using the per-profile D̄_1 array from ``cbg.cumulants.D_bar_1`` (which
    routes through the Council-cleared displacement-profile registry).

    Parameters
    ----------
    N_card : int
        Perturbative cap (must be in {0, 1, 2} per the existing thermal
        path's range; v0.1.0 cards use N_card = 2).
    t_grid : ndarray, shape (n_t,)
        Time points.
    system_hamiltonian, coupling_operator : ndarray, shape (d, d)
    bath_state : dict
        Must have family == "coherent_displaced" and include the
        ``displacement_profile`` key per the §6.1 registry-clearance-gate.
    spectral_density : dict
        Card bath_spectral_density (ohmic at v0.1.0).
    basis : list of (d, d) ndarrays, optional
        HS-orthonormal basis for Letter Eq. (6); defaults to matrix_unit.

    Returns
    -------
    ndarray, shape (n_t, d, d), dtype complex
        K(t_grid) under the displaced bath.

    Raises
    ------
    ValueError
        If N_card is not a non-negative integer.
    NotImplementedError
        If N_card > 2 (DG-2-recursion territory; out of scope).
    """
    if not isinstance(N_card, int) or isinstance(N_card, bool) or N_card < 0:
        raise ValueError(
            f"K_total_displaced_on_grid: N_card must be a non-negative integer; "
            f"got {N_card!r}"
        )
    if N_card > 2:
        raise NotImplementedError(
            f"K_total_displaced_on_grid: N_card={N_card} not implemented at "
            f"v0.1.0. K_n at orders n >= 3 is out of scope (future K_2-K_4 "
            f"numerical-recursion plan)."
        )
    if bath_state.get("family") != "coherent_displaced":
        raise ValueError(
            f"K_total_displaced_on_grid: bath_state.family must be "
            f"'coherent_displaced'; got {bath_state.get('family')!r}. "
            f"For thermal, use K_total_thermal_on_grid."
        )

    H_S = np.asarray(system_hamiltonian, dtype=complex)
    A = np.asarray(coupling_operator, dtype=complex)
    t_grid = np.asarray(t_grid, dtype=float)
    d = H_S.shape[0]

    if basis is None:
        basis = matrix_unit_basis(d)

    # Precompute D̄_1 (per-profile) and D̄_2 (thermal-baseline; invariant
    # under displacement). D̄_2 needs a temperature; for an unspecified
    # vacuum-baseline displaced state the natural choice is T = 0, but
    # the bath_state may carry a temperature override (e.g. for
    # thermal-on-top-of-displaced studies). At v0.1.0 cards do not set
    # temperature on coherent_displaced bath_states; default to 0.
    D_bar_1_array = D_bar_1(
        t_grid, bath_state=bath_state, spectral_density=spectral_density,
    ) if N_card >= 1 else None

    # For D̄_2 we forward to the existing connected-two-point evaluator
    # at the spec's temperature (or T=0 default). The evaluator already
    # handles bath_state.family == "coherent_displaced" by treating the
    # connected part as the thermal baseline (see cbg.bath_correlations
    # module docstring).
    D_bar_2_array = None
    if N_card >= 2:
        bs_for_d2 = dict(bath_state)
        if "temperature" not in bs_for_d2:
            bs_for_d2["temperature"] = 0.0
        D_bar_2_array = D_bar_2(
            t_grid, bath_state=bs_for_d2, spectral_density=spectral_density,
        )

    K = np.zeros((len(t_grid), d, d), dtype=complex)
    for t_idx in range(len(t_grid)):
        # n = 0: bare Liouvillian (bath-state-independent).
        L0 = L_n_thermal_at_time(0, t_idx, t_grid, H_S, A)
        K[t_idx] += K_from_generator(L0, basis)
        # n = 1: displaced contribution.
        if N_card >= 1:
            L1 = L_1_displaced_at_time(t_idx, A, D_bar_1_array)
            K[t_idx] += K_from_generator(L1, basis)
        # n = 2: TCL2 dissipator (D̄_2 invariant; same as thermal).
        if N_card >= 2:
            L2 = L_n_thermal_at_time(
                2, t_idx, t_grid, H_S, A, D_bar_2_array=D_bar_2_array,
            )
            K[t_idx] += K_from_generator(L2, basis)
    return K


def K_total_thermal_on_grid(
    N_card: int,
    t_grid: np.ndarray,
    system_hamiltonian: np.ndarray,
    coupling_operator: np.ndarray,
    *,
    bath_state: Dict[str, Any],
    spectral_density: Dict[str, Any],
    basis: list | None = None,
) -> np.ndarray:
    """Compute K(t) = Σ_{n=0}^{N_card} K_n(t) at every t in t_grid for a
    thermal Gaussian bath.

    The runner-facing entry point: returns the full effective Hamiltonian
    on the time grid, ready for comparison against a card's expected_outcome.

    Parameters
    ----------
    N_card : int
        Perturbative cap from the card's frozen_parameters.truncation
        .perturbative_order; must be in {0, 1, 2} at DG-1.
    t_grid, system_hamiltonian, coupling_operator, bath_state,
    spectral_density, basis : as in K_n_thermal_on_grid.

    Returns
    -------
    ndarray, shape (n_t, d, d), dtype complex
        K(t_grid).
    """
    if not isinstance(N_card, int) or isinstance(N_card, bool) or N_card < 0:
        raise ValueError(
            f"K_total_thermal_on_grid: N_card must be a non-negative integer; "
            f"got {N_card!r}"
        )
    if N_card > 2:
        raise NotImplementedError(
            f"K_total_thermal_on_grid: N_card={N_card} not implemented at "
            f"DG-1. K_n at orders n >= 3 is DG-2 territory per Sail v0.5 "
            f"§9 DG-2 and DG-1 work plan v0.1.4 §1.2."
        )

    H_S = np.asarray(system_hamiltonian, dtype=complex)
    d = H_S.shape[0]
    K = np.zeros((len(t_grid), d, d), dtype=complex)

    for n in range(N_card + 1):
        K += K_n_thermal_on_grid(
            n, t_grid, system_hamiltonian, coupling_operator,
            bath_state=bath_state, spectral_density=spectral_density,
            basis=basis,
        )
    return K


# ─── Existing-stub-signature shim ────────────────────────────────────────────


def L_n(n: int, **kwargs):
    """Compute the n-th order TCL generator term per Companion Eq. (28).

    DG-1 thin wrapper: routes to L_n_thermal_at_time when called with
    the canonical (t_idx, t_grid, system_hamiltonian, coupling_operator,
    D_bar_2_array) kwargs and a thermal bath state. Other configurations
    raise NotImplementedError with explicit DG-2 routing.

    Callers should generally prefer L_n_thermal_at_time (explicit
    parameters) or K_n_thermal_on_grid (higher-level batched form) over
    this generic-stub shim.
    """
    if n >= 3:
        raise NotImplementedError(
            f"L_n: n={n} not implemented at DG-1; n >= 3 is DG-2 territory."
        )
    bath_state = kwargs.get("bath_state")
    if bath_state is not None and bath_state.get("family") != "thermal":
        raise NotImplementedError(
            "L_n: non-thermal bath at orders >= 1 requires the displacement "
            "convention deferred to DG-2 per plan v0.1.4 §1.1."
        )
    required = ("t_idx", "t_grid", "system_hamiltonian", "coupling_operator")
    missing = [k for k in required if k not in kwargs]
    if missing:
        raise ValueError(
            f"L_n: missing required kwargs {missing}; pass "
            f"(t_idx, t_grid, system_hamiltonian, coupling_operator) "
            f"and (D_bar_2_array for n=2)."
        )
    return L_n_thermal_at_time(
        n=n,
        t_idx=kwargs["t_idx"],
        t_grid=kwargs["t_grid"],
        system_hamiltonian=kwargs["system_hamiltonian"],
        coupling_operator=kwargs["coupling_operator"],
        D_bar_2_array=kwargs.get("D_bar_2_array"),
    )


# ─── Stubbed: full canonical Lindblad decomposition (DG-2) ───────────────────


def canonical_lindblad_form(L_generator: Callable):
    """Decompose L into K (Hamiltonian part) + canonical dissipator with
    traceless jump operators, per Companion Eq. (43).

    DG-1 only needs K (via Letter Eq. (6); use cbg.effective_hamiltonian.
    K_from_generator). The full K + traceless-dissipator decomposition is
    DG-2 territory and stays stubbed here.
    """
    raise NotImplementedError(
        "canonical_lindblad_form: not implemented at DG-1. The K + "
        "traceless-dissipator decomposition (Companion Eq. (43)) is DG-2 "
        "territory; DG-1 cards only need K, which is provided by "
        "cbg.effective_hamiltonian.K_from_generator via Letter Eq. (6)."
    )

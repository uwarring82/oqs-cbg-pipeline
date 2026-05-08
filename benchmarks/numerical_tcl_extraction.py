"""
benchmarks.numerical_tcl_extraction -- DG-4 Path B helpers.

This module is deliberately benchmark-side. It reconstructs and manipulates
finite-environment dynamical maps for the numerical Richardson route recorded
in the DG-4 n=4 deferral. It is not an analytic TCL recursion implementation,
and cbg/ must not import it.

Implemented here:
    - process-tomography assembly of superoperators from basis outputs;
    - raw Schrodinger-picture map reconstruction from exact_finite_env builders;
    - even-amplitude least-squares extraction of Lambda_2 and Lambda_4;
    - order-4 time-local generator reconstruction:
          L_2 = d_t Lambda_2
          L_4 = d_t Lambda_4 - L_2 Lambda_2

The caller is responsible for picture convention and coupling convention. The
exact finite-env adapter returns raw Schrodinger-picture maps; for the
perturbative expansion above, callers should either provide a closed-system
baseline or transform to the interaction picture before fitting. The alpha-grid
runner treats alpha as the interaction-amplitude parameter and writes
``bath_spectral_density.coupling_strength = alpha**2`` by default, because the
finite-env builders discretise g_k proportional to sqrt(coupling_strength).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from scipy.linalg import expm

from cbg.basis import matrix_unit_basis
from cbg.effective_hamiltonian import K_from_generator


@dataclass(frozen=True)
class EvenAlphaFit:
    """Least-squares fit of even alpha-order map coefficients."""

    alpha_values: np.ndarray
    orders: tuple[int, ...]
    coefficients: dict[int, np.ndarray]
    reconstructed: np.ndarray
    residual_norm: float
    relative_residual_norm: float
    rank: int
    singular_values: np.ndarray


@dataclass(frozen=True)
class TCLOrder4Extraction:
    """Numerically extracted second- and fourth-order TCL generators."""

    L2: np.ndarray
    L4: np.ndarray
    dLambda2_dt: np.ndarray
    dLambda4_dt: np.ndarray


ExactEnvBuilder = Callable[..., tuple[np.ndarray, np.ndarray, int, int]]


def identity_superoperator(system_dim: int) -> np.ndarray:
    """Return the identity superoperator in row-major vectorisation."""
    if not isinstance(system_dim, (int, np.integer)) or system_dim < 1:
        raise ValueError(f"system_dim must be a positive integer; got {system_dim!r}")
    return np.eye(system_dim * system_dim, dtype=complex)


def reconstruct_superoperator_from_basis_outputs(
    basis_outputs: np.ndarray,
) -> np.ndarray:
    """Assemble time-indexed superoperators from matrix-unit basis outputs.

    Parameters
    ----------
    basis_outputs:
        Array with shape ``(d*d, n_times, d, d)``. Entry ``basis_outputs[k]``
        is the propagated output for the kth matrix unit from
        ``cbg.basis.matrix_unit_basis(d)``.

    Returns
    -------
    maps:
        Array with shape ``(n_times, d*d, d*d)`` satisfying
        ``vec(output_t) = maps[t] @ vec(input)`` under row-major vectorisation.
    """
    outputs = np.asarray(basis_outputs, dtype=complex)
    if outputs.ndim != 4:
        raise ValueError(
            "basis_outputs must have shape (d*d, n_times, d, d); " f"got {outputs.shape}"
        )
    n_basis, n_times, d_left, d_right = outputs.shape
    if d_left != d_right:
        raise ValueError(f"basis output matrices must be square; got {outputs.shape}")
    if n_basis != d_left * d_left:
        raise ValueError(f"expected d*d={d_left * d_left} basis outputs; got {n_basis}")

    maps = np.empty((n_times, n_basis, n_basis), dtype=complex)
    for col in range(n_basis):
        maps[:, :, col] = outputs[col].reshape(n_times, n_basis)
    return maps


def reconstruct_schrodinger_maps_from_exact_env(
    builder: ExactEnvBuilder,
    model_spec: Mapping[str, Any],
    t_grid: Sequence[float],
    *,
    system_dim: int = 2,
    builder_kwargs: Mapping[str, Any] | None = None,
) -> np.ndarray:
    """Reconstruct raw Schrodinger-picture maps from an exact-env builder.

    ``builder`` must follow the public ``benchmarks.exact_finite_env`` builder
    contract and accept ``initial_system_rho=...``. The tomography inputs are
    matrix units, not necessarily physical density matrices; the finite-env
    propagation is linear in the initial system operator.
    """
    from benchmarks.exact_finite_env import propagate

    t_array = _as_time_grid(t_grid)
    kwargs = dict(builder_kwargs or {})
    outputs: list[np.ndarray] = []
    for basis_op in matrix_unit_basis(system_dim):
        H_total, rho_initial, built_system_dim, bath_dim = builder(
            dict(model_spec), initial_system_rho=basis_op, **kwargs
        )
        if built_system_dim != system_dim:
            raise ValueError(
                f"builder returned system_dim={built_system_dim}; expected {system_dim}"
            )
        outputs.append(propagate(H_total, rho_initial, t_array, system_dim, bath_dim))
    return reconstruct_superoperator_from_basis_outputs(np.asarray(outputs))


def fit_even_alpha_series(
    alpha_values: Sequence[float],
    maps_by_alpha: np.ndarray,
    *,
    orders: Sequence[int] = (2, 4),
    baseline: np.ndarray | None = None,
) -> EvenAlphaFit:
    """Fit ``maps(alpha) = baseline + sum alpha**n Lambda_n``.

    The default baseline is the identity superoperator at every time, which is
    appropriate only after transforming to the interaction picture. For raw
    Schrodinger-picture maps, pass the closed-system map as ``baseline``.
    """
    alphas = _as_alpha_values(alpha_values)
    even_orders = _as_even_orders(orders)
    maps = np.asarray(maps_by_alpha, dtype=complex)
    if maps.ndim != 4:
        raise ValueError(
            "maps_by_alpha must have shape (n_alpha, n_times, m, m); " f"got {maps.shape}"
        )
    if maps.shape[0] != alphas.size:
        raise ValueError(
            f"alpha_values length {alphas.size} does not match maps axis {maps.shape[0]}"
        )
    n_alpha, n_times, op_dim_left, op_dim_right = maps.shape
    if op_dim_left != op_dim_right:
        raise ValueError(f"superoperator matrices must be square; got {maps.shape}")

    base = _broadcast_baseline(baseline, n_times, op_dim_left)
    design = np.column_stack([alphas**order for order in even_orders])
    rank = int(np.linalg.matrix_rank(design))
    if rank < len(even_orders):
        raise ValueError(
            "even-alpha fit is rank-deficient; need enough distinct positive "
            f"alpha values for orders {even_orders}"
        )

    rhs = (maps - base[None, :, :, :]).reshape(n_alpha, -1)
    coeff_flat, _, lstsq_rank, singular_values = np.linalg.lstsq(design, rhs, rcond=None)
    coefficients = {
        order: coeff_flat[idx].reshape(n_times, op_dim_left, op_dim_left)
        for idx, order in enumerate(even_orders)
    }

    reconstructed = np.broadcast_to(base, maps.shape).astype(complex).copy()
    for order in even_orders:
        reconstructed += (alphas[:, None, None, None] ** order) * coefficients[order][None, :, :, :]
    residual_norm = float(np.linalg.norm(maps - reconstructed))
    scale = float(np.linalg.norm(maps - base[None, :, :, :]))
    relative_residual_norm = residual_norm / scale if scale > 0.0 else residual_norm
    return EvenAlphaFit(
        alpha_values=alphas,
        orders=even_orders,
        coefficients=coefficients,
        reconstructed=reconstructed,
        residual_norm=residual_norm,
        relative_residual_norm=relative_residual_norm,
        rank=int(lstsq_rank),
        singular_values=np.asarray(singular_values, dtype=float),
    )


def finite_difference_time_derivative(values: np.ndarray, t_grid: Sequence[float]) -> np.ndarray:
    """Differentiate a time-indexed array along axis 0."""
    array = np.asarray(values, dtype=complex)
    times = _as_time_grid(t_grid)
    if array.shape[0] != times.size:
        raise ValueError(f"values axis 0 has length {array.shape[0]}, but t_grid has {times.size}")
    edge_order: Literal[1, 2] = 2 if times.size >= 3 else 1
    return np.gradient(array, times, axis=0, edge_order=edge_order)


def compose_time_local_superoperators(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return ``left[t] @ right[t]`` for each time index."""
    left_array = _as_time_superoperators(left, "left")
    right_array = _as_time_superoperators(right, "right")
    if left_array.shape != right_array.shape:
        raise ValueError(
            f"left and right must have the same shape; got {left_array.shape} "
            f"and {right_array.shape}"
        )
    return np.einsum("tij,tjk->tik", left_array, right_array)


def adjoint_unitary_superoperator(unitary: np.ndarray) -> np.ndarray:
    """Return the Liouville matrix of ``rho -> U rho U^dagger`` in row-major vec.

    Row-major convention: ``vec(rho)[i*d+j] = rho[i,j]``. Then
    ``vec(A rho B)[i*d+j] = A[i,k] rho[k,l] B[l,j]``, so the Liouville
    matrix of ``rho -> A rho B`` is ``np.kron(A, B.T)``. For
    ``rho -> U rho U^dagger`` this is ``np.kron(U, U.conj())``.
    """
    U = np.asarray(unitary, dtype=complex)
    if U.ndim != 2 or U.shape[0] != U.shape[1]:
        raise ValueError(f"unitary must be square; got shape {U.shape}")
    return np.kron(U, U.conj())


def transform_to_interaction_picture(
    schrodinger_maps: np.ndarray,
    t_grid: Sequence[float],
    system_hamiltonian: np.ndarray,
) -> np.ndarray:
    """Transform raw Schrödinger-picture superoperators to the interaction picture.

    For each time ``t``, computes ``U(t) = expm(-i H_S t)`` and applies
    ``Ad U^dagger(t)`` from the left to the Liouville matrix
    ``Lambda^S(t)``. The result satisfies ``Lambda_0^IP(t) = id`` (the
    closed-system propagator becomes trivial in the interaction picture),
    which is the assumption the order-4 extractor
    ``extract_tcl_generators_order4`` relies on.

    Parameters
    ----------
    schrodinger_maps:
        Time-indexed Liouville matrices in row-major vec convention,
        shape ``(n_t, d*d, d*d)``.
    t_grid:
        Times at which the maps are evaluated.
    system_hamiltonian:
        ``H_S`` as a ``(d, d)`` Hermitian matrix.

    Returns
    -------
    Time-indexed Liouville matrices in the interaction picture, same
    shape as ``schrodinger_maps``.
    """
    times = _as_time_grid(t_grid)
    H_S = np.asarray(system_hamiltonian, dtype=complex)
    if H_S.ndim != 2 or H_S.shape[0] != H_S.shape[1]:
        raise ValueError(f"system_hamiltonian must be square; got shape {H_S.shape}")
    d = H_S.shape[0]
    maps = _as_time_superoperators(schrodinger_maps, "schrodinger_maps")
    if maps.shape[1] != d * d:
        raise ValueError(
            f"schrodinger_maps Liouville dim {maps.shape[1]} does not match "
            f"d*d = {d * d} from system_hamiltonian shape {H_S.shape}"
        )
    if maps.shape[0] != times.size:
        raise ValueError(
            f"schrodinger_maps time axis {maps.shape[0]} does not match "
            f"t_grid size {times.size}"
        )
    out = np.empty_like(maps)
    for ti, t in enumerate(times):
        U_t = expm(-1j * H_S * t)
        # Ad U^dagger acting from the left on Lambda^S in Liouville form:
        # use np.kron(U^dagger, (U^dagger).conj()) = np.kron(U.conj().T, U.T).
        Ad_U_dagger = np.kron(U_t.conj().T, U_t.T)
        out[ti] = Ad_U_dagger @ maps[ti]
    return out


def extract_tcl_generators_order4(
    Lambda2: np.ndarray, Lambda4: np.ndarray, t_grid: Sequence[float]
) -> TCLOrder4Extraction:
    """Extract ``L_2`` and ``L_4`` from fitted map coefficients.

    Uses the interaction-picture order-4 expansion of
    ``L_t = (d/dt Lambda_t) Lambda_t^{-1}``, which collapses to

        L_2 = d_t Lambda_2,
        L_4 = d_t Lambda_4 - L_2 Lambda_2

    only when the closed-system map is the identity at every ``t`` (i.e.
    in the interaction picture, or when ``H_S = 0``). For raw
    Schrödinger-picture maps with ``H_S != 0``, transform first via
    :func:`transform_to_interaction_picture`; otherwise the omitted
    ``Lambda_0^{-1}`` similarity and ``L_0 Lambda_n Lambda_0^{-1}``
    correction terms make the extraction picture-dependent.
    """
    lambda2 = _as_time_superoperators(Lambda2, "Lambda2")
    lambda4 = _as_time_superoperators(Lambda4, "Lambda4")
    if lambda2.shape != lambda4.shape:
        raise ValueError(
            f"Lambda2 and Lambda4 must have the same shape; got {lambda2.shape} "
            f"and {lambda4.shape}"
        )
    dLambda2_dt = finite_difference_time_derivative(lambda2, t_grid)
    dLambda4_dt = finite_difference_time_derivative(lambda4, t_grid)
    L2 = dLambda2_dt
    L4 = dLambda4_dt - compose_time_local_superoperators(L2, lambda2)
    return TCLOrder4Extraction(L2=L2, L4=L4, dLambda2_dt=dLambda2_dt, dLambda4_dt=dLambda4_dt)


def fit_even_alpha_series_from_exact_env(
    builder: ExactEnvBuilder,
    base_model_spec: Mapping[str, Any],
    alpha_values: Sequence[float],
    t_grid: Sequence[float],
    *,
    baseline: np.ndarray | None = None,
    orders: Sequence[int] = (2, 4),
    coupling_path: Sequence[str] = (
        "bath_spectral_density",
        "coupling_strength",
    ),
    coupling_value_from_alpha: Callable[[float], float] | None = None,
    system_dim: int = 2,
    builder_kwargs: Mapping[str, Any] | None = None,
) -> EvenAlphaFit:
    """Reconstruct exact-env maps across alpha values and fit even orders.

    ``alpha_values`` are interaction-amplitude values for the even-power fit.
    By default, the exact-env model receives ``coupling_strength = alpha**2``.
    Pass ``coupling_value_from_alpha`` to override that mapping.
    """
    alphas = _as_alpha_values(alpha_values)
    maps = []
    for alpha in alphas:
        model_spec = deepcopy(dict(base_model_spec))
        coupling_value = (
            float(alpha * alpha)
            if coupling_value_from_alpha is None
            else float(coupling_value_from_alpha(float(alpha)))
        )
        if not np.isfinite(coupling_value) or coupling_value < 0.0:
            raise ValueError(
                "coupling_value_from_alpha must return a finite non-negative value; "
                f"got {coupling_value!r} for alpha={alpha!r}"
            )
        _set_nested_value(model_spec, coupling_path, coupling_value)
        maps.append(
            reconstruct_schrodinger_maps_from_exact_env(
                builder,
                model_spec,
                t_grid,
                system_dim=system_dim,
                builder_kwargs=builder_kwargs,
            )
        )
    return fit_even_alpha_series(
        alphas.tolist(), np.asarray(maps), orders=orders, baseline=baseline
    )


@dataclass(frozen=True)
class DissipatorNormCoefficients:
    """Time-averaged dissipator norm coefficients of L_2 and L_4.

    The norms are *coefficients* in the alpha-power expansion
    ``L_t(alpha) = L_0 + alpha**2 L_2 + alpha**4 L_4 + O(alpha**6)``,
    so they are independent of any specific swept coupling strength.
    The convergence-ratio metric for D1 v0.1.2 evaluates as

        r_4(alpha**2) = alpha**2 * (l4_avg / l2_avg)

    at each swept ``coupling_strength = alpha**2``.

    Attributes
    ----------
    l2_per_t, l4_per_t : ndarray, shape (n_t,)
        Per-grid-time Liouville-Frobenius norm of L_n^dissipator with
        ``L_n^dissipator := L_n + i [K_n, .]`` (the corrected sign per
        DG-4 work plan v0.1.4).
    l2_avg, l4_avg : float
        Time-averaged scalars.
    fit_relative_residual : float
        Path B Richardson polynomial fit's relative residual norm; see
        EvenAlphaFit.
    """

    l2_per_t: np.ndarray
    l4_per_t: np.ndarray
    l2_avg: float
    l4_avg: float
    fit_relative_residual: float


def path_b_dissipator_norm_coefficients(
    builder: ExactEnvBuilder,
    model_spec: Mapping[str, Any],
    t_grid: Sequence[float],
    alpha_values: Sequence[float],
    *,
    system_dim: int = 2,
    builder_kwargs: Mapping[str, Any] | None = None,
    system_hamiltonian: np.ndarray | None = None,
) -> DissipatorNormCoefficients:
    """Path B end-to-end: returns ||L_2^dis|| and ||L_4^dis|| coefficients.

    Pipeline:
      1. Reconstruct Schrödinger-picture maps Lambda_t(alpha) at the
         supplied alpha values via ``fit_even_alpha_series_from_exact_env``.
      2. Subtract the alpha=0 closed-system baseline (the ``Lambda_0``
         coefficient) before fitting, so the extracted ``Lambda_2`` and
         ``Lambda_4`` are clean perturbative coefficients in the
         Schrödinger picture.
      3. Transform the perturbative coefficients to the interaction
         picture via :func:`transform_to_interaction_picture` using
         ``system_hamiltonian``. This is required because the order-4
         extractor ``extract_tcl_generators_order4`` uses the
         interaction-picture formula ``L_2 = d_t Lambda_2``,
         ``L_4 = d_t Lambda_4 - L_2 Lambda_2`` which is the order-4
         expansion of ``L_t = (d/dt Lambda_t) Lambda_t^{-1}`` only when
         ``Lambda_0 = id`` (i.e. in the interaction picture, or when
         ``H_S = 0``). For raw Schrödinger maps with ``H_S != 0`` the
         omitted ``Lambda_0^{-1}`` similarity and ``L_0 Lambda_n
         Lambda_0^{-1}`` correction terms make the extraction
         picture-dependent. After the IP transform, the dissipator
         norms are picture-invariant.
      4. Extract L_2 and L_4 via ``extract_tcl_generators_order4``.
      5. For each grid time t, compute K_n via Letter Eq. (6) on the
         L_n superoperator and form the dissipator residual
         ``L_n^dis = L_n + i [K_n, .]`` (per DG-4 plan v0.1.4 sign).
      6. Take the Liouville-Frobenius norm of L_n^dis at each t, average.

    The returned values are the *coefficients* in the alpha-power
    expansion (alpha-independent). The runner scales them per swept
    ``alpha**2 = coupling_strength``.

    Parameters
    ----------
    system_hamiltonian:
        ``H_S`` as a ``(d, d)`` Hermitian matrix. Required to perform
        the interaction-picture transformation in step 3. Pass
        ``np.zeros((d, d))`` only if the model truly has ``H_S = 0`` (no
        unitary drift); for any non-trivial ``H_S`` this argument is
        load-bearing and omitting it yields a picture-incorrect result.

    See logbook ``2026-05-06_dg-4-path-b-pilot-result.md`` for the
    finite-env extraction floor characterisation, and
    ``2026-05-06_dg-4-pass-path-b-superseded.md`` for the v0.1.1 verdict
    supersedure that forced this picture fix.
    """
    if system_hamiltonian is None:
        raise TypeError(
            "path_b_dissipator_norm_coefficients: system_hamiltonian is "
            "required since the v0.1.2 supersedure (DG-4 work plan v0.1.4 "
            "Phase D). Raw Schrödinger-picture maps must be transformed to "
            "the interaction picture before order-4 extraction; without H_S "
            "the extracted L_n is picture-incorrect for any model with "
            "H_S != 0. Pass np.zeros((d, d)) only if H_S is genuinely zero."
        )
    # The exact-env builder produces raw Schrödinger-picture maps; for the
    # alpha-power expansion we need a baseline (the closed-system map at
    # alpha=0). Compute it explicitly and pass as the fit baseline so the
    # extracted Lambda_2, Lambda_4 are clean perturbative coefficients.
    baseline_spec = deepcopy(dict(model_spec))
    _set_nested_value(baseline_spec, ("bath_spectral_density", "coupling_strength"), 0.0)
    baseline_maps = reconstruct_schrodinger_maps_from_exact_env(
        builder,
        baseline_spec,
        t_grid,
        system_dim=system_dim,
        builder_kwargs=builder_kwargs,
    )

    fit = fit_even_alpha_series_from_exact_env(
        builder,
        model_spec,
        alpha_values,
        t_grid,
        system_dim=system_dim,
        builder_kwargs=builder_kwargs,
        orders=(2, 4),
        baseline=baseline_maps,
    )
    if 2 not in fit.coefficients or 4 not in fit.coefficients:
        raise ValueError(
            "path_b_dissipator_norm_coefficients: Path B fit must include "
            "orders 2 and 4; got coefficients for "
            f"{sorted(fit.coefficients.keys())!r}"
        )
    # Picture transform: Schrödinger -> interaction picture. The fit
    # coefficients Lambda_2, Lambda_4 inherit the Schrödinger picture from
    # the raw exact_finite_env builders; the order-4 extractor below
    # assumes Lambda_0 = id (i.e. the interaction picture), so we conjugate
    # by Ad U^dagger(t) at each grid time before extraction.
    Lambda2_IP = transform_to_interaction_picture(fit.coefficients[2], t_grid, system_hamiltonian)
    Lambda4_IP = transform_to_interaction_picture(fit.coefficients[4], t_grid, system_hamiltonian)
    extraction = extract_tcl_generators_order4(Lambda2_IP, Lambda4_IP, t_grid)
    l2_per_t = _liouville_dissipator_frobenius_norms(extraction.L2, system_dim)
    l4_per_t = _liouville_dissipator_frobenius_norms(extraction.L4, system_dim)
    return DissipatorNormCoefficients(
        l2_per_t=l2_per_t,
        l4_per_t=l4_per_t,
        l2_avg=float(np.mean(l2_per_t)),
        l4_avg=float(np.mean(l4_per_t)),
        fit_relative_residual=float(fit.relative_residual_norm),
    )


def _liouville_dissipator_frobenius_norms(L_array: np.ndarray, system_dim: int) -> np.ndarray:
    """For each t in L_array shape (n_t, d^2, d^2), compute ||L^dis||_F.

    L^dis := L + i [K, .] under the repository convention
    L[X] = -i [K, X] + dissipator (cbg.effective_hamiltonian:82).
    K is extracted from L via Letter Eq. (6) using the matrix-unit basis.
    The returned norm is the Frobenius (= Hilbert-Schmidt) norm of the
    d^2 x d^2 Liouville matrix of L^dis in the matrix-unit basis.
    """
    L_array = np.asarray(L_array, dtype=complex)
    if L_array.ndim != 3:
        raise ValueError(f"L_array must have shape (n_t, d^2, d^2); got {L_array.shape}")
    n_t, d_sq_a, d_sq_b = L_array.shape
    if d_sq_a != d_sq_b or d_sq_a != system_dim * system_dim:
        raise ValueError(f"L_array shape {L_array.shape} inconsistent with system_dim={system_dim}")

    d = system_dim
    basis = matrix_unit_basis(d)
    norms = np.zeros(n_t, dtype=float)
    for t_idx in range(n_t):
        L_matrix = L_array[t_idx]

        def L_apply(X, _M=L_matrix, _d=d):
            return (_M @ X.reshape(_d * _d)).reshape(_d, _d)

        K = K_from_generator(L_apply, basis)
        L_dis_matrix = np.zeros((d * d, d * d), dtype=complex)
        for col, F_col in enumerate(basis):
            L_F = L_apply(F_col) + 1j * (K @ F_col - F_col @ K)
            for row, F_row in enumerate(basis):
                L_dis_matrix[row, col] = np.trace(F_row.conj().T @ L_F)
        norms[t_idx] = float(np.linalg.norm(L_dis_matrix, ord="fro"))
    return norms


def _as_alpha_values(alpha_values: Sequence[float]) -> np.ndarray:
    alphas = np.asarray(alpha_values, dtype=float)
    if alphas.ndim != 1 or alphas.size == 0:
        raise ValueError(f"alpha_values must be a non-empty 1D array; got {alphas.shape}")
    if not np.all(np.isfinite(alphas)):
        raise ValueError("alpha_values must be finite")
    if np.any(alphas <= 0.0):
        raise ValueError("alpha_values must be strictly positive for extraction")
    return alphas


def _as_even_orders(orders: Sequence[int]) -> tuple[int, ...]:
    even_orders = tuple(int(order) for order in orders)
    if len(even_orders) == 0:
        raise ValueError("orders must be non-empty")
    if len(set(even_orders)) != len(even_orders):
        raise ValueError(f"orders must not repeat; got {even_orders}")
    if any(order <= 0 or order % 2 != 0 for order in even_orders):
        raise ValueError(f"orders must be positive even integers; got {even_orders}")
    return even_orders


def _as_time_grid(t_grid: Sequence[float]) -> np.ndarray:
    times = np.asarray(t_grid, dtype=float)
    if times.ndim != 1 or times.size < 2:
        raise ValueError(f"t_grid must be a 1D array with at least two points; got {times.shape}")
    if not np.all(np.isfinite(times)):
        raise ValueError("t_grid must be finite")
    if np.any(np.diff(times) <= 0.0):
        raise ValueError("t_grid must be strictly increasing")
    return times


def _as_time_superoperators(values: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=complex)
    if array.ndim != 3:
        raise ValueError(f"{name} must have shape (n_times, m, m); got {array.shape}")
    if array.shape[1] != array.shape[2]:
        raise ValueError(f"{name} matrices must be square; got {array.shape}")
    return array


def _broadcast_baseline(baseline: np.ndarray | None, n_times: int, op_dim: int) -> np.ndarray:
    if baseline is None:
        return np.broadcast_to(np.eye(op_dim, dtype=complex), (n_times, op_dim, op_dim))
    base = np.asarray(baseline, dtype=complex)
    if base.shape == (op_dim, op_dim):
        return np.broadcast_to(base, (n_times, op_dim, op_dim))
    if base.shape == (n_times, op_dim, op_dim):
        return base
    raise ValueError(
        "baseline must be None, shape (m, m), or shape (n_times, m, m); " f"got {base.shape}"
    )


def _set_nested_value(mapping: dict[str, Any], path: Sequence[str], value: Any) -> None:
    if not path:
        raise ValueError("coupling_path must be non-empty")
    cursor: dict[str, Any] = mapping
    for key in path[:-1]:
        next_value = cursor.get(key)
        if not isinstance(next_value, dict):
            raise ValueError(f"cannot set nested path {tuple(path)!r}; missing {key!r}")
        cursor = next_value
    cursor[str(path[-1])] = value

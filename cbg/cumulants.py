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
      sufficient for K_1 and K_2 in Cards A3 and A4. The full
      left/right ordering machinery of Companion Eq. (24) is DG-2
      territory.

DG-2 territory (stubbed here):
    - General D_bar(τ_1^k, s_1^{n-k}) with mixed left/right indices.
    - Cumulants for n ≥ 3 (recursive subtraction beyond the leading
      product term D̄_1·D̄_1).
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

from typing import Any, Dict

import numpy as np

from cbg.bath_correlations import bath_two_point_thermal_array


# ─── First generalised cumulant D̄_1(t) ─────────────────────────────────────


def D_bar_1(
    t_grid: np.ndarray,
    *,
    bath_state: Dict[str, Any],
    spectral_density: Dict[str, Any] | None = None,
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
        raise ValueError(
            f"D_bar_1: t_grid must be 1D; got shape {t_grid.shape}"
        )

    family = bath_state.get("family")
    if family == "thermal":
        return np.zeros_like(t_grid, dtype=complex)
    if family == "coherent_displaced":
        raise NotImplementedError(
            "D_bar_1: coherent_displaced bath state has an unresolved "
            "convention gap at DG-1. The card spec carries "
            "`displacement_amplitude` but no displacement-mode frequency "
            "or envelope; ⟨B(t)⟩ is a model-specific assembly. "
            "Resolution paths: (1) encode the convention in "
            "cbg.models.<model>.bath_first_moment(...); "
            "(2) supersede Cards A3/A4 to defer the displaced sub-claims "
            "to DG-2 (parallel to Entry 1.B.3 deferral). "
            "See cbg.cumulants module docstring for the full rationale."
        )
    raise NotImplementedError(
        f"D_bar_1: bath_state.family {family!r} not implemented at DG-1. "
        f"Supported: 'thermal' (zero by symmetry); 'coherent_displaced' "
        f"(stubbed pending convention)."
    )


# ─── Second generalised cumulant D̄_2(τ, s) ─────────────────────────────────


def D_bar_2(
    t_grid: np.ndarray,
    *,
    bath_state: Dict[str, Any],
    spectral_density: Dict[str, Any],
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
        t_grid, alpha, omega_c, temperature
    )


# ─── Generic D_bar dispatch (existing-stub signature) ───────────────────────


def D_bar(tau_args, s_args, **kwargs):
    """Compute the generalised cumulant D̄(τ_1^k, s_1^{n-k}) by recursion.

    Implements the recursive subtraction of Letter Eq. (17) /
    Companion Eq. (27):

        D̄(τ_1^k, s_1^{n-k}) = D(τ_1^k, s_1^{n-k})
                              - Σ_{l,r} D̄(τ_1^l, s_1^r) ·
                                        D̄(τ_{l+1}^k, s_{r+1}^{n-k})

    DG-1 implements the leaf cases for the canonical time-ordered
    cumulants used by Cards A3 and A4:

        - k=1, n-k=0 (single τ argument) → D̄_1 = D_1 = ⟨B(τ)⟩.
        - k=2, n-k=0 (two τ arguments)   → D̄_2 = D_2 - D_1 ⊗ D_1
                                                 = connected two-point.

    For the canonical (all-left, time-ordered) DG-1 use cases, callers
    should prefer D_bar_1(t_grid, ...) and D_bar_2(t_grid, ...), which
    return precomputed (n,) and (n, n) arrays respectively. The
    array-form helpers compose efficiently with cbg.tcl_recursion.

    Mixed left/right indices (k != n) and orders n ≥ 3 are DG-2
    territory and raise NotImplementedError here.

    Parameters
    ----------
    tau_args : tuple of float
        Left-time arguments (τ_1, ..., τ_k).
    s_args : tuple of float
        Right-time arguments (s_1, ..., s_{n-k}).
    **kwargs
        bath_state, spectral_density (as for D_bar_1, D_bar_2).

    Raises
    ------
    NotImplementedError
        For mixed left/right indices, or for total order n ≥ 3.
    """
    n_left = len(tau_args)
    n_right = len(s_args)
    n_total = n_left + n_right

    if n_right > 0:
        raise NotImplementedError(
            "D_bar: mixed left/right ordering (s_args non-empty) is DG-2 "
            "territory. The canonical all-left time-ordered cumulants "
            "(s_args=()) are sufficient for Cards A3 and A4 at orders <= 2; "
            "use D_bar_1 / D_bar_2 array helpers."
        )
    if n_total >= 3:
        raise NotImplementedError(
            f"D_bar: total order n={n_total} not implemented at DG-1. "
            f"K_n at orders n >= 3 is DG-2 territory per Sail v0.5 §9 DG-2 "
            f"and DG-1 work plan v0.1.3 §1.2."
        )

    # n_total in {1, 2} with all-left ordering: thin wrappers over the
    # array-form helpers, sampled at the requested time arguments.
    bath_state = kwargs.get("bath_state")
    spectral_density = kwargs.get("spectral_density")
    if bath_state is None:
        raise ValueError("D_bar: bath_state kwarg required")

    t_grid = np.asarray(tau_args, dtype=float)
    if n_total == 1:
        return D_bar_1(t_grid, bath_state=bath_state,
                       spectral_density=spectral_density)
    # n_total == 2
    if spectral_density is None:
        raise ValueError("D_bar: spectral_density kwarg required for n=2")
    arr = D_bar_2(t_grid, bath_state=bath_state,
                  spectral_density=spectral_density)
    # arr is (2, 2); the requested cumulant is arr[0, 1] (or arr[1, 0]
    # by Hermiticity). Return the [0, 1] entry — D̄_2(τ_1, τ_2).
    return arr[0, 1]

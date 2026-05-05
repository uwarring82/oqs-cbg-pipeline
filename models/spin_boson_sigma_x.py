"""
models.spin_boson_sigma_x — Unbiased spin-boson, A = sigma_x, thermal bath.

Reproduces CL-2026-005 v0.4 Entry 4 within the current validity envelope:
the DG-1 thermal sub-case is covered by Card A4 v0.1.1, and the
coherent-displaced Entry 4.B.2 structural sub-claim is covered by
Card B5-conv-registry v0.2.0 under the Council-cleared displacement
profile registry.
    For H_S = (omega/2) sigma_z, A = sigma_x, thermal bosonic bath:
    odd-order contributions to K vanish; even orders are diagonal in
    sigma_z. Eigenbasis of H_S is NOT rotated by the interaction (the
    parity-class theorem of Letter Eqs. (D.4)-(D.6)).

Structural constraints declared for DG-2:
    - basis-independence of K (universal default);
    - parity rule: K_2m+1 = 0 (Letter App. D);
    - K diagonal in sigma_z basis at all orders.

Numerical anchor:
    Gatto, Colla, Breuer, Thoss, PRA 110, 032210 (2024) had reported
    numerical evidence; the present Letter provides the analytic proof.

Implemented scope:
    - hamiltonian(omega, omegas=None, gs=None): H_S = (omega/2) sigma_z.
      The omegas / gs arguments are kept in the signature for backward
      compatibility with the original v0.1.0 stub (which anticipated
      explicit-bath-mode constructions); they are ignored at DG-1, where
      the bath is treated via continuum spectral density in
      cbg.bath_correlations.
    - coupling_operator(): A = sigma_x.
    - system_arrays_from_spec(model_spec): runner-facing factory; reads
      a card's frozen_parameters.model dict and returns (H_S, A) numpy
      arrays after validating the symbolic strings match the expected
      sigma_x-coupling form.

Convention: same omega-units convention as models.pure_dephasing
(omega = 1.0 by default; see that module's docstring).

Anchor: SCHEMA.md v0.1.2; Cards A4 and B5-conv-registry.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

structural_constraints = (
    "basis_independence",
    "parity_rule_odd_orders_vanish",
    "K_diagonal_in_sigma_z",
)


_SIGMA_X = np.array([[0, 1], [1, 0]], dtype=complex)
_SIGMA_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def hamiltonian(
    omega: float,
    omegas: Sequence[float] | None = None,
    gs: Sequence[float] | None = None,
) -> np.ndarray:
    """H_S = (omega / 2) sigma_z.

    Parameters
    ----------
    omega : float
        System frequency. omega = 1.0 by convention in DG-1 cards.
    omegas, gs : sequence of float, optional
        Explicit bath-mode frequencies and couplings. Retained in the
        signature for backward compatibility with v0.1.0 stub
        expectations; ignored at DG-1, where the bath is represented
        via continuum spectral density in cbg.bath_correlations.

    Returns
    -------
    ndarray, shape (2, 2), dtype complex
    """
    # omegas / gs deliberately ignored at DG-1.
    del omegas, gs
    return 0.5 * float(omega) * _SIGMA_Z


def coupling_operator() -> np.ndarray:
    """A = sigma_x (orthogonal to H_S; the structurally-distinguishing
    feature vs. models.pure_dephasing)."""
    return _SIGMA_X.copy()


_EXPECTED_SYSTEM_HAMILTONIAN = "(omega / 2) * sigma_z"
_EXPECTED_COUPLING_OPERATOR = "sigma_x"


def system_arrays_from_spec(model_spec: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """Build (H_S, A) numpy arrays from a card's frozen_parameters.model dict.

    Validates:
        - system_dimension == 2
        - system_hamiltonian == "(omega / 2) * sigma_z"
        - coupling_operator == "sigma_x"

    Returns H_S = (omega/2) sigma_z with omega = 1.0, and A = sigma_x.

    Raises
    ------
    ValueError
        On any validation mismatch.
    """
    d = model_spec.get("system_dimension")
    if d != 2:
        raise ValueError(
            f"spin_boson_sigma_x.system_arrays_from_spec: system_dimension " f"must be 2; got {d!r}"
        )

    h_str = (model_spec.get("system_hamiltonian") or "").strip()
    if h_str != _EXPECTED_SYSTEM_HAMILTONIAN:
        raise ValueError(
            f"spin_boson_sigma_x.system_arrays_from_spec: system_hamiltonian "
            f"must equal {_EXPECTED_SYSTEM_HAMILTONIAN!r}; got {h_str!r}"
        )

    a_str = (model_spec.get("coupling_operator") or "").strip()
    if a_str != _EXPECTED_COUPLING_OPERATOR:
        raise ValueError(
            f"spin_boson_sigma_x.system_arrays_from_spec: coupling_operator "
            f"must equal {_EXPECTED_COUPLING_OPERATOR!r}; got {a_str!r}"
        )

    omega = 1.0
    return hamiltonian(omega), coupling_operator()

"""
models.pure_dephasing — Spin under pure dephasing, A = sigma_z.

Reproduces CL-2026-005 v0.4 Entry 3 within the current validity envelope:
the DG-1 thermal sub-case is covered by Card A3 v0.1.1, and the
coherent-displaced Entry 3.B.3 structural sub-claim is covered by
Card B4-conv-registry v0.1.0 under the Council-cleared displacement
profile registry.

For H_S = (omega/2) sigma_z and A = sigma_z, K(t) = (omega_r(t)/2) sigma_z;
even-order contributions vanish; odd-order contributions are proportional
to sigma_z. For thermal Fock-diagonal initial bath states, omega_r(t) = omega
at all orders (Łuczka 1990; Doll et al. 2008; Leggett et al. 1987).

Structural constraints declared for DG-2:
    - basis-independence of K (universal default);
    - parity rule: K_2m = 0 (Letter App. D);
    - K_2m+1 ∝ sigma_z;
    - for thermal bath (diagonal in Fock basis), all odd cumulants of B
      vanish, hence K(t) = (omega/2) sigma_z (no renormalisation, recovers
      Łuczka 1990 / Doll 2008 / Leggett 1987).

Implemented scope:
    - hamiltonian(omega): H_S = (omega/2) sigma_z.
    - coupling_operator(): A = sigma_z.
    - system_arrays_from_spec(model_spec): runner-facing factory; reads
      a card's frozen_parameters.model dict and returns (H_S, A) numpy
      arrays after validating the symbolic strings match the expected
      pure-dephasing form.

Convention: cards A3 v0.1.1's `system_hamiltonian: "(omega / 2) * sigma_z"`
is symbolic with omega = 1.0 in the cards' omega-units convention (time
grid in 1/omega units; bath cutoff and temperature in omega-units). The
runner factory hardcodes omega = 1.0; future cards that wish to override
should add a `parameters: {omega: ...}` block at model level (not
currently supported by the schema's model block — would be a v0.1.x
schema extension).

Anchor: SCHEMA.md v0.1.2; Cards A3 and B4-conv-registry.
"""

from __future__ import annotations

from typing import Any

import numpy as np

structural_constraints = (
    "basis_independence",
    "parity_rule_even_orders_vanish",
    "odd_orders_proportional_to_sigma_z",
)


# Pauli-z (the single matrix this model needs at DG-1; both H_S and A
# are proportional to sigma_z).
_SIGMA_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def hamiltonian(omega: float) -> np.ndarray:
    """H_S = (omega / 2) sigma_z.

    Parameters
    ----------
    omega : float
        System frequency. For DG-1 cards (A3 v0.1.1), the convention is
        omega = 1.0 in omega-units.

    Returns
    -------
    ndarray, shape (2, 2), dtype complex
    """
    return 0.5 * float(omega) * _SIGMA_Z


def coupling_operator() -> np.ndarray:
    """A = sigma_z (pure dephasing: coupling commutes with H_S)."""
    return _SIGMA_Z.copy()


# Required symbolic-string forms in the YAML spec (validated by
# system_arrays_from_spec). Whitespace must match exactly; the schema's
# Phase B card-drafting discipline produces these forms verbatim.
_EXPECTED_SYSTEM_HAMILTONIAN = "(omega / 2) * sigma_z"
_EXPECTED_COUPLING_OPERATOR = "sigma_z"


def system_arrays_from_spec(model_spec: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """Build (H_S, A) numpy arrays from a card's frozen_parameters.model dict.

    Validates:
        - system_dimension == 2
        - system_hamiltonian == "(omega / 2) * sigma_z"
        - coupling_operator == "sigma_z"

    Returns H_S = (omega/2) sigma_z with omega = 1.0 (omega-units convention),
    and A = sigma_z.

    Parameters
    ----------
    model_spec : dict
        The card's frozen_parameters.model mapping.

    Returns
    -------
    tuple (H_S, A) : (ndarray, ndarray), each shape (2, 2), dtype complex.

    Raises
    ------
    ValueError
        On any validation mismatch (with a descriptive message).
    """
    d = model_spec.get("system_dimension")
    if d != 2:
        raise ValueError(
            f"pure_dephasing.system_arrays_from_spec: system_dimension must " f"be 2; got {d!r}"
        )

    h_str = (model_spec.get("system_hamiltonian") or "").strip()
    if h_str != _EXPECTED_SYSTEM_HAMILTONIAN:
        raise ValueError(
            f"pure_dephasing.system_arrays_from_spec: system_hamiltonian "
            f"must equal {_EXPECTED_SYSTEM_HAMILTONIAN!r}; got {h_str!r}"
        )

    a_str = (model_spec.get("coupling_operator") or "").strip()
    if a_str != _EXPECTED_COUPLING_OPERATOR:
        raise ValueError(
            f"pure_dephasing.system_arrays_from_spec: coupling_operator "
            f"must equal {_EXPECTED_COUPLING_OPERATOR!r}; got {a_str!r}"
        )

    omega = 1.0  # omega-units convention; see module docstring
    return hamiltonian(omega), coupling_operator()

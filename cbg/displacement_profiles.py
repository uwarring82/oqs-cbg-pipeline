"""
cbg.displacement_profiles — Council-cleared displacement-mode profiles.

This module hosts the registered spectral-displacement profiles α(ω) for the
coherently-displaced bath state appearing in CL-2026-005 v0.4 Entries 3.B.3
(pure-dephasing time-dependent shift) and 4.B.2 (σ_x eigenbasis rotation).

The four registered profiles correspond to the displacement-profile registry
cleared by Council-3 ADM-EC at Act 2 (2026-05-04) under handling (c) of
CL-2026-005 v0.4 subsidiary briefing §4.3 — see
``ledger/CL-2026-005_v0.4_council-deliberation_act2_2026-05-04.md`` for the
sealed deliberation transcript and ``ledger/CL-2026-005_v0.4_council-
briefing_displacement-convention.md`` v0.3.0 §3.1–§3.4 + §6.1 for the
clearance scope and the registry-clearance-gate.

Profiles are returned as ``DisplacementProfile`` records (``kind`` + ``params``)
rather than callables ω→complex, because three of the four registered profiles
are distributions (δ-functions) or carry a callable spectral-density input
that is more naturally inspected structurally than as a single λ-function.
The cumulant module (``cbg.cumulants``) consumes the structured form and
dispatches per ``kind`` to compute D̄_1(t), D̄_3(t), … under the chosen
profile. That dispatch is verdict-commit work for the B4-conv-registry card
lineage; this module supplies the schema only.

Registry-clearance-gate
-----------------------

The four profiles below were Council-cleared as the *initial admissible
registry* at Act 2. Adding or removing profiles requires fresh Council
clearance recorded in the Sail's revision log. Under no circumstances is a
profile to be added at the Steward's discretion; doing so would erode the
discipline that handling (c) was selected to preserve (Act 2 Architect D-iii
+ Act 2 Verdicts §Architect amendment ratified).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict


@dataclass(frozen=True)
class DisplacementProfile:
    """Structured representation of a coherent-displacement spectral profile α(ω).

    Attributes
    ----------
    kind : str
        One of ``"delta"``, ``"broadband"``, ``"gaussian"``. Identifies the
        functional form of α(ω); the cumulant module dispatches on this field.
    params : dict
        Profile-specific parameters. The required keys depend on ``kind``:

        - ``kind="delta"`` requires ``omega`` (float, the Dirac centre) and
          ``amplitude`` (complex or real).
        - ``kind="broadband"`` requires ``alpha_0`` (real prefactor) and
          ``J`` (callable ω→float, the bath spectral density).
        - ``kind="gaussian"`` requires ``alpha_0`` (real prefactor),
          ``omega_d`` (real, envelope centre), and ``Delta_omega`` (positive
          real, envelope width).

    Notes
    -----
    The dataclass is frozen for hashability and to prevent in-place
    parameter drift. Construct via the four registered constructor functions
    below, not directly — the constructors apply per-profile validation.
    """

    kind: str
    params: Dict[str, Any] = field(default_factory=dict)


def delta_omega_c(alpha_0: float, omega_c: float) -> DisplacementProfile:
    """Single-mode coherent-displacement profile at the bath cutoff ω_c.

    Subsidiary briefing v0.3.0 §3.1; registry key ``delta-omega_c``.

    α(ω) = α_0 · δ(ω − ω_c). D̄_1(t) reduces to a single-frequency oscillation
    at ω_c.

    Parameters
    ----------
    alpha_0 : float
        Real-valued displacement amplitude on the resonant bath mode at ω_c.
    omega_c : float
        Bath cutoff frequency (must be positive). In ω-units, this is
        typically the Letter's ω_c (10.0 in the DG-1 spectral-density frame).

    Returns
    -------
    DisplacementProfile
        ``kind="delta"`` with ``omega = omega_c`` and ``amplitude = alpha_0``.

    Raises
    ------
    ValueError
        If ``omega_c`` is non-positive.
    """
    if omega_c <= 0.0:
        raise ValueError(
            f"delta_omega_c: omega_c must be positive (bath cutoff "
            f"frequency); got {omega_c!r}"
        )
    return DisplacementProfile(
        kind="delta",
        params={"omega": float(omega_c), "amplitude": float(alpha_0)},
    )


def delta_omega_S(alpha_0: float, omega_S: float) -> DisplacementProfile:
    """Single-mode coherent-displacement profile at the system Bohr frequency ω_S.

    Subsidiary briefing v0.3.0 §3.2; registry key ``delta-omega_S``.

    α(ω) = α_0 · δ(ω − ω_S). Maximises the resonant interaction with the
    system; tests the parity-class theorem most sharply at the system
    frequency.

    Parameters
    ----------
    alpha_0 : float
        Real-valued displacement amplitude on the resonant bath mode at ω_S.
    omega_S : float
        System Bohr frequency (must be positive). In ω-units, this is
        typically the Letter's ω (1.0 in the DG-1 spectral-density frame).

    Returns
    -------
    DisplacementProfile
        ``kind="delta"`` with ``omega = omega_S`` and ``amplitude = alpha_0``.

    Raises
    ------
    ValueError
        If ``omega_S`` is non-positive.
    """
    if omega_S <= 0.0:
        raise ValueError(
            f"delta_omega_S: omega_S must be positive (system Bohr "
            f"frequency); got {omega_S!r}"
        )
    return DisplacementProfile(
        kind="delta",
        params={"omega": float(omega_S), "amplitude": float(alpha_0)},
    )


def sqrt_J(alpha_0: float, J: Callable[[float], float]) -> DisplacementProfile:
    """Broadband coherent-displacement profile matched to √J(ω).

    Subsidiary briefing v0.3.0 §3.3; registry key ``sqrt-J``.

    α(ω) ∝ α_0 · √(J(ω)) on the bath spectrum. Physically natural for a
    "coherently-displaced thermal-perturbation analog" picture, where the
    displacement spectrum follows the bath's own coupling profile.
    D̄_1(t) is then an integral over the bath spectrum with the J-matched
    envelope.

    Parameters
    ----------
    alpha_0 : float
        Real-valued displacement-amplitude prefactor.
    J : callable
        Bath spectral density J(ω). Must be a callable ω→float defined for
        ω ≥ 0; the cumulant integral will sample J(ω) at quadrature points.

    Returns
    -------
    DisplacementProfile
        ``kind="broadband"`` with ``alpha_0`` and ``J``.

    Raises
    ------
    ValueError
        If ``J`` is not callable.
    """
    if not callable(J):
        raise ValueError(
            f"sqrt_J: J must be callable ω→float (bath spectral density); "
            f"got {type(J).__name__}"
        )
    return DisplacementProfile(
        kind="broadband",
        params={"alpha_0": float(alpha_0), "J": J},
    )


def gaussian(
    alpha_0: float, omega_d: float, Delta_omega: float,
) -> DisplacementProfile:
    """Specified-bandwidth Gaussian-envelope coherent-displacement profile.

    Subsidiary briefing v0.3.0 §3.4; registry key ``gaussian``.

    α(ω) = α_0 · exp(−(ω − ω_d)² / (2 Δω²)). Most general of the four
    registered profiles; reduces to ``delta-omega_c`` as Δω → 0 with ω_d = ω_c,
    to ``delta-omega_S`` as Δω → 0 with ω_d = ω_S, and approximates
    ``sqrt-J`` for an appropriate envelope match.

    Parameters
    ----------
    alpha_0 : float
        Real-valued displacement-amplitude prefactor.
    omega_d : float
        Centre frequency of the Gaussian envelope (must be positive in the
        physical bath spectrum, but the constructor only enforces the
        non-zero precondition; non-positive ω_d is unphysical for an
        ordinary bath but admissible for analytic-continuation studies).
    Delta_omega : float
        Envelope bandwidth (must be strictly positive; Δω = 0 collapses to a
        δ-function and would belong in ``delta_omega_c`` / ``delta_omega_S``).

    Returns
    -------
    DisplacementProfile
        ``kind="gaussian"`` with ``alpha_0``, ``omega_d``, ``Delta_omega``.

    Raises
    ------
    ValueError
        If ``Delta_omega`` is non-positive.
    """
    if Delta_omega <= 0.0:
        raise ValueError(
            f"gaussian: Delta_omega must be positive (Gaussian envelope "
            f"bandwidth); got {Delta_omega!r}. For Δω → 0 collapse, use "
            f"delta_omega_c or delta_omega_S."
        )
    return DisplacementProfile(
        kind="gaussian",
        params={
            "alpha_0": float(alpha_0),
            "omega_d": float(omega_d),
            "Delta_omega": float(Delta_omega),
        },
    )


# ─── Council-cleared profile registry (Act 2, 2026-05-04) ─────────────────────
#
# Mapping: registry key → constructor function.
#
# These four entries are the v0.1.0 admissible set per Council Act 2. Adding
# or removing entries requires fresh Council clearance recorded in the Sail's
# revision log (subsidiary briefing v0.3.0 §6.1 registry-clearance-gate).
#
# The runner-level analog lives in ``reporting.benchmark_card`` as
# ``_DISPLACEMENT_PROFILES``, importing these constructors by name.

REGISTERED_PROFILES: Dict[str, Callable[..., DisplacementProfile]] = {
    "delta-omega_c": delta_omega_c,
    "delta-omega_S": delta_omega_S,
    "sqrt-J": sqrt_J,
    "gaussian": gaussian,
}

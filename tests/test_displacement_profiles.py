# SPDX-License-Identifier: MIT
"""Behaviour tests for cbg.displacement_profiles (DG-2 Council Act 2 cleared).

Verifies the four Council-cleared displacement-mode profile constructors and
the REGISTERED_PROFILES dictionary used by the runner-level
``_DISPLACEMENT_PROFILES`` registry. Per the registry-clearance-gate
(subsidiary briefing v0.3.0 §6.1), the registry surface itself is part of
the test envelope: extending or contracting REGISTERED_PROFILES requires
fresh Council clearance, so the test asserts the v0.1.0 contents verbatim.
"""

from __future__ import annotations

import pytest

from cbg.displacement_profiles import (
    REGISTERED_PROFILES,
    DisplacementProfile,
    delta_omega_c,
    delta_omega_S,
    gaussian,
    sqrt_J,
)

# ─── DisplacementProfile dataclass ──────────────────────────────────────────


def test_displacement_profile_is_frozen():
    """Frozen dataclass: in-place parameter drift is forbidden."""
    p = DisplacementProfile(kind="delta", params={"omega": 1.0, "amplitude": 0.5})
    with pytest.raises((AttributeError, Exception)):
        p.kind = "broadband"  # type: ignore[misc]


def test_displacement_profile_default_params_is_empty_dict():
    p = DisplacementProfile(kind="delta")
    assert p.params == {}


# ─── delta_omega_c (registry key: delta-omega_c) ────────────────────────────


def test_delta_omega_c_returns_delta_kind():
    p = delta_omega_c(alpha_0=1.0, omega_c=10.0)
    assert p.kind == "delta"
    assert p.params == {"omega": 10.0, "amplitude": 1.0}


def test_delta_omega_c_rejects_non_positive_cutoff():
    with pytest.raises(ValueError, match="omega_c must be positive"):
        delta_omega_c(alpha_0=1.0, omega_c=0.0)
    with pytest.raises(ValueError, match="omega_c must be positive"):
        delta_omega_c(alpha_0=1.0, omega_c=-1.0)


def test_delta_omega_c_coerces_to_float():
    """Integer inputs are coerced to float for hashability + numerical determinism."""
    p = delta_omega_c(alpha_0=1, omega_c=10)
    assert isinstance(p.params["omega"], float)
    assert isinstance(p.params["amplitude"], float)


# ─── delta_omega_S (registry key: delta-omega_S) ────────────────────────────


def test_delta_omega_S_returns_delta_kind():
    p = delta_omega_S(alpha_0=1.0, omega_S=1.0)
    assert p.kind == "delta"
    assert p.params == {"omega": 1.0, "amplitude": 1.0}


def test_delta_omega_S_rejects_non_positive_system_frequency():
    with pytest.raises(ValueError, match="omega_S must be positive"):
        delta_omega_S(alpha_0=1.0, omega_S=0.0)
    with pytest.raises(ValueError, match="omega_S must be positive"):
        delta_omega_S(alpha_0=1.0, omega_S=-2.5)


def test_delta_omega_S_distinguished_from_delta_omega_c_by_centre():
    """Same kind, different parameters — both are δ-distributions."""
    p_c = delta_omega_c(alpha_0=1.0, omega_c=10.0)
    p_S = delta_omega_S(alpha_0=1.0, omega_S=1.0)
    assert p_c.kind == p_S.kind == "delta"
    assert p_c.params["omega"] != p_S.params["omega"]


# ─── sqrt_J (registry key: sqrt-J) ──────────────────────────────────────────


def test_sqrt_J_returns_broadband_kind():
    def J(omega: float) -> float:
        return 0.05 * omega

    p = sqrt_J(alpha_0=1.0, J=J)
    assert p.kind == "broadband"
    assert p.params["alpha_0"] == 1.0
    assert p.params["J"] is J


def test_sqrt_J_rejects_non_callable_J():
    with pytest.raises(ValueError, match="J must be callable"):
        sqrt_J(alpha_0=1.0, J=0.05)  # type: ignore[arg-type]


# ─── gaussian (registry key: gaussian) ──────────────────────────────────────


def test_gaussian_returns_gaussian_kind():
    p = gaussian(alpha_0=1.0, omega_d=5.0, Delta_omega=2.0)
    assert p.kind == "gaussian"
    assert p.params == {"alpha_0": 1.0, "omega_d": 5.0, "Delta_omega": 2.0}


def test_gaussian_rejects_non_positive_bandwidth():
    """Δω = 0 must route to delta_omega_c / delta_omega_S, not gaussian."""
    with pytest.raises(ValueError, match="Delta_omega must be positive"):
        gaussian(alpha_0=1.0, omega_d=5.0, Delta_omega=0.0)
    with pytest.raises(ValueError, match="Delta_omega must be positive"):
        gaussian(alpha_0=1.0, omega_d=5.0, Delta_omega=-1.0)


def test_gaussian_admits_arbitrary_centre():
    """ω_d non-positive is admissible (analytic-continuation studies)."""
    p = gaussian(alpha_0=1.0, omega_d=0.0, Delta_omega=1.0)
    assert p.params["omega_d"] == 0.0
    p_neg = gaussian(alpha_0=1.0, omega_d=-3.0, Delta_omega=1.0)
    assert p_neg.params["omega_d"] == -3.0


# ─── REGISTERED_PROFILES registry ───────────────────────────────────────────


def test_registry_contains_exactly_v0_1_0_keys():
    """Per the §6.1 registry-clearance-gate, the v0.1.0 admissible set is
    exactly four profiles; additions/removals require Council clearance."""
    assert set(REGISTERED_PROFILES.keys()) == {
        "delta-omega_c",
        "delta-omega_S",
        "sqrt-J",
        "gaussian",
    }


def test_registry_keys_map_to_correct_constructors():
    assert REGISTERED_PROFILES["delta-omega_c"] is delta_omega_c
    assert REGISTERED_PROFILES["delta-omega_S"] is delta_omega_S
    assert REGISTERED_PROFILES["sqrt-J"] is sqrt_J
    assert REGISTERED_PROFILES["gaussian"] is gaussian


def test_registry_constructors_all_return_displacement_profile():
    """Each registered constructor must produce a DisplacementProfile."""
    p_c = REGISTERED_PROFILES["delta-omega_c"](alpha_0=1.0, omega_c=10.0)
    p_S = REGISTERED_PROFILES["delta-omega_S"](alpha_0=1.0, omega_S=1.0)
    p_J = REGISTERED_PROFILES["sqrt-J"](alpha_0=1.0, J=lambda w: 0.05 * w)
    p_g = REGISTERED_PROFILES["gaussian"](alpha_0=1.0, omega_d=5.0, Delta_omega=2.0)
    for p in (p_c, p_S, p_J, p_g):
        assert isinstance(p, DisplacementProfile)

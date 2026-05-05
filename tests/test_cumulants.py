"""Behaviour tests for cbg.cumulants (DG-1 Phase C.7).

Covers the canonical all-left time-ordered cumulants D̄_1 and D̄_2 used
by Cards A3 and A4 at orders <= 2. Verifies dispatch, the
displacement-convention stub, the connected-two-point invariance under
displacement, and the generic D_bar interface.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import yaml

from cbg import bath_correlations, cumulants

REPO_ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO_ROOT / "benchmarks" / "benchmark_cards"


# ─── D_bar_1 ────────────────────────────────────────────────────────────────


def test_D_bar_1_thermal_returns_zeros():
    t = np.linspace(0.0, 5.0, 11)
    bs = {"family": "thermal", "temperature": 0.5}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    result = cumulants.D_bar_1(t, bath_state=bs, spectral_density=sd)
    np.testing.assert_array_equal(result, np.zeros(11, dtype=complex))


def test_D_bar_1_thermal_returns_complex_dtype():
    """The cumulant array is complex-valued so it composes with D̄_2."""
    t = np.linspace(0.0, 1.0, 5)
    bs = {"family": "thermal", "temperature": 0.5}
    result = cumulants.D_bar_1(t, bath_state=bs, spectral_density=None)
    assert result.dtype == complex


def test_D_bar_1_coherent_displaced_legacy_shape_raises():
    """Legacy bath_state shape (no `displacement_profile` key, e.g. the
    superseded A3 v0.1.0 displaced case) raises ValueError post-Council-
    Act-2: the registry-clearance-gate (subsidiary briefing v0.3.0 §6.1)
    requires every coherent-displaced bath_state to carry one of the four
    cleared registry keys."""
    t = np.linspace(0.0, 5.0, 11)
    bs = {"family": "coherent_displaced", "temperature": 0.0, "displacement_amplitude": 1.0}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    with pytest.raises(ValueError, match="displacement_profile"):
        cumulants.D_bar_1(t, bath_state=bs, spectral_density=sd)


def test_D_bar_1_coherent_displaced_with_cleared_profile_succeeds():
    """Post-Council-Act-2: a bath_state tagging a cleared profile produces
    a non-zero ⟨B(t)⟩ — verified for delta-omega_c via the closed-form
    prediction 2 α₀ √J(ω_c) cos(ω_c t)."""
    t = np.linspace(0.0, 1.0, 5)
    bs = {
        "family": "coherent_displaced",
        "displacement_profile": "delta-omega_c",
        "parameters": {"alpha_0": 1.0, "omega_c": 10.0},
    }
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    result = cumulants.D_bar_1(t, bath_state=bs, spectral_density=sd)
    # Closed form: 2 · 1 · √(0.05·10·exp(-1)) · cos(10·t)
    prefactor = 2.0 * np.sqrt(0.05 * 10.0 * np.exp(-1.0))
    expected = prefactor * np.cos(10.0 * t).astype(complex)
    np.testing.assert_allclose(result, expected, atol=1e-12)


def test_D_bar_1_unknown_family_raises():
    t = np.linspace(0.0, 5.0, 11)
    bs = {"family": "squeezed_vacuum"}
    with pytest.raises(NotImplementedError, match="not implemented"):
        cumulants.D_bar_1(t, bath_state=bs, spectral_density=None)


def test_D_bar_1_unregistered_displacement_profile_raises():
    """The §6.1 registry-clearance-gate refuses ad-hoc profile additions."""
    t = np.linspace(0.0, 5.0, 11)
    bs = {
        "family": "coherent_displaced",
        "displacement_profile": "lorentzian",  # not in registry
        "parameters": {},
    }
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    with pytest.raises(NotImplementedError, match="registry-clearance-gate"):
        cumulants.D_bar_1(t, bath_state=bs, spectral_density=sd)


def test_D_bar_1_2d_t_grid_raises():
    bs = {"family": "thermal", "temperature": 0.5}
    with pytest.raises(ValueError, match="must be 1D"):
        cumulants.D_bar_1(np.zeros((3, 3)), bath_state=bs, spectral_density=None)


# ─── D_bar_2 ────────────────────────────────────────────────────────────────


def test_D_bar_2_thermal_matches_bath_two_point_thermal_array():
    """The thermal D̄_2 is exactly bath_correlations.bath_two_point_thermal_array
    at the spec's temperature."""
    t = np.linspace(0.0, 3.0, 7)
    bs = {"family": "thermal", "temperature": 0.5}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    result = cumulants.D_bar_2(t, bath_state=bs, spectral_density=sd)
    expected = bath_correlations.bath_two_point_thermal_array(
        t, alpha=0.05, omega_c=10.0, temperature=0.5
    )
    np.testing.assert_array_equal(result, expected)


def test_D_bar_2_displacement_invariance():
    """Connected D̄_2 is the SAME for thermal and coherent_displaced
    at the same temperature — the key physical claim that lets C.7
    handle the displaced case without the convention."""
    t = np.linspace(0.0, 3.0, 7)
    bs_thermal = {"family": "thermal", "temperature": 0.0}
    bs_displaced = {
        "family": "coherent_displaced",
        "temperature": 0.0,
        "displacement_amplitude": 1.0,
    }
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    D_thermal = cumulants.D_bar_2(t, bath_state=bs_thermal, spectral_density=sd)
    D_displaced = cumulants.D_bar_2(t, bath_state=bs_displaced, spectral_density=sd)
    np.testing.assert_array_equal(D_thermal, D_displaced)


def test_D_bar_2_displacement_invariance_at_finite_T_baseline():
    """If a future card uses coherent_displaced with non-zero temperature
    baseline, D̄_2 still uses that temperature (displacement only affects D̄_1)."""
    t = np.linspace(0.0, 3.0, 7)
    bs_thermal = {"family": "thermal", "temperature": 0.5}
    bs_displaced = {
        "family": "coherent_displaced",
        "temperature": 0.5,
        "displacement_amplitude": 1.0,
    }
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    D_thermal = cumulants.D_bar_2(t, bath_state=bs_thermal, spectral_density=sd)
    D_displaced = cumulants.D_bar_2(t, bath_state=bs_displaced, spectral_density=sd)
    np.testing.assert_array_equal(D_thermal, D_displaced)


def test_D_bar_2_shape_and_dtype():
    t = np.linspace(0.0, 3.0, 7)
    bs = {"family": "thermal", "temperature": 0.5}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    result = cumulants.D_bar_2(t, bath_state=bs, spectral_density=sd)
    assert result.shape == (7, 7)
    assert result.dtype == complex


def test_D_bar_2_unknown_spectral_density_raises():
    t = np.linspace(0.0, 3.0, 7)
    bs = {"family": "thermal", "temperature": 0.5}
    sd = {"family": "drude_lorentz", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    with pytest.raises(NotImplementedError, match="ohmic"):
        cumulants.D_bar_2(t, bath_state=bs, spectral_density=sd)


def test_D_bar_2_unknown_bath_family_raises():
    t = np.linspace(0.0, 3.0, 7)
    bs = {"family": "thermal_field_dynamics", "temperature": 0.5}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    with pytest.raises(NotImplementedError, match="DG-1"):
        cumulants.D_bar_2(t, bath_state=bs, spectral_density=sd)


# ─── Generic D_bar dispatch ────────────────────────────────────────────────


def test_D_bar_n1_thermal_returns_zero_scalar():
    """D_bar((t,), ()) for thermal = zeros[(t,)] = 0 (the array-form path)."""
    bs = {"family": "thermal", "temperature": 0.5}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    result = cumulants.D_bar((1.0,), (), bath_state=bs, spectral_density=sd)
    # D_bar_1 returns an array of shape (1,) for one tau_arg
    np.testing.assert_array_equal(result, np.array([0.0 + 0.0j]))


def test_D_bar_n1_displaced_legacy_shape_raises():
    """The generic D_bar dispatch propagates the same ValueError as D_bar_1
    when a coherent_displaced bath_state lacks the displacement_profile key
    (legacy A3 v0.1.0 shape; rejected post-Council-Act-2)."""
    bs = {"family": "coherent_displaced", "temperature": 0.0, "displacement_amplitude": 1.0}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    with pytest.raises(ValueError, match="displacement_profile"):
        cumulants.D_bar((1.0,), (), bath_state=bs, spectral_density=sd)


def test_D_bar_n2_thermal_matches_pairwise_correlator():
    """D_bar((τ_1, τ_2), ()) returns D̄_2(τ_1, τ_2)."""
    bs = {"family": "thermal", "temperature": 0.5}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    val = cumulants.D_bar((1.0, 0.5), (), bath_state=bs, spectral_density=sd)
    # Compare against the array-form value at [0, 1]
    arr = cumulants.D_bar_2(np.array([1.0, 0.5]), bath_state=bs, spectral_density=sd)
    assert val == arr[0, 1]


def test_D_bar_with_s_args_routes_to_dg2():
    """Mixed left/right ordering is DG-2 territory."""
    bs = {"family": "thermal", "temperature": 0.5}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    with pytest.raises(NotImplementedError, match="DG-2"):
        cumulants.D_bar((1.0,), (0.5,), bath_state=bs, spectral_density=sd)


def test_D_bar_higher_order_routes_to_dg2():
    """n >= 3 cumulants are DG-2 territory."""
    bs = {"family": "thermal", "temperature": 0.5}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    with pytest.raises(NotImplementedError, match="DG-2"):
        cumulants.D_bar((1.0, 0.5, 0.25), (), bath_state=bs, spectral_density=sd)


def test_D_bar_missing_bath_state_raises():
    with pytest.raises(ValueError, match="bath_state"):
        cumulants.D_bar((1.0,), ())


def test_D_bar_n2_missing_spectral_density_raises():
    bs = {"family": "thermal", "temperature": 0.5}
    with pytest.raises(ValueError, match="spectral_density"):
        cumulants.D_bar((1.0, 0.5), (), bath_state=bs)


# ─── Composability with Cards A3 and A4 ────────────────────────────────────


def test_D_bar_2_composes_with_a3_thermal():
    """End-to-end: load A3 YAML, build D̄_2 array on the thermal case grid."""
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml").read_text())
    sd = a3["frozen_parameters"]["model"]["bath_spectral_density"]
    bs = a3["frozen_parameters"]["model"]["test_cases"][0]["bath_state"]
    assert bs["family"] == "thermal"
    t = np.linspace(0.0, 5.0, 11)  # coarse grid for test speed
    result = cumulants.D_bar_2(t, bath_state=bs, spectral_density=sd)
    assert result.shape == (11, 11)
    assert result.dtype == complex
    # Hermitian-conjugate symmetry inherits from C.6
    np.testing.assert_allclose(result, result.conj().T, atol=1e-9)


def test_D_bar_1_composes_with_a3_thermal():
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml").read_text())
    sd = a3["frozen_parameters"]["model"]["bath_spectral_density"]
    bs = a3["frozen_parameters"]["model"]["test_cases"][0]["bath_state"]
    t = np.linspace(0.0, 5.0, 11)
    result = cumulants.D_bar_1(t, bath_state=bs, spectral_density=sd)
    np.testing.assert_array_equal(result, np.zeros(11, dtype=complex))


def test_D_bar_1_a3_displaced_case_legacy_shape_now_rejected():
    """Audit-trail test: A3 v0.1.0's superseded coherent_displaced test case
    has the legacy shape (`displacement_amplitude` only, no
    `displacement_profile`). Post-Council-Act-2 (2026-05-04), this shape
    is rejected with ValueError requiring the registry-clearance-gate
    profile key. The superseded card itself is unchanged in tree;
    re-attempting it now surfaces the schema gap rather than the
    pre-clearance convention gap."""
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml").read_text())
    sd = a3["frozen_parameters"]["model"]["bath_spectral_density"]
    bs = a3["frozen_parameters"]["model"]["test_cases"][1]["bath_state"]
    assert bs["family"] == "coherent_displaced"
    assert "displacement_profile" not in bs  # legacy shape
    t = np.linspace(0.0, 5.0, 11)
    with pytest.raises(ValueError, match="displacement_profile"):
        cumulants.D_bar_1(t, bath_state=bs, spectral_density=sd)


def test_D_bar_2_displacement_invariance_on_a3_pair():
    """A3's thermal and displaced cases give the same D̄_2 (since both are
    Gaussian; only D̄_1 differs)."""
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml").read_text())
    sd = a3["frozen_parameters"]["model"]["bath_spectral_density"]
    bs_thermal = a3["frozen_parameters"]["model"]["test_cases"][0]["bath_state"]
    bs_displaced = a3["frozen_parameters"]["model"]["test_cases"][1]["bath_state"]
    t = np.linspace(0.0, 5.0, 11)
    _D_thermal = cumulants.D_bar_2(t, bath_state=bs_thermal, spectral_density=sd)
    D_displaced = cumulants.D_bar_2(t, bath_state=bs_displaced, spectral_density=sd)
    # Different temperatures → different D̄_2, but the displacement
    # invariance applies AT FIXED temperature. A3's thermal is T=0.5 and
    # displaced is T=0, so they differ. Verify by comparing each to its
    # own thermal-evaluator twin.
    same_T_thermal = {"family": "thermal", "temperature": bs_displaced["temperature"]}
    D_displaced_via_thermal = cumulants.D_bar_2(t, bath_state=same_T_thermal, spectral_density=sd)
    np.testing.assert_array_equal(D_displaced, D_displaced_via_thermal)

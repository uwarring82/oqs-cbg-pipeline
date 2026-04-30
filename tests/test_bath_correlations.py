"""Behaviour tests for cbg.bath_correlations (DG-1 Phase C.6).

Covers:
- ohmic_spectral_density at canonical evaluation points + validation.
- bath_two_point_thermal at T = 0 vs. analytical closed form
  C(t) = α / (1/ω_c + it)².
- bath_two_point_thermal at T > 0: structural properties (Hermiticity,
  high-T limit, T → 0 continuity).
- bath_two_point_thermal_array shape, stationarity, Hermitian
  conjugation under time-reversal.
- two_point dispatch on (bath_state.family, spectral_density.family).
- Composability with Cards A3/A4 frozen_parameters.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import yaml

from cbg import bath_correlations as bc


REPO_ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO_ROOT / "benchmarks" / "benchmark_cards"


# ─── ohmic_spectral_density ────────────────────────────────────────────────


def test_ohmic_at_zero_frequency_is_zero():
    """J(0) = 0 (the linear-in-ω prefactor)."""
    assert bc.ohmic_spectral_density(0.0, alpha=0.05, omega_c=10.0) == 0.0


def test_ohmic_at_cutoff_frequency_value():
    """J(ω_c) = α ω_c / e (well-known check at the cutoff)."""
    val = bc.ohmic_spectral_density(10.0, alpha=0.05, omega_c=10.0)
    assert val == pytest.approx(0.05 * 10.0 / np.e, rel=1e-12)


def test_ohmic_high_frequency_decays():
    """J(ω) decays as exp(-ω/ω_c) at high ω; J(10 ω_c) ≈ exp(-10) suppressed."""
    val = bc.ohmic_spectral_density(100.0, alpha=0.05, omega_c=10.0)
    assert val == pytest.approx(0.05 * 100.0 * np.exp(-10.0), rel=1e-12)


def test_ohmic_vectorized():
    """Accepts numpy array; returns same-shape array."""
    omegas = np.linspace(0.0, 50.0, 51)
    J = bc.ohmic_spectral_density(omegas, alpha=0.05, omega_c=10.0)
    assert J.shape == omegas.shape
    assert J[0] == 0.0  # ω=0
    assert np.all(J >= 0.0)  # J ≥ 0 everywhere on the domain


def test_ohmic_negative_alpha_raises():
    with pytest.raises(ValueError, match="alpha must be >= 0"):
        bc.ohmic_spectral_density(1.0, alpha=-0.1, omega_c=10.0)


def test_ohmic_zero_omega_c_raises():
    with pytest.raises(ValueError, match="omega_c must be > 0"):
        bc.ohmic_spectral_density(1.0, alpha=0.05, omega_c=0.0)


def test_ohmic_negative_omega_raises():
    with pytest.raises(ValueError, match="omega must be non-negative"):
        bc.ohmic_spectral_density(np.array([-1.0, 1.0]), alpha=0.05, omega_c=10.0)


# ─── bath_two_point_thermal at T = 0: analytical closed form ──────────────


def test_bath_two_point_T0_t0_equals_alpha_omega_c_squared():
    """C(0)|_{T=0} = α ω_c²  (∫_0^∞ ω e^{-ω/ω_c} dω = ω_c²)."""
    val = bc.bath_two_point_thermal(0.0, alpha=0.05, omega_c=10.0, temperature=0.0)
    assert val == pytest.approx(0.05 * 10.0**2, rel=1e-12)


def test_bath_two_point_T0_closed_form():
    """C(t)|_{T=0} = α / (1/ω_c + it)² for arbitrary t."""
    alpha, omega_c = 0.05, 10.0
    for t in [0.0, 0.1, 1.0, 5.0, -2.0]:
        val = bc.bath_two_point_thermal(t, alpha=alpha, omega_c=omega_c, temperature=0.0)
        denom = 1.0 / omega_c + 1j * t
        expected = alpha / (denom * denom)
        assert val == pytest.approx(expected, rel=1e-12)


def test_bath_two_point_T0_at_negative_time_is_conjugate():
    """C(-t)|_T=0 = conj(C(t))|_T=0 (Hermiticity of the bath two-point)."""
    alpha, omega_c = 0.05, 10.0
    for t in [0.5, 1.0, 3.0]:
        val_pos = bc.bath_two_point_thermal(t, alpha, omega_c, 0.0)
        val_neg = bc.bath_two_point_thermal(-t, alpha, omega_c, 0.0)
        assert val_neg == pytest.approx(np.conj(val_pos), rel=1e-12)


# ─── bath_two_point_thermal at T > 0: numerical structural checks ─────────


def test_bath_two_point_finite_T_at_t0_is_real_and_positive():
    """C(0) at T > 0 is purely real and positive (full bath occupation)."""
    val = bc.bath_two_point_thermal(0.0, alpha=0.05, omega_c=10.0, temperature=0.5)
    assert abs(val.imag) < 1e-10
    assert val.real > 0.0


def test_bath_two_point_finite_T_imag_part_independent_of_T():
    """The imaginary part is - ∫ J(ω) sin(ωt) dω, which is T-independent.
    Verify by comparing T = 0.5 and T = 2.0 imag parts."""
    t = 1.0
    val_T1 = bc.bath_two_point_thermal(t, alpha=0.05, omega_c=10.0, temperature=0.5)
    val_T2 = bc.bath_two_point_thermal(t, alpha=0.05, omega_c=10.0, temperature=2.0)
    assert val_T1.imag == pytest.approx(val_T2.imag, rel=1e-8)


def test_bath_two_point_finite_T_imag_matches_T0_analytical():
    """The imaginary part is the same as at T=0 (Im part has no thermal factor),
    so its analytical value -Im[α/(1/ωc+it)²] applies."""
    alpha, omega_c, t = 0.05, 10.0, 1.0
    val_finite_T = bc.bath_two_point_thermal(t, alpha, omega_c, temperature=0.5)
    denom = 1.0 / omega_c + 1j * t
    expected_imag = (alpha / (denom * denom)).imag
    assert val_finite_T.imag == pytest.approx(expected_imag, rel=1e-8)


def test_bath_two_point_finite_T_real_part_grows_with_T():
    """The real part at fixed t grows monotonically with T (more bath
    occupation enhances the symmetric/fluctuation channel)."""
    t = 0.0  # t=0 gives the integrated occupation
    val_low = bc.bath_two_point_thermal(t, alpha=0.05, omega_c=10.0, temperature=0.5)
    val_high = bc.bath_two_point_thermal(t, alpha=0.05, omega_c=10.0, temperature=5.0)
    assert val_high.real > val_low.real


def test_bath_two_point_T_to_zero_recovers_T0_limit():
    """As T → 0, the finite-T evaluator must converge to the analytical T=0 closed form."""
    alpha, omega_c, t = 0.05, 10.0, 0.5
    val_T0 = bc.bath_two_point_thermal(t, alpha, omega_c, temperature=0.0)
    val_small_T = bc.bath_two_point_thermal(t, alpha, omega_c, temperature=1e-3)
    assert val_small_T == pytest.approx(val_T0, abs=1e-3)


def test_bath_two_point_negative_alpha_raises():
    with pytest.raises(ValueError, match="alpha must be >= 0"):
        bc.bath_two_point_thermal(0.0, alpha=-0.05, omega_c=10.0, temperature=0.5)


def test_bath_two_point_zero_omega_c_raises():
    with pytest.raises(ValueError, match="omega_c must be > 0"):
        bc.bath_two_point_thermal(0.0, alpha=0.05, omega_c=0.0, temperature=0.5)


def test_bath_two_point_negative_temperature_raises():
    with pytest.raises(ValueError, match="temperature must be >= 0"):
        bc.bath_two_point_thermal(0.0, alpha=0.05, omega_c=10.0, temperature=-0.1)


# ─── bath_two_point_thermal_array ──────────────────────────────────────────


def test_bath_two_point_array_shape():
    t = np.linspace(0.0, 5.0, 11)
    C = bc.bath_two_point_thermal_array(t, alpha=0.05, omega_c=10.0, temperature=0.5)
    assert C.shape == (11, 11)
    assert C.dtype == complex


def test_bath_two_point_array_diagonal_is_real_C0():
    """Diagonal entries are C(0), which is real-positive."""
    t = np.linspace(0.0, 5.0, 6)
    C = bc.bath_two_point_thermal_array(t, alpha=0.05, omega_c=10.0, temperature=0.5)
    diag = np.diagonal(C)
    np.testing.assert_allclose(diag.imag, 0.0, atol=1e-10)
    assert np.all(diag.real > 0.0)


def test_bath_two_point_array_hermitian_conjugate_symmetry():
    """C[j, k] = conj(C[k, j]) by stationarity + the C(-t) = conj(C(t)) property."""
    t = np.linspace(0.0, 3.0, 7)
    C = bc.bath_two_point_thermal_array(t, alpha=0.05, omega_c=10.0, temperature=0.5)
    np.testing.assert_allclose(C, C.conj().T, atol=1e-10)


def test_bath_two_point_array_stationarity():
    """C[j, k] depends only on t[j] - t[k]: shifted grids give same correlators
    on the same time-difference matrix."""
    t = np.linspace(0.0, 3.0, 7)
    t_shifted = t + 100.0
    C = bc.bath_two_point_thermal_array(t, alpha=0.05, omega_c=10.0, temperature=0.5)
    C_shifted = bc.bath_two_point_thermal_array(t_shifted, alpha=0.05, omega_c=10.0,
                                                temperature=0.5)
    np.testing.assert_allclose(C, C_shifted, atol=1e-10)


def test_bath_two_point_array_T0_matches_analytical():
    """T = 0 array values match α / (1/ω_c + it_diff)² element-wise."""
    alpha, omega_c = 0.05, 10.0
    t = np.linspace(0.0, 2.0, 5)
    C = bc.bath_two_point_thermal_array(t, alpha, omega_c, temperature=0.0)
    diff = t[:, None] - t[None, :]
    denom = 1.0 / omega_c + 1j * diff
    expected = alpha / (denom * denom)
    np.testing.assert_allclose(C, expected, atol=1e-12)


def test_bath_two_point_array_2d_grid_raises():
    t = np.zeros((3, 3))
    with pytest.raises(ValueError, match="t_grid must be 1D"):
        bc.bath_two_point_thermal_array(t, alpha=0.05, omega_c=10.0, temperature=0.5)


# ─── two_point: generic dispatch ───────────────────────────────────────────


def test_two_point_thermal_ohmic_dispatches():
    bath_state = {"family": "thermal", "temperature": 0.5}
    spectral_density = {"family": "ohmic", "coupling_strength": 0.05,
                        "cutoff_frequency": 10.0}
    val = bc.two_point(1.0, 0.0, bath_state=bath_state,
                       spectral_density=spectral_density)
    expected = bc.bath_two_point_thermal(1.0, 0.05, 10.0, 0.5)
    assert val == pytest.approx(expected, rel=1e-12)


def test_two_point_coherent_displaced_uses_thermal_evaluator():
    """Coherent-displaced uses the same connected two-point as the
    underlying thermal-vacuum at the spec's temperature; displacement
    leaves the connected part invariant."""
    bath_state = {"family": "coherent_displaced", "temperature": 0.0,
                  "displacement_amplitude": 1.0}
    spectral_density = {"family": "ohmic", "coupling_strength": 0.05,
                        "cutoff_frequency": 10.0}
    val = bc.two_point(0.5, 0.0, bath_state=bath_state,
                       spectral_density=spectral_density)
    expected = bc.bath_two_point_thermal(0.5, 0.05, 10.0, 0.0)
    assert val == pytest.approx(expected, rel=1e-12)


def test_two_point_uses_only_time_difference():
    bs = {"family": "thermal", "temperature": 0.5}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    val_a = bc.two_point(1.0, 0.0, bath_state=bs, spectral_density=sd)
    val_b = bc.two_point(11.0, 10.0, bath_state=bs, spectral_density=sd)
    assert val_a == pytest.approx(val_b, rel=1e-10)


def test_two_point_unknown_spectral_density_family_raises():
    bs = {"family": "thermal", "temperature": 0.5}
    sd = {"family": "drude_lorentz", "coupling_strength": 0.05,
          "cutoff_frequency": 10.0}
    with pytest.raises(NotImplementedError, match="DG-2"):
        bc.two_point(1.0, 0.0, bath_state=bs, spectral_density=sd)


def test_two_point_unknown_bath_state_family_raises():
    bs = {"family": "squeezed_vacuum", "temperature": 0.0}
    sd = {"family": "ohmic", "coupling_strength": 0.05, "cutoff_frequency": 10.0}
    with pytest.raises(NotImplementedError, match="DG-1"):
        bc.two_point(1.0, 0.0, bath_state=bs, spectral_density=sd)


# ─── n_point_ordered: still stubbed at DG-2 ────────────────────────────────


def test_n_point_ordered_remains_stubbed_at_dg1():
    with pytest.raises(NotImplementedError, match="DG-2"):
        bc.n_point_ordered((), (), {}, None)


# ─── Composability with Cards A3 and A4 ────────────────────────────────────


def test_two_point_composes_with_a3_thermal_case():
    """End-to-end: load A3 YAML, extract spectral_density + thermal bath_state,
    evaluate two_point. Confirms the dict shapes match."""
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml").read_text())
    sd = a3["frozen_parameters"]["model"]["bath_spectral_density"]
    bs = a3["frozen_parameters"]["model"]["test_cases"][0]["bath_state"]
    assert bs["family"] == "thermal"
    val = bc.two_point(1.0, 0.0, bath_state=bs, spectral_density=sd)
    assert isinstance(val, complex)


def test_two_point_composes_with_a3_displaced_case():
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml").read_text())
    sd = a3["frozen_parameters"]["model"]["bath_spectral_density"]
    bs = a3["frozen_parameters"]["model"]["test_cases"][1]["bath_state"]
    assert bs["family"] == "coherent_displaced"
    val = bc.two_point(1.0, 0.0, bath_state=bs, spectral_density=sd)
    assert isinstance(val, complex)


def test_two_point_array_smoke_with_a3_grid():
    """Build the A3 time grid + correlator array end-to-end."""
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.0.yaml").read_text())
    sd = a3["frozen_parameters"]["model"]["bath_spectral_density"]
    bs = a3["frozen_parameters"]["model"]["test_cases"][0]["bath_state"]
    # Use a coarse 21-point grid to keep the test fast (full 200-point grid
    # exercises the same code path; coarse grid is sufficient for smoke).
    t = np.linspace(0.0, 5.0, 21)
    C = bc.bath_two_point_thermal_array(
        t, sd["coupling_strength"], sd["cutoff_frequency"], bs["temperature"]
    )
    assert C.shape == (21, 21)
    assert C.dtype == complex
    np.testing.assert_allclose(C, C.conj().T, atol=1e-9)

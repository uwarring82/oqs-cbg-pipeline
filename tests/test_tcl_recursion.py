"""Behaviour tests for cbg.tcl_recursion low-order runner paths.

Covers:
- interaction_picture helper at canonical points.
- L_0[X] = -i [H_S, X] (the bare Liouvillian).
- L_1[X] = 0 for thermal Gaussian bath.
- L_2[X] for sigma_z (pure dephasing): K_2 = 0 (Card A3 thermal trivialisation).
- L_2[X] for sigma_x (orthogonal coupling): K_2 ∝ sigma_z (Card A4 parity-class
  theorem; transverse components vanish).
- K_total over the full t_grid for both cards' thermal baselines.
- Stubs: canonical_lindblad_form, n >= 3 routing, non-thermal at order >= 1.
- Composability with the actual A3 v0.1.1 and A4 v0.1.1 card YAMLs.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import yaml

from cbg import tcl_recursion as tr

REPO_ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO_ROOT / "benchmarks" / "benchmark_cards"


# ─── Test fixtures ─────────────────────────────────────────────────────────

sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
identity_2 = np.eye(2, dtype=complex)


def _hs(omega=1.0):
    return 0.5 * omega * sigma_z


def _coarse_t_grid(t_end=2.0, n_points=11):
    return np.linspace(0.0, t_end, n_points)


def _thermal_state(temperature=0.5):
    return {"family": "thermal", "temperature": temperature}


def _ohmic_sd(alpha=0.05, omega_c=10.0):
    return {"family": "ohmic", "coupling_strength": alpha, "cutoff_frequency": omega_c}


# ─── interaction_picture ───────────────────────────────────────────────────


def test_interaction_picture_identity_at_tau_zero():
    """A_I(0) = A."""
    H_S = _hs()
    A = sigma_x
    np.testing.assert_allclose(tr.interaction_picture(H_S, A, 0.0), A, atol=1e-12)


def test_interaction_picture_commuting_op_invariant():
    """If [H_S, A] = 0, then A_I(τ) = A for all τ."""
    H_S = _hs()
    A = sigma_z  # commutes with H_S = (omega/2) sigma_z
    for tau in [0.5, 1.0, 5.0, -2.0]:
        np.testing.assert_allclose(tr.interaction_picture(H_S, A, tau), A, atol=1e-12)


def test_interaction_picture_sigma_x_rotates():
    """For H_S = (omega/2) sigma_z and A = sigma_x:

    e^{i H_S tau} sigma_x e^{-i H_S tau} = sigma_x cos(omega tau) − sigma_y sin(omega tau)

    (Heisenberg-picture evolution under H_S; the sign on the sigma_y term
    follows from [sigma_z, sigma_x] = 2i sigma_y and the d/dτ formula.)
    Check at tau = pi / (2 omega): cos = 0, sin = 1 → result = -sigma_y."""
    omega = 1.0
    H_S = _hs(omega=omega)
    A = sigma_x
    tau = np.pi / (2 * omega)
    result = tr.interaction_picture(H_S, A, tau)
    np.testing.assert_allclose(result, -sigma_y, atol=1e-12)


def test_interaction_picture_inverse():
    """A_I(-tau) is the inverse rotation of A_I(tau)."""
    H_S = _hs()
    A = sigma_x
    tau = 0.7
    forward = tr.interaction_picture(H_S, A, tau)
    backward = tr.interaction_picture(H_S, forward, -tau)
    np.testing.assert_allclose(backward, A, atol=1e-12)


# ─── L_0 ────────────────────────────────────────────────────────────────────


def test_L_0_returns_minus_i_commutator():
    """L_0[X] = -i [H_S, X]."""
    t = _coarse_t_grid()
    H_S = _hs()
    A = sigma_x  # ignored at n=0
    L_0 = tr.L_n_thermal_at_time(0, 5, t, H_S, A, D_bar_2_array=None)
    X = sigma_x
    expected = -1j * (H_S @ X - X @ H_S)
    np.testing.assert_allclose(L_0(X), expected, atol=1e-12)


def test_L_0_zero_for_commuting_X():
    """L_0[H_S] = 0 (H_S commutes with itself)."""
    t = _coarse_t_grid()
    H_S = _hs()
    L_0 = tr.L_n_thermal_at_time(0, 0, t, H_S, sigma_x, D_bar_2_array=None)
    np.testing.assert_allclose(L_0(H_S), np.zeros((2, 2), dtype=complex), atol=1e-12)


# ─── L_1 thermal ────────────────────────────────────────────────────────────


def test_L_1_thermal_returns_zero():
    """For a thermal Gaussian bath, L_1[X] = 0 (D̄_1 = 0 by symmetry)."""
    t = _coarse_t_grid()
    H_S = _hs()
    L_1 = tr.L_n_thermal_at_time(1, 5, t, H_S, sigma_x, D_bar_2_array=None)
    np.testing.assert_array_equal(L_1(sigma_x), np.zeros((2, 2), dtype=complex))


# ─── L_2 thermal ───────────────────────────────────────────────────────────


def _D_bar_2_for_grid(t_grid, bath_state, spectral_density):
    from cbg.cumulants import D_bar_2

    return D_bar_2(t_grid, bath_state=bath_state, spectral_density=spectral_density)


def test_L_2_at_t0_returns_zero():
    """The integral has zero length at t = t_grid[0]; L_2 = 0."""
    t = _coarse_t_grid()
    H_S = _hs()
    A = sigma_x
    D = _D_bar_2_for_grid(t, _thermal_state(), _ohmic_sd())
    L_2 = tr.L_n_thermal_at_time(2, 0, t, H_S, A, D_bar_2_array=D)
    np.testing.assert_allclose(L_2(sigma_x), np.zeros((2, 2), dtype=complex), atol=1e-12)


def test_L_n_thermal_at_time_n_3_returns_zero_post_phase_b2():
    """Phase B.2 wires n=3 to return the zero superoperator (thermal
    Gaussian D̄_1 = D̄_3 = 0 ⇒ L_3 = 0 identically)."""
    t = _coarse_t_grid()
    L_3 = tr.L_n_thermal_at_time(3, 5, t, _hs(), sigma_x, D_bar_2_array=None)
    np.testing.assert_allclose(L_3(sigma_x), np.zeros((2, 2), dtype=complex), atol=1e-12)
    np.testing.assert_allclose(L_3(sigma_z), np.zeros((2, 2), dtype=complex), atol=1e-12)


def test_L_n_thermal_at_time_n_4_raises_pending_recursion():
    """n=4 is the deferred Phase B.2 follow-up; clearly named in error."""
    t = _coarse_t_grid()
    with pytest.raises(NotImplementedError, match="n=4|deferred"):
        tr.L_n_thermal_at_time(4, 5, t, _hs(), sigma_x, D_bar_2_array=None)


def test_L_n_thermal_at_time_n_5_raises_out_of_scope():
    """Orders n >= 5 are out of DG-4 Phase B scope altogether."""
    t = _coarse_t_grid()
    with pytest.raises(NotImplementedError, match="out of scope|not implemented"):
        tr.L_n_thermal_at_time(5, 5, t, _hs(), sigma_x, D_bar_2_array=None)


def test_L_2_requires_D_bar_2_array():
    t = _coarse_t_grid()
    with pytest.raises(ValueError, match="D_bar_2_array"):
        tr.L_n_thermal_at_time(2, 5, t, _hs(), sigma_x, D_bar_2_array=None)


# ─── K_n_thermal_on_grid: Card A3 (sigma_z, pure dephasing) ────────────────


def test_K_2_pure_dephasing_thermal_is_zero():
    """For A = sigma_z, thermal Gaussian bath: K_2(t) = 0 at all t.

    This is the spin-boson exact-result trivialisation (Łuczka 1990;
    Doll et al. 2008; Leggett et al. 1987) — the central B.2 prediction
    of CL-2026-005 v0.4 Entry 3 in the thermal case.

    The pure dephasing dissipator [σ_z, [σ_z, X]] = 4(X - σ_z X σ_z)
    has zero Hamiltonian content under Letter Eq. (6); the computation
    confirms this numerically.
    """
    t = _coarse_t_grid(t_end=5.0, n_points=21)
    K_2 = tr.K_n_thermal_on_grid(
        2,
        t,
        _hs(),
        sigma_z,
        bath_state=_thermal_state(temperature=0.5),
        spectral_density=_ohmic_sd(alpha=0.05, omega_c=10.0),
    )
    # K_2 should be the zero matrix at every t; check the Frobenius norm.
    for t_idx in range(len(t)):
        assert np.linalg.norm(K_2[t_idx], ord="fro") < 1e-10, (
            f"K_2(t={t[t_idx]:.2f}) is non-zero in pure dephasing; "
            f"got max abs entry {np.max(np.abs(K_2[t_idx])):.3e}"
        )


def test_K_total_pure_dephasing_thermal_is_H_S():
    """K_total = K_0 + K_1 + K_2 = H_S in thermal pure dephasing.

    Card A3 v0.1.1 thermal_bath expected_outcome: K(t) = (omega/2) sigma_z
    exactly at every order ≤ N_card. This is the runner-facing entry-point
    test."""
    t = _coarse_t_grid(t_end=5.0, n_points=21)
    H_S = _hs(omega=1.0)
    K = tr.K_total_thermal_on_grid(
        2,
        t,
        H_S,
        sigma_z,
        bath_state=_thermal_state(temperature=0.5),
        spectral_density=_ohmic_sd(alpha=0.05, omega_c=10.0),
    )
    for t_idx in range(len(t)):
        np.testing.assert_allclose(
            K[t_idx],
            H_S,
            atol=1e-10,
            err_msg=f"K(t={t[t_idx]:.2f}) deviates from H_S in pure dephasing",
        )


# ─── K_n_thermal_on_grid: Card A4 (sigma_x, parity-class theorem) ──────────


def test_K_2_sigma_x_thermal_has_no_transverse_components():
    """For A = sigma_x, thermal Gaussian bath: K_2(t) ∝ sigma_z at all t.

    This is the Letter Eqs. (D.4)-(D.6) parity-class theorem in the
    thermal case — odd-order bath cumulants vanish, and even orders
    contribute only diagonal terms (the σ_z component). The transverse
    components (σ_x, σ_y) of K_2 must be zero to numerical tolerance.

    This is the central B.1 prediction of CL-2026-005 v0.4 Entry 4 in
    the thermal case (Card A4 v0.1.1).
    """
    t = _coarse_t_grid(t_end=5.0, n_points=21)
    K_2 = tr.K_n_thermal_on_grid(
        2,
        t,
        _hs(),
        sigma_x,
        bath_state=_thermal_state(temperature=0.5),
        spectral_density=_ohmic_sd(alpha=0.05, omega_c=10.0),
    )
    # Project onto Pauli basis: K = a I + b σ_x + c σ_y + d σ_z
    # b = Tr(σ_x K) / 2; c = Tr(σ_y K) / 2; d = Tr(σ_z K) / 2; a = Tr(K) / 2.
    for t_idx in range(len(t)):
        K_t = K_2[t_idx]
        b = 0.5 * np.trace(sigma_x @ K_t)
        c = 0.5 * np.trace(sigma_y @ K_t)
        # Transverse components must vanish (parity-class theorem).
        assert abs(b) < 1e-10, (
            f"K_2(t={t[t_idx]:.2f}) has nonzero σ_x component {abs(b):.3e}; "
            f"parity-class theorem violated"
        )
        assert abs(c) < 1e-10, (
            f"K_2(t={t[t_idx]:.2f}) has nonzero σ_y component {abs(c):.3e}; "
            f"parity-class theorem violated"
        )


def test_K_2_sigma_x_thermal_is_hermitian():
    """K_2(t) must be Hermitian (Hermiticity-preserving L → Hermitian K)."""
    t = _coarse_t_grid(t_end=2.0, n_points=11)
    K_2 = tr.K_n_thermal_on_grid(
        2,
        t,
        _hs(),
        sigma_x,
        bath_state=_thermal_state(),
        spectral_density=_ohmic_sd(),
    )
    for t_idx in range(len(t)):
        np.testing.assert_allclose(
            K_2[t_idx],
            K_2[t_idx].conj().T,
            atol=1e-10,
            err_msg=f"K_2(t={t[t_idx]:.2f}) is not Hermitian",
        )


def test_K_total_sigma_x_thermal_no_transverse():
    """Card A4 v0.1.1 PASS condition: K_total has no transverse components."""
    t = _coarse_t_grid(t_end=5.0, n_points=21)
    K = tr.K_total_thermal_on_grid(
        2,
        t,
        _hs(),
        sigma_x,
        bath_state=_thermal_state(),
        spectral_density=_ohmic_sd(),
    )
    for t_idx in range(len(t)):
        K_t = K[t_idx]
        b = 0.5 * np.trace(sigma_x @ K_t)
        c = 0.5 * np.trace(sigma_y @ K_t)
        transverse_norm = np.sqrt(abs(b) ** 2 + abs(c) ** 2)
        assert transverse_norm < 1e-10, (
            f"K_total(t={t[t_idx]:.2f}) transverse_norm = {transverse_norm:.3e}; "
            f"Card A4 v0.1.1 B.1 violated"
        )


# ─── Validation / routing ──────────────────────────────────────────────────


def test_K_total_negative_N_card_raises():
    t = _coarse_t_grid()
    with pytest.raises(ValueError, match="non-negative"):
        tr.K_total_thermal_on_grid(
            -1,
            t,
            _hs(),
            sigma_x,
            bath_state=_thermal_state(),
            spectral_density=_ohmic_sd(),
        )


def test_K_total_N_card_3_succeeds_post_phase_b2():
    """DG-4 Phase B.2 wires n=3 (returns zero by Gaussianity), so
    K_total at N_card=3 now matches K_total at N_card=2 for thermal."""
    t = _coarse_t_grid()
    K_at_2 = tr.K_total_thermal_on_grid(
        2, t, _hs(), sigma_x, bath_state=_thermal_state(), spectral_density=_ohmic_sd()
    )
    K_at_3 = tr.K_total_thermal_on_grid(
        3, t, _hs(), sigma_x, bath_state=_thermal_state(), spectral_density=_ohmic_sd()
    )
    np.testing.assert_allclose(K_at_3, K_at_2, atol=1e-12)


def test_K_total_N_card_4_raises_pending_recursion():
    """DG-4 Phase B.2 covers n in {0, 1, 2, 3}; n=4 is the deferred
    follow-up."""
    t = _coarse_t_grid()
    with pytest.raises(NotImplementedError, match="n=4|deferred"):
        tr.K_total_thermal_on_grid(
            4,
            t,
            _hs(),
            sigma_x,
            bath_state=_thermal_state(),
            spectral_density=_ohmic_sd(),
        )


def test_K_3_thermal_pure_dephasing_is_zero():
    """A3 fixture (σ_z + thermal Gaussian): K_3 = 0 by parity + thermal
    D̄_1 = 0. This is the Phase B.2 falsification at the K_n level —
    consistent with cbg.cumulants Phase B.1's D̄_3 = 0 witness."""
    t = _coarse_t_grid()
    K3 = tr.K_n_thermal_on_grid(
        3, t, _hs(), sigma_z,
        bath_state=_thermal_state(), spectral_density=_ohmic_sd(),
    )
    np.testing.assert_allclose(K3, np.zeros_like(K3), atol=1e-12)


def test_K_3_thermal_sigma_x_is_zero():
    """A4 fixture (σ_x + thermal Gaussian): K_3 = 0 by parity (odd-order
    vanishing for σ_x parity-class theorem, Letter App. D), independent
    of the σ_z Feynman-Vernon argument."""
    t = _coarse_t_grid()
    K3 = tr.K_n_thermal_on_grid(
        3, t, _hs(), sigma_x,
        bath_state=_thermal_state(), spectral_density=_ohmic_sd(),
    )
    np.testing.assert_allclose(K3, np.zeros_like(K3), atol=1e-12)


def test_K_n_non_thermal_points_to_displaced_entry_point():
    """The thermal-only path points displaced cards to the displaced runner."""
    t = _coarse_t_grid()
    bs = {"family": "coherent_displaced", "temperature": 0.0, "displacement_amplitude": 1.0}
    with pytest.raises(NotImplementedError, match="K_total_displaced_on_grid"):
        tr.K_n_thermal_on_grid(
            2,
            t,
            _hs(),
            sigma_x,
            bath_state=bs,
            spectral_density=_ohmic_sd(),
        )


# ─── L_n shim with the existing-stub signature ─────────────────────────────


def test_L_n_shim_thermal_n_2_dispatches_to_thermal_at_time():
    """The L_n shim routes thermal n=2 to L_n_thermal_at_time."""
    t = _coarse_t_grid()
    H_S = _hs()
    A = sigma_z
    D = _D_bar_2_for_grid(t, _thermal_state(), _ohmic_sd())
    via_shim = tr.L_n(
        n=2,
        t_idx=5,
        t_grid=t,
        system_hamiltonian=H_S,
        coupling_operator=A,
        D_bar_2_array=D,
        bath_state=_thermal_state(),
    )
    via_direct = tr.L_n_thermal_at_time(2, 5, t, H_S, A, D_bar_2_array=D)
    X = sigma_x
    np.testing.assert_allclose(via_shim(X), via_direct(X), atol=1e-12)


def test_L_n_shim_n_3_returns_zero_post_phase_b2():
    """The L_n shim now routes n=3 through L_n_thermal_at_time, which
    returns the zero superoperator for thermal Gaussian baths."""
    L3 = tr.L_n(
        n=3,
        t_idx=0,
        t_grid=_coarse_t_grid(),
        system_hamiltonian=_hs(),
        coupling_operator=sigma_x,
        bath_state=_thermal_state(),
    )
    X = sigma_z
    out = L3(X)
    np.testing.assert_allclose(out, np.zeros_like(X), atol=1e-12)


def test_L_n_shim_n_4_raises_pending_recursion():
    """n=4 is the deferred Phase B.2 follow-up."""
    with pytest.raises(NotImplementedError, match="n=4|deferred"):
        tr.L_n(
            n=4,
            t_idx=0,
            t_grid=_coarse_t_grid(),
            system_hamiltonian=_hs(),
            coupling_operator=sigma_x,
            bath_state=_thermal_state(),
        )


def test_L_n_shim_non_thermal_points_to_displaced_entry_point():
    bs = {"family": "coherent_displaced", "displacement_amplitude": 1.0}
    with pytest.raises(NotImplementedError, match="K_total_displaced_on_grid"):
        tr.L_n(
            n=2,
            t_idx=5,
            t_grid=_coarse_t_grid(),
            system_hamiltonian=_hs(),
            coupling_operator=sigma_x,
            bath_state=bs,
        )


def test_L_n_shim_missing_required_kwargs_raises():
    with pytest.raises(ValueError, match="missing required kwargs"):
        tr.L_n(n=2)


# ─── Stubbed: canonical_lindblad_form ──────────────────────────────────────


def test_canonical_lindblad_form_remains_pending():
    with pytest.raises(NotImplementedError, match="not implemented"):
        tr.canonical_lindblad_form(lambda X: X)


# ─── Composability with Cards A3 v0.1.1 and A4 v0.1.1 ──────────────────────


def test_K_total_composes_with_A3_v011_thermal_case():
    """End-to-end smoke: load A3 v0.1.1, compute K_total over a coarse
    sub-grid, verify K = H_S exactly (the pure-dephasing thermal trivialisation).

    Uses a coarse 11-point sub-grid of the card's 200-point grid for test
    speed; the full 200-point run is exercised in Phase D once the runner
    is wired."""
    a3 = yaml.safe_load((CARDS_DIR / "A3_pure-dephasing_v0.1.1.yaml").read_text())
    fp = a3["frozen_parameters"]
    bs = fp["model"]["test_cases"][0]["bath_state"]
    sd = fp["model"]["bath_spectral_density"]
    omega = 1.0
    H_S = 0.5 * omega * sigma_z
    A = sigma_z
    t = np.linspace(0.0, 5.0, 11)  # coarse sub-grid
    K = tr.K_total_thermal_on_grid(2, t, H_S, A, bath_state=bs, spectral_density=sd)
    for t_idx in range(len(t)):
        np.testing.assert_allclose(K[t_idx], H_S, atol=1e-10)


def test_K_total_composes_with_A4_v011_thermal_case():
    """End-to-end smoke: load A4 v0.1.1, compute K_total over a coarse
    sub-grid, verify the parity-class theorem (no transverse components)."""
    a4 = yaml.safe_load((CARDS_DIR / "A4_sigma-x-thermal_v0.1.1.yaml").read_text())
    fp = a4["frozen_parameters"]
    bs = fp["model"]["test_cases"][0]["bath_state"]
    sd = fp["model"]["bath_spectral_density"]
    omega = 1.0
    H_S = 0.5 * omega * sigma_z
    A = sigma_x
    t = np.linspace(0.0, 5.0, 11)
    K = tr.K_total_thermal_on_grid(2, t, H_S, A, bath_state=bs, spectral_density=sd)
    for t_idx in range(len(t)):
        K_t = K[t_idx]
        b = 0.5 * np.trace(sigma_x @ K_t)
        c = 0.5 * np.trace(sigma_y @ K_t)
        transverse = np.sqrt(abs(b) ** 2 + abs(c) ** 2)
        assert transverse < 1e-10, (
            f"A4 v0.1.1 K_total(t={t[t_idx]:.2f}) transverse_norm " f"{transverse:.3e} violates B.1"
        )

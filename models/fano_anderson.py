"""
models.fano_anderson — Fano–Anderson model.

Natural venue for DG-5 (thermodynamic discriminant). Solvable; admits
a known K(t) under the minimal-dissipation gauge (Picatoste, Colla,
Breuer, PRR 6, 013258 (2024)) AND comparison with a competing
framework (e.g. Hamiltonian of mean force, polaron) to satisfy the
"distinguishable thermodynamic prediction" criterion of DG-5.

Structural constraints declared for DG-2:
    - basis-independence of K (universal default);
    - fermion-number conservation;
    - particle-hole symmetry where applicable.

DG-5 pass criterion (per Sail v0.5 §9):
    Identify at least one thermodynamic observable (work extraction,
    efficiency, heat current, work-heat partition) where the
    minimal-dissipation K(t) and the competing framework yield
    NUMERICALLY DISTINGUISHABLE predictions in the same model
    parameter regime. Side-by-side computation in a regime where
    the two predictions agree is NOT a DG-5 pass.

Stub depth at v0.1.0 (Path S10-a):
    This module is *not* a DG-1 venue (DG-1 covers CL-2026-005 v0.4
    Entries 1, 3, 4, which use pure_dephasing and spin_boson_sigma_x).
    The model is referenced by Card E1 (DG-5 scope-definition) as the
    natural Fano–Anderson venue for the thermodynamic discriminant.
    A callable model API is not yet implemented: the four prerequisite
    pieces are (i) Fano–Anderson Hamiltonian + coupling factory,
    (ii) Hamiltonian-of-mean-force (HMF) reference for the competing-
    framework comparison, (iii) fermionic-bath cumulant support in
    cbg/, (iv) a DG-5 work plan.

    The functions below provide a **callable stub API surface** so
    that any future card or runner code can reference
    ``models.fano_anderson.<fn>`` without ``AttributeError``;
    each stub raises ``ScopeDefinitionNotRunnableError`` *when called*
    (NOT on import), so ``from models import fano_anderson`` and
    Sphinx autodoc still succeed. The error message names the
    prerequisite pieces so the path forward is auditable.
"""

from typing import Any

structural_constraints = (
    "basis_independence",
    "fermion_number_conservation",
    "particle_hole_symmetry",
)


_SCOPE_DEFINITION_PRECONDITIONS = (
    "models.fano_anderson is scope-definition only (Path S10-a, work-package "
    "§6 item 8). Prerequisites before a callable API can land: "
    "(i) Fano-Anderson Hamiltonian + coupling factory; "
    "(ii) Hamiltonian-of-mean-force reference (competing-framework gauge); "
    "(iii) fermionic-bath cumulant support in cbg/; "
    "(iv) DG-5 work plan. See benchmarks/benchmark_cards/"
    "E1_thermodynamic-discriminant-fano-anderson_v0.1.0.yaml failure_mode_log."
)


def hamiltonian(*args: Any, **kwargs: Any) -> Any:
    """Stub Fano–Anderson Hamiltonian factory. Raises when called."""
    # Late import to avoid a models → reporting dependency cycle at import time.
    from reporting.benchmark_card import ScopeDefinitionNotRunnableError

    raise ScopeDefinitionNotRunnableError(_SCOPE_DEFINITION_PRECONDITIONS)


def coupling_operator(*args: Any, **kwargs: Any) -> Any:
    """Stub Fano–Anderson coupling-operator factory. Raises when called."""
    from reporting.benchmark_card import ScopeDefinitionNotRunnableError

    raise ScopeDefinitionNotRunnableError(_SCOPE_DEFINITION_PRECONDITIONS)


def system_arrays_from_spec(model_spec: dict[str, Any]) -> Any:
    """Stub (H_S, A) builder from a card's ``frozen_parameters.model`` block.

    Mirrors the spin_boson_sigma_x / pure_dephasing signature for forward
    compatibility. Raises ``ScopeDefinitionNotRunnableError`` when called.
    """
    from reporting.benchmark_card import ScopeDefinitionNotRunnableError

    raise ScopeDefinitionNotRunnableError(_SCOPE_DEFINITION_PRECONDITIONS)

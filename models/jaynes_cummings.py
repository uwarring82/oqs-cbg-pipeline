"""
models.jaynes_cummings — Jaynes–Cummings model.

Solvable model used for Tier 2 (perturbative convergence) and as a
candidate venue for Tier 4 / DG-5 (thermodynamic discriminant against
competing gauges).

Structural constraints declared for DG-2:
    - basis-independence of K (universal default);
    - RWA-consistency of computed K_n;
    - block-diagonal structure preserved by JC dynamics.

Reference for exact TCL form: Smirne & Vacchini, PRA 82, 022110 (2010).

Stub depth at v0.1.0 (Path S10-a):
    This module is *not* a DG-1 venue (DG-1 covers CL-2026-005 v0.4
    Entries 1, 3, 4, which use pure_dephasing and spin_boson_sigma_x).
    No benchmark card references this model yet; the next-earliest
    use is DG-2 (perturbative-convergence checks) or DG-5
    (competing-gauge thermodynamic discriminant).

    The functions below provide a **callable stub API surface** so
    that any future card or runner code can reference
    ``models.jaynes_cummings.<fn>`` without ``AttributeError``;
    each stub raises ``ScopeDefinitionNotRunnableError`` *when called*
    (NOT on import), so ``from models import jaynes_cummings`` and
    Sphinx autodoc still succeed.
"""

from typing import Any

structural_constraints = (
    "basis_independence",
    "rwa_consistency",
    "jc_block_diagonal",
)


_SCOPE_DEFINITION_PRECONDITIONS = (
    "models.jaynes_cummings is scope-definition only (Path S10-a, work-package "
    "§6 item 8). No benchmark card targets the Jaynes-Cummings model at v0.1.0; "
    "a callable API will land when the first card referencing this model is "
    "drafted (no earlier than DG-2 perturbative-convergence work or DG-5 "
    "competing-gauge discriminant). Reference for the exact TCL form: "
    "Smirne & Vacchini, PRA 82, 022110 (2010)."
)


def hamiltonian(*args: Any, **kwargs: Any) -> Any:
    """Stub Jaynes–Cummings Hamiltonian factory. Raises when called."""
    # Late import to avoid a models → reporting dependency cycle at import time.
    from reporting.benchmark_card import ScopeDefinitionNotRunnableError

    raise ScopeDefinitionNotRunnableError(_SCOPE_DEFINITION_PRECONDITIONS)


def coupling_operator(*args: Any, **kwargs: Any) -> Any:
    """Stub Jaynes–Cummings coupling-operator factory. Raises when called."""
    from reporting.benchmark_card import ScopeDefinitionNotRunnableError

    raise ScopeDefinitionNotRunnableError(_SCOPE_DEFINITION_PRECONDITIONS)


def system_arrays_from_spec(model_spec: dict[str, Any]) -> Any:
    """Stub (H_S, A) builder from a card's ``frozen_parameters.model`` block.

    Mirrors the spin_boson_sigma_x / pure_dephasing signature for forward
    compatibility. Raises ``ScopeDefinitionNotRunnableError`` when called.
    """
    from reporting.benchmark_card import ScopeDefinitionNotRunnableError

    raise ScopeDefinitionNotRunnableError(_SCOPE_DEFINITION_PRECONDITIONS)

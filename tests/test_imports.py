# SPDX-License-Identifier: MIT
"""
test_imports — Smoke tests for repository structural compliance.

These tests do NOT verify scientific correctness. They verify only that:
    - the package imports cleanly;
    - the protective documents are present;
    - module stubs raise NotImplementedError as expected at v0.1.0.

Scientific tests are added as Decision Gates pass.
"""

import os


def test_protective_docs_exist():
    """Sail v0.5 §11: five protective docs must be present at HEAD."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for required in (
        "docs/endorsement_marker.md",
        "docs/stewardship_conflict.md",
        "docs/do_not_cite_as.md",
        "docs/validity_envelope.md",
        "docs/benchmark_protocol.md",
    ):
        assert os.path.isfile(
            os.path.join(repo_root, required)
        ), f"Mandatory protective doc missing: {required}"


def test_ledger_vendored():
    """The cleared Ledger v0.4 must be vendored."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert os.path.isfile(
        os.path.join(repo_root, "ledger/CL-2026-005_v0.4.md")
    ), "Vendored Ledger CL-2026-005 v0.4 missing"


def test_sail_vendored():
    """The active Sail v0.5 must be vendored. The previous v0.4 is also retained."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert os.path.isfile(
        os.path.join(repo_root, "sail/sail-cbg-pipeline_v0.5.md")
    ), "Vendored Sail v0.5 missing"
    assert os.path.isfile(
        os.path.join(repo_root, "sail/sail-cbg-pipeline_v0.4.md")
    ), "Vendored Sail v0.4 missing (retained per supersedure discipline)"


def test_cbg_imports():
    """The cbg package must import without error and expose anchor metadata."""
    import re

    import cbg

    # __version__ is sourced from package metadata (pyproject.toml). It must be
    # a non-empty PEP 440-style identifier; we do not pin a literal value here
    # because the version is bumped per release without test churn.
    assert isinstance(cbg.__version__, str) and cbg.__version__
    assert re.match(r"^\d+\.\d+", cbg.__version__) or cbg.__version__ == "0.0.0+unknown"

    assert cbg.__sail_version__ == "0.5"
    assert cbg.__ledger_anchor__ == "CL-2026-005_v0.4"


def test_stubs_raise_notimplementederror():
    """Stubs not yet implemented must raise NotImplementedError.

    Covers every still-stubbed function across cbg/ and the DG-1-venue
    model modules. As DG-1 Phase C lands, entries are removed from
    ``cases`` (and replaced by behaviour tests in dedicated test
    modules); see the per-module test files (e.g. tests/test_basis.py)
    for behaviour assertions on the implemented functions. This test
    is for the still-stubbed surface.

    Non-DG-1 model modules (jaynes_cummings, fano_anderson) carry
    callable stub functions at v0.1.0 (Path S10-a from work-package §6
    item 8): the API surface is present so future cards / runner code
    can reference ``models.<stub>.<fn>`` without ``AttributeError``,
    but each function raises ``ScopeDefinitionNotRunnableError`` (a
    ``NotImplementedError`` subclass) when called. See those modules'
    docstrings for the prerequisite-implementation list.
    """
    from cbg import basis, diagnostics, effective_hamiltonian
    from models import fano_anderson, jaynes_cummings

    # (callable, args, kwargs) — args sized so each call would otherwise reach
    # the function body. The body must raise NotImplementedError.
    #
    # Removed (now implemented; see per-module test files):
    #   - basis.matrix_unit_basis              (DG-1 Phase C.1; tests/test_basis.py)
    #   - basis.verify_orthonormality          (DG-1 Phase C.1; tests/test_basis.py)
    #   - basis.su_d_generator_basis           (DG-2 Card B3 v0.1.0; tests/test_basis.py;
    #                                           d=2 only at v0.1.0, higher d still raises NotImplementedError)
    #   - effective_hamiltonian.K_from_generator
    #     (DG-1 Phase C.3; tests/test_effective_hamiltonian.py)
    #   - pure_dephasing.hamiltonian           (DG-1 Phase C.9; tests/test_pure_dephasing.py)
    #   - pure_dephasing.coupling_operator     (DG-1 Phase C.9; tests/test_pure_dephasing.py)
    #   - spin_boson_sigma_x.hamiltonian
    #     (DG-1 Phase C.10; tests/test_spin_boson_sigma_x.py)
    cases = [
        # su_d_generator_basis at d > 2 still stubbed pending higher-d freeze.
        (basis.su_d_generator_basis, (3,), {}),
        (effective_hamiltonian.K_perturbative, (2,), {}),
        (diagnostics.perturbative_order_norms, ([],), {}),
        (diagnostics.tcl_invertibility_distance, (None,), {}),
        (diagnostics.basis_independence_check, (None, [], []), {}),
        # WS-Lb S10 (2026-05-11): scope-definition stubs in non-DG-1 models.
        # Each raises ScopeDefinitionNotRunnableError (NotImplementedError subclass).
        (fano_anderson.hamiltonian, (), {}),
        (fano_anderson.coupling_operator, (), {}),
        (fano_anderson.system_arrays_from_spec, ({},), {}),
        (jaynes_cummings.hamiltonian, (), {}),
        (jaynes_cummings.coupling_operator, (), {}),
        (jaynes_cummings.system_arrays_from_spec, ({},), {}),
    ]

    for case in cases:
        if case is None:
            continue
        callable_obj, args, kwargs = case
        try:
            callable_obj(*args, **kwargs)
        except NotImplementedError:
            pass
        else:
            raise AssertionError(
                f"{callable_obj.__module__}.{callable_obj.__name__} did not raise NotImplementedError"
            )


def test_scope_definition_stub_modules_import_cleanly():
    """WS-Lb S10 (Path S10-a) contract: scope-definition stub modules must
    import without raising. Importing models.fano_anderson or
    models.jaynes_cummings must succeed even though every callable in those
    modules raises when invoked; otherwise Sphinx autodoc, ``from models
    import *``, and any CI step that imports the ``models`` package as a
    whole would break.
    """
    from models import fano_anderson, jaynes_cummings  # noqa: F401

    # Module-level attributes (structural_constraints + the stub functions)
    # must be present without invoking them.
    assert isinstance(fano_anderson.structural_constraints, tuple)
    assert isinstance(jaynes_cummings.structural_constraints, tuple)
    assert callable(fano_anderson.hamiltonian)
    assert callable(fano_anderson.coupling_operator)
    assert callable(fano_anderson.system_arrays_from_spec)
    assert callable(jaynes_cummings.hamiltonian)
    assert callable(jaynes_cummings.coupling_operator)
    assert callable(jaynes_cummings.system_arrays_from_spec)


def test_scope_definition_stubs_raise_specific_error():
    """WS-Lb S10 contract: stub functions raise ``ScopeDefinitionNotRunnableError``
    (not just generic ``NotImplementedError``) so callers can pattern-match
    on the precise refusal reason. The error class is defined in
    ``reporting.benchmark_card`` and imported lazily from the stub function
    bodies to avoid a ``models → reporting`` dependency cycle at import time.
    """
    import pytest

    from models import fano_anderson, jaynes_cummings
    from reporting.benchmark_card import ScopeDefinitionNotRunnableError

    # Sanity: the error class is still a NotImplementedError subclass (this
    # is part of the existing public contract via test_benchmark_card.py).
    assert issubclass(ScopeDefinitionNotRunnableError, NotImplementedError)

    for fn, args in (
        (fano_anderson.hamiltonian, ()),
        (fano_anderson.coupling_operator, ()),
        (fano_anderson.system_arrays_from_spec, ({},)),
        (jaynes_cummings.hamiltonian, ()),
        (jaynes_cummings.coupling_operator, ()),
        (jaynes_cummings.system_arrays_from_spec, ({},)),
    ):
        with pytest.raises(ScopeDefinitionNotRunnableError) as exc_info:
            fn(*args)
        # Each error message should name the prerequisite-implementation
        # list so a caller catching the error gets actionable context.
        assert "scope-definition" in str(exc_info.value).lower()


def test_diagnostics_constants_present():
    """cbg.diagnostics must export the five DG-4 cause labels (Sail v0.5 §9 DG-4).

    These are scaffolding constants, not scientific implementations; they
    are exempt from the no-NotImplementedError-before-DG-1 rule and must be
    importable from v0.1.0 onward so benchmark cards can reference the same
    vocabulary.
    """
    from cbg import diagnostics

    expected = {
        "convergence_failure",
        "tcl_singularity",
        "projection_ambiguity",
        "truncation_artefact",
        "benchmark_disagreement",
    }
    assert (
        diagnostics.VALID_CAUSE_LABELS == expected
    ), f"VALID_CAUSE_LABELS mismatch: {diagnostics.VALID_CAUSE_LABELS} vs {expected}"

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
        assert os.path.isfile(os.path.join(repo_root, required)), \
            f"Mandatory protective doc missing: {required}"


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
    """The cbg package must import without error at v0.1.0."""
    import cbg
    assert cbg.__version__ == "0.1.0"
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

    Non-DG-1 model modules (jaynes_cummings, fano_anderson) carry only
    ``structural_constraints`` tuples at v0.1.0 (no function stubs); see
    those modules' docstrings for the rationale and the DG at which their
    function stubs land.
    """
    from cbg import basis, effective_hamiltonian, diagnostics

    # (callable, args, kwargs) — args sized so each call would otherwise reach
    # the function body. The body must raise NotImplementedError.
    #
    # Removed (now implemented; see per-module test files):
    #   - basis.matrix_unit_basis              (DG-1 Phase C.1; tests/test_basis.py)
    #   - basis.verify_orthonormality          (DG-1 Phase C.1; tests/test_basis.py)
    #   - effective_hamiltonian.K_from_generator
    #     (DG-1 Phase C.3; tests/test_effective_hamiltonian.py)
    #   - pure_dephasing.hamiltonian           (DG-1 Phase C.9; tests/test_pure_dephasing.py)
    #   - pure_dephasing.coupling_operator     (DG-1 Phase C.9; tests/test_pure_dephasing.py)
    #   - spin_boson_sigma_x.hamiltonian
    #     (DG-1 Phase C.10; tests/test_spin_boson_sigma_x.py)
    cases = [
        (basis.su_d_generator_basis, (2,), {}),
        (effective_hamiltonian.K_perturbative, (2,), {}),
        (diagnostics.perturbative_order_norms, ([],), {}),
        (diagnostics.tcl_invertibility_distance, (None,), {}),
        (diagnostics.basis_independence_check, (None, [], []), {}),
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
    assert diagnostics.VALID_CAUSE_LABELS == expected, \
        f"VALID_CAUSE_LABELS mismatch: {diagnostics.VALID_CAUSE_LABELS} vs {expected}"

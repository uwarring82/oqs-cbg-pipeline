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
    """Sail v0.4 §11: three protective docs must be present at HEAD."""
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
    """The active Sail v0.4 must be vendored."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert os.path.isfile(
        os.path.join(repo_root, "sail/sail-cbg-pipeline_v0.4.md")
    ), "Vendored Sail v0.4 missing"


def test_cbg_imports():
    """The cbg package must import without error at v0.1.0."""
    import cbg
    assert cbg.__version__ == "0.1.0"
    assert cbg.__sail_version__ == "0.4"
    assert cbg.__ledger_anchor__ == "CL-2026-005_v0.4"


def test_stubs_raise_notimplementederror():
    """v0.1.0 stubs must raise NotImplementedError, not return placeholder values."""
    from cbg import basis, effective_hamiltonian

    # Verify with raw try/except so this works even without pytest installed
    for callable_obj, args in (
        (basis.matrix_unit_basis, (2,)),
        (basis.su_d_generator_basis, (2,)),
    ):
        try:
            callable_obj(*args)
        except NotImplementedError:
            pass
        else:
            raise AssertionError(
                f"{callable_obj.__name__} did not raise NotImplementedError"
            )

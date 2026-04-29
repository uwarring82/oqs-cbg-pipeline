"""
models — Microscopic open-system models served as benchmark targets.

At v0.1.0, the only API exposed by every model module is:

    structural_constraints : tuple[str, ...]
        Model-appropriate DG-2 checks declared by the model.

The callable model API (Hamiltonian, coupling operators, environment
specification, initial bath state) is added per-module as DG-1
implementation lands; the surface is therefore *partial* across modules
at v0.1.0 and will be extended by Phase C of the DG-1 work plan
(plans/dg-1-work-plan_v0.1.0.md). Two of the four modules
(pure_dephasing, spin_boson_sigma_x) carry hamiltonian() and
coupling_operator() function stubs raising NotImplementedError; the
other two (jaynes_cummings, fano_anderson) are not DG-1 venues and
expose only structural_constraints at this version (see those modules'
docstrings for the rationale).

The structural_constraints attribute is consumed by DG-2 verification
(see cbg/effective_hamiltonian.py and cbg/diagnostics.py) to catch
numerically-stable-but-wrong implementations.

Per Sail v0.5 §9 DG-2, models declare the model-appropriate constraints
that stack on top of the universal basis-independence default.
"""

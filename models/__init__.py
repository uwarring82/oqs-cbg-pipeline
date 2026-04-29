"""
models — Microscopic open-system models served as benchmark targets.

Each model module defines:
    H_S, H_E, H_I (system, environment, interaction Hamiltonians)
    rho_E_initial (factorisable initial bath state)
    structural_constraints (model-appropriate DG-2 checks)

The structural_constraints attribute is consumed by DG-2 verification
(see cbg/effective_hamiltonian.py and cbg/diagnostics.py) to catch
numerically-stable-but-wrong implementations.

Per Sail v0.4 §9 DG-2, models declare the model-appropriate constraints
that stack on top of the universal basis-independence default.
"""

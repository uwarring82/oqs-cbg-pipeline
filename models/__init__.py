# SPDX-License-Identifier: MIT
"""
models — Microscopic open-system models served as benchmark targets.

The API exposed by every model module includes:

    structural_constraints : tuple[str, ...]
        Model-appropriate DG-2 checks declared by the model.

The callable model API (Hamiltonian, coupling operators, environment
specification, initial bath state) is intentionally partial across
modules. The DG-1/DG-2 benchmark venues (pure_dephasing,
spin_boson_sigma_x) expose the callable surface needed by their frozen
cards; the other modules remain scaffolded until they receive cards.

The structural_constraints attribute is consumed by DG-2 verification
(see cbg/effective_hamiltonian.py and cbg/diagnostics.py) to catch
numerically-stable-but-wrong implementations.

Per Sail v0.5 §9 DG-2, models declare the model-appropriate constraints
that stack on top of the universal basis-independence default.
"""

# This package is a namespace for individual model submodules; nothing
# is re-exported at the package-init level. Use explicit imports such as
# ``from models import pure_dephasing`` rather than ``from models import *``.
__all__: list[str] = []

"""
reporting.benchmark_card — Read, write, and validate YAML benchmark cards.

Schema enforcement (planned for v0.2.0):
    - frozen_parameters block (all parameters fixed before run);
    - structural_identity_check results (DG-2);
    - failure_asymmetry_clearance status (DG-3);
    - cause_label if applicable (DG-4);
    - stewardship_flag (primary/secondary/conflict-bound);
    - coordinate_choice annotation (Sail §4).
"""


def write_card(spec, path):
    raise NotImplementedError("not implemented at v0.1.0")


def validate_card(path):
    raise NotImplementedError("not implemented at v0.1.0")

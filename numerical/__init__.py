# SPDX-License-Identifier: MIT
"""
numerical — Time-grid integration and tensor operations.

Strictly separate from cbg.bath_correlations to prevent accidental
importation of Markovian solver defaults from libraries like QuTiP
into the bath-correlation evaluation. See cbg/bath_correlations.py
for the rationale.
"""

# Submodules are accessed via explicit import; nothing is re-exported
# at the package-init level.
__all__: list[str] = []

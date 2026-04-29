"""
numerical — Time-grid integration and tensor operations.

Strictly separate from cbg.bath_correlations to prevent accidental
importation of Markovian solver defaults from libraries like QuTiP
into the bath-correlation evaluation. See cbg/bath_correlations.py
for the rationale.
"""

# `models` — System–environment model factories

Concrete system–bath models that supply system Hamiltonians and coupling
operators to the dynamical-card runner. Each module exposes a
`system_arrays_from_spec(model_spec)` factory that consumes the
`frozen_parameters.model` block of a benchmark card and returns
`(H_S, A)` arrays, plus model-specific diagnostics where useful.

`pure_dephasing` is exercised by DG-1 Card A3 and DG-2 Cards B1, B2, B3,
B4-conv-registry, plus DG-3 Card C1; `spin_boson_sigma_x` is exercised by
DG-1 Card A4, DG-2 Card B5-conv-registry, DG-3 Card C2, and DG-4 Card
D1 v0.1.2 (PASS via picture-fixed Path B numerical L_4, 2026-05-06,
superseding the v0.5.0-tagged v0.1.1 verdict that was downgraded on
review the same day). `fano_anderson` is referenced by DG-5 Card E1 as a
scope-definition entry; `run_card(E1)` raises
`ScopeDefinitionNotRunnableError` because the model factory, the HMF
reference, and fermionic-bath support in `cbg.bath_correlations` are not
yet implemented. `jaynes_cummings` remains a scaffold for future plans.

## `models.pure_dephasing`

```{eval-rst}
.. automodule:: models.pure_dephasing
   :members:
```

## `models.spin_boson_sigma_x`

```{eval-rst}
.. automodule:: models.spin_boson_sigma_x
   :members:
```

## `models.fano_anderson`

```{eval-rst}
.. automodule:: models.fano_anderson
   :members:
```

## `models.jaynes_cummings`

```{eval-rst}
.. automodule:: models.jaynes_cummings
   :members:
```

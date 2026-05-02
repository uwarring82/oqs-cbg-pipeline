# `models` — System–environment model factories

Concrete system–bath models that supply system Hamiltonians and coupling
operators to the dynamical-card runner. Each module exposes a
`system_arrays_from_spec(model_spec)` factory that consumes the
`frozen_parameters.model` block of a benchmark card and returns
`(H_S, A)` arrays, plus model-specific diagnostics where useful.

DG-1 currently exercises `pure_dephasing` (Card A3) and
`spin_boson_sigma_x` (Card A4); the remaining modules are scaffolds for
DG-2+ work and may carry `NotImplementedError` stubs at this version.

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

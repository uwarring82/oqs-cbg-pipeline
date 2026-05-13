# `cbg` — Colla–Breuer–Gasbarri effective-Hamiltonian construction

Modules implementing the basis-independent operational expression for the
effective Hamiltonian *K* (Letter Eqs. (6), (7)) and the runner-facing
recursive perturbative expansion (Letter Eq. (15), (16); Companion
Eq. (45)). The thermal-Gaussian path now supports n ≤ 4 through
`cbg.tcl_recursion`; broader Entry-2-wide recursion closure is still
governed by the validity envelope.

All outputs of this package are coordinate-dependent under the
**Hayden–Sorce minimal-dissipation gauge** per Sail v0.5 §4. They are
**not** directly observable Hamiltonians; any plot or table presenting
*K(t)* must carry the gauge annotation specified in
[`docs/benchmark_protocol.md`](https://github.com/uwarring82/oqs-cbg-pipeline/blob/main/docs/benchmark_protocol.md) §1.

## `cbg.effective_hamiltonian`

```{eval-rst}
.. automodule:: cbg.effective_hamiltonian
   :members:
```

## `cbg.basis`

```{eval-rst}
.. automodule:: cbg.basis
   :members:
```

## `cbg.tcl_recursion`

```{eval-rst}
.. automodule:: cbg.tcl_recursion
   :members:
```

## `cbg.cumulants`

```{eval-rst}
.. automodule:: cbg.cumulants
   :members:
```

## `cbg.bath_correlations`

```{eval-rst}
.. automodule:: cbg.bath_correlations
   :members:
```

## `cbg.diagnostics`

```{eval-rst}
.. automodule:: cbg.diagnostics
   :members:
```

# DG-3 Phase F step 1 — OQuPy route blocked by a hard `numpy<2` dependency conflict

**Date:** 2026-05-16
**Type:** experimental-result / dg-3-route-block
**Triggering commit:** _(self-referential; to be populated on commit per [`logbook/README.md`](README.md) §Immutability exception 2)_

**Triggering evidence:**
- Phase F step 1 attempt: `.venv/bin/python -m pip install 'oqupy>=0.5,<0.6'` → wheel metadata `Collecting numpy<2.0,>=1.18 (from oqupy==0.5.0)`; `pip index versions oqupy` → latest is `0.5.0` (0.5.0/0.4.0/0.3.x/0.2.0).
- Environment: numpy 2.4.4, scipy 1.17.1, qutip 5.2.3 (the HEOM gating method is validated on this numpy-2 / qutip-5.2 stack; the 560-test suite runs on numpy 2.x).
- DG-3 work plan [`v0.1.3`](../plans/dg-3-work-plan_v0.1.3.md) §§1.3, 2.3, 2.4 (route correction); supersedes [`v0.1.2`](../plans/dg-3-work-plan_v0.1.2.md).
- Phase E commit `1b4c21d` (declared the now-uninstallable `oqupy>=0.5,<0.6` dependency).

## Summary

DG-3 Phase F step 1 (refresh/install OQuPy) failed on a **hard, mutually-exclusive dependency conflict**, not a transient build error: OQuPy 0.5.0 (the latest release) hard-pins `numpy<2.0,>=1.18`, while the repo's validated HEOM stack is numpy 2.4.4 + qutip 5.2.3. The two intended v0.3.0 gating methods cannot coexist in this Python environment. A subprocess/isolated-env bridge was rejected as disproportionate (steward judgement: it converts DG-3 into environment orchestration and adds a failure surface where a clean reference comparison is needed). **Decision: withdraw the OQuPy/TEMPO route (dormant unless upstream numpy-2 support lands); promote pseudomode (QuTiP `mesolve`; no new dependency; numpy-2-native; non-overlapping auxiliary-system class) as HEOM's gating partner.** No DG-3 verdict; no code; environment unharmed (the failed install rolled back cleanly — `oqupy` absent, `pip check` clean, numpy 2.4.4 / qutip 5.2.3 intact).

## Detail

- OQuPy 0.5.0 wheel metadata requires `numpy<2.0,>=1.18`; `pip` attempted a source-build of numpy 1.26.4 (also fails under clang 21). Even a successful build would downgrade numpy and break HEOM/qutip-5.2 and the suite. No newer OQuPy release exists (0.5.0 is latest).
- v0.1.3 supersedes v0.1.2: §2.3 withdraws OQuPy (retained as a dormant, re-openable option iff upstream drops the `numpy<2` pin); §2.4 promotes pseudomode; card supersedure retargeted **C1/C2 v0.3.0 → v0.4.0** (steward: gating-method-family change is structural, not a v0.3.1 knob bump). Schema v0.1.5 / Option-A four-method scaffolding is method-agnostic and retained (no schema bump).
- **Side effect requiring urgent remediation:** Phase E commit `1b4c21d` declared `oqupy>=0.5,<0.6` as a **hard runtime dependency**. It is uninstallable on numpy-2, so `pip install -e .` / `".[dev]"` fails at that commit. v0.1.3 Phase F.0 (included in this commit; no executable code) removes it and updates `README.md` dependency prose.

## Routing notes

Next: DG-3 work plan v0.1.3 **Phase F** (`benchmarks/pseudomode_reference.py` + tests), then **Phase G** (C1/C2 v0.4.0 cards + N-method runner + `KNOWN_SCHEMA_VERSIONS` v0.1.5 + Rule 19 enforcement), **Phase H** (verdict). Phase F.0 is included here: `pyproject.toml` drops the uninstallable `oqupy` hard dep, and `README.md` dependency prose is updated. No Ledger or Sail change. DG-4 D1 v0.1.2 PASS unchanged. Superseded by execution when Phase F lands.

## Permitted post-commit edits to this entry

Per [`logbook/README.md`](README.md) §Immutability: (1) `superseded by:` annotation when a successor entry is added; (2) self-referential `Triggering commit:` placeholder fill (follow-up message `logbook: fill self-referential triggering-commit placeholder for dg-3-oqupy-numpy2-dependency-blocked`). Any other text edit requires supersedure.

---

*Logbook entry. Immutable once committed.*

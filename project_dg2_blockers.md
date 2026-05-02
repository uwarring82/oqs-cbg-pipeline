---
name: DG-2 progress and remaining blockers
description: Partial DG-2 progress as of 2026-05-01; remaining work gated on specific external/internal items
type: project
---

DG-2 partial progress (as of 2026-05-01):
- **Card B1 v0.1.0 PASS** (commits 4502863 + efcb031) — Entry 1.B.3 *diagonal* pseudo-Kraus reduction reproduces Hayden-Sorce 2022 H_HS at machine precision (3 fixtures, error = 0.0). HPTA gate enforced via runner. Does **not** constitute full DG-2 PASS.

Remaining DG-2 work and its blockers:
1. **Entry 1.B.3 off-diagonal half + Entry 1.D**: gated on a transcription bump (Hayden-Sorce 2022 §3.x off-diagonal extension; same source, not yet transcribed in v0.1.0). Steward action; no external dependency.
2. **Entries 3.B.3, 4.B.2 (coherent-displacement)**: gated on Council-cleared displacement convention. External dependency; unchanged from DG-1 carve-out.
3. **Cross-basis universal-default structural-identity check** (Sail v0.5 §9 DG-2): not externally gated; implementable now as a separate card. Tests basis-independence of `K_from_generator`.

**Why:** B1 closed cleanly the day the first DG-2 unblocker landed; the remaining items are independent work tracks, not a single batch.

**How to apply:** When asked to "advance DG-2," ask which track. Do not assume the displacement-convention gap has cleared — that one still needs Council clearance. Do not start the off-diagonal extension without first bumping or co-authoring the Hayden-Sorce transcription.

---
name: DG-2 progress and remaining work
description: DG-2 structural sub-claims PASS as of 2026-05-04; only literal K_2-K_4 fourth-order recursion remains
type: project
---

DG-2 structural sub-claims PASS (2026-05-04) under the Council-cleared
displacement-profile registry. All five frozen DG-2 cards are at PASS:

- **B1 v0.1.0** — Entry 1.B.3 *diagonal* pseudo-Kraus reduction reproduces
  Hayden–Sorce 2022 H_HS at machine precision (3 fixtures, error = 0.0).
- **B2 v0.1.0** — Entry 1.B.3 *off-diagonal* half + Entry 1.D, off-diagonal
  pseudo-Kraus consequence at machine precision.
- **B3 v0.1.0** — Entry 1.A *basis-independence* of `K_from_generator` at d = 2.
- **B4-conv-registry v0.1.0** — Entry 3.B.3 (coherent-displaced bath, σ_z
  coupling) under all four Council-cleared displacement profiles
  (`delta-omega_c`, `delta-omega_S`, `sqrt-J`, `gaussian`).
- **B5-conv-registry v0.2.0** — Entry 4.B.2 (coherent-displaced bath, σ_x
  coupling) under all four Council-cleared profiles. v0.2.0 supersedes v0.1.0
  same-day after correcting an interaction-picture vs Schrödinger-picture
  prediction error in the σ_x channel.

Remaining DG-2 work:

1. **K_2-K_4 numerical recursion at perturbative order >= 4.** This is the
   literal "fourth-order recursion" portion of the Sail's DG-2 description.
   `cbg.tcl_recursion.L_n_thermal_at_time(n=3)` returns the zero superoperator
   by Gaussian-Wick parity (Phase B.2 wired during DG-4 work); `n=4` remains
   intentionally deferred behind a structured Path A / B / C wall and surfaces
   a `DeferredKnownStructure` error rather than fabricating a candidate
   formula. Analytic Path A (Companion Sec. IV closed form) is the preferred
   deliverable.

**Why:** All structural sub-claims (Entries 1.A, 1.B.3 diagonal, 1.B.3
off-diagonal + 1.D, 3.B.3, 4.B.2) closed cleanly under the Council-cleared
registry on 2026-05-04. A DG-4 v0.1.1 PASS verdict via Path B numerical L_4
was recorded on 2026-05-06 at tag `v0.5.0` and **superseded on review** the
same day for two HIGH-severity defects in the Path B extraction; v0.1.2
supersedure with repaired Path B and operational `omega_max_factor` is
pending. The literal fourth-order CBG recursion (analytic K_2-K_4) remains a
separate work track within DG-2 that does not block other Decision Gates;
analytic Path A for L_4 is the natural deliverable that would unblock both
DG-2's literal fourth-order recursion milestone and DG-4 cross-validation.

**How to apply:** When asked to "advance DG-2," the only remaining work is
the literal K_2-K_4 fourth-order recursion (Path A analytic preferred). Cite
DG-2 PASSes by their card name + entry number, and name the registered
displacement profile when citing Entries 3.B.3 / 4.B.2 (registry extensions
require fresh Council deliberation per subsidiary briefing v0.3.0 §6.1).

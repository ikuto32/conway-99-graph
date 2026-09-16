# Universal-baseline assumption-core audit

## Result

The premise is valid.  In the byte-pinned baseline
`scratch_general_exact.cnf` (SHA-256
`91D22E62625E1221DD46B819E89494DB8141DD4DDC9A06F13B9ABDB530B83242`),
variables `1..3486` are exactly the outer-edge coordinates.  A normalized
local representative fixes all 1,806 variables whose two support fibres are
not disjoint, with one positive or negative literal per variable.  The 1,680
unfixed variables are exactly the edges between disjoint support fibres.

The independent generator in `scratch_root_universal_core_harness.py` does
not import the shared or fixed-local encoders.  It reconstructed all 352 E75
vectors; all were distinct, all had 93 positive and 1,713 negative literals,
and every literal vector and assumption hash matched the original probe path.
Its coordinate-map SHA-256 is
`314B9AB1519F321E0E9B643E2471632AE7B1245EAE6B758C8798A834BD83EEB7`.

## Why the universal and fixed-local outer problems agree

The 1,176 BP rows force outer degree 12.  Hence the sum over all outer pairs
of `edge + common_outer` is

```
84 * C(12,2) + 84*12/2 = 5544 + 504 = 6048.
```

The 3,486 baseline upper bounds have target histogram
`1:924, 2:2562`, also summing to 6,048.  Therefore every upper bound is an
equality.  Conversely, an exact fixed-local edge solution extends the
baseline's one-way product helpers by setting every helper to the actual AND.

The ordinary-C4 disjoint-block rows need one scope qualification: they are
not consequences of BP alone.  BP gives degree 12, zero overlap incidence for
an ordinary C4, and 40 total disjoint incidences.  A C4's opposite pair
already has its two internal common neighbours, so the corresponding pair
upper bound permits every external vertex at most one neighbour in the C4.
There are exactly 40 vertices on disjoint supports, so each has exactly one.
Thus these fixed-local rows follow from the full baseline (BP plus pair
upper bounds).  Direct rebuilding of the four fixed-local CNFs confirmed all
1,806 Boolean edge values and all 1,680 remaining edge coordinates exactly.

## Probe results

One CaDiCaL 1.9.5 instance was used, with a 200,000-conflict budget per row.

| E75 global | record:rep | result | conflicts | seconds | core size (+/-) | E75 assignments covered |
|---:|:---:|:---:|---:|---:|---:|:---:|
| 0 | 0:0 | UNSAT | 10,140 | 9.344 | 85 (68/17) | 0 only |
| 128 | 1:0 | UNSAT | 70,922 | 28.782 | 91 (68/23) | 128 only |
| 192 | 2:0 | UNSAT | 27,700 | 12.062 | 98 (68/30) | 192 only |
| 288 | 4:0 | UNSAT | 36,877 | 14.156 | 92 (68/24) | 288 only |

Every returned core is nonempty, uses only signed non-disjoint edge
assumptions, and is a literal subset of its source's complete assignment.
An independent exact-containment scan over all 352 E75 representatives found
no cross-source reuse: the four raw cores cover exactly their four sources.
Ignoring signs would incorrectly make every core appear compatible with all
352 assignments, since every assignment has the same variable domain.

For the exact baseline `F`, a core `C` may safely exclude another complete
assignment `A` only when **every signed literal** in `C` occurs in `A`.
Matching variable IDs without signs, using a partial assignment, or changing
the baseline hash/coordinate map is unsafe.

E74 containment has not been evaluated: its future normalized catalogue must
first be converted to the same complete 1,806-literal representation.  The
generic harness supports fail-closed catalogue validation, core-only
screening, one-instance incremental solving, atomic checkpoints, and full
99-vertex verification on any SAT answer.

## Artifacts and boundary

- `scratch_root_universal_core_probe.py/json`: four direct solves and raw cores.
- `scratch_root_universal_core_harness.py` and
  `scratch_root_universal_core_harness_smoke.json`: future-catalogue harness
  and four-row containment smoke test.
- `scratch_root_universal_core_audit.py/json`: independent reconstruction,
  fixed-local differential check, and all-352 containment audit (`ok: true`).

This is a four-representative computational probe, not an exhaustive E75 or
E74 universal-baseline sweep.  No independently checked UNSAT proof
certificate was generated.

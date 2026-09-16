# Independent audit of the `E0=77` compression and local-port reduction

## Result

The independent implementation in `scratch_e77_ports_audit.py` reproduces
the saved reduction without a count or coverage discrepancy:

- 883,179 labelled deficit placements in 459 `S7` support orbits;
- 172 support orbits after the solver-free overlap and exact-real spectral
  screen;
- 165 support orbits with an explicit bounded-integer disjoint witness;
- three support orbits and 48 labelled fibre states after exact port
  matchability;
- only support orbit `(1^7, orbit 22)` after the two subsequent local
  necessities, with 512 labelled local graphs in exactly three symmetry
  orbits of sizes `256,128,128`.

The final 512-set and its three canonical orbits agree exactly (not just in
cardinality) with `scratch_general_e77_local_reps.json` after translating the
two vertex labellings.  This is still only a local reduction, not a full
84-outer-vertex lift.

## Spectral constants

For the 21 by 21 normalized compression `R=D/4`, the fixed Ritz values are
`12,-2^6`.  The other fourteen values lie in `[-4,3]` and sum to `77/2`.
The largest possible sum of their squares occurs at
`3^13,(-1/2)^1`.  Hence

```
tr(D^2) <= 16*(12^2 + 6*2^2 + 13*3^2 + (-1/2)^2) = 4564.
```

There are 105 disjoint support pairs.  For `x_FG=4-D_FG`, the row equations
give `sum_{F<G} x_FG=7`, and therefore

```
2*sum_disjoint D_FG^2
  = 2*(105*4^2 - 8*7 + sum_disjoint x_FG^2)
  = 3248 + 2*sum_disjoint x_FG^2.
```

Both `4564` and `3248` are therefore correct.  The exact rational minimum
`b^T(HH^T)^(-1)b` was recomputed by Fraction Gaussian elimination, rather
than by the closed formula used by the source audit.

## Support-orbit audit

Every saved representative was canonicalized under all 5,040 permutations;
its orbit-stabilizer product and the sum of its orbit sizes were checked.
Burnside counts were recomputed independently from the cycle action on the
21 edges of `K7`:

| deficit partition | labelled placements | `S7` orbits | Burnside |
|---|---:|---:|---:|
| `4+3` | 420 | 2 | 2 |
| `4+2+1` | 7,980 | 9 | 9 |
| `3+3+1` | 3,990 | 7 | 7 |
| `3+2+2` | 3,990 | 7 | 7 |
| `4+1+1+1` | 23,940 | 20 | 20 |
| `3+2+1+1` | 71,820 | 42 | 42 |
| `2+2+2+1` | 23,940 | 20 | 20 |
| `3+1^4` | 101,745 | 56 | 56 |
| `2+2+1^3` | 203,490 | 96 | 96 |
| `2+1^5` | 325,584 | 135 | 135 |
| `1^7` | 116,280 | 65 | 65 |
| **total** | **883,179** | **459** | **459** |

The solver-free overlap recursion and independently inverted disjoint Gram
matrix reproduce the same 172 real-bound survivors.  All 165 positive
integer rows in `scratch_root_e77_integer.json` were checked directly from
their signed `x_FG` witnesses (row sums, upper bound, square cost).  The seven
negative CP-SAT rows have no proof certificates; this audit does not elevate
those seven exclusions beyond their recorded computational status.

## Fibre-state completeness and port criterion

All 64 graphs on the four labelled fibre vertices were regenerated from the
exact-symbol BP capacities (and independently compared with the internal
pair upper test).  By deficit `delta=4-e_F`, the complete counts are

```
delta 0,1,2,3,4 : 1,4,7,6,1.
```

In particular, deficit three has all six one-edge graphs: four single sides
and two single diagonals.  It was not omitted.  Deficit two consists of four
adjacent-side pairs, two opposite-side pairs, and the unique two-diagonal
state.

For one root-neighbour group, a port has type `(sigma,required)`.  Compatible
ports have reversed types and must lie in distinct fibres.  Thus:

- types `(0,0)` and `(1,1)` each form a complete multipartite matching
  problem; a perfect matching exists exactly when the total is even and no
  fibre part exceeds half the total;
- `(0,1)` must be matched to `(1,0)`; equality of the two totals and
  `left_i <= total-right_i` for every fibre `i` are precisely Hall's
  conditions.

The full 165-orbit labelled-state scan reproduces the three positive support
orbits.  Every one of their 48 positive states was also expanded into simple
edge matchings and checked directly.  Each positive state has 64 exact
overlap completions, so each support representative initially has 1,024
local configurations.  Every actual overlap square is 22.

## The three port-surviving support graphs

1. `(2+1^5, orbit 0)`: a `K4` plus three isolated group vertices, with one
   distinguished `K4` edge of weight/deficit two and its other five edges of
   weight one.  Support stabilizer order: 24.
2. `(1^7, orbit 2)`: a cone over `P4` plus two isolated group vertices.
   Degree sequence `(4,3,3,2,2,0,0)` and three triangles.  Support stabilizer
   order: 4.
3. `(1^7, orbit 22)`: `theta(1,3,3)` plus one isolated group vertex.  In the
   saved labels its endpoints are groups 3 and 6, with paths
   `3-6`, `3-4-2-6`, and `3-5-1-6`.  Degree sequence
   `(3,3,2,2,2,2,0)` and no triangle.  Support stabilizer order: 4.

All 16 feasible labelled fibre-state assignments form one orbit in each
case.  Quotienting the state-plus-overlap configurations gives:

| support type | raw configs/orbits | after pair upper | after ordinary-C4 support BP |
|---|---:|---:|---:|
| weighted `K4` | 1,024 / 20 | 576 / 10 | 0 / 0 |
| cone over `P4` | 1,024 / 16 | 1,024 / 16 | 0 / 0 |
| `theta(1,3,3)` | 1,024 / 6 | 1,024 / 6 | 512 / 3 |

The action is the full support stabilizer times all `2^7` independent sign
flips.  On exceptional vertices its distinct faithful action orders are
respectively 64, 64, and 256; the smaller numbers only remove kernels from
isolated/unused groups.  The abstract group orders are 3,072, 512, and 512.

## Exactly why orbit 22 goes from 1,024 to 512

The induced-pair upper bound removes none of orbit 22.  The exact additional
condition is the necessary support-incidence completion left after all
ordinary C4 fibres are accounted for.

Let `F` be an exceptional fibre, `u` one of its vertices, `a` its internal
degree, `s` its already chosen overlap degree, and `r` the number of other
exceptional supports disjoint from `F`.  Port balance gives `2a+s=4`.
For every exceptional disjoint support `G`, let `z_G` be the number of
neighbours of `u` in `G`.  Ordinary C4 pair equations force every vertex of
`F` to have exactly one neighbour in every ordinary C4 support disjoint from
`F`.  After subtracting those forced neighbours, the remaining integers must
satisfy

```
sum_G z_G = r+a-2,
sum_{G contains q} z_G = t_q-o_q       for every q not in F,
0 <= z_G <= 4.
```

Here `t_q` counts exceptional disjoint supports containing group `q`, and
`o_q` counts already selected overlap neighbours of `u` whose supports
contain `q`.  These are consequences of degree and exact-symbol BP, not an
extra modelling assumption.

Exactly 512 of the 1,024 orbit-22 configurations solve all these per-vertex
systems.  At the raw symmetry-orbit level, three of the six orbits survive:
one of size 256 and two of size 128.  The other three, also of sizes
256,128,128, fail at least one such incidence system.  This accounts exactly
for `1024 -> 512`; no spectral or induced-pair filtering is hidden in that
step.

## Reproducible artifacts

- `scratch_e77_ports_audit.py`: independent implementation.
- `scratch_e77_ports_audit.json`: full orbit tables, local representatives,
  stage counts, and action data.
- `scratch_e77_ports_compare.py` and `scratch_e77_ports_compare.json`:
  cross-labelling proof that the final three canonical orbit dictionaries
  equal the independently produced reference dictionaries.
- `scratch_e77_ports_summary.md`: this audit report.

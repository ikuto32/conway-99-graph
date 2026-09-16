# Exact bounded structural audit of `E0=74`

## Outcome

At total fibre-edge deficit ten, the unrestricted rooted class has been
reduced, solver-free, from all **28,929,495 labelled weighted support
placements** to **249 weighted `S7` support orbits** (618,408 labelled
placements), and then by an exhaustive labelled fibre-state port census to
**175 support orbits and 29,203 feasible labelled fibre-state assignments**.
Coordinate port matchings, local pair/BP filters, and the full 84-vertex lift
have not yet been enumerated.  Consequently `E0=74` remains **UNKNOWN**; no
SRG witness is claimed.

## Analytic compression

Write `delta_F=4-e_F` on each of the 21 four-vertex fibres.  For `E0=74`,

```
sum_F delta_F = 10.
```

The compression matrix has fixed Ritz values `12,-2^6`.  Its fourteen free
Ritz values lie in `[-4,3]` and sum to `37`.  A convex square objective over
this sliced box is maximized at a vertex, hence at most one coordinate is not
an endpoint.  Exact endpoint enumeration gives `3^13,-2`, with square sum
`121`.  Therefore

```
tr(D^2) <= 16*(12^2 + 6*2^2 + 121) = 4624.
```

For overlap totals `M_FG` and disjoint deviations `x_FG=4-D_FG`,

```
tr(D^2) = sum_F (8-2 delta_F)^2 + 3200 + 2*(M2+X2),
sum_{G overlapping F} M_FG = 4 delta_F,
sum_{G disjoint from F} x_FG = 2 delta_F.
```

The constant is exact because on the 105 disjoint pairs
`2 sum(4-x)^2 = 3360-16*sum(delta)+2 sum(x^2) = 3200+2X2`.
The `X2` lower bound used below is the exact rational unconstrained-real
least-norm value, so it is a rigorous relaxation of the required integer
system (including the omitted `x<=4` condition).

Each deficit-`d` fibre has exactly `2d` BP ports at each of its two root-group
endpoints.  At a fixed group, ports must pair with ports belonging to a
different incident fibre.  Thus necessarily

```
2*max(incident deficits) <= sum(incident deficits).
```

This is orientation-independent.  It is also sufficient for the aggregate
integer overlap totals at one group: they are precisely a loopless
multigraph degree sequence with degrees `2 delta_F`.

## Exhaustive placement census

[`scratch_general_e74_compression.py`](scratch_general_e74_compression.py)
generates every repeated-weight-unlabelled placement on the 21 supports for
all 23 integer partitions of ten.  For each new placement it computes exact
images under all 5,040 permutations of the seven root groups while preserving
the support weights.  Runtime assertions check canonical representatives,
orbit/stabilizer, uniqueness, and that orbit-size sums equal the closed-form
labelled-placement count.  Each partition is committed atomically to
`scratch_general_e74_compression_part_00.json` through
`scratch_general_e74_compression_part_22.json` before and during filtering.

The exact census is:

| deficit partition | labelled placements | weighted `S7` orbits | balanced | exact overlap | exact-real |
|---|---:|---:|---:|---:|---:|
| `4+4+2` | 3,990 | 7 | 0 | 0 | 0 |
| `4+4+1+1` | 35,910 | 28 | 0 | 0 | 0 |
| `4+3+3` | 3,990 | 7 | 0 | 0 | 0 |
| `4+3+2+1` | 143,640 | 69 | 0 | 0 | 0 |
| `4+3+1^3` | 406,980 | 156 | 0 | 0 | 0 |
| `4+2^3` | 23,940 | 20 | 0 | 0 | 0 |
| `4+2^2+1^2` | 610,470 | 226 | 0 | 0 | 0 |
| `4+2+1^4` | 1,627,920 | 504 | 0 | 0 | 0 |
| `4+1^6` | 813,960 | 281 | 0 | 0 | 0 |
| `3^3+1` | 23,940 | 20 | 0 | 0 | 0 |
| `3^2+2^2` | 35,910 | 28 | 0 | 0 | 0 |
| `3^2+2+1^2` | 610,470 | 226 | 1 | 1 | 1 |
| `3^2+1^4` | 813,960 | 292 | 0 | 0 | 0 |
| `3+2^3+1` | 406,980 | 156 | 0 | 0 | 0 |
| `3+2^2+1^3` | 3,255,840 | 933 | 3 | 3 | 3 |
| `3+2+1^5` | 4,883,760 | 1,318 | 1 | 1 | 1 |
| `3+1^7` | 1,627,920 | 500 | 2 | 2 | 2 |
| `2^5` | 20,349 | 21 | 2 | 2 | 2 |
| `2^4+1^2` | 813,960 | 292 | 4 | 4 | 4 |
| `2^3+1^4` | 4,069,800 | 1,143 | 17 | 17 | 17 |
| `2^2+1^6` | 5,697,720 | 1,541 | 50 | 50 | 50 |
| `2+1^8` | 2,645,370 | 764 | 93 | 93 | 93 |
| `1^10` | 352,716 | 148 | 76 | 76 | 76 |
| **total** | **28,929,495** | **8,680** | **249** | **249** | **249** |

Here “exact overlap” is exhaustive nonnegative-integer recursion for the
combined row equations.  It is run only after an orbit fails to be excluded
by the analytic balance condition.  “exact-real” additionally applies the
exact-Fraction disjoint least-norm bound.  All 249 balanced orbits pass both;
the compression master is
[`scratch_general_e74_compression_audit.json`](scratch_general_e74_compression_audit.json).

An independent stage census in
[`scratch_general_e74_balance_audit.json`](scratch_general_e74_balance_audit.json)
recomputes balance directly from all committed representatives.  It verifies
8,680 orbits / 28,929,495 labelled placements and 249 balanced orbits /
618,408 balanced labelled placements.

## Group-resolved exact overlap strengthening

The combined equations above can be strengthened before choosing fibre
orientations: at each endpoint group, fibre `F` has row sum exactly
`2 delta_F`.  [`scratch_general_e74_group_overlap_audit.py`](scratch_general_e74_group_overlap_audit.py)
uses a separate exhaustive dynamic program for the seven loopless integer
multigraphs and sums their exact minimum squares.  All minimizers are directly
verified against their degree rows.

The group-resolved minimum is larger than the combined-row minimum on 130 of
249 orbits (difference histogram `0:119, 2:82, 4:29, 6:15, 8:3, 10:1`), but
all 249 still satisfy the spectral/exact-real bound.  Their remaining bound
slack ranges from 60 to 156.  The complete rows and witnesses are in
[`scratch_general_e74_group_overlap_audit.json`](scratch_general_e74_group_overlap_audit.json).

## Count-only exact labelled fibre-state port census

There are 249 input support orbits and 134,371,022 labelled products of their
allowed induced fibre states.  The domains retain every orientation and type:
four states at deficit one, seven at deficit two, and all six states at
deficit three.  In particular the two deficit-three states with the same
aggregate signature remain distinct state indices.

[`scratch_general_e74_port_census.py`](scratch_general_e74_port_census.py)
does not materialize this Cartesian product.  For each root group it
exhaustively projects all Hall-matchable local assignments to sets of
extendable state-index prefixes.  A fixed-order global DFS tests both endpoint
groups after each fibre choice and prunes a subtree only when its current
prefix has no local completion.  For every support row it asserts

```
feasible leaf count + pruned suffix-product count = full Cartesian product.
```

Only 523,800 partial nodes are visited.  The exact partition census is:

| deficit partition | support inputs | labelled tuples covered | DFS nodes | feasible supports | feasible tuples |
|---|---:|---:|---:|---:|---:|
| `3^2+2+1^2` | 1 | 4,032 | 338 | 1 | 44 |
| `3+2^2+1^3` | 3 | 56,448 | 2,962 | 3 | 116 |
| `3+2+1^5` | 1 | 43,008 | 1,060 | 1 | 56 |
| `3+1^7` | 2 | 196,608 | 2,240 | 2 | 96 |
| `2^5` | 2 | 33,614 | 2,786 | 2 | 193 |
| `2^4+1^2` | 4 | 153,664 | 5,058 | 4 | 266 |
| `2^3+1^4` | 17 | 1,492,736 | 27,384 | 15 | 1,716 |
| `2^2+1^6` | 50 | 10,035,200 | 87,520 | 41 | 4,924 |
| `2+1^8` | 93 | 42,663,936 | 175,236 | 65 | 9,268 |
| `1^10` | 76 | 79,691,776 | 219,216 | 41 | 12,524 |
| **total** | **249** | **134,371,022** | **523,800** | **175** | **29,203** |

The merged output is
[`scratch_general_e74_port_census.json`](scratch_general_e74_port_census.json),
with atomic per-partition checkpoints.  The category/Hall formula was also
checked against a direct perfect-matching DFS on every group layout occurring
in the input.  [`scratch_general_e74_port_group_check.json`](scratch_general_e74_port_group_check.json)
records 49 layouts, 20,476 labelled group-state assignments, and 4,497 unique
signature rows, with exact agreement.  The first feasible global assignment
of every positive support row is checked using the direct matcher as well.

## Claim boundary

- The spectral bound, trace identities, group port equations, and balance
  obstruction are analytic necessary conditions.
- The placement/orbit coverage, overlap recursion, rational relaxation,
  group-resolved dynamic program, and labelled fibre-state port census are
  exact solver-free finite computations.
- No CP-SAT/SAT status or uncertified negative result is used.
- The surviving 175 support orbits / 29,203 labelled fibre states have not yet
  been expanded through all coordinate matchings, and no claim of `E0=74`
  SAT/UNSAT is made.

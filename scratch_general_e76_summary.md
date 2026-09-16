# Complete bounded structural audit of `E0=76`

## Outcome

The unrestricted rooted `E0=76` class is reduced, without a local SAT
assumption, to **10 weighted-support branches and 311 explicit local-graph
orbits** (68,864 labelled local graphs).  It is **not eliminated** by this
audit.  The exact full 84-vertex lift of these representatives is a separate
SAT task, so the present status of `E0=76` is `UNKNOWN`.

The compression and local counts were reproduced independently.  All 311
representatives were also reconstructed from their explicit edge lists and
checked independently for the fibre, port, pair, BP, spectral, and weighted
symmetry conditions described below.

## Spectral compression

Write `delta_F=4-e_F` for the edge deficit of each of the 21 four-vertex
fibres.  At `E0=76`,

```
sum_F delta_F = 8.
```

The fourteen free Ritz values of the compression matrix lie in `[-4,3]`,
have sum 38, and their square sum is maximized by `3^13,(-1)^1`.  Hence

```
tr(D^2) <= 4576,
tr(D^2) = sum_F (8-2 delta_F)^2 + 3232
          + 2 (M2 + X2).
```

Here `M2` is the sum of squares of overlap-block counts, and `X2` is the sum
of squares of the disjoint deviations `x_FG=4-D_FG`.  Their row equations
are, respectively, `sum M_FG=4 delta_F` and
`sum x_FG=2 delta_F`.

[`scratch_general_e76_compression_audit.py`](scratch_general_e76_compression_audit.py)
enumerates all 3,070,914 labelled deficit placements in all 15 integer
partitions of 8.  Exact `S7` canonicalization gives 1,260 orbits; every orbit
size is checked against the full 5,040-element action.  Solver-free
nonnegative-integer overlap recursion and an exact rational least-norm bound
for the disjoint variables leave 639 orbits:

| partition | `S7` orbits | overlap feasible | exact-real survivors | bounded-integer survivors |
|---|---:|---:|---:|---:|
| `4+4` | 2 | 1 | 0 | 0 |
| `4+3+1` | 9 | 3 | 0 | 0 |
| `4+2+2` | 7 | 3 | 0 | 0 |
| `4+2+1+1` | 42 | 6 | 0 | 0 |
| `4+1^4` | 56 | 6 | 6 | 6 |
| `3+3+2` | 7 | 2 | 0 | 0 |
| `3+3+1+1` | 28 | 11 | 0 | 0 |
| `3+2+2+1` | 42 | 11 | 8 | 4 |
| `3+2+1^3` | 156 | 52 | 27 | 25 |
| `3+1^5` | 135 | 49 | 49 | 49 |
| `2^4` | 10 | 6 | 3 | 3 |
| `2^3+1^2` | 96 | 49 | 32 | 32 |
| `2^2+1^4` | 292 | 185 | 185 | 171 |
| `2+1^6` | 281 | 236 | 236 | 236 |
| `1^8` | 97 | 93 | 93 | 93 |
| **total** | **1,260** | **713** | **639** | **619** |

The last column is only supplemental: it uses one-worker CP-SAT `OPTIMAL` or
infeasibility statuses without proof certificates.  Positive witnesses are
checked directly, but negative statuses are not formally certified.  All
subsequent solver-free local coverage therefore starts from the full 639
exact-real survivors, not the reduced 619.

## Weighted port balance and every labelled fibre state

A deficit-`d` fibre supplies exactly `2d` BP ports at each of its two support
groups.  An overlap edge pairs ports from two different fibres.  Thus, at
each root group, if the incident fibre deficits are `d_1,...,d_m`, necessarily

```
2 max_i d_i <= sum_i d_i.
```

This analytic capacity condition cuts 639 support orbits to 36.  In
particular every surviving support assignment uses only deficits one and
two.

[`scratch_general_e76_port_audit.py`](scratch_general_e76_port_audit.py)
then checks every labelled allowed induced fibre state, with no orientation
or type WLOG:

- deficit one: four P4 states;
- deficit two: six two-side states and the two-diagonal state;
- deficit three: four single-side and two single-diagonal states;
- deficit four: the empty state.

The last two domains are recorded for complete input coverage, although the
weighted capacity test removes every branch containing them.  The full
labelled-state result is:

| partition | exact-real input orbits | balanced orbits | states checked | port-feasible support orbits | feasible states |
|---|---:|---:|---:|---:|---:|
| `2^4` | 3 | 1 | 2,401 | 1 | 23 |
| `2^3+1^2` | 32 | 1 | 5,488 | 1 | 32 |
| `2^2+1^4` | 185 | 4 | 50,176 | 3 | 148 |
| `2+1^6` | 236 | 8 | 229,376 | 7 | 396 |
| `1^8` | 93 | 22 | 1,441,792 | 9 | 608 |
| all partitions containing `3` or `4` | 90 | 0 | 0 | 0 | 0 |
| **total** | **639** | **36** | **1,729,233** | **21** | **1,207** |

For each group, port feasibility is checked by an exact perfect-matching
recursion, including endpoint signs and the prohibition on pairing two ports
from the same fibre.

## Exact overlap matching and local BP expansion

[`scratch_general_e76_local_expansion.py`](scratch_general_e76_local_expansion.py)
expands every exact coordinate matching of all 1,207 states on all 21 support
orbits.  There are 130,560 completions.  For every graph it applies, in
order:

1. the actual overlap square `M2` plus the exact-real disjoint least-norm
   bound;
2. the induced common-neighbour upper bound for every pair of exceptional
   low vertices;
3. the support-aggregate `BP` feasibility forced by all ordinary C4 fibres.

All 130,560 happen to pass the first bound; 109,696 pass the pair bound, and
68,864 pass the forced-C4 BP equations:

| partition | exact overlap graphs | pair-upper | forced-C4 BP | support rows | weighted graph orbits |
|---|---:|---:|---:|---:|---:|
| `2^4` | 2,048 | 1,904 | 1,792 | 1 | 58 |
| `2^3+1^2` | 10,240 | 1,840 | 0 | 0 | 0 |
| `2^2+1^4` | 6,144 | 5,088 | 2,048 | 1 | 52 |
| `2+1^6` | 28,160 | 16,896 | 1,536 | 2 | 22 |
| `1^8` | 83,968 | 83,968 | 63,488 | 6 | 179 |
| **total** | **130,560** | **109,696** | **68,864** | **10** | **311** |

The ten nonempty rows are:

| partition | compression orbit | raw survivors | local orbits | symmetry actions |
|---|---:|---:|---:|---:|
| `2^4` | 1 | 1,792 | 58 | 128 |
| `2^2+1^4` | 20 | 2,048 | 52 | 128 |
| `2+1^6` | 6 | 768 | 16 | 64 |
| `2+1^6` | 87 | 768 | 6 | 256 |
| `1^8` | 1 | 8,192 | 40 | 256 |
| `1^8` | 13 | 43,008 | 74 | 3,072 |
| `1^8` | 15 | 1,024 | 12 | 256 |
| `1^8` | 20 | 8,192 | 28 | 512 |
| `1^8` | 88 | 1,024 | 13 | 1,024 |
| `1^8` | 89 | 2,048 | 12 | 512 |

Orbit indices are scoped to their deficit partition.  The exact action is
the setwise stabilizer of the **weighted** support assignment
`support -> deficit`, together with every independent bit flip on a used root
group.  Permutations of unused root groups are deduplicated because they act
trivially on these local vertices.

An audit assertion deliberately checks that each enumerated labelled graph
set is closed under this action.  This caught an initial implementation error
in which the unweighted support stabilizer could exchange deficit-one and
deficit-two fibres.  That attempted run stopped at the assertion and produced
no final result.  The final JSON and the counts above use the corrected
weighted stabilizer.  Within each final row the graph masks are unique, orbit
images remain in the enumerated set, and orbit sizes sum exactly to the raw
survivor count.

## Explicit representatives and independent normalization check

[`scratch_general_e76_local_graph_reps.json`](scratch_general_e76_local_graph_reps.json)
contains one explicit low-vertex edge list for every one of the 311 local
orbits.  A low vertex on support `{g,h}` is represented as the sorted symbol
pair `[2g+b_g,2h+b_h]`; thus the edge lists are independent of an opaque SAT
variable numbering.

[`scratch_general_e76_reps_check.py`](scratch_general_e76_reps_check.py)
reconstructs every representative and independently checks:

- unique valid edges and vertices;
- exactly one allowed labelled state in every exceptional fibre;
- exactly 16 cross-fibre edges forming the required product of coordinate
  port matchings;
- every induced pair upper bound and every forced-C4 support BP row;
- the actual-overlap/exact-real spectral bound;
- canonical minimality and exact orbit size under the weighted action;
- per-row orbit-size sums.

The result in
[`scratch_general_e76_reps_check.json`](scratch_general_e76_reps_check.json)
is `VERIFIED`: 10 rows, 311 representatives, and raw orbit-size sum 68,864.

As a separate solver-dependent check,
[`scratch_general_e76_integer_local_filter.py`](scratch_general_e76_integer_local_filter.py)
intersects these representatives with the independently computed CP-SAT
disjoint minima from
[`scratch_root_e76_disjoint_integer.json`](scratch_root_e76_disjoint_integer.json).
[`scratch_general_e76_integer_local_filter.json`](scratch_general_e76_integer_local_filter.json)
records no additional reduction: `10/311/68864 -> 10/311/68864`.

## Claim boundary

- The spectral identities and weighted port-capacity inequality are analytic
  necessary conditions.
- Placement, fibre-state, exact-overlap, local-filter, and weighted-symmetry
  coverage is exact finite enumeration.  The local reduction to 311 explicit
  representatives is solver-free.
- The 619-orbit compression column and the supplemental disjoint-minimum
  intersection use CP-SAT without proof certificates and are not used to
  strengthen the solver-free claim.
- No exact full lift has yet been established SAT or UNSAT here.

Therefore `E0=76` remains **UNKNOWN**, represented exhaustively at this local
stage by the 311 graphs in the representative JSON.  No SRG(99,14,1,2)
witness was found in this audit.

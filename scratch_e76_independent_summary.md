# Independent `E0=76` compression and port audit

## Aggregate and orientation-free balance

[`scratch_e76_independent_balance.py`](scratch_e76_independent_balance.py)
reads only `scratch_general_e76_compression_audit.json`; no existing E76 port
code is read or imported.  Direct aggregation reproduces:

- 1,260 `S7` placement orbits;
- 3,070,914 labelled placements;
- 639 orbits passing the solver-free overlap and exact-real disjoint bound
  (1,682,982 labelled placements).

For a support fibre with deficit `d=4-e`, its four vertices have eight BP
quota slots in either support group.  Its `e` internal edges consume `2e`, so
it contributes exactly `8-2e=2d` missing ports to each incident group,
independently of the labelled fibre orientation.  Since these ports must be
paired with ports from *other* fibres, every group necessarily satisfies

```
max(incident deficits) <= sum(other incident deficits).
```

Applying this condition to all 639 real-pass rows leaves exactly 36 support
orbits (46,620 labelled placements):

| deficit partition | all orbits | real-pass | balanced |
|---|---:|---:|---:|
| `2+2+2+2` | 10 | 3 | 1 |
| `2+2+2+1+1` | 96 | 32 | 1 |
| `2+2+1+1+1+1` | 292 | 185 | 4 |
| `2+1+1+1+1+1+1` | 281 | 236 | 8 |
| `1+1+1+1+1+1+1+1` | 97 | 93 | 22 |
| all other partitions | 484 | 90 | 0 |
| **total** | **1,260** | **639** | **36** |

The full per-partition aggregation, all 36 supports, and seven group
diagnostics per support are in
[`scratch_e76_independent_balance.json`](scratch_e76_independent_balance.json).

## All labelled fibre states and exact matching DFS

[`scratch_e76_independent_port.py`](scratch_e76_independent_port.py) starts
from those 36 rows and independently enumerates all 64 edge subsets on a
four-vertex fibre.  BP-bin capacity and same-fibre pair upper bounds give the
complete state counts

```
delta 0,1,2,3,4 : 1,4,7,6,1 states.
```

In particular, deficit two consists of four adjacent-side pairs, two
opposite-side pairs, and both diagonals; deficit three consists of four
single sides and two single diagonals.

For each support row, every product of these labelled state domains is
visited.  For every matched-pair group and restricted state tuple, a fresh
memoized DFS counts all compatible labelled-port perfect matchings.  It
forbids same-fibre matches.  A fixed pair of outer vertices determines a
unique port pair, which is checked explicitly, so every counted matching is
a simple overlap-edge set.

The exhaustive totals are:

| deficit partition | support inputs | states tested | port-surviving supports | feasible states | exact matching completions |
|---|---:|---:|---:|---:|---:|
| `2+2+2+2` | 1 | 2,401 | 1 | 23 | 2,048 |
| `2+2+2+1+1` | 1 | 5,488 | 1 | 32 | 10,240 |
| `2+2+1+1+1+1` | 4 | 50,176 | 3 | 148 | 6,144 |
| `2+1+1+1+1+1+1` | 8 | 229,376 | 7 | 396 | 28,160 |
| `1+1+1+1+1+1+1+1` | 22 | 1,441,792 | 9 | 608 | 83,968 |
| **total** | **36** | **1,729,233** | **21** | **1,207** | **130,560** |

Per-orbit state counts, matching-table sizes, type histograms, and first
witness states are stored in
[`scratch_e76_independent_port.json`](scratch_e76_independent_port.json).

## Claim boundary

This is an exact finite audit of fibre-state and overlap-port feasibility.
The 21 surviving support orbits are only candidates: disjoint-support edges,
ordinary-`C4` completion constraints, the remaining signed BP equations, and
the full outer-pair common-neighbour equalities have not yet been imposed.
Thus this step neither constructs nor proves the existence of an
`srg(99,14,1,2)`.

## Exact overlap-edge expansion

[`scratch_e76_independent_local.py`](scratch_e76_independent_local.py)
reconstructs every one of the 130,560 matching completions as an explicit
simple overlap-edge set.  It was written solely from the independent port
artifacts and does not read or import the existing general E76 local
implementation.  The sequential filters give:

| stage | labelled local graphs |
|---|---:|
| exact overlap matching | 130,560 |
| actual block-square plus exact rational disjoint-real lower bound | 130,560 |
| induced outer-pair upper bound | 109,696 |
| ordinary-`C4` unsigned support-BP feasibility | 68,864 |

The final 68,864 graphs lie on ten support branches and form 311 local
orbits under the full weighted-support stabilizer and all active coordinate
flips:

| partition | support orbit | exact completions | pair-upper | `C4`-BP | local orbits |
|---|---:|---:|---:|---:|---:|
| `2+2+2+2` | 1 | 2,048 | 1,904 | 1,792 | 58 |
| `2+2+1+1+1+1` | 20 | 2,048 | 2,048 | 2,048 | 52 |
| `2+1+1+1+1+1+1` | 6 | 6,400 | 5,504 | 768 | 16 |
| `2+1+1+1+1+1+1` | 87 | 1,536 | 1,536 | 768 | 6 |
| `1^8` | 1 | 8,192 | 8,192 | 8,192 | 40 |
| `1^8` | 13 | 43,008 | 43,008 | 43,008 | 74 |
| `1^8` | 15 | 10,240 | 10,240 | 1,024 | 12 |
| `1^8` | 20 | 8,192 | 8,192 | 8,192 | 28 |
| `1^8` | 88 | 5,120 | 5,120 | 1,024 | 13 |
| `1^8` | 89 | 2,048 | 2,048 | 2,048 | 12 |

For every support branch, the sum of the stored local orbit sizes is asserted
to equal its raw survivor count.  All 311 canonical representatives are
stored explicitly in
[`scratch_e76_independent_local.json`](scratch_e76_independent_local.json),
both as symbol-label edge lists and as zero-based indices in the 84 outer
vertices.

## Independent disjoint integer minima

[`scratch_e76_independent_integer.py`](scratch_e76_independent_integer.py)
independently solves, for each of the ten branches,

```
-12 <= x_FG <= 4,
sum_{G disjoint F} x_FG = 2 delta_F,
minimize sum_{F,G} x_FG^2,
```

where `x_FG=4-D_FG`.  Exact finite value-square tables and each branch's
remaining spectral budget are used.  OR-Tools returned `OPTIMAL` for all ten
branches, with minima

```
20, 12, 12, 10, 8, 8, 10, 8, 8, 8
```

in the table order above.  Every 105-variable witness was directly checked
for range, all 21 row sums, physical `D` range, and objective value.  These
minima agree with the independently produced compression values and remove
no additional local graph: all ten branches and all 311 orbits remain.

The integer output also repeats every retained representative, now annotated
with its actual overlap square, in
[`scratch_e76_independent_integer.json`](scratch_e76_independent_integer.json).
[`scratch_e76_independent_local_audit.py`](scratch_e76_independent_local_audit.py)
mechanically rechecks all 311 explicit edge lists, their orbit coverage, and
all ten integer witnesses;
[`scratch_e76_independent_local_audit.json`](scratch_e76_independent_local_audit.json)
has `"ok": true`.

The integer optimality statements are solver results without independently
checked optimization certificates.  More importantly, these remain local
necessary conditions: the 311 representatives still require exact signed BP,
disjoint block realization, and all outer-pair equalities.

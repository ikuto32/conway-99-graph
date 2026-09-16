# Complete bounded audit of `E0=78`

## Outcome

All `E0=78` branches are computationally UNSAT/INFEASIBLE in two independent
exact encodings after a solver-free compression and local-graph reduction.
No solver emitted an UNSAT proof certificate, so this is reproducible finite
computational evidence rather than a formally certified theorem.

## 1. Compression coverage

Put `delta_F=4-e_F`, so `sum delta_F=6`.  The fourteen free Ritz values of
the fibre compression lie in `[-4,3]`, sum to `39`, and have maximum square
sum `13*3^2+0^2=117`.  Thus

```
tr(D^2) <= 4560,
tr(D^2) = sum_F (8-2 delta_F)^2 + 3264
          + 2 (sum_overlap D_FG^2 + sum_disjoint x_FG^2),
x_FG = 4-D_FG.
```

[`scratch_general_e78_compression_audit.py`](scratch_general_e78_compression_audit.py)
generates all 229,789 labelled placements in all nine partitions and forms
170 exact `S7` orbits.  Every orbit size is checked against its stabilizer by
all 5040 permutations.  Solver-free overlap recursion plus the exact
`Fraction` disjoint least-norm lower bound leaves 67 orbits.

The supplemental bounded integer `x` optimization leaves 50:

| partition | all `S7` orbits | real-relaxation survivors | integer survivors |
|---|---:|---:|---:|
| `2+2+1+1` | 28 | 5 | 2 |
| `2+1+1+1+1` | 56 | 28 | 14 |
| `1+1+1+1+1+1` | 41 | 34 | 34 |
| every other partition | 45 | 0 | 0 |
| **total** | **170** | **67** | **50** |

The integer column used one-worker CP-SAT and has no proof certificates.
It is not needed for the final coverage: the next solver-free stage starts
from the larger set of all 67 real-relaxation survivors.

## 2. Exact local fibre and overlap enumeration

[`scratch_general_e78_local_ports_all.py`](scratch_general_e78_local_ports_all.py)
enumerates every labelled allowed fibre state on all 67 orbits:

- deficit one: all four P4 orientations;
- deficit two: all six two-side subgraphs of the coordinate square and the
  pair of diagonals.

Missing root/inner symbol equations are represented by endpoint ports.  All
simple compatible overlap-port matchings are enumerated group by group, then
checked against induced common-neighbour upper bounds and exact necessary
support-count consequences of ordinary C4 fibres.  This stage is
solver-free.  It leaves four local support forms before the last
support-count test:

| partition/support form | fibre states | overlap graphs | pair-upper survivors | ordinary-C4 support-BP survivors |
|---|---:|---:|---:|---:|
| `2+1^4`, weighted `K4-e` | 20 | 192 | 48 (2 orbits) | 0 |
| `1^6`, `K2,3` | 12 | 512 | 512 (8 orbits) | 512 (8 orbits) |
| `1^6`, bowtie | 32 | 256 | 256 (2 orbits) | 0 |
| `1^6`, `C6` | 16 | 128 | 128 (2 orbits) | 128 (2 orbits) |

Thus only `K2,3` and `C6` remain: 640 labelled local graphs in ten exact
orbits.  [`scratch_general_e78_local_reps.py`](scratch_general_e78_local_reps.py)
regenerates them and verifies closure, disjoint orbit partition,
orbit-stabilizer, and Burnside counts.  The orbit sizes are

```
K2,3: 32,96,96,32,32,96,96,32  (sum 512)
C6:   64,64                       (sum 128).
```

Exact representative edge sets and zero-based outer/one-based full-graph
vertex mappings are in
[`scratch_general_e78_local_reps.json`](scratch_general_e78_local_reps.json).

## 3. Why the strengthening rows are not assumptions

Fix a vertex `u` in an exceptional fibre `F`.  Let

- `a` be its degree inside `F`;
- `r` be the number of exceptional supports disjoint from `F`;
- `z_G` be its number of neighbours in an exceptional disjoint fibre `G`.

Own-support BP gives overlap degree `4-2a`.  Every ordinary disjoint C4
fibre contains exactly one neighbour of `u`, and there are `10-r` such
fibres.  The outer degree equation therefore gives

```
sum_G z_G = 12-a-(4-2a)-(10-r) = r+a-2.             (A)
```

For a base group `q` outside `F`, exactly four supports disjoint from `F`
contain `q`.  If `t_q` of those are exceptional and `o_q` already-realized
overlap neighbours have support containing `q`, summing the two symbol BP
equations at `q` gives

```
sum_{G contains q} z_G = t_q-o_q.                   (B)
```

For `K2,3`, equations (A)-(B) uniquely fix both exceptional-disjoint block
row degrees for every low vertex.  The 24 total rows and 48 individual block
rows added to the compact models are therefore redundant consequences of
the full BP equations, not symmetry breaking or extra hypotheses.

## 4. Exact full lifts and solver results

The exact compact models retain every edge in all 105 disjoint-support
blocks.  Ordinary C4--C4 blocks are permutation matrices; C4--P4 blocks have
only the valid P4-side degree-one condition; exceptional disjoint blocks are
otherwise unrestricted.  They impose all 1176 equations `BP=PA0` and all
3486 outer-pair equalities, with full Boolean equivalences for products.

The initial four-support CNF in
[`scratch_general_e78_exact_sat.py`](scratch_general_e78_exact_sat.py)
eliminated the weighted `K4-e`, bowtie, and `C6` support branches.  The
unfixed `K2,3` support branch timed out at 60 seconds.  Splitting its 512
local graphs into the eight audited orbits gives the exact model
[`scratch_general_e78_k23_sat.py`](scratch_general_e78_k23_sat.py), with
1680 edge variables, 65,520 product variables, and about 653,700 clauses per
branch.  CaDiCaL 1.9.5 returned UNSAT on all eight:

| branch | local orbit | solve seconds | conflicts | decisions |
|---:|---:|---:|---:|---:|
| 0 | 32 | 0.41 | 211 | 420 |
| 1 | 96 | 0.41 | 211 | 420 |
| 2 | 96 | 4.45 | 9,757 | 17,337 |
| 3 | 32 | 5.05 | 9,078 | 16,311 |
| 4 | 32 | 0.44 | 159 | 352 |
| 5 | 96 | 0.72 | 1,047 | 1,624 |
| 6 | 96 | 5.59 | 10,115 | 20,258 |
| 7 | 32 | 6.05 | 9,728 | 22,571 |

Machine-readable logs are in
[`scratch_general_e78_k23_sat_portfolio.json`](scratch_general_e78_k23_sat_portfolio.json).

An independent OR-Tools model in
[`scratch_general_e78_k23_cpsat.py`](scratch_general_e78_k23_cpsat.py)
reconstructs all variables and equations directly rather than translating
the CNF.  It returned INFEASIBLE for all eight `K2,3` branches.  Seven did so
within 7.89--26.17 seconds; branch 3 was UNKNOWN at 30 seconds and then
INFEASIBLE in 32.70 seconds under a 120-second isolated retry.  The two `C6`
local orbits independently returned INFEASIBLE in 8.45 and 8.67 seconds.
Logs are in
[`scratch_general_e78_k23_cpsat.json`](scratch_general_e78_k23_cpsat.json),
[`scratch_general_e78_k23_cpsat_branch03_retry.json`](scratch_general_e78_k23_cpsat_branch03_retry.json),
and [`scratch_general_e78_c6_cpsat.json`](scratch_general_e78_c6_cpsat.json).

## Claim boundary

- Spectral identities, endpoint-port equations, and redundant rows (A)-(B)
  are analytic necessities.
- Placement/orbit generation and local completion are exact solver-free
  finite computations.
- Terminal full-lift exclusions agree between CaDiCaL and independently
  constructed CP-SAT models, but neither produced a checkable UNSAT proof
  certificate.

Therefore `E0=78` is **finite-computationally eliminated**, not claimed as a
proof-assistant-certified theorem.  No SRG(99,14,1,2) witness was produced.

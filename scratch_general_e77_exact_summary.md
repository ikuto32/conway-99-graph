# Complete bounded audit of `E0=77`

## Outcome

All `E0=77` branches are computationally UNSAT/INFEASIBLE after exhaustive
compression, fibre-state, local-edge, and symmetry coverage.  CaDiCaL and an
independently constructed OR-Tools model agree on every final branch.  No
UNSAT proof certificate was produced, so this remains a finite-computational
elimination rather than a formally certified theorem.

## Compression

Here `sum_F delta_F=7`.  The fourteen free Ritz values lie in `[-4,3]`, sum
to `77/2`, and have extremal square multiset `3^13,(-1/2)^1`.  Therefore

```
tr(D^2) <= 4564,
tr(D^2) = sum_F (8-2 delta_F)^2 + 3248
          + 2 (sum_overlap D_FG^2 + sum_disjoint x_FG^2).
```

[`scratch_general_e77_compression_audit.py`](scratch_general_e77_compression_audit.py)
generates all 883,179 labelled placements in all eleven deficit partitions
and forms 459 exact `S7` orbits.  Full 5040-element stabilizer checks verify
every orbit size.  Solver-free nonnegative-integer overlap recursion and the
exact rational disjoint least-norm bound leave 172 orbits:

| partition | `S7` orbits | overlap feasible | exact-real-bound survivors | bounded-integer survivors |
|---|---:|---:|---:|---:|
| `3+2+1+1` | 42 | 6 | 5 | 0 |
| `3+1^4` | 56 | 6 | 6 | 6 |
| `2+2+2+1` | 20 | 4 | 4 | 3 |
| `2+2+1^3` | 96 | 35 | 30 | 29 |
| `2+1^5` | 135 | 68 | 68 | 68 |
| `1^7` | 65 | 59 | 59 | 59 |
| all other partitions | 45 | 4 | 0 | 0 |
| **total** | **459** | **182** | **172** | **165** |

The integer column uses bounded one-worker CP-SAT without proof
certificates.  It is supplemental: the next solver-free screen starts from
all 172 real-bound survivors.

## All fibre states and exact local edges

[`scratch_general_e77_port_audit.py`](scratch_general_e77_port_audit.py)
checks every labelled allowed state, with no type or orientation WLOG:

- deficit one: 4 P4 states;
- deficit two: 6 two-side states plus both diagonals;
- deficit three: 4 single-side states plus 2 single-diagonal states.

It checks 1,566,224 state assignments over all 172 support orbits.  Exact
symbol-port matchability leaves only three support orbits and 48 fibre-state
assignments:

| partition | input support orbits | state assignments checked | local support survivors | feasible states |
|---|---:|---:|---:|---:|
| `3+2+1+1` | 5 | 3,360 | 0 | 0 |
| `3+1^4` | 6 | 9,216 | 0 | 0 |
| `2+2+2+1` | 4 | 5,488 | 0 | 0 |
| `2+2+1^3` | 30 | 94,080 | 0 | 0 |
| `2+1^5` | 68 | 487,424 | 1 | 16 |
| `1^7` | 59 | 966,656 | 2 | 32 |

The independent exact overlap expansion in
[`scratch_root_e77_local.py`](scratch_root_e77_local.py) then gives:

| support orbit | exact overlap completions | induced-pair survivors | ordinary-C4 support-BP survivors |
|---|---:|---:|---:|
| `2+1^5`, orbit 0 | 1,024 | 576 | 0 |
| `1^7`, orbit 2 | 1,024 | 1,024 | 0 |
| `1^7`, orbit 22 | 1,024 | 1,024 | 512 |

The last 512 graphs form exactly three orbits under the full setwise support
stabilizer and independent coordinate flips.  A separate reconstruction in
[`scratch_general_e77_local_reps.py`](scratch_general_e77_local_reps.py)
checks that their orbit sizes are `256,128,128`, pairwise disjoint, and sum
to 512.  The explicit symbol/outer-index representatives are stored in
[`scratch_general_e77_local_reps.json`](scratch_general_e77_local_reps.json).

## Exact full lifts

The final support representative is

```
15, 16, 24, 26, 34, 35, 36
```

and all seven exceptional fibres are P4s.  For each of the three local graph
orbits, [`scratch_general_e77_exact_sat.py`](scratch_general_e77_exact_sat.py)
keeps every disjoint-support edge variable: 46 ordinary C4--C4 permutation
blocks, 48 one-sided C4--P4 blocks, and 11 unrestricted P4--P4 blocks.
Every `BP=PA0` equation and all 3486 outer-pair common-neighbour equalities
are exact.

As in the `E0=78` audit, support-aggregate rows are added only as redundant
consequences.  For a low vertex of same-fibre degree `a`, with `r`
exceptional disjoint supports,

```
sum_G z_G = r+a-2,
sum_{G contains q} z_G = t_q-o_q
```

follows by subtracting the forced one-neighbour contributions of ordinary
disjoint C4 fibres from degree/BP.  In this branch these give 28 total rows
and 56 individually forced low-low block rows; they introduce no new
assumption.

CaDiCaL 1.9.5 results:

| local branch | orbit size | solve seconds | conflicts | decisions |
|---:|---:|---:|---:|---:|
| 0 | 256 | 0.66 | 1,000 | 2,864 |
| 1 | 128 | 2.64 | 3,703 | 6,259 |
| 2 | 128 | 0.62 | 910 | 2,600 |

Each branch has 1,680 edge variables, 65,520 product variables, and about
655,600 clauses.  Full logs are in
[`scratch_general_e77_exact_sat_portfolio.json`](scratch_general_e77_exact_sat_portfolio.json).

[`scratch_general_e77_exact_cpsat.py`](scratch_general_e77_exact_cpsat.py)
independently rebuilds the model in OR-Tools.  All three branches returned
INFEASIBLE in `8.58, 8.75, 8.84` seconds.  Its log is
[`scratch_general_e77_exact_cpsat.json`](scratch_general_e77_exact_cpsat.json).

## Claim boundary

- The spectral and BP identities are analytic necessities.
- Placement, port, local-graph, and symmetry coverage is exact finite
  enumeration; the decisive local reduction is solver-free.
- Final UNSAT agrees across two independently encoded solvers, but neither
  emitted a formally checkable proof certificate.

Thus `E0=77` is **finite-computationally eliminated**.  No
SRG(99,14,1,2) witness was found.

# Exact fibre-compression audit at `E0=79`

This audit is independent of every `E0=80` computation.  It neither assumes
nor cites an `E0=80` SAT result.

## Exact setup

Index the 21 support fibres by the edges of `K7`.  Write

```
e_F     = number of edges inside fibre F,
delta_F = 4-e_F,
E0      = sum_F e_F = 79,
sum_F delta_F = 5.
```

For the symmetric compression `D=4R`, the BP equations give

```
D_FF = 8-2 delta_F,
sum_{G overlaps F} D_FG = 4 delta_F,
sum_{G disjoint F} D_FG = 40-2 delta_F.
```

All entries `D_FG` are nonnegative integers.  On a disjoint support pair put
`x_FG=4-D_FG`.  Then `x_FG<=4` is integral and

```
sum_{G disjoint F} x_FG = 2 delta_F.
```

Summing these 21 equations gives `sum_{F<G} x_FG=5`.  Since `KG(7,2)` has
105 edges,

```
tr(D^2)
  = sum_F (8-2 delta_F)^2
    + 3280
    + 2 sum_overlap D_FG^2
    + 2 sum_disjoint x_FG^2.                         (1)
```

The fixed Ritz values of `R` are `12,-2^6`.  Its other 14 Ritz values lie in
`[-4,3]` and sum to `79/2`.  The exact maximum of their square sum is attained
at `3^13,(1/2)^1`.  Therefore

```
tr(D^2) <= 16 * (12^2 + 6*2^2 + 13*3^2 + (1/2)^2) = 4564.   (2)
```

The six deficit partitions and the resulting budget for
`sum_overlap D_FG^2 + sum_disjoint x_FG^2` are:

| Deficit partition | Diagonal square | Joint square budget |
|---|---:|---:|
| `4+1` | 1252 | 16 |
| `3+2` | 1236 | 24 |
| `3+1+1` | 1228 | 28 |
| `2+2+1` | 1220 | 32 |
| `2+1+1+1` | 1212 | 36 |
| `1+1+1+1+1` | 1204 | 40 |

## Exhaustive placement classification

Every labelled placement was generated and quotiented by the six adjacent
transpositions generating `S7`.  Orbit sizes sum back to the direct labelled
counts.

| Deficit partition | Labelled placements | `S7` orbits | Overlap-row feasible | Survives (1)-(2) |
|---|---:|---:|---:|---:|
| `4+1` | 420 | 2 | 0 | 0 |
| `3+2` | 420 | 2 | 0 | 0 |
| `3+1+1` | 3990 | 7 | 0 | 0 |
| `2+2+1` | 3990 | 7 | 2 | 0 |
| `2+1+1+1` | 23940 | 20 | 3 | 0 |
| `1+1+1+1+1` | 20349 | 21 | 12 | 12 |
| **Total** | **53109** | **59** | **17** | **12** |

For `2+2+1`, the two overlap-feasible orbits already have overlap square 44,
above their joint budget 32.  For `2+1+1+1`, 17 orbits have no nonnegative
integer overlap solution.  The remaining three have:

| Orbit | Minimum overlap square | Remaining `x` budget | Exact integer minimum `sum x^2` |
|---:|---:|---:|---:|
| 0 | 24 | 12 | 13 |
| 4 | 24 | 12 | 15 |
| 5 | 28 | 8 | 11 |

The last column was first obtained by bounded one-worker CP-SAT.  It was
independently rechecked by `scratch_general_e79_boundary_sat.py`: because the
row equations imply `sum x=5`, the script exhausts all signed global value
count profiles within the relevant square budget, then applies an exact
one-hot row-sum CNF with explicit mod-2 rows.  The profile counts are 11, 11,
and 3, respectively, and all 25 CNFs are UNSAT.  As a positive encoding
control, the first profile outside each budget (squares 13, 15, and 11) was
then solved by the same CNF and was SAT with a directly checked row-sum
witness.

Consequently the compression necessary conditions force

```
sixteen fibres with e_F=4, hence induced C4;
five fibres with e_F=3, hence induced P4.
```

The implication `e_F=4 => C4` and `e_F=3 => P4` uses the prior exact local
BP rule: a diagonal fibre edge isolates its two endpoints; otherwise the
fibre graph is a subgraph of its coordinate square.

## The twelve surviving support configurations

Let `H` be the graph on the seven matched-pair groups whose five edges are the
five exceptional `P4` supports.  Its line graph `L(H)` is exactly the overlap
graph on the five supports.  The following table gives all `S7` orbits.
Isolated vertices needed to bring `H` to seven vertices are implicit.

The canonical bit string lists the upper triangle of `L(H)` in order
`01,02,03,04,12,13,14,23,24,34`, minimized over `S5`.  `M2` and `X2` are the
computed exact integer minima of the two off-diagonal square sums in (1).
`slack` means `4564-min tr(D^2)`; it is not extension slack for the full graph.

| ID | Form of `H` | orbit size | degree sequence of `L(H)` | canonical bits | `M2` | `X2` | min `tr(D^2)` | slack |
|---:|---|---:|---|---|---:|---:|---:|---:|
| 0 | `K4-e` | 210 | `4,3,3,3,3` | `0111111011` | 14 | 11 | 4534 | 30 |
| 1 | triangle with two leaves at the same triangle vertex | 630 | `4,4,3,3,2` | `0011111111` | 16 | 11 | 4538 | 26 |
| 2 | triangle with two leaves at distinct triangle vertices | 1260 | `4,3,3,2,2` | `0011101111` | 20 | 9 | 4542 | 22 |
| 3 | `C4` with one pendant edge | 1260 | `3,3,2,2,2` | `0011101101` | 20 | 7 | 4538 | 26 |
| 4 | triangle with a pendant path of length two | 1260 | `3,3,3,2,1` | `0001110111` | 28 | 9 | 4558 | 6 |
| 5 | `C5` | 252 | `2,2,2,2,2` | `0011101100` | 20 | 5 | 4534 | 30 |
| 6 | `K1,5` | 42 | `4,4,4,4,4` | `1111111111` | 10 | 15 | 4534 | 30 |
| 7 | `K1,4` with one edge subdivided | 840 | `4,3,3,3,1` | `0001111111` | 28 | 11 | 4562 | 2 |
| 8 | double star `S(2,2)` | 630 | `4,2,2,2,2` | `0011101011` | 22 | 7 | 4542 | 22 |
| 9 | `K1,3` with one arm subdivided twice | 2520 | `3,2,2,2,1` | `0001110101` | 28 | 7 | 4554 | 10 |
| 10 | `K3 disjoint-union P3` | 420 | `2,2,2,1,1` | `0001110100` | 28 | 7 | 4554 | 10 |
| 16 | `K1,3 disjoint-union P3` | 420 | `2,2,2,1,1` | `0001110100` | 28 | 7 | 4554 | 10 |

The two last rows have isomorphic overlap graphs `K3 disjoint-union K2`, but
their embeddings as five supports in `K7` are not `S7`-equivalent.  The 12
orbit sizes total 9744 of the 20349 labelled five-support sets.

Exact representatives, minimum overlap assignments, and verified integer
`x` witnesses are stored in `scratch_general_e79_compression_audit.json`.

## Claim boundary and reproducibility

The spectral bound and BP equations above are analytic necessities.  The
partition/support result is an exact finite computation using integer
arithmetic:

- support orbits: explicit closure under generators of `S7`;
- overlap minima: solver-free exhaustive recursion;
- disjoint minima: bounded CP-SAT, with every positive witness checked again
  by direct integer arithmetic;
- the only three exclusion decisions depending on the disjoint integer
  solver: independently reproduced by 25 sparse CNFs.

Neither solver run emitted a formally checkable UNSAT proof certificate.
Thus this is a reproducible, independently cross-checked computational
classification, not a proof-assistant theorem.  More importantly, the 12
surviving compressions are only necessary block-total data: no local `P4`
orientation or 84-vertex lift was proved to exist, and `E0=79` itself remains
unexcluded.

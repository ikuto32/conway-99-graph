# Source 724: what the 1,025 pair violations do and do not prove

Status: `SOURCE724_PAIR_VIOLATION_DISCOVERY_INDEPENDENT_AUDIT_PASS`.

The producer is `scratch_theory_e71_source724_pair_violation_discovery.py`;
the independent replay is
`scratch_theory_e71_source724_pair_violation_discovery_audit.py`.  The input
is the explicit 84-vertex degree witness in
`scratch_theory_e71_source724_degree_witness.json`.

## Exact setting

For outer vertices `x,y`, let `rho(x,y)` be the number of common actual
root-neighbour labels, and let `c_out(x,y)` be their number of common outer
neighbours.  The rooted SRG pair equation is

```text
A_xy + c_out(x,y) = 2 - rho(x,y).
```

The stored graph has 84 vertices, 504 edges, degree 12, the exact source-724
compression matrix, and

```text
R^T R = 4 K4, equivalently 16 W^T W = K4.
```

Its residual histogram is

| residual | -2 | -1 | 0 | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pairs | 726 | 768 | 967 | 397 | 334 | 110 | 95 | 89 |

Thus exactly 1,025 of the 3,486 pairs violate the upper equation.

## Classification

The broad endpoint/fibre census is

| endpoint kinds | same fibre | overlapping supports | disjoint supports | total |
|---|---:|---:|---:|---:|
| exceptional--exceptional | 16 | 74 | 74 | 164 |
| exceptional--ordinary | 0 | 267 | 265 | 532 |
| ordinary--ordinary | 0 | 158 | 171 | 329 |

The local pair shapes are

| pair shape | violations |
|---|---:|
| overlap, same actual root label | 423 |
| disjoint-support block edge | 314 |
| disjoint-support block nonedge | 196 |
| overlap, opposite mate labels | 76 |
| same-fibre side | 14 |
| same-fibre diagonal | 2 |

There are 334 adjacent and 691 nonadjacent endpoint pairs.  The two endpoint
label-pairs share one actual root-neighbour in 437 cases and are disjoint in
588 cases.  Respectively 20, 731, and 274 pairs need one, two, and three
outer common witnesses to give a minimal contradiction.

The most frequent fine class is not universal: it consists of 127
ordinary--ordinary endpoints in a disjoint-support block, adjacent in the
chosen completion, with three outer common neighbours (excess two).  The
JSON retains every labelled pair, its two port types, all common-neighbour
fibres, and all fibrewise collision counts.

## Exact small certificates

For each bad pair the producer enumerates every minimum-cardinality subset of
outer common witnesses.  It includes the distinguished root, every used
root-neighbour label, the marked endpoint pair, and those witnesses, takes
the induced graph, and canonises it while preserving those four roles.

The minimum-order census is

| order | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| violations | 20 | 12 | 366 | 341 | 40 | 213 | 29 | 4 |

There are 80 role-preserving canonical certificate masks.  The two largest
classes have 337 and 274 instances.  The audit independently re-enumerates
4,506 witness subsets and recomputes all 1,025 canonical masks.

Crucially, no certificate has order at most eight.

## Why this is not yet a kernel--port cut

The pointwise defect identity fixes each fibre degree:

```text
8 W[x,F] = 4 d_x(F) - C[G,F]       (x in fibre G).
```

For one endpoint pair and one target fibre `F`, delete the endpoints from the
four possible witnesses and write the remaining degrees as `d'_x(F)` and
`d'_y(F)`.  Marginal degrees alone force only

```text
|N(x) intersect N(y) intersect F|
  >= max(0, d'_x(F)+d'_y(F)-|F\{x,y}|).
```

Summing this lower bound over all 21 fibres would give a genuine universal
one-pair cut if

```text
fixed_A_xy + rho(x,y) + sum_F lower_bound_F > 2.
```

For disjoint endpoint fibres `A_xy` is itself free, so the safe test uses
zero; for same or overlapping fibres its locally fixed value is used.  The
exact audit tests all 3,486 pairs and obtains **zero** forced violations.
For the 1,025 actually bad pairs, the chosen common-neighbour intersections
exceed this marginal lower bound by one through six.

There is a second clean control.  Delete every freely chosen disjoint-support
edge and retain all fixed internal and overlap/port edges on all 84 vertices.
Its residual census is

```text
-2: 2443,  -1: 925,  0: 118,  positive: 0.
```

Every minimum certificate uses at least one freely materialised disjoint-
block proof edge (the census is 1:1, 2:24, 3:61, 4:540, 5:332, 6:67).
Therefore the failures are real failures of this deterministic completion,
but they are not already forced by its fixed port graph or its marginal
kernel degree rows.  A useful next cut would have to synchronize two or more
block maps/pairs, or use a genuinely cross-root condition.

## Whole-macro boundary

The source-724 macro has key `(724,1,0)`, `Q=2`, and labelled coverage
32,768.  Its exact rank-three census has

```text
overlap products                         1024
empty fibre-configuration domain         512
global Gram/graphical UNSAT               384
feasible overlap products                 128
distinct fixed overlap signatures          16
```

The present graph is the first stored feasible rank-three degree witness and
uses the lexicographically first graphical realization of every remaining
disjoint block.  The other feasible products and all alternative block maps
have not been excluded.  Hence no part of the macro's 32,768 coverage is
declared impossible here.

This is the requested boundary: it destroys one explicit witness, not the
source-724 macro.

## Relation to order eight and four-root masks 3/12

There is a useful visual analogy but no valid identification.

* If the two endpoint label-pairs share one label, their incidence pattern is
  a `P3` (437 cases).
* If they share none, it is a `2K2` (588 cases).

Wave152's **four-root** mask 3 means actual induced root edges
`(0,1),(0,2)`; mask 12 means actual induced root edges `(0,3),(1,2)`.
The source-724 description above concerns two incidence-label pairs attached
to two outer vertices.  It does not supply four fixed graph roots, their
induced adjacencies, or a canonical fourth root.  Thus `P3/2K2` is only a
shape analogy, not a map into either covariance block.

The mask number spaces are also different.  The known order-eight E0
adjacent-side-pair class is Wave147 degree-cell mask `127242964` (global
least mask `14333541`), not four-root mask 3 or 12.  The Wave159 result says
that its rational pseudowitness has exact negative full covariance blocks at
four-root masks 3 and 12; those whole-block PSD failures are not entries of
the source-724 pair residual table.

Because the smallest explicit source-724 pair certificate has order nine,
none of the 1,025 failures is itself an induced order-eight marked-pair
class.  This does not rule out a new indirect order-eight or four-root PSD
consequence, but such a lift would need an explicit embedding and coefficient
identity; the present data do not provide one.

## Conclusion

The classification supplies 1,025 exact, independently replayed local
countercertificates and identifies two dominant small shapes.  It also gives
two counter-controls to the hoped-for simple universal cut: no fixed local
pair is bad, and no pair is forced bad by the kernel-determined fibre degree
margins.  The correct conclusion is therefore negative but sharp: this one
completion fails badly, while source 724 remains open to stronger
multi-block or cross-root compatibility.

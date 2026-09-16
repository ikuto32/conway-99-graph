# Triangle-mate cells in the opposite-edge graph

Status: `INDEPENDENT_TRIANGLE_MATE_PARTITION_AUDIT_PASS`.

This note is conditional on a putative `srg(99,14,1,2)`.  It proves a new
quotient/Gram formulation and records its exact numerical boundary.  It does
not construct the graph and it does not exclude the endpoint considered
below.

## 1. The 99 cells

Let `J_E` be the graph on the 693 edges of the putative graph in which two
edges are adjacent when they are opposite edges of an induced four-cycle.
The standard local bijection makes `J_E` 12-regular.  Each graph edge lies in
a unique triangle.  Let `m(e)` denote the third vertex of that triangle and
put

```text
R_r={e:m(e)=r}.
```

The 99 sets `R_r` partition the 693 edges and each has size seven: `R_r` is
exactly the seven matching edges in the graph induced by `N(r)`.  In
particular each `R_r` is independent in `J_E`.  Indeed, different matching
edges in `N(r)` have no cross-edge in `N(r)`, whereas opposite edges of a
four-cycle require two such cross-edges.

Let `R` be the `99 x 693` zero-one incidence matrix of this partition and,
for a vertex `v` of `J_E`, define

```text
k_r(v)=|N_J(v) intersect R_r|=(R J_E)_{r,v}.
```

The augmented-flag calculation identifies its old diagonal count exactly as

```text
D(r)=sum_v binom(k_r(v),2).                         (1)
```

Equivalently, (1) counts, with multiplicity, common `J_E`-neighbours of
unordered pairs in `R_r`.  Since `R_r` is already independent,

```text
D(r)=0  iff  its seven vertices have pairwise J_E-distance at least 3.  (2)
```

Thus `D_*=sum_r D(r)=0` says that all 99 cells are distance-two packings.
It also says every bipartite block `J_E[R_r,R_s]` is a matching.  This is a
consequence, not an assumption: a vertex with two neighbours in the other
cell would be a common neighbour of a pair in that cell.

## 2. Quotient and second-moment Gram matrix

Write

```text
Z=R J_E R^T,
G=R J_E^2 R^T=(R J_E)(R J_E)^T.
```

The partition identities `R R^T=7I` and `R^T 1=1` give

```text
Z=Z^T,       diag Z=0,       Z 1=84 1,
G>=0,                         G 1=1008 1.
```

Moreover, `sum_v k_r(v)=7*12=84`, so (1) gives the pointwise and global
second moments

```text
G_rr=84+2D(r),                  tr G=8316+2D_*.       (3)
```

Normalize the cell incidence by `P=R^T/sqrt(7)`.  Then `P^T P=I`, and the
component of `J_E P` perpendicular to `im P` has Gram matrix

```text
P^T J_E(I-PP^T)J_E P=G/7-Z^2/49>=0.
```

Hence

```text
7G-Z^2>=0,                 tr Z^2<=58212+14D_*.       (4)
```

This is the exact quotient defect; no equitability of the cells is assumed.

## 3. The prism-free endpoint and quotient variance

Let `P_prism` be the number of triangular prisms.  Wave6 gives
`4158=n3+3P_prism`; hence at `n3=4158`, `P_prism=0` and `J_E` is
triangle-free.  If `e,f` are opposite edges and their triangle mates are
`r,s`, then `r~s` would add the missing third matching edge and make a
triangular prism.  Therefore, at this endpoint, `Z` is supported on the
complement adjacency

```text
K=One-I-A.
```

Both `Z` and `K` have row sum 84.  Both have total unordered weight 4158:
for `Z` this is `|E(J_E)|`, while the 84-regular complement has 4158 edges.
Put `W=Z-K`.  It is symmetric and hollow, is supported only on graph
nonedges, and satisfies

```text
W 1=0,   <W,I>=<W,A>=<W,One>=0.
```

Thus it is orthogonal to the full Bose--Mesner algebra.  Since
`tr K^2=99*84=8316`,

```text
tr Z^2=8316+||W||_F^2.                              (5)
```

Equations (3)--(5) first give the exact but weak variance bound

```text
||W||_F^2<=49896+14D_*.                             (6)
```

The special case `W=0` means exactly one `J_E` edge between every
nonadjacent pair of mate cells.

## 4. Refinement using ordinary endpoint incidence

Let `C` be ordinary vertex-edge incidence.  Direct entrywise counting gives

```text
C C^T=14I+A,               C R^T=A,
C J_E=A C-C-2R,
C J_E R^T=R J_E C^T=2K.                           (7)
```

For example, for a graph edge `xy` with triangle mate `z`, the 99 rows of
`C J_E` split into `x,y`, `z`, the 24 vertices adjacent to exactly one of
`x,y`, and the remaining 72.  The four values of `A C-C-2R` are respectively
`0,0,1,0`.  The 24 ones are precisely the endpoints of the twelve opposite
edges.  This proves the nontrivial identity in (7) without a regularity or
transitivity assumption.

Set

```text
S=14I+A,              Y=J_E R^T.
```

Projecting `Y` onto `im C^T` and using (7) yields

```text
G >= 4K S^{-1}K.                                      (8)
```

On the three eigenspaces of `A`, with eigenvalue/multiplicity
`14/1, 3/54, -4/44`, the matrix on the right of (8) has eigenvalues

```text
1008, 64/17, 18/5
```

and trace `116424/85`.

There is a second orthogonal projection.  Residualize the mate incidence:

```text
U=(I-C^T S^{-1}C)R^T,
H=U^T U=7I-A S^{-1}A.
```

The eigenvalues of `H` are

```text
0, 110/17, 27/5,                                      (9)
```

and

```text
U^T(I-C^T S^{-1}C)Y=Z-2A S^{-1}K.                    (10)
```

Projecting the residual of `Y` onto `im U` gives the Schur/Bessel inequality

```text
G-4K S^{-1}K
 >= (Z-2A S^{-1}K)^T H^+ (Z-2A S^{-1}K).             (11)
```

At the prism-free endpoint substitute `Z=K+W`.  The fixed part
`K-2A S^{-1}K` has eigenvalues

```text
0, -44/17, 27/5.
```

Its contribution on the right of (11) has eigenvalues

```text
0, 968/935, 27/5
```

and trace `24948/85`.  The mixed trace with `W` is zero, because the fixed
matrix is in the Bose--Mesner algebra and `W` is orthogonal to that algebra.
Finally, on `1^perp`, the least eigenvalue of `H^+` is `17/110`.  Taking
traces in (11) therefore proves

```text
(17/110)||W||_F^2 <= 33264/5+2D_*,

||W||_F^2 <= 731808/17+(220/17)D_*.                  (12)
```

At `D_*=0`, symmetry and zero diagonal make `||W||_F^2` an even integer, so
(12) sharpens to

```text
||W||_F^2<=43046.                                    (13)
```

This is substantially better than (6), but it is still an upper bound on
quotient variance and gives no positive lower bound on `D_*`.

## 5. Direct packing bounds

At the endpoint `J_E` is triangle-free.  Consequently

```text
L=J_E^2-12I
```

is a nonnegative weighted adjacency matrix: its off-diagonal entries count
common `J_E`-neighbours.  It is 132-regular.  Every eigenvalue is
`theta^2-12>=-12`, where `theta` is an eigenvalue of `J_E`.  The weighted
Hoffman bound therefore gives

```text
alpha(L)<=693*12/(132+12)=231/4=57.75.               (14)
```

A mate cell has size only seven, so (14) does not exclude (2).  Likewise,
the seven disjoint closed radius-one balls around such a cell contain only

```text
7(1+12)=91<=693
```

vertices.  Hoffman gives only `chi(L)>=12`, while the proposed partition
uses 99 colour classes.

## 6. Relation to earlier waves and exact boundary

- Wave6 constructs `J_E`, identifies its triangles with triangular prisms,
  and proves the endpoint is triangle-free.
- Wave20 compresses `J_E` with `C`.  Its Ritz values
  `12,28/17,-21/5` are recovered here, but Wave20 does not use the
  triangle-mate cells.  The present route first compresses with `R` and then
  uses `C` to obtain (11).
- Wave35 uses the same triangle-free endpoint for signed spectral and
  one-triangle local constraints; it does not contain this 99-cell quotient.
- In Wave65 language, row `r` of `R J_E` is the weighted factor `U_r`.
  When `D(r)=0`, it is the simple factor of type `(Q,d)=(0,1)`, distinct from
  the Wave65 transition factor of type `(1,0)`.

All inequalities above accept the formal substitution `D_*=0,W=0`.  The
Hoffman and sphere bounds also accept a seven-point packing.  Therefore the
exact conclusion of this route is

```text
distance-two mate cells excluded:  NO
new rigorous lower bound on D_*:     D_*>=0 only
endpoint excluded:                  NO.
```

This does not show that `W=0`, the 99 simultaneous packings, or the graph are
realizable.  It isolates the missing information: one needs constraints on
the individual `7 x 7` blocks/ports (or higher mixed moments), not just the
quotient, its second moment, ordinary incidence, and universal packing
bounds.

## Reproduction

```text
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_root_opposite_edge_mate_partition.py
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_root_opposite_edge_mate_partition_audit.py
```

The machine-readable outputs are
`scratch_theory_root_opposite_edge_mate_partition.json` and
`scratch_theory_root_opposite_edge_mate_partition_audit.json`.

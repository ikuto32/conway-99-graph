# A PSD Gram-circulation condition for rooted fibre deficits

This note records a necessary condition for every rooted model of an
`srg(99,14,1,2)`.  It is stronger than the trace-only fibre-compression
bound.  As a first application, it excludes the selected-root `E0=75`
branch without a SAT/CP-SAT conclusion.

## 1. The positive-semidefinite matrix

Index the 21 four-vertex fibres by the edges `F` of `K7`.  Let `R` be the
symmetric normalized compression of the outer adjacency matrix, and put

```
D = 4R,                 e_F = number of edges in fibre F,
delta_F = 4-e_F.
```

Thus `D_FF=2e_F`, while for distinct fibres `D_FG` is their number of cross
edges.  Let `L` be the unsigned `21 x 7` edge--vertex incidence matrix of
`K7`.  The all-one direction in `col(L)` has `R`-eigenvalue 12, the other
six directions in `col(L)` have eigenvalue -2, and all Ritz values on
`col(L)^perp` lie in `[-4,3]`.

Write `P_0=J/21`, `P_1` for the projector onto the six centred incidence
directions, and `P_f=I-P_0-P_1`.  On the free space put

```
Z = 4(3P_f - P_f R P_f).
```

The upper Ritz bound gives `Z >= 0`, and `ZL=0`.  To calculate its entries,
note that

```
L^T L = 5I+J,
(L^T L)^(-1) = I/5-J/60.
```

If supports `F,G` have `c=|F intersect G|`, then the projector onto
`col(L)` has entry `c/5-1/15`.  Subtracting `P_0` and simplifying gives

```
(9P_0-5P_1)_FG = 1-c.
```

Since

```
Z/4 = 3I-R+9P_0-5P_1,
```

we obtain the integral entry formula

```
Z_FF = 2 delta_F,
Z_FG = -D_FG       if F,G overlap,
Z_FG = 4-D_FG      if F,G are disjoint.                 (1)
```

In particular, this is a full matrix PSD constraint, not just the earlier
upper bound on `tr(D^2)`.

## 2. Vector circulation on the exceptional-support graph

If `delta_F=0`, then `Z_FF=0`; a zero diagonal entry of a PSD matrix forces
the whole row and column to vanish.  Restrict to the exceptional supports

```
H = {F : delta_F>0}.
```

Factor the surviving principal matrix as `Z_H=(<v_F,v_G>)`.  Equations
`ZL=0` and positive semidefiniteness imply

```
||v_F||^2 = 2 delta_F > 0,
sum_(F incident with g) v_F = 0       for every group g.       (2)
```

Thus the exceptional supports form a simple graph on the seven root groups
carrying nonzero vector values which sum to zero at every vertex.  In
particular it has no vertex of degree one.  More exactly, if `W` is any
rational basis matrix for the scalar kernel of the unsigned incidence
matrix of `H`, every possible Gram matrix has the form

```
Z_H = W K W^T,           K >= 0,                              (3)
```

and its prescribed diagonal is the linear system

```
(W K W^T)_FF = 2 delta_F.                                    (4)
```

Equations (2)--(4) are useful before any fibre orientation or full lift is
chosen.

## 3. Analytic exclusion of the selected-root E0=75 branch

Choose the root supplied by the independently proved side bound `S<=69`.
If `E0=S+Q=75`, then `Q>=6`.  The eight allowed fibre types show that a
deficit-two fibre contributes at most two diagonals, a deficit-three fibre
at most one, and all other deficits contribute none.  Since
`sum delta_F=84-E0=9`, the only deficit multisets with diagonal capacity at
least six are

```
(3,2,2,2),       (2,2,2,2,1),       (2,2,2,1,1,1).           (5)
```

They have respectively four, five, and six exceptional support edges.  We
now use only (2).

### Four edges

No degree one is allowed.  A simple four-edge graph with this property and
with every edge carrying a nonzero vector must be `C4`.  At each degree-two
vertex the two incident vectors are negatives, so all four vectors have the
same norm.  This contradicts the unequal deficits `(3,2,2,2)`.

### Five edges

There are at most five nonisolated vertices.  With five there is a `C5`, on
which alternating the degree-two equations around the odd cycle forces all
vectors to zero.  With four vertices the graph is `K4-e`.  If `a,b` are its
degree-three vertices and `c,d` its degree-two vertices, the equations at
`c,d`, followed by those at `a,b`, force the vector on edge `ab` to be zero.
Both alternatives contradict `||v_F||^2>0`.  Thus the middle pattern in (5)
is impossible regardless of its weights.

### Six edges

There are four, five, or six nonisolated vertices.

* Four vertices give `K4`.  Solving the four vertex equations shows that
  opposite edges carry equal vectors.  Hence each deficit value must occur
  an even number of times, contrary to the three 2s and three 1s.
* On five vertices the degree sequence is either `(4,2,2,2,2)` or
  `(3,3,2,2,2)`.  The first graph is two triangles sharing their degree-four
  vertex; its equations make all six vector norms equal.  In the second
  case, nonadjacent degree-three vertices give `K2,3`, whose three pairs of
  opposite incident edges have equal norms.  Adjacent degree-three vertices
  give a triangle and a four-cycle sharing their high--high edge; the two
  triangle-only edge vectors are forced to zero.  Every case contradicts
  the `2^3,1^3` deficit multiset or nonzeroness.
* Six vertices give a 2-regular graph: either `C6`, where all norms are
  equal, or `C3+C3`, where the odd-cycle equations force zero.

This exhausts (5).  Therefore a putative Conway 99-graph cannot have

```
E0=75
```

at the root selected by `S<=69`.

The standalone audit `scratch_theory_e75_gram_audit.py` independently
enumerates every labelled placement of the three multisets in (5) on the 21
supports.  It constructs the exact rational kernel `W`, solves (4), and
checks that zero placements are PSD-compatible.  It reads no prior SAT or
compression result.

## 4. Computationally useful reductions at E0=72 and E0=73

The same exact support-diagonal test is implemented by
`analyze_support(exceptional)` in
`scratch_theory_unsigned_kernel_filter.py`.  It is a support-level necessary
filter: no fibre state, matching, or SAT variable is needed.

Applied to the existing exhaustive support rows, it conservatively gives

```
E0=73: 295 -> 41 support orbits,
E0=72: 1171 -> 368 support orbits.
```

For a uniquely determined Gram parameter matrix, PSD is decided by exact
principal minors.  A consistent underdetermined system is retained, so these
counts never rely on a numerical SDP rejection.  Intersecting the `E0=72,
Q>=3` port output leaves 162 support rows and 8,354 of its 15,586 feasible
fibre-state assignments.

On the 1,804 already materialized `E0=73,Q>=4` local representatives, adding
their exact overlap-block totals makes (4) inconsistent for all 1,024
representatives in support record 1; 780 representatives remain.  This
local refinement is in `scratch_theory_local_psd_filter.py`.

These reductions are necessary conditions only.  A surviving row or local
representative is not asserted to extend to the full graph.

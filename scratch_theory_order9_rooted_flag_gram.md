# Rooted-flag Gram control on the 19 visible H9 columns

Subsequent structural result: `scratch_theory_triangle_six_flag_affine.md`
proves that **all 99** locally admissible triangle-rooted order-six flag
counts are affine in the root triangle's prism count.  The 74 in this note
are only the subset visible in the 19 H9 masks.  The complete 99-by-99 raw
Gram has rank at most two, and rank one in the prism-free case.  This
compresses the PSD condition but does not rule out an inconsistency among
the corresponding higher-order affine extension equations.  The archived
19-column computation and its certificates below are unchanged.

## Outcome

The Wave163 integral (T=0) extension passes every rooted-flag PSD block of
the natural mate/source family whose union order is at most nine and whose
order-nine support closes on the 19 visible masks.  No negative direction is
obtained.

The useful new result is an exact boundary for this family:

- 74 triangle-rooted order-six flag types occur as induced rooted flags in
  the 19 masks;
- only four of the 74 have a diagonal product supported entirely on the 19;
- those four are (X_0,X_1,X_2,P);
- the maximal closed principal blocks are exactly
  ({X_0,P},{X_1,P},{X_2,P});
- every one of the three blocks evaluates to

  \[
  \begin{pmatrix}199584&0\\0&0\end{pmatrix},
  \]

  hence is PSD of rank one.

Adding the 21 closed marked-pair equations and nonnegativity does not change
this conclusion.  The same nonnegative integral 19-column point remains
feasible.

## Flag family

Fix an ordered target triangle ((c,d,m)).  An order-six flag adds a disjoint
triangle (S).  Pair-upper admissibility makes the cross graph between the
two triangles a matching.  With the three target roots labelled, there are
eight natural types:

| type | cross relation |
|---|---|
| (R_0) | no cross edge |
| (R1_j) | one cross edge incident with target root (j) |
| (X_j) | two-edge matching with target root (j) unmatched |
| (P) | perfect three-edge matching |

The (P) type is an induced triangular-prism flag.  The `X_2` type is the
original good flag when root 2 is the unique mate (m) of the marked target
edge (cd).

There is an exactly equivalent two-root description.  Fix only the ordered
edge ((c,d)), and include its unique mate (m) among the four free vertices
of each order-six flag.  Two such flags can never have disjoint mates because
an edge has exactly one common neighbor.  Thus two nominally four-free flags
always share (m), and their actual union has order at most

\[
2+4+4-1=9.
\]

Direct enumeration verifies equality of the two-root and three-root
coefficient matrices separately for all

\[
62+208+916+19=1205
\]

consumed graph classes.  This equality is a finite check as well as the
obvious unique-mate bijection.

## Exact Gram convention

For each ordered root embedding (	heta), let (z_i(	heta)) be the number
of flags of type (i).  The raw integral moment is

\[
M=\sum_\theta z(\theta)z(\theta)^T\succeq0.
\]

The coefficient of an unmarked graph (H_s), (6\le s\le9), counts ordered
flag pairs whose vertex union is the whole (H_s).  Counts of order seven
and eight come directly from Wave163.  The order-six vector is recovered
without a census from the exact deletion identity

\[
93x_6[K]=\sum_{H_7}d(K,H_7)x_7[H_7].
\]

It has 62 integral nonnegative entries and sum
(inom{99}{6}=1120529256).

For a representative closed block ({X_2,P}), the union-order strata are

| union order | contribution |
|---:|---:|
| 6 | `[[16632,0],[0,0]]` |
| 7 | zero |
| 8 | zero |
| 9 | `[[182952,0],[0,0]]` |

The order-six term is the identical-source diagonal.  Union order seven
would require two distinct graph triangles to share an edge and is zero.
Union order eight is the one-nonmate-overlap stratum; its only relevant
coefficient column has zero Wave163 count.  Union order nine contains the
disjoint nonmate triples and supplies the remaining 182,952.

This rank-one block is the earlier coarse (G/P) status Gram in a raw
ordered-root normalization (twice the earlier `99792` entry).  Thus the PSD
itself is not a new cut.  What is new here is the exhaustive proof that no
larger closed principal block exists inside the full visible-derived
order-six flag family.

## Exhaustive closure graph

For each of the 74 visible-derived flags, the two copies were glued along
the ordered target triangle.  All (2^9) choices of edges between their
free triples were checked against the adjacent/nonadjacent common-neighbor
upper bounds.  Only

\[
X_0, X_1, X_2, P
\]

have closed diagonal support.

All ten unordered products of those four flags were then checked.  The
three (X_jP) products and all four diagonals close.  Each product
(X_jX_k), (j\ne k), has 14 locally admissible canonical H9 extensions:
five visible masks and the same nine masks outside the visible list,

```text
1452696264, 3667223248, 3669518466,
6091774020, 10042630856, 14681708612,
36940436610, 61422027409, 61424673410.
```

Consequently no three-dimensional principal Gram block is licensed by only
the 19 columns.

## Hostile zero-fill control

As a deliberately stronger negative control, all unlisted H9 coefficients
were set to zero even in the three nonclosed (X_jX_k) entries, and the full
eight-type matrix was evaluated:

```text
173448 180048 180048 180048  52372  52372  52372      0
180048 375672 230868 230868 130580 107622 107622      0
180048 230868 375672 230868 107622 130580 107622      0
180048 230868 230868 375672 107622 107622 130580      0
 52372 130580 107622 107622 199584  29352  29352      0
 52372 107622 130580 107622  29352 199584  29352      0
 52372 107622 107622 130580  29352  29352 199584      0
     0      0      0      0      0      0      0      0
```

The first seven coordinates are positive definite.  Under the (S_3)
action on target labels, the trivial congruence block has leading principal
minors

```text
173448,
143984687616,
38953440306215424,
```

and the standard block, occurring twice, has leading principal minors

```text
144804,
24123204764.
```

All are strictly positive.  The full matrix is therefore PSD of rank seven;
the zero (P) row accounts for its kernel.  This zero-fill matrix is not
claimed as a licensed full flag moment—the cross-(X) entries omit nine H9
types—but it is a useful hostile control: even this stronger artificial
test does not separate the endpoint.

## Combination with the targeted deck

The 19-column witness is

```text
all-G counts: (2335,7119,15108,19217,0,0,1197,762,0),
the other ten visible counts: 0.
```

It is nonnegative and integral, satisfies all 21 closed marked-pair rows,
and satisfies all three licensed Gram blocks.  Since the witness itself is
primal feasible, no rational combination of those PSD blocks, the closed
rows, and nonnegativity can give a separating negative direction.

## First missing data and next union order

There are three precise continuation choices:

1. At the same union order nine, add the nine missing H9 masks above.  This
   is the minimum support enlargement needed to license a block containing
   two distinct (X_j) coordinates.
2. If H9 support is held fixed to the 19, a generic two-root order-six flag
   which does not carry the shared unique mate has a disjoint diagonal of
   union order ten.  Thus order ten is the first new generic two-root
   moment layer.
3. A square Gram of triangle-rooted flags with four free vertices has union
   order eleven.  Order eleven is also the first order at which one doubled
   `D` source can be displayed explicitly, agreeing with the earlier
   mate-lift boundary.

Thus increasing union order is not the only option: the immediate missing
information is already present at order nine but lies in nine H9 columns
outside the permitted 19.  Under the fixed-support restriction, the first
new two-root layer is order ten, while the first enlarged triangle-rooted or
explicit-`D` layer is order eleven.

## Artifacts

- `scratch_theory_order9_rooted_flag_gram.py`
- `scratch_theory_order9_rooted_flag_gram.json`
- `scratch_theory_order9_rooted_flag_gram_audit.py`
- `scratch_theory_order9_rooted_flag_gram_audit.json`

The independent audit imports none of the producer code.  It repeats the
74 diagonal scans, ten special pair scans, 1,205 two-root/three-root class
coefficient comparisons, exact (S_3) PSD decomposition, and all 21 closed
linear-row substitutions.  No `submission.txt` was written.

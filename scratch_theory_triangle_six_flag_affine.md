# All 99 triangle-rooted six-vertex flags depend on one local count

For a putative `srg(99,14,1,2)`, fix an ordered triangle `T`.  Let `t(T)`
be the number of triangles disjoint from `T` that form an induced triangular
prism with it.  Every triangle-rooted six-vertex flag count is of the form

```text
z_f(T) = a_f + b_f t(T),       0 <= t(T) <= 12.
```

The exact table in the companion JSON includes all 99 locally admissible
rooted types, not just the 74 extracted from the earlier 19 H9 supports.
Of these 99 counts, 45 are constant and 54 depend on `t`.  At `t=0`, exactly
98 are positive; only the prism flag vanishes.  This gives a structural
compression of the entire order-six triangle-rooted Gram family, not a
positive `E0` lower bound.

## Equitable partition around a triangle

Write the three roots as `r0,r1,r2`.  An outside vertex cannot be adjacent
to two roots, since a root edge already has its unique common neighbour
in the triangle.  Let `Ai` be the outside neighbours of `ri`, and `D` the
vertices adjacent to no root.  Their sizes are `12,12,12,60`.

Each `Ai` induces a perfect matching: an edge from `ri` must have its unique
triangle mate in `Ai`.  For `v in Ai` and `j != i`, the nonedge `v,rj` has
common neighbour `ri` and exactly one additional neighbour in `Aj`.
Thus the three `Ai--Aj` bipartite graphs are perfect matchings.  Each
`v in Ai` has ten neighbours in `D`.  A vertex in `D` has two neighbours
in each `Ai`, by applying `mu=2` to each root, and eight within `D`.

Consequently the outside partition has quotient matrix

```text
       A0 A1 A2  D
A0      1  1  1 10
A1      1  1  1 10
A2      1  1  1 10
D       2  2  2  8.
```

These are pointwise valencies, not merely average edge counts.

## Colored triangles

A triangle cannot contain two vertices of one `Ai`, because their matching
edge already has its root as unique common neighbour.  A triangle meeting
all three `Ai` is exactly a prism mate of `T`; there are `t` of them, at
most 12.  Every edge of an `Ai--Aj` matching has its unique common neighbour
in either the remaining `Ak` or `D`.  Thus there are `12-t` triangles of
color pattern `Ai Aj D`, for each unordered pair `i,j`.

Counting the 120 edges from `Ai` to `D` gives

```text
2 N(Ai D D) + 2(12-t) = 120,
N(Ai D D) = 48+t.
```

Finally the 240 edges inside `D` belong either to one of the `3(48+t)`
triangles with a vertex in an `Ai`, or to a `D D D` triangle.  Hence

```text
N(D D D) = [240-3(48+t)]/3 = 32-t.
```

These are all possible colored triangles.

## Recovering every induced colored triple

A rooted six-vertex flag is exactly a three-vertex induced graph in these
four labeled cells.  There are only eight possible edge subsets on three
ordered free vertices.  For prescribed colors `(c0,c1,c2)`, the number of
injective ordered triples containing an edge subset is determined as follows:

- no edges: the product of falling cell sizes;
- one edge `ij`: `n_ci d_ci,cj (n_ck-[ck=ci]-[ck=cj])`;
- two edges with center `i`: `n_ci d_ci,cj (d_ci,ck-[cj=ck])`;
- three edges: the appropriate colored triangle count above, multiplied
  by the factorials of repeated color multiplicities.

Inclusion-exclusion over the three possible edges gives each exact induced
count.  Division by the color-preserving automorphism group gives the
number of free vertex subsets, the convention used by the archived Gram
coefficients.  Every expression is affine in `t`.  This is also a proof
that there are no extra hidden three-free-vertex statistics in this family.

The tiny `4^3 * 8 = 512` template calculation has 120 rooted isomorphism
types.  Exactly 21 violate a local common-neighbour cap, and their derived
expressions vanish identically.  The remaining 99 have integer affine
coefficients, are nonnegative throughout `0 <= t <= 12`, and sum to
`C(96,3)=142880`.  All earlier 74 types are contained in this list.  The six
flags in `scratch_theory_six_flag_uniformity.md` each give `(a,b)=(12,0)`.

## Gram compression and its precise limitation

Let `a,b` be the 99 coefficient vectors.  Let `P` be the total number of
induced triangular prisms and let

```text
U = 6 sum_(unordered triangles T) t(T)^2.
```

Each prism is incident to two root triangles, and each triangle has six
orderings, so `sum_(ordered T) t(T)=12P`.  There are `99*14=1386` ordered
triangles.  The full raw Gram therefore satisfies the universal equality

```text
G = 1386 aa^T + 12P (ab^T+ba^T) + U bb^T.
```

Its rank is at most two; its centered covariance has rank at most one.
The vectors `a,b` are independent because the prism coordinate is `t` and
there are nonzero constant coordinates.  After these exact relations are
imposed, PSD is equivalent to the ordinary second-moment constraint

```text
1386 U >= (12P)^2.
```

The elementary bound `0<=t<=12` additionally gives `0<=U<=144P`.
At `P=0` the entire matrix is exactly `1386 aa^T`, of rank one.  This
requires only prism-freeness, not the stronger condition `sum E0=0`:
the diagonal contribution `sum D(r)` is not a new variable of this Gram.

The correct use of this result is to replace the large PSD family with
its affine equalities and a single scalar moment inequality.  It does
**not** prove that every prospective higher-order motif assignment can
satisfy those equalities together with its extension rows.  Incompatibility
of a simultaneous H9 completion remains possible and is not ruled out.
The result also says nothing about triangle-rooted flags with four free
vertices, or flags rooted at a different type.

## Validation and retained failures

The producer uses exact rational arithmetic for all 512 templates.  It
checks the old 74-type inclusion, the six constant flags, nonnegativity,
and total counts.  As a separate calibration, the same general-valency
formulas are checked against every one of the 36 ordered root triangles
of the 3-by-3 rook graph, where the local prism count is two.

An independent proof review confirmed the equitable partition and all
colored triangle counts.  Two initial runs stopped on a wrong JSON field
name while loading the previous 74-type list; the correct archived key is
`complete_visible_support_closure_test.diagonal_rows`.  No result was
written by either failed run.  Frozen H8 classes were not regenerated.

The independent checker `scratch_theory_triangle_six_flag_affine_audit.py`
has now passed.  It imports neither the producer nor its encoding helpers:
it solves the eight colored-triangle balance equations by exact Gaussian
elimination, solves each induced-triple system by triangular substitution,
reconstructs all rooted types by six set-graph permutations, checks the
earlier 74 by rooted isomorphism, and independently recounts all 36 rook
root triangles.  Its status is
`INDEPENDENT_TRIANGLE_SIX_FLAG_AFFINE_AUDIT_PASS`.

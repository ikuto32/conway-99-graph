# Candidate: the target induced-rook count cannot be228

This is a new exact exclusion candidate, separate from and preserving both
earlier R228 restriction papers and every other rook artifact. Root suggested
the surviving h4/h5 boundary. Structural derives the point-fan inequality and
the weighted15-point contradiction below. Root separately reconstructed this
outline; agreement is shared derivation context, not different-author
verification. No mathematical program, graph census, import or solver ran.

## Exact statement and explicit prerequisite

For every complete finite simple SRG(99,14,1,2), the number R of actual induced
rook-nine vertex subsets, counted once by their vertex sets, is not228.

The present proof uses the exact population prerequisite

C-UNRESTRICTED-TARGET-ROOK-COUNT228-DEFICIENCY-TWO-POPULATION-FOUR-OR-FIVE r1:

under R228, the positive deficiencies are h4 or5 triangles with d_T=2 and
p10 or8 with d_T=1, respectively; every other triangle has d_T=0.
Here d_T=6-r_T and r_T counts the actual induced rooks containing T.

That prerequisite is the separately frozen paper
docs/CANDIDATE_20261004_TARGET_ROOK_COUNT228_D2_POPULATION_FOUR_OR_FIVE_V1.md,
SHA91ae9decf6e16eca3d6fd306d310031eefab8db6bd467fd1d0ac470b73ca45e1.
Its full defect-cycle, K3,3, seven-row and equality proof must be independently
checked along with this extension. No approval of a weaker h1..5 statement
suffices. A final prerequisite report/binding identity must be genuine;
it is not fabricated from the source or the shared outline.

Only that population theorem is an inherited mathematical premise here.
The local triangle and defect identities are reconstructed. In particular,
the old R!=230, R!=229 and R!=231 results are not this claim's proof gates.
No universal Hamming cover, N3-free assumption, automorphism, equitable
profile, chosen induced support, codeword or code-rank premise is used.

## Actual triangle geometry and local defect degrees

The target neighborhood at a point consists of seven disjoint edges:
lambda1 fixes the partner of each neighbor. Thus each point is on seven
actual triangles. Actual triangles meet in at most one point. Three actual
triangles cannot meet pairwise at three different points; those intersections
would form a triangle and give an original edge a second partner.

For each point v, let D_v be the simple graph on its seven incident actual
triangles, joining a pair when no induced rook contains both. The four cross
pairs' unique second common neighbors show that two triangles through v
belong to at most one rook. Each rook containing T gives one different
nondefective partner at v. Hence degree_Dv(T)=6-r_T=d_T.
Zero-deficiency nodes cannot supply a defect edge.

Let P be the total number of positive-deficiency actual triangles. At a point
v let r1 count d1 triangles through v and r2 count d2 triangles through v.
The sum of local degrees is r1+2r2, so r1 is even by the handshake identity.
By the prerequisite, h4 gives p10/P14, and h5 gives p8/P13.

## General positive-fan inequality, with incidence labels retained

The r=r1+r2 positive triangles through v form a fan. Each has two outer
points, all2r outer points being distinct by triangle linearity. At each
outer point of a d_i triangle, that node has d_i defect partners.
None can be another fan triangle, since those already meet it at v.
Thus there are exactly

    2r1+4r2

outer defect incidences to positive triangles outside the fan.

A positive external triangle can supply at most one such incidence in the
entire fan. It cannot meet two outer points of one fan triangle by linearity.
If it met outer points of two different fan triangles, these three triangles
would meet pairwise at v and those two distinct outer points, which is
forbidden. At the one possible outer point, it can meet only one fan triangle,
because outer fan points are distinct. It supplies at most one defect pair,
irrespective of its own deficiency.

Therefore the P-r external positive triangles must supply all these
incidences, proving

    P-r1-r2 >=2r1+4r2,
    P >=3r1+5r2.                                      (F)

No partner is counted merely by deficiency mass; this counts actual distinct
external triangles. The fan includes every positive triangle through v.

The d1 family has even incidence at every point. Repeat the same fan
argument using just its r1 triangles through v. Each of their2r1 outer
points needs another d1 triangle to make its incidence even, and an
external d1 triangle meets at most one fan outer point. Consequently

    p-r1 >=2r1,  hence p>=3r1.                        (E)

For p10 or8, r1 is even and (E) yields r1<=2.

## A point on d2 has exactly two d1 triangles and no other d2

Since P14 or13, (F) rules out r2>=3. If r2=2, it forces r1=0:
an even r1>=2 would give3r1+5r2>=16>P. But then the only positive
nodes of D_v would be two d2 nodes. Each needs degree two in a simple
graph on those two nodes, impossible. Zero-degree nodes cannot help.

It follows that r2<=1 at every point, so the h d2 triangles are pairwise
disjoint. If r2=1, its degree-two node needs at least two other positive
nodes at that point. Thus r1>=2; (E) already gives r1<=2. Exactly two
d1 triangles occur there. The local graph is the path d1-d2-d1;
the two d1 triangles are not themselves a defect pair.

At every point containing any d1 triangle, its even positive r1 count is
exactly two. This holds whether or not a d2 triangle is present. Accordingly
the p d1 triangles have3p/2 distinct used points.

## The h5 branch fails by distinct point counts

Five pairwise disjoint d2 triangles use15 distinct points. Every one belongs
to two d1 triangles by the preceding local argument. But p8 d1 triangles,
with point multiplicity exactly two, have only12 distinct used points.
They cannot contain those15 points. Thus h5 is impossible.

This is an actual point count, not a rank estimate or a uniform profile.
It does not select a nonconstant kernel or assume one exists.

## The h4 branch fixes the entire15-point support

Now h4 and p10. The ten d1 triangles use exactly15 points; call this set S.
Every point of every d2 triangle lies in S, and the four d2 triangles
are pairwise disjoint.

Choose one d2 triangle T={a,b,c}. At each of its points there are exactly
two d1 triangles. These six triangles form C, with two in each bucket
C_a,C_b,C_c. They are distinct. Their twelve outer points are all distinct:
two in one bucket cannot meet again by linearity; two in different buckets
would meet T and each other at three different points.

Thus T's three points and the twelve C outer points already form15 distinct
points of S, and exhaust S. Each outer point has its one C triangle and
one other d1 triangle. That other triangle cannot be in C, since the
C outer points are distinct. The remaining four d1 triangles V contain
no point of T, whose two d1 triangles are already fixed, and each of
their points is one of the twelve outer points. They partition those
twelve points into four triples.

This is the exact T/six-C/four-V geometry. It is derived from local degrees
and labels, not an assumed induced subgraph or a target symmetry.

## Upper-Gram equality forbids every additional support edge

The exact target equation is A^2=12I-A+2J. Its real symmetric spectrum is
14 on the all-ones vector and3,-4 on its orthogonal complement. Therefore

    Q=3I-A+J/9

is positive semidefinite, with eigenvalues0,0,7. No floating eigenvalue or
matrix program is used.

Give each point of T weight two, every other point of S weight one, and
all other target points weight zero. Then sum w=18 and ||w||^2=24.
Consider only the already known edges in T, the six C triangles and
the four V triangles. Their edge sets are disjoint because lambda1 gives
each edge its unique actual triangle.

The known edge-weight products sum exactly:

| Known triangles | Weights on each triangle | Edge-product sum |
|---|---|---:|
|T|2,2,2|12|
|Six C triangles|2,1,1|6*(2+2+1)=30|
|Four V triangles|1,1,1|4*3=12|
|Total||54|

Their contribution to w^t Q w is

    3*24 -2*54 +18^2/9 =72-108+36=0.

Any extra actual edge within S decreases this quadratic value by twice
the strictly positive product of its endpoint weights. Edges leaving S
do not affect the value because the outside weights are zero. Since the
actual Q is positive semidefinite, there can be no extra edge within S.
The known T/C/V edge union is the entire induced graph on S.

The other three d2 triangles are wholly inside S and distinct from T and
all ten d1 triangles. But every edge of the induced graph on S already
belongs to one of those eleven known actual triangles. An additional
actual triangle on S would contain such an edge; lambda1 fixes its third
point to the known triangle's partner. It would therefore be the same
known triangle, not an additional d2 triangle. Equivalently it would
need an extra support edge, which the Gram equality prohibits.

This contradiction excludes h4. Both population branches fail, so the
exact R228 supposition is discharged.

## Hand boundaries, failed shortcuts and review limits

The fan inequality counts distinct external partners, not their deficiency
sum. An external d2 triangle cannot supply two fan incidences at the same
outer point: that point belongs to one fan triangle and their pair
determines one edge in D_v. It cannot meet two fan outer points either.
This is the main boundary that must be challenged independently.

A point supporting three d2 nodes with local D_v a triangle is allowed
by local degree counting. The global positive-fan inequality needs P>=15.
At h3, P15 reaches that boundary; at h4/h5, P14/13 fails. Thus the
previous local triangle/collapsed-cycle controls remain valid as local
controls but are not global R228 realizations.

A local four-cycle on four d2 nodes likewise requires P>=20 from (F).
The earlier fourfold-point label example was explicitly only a local
boundary and is preserved; it does not invalidate this new global fan bound.

The known deficiency-two equality edge union on15 points has exactly the
displayed weighted value zero for any of its actual matching arrangements.
This does not supply a target. Adding an outer-outer, center-outer or
center-center edge reduces the value by2,4 or8 respectively; all are
forbidden when both endpoint weights are positive. No extra edge is
silently omitted.

The contradiction needs h4's extra three d2 triangles wholly on S.
The known eleven-triangle support itself is not outlawed by this argument;
its upper-Gram equality is compatible. Only the demanded additional
actual triangles, with fixed edge partners, fail.

The separately frozen h4/h5 prerequisite is essential to this proof route.
A weaker maximum-two or h1..5 result alone would leave cases untreated.
Root's shared reconstruction is not independent verification. A
different author must audit both full prerequisite and this extension,
including (F), (E), distinct D2 points,15-point exhaustion, exact weighted
products and uniqueness of the known eleven triangles before promotion.

No other rook count, target construction, code-rank conclusion or general
Conway99 resolution is asserted. This candidate has no mathematical
execution, scientific coverage census, live ledger write or Git mutation.


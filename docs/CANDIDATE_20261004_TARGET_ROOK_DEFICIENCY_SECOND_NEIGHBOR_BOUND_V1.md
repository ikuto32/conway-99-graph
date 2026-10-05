# Candidate: second-neighbor mass in the rook-defect incidence

Written only, with no mathematical program or enumeration. This is a new
conditional necessary screen on a complete simple SRG(99,14,1,2). It does not
exclude R=229, R=231, or a target graph. The earlier independently reviewed
R!=230 paper and all its evidence remain unchanged.

## Exact statement

Let R count actual induced rook-nine vertex subsets once. For each of the
231 actual triangles T, let r_T be the number of those subsets containing T,
and put d_T=6-r_T. Let D=sum_T d_T=6(231-R). Then for every actual triangle T,

    D >= 6 d_T,             d_T <= 231-R.

More precisely, if d_T=m>0, let C be the union of the three lists of its
defect-neighbor triangles, one list at each point of T, and put
K=sum_(U in C) d_U. Then

    |C|=3m,  K>=3m,  D>=m+K+ceil(2K/3).

If D=6m, the entire positive-deficiency support consists of T with deficiency
m, its 3m defect neighbors with deficiency one, and exactly 2m further
triangles with deficiency one. Their used points form a forced induced
(3+6m)-vertex edge union of 1+5m actual triangles. Each further triangle
contains one outer point from each of the three T-point buckets; each
defect neighbor contains its T point and two distinct further-triangle points.

On this induced set S, put w=m at the three points of T, w=1 at the other
6m points, and w=0 elsewhere. The exact full-target identity is

    A w = 3w + m j.

Consequently among vertices outside S, exactly 36-6m have one neighbor in T
and no neighbor in S\T, and exactly 60 have no neighbor in T and exactly m
neighbors in S\T. These are individual necessary incidences, not an equitable
partition assumed before proof. No assertion is made that the prescribed
edge union has a completion, or that every choice of three matchings is valid.

In particular, at R=229 either all twelve positive deficiencies are one, or
there is exactly one deficiency-two triangle and ten deficiency-one triangles.
The latter case has the forced induced fifteen-point, eleven-triangle set
above, with weights 2 on T and 1 on its twelve outer points. Neither branch
has been excluded by this paper.

## Exact defect convention and prerequisites

Every edge belongs to its unique triangle by lambda=1. At a vertex, its
fourteen neighbors are paired by those triangles, so it lies in seven actual
triangles, and there are 99*7/3=231. Distinct actual triangles meet at most
once. Three actual triangles cannot meet pairwise at three different points:
those points would form a triangle, giving an existing edge a second common
neighbor and contradicting lambda=1.

For two different triangles through a point v, an induced rook containing
both is unique if it exists. Its four opposite grid points are the uniquely
specified second common neighbors of their four nonadjacent cross pairs,
using mu=2. Existence is not inferred from this reconstruction.

Let D_v be the simple graph on the seven triangles through v, with an edge
precisely for a pair not contained together in an induced rook. A rook
containing T gives exactly one other triangle through each v in T; pair
uniqueness therefore yields deg_(D_v)(T)=6-r_T=d_T at every such v.
In particular 0<=d_T<=6. Each rook contains six actual triangles, so
sum r_T=6R and D=6(231-R). These are actual-subset counts, not embedding or
disjoint-packing counts. The same d_T at its three points is a consequence,
not a uniform-profile assumption.

## The second-neighbor estimate

Fix T={a,b,c} with d_T=m>0. At each of a,b,c it has m neighbors in D_v.
The three lists are disjoint by linearity, giving 3m triangles C. All have
positive deficiency, hence K>=3m.

For U in the a bucket, its other two points are outside T. At each of these
two points it has d_U defect partners. These two lists are disjoint, since
a different triangle cannot meet U twice. Each partner has positive
deficiency. Count these as 2d_U distinct incidences U--V. Do this for every
U in all three buckets, giving exactly 2K incidences.

Every such partner V avoids every point of T. If it contained a, it would
meet U at both a and the outer point, violating linearity. If it contained
b or c, then T,U,V would meet pairwise at three distinct points, violating
the lambda=1 prohibition. Thus all partners are disjoint from T and outside C.

Such a V meets at most one member of each bucket. Otherwise two bucket
members U1,U2 meet at a, while V meets them at their two different outer
points. This is the same forbidden three-triangle configuration. Hence one
outside partner can account for at most three of the 2K incidences. At least
ceil(2K/3) distinct outside triangles are required. Each has d>=1, so their
total deficiency is at least that number. The three disjoint groups T,C,
outside partners give

    D >= m+K+ceil(2K/3) >= m+3m+2m = 6m.

No weighted edge flow or equitable partition was substituted for actual
triangle incidences. The capacities are counts of distinct triangle nodes.

## Equality is rigid but is not a contradiction

If D=6m, every inequality above is an equality. All 3m bucket triangles
have deficiency one, and precisely 2m partner triangles each have deficiency
one. There are no other positive deficiencies. Each partner meets exactly
one bucket member in each of the three buckets, and every bucket member's
two outer points have distinct partner triangles.

Outer points from different bucket triangles are distinct. In one bucket,
this follows from linearity, since they already share their T point. Across
two buckets, a shared outer point would form the prohibited three-triangle
configuration with T. Thus there are exactly 6m outer points; the 2m
partner triangles partition them into triples, one point per bucket.

If the 2m partner triangles are used as labels, each bucket's m two-point
rows define a perfect matching on those labels. This is only a way to
describe the forced finite geometry. It makes no target automorphism claim
and does not identify arbitrary target vertices.

Start with the union H0 of the central triangle, all 3m bucket triangles,
and the 2m partner triangles. All 1+5m triples are distinct actual triangles;
their edges are distinct. Central points have H0 degree 2+2m, and outer
points have degree four. For the positive vector w_S described above,
sum w_S=9m. Directly at a central point,

    (H0 w_S)_a = 2m+2m=4m;

at an outer point,

    (H0 w_S)_p = m+1+2=m+3.

It follows that (3I-H0+J/9)w_S=0, so its quadratic value is zero.

For the full target, A^2=12I-A+2J. On j-perp the two possible adjacency
eigenvalues are 3 and -4; on j the eigenvalue is 14. Hence
U=3I-A+J/9 is positive semidefinite: its eigenvalues are 0,0,7.
Any additional edge inside S would decrease the displayed quadratic value
by 2w_p w_q>0, because every coordinate in S is positive. Positive
semidefiniteness forbids this. Therefore the forced edge union is induced.

Extend w_S by zero outside S. Its full quadratic value is zero; a real
symmetric positive-semidefinite matrix has U w=0 in that case. Thus
A w=3w+m j on every target vertex, including those outside S. For such a
vertex let a_v count its T neighbors and b_v count its S\T neighbors.
It satisfies m a_v+b_v=m. It can meet at most one point of T: meeting two
would give their existing triangle edge a second common neighbor. Therefore
(a_v,b_v) is (1,0) or (0,m).

The central points have degree 2+2m inside S and degree fourteen in the
target. Their outside boundary has 3(12-2m)=36-6m edges, and each vertex
receiving one is distinct. There are 99-(3+6m)=96-6m outside vertices;
the remaining number is sixty. This establishes the stated counts without
assuming a uniform incidence vector within either group.

## Hand challenges and the R=229 branches

At R=231 all d_T=0; the m>0 equality statement is inapplicable and no
nonzero w is forced. At R=230 the estimate gives d_T<=1, consistent with
the earlier deficiency-six argument; that earlier argument separately
rules the case out. No approval transfer from it is needed for this estimate.

At R=229, D=12 and max d<=2. If a d=2 occurs, its bound is tight and
the equality argument gives one d2 and ten d1. If none occurs, twelve d1
are possible under this screen. Parity alone does not forbid the latter:
the odd-deficiency triangles have even incidence, but an even twelve-triangle
selection was not classified here.

For m=1, the forced edge union is the usual rook nine, and w is its
indicator. Its known regular-set identity A w=3w+j is recovered. Its six
triangles are then contained together in that rook, inconsistent with all
six being actual positive-deficiency nodes. This familiar boundary is not
a new rook exclusion or a claim that any even-six dependency is impossible.

An inserted edge in any equality edge union is a useful hand negative:
its two positive endpoint weights change the U quadratic value from zero
to a strictly negative number. Merely counting points without the exact
triangles would not justify that test. Conversely, the zero quadratic
value of the unmodified union is not evidence of a target completion.

The usual claim that one outside partner can serve arbitrarily many leaves
would break the bound: the three-triangle lambda=1 prohibition is essential.
A linear triple family alone permits such cycles and is outside this theorem.
Replacing deficiency mass by an unweighted number of nodes before proving
d_U>=1 would also invalidate the equality reasoning.

## Overlap and verification scope

This strengthens the first-neighbor estimate D>=4d_T used in the earlier
R!=230 proof. The case m=1 regular-set identity overlaps the September17
rook regular-set audit. The new ingredients are the second-neighbor capacity,
its equality configuration and its positive weighted regular-set consequence.
A bounded Markdown search and those two complete named papers did not reveal
this precise package; this is not a worldwide or whole-archive novelty claim.

Root was sent the preliminary 6d_T argument and the m=2 geometry before this
freeze. That shared discussion is not independent verification. A different
author must challenge the incidence capacities, equality, inducedness and
all outside counts before promotion. No graph, matrix or matching program
was run. No ledger, fixed publication roster or historical artifact changed.

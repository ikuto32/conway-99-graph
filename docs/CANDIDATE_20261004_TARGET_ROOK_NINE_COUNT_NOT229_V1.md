# Candidate: the induced-rook count cannot be 229

This is a source-only written candidate for a new exact statement. All earlier
rook papers, raw packets and their open-case wording remain unchanged. Root
requested that multiplicity-four/six points be challenged without assuming a
cubic dual. Structural derives their exclusion before using that dual. No
graph census, mathematical script, matrix program, import or solver ran.
Different-author written approval remains pending.

## Exact statement and the remaining boundary

For every complete finite simple SRG(99,14,1,2), let R count actual nine-point
subsets inducing the3-by-3 rook graph, each subset once. Then R!=229.

Together with the separately established counting bound0<=R<=231 and the
R!=230 argument, this leaves R in {0,...,228,231}. No R231 exclusion or target
nonexistence follows. No Makhnev or Hamming-cover premise is used.

The proof bundle reconstructs the needed D12 reduction below; the earlier
strict second-neighbor paper supplies a longer general version. Neither
agreement with that paper nor an old execution gate is a new verification.

## Defects, uncovered squares and the D12 reduction

Every point is in seven actual triangles; every edge has its unique triangle
partner. Distinct actual triangles meet at most once. Three actual triangles
cannot meet pairwise at three distinct points, since their shared points
would form a triangle and give an original edge a second triangle partner.

For an actual triangle T, let r_T count induced rooks containing T and set
d_T=6-r_T. At each point v form D_v on its seven incident triangles, joining
a pair exactly when no induced rook contains both. Two triangles through v
determine at most one rook by the four cross pairs' unique second common
neighbors. Each rook containing T supplies one different partner at v.
Thus the degree of T in D_v is d_T at every v in T, and

    D=sum_T d_T=6(231-R).

A square is rook-covered if and only if its two actual edge triangles at
any specified corner are together contained in a rook. Their fixed second
common neighbor fixes the square in every proposed rook. Every uncovered
square has four defect corner pairs. There are2079 squares in the target,
and square uniqueness makes the nine square sets per rook disjoint, so

    U=2079-9R=3D/2.

Assume R229, hence D12. The second-neighbor mass calculation is short: if
d_T=m, its three points have3m distinct defect-neighbor triangles, of total
deficiency K>=3m. Their two outer points supply2K defect incidences with
triangles outside that collection. An outside triangle can meet at most
one of the neighbors in each bucket, by the three-triangle prohibition.
Their total positive deficiency is at least ceil(2K/3). Therefore

    D>=m+K+ceil(2K/3)>=6m.

If m2 occurs, equality holds throughout. The positive triangles are T(d2),
six bucket leaves(d1) and four further triangles(d1). On their15 points the
four further triangles supply four nodes; each bucket's two leaves pair
these nodes by a perfect matching. Give T's points weight2 and the twelve
outer points weight1. The exact target upper Gram3I-A+J/9 is positive
semidefinite: A^2=12I-A+2J gives eigenvalues14 on the all-one vector and
3,-4 on its orthogonal complement; the upper Gram eigenvalues are0,0,7.
Here the weight sum is18, squared norm24 and sum of edge weight products54,
so its quadratic value is72-108+36=0 for the
specified triangle edge union; any extra edge decreases it strictly. Hence
this15-point edge union is induced.

Every uncovered square has all corners on positive triangles and thus in
that15-point set. It needs U18 squares. A center and an outer point in either
other bucket give24 nonadjacent pairs with two common neighbors. Outer points
of different buckets and different further-triangle nodes have two common
neighbors exactly when their nodes are matched in both buckets; each shared
matching edge contributes two such pairs. Same-bucket unmatched pairs have
only their center, and same further-triangle nodes are adjacent. These are
all pair categories, giving12 squares plus the sum of the three pairwise
matching-intersection counts. Three perfect matchings on four nodes have
those sums6,2,0 according
as all coincide, exactly two coincide, or all differ. Thus the square counts
are18,14,12. The last two cannot supply18. If all coincide, the central
triangle and either matched pair of outer triangles make an actual induced
rook containing a designated central/leaf defect pair. That also fails.
This excludes m2; m>=3 was already excluded by D>=6m.

Consequently precisely twelve actual triangles have d_T=1, all others d_T=0.
Call these twelve the positive triangles. At every point their nodes in
D_v form a matching, since each has degree one and every other node has
degree zero. Their point multiplicity is therefore even:0,2,4 or6.
Only now do we analyze these multiplicities.

## Six is impossible by a fan-incidence bound

Suppose a point v is in r positive triangles. Their2r other points are all
distinct by linearity. A positive triangle not through v can meet at most
one of these fan points. Two from the same fan triangle violate linearity;
two from different fan triangles give three triangles meeting at different
points. Each fan point needs at least one of the remaining triangles for
its positive incidence to be even. Hence

    12-r >=2r,  so r<=4.

This rules out r6. It does not justify discarding r4 by itself.

## Four forces a rook across its required defect pair

Suppose r4 at v, with positive triangles T1,...,T4 and their eight fan points.
There are eight remaining positive triangles, each using at most one fan
point, and all eight fan points must be covered. Thus every remaining triangle
uses exactly one fan point, and each fan point is in exactly two positive
triangles. The remaining two points of each remaining triangle are new.

If a new point w lies in q positive triangles, each such triangle has a
different fan point. All q points are common neighbors of w and v. The target
common-neighbor count is at most two, whereas q is positive and even. Thus
q2, and w is nonadjacent to v. There are16 new-point incidences, giving eight
distinct new points.

Make a graph on these eight new points: each remaining triangle gives its
edge between its two new points, labeled by its unique fan point. The graph
is simple by triangle linearity and2-regular because every new point lies
in two remaining triangles. A3-cycle would add a second triangle partner
to a selected edge, so its cycles have length at least four. Each of the
four fan colors Ti labels exactly two edges. At any new point, its two edge
colors are different: two triangles using the two points of one Ti would
meet Ti and each other at three different points.

Those two different colors must be a defect pair in D_v. Otherwise a rook
containing Ti,Tj would contain their two incident fan points and their uniquely
fixed second common neighbor w. Its edge from a fan point to w lies in that
fan point's remaining selected triangle, so the rook would also contain that
triangle and Ti. But they are the only two positive triangles through the
fan point and must be a defect pair there. This contradiction proves the
color restriction.

D_v on four positive colors is a matching of two pairs. The new graph's
cycles therefore alternate between the colors of one matched pair. Each
color has exactly two edges, so each pair uses four edges and forms a4-cycle;
the graph is two disjoint4-cycles.

Take one such cycle w1-w2-w3-w4-w1. Let its alternating fan labels be
p_i,q_j,q_i,p_j, with Ti={v,p_i,q_i}, Tj={v,p_j,q_j}. The six actual triangles
are the rows and columns of the array

    v    p_i  q_i
    p_j  w1   w4
    q_j  w2   w3.

They form a rook-nine; any extra edge has the two other grid corners as
common neighbors and is forbidden by lambda1. This induced rook contains
Ti,Tj, although those colors were their required defect pair. Contradiction.
Therefore r4 is impossible too. Every point on the twelve positive triangles
has multiplicity exactly two. This conclusion is derived, not assumed.

## The cubic dual and its exact square equality

The positive support has18 points. Form F whose twelve nodes are the positive
triangles and whose eighteen edges are their shared points. It is simple by
linearity, cubic because each triangle has three points, and triangle-free
by the three-triangle prohibition. Let H be their edge union on the eighteen
points. H is precisely the line graph L(F). Additional actual graph edges
are not assumed absent from that eighteen-point support.

Nevertheless uncovered squares use only edges of H. At every corner their
two edge triangles must be its defect pair. There are exactly two positive
triangles at that point, and all other incident triangles have defect degree
zero. Thus both incident square edges belong to the selected triangle union.
Conversely every induced square of H is an induced target square: either
diagonal would have two existing common neighbors and cannot be an edge by
lambda1. At every corner it uses the two distinct positive triangles, which
are the defect pair there. So this square is uncovered.

There is a bijection between induced4-cycles of L(F) and ordinary4-cycles
of F. Four successive line-graph vertices are four F edges whose successive
intersections give four distinct F vertices; opposite line-graph vertices
are disjoint F edges. Conversely the four edges of any F4-cycle give that
induced line-graph square. It follows that

    C4(F)=C4(H)=U=18.

No extra-edge assumption or hypothetical automorphism is hidden in this step.

## Eighteen saturates the cubic bound and creates a forbidden rook

In a cubic graph, a vertex has three neighbor pairs. Each pair has that
vertex and at most two further common neighbors. Therefore it is in at most
six4-cycles. On twelve nodes this gives C4(F)<=12*6/4=18.

Equality at18 forces equality at every vertex. For any v, each pair among
its neighbors x,y,z has three common neighbors. Since x,y,z each have degree
three, their full neighbor sets coincide. Write the shared set {v,p,q}.
It is disjoint from {x,y,z}, and every one of these six points has its full
degree within their K3,3. Thus every component of F is K3,3; with twelve
nodes there are two such components.

For a K3,3 component, its six positive triangle nodes and nine shared-point
edges are exactly the rows and columns of a rook-nine. Any extra graph edge
on those nine points violates lambda1 as above, so it is an actual induced
rook. At any shared point its two positive triangles are therefore together
in that rook. They cannot be the required defect edge. This is the final
contradiction, excluding R229.

## Hand falsifications, overlap and limitations

An arbitrary even twelve-triangle selection need not avoid multiplicity four.
Two rook-nine graphs joined at one point give twelve distinct row/column
triangles: the shared point has incidence four and the other sixteen points
incidence two. This is a hand local edge-union boundary, not a target completion.
The rook cover prevents its triangles from all having target deficiency one.
Our proof uses that extra condition; it does not outlaw every binary right
relation of weight twelve.

Two abstract K3,3 components have twelve cubic nodes and eighteen4-cycles,
showing the cubic upper bound is sharp. Their line graphs are two rooks, so
the required defect rule fails. The hexagonal prism is a connected cubic
triangle-free graph on twelve nodes with six4-cycles (one rectangle per
hexagon edge), illustrating why merely producing a locally admissible cubic
dual does not meet the required eighteen. Neither example is reported as an
SRG99 or a globally admissible defect configuration.

The general strict mass lemma, even-six rook reconstruction and square count
overlap the pinned earlier papers. A bounded comparison also read Wave17's
different n3=54,27-point line-graph reduction and Wave102/Wave112 coding notes.
Their cubic line-graph terminology is shared; no archived census or gate is
imported. This new argument is the deficiency-one color/fan restriction and
the exact eighteen-square saturation, with no catalog enumeration.

Root received the outline before freeze. A different reviewer must challenge
the D12 reduction, fan-incidence cover, four-color square transport, distinction
between selected and extra edges, and sharp cubic equality classification.
R231 remains possible on this proof and on the preceding defect argument.
No mathematical execution, ledger/index/Git mutation, or new proof gate exists.

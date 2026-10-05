# Candidate: R227 with maximum deficiency two cannot have seven d2 triangles

This is a separate written candidate. Root proposed extending the faithful
defect-cycle map to b5..7; Structural instead derived the following fifteen-
point support obstruction for b7. Root challenged the selected-fan bound,
triple-concurrence lemma and integer equality before this freeze. No
mathematical program, enumeration, import, backend or worker ran. The earlier
R227 candidates remain unchanged; different-author verification is required.

## Exact statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
nine-vertex rook subsets once by their vertex sets and put d_T=6-r_T for
each actual triangle, where r_T counts the rooks containing T. If R=227
and every d_T belongs to {0,1,2}, then it is impossible that exactly seven
actual triangles have deficiency two. Equivalently, the positive family
cannot consist of ten d1 and seven d2 triangles with every other d_T zero.

The maximum-deficiency-two condition is explicit, not inherited from a
different R227 candidate. This does not exclude R227, other populations,
or an arbitrary even ten-triangle selection. No uniform profiles, graph
automorphism, induced selected-support premise or additional left-code
existence is assumed.

## Local degrees, parity and fan capacities

Each vertex belongs to seven actual triangles. Distinct triangles meet at
most once. Three cannot meet pairwise at three distinct points: the three
intersection points would give an edge a second triangle partner, violating
lambda1. Two intersecting triangles determine at most one induced rook by
their four cross pairs' uniquely fixed second common neighbors.

At a point v define the local defect graph on its seven incident triangles,
joining a pair if no rook contains both. Its degree at T is d_T: every rook
containing T supplies one covered partner through v and pair uniqueness
makes those partners distinct. Thus the sum of the d_T through every point
is even. Under maxd2, the d1 triangles form an even point-incidence selection.

There are231 actual triangles, and each rook has six, so D=sum d_T=24.
The hypothesized b7 boundary has a10 d1 and P17 positive triangles. The
general positive-fan bound at each point is

    P>=3r_1+5r_2.                              (1)

For each positive triangle through v, each of its two outer points needs
d_T external defect partners. Any external triangle meets at most one outer
point of this entire fan, by linearity and the forbidden distinct-intersection
triple. Zero-deficiency triangles cannot supply defect edges. This proves (1)
without identifying vertices of the same type or dropping actual extra edges.

## The ten odd triangles use exactly fifteen points

If r selected d1 triangles contain a point p, their2r outer points are
distinct. At each of those points the selected parity is odd, so another
selected triangle must meet it. Such an external selected triangle can meet
at most one of those outer points. Hence the ten selected triangles obey

    10-r>=2r,  or 10>=3r.

Every used point has positive even selected multiplicity, so it is exactly
two. This uses the selected ten-triangle fan, not the weaker P17 bound,
which alone would allow four d1 triangles at a point. The selected support
S has15 distinct actual vertices. Its ten actual triangles supply30 distinct
edges in S; distinct actual triangles cannot share an edge. No inducedness
of S is asserted.

## Every d2 point outside S is a triple concurrence

At a point outside S there is no d1 triangle. A d2 triangle needs two
different local defect partners, so at least three d2 triangles occur there.
By (1), P17 permits at most three. Thus every point of a d2 triangle outside
S belongs to exactly three of the seven d2 triangles. Let h count these
distinct points, and let t_i in {0,1,2,3} count the outside-S points of the
i-th d2 triangle. Then

    sum_i t_i=3h.                              (2)

The next lemma bounds h using actual point labels, not an abstract graph
whose triangle edges are allowed to have different labels.

## Seven actual triangles have at most three such triple points

If h is nonzero, fix a triple point p. Its three selected d2 triangles
form a base fan. Call the other four triangles external. Any other triple
point q belongs to at most one base triangle, since two base triangles
already meet at p. If q is attached to a base triangle, it belongs to exactly
two external triangles. If it is detached from the base fan, it belongs to
three external triangles.

The external pairs used by distinct attached points are disjoint. Suppose
an external triangle U were used at attached points q and q'. If their
base root is the same, that root and U share two points, contradicting
linearity. If their base roots are different, those roots meet at p and
meet U at q and q', making the forbidden three distinct intersections.
Only four external triangles exist, so at most two attached points occur.

At most one detached point occurs: two three-subsets of four external
triangles have at least two triangles in common, and those two triangles
would then share two points. If there were two attached points and one
detached point, the two disjoint external pairs would partition the four
external triangles. The detached three-subset contains both triangles of
one pair. They already meet at that attached point and would meet again at
the detached point, also contradicting linearity. Therefore there are at
most two other triple points besides p, or

    h<=3.                                     (3)

Additional intersections of the external triangles cannot evade this
argument; they can only create further forbidden intersections. No
concurrency or nonconcurrency of the uncounted target triangles is imposed.

## Five more edges are unavoidable

The i-th d2 triangle has3-t_i points in S and consequently contributes
binom(3-t_i,2) edges inside S. All these edges are distinct from one another
and from the30 d1 edges, by unique actual triangle partners.

For integer t in {0,1,2,3}, direct inspection gives

    binom(3-t,2)>=2-t,

with equality precisely at t1 or2. From (2) and (3),

    sum_i binom(3-t_i,2)>=14-sum_i t_i>=5.

The exact integer boundary for equality is h3, five t_i equal to1 and two
equal to2. This distribution is not asserted to extend to a target.
It cannot be excluded just by the abstract triple-point lemma. For h<=2
the stronger direct identity gives at least21-6h>=9 edges, also enough.
Thus the actual induced edge count of S, including all arbitrary additional
edges, satisfies

    e(S)>=30+5=35.                             (4)

## The target upper Gram makes that edge count impossible

The target adjacency identity is A^2+A=12I+2J, with row sum14. On the
orthogonal complement of j its eigenvalues belong to {3,-4}. Therefore

    Q=3I-A+J/9

is positive semidefinite: its eigenvalue on j is0 and its other eigenvalues
are0 or7. For the fifteen-point indicator chi of S,

    chi^T Q chi=45-2e(S)+225/9=70-2e(S).

Positivity gives e(S)<=35. If e(S)=35, positivity also gives Q chi=0.
At any vertex outside S that equation would say

    number of its S neighbors=15/9=5/3,

which is impossible for an ordinary integer neighbor count. There are84
outside vertices. Hence e(S)<=34, contradicting (4). This proves the exact
conditional boundary exclusion.

## Hand counter-controls, overlap and limits

Three triple points are compatible with the selected triangle geometry:
one triangle can pass through three such points, each with two private
triangle leaves. Another incidence pattern puts p on T1,T2,T3; q on
T1,T4,T5; and r on T2,T6,T7, with other points private. Its outside-point
counts are two t2 and five t1 and it attains the edge lower bound5.
These are hypergraph/local geometry controls, not complete SRG constructions.
The target Gram equality is essential to reject the boundary distribution.

If the forbidden distinct-intersection triple premise is removed, take four
points and six triangles whose two distinguished points are the six pairs
of those four points, with a private third point for each. Add a seventh
private triangle. All four distinguished points then have multiplicity
three, but the triangles on pairs12,13,23 meet at three distinct points.
This linear hypergraph is an explicit counter-control to a stronger lemma
using linearity alone. It cannot be the actual target triangle geometry.

Positive semidefiniteness alone gives the non-strict edge bound35. The
integer full99 equality equation improves it to34; it is not valid to
discard this equality step. Nor can a fractional formal Gram realization
be substituted for ordinary target neighbor counts.

The parity, fan and upper-Gram ingredients overlap earlier incidence and
rook-deficiency arguments. The new scoped boundary uses the ten-selection
support, the seven-triangle triple-concurrence lemma and the strict
fifteen-point edge bound together. No general novelty or target resolution
is claimed. Earlier maxd2/minimum-b/no-eight/common-point candidates are
comparison evidence only; no verification gate or logical premise is
transferred. Other R227 populations remain unresolved and this written
candidate is outside the frozen publication cutoff.

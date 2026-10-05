# Candidate: the R226 one-d3 lane cannot have eight d2 roots

Structural derived the attached-root capacity and zero-Gram-coordinate
argument; Root separately challenged its exact pair injection, actual labels,
thresholds and equality case. This is a new written CANDIDATE requiring a
different full audit. No earlier one-d3 range gate is assumed. No mathematical
program, import, census, solver or worker ran; historical bytes are unchanged.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle T.
Suppose R=226, every d_T belongs to {0,1,2,3}, and exactly one actual
triangle has deficiency three. The number b of actual deficiency-two
triangles is not eight.

Maximum deficiency three and the one-d3 population are literal hypotheses.
No pending R226 statement is used as a premise. This does not exclude the
whole one-d3 lane, R226 or the target. The logical dependency list is empty;
the required fan, selected-family and equality facts are derived below.

Assume b8 for contradiction. Let T be the sole d3 root. Summing deficiency
over actual triangles gives D=1386-6R=30, hence a=11 d1 roots and P=20
positive roots. At an actual point the local simple defect graph joins
uncovered rook pairs of incident triangles and has node degrees d_T.
Each containing rook supplies one covered partner at that point, and
lambda1/mu2 make the containing rook unique for a fixed row/column pair.
Thus r1+r3 is even.

Distinct actual triangles meet at most once. Three pairwise-intersecting
actual triangles must concur, since three distinct intersection points
would give a target edge a second common neighbor. These label facts imply
the actual positive fan inequality

    P>=3r1+5r2+7r3.                                  (1)

Indeed every positive fan root requires two sets of d_T outer defect
partners; each external positive root meets at most one outer point of
the whole fan, by linearity and the preceding distinct-triple prohibition.
No equitable profile, automorphism or selected inducedness is assumed.

## All three T-point profiles are retained

At a point of T, r3=1 and r1 is positive odd. If r1=1, T's degree three
requires at least two d2 roots. Formula(1) with P20 permits exactly two,
and the local sequence(3,2,2,1) has T joined to both d2 roots and the d1
root, with the d2 pair joined as well. Call this a bad point.
If r1=3, the fan already has weight16, so no d2 root is permitted;
the local graph is T's three-d1-leaf star. Call this a good point.
Values r1>=5 have fan weight at least22 and are impossible.
No separate positive local component fits the bad-point fan, and none
changes the good-point profile. Let h be the number of bad T points.
Every integer h0,1,2,3 will be treated.

Select O=D1 union {T}, of size s12. Its point incidences are even. Put w
equal to half that incidence on its actual support S, K=sum w(w-1),
ell=sum(w_u-1)(w_v-1) over selected triangle edges, and H equal to the
weighted sum of every other actual internal edge. All nonzero w are at
least one; K,ell,H are nonnegative, and no upper multiplicity is assumed.
Each good T point has w2, each bad T point has w1. With
Q=3I-A+J/9 positive semidefinite, the exact expansion gives

    q=w^TQw=s(s-6)/4-5K-2ell-2H
            =18-5K-2ell-2H>=0.                      (2)

In particular K>=2(3-h) and ell>=binom(3-h,2) from T's own edges.
At h0, q<=18-30-6=-18; at h1, q<=18-20-2=-4. Both are impossible.
Larger selected incidences or extra actual edges strengthen these bounds.

## Attached roots and the outside-point injection

The two d2 roots at every bad point are called attached. There are exactly
2h distinct such roots, and no other d2 root meets T. Their2(2h) outer
points are all distinct. Two attached roots at the same bad point cannot
share another point by linearity. Two attached roots at different points
cannot intersect anywhere, as those roots together with T would have
three distinct pairwise intersections. None of these outer points is in T.

At any attached outer point there is consequently at most one attached
root. If the point is outside S, there is no d1 or d3 root there. Its local
degree-two node needs at least three d2 roots. It therefore contains at
least two unattached d2 roots. Associate to each such outside point one
pair of those unattached roots. Distinct points receive distinct pairs,
because two actual triangles cannot intersect twice.

Each attached root already has its T point in S, of weight one. If it has
k of its two outer points in S, its nonselected internal edge contribution
to H is at least0,1,3 for k0,1,2 respectively. These actual edges cannot be
selected O edges, because an edge has its unique triangle partner and the
attached root is not in O. Contributions of distinct attached roots are
distinct. In particular each inside outer incidence contributes at least
one to this lower bound, without assuming S induced.

## h2: the only nonnegative Gram equality is impossible pointwise

There are four attached and four unattached d2 roots, with eight distinct
attached outer points. At most four of those points can be outside S.
For otherwise the pair injection gives at least five distinct pair edges
in the actual intersection graph of the four unattached roots. A graph
on four nodes with five edges contains a diamond. Each of its two triangle
triples must concur, and their shared root pair has only one intersection,
so all four unattached roots concur at the same actual point. The pair
labels used for five distinct outside points could then not be distinct.
Equivalently, any such outside point would contain all four unattached
roots and its attached root, giving fan weight25>P20. This is an actual
intersection graph, not an assertion that covered intersections are F edges.

Thus at least four attached outer points lie in S and H>=4. The one good
T point gives K>=2. Formula(2) now gives q<=18-10-8=0. Positive
semidefiniteness forces equality: K2, ell0, H4 and Qw=0. The sole point
with w>1 is the good T point, with w2; every other support point has w1.
Since sum w=3s/2=18, this coordinate equation is

    Aw=3w+2j.                                       (3)

At either bad T point p, the two selected triangles are T and its one d1
root. T's other two points have weights2 and1; the d1 root's other two
points have weight1 each, being distinct from T and its sole peak.
The selected neighbor contribution to (Aw)_p is therefore
2+1+1+1=5. Equation(3) at w_p1 demands exactly5, leaving no additional
actual edge from p to any support point with positive weight.

But any of the at least four attached outer points in S gives precisely
such an extra edge from its bad T point. Its triangle is not a selected
one, so that neighbor is distinct from the four already counted. This
contradicts(3). The zero q case is rejected by this actual coordinate,
not by an invalid generic claim that every nonempty q must be positive.

## h3: two unattached roots cannot absorb the twelve outer points

There are six attached roots, only two unattached roots and twelve distinct
attached outer points. At most one outer point lies outside S: every such
point needs the same pair of unattached roots, whose intersection is unique.
At least eleven outer points are in S. Across six two-outer-point roots,
this forces at least five roots to have both outer points in S and the
remaining root at least one. Their internal edges give H>=5*3+1=16.
Formula(2) gives q<=18-32=-14, a contradiction. If all twelve points are
inside, or their weights or other internal edges are larger, the bound
only strengthens. No assumption of identical attached-root profiles is made.

The four h cases are exhaustive, so b8 is impossible under the literal
one-d3 R226/maxd3 hypotheses.

## Falsification boundaries and review requirement

The four-unattached pair budget allows four outside attached points, not
three: a four-cycle intersection pattern alone has no diamond. The h2
inequality consequently reaches q0, and the separate bad-point coordinate
argument is essential. Also sum w/9=2 is integral, so integrality alone
does not reject this equality. The h3 proof uses distinct actual outer
labels and at least three d2 roots at every outside point, not a presumed
uniform incidence. Larger selected incidences are retained until K2 is
forced by equality.

The fan, parity and weighted upper Gram components overlap earlier work;
no archive-novelty conclusion is asserted. The new exact scope is only
the b8 boundary in the one-d3 R226/maxd3 lane. A different complete written
audit is required before VERIFIED or registration use. No whole one-d3,
R226 or target exclusion, mathematical execution or publication change
is claimed, and all old proof artifacts remain unchanged.

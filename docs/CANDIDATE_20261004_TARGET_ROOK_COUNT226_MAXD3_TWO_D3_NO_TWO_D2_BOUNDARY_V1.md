# Candidate: disjoint two-d3 roots at R226 cannot have two d2 roots

Root supplied the strict weighted-zero and small high-topology outlines.
Structural independently reconstructed their exact inequalities, actual
labels and every opposite-cycle pool. This new written CANDIDATE needs
a different full challenge. No mathematical program, enumeration, import,
solver or worker ran; earlier candidate bytes remain unchanged.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T. Suppose R=226, every d_T
belongs to {0,1,2,3}, exactly two actual deficiency-three triangles occur
and are disjoint, and b counts actual deficiency-two triangles. Then b
is not two.

All hypotheses are literal; no pending R226 result is used as a premise.
The necessary local/weighted/cycle facts are derived here, and the logical
dependency list is empty. This does not exclude all two-d3 populations,
R226 or the target.

Assume b2. Name the disjoint d3 roots A,B and the two d2 roots X,Y. There
are twenty d1 roots and P24. At a point the local degrees are the root
deficiencies, r1+r3 is even, and the actual fan has3r1+5r2+7r3<=24. This
fan follows by injecting the two outer partner sets of each focal root:
an external positive triangle cannot meet two fan outer points by actual
linearity or the lambda1 prohibition on three pairwise distinct triangle
intersections.

A point on A/B is bad if r1=1. It must have both X,Y and the valid local
graph(3,2,2,1); a third d2 is unavailable. There can be at most one bad
point by X/Y linearity. The nonbad A/B points have r1>=3. Thus h0/1 is
the complete case split.

## With no bad point, strict Gram energy removes all D3-D2 intersections

Select O=D1 union D3, of size22. Its incidences are even by the local
degree sum; let w be half those incidences on support S and zero elsewhere.
Then sum w=33. Put K=sum w(w-1), ell=sum_(selected O edges)(w_u-1)(w_v-1),
and H the weighted sum of all other actual internal S edges. Unique actual
triangle edges give

    E_selected=3*22+4K+ell,
    q=w^T Qw=88-5K-2ell-2H>=0,
    Q=3I-A+J/9, Q^2=7Q.                       (1)

Larger selected incidence and all extra actual edges remain in (1).
At h0 all six A/B points have w>=2, so K>=12 and their six selected
triangle edges give ell>=6.

Every d2 triangle is wholly in S: an outside point has no odd-deficiency
root, and local degree two would require at least three d2 nodes, while
only two exist. Let t count actual intersections of X/Y with A/B. Each
d2 root has at most two such points, one from each disjoint d3. Its three
internal edges have weight at least3 if t_root0, at least5 if t_root1,
and at least8 if t_root2. Thus H>=6+2t, and (1) gives q<=4-4t.

In fact q is strictly positive. If q0, (1) and Q^2=7Q give Qw0. But each
coordinate of Qw is the integer3w_v-(Aw)_v plus33/9=11/3, and cannot
vanish. Hence t>=1 is impossible, and both X,Y are actually disjoint
from A and B. This uses integer coordinates, not equitability or a
forced codeword premise.

## Actual cycle bounds used below

Let F be the global positive defect graph. Its edges carry the actual
intersection labels, node degrees are3d, and it has45 edges. The target
has45 uncovered squares. Every F4 with distinct labels gives its actual
uncovered induced square and conversely. A collapsed F4 needs four high
roots at one point, impossible here because A,B are disjoint. Thus
C4(F)=45 and total node cycle incidence180.

F has no K3,3: repeated labels would require six roots with local degree
at least three at one point, but only A,B are d3; distinct labels give
an actual induced rook incompatible with its defect edges. All codegrees
are at most three, by actual cross-edge matchings for disjoint highs,
literal common-point high sets for intersecting highs, or low degree three.

No low lies in an F triangle. A low with a low neighbor has at most five
cycles, since six produces K3,3 using that neighbor's degree three. Only
a low with three independent high neighbors can be an exception, adding
at most one to this bound; there are at most three for each high triple.

For a high root Z let N be its F neighbor set. In every topology below,
its internal graph is empty or one edge, with no internal opposite cycle.
The external incidence
B=sum_N deg-deg(Z)-2e(N) bounds c_Z from above because codegrees l<=3
give binom(l,2)<=l. If B is not divisible by three then c_Z<=B-1.
Low root-neighbor slots are filled and cross-bucket intersections are
forbidden, so no unspecified internal neighbor edges are discarded.

## Complete no-bad-point cycle contradiction

A and B each have nine independent low defect neighbors, giving B18.
If X,Y have no F edge, each has six independent low neighbors and B12.
There are four possible independent high triples and at most twelve low
exceptions, so the full incidence upper bound is

    20*5+12+2*18+2*12=172<180.

If X,Y have their F edge, each has five low neighbors and the other
degree-six high, giving B15. There are only two independent high triples,
so at most six low exceptions. The total is again

    20*5+6+2*18+2*15=172<180.

An actual X/Y intersection with a covered pair may have no F edge and is
included in the first safe bound; actual intersection is not silently
equated with a defect edge. These contradictions reject h0.

## One bad point gives a high triangle, with or without a pendant

Let the bad point belong to A. The valid local graph is the high triangle
AXY and a single d1 leaf at A. B can intersect at most one of X,Y:
two distinct intersections would give the forbidden actual loose triple
B,X,Y, while coincidence would make X,Y share two points or make B meet A.
If B meets one, name it X. Its local profile is(3,2,1,1,1), with forced
BX edge, since r1>=5 would need fan27>24. Thus the two complete high F
topologies are a triangle plus isolated B, or a triangle with pendant B-X.
Their high independent sets have size at most two, so every low has a
low neighbor and their complete contribution is at most100.

In the isolated case A has seven lows and degree-six neighbors X,Y, with
internal XY edge. Its B=7*3+6+6-9-2=22 gives c_A<=21. X,Y each have four
lows and degree-nine/six high neighbors, with one internal high edge:
B=4*3+9+6-6-2=19 gives c<=18. B itself has c<=18. Total incidence is

    100+21+18+18+18=175<180.

For the pendant case the generic bounds are c_A<=21, c_X<=24, c_Y<=18,
c_B<=21. The key safe refinement is c_Y<=12. Y has high neighbors A,X
and four independent lows L_Y. A low in L_Y can have a second high
neighbor only B, since A,X intersect Y at the bad point. If n is their
number, n<=2: Y,B already have common high X and total codegree at most
three. Thus L_Y has8-n LL stubs. The external high B has I1 through X
and n low neighbors in L_Y, giving binom(1+n,2)<=3n/2. An external low
opposite has at most one A/X neighbor and x LL neighbors in L_Y;
binom(I+x,2)<=3x/2 for I0/1. Their x sum is8-n. Internal AX is one edge
and gives no opposite with two internal edges. Hence c_Y<=3n/2+3(8-n)/2=12.
All high and low opposite nodes and LL stubs have been counted. The total
is now

    100+21+24+12+21=178<180.

Thus h1 also fails, proving the exact b2 exclusion under disjointness.

## Boundaries and pending status

Strict q0 impossibility comes from the literal coordinate fraction11/3
and Q^2=7Q. It is not an asserted unequal-profile bound. All extra support
edges remain in H. Both the high triangle and its pendant are valid local
graphs; only the complete target incidence rejects them. The Y12 bound
uses the exact cancellation8-n plus n, not a generic bound on a degree-six
root. The possible covered X/Y actual intersection is explicitly included.

Fan, weighted Gram, actual-square and low-cycle methods overlap prior
papers. The new exact scope is the disjoint c2/b2 lane at R226/maxd3.
No novelty, whole-archive coverage, full two-d3/R226 exclusion, construction
or target resolution is claimed. The current publication cutoff stays
unchanged; a different author must challenge the full frozen proof before
any VERIFIED or ledger use.

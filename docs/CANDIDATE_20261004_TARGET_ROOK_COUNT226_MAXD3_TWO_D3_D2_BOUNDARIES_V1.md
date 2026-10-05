# Candidate: the two-d3 lane at R226 has between two and six d2 roots

Structural independently derived the local common-point possibilities and
the exact small-population cycle bounds after the preceding R226 work.
Root received the outline for a separate challenge. This is a new written
CANDIDATE, not a gate inferred from an earlier R227 result. No mathematical
program, enumeration, import, solver or worker ran.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle.
Suppose R=226, every d_T belongs to {0,1,2,3}, and exactly two actual
triangles have deficiency three. If b counts the actual deficiency-two
triangles, then 2<=b<=6. Moreover, if the two deficiency-three triangles
intersect, then b=2 and at their common point the complete positive local
defect graph has degree sequence(3,3,2,2): K4 minus the edge between the
two d2 nodes, with no d1 root at that point.

All hypotheses, including maxd3 and c2, are literal. No pending R226
maxd3/c3 result is used as a logical premise. The argument below derives
the necessary fan, point-label and cycle facts; its logical dependency
list is empty. It does not exclude the two-d3 lane or R226, and makes no
surviving-case realization claim.

Put a=24-2b and P=26-b, so 0<=b<=12. At each actual point the local
defect degrees are the root deficiencies, parity makes r1+r3 even, and
the actual fan injection gives

    3r1+5r2+7r3<=P.                            (1)

The injection counts two outer sets of defect partners for each focal
root: an external positive triangle cannot meet two fan outer points by
linearity or by the prohibition of three actual triangles pairwise
meeting at distinct points. This is exact target lambda1, not an
automorphism or a uniform-neighborhood premise.

## All possible common-point profiles are explicit

If the two d3 roots meet at v, r3=2 and r1 is even. A degree-three node
requires at least four local nodes. The complete possibilities under (1)
are:

| b | (r1,r2,r3) at v | actual local defect graph |
|---:|---|---|
|0|(4,0,2)|the d3-d3 edge, with two d1 leaves at each high|
|1|(2,1,2)|a triangle on the two d3 and one d2, with one d1 leaf at each d3|
|2|(0,2,2)|K4 minus the d2-d2 edge|

For completeness, r1=0 needs r2>=2 and fan at least24; it forces b2
because P=26-b and b>=2. Additional d2 nodes exceed P. At r1=2,r2=0,
degree sequence(3,3,1,1) is nongraphical. Adding a d2 gives fan25 and forces
b1, with exactly one d2. At r1=4 the fan26 forces b0, and larger r1 fails.
No unlisted common-point profile is possible.

The first two graphs follow from their literal high/low degree sums: one
high-high edge with four attached leaves in the first, and all three
high-high edges plus two attached leaves in the second. The third has
universal degree-three nodes, leaving the degree-two nodes adjacent only
to those universals. These are valid local graphs. In particular the third
contains a collapsed local four-cycle and is not falsely declared
nongraphical or treated as an ordinary target square.

Thus for b>=3 the two d3 roots are disjoint. A common point, if it occurs,
is unique by actual triangle linearity.

## The upper bound b<=6 needs only the actual pair moment

If b>=7, P<=19. The d3 roots are disjoint by the common-point table. At
each of their six points there is one d3, so r1 is odd. A value r1=1 needs
at least two d2 nodes for degree three, with fan at least20. A value
r1>=5 has fan at least22. A d2 together with r1=3 has fan21. Therefore
all six points have exactly three d1 leaves and no d2.

Let t_L count how many of these six points lie on each actual d1 triangle.
It belongs to {0,1,2}, since it cannot meet either d3 root twice. The
point count gives sum t_L=18. The two disjoint d3 roots have at most three
cross edges, a matching, each with a unique actual triangle completion.
Consequently

    sum binom(t_L,2)<=3,
    sum binom(t_L,2)>=sum(t_L-1)=18-a.

Hence a>=15, while a=24-2b<=10 at b>=7. This rejects every b7 through12,
without a numerical enumeration or selected inducedness assumption.

## Exact small-population defect-cycle method

For b0/1, let F have the positive actual triangles as nodes and local
uncovered rook pairs as edges, labeled by their actual intersection
points. A deficiency-i node has degree3i. Here F has45 edges, and the
target has45 uncovered actual squares at R226.

An F four-cycle either has four distinct point labels, giving its unique
actual uncovered induced square, or all four labels coincide. The latter
requires four local nodes of deficiency at least two. At b0/1 there are
only two or three such nodes, so no collapsed cycle is possible. The
actual square/F4 maps are inverse, and C4(F)=45, with180 node incidences.

F has no K3,3 in these cases. A repeated grid label propagates to all
six triangles at one point and would require six local degree-at-least-
three roots, unavailable here. With all nine labels distinct it is an
actual induced rook, whose pairs cannot be designated defects; extra grid
nonneighbor edges would violate lambda1. Every codegree is at most three:
disjoint high roots have at most three cross-matching completions, an
intersecting high pair has at most its one third high root, and any low
node has degree three.

No F triangle contains a d1 node. A low with a low neighbor lies in at
most five four-cycles; six forces K3,3 using the degree-three neighbor.
Only a low adjacent to three independent highs can be an exception,
contributing at most six. There are at most three such exceptions for a
given high triple, and none if any pair of its highs intersects.

For a high root Z with neighbor set N, the graphs used below have at
most one internal N edge. Let

    B=sum_{x in N}deg_F(x)-deg_F(Z)-2e_F(N).

No opposite-cycle node lies inside N because its internal maximum degree
is at most one. All external common-neighbor counts l are at most three,
so c_Z=sum binom(l,2)<=B. If B is not divisible by three, at least one
l1/2 loses a unit and c_Z<=B-1. Actual local filled low slots and the
distinct-intersection prohibition exclude all unspecified internal N
edges. High triangles themselves remain allowed.

## Exclude b0

There are twenty-four lows and two degree-nine d3 highs. If the highs
are disjoint, each has nine independent low neighbors and B18. If they
intersect, the first common-point profile gives eight lows plus the other
degree-nine high, with no internal neighbor edge, and B24 at each.
There cannot be an all-high low with only two highs. The complete incidence
bounds are therefore

    disjoint: 24*5+2*18=156,
    intersecting: 24*5+2*24=168,

both less than180. Extra separate low-low matchings at a high point do not
alter the high's actual defect neighbors or these bounds.

## Exclude b1, including the valid local high triangle

There are twenty-two lows, two degree-nine highs A,B, and one degree-six
high C. First let A,B be disjoint. Let k count how many of them meet C.
An actual intersection with C has local profile(3,2,1,1,1): the high-high
edge, two leaves on d3 and one on d2. If k2, those points are distinct,
and A,B are not adjacent in F. At each root all low neighbor slots are
filled and there is no internal neighbor edge. A d3 meeting C has B21
instead of18; C has B12+6k. Thus the high contribution is48+9k.

At k0 the high triple is independent, allowing at most three low
exceptions. At k1/2 there is a high edge, so no exception. The totals are

    k0: 22*5+3+48=161,
    k1: 22*5+57=167,
    k2: 22*5+66=176.

All fail180.

If A,B intersect, the common-point table forces the valid local high
triangle A,B,C, with one leaf at each d3. Each d3 root has seven low
neighbors and the degree-nine/six highs; its neighbor set contains the
one high-high edge. Thus B=7*3+9+6-9-2=25, and c<=24. The d2 root has
four lows and two degree-nine highs, with their one internal edge:
B=4*3+9+9-6-2=22, hence c<=21. The three highs are not independent, so
no low exception occurs. The total is

    22*5+24+24+21=179<180.

The integer losses25->24 and22->21 are necessary. Without them the
loose bound182 would not give this contradiction; the valid local high
triangle is not deleted to obtain a false triangle-free estimate.

## Conclusion and the deliberately retained b2 boundary

The upper pair-moment proof and the b0/1 cycle contradictions prove
2<=b<=6. The common-point table then leaves only b2 when the d3 roots
intersect, with the stated exact K4-minus-edge local graph.

That b2 graph has a genuine abstract local four-cycle whose actual point
labels all coincide. It must not be identified with a target square or
run through the faithful180-incidence argument. This statement does not
exclude it, or the disjoint b2..6 populations. No count of those possible
graphs, their extra edges or their matching labels is asserted.

Fan, pair-matching, K3,3 and integer cycle bounds overlap earlier methods.
The new literal scope is the complete two-d3 population boundary at
R226/maxd3, with its valid collapsed-cycle exception retained. No novelty
or whole-archive coverage assertion is made. The proof requires a
different-author exact written challenge before any VERIFIED/ledger use;
the current publication cutoff is unchanged.

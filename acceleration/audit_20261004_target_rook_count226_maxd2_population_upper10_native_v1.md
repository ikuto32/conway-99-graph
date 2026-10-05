# Independent written audit: literal R226/maxd2 implies b<=10

Completed independent verification: 2026-10-04T22:29:26.2279984Z.
Verifier: /root/native_driver. Mathematical producer: /root/structural.
Method: independent_derivation. No computational executor or worker.

Paper: docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD2_D2_POPULATION_UPPER10_V1.md,
SHA256 8752bc4a1a8452234f6dcc18e9bd633f8f519f73d58104925c72d35ea21787d2.
Raw candidate: acceleration/results/20261004_target_rook_count226_maxd2_d2_population_upper10_candidate01.json,
SHA256 db0594afec5db614cfc682f7ba76ae503663c6e5f805e938c029b19f0a52758e.
Exact ID: C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD2-D2-POPULATION-UPPER10 r1.

The whole paper and raw statement survive the independent reconstruction
below. This is a written PASS for their exact conditional statement. It
does not exclude R226/maxd2, R226, or the target. Maximum deficiency two is
a literal hypothesis, and no earlier mathematical gate is a premise.

## Exact statement and inherited discovery boundary

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle T.
Suppose R=226 and every d_T belongs to {0,1,2}. If b counts actual
deficiency-two triangles, then b<=10.

Structural supplied the bridge and eleven-node two-step discovery. Root
challenged the selected multiplicity boundary. Native separately derived
the actual geometry, each population branch and their quantitative
contradictions. Earlier parity, even-six, cubic-eight, rook uniqueness and
upper-Gram mechanisms overlap; this review asserts no independent discovery
or archive novelty. Shared agreement is not its verification basis.

## Reconstruction from the complete target hypotheses

There are 693 edges. Every edge has exactly one triangle completion, so
there are 231 actual triangles. Every vertex belongs to seven triangles;
their outer pairs partition its fourteen neighbors. Distinct triangles
meet at most once. Three pairwise-intersecting triangles with three distinct
intersection points are impossible: those points themselves form a triangle,
and one of its edges would have both its designated completion and the
third intersection point as common neighbors. Thus any intersecting triple
of actual triangles is concurrent.

For intersecting triangles in a containing rook, their common point and
four outer points determine the remaining four points. Each cross pair of
outer points is nonadjacent in that rook, has the common point as one common
neighbor, and mu=2 determines its second common neighbor. For disjoint
triangles in a containing rook, their actual cross edges are the matching
of three parallel-row positions; each edge's unique completion determines
the third row. Consequently any two actual triangles determine at most
one containing actual induced rook, conditional on its existence.

At a point p, the local defect graph has its seven actual triangles as
nodes. A pair is joined when no actual rook contains both. Each rook
containing T gives exactly one covered partner of T at p. The uniqueness
just proved prevents duplicate covered partners. Hence the local degree of
T is exactly d_T=6-r_T. Zero-deficiency nodes are isolated; all defect
partners have positive deficiency. Summing over 231 triangles, each rook
contributes six incidences, giving sum d_T=1386-6R=30. Under the literal
maxd2 assumption, a=30-2b, P=a+b=30-b, and 0<=b<=15. The odd local degrees
are precisely the d1 nodes, so their incidence count is even at every point.

For a fan of r1 d1 roots and r2 d2 roots at p, the focal roots require
2r1+4r2 external positive defect partners through their outer points.
No external triangle can meet two outer points of the whole fan: two
points on one root violate linearity; points on different roots give a
nonconcurrent triple. Thus the partners are distinct and

    P >= r1+r2+2r1+4r2 = 3r1+5r2.

This is an actual-label count, independent of uniformity or automorphisms.

## Selected-family and full-target Gram identities

For any even selection of s actual triangles and a point of selected
multiplicity r, its 2r outer points have odd incidence from their one focal
root. Each requires an additional selected root. A selected root outside
the fan can meet at most one of these points, so s-r>=2r, or s>=3r.
If s is six or eight, positive even multiplicity is therefore exactly two.
The dual graph has triangle nodes and intersection-point edges. It is
simple, cubic and triangle-free, with every edge label an actual point.

This multiplicity conclusion is not silently used for s two or four.
For any positive even selection, write w_v for half its multiplicity,
K=sum w_v(w_v-1), ell=sum(w_u-1)(w_v-1) over selected edges, and H for the
weighted contribution of every other actual internal edge. All are
nonnegative. The number of selected edges is 3s; their weighted sum is
3s+4K+ell, because the selected degree at v is 4w_v. Also sum w=3s/2 and
sum w^2=3s/2+K. The complete target identity is

    A^2=12I-A+2J, A j=14j.
    Q=3I-A+J/9, Q^2=7Q.

As Q is real symmetric, w^TQw=||Qw||^2/7>=0, and direct substitution gives

    w^TQw=s(s-6)/4-5K-2ell-2H.

All extra actual edges and arbitrary larger selected incidences are
included. Positive even selections of size two or four have base -2 and
are impossible.

For s six, the cubic triangle-free six-node dual is K3,3: the three
neighbors of a node are independent, and each must join both remaining
nodes. Its nine actual edge points form the grid. Grid nonneighbors
already have two common grid neighbors, so any additional edge between
them would violate lambda=1. The grid is an actual induced rook, with
precisely the six selected triangles as its rows and columns.

An even eight-selection O cannot overlap an actual rook's six triangles
B in at least four roots. Their symmetric difference is even, of size
14-2|O intersect B|. Overlap five or six yields the impossible positive
sizes four or two. Overlap four yields a second induced rook, distinct
from B, sharing its two B\O triangles. Conditional two-triangle rook
uniqueness rejects this. The eight-selection itself is not rejected.

## Exhaustive b11..15 proof

At b11, a=8 and P=19. The selected d1 family has multiplicity two and
twelve actual support points. Every edge of its cubic triangle-free
eight-node dual lies in a four-cycle. To establish this without enumeration,
first note that a four-cycle-free root would require itself, three
neighbors and six distinct second neighbors: ten nodes. Choose a four-cycle
C. It has no chord. Its four cross edges leave four edges on the other
four vertices. A triangle-free four-vertex graph with four edges is C4:
a degree-three vertex permits only its three incident edges, and otherwise
four edges force every degree to be two. Thus the cross edges are a perfect
matching between C and the other C4. Transporting the second cycle along
that matching gives two cycles on four labels. Their complements are
perfect matchings; the cycles are equal or share a perfect matching. Every
cross edge is therefore on a square, and all other edges already are.

Each dual square yields an induced actual square on its four distinct
intersection points. A diagonal would violate lambda=1. A containing rook
would contain its four unique edge-completing selected triangles, forbidden
by the overlap bound. Hence the two d1 roots at every support point are
each other's defect partners, occupying both degree-one slots. A d2 root
there would require two more d2 partners; the fan would have r1=2, r2>=3
and need at least 21 positive roots, exceeding 19. No d2 root meets that
selected support.

At any d2 point, r1=0 and local degree two requires r2>=3. The fan gives
5r2<=19, so r2=3 and the local graph is K3. The eleven d2 triangles form
a simple six-regular defect graph F2. Every actual intersection of two of
them is a defect edge. An adjacent pair has exactly one common F2 neighbor:
every common triangle must concur at their unique intersection, where
exactly three d2 roots occur. Nonadjacent pairs are actual disjoint
triangles. Their cross target edges form a matching of at most three,
and each has its unique triangle completion, so they have at most three
common F2 neighbors. From a root there are 6*5=30 nonreturn length-two
paths, but their endpoints contribute at most six adjacent common counts
of one and four nonadjacent counts of three: 30<=6+12=18. Contradiction.

At b12, the six selected d1 roots form an induced actual rook on S of
size nine. Its eighteen edges give chi^TQchi=27-36+9=0. Therefore
Qchi=0 and Achi=3chi+j: each outside actual point has exactly one S
neighbor. Only the six selected row/column triangles are wholly inside S;
any other triangle meets S at most once. A pair of adjacent S points has
its unique triangle completion in S, and an outside point cannot have two
S neighbors.

At every S point the two d1 roots are a covered rook pair. Their defect
partners must consequently be d2 roots. In particular there is at least
one d2/S incidence at each point. Let t be their total, at least nine;
it counts distinct bridge triangles. Their 2t outer points are outside S
and all distinct. If two bridges shared one, the outside-one-neighbor
equation would make their S points equal, contradicting linearity. No d1
root meets an outer point, because all six d1 roots are wholly in S. Each
outer point requires at least three d2 roots. Thus the complete outside
d2 incidence is 3b-t>=6t, so 3b>=7t>=63. But 3b=36. Contradiction.

At b13 and b14 the positive even d1 families have sizes four and two.
Their exact Gram base -2, less the retained nonnegative corrections,
contradicts PSD.

At b15 there is no selected d1 family. The fifteen d2 roots have 45 actual
point incidences. Local degree two requires at least three roots per used
point, and the positive fan bound permits at most three. Thus their support
has exactly fifteen points. Their 45 triangle edges are distinct actual
edges inside this support. With all additional edges allowed, e(S)>=45
and chi_S^TQchi_S=45-2e(S)+25<=-20, contradicting PSD. This separate
branch never assigns an invented support to an empty selection.

All possible b above ten, and only those values, have been excluded.

## Written proof-check record: 34 checks, zero executions

1. Edge count 693 and unique completions give 231 actual triangles.
2. Seven incident triangles and outer-pair disjointness at each point.
3. Actual linearity and the nonconcurrent-triple prohibition.
4. Intersecting two-triangle rook uniqueness uses mu=2.
5. Disjoint two-triangle rook uniqueness uses actual cross matching.
6. Local degree d_T equals six minus its covered partner count.
7. Deficiency mass 30, a=30-2b, P=30-b and integer domain 0..15.
8. Local d1 parity and even selected incidence.
9. Full-fan outer partner injection and P>=3r1+5r2.
10. Selected fan parity injection proves s>=3r.
11. Six/eight multiplicity two is derived, including the r4 challenge.
12. The resulting dual is simple, cubic and triangle-free.
13. Complete target identities A^2 and A j.
14. Exact Q^2=7Q and its norm-based PSD implication.
15. Selected weighted-edge sum 3s+4K+ell.
16. Exact q formula with arbitrary extra actual edges.
17. Positive even sizes two and four have Gram base -2.
18. The six-node cubic triangle-free dual is K3,3.
19. Its labelled grid is an induced actual rook.
20. Even symmetric difference rejects all eight-selection overlaps >=4.
21. Eight-node C4 existence is a ten-node distance count.
22. The remaining four-node graph is C4 and the cross edges a matching.
23. Two transported four-cycles ensure every cross edge is on a square.
24. Actual dual-square inducedness and unique edge completions.
25. Occupied d1 slots exclude every b11 d2/S incidence.
26. Remaining b11 d2 points have exactly three roots and local K3.
27. Global eleven-root graph is simple six-regular.
28. Adjacent-one and disjoint-at-most-three common-root bounds.
29. Complete two-step contradiction 30>18.
30. Actual b12 rook has Qchi=0 and every outside point one S neighbor.
31. At least nine distinct bridge roots and 2t distinct outer labels.
32. Complete bridge incidence contradiction 36<63.
33. Both b13/14 Gram branches retain all multiplicities and edges.
34. Separate b15 support/edge count gives q<=-20.

## Written falsification/boundary record: 14 challenges

1. A fourfold selected point is counted before the dual is made cubic.
2. An arbitrary even eight-selection is not itself asserted impossible.
3. The no-C4 distance argument does not presume connectedness.
4. Four-node degree-three alternatives really have at most three edges.
5. Cross edges can initially repeat a destination; C4 degrees force the bijection.
6. Rook uniqueness is conditional on actual existence, not completion existence.
7. Symmetric difference preserves even incidence but not arbitrary graph hypotheses.
8. A square alone is insufficient; its four edge-completing roots are counted.
9. A covered actual intersection is not globally assumed to be an F edge.
10. The b11 local K3 proof, specifically, makes every positive intersection an edge.
11. Abstract six-regular graphs without the exact common-root bounds are permitted.
12. The b12 outside equation comes from the full target Q, not rook geometry alone.
13. Distinct bridge outer labels are proved; counting repeated labels would fail.
14. The empty d1 branch and all added internal edges are retained separately.

There are 48 written checks, no computational/formal/external checks and
no solver calls. Small documentary reads, four selected file hashes and
append-only metadata are the only tool work. No ledger was parsed or
changed, and no scientific program, import, worker, enumeration, Git/index
or publication mutation occurred. Root-reported live467 is contextual
only; the original candidate times/nulls and all historical bytes remain.
Registration and Root's exact new acceptance are separate later actions.

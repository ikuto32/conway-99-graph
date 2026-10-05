# Independent derivation of the conditional R228 deficiency patterns

Reviewer: /root/checkpoint_audit; producer: /root/structural. The whole frozen
paper and raw statement were read. The two stated accepted r1 dependencies
supply only maximum deficiency at most two and existence of deficiency at least
two. The following reconstruction is written mathematics; there was no graph
enumeration, import, solver, matrix program or ledger/Git operation.

In a complete SRG(99,14,1,2), an edge has a unique triangle. A point's fourteen
neighbors induce seven separate edges, so 231 actual triangles occur. Two
triangles have at most one common point. Three triangles with three different
pairwise intersections are impossible: their intersection points would form
another triangle using an edge of one of the original triangles.

For a triangle T through point v, each of the other six triangles through v
either participates with T in its uniquely determined rook or is defective.
The four cross pairs have unique second common neighbors, fixing any rook.
Different rooks containing T supply different partners at v. Thus the local
defect degree of T is its deficiency d_T at each of its three actual points.
Six triangle incidences per rook give D = 6(231-R) = 18. The dependencies now
give d_T in {0,1,2} and at least one d2 triangle. If h is the d2 population,
p = 18-2h is the d1 population. Handshaking in each local defect graph makes
the d1 selection even at every point; this permits high point multiplicities.

For a chosen d2 T, its six defect partners form three buckets of two. The
twelve points away from T are distinct. A repeated point within a bucket
violates linearity, and a repeat between buckets makes the forbidden triple
of triangles. At the two outer points, all defect partners of a bucket
triangle lie outside those six triangles and T. If k bucket triangles have
d2, their mass is 6+k and they demand 12+2k outer incidences. Every external
triangle can supply at most one in each bucket, hence at most three overall.
The external mass is 10-k; if ell external triangles have d2, there are
10-k-ell positive external triangles. Therefore 3ell+5k <= 18 and k <= 3.
This is an incidence capacity statement, not a distinct-neighbor count.

The even d1 selection cannot have two or four members. At size four, a
fourfold point leaves eight distinct odd outer points; without a fourfold
point every used point has multiplicity two and the dual is a simple cubic
K4. Its triangle would be the forbidden three-intersection configuration.
At size six, a sixfold point leaves twelve odd outer points. A fourfold point
leaves eight that the remaining two triangles' six incidences cannot repair.
All point multiplicities are consequently two. A simple cubic triangle-free
graph on six nodes is K3,3: the three neighbors of a node each must use both
remaining nodes. Its edge-points are a nine-point rook; any extra grid edge
would already have two common neighbors, contradicting lambda1.

Hence h8 and h7 fail by p2 and p4. If h9, all positive triangles have d2,
so the chosen T would have k6, contrary to k <= 3. If h6, the six d1 triangles
form that actual induced rook. At every one of its nine points the two d1
triangles are rook-covered and cannot be each other's defect partners. A
positive partner must instead be one of six d2 triangles. A different actual
triangle meets the induced rook in at most one point: a nonadjacent pair cannot
share a triangle and an adjacent pair already has its third point fixed.
Six available triangles cannot supply all nine points. Thus 1 <= h <= 5.

When k3, h = 1+k+ell leaves h4/ell0 or h5/ell1. The latter has exactly six
positive external triangles and eighteen required outer incidences, exhausting
all three slots of every external triangle. Their three points are all outer
C points. The unique external d2 triangle O needs a second defect partner at
each of its points after its edge to the unique C triangle. It cannot use T,
another C triangle, or another external d2 triangle. An external d1 partner Z
is also saturated and already uses its sole defect edge there to that same
C triangle. It cannot additionally partner O. This is the needed individual
point contradiction; the scalar eighteen-slot equality alone is insufficient.
Thus k3 implies h4, and h5 gives maximum d2-graph degree two.

At h4 with a degree-three d2 node, the other three nodes are its bucket
partners. Any edge between two leaves requires a common bucket, and a bucket
has only two partners. At most one leaf edge occurs. Therefore the graph is
the three-leaf star or that star plus one leaf edge. Such a triangle occurs
at one actual point and is not prohibited by the three-different-points rule.

The capacity table is recovered directly: k0,1,2,3 give mass pairs (6,10),
(7,9),(8,8),(9,7), demand 12,14,16,18, and ell ceilings 6,4,2,1. Combining
h=1+k+ell with 1..5 and the saturation rejection yields respectively
h1..5, h2..5, h3..5 and h4 only. These are necessary possibilities.

Hand challenges retained: an actual even-six rook is permitted; the contradiction
uses its d1 degrees and shortage of d2 cover. The cube-star even-eight selection
does not contradict parity. The h4/k3 and h5/k2 cases retain respectively three
and two unused external slots and cannot be rejected by the saturated argument.
No induced full positive support, uniformity, automorphism, target realization,
R228 exclusion or nonconstant codeword was introduced.

PASS for the exact r1 conditional statement only. The stronger four/five paper
is a separate review, not a premise or approval of this weaker statement.

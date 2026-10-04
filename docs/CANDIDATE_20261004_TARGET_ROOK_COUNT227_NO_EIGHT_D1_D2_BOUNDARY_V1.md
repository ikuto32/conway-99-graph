# Candidate: R227 cannot have eight d1 and eight d2 triangles

This is a separate written follow-up. The R227 sixteen-row table and the
single-d3 candidate remain unchanged. Root challenged the disjoint-triangle
rook uniqueness and cubic-eight square steps before this freeze. No
mathematical program, enumeration, import, backend or worker ran. Independent
written verification is required; this is outside the current publication cutoff.

## Exact statement

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once and define d_T=6-r_T for each actual triangle. If R=227
and no triangle has deficiency three, it is impossible that exactly eight
triangles have deficiency two. Equivalently, the positive deficiency family
cannot consist of exactly eight deficiency-one and eight deficiency-two
triangles, with every other triangle of deficiency zero.

This does not exclude R227, classify the remaining populations, or forbid an
arbitrary even eight-triangle incidence relation. In combination with a
separately established necessary sixteen-row table, this removes its c0,b8
row; that table is not an assumed verified premise here.

## Exact inputs and local facts

Only C-UNRESTRICTED-TARGET-ROOK-DEFICIENCY-STRICT-SECOND-NEIGHBOR-BOUND r1 is
inherited, to give d_T<=3 at total deficiency D=6(231-R)=24. Thus the stated
boundary has exactly eight d1 and eight d2 triangles, P=16 positive triangles.

Every edge has its unique triangle partner; distinct actual triangles meet
at most once; three cannot meet pairwise at three different points. At each
point the local simple defect graph has its incident triangles as nodes,
joining a pair if no induced rook contains both. Its node T has degree d_T.
The triangles of odd deficiency form an even-incidence selection; in the
present boundary these are exactly the eight d1 triangles.

The actual positive point-fan inequality is

    P>=3r_1+5r_2,

obtained by counting the two sets of external defect incidences of each
positive fan triangle. An external triangle can meet only one outer point
of the entire fan, by linearity and the forbidden distinct-intersection triple.
Zero-deficiency triangles cannot provide defect partners.

## The even eight-selection has a cubic dual

Suppose a point lies in r>=4 of the eight selected d1 triangles. Their2r
outer points are distinct. Each outer point has one selected incident triangle
and therefore requires another selected triangle for parity. A selected
triangle external to this point fan meets at most one of its outer points,
by the same geometric prohibition. The eight-r external selected triangles
must consequently number at least2r, or8>=3r, impossible for r>=4.

Every used point has even selected multiplicity, so it is exactly two.
The eight selected actual triangles form a simple cubic dual G: its nodes
are the selected triangles and its edges are their twelve intersection points.
A dual triangle would be three actual triangles meeting at three different
points, so G is triangle-free. These assertions concern actual labels and
do not declare the twelve-point support induced.

## Every edge of a triangle-free cubic graph on eight nodes lies in a square

First G has a four-cycle. If it had no such cycle, the three neighbors of
any node would have six distinct further neighbors, distinct from the root
and its three neighbors by the absence of triangles and four-cycles. This
would require at least ten nodes, contrary to eight.

Choose a four-cycle C. It has no chord, since a chord makes a triangle.
Each of its four nodes has exactly one neighbor outside C. The remaining
four nodes consequently have total internal degree12-4=8, or four internal
edges. A triangle-free simple graph on four nodes with four edges is a
four-cycle C': a node of degree three would leave an independent three-node
neighborhood and hence only three edges. Thus every remaining node has two
internal neighbors and one C neighbor. The four cross edges form a bijective
matching, not a presumed target symmetry.

Transport the order of C' back to the four labels of C using that matching.
Two four-cycle graphs on four labels are either identical or have a two-edge
perfect matching in common: each is K4 minus one of its three perfect
matchings. For every label v there is therefore a label u adjacent to it
in both cycle graphs. The two cross edges at v,u and those two cycle edges
form a square containing the cross edge at v. All eight internal cycle edges
already lie in C or C'. Hence all twelve edges of G lie in four-cycles.
This proof uses exactly eight nodes and no graph enumeration.

## Any two actual triangles determine at most one rook

For intersecting triangles, any rook places them as a row and column through
their common point. The four cross pairs have unique second common neighbors,
so their four opposite grid points fix the full nine-subset.

For disjoint triangles T,U, any rook places them as two parallel rows or
two parallel columns. In such a rook each point of T is adjacent to precisely
one point of U. These three cross edges are the entire cross adjacency:
an outside vertex cannot meet two vertices of an actual triangle, since
their edge already has its triangle partner. Thus the matching of cross
edges is determined by the actual target, rather than chosen by a labeling.
Their three unique triangle completions are exactly the third parallel
row or column. T,U and those three points fix the same nine-subset in every
proposed rook. This is uniqueness conditional on existence, not a claim that
an arbitrary pair completes to a rook. Arbitrary other target edges are allowed.

Consequently two distinct induced rooks share at most one actual triangle.
This statement concerns actual triangle subsets, not embeddings or a graph
automorphism identifying row and column labels.

## An even eight-selection cannot share four triangles with a rook

An even selection of two actual triangles is impossible by linearity. An
even selection of four is also impossible: a fourfold point leaves eight
private odd outer points; otherwise every point has multiplicity two and
the simple cubic dual is K4, whose triangles violate the geometric prohibition.

An even selection of six is an induced rook. A sixfold point leaves twelve
private outer points; a fourfold point leaves eight odd points for the other
two triangles' six incidences. Otherwise all multiplicities are two and
the simple cubic triangle-free six-node dual is K3,3: the three neighbors
of any node each must join both remaining nodes. Its nine edge points form
the rook. Any additional edge between grid nonneighbors would have two
known common neighbors, contradicting lambda1 for that extra edge. This
inducedness is proved before invoking the disjoint-triangle uniqueness.

Let A be the eight selected d1 triangles and B the six triangles of any
actual rook. Both selections have even point incidence. If k=|A intersect B|
is at least four, their symmetric difference is an even selection of size
14-2k. For k=5 or6 this is four or two, already impossible. For k=4 it is
six, hence is the triangle set of another induced rook B'. This second rook
shares with B the two triangles of B outside A, and is distinct because
A is nonempty. The uniqueness just proved forbids this. Therefore no rook
contains four or more of the eight selected triangles.

## Every selected intersection is its d1 defect pair

The four distinct edge-points of a four-cycle of G form an actual induced
square. Their successive pairs lie in the four selected triangles. A diagonal
edge would have both other square corners as common neighbors and violate
lambda1, so arbitrary additional target edges do not spoil this square.

If a rook covered it, it would contain all four selected edge triangles
because each square edge has its unique triangle partner. That is forbidden
by the preceding paragraph. Thus the square is uncovered. At each corner
its two selected triangles are a defect pair: a rook containing that pair
would also contain the square, since its opposite corner is their cross
pair's uniquely fixed second common neighbor.

Every edge of G lies in a four-cycle, so at all twelve used points the two
d1 triangles are each other's defect partners and their degree-one defect
slots are fully occupied. A d2 triangle through such a point cannot use
either of them. It needs two other d2 nodes, so r_2>=3 there. The positive
fan inequality would then give P>=3*2+5*3=21, contradicting P16. Thus no
d2 triangle contains any point of the twelve-point selected support.
This does not assume that the whole selected support is induced.

## The remaining eight d2 triangles have too many common defect neighbors

At any point of a d2 triangle, no d1 triangle is present, because all d1
triangles are wholly in that selected support. Its degree two therefore
requires at least three d2 nodes at the point. The fan inequality P16>=5r_2
permits at most three. Each such point has exactly three d2 nodes forming
a local K3 of defect edges.

Form F2 on the eight d2 actual triangles, joining local defect pairs.
Each node has two distinct partners at each of its three points. No partner
can repeat at a different point by linearity. Hence F2 is a simple
six-regular graph on eight nodes, or K8 minus a perfect matching.

For any adjacent nodes T,U, their F2 neighborhoods have four common nodes:
exclude T,U and their two distinct missing neighbors. Each common node W
forms three actual triangles meeting pairwise. Their intersections cannot
be distinct, so all three must contain the unique intersection point of
T,U. But only one third positive triangle is present at that point, not
four. This contradiction proves the boundary impossible.

## Hand boundaries, overlap and failed extensions

The stars of the cube, or the explicit eight-node cubic graph in the
preserved five-cycle XOR collision paper, give an even eight-triangle
selection in their twelve-point line graph. Such a relation is not forbidden
by parity or local CN1/CN<=2. The present contradiction requires target rook
deficiency degrees and exactly sixteen positive triangles.

The local defect graph consisting of a d1 edge plus a d2 triangle is
graphical, with degrees1,1,2,2,2. It requires fan capacity21 rather than16.
That boundary shows why one cannot forbid d2 incidence on the selected
support independently of the global positive population.

The disjoint-triangle uniqueness step assumes a rook exists containing
the pair; it never asserts that a cross matching or three completions alone
form an induced rook. The even-six step separately proves its inducedness
before using that uniqueness. No additional actual target edges are removed
from the eight-triangle support by assumption.

Even-six and cube-star ingredients overlap earlier rook and binary-incidence
papers, including the September/October3 records and the CP R228 audit.
The new boundary argument combines the cubic-eight edge coverage,
two-triangle rook uniqueness, even symmetric difference and the remaining
degree-two family's point capacity. No novelty conclusion follows from a
bounded repository search. This precise boundary remains CANDIDATE until a
different author reconstructs the labels and all four common-neighbor steps.
R227 and Conway99 remain UNKNOWN, and no execution or registry gate is requested.

# Candidate: the ordinary-support five-d2 branch cannot have two outside points

Root proposed the leaf-root cycle-incidence bound. Structural independently
reconstructed the actual point labels, local deficiency graphs, full cycle
correspondence and each finite inequality below. Agreement is not verification;
a distinct written audit is still required. An independently explored longer
central-root bound was not needed. The earlier Gram, h1 and fourfold papers
remain unchanged. No program, enumeration, solver, import or worker ran.

## Exact statement

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once by their vertex sets, and put d_T=6-r_T for each actual
triangle. Suppose R=227, every d_T belongs to {0,1,2}, and exactly five actual
triangles have deficiency two. Suppose every vertex used by the deficiency-one
triangles lies in exactly two of them; let S be their support. It is impossible
that exactly two outside-S vertices lie in deficiency-two triangles.

The selected multiplicity-two and outside-point conditions are explicit.
This statement alone does not exclude all b5, fourfold support or R227.
No inducedness of S, uniform profile, equitable partition, automorphism,
N3-free premise or literature classification is assumed. Arbitrary other
actual edges are retained until their prohibition is proved from lambda/mu.

## Local triangles, deficiency and the two fans

The target has231 actual triangles, seven through each point, and exactly one
through each edge. Distinct triangles meet at most once. They cannot meet
pairwise at three distinct points, since those three points make an edge have
two triangle partners.

At a point v join two incident triangles by a local defect edge if no actual
induced rook contains them both. The local node T has degree d_T. Indeed
each of its six other incident triangle partners is covered by exactly one
rook or none: two intersecting triangles determine at most one rook, since
their four cross-pair second common neighbors fix the remaining grid. Every
rook through T supplies one partner at v. Thus the local degree is6-r_T.

An external positive triangle meets at most one outer point of an entire
positive fan, by linearity and the distinct-intersection prohibition. A point
with r_1 d1 and r_2 d2 roots therefore needs P>=3r_1+5r_2 positive triangles:
the fan roots themselves and their2r_1+4r_2 distinct external partners.

Double counting gives sum_T d_T=6(231-R)=24. Thus b5 fixes a14 and P19.
The fourteen selected d1 triangles have42 point incidences. The literal
selected multiplicity-two condition gives |S|21 and two selected roots at
each S point.

Each outside-S point lies on at least three d2 roots, because a simple
degree-two local graph needs at least three nodes; the fan19>=5r_2 allows
at most three. If p,q are the stated outside points, their sets of three roots
share exactly one of the five roots: they must share at least one, cannot
share two by linearity, and use all five. Label the actual triangles

    C={p,q,u}, A={p,a1,a2}, B={p,b1,b2},
               D={q,d1,d2}, E={q,e1,e2}.       (1)

All nine displayed S points are distinct. Same-fan repeated points violate
linearity. A cross-fan repeated leaf point would be a second common neighbor
of the adjacent p,q, whose unique common neighbor is u. No leaf point equals
u, again by linearity.

Every selected d1 triangle contains at most one p-neighbor and at most one
q-neighbor among these nine points. Two p-neighbors in a selected actual
triangle would give their edge two triangle partners, the selected third
point and p; the q statement is identical. A selected triangle containing u
contains none of the other eight displayed points, since u is already a
neighbor of both p and q. In particular each d1 root contains at most two
d2-support points; the two selected roots through u contain exactly one.

## Full labeled defect graph and its exact36 four-cycles

Let F have the nineteen positive actual triangles as nodes and local defect
pairs as edges. It is simple, each edge has its unique actual intersection
point as label, and each d1 node has degree3 while each d2 node has degree6.
Its total edge count is36.

The local defect graphs are completely determined here. At p and q they
are K3 on the three d2 roots. At each of the nine displayed S points they
are P3: the one d2 root joins each of the two d1 roots, whose own pair is
covered. At every other S point they are one d1-d1 edge. At other points
they have no positive nodes. Hence no local defect graph has a four-cycle.

Any repeated point label in an F four-cycle forces all four triangles
through that point. For adjacent repetitions, the fourth triangle otherwise
makes a forbidden distinct-intersection triple with two of the first three;
opposite repetitions directly put all four through the same point. Linearity
then forces all labels equal. Such a collapsed cycle is excluded by the
just-listed local graphs. Thus every ordinary F four-cycle has four distinct
actual point labels, which form an induced actual square. A diagonal edge
would already have the two other corners as common neighbors, violating
lambda1.

A square is uncovered by rooks exactly when its corner triangle pairs are
defects. A rook containing one corner pair must contain the opposite square
point fixed by the cross-pair second common neighbor. Conversely a rook
through the square contains those corner pairs. Therefore the maps between
F four-cycles and uncovered actual squares are inverse, with actual labels
preserved.

There are2079 actual induced squares: the4158 nonadjacent vertex pairs each
have their unique two common neighbors and supply the two diagonals of one
square. Each rook contains nine squares, and a square lies in at most one
rook: its four edge-triangle completions and the remaining unique edge
completion fix the nine-set. Consequently

    C4(F)=2079-9*227=36,
    sum_Z c_Z=4*36=144,                        (2)

where c_Z counts F four-cycles through Z. No local collapsed cycle is
counted as an actual square.

## No defect K3,3, codegrees and the fourteen low nodes

A K3,3 of defect edges has six actual triangle nodes and nine intersection
labels. A repeated grid label propagates through cross edges and the
distinct-intersection prohibition until all six roots meet at one point.
They would each have local degree at least3, contrary to max deficiency2.
With nine distinct labels the six roots are the rows and columns of an
actual nine-point rook. Any extra grid-nonneighbor edge has two grid common
neighbors and violates lambda1. Thus the rook is induced, contradicting its
row/column pairs being defects. F has no K3,3 subgraph.

Any two disjoint high triangles have at most three common F neighbors:
their cross edges form a matching of size at most3 (two from one endpoint
would give an adjacent edge a second triangle partner), and each cross edge
has its unique actual completion. Intersecting highs can share a third F
neighbor only at their same point. Here p/q have just three high roots,
so such a pair has at most one common F neighbor. A pair with a low node
has codegree at most3 simply from its degree. Thus all F codegrees are at
most3.

A low node has three F neighbors and at most two high neighbors, by the
d2-support point bound above. Hence it has a low neighbor. It lies on at
most six F four-cycles from its three neighbor pairs, each with at most two
other common neighbors. If it reached six while one neighbor W is low,
the set N_F(W) of size3 would be contained in the neighborhoods of both
other neighbors, making a K3,3. The six nodes are distinct because an F
triangle cannot contain a d1 node: three distinct labels are forbidden,
and a single-point triangle would give it local degree2. Therefore

    c_Z<=5 for every one of the fourteen low nodes.       (3)

## Each of the four leaf high roots has at most12 cycles

At the high root A let L_A be its four low F neighbors, two at a1 and two
at a2. They are distinct since a selected root cannot use two p-neighbors.
They form an independent set in F. At the same A-point their pair is
covered by the local P3; at different A-points any intersection would make
a forbidden distinct-intersection triple with A.

The full neighbor set of A is {C,B} union L_A. Its internal graph has exactly
the edge CB. Neither C nor B can meet any node in L_A: they already meet A
at p, while that low meets A at a1 or a2, so a new intersection would make
three distinct triangle-intersection points. The only other possible high
neighbor of a node of L_A is D or E, at most one of them. Put m_A equal to
the number of those four lows having such a second high neighbor.
Their total low-low neighbor stubs are

    4*2-m_A=8-m_A.                            (4)

No stub ends inside L_A, which is independent. The nodes C and B have
internal-neighbor degree1, and the lows there degree0; thus no node inside
N_F(A) can be the opposite node of a four-cycle through A.

For an opposite high D or E write t_AD or t_AE for its number of neighbors
in L_A. It has the additional common neighbor C with A, so its total is
l=1+t. Codegree<=3 gives t<=2. Every counted low has at most one of D,E
as second high, so t_AD+t_AE=m_A. For t0,1,2,

    binom(1+t,2)<=3t/2.

These two opposite highs therefore contribute at most3m_A/2 cycles.

For an opposite low Z, let I be its number of neighbors among C,B and
x its low-low neighbors in L_A. Here I is0 or1: meeting both intersecting
actual C and B would force their common point p, which is outside S,
or give a forbidden distinct-intersection triple. Its l is I+x.
If I1, its low degree3 leaves at most two low-low neighbors, so x<=2 and
binom(1+x,2)<=3x/2. If I0, x<=3 and
binom(x,2)<=x<=3x/2. Summing x over all opposite lows counts exactly the
stubs in (4). Thus their total cycle contribution is at most
3(8-m_A)/2. Combining both classes gives

    c_A<=3m_A/2+3(8-m_A)/2=12.                 (5)

Every possible opposite node has been included: the only other highs are
D,E, and the remaining nodes are lows. Identical labeled arguments at
B,D,E give the same bound12. No half-integral rounding is needed.

## The common high root has at most20 cycles

The neighbors of C are A,B,D,E and its two low nodes through u. Its internal
neighbor graph consists exactly of AB and DE. Those two lows cannot meet a
leaf high, since a selected root through u contains no other displayed d2
support point, and their own pair is covered at u. As before no internal
node can be an opposite node, because every internal degree is at most1.

For any external opposite node O let l_O=|N_F(O) intersect N_F(C)|<=3.
Counting all external neighbor incidences gives

    sum_O l_O=4*6+2*3-6-2*2=20.

For l0,1,2,3, binom(l,2)<=l. Hence

    c_C<=20.                                  (6)

The two internal edges are subtracted twice, explicitly. No erroneous
global triangle-free assumption removes the allowed two local K3s.

## Contradiction, hand checks and scope

Equations (3),(5),(6) bound the complete cycle incidence by

    sum_Z c_Z<=14*5+4*12+20=138<144,

contradicting (2). This proves precisely the stated multiplicity-two/h2
branch exclusion.

The t2 case gives binom(3,2)=3=3t/2 and the I1/x2 case gives the same
sharp local scalar bound. The I0/x3 case gives3<=9/2, so dropping its
unused slack is conservative. m_A can range0..4 without assuming equal
leaf profiles; the cancellation in (5) holds for every value. No particular
incidence pattern is asserted realizable.

A six-node defect K3,3 with repeated labels cannot be replaced by a generic
abstract graph: local degree3 would be essential and is impossible here.
A six-node even selected family that forms an actual rook is allowed in
general; no generic prohibition of selected K3,3 components is inherited.
Only the defect K3,3 argument above is used.

The square/defect correspondence, codegree and K3,3 mechanisms overlap
earlier R228 and R227 papers and are reconstructed for these exact labels.
The new contribution is the five-high bowtie's four leaf-root12 bound.
Earlier weighted edge ranges and e50 neighbor refinements are not logical
premises. No mathematical execution, broader b5 exclusion, R227 exclusion,
registry action or frozen publication change is claimed.

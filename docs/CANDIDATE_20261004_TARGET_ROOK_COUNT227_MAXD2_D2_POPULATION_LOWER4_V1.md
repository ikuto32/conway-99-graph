# Candidate: at R227, maximum deficiency two requires at least four d2 triangles

This separate written candidate assumes maximum deficiency at most two
explicitly. It does not inherit the unreviewed no-d3 descendant as a theorem.
All previous R227 papers remain unchanged. No mathematical program,
enumeration, import, backend or worker ran. Root requested the exact
conditional statement and challenged concurrency in the three-d2 case.
Different-author written verification is required.

## Exact statement

For every complete finite simple SRG(99,14,1,2), suppose R=227 actual
induced rook-nine vertex subsets occur, counted once by their vertex sets.
Define d_T=6-r_T for each actual triangle, with r_T the number of those
subsets containing T. If every d_T is zero, one or two, then at least
four actual triangles have deficiency two. If b is their number, the
number a of deficiency-one triangles is24-2b.

The maximum-deficiency-two condition is a hypothesis of this statement.
There is no R227 exclusion, graph construction, uniform point profile,
equitable partition, automorphism or induced positive-support assumption.
This does not count collapsed local defect cycles as actual squares.

## Dependency and exact global graph

Only C-UNRESTRICTED-TARGET-NONZERO-ROOK-DEFICIENCY-MAXIMUM-LOWER2 r1 is
inherited, to exclude b0 when total deficiency is positive. The remaining
small-population cycle argument is reconstructed rather than approved
by any older gate.

Each edge has a unique actual triangle partner; each vertex lies in seven
triangles; distinct triangles meet at most once. Three triangles cannot
meet pairwise at three different points, since those points would give
an edge a second triangle partner. At each point v, the simple local
defect graph joins incident triangles if no induced rook contains both;
its node T has degree d_T. Two triangles through v determine at most one
rook by their four cross pairs' unique second common neighbors, justifying
this degree identity.

Double counting six triangles per rook gives D=sum d_T=24. If b<=3,
a=24-2b and the global defect graph F has the positive triangles as nodes,
degrees3 for d1 and6 for d2, and36 edges. A pair can meet at only one point,
so F is simple and each of its edges has that unique actual point as label.
The three local partners of a triangle at different points cannot repeat.

The target has2079 actual induced squares and each rook contains nine.
A square belongs to at most one rook: its four edge triangle completions
and a further unique edge completion fix the nine-subset. Therefore U=36
squares are uncovered. A square's corner triangle pair is a defect exactly
when the square is uncovered: a rook containing that pair must contain
the opposite point fixed by the nonadjacent cross pair's second common
neighbor. No N3-free or literature-classification premise is used.

## Faithful F four-cycles when there are at most three d2 nodes

If two adjacent point labels of an F four-cycle coincide, three actual
triangles contain that point. The fourth must also contain it; otherwise
it and two of those triangles meet pairwise at distinct points. Linearity
then makes all four labels equal. Opposite label coincidence directly
puts all four triangles through one point. All four local degrees would
be at least two, requiring four d2 nodes. This is impossible under b<=3.

Thus all four labels are distinct and form an actual induced square.
Its diagonals cannot be edges because their endpoints already have the
two other corners as common neighbors. Its four corner pairs are defects,
so it is uncovered. Conversely every uncovered square supplies four
distinct edge triangles and their F cycle. Uniqueness of intersection
labels makes the constructions inverse. Consequently

    C4(F)=36,  sum_z c_z=144.                    (1)

A local F triangle is possible among three d2 nodes through one point.
It is not deleted. No F triangle can contain a d1 node, since three
different intersection points are forbidden and a coincident triangle
would give that node local degree at least two.

## No K3,3 and the d1-node cycle contribution

A K3,3 of defect pairs has six actual triangle nodes. If adjacent grid
labels coincide, the other rows must contain the same point, or make
the forbidden distinct-intersection triple with the two columns. Then
the remaining column also contains that point. Opposite label repetition
implies adjacent repetition by a cross edge. Thus any repeated label
would put all six nodes through one point, requiring local degree three,
impossible when every deficiency is at most two.

With nine distinct labels the six actual triangles are the rows and
columns of a rook. Any extra grid-nonneighbor edge has two common
neighbors inside the grid and violates lambda1, so the rook is induced.
Its row/column pairs cannot be defect edges. Hence F has no K3,3 subgraph.

Any two d2 nodes have at most three common F neighbors. If their actual
triangles are disjoint, each common triangle uses a cross edge. Cross
edges form a matching of at most three, and their unique completions
give distinct common triangles. If they intersect, a common F neighbor
must meet them at that same point; otherwise three distinct intersections
are forbidden. That common node must itself be d2, because it has local
degree at least two. With at most three d2 nodes, at most one third node
is possible. Pairs with a d1 member also have codegree at most three,
by its global degree three.

For a d1 node Z, each of its three neighbor pairs has Z and at most two
other common neighbors, so c_Z<=6. If it has a d1 neighbor W and reaches
six, the set N_F(W) of three nodes is contained in each neighbor set of
Z's other two neighbors. This yields a K3,3. Its six nodes are distinct
because an F triangle cannot contain a d1 node. Thus c_Z<=5 unless all
three of its neighbors are d2.

That exception requires b3 and occurs at at most three nodes, by the
common-neighbor bound for any d2 pair. If the d2 graph has any edge,
there is no exception: a d1 node adjacent to all three would make an
F triangle containing d1. Therefore the total d1 contribution is at
most5a+q, with q<=3 only for b3 and an edgeless d2 graph; otherwise q0.

## Root-neighbor mass and internal-edge accounting

Fix a d2 root T with its six F neighbors C. Let k be the number of d2
nodes in C, and a_C count F edges internal to C. The d1 neighbors cannot
participate in an internal edge: at the root point their sole local
defect slots are filled by T; an intersection across different root
points is prohibited by the distinct-intersection triple. Thus internal
edges can only join the two other d2 nodes, and there is at most one.
If that edge occurs, both meet T at the same point, forming the local
d2 triangle. Internal neighbor degrees are at most one, so no internal
node can be the opposite node of a four-cycle through T.

For an external node O let l_O=|N_F(O) intersect C|. By the preceding
codegree bound l_O<=3, including an external d2 node. Direct degree
accounting, retaining the internal edge twice, gives

    B=sum_O l_O=(6-k)*3+k*6-6-2a_C
      =12+3k-2a_C,
    c_T=sum_O binom(l_O,2)<=B.                  (2)

If B is not divisible by three at least one l_O is1 or2, so c_T<=B-1.
This keeps shared incidence edges; it does not count the same internal
edge as two external opportunities.

Let F2 be the graph on the b d2 nodes, with e edges. The sum of k over
those roots is2e. For b3, if e3, all three d2 triangles intersect at
one point: distinct pairwise intersection points are forbidden. Each
root then has a_C=1, so sum a_C=3. Thus the general sum of high bounds
is12b+6e-2 sum a_C. This is not a claim that the global F is triangle-free.

## Complete hand table for b1, b2, b3

The following table lists all possible F2 graphs at these orders. The
three-node path may have its two edges at the same actual point, or at
different points; both share the displayed upper bound.

| b | F2 | a | d1 contribution | d2 contribution | total bound |
|---|---|---:|---:|---:|---:|
|1|isolated|22|110|12|122|
|2|no edge|20|100|24|124|
|2|one edge|20|100|30|130|
|3|no edge|18|93|36|129|
|3|one edge|18|90|42|132|
|3|two-edge path|18|90|48|138|
|3|triangle at one point|18|90|45|135|

The last row improves the loose high bound48 to45: each root has
B=12+6-2=16, not divisible by three, so each c_T<=15. Even the loose
48 would leave138<144; the full residue loss is retained honestly.
Every row contradicts (1). The inherited maximum-lower2 premise
rejects b0, so b>=4 as claimed.

## Boundaries and overlap

Three d2 triangles through one point can form a local K3 and are included,
not rejected as a distinct-intersection triangle. Four d2 nodes through
one point can support a collapsed four-cycle, so the faithful square
map is asserted only for b<=3 and is not transferred to the survivors.

The two-edge path scalar row gives138, not144. No assumption of distinct
path-edge point labels is needed for this table. No actual extra target
edges are removed from the positive support.

The earlier R228 four/five proof already used the seven F2 graphs,
K3,3/codegree argument and B=12+3k-2a_C mechanism. Its D18 table and
path equality stay unchanged. Here the D24 total requires144 and has
six additional d1 nodes in each corresponding row, giving the exact
new conditional threshold. This is disclosed overlap, not a claimed
new general graph theorem or transfer of the old verification gate.

The separately frozen no-d3-at-R227 paper is comparison evidence,
not a logical premise of this maximum-d2-conditional statement. The
separate a8,b8 exclusion also is not used. Combining accepted precise
statements later may leave b4..7; that is not a current R227 exclusion
or an asserted construction of any surviving population. The target
and coverage remain UNKNOWN, and no scientific execution is requested.

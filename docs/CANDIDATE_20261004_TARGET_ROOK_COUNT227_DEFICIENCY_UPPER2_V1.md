# Candidate: every triangle has deficiency at most two when R227

This is a new written candidate, separate from all three preserved R227
population papers. No mathematical program, enumeration, import, backend or
worker ran. Root received the outline and challenged the point labels and
tight residue case. It needs a different-author written audit, outside the
current publication cutoff; agreement does not supply verification.

## Exact statement and dependencies

For every complete finite simple SRG(99,14,1,2), suppose R=227 actual
induced rook-nine vertex subsets occur, counted once by their vertex sets.
For every actual triangle T, put d_T=6-r_T where r_T counts those rooks
containing T. Then every d_T is zero, one or two. No deficiency-three
triangle occurs. This does not exclude R227 or resolve the target.

Use these exact r1 results as explicit premises:

* C-UNRESTRICTED-TARGET-ROOK-DEFICIENCY-STRICT-SECOND-NEIGHBOR-BOUND.
* C-UNRESTRICTED-TARGET-ROOK-COUNT227-DEFICIENCY-POPULATION-TABLE.
* C-UNRESTRICTED-TARGET-ROOK-COUNT227-SINGLE-D3-D2-POPULATION-UPPER2.

The latter two have distinct Native written reports bound to their frozen
statements. They do not approve this new global cycle argument. Their
particular logical use is to leave only c=2,b0/1 and c=1,b0/1/2 as the
possible cases with a positive deficiency-three population. Write a,b,c
for the d1,d2,d3 populations; a+2b+3c=24 and P=a+b+c.

No deficiency-one-only parity is applied with c>0. No equitable point
profile, automorphism, induced positive support, N3-free or literature
classification assumption is used. Arbitrary other target edges remain.

## Global defect graph and actual-square correspondence

At each point the simple local defect graph joins two incident triangles
when no induced rook contains both. Its node T has degree d_T. Let F have
all positive triangles as nodes and these defect pairs as edges, carrying
their unique actual intersection points as labels. It is simple. Each
triangle has d_T partners at each of its three points, and a partner cannot
repeat at a different point by linearity. Thus its global degree is3d_T.
Consequently F has36 edges.

Distinct actual triangles meet at most once. Three cannot meet pairwise
at three different points, since their intersection points would give an
edge a second triangle partner. An F triangle must therefore have all
three labels equal. Such a local triangle requires each node's deficiency
at least two, so no F triangle contains a d1 node. A triangle among high
nodes is permitted in the final nonstar case below and is not discarded.

There are2079 actual induced squares, each in at most one rook, and a rook
contains nine. The unique second-common-neighbor reconstruction fixes any
rook through a square. Thus U=2079-9*227=36 squares are uncovered.

Each ordinary F four-cycle has four distinct point labels. If two adjacent
labels coincided at v, three of its triangles would contain v. The fourth
must also contain v: otherwise it meets the first and third at two different
points and makes the forbidden distinct-intersection triple. All four cycle
labels would then equal v by linearity. Opposite label coincidence already
puts all four triangles through the same point and has the same consequence.
But every node of this collapsed four-cycle would have local degree at
least two; all five population cases have at most three high nodes. This
is impossible. The argument uses local deficiency, not an unproved
triangle-free assumption on the global defect graph.

The four distinct labels form an induced actual square. A diagonal edge
would have its two other corners as common neighbors, contrary to lambda1.
All its corner pairs are defects, so it is uncovered. Conversely the four
distinct edge triangles of an uncovered square make an F four-cycle.
Its corner labels are fixed by their intersections. These maps are inverse,
so ordinary four-cycles, without a selected cycle catalog, satisfy

    C4(F)=36,  sum_z c_z=144,                    (1)

where c_z counts four-cycles through node z. No local collapsed cycle is
silently counted as a square.

## F has no K3,3 subgraph in these cases

Consider six distinct actual triangles forming a K3,3 of defect edges.
If adjacent grid labels coincide, say one row meets two columns at v,
both other rows must also contain v. Otherwise one of them and those two
columns meet pairwise at different points. The third column must then
contain v for the same reason. All six nodes would have local degree
at least three at v, requiring six d3 triangles, while c<=2. Opposite
label repetition implies an adjacent repetition using a cross grid edge.
Therefore all nine grid labels are distinct.

The actual triangles are then the three rows and columns on those nine
points. They give a rook. Any extra edge between grid nonneighbors has
two grid common neighbors and would violate lambda1, so this rook is induced.
Its row/column pairs cannot be defect edges. Hence no K3,3 subgraph exists.
This proof explicitly handles repeated point labels before inducedness.

## Common-neighbor and d1 cycle bounds

Call d2 and d3 nodes high. For any two high actual triangles, their number
of common F neighbors is at most three. If disjoint, every common actual
triangle uses one of their cross edges; those edges form a matching of
size at most three and each has one triangle completion. If they intersect
at v, every common F triangle must also contain v, by the distinct-intersection
prohibition. It then has local degree at least two, so is high. There are
at most three high nodes in total, allowing at most one third node here.
If either member of a pair has deficiency one, its global degree three
gives the same codegree upper bound.

A d1 node Z has three F neighbors. Each pair has Z and at most two other
common neighbors, so c_Z<=6. If it has a d1 neighbor W and attained six,
then for the other two neighbors A,B the three-node set N_F(W) would be
contained in each of N_F(A),N_F(B). This gives a K3,3 on row nodes W,A,B
and column nodes N_F(W). These six nodes are distinct: no F triangle
contains a d1 node. The forbidden K3,3 therefore gives c_Z<=5.

The only potential exceptions have all three neighbors high. They require
three high nodes and lie among common neighbors of any high pair, so their
number q<=3. If the three high nodes intersect at one point, no d1 node
can be such an exception, since its two edges to an intersecting high pair
would require local degree two. Then q=0.

Thus the total d1 cycle contribution is at most5a+q. When there are only
two high nodes q is zero. This argument remains valid when the three high
nodes themselves form a local F triangle.

## Root-neighbor incidence formula, including internal edges

For a high root Z let C=N_F(Z), and let a_C count edges of F inside C.
In every local configuration used below, F[C] is empty or is one edge.
Its maximum internal degree is at most one, so an opposite node of a
four-cycle through Z cannot belong to C: binom(deg_F[C](O),2)=0.

For O outside C and Z put l_O=|N_F(O) intersect C|. It is a common-neighbor
count of Z,O, hence l_O<=3 by the preceding bound. The external incidence is

    B=sum_O l_O=sum_(Y in C) deg_F(Y)-deg_F(Z)-2a_C,
    c_Z=sum_O binom(l_O,2)<=B.                  (2)

If B is not divisible by three, at least one l_O is1 or2, losing at least
one, so c_Z<=B-1. This exact integer loss, rather than a floating estimate,
is essential for the final case.

## Case c=2, b=0 or1

The two d3 triangles are disjoint, and each of their six points has precisely
three d1 triangles and no d2. Reconstruct this local fact as follows.
P=20-b<=20. Two d3 nodes at a point need even r_1; the fan inequality
P>=3r_1+5r_2+7r_3 leaves only (r_1,r_2)=(0,0),(0,1),(2,0).
The first two lack enough nodes for degree three; (3,3,1,1) is nongraphical.
At a single d3 point r_1 is odd. r_1=1 requires r_2>=2, but then fan weight20
exceeds P<=18 when b>=2; r_1>=5 and r_1=3,r_2>=1 exceed20.
Thus every such point is the three-leaf star. This also makes the optional
d2 triangle disjoint from both d3 triangles.

For either d3 root C has nine d1 nodes and no internal edge: same-bucket
d1 nodes have their sole local defect slot filled by the root; different
buckets cannot intersect by the triangle prohibition. Formula (2) gives
B=9*3-9=18, so c_Z<=18.

If b=1, its d2 root has six d1 neighbors and no internal edge for the same
reason. Its B=6*3-6=12 gives c_Z<=12. At b=0 every d1 node has a d1 neighbor;
at b=1 exceptions number at most three. Hence total cycle incidences are
bounded respectively by

    18*5+2*18=126,
    16*5+3+2*18+12=131.

Both are less than the required144. These reject both c=2 rows.

## Case c=1, b=0

There are21 d1 nodes. The d3 root has nine d1 neighbors. At a root point
extra d1 triangles may occur in a separate matching; they are not silently
discarded or assumed root neighbors. Its nine actual defect neighbors still
have no internal F edge, by their filled local slots and the different-bucket
prohibition. Thus B18 and c_root<=18. There are not three high nodes, so q0.
The total cycle contribution is at most21*5+18=123<144.

## Case c=1, b=1

There are19 d1 nodes and one d2 node. Let k=0 or1 indicate whether the two
high nodes are F neighbors. The d3 root has9-k d1 neighbors and k d2
neighbors. Its neighbor graph has no internal edge: a d1 neighbor has
its local slot filled by the root; across root points an internal intersection
is prohibited. The d2 neighbor cannot meet another bucket because it already
meets the root at the first point. Consequently B=18+3k.

The d2 root analogously has6-k d1 neighbors and k d3 neighbors, no internal
edge, and B=12+6k. This does not require the high triangles to be disjoint
when k1. There are only two high nodes, so q0. The total is at most

    19*5+(18+3k)+(12+6k)=125+9k<=134<144.

## Case c=1, b=2 with the d3 triangle disjoint from the d2 triangles

P20 forces the d3 point stars if neither d2 triangle is present there.
The d3 root again has B18. For a d2 root let k indicate whether the other
d2 triangle is its F neighbor. The d3 node cannot be a neighbor because
it is disjoint. Its six neighbors are6-k d1 and k d2, with no internal
edge, giving B=12+3k<=15. The other d2 root has the same upper bound.

Here q<=3, a17, so the total cycle incidence is at most

    17*5+3+18+2*15=136<144.

## Case c=1, b=2: the valid nonstar local boundary

If a d2 triangle meets the d3 triangle, both d2 triangles must be at the
same point v. Precisely one would force r_1>=3 and fan weight21>P20;
two at different d3 points would have that same problem. With two at v,
odd parity and P20 give exactly r_1=1. The local degree sequence is
(3,2,2,1), with its three high nodes forming a triangle and a single d1
leaf attached to the d3 node. This locally valid configuration is retained.
At the other two d3 points there are three d1 leaves each.

The d3 root has seven d1 and two d2 neighbors. Inside its neighbor graph
there is exactly the one edge between the d2 nodes. Thus

    B=7*3+2*6-9-2=22,  c_root<=21.

Each d2 root has four d1 neighbors and the other two high nodes. Its neighbor
graph has exactly the high-high edge at v and no other edge. Therefore

    B=4*3+9+6-6-2=19,  c_root<=18.

These bounds use the nondivisibility losses in (2). The three high nodes
intersect at v, so q0. The total cycle incidence is at most

    17*5+21+18+18=142<144.

Without these losses the loose total would be145 and would not contradict
144. The proof neither deletes the valid local high triangle nor extends
a triangle-free graph formula to it.

## Conclusion, exact hand table and retained boundaries

| c | b | high configuration | d1 bound | high bound | total bound |
|---|---|---|---:|---:|---:|
|2|0|two disjoint d3 stars|90|36|126|
|2|1|two d3 stars and disjoint d2|83|48|131|
|1|0|one d3; extra d1 matches allowed|105|18|123|
|1|1|high edge absent/present|95|30/39|125/134|
|1|2|d3 disjoint from both d2|88|48|136|
|1|2|local high triangle plus d1 leaf|85|57|142|

Every case permitted by the two population premises with c>0 fails (1).
Thus c=0 and max deficiency is two at R227. This is a new necessary
restriction, not an exclusion of R227 or a census of the surviving d2 family.

The local (3,2,2,1) graph is positive as a graph and meets its fan bound
exactly. The contradiction requires full target uncovered-square counts,
not merely local graphical feasibility. An abstract four-cycle on four
degree-two nodes all through one point can collapse; the proof excludes
that behavior here only because every examined population has at most
three high nodes. It is not extended to the surviving c0,b>=4 families.

The R228 four/five paper already used root incidences B and d1/K3,3 cycle
mechanisms. Their overlap is explicit. New ingredients here are allowing
deficiency-three roots, bounding the at-most-three high nodes with actual
labels, and the exact residue losses22->21 and19->18 in the allowed local
high triangle. No older gate approves this statement.

All original R227 statements and reports remain immutable. A different
reviewer must challenge the whole cycle-label map, repeated-label K3,3
argument, high codegrees, internal neighbor edges and the six table rows.
No candidate population is asserted realizable, no target resolution or
scientific coverage is promoted, and no execution/registry action is requested.

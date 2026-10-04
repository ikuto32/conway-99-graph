# Independent derivation of the R228 four-or-five d2 population

Reviewer: /root/checkpoint_audit; producer: /root/structural. The frozen paper
and raw statement were read whole. Only the two declared accepted r1 bounds
are inherited. The preliminary h1..5 proof was independently reconstructed
from local parity and rook geometry as recorded in the separate pattern audit;
it is repeated in the producer paper and is not used here as an unapproved
candidate gate. No mathematical program, graph census, import or solver ran.

Use D18, d in {0,1,2}, p=18-2h and h1..5. Every induced square is covered by
a rook precisely when its two edge-triangles at a corner are rook-covered:
the opposite corner is their unique second common neighbor. The target has
4158 nonedges; each supplies the same square as its other opposite pair, so
2079 squares occur. A square fixes its possible rook uniquely and each rook
has nine. R228 leaves exactly U27 uncovered squares.

Let F be the graph of actual defect pairs on positive triangles. It is simple
and each node has degree 3d, because its three actual points each contribute
d different partners. Thus F has 27 edges. Any F triangle has all three
intersection labels equal: otherwise the three-actual-triangle prohibition
applies. Such nodes all have local degree at least two and must be d2.
This explicitly retains a local triangle on three d2 nodes.

For h <= 3, a four-cycle cannot repeat any intersection label. If two
successive edges use point v, three actual triangles contain v; the fourth
must also contain v, since otherwise it and two of those triangles would
meet pairwise at three different points. Opposite label repetition likewise
puts all four triangles through v. All four would require local degree two,
hence four d2 nodes. Therefore all labels are distinct. They give an induced
square: a proposed diagonal already has two common neighbors. All four corners
are defective. Conversely the four unique edge-triangles of an uncovered
square give that exact F cycle. The constructions are inverse and count
ordinary four-cycles, so C4(F)=27 and the sum of node-cycle incidences is 108.
This argument deliberately stops at h3.

F has no K3,3 subgraph even at h4/h5. An adjacent repeated grid label makes
one row and two columns meet at v. Every other row must also meet v, or it
and those columns give three distinct intersections. A column would then
have three defect partners at v, exceeding d2. A repeated pair of disjoint
grid labels also forces an adjacent repetition through a cross grid edge.
All nine labels must therefore be distinct. The six actual triangles are
the induced rook's rows and columns, and their cross pairs cannot be defects.
This contradiction concerns defective grid edges, not the permitted even-six
rook relation.

Two disjoint actual triangles have at most three common F neighbors. Each
common triangle uses a cross edge of the pair. Such cross edges form a
matching: two incident cross edges would give an edge of the other triangle
a second triangle partner. There are at most three edges, each with one
unique triangle completion. A d1 node Z has its three F neighbors at different
actual points; any two d2 neighbors must be disjoint, or linearity/the
three-intersection prohibition fails. Thus every pair among Z's neighbors
has at most three common F neighbors, including Z, and c_Z <= 6.

If Z has a d1 neighbor W and c_Z=6, each pair involving W has all three
of W's neighbors in common. Those three neighbors and Z's three neighbors
give a K3,3. The two sides cannot overlap: overlap would place a d1 node
on an F triangle. This is forbidden, so c_Z <= 5. An exception requires
all three d2 nodes as neighbors of Z, hence h3. Any one exception shows
the d2 triangles are pairwise disjoint; at most three exceptions occur by
the common-F-neighbor bound. If a d2 edge exists, an exception creates an
F triangle containing Z and is impossible. The d1 sum is therefore 5p,
except for at most three additional incidences in edgeless h3.

For a d2 root T with six neighbors C, let k count d2 neighbors and a count
edges inside C. Under h<=3, an inner edge requires the three d2 nodes in
their permitted one-point triangle; it is then exactly one. No node of C
has two C-neighbors, so C nodes cannot be opposite nodes of a four-cycle
through T. For an external node O let l_O count its C neighbors. A d1 has
l<=3. For an external d2, C contains at most one d2. Two partners at one
actual point would be two same-bucket C triangles, both already defective
to T there; both would need d2. This is impossible. Hence l<=3 here also.

The C-to-outside edges total B=3(6-k)+6k-6-2a=12+3k-2a. Therefore
c_T=sum binom(l_O,2) <= sum l_O=B. Equality needs every l0 or l3; l1/l2
each lose one. In the local d2 triangle branch B16 cannot be a sum of
threes at equality, giving the stronger c_T<=15.

The complete h<=3 table is independently recovered. The d1/d2 incidence
bounds are (80,12), (70,24), (70,30), (63,36), (60,42), (60,48), (60,45)
for respectively h1, h2 edgeless, h2 edge, h3 edgeless, h3 one edge, h3 path,
and h3 local triangle. Their totals are 92,94,100,99,102,108,105. Every row
except the path is strictly below the required 108, including the allowed
local triangle handled by the mod-three loss.

For the remaining d2 path T-U-V, equality forces c_U=18. Its neighbors are
T,V and four d1 nodes with no internal edge. The remaining eight positive
nodes are d1, and equality l0/l3 with sum18 makes exactly six of them active.
Each endpoint has only U among U and its six neighbors, so each needs five
distinct neighbors among those six active nodes. Their two five-subsets
overlap in at least four. A common d1 neighbor forces T,V disjoint by the
actual-point argument above, whereas disjoint triangles have at most three
common F neighbors. Four distinct common neighbors contradict that cap.
Thus h1,2,3 all fail and h is exactly four or five, with p10 or p8.

Boundary challenges: four d2 triangles through a point may make a local
four-cycle with all labels equal; it need not represent a square. No h4/h5
cycle equality was used. Three d2 triangles through one point remain a
legitimate local configuration, handled by B16 rather than a false triangle
prohibition. The scalar path total 108 is not itself a rejection: its failure
uses the exact active-node saturation and cross-matching cap. Extra target
edges and high point multiplicities remain allowed. No global positive
support is assumed induced and no equitable profile is imposed.

PASS for the exact r1 conditional population statement only. R228 itself,
the surviving h4/h5 patterns and target existence remain unresolved.

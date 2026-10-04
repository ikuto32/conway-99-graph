# Candidate: exactly228 rooks forces four or five deficiency-two triangles

This is a separate, stronger written candidate. The earlier pattern paper
3e99eb702f0d5e14ce42008af47f1bb0684ab13de431893f3dfc2edb813f5fd8
and raw c779d998246255d1aa1187c3ff961ff8cdb372caa01b69b56541d7b887277f09
remain unchanged. Root suggested studying the gap-six boundary; Structural
derives the defect-four-cycle restrictions below. No mathematical program,
enumeration, import or solver ran. Different-author verification is required.

## Exact statement

For every complete finite simple SRG(99,14,1,2), suppose that exactly228
actual induced rook-nine vertex subsets occur, counted once. For an actual
triangle T let r_T count those containing T and d_T=6-r_T. Then exactly
four or five actual triangles have deficiency two, exactly ten or eight,
respectively, have deficiency one, and every remaining triangle has
deficiency zero.

This does not exclude R228 or the target. In particular, the ordinary
four-cycle correspondence used below is proved only when there are at
most three deficiency-two triangles. It must not be extended silently
to the surviving four/five-triangle boundary.

## Dependency use, overlap and definitions

The independently reviewed strict second-neighbor bound gives d_T<=2
at R228. The independently reviewed nonempty-maximum-lower2 result gives
some d_T=2. These are the only inherited mathematical results:

- C-UNRESTRICTED-TARGET-ROOK-DEFICIENCY-STRICT-SECOND-NEIGHBOR-BOUND r1.
- C-UNRESTRICTED-TARGET-NONZERO-ROOK-DEFICIENCY-MAXIMUM-LOWER2 r1.

The local defect identities, even-six classification and square count
are reconstructed below. Their overlap with earlier rook papers and
Structural's preserved R228 pattern candidate is explicit. No earlier
gate approves this stronger claim.

Every edge has a unique actual triangle; distinct triangles meet at most
once; three triangles cannot meet pairwise at three different points,
since the three intersections would give an edge two triangle partners.
A vertex belongs to seven actual triangles, so there are231 triangles.

At each point v define the simple graph D_v on its incident triangles,
joining a pair if no induced rook contains both. Two triangles through
v determine at most one rook through the four cross pairs' unique
second common neighbors. Thus degree_Dv(T)=d_T for each v in T.
Counting six triangles per rook gives sum_T d_T=6(231-R)=18.

Write h for the number of d2 triangles, p for the number of d1 triangles.
Then p=18-2h. At every point the d1 triangles have even incidence by
the local handshake identity. A square is uncovered by rooks precisely
when its two edge triangles at any corner form a defect pair. The square
opposite corner is their fixed second common neighbor, so a rook
containing the pair must contain the square. There are2079 squares,
each in at most one rook; each rook has nine. Hence the number of
uncovered squares is U=2079-9*228=27.

## Reconstructed preliminary range h1..5

Choose a d2 triangle T. Its six distinct defect neighbors C are arranged
as two at each of its three points. If k of them have d2, their total
deficiency is K=6+k. At the two outer points of each member of C, all
defect partners lie outside C and T. The twelve outer C points are
distinct: a same-bucket repetition violates linearity and a
different-bucket repetition gives three triangles meeting at different
points.

There are2K outer defect incidences. Any external triangle contributes
at most three. If ell is the number of external d2 triangles, their
positive triangle count is10-k-ell. Therefore
12+2k<=3*(10-k-ell), or3ell+5k<=18. In particular k<=3.
All-d2 support h9 would instead give k6 and is impossible.

A nonempty even-incidence selection of fewer than six actual triangles
cannot occur. Two would need to meet in three points. For four, a
fourfold point leaves eight odd outer points unrepaired; otherwise
all points have multiplicity two and the dual is K4, whose triangle
violates the three-triangle prohibition. Thus h8 or7, giving p2 or4,
is impossible.

An even six-triangle selection is an induced rook: a sixfold point leaves
twelve odd points; a fourfold point leaves eight requiring the other
two triangles' six incidences. All used points therefore have
multiplicity two. The dual is simple cubic triangle-free on six nodes.
The three neighbors of any node must each use the same two remaining
nodes for their other neighbors, giving K3,3. Its nine edge points
give the rook's rows and columns. Extra edges are excluded by lambda1.

If h6 and p6, those six d1 triangles form that rook. At each of its nine
points the two d1 triangles are rook-covered, yet each needs a defect
partner of positive deficiency. It must be d2, since no other d1
triangle contains that point. A different actual triangle meets an
induced rook in at most one point: two adjacent rook points have
their triangle already fixed, and two nonadjacent points cannot be
in a triangle. Six d2 triangles cannot meet all nine required points.
Hence h<=5; the accepted maximum-lower2 result gives h>=1.

## The global defect graph and its faithful cycles when h<=3

Let F have all p+h positive-deficiency actual triangles as nodes.
Join two whenever they form a defect pair at their unique intersection
point, which labels their F edge. F is simple and its node degree is
three times the triangle's deficiency. Thus it has h nodes of degree6,
p nodes of degree3, and27 edges. The three local points of a d1 node
carry exactly one of its three F edges each; a d2 node carries two each.

An F triangle can only have all three actual triangles meeting at a
single point. Three different intersection points are forbidden. Its
three local degrees are at least two, so all its nodes must be d2.
Consequently F triangles are possible only among three d2 nodes;
when h3 and the d2 graph is a triangle, their intersection is one point.

Assume h<=3. Take a four-cycle of F with four distinct nodes. If two
successive edge labels coincide at v, its three successive actual
triangles contain v. The fourth must also contain v: otherwise it
and the first and third triangles meet pairwise at three different
points. With all four through v, all cycle edges have label v by
linearity. Each node would have local degree at least two, requiring
four d2 nodes, contrary to h<=3.

Opposite label repetition likewise puts all four triangles through
one point and has the same contradiction. Thus all four labels are
distinct. They form an actual induced square: each successive pair is
adjacent in its actual triangle, and either diagonal edge would have
two common neighbors, contrary to lambda1. Its four corner pairs are
defects, so it is uncovered.

Conversely an uncovered actual square has four distinct edge triangles,
joined by the four defect corner pairs, giving an F four-cycle.
Unique edge partners and intersection labels make these maps inverse.
Ordinary four-cycles, not only an assumed selected catalog, are counted.
For h<=3,

    C4(F)=U=27,
    sum_z c_z=108,

where c_z is the number of F four-cycles through node z.

## No K3,3 subgraph of F for any maximum deficiency two

Suppose a K3,3 subgraph has its six actual triangles as row/column nodes.
If two adjacent grid edges have the same point v, say row A meets
columns X,Y there, the other two row triangles must also contain v.
Indeed a row not through v meets X and Y at two different points and
would form the forbidden three-triangle configuration with X,Y.
Thus X would have three defect partners at v, contradicting d_X<=2.

No adjacent grid labels can coincide. If two opposite grid labels
coincided, a cross grid edge between their nodes would give an adjacent
coincidence, also impossible. All nine labels are distinct. The six
actual triangles form the rows and columns of an induced rook, since
an extra edge between grid nonneighbors would have two rook common
neighbors. Its row/column pairs cannot be defect edges. Therefore F
has no K3,3 subgraph. This does not require h<=3.

## Common defect neighbors and the d1 cycle bound

A d1 node Z has its three F neighbors at three different actual points.
Any two of its neighbors which are d2 triangles must therefore be
disjoint. An intersection would make those two triangles and Z meet
pairwise at different points, or violate linearity if that intersection
were one of Z's two points.

For any two disjoint actual triangles, common F neighbors number at most
three. Each common triangle meets both, so it uses a cross edge between
them. Such cross edges are a matching of size at most three by lambda1,
and each has one triangle partner. This bound uses actual point geometry,
even when both F nodes have degree6.

Every pair among Z's three F neighbors has at most three common F
neighbors: if one has degree3 this is a degree bound; if both have
degree6 it is the preceding geometric bound. Excluding Z, each pair
therefore contributes at most two four-cycles through Z. Hence c_Z<=6.

If Z has a d1 neighbor W and c_Z=6, W's three F neighbors must all
belong to the neighbor sets of each of Z's other two neighbors.
These two neighbors and W, together with W's three neighbors, form
a K3,3 subgraph, already excluded. Thus c_Z<=5 whenever Z has a d1
neighbor.

The only remaining exception with h<=3 is a d1 node whose three
neighbors are all three d2 nodes, at h3. There are at most three such
exceptions, by the common-neighbor bound for two disjoint actual
triangles. If the d2 graph has any edge, an exception would place a
d1 node on an F triangle, which is impossible. Thus

    sum_(d1 nodes) c_Z <=5p+q,

where q=0 except possibly h3 with an edgeless d2 graph, when q<=3.

## The d2 cycle bound from actual point labels

Fix a d2 node T and let C be its six F neighbors. Write k for its d2
neighbors and a for the number of F edges within C. For h<=3, an
inner edge is possible only between the other two d2 nodes when
those and T make the local d2 triangle. Thus a=1 precisely in that
case, and otherwise a=0.

No node of C contributes a pair of common neighbors with T: any
inner degree is at most one, giving binom(1,2)=0. For a node O outside
C and T, put l_O=|N_F(O) intersect C|. If O is d1, l_O<=3 by degree.
If O is d2, C contains at most one d2 node, since h<=3 and O is external.
Two C partners at one actual point would need both C nodes to be d2:
their common point is a central point of T, and a d1 C node already
uses its single defect edge there to T. Thus O also has at most one
C partner at each of its three points, giving l_O<=3.

The total number of C-to-outside F edges is exactly

    B=sum_O l_O=12+3k-2a.

Counting cycles through T by their opposite node gives
c_T=sum_O binom(l_O,2)<=B. Equality requires every l_O to be0 or3,
since l1 or2 gives a strict loss. In the local d2-triangle case B16
is not divisible by three, so c_T<=15 rather than16.

## Complete small population table

Let e be the number of edges in the graph F2 on the d2 nodes.
The preceding bounds give this table of total four-cycle incidences:

| h | F2 | p | d1 incidence bound | d2 incidence bound | total bound | C4 bound |
|---|---|---:|---:|---:|---:|---:|
|1|one isolated node|16|80|12|92|23|
|2|no edge|14|70|24|94|23|
|2|one edge|14|70|30|100|25|
|3|no edge|12|63|36|99|24|
|3|one edge|12|60|42|102|25|
|3|two-edge path|12|60|48|108|27|
|3|triangle at one point|12|60|45|105|26|

All rows except the path contradict C4(F)=27 immediately. These integer
bounds do not presume F triangle-free in the local triangle row.
That row is retained explicitly and fails by the divisibility loss.

## The two-edge path equality fails through actual triangles

In the remaining row label the d2 path T-U-V with center U.
Equality108 forces c_U=18, because the individual upper bounds
are c_T<=15, c_U<=18, c_V<=15, and all twelve d1 nodes have c<=5.

The six neighbors C of U are T,V and four d1 nodes. There is no inner
edge in C. The eight positive nodes outside C and U are all d1.
Equality at U requires l_O=0 or3 for each; the total sum18 therefore
means exactly six outside d1 nodes have l3 and two have l0.

Both T and V have degree6, with only U as a neighbor among C and U.
Each needs five distinct neighbors among those six active outside d1
nodes. Thus T and V share at least four outside d1 neighbors.
The existence of even one such d1 common neighbor forces the actual
triangles T,V to be disjoint, as proved above. Disjoint triangles
have at most three common F neighbors via their cross matching.
Four distinct ones are impossible. This rejects the last row.

Consequently h1,2,3 cannot occur. Combined with the reconstructed
h1..5 range, h is exactly4 or5, giving p10 or8 as claimed.

## Hand boundaries and failed extensions retained

The nine-point rook has six actual row/column triangles and an ordinary
even binary selection. It is not forbidden; its pairs are nondefective.
The contradiction here forbids a K3,3 made of actual defect edges.

A local D_v triangle on three d2 nodes is allowed by local degree
counting. It must not be called a forbidden three-triangle configuration:
all intersections coincide. It is handled by the table's B16 loss.

At h4, a local D_v four-cycle on four d2 triangle nodes has all four
F edge labels equal v. Four triangles {v,a_i,b_i} with disjoint outer
pairs provide that local labeling boundary; this is not a target or
an actual global rook-deficiency realization. Such a cycle need not
give an actual square. It shows exactly why the proof restricts the
faithful C4 correspondence to h<=3 and supplies no h4 exclusion.

The table's path row attains the scalar108 bound; a numerical or
unlabeled degree count cannot reject it. The contradiction needs
the six active outside nodes and the actual cross-matching cap.
No induced full positive support or automorphism is assumed.

The h4/h5 cases, arbitrary extra target edges and the possibility of
a target with R228 remain. This is a new conditional population
restriction, not a full defect classification, scientific census,
global target contradiction or approval of a future computation.
The weaker h1..5 candidate and every accepted earlier source remain
immutable. A different reviewer must challenge the cycle-label map,
K3,3 label argument, exception bound, seven-row table and path equality.


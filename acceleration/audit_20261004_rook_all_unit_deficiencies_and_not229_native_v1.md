# Independent written challenge: unit rook deficiencies and R=229

Audit writing began at 2026-10-04T16:59:34Z. Native `/root/native_driver` is
the different mathematical reviewer; Structural `/root/structural` authored
both frozen candidates. Root received their discovery outlines and asked for
the multiplicity and point-identification challenges. Shared discovery is
disclosed; it is not a second verification. The final reports separately
record completed written verification time. No graph census, matrix program,
source import, solver, code execution or proof-checking worker is used here.

I independently obtain both exact statements. The first says a complete
SRG(99,14,1,2) with nonzero actual rook deficiency has a triangle of deficiency
at least two. The second excludes exactly R=229. Neither argument forces a
nonzero deficiency, excludes R=231, constructs a target, or approves any
literature-based global exclusion. Empty dependencies are appropriate because
the required local counting and target spectral facts are rederived below.

## Reconstructing the local dictionary

The neighborhood of a vertex is seven disjoint edges: for a neighbor u, the
unique common neighbor of u and v is u's sole neighbor within N(v). Hence
each vertex lies in seven actual triangles, and there are 99*7/3=231 triangle
subsets. Every graph edge has one triangle partner. Two different triangles
share at most one vertex. Three different triangles cannot meet pairwise at
three distinct vertices: those vertices form an additional triangle, giving
an edge two common neighbors. These are consequences of lambda=1, not generic
properties of all linear triple systems.

If triangles T,U share v, their four cross pairs outside v are nonadjacent.
An adjacency would give an edge in T or U a second triangle partner. Each
cross pair has v and its unique second common neighbor. A rook containing T,U
has these four second common neighbors as its opposite grid points. Thus the
pair determines at most one actual nine-subset. A rook containing T gives one
different companion triangle at each of T's vertices. Consequently at any
v in T exactly r_T of its six companions are covered and 6-r_T=d_T are defect
partners. In particular d_T is a nonnegative integer, the same local degree
at all three vertices of T. Counting six triangles per rook gives

    D = sum_T d_T = 6*231 - 6R = 6(231-R).

A target square has two nonadjacent opposite pairs, each with exactly two
common neighbors. There are 99*(98-14)/2=4158 nonedges, and each square is
counted by both diagonals, giving 2079 squares. A rook has nine squares.
For the two edge triangles at a specified corner of a square, a rook
containing them must contain the opposite corner: it is the unique second
common neighbor of the two adjacent square vertices. Conversely a rook
containing the square contains those edge triangles, because triangle partners
are unique. Its corner triangle pair determines at most one rook. Therefore
the nine-square sets of distinct actual rooks are disjoint. The uncovered
square count is

    U = 2079 - 9R = 3D/2.

Every corner pair of an uncovered square is a defect pair. This statement is
at every corner, not merely an existential choice of one defective corner.

## A global defect graph that does not assume point multiplicity two

Assume D>0 and every positive d_T equals one. At each actual point v the local
defect graph has degrees zero or one; its positive nodes form a matching.
Build F on the D positive triangle subsets. Give it an edge for each actual
defect triangle pair, remembering the actual intersection point as that
edge's label. Linearity forbids two edges on the same pair, and no triangle
is its own partner. F is simple. Each triangle has one partner at each of
its three points, and these partners are distinct. It is cubic.

At a node, its three F-edge labels are distinct points. An F triangle would
therefore be three actual triangles meeting at three distinct points, already
forbidden. F is triangle-free. Edges having no common F node may still have
the same actual point label. This construction deliberately allows positive
point multiplicities four or six and makes no support-inducedness assumption.

Consider an F four-cycle T1,T2,T3,T4. Its successive intersection labels
v12,v23,v34,v41 are distinct when consecutive, since a triangle has only one
defect partner at each point. They are distinct when opposite too. If v12=v34,
all four triangles contain that point; T2,T3 already meet there, so their
intersection v23 must be that point by linearity, contradicting the preceding
distinctness. The other opposite equality is excluded identically.

The four distinct labels form a graph four-cycle since successive labels
belong to an actual triangle. Neither diagonal can be an edge: it already has
the other two corners as common neighbors, contradicting lambda=1. At every
corner the two actual edge triangles are precisely its F defect pair, so
this is an uncovered target square.

In the reverse direction, the four actual edge triangles of an uncovered
square are distinct. Adjacent edge triangles cannot coincide, since that
would insert a square diagonal. Opposite edges cannot belong to a single
three-point triangle, since they have four distinct endpoints. They are
positive and their four corner defect pairs are F edges. Thus they give an F
four-cycle. Linearity and the unique edge partners show the two constructions
are inverse. They count cycles and squares once, without orientation factors:

    C4(F) = U = 3D/2.

An extra target edge elsewhere in the support does not affect this bijection.
An extra diagonal in a mapped square is specifically excluded by lambda=1.
We do not identify F with a line-graph dual based on multiplicity two.

## Sharp cubic equality and the nine distinct actual points

A vertex of a simple cubic triangle-free graph has three neighbor pairs.
Each pair has that vertex and at most two further common neighbors, because
either neighbor has degree three. It lies in at most six four-cycles. Counting
each cycle at four vertices gives C4(F)<=6D/4=3D/2.

Our forced equality makes every one of these local inequalities sharp. At
any vertex v with neighbors x,y,z, all three pairs have three common neighbors.
Their full three-element neighbor sets are equal; write that set {v,p,q}.
It is disjoint from {x,y,z}; a common element there would create a loop or
triangle. Every point in these two sets has its full degree within their
K3,3. Hence it is a connected component. Repeating at every node shows that
all components are K3,3. No connected catalog or graph enumeration is used.

In a K3,3 component label its triangle nodes a,b,c on one side and x,y,z on
the other. Its nine edge labels are nine distinct actual points. Edges sharing
a node have distinct labels. If disjoint edges (a,x),(b,y) had the same label
v, all four actual triangles contain v. The existing cross edge (a,y) is
their unique intersection v, giving a two defect partners x,y at the same
point. This contradicts the local matching. Thus even disjoint edge labels
cannot coincide in this component.

Each of the six actual triangles uses exactly its three incident edge labels;
they form the three rows and three columns of a nine-point grid. It is an
induced rook. Any additional edge between different rows and columns already
has the two alternate grid corners as common neighbors, contradicting lambda=1.
Every component edge is consequently a pair of actual triangles together
in a rook, contrary to the definition of F. This contradiction proves the
nonzero-deficiency maximum-at-least-two statement. D=0 yields an empty F and
is not contradicted.

## Independent R=229 reduction, without borrowing an old gate

Suppose R=229, so D=12 and U=18. Fix a triangle T with deficiency m>0.
It has m defect companions at each of its three points; the three buckets
are disjoint and contain 3m triangles. Let their total deficiency be K>=3m.
Each bucket triangle supplies d_U defect partners at each of its two outer
points. The resulting 2K incidences go to triangles outside T and all buckets:
an intersection with T or another bucket would violate linearity or the
three-triangle prohibition. A further partner meets at most one triangle
from each bucket. Hence at least ceil(2K/3) further positive triangles occur,
and

    12 = D >= m+K+ceil(2K/3) >= 6m.

Thus m<=2. If m=2, equality holds throughout. The six bucket companions and
four further triangles all have deficiency one; there are no other positive
triangles. The twelve outer points are distinct. Each further triangle has
one point in each bucket. Each bucket's two companions give a perfect matching
on the four further-triangle nodes.

The edge union on the three central and twelve outer points is induced. To
derive this, A^2=12I-A+2J and Aj=14j give eigenvalues 3 and -4 on j-perp, so
Q=3I-A+J/9 is positive semidefinite. Give the central points weight two and
the outer points weight one. The sum is 18 and squared norm 24. Triangle edge
products are 12 for T, 6*5=30 for the bucket triangles and 4*3=12 for further
triangles, total 54. The specified edge union has Q quadratic value
3*24-2*54+18^2/9=0. An additional positive-support edge would decrease it
strictly, contradicting positive semidefiniteness. This is not a general
assumption of support inducedness.

All corners of every uncovered square are on positive triangles, hence in this
15-point induced support. Its complete nonadjacent-pair classification gives
12 squares from the 24 central/other-bucket pairs, plus one square per common
edge of each pair of bucket matchings. Same-bucket unmatched outer pairs have
only their center as common neighbor; same further-node outer pairs are
adjacent. For different buckets and different nodes, two common neighbors
occur exactly when that node pair belongs to both matchings. Each shared
matching edge produces two opposite pairs and hence one square.

The perfect matchings on four nodes are {12,34},{13,24},{14,23}. The sum of
pairwise intersection sizes is 6,2 or 0 according as three matchings all
coincide, exactly two coincide, or are all different. Thus the support has
18,14 or 12 squares. Since all U=18 uncovered squares must occur there, all
matchings coincide. T, the two further triangles of either common matched
pair and the three corresponding bucket triangles are the rows and columns
of an actual rook through a designated defect pair. This is impossible.
Therefore m=2 is excluded; every positive deficiency is one. The independent
global defect-graph contradiction just proved then excludes R=229.

## Challenging the original R229 fan and line-graph proof too

The original proof's alternative route is also sound. With twelve d1 triangles,
at every point positive incidence is even. If a point is in r such triangles,
their 2r fan points are distinct. A positive triangle not through the center
uses at most one fan point: two points in the same fan triangle violate
linearity; two in different fan triangles violate the three-triangle rule.
Even incidence requires every fan point to be covered again, so 12-r>=2r.
This excludes r=6, while allowing r=4 at this stage.

For r=4 all eight remaining triangles use exactly one fan point. No additional
fan point may lie in one of their two remaining positions, by the same bound.
A new point on q of these triangles has q distinct fan points as common
neighbors with the center. Its even positive incidence and q<=2 force q=2;
it is not adjacent to the center, because an adjacency permits only one common
neighbor. The sixteen new incidences give eight new points, with a simple
two-regular graph whose eight triangle edges carry fan-color labels.

Two incident colors are different. If they were the same, their two triangles
and the associated fan triangle meet at three different points. If different
colors were rook-covered at the center, the rook would contain the two fan
points and their fixed second common neighbor, this new point. Unique triangle
partners then put their remaining triangle and the fan triangle together in
that rook. Those are the two positive triangles through the fan point and
must instead be a defect pair. Thus incident colors are a defect pair at the
center. Its four colors are matched in two pairs. Each pair has four edges
and forces an alternating four-cycle, giving two disjoint cycles. Each cycle
and its two fan triangles produce the explicit nine-grid in the source paper;
lambda=1 excludes extra grid edges. This contradicts their central defect
pair. Point multiplicity two is therefore derived only after excluding six
and four.

With that derived condition the original cubic dual on twelve triangle nodes
is valid. Its selected edge union is a line graph, but need not be globally
induced. Uncovered square edges nevertheless all belong to the selected union
because each corner's unique defect pair consists of its two positive triangles.
Conversely its induced squares cannot acquire target diagonals. Their exact
count is 18. Cubic saturation again forces two K3,3 components and the forbidden
rooks. The extra-edge limitation is correctly handled; it is not waived.

## Written falsification boundaries and exact scope

Two rooks joined at a point give an even triangle selection with multiplicity
four. This defeats any unconditional claim that an even selection has only
multiplicity two. It does not defeat either candidate: its relevant pairs are
rook-covered and fail the d1 defect premise. Two abstract K3,3 components meet
the cubic bound with 18 squares; their rook realizations similarly contradict
the required defect labels. A hexagonal prism has six rectangular squares,
strictly below the 18 required for a twelve-node cubic equality. Cubic and
triangle-free alone are therefore insufficient.

A triangle-free cycle graph can have no four-cycles; an arbitrary cubic graph
can have fewer than the upper bound. The step forcing equality is the exact
uncovered-square bijection under the actual target defect premise. None of
these abstract examples is promoted to a complete SRG99 or an executed test.

The previous Native strict-mass audit provides comparison history, but this
audit rederives the D12 equality needed here. Local squares, six-triangle rook
reconstructions and cubic terminology overlap preserved papers. There is no
novelty assertion, cited theorem approval, archived census import or gate
transfer. The all-d1 argument is stronger than the R229-specific fan route,
and its strength comes from faithfully labeling defect edges, not imposing
uniform positive-support geometry.

The two exact raw statements survive. This audit does not infer R231 exclusion
or target nonexistence. Combining the separately verified strict mass inequality
with the new maximum-two fact would exclude additional near-top counts; such a
combination is not silently inserted in either report. Original source bytes,
candidate scopes, live ledger, index and Git state remain untouched.

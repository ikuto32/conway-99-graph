# Candidate: four d2 triangles cannot share a point at R227

This is a separate written boundary argument. Root proposed the saturated
four-d2 fan and its two opposite-pair rooks; Structural reconstructed the
labelled outside array and the complete defect-cycle count. The earlier R227
candidates remain unchanged. No mathematical program, enumeration, import,
backend or worker ran. Different-author written verification is required.

## Exact statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
nine-vertex rook subsets once by their vertex sets, and put d_T=6-r_T for
each actual triangle T, where r_T counts the rooks containing it. Suppose
R=227, every d_T belongs to {0,1,2}, and exactly four actual triangles have
deficiency two. Then those four triangles do not all contain one vertex.

The maximum-deficiency-two condition and the four-d2 population are explicit
hypotheses. This does not exclude every four-d2 population, R227, or the target.
No equitable profile, graph automorphism, induced positive-support assumption
or equality of arbitrary row and column matchings is imposed.

## Local geometry and the exact square count

Every edge has its unique actual triangle partner. Each vertex lies in seven
triangles. Distinct actual triangles meet at most once; three cannot meet
pairwise at three distinct points, because those three intersection points
would give one edge a second triangle partner.

Two intersecting actual triangles determine at most one induced rook: their
four cross pairs' unique second common neighbors fix its four opposite grid
points. At each point v define a simple local defect graph on the seven actual
triangles through v. A pair is joined if no rook contains both. Its degree
at T is d_T: each rook containing T supplies exactly one covered partner
through v, and pair uniqueness makes those r_T partners distinct.

The global defect graph F has positive-deficiency triangles as nodes, with
one edge for every such defect pair. An edge is labelled by the pair's
unique intersection point. A node T has degree 3d_T, since its three local
partner sets cannot repeat by linearity.

There are231 actual triangles and each rook contains six, so

    D=sum_T d_T=6(231-R)=24.

Under the stated hypothesis the d1 population is16, the total positive
population P is20, and F has36 edges. The target has4158 nonadjacent pairs.
Their two common neighbors give one induced square per pair, and every
square has two opposite pairs; thus there are2079 induced squares. Each
rook has nine. A square is contained in at most one rook, since its two
edge triangles at a corner already determine that rook. Therefore

    U=2079-9*227=36                              (1)

actual squares are uncovered. A square's corner triangle pair is a defect
precisely when the square is uncovered: a rook containing that pair must
contain the opposite point fixed by its cross pair's second common neighbor.

## The saturated point fan

Assume for contradiction that all four d2 triangles contain v. For any
positive triangle through v, each of its two outer points needs d_T external
defect partners. An external actual triangle can meet at most one outer
point of the entire v fan: meeting two from one fan triangle violates
linearity; meeting points on two fan triangles makes the forbidden three
distinct intersections. Defect partners have positive deficiency. Hence
if r_i positive triangles of deficiency i pass through v,

    P>=3r_1+5r_2.

Here P=20 and r_2=4, so r_1=0 and equality holds. The four d2 nodes in the
local defect graph have degree two; all other nodes have degree zero.
Their graph is a four-cycle. Label it

    A -- B -- C -- D -- A.

The opposite pairs A,C and B,D are covered by induced rooks S1 and S2,
respectively. The eight outer points of these four triangles are distinct.
At each such point, its d2 triangle requires two external defect partners.
The sixteen remaining positive triangles are all d1. Saturation forces
each to supply exactly one of the sixteen required outer defect incidences.
Consequently each outer point has exactly two attached d1 triangles; they
are its d2 root's two defect partners. There are no other positive triangles
through that point. No d1 triangle contains v.

Let the two outer points of A and of C together form a four-point set X,
and let the outer points of B and D form a four-point set Y. Both sets have
their distinguished two-by-two partition into the actual d2 roots.

## The two rooks separate every remaining positive point

For any induced rook S, an outside vertex meets S at most once. Any two
vertices of S already have all their required common neighbors inside S,
so an outside vertex adjacent to both would violate lambda1 or mu2.
There are9*(14-4)=90 boundary edges and90 outside vertices. Thus every
outside vertex meets S exactly once. This reconstructs the historical
rook regular-set property; no current ancestor gate is substituted for it.

S1 contains v, X and four opposite grid points; S2 contains v, Y and four
opposite grid points. An X point is outside S2: its edge to v has actual
triangle A or C, whereas the two S2 triangles through v are B and D.
It already has its unique S2 neighbor v. Each opposite grid point of S1
is adjacent to two X points, so it cannot belong to S2. The symmetric
argument proves

    S1 intersect S2={v}.

In particular no X point is adjacent to a Y point. A d1 triangle attached
at x in X cannot contain another S1 point: if it did, uniqueness of the
edge's triangle partner would put the whole triangle in S1, making its
pair with its d2 root covered rather than defective. Nor can it contain
an S2 point, since x already has its S2 neighbor v. It cannot contain v
by linearity with its root. Its other two points are therefore outside
S1 union S2. The analogous statement holds for every Y-attached triangle.

## An exact four-by-four array, without a uniform matching premise

At each point the sum of local defect degrees is even. Outside the fan
there are no d2 triangles, so the number of incident d1 triangles is even.
Take an outer point z of an X-attached d1 triangle. A second d1 triangle
must contain z. It cannot be attached at the same x, since the two triangles
would share x and z. It cannot be attached at another X point, since z
would then have two S1 neighbors. It must be attached at a Y point y.
The same one-neighbor argument allows at most one triangle of each family.
Thus every such z belongs to exactly one X-attached and one Y-attached d1
triangle. It has unique S1 neighbor x and unique S2 neighbor y.

There are32 outer incidences from sixteen d1 triangles, so there are sixteen
such distinct points. Each has a label pair (x,y) in X times Y. Two points
with the same pair would give the nonadjacent pair x,y three common neighbors
(v and those two points), violating mu2. Hence the labels give a bijection
with all sixteen pairs. Write these points Z_xy. This also agrees with
the unique second common neighbor of x,y besides v.

For each x its four Z_xy points are paired by its two attached d1 triangles.
For each y its four Z_xy points are paired by its two attached d1 triangles.
These are arbitrary perfect matchings, respectively on Y and on X.
Their equality or preservation of the root partitions has not been assumed.
All sixteen actual d1 triangles are exactly these eight row and eight
column triangles. Every Z_xy is incident with its one row and one column
triangle, which are a defect pair because both have local degree one there.

## Complete cycle count, with the collapsed local cycle retained

Let F1 be the d1-only subgraph of F. Its row nodes and column nodes form
a bipartition. Every Z_xy is one of its sixteen edges. Each d1 triangle
has two such neighbors and its one d2 root neighbor, so F1 is a simple
two-regular bipartite graph on sixteen nodes. It is a union of even cycles
of length at least four. Let q count its four-cycle components; q<=4.

The four d2 nodes form the displayed high-node cycle at v, and these are
their only mutual intersections. Each d1 node has exactly one high neighbor.
If a four-cycle of F has repeated point labels, the forbidden distinct
intersection triple forces all four triangles through one point. Each
would then need local degree at least two. It must consist of the four
d2 nodes, and is exactly the one cycle at v. Every other F four-cycle has
four distinct labels, giving an actual induced square whose corner pairs
are defects. Conversely every uncovered square gives this faithful F cycle.
Thus the collapsed cycle is retained, and the number of all other cycles
is the U=36 in (1).

Let K be the number of row or column matching edges whose two attachment
labels lie in the same d2 root. There are sixteen matching edges in total,
one per d1 triangle, so K<=16. The complete classification of F four-cycles
is as follows.

| Number of d2 nodes | Cycles | Reason |
|---|---:|---|
|4|1|The unique local cycle at v; collapsed, not an actual square.|
|3|0|A d1 node has only one d2 neighbor.|
|2|16|Each F1 edge has its two different roots in X and Y, which are adjacent high nodes.|
|1|K|The opposite d1 node's matching joins two attachment labels belonging to this high root.|
|0|q|Exactly the four-cycle components of F1.|

For the two-high row, the high nodes must be consecutive; an alternating
high/low cycle would require a low node with two high neighbors. Each F1
edge gives exactly one consecutive-high cycle, and every such cycle uses
that unique F1 edge. For the one-high row, the middle d1 node has degree
two in F1; its two neighbors have the same root exactly when its matching
edge is counted in K. The labels are distinct, so these are genuine cycles.
This identifies all cases without discarding arbitrary extra actual edges.

Removing the one collapsed cycle gives

    36=16+K+q,  K<=16,  q<=4.

Equality forces K=16 and q=4. In particular every row matching pairs the
two B points together and the two D points together. Every column matching
pairs the two A points together and the two C points together. This root
preservation is a conclusion of the exact count, not a uniformity premise.

## The forced nine-point rook contradicts an actual defect edge

Choose any I in {A,C} and J in {B,D}; they are adjacent nodes of the local
defect cycle. Write their two outer points as x1,x2 and y1,y2. The nine
distinct points

    v, x1, x2, y1, y2,
    Z_x1y1, Z_x1y2, Z_x2y1, Z_x2y2

now have the six actual triples of a rook grid: I and J, the two row
triangles at x1,x2, and the two column triangles at y1,y2. Their required
row and column edges all exist. Any additional edge between grid
nonneighbors would have two known common neighbors inside the grid and
violate lambda1 for that edge. Therefore this is an induced rook containing
I and J. That contradicts their actual defect edge at v and proves the
exact statement.

## Hand counter-controls and scope limits

Four degree-two nodes may form a local C4. The proof does not reject this
local graph on degree grounds; it uses the global saturated fan, two actual
opposite-pair rooks and the exact square count. A d1-containing local C4 is
impossible by its local degree one, which is why only one collapse occurs.

The arbitrary row/column matching stage permits root-crossing matchings.
They reduce K and fail the required U=36 count; they are not silently
relabelled into root-preserving matchings. The all-root-preserving abstract
defect graph really has one high cycle, sixteen two-high cycles, sixteen
one-high cycles and four low cycles, or37 in total. It is not excluded by
that abstract graph count alone. Its forbidden actual induced rook is the
essential final geometric obstruction. This distinguishes a graph-only
counter-control from a valid target extension.

The equality does not state that every point of the target has this array
profile. The array contains only the forced outer points of the sixteen
positive d1 triangles. All other target vertices and edges are retained,
and all inducedness conclusions use exact lambda1 saturation explicitly.

The historical rook regular-set one-neighbor proof, the earlier faithful
defect-cycle map, parity and fan inequality are disclosed shared ingredients.
The new boundary combines them at P20 with a complete matching-sensitive
cycle classification and a labelled nine-point obstruction. No novelty
claim follows from a bounded archive comparison. The separate max-d2 and
minimum-b candidates are not inherited as theorems here: those conditions
are literal hypotheses. Nonconcurrent b4 and all other R227 populations
remain unresolved. This is a CANDIDATE, outside the frozen publication
cutoff, until a different author reconstructs the whole proof.

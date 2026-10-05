# Independent written challenge of four concurrent D2 roots at R227

Verification timestamp: 2026-10-04T19:39:35.1785776Z.
Mathematical producer /root/structural; independent verifier /root/native_driver.
Root shared the saturated-fan idea and challenged the producer outline.
Structural wrote the labelled array and cycle argument. Those shared
mechanisms are disclosed; agreement is not independent verification.

Exact claim C-UNRESTRICTED-TARGET-ROOK-COUNT227-NO-FOUR-D2-COMMON-POINT r1.
The whole frozen paper19484aab2a31ba6cec339a2c1cdcb0b23a007963453ee38e459741067cb73e17
and raw30274bd4c488ab15f50c10b45a274afd4710a751a7a68f3b40bfd4db8f07b8b7
were read. No mathematical code, import, AST/syntax check, solver, backend,
census or computational worker was used. No ledger parse, Git/index or
publication mutation occurred; this is separate next-wave47 evidence.

## Scope: only the literal common-point boundary

Take a complete finite simple SRG(99,14,1,2). Count actual induced rook-nine
vertex subsets once, with R227; put d_T=6-r_T. ASSUME every d_T is0,1,2
and exactly four actual triangles have d2. For contradiction ASSUME those
four share one actual point v. These are explicit hypotheses, not inherited
no-D3/population theorems. The logical dependency list is empty. Earlier
conditional papers are comparison evidence only, and no current registry
presence or approval transfer is assumed.

Every edge has its unique actual triangle partner. Triangles meet at most
once; three cannot meet pairwise at three distinct points, since those
points would make an edge have a second triangle partner. Each vertex has
seven incident triangles. An intersecting triangle pair determines any
containing induced rook through its four opposite cross pairs' unique
second common neighbors. Thus at each point, the simple defect graph on
its seven triangles has node degree d_T, where an edge means no containing
rook for that pair. Covered partners supplied by the r_T rooks are distinct.
Zero-degree nodes cannot partner in a defect edge.

There are99*14/6=231 actual triangles and6 per rook. Hence total deficiency
D=6(231-227)=24, d1 count16, positive countP20. The global defect graph F
on these20 triangles has node degree3d_T, because partners at different
points of T cannot repeat by linearity. It is simple, with36 edges, carrying
their unique actual intersection points as labels.

Nonadjacent vertex pairs number4158, each with two nonadjacent common
neighbors (adjacency of those two would violate lambda1). Their induced
squares are counted twice, giving2079. Every actual rook has9 squares; a
square corner-triangle pair fixes any containing rook, so no square lies
in two rooks. There are U=2079-9*227=36 uncovered squares. A square corner
pair is covered exactly when the square is covered, by the unique second
common neighbor for its opposite point. No N3-free condition is used.

## Saturation gives exactly sixteen distinct outside low triangles

At v let r1,r2 count positive incident triangles. Their outer points are
all distinct by linearity. Each of the two outer points of a di triangle
needs i other positive triangle defect partners. An external triangle
meets at mostone outer point of the entire fan: two from one triangle
violate linearity; two from different triangles yield the forbidden
distinct-intersection triple with v. Therefore

    P >= 3r1+5r2.

Here r2=4,P20, so r1=0 and equality holds. The four high nodes at v each
have degree2 on themselves; no zero node is a defect partner. A simple
two-regular graph on four nodes is the four-cycle A-B-C-D-A. The opposite
pairs A,C and B,D are nondefect pairs, so actual containing rooks S1,S2
exist. This is existence for these pairs by definition, not existence for
an arbitrary matching or completion list.

There are eight outer fan points. At each its high triangle requires two
external defect partners, giving16 required incidences. Exactly16 other
positive triangles exist, all d1 and none through v. Each can supply at
mostone fan incidence, so equality forces a one-to-one assignment: every
d1 is attached at exactlyone outer point, and every outer point has exactly
two such attached defect partners. There is no room for any additional
positive incidence at an outer point, even a nondefective one. If a d1
were not used, the required16 incidences could not be covered by the others.

Let X be the four outer points of A,C, with their two distinguished root
pairs, and Y the four outer points of B,D with its root pairs. Eight d1
triangles attach to X and eight to Y, all sixteen distinct.

## Direct outside-one-neighbor proof separates the two actual rooks

Any pair of vertices in an induced rook already has all required target
common neighbors inside it:1 if adjacent,2 if nonadjacent. An outside
vertex cannot neighbor two rook vertices. There are9*(14-4)=90 boundary
edges and90 outside vertices. At mostone neighbor therefore becomes
exactlyone for every outside vertex. This is independently rederived from
the complete target, not imported from a historical computational gate.

S1 contains v,X and its four opposite grid points. S2 contains v,Y and
four others. If x in X were in S2, its edge vx would have its third
triangle point in S2. Its actual root A or C would then be one of S2's
two triangles through v, but those are B,D. Contradiction. Thus every X
point is outside S2 and already has its sole S2 neighbor v. An opposite
grid point of S1 is adjacent to two X points; it cannot belong to S2,
since either of those X points would gain a second S2 neighbor. The same
argument with the roles reversed gives S1 intersect S2={v}. In particular
no x in X is adjacent to y in Y.

Take a d1 triangle attached to x in X. Its other two vertices cannot
include another S1 vertex: an edge internal to the induced rook has its
unique third triangle point inside S1, putting the whole triangle there.
Then S1 would cover its pair with its high root, contrary to its actual
attachment defect. It cannot include an S2 point, since x's unique S2
neighbor is v; v itself is forbidden by linearity with the high root.
Its two remaining points are therefore outside S1 union S2. The symmetric
statement holds for every Y-attached d1 triangle. No whole positive support
or union of these rooks is asserted induced beyond the two actual rooks.

## Parity and mu2 give a labelled 4-by-4 array with arbitrary matchings

At any remaining outer point z, no high triangle occurs, since all four
high triangles consist of v and fan points. Local handshake says the
number of positive d1 triangles there is even. Starting from an X-attached
one, a second d1 must occur. Two with the same X attachment would share
x,z, violating linearity. Two with different X attachments would give z
two S1 neighbors. Thus at mostone X-attached triangle occurs, and the
second must be Y-attached. The same S2 and linearity argument gives at
mostone Y-attached triangle. Hence exactlytwo d1 triangles occur at z,
one of each family, and they are a local defect pair of degrees1,1.

The16 d1 triangles give32 outer incidences. Exactlytwo occur at each point,
so there are16 distinct z points outside S1 union S2. Each has its unique
S1 neighbor x and S2 neighbor y, supplying a label (x,y) in X times Y.
If two different z shared the same label, the nonadjacent pair x,y would
have common neighbors v,z1,z2, contradicting mu2. Thus labels inject into
16 possible pairs and are bijective. Call the points Z_xy; they are exactly
the second common neighbors of x,y after v.

At fixed x its four Z_xy points are partitioned by its two actual attached
d1 triangles. This is an arbitrary perfect matching on four Y labels.
At fixed y its four Z_xy similarly give an arbitrary perfect matching on
X. Each four-label set has three possible pairings; no pairing is preferred,
no row/column matching equality or root-preservation is assumed. The16
actual d1 triangles are exactly eight row and eight column triples.

Their graph F1 is bipartite by row/column family. Each Z_xy supplies one
edge. Distinct actual triangles cannot share two Z points, so F1 is simple,
not a multigraph. Each low node has two distinct F1 neighbors and exactly
one high neighbor, its attachment root. Thus F1 is2-regular on16 nodes,
with16 edges, a union of even cycles of length at least4. Its number q
of four-cycle components is at most4. Longer components are not discarded.

## Exact cycle decomposition includes one collapse

For an ordinary F4cycle with repeated labels, adjacent coincidence forces
all four actual triangles through one point by the forbidden intersection
triple; opposite coincidence has the same effect. Every local cycle node
then has defect degree at least2, so it must consist of the four high
triangles. They meet at v and have no other common point. Their mutual
defect graph is exactly C4, producing exactlyone collapsed cycle. All
other ordinary F4cycles have four distinct labels, giving faithful induced
uncovered squares. Every uncovered actual square gives the inverse F4cycle.
Hence the count of all cycles other than that single collapse is36.

Classify all cycles by the number h of high nodes:

| h | count | independent identification |
|---|---:|---|
|4|1|The local C4 at v, collapsed.|
|3|0|Its sole low node would have two different high neighbors.|
|2|16|High nodes must be consecutive; each unique F1 edge gives its cycle.|
|1|K|The opposite low node's two attachment labels lie in this root pair.|
|0|q|Exactly the four-cycle components of the2-regular F1.|

For h2, an alternating cycle would give a low node two high neighbors.
With the highs consecutive, the two lows give an F1 edge. Every F1 edge
joins an X-attached row node with a Y-attached column node. Their roots
are respectively in{A,C} and{B,D}, which are adjacent in the local high
C4. This yields exactlyone cycle per F1 edge, all16, with distinct actual
labels v,x,Z_xy,y. Conversely its unique F1 edge recovers any such cycle.

For h1, the opposite low node has exactlytwo F1 neighbors. The cycle closes
through a high root precisely when those neighbors have that same attachment
root. If the opposite low is a row triple, its matching edge pairs two Y
attachment labels; they belong to one root exactly for the relevant cycle.
For a column triple the same criterion uses X. The two F1 neighbors are
distinct by simplicity, and their common attachment root is unique. Thus
K counts exactly the16 row/column matching edges that preserve a root pair,
one possible contribution per low triple; K<=16. No guessed annotation or
enumeration of arbitrary matching choices is needed.

Removing the unique collapse gives U=16+K+q=36. Since K<=16 and q<=4,
equality forces K16 and q4. Every matching edge then pairs labels in one
distinguished high root. On a four-label set partitioned into two root
pairs, this forces exactly the root-preserving perfect matching. Thus all
rows pair the B pair and D pair, and all columns pair the A pair and C pair.
This is derived from counting, not imposed as uniformity or symmetry.

## Labelled induced rook contradicts the original defect

Choose any high adjacent pair I in{A,C}, J in{B,D}, with outer points
x1,x2 and y1,y2. The nine distinct actual vertices

    v,x1,x2,y1,y2,Z_x1y1,Z_x1y2,Z_x2y1,Z_x2y2

contain the actual triangles I={v,x1,x2}, J={v,y1,y2}, the two row triples
{x1,Z_x1y1,Z_x1y2},{x2,Z_x2y1,Z_x2y2}, and the two column triples
{y1,Z_x1y1,Z_x2y1},{y2,Z_x1y2,Z_x2y2}. They are the six triangles of a
3-by-3 rook grid. Required row/column edges therefore all exist. Any extra
edge between grid nonneighbors would have its two known grid common
neighbors, contrary to lambda1 for that extra edge. This nine-subset is
an actual induced rook containing I,J. They were an actual defect pair
at v, so this is the contradiction. No general completeness of a matching
list is assumed: all six actual labelled triples are explicitly obtained.

Only the common-point configuration of exactlyfour D2 triangles under
the explicit R227/maxd2 hypotheses is excluded. Nonconcurrent b4, other
b populations, R227 and target existence remain unresolved.

## Ten hand falsification boundaries

1. A degree2 graph on four local high nodes is a graphical C4. It is retained
   as one collapsed F cycle, not called an actual uncovered square.
2. The all-root-preserving abstract graph has37 ordinary cycles:1 high,
   16 two-high,16 one-high and4 low. This meets the scalar count; the final
   actual induced rook through a defect pair is essential to reject it.
3. A single root-crossing row matching uses two cross-root pair edges and
   reduces K by2. K14,q<=4 gives at most34 faithful cycles, so it fails
   U36. It is permitted before equality, not relabelled away.
4. Every row/column four-label matching has three choices; the proof does
   not require their equality or global matching symmetry at the array stage.
5. The outside-one-neighbor identity needs the complete target degree and
   90 outside vertices; an arbitrary partial graph gives only at-mostone.
6. A second z with the same(x,y) label creates three distinct common
   neighbors v,z1,z2. Exact mu2, not a mere naming convention, forbids it.
7. Two low triangles with one attachment cannot share another z by linearity;
   two with different same-family attachments violate the rook neighbor cap.
8. Longer even F1 components are allowed. Only exact four-cycle components
   contribute q, so q<=4 uses simplicity/degree2, not a presumed decomposition.
9. Additional actual edges outside the final nine-grid are retained; only
   potential grid-nonneighbor edges are excluded via their two known CN.
10. Dropping maxd2/exactb4 or the common-point assumption destroys fan
    saturation/unique-collapse arguments. No broader b4 or R227 exclusion follows.

## Forty explicit written proof checks

1. Exact target/R227/maxd2/exactb4/common-point contradiction scope.
2. Empty logical dependencies; earlier results comparison only.
3. Edge uniqueness, triangle linearity and forbidden distinct intersections.
4. Exact local degree d from actual pair-rook uniqueness.
5. D24,a16,P20 and global F36 edges.
6. Actual square count2079 and unique rook coverage9 each.
7. U36 and corner defect/coverage equivalence.
8. Fan injection3r1+5r2.
9. r2=4 forces r1=0 and equality.
10. Local high graphC4 and actual opposite-pair rooks exist.
11. Eight distinct fan outer points and16 required low incidences.
12. All16 low triangles used exactlyonce; no surplus incidence.
13. Four X/four Y attachment labels, eight low triples each family.
14. Outside rook at-mostone neighbor by exact common-neighbor saturation.
15. Boundary90/outside90 makes exactlyone.
16. X outside S2 and Y outside S1 by actual triangle identity at v.
17. Opposite grid points outside other rook; S1 intersection S2={v}.
18. No X-Y adjacency.
19. Defect-attached low triangle's other points outside both rooks.
20. Parity outside high support demands a second low incidence.
21. Linearity/one-neighbor bounds give exactlyone X/one Y incidence per z.
22.32 incidences yield16 distinct z; local row-column pair defective.
23. Label injection via mu2(v,z1,z2), hence16-pair bijection.
24. Arbitrary independent row/column perfect matchings, no uniformity premise.
25. Actual low triples exactly8 row and8 column.
26. F1 bipartite/simple/degree2 with16 edges and q<=4.
27. Every repeated-label F4 collapses through one point/high nodes only.
28. Exactlyone collapse: highC4 at v.
29. All remaining F4 cycles correspond bijectively to U36.
30. Four-high1/three-high0 classification complete.
31. Two-high cycles consecutive and bijective with16 F1 edges.
32. One-high cycles bijective with root-preserving matching edges K<=16.
33. Zero-high cycles exactly q components.
34. Equation36=16+K+q forces K16/q4.
35. K16 forces every row/column distinguished root matching.
36. No arbitrary root preservation, automorphism or matching equality inserted.
37. Explicit final nine labels distinct and six actual triples present.
38. Rook-grid extra edges forbidden by two known CN/lambda1.
39. Actual induced rook contradicts defining adjacent high defect.
40. Only exact common-point boundary excluded; no broader population conclusion.

Historical rook regular-set neighbor proof was whole-read as explicit overlap;
the same universal proof is reconstructed here without a prior gate. Earlier
fan/parity/defect-cycle mechanisms and Root/Structural shared-origin are
disclosed. Fifty written hand checks survive, with zero executed/formal/
external checks. No whole-archive novelty, actual target resolution, scientific
coverage, registrar eligibility or execution authority is asserted. Frozen
historical evidence and closed Wave46 cutoff remain unchanged; exact Root
scope review and any future next-wave47 registration are separate.

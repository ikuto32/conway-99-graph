# Independent written review: target induced-rook count cannot be231

Exact subject: C-UNRESTRICTED-TARGET-ROOK-NINE-COUNT-NOT231, revision1.
Reviewer: /root/structural. Producer of the reviewed composition: /root/checkpoint_audit.
Verification timestamp: 2026-10-04T17:38:17Z. Verification start was not durably recorded and remains null.

Result: WRITTEN PASS within the literal subject statement and assumptions. No
material mathematical veto was found. This is a written derivation and attempted
falsification, with zero mathematical programs, enumerations, matrix calculations
by a program, solver calls or formal proof executions. It does not update the
ledger or supply an execution gate.

## Exact statement and authenticated subject

The literal candidate statement is:

> For every complete finite simple undirected SRG(99,14,1,2), the number R of actual induced rook-nine vertex subsets, each once, is not231.

The two literal assumptions are "complete finite simple undirected
SRG(99,14,1,2)" and "R counts actual induced9-vertex rook subsets, each
vertexsubset once". The raw dependency list is empty. The conclusion is a
necessary conditional restriction on an arbitrary target, not existence or
nonexistence of the target. N3-freeness will be derived only under the supposition
R=231; it is not inserted as a hypothesis of this claim.

The entire candidate paper and raw claim were read. Fresh small-file hashes:

- docs/CANDIDATE_20261004_TARGET_ROOK_NINE_COUNT_NOT231_V1.md:
  2ff5f42bc27f791c3ae0ffd329f49e1ece9184d5bdffe4fe9426907e00b317f8
- acceleration/results/20261004_target_rook_nine_count_not231_candidate01.json:
  e4bd4e06f05d8427236127c103d837b46d270ebed9041cda099d49673d5f6207

The primary PDF was not visually reread by this reviewer. The candidate's
historical attribution and Checkpoint's separate primary-source audit are
comparison evidence. The proof checked below is self-contained and does not
need Makhnev's Hamming/classification theorem or its separate Theorem1. This
report makes no new Russian-reading, pagination or primary-PDF authentication
claim. The candidate's attribution to the1988 theorem is not a novelty claim.

## Shared origin and order of the challenge

Structural authored the earlier square-coverage/N3 equivalence candidate.
Native independently reviewed that earlier statement. That shared forward
component and Root's scope question are disclosed. Checkpoint authored this
new exact count composition and its primary-source reconstruction.

The triangle-component argument below was reconstructed from the new frozen
candidate before comparison with Checkpoint's separate Lemmas6-9 audit. Its
reasoning is recorded explicitly rather than accepted from agreement or from
a literature label. The already-known forward argument was rederived here too.
No old R!=230, R!=229, Hamming or computational gate is transferred.

Comparison pins freshly matched:

- acceleration/audit_20261004_makhnev_theorem2_lemmas6_9_checkpoint_v1.md:
  dd8cf99cffc2d09a869d3dba5961af5a85cd34c99b3b11e03f3eb4f1ed38cbe8
- acceleration/results/20261004_makhnev_theorem2_lemmas6_9_checkpoint_written_review01.json:
  71444bcd8884f0520059228272d71caf42f5ae944980f475dc9a7fadf5c21a50
- docs/CANDIDATE_20261004_TARGET_ROOK_SQUARE_COVERAGE_N3_EQUIVALENCE_V1.md:
  6a9783a607272fc9ebef29d37af3b1864e57efb2012ea1d510255e15e824fd72
- acceleration/results/20261004_independent_review/rook_square_coverage_n3_native01/summary.json:
  4b27c99f7e61199d157399037fc2531f95dccc4ce4507a3dac4f3b325be2b379

## Forward count and N3 implication

In a rook L2(3), an induced square is a rectangle with two distinct rows and
columns. Its four edge partners are fixed by lambda1 in the ambient target.
The partners on two opposite row edges lie in the remaining common column;
their unique triangle partner fixes the ninth vertex. Thus two actual induced
rook subsets containing the square must have exactly the same nine vertices.
This proves uniqueness, not existence, of a containing rook.

There are99*84/2=4158 nonadjacent pairs. The two common neighbors of such a
pair cannot be adjacent: their edge would have both original vertices as
common neighbors. Each pair therefore yields an induced square. A square
has two opposite pairs, giving2079 squares. Each actual rook contains nine
squares; uniqueness makes these nine-square sets disjoint across rooks.
Consequently9R<=2079.

If R=231, every square is covered. Consider two disjoint triangles012 and345
with exactly cross edges03 and14. Their square0-1-4-3 has fixed edge partners
2 and5 on its opposite parallel edges01 and43. Any containing rook requires
edge25, contrary to this induced N3 presentation. Hence R=231 excludes N3.

An outside vertex cannot meet two points of any triangle: its two adjacent
neighbors already have the third triangle point as their unique common
neighbor. Thus cross edges between disjoint triangles form a matching of
size at most three. The absence of N3 is exactly the property (*) that any
two such cross edges force the third. This is the only added condition in
the following contradiction, and its source is the R=231 supposition.

## Independently checked triangle graph

Let Lambda have all actual triangles as nodes, with adjacency requiring
disjointness and three cross edges. Triangle pairs sharing a vertex are not
adjacent. Cross edges of adjacent nodes form a perfect matching.

The open neighborhood of a target vertex induces seven disjoint edges:
for each neighbor, lambda1 fixes exactly one other neighbor. Thus a vertex
belongs to seven triangles. For Delta={a,b,c}, the points outside Delta
neighboring a,b,c form three disjoint classes of size12. Write their union
with Delta as U, and its complement as X. Then |U|=39 and |X|=60.

Take x in the a-class. The nonadjacent pair x,b has common neighbors a and
one further y in the b-class. The third point z of edge xy is outside
Delta; none of a,b,c can be its third point. The disjoint triangles Delta
and xyz have cross edges ax,by, so (*) gives cz. Any Lambda neighbor of
Delta containing x must use that same y and z, by mu2 and lambda1.
The36 external neighbors therefore partition into12 neighbor triangles.
This proof applies at every triangle, so Lambda has degree12 everywhere.

For adjacent Delta={a1,a2,a3}, E={e1,e2,e3}, label their matching ai-ei.
Let fi be the unique partner of ai-ei. These three points are outside both
triangles and are distinct. For i!=j, triangles ai,ei,fi and aj,ej,fj are
disjoint and have cross edges ai-aj,ei-ej. Their third cross edge must be
fi-fj. Thus F={f1,f2,f3} is adjacent in Lambda to both Delta and E.

Any common Lambda neighbor G is disjoint from Delta and E. Its point
meeting ai and ej cannot have i!=j: ai and ej already have common neighbors
aj and ei, and mu2 excludes a third. For i=j, lambda1 makes that point fi.
It follows that G=F. This establishes Lambda's adjacent common-neighbor
number1, with no unproved triangle-graph classification.

## The twenty X triangles

For v in X, each of v,a; v,b; v,c has two common neighbors in the
corresponding U class. These are six distinct U neighbors of v. Two in
the same class cannot be adjacent, since both v and the color's point
would be common neighbors of their edge. Two in different classes cannot
be adjacent either: their triangle with v would have two cross edges to
Delta and (*) would force an edge from v to Delta. Thus the six are
independent.

Within the seven disjoint edges induced on N(v), those six U points pair
with six distinct X points. The remaining two neighbors lie in X and
pair with each other. Hence v is on exactly one triangle wholly in X.
These triangles partition X into20 nodes denoted Lambda2. Denote the12
Lambda neighbors of Delta by Lambda1.

## Exact closure at a first-layer node

Take E in Lambda1, with the same labels ai-ei and its companion F above.
Let G be adjacent to E and contain a U point g, matched to ei.

If g belongs to Delta, it must be ai. For j!=i, the point of G matched to
ej is adjacent to ai and ej. Their two common neighbors are aj and ei.
Since G is disjoint from E, this point must be aj. Hence G=Delta.

Otherwise g is in U-Delta and has a unique neighbor al in Delta. If l!=i,
g would be a third common neighbor of al and ei in addition to ai and el;
g is neither of those, since it is outside Delta and G is disjoint from E.
This is impossible. If l=i, g is the partner fi of edge ai-ei.

For j!=i, fi and ej are nonadjacent. An extra edge would make fi a
second common neighbor of edge ei-ej. Their two actual common neighbors
are ei and fj. The point of G matched to ej must therefore be fj, again
because G is disjoint from E. So G=F.

This exhausts every G containing a U point. Every other neighbor of E is
wholly in X and lies in Lambda2. Degree12 therefore gives exactly ten
Lambda2 neighbors, together with Delta and F.

## Saturation, then recentering

For G in Lambda2, its three points have18 distinct U neighbors. A U point
meeting two vertices of G would violate lambda1 on that edge. Each
Lambda1 neighbor consumes three of these points, and distinct neighbor
triangles are disjoint by the12-triangle partition centered at G.
Thus G has at most six neighbors in Lambda1.

The first-layer count gives12*10=120 incidences. Twenty second-layer
triangles each have at most six, so every one attains six. These consume
all18 U points neighboring G. The remaining six Lambda neighbors of G
cannot contain any U point; the centered partition has already used
every such point. They are wholly in X and hence in Lambda2.

The33-node set {Delta} union Lambda1 union Lambda2 is closed under
every Lambda edge. It is connected, since Delta meets every Lambda1
node and every Lambda2 node meets six Lambda1 nodes. It is consequently
the full connected component containing Delta.

The initial incidence count establishes six common neighbors only for
Delta and its20 nonneighbors. It alone is insufficient for all nonedges.
Repeat the entire construction at an arbitrary E of this component.
The result is a closed connected33-node set containing E and therefore
the same full component. Each of E's20 nonneighbors now has six common
neighbors with E. This proves mu6 for every nonadjacent pair. No vertex
transitivity, equitable profile or graph automorphism is assumed.

## Exact spectral ending

The component adjacency matrix M satisfies
M^2=12I+M+6(J-I-M)=6I-5M+6J.
Its degree12 eigenvalue is simple because the component is connected.
As M is real symmetric, its other32 eigenvalues, on the orthogonal
complement of the all-ones vector, satisfy x^2+5x-6=0 and are1 or-6.
Write their multiplicities f,g. Then f+g=32 and zero diagonal gives
12+f-6g=0, whence7g=44. No integer g exists.

As checks on the arithmetic, applying the matrix identity to the
all-ones vector gives144=6-60+198, and the elementary parameter equation
12*(12-1-1)=20*6 gives120=120. Thus it is specifically the impossible
spectral multiplicity, not a failed degree count or floating estimate,
that contradicts the component. Property (*) is impossible for the
target. The supposition R=231 implied (*), so the literal claim follows.

## Attempted falsification and scope boundaries

1. Counting square pairs divides by two, not four; an actual square has
   two nonadjacent opposite pairs.
2. The containing-rook uniqueness proof uses lambda1-fixed partners and
   the ninth partner. It does not identify rooks only up to isomorphism.
3. The square from the two disjoint triangles is induced because cross
   edges are only03 and14. A sparse non-complete six-point N3 pattern
   is not itself a complete SRG counterexample.
4. Removing (*) breaks the forced cz edge, the fi-fj triangle, and
   cross-color independence. These steps are never asserted before
   R=231 has supplied (*).
5. Shared-point triangles are excluded from Lambda adjacency. The
   common-neighbor proof separately prohibits a common triangle from
   reusing a point of Delta or E.
6. In closure, the forbidden third common neighbor cannot secretly
   equal ai or el: g is outside Delta and outside E.
7. The18 U neighbors of a second-layer triangle are distinct by
   lambda1, not by a symmetry or uniform-distribution assumption.
8. The120 incidence count needs the at-most-six inequality for each
   of all20 second-layer nodes before equality can force six each.
9. A locally counted Delta pair does not establish all mu6; recentering
   at every node is indispensable and has been checked above.
10. The33 nodes need not be all231 actual target triangles. Even seven
    putative33-node components would not repair one component's
    impossible spectral multiplicities.
11. Connectedness is proved before degree12 simplicity is used.
12. The known rook SRG(9,4,1,2) is N3-free and has two K3 components in
    its triangle graph. It does not contradict this target-specific
    argument: its degree/order give U=9, X=0, not39/60/33.
13. No general Hamming cover, spectral classification theorem or
    literature premise is substituted for the recentered local proof.
14. No new bound obtained by composing R!=230 or R!=229 is claimed in
    this report; those immutable statements have separate evidence.

These14 challenge boundaries accompany the14 sequential derivation
checks listed in the report, for28 written checks total. Executed
mathematical, solver and formal controls are all zero.

## Result and administrative limits

No material theorem veto was found. This written review recommends the
exact r1 statement for VERIFIED/CLEAR treatment after Root's separate
administrative review. It does not itself register the claim, change
availability, certify any graph construction, or resolve Conway99.
The raw scope retains scientific_coverage UNKNOWN and target_resolution
NONE. Existing source, candidate, primary evidence, ledger and Git
bytes were not edited. No computational worker is owned by this reviewer.


# Independent written audit of the exact four-class family revision1

Subject: `docs/CANDIDATE_20261003_SEVENTEEN_POINT_FAMILY_FOUR_CLASSES_V1.md`,
SHA256 `1faee8e574557fcbb75847e92dbfb6c8e5efd125a2f660b406641e4ed9104ed9`.
Claim `C-SEVENTEEN-POINT-LABELLED-TRIANGLE-FAMILY-FOUR-ISOMORPHISM-CLASSES`,
revision1. Discovery producer Root; different-author verifier Structural.

Outcome: **PASS for precisely the defined small-graph construction**. The
whole frozen candidate was read, and both directions and orbit exhaustion
were reconstructed below. This is written verification, not executable
isomorphism replay, target-family coverage, occurrence or completion evidence.
There are eighteen handwritten falsification boundaries and zero mathematical
commands, fixtures, formal checks or external reviews for this audit.

Root originated the partition mechanism. Before freezing, Structural supplied
a separate preliminary reconstruction and corrected the omitted bridge:
`notes_20261003_seventeen_point_family_four_orbits_preliminary_v1.md`, SHA256
`ba1791bf11d7e1e3c7b6802ac822d88fec5e37fcb3615c151ae0ab9b5b855f89`.
That shared history is disclosed rather than treated as prior approval of
this exact revision. The present independent audit is bound to the frozen
candidate above. The preliminary optional multiplicities and automorphism
orders are not statements approved by this audit.

## 1. Independently recover the intrinsic geometry

Write the four A points as a_i, their matched B points as b_i=sigma(a_i),
and their assigned free points as v_i=rho(a_i). The complete graph is the
edge union of the exact twelve triangles in the candidate. Any two of those
triangles intersect in at most one vertex: the four positive row triangles
are pairwise disjoint, negative A/B/R triangles meet a row only in its one
point from that named set, and the center and x triangles have only their
declared intersections. Thus there are no duplicate triangle edges.

Each center belongs to three triangles, and every other point to two.
The graph degrees are therefore6 at s,t and4 at all fifteen other vertices.
This intrinsically identifies the unordered pair {s,t}. In addition,

    N(s) = {t,x} union A,     N(t) = {s,x} union B,
    N(s) intersect N(t) = {x}.

Hence x is intrinsic. Choosing an order of the centers identifies A and B;
the six remaining points are L union R. Their induced graph contains the
two negative triangles and exactly one further edge, ell-r, from {x,ell,r}.
The two R-set neighbors of x identify ell,r, so deleting their connecting
edge recovers the unordered two triangles. The initial informal assertion
of two disconnected components was false and is correctly absent from the
frozen proof. No assumption about a target graph is used to recognize them.

The only A-B edges are the four matched pairs. For a matched pair a_i,b_i,

    N(a_i) = {s, a_i's negative-pair mate, b_i, v_i},
    N(b_i) = {t, b_i's negative-pair mate, a_i, v_i}.

The named sets are disjoint, so these two sets intersect exactly at v_i.
In particular each row's free vertex is recovered without assuming that
the graph's actual triangles were previously enumerated or validated.

## 2. Independently prove both isomorphism implications

Use the four A-B edges as the abstract row set. PA is its partition by the
two negative A edges; PB is its partition by the two negative B edges;
PR is its partition by which recovered R triangle contains the free vertex.
Each is an unordered partition into two pairs.

For any graph isomorphism, the degree argument maps the two centers to the
two centers. The unique-common-neighbor argument then maps x to x and maps
A,B either in order or exchanged. The recovered bridge and sides, matching
and free vertices consequently map as well. Thus a row bijection preserves
PA,PB,PR as named, or exchanges PA/PB if the centers exchange. PR is the
intrinsic R-side name, so it is not exchanged with either other partition.

For the converse take a row bijection with precisely this property. Map
s,t in the prescribed order or exchange, map x, map each A/B row endpoint,
and map its assigned free vertex. A block of PR determines one R triangle;
map its distinguished bridge endpoint to the endpoint on the corresponding
triangle. These assignments are bijections on the two centers, x, four A,
four B, four free R points and two distinguished R points: all17 vertices.

The center triangle maps to the center triangle. PA/PB preservation (or
exchange) maps the four A/B negative triangles. PR preservation maps the
two R triangles and their bridge endpoints, hence the x triangle. The four
row triangles map row by row. These are all twelve triangles whose edges
define the complete graph, so every edge and nonedge is preserved. There
is no remaining orientation, side order or vertex choice to constrain the
converse. This explicitly addresses the common gap of proving only an
invariant without proving its sufficiency for isomorphism.

## 3. Independently exhaust the partition orbits and their realization

Four elements have three pair partitions: M0=12|34, M1=13|24, M2=14|23.
The row transposition(23) exchanges M0/M1 and fixes M2. Transposition(34)
fixes M0 and exchanges M1/M2. Thus row bijections realize every simultaneous
permutation of these three symbols; no symbolic relabelling is assumed
without an actual row permutation.

The equality pattern of (PA,PB,PR), remembering PR's name but allowing the
first two names to exchange, has only four possibilities:

    all three equal;
    PA=PB unequal to PR;
    PR equal exactly one of PA/PB;
    all three distinct.

These patterns are invariant under the necessary isomorphism condition.
Within each pattern, simultaneous permutations of M0,M1,M2 normalize to
the candidate representatives. In the third pattern the two possible
positions of the equal pair are identified by exchanging centers. The
isomorphism converse proves each pattern is a single orbit; the invariance
proves two different patterns cannot merge under an arbitrary permutation
of all17 vertices. This exhausts all partition triples, not merely a sampled
subset of the 5184 labels.

Each orbit is nonempty. For any chosen PB, map its two row blocks bijectively
to the two fixed B pairs and orient inside each pair; this gives sigma.
For any chosen PR, map its two row blocks to the two free points on each R
side, orienting inside each side; this gives rho. Any of the nine choices
of distinguished points is allowed. This realizes all four representative
patterns in the declared family. Their exact count is therefore four.

## 4. Falsification boundaries and exact limits

1. The17 points and named subsets are disjoint; point reuse would invalidate
   the degree and intrinsic-neighborhood reconstruction.
2. Sigma and rho are bijections, not arbitrary repeated-value maps.
3. There are twelve selected triangles, not an arbitrary extension graph.
4. All edges are exactly their union; adding an internal edge is outside scope.
5. Triangle-edge disjointness is established before using the degrees.
6. Only the two centers have degree6, blocking a hidden center/free-point swap.
7. The unique center common neighbor fixes x rather than merely its degree.
8. R contains the bridge; pretending its two triangles are components is wrong.
9. Its two x-neighbors determine the bridge endpoints and recover its sides.
10. A-B adjacency is precisely the matching; it cannot supply other row edges.
11. The matched pair's free vertex is its unique common neighbor by explicit
    neighbor sets, rather than a presumed target lambda condition.
12. PA,PB,PR blocks are unordered; their side orientations are not extra data.
13. Center exchange swaps only PA/PB; treating all three names as freely
    interchangeable would incorrectly merge two equality patterns.
14. The converse maps every17 vertex and every defining triangle explicitly.
15. S4 really induces all S3 partition permutations by the two written generators.
16. All four patterns are both invariant and realized by literal bijections.
17. The proof does not rely on a computer catalogue, raw local-validity result,
    or a target automorphism assumption.
18. Extra edges, induced target occurrence, circuit minimality, graph completion,
    target exclusion, multiplicities and automorphism orders are not concluded.

The independent family raw report f9a97 is informational provenance only; it
is not a material premise of this construction theorem. The same holds for
the earlier preliminary reconstruction. The proof needs no theorem dependency
besides the displayed definition and elementary finite bijections. Existing
sources, reports, ledger, index and candidate bytes are preserved. No formal
proof assistant or external review ran. Novelty is UNKNOWN.

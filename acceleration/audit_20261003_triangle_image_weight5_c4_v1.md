# Independent weight-five collision subtraction derivation V1

Verifier: /root. Preparation reviewed 2026-10-02T22:04:19+00:00 from the working tree
based on source commit 16be41cee26421941eaecb615b64bd21095c5765.
The timestamp is preparation metadata; finite checking has not yet run.
Discovery: /root/structural's proposed improvement of the weight-five path
count. This written derivation does not approve a computational producer.

Let G be a finite simple graph in which each edge has exactly one common
neighbor. Let T be its complete set of actual triangles. A path is an
unordered pair of end triangles meeting a central triangle at different
vertices, with all three triangles distinct. The established independent
derivation in audit_20261003_triangle_image_weight5_v1_proof.md (SHA256
8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee)
shows that the three-triangle binary sum has weight five and that its
inverse fibers have size one or two. It independently establishes the
complete path population

P = sum over central tau of sum over unordered {p,q} in tau
    (r_p - 1)(r_q - 1),

where r_v is the number of actual triangles incident with v. In particular,
the two end triangles intersect only the central triangle, at p and q.
For the image support S, the remaining central vertex r is the unique
isolated vertex in G[S]. The four end vertices admit a perfect matching
formed by the two end-triangle edges. Their induced graph is 2K2, P4 or C4;
each permissible perfect matching reconstructs at most one path using the
unique triangle completion of each matched edge.

If a fiber has size two, the four nonisolated support vertices have two
different perfect matchings. Among these three possible induced shapes,
only C4 has two. Thus every double fiber supplies an induced C4 Q.

The assignment from double fibers to induced C4s is injective. To check this,
fix Q and either one of its two perfect matchings {e,f}. The unique common
neighbor p of the endpoints of e and the unique common neighbor q of the
endpoints of f are determined by G and the matching. If the matching
represents a path, p,q are distinct outside Q and pq is an edge. The
isolated support vertex r must be the unique common neighbor of p and q.
Consequently this matching determines at most one r and hence at most one
support Q union {r}. Every double fiber on Q uses both perfect matchings,
so two different double fibers on the same Q are impossible. This argument
uses the existence of a represented path only conditionally and does not
assert that any induced C4 actually has a double fiber.

Let D be the number of double fibers. Since all fibers have size one or
two, the number of distinct path-image words is P-D. The injection proves
D <= c4(G), where c4(G) counts induced four-cycles by their unordered vertex
sets. Therefore the number N5 of all weight-five words in the binary span
of the complete triangle incidence vectors satisfies

N5 >= P - c4(G).

No injectivity of all paths, equality with the full weight-five image,
regularity, nonedge-common-neighbor condition, or automorphism is assumed
in this general inequality. A negative right-hand side is simply a weak
lower bound.

For a hypothetical srg(99,14,1,2), r_v=7 and there are 231 triangles, so
P=231*3*6*6=24948. Every nonadjacent pair u,v has exactly two common
neighbors x,y. They are nonadjacent: an edge xy would have the two different
common neighbors u,v, contradicting the edge condition. The four vertices
therefore induce C4. Each nonadjacent pair determines one such four-cycle,
and each four-cycle has exactly two opposite pairs. The number of unordered
nonadjacent pairs is 99*84/2=4158; hence c4(G)=4158/2=2079. This gives the
conditional, unrestricted necessary inequality N5>=22869.

For C=ker(B^T), character orthogonality gives the exact necessary row

sum over nonzero w of A_w(22869-K_5(w)) <= binomial(99,5)-22869
                                               = 71500275.

The zero-word term is included in the derivation: sum_w A_w K_5(w)=|C|N5,
K_5(0)=binomial(99,5)=71523144 and A_0=1. This row does not force C to be
nonzero, does not impose a rank upper bound, and supplies no graph or
nonexistence certificate. The old lower bound 12474 remains valid and its
artifacts must remain unchanged.

Suggested independent finite challenges (not yet executed): enumerate all
three-triangle paths and all induced four-cycles on known lambda-one
fixtures; reconstruct double-fiber-to-C4 injection from raw adjacency;
rook9 has P18, D9, c4=9 and nine weight-five image words. Reject a falsely
claimed injective path map, a duplicated cycle assignment, an incorrect
isolated vertex, an overstated lower bound, and a K7 fixture lacking the
edge-common-neighbor premise at precise stages. Check the target cycle
count and shifted character constant with exact integers. Finite controls
are separate from the universal written proof above.

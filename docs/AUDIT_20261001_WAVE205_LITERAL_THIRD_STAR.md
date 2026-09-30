# Independent literal third-star exclusion

Reviewer `/root`; producer `/root/state_literature_audit`.
Written coverage review completed 2026-09-30T17:24:35+00:00.

**PASS, conditional on the exact stated local configuration and rank/prism
premises.** The complete finite audit is
`acceleration/results/20261001_independent_review/wave205_third_star/summary.json`,
SHA256 `36a4145f17112f6b40fb42a78af801cbce1ade3dcf497f1bd8d79bde11f5b92b`.
It independently reconstructed all4,050 options and the complete17-node search,
with zero complete covers, in6.594seconds. It checked192 full augmented pair
Gram ranks. No native solver or floating-point arithmetic was used.

The exact claim is: no srg(99,14,1,2) that is prism-free and whose full
triangle-incidence Gram D=B^T A B over F3 has rank11 can contain the raw
induced28-vertex t6_h1 graph authenticated by the report. This is one literal
configuration exclusion under additional premises. Neither those premises nor
the presence of this configuration is asserted for an arbitrary target.

I reviewed the producer's complete coverage derivation,
`docs/DERIVATION_20261001_WAVE205_LITERAL_THIRD_STAR.md`, SHA256
`ea52e810a78fc806e05d9eed2f3307f284fda133234fc865c3b7a0ccb343102f`.
The following checks establish its applicability without importing the
archive's historical VERIFIED labels.

The raw induced graph has nonadjacent centers x,y, each already of degree14,
and common neighbors a,b. All old vertices are x,y or in their neighborhoods.
The only old neighbors of a are x,alpha,y,gamma, already paired by the edges
x-alpha and y-gamma. In an SRG with lambda=1 every neighborhood is a disjoint
union of edges: each neighbor has exactly one neighbor in that neighborhood.
Thus a needs precisely ten new neighbors, partitioned into five edges. There
are no edges between these pairs or to the four old a-neighbors.

Every new vertex p is outside both complete old neighborhoods. Its common
neighbors with x include a, so it needs exactly one additional old x-neighbor;
the same holds for y. The common vertex b cannot be used, because a,b already
have x,y as their two common neighbors. Alpha and gamma cannot be used, since
their unique partners in N(a) already exist. For every remaining old exclusive
vertex r, its number of new attachments is exactly
2-|N_old(a) intersect N_old(r)|. Independent raw reconstruction gives ten
deficits1 on each side and one deficit0, at x20 or y20. Every eligible label
must therefore be used exactly once. No edge to any other old vertex remains
unspecified.

Consequently each new triangle uses two distinct X labels, two distinct Y
labels and a matching between them. The complete4,050 population follows.
Ordering the two new vertices by their X attachments names otherwise unnamed
vertices; it assumes no automorphism of the completed graph. Every actual
extension determines a five-option exact cover of both ten-label pools.

The independent checker reconstructs all old triangle-incidence adjacency
products directly. Their14x14 ternary Gram has rank11. Any actual new
triangles must give principal Gram matrices of the global D, hence rank at
most11. A triangle has diagonal6=0 in F3. Two distinct new triangles through
a have exactly four incidence-adjacency contributions, so their off-diagonal
Gram entry is1. This follows from the induced matching N(a), not an assumed
unconstrained projector model. Integer common-neighbor caps and the absence
of three-cross-edge disjoint triangle pairs are also necessary on each
fully specified induced local graph.

Unlike the producer, the independent checker uses adjacency sets and full
14x15,15x15 and16x16 ranks by column-basis insertion. It does not use the
producer's principal inverse or coordinate vectors. Every candidate's
retained/rejected status agrees. Rank checking was calibrated on all729
symmetric3x3 ternary matrices by independently enumerating exact minors.
The known9-vertex rook SRG and deliberately corrupted cases calibrate the
graph predicates; changed outcome, missing candidate, missing subtree exit
and wrong-rank controls were rejected.

For complete search coverage, choose the least unused X label. Every cover
has exactly one option containing it, so enumerating all retained options
containing it loses no cover. Rejecting an already used X/Y label or a pair
whose augmented Gram rank exceeds11 is necessary. The independent traversal
matches every saved enter/exit event:16 possible first options and no legal
continuation covering the next required X label, all exhausted. Since no
five-option cover exists even in these necessary pair tests, no assumption
about the unexecuted later38-vertex leaf checker is needed.

The archive control itself remains valid for its original two-center scope.
This result neither refutes it nor excludes all integer lifts of its cross
Gram, the18 normalized t=6 matrices, the rank11 branch, or the prism-free
endpoint. The archived raw source is pinned to
YesterdaysLemon/conway-99-research commit
`85e705cc6c2a14d123120c93a847e30aaab1789e`, path
`attempts/wave205-nonedge-fourth-trace-proof-a/controls.json`, SHA256
`e52c068f5fdba18110debdd1455195ec22145f07993437b5438e8f77ae03fdcf`.
No target-resolution or external-review claim follows.

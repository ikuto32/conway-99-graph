# Independent review of the conditional rook-nine encoding

The exact encoding and the compatible eighteen-cell spectrum pass this
review. This is an equivalence restricted to targets containing an induced
3x3 rook graph. It neither assumes nor proves that all targets contain one.
No automorphism, chosen matching between groups, or graph search result is
a premise. The accompanying report binds claim
`C-ROOK-NINE-REGULAR-SET-ENCODING` revision1 and the exact producer artifacts.

## Independent universal derivation

Let S be the nine vertices of an induced rook graph B. Each vertex has four
neighbors in S. Each adjacent pair in S already has exactly one common
neighbor in S; each nonadjacent pair has exactly two. If an outside vertex
were adjacent to two distinct vertices of S, it would exceed the target
common-neighbor count of that pair. Thus each outside vertex meets S at
most once. The target diagonal equation forces degree14. There are90
boundary edges, by9*(14−4), and90 outside vertices. Hence every outside
vertex meets S exactly once, and each vertex of S has a group X_i of ten
outside neighbors. Arbitrarily labeling each group gives T=I9⊗1_10^T;
arbitrary labels are not an assumption of an automorphism.

In these labels A=[[B,T],[T^T,H]], and H is symmetric, binary and hollow.
The top-left target block is automatic: B²+TT^T=(2I−B+2J)+10I.
The top-right block BT+TH=−T+2J is precisely TH=(2J9−B−I9)T,
because J9*T=J_(9x90). The remaining block is precisely
H²=12I90−H+2J90−T^TT. Symmetry gives the fourth block. These block
equalities prove both directions for every H of the declared type. In the
reverse direction A is a complete symmetric binary hollow99x99 matrix
satisfying the target equation and containing B, so no extra degree or
regularity premise is needed.

Write Q=2J9−B−I9. For x∈X_i, (TH)_(j,x)=Q_(j,i), its number of
neighbors in X_j. Q has one on the diagonal and at rook-adjacent pairs,
two elsewhere, with row sum13. Consequently each X_i induces a perfect
matching; each rook-adjacent pair of groups is joined by a perfect matching;
each other pair supports a2-regular bipartite graph. None of these block
graphs has been constructed or excluded by this encoding.

The eighteen-cell equitable quotient is K=[[B,10I],[I,Q]]. On the constant
subspace, the corresponding2x2 matrix is[[4,10],[1,13]], with eigenvalues14
and3. On each of four B-eigenvectors of eigenvalue1, it is[[1,10],[1,−2]],
with eigenvalues3 and−4. On each of four B-eigenvectors of eigenvalue−2,
it is[[−2,10],[1,1]], again with eigenvalues3 and−4. Thus K has spectrum
14^1,3^9,(−4)^8. The remaining81-dimensional invariant subspace consists
of outside vectors with zero sum in each X_i. Subtracting the quotient
multiplicities from the target spectrum leaves3^45,(−4)^36. Every multiplicity
is nonnegative; there is no spectral contradiction.

## Independent exact artifact checks

The reviewer imports no producer. It reconstructs B from grid-coordinate
equality, T from group membership, Q entrywise, and K from its cell degrees.
It checks all raw entries. Rational Gaussian elimination determines every
claimed eigenspace dimension; their dimensions sum to the matrix order, so
no floating-point eigenvalues or producer Newton-trace routine is used.
The recorded characteristic polynomials are checked against those dimensions.
All512 possible attachments of one outside vertex to S are checked against
saturation; exactly the empty attachment and nine singletons pass.

Separate set-neighborhood intersections reconstruct the full99 residual and
the cross/lower block residuals on all ten saved deterministic calibration
patterns. These finite checks test implementation and signs; the universal
proof is the block expansion above, not agreement on ten examples. The H
patterns are reconstructed from the producer's disclosed deterministic
formula because raw H matrices were not saved. This shared fixture formula
is disclosed; the residual checker uses an independent set-counting path.
Corrupt B, T, Q, quotient, polynomial and block-residual controls are rejected.
No H satisfying the target equations is provided by the calibration.

## Archive and literature scope

Archive commit85e705cc6c2a14d123120c93a847e30aaab1789e already records the
two-cell boundary-edge argument and quotient in Wave102's derivation and
independent verification§5. This review derives the present statement anew;
historical VERIFIED labels are not treated as current fresh artifact checks.
No claim of novelty is made.

The focused2026-09-17 inspection of
[arXiv2604.23037v2](https://arxiv.org/html/2604.23037v2),§3.4.2, confirms that
exclusion of a single Paley9 subgraph is labeled Conjecture3.4.4. Theorem3.4.3
concerns eleven independent copies and explicitly omits its proof. These
are scope checks only; neither assertion is used in this encoding proof.
The front matter states June2023 and the arXiv version is dated28April2026.
This is not a comprehensive literature-status or novelty audit.

Target resolution remains UNKNOWN. Overall search coverage: UNKNOWN;
no validated denominator. No claim-ledger file was edited by this review.

# Candidate ternary reduced-Gram countermodel

Author: `/root/structural`. This is a paper construction, not an executed
calculation or an independently checked result. Status: **CANDIDATE**. It
concerns exact algebra over GF(3); it is not a triangle incidence matrix or a
graph with integer degree14, and it does not exclude Conway-99.

Prepared at2026-10-03T00:47:36+00:00. Repository source context:
`00ffb6fdd7d91bd38269e1cc5e6b214ebf7591c8`; this new note is separately
pinned working material and is not claimed to belong to that commit.

The existing fixed non-SRG rank98 experiment has a different scope: actual
linear, regular triangle incidence, without the target's mu2 equations. The
construction here tests the other potential weak step: whether the reduced
target matrix equations together with the elementary ternary incidence
identities alone force a second left-kernel vector. Neither construction
combines all target hypotheses.

## Explicit reduced target matrix

Partition the first72 coordinates into18 four-element blocks; the other27
coordinates are singletons. Work throughout in GF(3). Let P be the block
diagonal matrix with18 blocks I4-J4 and27 zero singleton blocks. Then

* P is symmetric, has zero diagonal, P squared equals P, and rank(P)=54;
* P times the99-coordinate all-one vector equals0;
* J99 squared equals0, and PJ99=J99P=0.

Define M=P+J99 and A=M-I99. A is a symmetric zero-diagonal binary matrix:
within each four-block its off-diagonal entries are0, and every other
off-diagonal entry is1. It is the complete multipartite graph with18 parts
of size4 and27 parts of size1. Its integer degrees are95 and98, not14.
Both degrees reduce to2 modulo3.

Exactly over GF(3), rank(M)=55, M squared=P, A times1=2 times1, and

    A squared = -A + 2J99.

For the rank claim, im(P) is a54-dimensional nondegenerate space orthogonal
to1. The vector1 is outside im(P), has squared norm99=0, and J99 has image
span(1). On the orthogonal complement of im(P), J99 still has rank1: e.g.
any of the27 singleton coordinate vectors has coordinate sum1. Thus im(M)
is the direct sum of im(P) and span(1).

## A99-by231 factor of rank98

In each four-block, use three column vectors

    f=(1,2,1,2), g=(1,2,2,1), h=(1,1,2,2).

Each has coordinate sum0 and squared norm1; their mutual dot products are0.
Their span is the three-dimensional sum-zero subspace of that block. Their
three outer products sum to I4-J4. Across all18 blocks, extend these by zeros
to obtain54 mutually orthonormal vectors v1,...,v54. Their outer products sum
to P. Add a column equal to1. These55 columns have Gram sum M and span

    W = im(P) + span(1),  dim(W)=55.

Let H=1-perp, which has dimension98, and choose any43 vectors q1,...,q43
whose residue classes form a basis of H/W. This choice is explicit in the
linear-algebra sense: scan the98 independent vectors e_i-e_98, for
i=0,...,97, and retain the first vectors extending the displayed55-column
basis. No numerical approximation or graph automorphism is involved.

Append three identical copies of each q_i. Each triple contributes zero to
BB-transpose because3=0. It also has column sum zero as a vector, so this
addition changes neither the Gram sum nor the sum of the columns. It raises
the column-space dimension to98.

Let s=sum(v_i), and append the three columns -s,-s,s. Their outer products
also sum to zero, while their sum is -s. Pad by44 zero columns. There are
54+1+129+3+44=231 columns in total. The resulting matrix B satisfies

    rank(B)=98,
    B B-transpose = M = A+I99,
    B-transpose 1 = 0,
    B 1_231 = 1_99.

The only left-kernel vectors are constants: every column belongs to H and
the columns span H. The padding and the added algebraic columns are not
actual triples; many entries are2. In particular, this is not a regular
3-uniform incidence construction. Its elementary sum identities reproduce
only the reductions modulo3 of triangle column weight3 and point row weight7.

## Exact scope and falsification requirements

If independently checked, this construction refutes only the implication
that a second ternary kernel vector follows from the displayed reduced
matrix identities, binary symmetry/zero diagonal of A, and elementary
ternary incidence sum identities. It cannot refute an implication using
the exact integer SRG equation, degree14, actual triangle columns, or other
missing incidence constraints. The previous actual rank98 fixture and this
algebraic countermodel cannot be combined into a single counterexample.

Before recording a claim, a separate checker should reconstruct all18
blocks,54 vectors, the43 selected extensions, all231 columns and all exact
scalar identities, with corrupted block/vector/coefficient controls. A
written independent basis/dimension argument is also needed. No such
execution or approval is claimed here. No novelty or external review is
claimed. No live ledger, current-state document, or graph artifact is changed.

Overall search coverage: UNKNOWN; no validated denominator.

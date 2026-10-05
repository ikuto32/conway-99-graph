# Candidate: excluding the whole octahedral ternary residual support

Discovery producer `/root`; source context
`63437c9b9fc2dd58b3bdfb51fc347b880b397503`. This is a new exact written
candidate outside the frozen 371-claim publication cutoff. Status CANDIDATE;
independent derivation and falsification review are pending. No mathematical
execution, numerical spectrum, formal proof, external review or novelty claim
is supplied.

## Precise revision-1 statement

For every symmetric binary integer 99-by-99 matrix A with zero diagonal and
exactly 14 ones in every integer row, put R=A^2+A-12I-2J and let M be R reduced
over GF(3). The whole nonzero unordered off-diagonal support graph of M cannot
be K6 minus a perfect matching. This is a whole-support exclusion, not an
exclusion of a component within another support, all twelve-edge supports or
a solution of Conway-99. Empty support remains permitted.

The material dependency is revision 1 of
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`, report
`acceleration/results/20261003_independent_review/ternary_equal_outside_nine_01/equal_outside_filter/summary.json`,
SHA256 `7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`.
Its needed facts are explicitly recalled here. No twelve-edge classification,
K2,6 lift, defect lower bound or automorphism assumption is used.

## Exact outside-row restriction

Let S be this whole six-vertex support. The integer residual R has zero diagonal
and zero row sum; the field residual M has zero rows outside S and zero row
sum everywhere. A commutes with M since A is symmetric and regular, so for
every vertex outside S its binary adjacency row x into S satisfies x M_S=0.

Every support vertex has degree four. A signed row with two labels 1 and two
labels 2 is the only way its four nonzero GF(3) entries can sum to zero: if c
is the number of 1 labels, c+2(4-c)=8-c is zero modulo 3 only for c=2.
The graph of label 1 is therefore a simple 2-regular graph on six vertices.
It is either two disjoint triangles or a six-cycle. Label 2 is interpreted as
-1 in the field in the following matrices, not as the integer residual itself.

If two support vertices have the same adjacency coordinates in every such x,
they have identical outside neighborhoods. With m=6, the equal-outside
restriction gives CN(u,v)>=14-floor(6/2)=11. Thus their integer R_uv is at least
9. But an endpoint with support degree four has maximum total negative budget
beta=2c1+c2=6. Any single good entry is at most 6, and a bad entry is at most
4 or 5 according to its residue. Consequently no two distinct support
vertices of degree four can have equal outside neighborhoods. It suffices to
force even one such pair from the exact kernel.

## Two label-1 triangles

Order the two positive triangles into two groups of three. Each vertex already
has its two positive neighbors inside its group. Its one nonedge partner must
lie in the other group, so the removed perfect matching is entirely between
the groups. Relabel the second group so its matching partners have the same
index. Let B=J3-I3. The signed support matrix is

    M_S = [[ B, -B ], [ -B, B ]].

Over GF(3), J3^2=0, hence B(-I3-J3)=I3. In particular B is invertible. The
kernel condition gives B(x_first-x_second)=0, so the three matched coordinate
pairs are equal in every outside row. Any one of these pairs violates the
degree-four equal-outside budget just derived. Reversing all signs preserves
the kernel, so the case of two label-2 triangles is excluded as well.

## A label-1 six-cycle

Order its vertices cyclically 0,1,2,3,4,5. The removed perfect matching must
use only noncycle edges. Divide the vertices into the three even and three odd
indices. The number of removed matching edges between the two parts is odd,
and therefore one or three: the vertices left in each part must pair internally.

If it is three, each even vertex has only its opposite odd vertex available
after excluding the two cycle edges. The removed matching is (0,3),(2,5),(4,1).
The negative edges are then two triangles on the even and odd parts. Sign
reversal reduces this case to the preceding exact matrix argument.

If it is one, that cross edge must again be an opposite pair. A rotation of
the labeled cycle puts it at (0,3); the remaining matching edges are forced
to be (2,4) and (1,5). This labeling only enumerates every possible signed
support. It does not assume an automorphism of A or of a hypothetical target.
The full signed support matrix, with entries interpreted over GF(3), is

    [[ 0, 1,-1, 0,-1, 1],
     [ 1, 0, 1,-1,-1, 0],
     [-1, 1, 0, 1, 0,-1],
     [ 0,-1, 1, 0, 1,-1],
     [-1,-1, 0, 1, 0, 1],
     [ 1, 0,-1,-1, 1, 0]].

For a kernel vector x, adding rows 1 and 5 gives 2(x0-x3)=0, hence x0=x3.
Row 1 then gives x2=x4, and row 2 gives x1=x5. Row 0 gives
2(x1-x2)=0. Thus x1=x2=x4=x5 and x0=x3. Every outside binary row satisfies
these equalities, so there are again distinct degree-four vertices with equal
outside neighborhoods, contrary to the exact negative budget.

These two cycle cases and the triangle case exhaust every label-1 2-factor
and every possible removed matching. They prove the candidate statement with
exact integer and GF(3) arithmetic.

## Limits and independent review requirements

The independent reviewer should reconstruct the signed-degree condition,
all 2-factors on six vertices, the matching parity/cycle cases, the literal
matrix and each kernel equality, and the applicability of the integer
equal-outside budget. The matrix is not claimed to satisfy M^2=4(I-P), nor is
any numerical eigenvalue needed. The graph labels and sign reversal are
enumeration devices only. No result about an arbitrary component, incidence
rank, sharpness, general twelve-edge coverage or target resolution is asserted.

All artifacts are LOCAL_ONLY pending immutable publication. Mathematical
verification command: null, because this is a written discovery, with zero
executed fixtures. Creation timestamp is not asserted; the review/report should
record its actual clock and the final candidate SHA256. No ledger, index,
scientific source or frozen milestone is changed by this paper.

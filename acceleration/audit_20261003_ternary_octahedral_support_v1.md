# Independent written audit: whole octahedral ternary residual support

Verifier `/root/structural`; discovery producer `/root`. Actual review clock
before saving: `2026-10-03T09:54:39+00:00`. Source context
`63437c9b9fc2dd58b3bdfb51fc347b880b397503` is historical context, not a claim
that these new files are committed. Mathematical programs, enumerations,
executed fixtures, formal checks, external review, ledger and index mutations:
zero. This is a different-author exact written derivation and falsification
review. Outcome **PASS** within the precise whole-support scope below.

## Exact discovery and statement

The complete frozen discovery read is
`docs/CANDIDATE_20261003_TERNARY_OCTAHEDRAL_SUPPORT_V1.md`, SHA256
`4fe0d18e60d62af2b6c95a784b4bf4201168aa4cfdc141e1681f8561b9cbbd5a`.

For every symmetric binary integer 99-by-99 matrix A with zero diagonal
and exactly 14 ones in every integer row, define

  R=A^2+A-12I-2J, and M=R modulo 3 over GF(3).

The whole nonzero unordered off-diagonal support graph of M cannot be
K6 minus a perfect matching. Empty support is allowed. The statement
excludes neither a component within another residual support nor all
twelve-edge supports; it supplies no target resolution or graph realization.

The sole material dependency is revision 1 of
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`.
ROOT's independent audit is
`acceleration/audit_20261003_ternary_equal_outside_nine_v1.md`, SHA256
`0497fef0e3a9ca8558acc2aacdbc68abe6b9ef8db925e502765d02a85676be18`;
its exact filter report is
`acceleration/results/20261003_independent_review/ternary_equal_outside_nine_01/equal_outside_filter/summary.json`,
SHA256 `7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`.
The original filter discovery was authored by this verifier at
`docs/CANDIDATE_20261003_TERNARY_EQUAL_OUTSIDE_BUDGET_NINE_DEFECT_V1.md`,
SHA256 `a67fe7e196228165b4fcccedef9e8956362d9248404766f0a0202ddd370670cd`.
Its required elementary arguments are independently repeated below; it
is not accepted here as an unverified self-authored premise.

Neither the new twelve-edge classification nor the separate K2,6 lift,
nonzero-defect-lower12, eigenvalue parity or incidence-rank result is used.

## Independent reconstruction of outside words and integer budgets

Integer R has diagonal 14-12-2=0 and row sum 196+14-12-198=0. Every
off-diagonal entry is CN(u,v)+A_uv-2, at least -2. A good field-zero
entry is a multiple of three and is therefore nonnegative. Residue-one
and residue-two minima are -2 and -1.

Since A is symmetric and integer14-regular, AJ=JA=14J, so A commutes
with R and M. Let S be the WHOLE alleged six-vertex support. Every
outside M row and column is zero; the (outside,S) block of AM=MA gives
X M_S=0, where X=A[outside,S]. Every outside binary adjacency word
therefore lies in the literal kernel of M_S. This does not hold if another
nonzero residual component is silently dropped from S.

The signed field row of a degree-four support vertex has c labels 1
and 4-c labels 2. Its zero sum is 8-c=0 modulo three, forcing c=2.
Its exact negative budget is then beta=2*2+2=6. Zero integer row sum
bounds any chosen paired good entry by six and any paired bad entry
by four or five. These upper bounds permit all other bad entries at
their negative minima, and hence apply without assuming saturation.

If distinct u,v in S have identical outside adjacency neighborhoods
of size t, both have internal degree d=14-t. Their internal neighborhood
intersection has size at least max(0,2d-6). Consequently

  CN(u,v) >= 14-d+max(0,2d-6) >= 11.

Thus R_uv=CN+A_uv-2>=9, regardless of the binary value A_uv. This
already contradicts the good upper bound six or the bad upper bound
at most five. It remains only to derive some coordinate equality in
every outside kernel word, using every possible signed octahedral M.

## Independently exhaustive positive-label graph

Every support row has exactly two labels 1, so those edges form a
simple spanning 2-regular graph on six vertices. Every simple component
is a cycle of length at least three. The only partitions of six into
such lengths are six and three plus three. Thus it is a six-cycle or
two triangles. This is an elementary degree argument, not an imported
isomorphism catalogue or an automorphism assumption on A.

In either case the six support nonedges form the given perfect matching
in the sense of three unordered missing pairs. Those pairs cannot be
positive edges. All other support edges not positive have label 2=-1
in the field. Only the field matrix is being signed; the integer R
entries are not replaced by these signs.

### Two positive triangles

Within each three-vertex triangle all pairs are already positive. Every
missing pair therefore crosses the two groups, and the missing pairs
form a bijection between them. Order the second group by that bijection.
For B=J3-I3 the full signed matrix is exactly

  M_S = [[B,-B],[-B,B]].

In GF(3), J3^2=3J3=0. Direct multiplication gives

  (J3-I3)(-I3-J3)=I3-J3^2=I3.

Thus B is invertible. The kernel equation on (p,q) is B(p-q)=0,
so p=q. In particular each missing pair has equal coordinates in every
outside word. Its endpoints have support degree four and fail the
integer budget above.

This proves the needed kernel restriction for every two-triangle
positive labeling. Reversing all field signs also preserves its kernel
and each row's balanced label counts. This field sign reversal changes
no claimed integer residual and supplies no adjacency symmetry.

### Positive six-cycle: exhaustive missing-matching split

Label the cycle 0,1,2,3,4,5 in cyclic order. Its parity classes have
three vertices each. If q missing-matching pairs cross these classes,
the remaining 3-q vertices in each class must be paired internally.
Therefore q is odd: q=1 or q=3.

The only noncycle even-odd pairs are the opposite pairs (0,3), (2,5)
and (4,1), because each cycle vertex has only one opposite-parity
noncycle partner. With q=3 all three are missing. The negative edges
then form the two triangles on the parity classes. Negating this
field matrix reduces its kernel to the preceding triangle case, and
the balanced degree-four integer budget remains the same.

With q=1 the crossing missing pair is an opposite pair. Cyclic
relabeling puts it at (0,3); the two remaining missing pairs are
forced to be (2,4) and (1,5). This exhausts all q=1 arrangements,
including reflections, without asserting an automorphism of A.

I reconstructed the literal signed matrix directly from the positive
cycle and these three missing pairs. The positive edges are
01,12,23,34,45,50; the negative edges are 02,04,13,14,25,35. The result is

  [[ 0, 1,-1, 0,-1, 1],
   [ 1, 0, 1,-1,-1, 0],
   [-1, 1, 0, 1, 0,-1],
   [ 0,-1, 1, 0, 1,-1],
   [-1,-1, 0, 1, 0, 1],
   [ 1, 0,-1,-1, 1, 0]].

For a kernel vector x, its row-1 equation is x0+x2-x3-x4=0 and
its row-5 equation is x0+x4-x2-x3=0. Adding gives 2(x0-x3)=0, so
x0=x3 because two is invertible in GF(3). Row 1 then gives x2=x4;
row 2 gives x1=x5; row 0 finally gives 2(x1-x2)=0. Therefore

  x=(a,b,b,a,b,b).

Conversely that displayed vector makes each of the six literal rows
zero, confirming the exact kernel description without Gaussian
elimination. In particular the missing pair (0,3) has equal outside
coordinates. Its endpoints again contradict CN>=11 versus beta=6.

All positive 2-factors and every compatible missing perfect matching
have now been considered. Each contradicts the actual integer lift.
The precise whole-octahedral statement is therefore independently derived.

## Fourteen written falsification and scope checks

1. Binary simple99/14 assumptions give the exact diagonal and row sums;
   no lambda-one or triangle-incidence premise enters the proof.
2. The block X M_S=0 uses the whole support and actual commutation,
   not an approximate neighborhood similarity or chosen component.
3. Four nonzero row labels sum to zero only when their counts are two
   and two. No all-equal or three-to-one case is silently omitted.
4. Exact minima are -2 and -1. The paired bad entry's own minimum is
   removed from its available negative budget.
5. At m=6 the equal-outside lower CN is eleven, including all outside
   witnesses and allowing either value of A_uv.
6. A simple positive 2-factor has no two-cycle or singleton; only C6
   and C3+C3 are possible at six vertices.
7. Positive triangles force every missing partner across their groups,
   and reordering by that bijection gives the exact signed block matrix.
8. The inverse B(-I-J)=I uses J3^2=0 only over GF(3), not over the
   integers. It gives literal pair equalities, not an assumed M^2 formula.
9. Matching cross parity is odd; every available cross noncycle pair
   is an opposite pair. Both one and three are explicitly considered.
10. Three cross missing pairs leave exactly two negative triangles;
    field sign reversal preserves the kernel but does not negate R.
11. One cross missing pair forces the two same-parity pairs. Every
    matrix entry was independently rebuilt from those missing pairs.
12. Four separate row steps give x0=x3 and x1=x2=x4=x5, and direct
    substitution verifies every vector of that form satisfies all rows.
13. Equal coordinates are translated only to outside A neighborhoods;
    support nonedges are never assumed to be A nonedges.
14. Empty residual stays allowed. Neither a general twelve-defect
    theorem, arbitrary-component exclusion, target resolution, optimum,
    numerical spectrum, executed fixture nor external review is asserted.

The new claim-revision report is a written exact internal verification
record only. No live ledger, index, current publication notice or engine
gate is changed. The candidate's bytes are preserved. My separately
authored twelve-support classification remains CANDIDATE and is not
promoted by this review of ROOT's different discovery.

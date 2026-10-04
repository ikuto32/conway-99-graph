# Independent written audit of the four-class upper Gram

Claim under review:
`C-SEVENTEEN-POINT-FOUR-CLASS-UPPER-GRAM-CLASSIFICATION`, revision 1.
Discovery producer `/root/structural`; upper-Gram question originated with
`/root`. Independent verifier `/root/native_driver`, method
`independent_derivation`. No executed matrix arithmetic, numerical spectrum,
enumeration, optimizer, producer import, formal or external checking occurred.
No ledger, index or source bytes were changed.

The exact source paper is
`docs/CANDIDATE_20261003_SEVENTEEN_POINT_FOUR_CLASS_UPPER_GRAM_V1.md`, SHA256
`1750e24a5d2a5664778efeaf9a86fa9d6774a8f7daee9d87e96c4e614f8dcf67`;
the complete source candidate is
`acceleration/results/20261003_seventeen_point_four_class_upper_gram_candidate01.json`,
SHA256 `742f81eb056a81010764db7cd7f3884e62b5d1fe2c516798db55e933d8055e72`.
Both were whole-read, together with the exact construction and historical
Gram sources listed in the report. The stated inertia table survives the
independent hand reconstruction. A sign orientation in the short witness
must be chosen as specified below; it does not alter the existential witness
or the claim's inertia statement.

## 1. Recover the small graph before using its blocks

The frozen construction has centers s,t; their common neighbor x; four rows
(a_i,b_i,f_i); and two bridge endpoints ell,r. Each row contributes edges
a_i-b_i, a_i-f_i, b_i-f_i. There are the A and B pair matchings, a pair
matching on the four free points f_i, all four s-A and t-B edges, and the
edges s-t, s-x, t-x, x-ell, x-r, ell-r. Each bridge endpoint is adjacent to
the two free points on its side. This totals 36 edges. Centers have degree
6; all fifteen other points have degree 4.

The PA,PB,PR partitions are the three named pair matchings pulled back to
the same four rows. The construction theorem's four patterns can be used
without assuming any target automorphism. Row permutations simultaneously
permute the three pair partitions, and exchanging the centers exchanges
PA/PB while preserving PR's distinguished role. For the present calculation,
the actual three matchings on four rows commute: after naming one row 0,
their three involutions are exactly addition by the three nonzero elements
of a Klein four group. Its constant row vector and three sign characters
therefore diagonalize all the matchings simultaneously.

Every character has two plus and two minus signs. Normalize its four row
coordinates by division by 2, separately on A,B and free points. The
nonconstant row characters have zero sum, so the centers do not couple to
them. When PR acts by minus one, each PR-side sum is zero and neither bridge
endpoint couples to that free character. When PR acts by plus one, the
character is constant on the two sides with opposite signs. The corresponding
free vector has dot product sqrt(2) with the image of the normalized endpoint
difference (ell-r)/sqrt(2): four equal contributions are 1/(2sqrt(2)).
This verifies the coupling coefficient rather than assuming it.

There are two uncoupled character spaces of dimension 3, one character plus
endpoint-difference space of dimension 4, and the common constant space of
dimension 7. They are mutually orthogonal and account for all 17 dimensions.
The J term vanishes on the first ten dimensions, including the endpoint
difference. It does not vanish on the whole common block.

## 2. Derive the universal upper Gram independently

For a hypothetical target, A squared equals 12I-A+2J, AJ=JA=14J and
J squared equals 99J. Direct expansion of G=27I-9A+J gives

    G squared = 1701I-567A+63J = 63G.

Symmetry then gives v^T G v = ||Gv|| squared /63 >=0 for every real v.
Every principal submatrix is PSD by extending its vector by zeros. Also
G/63 is an orthogonal projection and trace(G)=99*28=2772, so its rank is
44. This is the archived target upper-Gram theorem, not a new rank premise.
For an exact induced H, G[H]/9 is U(H)=3I-H+J/9. A negative quadratic
therefore forbids only an induced copy with exactly that H adjacency.

## 3. Recheck every nonconstant block and sign

For a nonconstant character let alpha,beta,gamma be its matching signs.
The adjacency on its A,B,free coordinates has those diagonal entries and
off-diagonal entries 1. If gamma=-1, its U block is the K3 Laplacian plus
diag(1-alpha,1-beta,2). The Laplacian is PSD with only the constant line
as kernel; the last added positive entry kills that kernel. Both uncoupled
blocks are therefore positive definite in every class.

For the unique gamma=+1 character, the endpoint-difference adjacency
diagonal is -1 (the bridge edge), so its U diagonal is 4. Its only coupling
is minus sqrt(2) to the free coordinate. Eliminating this positive endpoint
pivot reduces the free U diagonal from 2 to 2-2/4=3/2. The remaining
three-by-three matrix has diagonal (3-alpha,3-beta,3/2) and all its
off-diagonal entries minus one.

The leading A,B block is positive definite in all four sign cases. Its
determinants are 3,15 or 7. The sum of its inverse entries is respectively
2 for (+,+), 2/3 for (-,-), and 8/7 for (+,-) or (-,+). Consequently the
last congruence pivot is respectively -1/2, 5/6 or 5/14. These are exact
rational signs, with no numerical square-root approximation.

For the PR-plus character, PA=PB=PR gives (+,+); PA=PB different from PR
gives (-,-); PR equal exactly one gives the two mixed cases; and all three
different gives (-,-). Thus the four-dimensional block has (3,1,0) inertia
only in the first class, and (4,0,0) in each other class. This checks both
mixed-sign orientations and the repeated (-,-) entry of the table.

## 4. Reconstruct and check the entire common block

The common space consists of coordinates s,t,x, constant A,B, constant free,
and equal ell,r. Its restricted operator is invariant under exchanging the
center/A coordinate with the center/B coordinate even when that exchange
alone is not an automorphism of the whole graph. This is a symmetry of the
restricted constant-coordinate matrix, which suffices for the even/odd split.

For the odd part put s=-t=c, A=-B=p and all other coordinates zero.
Its norm is 2c squared +8p squared and the adjacency quadratic is
-2c squared +16cp. Its U quadratic is therefore
8c squared -16cp+24p squared. In normalized coordinates this is
[[4,-2],[-2,3]], with determinant 8 and positive first pivot.

For the even part put s=t=c, x=z, ell=r=e, A=B=p and free=f. The sum of
edge products is

    c^2+2cz+8cp+8p^2+2f^2+4ef+e^2+2ze+8pf.

The norm is 2c^2+z^2+2e^2+8p^2+4f^2. Thus 3I-H has the exact quadratic
coefficient matrix

    B = [[4,-2,0,-8,0],[-2,3,-2,0,0],[0,-2,4,0,-4],
         [-8,0,0,8,-8],[0,0,-4,-8,8]],
    j = (2,1,2,8,4)^T.

The J contribution is (j^T(c,z,e,p,f)) squared /9. All coefficients were
recovered from the edges above, independently of the supplied B matrix.

Eliminating the z pivot 3 leaves on c,e the matrix
(4/3)[[2,-1],[-1,2]], whose inverse is [[2,1],[1,2]]/4. The p/f coupling
columns to c,e are (-8,0) and (0,-4). Their inverse-form corrections are
32,8 and 8 on the two diagonals and off-diagonal. The remaining p,f block
is therefore [[-24,-16],[-16,0]], with determinant -256. This gives one
positive and one negative pivot, so B has inertia (4,1,0) and is nonsingular.

The displayed candidate for B^-1j is
v=(-11/8,-3/4,-1/4,-3/4,-3/8). Its five row products are, in order,

    -11/2+3/2+6 = 2;
    11/4-9/4+1/2 = 1;
    3/2-1+3/2 = 2;
    11-6+3 = 8;
    1+6-3 = 4.

These verify Bv=j. The dot product j^T v is -23/2. For the bordered matrix
[[B,j],[j^T,-9]], eliminating B gives the positive scalar 5/2 and hence
inertia (5,1,0). Eliminating the negative pivot -9 instead gives
diag(-9,B+jj^T/9), proving the even five-dimensional block positive definite.
The sign of the rank-one update is plus, not minus. Together with the odd
two-dimensional block, the common seven-dimensional block is PD for every
partition pattern.

Combining 3+3+4+7 dimensions gives exactly (16,1,0) for all-equal and
(17,0,0) for each other pattern. There are no omitted or zero directions.

## 5. Independently count the negative witness and its orientation

Choose chi=+1 on the common PR pair whose free points meet ell, and -1
on the pair whose free points meet r. This is an allowed choice of the
paper's "one common partition pair". Give A,B,free points value 2chi,
ell value 1, r value -1 and the other three points value zero. Its total
sum is zero and its squared norm is 50. The three pair matchings contribute
24 to the edge-product sum; the three sets of four row-triangle edges
contribute 48; endpoint/free edges contribute 8; and the bridge contributes
-1. Thus the edge-product sum is 79 and w^T U w=150-158=-8, or -72 for G.

The orientation matters: reversing chi alone while retaining ell=1,r=-1
changes the endpoint/free contribution to -8, giving total 63 and quadratic
24. Therefore the short negative witness must align chi with the named
endpoint signs, or reverse both together. This is a sign-choice clarification,
not a counterexample to the existence of the negative witness or to the
independently verified block inertia.

An added edge changes this quadratic by -2w(u)w(v). Opposite-sign endpoints
can increase it. Therefore an edge-containing copy does not inherit the
negative value, and extra internal edges are not covered. Conversely the
other three PD classes merely pass this necessary principal test; no target
extension, integer completion, exhaustive target occurrence or global graph
exclusion is proved.

## 6. Dependencies, shared origins and limits

The exact four-class construction r1 and historical target-upper-Gram r1
are the two stated mathematical dependencies. The construction paper and
its accepted written packet were read; this audit reconstructs the literal
small graph and pattern signs without taking any raw5184 replay as a premise.
The historical upper-Gram proof a450e7 was whole-read and reconstructed
above. Closed28 upper-Gram redundancy 7e925f and triangle39 Gram/SOS 1dead1
were read for overlap; their complete-neighborhood assumptions are not
silently used for these degree6 centers. No novelty or exhaustive literature
search is asserted. Shared Root question, Structural proof and these written
archives are disclosed rather than represented as independent external input.

Fourteen written falsification boundaries were checked: edge inventory;
simultaneous matching basis; endpoint sqrt(2) normalization; all17 dimensions;
J only on common coordinates; both mixed theta signs; final theta pivots;
common edge-count coefficients; odd restricted symmetry rather than target
automorphism; B nonsingularity; all five Bv products; bordered update sign;
short-witness orientation; and induced/extraedge versus completion scope.
There were zero executed control cases. No actual saved adjacency matrix,
472-type inverse or pair population was computed. This report authorizes no
execution and makes no ledger or target-resolution transition.

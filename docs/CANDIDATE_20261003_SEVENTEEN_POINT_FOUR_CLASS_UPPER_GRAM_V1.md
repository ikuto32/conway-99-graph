# Candidate: exact upper Gram distinction among the four defined 17-point classes

Claim `C-SEVENTEEN-POINT-FOUR-CLASS-UPPER-GRAM-CLASSIFICATION`, revision 1.
Basis DERIVED; status CANDIDATE; review NEEDS_RECHECK. Written by
`/root/structural` from the upper-Gram question proposed by `/root`.
No source execution, matrix-arithmetic worker, numerical spectrum, formal or
external verification is asserted. This is a new paper for different-author
review, not approval of its author's derivation.

## Exact statement and scope

Let H be precisely one of the 17-point edge unions defined in
`CANDIDATE_20261003_SEVENTEEN_POINT_FAMILY_FOUR_CLASSES_V1.md`, SHA256
`1faee8e574557fcbb75847e92dbfb6c8e5efd125a2f660b406641e4ed9104ed9`.
Thus its vertices are s,t,x, four A points, four B points and two three-point
sides L,R; the twelve triangles are exactly the displayed negative seven and
positive five in that paper. No additional edges are included. Pull the B
pairing and free-side pairing back to the four A-B matching rows, obtaining
the named pair partitions PA,PB,PR.

Set U(H)=3I17-H+J17/9. Then:

| Named partition pattern | Inertia of U(H), positive/negative/zero |
| --- | --- |
| PA=PB=PR | (16,1,0) |
| PA=PB different from PR | (17,0,0) |
| PR equal exactly one of PA,PB | (17,0,0) |
| PA,PB,PR all different | (17,0,0) |

Consequently the exact first-class edge union cannot be an induced principal
subgraph of a (99,14,1,2) target. The other three classes pass this one principal
positivity condition. Passing does not prove a target extension. This statement
does not cover extra internal edges, target-family coverage, an automorphism
of an unknown target, or a global graph exclusion. It does not claim class
multiplicities or small-graph automorphism orders.

The mathematical dependencies are the revision-1 four-class construction
theorem and the historical revision-1 target upper Gram PSD theorem
`C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS`. The calculations below separately
derive the necessary target identity and each small-block sign.

## Historical target Gram premise

For the exact target identity A²=12I-A+2J, regularity gives AJ=JA=14J and
J²=99J. Set G=27I-9A+J. Expansion gives G²=63G, whence
xᵀGx=||Gx||²/63>=0. Therefore every principal matrix is PSD, and G/9 is
3I-A+J/9. This is the already archived upper Gram, not a new general premise.
Its target rank is 44; no new rank bound is claimed here. The small proof below
uses exact quadratic/congruence algebra, not approximate eigenvalues.

## A short exact negative direction for the first class

Write f_i for the free L/R point attached to matching row (a_i,b_i), and ell,r
for the bridge endpoints. When PA=PB=PR, put chi_i=+1 on one common partition
pair and -1 on the other. Define an integer vector w by

    w(s)=w(t)=w(x)=0,
    w(a_i)=w(b_i)=w(f_i)=2 chi_i,
    w(ell)=1, w(r)=-1.

The sum of coordinates is zero and ||w||²=12*4+2=50. The sum of products
w(u)w(v) over the edges is 79: the A, B and free-side matchings contribute
8 each; the A-B, A-free and B-free matching edges contribute 16 each; the four
endpoint-free edges contribute 8; the bridge contributes -1. Edges through
s,t,x contribute zero. Thus

    wᵀU(H)w = 3*50-2*79+0 = -8,
    wᵀ(27I-9H+J)w = -72.

This is already a strictly negative exact witness, without a spectrum.
Extra edges between opposite-sign coordinates could increase this quadratic,
so they have not been silently excluded by the witness.

## Complete invariant decomposition

Relabel the four matching rows as a four-element Klein group. Each unordered
pair partition is one of the three fixed-point-free matching involutions.
These commute. The constant vector and three real sign characters form an
orthogonal basis on four rows; each nonconstant character has two +1 and two
-1 entries and is normalized by division by 2. A matching acts by +1 on one
of these characters and -1 on the other two.

This is only a choice of basis of the explicitly defined small matrix; no
target automorphism or additional graph symmetry is assumed. For a character
write alpha,beta,gamma for its PA,PB,PR signs. The only character coupled to
the difference of the bridge endpoints is the one with gamma=+1; call it theta.
All other nonconstant characters have gamma=-1, and their endpoint sums vanish
on each side. The all-one J term vanishes on every such zero-sum subspace.

There are two uncoupled three-dimensional blocks, one four-dimensional theta
block, and a seven-dimensional common block: 3+3+4+7=17. Every edge of H maps
each displayed subspace into itself, using exactly the matching edges,
center-to-A/B edges and endpoint-to-side edges in the frozen construction.

### Two uncoupled blocks

For either gamma=-1 character, H on the A,B,free coordinates is

    [[alpha,1,1], [1,beta,1], [1,1,gamma]].

Its U block has diagonal 3-alpha,3-beta,3-gamma and off-diagonal -1.
It is the K3 Laplacian plus diagonal (1-alpha,1-beta,1-gamma).
All added entries are nonnegative and the last is 2. The Laplacian kernel is
the constant line, where that added entry is nonzero. Therefore both blocks
are positive definite for every partition pattern.

### Theta and endpoint difference

Use the normalized endpoint difference (ell-r)/sqrt(2). The theta block of H
is

    [[alpha,1,1,0], [1,beta,1,0],
     [1,1,1,sqrt(2)], [0,0,sqrt(2),-1]].

The endpoint diagonal in U is 4. Eliminating it by exact congruence leaves

    [[3-alpha,-1,-1], [-1,3-beta,-1], [-1,-1,3/2]].

Its leading two-dimensional block is PD. Eliminating that block leaves one
scalar, as follows:

| Pattern | (alpha,beta) for theta | Last Schur scalar |
| --- | --- | --- |
| all equal | (+1,+1) | 3/2-2 = -1/2 |
| PA=PB different from PR | (-1,-1) | 3/2-2/3 = 5/6 |
| PR equal exactly one | (+1,-1) or (-1,+1) | 3/2-8/7 = 5/14 |
| all different | (-1,-1) | 5/6 |

For example, the (+1,-1) leading block has inverse
[[4,1],[1,2]]/7, whose entries sum to 8/7. The (-1,-1) inverse entries sum
to 2/3. Thus theta has inertia (3,1,0) in the first class and is PD in each
other class. This also establishes that the short negative witness accounts
for exactly one negative direction once the common block is checked.

### The same seven-dimensional common block for every class

All A coordinates are constant, all B coordinates constant, all free coordinates
constant, and the bridge endpoints equal. Partition choices do not affect the
induced operator. Split this subspace by exchanging s/A with t/B. The odd
two-dimensional part has zero sum; in normalized center and A-B difference
bases its U matrix is [[4,-2],[-2,3]], which is PD (leading entry 4, determinant
8).

In the remaining five-dimensional part set s=t=c, x=z, ell=r=e, all A/B
coordinates p and all free coordinates f. The exact quadratic is

    (c,z,e,p,f) B (c,z,e,p,f)ᵀ + (2c+z+2e+8p+4f)²/9,

where the symmetric coefficient matrix and sum vector are

    B = [[4,-2,0,-8,0], [-2,3,-2,0,0], [0,-2,4,0,-4],
         [-8,0,0,8,-8], [0,0,-4,-8,8]],
    j = (2,1,2,8,4)ᵀ.

These coefficients follow by counting the explicit edges; no actual saved
17-matrix has been multiplied by a program. Eliminate z with pivot 3. The
c,e block becomes (4/3)[[2,-1],[-1,2]], a PD block with inverse
[[2,1],[1,2]]/4. Its elimination leaves the p,f block
S=[[-24,-16],[-16,0]], determinant -256, hence one sign of each kind.
Thus B is nonsingular with inertia (4,1,0).

For completeness, solving these displayed hand equations gives

    B⁻¹j = (-11/8,-3/4,-1/4,-3/4,-3/8)ᵀ,
    jᵀB⁻¹j = -23/2.

The five products B(B⁻¹j)=j can be checked directly row by row. Consider the
bordered symmetric matrix [[B,j],[jᵀ,-9]]. Eliminating B leaves scalar
-9-jᵀB⁻¹j=5/2, so its inertia is (5,1,0). Eliminating the negative scalar
-9 instead leaves B+jjᵀ/9. Consequently that five-dimensional matrix has
inertia (5,0,0). Together with the odd two-dimensional part, the entire common
block is positive definite. Counting all invariant blocks proves the table.

## Archive overlap, provenance and boundaries

Root proposed applying the historical upper Gram to these four classes after
the lower Gram one-type redundancy. Structural derived the new negative vector
and the exact block classification above. Root's four-class mechanism and
Structural's earlier independent bridge correction are shared background,
disclosed in the frozen four-class paper and separate audit. No agreement with
Root is independent approval of this new derivation.

Read-only archive inspection found the universal target Gram already derived
in `docs/DERIVATION_20260930_TARGET_GRAM_NOGOODS.md` (SHA256
`a450e71f0d566c218123b831a6ad07b3b2bd17e8c78edaab2cb380d306693153`).
Closed28 redundancy is separately in
`acceleration/theory_20260930_closed28_gram_redundancy.md` (SHA256
`7e925f56b520e6b06aa028b252aa7d4137b41071730ae5e0dbc873dcf97e7407`),
and triangle39 redundancy in `docs/DERIVATION_20260930_TRIANGLE39_GRAM_SOS.md`
(SHA256 `1dead12449d33270d3adca585fc44616d4865bfe8fbe9532b7412861cbd544fb`).
Their complete-neighborhood/cubic assumptions do not hold for these centers
of degree6. The inspected current 17-point circuit and family sources do not
perform this full target upper Gram test. This bounded archive inspection is
not a novelty claim or an exhaustive literature search.

Written falsification boundaries include the bridge's -1 contribution, all
17 dimensions, J vanishing only on zero-sum blocks, matching signs when two
partitions coincide, both choices in the third class, exact Schur determinant
signs, nonsingular B, the rank-one update sign, and the distinction between
an induced edge union and an edge-containing subgraph. A singleton type test,
local CN validity or the older inertia of H-3I cannot replace these checks.
There are zero executed mathematics, formal-proof or external-review controls.
An independent written audit must bind this exact revision before any claim
promotion. No ledger, index, source gate or target status is changed.

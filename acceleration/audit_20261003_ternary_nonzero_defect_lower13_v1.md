# Independent written audit: nonzero ternary defect count is at least thirteen

Discovery producer `/root`; verifier `/root/checkpoint_audit`. The frozen
discovery is `docs/CANDIDATE_20261003_TERNARY_NONZERO_DEFECT_LOWER13_V1.md`,
SHA256 `440e68ac8c857295cc8e6177d556615432e9ef9f646d1d110d133bb5a12a4c27`.
I read every candidate, independent audit and report in all four pinned
revision-1 packages. A truncated initial read was completed by separate
nontruncated reads before this verdict. Every one of their thirteen direct
input hashes was freshly checked. No producer program, numerical spectrum,
support catalogue, mathematical execution, fixture or formal prover was used.
The accompanying report records the actual review clock; creation/start times
are unavailable. Current source context is `63437c9b9fc2dd58b3bdfb51fc347b880b397503`,
without an assertion that these working artifacts occur in that commit.

## Exact statement and four material premises

For every symmetric binary integer 99-by-99 matrix A with zero diagonal and
every integer row sum exactly14, define R=A^2+A-12I-2J over the integers,
M=R modulo3 over GF(3), and F3 as the number of unordered off-diagonal
nonzero entries of M. Then F3=0 or13<=F3<=4851.

The four dependencies, all revision1 and relation `uses_result`, are:

1. `C-UNRESTRICTED-DEGREE14-TERNARY-NONZERO-DEFECT-LOWER12`.
   Candidate `8af2f38aeb004b5d485b8596f10d04caf1d3bb061d03885031641a9b8ebcdd25`,
   audit `74fa37e72d3c2b44ee054933d06f887baf3bb2c4d9370fa1f09aa993973fb7a6`,
   report `b5cb1f515ff8f36dd9b18c57208c7b12540a6750e375ca932be3906ccaed5ea0`.
2. `C-UNRESTRICTED-DEGREE14-TERNARY-TWELVE-DEFECT-SUPPORT-CLASSIFICATION`.
   Candidate `8a773e82bdd4bc7255f960deb93717c27c8ade0fab8a1fb4017e05a68e09384e`,
   audit `a53823f058201aca934349d79c049cea4762672d5d2574aa7327c4946205666b`,
   report `a54c3eab6419ba0ce4e563c52444fd3d748d2e0687640b9bed81d1fe087da707`.
3. `C-UNRESTRICTED-DEGREE14-TERNARY-WHOLE-K2-6-SUPPORT-NONREALIZABILITY`.
   Candidate `4efb2e1ffbcf4bf8c310c3521b175e570b93e1ed7ef18d20cbecaf05dea55260`,
   audit `2b8dad64a3d15443ddca45ddd4946ccc5aa215a7739a9d9f234b4c7f4873bd7d`,
   report `0301d9591b261b3cf1b29f1f51bd52b0233126ea2bf01dfa2e0721e2e9cd8832`.
4. `C-UNRESTRICTED-DEGREE14-TERNARY-WHOLE-OCTAHEDRAL-SUPPORT-NONREALIZABILITY`.
   Candidate `4fe0d18e60d62af2b6c95a784b4bf4201168aa4cfdc141e1681f8561b9cbbd5a`,
   audit version2 `812014ddb5aa877ab4a0ae83e5371a49f32adf40b22894f80b882c32fc8ce9fe`,
   report `7320feba0d6e86e6691fbef55daab95b561829d659fe9365242f8afbb9676a97`.

Full paths accompany these pins in the report. Their definitions, complete
99/14 domain and whole-support quantifiers agree. The first two discoveries
are Structural-produced and ROOT-verified; the last two are ROOT-produced
and Structural-verified. This verifier produced none of those four discoveries
or audits. Their earlier common filter is reconstructed below, rather than
silently added as a fifth material dependency. My engineering/registrar
authorship supplies no mathematical evidence for ROOT's combined discovery.

## Independent common identities and budget calculation

The diagonal of R is14-12-2=0. Since A1=14*1, its row sum is
196+14-12-198=0. For u!=v, R_uv=CN(u,v)+A_uv-2>=-2. A residue-zero
entry is therefore a nonnegative multiple of3. Residues1 and2 have exact
integer minima -2 and -1. A support row with c1 and c2 such entries has
negative allowance beta=2c1+c2. Its field row equation c1+2c2=0 makes
beta divisible by3, and beta<=3*floor(2d_H/3). Isolating one paired entry
gives upper bounds beta, beta-2 and beta-1 at residues0,1 and2 respectively.
The last two subtract that entry's own potential negative allowance.

AJ=JA=14J, so A commutes with R and M. Let S be the WHOLE nonisolated
support set, m=|S|. All outside M rows and columns are zero; hence
X*M[S,S]=0 for X=A[outside S,S]. A support-degree2 row has opposite
nonzero labels and forces its two neighbors' outside coordinates equal.
A degree3 row has three equal labels. Three binary coordinates with zero
sum modulo3 are all0 or all1, again giving equality. This uses binary
adjacency coordinates, not arbitrary ternary kernel words.

If u,v in S have equal outside neighborhoods of size t, their internal
degrees both equal d_A=14-t. Their inside intersection is at least
max(0,2d_A-m), so

  CN(u,v)>=14-d_A+max(0,2d_A-m)>=14-floor(m/2).

The minimization holds for both parities: below m/2 the bound decreases
with d_A, above m/2 it increases, and the integer choices straddling the
midpoint give14-floor(m/2). At m<=11 this gives R_uv>=7. A support
endpoint of degree<=4 has good budget<=6 and bad paired budget<=5.
Thus both endpoints of an equal-outside pair must have support degree>=5.
Finally, degree1 cannot satisfy a nonzero field row sum. These identities
use no lambda-one, triangle, automorphism or connected-support premise.

## Rechecking the complete lower12 premise

For1<=e<=11, minimum support degree2 gives m<=e<=11 and total degree<=22.
A degree3 vertex and its three high neighbors cost at least2m+10. Simplicity
of a degree>=5 neighbor requires m>=6; the total requires m<=6. At m=6
the three highs are universal and the exact forced degrees are(5,5,5,3,2,2).
Either degree2 vertex would meet all three highs, a contradiction.

A degree2 vertex has two high neighbors and costs at least2m+6, forcing
6<=m<=8. With no degree3:

* m=8 forces(5,5,2,2,2,2,2,2); the six lows each join both highs, already
  exceeding the high degree5.
* m=7 allows only two highs and at most one degree4 medium. Saturated lows
  leave a medium at most its two high neighbors. Thus all five lows are
  degree2, giving K2,5 with or without the high-high edge.
* m=6 makes the two highs universal. Three highs would force every remaining
  degree>=4 and exceed22. With two highs there are at most two degree4
  mediums; each can meet only the highs and the other medium, at most3.
  The result is K2,4 with its necessary high-high edge.

Without degree2 or3, minimum degree4 and the total force m=5 and support K5.
Orders smaller than5 cannot meet either high-neighbor requirement or min4.
Thus these four shapes exhaust all nonempty supports with at most11 edges,
including disconnected possibilities; connectivity was not assumed.

For K2,r plus the high edge, each low row cancels its opposite high labels.
Adding the two high row sums leaves twice the nonzero high-edge label,
impossible in GF(3). For K2,5 without that edge, c residue-one incidences
at one high satisfy10-c=0 modulo3, so c=1 or4. High budgets are6 and9;
their equal outside neighborhoods make their good pair R>=9, exceeding6.
For K5 each row has two labels of each residue, and label-one edges form C5.
The signed matrix B squares to5I-J (diagonal4, both cyclic off-diagonal
product sums -1). Over GF(3), Bx=0 implies2x=Jx; hence x is constant.
All outside neighborhoods coincide and the degree4 budget fails. No actual
support with1..11 edges remains. The lower12 premise is sound in its scope.

## Rechecking every twelve-edge classification branch

At e=12, total degree24 and min2 give m<=12; simplicity gives m>=6.
For m=12 all degrees are2. A degree2 row's two degree2 neighbors have equal
outside words and CN>=8/R>=6, exceeding their good budget3 or bad budget<=2.
This is a separate boundary calculation, not an extension of the min5 filter.

At m<=11, a degree3 vertex requires2m+10<=24, so m=6 or7. At m=6
universal highs force(5,5,5,3,3,3). At m=7 exact equality forces
(5,5,5,3,2,2,2). Its nine low-high incidences leave six high-high incidences,
forcing the high triangle. In both cases the three highs have equal outside
words, CN>=11/R>=9, while a degree5 BAD pair has upper bound<=8. Both fail.

With degree2 but no degree3, 2m+6<=24 gives6<=m<=9. Writing h>=2 for highs
and r for degree4 mediums, excess above2m is at least3h+2r. Every degree2
vertex is saturated by two highs.

* m=9 forces two degree5 highs and seven lows, giving impossible high degree>=7.
* m=8 permits two highs and at most one medium. The medium cannot reach4;
  six lows joined to two highs leave K2,6. A high edge would be edge13.
* m=7 with three highs forces high degrees(6,5,5). Eight low-high incidences
  leave eight internal-high incidences, exceeding the available six. With two
  highs, at most two mediums each have at most three available neighbors.
  Without mediums the edge count is10 or11, rather than12.
* m=6 has exactly two universal highs: three or more would cost at least27.
  The other degrees are(4,4,4,2), and the mediums form a triangle. This is a
  genuine twelve-edge shape, not a degree-count contradiction. Its low forces
  the adjacent highs' outside words equal; R>=9 exceeds their bad bound8.

Without degree2 or3, minimum degree4 and total24 force m=6, all degrees4.
The complement has degree1 and is a perfect matching. Orders6..12 and all
degree alternatives were covered without selecting a component. The complete
whole support is therefore K2,6 or K6 minus a perfect matching, as claimed.

## Rechecking the forced K2,6 integer lift by a distinct norm certificate

Let a,b be the highs and L the six lows. Their outside neighborhoods agree.
At m=8 their CN>=10, so the good R_ab, after residue rounding, is>=9.
If c counts residue-one high incidences at a, its field row gives12-c=0;
c=0,3,6 and high budgets are6+c,12-c. Unbalanced c fails budget6. Balanced
c=3 forces R_ab=9 and uses each high's full allowance9. Every high-low entry
therefore equals its own minimum, -2 or -1, and every other good high entry is0.

Each outside row is entirely good, nonnegative and sums0, so the WHOLE integer
row vanishes. Each low's two high residuals sum -3. Exactly one other low has
residual3; symmetry and zero diagonal force a perfect matching P with P^2=I.
Let s have three +1 and three -1 entries, recording the high-low -2/-1 order.
The exact high-low rows are -3*1/2-s/2 and -3*1/2+s/2; the low block is3P.
This is forced integer data, not an arbitrary residue lift or matching choice.

The two-dimensional real subspace U, constant on the two highs and on the six
lows separately, is invariant. Its coordinate action is(9x-9y,-3x+3y), with
distinct eigenvalues0 and12. The integer eigenvector z has value -3 at a,b,
+1 at every low and0 elsewhere. Its sum is0 and Rz=12z.

On U's orthogonal complement inside S, v has highs(x,-x) and low vector l
with sum0. Direct expansion gives

  ||v||^2=2x^2+||l||^2,
  Q=v^T Rv=-18x^2-2x*s^T*l+3l^T*P*l.

I use the following independently expanded certificate, sufficient to exclude
eigenvalue12 there without relying on the earlier audit's numerical bound4:

  12||v||^2-Q =36x^2+||l+x*s||^2+8||l||^2+(3/2)||l-P*l||^2.

The equality uses ||s||^2=6 and P=P^T=P^{-1}; expanding both sides gives
42x^2+12||l||^2+2x*s^T*l-3l^T*P*l. The right side is strictly positive
for every nonzero v. Hence12 is not an eigenvalue on this invariant six-
dimensional complement. The91 outside coordinates have eigenvalue0, so12 is
simple in the full99-dimensional R, not just in a two-dimensional quotient.

Since A commutes with R, Az=theta*z. A low coordinate z_i=1 makes theta
integer. Jz=0 and the actual polynomial give theta^2+theta-24=0, equivalently
(2theta+1)^2=97. As81<97<100, no integer theta exists. Whole K2,6 is impossible.
An abstract zero-row, cube-nilpotent signed K2,6 remains algebraically valid;
the obstruction is its integer adjacency-polynomial lift, not that field example.

## Rechecking all signed octahedral lifts

Every support-degree4 row must have two labels1 and two labels2, giving
budget6. Label-one edges form a simple spanning2-factor on six vertices:
only C3+C3 or C6. Missing support pairs are exactly one perfect matching.

For two positive triangles the matching necessarily crosses the groups.
Ordering by that matching gives M_S=[[B,-B],[-B,B]], B=J3-I3. Over GF(3),
B*(-I3-J3)=I3 since J3^2=0. Thus every kernel word has equal coordinates on
each missing pair. Those vertices have equal outside A-neighborhoods; CN>=11
forces their good residual>=9, contradicting budget6.

For a positive6-cycle, parity classes each have three vertices. The number q
of missing cross pairs must be odd, hence1 or3. Available noncycle cross pairs
are exactly the three opposite pairs. At q=3, negative edges are two triangles,
reducing by field sign reversal to the preceding kernel argument. At q=1,
cyclic relabeling places the sole cross pair at03, and the others are24,15.
The signed matrix rows1 and5 sum to2(x0-x3)=0; row1 then gives x2=x4,
row2 gives x1=x5, and row0 gives x1=x2. Every kernel word is(a,b,b,a,b,b),
and direct substitution satisfies all six rows. In particular missing pair03
has equal outside neighborhoods and violates budget6 as above.

This exhausts all2-factors and compatible missing matchings. Relabeling and
field sign reversal enumerate labels; they assert no automorphism of A or
negation of its integer residual. Whole octahedral support is impossible.

## Exact composition and eighteen written counterattacks

F3 is an integer between0 and99*98/2=4851. If nonzero, the first reviewed
premise gives F3>=12. At F3=12, the second gives its WHOLE support as exactly
one of the two shapes; the third and fourth each contradict its actual lift.
Consequently F3!=12, and integer discreteness gives F3>=13. No premise is
applied to an arbitrary component, and no repeated exclusion is counted as a
realization, search denominator or executed fixture.

The eighteen written boundary checks are: common99/14 definitions; integer
row/diagonal identities; residue minima and paired allowance subtraction;
binary-only degree3 propagation; whole outside-zero commutation; both parities
of the CN bound; degree1 exclusion; complete1..11 shape exhaustion; signed
K5 square/kernel; m12 separate degree2 budget; every e12 low-degree branch;
the retained(5,5,4,4,4,2) shape; K2,6 unbalanced/balanced saturation; forced
matching and all outside integer rows; full-dimensional simple12 certificate;
primitive eigenvector/integer theta/nonsquare97; all signed octahedral cycle-
matching cases; and integral composition with empty support and unknown13
realizability retained. These are written checks, not executed controls.

**PASS** for the exact revision1 necessary bound with exactly the four pinned
material dependencies. This is an internal different-author written derivation,
not a formal proof or external review. Trusted components are ordinary exact
integer/GF(3) arithmetic, finite simple-graph degree arguments, real sums of
squares and symmetric spectral decomposition. Novelty and sharpness remain
UNKNOWN. There is no target graph, general nonexistence, automorphism,
lambda-one assumption, incidence rank, whole-trajectory or heuristic gate claim.
F3=0 remains possible;13 is not asserted attainable or excluded.

The original candidate/packages were preserved. No mathematical program,
fixture, graph realization, formal prover, ledger or index mutation occurred.
Metadata reads/hashes and saving this written record are not theorem computation.
Current ledger/index hashes are historical observations only, not immutable
mathematical premises. All new records stay LOCAL_ONLY and outside the frozen
371-claim publication cutoff until separately authorized registration/publication.

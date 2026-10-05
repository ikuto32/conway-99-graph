# Independent written audit: the two twelve-defect whole supports

Verifier `/root`; discovery producer `/root/structural`. The complete candidate
read is `docs/CANDIDATE_20261003_TERNARY_TWELVE_DEFECT_SUPPORT_CLASSIFICATION_V1.md`,
SHA256 `8a773e82bdd4bc7255f960deb93717c27c8ade0fab8a1fb4017e05a68e09384e`.
Source context is `63437c9b9fc2dd58b3bdfb51fc347b880b397503`. This is exact
written different-author verification, with zero executed mathematical commands,
fixtures, catalogue enumerations, numerical spectra or formal-prover checks.
The accompanying report records its actual review clock; the start time is
unavailable and no file-creation time is inferred.

## Revision-1 statement independently checked

For every symmetric binary integer 99-by-99 matrix A with zero diagonal and
every integer row sum fourteen, define R=A^2+A-12I-2J and M=R mod3. If the whole
nonzero unordered off-diagonal support H of M has twelve edges, H is isomorphic
to K2,6 or K6 minus a perfect matching. This is a necessary shape classification,
not realization of either shape, an arbitrary-component claim or general
twelve-defect exclusion. No adjacency automorphism is assumed.

The sole material dependency is revision1 of
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`, report
`acceleration/results/20261003_independent_review/ternary_equal_outside_nine_01/equal_outside_filter/summary.json`,
SHA256 `7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`.
ROOT independently derived that filter previously. No lift, defect lower bound,
incidence-rank statement or support catalogue is a premise of this audit.

## Independent reconstruction of the exhaustive branches

R has diagonal zero and row sums zero. Every good entry is a nonnegative
multiple of three; bad residues1/2 have minima minus2/minus1. At support degree d,
the negative budget beta is a multiple of three and at most3*floor(2d/3).
A good paired term is at most beta, a bad paired term at most beta minus2 or1.

AM=MA, and all outside-support M rows vanish. Thus every binary adjacency row
from outside into the whole support lies in ker M. A support-degree2 row forces
its two neighbors' outside words equal; a support-degree3 row forces all three
equal because their common signed sum of three binary bits is zero modulo3.
At whole support order m<=11 equal outside words have CN>=14-floor(m/2), giving
R>=7. A degree-at-most4 endpoint has good budget at most6 and bad budget at
most5, so all such neighbors must have support degree at least5.

Since the field rows sum to zero, degree1 is impossible. With e=12 and total
degree24, minimum degree2 gives m<=12. Simplicity gives m>=6 since five vertices
have at most10 edges. These are bounds on the whole support, regardless of
connectivity or component count.

At m=12 every degree is2. A degree2 row forces its two degree2 neighbors'
outside words equal. Now CN>=8 and R>=6, exceeding either good budget3 or bad
budget at most2. This excludes m=12 without wrongly applying the degree4
filter at its unsupported boundary.

If there is a degree3 vertex, its three neighbors are highs of degree>=5.
The total is at least3+15+2(m-4)=2m+10, so m<=7. At m=6 the highs are universal;
every other vertex has degree>=3, and total24 forces degrees(5,5,5,3,3,3).
At m=7 equality forces(5,5,5,3,2,2,2). All low incidences go to the highs and
total9; the high sum15 leaves6 internal high incidences, so all three high-high
edges are present. In both cases the chosen degree3 row forces the three highs'
outside neighborhoods equal. Their high-high pairs are bad, CN>=11, hence R>=9.
Their degree5 budgets are at most9 but their bad paired bounds at most8.
Both degree3 cases are impossible.

Suppose instead there is degree2 and no degree3. At least two highs are needed,
so total degree24>=10+2(m-2)=2m+6 and6<=m<=9. The other degrees are2,4 or>=5.
Let h>=2 count highs and r count degree4 mediums. The excess over2m is at
least3h+2r. All degree2 vertices use both incidences on highs.

* At m=9 excess6 forces precisely two degree5 highs and seven degree2 lows.
  Those lows would make both highs degree>=7, contradiction.
* At m=8 excess8 gives exactly two highs and at most one medium. Any medium
  can meet only the two highs because every low is saturated, so cannot reach4.
  Thus all six other vertices are degree2, adjacent to both highs. The high-high
  edge would cost a thirteenth edge; it is absent, leaving exactly K2,6.
* At m=7 excess10 allows h=2 or3. With h=3 the four other vertices must have
  degree2 and the high sum is16, namely(6,5,5). Their eight low incidences leave
  eight internal high incidences, exceeding the six available among three highs.
  With h=2, there are at most two mediums. One medium can meet at most two highs;
  two mediums can meet at most those highs and each other, at most three each.
  Neither can have degree4. All five other vertices are therefore degree2,
  giving K2,5 with or without the high edge, e=10 or11, not12.
* At m=6 every high is universal. Three highs would force every remaining vertex
  to have at least3 neighbors; absent degree3 it has at least4. Already3*5+3*4=27
  exceeds24, and further highs only increase this bound. Thus there are precisely
  two degree5 highs, and the remaining sum14 forces(4,4,4,2). The mediums form
  a triangle and the low meets both highs. This valid twelve-edge support shape
  (5,5,4,4,4,2) is retained explicitly. The low forces the adjacent highs'
  outside words equal, CN>=11/R>=9, but a degree5 bad pair has upper bound8.
  It is excluded by the exact pair budget, not by an incorrect degree count.

Finally, with no degree2 or3, minimum degree4 and total24 force m=6 with all
degrees4. Its complement on those six vertices has degree1 everywhere and is
a perfect matching. Thus this branch is exactly K6 minus a perfect matching.

Every possible order6..12 and low-degree branch has been covered. The only
surviving necessary shapes are the two in the precise statement.

## Falsification and scope checks

Twelve written checks were made: the exact24 incidence total; the m>=6 simple
graph bound; the separate degree2 m=12 boundary; binary-only degree3 word
propagation; m6 degree3 universality; m7 degree3 high triangle count; bad-pair
budget removal; saturated-low medium restrictions at m8/m7; three-high m7
internal incidence capacity; the explicit valid(5,5,4,4,4,2) shape before its
integer veto; complement degree1 at the final branch; and whole-support scope
with no assumed connectivity or target automorphism. These are written checks,
not an executed enumeration or calibrated graph-fixture batch.

Verdict PASS for the exact revision1 necessary classification, by complete
independent written derivation. ROOT's separate K2,6 and octahedral discoveries
were independently checked by Structural, but neither is used as a premise
here. Their combination needs a separate claim and dependency review.
Target resolution remains NONE, external review is unavailable, novelty UNKNOWN,
and all new evidence is LOCAL_ONLY. Ledger/index/current notices and frozen
371-claim publication are unchanged by this audit.

# Candidate: thirteen ternary defects cannot occur

Producer `/root`; source context `d0c0dd7db0d3de420b1d718b59122b069df01107`.
Status CANDIDATE pending a complete different-author exact written audit.
This is outside the frozen371-claim publication checkpoint. No executable
enumeration, mathematical worker, graph realization, formal proof, external
review or novelty assertion is supplied. Creation time is recorded separately
from the independent verification time; neither is a mathematical premise.

## Exact revision1 statement and dependency

For every symmetric binary integer99-by-99 matrix A with zero diagonal and
every row sum14, put R=A^2+A-12I-2J over the integers and M=R modulo3 over
GF(3). Let F3 count unordered off-diagonal nonzero entries of M. Then F3!=13.
This excludes precisely the whole thirteen-edge residual support in this
unrestricted degree14 adjacency domain. It does not force F3!=0, assume any
automorphism, prove sharpness, construct the target or prove its nonexistence.

The sole material dependency is revision1
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`, relation
`uses_result`. Independent ROOT audit
`acceleration/audit_20261003_ternary_equal_outside_nine_v1.md`, SHA256
`0497fef0e3a9ca8558acc2aacdbc68abe6b9ef8db925e502765d02a85676be18`;
report `acceleration/results/20261003_independent_review/ternary_equal_outside_nine_01/equal_outside_filter/summary.json`,
SHA256 `7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`.
The elementary ingredients are repeated below. No lower12/lower13 theorem,
twelve-edge classification, incidence rank or support catalogue is used.

## Residual facts and exact pair budget

Let S be the vertices incident with an edge of M and m=|S|. Let H be the
simple WHOLE support graph on S. Its degrees d count residual defects, not
adjacency degrees of A. Each nonzero M entry is labelled1 or2=-1.
R has zero diagonal and R1=0. Thus M1=0, so d>=2. If c1 and c2 count the
labels in a row, c1+2c2=0 in GF(3). Define beta=2c1+c2. It is divisible
by3 and beta<=3floor(2d/3). Each integer off-diagonal R entry is at least-2.
Every residue0 entry is therefore nonnegative. The total positive integer
mass of a row is at most beta. An individual residue1 positive entry is at
most beta-2, a residue2 entry at most beta-1, and a residue0 entry at most
beta. These individual bounds remove its own negative-mass allowance.

Set T to the other99-m vertices, and X=A[T,S] over GF(3). Polynomial
commutation AR=RA gives XM[S,S]=0: all rows/columns of M outside S vanish.
Each row of X is a binary word. A degree2 support row has opposite labels,
so its two neighbor coordinates have equal outside words. A degree3 row
has all three labels equal, so its three neighbor coordinates have equal
outside words: three binary values sum to0 in GF(3) only when all agree.

If vertices p,q have equal outside words, their integer common-neighbor
count satisfies CN(p,q)>=14-floor(m/2). Hence R[p,q]>=CN(p,q)-2. For
m<=11 the pair budget forces BOTH support degrees to be at least5.
The stronger multiple-pair budget remains available even when a single
pair bound is attained. Support adjacency does NOT imply A adjacency.

Assume F3=13. Then sum d=26, m<=13, and m>=6 because binomial(5,2)<13.

## No degree3 vertex

A degree3 vertex produces three distinct neighbors with equal outside
words. Since m<=13 their pairwise CN>=8 and each of the three pair
residuals is at least6, positively over the integers. Each neighbor's
row consequently has positive mass at least12. A support degree<=5 has
beta<=9, so all three neighbors have support degree>=6.

For m=6 this is impossible in a simple graph. For m>=7, the minimum
sum of support degrees would be 2m+1+3(6-2)=2m+13>=27>26. Thus no
degree3 vertex exists. Every vertex has degree2 or degree at least4.

## All cases containing a degree2 vertex

For m<=11, call a vertex high when its support degree is at least5;
every degree2 vertex has two high neighbors. Let h be the number of
high vertices, r the number of degree4 vertices, and l the number of
degree2 vertices. They satisfy h+r+l=m and the excess sum
sum(d-2)=26-2m. In particular h>=2 and 3h+2r<=26-2m.

* m=13: all degrees are2. A degree2 vertex makes its two degree2
  neighbors' outside words equal. Their pair residual is at least6,
  exceeding beta<=3.
* m=12: the excess is2, so there is one degree4 vertex and all others
  have degree2. An equal-outside pair still has residual at least6;
  neither endpoint can have degree2. Two degree>=4 neighbors would
  require excess at least4. There are not two such vertices.
* m=11: the excess is4, less than the6 required by two high vertices.
* m=10: the excess is6, giving exactly two degree5 high vertices and
  eight degree2 vertices. All eight low vertices meet both highs,
  contradicting the high degrees5.
* m=9: the excess is8. Necessarily h=2 and r<=1. If r=1, its degree4
  vertex could meet only the two highs: lows cannot meet it. If r=0,
  each high meets all seven lows, although the total high degree is
  26-14=12<14. Both cases are impossible.
* m=8: the excess is10. If h=2, r<=2. Any degree4 vertex can meet
  at most the two highs and one other degree4 vertex, fewer than4.
  Thus r=0. The support is K2,6 plus the high-high edge, with both
  highs of degree7. Every low row has opposite labels, so the sum
  of the two high row sums in GF(3) is twice the nonzero high-high
  label. This contradicts M1=0.
  If h=3, r=0 and the high degrees are(6,5,5), with five lows. The
  high degrees sum16, and the low incidences sum10, leaving six
  high-high incidences: the high support is a triangle. Its high-to-low
  incidences are(4,3,3). The low neighbor-pair multiplicities must
  therefore be(2,2,1), so all three high outside words are equal.
  Each degree5 high has TWO positive pair residuals at least8 because
  CN>=10. Their total16 exceeds beta<=9. This is a multiple-pair
  contradiction; no implication from support adjacency to A adjacency
  is used. These exhaust h, since h>=4 would require excess>=12.
* m=7: the excess is12. If h=4, r=0, all highs have degree5 and the
  three lows have degree2. The high internal incidences would be
  20-6=14, exceeding the twelve available in a four-vertex simple
  graph. If h=3, r<=1. For r=0 all highs have degree6 and are
  universal, impossible for the four degree2 lows. For r=1 the highs
  have degrees(6,5,5), with three lows. Each low meets the universal
  high and a degree5 high. These highs have equal outside words,
  and their supported pair has residual at least9 (CN>=11) while
  its degree5 endpoint allows at most beta-1<=8.
  If h=2, r can be0,1,2,3. For r=1 or2 a degree4 vertex has at most
  two high and one medium neighbor, impossible. For r=0 both highs
  meet all five lows, with possibly their mutual edge, giving only
  ten or eleven edges. For r=3 the degree sequence is
  (5,5,4,4,4,2,2). Each medium must meet both highs and both other
  mediums, and both lows meet both highs. Thus H is two independent highs joined to
  a triangle and two isolated vertices, with the highs nonadjacent.
  Each low has c1=1 and each medium c1=2. Each high has c1=1 or4.
  The total number of label1 incidences is even, so the two highs
  have the same c1. If both are1 then beta=6; their equal-outside
  unsupported pair has residual at least9, impossible. If both
  are4 then the highs contribute eight label1 cross incidences.
  The low cross edges use two, so all six high-medium edges have
  label1, and all three medium-medium edges have label2. In each
  binary outside word the high coordinates are equal, say t.
  The three medium equations are 2t-p-q=0, 2t-p-s=0,
  2t-q-s=0 over GF(3). They force p=q=s=t. A medium and a high
  now have equal outside words. Their supported pair residual is
  at least9; the degree4 endpoint permits at most beta-1<=5.
* m=6: a low has two degree5 neighbors, which are universal in H.
  Their supported equal-outside pair has CN>=11 and residual>=9;
  either degree5 endpoint permits at most beta-1<=8.

## The remaining minimum-degree4 support

With no degree2 or3 vertex, 4m<=26, so m=6. The degree sequence is
(5,5,4,4,4,4), and H is K6 minus two disjoint edges. Write a,b for
the highs. Each low has c1=2; each high c1=1 or4. Evenness of the
total label1 incidence implies both high counts agree. Multiplying
M by-1 if necessary gives both high counts1 and all low counts2.
This changes no kernel. It is solely a field sign normalization;
the original integer R and its row budgets are never negated.

The label1 subgraph has degrees(1,1,2,2,2,2): a path between a,b
and cycles covering the remaining lows. The low support is C4,
so a three-low triangle is unavailable. Simple cycles on one or
two vertices are unavailable. Thus the only two possibilities are
the single positive high-high edge with a positive low C4, or a
positive Hamilton path through all six vertices. This is an exact
label classification, not an automorphism assumption about A.

For the first case, the two high equations in Mx=0 are
b-sum(lows)=0 and a-sum(lows)=0, forcing a=b. The original integer
equal-outside supported high pair again violates the degree5 budget.

For the Hamilton path, order it a,u,v,w,z,b. The missing support
edges are uw and vz. For any vector in the field kernel, the six
equations are

    u-v-w-z-b=0,             z-u-v-w-a=0,
    a+v-z-b=0,              -a+u+w-b=0,
    -a+v+z-b=0,             -a-u+w+b=0.

The last four give z+u=v+w and u+w=v+z, hence z=w and u=v
because2 is invertible in GF(3). The first two then give b=z
and a=u. The third gives a-b=z-u, forcing u=z. Every coordinate
is equal. Thus all six outside words are equal. Any supported pair
incident with a low has residual>=9 by CN>=11, contradicting the
degree4 supported-pair upper bound<=5. The sign normalization was
used only to compute this kernel and applies equally to original M.

All cases are exhausted, so F3=13 is impossible, conditionally on the
independent audit accepting every step and the stated material dependency.

## Falsification history, review and limitations

Version1 used the ambiguous phrase K2 joined for the m=7 exceptional support, despite explicitly saying that its two highs are nonadjacent. Version2 corrects that phrase to two independent highs joined. Version1 is preserved; no mathematical statement or kernel equation changes.

The preliminary chat outline incorrectly used a supported high triangle
at m=8 to infer A adjacency and a single-pair residual>=9. Support
adjacency does not imply A adjacency. Before freezing this paper the
producer withdrew that argument and replaced it with the complete
(2,2,1) low-pair/multiple-positive-mass argument above. This failed
reasoning is preserved here; no verified claim was based on it.

The reviewer should reconstruct all degree and label cases, especially
m=8 high multiplicities, the m=7 exceptional join and both signed six-
vertex kernels. Check arithmetic over GF(3), original integer budgets,
whole-support coverage and disconnected cases without assuming a connected
support. A counterexample must be tested against the exact99/14 adjacency
polynomial hypothesis; a field-only signed graph is not such a lift.

No executable finite control, catalogue coverage, graph fixture, numerical
eigenvalue calculation or solver result is offered. Artifact availability
is LOCAL_ONLY. Overall search coverage: UNKNOWN; no validated denominator.
The target F3=0 case remains allowed. The paper changes no ledger, index,
frozen milestone, historical evidence, driver or checker.

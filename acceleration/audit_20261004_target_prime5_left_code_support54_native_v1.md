# Independent written review: target prime-five left-code support54

This is Native's independently reconstructed mathematical proof and adversarial
review of the first frozen Structural support54 candidate. It is a written
review: no research source was imported, no matrix or code word was enumerated
by a program, no numerical backend or scientific worker was launched, and no
ledger or Git state was parsed or changed. The paper and raw candidate remain
unchanged. The separately proposed signed integer 1-design corollary is not
included in this review because its frozen statement has not yet been supplied.

Exact claim: C-UNRESTRICTED-TARGET-PRIME5-LEFT-CODE-SUPPORT-LOWER54, revision1.

Paper: docs/CANDIDATE_20261004_TARGET_PRIME5_LEFT_CODE_SUPPORT54_V1.md,
SHA256 2d2ac115080485ffd98d8e2478bc3979a8c8c41751d524e4396d34cf6f31cc3e.

Raw candidate:
acceleration/results/20261004_target_prime5_left_code_support54_candidate01.json,
SHA256 ccdf184ffbd3a3244d01e160777e3f397c7e568d37237f29657fc57676e13acc.

## Statement and independent conclusion

For every finite simple SRG(99,14,1,2), N is the99-by231 binary incidence
matrix of every actual triangle once, and L5 is ker(N-transpose) over F5.
Every nonzero word of L5 has Hamming weight at least54. The code may be zero.
The exact raw statement also withholds any nonzero-word, automorphism,
equitable-profile, extra ternary dependency, rank improvement or target
exclusion assertion. All those qualifications are retained.

The result passes the written derivation below under precisely these complete
target hypotheses. It is a universal necessary support condition, conditional
on a target and a nonzero F5 word. This is not an actual word, graph, exclusion,
rank computation, executable checker qualification or novelty certification.

## 1. Derive the complete geometry and real spectral inequalities

Every adjacent pair has exactly one common neighbor, hence every edge belongs
to exactly one actual triangle. At a vertex its14 neighbors induce a matching:
each neighbor has exactly one neighbor within that14-element neighborhood,
because those neighbors are the common neighbors of the vertex-neighbor edge.
There are therefore seven incident triangles at every point. Counting
point-triangle incidences gives99*7/3=231 triangles. Distinct vertices share a
triangle exactly once if adjacent and never if nonadjacent. Thus NN^T=A+7I=H,
N1=7j, and N^Tj=3*1.

The integer adjacency identity follows entry by entry: diagonal14, adjacent
off-diagonal1, nonadjacent off-diagonal2, giving A^2=12I-A+2J. Since Aj=14j,
the real subspace j-perp is invariant and (A-3I)(A+4I)=0 on it. Symmetry makes
the decomposition orthogonal. Trace0 and dimensions give multiplicities54
and44. H consequently has eigenvalues21,10,3, so H is positive definite and

    X^T H X >= 3 X^T X

for every ordinary real X, without requiring its sum to vanish. This is a
real inequality on a chosen ordinary integer lift, not an F5 ordering or a
field norm.

For an arbitrary support S with indicator chi and cardinality s, put
z=chi-(s/99)j. Orthogonality and Aj=14j give

    2e = chi^T A chi
       = z^T A z + 14s^2/99
      <= 3(s-s^2/99)+14s^2/99
       = 3s+s^2/9.

There is no regularity assumption on A[S] and no uniform color-neighbor
profile. At s=99 the centered vector is0 and the inequality is equality;
division by its norm is never used.

## 2. Independently classify the triangle lifts

Represent F5 by {0,1,2,-2,-1}, and choose the unique centered integer lift X
of a nonzero x. Its support S has s>0. Every triangle's lift sum is divisible
by5 and lies from-6 to6, hence is exactly0,5 or-5. A triangle cannot meet S
in exactly one point, since a single nonzero F5 entry would not sum to0.

For exactly two supported points their centered values are opposite. This
remains true after multiplication by2 in F5. For three supported points,
sort their entries in the ordinary order -2<-1<1<2. The entire list of20
three-element multisets, with repetitions, has sums:

    (-2,-2,-2):-6  (-2,-2,-1):-5  (-2,-2,1):-3  (-2,-2,2):-2
    (-2,-1,-1):-4  (-2,-1,1):-2   (-2,-1,2):-1
    (-2,1,1):0    (-2,1,2):1     (-2,2,2):2
    (-1,-1,-1):-3 (-1,-1,1):-1   (-1,-1,2):0
    (-1,1,1):1    (-1,1,2):2     (-1,2,2):3
    (1,1,1):3     (1,1,2):4      (1,2,2):5  (2,2,2):6.

Only four of these sum to0 modulo5: the two signs of (1,1,-2) and the
two signs of (1,2,2). This is a written finite type check, not a program.

Under centered multiplication by2 the entries change as

    1->2, 2->-1, -1->-2, -2->1.

It sends (1,1,-2) to (2,2,1), and (1,2,2) to (2,-1,-1).
Their negatives do the same with signs reversed. Thus zero-sum fully
supported triangles and winding triangles exchange. Exactly-two and
empty triangles never wind for either scalar. If t and t2 count nonzero
integer triangle sums for X and the centered lift X2 of2x, and m3 counts
fully supported triangles, then t+t2=m3 exactly.

If p entries of X have absolute value1 and q have absolute value2, then
p+q=s, ||X||^2=p+4q, and ||X2||^2=4p+q. From the Gram identity,

    25t  = ||N^T X||^2  >= 3(p+4q),
    25t2 = ||N^T X2||^2 >= 3(4p+q).

Adding proves25m3>=15s, or m3>=3s/5. Multiplication by2 changes values
on the same labelled graph; it invokes no graph permutation or automorphism.
The strict/non-strict distinctions are correct: equality is allowed in
the spectral bounds, and no unjustified positive margin is inserted.

## 3. Count the support and exclude every integer s from1 through52

Let m2 count triangles meeting S in two points. The absence of one-point
triangles gives7s=2m2+3m3. Every edge in A[S] belongs to its unique actual
triangle: a two-point intersection contributes one such edge, a three-point
intersection three. Consequently e=m2+3m3 and2e=7s+3m3.

Combining with the support Rayleigh bound gives

    7s+3m3 <= 3s+s^2/9,
    27m3 <= s(s-36).

Together with m3>=3s/5, and s>0, this yields

    (81/5)s <= s(s-36),
    s >= 36+81/5 = 261/5 = 52+1/5,
    s >= 53 for integer s.

This covers all integers1..52 symbolically, including the requested0..42
boundary:0 belongs only to the excluded zero word; every positive integer
in that interval is impossible, as are43..52. No enumeration of supports or
unproved moment congruence is needed. The unfrozen preliminary support43
route is not a mathematical premise or an additional claim in this package.

As a subsidiary parity check7s=2m2+3m3 means s and m3 have the same parity.
As a subsidiary F5 congruence, self-orthogonality below implies p+4q=0 mod5,
equivalently s-2q=0 mod5. The stronger support proof does not rely on that
congruence or assume a nonconstant color partition.

## 4. Exclude s53 by ordinary integer arithmetic

At s53, (3s/5)=159/5=31+4/5 gives m3>=32. The upper numerator is
53*(53-36)=901 and901/27=33+10/27, giving m3<=33.
Since m3 has odd parity, m3=33. The exact edge count is

    2e=7*53+3*33=371+99=470,  e=235,
    m2=(371-99)/2=136.

Set Q=27I-9A+J. Its row sum is27-9*14+99=0. Direct expansion gives

    Q^2 = 729I+81A^2+J^2-486A+54J-18AJ
         =1701I-567A+63J
         =63Q.

Here symmetry gives AJ=JA=14J and J^2=99J. No modular reduction,
division by7, numerical eigensolver or archived projector rank is used.

For chi=chi_S the exact energy is

    chi^T Q chi = 27*53-9*470+53^2
                =1431-4230+2809=10.

Y=Qchi is an ordinary integer99-vector. Its sum is0 and every coordinate
equals27chi_v-9(Achi)_v+53, hence is-1 modulo9. Its squared Euclidean norm is

    Y^T Y=chi^T Q^2 chi=63*10=630.

There is an integer vector a with Y=9a-j. Summing gives9sum(a)-99=0,
so sum(a)=11. Squaring gives

    630=81sum(a_v^2)-18sum(a)+99
       =81sum(a_v^2)-99,
    sum(a_v^2)=729/81=9.

For every integer a, a^2-a=a(a-1)>=0, including negative a.
Therefore sum(a_v^2)>=sum(a_v)=11, contradicting9.
No nonnegative assumption is made about a or Y. This completes s>=54.

## 5. Ancillary F5 statements: independently checked, not rank transfer

For x,y in L5, choose ordinary integer lifts X,Y. Both N^T X and N^T Y
are5-divisible. Consequently HX=N(N^T X) and HY are5-divisible; moreover

    X^T H Y=(N^T X)^T(N^T Y)

is25-divisible. From7sum(X)=1^T N^T X, and gcd(7,5)=1, both coordinate
sums are5-divisible. The identity

    H^2-13H+30I-2J=0

is checked directly by H=A+7I and A^2=12I-A+2J.
Pairing it with X,Y makes the H^2, H and J terms25-divisible, hence
30 X^T Y is25-divisible. Since v5(30)=1, X^T Y is5-divisible.
Thus L5 is self-orthogonal for the ordinary dot product over F5. Constants
c*j with c nonzero are excluded since N^T(c*j)=3c*1 is nonzero in F5.
This proves the ancillary assertion without incorrectly equating rank(N)
and rank(NN^T) over F5.

The stated elementary rank bound rank_F5(N)>=72 follows independently:
det(H)=21*10^54*3^44 has5-adic valuation54. If N has rank r modulo5,
invertible row operations over the local integers at5 put the last99-r rows
of N in5 times that module. The corresponding congruent Gram matrix has a
factor5 from each of its last99-r rows and last99-r columns, so its
determinant is divisible by5^(2(99-r)). Therefore2(99-r)<=54 and r>=72.
This is only a determinant inequality. It neither says r=72 nor improves
that inherited bound, and ordinary real rank99 does not force F5 rank99.

Full F5 rank99, zero code, and all its implications remain logically allowed.
Nothing here transfers a ternary or binary rank conclusion to characteristic5.

## 6. Written falsification and boundary controls

1. A singleton supported triangle coordinate cannot sum to0 mod5.
2. Two opposite entries have zero winding before and after scalar2.
3. The20 written fully nonzero multisets admit exactly the four types above.
4. (1,1,-2) and (1,2,2) demonstrate the actual exchange, not just equal norms.
5. Changing scalar2 to a graph automorphism would add an unnecessary hypothesis;
   no such operation was used.
6. s0 cannot be divided away: it is an allowed zero word.
7. s52 has upper m3<=832/27<31 while the lower is156/5>31; impossible.
   Equivalently the universal rational bound already excludes it.
8. s53 permits m3=32 or33 before parity; even32 violates7s-3m3 even.
9. At s53 the exact m2=136, e235, Q energy10 and norm630 were recomputed.
10. Replacing the9-residue by a5-residue would not support the integer-vector
    conclusion; the correct residue comes from Q's27 and-9 coefficients.
11. Negative integer a remains subject to a^2>=a; a real fractional a does not.
    For instance99 equal real entries1/9 have sum11 and squared sum11/9.
    Integer coordinates are essential to the contradiction.
12. Rook9 has only six actual triangle columns and row incidence2. The array
    (1,-1,0),(-1,1,0),(0,0,0) has all row/column sums0 and support4 in its F5
    left code. Its Gram least eigenvalue is0, so target3 and degree7 cannot
    be transplanted to it.
13. An incomplete triangle selection can lose row7 and NN^T=A+7I; the full
    counting proof then fails. A fixed17 count witness supplies no complete N.
14. An unrestricted-entry 3-adic Gram factor supplies no ordinary binary
    triangles or real centered support inequality, and cannot be substituted.
15. Neither a53-support code word nor a54-support code word was constructed.
    The inequality leaves existence and the attained minimum unknown.
16. A zero F5 left code satisfies every asserted statement. No hypothetical
    target existence or exclusion is inferred.

These are hand checks and logical corruption boundaries, not executed test
cases or empirical evidence from an actual99-point graph.

## 7. Archive overlap and review provenance

The complete modular-rank audit was read: it derives the same ordinary
spectrum and historical Q^2=63Q projector, with characteristic2/3 necessity.
The entire Wave23 failed-routes note was read: it warns against collided
eigenvalue/Smith inference and retains the weak ternary rank interval. Those
warnings were respected here. The whole Wave168 derivation was read: it
already supplies complete triangle geometry, incidence Gram, ordinary
spectrum and higher-minor energy. Its characteristic2/3 block code differs
from this F5 vertex left code.

The exact mod9 and3-adic boundary papers were already whole-read in Native's
preceding independent reviews and were freshly identity-checked here.
Their p3 statements are not a premise for this p5 proof. The current proof
uses shared historical algebra, but its rank/support characteristic is
explicit. This is a bounded comparison of the five named documents, not an
exhaustive search or a novelty claim.

Root requested the ordinary-integer prime follow-up and Structural authored
the frozen support54 candidate. Native had independently reached the53
precursor before receiving Structural's strengthening message, then
reconstructed the53 residue exclusion independently from the frozen paper.
The shared Root direction and historical Q identity are disclosed; Root's
separate hand residue check is not substituted for Native verification.

Review began at the authentically recorded2026-10-04T13:24:55Z. The companion
report gives the actual sealing timestamp. The candidate's creation time is
not a verifier start or end time. No source commit or current ledger identity
is invented. Registration, a canonical metadata wrapper, future computational
screens, and the separate signed integer 1-design corollary require their
own explicit next work.

Result: written PASS for the exact support54 claim/r1, with the stated
ancillary facts independently checked and all target conclusions withheld.


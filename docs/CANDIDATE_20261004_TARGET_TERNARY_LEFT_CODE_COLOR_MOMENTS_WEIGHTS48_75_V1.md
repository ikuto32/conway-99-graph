# Target ternary left-code color moments: nonconstant weights48..75

CANDIDATE, revision1, independently unverified. Discovery `/root/structural`.
Root requested this follow-up to the accepted42..78 paper; the identities and
target hypotheses are shared. This is a new, materially stronger statement,
not a rewrite of that earlier claim. No mathematical script or programmatic enumeration,
solver, imported source, numerical worker or ledger/index/Git mutation occurred.

## Exact statement and dependency

Let A be the adjacency of any complete simple SRG(99,14,1,2), and let N be
its99 by231 incidence matrix containing each actual triangle exactly once.
For every nonconstant word x in L=ker(N^T mod3), each of its three vertex
color classes has size divisible by3 in [24,51]. Thus

    wt(x) in {48,51,54,57,60,63,66,69,72,75}.

The constant words have weights0,99,99 and remain permitted. In particular
L=span(j) remains possible. No nonconstant dependency, incidence-rank bound,
small right-circuit implication, fixed17 occurrence or target exclusion follows.

Logical dependency is the exact-r1 result
`C-UNRESTRICTED-TARGET-TERNARY-LEFT-CODE-DOT-FORM-WEIGHTS42-78`, written
independently by Checkpoint against paper653a/raw0e256. That establishes three
positive class sizes divisible by3 in [21,57], the local rainbow profile and
the indicator Rayleigh inequality. The old October3 design45c27c already
contains the second-moment identities below; I rederive them here rather than
assign a computational approval or a new historical identity to the design.

## Exact moments and integer envelopes

Write the sorted class sizes a<=b<=c, a+b+c=99. Let t be the number of rainbow
triangles; for v in class i let r_v count its incident rainbow triangles.
Every actual triangle is monochromatic or rainbow, and the seven incident
triangles partition a vertex's neighbors, so the three degrees are

    own color:14-2r_v; each other color:r_v; 0<=r_v<=7.

For each class, sum r_v=t. Monochromatic triangle counts are (7s_i-t)/3;
therefore t is a multiple of3 and t<=7a. Put Z_i=sum_(v in class i) r_v^2
and Q=ab+ac+bc. The integer target identity A^2=12I-A+2J, applied to distinct
class indicators, gives

    (A chi_i)^T(A chi_j)=28t-2Z_i-2Z_j+Z_k
                        =2s_i s_j-t,
    -2Z_i-2Z_j+Z_k=2s_i s_j-29t.

Summing and substituting yields exactly

    Z_i=(29t+2s_j s_k)/3-(4/9)Q.                  (1)

For s integer entries r in [0,7] with sum t, write t=qs+u,0<=u<s. Then

    Z>=s q^2+u(2q+1),       Z<=7t.               (2)

The lower bound follows by moving one unit from entries that differ by at
least2; its equality requires every entry q or q+1. The upper bound follows
pointwise from r^2<=7r. These are integer necessary inequalities, not graph
or histogram realizations. The old spectral bound simplifies to

    t>=s_i(99-s_i)/18.                           (3)

Indeed11/198=1/18. No constant r profile is assumed.

## Complete seven-case hand exclusion when a=21

Assume a=21. Then b is one of21,24,27,30,33,36,39 and c=78-b. This list
is complete because all sizes are multiples of3 and21<=b<=c. Formula(3)
for c gives the least multiple-of3 t in the second column below. In all
cases132<=t<=147, so the21-entry envelope is

    Z_A>=13t-882.

For a=21, (1) takes Z_A=29t/3-D_A, with D_A=728-2bc/9. Combining these
gives t<=(3/10)(882-D_A). The table records the exact rounded result and
one additional necessary inequality; all arithmetic is hand derivation.

|b,c|Lower t from(3), rounded to3|D_A|Upper t from21-entry envelope, rounded to3|Additional condition or result|
|---|---:|---:|---:|---|
|21,57|135|462|126|No t interval|
|24,54|135|440|132|No t interval|
|27,51|138|422|138|Z_C=29t/3-962 >=5t-306 requires t>=141|
|30,48|138|408|141|Z_B=29t/3-696 >=9t-600 requires t>=144|
|33,45|135|398|144|Z_B=29t/3-758 >=9t-660 requires t>=147|
|36,42|135|392|147|Z_C=29t/3-896 >=7t-504 requires t>=147|
|39,39|132|390|147|Z_B=29t/3-858 >=7t-468 requires t>=147, but Z_A<=7t requires t<=144|

The displayed integer envelopes apply throughout each already admitted t
interval: q_C=2 for the51-class, q_B=4 for the30/33-classes and q_C=3 for
the42-class. For the39/39 row the39-entry q=3 envelope applies throughout
132..147. Its upper condition is t<=585/4=146.25, hence t<=144. No floating
rounding establishes any conclusion; the fractions and multiple-of3 t do.

For clarity, the inequalities before rounding in the three middle rejected
rows are t>=984/7, t>=144 and t>=147 respectively. In the36/42 row the
remaining interval is the single value t=147. Thus the only possible scalar
boundary with a=21 has

    (a,b,c)=(21,36,42), t=147,
    (Z_A,Z_B,Z_C)=(1029,609,525).                 (4)

The21-class then has every r_v=7 and is independent. Equality in the42-class
integer envelope forces exactly21 entries r=3 and21 entries r=4. No uniform
profile has been imposed on the36-class.

## Pointwise common-neighbor contradiction at the boundary

Call these classes A,B,C of sizes21,36,42. Fix any vertex v in B and put
r=r_v. It has r neighbors in A, r in C and14-2r in B. Let R_B and R_C
be the sums of r_w over its neighbors w in B and C. Every A vertex has
r_w=7 and no neighbors in A, so length-two walks from v to A total
R_B+R_C. Of the21 vertices of A, r are adjacent to v and21-r are
nonadjacent. Exact lambda1/mu2 therefore gives

    R_B+R_C=r+2(21-r)=42-r.                      (5)

Length-two walks from v to C through A,B,C respectively number7r, R_B,
and14r-2R_C. Exact common-neighbor counts to the42 vertices of C give

    21r+R_B-2R_C=r+2(42-r)=84-r.                 (6)

There is no return-walk term: v belongs to neither A nor C. Subtracting(6)
from(5) yields R_C=7r-14. Each of its r neighbors in C has rainbow degree
3 or4 by(4), hence

    3r<=7r-14<=4r.

These inequalities require r>=7/2 and r<=14/3. Its integral value is
therefore exactly4. This was derived separately for an arbitrary v in B;
it is not an equitable-partition or same-type-profile premise. It forces
sum_(v in B) r_v=36*4=144, contradicting t=147. All possibilities with a=21
are excluded. Population divisibility then gives a>=24 and c<=99-2*24=51,
which proves the exact stated weight interval.

## Hand falsification boundaries and surviving scalar data

1. Constants have empty color classes, invalidate the positive-class proof,
   and are explicitly retained. The proof never forces a word outside span(j).
2. The boundary(21,36,42),t147 passes the prior scalar moments: A has21 r7,
   B can have one r7 and35 r4, C has21 r3 and21 r4. Their totals and squares
   give(4), and monochromatic counts0,35,49 plus147 rainbow give231 triangles.
   These are scalar data, not a graph. The pointwise CN contradiction is
   necessary; declaring scalar infeasibility alone would be incorrect.
3. R_C in(6) counts own-color degrees14-2r_w; using r_w there reverses the
   inference. Common-neighbor totals are84-r, not84 or84-2r. Both class totals
   exclude a return vertex because v is in B.
4. The scalar survivor(33,33,33),t132 has11 entries each r3,4,5 and Z550
   per class. It satisfies(1)--(3) and the new population bounds. No graph,
   code or adjacency realization is inferred.
5. The scalar boundary(24,24,51),t141 also survives: each24-class can have
   17 r6,5 r5,2 r7 (sum141,Z835); the51-class can have35 r3,14 r2,2 r4
   (sum141,Z403). Formula(1) yields those same squares. The largest-class
   bound is136<=141. Thus this argument does not reduce the maximum class
   size below51, or the minimum word weight above48.
6. Rook(9,4,1,2), colored by its three rows, has three color classes of3,
   three rainbow column-triangles and r=1 at every point. It is a genuine
   nonconstant ternary left word, but has degree4/two incident triangles.
   It refutes transfer of these numerical target bounds to arbitrary
   lambda1/mu2 graphs, not the target-specific derivation.
7. Formula(1), the old sum-of-square envelopes and Rayleigh bound are prior
   identities. The new material consequence is their seven-case reduction
   followed by the pointwise CN contradiction. No new rank, automorphism,
   fixed17-completion or unrestricted target-resolution bridge is supplied.
8. Removing integrality, class divisibility or the exact common-neighbor
   identity changes the scope and invalidates the rounded table/conclusion.

## Bounded overlap and next use

The reviewed current dot/weight paper and independently written Checkpoint
audit retain21..57 and42..78. The old nonconstant-kernel design already states
all of(1) and the integer moment screen. Bounded exact-string/current-doc
searches found no recorded24..51/48..75 statement or21/36/42 pointwise
contradiction. Archive comparison was restricted to the previously relevant
Wave170/171/174/191 derivations and derivation files matching left-code/
rainbow/color-class terms. Wave174 imposes an additional prism-free weight3
block-dual configuration; Wave191's left code has an additional endpoint.
Neither conditional family is imported as an unrestricted premise. Other
matches describe binary codes, lattice coefficients or root colors. This is
bounded comparison, not an exhaustive literature/novelty claim.

After this written theorem is independently checked, a small optional scalar
screen could retain all12 sorted population triples in [24,51], and all761
multiple-of3 t labels from0 through7*minimum, including first-veto rejections.
Histogram and pointwise neighbor-r conditions remain necessary-only. No source,
control packet, worker or numerical enumeration is supplied or authorized here:
the hand proof already completely rejects its sole21-point family. The
surviving scalar controls make a new run unnecessary for this statement.

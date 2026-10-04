# Independent written audit: prime-five linear-triple image counts

Reviewer: /root/native_driver. Mathematical producer: /root/structural.
Method: independent_derivation. Claim: C-PRIME5-LINEAR-TRIPLE-IMAGE-WEIGHT-COUNTS,
revision1. Verdict: PASS within the exact frozen statement and hypotheses.
No program, import, code enumeration, formal check, LP, solver, ledger parse,
Git operation or computational worker was used.

The complete new paper04eb12 and raw candidateee15e3 were read. The exact raw
statement and scope are preserved in the companion report. The following is
an independent proof, including a separate small-column independence argument
that does not rely on merely agreeing with the producer's recovery argument.

## Domain and the meeting-pair count

Let the finite point set have size n, and let the columns of N be the
characteristic vectors of m DISTINCT three-element subsets. Any two distinct
triples intersect in at most one point. Coefficients and image words are overF5.
Hamming weight counts nonzero field coordinates, not an integer norm.

For a point v with replication t_v, choose(t_v,2) counts pairs of triples
meeting there. Linearity makes each meeting pair appear exactly once, so
Q=sum_v choose(t_v,2) is exactly the number of unordered meeting pairs.
Therefore choose(m,2)-Q is the number of unordered disjoint pairs and is
nonnegative. This identification would fail without linearity.

Four nonzero scalar multiples of a column have weight3. The support recovers
the triple and any one nonzero coordinate recovers its coefficient. Thus
these4m vectors are all distinct.

## Independent collision challenge: at most four columns are independent

Suppose a nonzero relation uses h<=4 DISTINCT columns, all retained
coefficients nonzero. A point occurring in just one retained triple would
force that coefficient to vanish.

If h<=3, each triple has at most h-1<=2 intersection points with the other
triples. Its third point is private, a contradiction.

If h=4 and no point is private, a fixed triple must cover its three points
by intersections with its three companions. Each companion meets it at most
once, so the three intersections must all exist and be distinct. No point
can lie on three of the four triples: that would use two companions at one
point and leave only one companion to cover the other two points of a triple.
Thus all six unordered triple pairs have six distinct two-triple intersection
points. If c_i are the four coefficients, each pair gives c_i+c_j=0.

In particular c1+c2=c1+c3=c2+c3=0 implies c2=c3 and2c2=0. Since2 is invertible
overF5, c2=0, contradicting retention. Hence there is no nonzero relation.

Consequently the map from coefficient vectors supported on at most TWO
columns into im(N) is injective: equality of two such representations would
give a relation on at most four distinct columns after cancelling common
coordinates. This separately rules out collisions across all two-column
families and all chosen unordered-pair coefficient orderings.

This written checking lemma is not a newly registered claim or a claim of
independence of five or more columns. It fails in characteristic2 exactly at
the six-point four-triple boundary discussed below.

## Two meeting columns

Write T={v,a,b} and U={v,c,d}; the four outer points are distinct.
Fix one ordering of the unordered pair and choose nonzero alpha,beta.

If beta=-alpha, the common coordinate vanishes. The word has value alpha
on{a,b}, -alpha on{c,d}, and zero elsewhere, so its weight is4. There are
four coefficient assignments. OverF5, alpha and-alpha are distinct. The
two value classes recover the two outer pairs, and each outer pair has
at most one containing triple by linearity. This is also a direct recovery
check independent of the no-four-column-relation argument. It gives4Q
distinct weight4 words.

Otherwise alpha+beta is nonzero and the weight is5. There are4*3=12
assignments. If alpha!=beta, the three values alpha,beta,alpha+beta are
distinct, with multiplicities2,2,1. The unique singleton is v and the two
outer value classes recover the triples.

If alpha=beta, the value2alpha is nonzero and differs from alpha. It uniquely
identifies v; every outer point u belongs to at most one triple containing
{v,u}. Therefore the four equal outer entries still have a unique pairing
into the two original triples. This verifies the potentially ambiguous
equal-coefficient case. No factor-of-two is inserted: coefficients are
assigned to a fixed ordering of each unordered pair and the vector recovers
that assignment.

The complete addition table, with rows alpha=1,2,3,4 and columns beta=1,2,3,4,
is
    2 3 4 0
    3 4 0 1
    4 0 1 2
    0 1 2 3.
There are exactly four cancellation entries and twelve nonzero sums.
This establishes B4>=4Q and B5>=12Q, without any graph edge premise.

## Disjoint columns

For disjoint T,U and nonzero alpha,beta, all six coordinates survive.
There are16 assignments.

If alpha!=beta, the two three-point value classes recover T,U and their
coefficients. If alpha=beta, the six-point support alone has exactly the
two original system triples. A third triple within their union would contain
two points of T or two points of U, contradicting linearity. Thus the
equal-coefficient case is unique as well. The independent four-column argument
also certifies this recovery.

It follows that B6>=16*(choose(m,2)-Q). Vectors involving three or more
columns may increase any displayed B_j. The theorem supplies lower bounds,
not a complete classification or enumerator.

## Constant translates and the n>6 boundary

Assume n>6 and the all-one vector j_n lies in im(N).
For every c!=0 and triple T, c*j_n-c*N_T vanishes exactly on T and has
weight n-3. Its zero set recovers T; a point outside T recovers c.
These are4m distinct words.

For c!=0 and a!=0,-c, c*j_n+a*N_T has no zero coordinate.
There are4*3=12 choices per T. To compare representations using T and U,
choose a point outside T union U, possible because its size is at most6<n.
That coordinate forces the same c; subtracting c*j_n then forces the same
triple and a. None is a constant vector, since a!=0 and T is a proper subset.
Adding the four distinct nonzero constants gives B_n>=12m+4.

A concrete falsification of dropping n>6 is the six-point system
T={1,2,3}, U={4,5,6}. Its image is exactly the vectors constant a on T and
constant b on U. The all-one vector is present, but there are only4*4=16
full-weight words, smaller than12*2+4=28. This violates an unqualified
full-weight assertion, not the frozen theorem. The n>6 hypothesis is sufficient
for the stated two high rows; this audit does not assert that it is minimal
for the n-3 row considered by itself.

If high and low indices coincide, keep the separately stated inequalities.
They cannot be added without proving disjointness of the two constructions.

## Exact complete-target specialization

In a complete simple SRG(99,14,1,2), every edge belongs to one actual
triangle. Distinct triangles cannot share an edge; hence the system is linear.
The14 edges at each vertex partition into seven incident triangles.
Counting vertex-triangle incidences gives m=99*7/3=231.

Every vertex has replication7, so Q=99*choose(7,2)=99*21=2079.
The total pair count is choose(231,2)=231*230/2=26565.
Thus the disjoint count is26565-2079=24486.

The six lower counts are exactly
    weight3:   4*231=924
    weight4:   4*2079=8316
    weight5:  12*2079=24948
    weight6:  16*24486=391776
    weight96:  4*231=924
    weight99: 12*231+4=2776.
These six target indices are distinct.

Row sums give N*j_231=7*j_99=2*j_99 overF5, so3*N*j_231=j_99.
This proves the constant-word premise directly. No left word, rank reduction,
triangle factor, automorphism or equitable profile is required.

## Exact character and shifted-constant check

Let C=ker(N^T) overF5 with ordinary dot product, and D=im(N).
Orthogonality gives D subset C-perp. Rank-nullity gives equal dimensions,
so D=C-perp. This is finite-field dot orthogonality, not ordinary real rank
or a divided Gram form.

For a nontrivial additive character psi ofF5, summing psi(u dot x) over x in C
is M=|C| if u is in D and0 otherwise. If u is not in D, shift the sum by an
x0 with u dot x0!=0; the nonunit character multiplier forces the sum to0.

For fixed x of weight w, choose j nonzero coordinates of u. At a zero
coordinate of x, summing over u_i!=0 contributes4; at a nonzero coordinate
it contributes-1. The generating expression is
    (1+4z)^(n-w)*(1-z)^w.
Its z^j coefficient is exactly
    K_j(w)=sum_h (-1)^h*4^(j-h)*choose(w,h)*choose(n-w,j-h),
with out-of-range binomial coefficients0. Finite interchange of the two sums
therefore gives sum_w A_w*K_j(w)=M*B_j.

For a lower bound B_j>=L_j, A0=1 and M=1+sum_(w>0)A_w give
    sum_(w>0) A_w*(L_j-K_j(w)) <= K_j(0)-L_j.
The direction and the constant are exact. There is no hidden multiplication
of the right side by an unknown M. If several constructions use one j,
each valid row may be retained, equivalently their maximum lower count.

A fully hand-calibrated case is one triple on three points.
D has B0=1,B3=4. C={x1+x2+x3=0} has
A0=1,A2=12,A3=12 and M=25:
weight2 chooses the zero coordinate and one of four opposite pairs;
weight3 chooses two nonzero entries except the four opposite pairs.
Here K3(0)=64,K3(2)=4,K3(3)=-1, so
64+12*4-12=100=25*4.
The shifted row is12*(4-4)+12*(4+1)=60=64-4.
For j1, K1=(12,2,-3) on weights0,2,3 and12+24-36=0.
For j2, K2=(48,-7,3) on those weights and48-84+36=0.
Dropping A0 or using right side-L_j would reject this valid case:
the actual nonzero shifted sum60 is not <=-4.

Scalar multiplication gives4|A_w for w>0. A later restriction to55..99
requires its separate accepted support55 premise. A target self-orthogonality
restriction requires its separate justification; it is not universal for
linear triple systems. In this same one-triple example, (1,4,0) is in C
but not in span(1,1,1), so C need not be a subset of D in the general theorem.

## Additional deliberate boundaries and hand controls

* Empty system: m=Q=0 gives four valid zero lower bounds; j_n is not
  automatically in the image.
* Duplicate triple columns: two copies of123 have only four weight3 image
  words, contradicting an invalid4m=8 count. DISTINCT is essential.
* Nonlinear system123,124: Q=2 while there is only one meeting pair.
  Its point count is4, so B5=0 and a false unqualified12Q=24 row fails.
* Linear Pasch system123,145,246,356: every two triples meet once, and
  each point occurs twice. OverF2 the sums123+145 and246+356 both have
  support2345; its image has only three weight4 words rather than Q=6.
* OverF5 those two cancelling words are respectively
  (0,1,1,4,4,0) and(0,1,4,1,4,0). Their values retain different outer partitions.
  A relation among all four columns would require all six c_i+c_j=0,
  impossible overF5. This is a field boundary, not a binary theorem approval.
* Rook9: its three row and three column triangles give m=6,Q=9;
  six same-orientation unordered pairs are disjoint. The low construction
  counts are24,36,108,96 at weights3,4,5,6. Since j is the sum of its three
  row columns, the high counts are24 at weight6 and76 at weight9.
* Rook overlap is explicit: j-N_row1=N_row2+N_row3. This weight6 word belongs
  to both constructions, so96+24 cannot be inferred as one count.
  No3125-word code census was executed or asserted.
* The zero left code has D=F5^99 with B_j=4^j*choose(99,j) and remains permitted.
  These rows do not force a nonzero kernel or a Conway99 conclusion.
* The abstract code span((1^55,0^44)) has enumerator1+4z^55, sum0 and
  self-dot0 overF5. It disproves a generic balanced/self-orthogonal-code
  contradiction shortcut; it is not claimed to be an actual triangle kernel.
* Quinary Griesmer at distance55 gives55+11+3+30*1=99 for dimension33;
  dimension34 requires100. This is weaker than the already independently
  derived conditional target dimension ceiling27, not a new rank result.

## Comparison, shared origin and limits

The two named binary candidate notes were read completely. Their low-image
count theorem needs the edge-unique-triangle graph premise for binary
cancelling-pair recovery; the Pasch boundary explains the difference.
The sharp character constant is classical and shared with that historical
proof. Native independently rederived it above, rather than transferring
a binary executable gate toF5.

Wave102's incidence/kernel first section and the indicated Wave46/80
MacWilliams sections were read in bounded excerpts. Wave171 failed-routes
was read completely. The inspected archive already emphasizes that ordinary
enumerators and self-orthogonality do not construct an incidence structure.
These reads are bounded overlap checks, not whole-archive novelty verification.
The archived exact computations are not freshly executed or endorsed here.

Root requested the direction; Structural authored the candidate. Native's
coefficient recovery, separate four-column challenge, high-count boundary,
character derivation and displayed hand cases are independent written work.
No source algorithm, backend, program enumerator or matrix computation was used.

The exact statement survives these challenges. All counts remain separate
lower bounds and all target conclusions remain conditional. No numerical
dimension, feasible code, actual target, external/formal review, novelty,
registered dependency or scientific execution is supplied.

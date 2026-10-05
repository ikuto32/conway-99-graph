# Independent written review: the R226 maximum deficiency is three

Completed verification: 2026-10-04T21:33:24.0719487+00:00.
Producer /root/structural; different written verifier /root/native_driver.
No mathematical program/import/AST/solver/census/worker ran. This independently
checks the new implication; the two explicit r1 premises remain inherited
mathematical results with their own authentic reviews, not retrospectively
rechecked at this timestamp. Metadata creation and Root acceptance are later.

## Exact statement and dependency boundary

I whole-read paper
docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_DEFICIENCY_UPPER3_V1.md,
SHA ffcf7c6cd4d8ec39b55d56378d4f9a9444e65d05c03250d87b64a294190d6c75,
and rawcandidate01, SHA
3b26951a5faa6a28aeee626f663baf76bf32bbcc7767f8a4179fa65f1e09fff3.
The exact ID is C-UNRESTRICTED-TARGET-ROOK-COUNT226-DEFICIENCY-UPPER3 r1:
in every complete finite simple target, actual R226 implies every deficiency
belongs to{0,1,2,3}. This is not an R226 exclusion.

Strict-second-neighbor-bound r1 gives D30=>max4. The distinct deficiency4-
boundaries r1 says that, if a d4 exists here, it is unique, a=26-2b-3c,
3<=b+2c<=6, each of its points has pure K1,4 with four d1 leaves, and it
is disjoint from every d2/d3. The newly sealed Native review of that literal
result is separately referenced; producer-time pending slots stay null.
No pending R227 result or general target conclusion is a premise.

## Parity uses the odd family, not only deficiency one

Suppose the unique d4 root T exists. O=D1 union D3 has s=a+c=26-2b-2c.
Local defect-degree sum is even, so the number of odd-deficiency roots at
every actual point is even. D1 alone need not have even incidence.

The three T points each have four d1 roots. These twelve triangles are
distinct since none can contain two T points. Their24 outer points are
distinct: in the same bucket repeated intersection violates triangle
linearity; in different buckets a shared point is a second common neighbor
of a central adjacent pair, contrary to lambda1. Each outer point has O
incidence at least2, and each center4. Hence3s>=12+48=60, so b+c<=3.
With3<=b+2c<=6 this leaves exactly
(b,c)=(3,0),(2,1),(1,2),(0,3),(1,1),(0,2).
No maximum-support/codeword assumption or equitable quotient is used.

## All three equality-support cases include every further actual edge

For the first three pairs, s20 makes the incidence bound exact. S27 consists
of three centers with O incidence4 and24 outerpoints incidence2. No further
O point is possible. Put w=half the O incidence: weights2 at centers and1
outside, sum30/squared norm36. Every outerpoint has exactly one central
neighbor, again by lambda1 on the central edge. Twelve central O triangles
contribute weighted edge5 each, the other8 contribute3 each:84. All edges
are distinct. T adds three edges of weight4, giving known weighted total96.

From A²=12I-A+2J and Aj=14j, Q=3I-A+J/9 is PSD, Q²=7Q and Qj0.
Y=3Qw=9w-3Aw+10j is integral,1mod3, sum0. The known O edges give Y4
at all S; T changes the three centers to-8. Thus initial inside norm576,
sum72. Let z be the nonnegative integer weighted sum of all other actual
S edges. Their neighbor increments t are nonnegative integers; weights1/2
give sum t<=2z. For y<=4/integer t>=0,
(y-3t)²-y²>=-15t. Therefore inside norm>=576-30z and sum>=72-6z.

For every integer y1mod3, y²+y-2>=0, with equality only y1/-2. All72
outside coordinates are included, so outside norm>=144+inside sum>=216-6z.
Total norm>=792-36z. Independently its exact value is
63wQw=63[3*36+30²/9-2(96+z)]=1008-126z.
Consequently90z<=216, and integer z<=2. The factor is63, not7.

Any point outside S carries no O root and no T. A d2 there requires at
least three d2 roots at that point because its local degree is2. For b1/2
this is impossible; each d2 is wholly-S and adds three internal edges.
For b3, an outside point must contain all three; there can be at most one
by triangle linearity. Each d2 still has two S points, and hence adds a
distinct edge of weight>=1. These edges are not O/T edges by lambda1.
Thus z>=3 in every first-three case, contradicting z<=2.

## The other cases retain actual labels and nonstar components

F nodes are positive actual triangles, degree3d; edges are uncovered local
rook pairs, not every intersection. There are45 actual uncovered squares.
For each remaining population I separately checked collapsed cycles and
K3,3 labels. A collapsed F4 needs four local degree>=2 roots; impossible
after the local disjointness checks below. Repeated K3,3 labels require
six local degree>=3 roots, more than the whole high population; distinct
labels give a forbidden actual induced rook. Thus F has45 faithful cycles
and180 required incidences. Codegree<=3 follows from actual crossmatching
for disjoint highs, common-point locality for intersecting highs, and low
degree3. No low F triangle occurs. High low-neighbor sets are independent
and their internal graph consists only of a retained high-high edge.

For each root B=sum_Ndegree-degree(root)-2e(N) bounds cycle incidence,
with no internal opposite pair. Low nodes with a low neighbor have<=5;
all-high lows may add1 only when their three high neighbors are independent.
Each independent high triple has<=3 common lows by pair codegree. These
are upper bounds on arbitrary partner patterns, never constant-profile claims.

(b,c)=(0,3): a17/P21. Two intersecting d3 would have r1 even, fan14+3r1<=21,
r1<=2. The only nontrivial sequence(3,3,1,1) is nongraphical (the lows
would need degree2 if both highs were universal); r1=0 is too small.
Three d3 at a point require odd r1>=1/fan24. Single d3 forces exactly
three low leaves by degree and fan. All four highs are disjoint, degrees
12,9,9,9. Bounds24,18,18,18 and at most12 all-high-low exceptions give
17*5+12+24+54=175<180.

(b,c)=(1,1): a21/P24. D4 is disjoint from both other highs. If d2/d3
are nonadjacent in F, high bounds24/12/18 and at most3 low exceptions
give162. If they meet geometrically, fan12+3r1<=24 with parity odd and
degree3 requiring r1>=2 gives r1=3. In sequence(3,2,1,1,1), xHH-yLL=1,
so high edge1/low edge0. D3 N8lows+degree6 givesB21; d2 N5lows+degree9
givesB18. All-high-low exceptions are absent because the high triple has
an edge. Complete incidence105+24+21+18=168<180. No omitted local
low-low branch or unjustified high independence is used.

(b,c)=(0,2): a20/P23. D3 intersection permits only r1=0/2 by fan/parity,
already nongraphical; r1=4 would cost26. The d3 roots are disjoint from
each other/T. At a single d3 point r1 may be3 or5: the latter is a star
plus a disjoint low edge, not falsely eliminated. Its nine root-neighbor
lows remain independent; B18 holds in either profile. D4 B24, at most3
low exceptions give100+3+24+36=163<180.

All six pairs fail, so the unique d4 permitted by the necessity cannot
exist. Strict mass had excluded deficiencies>=5, proving the literal
upper-three statement at actual R226.

## Independent challenge accounting and limits

Thirty-eight proof checks and twelve written failure/boundary challenges
give50 written checks, with six hand population rows. The twelve challenges
were: parity includes d3; outerpoints are distinct by actual central lambda1;
equality60 fixes support rather than only a lower bound; known edge84+12
is distinct; added edges remain arbitrary/integer; weights1/2 justify2z;
the -15t inequality is integer (a fractional t can break it); all72 outside
entries and factor63 are necessary; b3 concurrence has at mostonepoint;
K3,3 repeated-label and collapsed cycles are checked separately; valid
low-pair profile at d3/r1=5 is retained; exception bounds are upper counts
without asserted realization. None falsified the statement.

The paper's phrase 'their number is bounded below case by case' is editorial:
the proof and all actual uses supply upper bounds; the exact claim is unaffected.
Result PASS only for max3 at R226. Root supplied discovery outlines,
Structural produced the candidate, Native independently reconstructed this
whole argument; agreement is not evidence. The necessity and strict-mass
reviews keep their original scopes/times. No R226/R225/general target
exclusion, graph realization, rank or nonzero codeword conclusion, automorphism,
equity or novelty follows. No scientific/external/formal check, ledger parse,
protected/Git/index/publication mutation occurred; current457 is Root-reported.

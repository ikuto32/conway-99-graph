# Independent written audit: exactly thirteen ternary defects

Verifier `/root/structural`; discovery producer `/root`. The review is a
different-author exact derivation and falsification of the complete frozen
V2 paper, not approval by preliminary chat agreement. The report supplies
the actual review clock. Current source context observed read-only is
`d0c0dd7db0d3de420b1d718b59122b069df01107`; the new audit/report/binding are
not asserted present in that commit. Mathematical workers, enumerations,
executed fixtures, formal checks, external review, ledger/index mutations:
zero. Outcome **PASS** for precisely F3!=13 in the stated whole99/14 domain.

## Exact artifact, statement and sole dependency

The complete discovery read is
`docs/CANDIDATE_20261003_TERNARY_THIRTEEN_DEFECT_NONREALIZABILITY_V2.md`,
SHA256 `2b3dcd9469d8e21a5285693d798b0fc5b3304a702f1868d8f5e6ac7d4f2a2128`.
Its preserved V1 is
`docs/CANDIDATE_20261003_TERNARY_THIRTEEN_DEFECT_NONREALIZABILITY_V1.md`,
SHA256 `d926a2ddccaf571f6ef1c1e6ead869bf2cd258d2b355cde146b9dddb726f0df5`.
V1 had an ambiguous K2-join name despite explicitly nonadjacent highs;
V2 says two independent highs joined. No verdict below relies on V1.

For every symmetric binary integer 99-by-99 matrix A with zero diagonal
and exactly 14 ones in every integer row, put R=A^2+A-12I-2J and M=R
modulo 3 over GF(3). Let F3 count unordered off-diagonal nonzero pairs
of M. Then F3 cannot equal 13. Empty residual support is permitted.
This excludes only the whole thirteen-edge residual support; it does not
exclude a component of a larger support, resolve the target, establish a
combined lower14 bound, or assert sharpness or another defect realization.

The sole material dependency is revision 1 of
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`.
ROOT's independent audit is
`acceleration/audit_20261003_ternary_equal_outside_nine_v1.md`, SHA256
`0497fef0e3a9ca8558acc2aacdbc68abe6b9ef8db925e502765d02a85676be18`;
its exact filter report is
`acceleration/results/20261003_independent_review/ternary_equal_outside_nine_01/equal_outside_filter/summary.json`,
SHA256 `7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`.
This verifier authored its original discovery
`docs/CANDIDATE_20261003_TERNARY_EQUAL_OUTSIDE_BUDGET_NINE_DEFECT_V1.md`,
SHA256 `a67fe7e196228165b4fcccedef9e8956362d9248404766f0a0202ddd370670cd`.
Its required subproof is reproduced here, rather than treating that
discovery as an unverified self-authored assertion. No earlier defect
exclusion, support catalogue, incidence rank or lift theorem is a premise.

## Independently reconstructed residual and outside-word mechanism

The exact integer residual has diagonal 14-12-2=0 and row sum
196+14-12-198=0. Its off-diagonal entries are CN+A_uv-2>=-2. A field-zero
entry is a multiple of three, hence nonnegative; a residue-one or residue-
two entry has minimum -2 or -1. At support degree d with c1,c2 labels,
beta=2c1+c2 is a multiple of three by the zero field row sum, and
beta<=3 floor(2d/3). Total positive mass is at most beta. A paired
residue-one or residue-two positive entry is individually at most beta-2
or beta-1, because its own negative allowance must be removed.

Let S be the WHOLE nonisolated support, with m vertices and e=13 edges.
Minimum support degree is two, since one nonzero label cannot sum to
zero. Thus 6<=m<=13: five vertices supply at most ten pairs, while
the degree sum is exactly 26. These bounds do not assume connectivity.

Regular symmetry gives AJ=JA and AM=MA. Every outside M row/column
vanishes, so X M_S=0 for X=A[outside S,S]. Outside words are genuinely
binary. Degree-two rows have opposite labels and force their neighbors'
outside words equal. Degree-three rows have three identical labels and
force three neighbor coordinates equal: their binary sum can be only
zero or three when it is zero modulo three.

For equal outside neighborhoods of size t, both internal degrees are
d_A=14-t; their intersection is at least max(0,2d_A-m). Hence
CN>=14-floor(m/2) and R>=12-floor(m/2), independent of A_uv. At m<=11,
equal endpoints of degree at most four violate the good budget<=6 or
bad budget<=5. Thus degree-two neighbors must be high, meaning degree>=5.

The multiple-pair extension is independently immediate from the INTEGER
row, without assuming the pairs are A edges: if three outside words
coincide and m<=13, their three pair residuals are at least six. Each
of those three rows contains two distinct positive terms, so its beta
is at least twelve. Degrees<=5 have beta<=9; all three degrees are>=6.
A degree-three support vertex would therefore require three neighbors
of degree>=6. Simplicity forces m>=7, and their total degree is at least
3+3*6+2(m-4)=2m+13>=27, exceeding 26. No degree three is possible.

## Complete independent degree-two case exhaustion

For m<=11 put h=number of degree>=5 highs, r=number of degree-four
mediums and l=number of degree-two lows. These are all possible degrees
after degree three is excluded. A low requires two high neighbors,
so h>=2 and 3h+2r<=26-2m. Every low's two edges are already incident
with highs; no low can supply an extra medium or low neighbor.

**m=13.** All degrees equal two and beta=3. A low makes its two
degree-two neighbors' outside words equal, giving their R>=6. This
exceeds even their full beta. No higher-degree endpoint is available.

**m=12.** The degree excess is two. With no degree three, exactly one
vertex has degree four and all others degree two. A low forces two
equal-outside neighbors; R>=6 excludes degree two at either endpoint.
Both neighbors would need degree>=4, requiring excess>=4 rather than
two. This is a separate boundary calculation, not an illicit extension
of the degree-at-most-four filter to order twelve.

**m=11.** The excess is four; two required highs cost at least six.

**m=10.** Excess six forces two highs degree five and eight lows degree
two. All eight lows must meet both highs, contrary to degree five.

**m=9.** Excess eight permits only two highs and at most one medium.
A medium has at most two possible neighbors because lows are saturated
and there is no other medium. Without a medium, all seven lows meet
both highs, costing at least fourteen high incidences; their required
total is only 26-14=12. No degree/sign cases remain here.

**m=8, two highs.** Excess ten permits at most two mediums, each with
at most two highs plus one other medium as neighbors. They cannot have
degree four. With six lows, the exact thirteen-edge support is K2,6
plus its high-high edge. Each low's two field labels cancel. Summing
both high field rows leaves twice their nonzero mutual label, impossible.
This is signed-row cancellation, not an integer K2,6 lift premise.

**m=8, three highs.** No medium is possible; the five lows have degree
two and high degrees are (6,5,5). Their degree total sixteen minus
ten low incidences leaves six high incidences, so all three high pairs
are supported. Label the degree-six high a and others b,c. Their low
incidence counts are (4,3,3). If n_ab,n_ac,n_bc count the low neighbor
pairs, they solve n_ab+n_ac=4, n_ab+n_bc=3, n_ac+n_bc=3; thus (2,2,1).
Every high pair is forced equal outside by at least one low. Each
degree-five row now has TWO distinct integer residuals>=8, giving
positive mass>=16>beta<=9. This checks the repaired multiple-pair
argument and never equates a support edge to an actual A edge.
Four highs would already require excess twelve, so these exhaust m=8.

**m=7, four highs.** Excess twelve forces four degree-five highs and
three degree-two lows. High incidences internal to the four highs
would be 20-6=14, exceeding their maximum twelve.

**m=7, three highs.** At most one medium is possible. Without a medium,
the high degree sum is eighteen, so each high is degree six and
universal. Any degree-two low would then have at least three neighbors.
With one medium, the highs have degrees (6,5,5) and there are three
lows. Every low meets the universal degree-six high and a degree-five
high. These highs' outside words coincide, their M pair is supported,
and CN>=11 gives R>=9. The degree-five bad-pair allowance is at most
beta-1<=8, a contradiction. No actual A adjacency is used.

**m=7, two highs.** At most three mediums are possible. One or two
mediums have at most two highs plus one other medium as neighbors,
fewer than four. With no medium the five lows join both highs, with
their mutual high edge optional; these give only ten or eleven edges.

With three mediums the degree sequence is (5,5,4,4,4,2,2). Each medium
must join both highs and the other two mediums, and each low joins
both highs. The two highs have degree five and are NONADJACENT in H.
The exact support is two independent highs joined to K3 plus two isolated
points, with ten cross edges and three medium-triangle edges.

Each high has c1=1 or4; each medium c1=2 and each low c1=1. Total
label-one incidence is twice its edge count and therefore even, so
both high counts agree. Their outside words are equal by a low row.
If both high c1=1, beta=6 and their good R>=9 is impossible. If both
are four, eight high-side positive cross incidences include two on
the two low rows, leaving six on the high-medium edges. ALL six of
those edges are label one, and all three medium edges label two.
For any outside word with both high coordinates t, medium equations
2t-p-q=0, 2t-p-s=0, 2t-q-s=0 give p=q=s=t. A medium and a high now
have equal outside words and their supported pair has R>=9, exceeding
the degree-four allowance at most five (in fact four for label one).
This exhausts both signs; a field sign normalization has NOT been used
to replace this integer beta split.

**m=6.** A low's two highs must be degree-five universals; their mutual
M pair is supported. Their equal outside words give CN>=11, R>=9;
either degree-five bad-pair allowance is at most eight. This excludes
every degree-two case at order six without omitting medium configurations.

## The last six-vertex signed support and independently rebuilt kernels

If there is no degree two or three, minimum degree four gives 4m<=26.
Since m>=6, m=6 with exactly two degrees five and four degrees four.
Its complement has two isolated high vertices and four degree-one
vertices, hence exactly two disjoint missing pairs among the lows.
No other support order or disconnected shape is possible in this branch.

Let the highs be a,b. Each low has c1=2; each high c1=1 or4. As before,
the two high counts agree by parity of all label-one incidences. Replacing
the FIELD matrix M by -M if needed makes both high positive degrees one,
while low positive degrees remain two. Its kernel is unchanged. The
integer R and its negative budgets are never sign-reversed.

The positive graph has degree sequence (1,1,2,2,2,2). Its only path
has the two highs as endpoints; all other components are simple cycles
on the unused lows. Among four lows, any triple includes a missing pair,
because the two missing pairs partition the lows. Thus no low triangle
exists. The positive possibilities are exactly a high-high edge plus
the positive low C4, or a Hamilton path through all six vertices. A
three-vertex path plus a triangle is forbidden by that missing pair;
paths leaving one or two unused lows cannot be completed by simple cycles.

For the edge+C4 case, the two high field equations are x_b-sum(lows)=0
and x_a-sum(lows)=0. Hence x_a=x_b in every outside word. Their M pair
is supported. Using ORIGINAL integer signs and beta<=9, CN>=11 gives
R_ab>=9 while either possible bad label permits at most eight. This
also covers the opposite overall field sign, without assuming beta six
after normalization.

For the Hamilton case order its vertices (a,u,v,w,z,b). The missing
matching on the four lows must be uw and vz: uv,vw,wz are positive
path edges; the other possible complete matching would use one of
those edges. Direct reconstruction gives the full signed matrix

  [[ 0, 1,-1,-1,-1,-1],
   [ 1, 0, 1, 0,-1,-1],
   [-1, 1, 0, 1, 0,-1],
   [-1, 0, 1, 0, 1,-1],
   [-1,-1, 0, 1, 0, 1],
   [-1,-1,-1,-1, 1, 0]].

Here the high endpoint rows sum -3 and the low rows sum zero, all zero
in GF(3). From low rows v and w we get u+w=a+b=v+z. Adding low rows
u and z gives v+w=u+z. These two relations force u=v and w=z because
two is invertible. High row a then gives -2z-b=0, so b=z; high row b
gives -2u-a=0, so a=u. Low row u finally gives a+v-z-b=2(u-z)=0,
so all six coordinates agree. Conversely a constant vector makes all
six displayed rows zero; the exact kernel is its constant line.
Every outside word is therefore constant on all six support vertices.
Any supported pair incident with a low has R>=9, exceeding its degree-
four bad-pair upper bound five, irrespective of the original overall
field sign. This concludes the last branch.

## Twenty-eight written falsification and boundary checks

1. The exact99/14 diagonal, row sums and unordered degree total 26.
2. Both integer bad minima and beta's multiple-of-three upper bound.
3. Removal of a paired bad entry's own negative allowance.
4. Whole-support commutation and actual binary outside words.
5. Strict m<=11 pair filter and separate m=12 treatment.
6. Triple equality gives two distinct positive row terms, not a diagonal.
7. Degrees>=6, simplicity m>=7 and total>=27 exclude degree three.
8. All degree-two rows at m=13 have beta three and cannot meet R>=6.
9. m=12 has only one degree-four point but needs two higher endpoints.
10. m=11 needs excess six rather than its available four.
11. m=10 explicitly needs eight low neighbors at each degree-five high.
12. Both m=9 medium/no-medium alternatives are exhausted.
13. m=8 two-high mediums and both high-row signed cancellation terms.
14. m=8 three-high counts (4,3,3), pair counts (2,2,1) and mass16.
15. m=7 four-high internal incidences14 versus maximum twelve.
16. Both m=7 three-high medium alternatives and the original bad-pair budget.
17. All m=7 two-high medium counts zero through three are retained.
18. Exceptional m=7 highs are independent, with all thirteen edges counted.
19. High sign-count parity, and c1=1 branch's original beta-six veto.
20. c1=4 forces all six positive high-medium edges and three negative medium edges.
21. m=6 degree-two neighbors are universal and their M pair is bad.
22. Minimum-degree-four exhaustion gives precisely two disjoint missing pairs.
23. Field sign normalization changes only the kernel, never integer R or beta.
24. Positive path/cycle components include and explicitly veto P3+C3.
25. Edge+C4 kernel equalities veto the high bad pair under both original signs.
26. All Hamilton matrix entries, four low equations, both highs and constant converse.
27. Disconnected WHOLE support is included; no arbitrary component or target exclusion.
28. Preserved outline gap and V1 ambiguous join wording give no earlier approval.

The preliminary outline's m=8 individual-pair inference R>=9 was invalid:
support adjacency is not actual A adjacency and its coarse lower bound is
only eight. Before the paper was frozen it was replaced by the valid
multiple-pair mass16 argument, explicitly recorded in the discovery and
reconstructed here. The preserved V1 join phrase is editorial ambiguity;
V2 states the independent highs literally. Neither issue is silently erased.

Every whole-support order 6 through 13 has been exhausted with exact degree,
binary-word, field-label and integer-budget reasoning. No computational
catalogue, measured fixture agreement, numerical eigenvalue or older
defect exclusion enters the proof. This independently verifies exactly
F3!=13. It does not combine this with lower13 or modify any old claim,
publication, engine or validator. Any later composition needs its own
exact dependency statement and separate verification.

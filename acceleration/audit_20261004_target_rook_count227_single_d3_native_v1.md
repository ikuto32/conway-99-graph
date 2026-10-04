# Independent written audit: R227 with one deficiency-three triangle

Verification timestamp: 2026-10-04T19:01:59.4299721Z.
Mathematical producer /root/structural; independent verifier /root/native_driver.
Root suggested the follow-up/shared outline. No approval by agreement is used.

This audit binds C-UNRESTRICTED-TARGET-ROOK-COUNT227-SINGLE-D3-D2-POPULATION-UPPER2 r1.
Paper docs/CANDIDATE_20261004_TARGET_ROOK_COUNT227_SINGLE_D3_BOUND_V1.md,
SHA256c75f1295d17a9f1fee8fea30f72e30e714aae620ba33c359ac50f45ccb1917a3;
raw acceleration/results/20261004_target_rook_count227_single_d3_bound_candidate01.json,
SHA256b0fbd63defa758d7531a5f81a7c10f4a926a02a9bc06c6588552953e64f60dc0.
The entire151-line paper and116-line raw packet were read. All proof and
boundary checks below are independent written hand derivations. No mathematical
program, source import, backend, solver, enumeration or worker ran. No ledger,
Git/index, frozen cutoff or publication bytes changed. This is next-wave47 only.

## Exact scope and sole inherited premise

Take a complete finite simple SRG(99,14,1,2), with exactly227 actual induced
rook-nine vertex subsets counted once, and d_T=6-r_T for actual triangles.
Assume precisely one actual triangle T has d_T=3. The sole logical dependency
is C-UNRESTRICTED-TARGET-ROOK-DEFICIENCY-STRICT-SECOND-NEIGHBOR-BOUND r1,
whose exact canonical statement and Root written acceptance were read.
The weaker sixteen-row R227 result is comparison only and is not a premise;
no maximum-lower2 theorem is needed since T already has positive deficiency3.

The exact conclusion is b in{0,1,2}, a=21-2b and all deficiencies in{0,1,2,3}.
It excludes neither R227 nor any target, and asserts no retained population
realizable. Every step uses actual triangles/point labels rather than a uniform
profile, automorphism, nonconstant-codeword hypothesis or support-inducedness.

## Reconstructed local degrees, parity and fan

There are seven actual triangles at each vertex and231 in total. Distinct
triangles meet at most once and have unique edge partners. Three cannot meet
pairwise at distinct points, since those points would give an original edge
a second triangle partner. Two incident triangles determine at most one
rook: the four remaining grid vertices are their cross pairs' unique second
common neighbors. Therefore the simple local defect graph D_v has degree
d_T at T, for every v in T. A zero-deficiency node has no defect edges.

Each rook contains six actual triangles, giving D=6(231-227)=24. The sole
inherited strict bound24>=6m+6 gives every positive d<=3. With c1,

    a+2b=21,  P=a+b+1=22-b.

Local handshake gives even r1+r3, not d1-only parity. For a point's positive
fan, its2r outer points are distinct. Each deficiency d requires d external
positive defect partners at each of its two outer points. An external actual
triangle meets at most one outer point of the entire fan, by linearity and
the forbidden distinct-intersection triple. Thus

    P>=3r1+5r2+7r3.                                      (F)

Suppose b>=3. Then P<=19. At each of T's points r3=1 and r1 is odd. If r1=1,
degree3 needs r2>=2, forcing fan weight20; r1>=5 forces22; r1=3,r2>=1 forces21.
Therefore the local graph is precisely the star(3,1,1,1), with three d1
triangles and no d2. The three central buckets give nine distinct d1 partners
C. Their eighteen outer points are distinct: coincidences in one bucket
violate linearity and between buckets yield the forbidden triple with T.
These outer points are off T and on no other C.

## Odd parity capacity and its exact equality

At each of these eighteen points, its C contributes one odd d1 incidence
and T is absent. Odd-family parity forces another d1 triangle there. A d2
incidence is even and cannot fix the parity. There are s=a-9=12-2b other d1
triangles; C9 first implies s>=0. Since they have3s incidences in total,

    3s>=18,  so b<=3.

No assumption that the whole positive family has point multiplicity two is
made. The equality b3 is not rejected by parity alone.

At b3, a15 and s6. Exactly eighteen V incidences must cover eighteen distinct
C outer points, each needing at least one. Every V point therefore lies on
that outer set, every such point lies on exactly one V, and no V point lies
elsewhere. A V meets at most one outer C point in each central bucket, by
the actual fan geometry. It has three points, so one is in each bucket.
The support S has21 points: T3 and the18 outer points. All sixteen odd
triangles are precisely T, C9 and V6, lying wholly in S. Their three perfect
matching choices are arbitrary and are not assumed coincident.

## Independently counted weighted Gram equality

Give each central point weight3, each outer point weight1 and other points0.
Then sum w=27 and squared norm=3*9+18=45. Known triangle edge endpoint products
are T:3*9=27; each C:3+3+1=7, hence63; each V:3, hence18. Unique edge partners
prevent duplicating any known edge across these distinct triangles. The total
is108. A separate row check gives known weighted neighbor sum12 at a central
point (two central weights plus six outer weights) and6 at an outer point
(central3, C mate1, two V neighbors1+1). These checks agree with the energy.

From A^2=12I-A+2J, the full target has principal eigenvalue14 and eigenvalues
3,-4 on j-perp. Hence Q=3I-A+J/9 is PSD. On the known triangle union,

    w^T Qw=3*45-2*108+27^2/9=135-216+81=0.

Every further edge inside S has two strictly positive endpoint weights and
would decrease this expression by2w_xw_y. All known edges are actual edges,
so PSD prohibits every extra internal edge. Therefore the known union is
exactly G[S]. This derives inducedness; it is not an input assumption. It
uses the ambient target spectrum, not a generic21-point triangle union.

Every internal edge has its unique triangle partner in T,C,V. A different
actual triangle meeting S twice would contain that internal edge and thus
be that known triangle. None of the three d2 triangles is known odd, so
each meets S at most once and has at least two distinct outside points.

## Outside degree-two contradiction

All odd positive triangles lie in S, and the only remaining positive triangles
are the three d2 triangles. At an outside point z of one of them, no odd
triangle is incident. In the simple local defect graph the degree2 node
requires two distinct positive neighbors; zero nodes cannot supply them.
Both other d2 triangles must therefore contain z. Apply this at the at
least two outside points of one d2 triangle. The other two then meet it
twice, contradicting actual triangle linearity. This rules out b3.
The retained necessary rows are(a,b,c,P)=(21,0,1,22),(19,1,1,21),(17,2,1,20).
Their sums a+2b+3c=24 and P=22-b were checked by hand, not by an enumeration.

## Eight hand falsification boundaries

1. The valid star(3,1,1,1) has r1 odd but r1+r3 even; d1-only parity at T
   would be wrong. It is used only outside T where r3=0.
2. At b2, (3,2,2,1) is graphical (star plus edge between degree2 nodes) and
   has fan weight20=P. The star conclusion cannot be transferred to b0/1/2.
3. Six external d1 triples have exactly the18 incidences needed at b3; odd
   parity capacity alone does not exclude that boundary.
4. The three matching choices of V and C are unrestricted. No common-matching,
   rook count or faithful collapsed-defect-square assumption enters the proof.
5. The products27+63+18=108 and independent weighted rows12/6 retain all
   known actual edges; any extra edge strictly lowers zero energy, since
   every point of S has positive weight.
6. A generic local triangle union need not have the target ambient PSD. The
   argument does not assert its inducedness or impossibility without that premise.
7. Three d2 triangles at one point can give the valid simple K3 local degree2
   graph. One outside point is not itself a contradiction; two distinct shared
   outside points plus linearity are essential.
8. A zero-degree node cannot fill a missing defect partner even if it intersects
   a positive triangle. Positive roster completeness, rather than incidence
   multiplicity-two or a hidden equity assumption, limits the outside partners.

## Twenty-four explicit written proof checks

1. Exact R227 complete-target/actual induced-subset counting scope.
2. Seven point triangles and total231 from actual incidence.
3. Unique rook-pair geometry and exact local defect degrees.
4. Exact total deficiency24.
5. Sole strictmass premise gives maxd3.
6. c1 gives a+2b21 and P22-b.
7. Handshake parity of d1+d3.
8. Distinct actual fan outer points.
9. One external triangle supplies at most one fan outer incidence.
10. Fan coefficients3,5,7.
11. b>=3 gives P<=19.
12. All local alternatives at T except the star fail this fan ceiling.
13. Nine distinct d1 central partners.
14. Eighteen distinct outer C points off T.
15. Outside odd parity demands external d1 rather than d2.
16. s>=0 and3s>=18 give b<=3.
17. Equality b3 gives an exact6-triangle cover of18 points.
18. Every V uses one point per bucket without matching equality.
19. Complete odd roster T+C9+V6 and21-point support.
20. All108 edge products, sum27/norm45 and weighted rows12/6.
21. Full target Q PSD makes that support induced at zero energy.
22. Internal unique partners give D2 support intersection at most1.
23. Every D2 has at least2 outside points; only three positive nodes available.
24. Degree2 forces the other two at both points, violating linearity; all3
    retained rows have the correct sums and no realization claim.

The m3 weighted support mechanism overlaps the strictmass paper. Here parity
forces its six V while three extra d2 triangles remain, and their outside
degrees create the new contradiction. The weaker16-row result is comparison
only. Its original bytes and all other reports remain unchanged. No global
novelty, cited exclusion, formal/external review, worker gate or registration
is inferred. The exact r1 conditional statement survives this challenge;
R227, overall scientific coverage and the target remain UNKNOWN.
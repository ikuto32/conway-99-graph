# Independent written review: corrected intersecting D3 / b2 proof

Completed written verification: 2026-10-04T22:01:57.9291347+00:00.
Producer: /root/structural. Different author verifier: /root/native_driver.
Method: independent_derivation. Actual computational executor: null.
Outcome: PASS for the exact r1 conditional statement, with V2 source scope.

Claim: C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-TWO-D3-B2-NO-INTERSECTION r1.
Paper: docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD3_TWO_D3_B2_NO_INTERSECTION_V2.md
SHA256 deea56556dd520bffffbf484e6b2efef5469e5eb092567ac2d6d974661412279.
Raw: acceleration/results/20261004_target_rook_count226_maxd3_two_d3_b2_no_intersection_candidate02.json
SHA256 9eba53d256a1b19b84ac685c2304e6de473ebe8307e19528c71475f187136a77.
The literal statement, assumptions, empty dependency list and original pending
nulls are copied into the bound report. This review rereads the whole V2 proof;
it is not a scalar repair gate inherited from V1.

## Independently reconstructed target facts

In a complete finite simple SRG(99,14,1,2), every edge belongs to its unique
actual triangle. There are 99*14/6=231 actual triangles. Two distinct actual
triangles meet at most once. Three meeting pairwise at distinct points are
impossible: their three intersection vertices form a triangle sharing an edge
with one of them, contrary to lambda=1. A point's fourteen neighbors are seven
disjoint edges, hence seven actual incident triangles.

A rook containing an actual triangle corresponds bijectively to its compatible
local partner at each of that triangle's three vertices. Thus the local defect
degree is d_T=6-r_T at every such vertex. The global defect graph F on positive
actual triangles has edge labels equal to actual intersection points and degree
3d_T. Its deficiency mass is D=6(231-R). At R226 it is30, so under c2/b2 there
are a20 degree-one roots and P24 positive roots. F has45 edges.

At a point, the simple local graph has degrees 1/2/3 according to the actual
positive roots present. Its degree sum gives r1+r3 even. For every local root
of degree d, its two other vertices each have d positive partners. Those 2d
partners are distinct from the local roots and from other such partners: any
duplication violates triangle linearity or the distinct-intersection triple
prohibition. Therefore r1+2r2+3r3 multiplied as local-plus-outer counts gives
3r1+5r2+7r3 <= P24. This is an actual injection, not a profile assumption.

Each nonadjacent target pair has two common neighbors, which are nonadjacent
(otherwise their common edge would have two triangle partners). Consequently
there are (99*84/2)/2=2079 actual induced squares. An actual induced rook has
nine squares; a square has at most one containing rook, since its edge triangles
are unique. R226 therefore leaves2079-9*226=45 uncovered squares. Their four
edge triangles give an injective map into F four-cycles with four distinct labels.
Hence sum of cycle incidences in F is at least180. No faithful converse is needed.

## The common point forces the exact local high graph

Assume the two D3 triangles A,B intersect at p. There r3=2 and r1 is even.
The case r1=2/r2=0 would require a simple local graph with degrees (3,3,1,1):
both degree-three vertices would be universal, forcing each degree-one vertex
to have degree at least two. Adding a D2 gives fan25>24. Four or more D1 gives
fan26>24. With r1=0, degree three requires at least four nodes; the two available
D2 roots C,D must both occur, giving the valid K4 minus CD local graph.

All four high actual triangles now intersect only at p. A low actual triangle
intersecting two highs must contain p by the distinct-intersection prohibition.
There is no D1 at p; a common defect neighbor there would also need degree two.
Thus every low has at most one high neighbor globally. Lows in a high neighbor
pool have their degree-one local slot filled; two in the same local bucket
cannot be defect adjacent, and different buckets cannot meet without a loose
actual triple. Every such pool is independent, and each member has exactly two
remaining low-low edges. F high degrees are9,9,6,6 and all twenty low degrees3.

All pair codegrees are at most three. A pair including a low has this cap from
its degree3. Two highs have no common low; their common highs are just those
specified by the local K4-minus-edge graph. No F triangle contains a low:
three distinct labels would be a loose actual triple, whereas one label would
require local degree at least two from that low.

F contains no K3,3. If two grid labels coincide, triangle linearity and the loose
triple prohibition propagate concurrence to all six roots; every root would
then have local degree at least three, but only A,B are D3. If all nine labels
are distinct, their row and column triples give an actual rook. A diagonal
extra edge is forbidden because its endpoints already have two distinct grid
common neighbors. The selected defect edges contradict that actual rook.

A low has a low neighbor. Its three independent neighbors give three pairs of
potential opposites, each with at most two extra common neighbors, so at most
six cycles. Equality forces the chosen low neighbor's degree-three set to be
common to the other two neighbors, yielding K3,3. Hence each low has at most
five cycles, contributing at most100 in total.

## Full opposite decomposition, with the V1 omission restored

For any root, sum binom(|N(root) intersect N(opposite)|,2) over all other
opposites counts its cycles once. Opposites may lie inside or outside its
neighbor set; being a neighbor is not a reason to delete the contribution.

N(A) consists of B,C,D and six independent lows L_A. Its internal edges are
BC and BD. The internal opposite B therefore contributes exactly one through
its neighbors C,D; the other internal opposites contribute zero. All external
opposites are low. Write I for their neighbors in {B,C,D} and x for those in
L_A. We have I0/1. For I0, x<=3 and binom(x,2)<=3x/2. For I1, x<=2 and
binom(1+x,2)<=3x/2, including x0. The twelve LL stubs from L_A all reach
external low opposites. Thus c_A<=1+18=19, and independently c_B<=19.

N(C) consists of A,B and four independent lows L_C. Its internal edge AB has
maximum internal degree one, hence no internal opposite contribution. The
eight LL stubs give external LOW contribution at most12 by the same inequality.
There is also the external HIGH opposite D. It has common neighbors A,B and
no common low with C, so contributes binom(2,2)=1. Therefore c_C<=13. The
symmetric external high C supplies the same1 at D, so c_D<=13.

The one collapsed cycle A-C-B-D is counted internally at A,B and externally
at C,D, one incidence at each root. It is never equated with a target square.
The complete upper bound is100+19+19+13+13=164<180, which contradicts the
injective lower bound. This proves only the literal D3 disjointness statement.

## Independent checks and failed-boundary challenges

Thirty proof checks were completed on paper:
1. Unique edge triangles and231 total; 2. triangle linearity; 3. loose-triple
prohibition; 4. seven local roots; 5. local d_T degree; 6. global3d_T degree;
7. deficiency mass30; 8. a20/P24; 9.45 F edges; 10. fan injection;
11. local parity; 12. nongraphical(3,3,1,1); 13. two fan exclusions;
14. exact K4-minus-CD; 15. high concurrence onlyp; 16. low high-count cap;
17. independent low pools; 18. exact remaining LL stubs; 19. codegree cap;
20. low-triangle prohibition; 21. repeated-label K3,3 rejection;
22. distinct-grid rook rejection; 23. low cycle bound5;
24.2079 squares; 25. rook-square uniqueness and45 uncovered;
26. square-to-F4 injection; 27. internal A/B opposite1;
28. complete external low pools; 29. external C/D high opposite1;
30. total164 and exact conclusion.

Twelve failure/boundary challenges were checked on paper:
1. Local(3,3,2,2) is valid and cannot be rejected locally.
2. The collapsed cycle is retained rather than declared faithful.
3. Internal A/B1 and external C/D1 are incidences of the same cycle, not extras.
4. V1's12/12/162 omits C/D's high opposite and remains rejected.
5. I1/x3 is outside the actual degree-three domain.
6. I0/x3 is allowed and attains the safe low inequality.
7. I1/x0 contributes zero and does not create a fictitious stub.
8. A covered actual intersection is not automatically a defect edge.
9. An extra diagonal grid edge is rejected by lambda1, not assumed absent.
10. Distinct local buckets cannot be joined without the actual-label veto.
11. No disjoint c2/b2, c2 lane, R226 or target exclusion follows here.
12. No prior V1 gate, pending population theorem or shared agreement is a premise.

Total42 written checks; executed/formal/external/solver checks all zero.

## Provenance and limitations

The earlier Native veto report a3144351d3de865e04d5635c4fb2844ebb0496b3a023dc0134ac3a5cb33e81c0
and audit40f3156ca013d8d68485ba84ff053553190046eba1eb666c6614bf77772b58e2
remain preserved alongside the original V1 candidate. The literal proposed
theorem was not REFUTED; its old argument omitted a contribution. This fresh
whole V2 derivation is distinct from discovering that omission. Structural
authored the theorem/source; Root and Structural acknowledged the earlier
challenge. Shared mechanisms and agreement are not independent verification.

All logical dependencies are empty; the needed target geometry was rederived.
Review scope is the exact literal R226/maxd3/c2/b2 condition. No novelty,
construction, uniform profile, automorphism, broader nonexistence or target
resolution is asserted. Scientific coverage remains UNKNOWN, target resolution
NONE. Source-only document and selected metadata work: no mathematical program,
import/AST/backend/worker/census, ledger parse, Git/index/publication/protected
mutation, or historical-byte overwrite. Root-reported457 is context only.
The original paper's future-tense veto editorial sentence is preserved; its
raw V2 packet already binds the genuine existing veto with exact hashes.

# Independent written review: the R226 deficiency-four necessary lane

Completed verification: 2026-10-04T21:33:24.0719487+00:00.
Producer: /root/structural. Different written verifier: /root/native_driver.
No mathematical program, import, AST, solver, census or computational worker ran.
This audit preserves all candidate and earlier review bytes. Metadata sealing is
separate from this completed derivation and from any Root acceptance/registration.

## Exact object and inherited premise

I read the complete paper
docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_DEFICIENCY4_BOUNDARIES_V1.md,
SHA256 ba19a46fdf1fc24e5173ca905a52b1f2ab7d2f2440415b1536c1150c441dfe8b,
and candidate01, SHA256
49d76fc8d12d4465d9a7016c103ab82d209425fc304a0dacf65c0d14f7cb7700.
The exact r1 ID is
C-UNRESTRICTED-TARGET-ROOK-COUNT226-DEFICIENCY4-BOUNDARIES.
Its literal statement is retained in the bound report; this is a necessary
restriction assuming R226 and at least one d4, not an R226 exclusion.

The sole uses_result premise is strict-second-neighbor-bound r1, with the
literal canonical binding edbfc835f0f6ee7b507f563960178111e11fc04d59adb08f4f96190902dcc6cf.
It gives D>=6m+6 at positive deficiency. At R226, D30 implies m<=4.
Its immutable report retains the original16:28:28Z review and transitive
evidence. No pending R227 result is a premise here.

## Reconstruction of the actual local objects

A complete SRG(99,14,1,2) has 693 edges and 231 actual triangles, since every
edge has exactly one triangle partner. Distinct triangles share at most one
point, and three triangles cannot have three different pairwise intersections:
those three points would give an edge an extra triangle partner. Each point
lies on seven triangles. The positive local defect graph has one node per
positive triangle through that point and local degree equal to its deficiency.
Rook occurrence is counted by actual nine-vertex sets, once. A covered pair
of intersecting triangles has a unique such rook completion. Thus the global
defect graph F is simple, has degree3d_T at T, and D30 gives45 edges.

If r_i counts local roots of degree i and P is the total positive triangle
population, its fan requires 3r1+5r2+7r3+9r4<=P. Each other positive triangle
can meet at most one outer fan point: two in one root violate linearity, and
two in different roots violate the preceding three-intersection rule.
The local degree sum gives r1+r3 even. These statements concern actual point
labels; no quotient, equity or relabeling assumption is used.

Write a,b,c,d for populations1,2,3,4. Then a+2b+3c+4d=30 and
P=30-b-2c-3d. A degree4 node needs at least four other local nodes.

## Complete degree-four profile check

Two d4 roots at a point imply d>=2/P<=24. Their fan18 leaves at most6,
which cannot pay for the three additional nodes required. Three local d4
already cost27 while P<=21; larger counts only worsen the bound.

For one d4 with one d3, parity makes r1 odd. With r1=1, at least two d2
are needed to reach five nodes and the fan is29. With r1=3/r2=0, the
sequence(4,3,1,1,1) is nongraphical: degree4 is universal, leaving the degree3
node needing edges to residual-zero leaves. Larger r1/additional d2 exceed27.
With two d3, r1 even: r1=0 requires two d2/fan33, r1=2 gives29. Three d3
already give30 with the d4. These exhaust the d3 alternatives.

With one d4/no d3, r1 even and r1+r2>=4. The only possibilities under27 are
(r1,r2)=(4,0),(2,2),(4,1),(6,0), of fan21,25,26,27. For r1=0, r2>=4
costs29; r1=2 permits only r2=2; r1=4 permits r2=0/1; r1=6 permits only0.
The graphs are respectively K1,4; universal d4 plus a d2-d2 edge;
d4-d2 with three low leaves at d4 and one at d2; K1,4 plus disjoint low edge.
In the third row, high-high x and low-low y satisfy x-y=1, so x1/y0.
The valid sequence(4,2,2,1,1) is retained; it is not rejected as nongraphical.

## Multiple d4 roots: arbitrary actual partner multiplicities

For d>=2, P<=24, so all d4 point profiles are pure K1,4. Distinct d4
triangles are disjoint; each has twelve distinct d1 partners. If a low meets
t d4 roots then t<=3. Hence 12d<=3a and a<=30-4d force d<=3.
Disjoint actual triangles have cross edges forming a matching of size<=3:
one point cannot be adjacent to two points of the other triangle by lambda1.
Each cross edge has a unique third partner. Therefore any d4 pair has<=3
common lows and sum binom(t,2)<=3binom(d,2). Also binom(t,2)>=t-1 even at0,
so the lower bound is12d-a, with no omission of lows having t0.

For d3, a=18-2b-3c gives lower18+2b+3c>9. For d2, a=22-2b-3c gives
2+2b+3c<=3, forcing b=c0/a22. The number of double partners is2 or3;
no constant partner multiplicity is inferred.

## Faithful square counts and complete incidence bounds

The target has2079 actual induced squares, and each actual rook contributes
nine distinct squares, with a square belonging to at most one rook. Thus
R226 has45 uncovered squares. A distinct-label F4 gives such a square and
conversely. A collapsed F4 requires four local degree>=2 roots. All small
cases below have at most three high nodes, so collapse is absent. Consequently
C4(F)=45 and sum of root cycle incidences is180.

A K3,3 with repeated geometric labels forces all six roots to share a point
with local degree>=3, unavailable here. With distinct labels it gives an
induced rook, contrary to its defect edges; lambda1/mu2 forbid added grid
edges. Thus no K3,3 occurs. Codegrees<=3 follow from the actual matching
argument for disjoint highs, the common-point rule for intersecting highs,
and low global degree3. Common lows of intersecting highs would need two
local slots, which deficiency1 forbids; at most one remaining high can help.

No F triangle contains a low. At a high root, low neighbors have their only
local slot filled by that root; different root-point buckets cannot meet.
The internal neighbor graph consists only of the explicitly retained high
edge and has maximum degree1, so it contributes no internal opposite pair.
For N=N_F(T), B=sum_N degree-degree(T)-2e(N), external opposite codegrees
l<=3 give c(T)<=B. If B is not divisible by3, equality would require only
l0/3 and is impossible, so c(T)<=B-1. A low with a low neighbor has c<=5;
attaining6 forces K3,3. An all-high low can add one, but its three highs
must be independent, and with exactly three highs there are at most3 such
exceptions by their pair codegree. These facts retain the local high triangle.

For d2/a22, each high has independent twelve-low N and B24. All lows
have a low neighbor (only two highs), giving110+48=158<180. Thus d=1.

If b+2c<=2, the following exhaustive bounds contradict180:

|b,c|actual F high arrangement|complete incidence upper bound|
|---|---|---:|
|0,0|one d4|26*5+24=154|
|1,0|d4 and d2 with no edge|24*5+24+12=156|
|1,0|d4-d2 edge|24*5+27+21=168|
|2,0|three-high triangle at one point|22*5+27+21+21=179|
|2,0|d4 isolated, d2 pair nonadjacent in F|22*5+3+24+12+12=161|
|2,0|d4 isolated, d2 pair adjacent in F|22*5+24+15+15=164|
|0,1|disjoint d4/d3|23*5+24+18=157|

For b2/P25 a d2 meeting d4 brings both d2 to the same point: the single
d2 profile needs26. D4 then has ten lows/two degree6 highs/internal edge,
B28 and c<=27; each d2 has four lows/degrees12,6/internal edge, B22 and
c<=21. This is the crucial179 rather than a loose181. If the d2 pair meets
geometrically but is covered/nonadjacent in F, it remains in the isolated-F
161 case; actual disjointness is not needed for that branch. For an adjacent
d2 pair each B15. With b0/c1 the local profile proved their disjointness.

## Conclusion and hand boundaries

The single d4 has b+2c>=3, hence P<=24 and only pure K1,4 at each point.
It is disjoint from all other high triangles. Fan21<=P=27-b-2c also gives
b+2c<=6. The twelve necessary pairs are c0/b3..6, c1/b1..4, c2/b0..2,
c3/b0. These are hand scalar possibilities, not realizations or a census.

I challenged twelve distinct failure boundaries: maximum4 inherited at the
exact count; local degree4 needs five nodes; parity includes d3; fan25 graph
is valid; nongraphical(4,3,1,1,1) does not reject larger valid profiles; t0
is retained; actual crossmatching requires lambda1; F edges differ from actual
intersection; high triangles invalidate global F triangle-freeness; collapsed
cycles need four local high nodes; B28/B22 equality loses one; extra partner
multiplicities and covered high intersections remain included. None falsified
the exact statement. Forty explicit proof checks plus these twelve boundary
checks give52 written checks; twelve scalar rows are additional hand coverage,
not executed tests. No external/formal verification was used.

Result PASS for the literal r1 necessary statement only. Shared Root discovery
outlines and Structural production are explicit; independent reconstruction
does not mean independent discovery. Prior fan/square/archive mechanisms
overlap is disclosed, not novelty. No d4-at-other-count, R226 or target
exclusion, uniform profile, automorphism, codeword or graph construction
follows. Root exact acceptance and registration are separate. Current457
baseline is Root-reported only; it was neither read nor changed.

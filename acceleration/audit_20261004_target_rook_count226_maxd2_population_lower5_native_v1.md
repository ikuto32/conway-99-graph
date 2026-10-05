# Independent written review: R226/maxd2 requires b>=5

Completed written verification: 2026-10-04T22:17:47.0625025+00:00.
Producer /root/structural; different author verifier /root/native_driver.
Method independent_derivation; computational executor null. Outcome PASS.
Exact claim C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD2-D2-POPULATION-LOWER5 r1.
Paper docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD2_D2_POPULATION_LOWER5_V1.md
SHA256 b5581b9432d05e0c43835b5c12ffe0f70fc44d3f2ee88706ad0ac213b3db83e9.
Raw acceleration/results/20261004_target_rook_count226_maxd2_d2_population_lower5_candidate01.json
SHA256 68a80bb7bc436fed277f54f2a31337e1851069049ec0b0ce54d2401bab95d94d.
The exact statement, literal maxd2 assumption, empty dependency list and original
pending nulls are retained. This independent whole review verifies necessity
only, not realization or exclusion of the maxd2 lane/R226/target.

## Actual rook and defect foundations, rederived

Each target edge has a unique actual triangle partner, giving99*14/6=231 actual
triangles. Two distinct triangles meet at most once. Three pairwise distinct
intersection points form a triangle sharing an edge with one of the originals,
contrary to lambda1. Thus three pairwise intersecting triangles concur.
A target point's fourteen neighbors form seven disjoint edges, the seven
incident actual triangles.

An actual rook containing a designated triangle T pairs it with exactly one
of the six other triangles at each vertex, its crossing row/column. Two
specified intersecting row and column triangles determine that rook at most
once: each opposite pair of their outer points already has their common point
as a common neighbor, so mu2 fixes the other common neighbor, determining
the four remaining points. This is uniqueness conditional on existence.
It implies r_T<=6 and local defect degree d_T=6-r_T at each vertex of T.
Every rook has six actual triangles, so summing gives sum d_T=6(231-R)=30.
Under literal maxd2, a=30-2b, positive population30-b, b integer0..15.

Let F have positive actual triangles as vertices and uncovered local rook
pairs as labeled edges. Their labels are actual intersections and degree is
3d_T: lows have3, highs6. It has45 edges. Each of4158 nonadjacent target
pairs has two nonadjacent common neighbors and defines an induced square,
counted by two diagonals, giving2079 squares. A square determines its unique
edge triangles at a corner, and those intersecting triangles determine at most
one containing rook. Each actual rook contains nine squares. Therefore R226
leaves45 uncovered squares. Their four edge triangles are distinct positive
roots joined by four distinct corner labels in F. A covered pair would force
the square into its rook through the same unique completions, impossible.
The corner labels recover the square, so the map is injective and gives
C4(F)>=45 and total cycle incidence at least180. Extra collapsed F4s remain.

For disjoint actual high triangles, cross edges form a matching: a vertex
outside an actual triangle cannot be adjacent to two of its vertices without
giving an edge a second common neighbor. Each of at most three cross edges
has its unique completing triangle, so high pair codegrees are at most3.
Intersecting highs' common roots must all contain their unique point; local
degree2 bounds their common F neighbors by2. A pair including a low has its
global degree3 cap. Thus all pair codegrees<=3, with covered actual intersections
retained rather than equated with F edges.

No F triangle contains a low: distinct labels would be an actual loose triple,
and equal labels would require local degree at least2 at a D1 root. No K3,3
occurs. A repeated grid label propagates all six roots to one point by linearity
and the loose-triple veto, requiring local degree at least3 against maxd2.
All-distinct grid labels give the actual row/column triangles of a rook;
additional diagonal edges are forbidden by lambda1 because those endpoints
already have two grid common neighbors. Its row/column defect pairs contradict
the rook.

## Exact general low/high cycle bounds

A low has three independent F neighbors. Their three pairs have at most two
common opposites beyond the low, so it has at most6 cycles. If it has a low
neighbor, equality6 forces that neighbor's entire degree-three set to be
common with the other two neighbors, a K3,3. Therefore such a low has<=5.
Only a low whose three neighbors are independent highs can be exceptional,
adding at most1. There are at most3 exceptional lows per independent high
triple by the pair codegree bound. This is a safe upper population bound.

For high Z, every low in N(Z) has its local degree-one slot filled by Z.
Two such lows cannot have an F edge in the same bucket, nor in different
buckets without a loose actual triple with Z. A low cannot be adjacent to
another high in N(Z). Edges internal to N(Z) are between highs in the same
bucket; at local degree2 they form a matching. For b<=4 there are at most
three high neighbors, hence at most one internal edge. It gives no internal
opposite with two neighbors and therefore zero internal cycle contributions.

Let k_Z count high F neighbors and t_Z the internal matching-edge count.
The exact external stub sum is
B_Z=sum_(N(Z))deg-deg(Z)-2e(N(Z))=12+3k_Z-2t_Z.
For every external high or low opposite, codegree l<=3 gives choose(l,2)<=l,
so c_Z<=B_Z. Equality requires every nonzero l=3; if B_Z is not divisible
by3 then c_Z<=B_Z-1. All high opposites are included in this sum; it is not
an external-low-only estimate. Summing the safe bound gives12b+6e_H-6tau.

## All b0..3 cases

At b0,30 lows and no exceptional high triple give total<=150.
At b1,28 lows contribute140, the single high12, total152.
At b2,26 lows contribute130; no high edge gives high24/total154, while its
one high edge gives high30/total160. Covered actual high intersection with
no defect edge remains in the first case.

At b3,24 lows and three highs have four complete graph types:

| high graph | low upper | high upper | full upper |
|---|---:|---:|---:|
|empty|123|36|159|
|one edge|120|42|162|
|two-edge path|120|48|168|
|triangle|120|45|165|

Only the empty high graph has one independent triple and permits three
exceptional lows. A high triangle has actual concurrent roots; each B_Z=16,
so each c_Z<=15. Separate low-low local matching components remain outside
the high N pools and are retained in the24 low count. All totals are<180.

## All eleven four-high graph types, without program enumeration

Here a22, the baseline low bound110 and summed high bound48+6e_H-6tau.
There are eleven unlabeled simple graph types on four highs: by edge count,
one at0, one at1, two at2, three at3, two at4, one at5 and one at6. This
elementary complete edge-type split gives the following hand table.

| high graph | edges | triangles | independent triples | complete upper/status |
|---|---:|---:|---:|---|
|empty|0|0|4|170|
|one edge|1|0|2|170|
|two disjoint edges|2|0|0|170|
|two-edge path plus isolated|2|0|1|173|
|triangle plus isolated|3|1|0|170|
|four-node path|3|0|0|176|
|triangle plus pendant|4|1|0|176|
|three-leaf star|3|0|1|179|
|four-cycle|4|0|0|162 common labels /170 distinct labels|
|diamond|5|2|0|impossible local degree3|
|K4|6|4|0|impossible local degree3|

The eight generic numeric rows are110+3*(independent triples)+48+6e_H-6tau.
They are170/170/170/173/170/176/176/179, each<180. Diamond/K4 contain two
high triangles sharing an F edge. Actual concurrence of each triangle and
linearity of the shared roots put all four actual triangles at one point.
A shared root would have three local defect neighbors, contrary to maxd2.

## C4 special case: retain collapsed external high opposites

Write A-B-C-D-A for the high C4. Adjacent equal labels propagate all four
triangles to one point by the actual loose-triple prohibition; equal opposite
labels also put all four at one point, then linearity forces every edge label
equal. Therefore either all four labels are distinct or all four coincide.
No partial label pattern is dropped.

For all labels equal, a low cannot be a defect neighbor of two highs: actual
intersection with both would force the common point and local degree2 for it.
For A, N has B,D and four independent lows L_A, each with only A as high
neighbor and two LL stubs. All external low opposites have I0/1 high neighbors
among B,D and x in L_A, with x<=3-I, so choose(I+x,2)<=3x/2. The LL sum8
gives<=12. The external HIGH C has common B,D and no common low, contributing
one more. N is independent, so no internal contribution. Thus every high
has c<=13, including its external high opposite, and total110+52=162.
The same collapsed cycle is counted at each of its four roots. No faithful
square-cycle converse is asserted; injection180 suffices for contradiction.

For all labels distinct, opposite actual triangles A,C are disjoint, as are
B,D. An extra opposite intersection would make a loose actual triple with an
adjacent high; an intersection equal to an existing label would repeat a
pair intersection. A low cannot be an F neighbor of two adjacent highs, so
it has at most two high neighbors and if two they are an opposite pair.
All lows have LL neighbors, still giving total<=110.

Let n_AC,n_BD be the respective common LOW counts. Each opposite high pair
already has two common HIGH neighbors, so codegree<=3 gives both n<=1.
For A, four independent lows L_A have8-n_AC LL stubs. The external HIGH C
contributes choose(2+n_AC,2)=1+2n_AC, exactly for n_AC0/1.
For an external LOW opposite Z, let I count B,D neighbors and x L_A neighbors.
For I0/1, choose(I+x,2)<=3x/2. For I2, x<=1 and choose(2+x,2)=1+2x,
whose excess above3x/2 is1+x/2. There are at most n_BD such opposites and
their x sum<=n_BD. Thus their extra correction is at most3n_BD/2.
All other low contributions use the exact LL sum8-n_AC; no internal opposite
contributes. Consequently
c_A<=1+2n_AC+3(8-n_AC)/2+3n_BD/2
    =13+n_AC/2+3n_BD/2<=15.
For C the same AC/BD roles apply; for B,D they swap. Independently bounding
each high by15 gives total<=110+60=170<180. No equality/realization or symmetric
distribution of the n values is assumed. All external high, exceptional I2
low, ordinary low and internal pools are exhausted.

Therefore every b0,b1,b2,b3,b4 case contradicts injection180. The full original
integer domain0..15 yields b>=5, with every remaining value outside this proof.

## Independent checks and failure boundaries

Thirty-eight proof checks on paper:
1. Whole source/raw statement; 2.231 actual triangles; 3. triangle linearity;
4. loose-triple prohibition; 5. seven local triangles;
6. conditional intersecting-row/column rook uniqueness;
7. r_T<=6/local defect degree; 8. mass30/a30-2b;
9. complete b0..15; 10. global degree3d and45edges;
11.2079 squares; 12. covered-square uniqueness;
13.45 uncovered; 14. injective required180 without converse;
15. disjoint-high cross matching; 16. intersecting-high local cap2;
17. all codegrees<=3; 18. low-triangle prohibition;
19. repeated-grid K3,3 contradiction; 20. distinct-grid induced rook;
21. low5/equality6 obstruction; 22. independent-triple exceptions;
23. internal high-neighbor matching; 24. zero internal opposites;
25. full external B_Z formula; 26. integer loss;
27. b0/b1; 28. both b2 cases; 29. all four b3 cases;
30. complete eleven graph-type split; 31. eight generic totals;
32. diamond/K4 actual concurrence; 33. C4 label dichotomy;
34. collapsed external high1 and162;
35. distinct opposite actual disjointness and n<=1;
36. LL8-n plus I2 correction; 37. all high15/total170;
38. exhaustive b0..4 rejection and exact lower5 conclusion.

Fourteen failure/boundary challenges on paper:
1. Rook uniqueness is conditional and does not construct a rook.
2. Actual covered high intersections may have no F edge.
3. Separate low-low local matching components remain in the population.
4. Low exceptions are not equated with realizable common-high sets.
5. Generic high C4 bound182 is insufficient and requires its special split.
6. Diamond/K4 are ruled out by actual local degree, not abstract graph absence.
7. Collapsed C4 is retained rather than classified as an uncovered square.
8. Its high opposite1 cannot be omitted from the low-only12 estimate.
9. I0/x3 and I1/x2 are both within the exact degree-three domains.
10. I2/x0 contributes1 and must not be bounded by3x/2 alone.
11. I2/x1 contributes3 with correction1.5, not a false1.5-only estimate.
12. n_AC/n_BD are independently allowed0/1 without a uniformity assumption.
13. Larger high populations may have more internal matching edges, but are
    outside the b<=4 formula's scoped proof.
14. Maxd2 is a literal assumption; b>=5 values and R226/target stay unexcluded.

Total52 written checks; twenty-one hand rows (b0 one, b1 one, b2 two,
b3 four, b4 eleven plus the second C4 label branch and integer-domain coverage
record). Executed/formal/external/solver counts zero. No scientific census,
enumeration program or source import occurred.

## Provenance and scope

Root shared the small-topology outline; Structural authored and challenged the
whole source. Native independently reconstructed all eleven types and both
complete C4 opposite decompositions. Shared outlines are not verification,
independent discovery or novelty. Every necessary target fact was rederived;
logical dependencies are empty. Arbitrary actual target edges, covered pairs
and local matching components remain. No equitable partition, automorphism,
uniform incidence, selected inducedness or codeword existence is assumed.
Original bytes, pending nulls and authentic timestamps remain unchanged.
Verification time differs from later metadata creation. Scientific coverage
UNKNOWN and target resolution NONE; no full maxd2/R226 exclusion. No program,
import/AST/backend/worker/census/solver, ledger parse or Git/index/publication/
protected mutation. Root-reported457 is context only. Exact new Root review
and administrative registration remain separate.

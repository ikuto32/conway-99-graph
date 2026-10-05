# Independent written audit: ordinary b4 high path or cycle

Verification completed **2026-10-04T21:09:51.1591567+00:00** by Native
(`/root/native_driver`), method `independent_derivation`. Structural is the
mathematical producer. No computational executor or mathematical worker exists.

## Exact frozen claim

Whole paper
`docs/CANDIDATE_20261004_TARGET_ROOK_COUNT227_FOUR_D2_NO_HIGH_PATH_OR_CYCLE_V1.md`,
SHA256 `686b6cc9a93f92f3287111171ceb001fce89b6b36767d71bf52e47db0bda4165`,
and whole candidate
`acceleration/results/20261004_target_rook_count227_four_d2_no_high_path_or_cycle_candidate01.json`,
SHA256 `ff088e86b702732f14e8aa9887004aca475fab4e27bb84a6ff1525d4d6a9063c`,
were independently derived and challenged. Exact ID
`C-UNRESTRICTED-TARGET-ROOK-COUNT227-FOUR-D2-NO-HIGH-PATH-OR-CYCLE` r1.

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once and let d_T=6-r_T. Suppose R=227, every d_T is0,1 or2,
and exactly four triangles have deficiency2. Suppose every point used by the
sixteen deficiency1 triangles lies in exactly two of them, with support S,
and all four deficiency2 triangles lie in S. Their actual intersection graph
cannot be P4 or C4.

**PASS for this literal conditional exclusion.** Dependencies are empty.
Ordinary selected support and all high roots lying in it are explicit
hypotheses, not a transferred gate from the topology paper. Root supplied
inner/opposite-root discovery outlines; Structural produced the whole frozen
proof and separately obtained the C4 outline. Native independently checks
the complete counting and actual labels below. Shared agreement is not proof.

## Target geometry reconstructed without a descendant premise

Lambda1 gives a unique actual triangle per edge and seven triangles through
each point. Thus there are231 triangles. Actual triangles meet at most once.
Three pairwise intersections at three different points would give an edge
two triangle partners; such a loose triple is impossible.

Two actual triangles through v have four outer points, no cross edges, and
the four cross pairs each have a unique second common neighbor beyond v.
Those four neighbors are distinct: a repeated row/column neighbor would give
an edge two common neighbors, as would a repeated diagonal neighbor. They
therefore fix at most one induced rook completion. Each rook containing T
determines its covered partner at each of T's three points; conversely the
partner fixes that rook. The uncovered-pair graph at a point has degree
d_T at T. In the global defect graph F each actual triangle consequently
has degree3d_T; another root cannot occur twice by triangle linearity.

Each rook contains six actual triangles, hence total deficiency
6(231-R)=24. With four d2 roots and no larger deficiency, a16 and P20
follow. The selected incidence2 hypothesis gives S24. At a point with
r1 lows/r2 highs, the full positive fan needs at least3r1+5r2 roots:
each root's two outer points need respectively2d_T additional partners,
and no off-point root can be used by two concurrent roots, by no-loose
triples. At a high point r1=2, so r2<=2 from20>=6+5r2.

The only local positive degree sequences are (1,1), (2,1,1) and
(2,2,1,1), producing K2, P3 and P4. In the last case a high-high edge
is necessary: omitting it forces both lows to have degree2. Its remaining
edges attach one distinct low to each high. Thus all actual high
intersections are defect edges. No local four-cycle exists.

## Actual-square bijection, K3,3 and codegrees

F has16 degree3 lows,4 degree6 highs and36 edges. On an F four-cycle,
if adjacent labels coincide then three roots concur; the fourth must also
concur by no-loose triples. An opposite label repetition likewise makes
all four concur. This would require a local four-cycle, absent above.
Distinct labels are four actual vertices joined cyclically in the four
roots. Either diagonal edge would have two common cycle neighbors and
violate lambda1, so the square is induced.

Conversely the unique edge triangles of an induced actual square give the
four-cycle. A rook containing either corner pair contains the opposite
corner fixed by mu2, and therefore the entire square. The corner pair
fixes at most one rook. The square is uncovered precisely when all its
corner pairs are defects, so the inverse map is unique. There are4158
nonadjacent pairs and hence2079 squares, counted by their two diagonals.
Each induced rook has9 squares and none has two rook completions. Thus
C4(F)=2079-9*227=36, with node-cycle incidence144.

In a defect K3,3, any repeated grid label propagates concurrency to all six
roots: two column roots meet there, so a third row meeting both must also
contain that point. Each root would then have local degree3, contrary to
maxd2. With nine distinct labels, each row and column is its actual
triangle, giving the induced nine-point rook. Any extra nonrook edge has
two common grid points and violates lambda1. Its row/column pairs would
be covered, contradicting their defects. Both cases prohibit K3,3.

Two disjoint high roots have a cross-edge matching of size at most3:
one point cannot meet two points of another triangle. Every common F
neighbor uses such an actual edge, whose triangle completion is unique.
Intersecting highs have common F neighbors only at their common point;
the local P4 has none. Pairs involving a low have codegree<=3 from its
degree. Hence all F codegrees are<=3.

No F triangle contains a low: distinct labels give a loose actual triple,
while concurrent labels would need its local degree2 instead of1. A low
node has at most6 four-cycles, from three neighbor pairs each with at most
two other common neighbors. If it has a low neighbor and attained6,
that neighbor's complete three-node neighborhood would be shared with
both other neighbors, making K3,3. It therefore has at most5. An all-high
low has an independent high neighbor triple. The P4/C4 independence
number is2, so there are no such exceptions and the16 lows contribute<=80.

## Complete root/opposite-node partitions

For any high T its low neighbor set is independent. Same-point lows at T
have their pair covered in a P3; different-point intersections would form
a loose triple. No such low is also adjacent in F to a high intersecting
T: at the same point its local slot is already filled by T, and at a
different point it would make a loose triple. Under P4/C4 its high
neighbors have no mutual edge either. Thus all six neighbors of T are
independent.

Every opposite node of a cycle through T lies outside T and this independent
neighbor set. Put l_O=|N(O) intersect N(T)|. The exact formula is
c_T=sum_O binom(l_O,2). Each l0..3 satisfies binom(l,2)<=l, and the sum
of l is the neighbor degree sum minus6. For a P4 endpoint, one high and
five low neighbors give6+15-6=15, so both endpoint cycle bounds are15.
No inside opposite cycles or hidden high opposites are discarded.

## P4 independent calculation

Label high path A-B-C-D. Let n_AC,n_BD count low common neighbors of
the indicated disjoint high pairs. Their common high B,C respectively
already consumes one of the codegree3 slots, so each n<=2.

At B, neighbors are A,C and four lows L_B. Each such low has high
profile B or BD: A/C are forbidden by their intersections with B.
Exactly n_BD have the latter profile. Their low-low degree is1, while
the others have low-low degree2, giving8-n_BD stubs. L_B is independent,
so all these stubs end at opposite lows. The only opposite high is D,
whose l is1+n_BD. Its cycle contribution is at most3n_BD/2 for n0,1,2.

For an opposite low Z, let I be its high neighbors among A,C and x its
low-low neighbors in L_B. Its degree gives x<=3-I. At I0 or1, its cycle
contribution is<=3x/2. At I2 it contributes1+2x with x0/1, or
3x/2+1+x/2. The I2 lows are exactly the n_AC lows, all outside N(B).
Their total x, X, is<=n_AC. Every low-low stub is counted exactly once
in sum x=8-n_BD. Consequently

    c_B<=3n_BD/2+3(8-n_BD)/2+n_AC+X/2
        <=12+3n_AC/2<=15.

At C the same complete partition interchanges n_AC and n_BD, giving
c_C<=15. All four high bounds are15, so total incidence<=80+60=140,
contradicting144. The cancellation never assumes the n values equal.

## C4 independent calculation

Label the high cycle A-B-C-D-A. Opposite pairs AC and BD already have
two common highs, so n_AC,n_BD<=1. At A, its four lows have high profiles
A or AC; hence low-low stubs8-n_AC. The sole opposite high C has
l=2+n_AC, contributing1+2n_AC for n0/1.

For opposite lows I counts high neighbors among B,D and x counts
neighbors in L_A. The same exhaustive I0/1 and I2 bounds apply. I2
occurs at n_BD lows with total X<=n_BD. Thus

    c_A<=1+2n_AC+3(8-n_AC)/2+n_BD+X/2
        <=13+n_AC/2+3n_BD/2<=15.

At every other high the opposite counts either stay or interchange.
All four are<=15, giving the independent140<144 contradiction.

## Thirty-two proof checks and ten written falsification controls

The32 proof checks are: unique triangle/231; no-loose/linearity; rook
pair uniqueness; local d_T; global3d_T/D24; a16/P20; ordinaryS24;
fan/r2<=2; K2/P3/P4; actual HH=defect; no collapsed F4; actual square
faithfulness; inverse covered-corner equivalence;2079/9/36/144;
repeated-label K3,3; distinct-grid K3,3; disjoint high codegree;
intersecting/low codegrees; no low F triangle; low5 and exceptions;
independence2; root low independence; no internal HL/HH edge;
opposite-node formula; endpoint15; P4 n caps; P4 profiles/stubs;
P4 opposite high; P4 I2/X/cancellation; C4 n/profiles/stubs;
C4 high and I2 decomposition; both complete140 scope.

Ten hand controls:

1. Local (2,2,1,1) needs its high-high edge and distinct low attachments.
   A collapsed local C4 would give the lows degree2 and is invalid here.
2. Repeated K3,3 labels are not assumed distinct: concurrency forces
   local degree3. An abstract K3,3 with no actual label geometry cannot
   replace that target argument.
3. A degree3 low whose three neighbors are high can attain the crude6;
   it is excluded here by path/cycle independence2, not maxd2 alone.
4. I0/x0,1,2,3 contributes0,0,1,3; I1/x0,1,2 contributes0,1,3.
   Each is<=3x/2, without identifying an actual graph realization.
5. I2/x0 contributes1 even though x0, while I2/x1 contributes3.
   Omitting the baseline1 would falsely strengthen both bounds.
6. In P4, opposite high n0/1/2 contributes0,1,3, safely bounded by0,3/2,3.
   LL stubs8-n remain8/7/6, so the stated cancellation is valid.
7. P4 n_AC0/1/2 gives inner bounds12,27/2,15; the opposite-pair count
   may differ and is never assumed uniform across roots.
8. C4 opposite high n0/1 contributes1/3. Omitting the existing cycle
   among the four highs would lose the baseline1.
9. C4 (n_AC,n_BD)=(0,0),(1,0),(0,1),(1,1) gives13,27/2,29/2,15.
   Fractional upper bounds are sound, not claims of fractional cycles.
10. An ordinary high star has an independent leaf triple and needs a
    separate low-exception calculation. This audit neither rejects that
    graph nor broadens literal support hypotheses to all b4.

This is42 written checks (32 proof,10 hand), no executed, formal,
external, solver or scientific checks. Small source/metadata reads and
selected identity hashes only. Historical mechanisms are openly shared;
all actual label and opposite-node arguments are rederived. No imported
code, mathematical program, census, worker, ledger parse, Git/index or
publication/protected mutation occurred. Verification/worker starts and
executor are null. Root exact new acceptance is null at metadata creation.
Only P4/C4 under the stated ordinary-support assumptions is excluded;
target resolution NONE and overall scientific coverage UNKNOWN remain.

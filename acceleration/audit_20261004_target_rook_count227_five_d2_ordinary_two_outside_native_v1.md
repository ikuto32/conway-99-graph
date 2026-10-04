# Independent written audit: ordinary b5 support with two outside points

Verification completed **2026-10-04T20:37:14.5938314Z** by Native
(`/root/native_driver`), method `independent_derivation`. Mathematical
producer Structural; no computational executor or worker is involved.

## Exact frozen source and result

Whole paper
`docs/CANDIDATE_20261004_TARGET_ROOK_COUNT227_FIVE_D2_ORDINARY_TWO_OUTSIDE_POINTS_V1.md`,
SHA256 `be3621b85bd10a5d6ca9b3b961a0b1a7bdadfa5cbece6af6f6edc96d81afe0a6`,
and whole raw
`acceleration/results/20261004_target_rook_count227_five_d2_ordinary_two_outside_points_candidate01.json`,
SHA256 `031ff160a35f2b0d06d14fd81cb24e2b0c7f0cd594042817446c5cdeae967805`,
were separately reconstructed and challenged. Exact r1 ID:
`C-UNRESTRICTED-TARGET-ROOK-COUNT227-FIVE-D2-NO-ORDINARY-TWO-OUTSIDE-POINTS`.

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once by their vertex sets, and put d_T=6-r_T for each actual
triangle. Suppose R=227, every d_T belongs to {0,1,2}, and exactly five actual
triangles have deficiency two. Suppose every vertex used by the deficiency-one
triangles lies in exactly two of them; let S be their support. It is impossible
that exactly two outside-S vertices lie in deficiency-two triangles.

**PASS for exactly this ordinary multiplicity-two/h2 conditional branch.**
Dependencies are empty; all foundations below follow the target and literal
hypotheses. Root discovered the leaf-cycle argument and Structural produced
the frozen whole proof. Their shared outline is not the independent check.
Native's previous e<=50 neighbor refinement is neither used nor approved.
No fourfold/h1/all-b5/R227/target exclusion is made by this package.

## Fresh target and fan geometry

Each vertex has fourteen neighbors, whose induced graph is a matching by
lambda1. Hence it lies in seven triangles. The693 actual edges each lie in
one triangle, so there are231 actual triangles. Distinct actual triangles
meet at most once. Three triangles meeting pairwise at three different
points are impossible: those points form a triangle, giving any one of
its edges the original third point and the new intersection point as two
triangle partners.

Intersecting triangles T,U have at most one actual induced rook completion.
Given their common point and four outer points, each cross outer pair has
that point and a unique second common neighbor. The four second neighbors
fix the nine-set whenever a rook exists. In a rook containing T, at each
point of T exactly one other rook triangle meets T. Its six possible
incident partners are therefore covered by exactly r_T distinct rooks.
The uncovered local graph at that point has degree6-r_T=d_T at T.
An uncovered partner has positive deficiency as well; a D0 node cannot
participate in a local defect edge.

Every rook has six actual triangles, giving total deficiency
6(231-R)=24. Five D2 leave fourteen D1 and P=19 positive triangles.
For a positive fan with r1 D1/r2 D2 roots, each root's two outer points
require d_T uncovered partners. No external actual triangle meets two
outer fan points: two on one root violate linearity, and two on different
roots give the forbidden distinct-intersection triple. These partners are
distinct and are not other fan roots. Thus P>=3r1+5r2.

The stipulated D1 incidence2 gives |S|42/2=21. At an outside point on D2
there are no D1 roots. A simple degree-two local positive graph needs at
least three nodes, while19>=5r2 permits at most three. Its three roots
therefore form a local K3. The two outside points p,q each use three of
five D2 roots; they share exactly one by linearity. Write them as

    C={p,q,u}, A={p,a1,a2}, B={p,b1,b2},
               D={q,d1,d2}, E={q,e1,e2}.

All nine displayed S points are distinct. Same-fan repetition violates
linearity. A cross-fan repeated leaf point is a second common neighbor
of adjacent p,q, whose unique common neighbor is u. A leaf cannot equal
u either. Any selected D1 triangle contains at most one of p's S
neighbors, since two adjacent p-neighbors give their actual edge both p
and its selected triangle's third point as common neighbors. The same
holds for q. A selected root through u contains no other displayed point,
because u already neighbors both p and q. Every selected root thus
contains at most two D2 S-support points, and those through u only one.

## Labeled defects and all actual square counts

Form F on the nineteen positive actual triangles, with an edge for each
uncovered intersecting pair, labeled by its actual common point. It is
simple by triangle linearity. A D1 node has degree3, a D2 node degree6,
and |E(F)|=(14*3+5*6)/2=36. All local defect graphs are determined:
K3 at p/q, P3 at each of the nine displayed S points (D2 center, two D1
leaves), and K2 at each of the other twelve S points. Elsewhere they
are empty. In particular none has a four-cycle.

Consider a four-cycle of four distinct F nodes. If successive edge labels
repeat at v, three roots pass through v. The fourth either also passes
through v, or its intersections with the two nonconsecutive roots give a
forbidden distinct-intersection triple. In the first case linearity makes
all four labels v. If opposite labels repeat, all four roots immediately
pass through v, with the same conclusion. Thus a cycle either collapses
entirely into one local graph or has four distinct labels. The local list
excludes the collapsed case. Four distinct labels form an actual square;
a diagonal would have both other corners as common neighbors, violating
lambda1 for an adjacent pair. This proves inducedness from the complete
target rather than assuming a generic labeled-graph correspondence.

The unique actual triangle on each square edge recovers the four F nodes.
A rook through a corner pair necessarily contains the opposite square
corner, since it is the unique second common neighbor of the two outer
points of that corner. Conversely a rook through the square contains its
corner pairs. Therefore a square is uncovered exactly when these corner
pairs are defects. The four-node/point maps are inverse. A square has at
most one rook completion, already fixed by a corner pair.

There are4851-693=4158 nonadjacent pairs. Each has exactly two common
neighbors, which are nonadjacent (otherwise lambda1 fails on their edge).
It supplies a square diagonal; each induced square has two diagonals.
Hence2079 actual induced squares exist. Each rook has exactly9 squares,
and the unique-completion property prevents duplicate covered squares.
Thus F has2079-9*227=36 four-cycles and its total node-cycle incidence
is144. No local collapsed F cycle is included in that count.

## Defect K3,3 and codegree bounds

Suppose F has a K3,3 on six distinct actual roots, with a3-by-3 grid of
cross-intersection point labels. If two labels in one row coincide at v,
one row root and two column roots meet at v. Every other row root must
meet those two column roots at v: otherwise they form a forbidden
distinct-intersection triple. The remaining column root then meets two
row roots through v, so it too passes through v. If repeated labels
initially occur in different rows and columns, those four roots already
pass through v and the same argument propagates to all six. Thus any
repetition makes all six roots concurrent. Every root then has at least
three local defect partners, contradicting d_T<=2. Distinct nine labels,
in contrast, give six complete row/column triangles. Any extra grid
nonneighbor edge has two grid common neighbors and violates lambda1.
The grid is an induced actual rook, contradicting its defect cross-pairs.
This excludes only a defect K3,3; an even six-triangle selected rook in
another setting is not prohibited.

For disjoint high actual triangles, cross edges form a matching of size
at most3. If one endpoint met two points of the other triangle, their
edge would have two triangle partners. Every common F neighbor completes
one such cross edge, uniquely by lambda1. Their F codegree is<=3.
Intersecting high roots can have a common F neighbor only through their
own intersection, since distinct intersections would make a loose triple.
Here the only high-high intersections are p/q with three high roots,
so such codegrees are<=1. A pair including a low node has codegree<=3
from its degree. These statements cover every pair of F nodes.

Every low has at most two high F neighbors by the selected-root support
bound, so it has a low F neighbor. No F triangle contains a low: distinct
labels give a forbidden loose triple, and a common label gives that low
local degree2 instead of1. A low's three neighbor pairs each supply at
most two other common neighbors, so its cycle count is<=6. Equality
would make all three neighbor-pair codegrees3. Choose its low neighbor W.
Since deg_F(W)=3, both other neighbors would contain all of N_F(W).
The two triples are disjoint: any cross membership among the chosen
neighbors creates an F triangle containing the original low. They would
therefore form a K3,3, already excluded. Each of fourteen low nodes has
cycle contribution<=5, totaling at most70.

## Four leaf roots: complete opposite-node decomposition

For leaf A, N_F(A) consists of C,B and four distinct lows L_A, two at
a1 and two at a2. A selected root cannot use both A endpoints, so these
lows are distinct. At a common endpoint their low pair is covered by the
local P3, hence is not an F edge. At different endpoints, an actual
intersection would make a loose triple with A. Thus L_A is F-independent.
C or B cannot meet one of these lows: it meets A at p, while that low
meets A at an S point, so a further actual intersection would make a
loose triple or violate linearity. The induced neighbor graph is exactly
the single edge CB. Its vertices have internal degree1 or0, giving no
inside opposite-node contribution to a four-cycle through A.

Each L_A low already has one high neighbor A. Its only possible second
high is D or E, at most one. Let m count the lows with such a neighbor.
The other lows have two low-low neighbors, these m lows only one. Total
low-low stubs from L_A equal8-m, all ending outside L_A.

Opposite high D or E has C as a common F neighbor with A, and t further
neighbors in L_A. Its codegree1+t<=3 gives t0..2. Each qualifying low
has at most one of D/E, so the two t values sum to m. Since
choose(1+t,2)<=3t/2, their total contribution is<=3m/2.

For an opposite low Z let I count its F neighbors among C,B and x its
low-low neighbors in L_A. I<=1 is a geometric condition: if Z met both
actual C and B, their common point p would force it through p, outside
S, or three different intersections would violate lambda1. I is a count
of F neighbors, not a count of coincident point labels. If I1, degree3
leaves x<=2 and choose(1+x,2)<=3x/2. If I0, x<=3 and
choose(x,2)<=x<=3x/2. Summing x over all opposite lows counts exactly
the8-m stubs, since L_A is independent. Their contribution is therefore
<=3(8-m)/2. Every opposite node has been covered. Consequently

    c_A<=3m/2+3(8-m)/2=12.

The argument applies to each of B,D,E with its own m. It does not impose
a common m, equal profiles or an abstract incidence pattern.

## Common root and complete contradiction

N_F(C) comprises A,B,D,E and two lows through u. Its internal graph is
exactly AB and DE. The two lows cannot meet any leaf, because a selected
root containing u contains no other displayed high support point, and
they cannot contain outside p/q. Their pair is covered at u. Again every
internal neighbor degree is at most1, so no inside opposite-node cycles
occur. The degrees of these six neighbors total4*6+2*3=30. Remove six
edges back to C and twice the two internal edges, giving total external
neighbor incidence30-6-4=20. All external codegrees l<=3 satisfy
choose(l,2)<=l. Thus c_C<=20.

The total node-cycle incidence is at most

    fourteen lows*5 + four leaf highs*12 + common high*20
    =70+48+20=138<144.

The required144 counts every actual uncovered square exactly. This is the
contradiction for the literal ordinary/h2 branch, without a Gram edge
range or Native e<=50 refinement.

## Thirty-six proof checks and twelve hand challenges

The36 proof checks cover: target triangle count; linearity; no-loose
triple; intersecting-rook uniqueness; local defect degree; D24/a14/P19;
support21; fan injection; outside three roots; exactly one shared root;
nine distinct S points; selected p/q support bound; special u bound;
simple F/degrees36edges; complete local shapes; adjacent repeated-label
collapse; opposite repeated-label collapse; faithful induced square;
corner-rook equivalence; inverse mapping/unique completion;2079 square
count;9 per rook/no duplicates;36 F cycles/144 incidences; K3,3 repeated
label propagation; distinct-label induced rook; high-disjoint cross-edge
matching; high-intersecting concurrence; all codegrees3; each low has a
low neighbor; no low F triangle; low bound5; leaf independent set/internal
CB; second-high types/stub sum; opposite-high bound; opposite-low I and
complete leaf12; common root20 and final138<144.

Hand challenges:

1. A local K3 has triangles but no four-cycle. The two allowed global
   high K3s are retained; global triangle-freeness would be false.
2. A D2 center plus two D1 leaves has the P3 local degree sequence2,1,1,
   with no low-low defect edge. Its four-cycle contribution is zero.
3. A generic linear triple family {a,b,x},{b,c,y},{c,a,z} has a loose
   triple; the actual target rejects it since edge ab has two partners
   x and c. Linearity alone cannot establish the square correspondence.
4. A repeated-label six-root K3,3 requires local degree at least3, not a
   permissible multiplicity-two replacement. Distinctness is proved before
   applying the actual induced-grid argument.
5. An even selected six-triangle rook is allowed generally. The forbidden
   K3,3 here consists of defect edges, which the same rook would cover.
6. The leaf internal CB edge and common internal AB/DE edges are preserved;
   they have no inside-opposite contribution because their degrees are1.
7. For t0,1,2 the opposite-high counts are0,1,3 and bounds0,3/2,3.
   At t2 the scalar bound is attained, so no omitted rounding is used.
8. For I1 and x0,1,2 the counts are0,1,3, bounded by0,3/2,3.
   An extra high neighbor can only reduce the admissible low degree.
9. For I0 and x0,1,2,3 the counts are0,0,1,3, bounded by0,3/2,3,9/2.
   The x3 slack is intentionally retained, not silently set equal.
10. Every m0..4 gives3m/2+3(8-m)/2=12. Individual leaf m values may
    differ; no uniform leaf profile or realizable equality is inferred.
11. The common-node incidence is30-6-2*2=20. Subtracting its two
    internal edges only once would give the wrong count22.
12. A low may meet leaf A and opposite high D at distinct p/q-side
    support points; this allowed possibility is m, not forbidden. In
    contrast meeting intersecting C and B forces their actual point p.
    Common F neighbors are triangle nodes, not their intersection labels.

This is48 written checks (36 proof,12 hand), with zero executed, formal,
external, solver or scientific checks. The finite t/I tables are hand
arithmetic, not computer enumeration.

## Provenance, scope and metadata boundaries

Earlier square/codegree/K3,3 mechanisms overlap the stated R228/R227
archive comparisons and are independently reconstructed here. Earlier
weighted edges and Native e<=50 are comparison only, not logical premises.
The unchanged factor-nine outline and failed earlier weighted-wrapper
metadata remain saved provenance, not theorem refutations or gates for
this different exact statement. No novelty or exhaustive-archive claim.

Selected small metadata reads/hashes and new written artifacts only. No
mathematical program/import/AST/syntax/backend/worker/census/solver,
ledger parse, Git/index/publication operation or protected edit occurred.
Start/executor times remain null; Root acceptance is null at creation.
Only this literal branch is excluded, pending separate Root exact review
and nextWave47 registration outside closedWave46 cutoff449.

# Independent written audit: ordinary support and high topology at b4

Verification completed **2026-10-04T20:57:33.0462908Z** by Native
(`/root/native_driver`), method `independent_derivation`. Mathematical
producer Structural; no computational executor or worker.

## Exact frozen source and result

Whole paper
`docs/CANDIDATE_20261004_TARGET_ROOK_COUNT227_FOUR_D2_ORDINARY_SUPPORT_TOPOLOGIES_V1.md`,
SHA256 `f40e99a2b53aea39ab02ad332cacd1202c9bd193bb8d4673732aec918030b488`,
and whole raw
`acceleration/results/20261004_target_rook_count227_four_d2_ordinary_support_topologies_candidate01.json`,
SHA256 `c4c5110d2a3dc63df431acee2ca0e619f7608bcbf09468e52e338fe8fee70e03`,
were independently reconstructed and challenged. Exact ID
`C-UNRESTRICTED-TARGET-ROOK-COUNT227-FOUR-D2-ORDINARY-SUPPORT-TOPOLOGIES` r1.

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once by their vertex sets and put d_T=6-r_T for each actual
triangle. Suppose R=227, every d_T belongs to {0,1,2}, and exactly four actual
triangles have deficiency two. Then there are sixteen deficiency-one triangles.
Every vertex used by them lies in exactly two of them, so their support S has
twenty-four vertices. All four deficiency-two triangles lie wholly in S, and
their actual intersection graph is a four-node star K1,3, a four-node path P4,
or a four-cycle C4.

**PASS for this exact necessary restriction.** None of the remaining three
topologies, b4 itself, R227 or target existence is excluded or constructed
here. Root supplied topology and norm outlines; Structural produced the
whole frozen candidate. Native supplies the separate derivation below.

The sole mathematical dependency is
`C-UNRESTRICTED-TARGET-ROOK-COUNT227-NO-FOUR-D2-COMMON-POINT` r1,
relation `uses_result`. Exact binding
`acceleration/results/20261004_independent_review/target_rook_count227_four_d2_common_point_native01/claim_binding_schema2.json`
SHA `ba845921017175de16810e69425290244762500b4c600b00e32946f56d552939`,
report SHA `bdecc58d5517aa19aaba379253d1c626da4e700c2cba89dd5659e0005664522f`
and Root exact-scope receipt
`20261004_target_rook_count227_four_d2_common_point_root_written_acceptance01.json`
SHA `b2ac211bd6915ef3ef61d358d60d8ca09cfb40b2388f40e89f55c53c33818fca`
were read. Its exact R227/maxd2/b4 statement directly forbids all four high
roots through one point. No noD3, b5, stronger descendant or literature
statement is inherited. Existing premise manifests retain their complete
identity maps; this audit does not repeat their earlier fifty-check proof.

## Selected support, outside roots and first weighted bounds

Lambda1 makes neighborhoods matchings, hence seven triangles per vertex
and231 total. Actual triangles are linear and cannot meet pairwise at
three distinct points: an edge would get two triangle partners. Two
intersecting triangles have at most one induced rook completion by the
four cross-pair second common neighbors. Thus the local uncovered-pair
graph has degree d_T at T, at each point of T.

Total deficiency6(231-227)=24 gives a16, b4 and P20. Local degree sums
are even, so the selected D1 point incidence is even. Every outer point
of a selected r-root fan has another selected triangle by this parity.
An external selected triangle cannot meet two such outer points, by
linearity/no-loose triples. Therefore16>=3r, and positive selected
incidences are2 or4. With k incidence4 points and w half incidence,

    |S|=24-k, sumw=24, ||w||^2=24+2k.

The full positive fan has P>=3r1+5r2 by counting the two outer defect
partner sets of each root. At an outside-S point there is no D1 root;
local degree2 needs at least three D2 nodes, and20>=5r2 permits at most
four. The sole inherited theorem excludes four. Two outside points each
on three of four roots would share at least two roots, violating linearity.
Thus h0 or h1, and h1 means exactly three roots at one outside point.
The fourth high is wholly S in that case. No all-high-points-in-S premise
is used yet.

The48 distinct selected edges contribute weighted48+8k+ell, where ell
counts selected edges between peaks. D2 edges are distinct from these
and one another. They give at least H12 inside edges at h0, H6 at h1.
All positive edge products are at least1 and all additional edges stay
in E. Complete target Q=3I-A+J/9 is PSD, Q²=7Q and Qj0, so

    q=w^TQw=136+6k-2E<=40-10k-2ell-2H.

It is strictly positive because Qw has integer-plus8/3 coordinates.
Consequently h0 permits only k0/1 and h1 only k0/1/2. This is a first
bound, not the ordinary-support conclusion.

## Exact local graphs, actual squares and general cycle bounds

F has twenty actual positive-triangle nodes, degree3 at each of sixteen
lows and6 at each of four highs, hence36 edges labeled by intersections.
At S, r1=2 permits r2<=2, while r1=4 permits r2<=1 by the P20 fan.
Their local degree sequences give precisely K2, P3, P4, 2K2 or P3+K2.
For(2,2,1,1), the high-high edge is necessary: otherwise the two highs
would give both lows degree2. The remaining high-low edges are a matching,
so this local graph is P4. At h1 the only outside local graph is K3.
None of these graphs has a four-cycle.

Any repeated label on a four-cycle forces all four actual roots through
that same point, by linearity and no-loose triples, hence is absent by
the local list. Distinct labels give an actual induced square: a diagonal
would have two common neighbors in violation of lambda1. The unique edge
triangles invert the map. A rook through one square corner pair contains
the opposite corner fixed by mu2, so the square is uncovered precisely
when its corner pairs are defects. A corner pair fixes at most one rook.
There are4158 nonadjacent pairs, giving2079 squares by their two diagonals;
each rook contains9 distinct squares. Thus C4(F)=2079-9*227=36 and
complete node-cycle incidence144.

A repeated grid label in a defect K3,3 propagates all six roots to one
point via no-loose triples and requires local degree3, violating maxd2.
Nine distinct labels give an induced actual rook, since any extra grid
nonneighbor edge has two common grid neighbors, contradicting its defect
pairs. Thus no defect K3,3 occurs. Disjoint high roots have at most three
cross edges, a matching with unique triangle completions. Intersecting
highs have common F neighbors only at their intersection: at S the local
high pair has no such low partner, and at p only the third high qualifies.
Every codegree is<=3, including low pairs by low degree3. No F triangle
contains a low node (distinct labels give a loose triple; one label needs
its local degree2 instead of1).

A low node with a low neighbor has cycle count<=5: the crude three
neighbor-pair bound is6, but equality would use its low neighbor's entire
three-node neighborhood twice and make a disjoint defect K3,3. A low
with all three neighbors high can instead have count6; those three highs
must be independent. This exception is retained, not silently omitted.

For high T with k_T high F neighbors, its neighbor-degree sum is
18+3k_T. A low neighbor has no internal edge to another neighbor: its
local degree1 is filled by T, and another bucket intersection makes a
loose triple. Internal high edges are matching or empty in the cases
used below. Their internal degree<=1 gives no inside opposite-node
four-cycles. Thus the complete external opposite-node incidence is

    B_T=18+3k_T-6-2e(N_F(T))
       =12+3k_T-2e(N_F(T)).

External codegrees l0..3 give c_T=sum choose(l,2)<=sum l=B_T.
Equality uses only l0 or3. If B_T is not divisible by3, at least one
l1/2 gives one unit loss, so c_T<=B_T-1. Allowed high K3s are retained;
global defect triangle-freeness is not assumed at h1.

## Both one-outside cases fail before ordinary support is known

At h1 three high roots form the actual K3 at p. The fourth cannot
intersect two of them at S points without a loose triple; each permitted
single intersection is a P4 high-high defect edge. The complete high
graph is therefore K3+isolated or K3+pendant. Its independence number2
rules out all three-high low exceptions, so the low total is<=80,
independently of selected k0/1/2.

For the isolated case, the three K3 nodes have k_T2/internal edge1,
B16, hence c<=15; the isolate has B12. Total<=80+45+12=137<144.
For the pendant case the joined K3 node has k_T3/internal edge1,
B19, hence c<=18; the other K3 nodes are<=15 and the pendant B15.
Total<=80+18+15+15+15=143<144. These exclude h1 without assuming
all high points are already inside S. Now h0 is proved.

## h0 high topology: complete low-edge table

Every high point is now in S. Three concurrent highs would require at
least r1=2 there and P>=6+15=21, impossible. A high intersection triangle
with three different labels is also impossible. Thus the actual four-high
intersection graph is triangle-free. Its intersections have local P4,
so every high intersection is a defect edge; actual and F high graphs
are identical. Let t be the high-edge count.

High neighbor graphs are empty and total high contribution is<=48+6t.
If q_e lows have all three neighbors high, each uses three of the
24-2t high-low edges; thus q_e<=floor((24-2t)/3). Normal lows contribute
at most5 and exceptions at most6, yielding80+q_e. For a two-edge matching
there is no independent high triple, so q_e0. For a two-edge path plus
isolate there is one independent triple; its common low neighbors are
at most3 by a pair-codegree bound. The complete t<=2 table is

| high graph | low bound | high bound | full bound |
|---|---:|---:|---:|
| empty |88|48|136|
| one edge/two isolates |87|54|141|
| two-edge matching |80|60|140|
| two-edge path/isolate |83|60|143|

All fail144, hence t>=3. On four vertices a triangle-free three-edge
graph is a connected tree, star or path; a four-edge triangle-free graph
must be C4. No permutation or target automorphism is invoked.

## k1 complete norm obstruction, retaining arbitrary peak placement

The remaining preliminary k1/h0 case has S23, one weight2 peak f,
sumw24 and squared norm26. For Y=3Qw, every integer coordinate is2mod3,
sumY0 and ||Y||²=63q. The inequality y²-y-2>=0 for y2mod3 gives
||Y||²>=198. Since q=142-2E is positive even and E>=68, this residue
floor rejects q2 (whose norm126 is too small), leaving q4/6. Positivity
and evenness alone would not suffice. Write E=68+z with z0/1; exact
norm is378-126z.

If f belonged to a D2 root, its two incident D2 edge products would
add at least2 above the baseline12, forcing E>=70. One extra nonselected,
non-D2 peak edge likewise contributes weight2 and forces E>=70. Both
contradict E68/69, so f has no D2 or extra peak edge and degree_S(f)=8.
Every D2 endpoint is now nonpeak; no peak position was assumed earlier.

Selected Y baselines are2 at f/eight selected neighbors and5 at the
other fourteen S vertices: sum88, squared norm386. The t high intersections
have distinct actual point labels, because three highs cannot concur.
They give t shared points with four new D2 incident edges, and12-2t
private points with two new D2 edges. These edges are all nonpeak,
weight1 and distinct from selected edges. Y decreases by12 at a shared
point and6 at a private point. Private baseline5 changes its square by
-24, baseline2 by+12; shared baseline5 by+24, baseline2 by+96.
Consequently, before any extra edge,

    inside norm>=386-24(12-2t)+24t=98+72t,
    inside sum=88-3*24=16.

At z1 there is one additional nonpeak actual edge. Each endpoint's prior
Y is<=5, so reducing it by3 changes its square by9-6Y>=-21. Total norm
loss is at most42z, and sum falls6z. Thus inside norm>=98+72t-42z,
inside sum16-6z. All76 outside vertices have residue2mod3 and sum
-16+6z; individually y²>=y+2 gives outside norm>=136+6z. Therefore

    full norm>=234+72t-36z>=450-36z,
    actual norm=378-126z,
    lower minus actual>=72+90z>0.

Both z values fail. Combined with earlier h0/k0or1 coverage, this forces
k0: every selected incidence2, S24, all four highs wholly S, with exactly
the star/path/cycle necessary alternatives.

## Forty proof checks and ten hand challenges

The40 proof checks are: target count/triangle law; rook uniqueness/local
degree; D24/a16/P20; selected parity; selected fan; weighted parameters;
outside three/four; exact inherited four-common exclusion; h<=1;
selected weighted edges; H12/6; Q/q strictness; initial k coverage; F
degrees/36edges; S fan capacity; local S graph list; outside K3;
label collapse/faithfulness; square/rook inverse map2079;36cycles144;
K3,3 labels; codegrees/no-low triangles; low exceptions; high neighbor
internal graph; external B; nondivisibility loss; h1 topologies/no-low
exceptions; h1 bound137; h1 bound143; h0 high graph; summed48+6t;
exception stub/independent-triple bounds; four h0 table rows; t>=3 and
classification; k1 residue/E68/69; peak exclusions; baselines88/386;
shared/private changes; extra42 loss/76 outside bound; exact norm gap
and final ordinary-support scope.

Ten hand challenges:

1. r1=2/r2=3 demands21>20, and r1=4/r2=2 demands22>20. These exclude
   local graphs with extra highs before a square correspondence is used.
2. A four-high outside common point can carry a collapsed local C4.
   It is removed only by the exact inherited theorem, not by a generic
   claim that all defect cycles have distinct labels.
3. The(2,2,1,1) P4 consists of the high-high edge plus one distinct low
   attachment to each high. Replacing it by a four-cycle corrupts low
   local degrees and would invalidate both high intersection assertions.
4. Scalar l values five3 plus one1 give B16/c15; six3 plus one1 give
   B19/c18. Nondivisibility loss is sharp as a scalar check, not a claim
   these complete target neighborhoods exist.
5. The two-edge path/isolate has an allowed independent triple and up
   to three exceptional lows. Setting q_e0 would overstate its143 bound.
6. q2 is positive and even but gives126<198. The residue floor, not
   parity alone, is necessary to reduce E to68/69.
7. Moving a D2 point onto a selected peak neighbor uses baseline2;
   its norm changes+12/+96, strengthening the conservative -24/+24
   private/shared bounds. Such positions are not silently omitted.
8. At an extra nonpeak edge, Y5 loses21 at each endpoint, the worst
   case. Negative Y such as-7 instead gains51. Peak edges have already
   been forbidden by the actual weighted bound, not by default.
9. At z0 the full lower450 exceeds378 by72; at z1 lower414 exceeds
   actual252 by162. Counts23 inside/76 outside and factor63 are literal.
10. Abstract star, path and cycle all meet the surviving triangle-free
    topology conditions. No realizability or simultaneous profile is
    inferred; later branch exclusions require their own exact reviews.

This is50 written checks (40 proof,10 hand), with two h1 and four h0
table rows, four private/shared square-change cases and two norm endpoints.
Executed, formal, external, solver and scientific checks are all zero.

## Scope and provenance

The sole inherited common-point r1 has exact applicability. The earlier
lower4 paper is comparison only. Fan, Q, labeled-square and K3,3 mechanisms
are reconstructed, with disclosed archive overlap and Root/Structural
discovery sharing. No old program/matrix/driver gate, b5 descendant,
noD3 result, native refinement or broad coverage claim is used.

Selected small metadata reads/hashes and new written artifacts only.
No mathematical program/import/AST/syntax/backend/worker/census/solver,
ledger parse, Git/index/publication operation or protected edit occurred.
Historical bytes and closedWave46 cutoff449 remain unchanged. Start and
executor times are null; Root exact new acceptance is null at creation.
Only this necessary restriction is verified; target-resolution NONE and
overall scientific coverage UNKNOWN. Registration is separate.

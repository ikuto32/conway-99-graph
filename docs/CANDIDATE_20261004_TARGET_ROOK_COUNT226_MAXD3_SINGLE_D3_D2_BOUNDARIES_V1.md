# Candidate: one d3 root at R226 requires between three and eight d2 roots

Root supplied the low-population cycle and large-b selected-family
outlines. Structural independently challenged all high topologies,
covered actual intersections, internal root-neighbor edges, integer losses
and positive selected sizes below. This is a separate written CANDIDATE
requiring a different full review. No mathematical program, enumeration,
import, solver or worker ran, and earlier proof bytes remain unchanged.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle.
Suppose R=226, every d_T belongs to {0,1,2,3}, and exactly one actual
triangle has deficiency three. If b counts actual deficiency-two triangles,
then 3<=b<=8.

The maxd3/c1 hypotheses are literal. No pending R226 theorem is used as a
premise, and the logical dependency list is empty. This is a necessary
range, not exclusion of the one-d3 lane, R226 or the target, and does not
assert any listed population is realized.

Let T be the d3 root and a=27-2b the d1 population. Then P=28-b and
0<=b<=13. At a point the local defect degrees equal the root deficiencies;
r1+r3 is even, and the actual positive fan has3r1+5r2+7r3<=P. Its injection
counts the two external outer-partner sets of every focal root. Linearity
forbids one external positive triangle meeting two outer points of one
root; the target lambda1 forbids the distinct-intersection triple across
two buckets. Extra actual target edges remain allowed.

## Complete defect-cycle method for b0,1,2

F has all positive actual triangles as nodes and uncovered local rook
pairs as edges, labeled by their actual intersection points. Node degrees
are3d, and F has45 edges at D30. The target has45 uncovered squares.
Every distinct-label F4 gives its actual induced uncovered square and
conversely. A collapsed cycle needs four nodes of local deficiency at
least two, impossible with at most three high nodes here. Hence the full
cycle incidence is180.

F has no K3,3: a repeated grid label propagates all six roots to one
point with local degree at least three, impossible with only T of d3;
distinct labels give an induced actual rook incompatible with the
designated defects. Disjoint highs have at most three cross-matching
triangle completions, intersecting highs have at most their one third
high node, and any low has degree three. Thus all codegrees are at most
three. No F triangle contains a d1 root.

A low with a low neighbor lies in at most five four-cycles, since six
forces K3,3 through that degree-three neighbor. Only a low with three
independent high neighbors can be an exception, adding at most one.
With fewer than three highs none occurs; with three independent highs
there are at most three exceptions.

For a high Z and N=N_F(Z), the literal configurations here have at most
one internal neighbor edge. No internal opposite contributes a cycle.
External incidences B=sum_N deg-deg(Z)-2e(N) bound c_Z from above because
l<=3 gives binom(l,2)<=l. When B is not divisible by three the exact
integer loss gives c_Z<=B-1. The root's low-neighbor slots are filled;
same-bucket or cross-bucket additional F edges are excluded by those
slots or the actual distinct-intersection prohibition. Separate low-low
local matching components not belonging to N are retained.

## b0 and b1

At b0, T has nine independent low defect neighbors regardless of any
extra disjoint low-low component at a point. Its B18 and the twenty-seven
low bounds give27*5+18=153<180.

At b1 there are twenty-five lows, T of degree nine and X of degree six.
Let k0/1 indicate their F edge. T has9-k low neighbors and k high,
so B_T=18+3k. X similarly has B_X=12+6k. Neither has an internal
neighbor edge; there is no low exception with only two highs. The totals
are25*5+30=155 for k0 and25*5+39=164 for k1, both below180.

Actual T/X intersection need not be a defect: for example the allowed
local r1=5/r2=1 profile can have two separate high stars with k0, or
the k1 edge plus a separate low-low matching edge. The proof uses the
literal F edge k, not a false equation between actual intersection and
defect. All these extra low components are included in the twenty-five.

## b2, all three-high topologies

There are twenty-three lows and highs T,X,Y of degrees9,6,6. Let e32
count T-X/T-Y F edges, e22 indicate X-Y, and tau indicate a high triangle.
The generic neighbor-incidence sum is

    B_T+B_X+B_Y=42+9e32+6e22-6tau.            (1)

If the high graph is empty there are at most three low exceptions;
otherwise no independent high triple exists. The complete topology table
is therefore

| high F graph | e32 | e22 | tau | low bound | high bound | total |
|---|---:|---:|---:|---:|---:|---:|
|empty|0|0|0|118|42|160|
|one T-d2 edge|1|0|0|115|51|166|
|the d2-d2 edge|0|1|0|115|48|163|
|two T-d2 edges|2|0|0|115|60|175|
|T-d2-d2 path|1|1|0|115|57|172|
|high triangle|2|1|1|115|57 after integer losses|172|

For the last row, the actual high roots concur at one point by lambda1.
The valid minimal local sequence is(3,2,2,1), and a separate two-low
matching component is also possible at P26; neither is removed. T's
global neighbor set has seven lows and two degree-six highs, with one
internal high edge, giving B22 and c_T<=21. Each d2 has four lows plus
degree-nine/six highs and one internal high edge, giving B19 and c<=18.
Thus the high sum is57. Without the integer losses the loose sum60 would
still reject this particular row, but the literal21/18/18 bounds are
retained and independently checked.

Every row is strictly below180. The table is an exhaustive graph table
on the three actual high nodes, not a census of target constructions.
Covered actual intersections and arbitrary matching labels are not
silently assumed absent. Hence b0,1,2 are impossible.

## b9 through13: the even odd-deficiency family is impossible

If b>=9 then P<=19. At each point of T, r1 is odd. A value r1=1 needs
at least two d2 roots and fan20; a value r1>=5 needs fan22; a d2 with
r1=3 needs fan21. Thus each T point has precisely three d1 roots and
no d2: a pure three-leaf star.

Select O=D1 union {T}, of positive even size s=28-2b in {10,8,6,4,2}.
Point incidences in O are even by the local degree sum. Let w be half
that incidence on its support; put K=sum w(w-1), ell equal to the sum
of(w_u-1)(w_v-1) over selected triangle edges, and H the weighted sum
of every other actual internal edge. The exact expansion gives

    E_selected=3s+4K+ell,
    0<=w^T(3I-A+J/9)w=s(s-6)/4-5K-2ell-2H.   (2)

The three T points each have selected incidence four, hence w2, K>=6.
Their three actual selected edges give ell>=3. Since the maximum of
s(s-6)/4 on the displayed positive even sizes is10, (2) is at most
10-30-6=-26, impossible. Other selected incidences, weighted edges or
extra internal actual edges only strengthen the contradiction.

All b9..13 are covered; s0 or a negative low population is not silently
included. This yields b<=8 and completes the exact necessary range3..8.

## Boundaries and review requirement

The argument keeps parity on D1 union D3 rather than D1 alone. It allows
covered high pairs, actual local high triangles, and separate low-low
matching components at their point. Cycle faithfulness is used only when
the number of high nodes is at most three. The large-b proof is a direct
positive-semidefinite integer inequality and makes no collapsed-cycle
assumption or floating inference.

Earlier fan, root-incidence, weighted Gram and square methods overlap.
The new exact scope is the one-d3 necessary b3..8 range at R226/maxd3.
No novelty, whole-archive coverage, realization, whole one-d3/R226
exclusion or target resolution is claimed. A different full written
challenge must bind this proof before any VERIFIED/ledger use; the
publication cutoff and all historical proof bytes remain unchanged.

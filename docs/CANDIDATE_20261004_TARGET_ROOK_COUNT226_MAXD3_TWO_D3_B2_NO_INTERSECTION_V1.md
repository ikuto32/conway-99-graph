# Candidate: two d3 roots cannot intersect in the R226/maxd3/b2 lane

Structural derived this branch from the retained valid common-point graph,
then notified Root for a separate challenge. The proof deliberately counts
its collapsed local four-cycle instead of assuming a faithful square/F4
map. This is a new written CANDIDATE, with no mathematical program,
enumeration, import, solver or worker run. Earlier boundary bytes remain
unchanged, including their honestly unexcluded preparation state.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle.
Suppose R=226, every d_T belongs to {0,1,2,3}, exactly two actual triangles
have deficiency three, and exactly two have deficiency two. Then the two
deficiency-three triangles are disjoint.

All hypotheses are literal. No pending R226 upper3, population, or two-d3
boundary gate is used. The proof derives the necessary local graph and
cycle inequalities directly; its logical dependency list is empty. It
does not exclude the disjoint b2 case, the two-d3 lane, R226 or the target.

There are twenty d1 roots and four high roots. Write A,B for the d3 roots
and C,D for the d2 roots. The positive population is24 and D30.

## The valid common-point graph and low-neighbor restriction

Assume A,B meet at p. At a point the positive local defect degrees equal
the root deficiencies, r1+r3 is even, and the actual fan bound is
3r1+5r2+7r3<=24. Two degree-three roots need at least four local nodes.
The alternatives r1=2,r2=0 give nongraphical(3,3,1,1); r1=2,r2>=1
need25; r1>=4 need26. Hence r1=0,r2=2: both C,D also contain p, and the
local graph is K4 minus CD, with A,B universal. It is a valid graph. All
four high actual triangles intersect only at p.

No d1 root can be a defect neighbor of two highs. Three actual triangles
meeting pairwise at distinct points would give their intersection edge a
second triangle partner, contrary to lambda1. Thus a triangle meeting two
highs must contain p. A common defect neighbor there would have local
degree at least two; a d1 has degree one, and in this local graph no d1
root occurs at all. Every low therefore has at most one high neighbor in
the global defect graph F. Its other neighbors are low.

Each low defect neighbor of a high has its unique local slot filled by
that high. Two such lows in the same root bucket cannot be F adjacent
there; two in different buckets cannot intersect without the forbidden
distinct-intersection triple. Thus the low neighbor set of each high is
independent, with each member having exactly two low neighbors globally.
This counts actual points and actual triangles; no uniform profile or
automorphism is assumed.

## Required cycle incidence without a faithfulness assumption

F joins positive actual triangles by uncovered local rook pairs and labels
each edge with its actual intersection point. Its high degrees are9,9,6,6,
its twenty low degrees are three, and it has45 edges. The target has45
actual uncovered squares at R226. The four edge triangles of each such
square form an F four-cycle with four distinct corner labels; the corner
intersections recover the square, so this map is injective. Consequently

    C4(F)>=45, sum_Z c_Z>=180.                 (1)

No converse faithful-map premise is needed. Indeed K4 minus CD at p
contains the collapsed four-cycle A-C-B-D-A, which is explicitly retained.
All other points have at most one high root, so this is the only collapsed
F4; the ordinary converse would give46 cycles and184 incidences. The
weaker lower bound (1) alone suffices below.

All pair codegrees in F are at most three. High pairs intersect at p;
their common F neighbors are the one or two other local highs. Low degree
three gives the cap whenever a pair includes a low. F has no K3,3:
repeated grid labels propagate to six roots at one actual point, each of
local degree at least three, but only A,B have that deficiency. A grid
with all nine labels distinct would be an actual induced rook, with extra
grid nonneighbor edges forbidden by lambda1, contradicting its designated
defect edges.

No F triangle contains a low. Each low has a low neighbor, and therefore
c_low<=5: attaining six would force its degree-three low neighbor's entire
neighbor set to be common with the other two root neighbors, giving K3,3.
Thus all twenty lows contribute at most100 incidences.

## Exact high-root decomposition including the internal opposite

For A its neighbors are B,C,D and six lows L_A. The only internal neighbor
edges are BC and BD, retained from the local graph. Hence B is one
internal opposite with its two edges to C,D and contributes exactly one
four-cycle; every other neighbor contributes zero as an internal opposite.

Every external opposite is low, since all other highs are already in the
neighbor set. For a low opposite Z put I=|N_F(Z) intersect {B,C,D}| and
x=|N_F(Z) intersect L_A|. The at-most-one-high restriction gives I0/1.
If I0 then x<=3 and binom(x,2)<=3x/2; if I1 then x<=2 and
binom(1+x,2)<=3x/2. Thus its external cycle contribution is at most3x/2.
Each of the six independent L_A nodes has two low edges, all reaching
external low opposites, so sum x=12. Therefore

    c_A<=1+(3/2)*12=19.

The same actual argument gives c_B<=19. The leading one counts precisely
the collapsed local cycle, not an actual square.

For C its neighbors are A,B and four lows L_C. Its one internal neighbor
edge AB gives no internal opposite with two edges, so contributes zero
cycles through C. Each L_C node has two low edges and their set is
independent. An external low opposite again has at most one high neighbor,
so the same I0/1 inequality applies. Now sum x=8 and

    c_C<=(3/2)*8=12.

Symmetrically c_D<=12. There is no omitted high opposite in either
decomposition, and the low stubs include every edge to its external pool.

The complete incidence upper bound is therefore

    20*5+2*19+2*12=162<180,

contradicting (1). This proves the exact disjointness statement.

## Boundaries and pending status

The local(3,3,2,2) graph remains a valid abstract positive control. The
contradiction is global and retains its internal opposite contribution one.
It does not apply a triangle-free formula to the actual high triangles,
delete the collapsed cycle, or identify it with a target square. The
inequalities for I1 use x<=2 from a low's literal remaining degree;
I0 allows x3. Other actual target edges are not removed to construct a
selected induced graph.

Fan, actual square injection, repeated-label K3,3 and low-cycle mechanisms
overlap prior work. The new literal branch is the retained R226/maxd3/c2/b2
intersection. No whole-archive or novelty assertion, no survivor
classification and no target resolution is claimed. The current
publication cutoff is unchanged, and a distinct exact written review
must bind this paper before any VERIFIED or ledger use.

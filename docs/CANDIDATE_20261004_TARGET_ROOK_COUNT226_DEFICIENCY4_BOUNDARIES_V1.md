# Candidate: the deficiency-four lane at R226 has one isolated high root

Root supplied the degree-four local-profile and pair-moment outlines.
Structural independently reconstructed them and derived the finite cycle
contradictions below. This remains CANDIDATE pending a different written
challenge. No mathematical program, enumeration, solver, import or worker
ran. Existing R227 and earlier proof bytes remain unchanged.

## Exact statement and one inherited premise

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and d_T=6-r_T for each actual triangle. Suppose
R=226 and some actual triangle has deficiency four. Then exactly one triangle
has deficiency four. If a,b,c count the deficiency-one, two and three triangles,
then a=26-2b-3c and 3<=b+2c<=6. At each of the unique d4 triangle's three
points the positive local defect graph is K1,4: that d4 root and precisely
four d1 roots, with no d2, d3 or other d4 root. In particular that d4 triangle
is disjoint from every other positive triangle of deficiency at least two.

Use C-UNRESTRICTED-TARGET-ROOK-DEFICIENCY-STRICT-SECOND-NEIGHBOR-BOUND r1:
D>=6m+6 for R<231 and nonzero maximum deficiency m. Here D=6(231-226)=30,
so m<=4. No other inherited theorem, no pending R227 exclusion, equitability,
automorphism or induced selected-support assumption is used. This does not
exclude all d4 triangles, R226 or the target, or construct any surviving case.

## Exact local degree-four possibilities

Write d for the d4 population. Then

    a+2b+3c+4d=30, P=a+b+c+d=30-b-2c-3d.

At a point with r_i roots of deficiency i, local graph degrees are i,
parity requires r_1+r_3 even, and the actual positive fan requires

    3r_1+5r_2+7r_3+9r_4<=P.                  (1)

Each external positive triangle can meet only one outer point of the entire
fan: otherwise linearity or three pairwise distinct intersections give an
edge two actual triangle partners. A degree-four node needs at least five
local positive nodes.

When d>=1, P<=27. No point contains two d4 roots: then d>=2 and P<=24,
but r_4=2 leaves weight at most6 in (1), allowing fewer than the three
additional nodes needed by degree four. Three d4 roots already need fan27
where global d>=3 gives P<=21. Higher r_4 is worse.

A point with its one d4 root cannot have a d3 root. For r_3=1, r_1 is odd:
r_1=1 needs r_2>=2 to reach five nodes and has fan29; r_1=3,r_2=0 has
degree sequence(4,3,1,1,1), which is nongraphical. Its universal degree-four
node leaves the degree-three node needing two edges to residual-zero leaves.
Larger r_1 or any additional r_2 exceeds27. For r_3=2, r_1 even: r_1=0
needs r_2>=2 and fan33, while r_1=2 already has fan29. Three d3 roots have
fan30 before any other node. All are impossible.

With r_4=1,r_3=0, parity makes r_1 even and node count needs r_1+r_2>=4.
Checking (1) under P<=27 gives exactly the following finite possibilities:

| r_1 | r_2 | fan weight | unique local graph up to labels |
|---:|---:|---:|---|
|4|0|21|K1,4 |
|2|2|25|d4 universal to two d2 and two d1, plus the d2-d2 edge |
|4|1|26|d4-d2 edge, three d1 leaves at d4 and one at d2 |
|6|0|27|K1,4 plus one disjoint d1-d1 edge |

This is a small hand degree-sequence classification, not a target
automorphism premise. The d4-d2 edge in the third row follows from
high-degree and low-degree sums: with its high-high edge indicator x and
low-low edge count y, x-y=1, so x1/y0. No unlisted degree-four profile
satisfies both the node count, parity and fan bound.

## At most two d4 roots, and the two-root population is fixed

If d>=2, P<=24, so every d4 point has only the first profile. The d4 roots
are pairwise disjoint and each has twelve distinct d1 partners across its
three points. A d1 triangle meets at most three d4 roots (it has three points),
and at most one point of each. Therefore 12d<=3a, giving a>=4d and d<=3
from a<=30-4d.

For each d1 triangle let t count the d4 roots it meets. Then sum t=12d.
Any pair of disjoint d4 triangles has at most three common d1 triangles:
their cross edges form a matching of at most3, each with unique completion.
Thus

    sum binom(t,2)<=3binom(d,2),
    sum binom(t,2)>=sum(t-1)=12d-a.            (2)

The second inequality also holds at t0. If d3, a=18-2b-3c, giving lower
18+2b+3c against upper9, impossible. If d2, a=22-2b-3c, so lower2+2b+3c
must be at most3. Hence b=c0 and a22. The number of d1 triangles meeting
both roots is2 or3, with no uniform-profile assumption.

## Exact cycle method in the small remaining populations

Let F have all positive actual triangles as nodes and local uncovered rook
pairs as edges, labeled by their intersection points. A node of deficiency i
has global degree3i. D30 gives45 defect edges and the target has
2079-9*226=45 uncovered squares. Each distinct-label F4 corresponds
bijectively to an actual uncovered square. In every small case below there
are at most three high nodes; a collapsed F4 would require four nodes with
local degree at least2. Thus C4(F)=45 and required incidence is180.

F has no K3,3 in these cases. Repeated grid labels require six local
degree-at-least-three roots, not available here; distinct labels instead
give an actual induced rook, contradicting its defects. Every codegree is
at most3: disjoint high cross edges form a matching of at most3 with unique
completions; intersecting highs can have common F neighbors only at their
point, with at most one further high; a low node has degree3.

No F triangle contains a low node. Every low with a low neighbor has at most5
cycles, since attaining6 would produce K3,3. An all-high low may contribute6,
but its three highs must be independent; such exceptions number at most3
when there are exactly three highs. At a high root, lows in its neighbor set
have their local slots filled by that root and cannot intersect across root
buckets. The only internal neighbor edges in the cases below are the
explicit high-high matching edge. With l<=3 over external opposite nodes,
c_root<=B=sum_N degree-degree_root-2e(N). If B is not divisible by3 then
c_root<=B-1. No global triangle-free assumption deletes the valid local
high triangle in the tight row.

For d2,b=c0 all roots have the K1,4 point profile. Each d4 root has twelve
low neighbors, independent, so B=12*3-12=24. Every one of the22 lows has
a low neighbor since only two highs exist. Hence the whole incidence is
at most22*5+2*24=158<180. Therefore d2 is impossible: any d4 population
is exactly one.

## Exclude b+2c<=2 for the single d4 population

Now d1, a=26-2b-3c, P=27-b-2c. Four hand cases exhaust b+2c<=2.

* b0/c0: the unique high has12 independent actual defect-neighbor lows,
  even if the extra disjoint low-low pair profile occurs at a point. Its B24
  and low26*5 give154<180.
* b1/c0: a24. If the d2 is disjoint from d4, their high bounds24/12 give156.
  If they meet, the r_1=4/r_2=1 profile forces their high edge and no internal
  neighbor edge. D4 has11 lows and one degree6 high, B27. D2 has5 lows and
  one degree12 high, B21. Together with120 low incidence this gives168<180.
* b2/c0: a22/P25. A d2 meeting d4 must bring both d2 roots to the same point,
  since the one-d2 profile needs26. The valid local degree sequence is
  (4,2,2,1,1): its three highs form a triangle, retained here. D4 has10 lows
  and two degree6 highs, with their one internal edge, so B28 and c<=27.
  Each d2 has4 lows and degree12/6 high neighbors, with their internal edge,
  so B22 and c<=21. No low exception is possible with this high triangle.
  Total110+27+21+21=179<180. If d4 is disjoint from both, an isolated or
  adjacent d2 pair gives complete bounds161 or164 respectively, with all
  possible three-high low exceptions included in the isolated case.
* b0/c1: a23/P25. The d4 and d3 are disjoint by the point classification.
  Their independent low neighbor sets give B24 and B18. There are only two
  highs, so lows115 and total157<180.

No pending theorem from R227 is used. These are complete actual defect
graph bounds for each listed population, not numerical infeasibility.

## Final necessary lane and boundaries

Thus d1 and b+2c>=3. Then P<=24, forcing all three d4 points to be pure
K1,4 and excluding every d2/d3 intersection with that root. Their fan21
also requires P>=21, so b+2c<=6. This proves the exact statement.

The twelve possible (b,c) pairs are c0/b3..6, c1/b1..4, c2/b0..2,
and c3/b0. They are a hand-listed necessary scalar set, not asserted
realizations. A=26-2b-3c is nonnegative for each, but that alone is no graph.

The five-node degree sequence(4,3,1,1,1) is retained as an explicit failed
local construction, while(4,2,2,1,1) is valid and only fails its complete
cycle incidence179. The multiple-root pair bound uses actual disjoint
triangles and all d1 roots including t0. Extra edges and arbitrary matching
labels are not discarded.

A bounded current filename check found no prior R226/deficiency4 paper;
an initial broad numeric226 glob mostly matched unrelated numerical record
indices and was not a literature or archive absence check. No novelty or
whole-archive coverage is claimed. Fan, cycle and codegree components overlap
earlier R227 work, with new d4 degree profiles and target D30/incidence180.
This CANDIDATE awaits distinct written verification; target/coverage stay
UNKNOWN, and no ledger, Git or publication mutation occurs.

# Independent written review: the single-D3 necessary b3..8 range

Completed written verification: 2026-10-04T22:10:35.7016506+00:00.
Producer /root/structural; different author verifier /root/native_driver.
Method independent_derivation; computational executor null. Outcome PASS.
Exact claim C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-SINGLE-D3-D2-BOUNDARIES r1.
Paper docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD3_SINGLE_D3_D2_BOUNDARIES_V1.md
SHA256 f8660ce2fd5ed79f198fba746238df44ab353a104d1e6f0b713f62d462a69c02.
Raw acceleration/results/20261004_target_rook_count226_maxd3_single_d3_d2_boundaries_candidate01.json
SHA256 96fc5f4bdbba530ad2d8be8496e0b53b84e3e83c298801eccd4af9ccabf44603.
All exact statement/assumption fields, empty dependencies and preparation-time
pending nulls are retained. This is necessary range only, not a single-D3 or
R226 exclusion and not realization of any remaining value.

## Whole actual geometry and cycle foundations

Each edge of a complete SRG(99,14,1,2) has one actual triangle partner, giving
231 actual triangles. Distinct ones meet at most once; three pairwise distinct
intersection labels give a second triangle partner on an edge and are impossible.
A point has seven incident actual triangles. The local rook partner bijection
gives local defect degree d_T and global degree3d_T. Deficiency mass is
6(231-R)=30 at R226. With one D3 root T and b D2 roots, a=27-2b and P=28-b,
so the entire nonnegative integer domain is b0..13.

The local simple graph gives r1+r3 even; injection of each local root's two
outer partner sets gives3r1+5r2+7r3<=P. No repeated external triangle can
meet two outer fan points, by linearity or the loose-triple prohibition. This
counts actual triangles and retains extra unrelated local matching components.

Every nonadjacent target pair defines its unique induced square through its
two nonadjacent common neighbors, giving2079 squares. A rook has nine; an
actual square has at most one containing rook because its edge triangles are
unique. Hence R226 leaves45 uncovered squares. Their edge triangles inject
into F4s in the positive defect graph F, which has45 edges. A repeated label
in an F4 forces all four roots concurrent by linearity/loose-triple arguments.
A local cycle needs four high roots; for b0..2 there are at most three. Thus
no collapsed cycle occurs; distinct-label cycles are actual uncovered squares.
Their full cycle-incidence count is180, though injection lower180 suffices.

No K3,3 occurs in F. Repeated grid labels force six concurrent actual roots of
local degree at least3; only T is D3. Distinct labels give an induced actual
rook: any additional diagonal edge would have two grid common neighbors,
contrary to lambda1. Its defect edges contradict that rook. All pair codegrees
are at most3: a low has degree3; disjoint high triangles have an actual
cross-edge matching with at most three transversal triangle completions;
intersecting highs' common roots are concurrent and there is at most one third
high in these small populations. A low cannot be in an F triangle because
it has local degree1 and a nonconcurrent triangle would be an actual loose triple.

A low with a low neighbor has cycle count<=5; reaching6 forces K3,3 through
that degree-three neighbor. Only three independent high neighbors can create
an exception, adding at most1; each high triple admits at most3 common lows.
With fewer than three highs there are none. With exactly three independent
highs there are at most3 exceptions, so the safe bound is a*5+3.

## Complete low-b cycle table with all high opposites retained

For each high Z let N=N_F(Z). In these configurations N has at most one
internal edge, so no internal opposite cycle. Filled local low slots and the
actual loose-triple prohibition exclude additional edges between its neighbors.
The exact external stub sum is B_Z=sum_(N)deg-deg(Z)-2e(N). Pair codegree
l<=3 gives choose(l,2)<=l, hence c_Z<=B_Z, counting external high and low
opposites. If B_Z is not divisible by3, equality would need all nonzero l=3,
so the integer correction gives c_Z<=B_Z-1. No high pool is omitted.

At b0, T has nine independent low neighbors, B_T=18. All27 lows have LL
neighbors and contribute<=135. Total153<180. Other low-low components at
T's points are not in N(T), remain counted in the global low population and
do not invalidate this neighbor calculation.

At b1 there are25 lows and one high X of degree6. Let k0/1 be the TX defect
edge. Then B_T=18+3k and B_X=12+6k; no neighbor graph internal edge appears.
Low exceptions are impossible. Total125+30=155 for k0 and125+39=164 for k1.
An actual TX intersection can be covered and have k0. The permitted profile
r1=5/r2=1 can contain two separated high stars at k0 or the high edge plus
a separate low-low matching edge at k1. Neither actual possibility is deleted.

At b2 there are23 lows and actual highs T9,X6,Y6. Write e32 for the two
possible T-D2 defect edges, e22 for the possible XY edge, tau for the high
triangle indicator. Each T-D2 edge adds(6-3)+(9-3)=9 to the sum of external
stub baselines; the D2-D2 edge adds6; a high triangle subtracts2 at each root.
Thus B_T+B_X+B_Y=42+9e32+6e22-6tau. The full graph table on three highs is:

| high F graph | e32 | e22 | tau | low upper | high upper | full upper |
|---|---:|---:|---:|---:|---:|---:|
|empty|0|0|0|118|42|160|
|one T-D2 edge|1|0|0|115|51|166|
|D2-D2 edge only|0|1|0|115|48|163|
|two T-D2 edges|2|0|0|115|60|175|
|T-D2-D2 path|1|1|0|115|57|172|
|high triangle|2|1|1|115|57|172|

These six rows cover all labeled graphs up to exchanging X,Y, not target
constructions. Only the empty high graph has an independent triple and the
three allowed low exceptions; all others have low upper115.

For the high triangle the three actual roots concur. Its minimal local profile
is(3,2,2,1), and an additional separate low-low matching pair can occur within
P26. T's N has seven lows, X,Y and internal XY edge, so B_T=22 and c_T<=21.
Each D2 has four lows, high degrees9/6 and one internal edge, giving B=19
and c<=18. The exact sum57 is21+18+18, with any separate local pair outside
these N pools still present in the low count. Generic high60 would also reject
this row, but the literal corrected integer losses are checked and retained.

All nine small-b branches (one b0, two b1, six b2) are strictly below180.
They do not equate covered actual intersections with defects or erase matching
components, and all applicable external high opposites are inside the stub sum.

## Large b: exact weighted PSD contradiction on a positive family

For b9..13, P<=19. At each point of T, r1 is odd. r1=1 needs at least two
D2 nodes to support local degree3, giving fan20>P. r1>=5 gives fan>=22>P.
At r1=3, one D2 gives fan21>P. Thus r1=3/r2=0 at all three T points,
the pure degree-three star. This restriction uses fan/parity and an actual
simple local graph, not assumed equitability.

Select O=D1 union {T}, size s=28-2b in10,8,6,4,2. These sizes are positive
even integers throughout the original b domain. O incidence is even by the
local degree sum. Let w be half it on its support, arbitrary larger integer
weights retained. Define K=sum w(w-1), ell=sum over selected triangle edges
of(w_u-1)(w_v-1), and H the weighted sum of every other support edge.
Unique actual triangle edges give E_selected=3s+4K+ell,
sumw=3s/2 and ||w||^2=3s/2+K. The full adjacency identity
A^2=12I-A+2J yields Q=3I-A+J/9 with Q^2=7Q and PSD, so
q=w^TQw=s(s-6)/4-5K-2ell-2H>=0.

Each of the three T points has w2, hence K>=6. Its three selected edges give
ell>=3. The constants for s10/8/6/4/2 are10/4/0/-2/-2. Thus the five q
upper bounds are -26/-32/-36/-38/-38, all strictly negative. Larger selected
incidences or further actual edges only reduce q. s0 and negative a are never
invoked. This excludes b9..13 and completes the exact necessary range3..8.

## Independent checks and failure boundaries

Thirty-four proof checks on paper:
1. Whole paper/raw statement; 2.231 actual triangles; 3. linearity;
4. loose-triple label veto; 5. local/global defects; 6. D30;
7. a27-2b/P28-b; 8. complete integer b0..13;
9. parity/fan injection; 10.2079 squares; 11. rook-square uniqueness;
12.45 uncovered; 13. at most three high roots in small-b scope;
14. no collapsed cycle there; 15. required180;
16. both K3,3 label cases; 17. actual codegree3;
18. low triangle prohibition; 19. low5 and permitted exceptions;
20. exact external B formula; 21. internal neighbor edges retained;
22. integer divisibility loss; 23. b0 total153;
24. b1 both155/164; 25. covered actual intersections retained;
26. generic b2 edge contribution formula; 27. all six topologies;
28. actual high triangle and separate low matching pair;
29. exact21/18/18; 30. all small-b strict totals;
31. large-b pure-star derivation; 32. positive sizes10/8/6/4/2;
33. full weighted identity and K6/ell3; 34. all five negative q bounds.

Twelve failure/boundary challenges on paper:
1. Actual TX intersection at b1 need not be its defect edge.
2. The r1five covered profile retains separate high stars.
3. A separate D1-D1 local matching pair can coexist with a high edge/triangle.
4. Exception lows cannot be suppressed in the empty b2 high graph.
5. The F high triangle is valid locally, not rejected as triangle-free.
6. Internal neighbor-edge subtraction and all external highs are retained.
7. Distinct-label faithfulness is invoked only with at most three highs.
8. The large-b proof makes no faithfulness claim for its larger D2 population.
9. Parity belongs to D1 union D3, not D1 alone.
10. Larger selected incidence and extra target edges remain in K/ell/H.
11. s0/negative a is outside the full b0..13 count domain.
12. Remaining b3..8 values are neither classified nor shown realizable/excluded.

Total46 written checks; nine small-b and five large-b rows, executed/formal/
external/solver checks zero. These are hand cases, not program enumeration.

## Scope and provenance

Root supplied outlines; Structural produced the complete literal candidate.
Native independently derived every case, including all high opposite pools,
covered-intersection boundaries and the five PSD bounds. No novelty or shared
agreement gate is asserted. Logical dependencies empty; literal maxd3/c1 is
not supplied by any pending R226 theorem. Original pending nulls, exact candidate
bytes and verification history remain unchanged. Global scientific coverage
UNKNOWN and target resolution NONE. No mathematical program/import/AST/backend/
worker/census, ledger parse, Git/index/publication/protected mutation. Root-
reported457 is context only; new Root acceptance and registration are separate.

# Independent derivation of maximum rook deficiency two at R227

Verification timestamp: 2026-10-04T19:17:50.1127510Z.
Mathematical producer /root/structural; independent verifier /root/native_driver.
Root shared the follow-up strategy and challenged the tight residue case.
That shared origin and Structural's previous cycle arguments are disclosed;
agreement does not supply verification of this new statement.

Exact claim C-UNRESTRICTED-TARGET-ROOK-COUNT227-DEFICIENCY-UPPER2 r1.
The whole frozen paper f966c0a6af78762d64ab47a8db9b9686a27b6790879bf02ac4e3138f68032f76
and raw 42bd5ab2c027c3f5f5f0c7beadde984f2a25908caa13750218729a25061a85a8
were read. The argument below is a separate hand reconstruction. No
mathematical source import, AST, syntax check, enumeration, backend, solver,
computational worker, ledger parse or Git/publication mutation was used.

## Exact inherited scope

Take a complete finite simple SRG(99,14,1,2). Count actual induced nine-vertex
rook subsets once by their vertex sets, with R227. For an actual triangle T
put d_T=6-r_T. The exact strict-mass r1 gives d<=3 from D=sum d=24.
The separately written and Root-accepted sixteen-row population r1 leaves
c=2,b0/1 or c=1,b0..5 whenever c>0. The exact single-D3 r1 reduces the latter
to b0/1/2. Those three named revisions are explicitly inherited premises,
not a reapproval of their old proofs. Their bindings, literal statements,
timestamps and distinct Root acceptance receipts were read.

Write a,b,c for d1,d2,d3 counts. Thus a+2b+3c=24 and P=a+b+c. The five
possible positive-c rows are (a,b,c)=(18,0,2),(16,1,2),(21,0,1),(19,1,1),
(17,2,1). Each has at most three high nodes, where high means d2 or d3.
The new c0,b8 boundary result is not a logical premise. Neither any surviving
population's realizability nor actual registration of the inherited records
is assumed. This is next-wave47 evidence outside the closed Wave46 cutoff.

At each actual point the seven incident triangles form a simple defect graph:
two are joined precisely when they do not belong together to an induced
rook. Each node T has degree d_T. A rook containing T supplies exactly one
other incident triangle at each of its three points; a containing rook is
unique for such a pair by the four opposite second-common-neighbor points.
Thus the local degree is exact and d0 nodes cannot be defect partners.

Triangles have unique edge partners and meet at most once. Three actual
triangles cannot intersect pairwise at three distinct points: those points
would make an original triangle edge have two triangle partners. At a point
with r1,r2,r3 positive incident triangles, local handshake gives r1+r3 even.
Their 2(r1+r2+r3) outer points are distinct. Each outer point of a dm triangle
needs m other positive triangle incidences. An external triangle meets at
most one of the entire fan's outer points, by linearity or the forbidden
distinct-intersection triple. Therefore

    P >= 3r1+5r2+7r3.                                    (A)

This is an actual point/triangle injection, not a presumed cycle catalog.

## Faithful ordinary four-cycles with at most three high nodes

Form F on the positive actual triangles, using all local defect pairs. Label
each edge by the unique actual intersection point. F is simple, and T has
3d_T distinct global neighbors; a partner cannot recur at another point.
Its total degree is3D=72, so F has36 edges.

Any triangle of F has all three labels equal, since three different actual
intersections are forbidden. It is a local triangle and its three nodes
each have local defect degree at least two. Thus no F triangle contains a
d1 node. A triangle of three high nodes is allowed, and will be retained.

For an ordinary four-cycle T1,T2,T3,T4 of F, suppose successive labels12
and23 are equal to v. Then T1,T2,T3 contain v. If T4 did not contain v,
its intersections with T1,T3 would be distinct from v and each other,
giving the forbidden three-triangle geometry. Thus T4 also contains v,
and all four edge labels equal v by linearity. Opposite label coincidence
also puts all four triangles through that same point. Such a collapsed
cycle requires four distinct high nodes, since every cycle node has two
local defect partners there. That is impossible in these five cases.

All four labels are consequently distinct. They form an actual square,
whose consecutive edges belong to the four actual triangles. A diagonal
edge would have the other two corners as common neighbors, contrary to
lambda1. The square is induced. If a rook contained one of its corner
triangle pairs, its grid cross-pair second-common-neighbor reconstruction
would contain the whole square. Since each corner is a defect pair, the
square is uncovered.

Conversely an uncovered induced square has four distinct actual edge
triangles. A triangle repeated at consecutive edges would be its forbidden
diagonal; repeated opposite edges cannot fit a three-point triangle. Any
rook containing a corner pair would cover the square, so its four corner
pairs are defect edges. It yields the inverse ordinary F four-cycle.
Unique edge partners and point labels make both maps inverse, rather than
merely giving an injection into a selected set of squares.

There are99*84/2=4158 nonadjacent vertex pairs. Each has exactly two common
neighbors, which cannot be adjacent because then that edge would have two
common neighbors. The induced square is counted at its two opposite pairs,
so there are2079 actual squares. Every rook has9; any containing square
fixes its rook through a corner-pair grid reconstruction, so these covered
square sets are disjoint. At R227,

    U=2079-9*227=36, C4(F)=36, sum_Z c_Z=144.              (B)

Here c_Z counts all ordinary F four-cycles through Z. No claim extends this
faithful correspondence to four or more high nodes in the remaining c0
branches, and no positive actual support is assumed induced.

## K3,3 and common-neighbor restrictions without global triangle-freeness

Suppose six distinct actual triangles give a K3,3 of defect edges. If one
row meets two columns at v, each other row must also contain v: otherwise
that row and those two columns have forbidden distinct pairwise intersections.
The third column then contains v by the same argument using two rows.
All six nodes would have three local partners there, requiring six d3
triangles. This contradicts c<=2. If two opposite grid labels repeat,
their four endpoints already share v and a cross grid edge supplies an
adjacent repeat. Therefore all nine grid labels are distinct.

Those nine actual points form three triangle rows and three triangle columns.
An extra edge between grid nonneighbors would have two known grid common
neighbors, contradicting lambda1 for that edge. It is an induced rook;
its row/column pairs cannot be defects. Thus F contains no K3,3. Label
coincidences are handled before the rook conclusion, and local high triangles
have not been forbidden by an incorrect global triangle-free assumption.

For any two disjoint high actual triangles, every common F neighbor supplies
an actual cross edge between them, and its unique triangle completion.
The actual cross edges form a matching of at most three: an external vertex
cannot meet two points of an actual triangle under lambda1. Hence their
F codegree is at most three. If the two high triangles intersect, every
common actual triangle is concurrent at that point; a common defect partner
has local degree at least two and is high. There are at most three high
nodes total, allowing at most one other there. If either member is d1,
its global degree three gives the same codegree bound. Thus every pair of
distinct F nodes has at most three common neighbors in these cases.

A d1 node Z has three neighbors and no F triangle. For each neighbor pair,
exclude Z from their at-most-three common neighbors. The three pairs give
c_Z<=6. If a neighbor W is d1 and equality6 holds, each neighbor pair has
codegree3. Write A,B for the other two neighbors. N(W) has size3 and is
contained in both N(A) and N(B), producing K3,3 with rows W,A,B and columns
N(W). These six nodes are distinct: no triangle contains a d1 node, so A,B
are not neighbors of W and no self-loop is possible. Hence c_Z<=5 when
Z has any d1 neighbor.

Only all-high neighbor sets can be exceptions. They require three high
nodes, and all such d1 Z belong to the common-neighbor set of any chosen
high pair. Thus q<=3 and total d1 contribution <=5a+q. With only two high
nodes q=0. If the three high triangles intersect at one point, a d1 node
cannot be a common defect partner of even two of them: concurrency would
give it local degree two. Then q=0 also, without suppressing the permitted
local high triangle itself.

## Root-neighbor internal edges and the exact integer loss

For a high root Z set C=N(Z), t=deg(Z), e_C=|E(F[C])|. A d1 member of C
cannot have an internal edge in its same point bucket, because its only
local defect slot is already used by Z. Members in different point buckets
cannot intersect, by the forbidden distinct-intersection triple with Z.
Therefore internal C edges can only join high neighbors at the same point.
At most two other high nodes exist, so F[C] is empty or one edge. In
particular its internal maximum degree is at most one.

An opposite node of a four-cycle through Z therefore cannot be in C: it
would need two C neighbors. For O outside C and Z put l_O=|N(O) intersect C|.
This is the codegree of O,Z, hence l_O<=3. Double counting C incidences gives

    B=sum_O l_O=sum_(Y in C) deg(Y)-t-2e_C,
    c_Z=sum_O choose(l_O,2).                               (C)

For l=0,1,2,3, l-choose(l,2) equals0,1,1,0. Thus c_Z<=B. If B is not
divisible by3, the l values cannot all be0/3, so at least one unit is lost
and c_Z<=B-1. No real relaxation or time-budget calculation is involved.
Internal edges are subtracted twice, not once, and their opposite-node
contribution is separately shown zero before using (C).

## All five population cases and seven exact hand rows

For c2,b0/1, P=20/19. Two d3 at one point would leave (r1,r2)=(0,0),
(0,1), or(2,0) by parity and (A). The first two give fewer than four
positive nodes for degree3; (3,3,1,1) is nongraphical since the two degree3
nodes consume both degree1 nodes twice. Thus the two d3 actual triangles
are disjoint. At a point of either d3 there cannot be a d2: with r2=1,
odd r1=1 leaves degree3 insufficient, whereas r1>=3 gives fan21>P.
With r2=0, odd r1 must be3, since r1=1 is insufficient and5 needs22>P.
These are exactly three-leaf stars, so each d3 root has9 low neighbors,
e_C=0, B=27-9=18. At b1 the d2 is disjoint from both d3, and has6 low
neighbors, e_C=0, B=18-6=12. For b0 q0; for b1 q<=3. The totals are
18*5+36=126 and16*5+3+36+12=131.

For c1,b0, a21,P22, the d3 root has9 low defect neighbors. At a root point
r1 may be5: the additional two low nodes form a separate matching and
are retained, not counted as root neighbors. The nine true root neighbors
still have no internal edge and B18. Since there is only one high node,
q0. The total is21*5+18=123.

For c1,b1, a19,P21, let k=0/1 be the high defect-edge indicator. This does
not presume disjointness when k1. The d3 root has9-k low plus k d2 neighbors;
the d2 has6-k low plus k d3 neighbors. With only one other high neighbor,
both internal neighbor graphs are empty. Their B are18+3k and12+6k.
Only two high nodes exist, so q0, giving125 when k0 or134 when k1. Counting
the k0 branch as an upper bound does not assert every high incidence is
realizable, and it does not silently discard nondefect intersections.

For c1,b2, a17,P20, first suppose the d3 is disjoint from both d2. Its
nine low neighbors give B18. Let k=0/1 indicate whether the two d2 are
defect neighbors. Each d2 has6-k low plus k d2 neighbors, e_C0 and B12+3k
at most15. With q<=3 the total is17*5+3+18+2*15=136.

Otherwise a d2 meets the d3. Precisely one d2 at a d3 point is impossible:
odd r1=1 supplies too few neighbors for degree3 and r1>=3 gives fan21>P20.
Both d2 must therefore meet the d3 at the same point, since two different
root points would each have only one. Then (A) and parity force r1=1.
The local degree list(3,2,2,1) has a unique defect graph: the d3 joins both
d2 and the low leaf, and the two d2 also join each other. This valid high
triangle is retained. At the other two d3 points there are three low leaves.
At each remaining d2 point, all true root defect neighbors are low; possible
extra low matchings do not become root neighbors.

The d3 root thus has7 low and2 d2 neighbors, with exactly the d2-d2
internal edge, yielding B=7*3+2*6-9-2=22. Its cycle bound is21. Each d2
root has4 low plus one d3 and one d2 neighbor; the sole internal edge
joins those two high neighbors. B=4*3+9+6-6-2=19, bound18. The three high
triangles are concurrent, so q0. The total is17*5+21+18+18=142. The loose
values22+19+19 would give145 and would NOT contradict144; all three exact
nondivisibility losses are required.

| c | b | a | configuration | d1 bound | high bound | total |
|---|---|---|---|---:|---:|---:|
|2|0|18|two disjoint d3 stars|90|36|126|
|2|1|16|d3 stars; d2 disjoint from both|83|48|131|
|1|0|21|one d3; extra low matches retained|105|18|123|
|1|1|19|k0|95|30|125|
|1|1|19|k1|95|39|134|
|1|2|17|d3 disjoint from d2 pair|88|48|136|
|1|2|17|concurrent high triangle and leaf|85|57|142|

Every permitted c>0 case has total cycle incidence strictly below144,
contradicting (B). Thus c0 and every triangle deficiency is0,1,2. This
does not exclude R227 or classify/realize the remaining d2 populations.

## Ten hand falsification boundaries

1. A local four-cycle on four high triangles through one point has repeated
   labels and need not be an actual square. It remains outside this proof's
   at-most-three-high regime; no surviving c0,b>=4 branch is excluded.
2. The local(3,2,2,1) graph is graphical and is a positive control. Removing
   its high triangle or declaring F globally triangle-free is invalid.
3. Its uncorrected B sum gives145, not a contradiction with144. Correct
   internal-edge subtraction and the three integer losses yield142.
4. With l distribution seven3s plus one1, B22 gives c21; with six3s plus
   one1, B19 gives c18. The residue loss one is a sharp scalar inequality.
5. A K3,3 of ordinary rook row/column intersections is valid but its edges
   are covered pairs, not defects. The rejection concerns a defect K3,3.
6. Repeated grid labels can collapse a K3,3 through one point only if all
   six local nodes have degree at least3. The c<=2 premise is indispensable.
7. A root with five low nodes at a point may have a three-leaf root star
   and one separate low matching. Those extra nodes are not root neighbors.
8. Disjoint high triangles can have up to three actual matching cross edges;
   unique completions bound common F neighbors without proving a rook exists.
9. A concurrent common high partner is permitted. Only a d1 common defect
   partner is forbidden by its degree1 slot, giving q0 in the nonstar case.
10. The B formula excludes internal opposite nodes only after proving maximum
    internal degree1. Arbitrary neighbor graphs would require the omitted
    internal choose(degree,2) contribution, so the formula is not universal.

## Forty explicit written proof checks

1. Literal exact R227/actual rook-subset statement and quantifiers.
2. Three exact inherited revisions and separate Root acceptances.
3. Strictmass gives D24 and maximum deficiency3.
4. Population and single-D3 premises leave precisely five positive-c rows.
5. At most three high nodes in each row.
6. Actual triangle linearity and unique edge partner.
7. Distinct-intersection triple prohibition.
8. Exact local defect degree and zero-node unusability.
9. Local odd parity is r1+r3, not r1 alone.
10. Actual fan injection gives coefficients3/5/7.
11. Global F degree3d, no repeated partner,36 edges.
12. Any F triangle is concurrent and high; low triangles impossible.
13. Successive C4 label collision collapses all four nodes.
14. Opposite collision has the same consequence.
15. Four-node collapse needs four high nodes, unavailable here.
16. Faithful labels give an induced actual square.
17. A rook containing a corner pair covers its square.
18. Uncovered square edge triangles are distinct and inverse maps exact.
19. Nonedge-pair square count4158/2=2079 and9 per unique rook.
20. Required C4 count36 and node incidence144.
21. K3,3 adjacent label repetition forces all six concurrent.
22. Opposite repetition reduces to adjacent repetition.
23. Six degree3 local nodes contradict c<=2.
24. Nine distinct grid points yield an induced rook of nondefect pairs.
25. Disjoint high codegree bounded by three matching cross completions.
26. Intersecting high common partners are concurrent/high, at mostone other.
27. Universal F codegree<=3 including low-degree pairs.
28. Low c_Z<=6 and equality with low neighbor yields six distinct K3,3 nodes.
29. Low bound5, exception q<=3 or0 with fewer highs/concurrency.
30. Root neighbor internal edges only between two high nodes at one point.
31. Internal maximum degree1 eliminates internal opposite nodes.
32. Exact incidence B subtracts rootdegree and twice internal edges.
33. l0/1/2/3 losses0/1/1/0 and nonmultiple-three strict bound.
34. c2 roots disjoint by parity/fan/nongraphical3311.
35. c2 exact stars and disjoint optional d2 give126/131.
36. c1b0 extra low matches retained and total123.
37. c1b1 k0/k1 roots give125/134 without disjointness assumption.
38. c1b2 disjoint root case gives136.
39. c1b2 valid nonstar graph gives exact B22/19/19, q0, total142.
40. All positive-c cases fail144; only deficiency upper2 is concluded.

The narrow R228 four/five paper's root incidence, K3,3, exception and residue
mechanisms were inspected as explicit overlap/comparison. Its old gates are
not inherited for this new statement. The three declared R227 premises are
the complete logical dependency list. No whole-archive novelty, formal or
external proof, scientific search coverage, graph realization, R227 exclusion,
registry eligibility or new execution authority is asserted. Fifty hand
proof/boundary checks survive; target scientific status remains UNKNOWN.

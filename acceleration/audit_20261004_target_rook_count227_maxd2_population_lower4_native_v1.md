# Independent conditional R227 maximum-d2 population-lower4 derivation

Verification timestamp: 2026-10-04T19:31:17.6428213Z.
Mathematical producer /root/structural; independent verifier /root/native_driver.
Root requested the narrow conditional statement and challenged the concurrent
three-d2 case. Structural's earlier R228 cycle/table authorship and that
shared outline are disclosed. Agreement is not the verification basis.

Exact r1 claim C-UNRESTRICTED-TARGET-ROOK-COUNT227-MAXD2-D2-POPULATION-LOWER4.
The whole paper8598aea89b6f61130e71bd7f79aee979f71945e86c9578acb8d78c7c637629b7
and raw67cbdf754da32db5282751b920c769cd29e6ac6128e6dfcf26ac3f3e3733ad90
were read. No mathematical worker, source import, AST/syntax check, backend,
solver, graph census, ledger parse or Git/index/publication mutation ran.

## Scope and sole inherited premise

Take a complete finite simple SRG(99,14,1,2), with R227 actual induced
nine-vertex rook subsets counted once. For each actual triangle define
d_T=6-r_T. ASSUME EXPLICITLY that every d_T belongs to{0,1,2}. This assumption
is not supplied by the separate no-D3 result, by its candidate, or by a
pending/current registry entry. Neither the sixteen-row classification nor
the c0,b8 boundary is a premise of the present proof.

Let a,b count d1,d2 actual triangles. The target has99*14/6=231 triangles;
each induced rook has6 triangles, so

    D=6*231-6*227=24, a+2b=24, a=24-2b.

The only inherited theorem is the exact nonempty-maximum-lower2 r1, whose
literal binding/report and distinct Root acceptance were read. At R<231
some d_T>=2. Under this proof's explicit maximum-d2 hypothesis this means
b>=1. It supplies no new cycle or population statement. To prove b>=4,
it remains to refute b1,b2,b3. No claimed survivor is constructed or realized.

## Direct actual geometry and ordinary square count

Each target edge has its unique third triangle vertex. Distinct actual
triangles meet at most once. Three cannot meet pairwise at three distinct
points: those points would make a triangle edge have a second partner.
At every actual point there are seven incident triangles. Join a pair of
them in the local defect graph exactly when no induced rook contains both.
A containing rook for an intersecting pair is unique: the four opposite
cross pairs have a unique second common neighbor after their shared point.
Each rook containing T supplies one other triangle at each point of T,
so the local node degree is exactly d_T. Zero-degree nodes cannot partner.

The global defect graph F uses all positive triangles and all local defect
pairs, each labelled by the actual unique intersection point. Its node T
has degree3d_T, since no partner repeats across different points of T.
It is simple and has3D/2=36 edges. Under b<=3 its only high nodes are at
most three d2 triangles; all other positive nodes are d1 of global degree3.
An F triangle must have one common actual intersection point. Otherwise
its three distinct intersections are forbidden. Such a local triangle
needs degree at least2 at each node, so no F triangle contains a d1 node.
The concurrent three-d2 triangle is permitted, not discarded.

The target has99*84/2=4158 nonadjacent vertex pairs. Each has exactly two
common neighbors, which cannot be adjacent because that edge would then
have two common neighbors. Its induced square is counted twice, once at
each opposite pair, giving2079 squares. An actual rook contains9. A
square determines any containing rook through a corner-triangle pair's
unique grid reconstruction, so no square belongs to two rooks. There are

    U=2079-9*227=36

uncovered actual squares. A rook containing a square's corner triangle
pair necessarily contains the opposite corner, the unique second common
neighbor of its corresponding cross pair. Thus an uncovered square has
all four corner pairs defective, and a covered one has all four covered.

## Faithful C4 correspondence only in the b<=3 contradiction cases

Take an ordinary four-cycle of F. If adjacent edge labels coincide at v,
the first three triangles contain v. The fourth also must: otherwise it
and the first/third triangles meet at three distinct points. Linearity then
puts all four labels at v. Opposite label coincidence puts all four nodes
through v directly. A collapsed cycle requires four distinct local nodes
of degree at least2, hence four d2 triangles. That is impossible at b<=3.

Therefore all four labels are distinct actual points. Consecutive point
pairs are edges in their actual triangles, while either diagonal edge
would have two known common neighbors and violate lambda1. This is an
induced actual square. A rook covering it would contain its corner pairs,
which are defects, so it is uncovered. Conversely an uncovered square has
four distinct actual edge triangles: repeating consecutive ones gives a
diagonal, and repeating opposite ones cannot fit their four vertices into
one triangle. Its defect corner pairs give the inverse F four-cycle.
Unique edge partners and labels prove the bijection, without an assumed
selected cycle catalog. In the b1,b2,b3 cases,

    C4(F)=36, sum_Z c_Z=144.                               (1)

No faithful C4 map is asserted for four or more d2 nodes. Other target
edges and nondefective intersections between positive triangles remain.
No global triangle-freeness or induced positive support is assumed.

## K3,3, codegrees, low-node bounds and the exception count

Suppose six distinct actual triangles form a K3,3 of defect edges. If one
row meets two columns at v, each other row also contains v, or produces
the forbidden distinct-intersection triple with those two columns. The
third column then also contains v. All six nodes would have local degree3,
contradicting maximum d2. Opposite grid-label repetition supplies an
adjacent repetition via a cross grid edge, so all nine labels are distinct.
Those points form three triangle rows and three columns; an extra grid
nonneighbor edge would have two grid common neighbors and violate lambda1.
The resulting rook is induced, and its row/column pairs are not defects.
Thus F has no K3,3 subgraph. Repeated labels are tested before rook formation.

Disjoint d2 triangles have at most three common F neighbors. Such a common
actual triangle supplies a cross edge whose unique triangle completion
is that neighbor. Cross edges form a matching of at most3, since a point
outside an actual triangle cannot meet two of its points under lambda1.
If two d2 triangles intersect, any common actual triangle is concurrent
at their shared point. A common defect node has local degree2 and is d2.
There are at most three d2 nodes, hence at mostone other. A pair with a d1
member has codegree at most3 from its global degree. All distinct F pairs
therefore have common-neighbor count at most3 in the examined cases.

For a d1 node Z, each pair of its three neighbors has Z plus at most two
other common neighbors. Summing the three pairs gives c_Z<=6. If Z has a
d1 neighbor W and reaches6, N(W) has3 members and is contained in both
neighbor sets of the other two neighbors A,B of Z. This forms K3,3 with
rows W,A,B and columns N(W). These six nodes are distinct because no
triangle of F contains d1. Hence c_Z<=5 if Z has any low neighbor.

An exception must have all three neighbors d2, requiring b3. Every such
Z is a common neighbor of a chosen d2 pair, so at most3 exceptions exist.
If F2, the graph on d2 nodes, has any edge, an exception together with
that edge would give an F triangle containing d1. Hence exceptions occur
only in the b3/edgeless case. Total low contribution is at most5a+q,
where q<=3 in that one case and q0 in all other rows.

## Root-incidence accounting including same-point internal edges

For a d2 root T let C=N(T), with six members; let k count its d2 neighbors
and e_C the edges inside C. A d1 member's local defect slot at the root
point is already filled by T, so it cannot use another same-bucket C node.
Different root-point buckets cannot intersect, by the distinct-intersection
triple. Thus internal C edges can only join the other two d2 nodes at
the same root point. There is at mostone such edge, internal degree<=1.

An internal C node cannot be opposite T in a four-cycle because it would
need two C neighbors. For O outside C and T put l_O=|N(O) intersect C|,
the codegree of T,O, at most3. External-incidence counting gives

    B=sum_O l_O=(6-k)*3+k*6-6-2e_C=12+3k-2e_C,
    c_T=sum_O choose(l_O,2)<=B.                             (2)

For l0/1/2/3 the loss l-choose(l,2) is0/1/1/0. If B is not divisible by3
at least one l1 or2 occurs, yielding c_T<=B-1. The internal edge subtracts
twice from external B, and its internal opposite-node contribution has
already been shown zero. This is not a formula for arbitrary root-neighbor
graphs and supplies no rounding or numerical inequality.

## Independent seven-row hand reconstruction

At b1, a22, the lone d2 root has k0/e_C0, B12; q0. Total110+12=122.
At b2, a20, no high edge gives two B12 and total100+24=124. One edge gives
each root k1/e_C0, B15, total100+30=130. No exception can exist at b2.

At b3, a18, the graph F2 on three vertices has exactly four possibilities
up to labels: zero, one, two or three edges. With zero edges each root B12;
q<=3 gives90+3+36=129. One edge gives k list1,1,0 and B15,15,12, with q0,
total90+42=132. A two-edge path gives k1,2,1, with no internal edge because
its endpoint high nodes are not joined; B15,18,15 and total90+48=138.
Its two high edges may have equal actual labels at one point, or different
labels. Neither possibility changes the internal graph or this bound.

With all three edges, the actual d2 triangles intersect pairwise. Their
intersections must coincide by the forbidden distinct-intersection geometry.
Their local defect graph is K3, using both local slots at each node. Each
root has two high neighbors, and exactlyone internal edge between them:
e_C1. Its B=12+6-2=16 and c_T<=15 by the integer loss. All three roots give
45. No low exception can occur when F2 has an edge, so total90+45=135.
The loose high48 would still give138<144, but the genuine loss is recorded.

| b | F2 | a | low bound | high bound | total |
|---|---|---|---:|---:|---:|
|1|isolated|22|110|12|122|
|2|zero edges|20|100|24|124|
|2|one edge|20|100|30|130|
|3|zero edges|18|93|36|129|
|3|one edge|18|90|42|132|
|3|two-edge path|18|90|48|138|
|3|concurrent triangle|18|90|45|135|

Every table bound is strictly below required144, contradicting (1). The
sole inherited maximum-lower2 statement rejects b0. Thus b>=4 under the
explicit maximum-d2 hypothesis, and a=24-2b. No stronger upper range,
R227 exclusion or actual realization is concluded.

## Eight hand falsification boundaries

1. Three concurrent d2 nodes can form local K3; they are included with
   e_C1 at all roots and B16->15, rather than declared impossible locally.
2. Four concurrent high nodes may form a collapsed ordinary F4cycle.
   The faithful square map is restricted to b<=3, not applied to survivors.
3. The two-edge path can share one actual point, using endpoint low leaves
   to fill its remaining local defect slots. Distinct edge labels are not
   needed for its scalar138 bound or for the general F4 map.
4. K3,3 made of actual rook rows/columns exists as nondefective intersections;
   the contradiction is specifically a K3,3 of defect edges.
5. Edgeless F2 can permit up to3 scalar all-high low exceptions; no assumption
   forces them to exist or makes their upper bound a realization.
6. A triangle edge in F2 forbids a low all-high exception through the F
   triangle rule. No assumption of high triangle-freeness is inserted.
7. B16 can be realized as scalar incidence five3s plus one1, giving cycle15;
   both double internal-edge subtraction and residue loss are required for
   the recorded exact high45, even though the looser138 would suffice.
8. Dropping maximum-d2 permits d3 cases outside this proof. The new noD3
   result is retained only as comparison; neither it nor c0b8 is inherited.

## Thirty-two explicit written proof checks

1. Exact target/actual rook-subset quantifiers and explicit maximum-d2 assumption.
2. Sole inherited nonempty-maximum-lower2 r1 and distinct Root acceptance.
3. Actual triangle/rook count gives D24 and a24-2b.
4. Inherited premise rejects b0 only under the explicit maximum-d2 assumption.
5. Unique edge partners, linearity and distinct-intersection prohibition.
6. Exact point defect degrees and global degree3d/36 edges.
7. Concurrent high triangles allowed; no F triangle containing low.
8. Actual square count2079 and covered9-per-rook uniqueness.
9. Corner-pair coverage exactly determines square coverage.
10. Adjacent repeated F4 labels collapse all four triangles.
11. Opposite repeated labels do the same.
12. Collapse requires four high nodes, unavailable at b<=3.
13. Distinct labels make induced square and inverse uncovered-square map.
14. Exact ordinary C4 count36 and node-incidence144.
15. K3,3 adjacent repeated labels force all six concurrent/localdegree3.
16. Opposite repetition reduces to adjacent repetition.
17. Maximum-d2 rejects repeated-label K3,3 without a population assumption.
18. Distinct grid labels form an induced rook of nondefect pairs.
19. Disjoint high codegrees use matching crossedges/unique completions.
20. Intersecting common high partners concurrent, at mostone other at b<=3.
21. Universal codegree<=3 including low-degree pairs.
22. Low c<=6 and equality with low neighbor makes six distinct K3,3 nodes.
23. All-high exceptions require b3 and number at most3.
24. Any F2 edge forbids every low all-high exception.
25. Root internal edges only between same-point high neighbors, at mostone.
26. Internal maximum degree1 eliminates internal opposite-node contributions.
27. Exact B12+3k-2e_C; l<=3 and nondivisibility loss.
28. b1/b2 rows122/124/130.
29. b3 zero/one-edge rows129/132 and q distinctions.
30. b3 two-edge path row138, including equal actual label boundary.
31. b3 triangle concurrency, all three e_C1/B16->15 and total135.
32. All seven bounds below144; only conditional b>=4/a24-2b follows.

The earlier R228 four/five paper's seven-graph, K3,3, exception and B-root
mechanisms are explicit comparison overlap, inspected previously in this
review chain. Its D18 threshold108 differs from this D24 threshold144;
six extra low nodes in each corresponding row increase low bounds by30.
No old gate approves this new conditional theorem. Forty written checks
and seven hand rows survive; zero executed/formal/external checks. Historical
bytes, closed Wave46 cutoff and protected state remain unchanged. Target
existence and scientific coverage remain UNKNOWN, with exact Root-scope
review and any future next-wave47 registration separate.

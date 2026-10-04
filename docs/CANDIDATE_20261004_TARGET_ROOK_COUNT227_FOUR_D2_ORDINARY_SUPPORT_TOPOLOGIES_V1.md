# Candidate: the four-d2 R227 boundary has ordinary support and three high topologies

Root supplied the outside-fan/topology and fourfold norm outlines. Structural
independently reconstructed their actual point labels, selected multiplicities,
full cycle bounds and all Gram scaling constants. Agreement is not independent
verification. This is a separate necessary-condition candidate, not a b4 or
R227 exclusion. All previous papers remain unchanged. No mathematical program,
enumeration, solver, import or worker ran.

## Exact statement and sole inherited result

For every complete finite simple SRG(99,14,1,2), count actual induced rook-nine
vertex subsets once by their vertex sets and put d_T=6-r_T for each actual
triangle. Suppose R=227, every d_T belongs to {0,1,2}, and exactly four actual
triangles have deficiency two. Then there are sixteen deficiency-one triangles.
Every vertex used by them lies in exactly two of them, so their support S has
twenty-four vertices. All four deficiency-two triangles lie wholly in S, and
their actual intersection graph is a four-node star K1,3, a four-node path P4,
or a four-cycle C4.

Use exactly C-UNRESTRICTED-TARGET-ROOK-COUNT227-NO-FOUR-D2-COMMON-POINT r1
to exclude the four high triangles all meeting at one point. Its explicit
maximum-deficiency-two/b4 scope applies directly. No stronger descendant,
whole-population b5 result or unreviewed target exclusion is inherited.
The remaining derivation is reconstructed below.

No surviving topology is asserted realizable. No graph automorphism, equitable
partition, uniform profile, induced selected support or literature premise is
assumed. Additional actual edges are retained in the weighted edge sum and
norm increments.

## Selected parity, fan capacity and at most one outside point

Each actual triangle has three vertices, each target vertex has seven incident
triangles, and each edge has one triangle partner. Distinct triangles meet at
most once. They cannot meet pairwise at three distinct points, which would
give an edge two triangle partners. The local deficiency graph at any point
is simple with triangle-node degree d_T: each of the six other incident
triangle partners is covered by a unique induced rook or none. Two triangles
through a point determine at most one rook via their cross-pair second common
neighbors.

The total deficiency6(231-227)=24 fixes a16, b4 and P20. At each point the
sum of local degrees is even, so selected d1 incidence r_1 is even. For the
selected even family alone, every outer point of an r_1 fan lies on another
selected triangle. Such an external selected triangle cannot meet two outer
fan points by linearity and the distinct-intersection prohibition. Therefore
16>=3r_1, giving nonzero selected multiplicities two or four.

The full positive fan similarly gives20>=3r_1+5r_2. Let k be the selected
fourfold-point count, S the selected support, w half its selected incidence,
and h the number of outside-S points on d2 triangles. Then

    |S|=24-k, sum w=24, ||w||^2=24+2k.

At an outside-S point local degree two needs at least three d2 nodes, and
fan20>=5r_2 permits at most four. Four would put all high triangles through
that point and is excluded by the exact inherited result. Thus every outside
point has three high roots. Two such points would select two triples from
the four roots, sharing at least two triangles and violating linearity.
Consequently h is zero or one, and h1 has exactly three roots through its
single outside point p.

## Weighted Gram first bounds, without discarding extra edges

Let E=sum_{v<t,A_vt=1} w_v*w_t, and let ell count selected edges between
fourfold points. The sixteen selected triangles have48 distinct edges and
selected weighted edge sum48+8k+ell. All d2 internal edges are distinct from
these edges and one another. They supply at least H=12 at h0, or H=6 at h1:
in the latter case three roots through p each supply one internal S edge,
and the fourth root is wholly S. Thus

    E>=48+8k+ell+H.

For the complete target Q=3I-A+J/9, Q is PSD, Q^2=7Q and Qj=0. Hence

    q=w^TQw=136+6k-2E
      <=40-10k-2ell-2H.

It is strictly positive: Qw has coordinate an integer plus8/3, so it cannot
vanish. These inequalities give

    h0: k0 or1;  h1: k0,1 or2.                 (1)

They do not by themselves exclude any of those cases.

## Faithful defect four-cycles and no defect K3,3

Let F have the twenty positive triangle nodes and local defect pairs as
edges, labeled by actual intersection points. Each low d1 node has degree3,
each high d2 node degree6, and F has36 edges.

At a point in S, r_1 is2 or4. Fan capacity gives r_2<=2 or<=1 respectively.
The corresponding degree sequences have local graphs K2, P3, P4, a two-edge
matching, or P3 plus an edge. In particular none has a four-cycle. At h1 the
outside point has a K3 on its three high roots; at every other outside point
there is no positive root. Thus no local F four-cycle is possible.

Any repeated actual point label in an F four-cycle forces all four roots
through that same point, by linearity and the distinct-intersection
prohibition. This would be one of the impossible local four-cycles just
listed. The four distinct labels of every ordinary F four-cycle therefore
form an actual induced square. A diagonal edge would have the two other
corners as common neighbors, contrary to lambda1. Conversely an uncovered
square's four corner triangle pairs are defects and give that F cycle.
A rook covering one corner pair must contain the opposite corner fixed by
the cross-pair second common neighbor, so the maps are inverse.

There are2079 target squares, each in at most one rook, and each rook has
nine squares. Thus U=2079-9*227=36 and

    C4(F)=36, sum_Z c_Z=144.                   (2)

A defect K3,3 with a repeated grid point label propagates to six triangles
through one point and requires local degree3, impossible under maxd2.
Nine distinct grid labels instead form an actual induced rook: extra
grid-nonneighbor edges violate lambda1 via two grid common neighbors.
Its row/column pairs cannot be defects. Therefore F has no K3,3.

All F codegrees are at most3. Disjoint high triangles have at most three
cross edges, forming a matching with unique triangle completions. For
intersecting highs, every common F neighbor must also meet their point;
at S there are at most two highs, and at p at most three. A low degree3
gives the bound for any pair with a low member. No F triangle contains a
low node: a distinct-label triangle is forbidden and an all-one-point
triangle would need local degree2 at that node.

A low node has c_Z<=5 if it has a low neighbor. Otherwise attaining six
would force a K3,3 using that low neighbor's three-node neighborhood and
the other two neighbors. A possible six-cycle low exception must meet
three high nodes, necessarily an independent high triple: meeting two
intersecting highs would require local degree at least2. These exception
counts are retained in the topology table below.

For any high root T its F neighbor graph has internal edges only between
other high nodes. A low neighbor has its local slot filled at the root
point, and cannot intersect neighbors in another root bucket. In every
case below this internal high graph is a matching or empty. No internal
neighbor can therefore be the opposite node of a cycle through T. With
l_O=|N_F(O) intersect N_F(T)|<=3 over external opposite nodes,

    B_T=sum_O l_O=12+3k_T-2e(N_F(T)),
    c_T=sum_O binom(l_O,2)<=B_T.                (3)

If B_T is not divisible by3, at least one l is1 or2 and c_T<=B_T-1.
The twofold internal-edge subtraction is kept; F is not declared globally
triangle-free in h1.

## Exclude the entire one-outside-point case

At h1 three highs A,B,C meet at p, making their local K3. The fourth high D
cannot meet two of them at S points: those three actual triangles would
meet pairwise at distinct points. If D meets one of them, the local degree
sequence at that S point is(2,2,1,1), a P4, and its high-high edge is a
defect. Thus the high graph is K3 plus an isolated node or K3 plus one
pendant node. Its independence number is2, so there are no low exceptions
and the low cycle contribution is at most16*5=80.

For K3 plus isolated D, each triangle root has k_T2 and one internal high
edge, so B16 and c<=15. D has B12. The total is at most

    80+3*15+12=137<144.

For a pendant DA, root A has three high neighbors but only the other two
triangle highs give one internal edge. Its B19 gives c_A<=18. The other
two triangle roots each have B16, c<=15. D has one high neighbor, B15,
c_D<=15. The total is at most

    80+18+15+15+15=143<144.

Both contradict (2). Therefore h0.

## In h0 the high graph is triangle-free with at least three edges

All high points lie in S, where r_2<=2. A triangle among three highs would
put them through one point by the distinct-intersection prohibition,
contrary to that bound. Thus the actual intersection graph on the four
highs is triangle-free. Any high intersection at S has the local P4 degree
sequence, so its edge is a defect and the intersection graph equals the
high induced subgraph of F.

With t high edges, all high neighbor graphs are empty and the summed high
bound from (3) is48+6t. Let q_e count low nodes with three high neighbors.
Each uses three of the24-2t high-low edges, so q_e<=floor((24-2t)/3).
For t2 matching there is no independent high triple, hence q_e0. For t2
path plus isolated node there is only one independent triple; its common
low neighbors number at most3 by the codegree bound. The complete small
table is

| high graph | t | low maximum | high maximum | total maximum |
|---|---:|---:|---:|---:|
| empty |0|80+8|48|136|
| one edge plus two isolates |1|80+7|54|141|
| two disjoint edges |2|80|60|140|
| two-edge path plus isolate |2|80+3|60|143|

Every row contradicts144. Hence t>=3. The only triangle-free simple
four-node graphs with at least three edges are K1,3, P4 and C4: three
edges form a connected tree (a disconnected three-edge triangle-free
four-node graph is impossible), and four edges must be K2,2. This is
abstract finite topology, not an assumption of target automorphism.

## Exclude the fourfold h0 branch by the correctly scaled full norm

It remains to reject k1 permitted by (1). Then S23, w has one peak f of
weight2, all others weight1, sumw24 and normw26. Let Y=3Qw. It is an
integer vector with every coordinate2mod3 and sum0. Therefore

    sum(Y_v^2-Y_v-2)=||Y||^2-198>=0.

Since q=142-2E is a positive even integer, q>=4. The lower edge bound E68
and upper q6 force E=68+z, z0 or1, q=6-2z, and

    ||Y||^2=63q=378-126z.                      (4)

The peak cannot belong to a d2 triangle: its two d2 incident edges would
have weight2 instead of1, raising the d2 weighted edge sum12 to at least14,
and E to at least70. Likewise no extra edge beyond selected/d2 edges can
touch the peak, since its weight2 would raise E to at least70. Thus its
ordinary internal degree remains8.

Before the d2 edges are added, selected-neighbor baselines give Y2 at the
peak and its eight selected neighbors, and Y5 at the other fourteen S
points. Their sum is88 and squared norm386. All d2 endpoints are nonpeak,
so d2 edges have weight1. Every shared high point has exactly two high
roots and four new incident internal edges; every private high point has
two new incident edges. The t high intersections have distinct actual
point labels (three highs at a point are impossible). There are t shared
points and12-2t private points.

At a private point, reducing the baseline by6 changes its square by -24
if the baseline is5, or by +12 if it is2. At a shared point, reducing by12
changes the square by +24 from5, or +96 from2. Thus after all known d2
edges the internal squared norm is at least

    386-24(12-2t)+24t=98+72t,

and the internal sum is88-3*24=16. If z1 there is one further nonpeak
edge, decreasing each endpoint by3. A starting Y value at most5 loses
at most21 squared units, so both endpoints lose at most42. Consequently

    sum_S Y^2>=98+72t-42z, sum_S Y=16-6z.     (5)

The other76 vertices have sum -16+6z. For every residue-two integer y,
y^2-y-2>=0. Hence their squared norm is at least136+6z. Combining with
(5), and using t>=3 already proved, gives

    ||Y||^2>=234+72t-36z>=450-36z.

This exceeds the exact378-126z from (4) by at least72+90z. Both z0 and z1
are impossible. Therefore k0 and all selected multiplicities are two.

## Conclusion, hand controls and overlap

All four d2 triangles lie in the ordinary selected S24, with high graph
K1,3, P4 or C4, exactly as stated. No topology is excluded or constructed
beyond this necessary restriction.

The local(2,2,1,1) P4 is retained, and so is the h1 K3 fan. The h1 pendant
row143 demonstrates why internal-edge subtraction and nondivisibility are
needed. The h0 path/isolate row143 retains its three all-high low exceptions.
The weighted baseline sums88/386 and outside count76 are literal; no
historical factor-nine norm is used. Moving a d2 point onto a selected peak
neighbor increases its square change, so the lower norm bound is safe in
that matching-sensitive case.

The Q, fan, codegree and K3,3 mechanisms overlap earlier R227 work. They
are reconstructed for the present b4 point types. The inherited four-common
point theorem is used once to reject an outside point on all four roots;
its exact scope and revision must remain in any verification or registration.
The target and coverage remain UNKNOWN. This new CANDIDATE requires a
distinct whole proof audit and makes no computation, ledger, Git, publication
or status mutation.

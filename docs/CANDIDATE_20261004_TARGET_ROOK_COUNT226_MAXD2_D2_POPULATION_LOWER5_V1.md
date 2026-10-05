# Candidate: R226 with maximum deficiency two requires at least five d2 roots

Root supplied the small-population topology outline. Structural independently
challenged all eleven four-high graphs, actual covered intersections, collapsed
cycles and the external high opposite in the common-point C4 case. This is a
written CANDIDATE, requiring a different complete review. No mathematical
program, census, import, solver or worker ran; prior proof bytes are unchanged.

## Exact conditional statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T for each actual triangle T.
Suppose R=226 and every d_T belongs to {0,1,2}. If b counts actual
deficiency-two triangles, then b>=5.

Maximum deficiency two is an explicit hypothesis. No pending R226 result is
used to infer it. This is a necessary population bound, not exclusion of the
maxd2 lane, R226 or the target, and does not assert any remaining population
is realized. The logical dependency list is empty: the needed cycle and
incidence facts are reconstructed below.

There are231 actual triangles, since every edge is in its unique triangle.
Each triangle is in at most six actual rooks. At a fixed point of T there
are six other incident triangles; each containing rook pairs T with one of
them as its crossing column. A designated intersecting row and column
determine at most one rook: if their common point is p and their other
points are a,b and c,d, each nonadjacent pair from {a,b} and {c,d} already
has common neighbor p, so mu2 fixes its one remaining common neighbor.
These are precisely the four remaining rook points. For any covered square,
lambda1 fixes the completing triangles of the two edges at one corner;
the same row/column argument fixes its unique containing rook. Likewise two
designated disjoint actual row triangles in a containing rook have their
three cross-matching edges; lambda1 fixes each completing third point and
hence that rook. All are uniqueness statements conditional on the rook
being present, not existence or an embedding assumption.

Summing r_T counts each actual rook six times, so D=sum d_T=1386-6R=30.
Let a count d1 triangles. Then a=30-2b, the positive population is P=30-b,
and 0<=b<=15.

## Defect graph and the required incidence180

At each actual vertex, its seven incident triangles have a local graph of
uncovered pairs. A pair is covered when it belongs to an actual containing
rook. Each incident triangle has exactly d_T uncovered partners there: a
containing rook gives one covered partner at each of its three points,
with the same r_T containing rooks at every point. Let F have the positive
actual triangles as nodes and those uncovered pairs as edges, labeled by
their actual intersection point. A node has degree3d_T. Here lows have
degree3, highs have degree6, and F has45 edges.

There are2079 induced squares: every one of the4158 nonadjacent pairs has
its two common neighbors, and each square is counted by its two diagonals.
Each rook has nine squares; square uniqueness gives45 uncovered squares.
An uncovered square determines its four edge-completing actual triangles,
which are distinct positive nodes, joined cyclically by their actual corner
labels. If a consecutive pair were covered, its containing rook would
contain this square and its unique completions, contrary to uncoveredness.
Different actual squares give different labeled cycles. Hence

    C4(F)>=45, and sum_Z c_Z=4C4(F)>=180.       (1)

Extra collapsed F cycles are allowed. In particular no faithfulness claim
is used in the four-common-high case below.

Three pairwise-intersecting actual triangles must concur: three distinct
intersection points would give an edge with a second common neighbor.
Linearity also gives at most one intersection per pair of triangles.
Thus an F triangle cannot contain a low, whose local degree is one.
For two disjoint actual triangles, cross edges form a matching, and each
edge has its unique third triangle; they have at most three common F
neighbors. Intersecting highs have all common neighbors at their single
intersection and local degree two, so at most two. Any pair involving a
low has at most three by its global degree. All codegrees are at most three.

There is no K3,3 in F. If a grid repeats an intersection label, the
distinct-intersection prohibition and linearity propagate all six roots to
one point, where a grid root would have local degree at least three,
contrary to maxd2. With all nine labels distinct they form the actual row
and column triangles of a rook. Any additional edge between nonadjacent
grid points would give an existing triangle edge a second common neighbor,
so that rook is induced; its row/column pairs could not be defects.

A low with a low neighbor has c<=5. Otherwise its three neighbor pairs
would each have two additional opposites, forcing K3,3 through that
degree-three neighbor. The only possible c6 lows have three high neighbors;
those highs must be independent in F, because no F triangle contains a
low. Each independent high triple has at most three common lows, by the
pair codegree bound. Thus low contributions are at most5a plus three
times the number of independent high triples. This is an upper bound,
not a claim that any such exception is realized.

For a high Z, its low neighbors fill their local degree-one slots, so they
have no F edges to other neighbors of Z. Two high neighbors can have an
internal F edge only in their common bucket at a point of Z. The internal
high edges form a matching, since Z has local degree two. When b<=4 there
is at most one such edge, and internal opposites contribute zero cycles.
For an external opposite W put l=|N_F(Z) intersect N_F(W)|. Then l<=3,
binom(l,2)<=l, and

    c_Z<=B_Z=sum_{V in N_F(Z)}deg_F(V)-6-2e(F[N_F(Z)]).
    B_Z=12+3k_Z-2t_Z.                         (2)

Here k_Z is its number of high F neighbors and t_Z the internal high
neighbor-edge count. If B_Z is not divisible by three, c_Z<=B_Z-1,
since equality requires all positive l equal three. Covered actual
intersections remain permitted; k_Z counts F edges, not all intersections.

Let e_H and tau count edges and triangles in the high F graph. Equation(2)
gives the safe summed high bound12b+6e_H-6tau.

## b0 through3

At b0, the thirty lows contribute at most150.
At b1, twenty-eight lows and the one high give140+12=152.
At b2, twenty-six lows and the two highs give154 with no high F edge,
or160 with their F edge.

At b3, a=24. The complete high-graph table is

| high graph | low bound | high bound | total |
|---|---:|---:|---:|
|empty|123|36|159|
|one edge|120|42|162|
|two-edge path|120|48|168|
|triangle|120|45|165|

For the high triangle, concurrence gives B16 at each high and the integer
loss gives c<=15. Arbitrary separate low-low matching components at the
same actual point are retained; they are not in these high neighbor sets.
Every displayed total is below180.

## b4: all eleven high graphs

Here a=22. The generic bounds handle eight graphs, two are impossible,
and the high C4 is treated separately.

| high F graph | e_H | tau | independent high triples | bound |
|---|---:|---:|---:|---:|
|empty|0|0|4|170|
|one edge|1|0|2|170|
|two disjoint edges|2|0|0|170|
|two-edge path and isolated node|2|0|1|173|
|triangle and isolated node|3|1|0|170|
|four-node path|3|0|0|176|
|triangle with pendant edge|4|1|0|176|
|three-leaf star|3|0|1|179|
|four-cycle|4|0|0|170 or162, below|
|diamond|5|2|0|impossible|
|K4|6|4|0|impossible|

The diamond and K4 have two high triangles sharing an edge. Actual
concurrence and linearity put all four roots at their common point,
where a root would have three defect partners, contrary to maxd2.

Write the high C4 as A-B-C-D-A. Its four edge labels are either all
distinct or all equal: equality of adjacent labels propagates through
the actual distinct-intersection prohibition; equality of opposite
labels puts all four roots through that point by linearity.

If all four meet at one point, a low can meet at most one of them as a
defect neighbor. For root A, its four low neighbors L_A have no internal
edges and have only A as a high neighbor, leaving eight low-low stubs.
Every external low Z has I=0 or1 high neighbors among B,D and x low
neighbors in L_A. Degree three gives x<=3-I and
binom(I+x,2)<=3x/2. These opposites contribute at most12.
The EXTERNAL HIGH opposite C has the two common neighbors B,D and
contributes one further cycle. No internal opposite contributes. Thus
c_A<=13, and similarly all four highs contribute at most52. The lows
contribute110, for total162. The external-high collapsed cycle is
explicitly counted; omitting it and using12 would be incorrect.

If all labels are distinct, opposite actual highs A,C are disjoint, as
are B,D: an additional intersection would give a forbidden distinct
triangle of actual roots. Let n_AC and n_BD count their common low F
neighbors. Their two common high neighbors already use two of the three
allowed common neighbors, so both n values are at most one.

For root A, each of its four low neighbors belongs only to high A or
to highs A,C. Their low-low stub count is8-n_AC; their set is independent.
The external HIGH C contributes
binom(2+n_AC,2)=1+2n_AC.
For an external LOW Z let I count its high neighbors B,D and x its
low neighbors in L_A. For I0 or1, binom(I+x,2)<=3x/2. For I2, x<=1
and the contribution is1+2x, adding at most1+x/2 above that bound.
There are at most n_BD such lows and their x sum is at most n_BD.
The complete opposite partition therefore gives

    c_A<=1+2n_AC+(3/2)(8-n_AC)+(3/2)n_BD
        =13+n_AC/2+3n_BD/2<=15.               (3)

There are no internal opposite contributions. Applying(3) to every
high gives at most60; the110 low contribution gives total170.
No symmetry, uniformity or realization of either n value is assumed.

Thus every b4 topology contradicts(1). Together with the b0..3 tables
this proves the literal necessary condition b>=5.

## Limits and review requirement

The proof uses only an injection from actual uncovered squares into F
cycles. Covered intersections, separate local matching components and
additional actual target edges are kept. The only collapsed four-high
topology is handled with its external HIGH opposite, not discarded.
No generic triangle-free premise, Hamming embedding, automorphism,
equitable partition, numerical feasibility or induced positive support
is assumed. The fan/cycle/Gram methods overlap prior work; no claim of
archive novelty is made. A different exact written audit is required
before VERIFIED or registration use. R226 and the target remain unresolved.

# Candidate: necessary deficiency populations when the rook count is 227

This is a new written candidate, outside the frozen Wave46 cutoff. Root
suggested the next count after the independently reviewed R228 arguments;
Structural derives the population restrictions here. No mathematical program,
enumeration, import, backend or worker ran. The earlier candidates and their
reviews remain unchanged. A different-author written challenge is required.

## Exact statement

For every complete finite simple SRG(99,14,1,2), suppose that R=227 actual
induced rook-nine vertex subsets occur, counted once by their vertex sets.
For each actual triangle T put d_T=6-r_T, where r_T counts those rooks
containing T. Let a,b,c count the triangles of deficiency one, two and three.
All other triangles have deficiency zero, and the following table is necessary:

| c | permitted b | a |
|---|---|---|
|0|1 through 8|24-2b|
|1|0 through 5|21-2b|
|2|0 or 1|18-2b|

No c>=3 occurs. This restricts the populations to sixteen triples (a,b,c).
It does not assert that any listed triple is realizable, exclude R227,
construct a target, or resolve Conway99.

The odd-deficiency family is the union of deficiency-one and deficiency-three
triangles. Its incidence is even at every point. The deficiency-one family
alone is not assumed even when c>0. No uniform point profile, equitable
partition, automorphism, extra codeword or induced positive support is assumed.

## Dependencies and reconstructed local facts

Only these two exact earlier results are inherited:

* C-UNRESTRICTED-TARGET-ROOK-DEFICIENCY-STRICT-SECOND-NEIGHBOR-BOUND r1:
  for positive total deficiency D, D>=6m+6 for every positive deficiency m.
* C-UNRESTRICTED-TARGET-NONZERO-ROOK-DEFICIENCY-MAXIMUM-LOWER2 r1:
  a nonempty positive-deficiency family has maximum deficiency at least two.

Every vertex lies in seven actual triangles. Each edge has a unique triangle
partner. Distinct triangles meet at most once, and three triangles cannot
meet pairwise at three different points: their intersection points would
give an edge a second triangle partner. Two triangles through a point
determine at most one rook through the four cross pairs' unique second
common neighbors. Thus at every point v the simple local defect graph D_v
has its seven incident triangles as nodes, an edge means that no rook contains
both triangles, and its node T has degree d_T.

Double counting six triangles in each rook gives

    D=sum_T d_T=6(231-R)=24.

The strict bound gives d_T<=3; the nonempty maximum bound rules out the
all-deficiency-one case. Consequently

    a+2b+3c=24,  P=a+b+c=24-b-2c,

where P is the number of positive triangles. At a point let r_1,r_2,r_3
count the positive triangles of each deficiency. The handshake identity is

    r_1+r_3 is even.

Zero-deficiency nodes provide no defect edges and cannot supply a missing
partner of a positive node.

## A point fan bound with actual labels

Fix v and its r=r_1+r_2+r_3 positive incident triangles, called the fan.
Their 2r outer points are distinct by linearity. At the two outer points
of a fan triangle of deficiency d, its d defect partners are outside the
fan. This gives 2(r_1+2r_2+3r_3) distinct triangle-point incidences.

An external actual triangle meets at most one outer point of the entire
fan. Two points on the same fan triangle violate linearity; two from
different fan triangles give three triangles meeting at distinct points.
So each of the P-r external positive triangles supplies at most one of
these defect incidences. Therefore

    P >= 3r_1+5r_2+7r_3.                         (1)

This is a general fan bound, not a point-profile assumption. It keeps the
actual point labels and does not count an ordinary defect-graph cycle as
an actual square when its labels may coincide.

## Two or more deficiency-three triangles

Assume c>=2. Then P<=20. Three deficiency-three triangles through one
point have fan weight at least21, while c>=3 would give P<=18. Four or
more also fail. If exactly two occur at a point, r_1 is even. The only
possibilities not immediately exceeding20 are

    (r_1,r_2)=(0,0),(0,1),(2,0).

The first two offer at most three positive nodes, so a degree-three node
cannot have three neighbors. The last has local degree sequence (3,3,1,1).
Both degree-three nodes would join every other node, forcing the purported
degree-one nodes to have degree at least two. Thus the c triangles are
pairwise disjoint in their actual vertices.

At a point of one such triangle r_3=1 and r_1 is odd. If r_1=1, a degree-three
node needs r_2>=2; (1) then needs P>=20, whereas b>=2 and c>=2 give P<=18.
If r_1>=5, the fan weight is at least22. If r_1=3 and r_2>=1, it is at least21.
Therefore every point of every deficiency-three triangle has exactly three
deficiency-one triangles and no deficiency-two triangle. The local graph
is the degree-three star. No statement about other points is inferred.

Let S be the 3c points of these disjoint triangles. The deficiency-one
triangles have exactly9c incidences in S. If t_T=|T intersect S| for a
deficiency-one triangle, then 0<=t_T<=3 and

    sum t_T=9c,  sum binom(t_T,2)>=9c-a.

The second inequality follows termwise from binom(t,2)>=t-1, including
t=0, and counts only known edges. Unique triangle partners ensure that
these edges do not duplicate the 3c edges of the deficiency-three triangles.
Thus e(S)>=12c-a. Also 9c<=3a gives a>=3c; substituting a=24-2b-3c yields
c<=4.

The target equation A^2=12I-A+2J gives the nonprincipal eigenvalues 3,-4.
Hence Q=3I-A+J/9 is positive semidefinite. Its indicator bound on S gives

    e(S) <= (9c+c^2)/2,
    a >= (15c-c^2)/2.                             (2)

For c=3, (2) requires a>=18, while a=15-2b<=15. For c=4 it requires a>=22,
while a=12-2b<=12. Thus only c=2 survives this branch.

For c=2, S consists of two disjoint actual triangles. A deficiency-one
triangle meets each at most once, so t_T<=2. The cross edges between two
disjoint actual triangles form a matching of size at most three: a vertex
outside an actual triangle cannot be adjacent to two of its points, since
that would give their edge a second common neighbor. Each cross edge has
one actual triangle partner. Therefore at most three deficiency-one triangles
meet both. If n_2 is their number, eighteen incidences in S require
a>=18-n_2>=15. Since a=18-2b, b is zero or one.

## Exactly one deficiency-three triangle

Now c=1, a=21-2b and P=22-b. At each of the sole deficiency-three triangle's
points r_3=1 and r_1 is odd. For b>=3, P<=19. The possibility r_1=1 requires
r_2>=2 to provide enough local partners, and its fan weight is at least20.
r_1>=5 has weight at least22. r_1=3 with r_2>=1 has weight at least21.
So for b>=3 every such point is exactly a (3,1,1,1) star: three deficiency-one
partners and no deficiency-two triangle. For b=0,1,2 this star conclusion
is not asserted; those small cases remain in the table.

The three stars provide nine distinct deficiency-one partners C, three in
each bucket of the central triangle T. Thus a>=9 and b<=6. Suppose b=6,
so a=9. All deficiency-one triangles are precisely C, and the remaining
six positive triangles are deficiency-two.

The eighteen outer C points are distinct: equality inside one bucket violates
linearity, while equality between buckets gives the forbidden three-triangle
configuration with T. Each C has one defect incidence at each outer point.
An external triangle meets at most one C outer point in each bucket, so
contributes at most three. The six external deficiency-two triangles must
supply all eighteen incidences, saturating their capacity. Each therefore
has one C defect partner at each of its three points.

At such a point the unique C node, of degree one, already uses its sole defect
edge to this external triangle O. To give O degree two needs another positive
node Z. T is absent there, no other C contains that point, so Z must be another
of the six external deficiency-two triangles. But saturation also makes C
the defect partner of Z at that same point. C would then have degree at least
two. This contradiction rejects b=6. Hence b<=5.

## No deficiency-three triangles: the rook equality point argument

Here c=0, a=24-2b, P=24-b; the deficiency-one family itself has even incidence.
The maximum-lower2 result gives b>=1. The scalar equation permits b<=12.
If b=12, all positive triangles are deficiency-two. Around one T there are
six distinct deficiency-two defect neighbors C. Their total deficiency is12,
so their outer points require24 defect incidences. Only five positive triangles
remain outside C and T, and each contributes at most three, a contradiction.

For b=11 or10, a is respectively two or four. A nonempty even-incidence
selection of two triangles cannot occur by linearity. For four, a fourfold
point leaves eight distinct odd outer points and no remaining triangles;
otherwise every used point has multiplicity two and the dual is K4, whose
triangle is forbidden. Thus b<=9.

Suppose b=9, so a=6. An even selection of six actual triangles is an induced
rook-nine. A sixfold point leaves twelve private outer points; a fourfold point
leaves eight odd outer points for the other two triangles' six incidences.
So every used point has multiplicity two. The dual is simple cubic and
triangle-free on six nodes, hence K3,3: the neighbors of any node must each
join both remaining nodes. Its nine edge-points form the rook's rows and
columns. Extra edges are forbidden by the two rook common neighbors of a
nonadjacent pair. Call this exact induced set S.

At each of the nine points of S its two deficiency-one triangles are together
in this rook and hence are not defect neighbors. Each still needs a degree-one
defect partner. No other deficiency-one triangle is present, so some
deficiency-two triangle must contain that point. Any actual triangle distinct
from the six rook triangles meets S in at most one point: an adjacent rook
pair already has its fixed triangle partner, and a nonadjacent pair cannot
be two vertices of a triangle. There are exactly nine deficiency-two triangles
and nine required points. Consequently each has precisely one rook point,
and each rook point has precisely one of them. In particular their rook roots
are all distinct and their other two vertices are outside S.

The indicator of S has Q-quadratic value

    3*9-2*18+9^2/9 = 0.

Since Q is positive semidefinite, Q*1_S=0 as a full 99-coordinate vector.
At an outside vertex z this equation reads exactly

    1-|N(z) intersect S|=0.

It is not merely a nine-coordinate calculation. Alternatively, common-neighbor
saturation of every rook pair gives at most one rook neighbor per outside
vertex; the90 boundary edges and90 outside vertices force exactly one.
Both arguments establish the same pointwise conclusion, without equitability.

Two different deficiency-two triangles cannot share an outer vertex z:
their distinct rook roots would both be adjacent to z, contradicting its
exactly-one-rook-neighbor property. At either outer point of any deficiency-two
triangle, no deficiency-one triangle is present (all six lie inside S), and
no other deficiency-two triangle is present (the preceding argument). All
other incident triangles have deficiency zero. Its node in D_z therefore
has no possible positive partner, contradicting its required degree two.
Thus b=9 is impossible, completing the table with b<=8.

## Hand challenges, limitations and overlap

* The local degree sequence (3,1,1,1) is a valid star at a common point.
  Its r_1=3 is odd but r_1+r_3=4 is even. Forbidding it by deficiency-one-only
  parity would be incorrect.
* The sequence (3,2,2,1) is locally realizable: join the degree-three node
  to the other three and join the two degree-two nodes. Its fan weight20
  reaches the c=1,b=2 boundary. The proof retains this boundary.
* The sequence (3,3,1,1) is not graphical; both high nodes force two edges
  on each low node. This is a local simple-graph check, not a global census.
* Two disjoint triangles can have three cross edges in a matching. The cap
  three used for c=2 is not replaced by an unjustified cap two.
* A rook's nine-point indicator really has zero Q energy. In the actual
  rook9 graph alone, the target Q is not its ambient PSD matrix and there
  are no90 outside vertices; the target extension premises are essential.
* The fan and induced-rook arguments retain arbitrary other target edges.
  No full positive support is presumed induced, and no collapsed local
  defect four-cycle is counted as a square.

The local degree/odd-family/even-six mechanisms overlap the preserved rook
gap and R228 papers. The one-neighbor property of an induced rook already
appears in the September17 regular-set audit; it is reconstructed here and
is not claimed novel. A narrow Markdown search of docs and acceleration
for R227/count227/deficiency24 returned no earlier precise table. This is
not a whole-archive or worldwide novelty assertion. An earlier malformed
wildcard search was not treated as evidence of absence.

The sixteen rows are necessary populations only, not a classification of
defect graphs or an existence census. The target remains UNKNOWN. The exact
fan, c>=2 PSD edge count, c=1 saturation and c=0 full-coordinate rook equality
need an independent written audit before any mathematical status promotion.

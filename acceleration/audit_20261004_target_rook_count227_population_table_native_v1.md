# Independent written derivation of the R227 necessary population table

Verification timestamp: 2026-10-04T18:54:45.9157103Z.
Mathematical producer: /root/structural. Independent written verifier:
/root/native_driver. Root suggested the follow-up and discussed the outline;
that shared origin is disclosed and supplies no approval by agreement.

Exact candidate paper: docs/CANDIDATE_20261004_TARGET_ROOK_COUNT227_DEFICIENCY_POPULATION_TABLE_V1.md,
SHA256 b5a76e8f0fe994007e5714931bca03d22e7064886e5971f85b7d02fdb8015f55.
Raw candidate: acceleration/results/20261004_target_rook_count227_deficiency_population_table_candidate01.json,
SHA25682e17eba237b222a9188044a8600f04a32bed9e3272c6432f460d8b5f9253c70.
This audit binds C-UNRESTRICTED-TARGET-ROOK-COUNT227-DEFICIENCY-POPULATION-TABLE r1.

I read the entire frozen256-line paper and155-line raw candidate, reconstructed
all deductions below, and checked all sixteen rows and boundaries by hand.
No program, graph enumeration, import, backend, solver, matrix calculation
worker, ledger parse or Git/publication mutation was used. This is the NEXT
Wave47 written lane; it changes no closed Wave46 checkpoint or roster.

## Scope and exact inherited premises

Let G be a complete finite simple SRG(99,14,1,2). R counts actual induced3x3
rook-nine vertex subsets once by their vertex sets. For each actual triangle
T, r_T counts those subsets containing T and d_T=6-r_T. Assume R=227.
Let a,b,c count actual triangles with d=1,2,3, and P=a+b+c.
Only two exact earlier r1 statements are inherited:

* C-UNRESTRICTED-TARGET-ROOK-DEFICIENCY-STRICT-SECOND-NEIGHBOR-BOUND:
  positive D=sum d satisfies D>=6m+6 for every positive d_T=m.
* C-UNRESTRICTED-TARGET-NONZERO-ROOK-DEFICIENCY-MAXIMUM-LOWER2:
  if R<231, a positive triangle has deficiency at least2.

Their actual canonical bindings and distinct Root written acceptances were
read and their precise statements authenticated. This audit does not reapprove
these premises from their historical VERIFIED labels, reexecute their checking
routes, or import a cited global rook exclusion. All remaining local, parity,
spectral and rook-equality steps are derived here.

## Local defects and the fan injection

Each vertex lies in seven actual triangles: its fourteen neighbors form seven
pairs, since an adjacent neighbor has exactly one common neighbor with the
vertex. Counting point-triangle incidences gives99*7/3=231 triangles. Every
edge lies in its unique actual triangle. Distinct triangles meet at most once;
three triangles cannot meet pairwise at three distinct points, for these points
would make a second triangle containing an edge of one original triangle.

At v consider its seven actual triangles. An induced rook containing two of
them has them as its perpendicular row and column. The four remaining grid
points are the unique second common neighbors of their four nonadjacent outer
cross pairs (v is the first). Consequently at most one rook contains that pair.
Every rook containing a fixed T contributes exactly one such other triangle
at each v in T. Thus the simple local graph D_v, joining triangle pairs not
contained together in any induced rook, has degree d_T at T. In particular
d_T>=0; a zero-deficiency node has no defect edges and cannot fill a positive
node's missing degree.

A rook has exactly six actual triangles, so

    D=sum_T d_T=6*231-6R=24.

The strict inherited bound yields m<=3. The maximum-lower2 premise rules out
b=c=0. Therefore a+2b+3c=24 and P=24-b-2c. Local handshake gives

    r1+2r2+3r3 even, equivalently r1+r3 even.

There is no deficiency-one-only parity condition when c>0.

Fix v. Its r positive triangles form a fan. Their2r outer points are distinct.
At the two outer points of a fan triangle of deficiency d, its d partners
cannot be other fan triangles: those meet it only at v. The2(r1+2r2+3r3)
defect incidences therefore use external positive triangles. An external
triangle can meet at most one outer point of the entire fan. Two on one fan
triangle violate linearity; two on different fan triangles give three
triangles meeting pairwise at distinct points. Hence the P-r external
positive triangles supply at most P-r incidences, and

    P>=r+2(r1+2r2+3r3)=3r1+5r2+7r3.                 (F)

This argument retains actual point labels and arbitrary other target edges.
It neither assumes a uniform profile nor identifies a collapsed defect cycle
with an actual square.

## c>=2: disjointness, stars, known edges and PSD

Here P<=20. Three d3 triangles at one point require fan weight21; that would
also imply c>=3 and P<=18. Larger r3 is still impossible. For two d3 triangles,
r1 is even, and (F) allows only (r1,r2)=(0,0),(0,1),(2,0). The first two give
fewer than four positive nodes, insufficient for degree3 in a simple graph.
The last gives degree sequence(3,3,1,1), impossible because each degree3 node
joins both leaves, raising each leaf's degree to at least2. Thus all c d3
triangles are vertex-disjoint.

At a point of one d3 triangle, r3=1 and r1 is odd. If r1=1, degree3 requires
r2>=2, and the fan requires P>=20, but then b>=2,c>=2 imply P<=18. If r1>=5,
the fan requires22. If r1=3,r2>=1 it requires21. Therefore exactly three d1
triangles and no d2 triangle occur there; the local defect graph is the star
with degrees(3,1,1,1). This conclusion concerns those d3 points only.

Let S be the3c points of the c disjoint d3 triangles. The d1 triangles have
exactly9c incidences in S. For every d1 triangle put t=|T intersect S|<=3.
Then sum t=9c and binom(t,2)>=t-1 for all t=0,1,2,3, including the negative
right-hand side at t0. The known d1 edges in S therefore number at least9c-a.
They are distinct across triangles and from the3c d3 edges, by the unique
triangle partner property. Arbitrary additional edges may exist, so only

    e(S)>=12c-a

is asserted. Also9c<=3a gives a>=3c; a=24-2b-3c then forces c<=4.

The exact ambient equation is A^2=12I-A+2J. On j, A has eigenvalue14;
on j-perp its eigenvalues are3 and-4. Therefore Q=3I-A+J/9 is PSD, with
Qj=0 and nonprincipal eigenvalues0 or7. Its full99-dimensional indicator
inequality on |S|=3c is

    0<=1_S^T Q1_S=9c-2e(S)+c^2.

Combining the two edge bounds yields a>=(15c-c^2)/2. At c3 this needs a>=18
but a=15-2b<=15. At c4 it needs a>=22 but a=12-2b<=12. Consequently c>=3
is impossible. No ordinary PSD property of an isolated support is substituted
for the full target premise.

For c2, S is two disjoint actual triangles. A d1 triangle meets each at most
once, so t<=2. Cross edges between the two triangles form a matching: an
outside point cannot be adjacent to two vertices of an actual triangle,
for their edge already has its unique common neighbor. There are at most
three cross edges. Each d1 triangle meeting both uses a distinct cross edge,
so n2<=3. Eighteen known incidences require a>=18-n2>=15. Since a=18-2b,
only b0 or b1 remains. The sharp cap3 is retained, not replaced by cap2.

## c1: the stars and the saturated b6 obstruction

Now a=21-2b and P=22-b. For b>=3, P<=19. At a point of the sole d3 triangle,
r3=1 and r1 is odd. r1=1 needs r2>=2 and fan weight20; r1>=5 needs22;
r1=3,r2>=1 needs21. Thus all three points are degree(3,1,1,1) stars.
For b0,1,2 these alternatives are not rejected and no star conclusion is
imposed. In particular the graphical degree(3,2,2,1) boundary has fan weight20.

The central triangle T has nine distinct d1 partners C, three in each bucket.
Thus a>=9 and b<=6. At b6 all a9 d1 triangles are these C, and exactly six
further positive triangles O have deficiency2. The18 outer C points are
distinct: same-bucket equality violates linearity; different-bucket equality
forms the forbidden three-triangle configuration with T. No other C or T
can supply any of their eighteen required d1 defect partners.

An O can meet at most one C outer point in each bucket, so can supply at most
three such incidences. Six O must supply eighteen incidences, hence every O
has a C defect partner at each of its three points. At any such point, C is
the unique d1 triangle and its degree1 edge already joins O. To complete O's
degree2, another positive triangle Z is needed. It cannot be T or another C,
so it must be another O. Saturation then gives C-Z a defect edge too at that
same point. C would have degree at least2, a contradiction. Therefore b6
is impossible, while b>=7 was already rejected by a>=9. This gives0<=b<=5.

## c0: even two/four/six families and the full99 rook equality

Here a=24-2b and P=24-b. The d1 family alone has even incidence, and the
maximum-lower2 premise gives b>=1. Nonnegative a gives b<=12.

At b12 all twelve positive triangles have degree2. At any of their points,
the local graph needs at least three positive nodes, so (F) gives P>=15,
contradicting P12. This is a shorter independent exclusion than the paper's
valid outer-mass route. In that route T has six distinct d2 partners C;
their12 distinct outer points need24 defect incidences. Only five external
positive triangles remain, each able to meet at most one C point per bucket,
so they supply at most15. Both routes preserve actual point labels.

At b11 there would be an even-incidence selection of two actual triangles,
impossible because linearity prevents their three vertices all being shared.
At b10 there would be an even selection of four. A multiplicity4 point leaves
eight distinct odd outer points and no other selected triangle to correct them.
Otherwise every selected point has multiplicity2; the simple cubic incidence
dual on four nodes is K4, with a triangle prohibited by the three-triangle
geometry. These exclusions are parity of the selected d1 family, not of all
positive triangles.

At b9, a6 d1 triangles form an even family. A multiplicity6 point leaves
12 private outer points. A multiplicity4 point leaves eight distinct odd
outer points requiring correction from the other two triangles, which have
only six point incidences. Thus every used point has multiplicity2. Its
incidence dual is simple, cubic and triangle-free on six nodes. If v has
neighbors x,y,z, those three are independent and must each join both other
nodes, so the dual is K3,3. Its nine distinct edge-points identify three rows
and three columns of an actual rook. Nonadjacent grid points already have
two common grid neighbors, forbidding any extra edge by target lambda1.
Thus S is an exact induced rook-nine; no inducedness of the whole positive
support is assumed.

At each point of S, the two d1 triangles lie together in this rook and are
not defect neighbors. Each still requires a positive degree1 partner, so at
least one d2 triangle contains the point. An actual triangle other than the
six rook triangles meets S at most once: an adjacent rook pair has its fixed
triangle partner, and a nonadjacent pair cannot lie together in a triangle.
Exactly nine d2 triangles cover nine necessary points. Every one therefore
has one rook root, every root is distinct, and its two outer points are
outside S. A d2 triangle can partner both local d1 nodes at its single root;
this is consistent and is not prematurely ruled out.

For the full target PSD Q,

    1_S^T Q1_S=3*9-2*18+9^2/9=0.

PSD of a real symmetric matrix implies Q1_S=0, for instance by its orthogonal
eigenspace decomposition. This is an equality in all99 coordinates. At an
outside vertex z the equation reads1-|N(z) intersect S|=0, so z has exactly
one rook neighbor. Internal zero-energy values alone would not prove this.

A separate combinatorial derivation confirms the same pointwise fact. Any
outside vertex cannot meet two rook vertices: adjacent pairs already have
one common neighbor inside S, nonadjacent pairs already have two. There are
9*(14-4)=90 boundary edges and90 outside vertices; all have at most one,
so each has exactly one. No automorphism or equitable-profile premise is
needed for either argument.

Two different d2 triangles cannot share an outer point, since it would be
adjacent to their distinct rook roots. At an outer point of any d2 triangle,
none of the six d1 triangles is present (all lie in S), no other d2 triangle
is present, and c0 excludes d3. All remaining local nodes have degree0.
Its required degree2 is therefore impossible. This rejects b9 and leaves
exactly the necessary range1<=b<=8.

## Complete hand table and falsification boundaries

All rows below satisfy a+2b+3c=24 and P=a+b+c=24-b-2c by hand.
They are retained necessary possibilities, not claimed realizable populations.

| c | b | a | P |
|---:|---:|---:|---:|
|0|1|22|23|
|0|2|20|22|
|0|3|18|21|
|0|4|16|20|
|0|5|14|19|
|0|6|12|18|
|0|7|10|17|
|0|8|8|16|
|1|0|21|22|
|1|1|19|21|
|1|2|17|20|
|1|3|15|19|
|1|4|13|18|
|1|5|11|17|
|2|0|18|20|
|2|1|16|19|

Eight written boundary challenges were checked:

1. The common-point star(3,1,1,1) is graphical; r1=3 is odd, while r1+r3=4
   is even. Incorrect d1-only parity when c>0 would reject a permitted case.
2. The sequence(3,2,2,1) is graphical: the high node joins all others and
   the two degree2 nodes join each other. Its fan weight20 is the c1,b2
   boundary, not an exclusion; local graph triangles at one point are allowed.
3. The sequence(3,3,1,1) is not graphical, since both high nodes must join
   every leaf. This uses simplicity and actual local degrees only.
4. A matching of three cross edges between two disjoint actual triangles
   does not violate the cap; the argument must not replace three by two.
5. K3,3 gives six even triangles on a rook, so even-six alone is not forbidden.
   The defect definitions plus the external d2 requirement provide the exclusion.
6. A zero-deficiency triangle supplies no defect edge, even if it intersects
   a positive triangle; geometric intersection is not a usable missing partner.
7. The isolated rook9 graph has degree4, not the target degree14/ambient PSD
   hypothesis or90 outside vertices. Its internal data alone do not justify
   Q1_S=0 outside S or an R227 exclusion.
8. Extra actual edges in S for the c>=2 branch can only increase e(S), so the
   known-edge lower bound remains valid. Full positive-support inducedness,
   a faithful collapsed-cycle map and a uniform point profile are not premises.

Thirty explicit proof/application checks are recorded for the report:

1. Seven incident actual triangles at every point.
2. Exactly231 actual triangles by point incidence.
3. Triangle linearity and unique edge partners.
4. The prohibition of three distinct pairwise intersection points.
5. At most one induced rook for an incident triangle pair.
6. Exact local degree d_T=6-r_T and nonnegative deficiencies.
7. Exact D24 from six triangles per actual rook.
8. Strict inherited bound implies maximum deficiency3.
9. Inherited nonempty maximum-lower2 excludes all d1.
10. Local handshake gives even r1+r3, not r1 alone for c>0.
11. Distinct2r actual fan outer points.
12. An external triangle meets at most one fan outer point.
13. Exact positive-fan coefficients3,5,7.
14. No three or more d3 triangles at a point for c>=2.
15. All two-d3 common-point degree/fan possibilities are rejected.
16. One-d3 points are precisely stars when c>=2.
17. The9c incidences imply a>=3c and c<=4.
18. Known S-edge lower bound12c-a without inducedness.
19. Full target PSD Q and |S|=3c indicator upper bound.
20. c3 and c4 contradict their available a.
21. c2 sharp matching cap3 implies b<=1.
22. c1,b>=3 stars and nine distinct d1 partners imply b<=6.
23. c1,b6 saturated six-d2 partner capacity contradicts degree1.
24. c0,b0 violates the nonempty maximum-lower2 premise.
25. c0,b12 fails both the fan and outer-mass routes.
26. c0,b11 and b10 fail even-two/four geometry.
27. Even-six geometry yields an induced rook without support-inducedness.
28. Exactly nine d2 triangles have distinct single rook roots.
29. Full99 PSD equality and independent90-edge argument force one neighbor.
30. No d2 shared outer point leaves its local degree impossible; all sixteen
    rows are retained with correct sums and no realizability conclusion.

## Archive and status boundary

The September17 regular-set audit independently contains the one-rook-neighbor
argument, including exactly90 boundary edges. It was read directly as a narrow
scope comparison; no archived computational gate is transferred. Even-six,
local deficiency, parity and previous R228 mechanisms overlap older sources.
No whole-archive search or global novelty assertion is made by this audit.
No unassigned stronger follow-up is implicitly approved here.

The exact r1 sixteen-row necessary statement survives this independent written
challenge. R227 is not excluded and no listed row is asserted realizable.
The target and overall scientific coverage remain UNKNOWN. No graph object,
formal/external proof, source execution or new worker gate is claimed. Original
paper/raw bytes, historical reports, ledger, Git/index and frozen rosters remain
unchanged. Exact new Root acceptance and registration are separate pending steps.
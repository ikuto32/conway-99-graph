# Independent written audit: exact R226/maxd3, c1/b7 necessary profile

Completed verification: 2026-10-04T22:37:53.9644142Z.
Producer /root/structural; verifier /root/native_driver;
method independent_derivation; computational executor null.

Paper docs/CANDIDATE_20261004_TARGET_ROOK_COUNT226_MAXD3_SINGLE_D3_SEVEN_D2_PROFILE_V1.md
SHA256 b98e0a6438880c9d7bb60fd37ee250650b954477050b17237e83a40951997d09.
Raw acceleration/results/20261004_target_rook_count226_maxd3_single_d3_seven_d2_profile_candidate01.json
SHA256 1f7c67e9f3a5cf3d6a084bfa6f2ef2a17636af023b80157c792240d770ed4ebb.
ID C-UNRESTRICTED-TARGET-ROOK-COUNT226-MAXD3-SINGLE-D3-SEVEN-D2-PROFILE r1.

The whole frozen statement survives independent derivation and boundary
challenge. Written PASS gives its precise necessary profile. Neither its
surviving 42-edge nor 43-edge option is excluded or constructed. Logical
dependencies are empty, and the literal maxd3/c1/b7 conditions are retained.

## Literal statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
rook-nine vertex sets once and put d_T=6-r_T. Suppose R=226, every d_T
belongs to {0,1,2,3}, exactly one actual triangle T has deficiency three,
and exactly seven actual triangles have deficiency two. Then T has two
points each incident to exactly three d1 and no d2 triangles, and one point
incident to exactly one d1 and two d2 triangles. The even selected family
O=D1 union {T} consists of fourteen actual triangles, supported on nineteen
actual points: the first two T points each have selected incidence four,
and all seventeen other support points have selected incidence two.
The induced support has exactly42 or43 edges, consisting of the42 selected
triangle edges and at most one further edge. Any further edge joins ordinary
points and avoids the third T point. The two d2 triangles through that third
T point have four distinct outer points, all outside the selected support.

Structural's attached/residue discovery and Root's baseline/pair-budget
challenge are shared history. Native independently reconstructs the full
proof below. Earlier fan/parity/Gram mechanisms overlap; this is not an
independent-discovery or archive-novelty claim. No previous c1 range or b8
theorem is used as a logical premise.

## Complete target foundations and all local profiles

Each of the 693 target edges has one triangle completion, giving 231 actual
triangles. Seven incident triangles at a vertex partition fourteen outer
neighbors. Actual triangles are linear. An actual triple meeting pairwise
at distinct points would form another triangle on these points and give
one edge two common neighbors, contradicting lambda=1. Thus pairwise
intersecting actual triples concur.

For two intersecting triangles in a containing induced rook, their common
point and four outer points determine the remaining four: each cross
nonadjacent pair has that common point as one neighbor and mu=2 fixes the
second. Containing-rook uniqueness makes local covered partners distinct.
The local defect graph of pairs in no rook has degree d_T=6-r_T, and
zero-deficiency nodes are isolated. Its odd-degree parity is r1+r3 even.
Summing triangle/rook incidences gives D=1386-6R=30. With c1/b7,
a=30-3-14=13 and positive population P=21.

For a positive fan, every focal root requires its d_T partners at both
outer points. Those external positive triangles are all distinct: one
cannot meet two points on one root by linearity or points on different
roots by the nonconcurrent-triple prohibition. Hence

    P>=3r1+5r2+7r3.

At a T point r3=1 and r1 is positive odd. With r1=1, degree three forces
at least two d2 roots; P21 permits exactly two. The sequence (3,2,2,1)
forces T joined to all other roots and the d2 pair joined: the bad profile.
With r1=3, r2 can be zero or one. Without it the graph is the T/three-d1
star. With it, the sequence (3,2,1,1,1) forces T-d2, two T-d1 edges and
the remaining d2-d1 edge: if T used all three leaves, no leaf capacity
would remain for d2. r1>=5 needs fan22 and is impossible. No extra positive
local component evades the counted profiles. Let h count bad points and
g count good points carrying a d2; h0..3 and g0..3-h cover all ten cases.

## Weighted selected identity and actual pair capacities

The selected O consists of thirteen d1 roots and T, size s=14, with even
point incidence. Put w equal to half that incidence. Define nonnegative
K=sum w(w-1), ell=sum(w_u-1)(w_v-1) over selected edges, and H as the
weighted sum of all other actual internal edges. The selected weighted
edge sum is 3s+4K+ell, since selected degree at v is 4w_v. Also sum w=21
and squared norm 21+K. Larger selected incidences are allowed at this stage.

The complete target identities give A^2=12I-A+2J, A j=14j and
Q=3I-A+J/9 with Q^2=7Q. Therefore q=w^TQw=||Qw||^2/7>=0 and

    q=28-5K-2ell-2H.
    Y=3Qw=9w-3Aw+7j, sum Y=0, Y_v=1 modulo3.
    ||Y||^2=63q.

This is the full factor63 norm, not seven. At good T points w=2 and at
bad points w=1, so K>=2(3-h) and ell>=binom(3-h,2).

There are m=2h+g attached d2 roots meeting T, all distinct. Their 2m
outer labels are distinct and outside T: same-point attachments cannot
meet twice; different-point attachments cannot meet by the nonconcurrent
triple rule. At an attached outer point outside S, no d1 or d3 root occurs
and at most one attached root occurs. Degree two requires two unattached
d2 roots. Selecting a pair injects the distinct outer points into distinct
actual intersection pairs of those roots. Covered intersections remain
allowed. With two unattached roots there is capacity one. With three there
is capacity two: three distinct pair labels would violate concurrency.
With four there is capacity four: five edges on four roots contain a
diamond whose two concurrent triples force all four roots to one point,
contradicting five distinct labels.

For zero/one/two inside outer points, attached roots centered at a bad
weight-one point contribute at least 0/1/3 to H. Those centered at a good
weight-two point contribute at least 0/2/5. All such edges are nonselected
and distinct by unique target edge completion. Actual extra edges and
larger weights only increase these bounds.

## Reject h0, h2, h3 without omitting good attachments

h0 has K>=6, ell>=3 and q<=28-30-6=-8, for every g.
h3 has six attached roots and one unattached root. No outer point can be
outside S, since two unattached roots would be required. All twelve are
inside and H>=6*3=18, giving q<=-8.

h2/g0 has four attached and three unattached roots. At most two of eight
outer points are outside S; six inside points among four two-slot roots
require H>=8. One good peak gives K>=2, so q<=2. K is an even integer;
if it exceeded two it would be at least four and force q<0. Thus exactly
the good T point has w=2, and every other support point has w=1. At the
two bad T points, selected neighbor weight is 2+1+1+1=5, giving baseline
Y=1. Attached inside outer contributions at those two centers sum at least
six, so their Y sum is at most 2-18=-16. Their squared norm is at least
(-16)^2/2=128, exceeding total ||Y||^2=63q<=126. This rejects h2/g0.

h2/g1 has four bad-center and one good-center attached root, and only two
unattached roots. At most one of ten outer points is outside S. All inside
would contribute 4*3+5=17; removing one inside incidence reduces this by
at most three, so H>=14 and q<=28-10-28=-10. These two branches exhaust h2.

## h1: derive the exact nineteen-point baseline and restrict every extra edge

There are two good T points. K>=4 and ell>=1; increasing the even integer
K to at least six would force q<0. Thus K=4: those two points are the only
peaks, both weight two; all other support points have weight one. Sum w=21
gives S19. The peak-peak T edge is the only selected edge with two peaks,
so ell=1 and q=6-2H.

Each peak has eight selected neighbors: the other peak, the bad T point,
and six points on its other selected roots. Its selected weighted neighbor
sum is nine, hence Y baseline 18-27+7=-2. The bad T point has weighted
neighbor sum 2+2+1+1=6, giving baseline 9-18+7=-2. The twelve other peak
neighbors are distinct: the adjacent peaks have only the bad point as a
common neighbor by lambda=1. Each has baseline one. The four remaining
ordinary support points have baseline four. Thus inside baseline counts
are three(-2), twelve(1), four(4), with sum22 and squared norm88.

Let zeta count extra actual edges incident to a peak. There is no extra
peak-peak edge because that edge already belongs to T. A peak-ordinary
edge has weight two; an ordinary-ordinary edge has weight one. Let k_v
be the added weighted neighbor increment at v. Its total over S is
2H-zeta, and its sum at the peaks is zeta. In particular H>=2zeta.

For any integer k>=0 and baseline v<=4, (v-3k)^2>=v^2-15k, because
9k^2-6vk>=9k^2-24k>=-15k. At a peak v=-2 the bound sharpens to
(v-3k)^2>=v^2+21k. Summing the generic bound and its peak improvement
36k gives

    ||Y||^2_S>=88-30H+51zeta,
    sum_S Y=22-6H+3zeta.

There are eighty outside coordinates, each 1 modulo3. For precisely this
integer residue class, y^2+y-2>=0, with equality at y=1 or -2. Since
sum Y=0, their norm is at least 160+sum_S Y=182-6H+3zeta. Consequently

    378-126H=63(6-2H)>=270-36H+54zeta,
    90H+54zeta<=108.

H is an integer, so H<=1. An extra peak edge alone costs two in H;
therefore zeta=0, using H>=2zeta rather than dropping that linkage.
Every remaining extra edge is between ordinary points with weight one.

If H=1 and that edge touched the bad T point, its baseline -2 changes
to -5, increasing its square by21. The other ordinary endpoint lowers
its square by at most15. The inside norm is then at least94 and sum16;
the outside residue inequality gives at least176. Total norm is at least
270, but q=4 and 63q=252. No extra edge can touch the bad T point.

Any attached outer point inside S would supply an extra edge at its
T center. At a bad center that has just been prohibited; at a good peak
it costs at least two, contradicting H<=1. All attached outer labels are
outside S. g1 would give three attached roots and four unattached roots:
six distinct outside labels exceed capacity four. g2 gives four attached
and three unattached roots: eight labels exceed capacity two. Hence g=0.

There are exactly two good points with three d1/no d2 and one bad point
with one d1/two d2. Four distinct attached outer labels are outside S.
The fourteen selected triangles have 42 distinct actual edges. H0/1 and
zeta0 give exactly zero or one further actual support edge, ordinary and
avoiding the bad point. The induced support consequently has 42 or 43
edges. This proves all components of the raw statement, with no assertion
that either remaining option exists or is impossible.

## Written proof-check record: 36 checks, zero executions

1. Actual edge and triangle counts are 693 and 231.
2. Local seven-root outer labels and linearity.
3. Actual intersecting triples concur.
4. Conditional intersecting-pair rook uniqueness.
5. Local degree equals d_T and zero-deficiency roots are isolated.
6. Deficiency mass30 gives a13/P21.
7. Odd local parity gives r1+r3 even.
8. Exact whole-fan outer-partner injection.
9. Coefficients3/5/7 and no component bypass.
10. Bad (3,2,2,1) point profile.
11. Good unattached star profile.
12. Good attached (3,2,1,1,1) profile.
13. All ten h/g cases are retained.
14. Selected fourteen-root even incidence and weight sum21.
15. General selected edge expansion 3s+4K+ell.
16. Q^2=7Q, PSD and exact q base28.
17. Integer-residue Y and exact norm63q.
18. Attached root and outer-label distinctness.
19. Outside points inject into actual unattached pairs.
20. Pair capacities one/two/four for two/three/four roots.
21. Attached bad/good H bounds 0/1/3 and 0/2/5.
22. All h0 profiles have q<=-8.
23. h3 has every outer point inside and q<=-8.
24. h2/g0 has H>=8 and K2 forced.
25. Its two bad-coordinate squared norm128 exceeds126.
26. h2/g1 retains good attachments and has H>=14/q<=-10.
27. h1 forces K4, unique two peaks and support19.
28. ell1 and exact q=6-2H.
29. Actual peak-neighbor overlap gives baseline counts3/12/4.
30. Exact added-increment identities2H-zeta and zeta, with H>=2zeta.
31. Integer quadratic bounds give inside norm88-30H+51zeta.
32. Eighty outside residue coordinates give norm182-6H+3zeta.
33. Complete norm inequality90H+54zeta<=108 gives H0/1/zeta0.
34. A bad-point extra edge forces270>252.
35. All attached outer points outside excludes g1/g2, leaving g0.
36. Distinct selected edges and H0/1 give precisely42/43 induced edges.

## Written falsification/boundary record: 14 challenges

1. No previous necessary range or b8 exclusion is used.
2. The good-point d2 attachment is included until its own rejection.
3. Covered intersections are included in every unattached-pair graph.
4. A four-cycle on four unattached roots still allows four outside points.
5. Distinct attachment labels follow from actual geometry, not F adjacency.
6. Higher even selected incidences are not excluded before K is forced.
7. The norm normalization is63, and all outside coordinates are counted.
8. Adjacent peak common-neighbor uniqueness is required for twelve baseline-one points.
9. Weighted increments differ from twice H by zeta; they are not ordinary degrees.
10. H>=2zeta is needed to finish zeta0 from the integer allowance.
11. The residue inequality fails for integer zero and is used only for1 modulo3.
12. An H1 bad edge is rejected separately; H<=1 alone does not exclude it.
13. H0/H1 surviving options are neither excluded nor claimed realizable.
14. No selected inducedness, outside uniform profile or target resolution is presumed.

There are 50 written checks, zero computational/formal/external checks and
zero solver calls. Tools read documentary source, hash four selected files
and save append-only metadata only. No mathematical program/import, worker,
enumeration, ledger parse/write, Git/index/protected or publication mutation
occurred. Root-reported live467 is context only. Original pending nulls,
scopes and timestamps remain, and new Root acceptance/registration are
separate later actions.

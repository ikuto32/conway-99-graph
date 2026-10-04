# Target twelve-column unbalanced words: remaining structural family

Status **CANDIDATE**, derivation by `/root/structural`, prepared
2026-10-03T16:14:00+00:00. Root proposed the sign/star branch outline in
conversation; Structural independently reconstructed the branches, including
the degree-four boundary, the sixteen-point anchor calculations and arbitrary
ambient extra-edge corrections. This is new discovery preparation, not an
independent approval of Root's outline. No mathematical program, enumeration,
fixture, solver, formal checker or external review was executed. Novelty is
unknown; no ledger/index/current-head or old-proof changes are made.

## Exact proposed statement

Let G be a finite simple (99,14,1,2) graph, with one column for each actual
triangle in its point-triangle incidence matrix B over GF(3). Let z satisfy
Bz=0, sum(z)!=0 and |supp(z)|=12. After globally changing sign, its selected
columns have p=5 positive and q=7 negative coefficients. All used points have
selected degree two or three; exactly two have degree three, both negative.
There are exactly seventeen used points. The two negative degree-three stars
share one selected negative triangle, and the selected rows have the family
description in Section5.

This is only a necessary family description. It asserts neither a unique
isomorphism class nor that its selected collinearity graph is induced. It does
not identify every possible ambient extra edge, prove completion, force a
twelve-column word in a target, or resolve target existence. A moment test of
one particular17-point member alone cannot exclude this whole family.

## 1. Selected degrees, including the degree-four boundary

Actual triangles are linear and contain no Berge triangle: three pairwise
intersections at different points create a second common neighbor on an
actual edge. Every used point has selected degree at least two, since its
nonzero coefficient sum must vanish.

For any selected degree-d point, its d columns have2d distinct outer points.
Another selected column meets at most one outer point, by linearity and the
Berge-triangle veto. Therefore, with w selected columns,

```
w-d >= sum_outer(d_u-1),     w>=3d,
sum_outer(d_u-2) <= w-3d.
```

For w=12, selected degrees are at most four. If a degree-four point exists,
its four coefficients must be two of each sign. The eight outer points all
have degree two because w-3d=0. The eight other columns each contain exactly
one outer point. The four outer incidences on the positive center columns
force four negative other columns, and the other four force four positive
other columns. Thus p=q=6 for the entire twelve-column word, regardless of
degrees at any points outside this star. This contradicts the unbalanced sum.

Hence every used point has degree two or three. Degree-two signs are opposite;
degree-three signs are all equal. If a,b are the positive/negative degree-three
point counts and c2 counts degree-two points, then

```
3p=3a+c2,    3q=3b+c2,    p-q=a-b.
```

All-degree-two words are balanced, so at least one degree-three point exists.
For any such star, at most w-9=3 outer points can have degree three. At least
three degree-two outer points require three distinct opposite-sign columns.
It follows that both p,q>=3. With p<=q, sum(z) nonzero leaves only
(p,q)=(4,8) or (5,7); (3,9) and (6,6) are balanced.
No connectedness, simplicity of the triangle-intersection graph, circuit
minimality or symmetry is assumed in this argument.

## 2. Exhausting degree-three star counts

Same-sign degree-three stars are three-subsets of that sign's column labels.
They are linear, have no Berge triangle, and a column lies in at most three
stars because an actual triangle has three points. Two stars need five labels.
Four stars need at least eight labels: if three share a label, they use seven
labels and a fourth, which cannot use that label, meets at most one of their
six outer labels, giving at least nine. Otherwise all labels have multiplicity
at most two. The four-star intersection graph is triangle free, has at most
four edges, and their union has size12-E>=8. For the edge bound, adjacent
degrees sum to at most four; summation and Cauchy give E^2<=4E.

Five stars similarly need at least nine labels. The common-three-label case
already reaches nine with a fourth. Otherwise the five-star triangle-free
intersection graph has at most six edges: sum(deg^2)<=5E and
sum(deg^2)>=(2E)^2/5 imply E<=25/4, hence E<=6. Their union has15-E>=9.

For (4,8), two positive stars cannot fit, so a<=1 and b=a+4. The a=1,b=5
choice cannot fit five stars in eight negative columns. Thus (a,b)=(0,4).
For (5,7), a<=2 and b<=3, with b=a+2. The only choices are (0,2) and (1,3).
All higher outer-point degrees have now been addressed globally; they are
not silently assumed absent in any branch below.

## 3. The (p,q,a,b)=(4,8,0,4) family

All eight negative columns are used by the four negative stars. Their union
has size eight, so the no-common-three case attains four intersection edges,
each star has intersection degree two, and this intersection graph is C4.
Name its centers n0,n1,n2,n3 cyclically. The negative columns are precisely

```
{ni,n_(i+1),ti},       {ni,fi,gi},       i mod4.
```

All twelve t/f/g points have selected degree two. The four degree-two outer
points at each center require four distinct positive columns. Since p=4,
every positive column meets each center's outer set exactly once. A cyclic t
belongs to two such outer sets and a free f/g belongs to one. Each positive
column therefore has exactly one t and two free points, from the two centers
not on that t's negative edge. This accounts for every positive column;
possible label assignments are not claimed isomorphic or enumerated.

For H0, the selected-triangle collinearity graph, C={n0,n1,n2,n3} has degree6
and L consists of twelve degree4 leaves. All center pairs are saturated:
cycle edges have their single t completion, and opposite nonedges have the
two remaining centers as common neighbors.

For each ni the C-L internal CN sum is exactly18:

| leaf category | size | individual CN | sum |
|---|---:|---:|---:|
| its adjacent leaves |4|1|4|
| nonincident cyclic t leaves |2|2|4|
| free leaves of its two adjacent center groups |4|2|8|
| free leaves of its opposite center group |2|1|2|

For an adjacent group's free leaf, the two common neighbors are its center
and either a cyclic t incident with ni or ni's free leaf on that positive
column. These two alternatives exhaust the forced positive-column structure.
For an opposite group's free leaf, only the appropriate incident t is common.

Thus C-L target sum=2*48-16=80 and internal sum=72, giving anchor deficit R=8.
Using the standalone budgets derived in the companion three-negative-star
paper, V=152,P=72,T=32,N=51, whence E=112,Q=64. The exact integer pair minimum
at112=2*51+10 is51+20=71>64.

This veto also covers every ambient extra edge. Every leaf meets one or two
centers; saturation prohibits new C-C/C-L edges and new L-L edges with shared
anchor neighbors. For any other added leaf edge, fixed anchor counts t_u,t_v
are at least one and at most two. Delta E=t_u+t_v-2>=0, while
Delta Q=-(1+d_H(u)+d_H(v))+(t_u+t_v)<=-5, since current leaf degrees are at
least four. T32,N51 remain fixed. Thus the integer pair minimum cannot
decrease and Q cannot increase. The branch cannot occur in a target even when
its selected graph is not induced. The proof does not rely on a one-edge
enumeration or compatibility of any particular addition.

## 4. The (5,7,1,3) branch

The complete derivation is preserved separately in
[the three-negative-star candidate](CANDIDATE_20261003_UNBALANCED_TWELVE_TRIANGLE_THREE_NEGATIVE_STARS_V1.md),
SHA43518d2aecf1ee79fdafa611ed5afa6b13b81b2ce140423f741266ea34a5edcc.
This is an unverified same-author written premise, not an independently approved
claim. Its derivation is part of this proposed package and requires separate
verification before using the present conclusion.

The one positive center's six outer degree-two points cover six distinct
negative columns. Every negative center must use the seventh uncovered column
to avoid three common neighbors with the positive center; that column contains
all three negative centers. Three cross-group t pairs and two free triples
then give the full sixteen-point geometry. Its total CN2 pair count24/28 must
not be substituted for the anchor deficit R=12. The correct center/leaf sum66
gives V152,P72,T32,N51,E108,Q60, whereas the exact pair minimum is63. The same
extra-edge monotonicity covers every possible final induced graph. This branch
is therefore also excluded conditionally on the companion derivation's
independent verification.

## 5. The remaining (5,7,0,2) family on seventeen points

Let s,t be the two negative degree-three points. Their negative stars cannot
be disjoint: either star would then have six degree-two outer points requiring
six positive columns, more than five. Thus they share one negative triangle
{s,t,x}; distinct stars share at most one column. The other four star columns
are two at s and two at t, each with two degree-two outer leaves. Call these
four s-leaves a1..a4 and four t-leaves b1..b4. The remaining two negative
columns partition six additional degree-two points r1..r6 into two triples.
Every point degree is determined by the global (a,b)=(0,2) count; no unseen
degree-three or degree-four outer point is omitted.

Each star has five degree-two outer points (x and its four a or b leaves),
requiring all five distinct positive columns. One positive column contains x
and two r points, one from each of the two remaining negative columns, by
linearity. Every other positive column contains one a, one b and one remaining
r. The a/b correspondence is a bijection; all four remaining r points occur
once. Together these rows cover all12 selected columns and17 used points.

This is a family with additional local CN restrictions, not a unique frozen
configuration. No enumeration of the a/b matching, r allocation, allowable
ambient extra edges or isomorphism classes has been performed. The accepted
literal17-point circuit is one member, and its24 individual possible additions
are not automatically an exhaustive test of this entire word family or their
simultaneous additions.

For reference, this selected family alone has V166,P116. The two centers are
pair-saturated with their common x, so T16,N66. Each has C-L internal CN sum
5*1+4*2+6*1=19, target sum25, and their anchor R=12. Thus E138,Q104; the exact
integer pair minimum at138=2*66+6 is78, which does not veto the family. Six r
points have zero anchor neighbors, so the sixteen-point monotonicity cannot be
transferred: adding an edge incident with such leaves may decrease E. This
explicit boundary is why all combined additions and complete exterior moments
remain necessary questions rather than conclusions.

## Limits and verification obligation

Every argument concerns the whole selected word, including disconnected
possibilities before the exhaustive counts. The branch arguments themselves
force the stated connected incidence families; connectedness was not an input
premise. The conclusion uses full99/degree14 target outside budgets to rule
out the two sixteen-point branches. It is not a stronger local lambda1/mu<=2
word-size theorem: valid local cap configurations can still have twelve-column
unbalanced words.

The companion moment design70ef/raw584c supplies necessary equations for a
specified complete induced17-point graph. It has not been executed and is not
an input feasibility verdict or a universal family classification. No rational
Farkas witness, integer realization, global rank obstruction, balanced-all-right-
kernel theorem, or target exclusion is asserted here. Structural discovery
requires a different verifier and ROOT review before any report or binding.

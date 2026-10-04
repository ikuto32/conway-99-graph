# Independent written audit: unbalanced twelve actual-triangle columns

Verifier: /root/checkpoint_audit. Producer: /root/structural.
This is a separate handwritten reconstruction of the two frozen candidate
papers, including an attempt to falsify their coverage and the non-induced
completion argument. Root's original branch outline and Structural's corrected
anchor calculation are disclosed shared origins; their agreement is not used
as an approval. No program, enumeration, solver, proof checker, graph fixture
or target realization was executed.

Inputs:
- docs/CANDIDATE_20261003_UNBALANCED_TWELVE_TRIANGLE_THREE_NEGATIVE_STARS_V1.md,
  SHA256 43518d2aecf1ee79fdafa611ed5afa6b13b81b2ce140423f741266ea34a5edcc.
- docs/CANDIDATE_20261003_UNBALANCED_TWELVE_TRIANGLE_WORD_TARGET_TYPES_V1.md,
  SHA256 6f26e9f4b989f76de8b5954627ed217a00a2beabf88e8b11f64eb33c34ba209b.

## Verdict and exact boundary

The necessary family conclusion survives this written audit. In any simple
(99,14,1,2) graph, an unbalanced GF(3) right-kernel word on twelve actual
triangle columns, after changing all signs if necessary, has five positive and
seven negative columns, no selected point of degree four or above, exactly two
degree-three selected points of negative sign, and seventeen used points.
Its rows have the stated shared-star/x/a/b/r family description.

Separately, the one-positive/three-negative degree-three branch has no target
completion, even if its selected graph is not induced. The four-negative-star
branch also has no target completion. These two full-target exclusions justify
discarding exactly those branches in the family argument.

This does not prove a target exists or does not exist; it does not force such
a word, show a unique isomorphism class, assert inducedness, approve all local
assignments, or exhaust the remaining seventeen-point family's simultaneous
extra edges. The conclusions concern the complete selected twelve-column
word; connectedness and circuit minimality are not assumed.

## 1. Geometry and the global degree-four boundary

Distinct actual triangles share at most one point: otherwise their common edge
would have at least two common neighbors. Three distinct triangles cannot
intersect pairwise at three different points. The three intersections form a
triangle; on one of its edges, the first selected triangle's third point and
the third intersection give two distinct common neighbors. Distinctness follows
again from the one-point intersection rule.

Let a point occur on d selected columns. They have 2d distinct other points.
Any other selected column meets at most one of these outer points: two in one
star column violate linearity; two in different star columns create the
forbidden three-triangle cycle. Every outer point must have at least one
additional selected incidence because a single nonzero coefficient cannot
sum to zero. Thus 12-d >= 2d, and d <= 4. More precisely,
sum_outer(deg_selected(u)-2) <= 12-3d.

For d=4 all eight outer points have degree two and all eight other columns
meet exactly one outer point. A zero row with four signs has two positive
and two negative incidences. Four outer points on the positive center columns
therefore require four distinct negative other columns; the other four require
four distinct positive other columns. Including the center's two columns of
each sign gives p=q=6 for the entire word. This argument counts all twelve
columns, not merely a component, so no remote branch can repair the imbalance.

Consequently all selected point degrees are two or three. Degree two has one
of each sign; degree three has three equal signs. With a positive degree-three
points, b negative degree-three points and c2 degree-two points,
3p=3a+c2, 3q=3b+c2 and p-q=a-b. If a=b=0 the word is balanced. At a degree-three
star, at most three of its six outer points have degree three, so at least
three outer points of degree two force distinct opposite-sign columns. The
star itself already uses three columns of its own sign; both sign populations
are at least three.

After a global sign change p<=q. Since p+q=12, imbalance modulo three leaves
only (p,q)=(4,8) and (5,7). The pairs (3,9) and (6,6) are balanced.

## 2. Exhaustive sign-star counts

A same-sign degree-three point is a three-subset of that sign's column labels.
These triples are linear and contain no three-triple cycle. A column label
lies in at most three such stars, because an actual triangle has three points.

Two stars need at least five labels. Three need at least six labels even before
the cycle veto, sufficient to exclude three stars within five labels.
Four stars need at least eight labels:
if three share a label, they use seven labels; a fourth cannot contain that
label and can meet at most one of the other six labels, so their union has
at least nine labels. Otherwise labels have multiplicity at most two and the
four-star intersection graph is simple triangle free. It has at most four
edges, giving union size 12-E >= 8.
For five stars, the common-three case already reaches nine labels on adding
a fourth. Otherwise the five-star intersection graph is triangle free and
has at most six edges, giving union 15-E >= 9. The small edge bounds can also
be proved without classification: every edge uv in a triangle-free graph on h
vertices satisfies deg(u)+deg(v)<=h; summing and Cauchy give
4E^2/h <= sum deg(v)^2 <= hE, hence E<=h^2/4.

For (4,8), a<=1 and b=a+4. The choice a=1,b=5 needs at least nine negative
labels, so only (a,b)=(0,4) remains. For (5,7), a<=2, b<=3 and b=a+2, leaving
exactly (0,2) and (1,3). This counts the whole word, whether initially
connected or disconnected, and includes every possible degree-three point.

## 3. Four negative stars: independent forced geometry

Four negative stars in eight negative labels attain the lower union bound.
They cannot have a threefold common label, which would need at least nine.
Their triangle-free four-vertex intersection graph has four edges and therefore
is C4. Write its four degree-three points n0,n1,n2,n3 cyclically. The negative
columns are {ni,n_(i+1),ti} and {ni,fi,gi}, for i modulo four. All twelve
t/f/g leaves have selected degree two.

Each center has four degree-two outer points requiring all four positive
columns, each meeting that outer set exactly once. A t belongs to two centers'
outer sets, and a free f/g to one. A positive column's three points must account
for four such incidences, so it has exactly one t and two free leaves. The free
leaves belong to the two centers not incident with that t's negative edge.
This derives all columns without choosing one particular labeling.

In the selected graph H0, all centers have degree six and all twelve leaves
have degree four. Center cycle edges have their unique t completion; opposite
center nonedges have their two other centers as common neighbors. Every center
pair is saturated.

For one center, its four adjacent leaves each have CN1; its two nonincident
t leaves each have one neighboring center and one own-group free leaf as
common neighbors, giving CN2. An adjacent group's four free leaves each have
that center and either an incident t or an own-group free leaf, giving CN2.
The opposite group's two free leaves each have the incident t as their sole
common neighbor. Hence the center-leaf CN sum is 4+4+8+2=18 per center, 72 total.
There are sixteen center-leaf edges, so the target center-leaf sum is
2*(4*12)-16=80 and the anchor deficit is R=8.

## 4. One positive and three negative stars: independent forced geometry

Let c be the positive degree-three point and n1,n2,n3 the negative ones.
The six outer points of c are degree two, and their negative columns are six
distinct columns, each meeting only one c-outer point. If some ni's three
negative columns were all among these six, ni and c would have at least three
distinct common neighbors, contradicting the target caps. Thus every ni is
in the seventh negative column, which is exactly {n1,n2,n3}.

The six remaining negative columns each have one ni, one c-outer point t and
one additional degree-two point f. They are
{ni,tiA,fiA},{ni,tiB,fiB}. All twelve t/f points are distinct; all incidences
of the four degree-three centers have now been consumed.
The c-positive columns pair the six t points. No pair may be from one negative
group, since its edge would have both c and ni as common neighbors. The group
quotient is a loopless degree-two multigraph on three groups, necessarily one
edge between every pair of groups. The remaining two positive columns cannot
contain two f points from one negative group for the same edge-CN reason;
each has one f from each group. Naming these columns A/B labels all possibilities
by assigning each group's A endpoint to one of its two quotient edges.

The center pairs are saturated: ni,nj are adjacent with their third center
as CN1; c,ni are nonadjacent with tiA,tiB as CN2. Their degrees are six, and all
t/f leaves have degree four.
The center c has CN1 with all six t and all six f, giving total12.
For ni, its four adjacent leaves contribute4. Of the four other-group t,
two are paired to its own t and have CN2; the other two have CN1, total6.
Each of four other-group f has its own negative center and ni's same-tag f
as common neighbors, total8. Thus each ni contributes18 and all center-leaf
CN sum is 66. There are eighteen center-leaf edges, so the target sum is
2*48-18=78 and the correct anchor deficit is R=12.

As a check of the paper's auxiliary total-CN2 count, exactly3 center pairs,
18 center-leaf pairs and3 same-group t pairs have CN2. The remaining CN2 pairs
are the two t/f cross pairs for each same-tag quotient edge. The product of the
three edge tag relations is -1, because the two endpoints at every group have
opposite tags; hence there are zero or two same-tag edges. This gives24 or28
total CN2 pairs. This quantity is not R and is never inserted into its budget.

## 5. Exact target budgets, with every extra edge covered

For a final induced H on m target vertices let V=sum_v(14-deg_H(v)).
Summing the target unordered-pair CN values and subtracting internal two-walks
gives P(H)=2*binom(m,2)-|E(H)|-sum_v binom(deg_H(v),2).
This is the number of unordered pairs of neighbors in S contributed by
vertices outside S, counting each outside vertex by binom(|N(x) intersect S|,2).

Both sixteen-point bases have36 edges, four degree-six centers and twelve
degree-four leaves. Therefore V=152 and P=240-36-60-72=72.
Each center needs eight outside neighbors, and saturation of every center pair
makes all32 such vertices distinct. Call these X; the remaining outside set
Y has51 vertices. For x in X let r_x count its leaf neighbors. The complete
center-leaf target deficits give sum_X r_x=R. Such an x contributes
binom(1+r_x,2)>=r_x to outside pairs. Hence Y has E=V-32-R incidences into S
and pair upper budget Q=P-R.

The four-negative case has E112,Q64. Among51 nonnegative integer counts summing
to112, balancing gives41 counts2 and10 counts3, whose pair sum is71>64.
The one-positive/three-negative case has E108,Q60:45 counts2 and6 counts3
give minimum63>60. The integer minimum follows by transferring one unit between
two counts differing by at least two, strictly decreasing their binomial sum.

To avoid an inducedness assumption, expose every final extra edge sequentially.
No center-center addition is possible: the missing center pairs already have
CN2 and cannot become edges with target CN1. No center-leaf addition is
possible either: every leaf already has a center neighbor, so a new center
neighbor would add a CN to a saturated center pair. Thus center rows, X32 and
Y51 remain fixed.
A new leaf edge cannot join leaves sharing a center; it would add a second CN
on an already completed center-leaf edge. Its endpoint center-neighbor sets
are disjoint, with fixed sizes t_u,t_v in {1,2}.

Exactly Delta V=-2, Delta R=-(t_u+t_v), and
Delta P=-(1+deg_H(u)+deg_H(v)). Consequently
Delta E=t_u+t_v-2>=0 and
Delta Q=-1-deg_H(u)-deg_H(v)+t_u+t_v<=-5.
The pre-addition endpoint degrees are at least four and can grow.
The integer minimum for51 vertices is nondecreasing in E, while Q decreases;
the initial contradictions persist for every simultaneous extra-edge set.
Intermediate graphs need not be induced target realizations. Negative final
deficits would themselves veto a target. This is an algebraic completion
argument, not a one-edge enumeration or a claim that all additions are compatible.

## 6. The only remaining necessary family

For (p,q,a,b)=(5,7,0,2), call the two negative degree-three points s,t.
Disjoint stars would require six distinct positive columns at either star,
more than five. They therefore share exactly one column {s,t,x}.
Their four other columns use four distinct a leaves at s and four distinct b
leaves at t. Each has selected degree two, so it has no second negative
incidence. The remaining two negative columns consist of six new r leaves
partitioned into triples. These account for all21 negative incidences:
six at the centers, one at x, eight at a/b, and six at r.

At each center, its five degree-two outer points require every one of the five
positive columns. The positive column containing x cannot contain an a or b
leaf, since that creates a forbidden same-anchor edge. Its two other points
are r leaves, one from each remaining negative column by linearity.
Each of the other four positive columns contains exactly one a and one b
(the five-column coverage at both centers), and its third point is one of
the remaining four r leaves. This gives the stated a/b bijection and r allocation.

There are exactly two selected degree-three points and fifteen degree-two
points: the incidence count is6+30=36, so seventeen used points. No hidden
higher-degree point, detached component, repeated leaf or unused column
survives the complete counts.

As a scope boundary, the seventeen-point base has center degrees6, leaf
degrees4 and36 edges, so V166 and P272-36-30-90=116. The two saturated adjacent
centers give X16,Y66. Each has center-leaf CN sum5+8+6=19 and target25, giving
R12,E138,Q104. The integer pair minimum is78<=104, not an exclusion.
The six r points have zero anchor neighbors, so added r-incident edges can
make Delta E negative. The sixteen-point monotonic proof must not be reused
for this family. No feasibility, completion, class count or target resolution
follows from the necessary description.

## 7. Written falsification and boundary inventory

The following sixteen checks were handwritten, not executed fixtures:
1. A single selected incidence cannot be a zero row over GF(3).
2. A degree-four row is exactly two signs of each kind.
3. Its8 outer points consume all8 other columns and balance the whole word.
4. The lower sign populations are3, including the all-negative-star case.
5. The balanced (3,9) and (6,6) sign populations are not mistaken for unbalanced.
6. Triple-shared column labels are separately handled in four/five-star bounds.
7. Four stars in exactly8 labels force C4; no star disconnectedness assumption.
8. Three positive stars cannot fit5 labels; four negative stars cannot fit7.
9. The p4 positive-column one-t/two-free constraint covers all assignments.
10. The p5 uncovered seventh column must contain all three negative centers.
11. The c/ni anchor deficit12 is kept distinct from total CN2 count24/28.
12. Integer minima are71 and63, with pair budgets64 and60 respectively.
13. Every ambient center-incident addition is vetoed by existing saturation.
14. Arbitrary combined leaf additions use growing degrees and monotone E/Q.
15. The remaining shared-star family's x positive column uses one r per unused
    negative triangle, and all four a-b-r rows are accounted for.
16. Zero-anchor r leaves block any transfer of the sixteen-point monotonicity;
    the seventeen-point78<=104 budget is deliberately not an exclusion.

No counterexample to the exact written necessary-family statement was found.
This audit supplies ordinary independent written derivation only; zero
mathematical commands, graph realizations, formal checks or external reviews.
The frozen candidate bytes remain CANDIDATE historical source evidence.

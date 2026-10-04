# Candidate: R227 with maximum deficiency two cannot have six d2 triangles

This new V2 written candidate preserves the rejected unsealed V1 draft and its
explicit veto receipt. Root suggested the fourfold-incidence split, identified
V1's five-versus-six neighbor error on shared triple fans, and challenged the
new wholly-S sixth-root norm correction. Structural reconstructed both actual
branches and the disjoint branch's triangle-sum energy. That joint discovery
and challenge is not independent verification. No mathematical program,
enumeration, import, backend or worker ran. Different-author whole-V2 written
reconstruction is required; all previous bytes remain unchanged.

## Exact statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
nine-vertex rook subsets once by their vertex sets and put d_T=6-r_T for
each actual triangle, where r_T counts the rooks containing T. If R=227
and every d_T belongs to {0,1,2}, then it is impossible that exactly six
actual triangles have deficiency two. Equivalently, the positive family
cannot consist of twelve d1 and six d2 triangles, with every other d_T zero.

The maximum-deficiency-two condition is a literal hypothesis. This does not
exclude other populations or R227 itself. It does not impose equitability,
an automorphism, an induced selected-support premise or uniform neighbour
profiles. The separate seven-d2 candidate is comparison evidence, not an
inherited logical premise or verification gate.

## Local parity and the two fan bounds

Each vertex lies in seven actual triangles. Distinct actual triangles meet
at most once; three cannot meet pairwise at three distinct points, since the
three intersection points would give an edge a second triangle partner.
Two intersecting actual triangles determine at most one induced rook by
the unique second common neighbors of their four cross pairs.

At a point v the local defect graph joins triangle pairs not contained in
a rook. Its degree at T is d_T: the r_T rooks containing T give distinct
covered partners through v. The sum of local degrees is even, so under
maxd2 the d1 triangles form an even point-incidence selection.

Each of231 actual triangles has baseline6 and each rook has six triangles.
Thus D=sum d_T=6(231-R)=24. At the hypothesized b6 boundary, a=12 and the
positive population is P=18. Counting the two sets of outer defect partners
of the positive triangles through any point gives

    18>=3r_1+5r_2.                              (1)

An external triangle can meet at most one outer point of that whole fan,
by linearity and the forbidden distinct-intersection triple. A zero-deficiency
triangle cannot supply a defect partner.

For the selected twelve d1 triangles alone, a point with selected multiplicity
r has2r distinct outer points whose selected parity must be completed by
external selected triangles. The same injection gives12>=3r. Every positive
selected multiplicity is even, and consequently belongs to {2,4}.

Let k count points of selected multiplicity four, and let S be the selected
support. The total selected point incidence is36, so

    |S|=18-k.

The twelve selected actual triangles give36 distinct edges inside S. These
edges are not asserted to be all its edges.

## At most two outside triple points of six actual triangles

Every point of a d2 triangle outside S has no d1. Its degree two needs
at least three incident d2 triangles. Bound (1) allows at most three.
It is therefore a concurrence point of exactly three of the six d2 triangles.

Let h count these points. Fix one if there is any. Its three d2 triangles
are a base fan, leaving three external triangles. Another outside triple
point contains at most one base root by linearity. An attached point uses
one base root and two external triangles; a detached point uses all three
external triangles.

The external pairs of two attached points would be disjoint: sharing an
external root with the same base root violates linearity; sharing one with
different base roots creates three distinct intersection points through the
base point. With only three external roots, at most one attached point exists.
There is at most one detached point. An attached point and a detached point
cannot both occur, since the attached external pair would then meet at
both points. Thus there is at most one other triple point, and

    h<=2.

If t_i counts the outside-S points of d2 triangle i, then sum t_i=3h<=6.
For t in {0,1,2,3}, binom(3-t,2)>=2-t. The six d2 triangles consequently
add at least12-sum t_i>=6 distinct edges inside S, separate from the36
d1 edges. Thus

    e(S)>=42.                                  (2)

## Fourfold selected incidence is impossible

The target upper Gram is Q=3I-A+J/9. The target adjacency identity
A^2+A=12I+2J and regularity14 show that Q is positive semidefinite and
Q^2=7Q. For an indicator on n vertices,

    chi^T Q chi=3n+n^2/9-2e.

If k>=3, then n=18-k<=15, and even the36 selected edges give a negative
quadratic form (at n15 its upper value is70-72=-2). If k1, the edge bound
is e<=floor((51+289/9)/2)=41. If k2, it is e<=floor((48+256/9)/2)=38.
Both contradict (2). Hence k0: S has18 points, every point lies in exactly
two selected d1 triangles, and all the selected multiplicities are retained
without invoking an equitable profile.

## The two outside points: exact shared or disjoint alternatives

For h<=1, sum t_i<=3. The direct integer identity

    binom(3-t,2)=3-2t+binom(t,2)

gives at least18-2*3=12 additional edges, or e(S)>=48. Positivity at n18
gives e(S)<=45, a contradiction. Thus h2, at points p,q.

Their three-root sets have at most one root in common by linearity. The
shared branch has t=(2,1,1,1,1,0); the disjoint branch has all six t_i=1.
Both branches must be checked. In particular a shared root has p,q and
only ONE S point; it cannot supply two S neighbors to either p or q.

Put y=Q chi_S. It is an ordinary integer vector because |S|/9=2:

    y_z=5-deg_S(z) for z in S,
    y_z=2-deg_S(z) for z outside S.

It has sum zero and

    ||y||^2=7(90-2e(S)).                         (3)

### Shared-root branch: the five-neighbor bound and the sixth-root correction

If p,q share one root, that root has only one S point. At each of p,q the
other two incident d2 roots each have two S points. These five points are
distinct by linearity, giving y_p,y_q<=-3, not-4. The integer edge terms are
0,1,1,1,1,3: there are seven d2 edges in S and e(S)>=43. If e(S)>=44,
(3) gives norm at most14 while p,q alone contribute at least18. Thus e(S)=43,
the whole vector has squared norm28, and the36 d1 plus seven d2 edges
exhaust all actual edges of S.

For z in S let k_z be the increment of its internal degree supplied by d2
edges beyond its four known d1 neighbors. Its exact degree is4+k_z, so
y_z=1-k_z. The seven d2 edges give sum k_z=14. The sixth root, with t=0,
is wholly inside S and gives increments at least2 at three distinct points.
For nonnegative integer k, k^2>=k; at those three points k^2-k>=2. Hence

    sum_S k_z^2>=20,
    sum_S y_z^2=18-28+sum_S k_z^2>=10,
    sum_S y_z=18-14=4.

The pair p,q has squared norm at least18 and sum at most-6. Since the whole
vector sums to zero, the remaining79 outside entries have sum at least2.
Every ordinary integer z obeys z^2>=z, so their squared norm is at least2.
The whole squared norm is therefore at least10+18+2=30, contradicting28.
This excludes the shared branch using five guaranteed neighbors and the
actual wholly-S sixth root. It does not repair V1 by pretending there were
six neighbors or by assuming values on the remaining outside vertices.

### Disjoint-root branch: the six-neighbor bound is genuinely applicable

If the two root sets are disjoint, every d2 has exactly one outside point
and contributes one edge in S. At each of p,q its three roots have six
distinct outer vertices in S, so y_p,y_q<=-4 and their squares total at
least32. Equations (2),(3) then force

    e(S)=42,  ||y||^2=42,  y_p=y_q=-4.           (4)

The last equality follows because an entry<=-5 would already force squares
at least25+16 plus the internal contribution below, exceeding42. All actual
edges of S are now exactly the36 d1 and six d2 edges; any extra edge would
have been included in e(S) and rejected by (3).

## The complete small-norm integer boundary

For a point z of S let r_z be the number of incident d2 triangles. It is
zero, one or two by (1), since there are exactly two d1 triangles there.
The d1 triangles give four distinct neighbors in S; each d2 gives one more,
and there are no additional edges after (4). Hence

    y_z=1-r_z,  sum_{z in S} r_z=12.

Let ell count the points with r_z=2. There are6+ell points with r_z=0,
12-2ell with r_z=1, and ell with r_z=2. Thus

    sum_{S} y_z=6,  sum_{S} y_z^2=6+2ell.

The81 outside vertices include p,q. Their remaining79 entries have sum2
and squared norm4-2ell. In particular ell<=1: an integer vector of sum2
has squared norm at least2. No remaining entry exceeds2, and at most one
can equal2, since its square alone uses the whole possible norm4.

The complete literal possibilities are ell1 with two entries+1, and ell0
with either one entry+2 or three entries+1 and one entry-1. All others
are zero. The proof below needs only the maximum2 and at-most-one+2 facts;
it does not assume which outside vertex receives a value or its adjacency.

For completeness, this same internal norm is at least6. If either y_p or
y_q were<=-5, the total norm would be at least6+25+16=47, verifying the
last step of (4) without presuming their exact boundary degrees.

## Ordinary triangle-sum energy leaves at most eighteen units for d0

Let N be the ordinary99 by231 actual triangle-incidence matrix. Every vertex
lies in seven triangles, and every edge in one, so NN^T=A+7I. Since Qy=7y
and sum y=0, Ay=-4y. Therefore the exact squared energy of all actual
triangle sums is

    sum_T (sum_{z in T} y_z)^2
      =y^T NN^T y=3||y||^2=126.                 (5)

The twelve d1 triangles count every S point twice, so their triangle sums
total12. For every ordinary integer s, s^2>=s, including negative s.
Consequently the d1 contribution to (5) is at least12; no sign or uniform
triangle-sum assumption is needed.

Each of the six d2 triangles contains p or q with value-4 and two S points.
Each such S point has r_z>=1 and y_z<=0. Its triangle sum is at most-4,
so the six d2 triangles contribute at least96. Thus all remaining actual
d0 triangles together have squared triangle-sum energy at most

    126-12-96=18.                               (6)

## The eight d0 triangles through p and q exceed that budget

Each of p,q belongs to seven actual triangles. Exactly three are d2 and
none is d1, so its other four are d0. If p and q are adjacent, their unique
triangle is d0. Its sum is at most-4-4+2=-6, so its square alone is at
least36, violating (6). Hence their two families of four d0 triangles are
disjoint: a triangle containing both would imply their adjacency.

At most one of the four d0 triangles through p can use the unique possible
vertex with value+2. A vertex cannot occur in two different triangles with
p, by unique edge partners. Any triangle not using it has both other values
at most1, so its sum is at most-2 and its square at least4. The one possible
exception has sum at most-1 and square at least1. Thus the four d0 triangles
through p contribute at least1+3*4=13; if no+2 vertex occurs they contribute
at least16. The same holds at q. Their disjoint families give at least26,
contradicting (6). This proves the exact conditional exclusion.

## Hand boundaries, overlap and limits

The ordinary integer edge inequality, Q positivity, Q^2=7Q and triangle
energy NN^T=A+7I are separate identities. Positive semidefiniteness alone
does not rule out42 edges on18 points. The final d0 energy is essential.

Two disjoint selected triple points of six actual triangles are compatible
with local triangle geometry: take three triangles through p and three
through q with their outer vertices private. They give six t1 values and
attain the added-edge bound6. Shared triple fans give t=(2,1,1,1,1,0),
added-edge bound7 and FIVE guaranteed S neighbors at each p,q. Their raw
pair norm18 fits a norm28 budget and is not rejected on that ground alone.
The wholly-S sixth triangle and remaining-vector sum supply the essential
extra norm. Neither control is asserted to extend to a target.

The integer outside vectors with sum2/norm4 have the two displayed scalar
patterns; they are not refuted by their scalar counts. The triangle-sum
budget rejects both, retaining any chosen locations of their nonzero values.
A negative d1 triangle sum cannot bypass s^2>=s. A shared d0 triangle at
p,q is charged once and already exceeds the budget, rather than being
double counted in two four-triangle families.

The hypergraph pairs on three base points would allow additional attached
triple points if distinct-intersection triples were permitted. The exact
lambda1 geometry is indispensable in the h<=2 lemma; linearity by itself
does not provide it. All arbitrary target edges are retained through the
inequalities until the actual e(S)=42 equality accounts for them.

The parity, fan, Q and incidence-energy ingredients overlap earlier work.
The new six-d2 boundary combines the fourfold-support split, the labelled
six-triangle concurrence lemma and a full ordinary triangle-sum budget.
A bounded comparison found earlier c1/b6 and R228 boundary arguments; their
different populations are preserved and not inherited here. No novelty,
coverage or target-level resolution follows. Other R227 populations remain
unresolved, and this CANDIDATE is outside the frozen publication cutoff.

The rejected unsealed V1 paper SHA8f2394b3932193fbf1dfb5f4d7c97383581fee03fc7519882ea88e2cfcb21d92
and veto receipt SHA61cad3090fa7c113d22b45155650e7808d24c7b42a0ad0ffa633bbed148d86ca
remain unchanged. V1 omitted the shared root's loss of one S neighbor and
also wrote84/82 rather than81/79 outside counts for S18. This V2 uses the
corrected shared branch and the exact99-point counts explicitly. No V1
approval exists or transfers to V2, and no theorem was marked REFUTED merely
because its former argument failed.

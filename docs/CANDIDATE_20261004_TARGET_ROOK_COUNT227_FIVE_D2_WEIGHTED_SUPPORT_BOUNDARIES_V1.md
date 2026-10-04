# Candidate: weighted-support boundaries for five d2 triangles at R227

This is a necessary-condition candidate, not an exclusion of the five-d2
population. Root proposed the weighted selected support; Structural derived
the exact outside concurrence cases and integral norm refinements. An earlier
message-only indicator-norm outline missed a scaling factor and was rejected
before a b5 paper or gate existed. Its correction receipt is preserved. No
mathematical program, enumeration, import, backend or worker ran. Independent
written verification is required; prior candidates remain unchanged.

## Exact statement

For every complete finite simple SRG(99,14,1,2), let R count actual induced
nine-vertex rook subsets once by their vertex sets and put d_T=6-r_T for
each actual triangle, where r_T counts the rooks containing it. Suppose
R=227, every d_T belongs to {0,1,2}, and exactly five triangles have d_T=2.
There are then fourteen d1 triangles. Let S be their vertex support, k the
number of points incident with four of them, and h the number of outside-S
points on d2 triangles. Define w_v as half the d1 incidence at v, zero
outside S, and E_w=sum_{u<v, A_uv=1} w_u w_v. Let e(S) be the ordinary
actual edge count of S.

Every positive d1 incidence is two or four. Exactly one of these necessary
cases occurs; none is asserted realizable:

* k0,h1: S has21 points. Three d2 triangles share the one outside point p,
  and the other two are wholly inside S. The actual edge count e(S) is51
  or52. In the former case deg_S(p) is6,7 or8; in the latter it is6 or7.
* k0,h2: S has21 points. The two outside points share one d2 triangle,
  the other four d2 triangles each contain one outside point, and
  46<=e(S)<=53.
* k1,h2: S has20 points. The same shared-triple pattern occurs, w is2 at
  its unique fourfold point and1 at every other S point, and E_w is54,
  55 or56. If that fourfold point lies on the d2 triangle joining the two
  outside points, then E_w is54 or55.

No other population, b5 itself or R227 is excluded. Maxd2 and exactly-five
are explicit hypotheses. No equitable profile, induced support, automorphism
or assumed existence of another codeword occurs.

## Target geometry, parity and the exact support parameters

Actual triangles are linear: they share at most one point. Three cannot
meet pairwise at three distinct points, since their intersection points
would give an edge a second triangle partner. Each point lies in seven
actual triangles. Two intersecting triangles determine at most one induced
rook by their cross pairs' fixed second common neighbors. Hence the local
defect graph at any point has degree d_T at its triangle node T.

The sum of local degrees is even. Under maxd2 the d1 family consequently
has even point incidence. D=sum d_T=6(231-R)=24, so b5 gives a14 and P19.
The positive point-fan bound, counting the2d_T distinct external outer
defect incidences of each root, is

    19>=3r_1+5r_2.                             (1)

Each external triangle meets at most one outer point of that whole fan,
by linearity and the forbidden distinct-intersection triple. Applying the
same injection to the selected fourteen-family alone gives14>=3r, where
r is selected multiplicity at its center. Its positive even multiplicities
are therefore2 or4. Their total incidence42 gives

    |S|=21-k,  sum w=21,  sum w^2=21+2k.

The fourteen selected actual triangles supply42 distinct actual edges.
No assumption is made about extra target edges on S.

## Outside points of five d2 triangles

At a d2 point outside S, no d1 is present. Degree two requires at least
three d2 roots, and (1) permits at most three. Each outside point is thus
an exact triple concurrence. Fix one. Its three roots are a base fan,
leaving two external d2 triangles. Any other triple point contains at most
one base root. A detached point would need three external roots, impossible.
An attached point uses both external roots; there cannot be two such points,
by linearity if they use the same base root or the forbidden three distinct
intersections if they use different ones. Hence h<=2.

Let t_i count outside-S points of d2 root i. The complete possibilities are

| h | t_i multiset | Unweighted d2 edges inside S, H |
|---|---|---:|
|0|0,0,0,0,0|15|
|1|1,1,1,0,0|9|
|2|2,1,1,1,1|4|

The h2 pattern has one shared root and uses all five roots. Its two outside
points each have five guaranteed distinct S neighbors, not six.

## The strictly positive weighted Gram removes all other k,h pairs

The target upper Gram Q=3I-A+J/9 is positive semidefinite and Q^2=7Q,
from A^2+A=12I+2J and row sum14. Put q=w^T Qw. Then

    q=112+6k-2E_w.

Among selected edges, each fourfold point has eight incident d1 edges.
For an edge with endpoint weights1 or2, its product is1 plus one for each
fourfold endpoint and one further if both endpoints are fourfold. If l
counts selected edges joining two fourfold points, their total weighted
edge contribution is42+8k+l. The d2 internal edges are distinct from the
selected ones and each has positive weight at least1. Thus

    q<=28-10k-2l-2H.                            (2)

In fact q is strictly positive. If it were zero, Q positivity would imply
Qw=0. Each coordinate is3w_v-(Aw)_v+21/9, which cannot vanish: the first
two terms are integers and21/9=7/3. This keeps the full-target integer
boundary and does not replace it with a fractional Gram realization.

For k>=2, even the smallest H4 makes the right side of (2) nonpositive.
For k1 and h0/1, H15/9 also makes it nonpositive. For k0,h0 it is-2.
Thus only k0,h1, k0,h2 and k1,h2 remain. This step does not reject the
remaining fourfold-support branch or silently drop its weight2 vertex.

## A correctly scaled integral norm and its residue floor

Set Y=3Qw. It is an ordinary integer vector:

    Y_v=9w_v-3(Aw)_v+7,
    sum Y=0,  ||Y||^2=63q.

Every entry is1 modulo3. For an integer y=1+3z,

    y^2+y-2=9z(z+1)>=0.

Consequently ||Y||^2>=198. If an entry is at most-8, its contribution to
the nonnegative excess y^2+y-2 is at least54. An entry at most-11 contributes
at least108. These literal constants can be checked at-8 and-11; for more
negative values the quadratic excess increases.

At h2 each outside point has five ordinary S neighbors, all of weight at
least1, so both Y entries are at most-8. Hence ||Y||^2>=198+108=306.

For k0, w=chi_S, E_w=e(S), and

    q=112-2e(S),  ||Y||^2=126(56-e(S)).

The h2 edge lower bound42+4=46 and norm floor306 give e(S)<=53, since
e54 would allow only252. For k1, equation (2) gives q<=10; q is an even
integer and306<=63q gives q>=6. Thus q is6,8 or10 and E_w=(118-q)/2
is56,55 or54. If its weight2 point is the shared root's only S point,
each outside weighted neighbor sum is at least2+4=6. Both Y entries are
then at most-11; norm>=198+216=414 gives q>=8 and E_w<=55.

## The k0,h1 edge and neighbor refinement

Here S has21 points, one outside point p has six guaranteed S neighbors,
and two d2 roots are wholly inside S. Write e(S)=51+z, z>=0, since the
42 selected edges and9 d2 edges are distinct. Let k_v=deg_S(v)-4 for v
in S. Its two selected triangles supply four distinct known neighbors,
so k_v is a nonnegative integer and

    sum_S k_v=18+2z,  Y_v=4-3k_v.

The two wholly-S d2 triangles force sum k_v(k_v-1)>=12. If they are
disjoint, each of their six vertices has k_v>=2. If they share a point,
that point has k_v>=4 and their other four vertices k_v>=2, giving at
least20 instead. Additional target edges cannot decrease these increments.
Therefore

    sum_S Y_v^2>=174-30z,
    sum_S Y_v=30-6z.

Write deg_S(p)=6+a, a>=0, so Y_p=-11-3a. The other77 outside entries
have sum -19+6z+3a. Applying y^2>=2-y individually to those entries and
adding the internal and p contributions gives

    ||Y||^2>=468-36z+63a+9a^2.

Its exact value is630-126z. Hence

    162-90z-63a-9a^2>=0.

For z>=2 this fails already at a0. Thus z0 or1. At z0 it permits only
a<=2; at z1 only a<=1. The case with z0,a2 and z1,a1 gives equality in
this scalar bound, not an asserted graph extension. These are precisely
the e51/52 and neighbor6..8/6..7 rows of the statement.

## Hand controls, failed outline and scope

The h2 pattern contains p,q on one root and four leaf roots; it is linear
and contains no forbidden distinct-intersection triangle if all other
points are private. Five S neighbors at each p,q are attainable locally.
Replacing that count with six would falsely strengthen the remaining
fourfold branch. The h1/two-wholly-S pattern also satisfies the local
incidence rules; neither is claimed to be a full target.

The residue-floor scalar vector of sixty-six entries1 and thirty-three
entries-2 has sum zero and norm198. An entry-8 adds54 to the residue excess;
an entry-11 adds108. The equality scalar boundaries in the h1 refinement
are retained, not converted into impossibility or uniform point profiles.

The rejected scaling outline is preserved in
acceleration/results/20261004_target_rook_count227_five_d2_scaling_outline_veto01.json,
SHA59638497433f0601414a2e335d4ae2f01bac5681c96b1535d4ca0b46a7ec3e5b.
It incorrectly used7 rather than63 for ||9Qchi_S||^2. This proof uses only
the exact Y=3Qw norm63q and does not inherit its rejected k1 exclusion.

Parity, fan, target Gram and residue identities overlap prior work. The
new necessary boundary is their explicit weighted-support case split and
integer edge/norm refinement. A bounded comparison is not a novelty claim.
Earlier no-d3/no-six/no-seven descendants are not logical premises; maxd2
is literal here. No target or R227 exclusion, scientific execution, census,
registration or publication-cutoff change is requested.

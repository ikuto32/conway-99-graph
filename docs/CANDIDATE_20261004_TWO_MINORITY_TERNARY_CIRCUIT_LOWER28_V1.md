# Candidate: two minority triangles require at least 28 circuit triangles

Discovery producer: `/root/checkpoint_audit`. CANDIDATE; a different author's
complete written derivation is pending. No mathematical program, enumeration,
solver, symbolic calculation or formal proof was executed for this paper.
Root proposed examining the two-minority case after its one-minority discovery;
the new incidence case split and outside-coordinate integer bound below were
derived by Checkpoint. Shared target premises and that research origin are
disclosed, and are not independent approval of this candidate.

Proposed claim `C-UNRESTRICTED-TARGET-TERNARY-TWO-MINORITY-CIRCUIT-LOWER28` r1:
for every hypothetical srg(99,14,1,2), a GF(3) circuit of distinct actual
triangles whose nonzero dependence, after global scaling, has exactly two
coefficients -1 and every other coefficient +1 has support size w >= 28.
If that dependence is unbalanced, meaning its coefficient sum is nonzero in
GF(3), then w >= 29.

This is a universal conditional circuit statement. It does not force such a
circuit in every target, classify or realize weight 28, bound circuit weight
above, or resolve target existence. The old two-minority unbalanced lower
bound 23 remains true and its evidence is unchanged. The proposed sole
`uses_result` dependency is `C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS` r1.

## Target geometry and the rank bound

Write S for the n used vertices, B for the union of the two minus triangles,
and M = S minus B. A target vertex has degree 14. Its neighbors induce a
matching of seven edges: for a neighbor u, the edge joining u to the vertex
has exactly one common neighbor. Thus every vertex belongs to exactly seven
actual triangles. Distinct actual triangles cannot share an edge and can
share at most one vertex. If a point has selected incidence d, its degree
in the selected edge union is exactly 2d; none of those edges is repeated.

At a point on m_v minus triangles, the dependence gives d_plus = m_v mod 3.
For a used point, with d = d_plus + m_v <= 7, the possibilities are:

| m_v | selected incidence d | selected degree |
| --- | --- | --- |
| 0 | 3 or 6 | 6 or 12 |
| 1 | 2 or 5 | 4 or 10 |
| 2 | 4 or 7 | 8 or 14 |

The incidence matrix of a circuit has rank w-1 over GF(3). Every column sums
to 3 = 0, so its all-ones left kernel gives rank at most n-1. Therefore
w <= n. This rank argument is over the used rows and requires no balancing
of the dependence's coefficients.

The two minus triangles are either disjoint or meet at exactly one point.
These possibilities exhaust their geometry.

## Disjoint minus triangles

Here B consists of two disjoint K3s, so |B| = 6. The actual edges between
these K3s form a matching. A point in one K3 adjacent to two points in the
other would be an additional common neighbor of their edge; its unique
common neighbor is already the third point of that other K3. The same
argument in both directions proves at most one cross edge at each endpoint,
and at most three in all. This applies to all actual edges, not only selected
edges.

Let c be the number of selected edges between the two K3s. Thus 0 <= c <= 3.
Let h count the B points with incidence 5 instead of 2, and let t count M
points with incidence 6 instead of 3. The incidence sum gives

    3w = 3n - 6 + 3h + 3t,
    n = w + 2 - h - t,
    h + t <= 2.

Every majority triangle contains at most one point of each minus K3, because
any edge within one of those K3s is already used by its minus triangle.
The six B points each require at least one majority incidence, so there are
at least three majority triangles and w >= 5.

There are 6+c selected edges within B. Its selected degree sum is 24+6h,
so the selected B-M edge count is 12+6h-2c. The selected M-M edge count is
therefore 3w-18-6h+c. If a is the number of additional actual induced M-M
edges, then a >= 0 and

    e(M) = 3w - 18 - 6h + c + a.

All actual additional B-B and B-M edges are permitted in the subsequent
arguments. They do not subtract selected M neighbors or any induced M edge.

In particular, when h=1 the exceptional B point has selected degree 10.
Exactly two selected neighbors are in its own minus K3 and at most one is
in the other minus K3. It consequently has at least seven selected M
neighbors. If c=0, it has exactly eight selected M neighbors. Its actual
number of M neighbors is at least these counts, even if additional B-B or
B-M edges are present.

## Minus triangles meeting at a point

Now |B| = 5. The common point lies on both minus triangles. The induced B
graph is exactly their six-edge bowtie. Edges between the two peripheral
pairs are impossible: all four peripheral points are neighbors of the common
point and its neighbor graph is a matching. Such an edge would give a
central-peripheral edge a second common neighbor.

No majority triangle can contain two B points. Their possible actual edges
are precisely the bowtie edges, each already in a minus triangle. Let h
count B points with incidence increased by 3, and t count M points with
incidence 6 instead of 3. The baseline incidences are 4 at the common point,
2 at each of four peripheral points, and 3 on M. Hence

    3w = 3n - 3 + 3h + 3t,
    n = w + 1 - h - t,
    h + t <= 1.

At least six majority incidences on B are necessary, each on a different
majority triangle, so w >= 8. When h=t=0 there are 12 selected B-M edges
and 3w-18 selected M-M edges. A point of M can be adjacent to at most one
point of each minus triangle, by the same unique-common-neighbor argument
used for a K3 above. Thus these 12 edges require |M| >= 6. In this baseline
case |M| = w-4, so w >= 10. An adjacency to the common point may impose
additional restrictions, but none is required for this bound.

## Exact inside and outside Gram identities

The target Gram premise gives G = 27I - 9A + J and G^2 = 63G. For any actual
vertex set X of size m and with e = e(X) actual induced edges, put

    F_X = chi_X^T G chi_X = m^2 + 27m - 18e >= 0,
    ||G chi_X||^2 = 63 F_X.

For v in X the coordinate is m+27-9deg_X(v). For v outside X it is
m-9k_v, where k_v = deg_X(v) is an integer between 0 and 14. Write
N=99-m and K=sum(outside X) k_v=14m-2e. For every integer k,

    (m-9k)^2 = (405-18m)k + m^2-486 + 81(k-2)(k-3)
             >= (405-18m)k + m^2-486.

The last product is nonnegative at every integer k: the two consecutive
roots are 2 and 3, with no integer strictly between them. Consequently

    63F_X >= sum(outside X) (m-9k_v)^2
           >= (405-18m)K + (m^2-486)N.

This is a lower bound on actual outside coordinates of the complete target
norm. It does not presume any outside realization or assign degrees to
individual unused vertices. When one particular outside point has k >= 7,
its retained remainder is at least 81(7-2)(7-3)=1620. When it has k >= 8,
the remainder is at least 2430. The product increases on integers k >= 7.
All other remainders remain nonnegative. These strengthened bounds apply
to the exceptional B point when X=M; full target degree 14 gives k <= 14.

## All n=w cases are impossible through w=27

The selected union has exactly 3w edges, and every actual extra edge is
retained in e(S)=3w+E with E >= 0. For n=w,

    F_S = w(w-27) - 18E.

This is negative for the applicable positive weights w <= 26. At w=27,
positivity forces E=0 and F_S=0. In the disjoint case h+t=2, so at most two
of the six B points have high incidence. At least four still have selected
degree 4. In the meeting case h+t=1, at least three peripheral points still
have selected degree 4. With no extra edges, such a point's coordinate of
G chi_S is 27+27-9*4=18. A nonzero coordinate contradicts the exact norm
63F_S=0. These arguments cover every n=w pattern without enumerating it.

## Maximal support size in either geometry

Consider the disjoint case n=w+2, h=t=0, or the meeting case n=w+1,
h=t=0. In both, m=|M|=w-4. In the disjoint case put d=c+a; in the meeting
case put d=a. The selected edge counts derived above yield

    e(M) = 3w-18+d,
    F_M = w^2-35w+232-18d.

In the disjoint case the selected B-M count 12-2c is at most 2m, because
each M point can meet at most one point of each minus K3. Thus c >= 10-w.
Together with c<=3 this requires w>=7. At w=7, c>=3 and F_M<=36-54<0;
at w=8, c>=2 and F_M<=16-36<0. The polynomial w^2-35w+232 has value -2
at both 9 and 26. Convexity puts it below the negative endpoint chord
throughout 9<=w<=26. In the meeting case w>=10, so that same negative
interval covers all its weights through 26.

At w=27 the polynomial equals 16. Since d is a nonnegative integer,
F_M>=0 forces d=0. Thus m=23, e(M)=63 and F_M=16. The exact outside
parameters are N=76 and K=14*23-2*63=196. The integer outside bound gives

    sum(outside M) (23-9k_v)^2 >= -9*196+43*76 = 1504,
    63 F_M = 1008.

This contradiction excludes w=27 in both maximal-support cases. It keeps
all outside points, including B and every unused target point. No condition
on additional B-M edges was discarded.

## Disjoint intermediate support size n=w+1

The only remaining possibility is the disjoint geometry with h+t=1.
For this support size, its actual induced edge count gives

    F_S <= (w+1)^2+27(w+1)-54w = w^2-25w+28.

At w=5 and w=23 this polynomial is respectively -72 and -18. Its convex
negative endpoint chord excludes 5<=w<=23. It remains to cover w=24,25,26,27.

If h=0,t=1, then m=w-5, and with d=c+a>=0,

    e(M) = 3w-18+d,
    F_M = w^2-37w+214-18d.

The polynomial values at w=24 and w=27 are -98 and -56. Convexity excludes
the full interval 24<=w<=27, even before subtracting 18d.

If h=1,t=0, m=w-5 and

    e(M) = 3w-24+d,
    F_M = w^2-37w+322-18d,
    d=c+a>=0.

The exceptional B point is outside M and has k>=7. Using its remainder
1620, the complete outside lower bounds and target norm budgets are:

| w | m | N | K | F_M | outside lower bound including 1620 | 63F_M |
| --- | --- | --- | --- | --- | --- | --- |
| 24 | 19 | 80 | 170-2d | 10-18d | 2330-126d | 630-1134d |
| 25 | 20 | 79 | 178-2d | 22-18d | 2836-90d | 1386-1134d |
| 26 | 21 | 78 | 186-2d | 36-18d | 3132-54d | 2268-1134d |
| 27 | 22 | 77 | 194-2d | 52-18d | 3212-18d | 3276-1134d |

For w=24,25,26, subtracting the rightmost column from the preceding bound
gives respectively 1700+1008d, 1450+1044d and 864+1080d. Each is positive
for every d>=0. At w=27 the difference is -64+1116d, positive when d>=1.
For the only residual case w=27,d=0, both c=0 and a=0. The exceptional B
point then has k>=8, so its remainder is at least 2430 instead of 1620.
The outside norm is at least 1592+2430=4022, greater than 63F_M=3276.
This covers every nonnegative c,a and all possible additional actual
edges between B and M or between the two minus triangles.

## Conclusion and exact review boundary

The rank/incidence identities allowed exactly the cases n=w,w+1,w+2 in
the disjoint geometry and n=w,w+1 in the meeting geometry. Each has now
been contradicted for every possible w<=27. The candidate conclusion is
w>=28. The dependence's coefficient sum is (w-2)-2=w-4 in GF(3). Weight
28 gives coefficient sum 24=0, so the additional unbalanced hypothesis
forces w>=29.

Independent review must reconstruct the selected-edge splits in both
geometries, both rank/incidence classifications, the absence of bowtie
cross edges, the matching bound between disjoint K3s, the exceptional
point's seven/eight selected M neighbors, and the integer outside norm
identity with its full 99-point cut count. In particular, attempt to
falsify the use of c as a selected-edge count when extra B-B edges exist,
and the retained positive remainder when extra B-M edges exist. The
proof makes no connectivity, symmetry, induced-selected-union or no-extra-edge
assumption. No actual circuit or complete graph is supplied.

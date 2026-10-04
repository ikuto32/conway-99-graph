# A seventeen-point unbalanced twelve-triangle circuit

Status: **CANDIDATE**, paper discovery by `/root/structural`, prepared
2026-10-03T13:16:43+00:00; context
`d0c0dd7db0d3de420b1d718b59122b069df01107`, observed ledger SHA256
`a0ed6dfb9716266e44dd8cdbef00620266190fa1bce0852a11bbabbf8d09416e`.
Zero mathematical execution, enumerated fixtures, formal checking or external
review. Independent derivation is required; novelty unknown. No ledger/index
or historical evidence changes.

This is a different local configuration from the excluded sixteen-point core.
It gives a genuine twelve-column unbalanced GF(3) circuit with adjacent CN=1,
nonadjacent CN<=2, and target eigenvalue interlacing caps. Its extension to a
99-vertex target is **UNKNOWN**. The two-anchor capacity test described below
does not veto it. No target embedding, forced occurrence or nonexistence
claim follows.

## 1. Literal points and triangles

Use points a=0,b=1,x=2; u_i=3+i,v_i=7+i,w_i=11+i for i=0,1,2,3;
and h_0=15,h_1=16. Put alpha(i)=i XOR 1, beta(i)=i XOR 2 and gamma(i)=i XOR 3.
Let epsilon(i)=0 for i in {0,3} and 1 for i in {1,2}.
The seven negative and five positive columns are

| Sign | Actual triples in the proposed point graph |
| --- | --- |
| - | (0,1,2), (0,3,4), (0,5,6), (1,7,9), (1,8,10), (15,11,14), (16,12,13) |
| + | (2,15,16), (3,7,11), (4,8,12), (5,9,13), (6,10,14) |

Let G contain precisely the edges of these triples and B_0 their incidence
matrix. The displayed neighborhoods are

```
N(a) = {b,x,u_0,u_1,u_2,u_3},
N(b) = {a,x,v_0,v_1,v_2,v_3},
N(x) = {a,b,h_0,h_1},
N(u_i) = {a,u_alpha(i),v_i,w_i},
N(v_i) = {b,v_beta(i),u_i,w_i},
N(w_i) = {h_epsilon(i),w_gamma(i),u_i,v_i},
N(h_s) = {x,h_(1-s),w_i:epsilon(i)=s}.
```

The two a,b degrees are six and the other fifteen degrees four. There are
36 edges and twelve prescribed actual triangles. All triples are linear.

## 2. Complete pair-type checks on paper

Direct neighborhood intersections give the following exhaustive counts.

* The a,b and a,x and b,x edges have CN one. Edges a,u_i and b,v_i have
  respectively their paired u or v point as unique common neighbor.
* Nonedges a,v_i and b,u_i have CN two. Pairs a,w_i and b,w_i have CN one,
  as do a,h_s and b,h_s.
* Every x,u_i and x,v_i and x,w_i nonedge has CN one. The x,h_s edges have
  the other h point as their unique common neighbor.
* For different indices, u_i,u_j have CN one (a), and v_i,v_j have CN one (b).
  The corresponding negative-pair edges also have precisely this CN.
* The w_i,w_gamma(i) edges have their h point as unique CN. Other different
  w_i,w_j pairs have CN zero.
* The u_i,v_i edge has unique CN w_i. For j!=i the CN of u_i,v_j is
  `[j=alpha(i)]+[j=beta(i)]`, at most one here because alpha!=beta.
* The u_i,w_i edge has unique CN v_i. For j!=i the CN of u_i,w_j is
  `[j=alpha(i)]+[j=gamma(i)]`, again at most one. The v_i,w_j version uses
  beta and gamma. Here brackets denote the integer indicator 0 or 1.
* For either s, h_s,u_i and h_s,v_i are nonedges, with CN one when
  epsilon(i)=s and zero otherwise. For h_s,w_i the CN is one in both cases:
  if epsilon(i)=s it is the paired w point on the negative triangle edge;
  otherwise it is h_(1-s) on the nonedge. The h_0,h_1 edge has CN x only.

Thus every adjacent pair has exactly one common neighbor, and all nonadjacent
pairs at most two. The twelve listed triples exhaust the actual triangles,
because every edge already has its unique prescribed completion. The graph
is not regular fourteen and many nonedges have CN zero or one.

## 3. The exact unbalanced circuit

Give each of the seven negative columns coefficient -1 and each of the five
positive columns coefficient +1. The integer incidence sum is -3 on a,b and
zero on every other point. Consequently B_0 z=0 over GF(3), but sum(z)=-2=1.

Every other point has selected degree two and joins one negative to one
positive column. The graph of these column links is connected: the negative
(a,b,x) column links to the positive (x,h_0,h_1); that positive links to both
negative h triangles; those link to all four positive (u_i,v_i,w_i) columns,
which link to every remaining negative a or b triangle. Thus the degree-two
equations force every dependence to be a scalar multiple of the displayed z.
The a,b equations impose no additional restriction, since each sums three
equal negative coefficients over GF(3). The kernel on these columns is
one-dimensional, all coordinates of a nonzero dependence are nonzero, and
no proper subset is dependent. It is a genuine GF(3) circuit, not merely an
unbalanced sum of smaller circuits.

## 4. Exact interlacing checks

The index translations of the four-element group act on the u,v,w coordinates
and interchange h_0,h_1 when they move between gamma cosets. These are
symmetries of this explicitly defined local graph, not assumptions about a
target. Decompose its real adjacency into the four index characters.

For the constant character the a,b and u,v antisymmetric part is
`[[-1,4],[1,0]]`, with eigenvalues (-1+sqrt(17))/2 and (-1-sqrt(17))/2,
both less than three. The remaining constant part has quotient, in coordinates
(a=b, x, u=v, h_0=h_1, w),

```
[1,1,4,0,0]
[2,0,0,2,0]
[1,0,2,0,1]
[0,1,0,1,2]
[0,0,2,1,1].
```

Its coordinate class sizes are (2,1,8,2,4). Multiplying (Q-3I) by these
diagonal class sizes makes a symmetric matrix. Eliminate the u=v coordinate,
whose pivot is -8. The remaining matrix is

```
[ 4, 2, 0, 8]
[ 2,-3, 2, 0]
[ 0, 2,-4, 4]
[ 8, 0, 4, 0].
```

Eliminating the first pivot 4 leaves

```
[-4, 2, -4]
[ 2,-4,  4]
[-4, 4,-16].
```

Its leading principal determinants are -4,12,-128, so it is negative
definite. The quotient therefore has exactly one eigenvalue greater than
three and four less, by congruence/inertia; no zero pivot is suppressed.

For the unique nonconstant character with gamma-value +1, alpha and beta
both have value -1. The u,v antisymmetric eigenvalue is -2; the symmetric
three-coordinate block in (u=v,w,h) is
`[[0,1,0],[2,1,1],[0,2,-1]]`. Its polynomial is
`(t+2)*(t^2-2t-1)`, giving -2 and 1+/-sqrt(2), all less than three.

For each of the other two characters, gamma-value is -1 and alpha,beta
have opposite signs. The block, after a possible u,v interchange, is
`[[1,1,1],[1,-1,1],[1,1,-1]]`, with eigenvalues 2,-1,-2.
These blocks account for all seventeen dimensions. Thus lambda_2<3.

Also A_G=B_0 B_0^T-D with D having diagonal entries two or three, so
A_G+3I is positive semidefinite. It is positive definite here: a vector in
its kernel must vanish on all degree-two points, then the a-only and b-only
negative columns force its remaining two coordinates zero. Hence
lambda_min>-3. The core passes both target principal-submatrix caps.

## 5. The two-anchor completion budget remains inconclusive

If the core were induced in a target, S would have n=17, with selected
point degrees three at a,b and two elsewhere. The exact fulltarget budgets
would be V=14*17-6*12=166 and
P=17*16-2*(2*9+15*4)=116. The pair {a,b} is saturated inside S.
Their two outside neighborhoods would contain T=16 different vertices.
Each has common-neighbor deficit one to all six free points w_i,h_0,h_1
and none to the remaining points, giving R=12.

The general anchor inequality then uses N=66,E=138 and P-R=104.
For every nonnegative integer a its right-hand side is
`138a-33a(a+1)`, whose maximum at integer a is 78, achieved at a=2.
Thus this particular two-anchor necessary test passes. No claim is made about
all possible anchor sets, other completion restrictions, or extra graph edges.

This supplies a concrete smallest-size candidate after the proposed
unbalanced-word lower bound twelve, while showing why vetoing the separate
sixteen-point twelve-line circuit is not an exhaustive twelve-word argument.
Full target completion and any universal circuit obstruction remain unknown.

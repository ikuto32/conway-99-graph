# A twelve-line ternary dependency: local caps and a target completion obstruction

Status: **CANDIDATE**, paper derivation by `/root/structural`, prepared
2026-10-03T12:31:49+00:00. Source context:
`d0c0dd7db0d3de420b1d718b59122b069df01107`; observed ledger SHA256
`a0ed6dfb9716266e44dd8cdbef00620266190fa1bce0852a11bbabbf8d09416e`.
No mathematical computation, enumeration, fixtures, formal checking, external
review or independent approval was performed for this note. Novelty is unknown.
No ledger, index, historical evidence or current notice is changed.

Two different statements are proposed here. First, adjacent-pair CN=1 and the
nonadjacent CN<=2 cap do not force every ternary triangle dependence to have
coefficient sum zero. Second, the particular twelve-line configuration below
cannot occur, even non-induced, in a 99-vertex degree-14 graph with adjacent
CN=1 and nonadjacent CN=2. Neither statement forces this configuration to occur
in a target. They do not resolve existence of the Conway-99 graph.

## 1. Literal configuration and the proposed statements

Indices in this note are modulo four. Use sixteen distinct points
`c_i, x_i, y_i, z_i`, with numeric labels respectively `i, 4+i, 8+i, 12+i`.
The twelve triples are

| Family | Triples with numeric labels |
| --- | --- |
| E_i={c_i,c_(i+1),x_i} | (0,1,4), (1,2,5), (2,3,6), (3,0,7) |
| V_i={c_i,y_i,z_i} | (0,8,12), (1,9,13), (2,10,14), (3,11,15) |
| T_i={x_i,y_(i+2),z_(i+3)} | (4,10,15), (5,11,12), (6,8,13), (7,9,14) |

Let G be their point graph: two points are adjacent precisely when one of these
triples contains them. Let B_0 be the 16 by 12 binary incidence matrix, with
columns ordered E_0,...,E_3,V_0,...,V_3,T_0,...,T_3.

**Proposed finite-geometry statement.** G is simple, these twelve triples are
exactly its actual triangles, every adjacent pair has one common neighbor,
and every nonadjacent pair has at most two common neighbors. The vector
`z=(-1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1)` satisfies B_0 z=0 over GF(3), but its
coefficient sum is -4=2 over GF(3). Its point graph also passes the necessary
target eigenvalue interlacing caps lambda_2<=3 and lambda_min>=-4.

**Proposed target-specific statement.** No simple degree-14 graph on 99 vertices
with adjacent CN=1 and nonadjacent CN=2 contains these twelve triples on
sixteen distinct vertices. This allows additional graph edges among the
sixteen vertices; no induced-copy hypothesis is used.

## 2. Exact topology and the ternary word

The point neighborhoods in G are

```
N(c_i) = {c_(i-1),c_(i+1),x_(i-1),x_i,y_i,z_i},
N(x_i) = {c_i,c_(i+1),y_(i+2),z_(i+3)},
N(y_i) = {c_i,x_(i+2),z_i,z_(i+1)},
N(z_i) = {c_i,x_(i+1),y_i,y_(i-1)}.
```

Thus the four c-points have degree six and the other twelve points degree four.
There are 36 edges. Each point belongs to three or two specified triples,
respectively. The triples are linear: no pair of points belongs to two of them.

For mixed point types, the following lists give the common-neighbor count for
the pair with indices i and i+delta, in delta order 0,1,2,3. The second list
gives exactly the deltas that are adjacent.

| Types | CN for delta=0,1,2,3 | Adjacent deltas |
| --- | --- | --- |
| c,x | 1,2,2,1 | 0,3 |
| c,y | 1,2,1,2 | 0 |
| c,z | 1,2,1,2 | 0 |
| x,y | 1,1,1,1 | 2 |
| x,z | 1,1,1,1 | 3 |
| y,z | 1,1,0,0 | 0,1 |

For equal point types, exclude delta=0. The lists for delta=1,2,3 are
`c,c: 1,2,1`, `x,x: 1,0,1`, `y,y: 1,0,1`, and `z,z: 1,0,1`.
Only c,c at deltas 1 and 3 is adjacent. These lists follow by direct
intersection of the displayed neighborhoods; they specify every unordered
pair, rather than a sampled class of pairs. In particular every edge has
exactly the third point of its prescribed triple as its common neighbor.
Every graph triangle contains an edge, so there are no additional triangles.

Give the E and V columns coefficient -1 and the T columns coefficient +1.
Every c_i then has integer incidence sum -3; every x_i,y_i,z_i has integer
incidence sum zero. Hence B_0 z=0 over GF(3), whereas sum(z)=-4 is nonzero.
This also forbids an affine point assignment B_0^T u=1: its inner product
with z would equate zero to -4 over GF(3).

The graph is not degree 14, has sixteen vertices, and has nonadjacent pairs
with CN zero or one. It is a counterexample only to a cap-only balance
inference. It is not a target or a counterexample to a target theorem.

## 3. Necessary target interlacing caps do not detect this core

This optional exact algebra records another necessary test that the local
core passes; it is not an extension proof. The order-four index shift commutes
with the adjacency matrix. On shift eigenvalue zeta in {1,-1,i,-i}, its block
in coordinates (c,x,y,z) is

```
[ zeta+zeta^-1, 1+zeta^-1, 1,       1        ]
[ 1+zeta,      0,          zeta^2,  zeta^3   ]
[ 1,           zeta^-2,    0,       1+zeta   ]
[ 1,           zeta^-3,    1+zeta^-1,0        ].
```

For zeta=1 the antisymmetric y,z vector has eigenvalue -2. The remaining
three eigenvalues have polynomial f(t)=t^3-4t^2-4t+4. Its three roots lie
in (-2,-1), (0,1), and (4,5): the endpoint signs give these disjoint intervals,
and the block is real symmetric. For zeta=-1, splitting the y,z sum and
difference gives eigenvalues -1+sqrt(3), -1-sqrt(3), sqrt(2), -sqrt(2).

For zeta=i, the Hermitian block has trace zero, trace of its square 16,
trace of its cube zero, and determinant 14. To make the determinant explicit,
the three paired-edge products sum to 4+1+1=6 and the real parts of the
three four-cycle products are -2,-2,0, giving 6-2(-4)=14. Its polynomial is
t^4-8t^2+14, with roots +/-sqrt(4+sqrt(2)) and +/-sqrt(4-sqrt(2)).
The conjugate zeta=-i block has the same roots.

Consequently exactly one eigenvalue exceeds three, and all eigenvalues exceed
-3. In particular lambda_2<3 and lambda_min>-3. The lower bound also follows
without Fourier algebra: A_G=B_0 B_0^T-D, where D has diagonal entries two
or three, so A_G+3I is positive semidefinite. These are compatible with the
principal-submatrix interlacing bounds from target spectrum
14^1,3^54,(-4)^44. They do not establish any other embedding condition.

## 4. Exhausting possible extra edges in a target embedding

Suppose, for contradiction, a target graph contains the twelve triples.
Write S for the sixteen vertices and H for the actual graph induced on S.
The graph G is a subgraph of H, but H is not assumed equal to G.

An extra edge uv cannot join a nonedge of G having a common neighbor w in G.
The existing edge uw already has a prescribed triangle completion different
from v. Adding uv would give it the second common neighbor v, violating
adjacent CN=1. Thus extra edges can only join the fourteen CN-zero pairs
listed in section 2:

* the two pairs of opposite x-points;
* the two pairs of opposite y-points and the two pairs of opposite z-points;
* the eight y_i,z_j pairs with j-i equal to two or three.

The edge x_i x_(i+2) is forbidden. The pair c_i,x_(i+2) already has two
common neighbors in G; this extra edge adds x_i as a third common neighbor.
For an extra edge y_i z_(i-1), the pair c_i,z_(i-1) similarly has its two
G-common neighbors plus y_i. These two forbidden types cannot instead
become adjacent, by the preceding common-neighbor argument.

Only edges between opposite-center leaf pairs remain. Put
L_i={y_i,z_i}. They lie in the two complete bipartite possibilities
L_0--L_2 and L_1--L_3. Within each possibility the extra edges must be a
matching: if one leaf were joined to both opposite leaves, their existing
local edge would acquire this leaf as a second common neighbor. Let f be
the number of actual extra edges, so 0<=f<=4. Every leaf is incident to
at most one extra edge. The four c degrees and the four x degrees remain
six and four; 2f leaf degrees increase from four to five.

No additional assumption about the completion of an extra edge is made.
In particular its unique triangle completion may lie outside S.

## 5. Full common-neighbor completion budget

There are 83 vertices outside S. For an outside vertex v, let t_v be its
number of neighbors in S. The total cut from S is

```
sum_v t_v = 4*(14-6)+12*(14-4)-2f = 152-2f.
```

The sum of internal unordered two-walks is
sum_(s in S) binom(deg_H(s),2)=4*15+12*6+8f=132+8f.
There are 36+f adjacent pairs within S and 120-(36+f) nonadjacent pairs.
The target total CN on these pairs is
(36+f)+2*(84-f)=204-f. Subtracting the internal two-walks therefore gives
the exact outside pair budget

```
sum_v binom(t_v,2) = 72-9f.
```

This formula includes the outside completion of any extra adjacent edge;
it does not incorrectly assign zero outside CN to that edge.

## 6. The four centers exhaust too much outside capacity

No outside vertex is adjacent to two c-points. Neighboring c-points already
have their unique G-triangle completion, and opposite c-points already
have their two G-common neighbors. Each c_i has exactly eight outside
neighbors, so the four centers are adjacent to 32 distinct outside vertices.

If an outside vertex is adjacent to c_i, it cannot also be adjacent to any
x-point: every c_i,x_j pair is already an edge completed inside G or a
nonedge with CN two inside G. Nor can it be adjacent to a local leaf or
a leaf at a neighboring center, for the same completed-edge/CN-two reason.
Its only possible additional S-neighbor is one of the two opposite leaves
in L_(i+2). It cannot take both, because those two leaves form a completed
edge in G.

Let f_i be the number of extra edges between L_i and L_(i+2). Then
sum_i f_i=2f. The internal common-neighbor count between c_i and each
opposite leaf is one, plus one exactly when that leaf is incident to an
extra edge from L_i. Thus exactly 2-f_i opposite leaves require one
outside common neighbor with c_i; the other opposite leaves require none.
The allowed leaves must be realized at different outside vertices. Among
the 32 center-neighbors, exactly

```
a = sum_i (2-f_i) = 8-2f
```

have t_v=2, and the remaining 32-a have t_v=1. Their cut contribution is
32+a=40-2f and their pair contribution is a=8-2f.

The remaining 51 outside vertices consequently satisfy

```
sum t_v = (152-2f)-(40-2f) = 112,
sum binom(t_v,2) = (72-9f)-(8-2f) = 64-7f.
```

For every nonnegative integer t,

```
binom(t,2)-(2t-3) = (t-2)*(t-3)/2 >= 0.
```

The inequality includes t=0 and t=1. Summing it over these 51 vertices
requires sum binom(t_v,2)>=2*112-3*51=71. But 64-7f<=64<71.
This contradiction proves the proposed target-specific configuration veto.

## 7. Limits and the next independently checkable question

The argument vetoes the specified configuration even with arbitrary extra
edges permitted by the target assumptions. It neither classifies all
twelve-triangle ternary dependencies nor proves that a target contains one.
The lower-weight circuit discussion and the earlier 15-point/11-line
lambda1-only example were exploratory context and are not premises here.

The finite graph G defeats any argument using only linear actual triangle
geometry, adjacent CN=1, the nonadjacent CN<=2 cap, or the stated interlacing
caps to force all ternary dependencies balanced. The completion proof shows
where exact global degree and CN saturation add information. A promising
next question is to derive analogous cut/pair budgets for the support of
an arbitrary minimal unbalanced right-kernel word; it needs its own exact
classification or inequality, and a separate independent derivation.

This note preserves the known scope limits: binary incidence can have zero
left kernel; the rejected generic rank<=72 step is not a premise; and the
existing degree-14 lambda1 non-target GF3 rank-98 fixture does not decide the
target-specific right-kernel geometry. No comparison of ranks over different
fields is used. Historical prime-seven full-row-rank and reduced ternary Gram
algebra are not presented as new results.

# Triangle-flag union formula for the rooted fibre count

Assume that `G` is an `srg(99,14,1,2)`.  This note gives a root-free
interpretation of the diagonal term in

```
E0(r)=S(r)+D(r)
```

and rewrites `E0(r)` as the complement of the support of one row of a
triangle-flag matrix.  It is an identity, not yet a lower bound on `E0`.

## 1. Triangles and the two-cross-edge flag relation

Every edge is in one triangle.  There are 231 triangles, and every vertex
is in seven.  For a triangle `T`, let `a_i(T)` be the number of disjoint
triangles joined to `T` by exactly `i` cross edges.  Cross edges form a
matching.  The standard two moments give, with `q(T)=12-a_3(T)`,

```
a_2(T)=3q(T),
2 n3 = 3 sum_T q(T),
n3+3P=4158,                                             (1)
```

where `n3` counts unordered triangle pairs with two cross edges and `P`
counts induced triangular prisms.

A triangle flag is a pair `(T,t)` with `t in T`; there are `693` flags.
Define the symmetric zero-one matrix `X` on flags by

```
X[(T,t),(U,u)]=1
```

exactly when `T,U` are disjoint, have two cross edges, and `t,u` are the
unmatched vertices of that two-edge matching.

For fixed `(T,t)`, write `T\{t}={x,z}`.  Choose an order of `x,z` and one of
the twelve neighbours `y` of `x` outside `T`.  The nonedge `yz` has `x` and
one other common neighbour `w`; the triangle on `yw` supplies a pair of
cross edges.  Reversing `x,z` counts each result twice.  Thus there are 12
such cross-edge pairs with `t` omitted.  A two-cross-edge partner unmatched
at `t` contributes once, and every prism partner contributes once.  Hence

```
deg_X(T,t)=12-a_3(T)=q(T).                                (2)
```

In particular `X` has `2n3` entries equal to one.

Let `M` be the integral triangle projector from the side-bound proof.  On
disjoint triangle pairs `M[T,U]=1-r(T,U)`, where `r` is the cross-edge
count; its diagonal is 4 and it vanishes on intersecting pairs.  Therefore
the triangle-level two-cross-edge adjacency matrix is exactly

```
K2=(M o M o M + M o M - 2M)/2 - 36I.                    (3)
```

If `C` is flag-to-triangle incidence, then `C^T X C=K2`.  Thus `X` is the
unmatched-endpoint refinement of a matrix given by Schur powers of `M`.

## 2. Collapse the source flag to its graph vertex

Let `F` be the `693 x 99` flag-to-vertex incidence matrix,

```
F[(T,t),r]=1 iff t=r,
```

and put

```
Y=F^T X.                                                  (4)
```

For a root `r` and target flag `(U,u)`, `Y[r,(U,u)]` counts the triangles
`T` through `r` for which the two-cross-edge matching from `T` to `U`
leaves `r,u` unmatched.

Every vertex of `U\{u}` has exactly two neighbours in `N(r)`.  Distinct
triangles through `r` use distinct matched pairs in `N(r)`.  Consequently

```
Y[r,(U,u)] is in {0,1,2}.                                 (5)
```

Its row and column sums are

```
sum_beta Y[r,beta] = sum_(T containing r) q(T) = 84-S(r), (6)
sum_r Y[r,(U,u)] = q(U).                                  (7)
```

For (6), a prism containing `r` has a unique triangle through `r`, so
`sum_(T containing r) a_3(T)` is the number of prisms containing `r`, which
is exactly `S(r)` by the rooted side/prism bijection.

## 3. Diagonals are precisely the entries equal to two

Suppose `Y[r,(U,u)]=2`, arising from distinct triangles `T,T'` through `r`.
The edge on the other two vertices `U\{u}` has one endpoint adjacent to each
non-root vertex of both `T` and `T'`.  Relative to `r`, its endpoints
therefore lie in the same support fibre and choose opposite members in both
root-neighbour pairs: it is a fibre diagonal.

Conversely, complete a fibre diagonal edge to its unique triangle `U` and
call the third vertex `u`.  The two root triangles defining its support are
two `X`-neighbours of `(U,u)` with the same unmatched root `r`.  Thus

```
D(r)=sum_beta binom(Y[r,beta],2).                          (8)
```

Equivalently, a marked pair `(r, diagonal edge)` is an induced seven-vertex
graph `H_delta`: two triangles `r-a0-a1` and `r-b0-b1`, the four edges
`x-a0,x-b0,y-a1,y-b1`, and the edge `xy`, with no other edges.  Its induced
degree sequence is `(4,3,3,3,3,3,3)`, so `r` is intrinsic and the
correspondence has multiplicity one.  In the standard upper-triangle bit
encoding its canonical mask is `120568`.

## 4. The support identity and global moments

Let

```
Z = 1_(Y>0) = (3Y-Y o Y)/2,                               (9)
```

where the second equality follows entrywise from (5).  If a row of `Y` has
`a` entries equal to one and `b` entries equal to two, then (6) and (8) give
`a+2b=84-S(r)` and `b=D(r)`.  Hence

```
E0(r)=84-(a+b)=84-|supp(Y[r,*])|=84-(Z1)_r.              (10)
```

This is the desired pointwise bridge.  Globally,

```
sum_r D(r) = (||Y||_F^2-2n3)/2,                          (11)
sum_r E0(r) = 8316-3n3+||Y||_F^2/2.                     (12)
```

If `z11` denotes the order-seven count in the existing deck convention for
which `sum D=n3-z11/4`, then (12) is the independently obtained formula

```
sum_r E0(r)=8316-n3-z11/4.                               (13)
```

The exact second-moment form is

```
sum_r E0(r)^2
 = 99*84^2 - 168*1^T Z 1 + 1^T Z Z^T 1                 (14)
 = 698544 - 167 H + 2 K,
H=sum_r |supp(Y[r,*])|=2n3-sum_r D(r),
K=sum_r binom(|supp(Y[r,*])|,2).                         (15)
```

Thus the only new term needed beyond the known first moments is the count
`K` of unordered pairs of distinct target flags hit by the same seven-flag
root block.  It is a union-of-two-marks motif count.

Two further fixed aggregate identities are

```
(YY^T)[r,r]=84-S(r)+2D(r),                               (16)
1^T YY^T 1 = 3 sum_T q(T)^2,                             (17)
sum_(r<s) (YY^T)[r,s]
 = (3 sum_T q(T)^2-2n3-2 sum_r D(r))/2.                 (18)
```

Equation (17) uses the column sum (7), repeated on the three flags of each
triangle.  The present identities fix the total off-diagonal mass in
`YY^T`; they do not by themselves fix its adjacent/nonadjacent split.

## 5. What a lower bound must prove

By (10), a universal bound `E0(r)>=L` is exactly the expansion bound

```
|union_(T containing r) N_X(T,r)| <= 84-L.               (19)
```

In particular `E0(r)>=73` is equivalent to a support bound of 11 on every
row of `Y`.  Positivity of `YY^T` only controls Euclidean row norms; a new
support-sensitive inequality for the Schur-defined lift `X`, or a bound on
the pair count `K`, is still required.  No such inequality is claimed here.


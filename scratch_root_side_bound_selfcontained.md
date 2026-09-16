# Self-contained root-side bound

This note removes the external `n3 >= 708` premise from the rooted side
argument.  It derives the weaker bound `n3 >= 705` directly from the SRG
axioms.  That weaker endpoint is already enough to prove that some root `r`
satisfies

```
S(r) <= 69,
```

where `S(r)` counts the four **side** pairs, not the two diagonals, in each of
the 21 four-vertex support fibres at `r`.

The Schur-projector idea and the notation `n3` follow the public Wave 20
report, but every numerical step needed here is reproduced below.  The small
standard-library audit `scratch_root_side_bound_selfcontained.py` checks all
displayed spectra, row moments, congruences, divisibility roundings, and final
pigeonhole arithmetic.

## 1. Triangles and their intersection graph

Assume only that `G` is an `srg(99,14,1,2)`.  Every edge is in exactly one
triangle.  Thus `G` has `693/3=231` triangles, and every vertex is in seven
triangles.

Let `N` be the `99 x 231` vertex--triangle incidence matrix, and let `Gamma`
join two graph triangles exactly when they meet.  Distinct triangles meet in
at most one vertex, so

```
N N^T = A + 7 I,
N^T N = 3 I + Gamma.
```

The SRG equation gives

```
spec(A) = 14^1, 3^54, (-4)^44.
```

Consequently

```
spec(Gamma) = 18^1, 7^54, 0^44, (-3)^132.
```

Put `C=Gamma^2-5Gamma-18I`.  Its diagonal and its entries on intersecting
triangle pairs are zero.  If two triangles are disjoint, `C[T,U]` is exactly
the number `r(T,U)` of cross edges between them.  Cross edges form a matching,
because two cross edges sharing an endpoint would put an edge of the opposite
triangle in two graph triangles.  Hence `r` is in `{0,1,2,3}`.

For a fixed triangle `T`, let `a_r(T)` count its disjoint triangle partners
having `r` cross edges.  There are 212 disjoint partners.  Counting one cross
edge and a second triangle through its outside endpoint gives

```
sum a_r = 212,
sum r a_r = 36*6 = 216.
```

For the second binomial moment, choose ordered distinct vertices `x,z` of
`T` and one of the twelve external neighbours `y` of `x`.  The nonedge `yz`
has common neighbours `x` and a unique other vertex `w`.  The triangle on the
edge `yw` is disjoint from `T` and supplies cross edges at `x` and `z`.
Reversing `x,z` counts the same unordered cross-edge pair twice.  Therefore

```
sum binom(r,2) a_r = 6*12/2 = 36.
```

Writing `p(T)=a_3(T)` and `q(T)=12-p(T)`, these equations solve to

```
(a_0,a_1,a_2,a_3) = (20+q, 180-3q, 3q, 12-q).
```

Let `n3` be the number of unordered pairs with `r=2`, equivalently the
induced two-triangle configuration with exactly two independent cross edges.
Then

```
2*n3 = sum_T a_2(T) = 3 sum_T q(T).
```

In particular `3` divides `n3`.

## 2. Integral Schur lift

The orthogonal projector onto the 44-dimensional zero eigenspace of `Gamma`
is

```
E = (3I + J - Gamma - C)/21.
```

This is checked directly on all four eigenspaces.  Thus `M=21E` is a
positive-semidefinite integer matrix satisfying

```
M^2=21M,
M[T,T]=4,
M[T,U]=0                    if T and U meet,
M[T,U]=1-r(T,U)             if T and U are disjoint.
```

Let `W=M o M`, the entrywise square.  By the Schur product theorem `W` is
positive semidefinite.  Therefore

```
A4 = M W M
```

is a symmetric positive-semidefinite integer matrix.

For every integer entry, `m^2=m (mod 2)`, hence `W=M (mod 2)`.  Since
`M^2=21M`,

```
A4 = M^3 = M (mod 2).
```

Every row of `M mod 2` is nonzero: it contains `a_0(T)=20+q(T)>0` entries
equal to one.  Hence every row of `A4` is nonzero.

There is also a mod-four diagonal refinement.  Put `D=(W-M)/2`.  It is
integral and symmetric, and its diagonal is `(4^2-4)/2=6`, hence even.  For
every integral row vector `v`, `v D v^T` is even: the diagonal terms are even
and every off-diagonal term occurs twice.  From

```
A4 = M^3 + 2 M D M
```

and `M^3=441M`, every diagonal entry of `A4` is divisible by four.  A
positive-semidefinite matrix with a zero diagonal has the corresponding row
zero.  The rows here are nonzero, so all 231 diagonal entries are positive
multiples of four and

```
tr(A4) >= 4*231 = 924.                         (1)
```

On the other hand, a row of `M` has cube sum

```
4^3 + a_0 - a_2 - 8a_3 = 6(q-2).
```

Using `sum q=2*n3/3`, cyclicity of trace, and `M^2=21M` gives

```
tr(A4)
 = tr(M^2 W)
 = 21 sum_(T,U) M[T,U]^3
 = 84*(n3-693).                                (2)
```

Equations (1)--(2) force `n3-693>=11`.  The difference is divisible by
three, so actually

```
n3 >= 705.                                      (3)
```

No automorphism, graph catalog, numerical eigensolver, or SAT-negative is
used in this derivation.

## 3. Prisms and rooted fibre sides

An `r=3` pair of disjoint triangles is exactly an induced triangular prism;
write `P` for the number of such prisms.  Summing `a_3=12-q` over the 231
triangles and remembering that an unordered pair is counted twice gives

```
2P = 231*12 - 2*n3/3,
n3 + 3P = 4158.                                 (4)
```

Now fix a graph vertex `r`.  Its neighbourhood is `7K2`.  The 84 vertices at
distance two split into 21 fibres of four according to the two matched
neighbour pairs supporting them.  In each fibre, four vertex pairs share one
root neighbour (the sides) and two share none (the diagonals).  Let `S(r)` be
the number of selected side edges.

If a side edge `xy` shares root neighbour `u`, and its other support vertices
are the matched pair `v,v'`, then

```
{u,x,y} and {r,v,v'}
```

are the two triangles of an induced prism, with matching edges `ur,xv,yv'`
(up to swapping `v,v'`).  Conversely, an induced prism containing `r`
recovers exactly one such side edge opposite `r`.  Thus marked pairs
`(r, side edge)` are in bijection with `(prism, chosen prism vertex)`, and

```
sum_r S(r) = 6P.                                (5)
```

From (3)--(5),

```
P <= (4158-705)/3 = 1151,
sum_r S(r) <= 6906.
```

If all 99 roots had `S(r)>=70`, the sum would be at least 6930.  Therefore

```
some root r has S(r) <= 69.                     (6)
```

This is precisely the bound encoded by `scratch_root_side_le69.cnf`: its 84
counter inputs are the four sides in each of 21 fibres, and none of the 42
diagonals is counted.

## Scope

The proof is conditional only in the ordinary mathematical sense that it
starts from a putative `srg(99,14,1,2)`.  It does **not** import the stronger
public `n3>=708` endpoint.  The arithmetic audit is not a formal proof
certificate, and the bounded SAT portfolio for the side-bound CNF remains
`UNKNOWN`; therefore this note neither constructs nor excludes the Conway
99-graph.

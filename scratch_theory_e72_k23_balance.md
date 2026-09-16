# Exact side-balance for the E72 `K_{2,3}` support row

Assume a putative `srg(99,14,1,2)` and fix the selected root used in the
`E0=72` reduction.  This note treats source row 133 (partition 27,
compression orbit 0).  Its six exceptional fibres are

```
A_i={0,i},  B_i={1,i}       (i=2,3,4),
```

all with deficit two.  The other fifteen outer fibres are ordinary `C4`s.
The conclusion is pointwise: apart from the four ordinary fibres

```
{0,5}, {0,6}, {1,5}, {1,6},
```

every outer vertex has equally many neighbours in the twelve `A` vertices
and in the twelve `B` vertices.  Thus this condition can be added as exact
linear clauses before any search over the remaining graph.

## 1. Gram matrix and exceptional block totals

In the order `A_2,A_3,A_4,B_2,B_3,B_4`, Gram circulation gives

```
Z = [ 4 -2 -2 -4  2  2 ]
    [-2  4 -2  2 -4  2 ]
    [-2 -2  4  2  2 -4 ]
    [-4  2  2  4 -2 -2 ]
    [ 2 -4  2 -2  4 -2 ]
    [ 2  2 -4 -2 -2  4 ].                         (1)
```

It satisfies `Z^2=12Z` and has rank two.  We may write its vectors as

```
v(A_i)=u_i,  v(B_i)=-u_i,
||u_i||^2=4,  <u_i,u_j>=-2 (i != j),  u_2+u_3+u_4=0.       (2)
```

For overlapping supports `Z_FG=-D_FG`, while for disjoint supports
`Z_FG=4-D_FG`.  Hence the exact exceptional--exceptional block totals are

```
D(A_i,A_j)=D(B_i,B_j)=2                 (i != j),
D(A_i,B_i)=4,
D(A_i,B_j)=2                            (i != j).            (3)
```

Every exceptional fibre has two internal edges, regardless of which of its
seven labelled deficit-two states is used.

## 2. A signed test vector

Let `B` now denote the adjacency matrix on the 84 outer vertices.  Define
the scalar vector `d` by

```
d_x=+1 on an A_i fibre,  d_x=-1 on a B_i fibre,  d_x=0 otherwise,
```

and put `h=Bd`.  Thus

```
h_x = (# exceptional A-neighbours of x)
      -(# exceptional B-neighbours of x).                    (4)
```

Let `P` be the outer-to-root-neighbour incidence matrix.  Each root group
has two vertices.  Directly from the supports,

```
sum d_x=0,  ||d||^2=24,
P^T d=(6,6) on group 0, (-6,-6) on group 1, and 0 elsewhere,
||P^T d||^2=144.                                             (5)
```

The signed exceptional edge sum is also zero.  Indeed, the twelve internal
edges and the twelve same-side cross-fibre edges have sign product `+1`,
whereas the twelve vertical and twelve nonmatching cross-side edges have
sign product `-1`.  Therefore

```
<d,Bd>=2(12+12-12-12)=0.                                    (6)
```

The outer SRG identity is

```
B^2+B=12I+2J-PP^T.                                          (7)
```

Taking its quadratic form at `d` and using (5)--(6) yields the exact norm

```
sum_x h_x^2 = ||Bd||^2
            =12||d||^2-||P^T d||^2-<d,Bd>
            =288-144=144.                                   (8)
```

## 3. Saturation by sixteen forced vertices

An ordinary `C4` fibre has no edges to an overlapping fibre.  Between two
disjoint ordinary fibres the block is a perfect matching.  If an ordinary
support is disjoint from `t` exceptional supports, the degree equation at
each of its four vertices says that its total exceptional degree is exactly
`t`: it already has two root neighbours, two internal neighbours, and one
neighbour in each of the other `10-t` disjoint ordinary fibres.

For a vertex in `{0,5}` or `{0,6}`, the three disjoint exceptional supports
are precisely `B_2,B_3,B_4`.  Thus `h_x=-3`.  For a vertex in `{1,5}` or
`{1,6}`, they are precisely `A_2,A_3,A_4`, so `h_x=+3`.  These sixteen
vertices alone contribute

```
16*3^2=144                                                     (9)
```

to the nonnegative sum in (8).  Equality therefore forces

```
h_x=0 for every other one of the 68 outer vertices.             (10)
```

This retains the one-sided port information; it is not merely a support-
level block-total statement.  In particular:

* each of the 24 exceptional vertices has two `A` and two `B` exceptional
  neighbours (including neighbours in its own fibre);
* each vertex in `{2,3}`, `{2,4}`, or `{3,4}` has one neighbour in each of
  the unique disjoint pair `A_i,B_i`;
* each vertex in `{i,5}` or `{i,6}` (`i=2,3,4`) has two `A` and two `B`
  exceptional neighbours;
* each vertex in `{5,6}` has three `A` and three `B` exceptional neighbours;
* vertices in `{0,1}` have no exceptional neighbours.

For the first assertion, an exceptional support has eight disjoint ordinary
supports, each of which supplies exactly one neighbour to every exceptional
vertex.  After its two root neighbours, exactly four of its remaining
neighbours therefore lie in exceptional fibres; (10) splits them `2+2`.

## 4. An equivalent invariant two-dimensional signed subspace

Let `e=-1` on `{0,5},{0,6}`, `e=+1` on `{1,5},{1,6}`, and zero elsewhere.
Equations (4), (9), and (10) say

```
Bd=3e.                                                        (11)
```

Support incidence gives `PP^T d=6(d-e)`.  Substituting this and (11) into
(7) gives

```
Be=2d+e.                                                      (12)
```

Consequently `2d+3e` and `d-e` are exact outer eigenvectors of eigenvalues
`3` and `-2`, respectively.  Equations (10)--(12) are necessary conditions,
not an exclusion of source row 133 by themselves.

## 5. Per-root-group balance and the six missing blocks

There is a second pointwise count which is useful after (10).  If `x` has
outer support `S` and `m_g(x)` denotes the number of outer neighbours of
`x` whose support contains root group `g`, then

```
m_g(x)=2  if g is in S, and  m_g(x)=4  otherwise.             (13)
```

For `g` outside `S`, the two root-neighbour vertices in group `g` are both
nonadjacent to `x`; each has two common neighbours with `x`, all outer, so
their total is four.  For `g` in `S`, one is adjacent to `x` and contributes
one outer common neighbour.  The other is nonadjacent and has two common
neighbours with `x`, one of which is its mate in the root neighbourhood;
it therefore contributes one outer common neighbour.  This proves (13)
without a spectral assumption.

Fix `x` in `A_i`.  Write `a` for its internal degree, `v` for its degree to
`B_i`, and, for the two indices `j != i`, write

```
p_j=degree from x to A_j,   z_j=degree from x to B_j.
```

Its eight disjoint ordinary supports supply one neighbour apiece.  Among
these supports, exactly two contain group 1 and exactly three contain each
of the two bottom groups `j != i`.  Subtracting these fixed contributions
from (13), and using (10), gives

```
p_j+z_j=1  for each j != i,
sum p_j=v=2-a,       sum z_j=a.                              (14)
```

The same statement holds with `A` and `B` exchanged.  In particular every
entry in (14) is genuinely vertex-level; a neighbour assigned to one side
of a complementary bottom group prevents one on the other side.

For each of the four regular macro branches (`Q=12,6,8,4`), every exceptional
fibre is a two-edge matching, so `a=1` at all 24 exceptional vertices.
Every such vertex consequently has exactly one neighbour of each of the
following four kinds:

```
internal, vertical A_i--B_i, same-side nonmatching,
cross-side disjoint.                                         (15)
```

If its same-side target has bottom index `j`, (14) forces its disjoint
cross-side target to have the other bottom index `k`, not `j`.  In the Gram
notation (2), its vector neighbour sum over exceptional vertices is thus

```
u_j-u_k (up to sign), with squared norm 12.                  (16)
```

Moreover, for a fixed disjoint block `A_i--B_k`, let `j` be the third bottom
index.  Its allowed endpoints are precisely the two vertices of `A_i`
whose same-side target is `A_j` and the two vertices of `B_k` whose
same-side target is `B_j`.  The missing block must be one of the two perfect
matchings between these two-element sets.  The six disjoint blocks are
edge-disjoint, so before pair-common-neighbour tests a fixed overlap graph
has exactly

```
2^6=64                                                        (17)
```

support-balanced completions of its missing exceptional blocks.

For the fifth, adjacent-side macro, (14) instead gives the exact profiles

```
a=2: (sum p,v,sum z)=(0,0,2),
a=1:                         (1,1,1),
a=0:                         (2,2,0),                         (18)
```

always with `p_j+z_j=1` separately for both complementary indices.

## 6. Quantized Gram sums on the four regular macros

The remainder of this note concerns the four regular macro branches only.
Give every exceptional vertex in fibre `F` the vector `v(F)` from (2), give
every ordinary vertex zero, call the resulting 84-vector `c_0`, and put

```
q=Bc_0.
```

Since `sum c_0=0` and `P^T c_0=0` by Gram circulation, (7) gives

```
(B+I)q=12c_0.                                                (19)
```

Equation (13), now applied at an ordinary vertex and with its fixed ordinary
neighbours subtracted, determines not only its total exceptional degree but
also its degree at every bottom index.  If
`alpha_i=n_{A_i}(x)` and `beta_i=n_{B_i}(x)`, the possibilities are:

* on `{0,5},{0,6}` (respectively `{1,5},{1,6}`), there is exactly one
  neighbour in every `B_i` (respectively every `A_i`), hence `q_x=0`;
* on the bottom triangle missing `i`, there is one neighbour in each of
  `A_i,B_i`, hence `q_x=0`;
* on `{i,5}` or `{i,6}`, for the other bottom indices `j,k`, both the two
  side sums and the two index sums equal two.  Therefore, for some
  `t_x in {-1,0,1}`,

  ```
  q_x=2t_x(u_j-u_k).                                        (20)
  ```

* on `{5,6}`, the side sums equal three and every index sum
  `alpha_i+beta_i` equals two.  Thus `q_x` is either zero or
  `+/-2(u_j-u_k)` for a pair of bottom indices.

For an exceptional fibre `F`, put `n_F(x)=|N(x) intersect F|` and

```
C=sum_x sum_F binom(n_F(x),2).
```

Every two-edge matching state needs exactly six outer common-neighbour
witnesses for its six internal vertex pairs, so `C=6*6=36`.  Exceptional
vertices have at most one neighbour in each exceptional fibre by (14)--(15),
and therefore contribute zero.  The first two ordinary categories above
also contribute zero.  A vertex in either of the last two categories
contributes zero when `q_x=0` and two otherwise.  Consequently exactly 18
of the 28 vertices in the six `{i,5},{i,6}` fibres and `{5,6}` initially
have nonzero `q`.

In fact none of the four `{5,6}` vertices can have nonzero `q`.  Let `T_i`
be the bottom-triangle fibre on the other two bottom indices.  At each
`x in T_i`, both `c_0(x)` and `q_x` vanish, so (19) says that the sum of the
`q` vectors on its neighbours is zero.  Apart from the unique neighbour in
`{5,6}`, every possibly nonzero term is a multiple of

```
w_i=u_j-u_k:
```

there is one exceptional neighbour in each of `A_i,B_i` and one ordinary
neighbour in each of `{i,5},{i,6}`.  Hence the `{5,6}` neighbour's `q` must
belong to `span(w_i)`.  But every `{5,6}` vertex is matched to one vertex in
each of `T_2,T_3,T_4`, while the three lines `span(w_i)` are distinct.
Their intersection is zero.  Thus

```
q_x=0 on {5,6},
exactly 18 of the 24 bottom--outside vertices have nonzero q. (21)
```

## 7. The six bottom--outside fibre types

For a whole fibre `U_i^a={i,a}`, `a in {5,6}`, the four values in (20)
sum to zero: every one of the four candidate exceptional blocks has total
four.  Its multiset of `t` values is therefore exactly one of

```
Z={0,0,0,0},  H={-1,0,0,1},  F={-1,-1,1,1}.                (22)
```

They contain respectively 0, 2, and 4 nonzero vertices.  From (21), the
six-fibre type multiset is initially either `H^3 F^3` or `Z H F^4`.

The four vertices of the ordinary fibre `{0,1}` give a further exact
restriction.  Such a vertex has one neighbour in every `U_i^5,U_i^6` and
all of its other neighbours have `q=0`.  Equation (19) and
`w_2+w_3+w_4=0` say pointwise that

```
t_{2,5}+t_{2,6}=t_{3,5}+t_{3,6}=t_{4,5}+t_{4,6}.             (23)
```

The edges from `{0,1}` to each `U` form an independent perfect matching.
Thus the three paired fibre types in (23) must admit a common four-entry
multiset of coordinatewise sums.  A direct four-symbol check gives:

* pairing `Z` with `H` gives only `{-1,0,0,1}`, which no `F,F` pairing gives;
* pairing `Z` with `F` gives only `{-1,-1,1,1}`, which no `H,F` pairing gives;
* the three families of sum multisets for `H,H`, `H,F`, and `F,F` have
  empty triple intersection.

The alternative `Z H F^4` is therefore impossible: according as `Z` is
paired with `H` or `F`, the other two pairs include the incompatible type
in the first or second bullet.  If `H^3 F^3` is not paired `H,F` at every
bottom index, its three pairs are `H,H`, `H,F`, `F,F`, contradicting the
third bullet.  Hence, after possibly exchanging outside groups 5 and 6
separately at the support-description level,

```
for every i=2,3,4, exactly one of U_i^5,U_i^6 has type H
and the other has type F.                                   (24)
```

This leaves eight labelled support-type patterns before the actual vertex
matchings are imposed.  Statement (24), like the earlier balance, is a
necessary structural reduction and not yet an exclusion of the row.

## 8. Every exceptional vertex sees exactly one zero `U` vertex

There is also a sharp consequence of (19) at an exceptional vertex.  Use
the cyclic orientations

```
w_2=u_3-u_4,  w_3=u_4-u_2,  w_4=u_2-u_3.
```

For `x in A_i`, its same-side target and its forced disjoint target are the
two other bottom indices.  The `q` vectors at those two exceptional
neighbours add to `3u_i`; for `x in B_i` they add to `-3u_i`.  The internal
and vertical exceptional neighbours both have `q` in `span(w_i)`.  If
`sigma=+1` on `A_i` and `-1` on `B_i`, and

```
T_l=t_(neighbour of x in U_l^5)+t_(neighbour of x in U_l^6),
```

then (19) reduces to

```
q_x+q_internal+q_vertical+2T_j w_j+2T_k w_k=9 sigma u_i,    (25)
```

where `j,k` are the other two bottom indices.  Taking the inner product
with `u_i`, and using `u_i perpendicular w_i` and
`<u_i,w_j>,<u_i,w_k>={-6,+6}`, shows that the two `T` values differ by
`3 sigma` in the appropriate cyclic orientation.  Since each is a sum of
two members of `{-1,0,1}`, their absolute values are exactly `{1,2}`.
The value of absolute size two uses two nonzero `U` neighbours and the value
of absolute size one uses exactly one.  Therefore

```
every exceptional vertex has exactly three nonzero-q neighbours and
exactly one zero-q neighbour among its four bottom--outside neighbours. (26)
```

This also matches the global incidence equality
`24*3=18*4=72`.  All six zero vertices occur in the three `H` fibres of
(24), and each has four exceptional neighbours.

Writing `q_x=epsilon_x w_i` on an exceptional vertex, equation (25) in the
remaining direction also gives

```
epsilon_x+epsilon_internal+epsilon_vertical is +1 or -1.    (27)
```

Thus those three signs are never all equal.  In each exceptional fibre the
four values in (27) consist of two `+1` and two `-1`, since each of the
self, internal-neighbour, and vertical-neighbour sign multisets is balanced.

`scratch_theory_e72_k23_balance_audit.py` verifies all support counts,
Gram arithmetic, signed edge sums, norm saturation, category counts, and
the two eigenvector identities, as well as (13)--(27), using exact integer
arithmetic and only the Python standard library.

## 9. Pair upper bounds as four-point collision rules

The regular branches admit a particularly small reformulation of the pair
upper bound.  Fix a bottom--outside fibre `U=U_i^a`.  If an exceptional
vertex `x` has bottom index different from `i`, write `phi_U(x)` for its
unique neighbour in `U`.  Of the four exceptional neighbours of `x`,
exactly three have support disjoint from `U`: its internal neighbour, its
vertical neighbour, and its unique cross-bottom neighbour whose bottom is
the third index.  Call this three-set `R_U(x)`.

For `y in U`, the part of

```
1_(x adjacent y) + |N(x) intersect N(y)|
```

already realized on the exceptional vertices and `U` itself is exactly

```
1_(y=phi_U(x)) + 1_(y adjacent_C4 phi_U(x))
  + |{z in R_U(x): phi_U(z)=y}|.                              (28)
```

The supports of `x,y` are disjoint, so the outer SRG identity bounds (28)
by two.  The first two indicators equal one on `phi_U(x)` and its two side
neighbours in the square, and equal zero only at the diagonal opposite.
Thus (28) is equivalent to the following **opposite-collision rule**:

```
if the three images phi_U(R_U(x)) contain a repeated point, that point is
the diagonal opposite phi_U(x), and its multiplicity is exactly two.     (29)
```

(A triple repetition is forbidden.)  This is an exact labelled rule, not a
block-total relaxation.

There is an equally small rule when `x` has bottom index `i`, so that its
support overlaps `U`.  Now precisely two exceptional neighbours of `x`
have supports disjoint from `U`.  If their two `phi_U` images coincide at
`y`, then `x` and `y` already have two exceptional common neighbours.  The
outer allowance is one when their selected root-neighbour labels in group
`i` agree and two otherwise.  Therefore

```
a collision of the two images is allowed only at a target y whose
group-i bit is opposite to the group-i bit of x.                         (30)
```

Both directions of (29)--(30) follow directly from the displayed count, so
they are equivalent to all exceptional--`U` pair-upper rows within the
48-vertex induced subsystem consisting of the 24 exceptional and 24 `U`
vertices.

These rules lead to a solver-free finite enumeration.  For each bottom
index `i` it performs the following exhaustive steps.

1. Enumerate the two H/F orientations and all `12*6` labelled H/F value
   patterns on `U_i^5,U_i^6`.
2. For each of the four exceptional source fibres disjoint from them,
   enumerate every map from its four labelled vertices to each target
   fibre.  The target loads are exactly `1+eta*t`, and the paired maps are
   retained exactly when their two selected `t` values give the required
   exceptional-row sum in (25).
3. Apply (29)--(30) pointwise and compress a surviving pair of maps only by
   its six labelled source-pair collision multiplicities.
4. Join the three bottom-index factors.  For each exceptional source fibre,
   the collision signatures supplied by its two disjoint bottom indices
   must sum to the exact six-entry remaining-common-witness vector computed
   from the already fixed exceptional graph.

No Boolean edge relaxation occurs in these steps: a state consists of
explicit functions between four-element labelled sets, and every such
function with the required loads is visited.  The implementation is
`scratch_theory_e72_k23_opposite_collision_enum.py`; its sharded outputs and
combiner provide the coverage bridge from the preceding 5,138-mask regular
frontier.  This enumeration deliberately does not apply (22)--(27) to the
fifth, adjacent-side macro, where exceptional internal degrees are not all
one.

## 10. Solver-free exclusion of all four regular macros

Two further collision profiles finish the regular branches.  For an
exceptional pair `x,z`, a target-bottom factor records

```
c_i(x,z)=1_(phi_(U_i^5)(x)=phi_(U_i^5)(z))
         +1_(phi_(U_i^6)(x)=phi_(U_i^6)(z)),                 (31)
```

whenever both supports are disjoint from the target fibres.  Summing (31)
over the available bottom indices is bounded by the exact residual

```
r(x,z)=2-|support-labels(x) intersect support-labels(z)|
         -1_(x adjacent z)-|N_E(x) intersect N_E(z)|.        (32)
```

For two vertices in the same exceptional fibre equality holds: the collision
identity in Section 6 is already saturated by the 18 nonzero `U` vertices,
so the other ordinary categories supply no same-fibre collision.  This is
precisely the six-entry signature join in Section 9.  For different
exceptional fibres inequality in (32) is retained explicitly.

Finally consider `y in U_i^5` and `z in U_i^6`.  Their supports overlap in
bottom group `i`, and their partial common neighbours in the 48-vertex
subsystem are exactly the exceptional vertices mapped to both.  Hence

```
|{x: phi_(U_i^5)(x)=y and phi_(U_i^6)(x)=z}|
  <= 1  if the group-i bits of y,z agree,
  <= 2  otherwise.                                         (33)
```

The analogous same-outside rule between `U_i^a,U_j^a` is checked as well;
it is not needed for the final zero count because (33) already kills the
last profile join.

The exact solver-free census is staged only to keep its audit artifacts
small:

```
input: H/F + exceptional-row + same-fibre frontier   5,138 masks
after (29)--(30) and the exact same-fibre join           81 masks
after all exceptional-pair bounds (31)--(32)              1 mask
after the U--U overlap bound (33)                          0 masks.
```

The corresponding labelled orbit masses are
`1,129,056 -> 9,952 -> 16 -> 0`.  The four regular macro counts at input are

```
macro 0 (Q=12):   891
macro 1 (Q= 6): 2,348
macro 2 (Q= 8): 1,234
macro 3 (Q= 4):   665.
```

The artifacts are:

* `scratch_theory_e72_k23_opposite_collision_enum.py`, its eight
  `..._shard_*.json` outputs, and
  `scratch_theory_e72_k23_opposite_collision_combine.py` for the first stage;
* `scratch_theory_e72_k23_ee_cross_enum.py/.json` for (31)--(32);
* `scratch_theory_e72_k23_final_uu_enum.py/.json` for (33) and the final
  zero-survivor assertion.

All three enumerators use only explicit maps on four labelled points and the
Python standard library.  In particular, this is independent of the
48-edge-variable SAT census.  Together with the exact preceding frontier it
excludes source-133 macros 0--3.  Macro 4 remains a separate adjacent-side
case because the H/F derivation assumes internal degree one at every
exceptional vertex.

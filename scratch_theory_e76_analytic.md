# Analytic exclusion of the selected-root `E0=76` branch

Assume a putative `srg(99,14,1,2)` and choose a root `r` with `S(r)<=69`,
using the self-contained triangle/prism side bound.  This note proves, with
no SAT/CP-SAT conclusion, that this root cannot have `E0=76`.

Together with the elementary diagonal-capacity bound and the separate Gram
circulation proof for `E0=75`, this gives the purely mathematical selected-
root normalization

```
E0 <= 74.                                                    (0)
```

## 1. The unique possible `E0=76` support and fibre types

Recall

```
E0 = S+Q,                    delta_F = 4-e_F,
sum_F delta_F = 84-E0.
```

The allowed four-vertex fibre types give the following maximum diagonal
count as a function of the deficit:

```
delta:       0  1  2  3  4
Q capacity:  0  0  2  1  0.                                (1)
```

If `E0=76`, the selected-root side bound gives `Q>=7`, while the total
deficit is eight.  The only way (1) can reach seven is four deficit-two
fibres, each in its two-diagonals state.  In fact

```
Q=8, S=68,       deficit multiset=(2,2,2,2).                 (2)
```

Use the PSD Gram-circulation matrix from
`scratch_theory_gram_circulation.md`.  Its nonzero Gram vectors have

```
||v_F||^2=2 delta_F,
sum_(F incident with g) v_F=0  for every root group g.       (3)
```

There are four exceptional support edges.  Since (3) forbids degree one,
their simple support graph is a four-cycle.  The degree-two equations make
the vectors alternate around it.  Label its supports cyclically

```
F0,F1,F2,F3
```

and put `w_Fi=(-1)^i`, with `w=0` on the other 17 supports.  The integral PSD
matrix is then

```
Z = 4 w w^T.                                                 (4)
```

Using `Z_FG=-D_FG` for overlapping supports and
`Z_FG=4-D_FG` for disjoint supports, (4) fixes every block total:

* an ordinary (`delta=0`) fibre is a `C4`;
* ordinary--ordinary disjoint blocks have total four and ordinary overlap
  blocks have total zero;
* consecutive exceptional fibres have total four;
* opposite exceptional fibres have total zero;
* an exceptional--ordinary block has total four or zero according as its
  supports are disjoint or overlapping.

The compression consequently satisfies

```
D w = -4w.                                                   (5)
```

## 2. An integral residual vector

Let `B` be the 84-vertex outer adjacency matrix.  Give all four vertices in
fibre `F` the value `w_F`; call the resulting integral vector `c`.  It has
16 nonzero entries, eight `+1` and eight `-1`.  Alternation at every cycle
group also gives

```
1^T c=0,             P^T c=0,                               (6)
```

where `P` is the outer--root-neighbour incidence matrix.  Equation (5) says
that the sum of `Bc` on each fibre is `-4w_F`.

The outer block of the SRG matrix equation is

```
B^2+B = 12I+2J-PP^T.                                        (7)
```

Define

```
q=(B+I)c.
```

From (6)--(7),

```
Bq=12c.                                                      (8)
```

Also `||c||^2=16` and, by (5), `<c,Bc>=-16`.  Equation (7)
then gives

```
||q||^2=192.                                                 (9)
```

Every exceptional fibre is in the two-diagonals state.  Each of its
vertices has one same-fibre neighbour of its own sign and, by the exact
symbol matchings, one neighbour in each consecutive exceptional fibre, both
of the opposite sign.  It has none in the opposite exceptional fibre.
Thus

```
q=0 on all 16 exceptional vertices.                         (10)
```

Equation (5) also says that every ordinary fibre has `q`-sum zero.

## 3. Ordinary-fibre categories and collision budgets

The four cycle groups leave three outside groups.  The 17 ordinary supports
split as follows:

```
2 chords   between opposite cycle groups,
12 spokes  between a cycle group and an outside group,
3 outside supports on the three outside groups.              (11)
```

A chord overlaps all four exceptional supports, so `q=0` on both chord
fibres.  A spoke is disjoint from exactly two exceptional supports, one of
each sign.  An outside support is disjoint from all four, two of each sign.

We use one standard consequence of an ordinary `C4` fibre.  It has no edge
to an overlapping fibre and block total four to every disjoint fibre.  Its
external collision budget is zero, so every vertex in a disjoint target
fibre has exactly one neighbour in it.  In particular, for an exceptional
fibre `F` and disjoint ordinary fibre `G`, each vertex of `F` has exactly one
neighbour in `G`.

For `x in G`, let `n_F(x)` count its neighbours in exceptional fibre `F`.
An exceptional two-diagonals fibre has six outer collision witnesses:

```
sum_(ordinary G disjoint from F) sum_(x in G) C(n_F(x),2)=6. (12)
```

Indeed, its two adjacent pairs and four nonadjacent pairs need ten common
neighbours in total; the four side pairs already have one inner common
neighbour each, and no vertex of the exceptional local graph or its overlap
matchings sees two vertices of `F`.  Summing (12) over the four exceptional
fibres gives total collision count 24.

An ordinary vertex has two internal neighbours and one neighbour in each
disjoint ordinary `C4` fibre.  Degree 12 therefore forces its total number
of exceptional neighbours to equal the number of exceptional supports
disjoint from its support.

For a spoke vertex, write its two exceptional occupancies as `a,b`.  They
satisfy `a+b=2`, and

```
q=a-b,
q^2/4 = C(a,2)+C(b,2).                                      (13)
```

For an outside vertex, write its four occupancies as
`n_1,n_2,n_3,n_4`, the first two belonging to positive exceptional fibres.
They sum to four.  If `A=n_1+n_2`, then `q=2A-4`, and direct minimization of
the binomial collision sum gives

```
q^2/4 - sum_i C(n_i,2) <= 2.                                (14)
```

Equality in (14) occurs only when `A` is zero or four and the two occupied
same-sign fibres contribute `2+2`.  There are twelve outside vertices.

Let `U_s,C_s` and `U_o,C_o` be respectively the sums of `q^2/4` and the
collision sums over spoke and outside vertices.  Equations (9)--(14) give

```
U_s+U_o = 48,
C_s+C_o = 24,
U_s=C_s,
U_o-C_o <= 12*2=24.
```

Every inequality is therefore equality.  Consequently

```
q=0 on every spoke vertex,
q is +4 or -4 on every outside vertex.                       (15)
```

## 4. The chord parity contradiction

Take a vertex `x` in either chord fibre.  It has `c_x=q_x=0`.  Its chord
support is disjoint from each of the three outside supports.  Both endpoint
fibres are ordinary `C4`s, so each of those three blocks is a perfect
matching.  All other possible neighbours have `q=0` by (10), (11), and
(15).  Hence

```
(Bq)_x
```

is a sum of exactly three numbers, each equal to `+4` or `-4`, and cannot be
zero.  But (8) gives `(Bq)_x=12c_x=0`, a contradiction.  This excludes the
selected-root `E0=76` branch.

## 5. Combined high-`E0` conclusion

For every fibre, (1) implies `Q<=sum delta_F=84-E0`.  The selected root has
`Q=E0-S>=E0-69`.  Therefore `E0>=77` is already impossible.  The exact Gram
circulation classification in `scratch_theory_gram_circulation.md` excludes
`E0=75`, and the argument above excludes `E0=76`.  This proves (0): every
putative target admits a root with `E0<=74`, without a solver-negative.

`scratch_theory_e76_analytic_audit.py` checks the numerical, projector,
support-category, occupancy, equality, and parity calculations with exact
integer/Fraction arithmetic.  The separate
`scratch_theory_e76_occupancy_independent_audit.py` independently enumerates
all local occupancy matrices and verifies that the global collision/norm
equalities force (15).

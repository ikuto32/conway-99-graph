# A fibre-summed recurrence exclusion inside E72 source row 150

This note gives a solver-free necessary-condition filter for source row 150
(`partition=[2,2,2,2,1,1,1,1]`, compression orbit 0) of the selected-root
`E0=72` frontier.  The stored frontier has 5,943 local graph orbits and
labelled orbit mass 2,244,608.  The argument excludes exactly the two
canonical macro branches `(state orbit, signature orbit)=(0,2),(3,2)`, or
1,008 local orbits and labelled mass 393,216.

The important directionality convention is retained throughout: an ordinary
`C4` makes every vertex of a disjoint exceptional fibre have exactly one
neighbour in that `C4`; it does **not** make the degree of an ordinary vertex
to the exceptional fibre equal to one.

## 1. Selected-root identities

Write `B` for the adjacency matrix on the 84 vertices outside a selected
root and its 14 neighbours, and `P` for the `84 x 14` outer-to-root-neighbour
incidence matrix.  The SRG equations give

```
B^2+B=12I+2J-PP^T.                                         (1)
```

The outer vertices lie in four-vertex support fibres indexed by the 21 pairs
of root groups.  If `x` has support `S` and `m_g(x)` is the number of outer
neighbours of `x` whose support contains group `g`, then

```
m_g(x)=2 if g in S, and m_g(x)=4 otherwise.                 (2)
```

An ordinary fibre induces a `C4`.  Its four adjacent pairs already use their
one allowed common neighbour (a root neighbour), and its two opposite pairs
already use their two allowed common neighbours (the two internal vertices
of the `C4`).  Hence no outside vertex can see two vertices of an ordinary
fibre.  A disjoint block incident with that fibre has total four, so every
vertex at the other end sees exactly one vertex of the ordinary fibre.  This
is the one-sided function property used below.

## 2. The source-150 Gram vectors

In the order

```
A_2={0,2}, A_3={0,3}, A_4={0,4}, A_5={0,5},
B_2={1,2}, B_3={1,3}, B_4={1,4}, B_5={1,5},                (3)
```

put

```
u_2=(1,1,1), u_3=(-1,0,0), u_4=(0,-1,0), u_5=(0,0,-1),
v(A_i)=u_i, v(B_i)=-u_i.                                   (4)
```

Thus the vector sum on every root group is zero.  Give all four vertices of
an exceptional fibre `F` the vector `v(F)`, give every ordinary vertex zero,
and call the resulting vector `c`.  Then

```
sum(c)=0, P^T c=0.                                          (5)
```

Set `q=Bc`.  Equations (1) and (5) imply the pointwise Gram-vector recurrence

```
(B+I)q=12c.                                                 (6)
```

The five exact source-150 Gram profiles use the same coordinates (4), with
five positive-semidefinite coordinate Gram matrices `H`.  The two branches
excluded below have

```
H_* = [ 4 -1  0 ]
      [-1  2 -1 ]
      [ 0 -1  2 ].                                         (7)
```

## 3. Exceptional values of q are fixed

The saved local graph contains every internal and overlapping-support edge
among the 32 exceptional vertices.  Its full Gram profile also fixes the
total `D_FG` in each of the twelve omitted disjoint exceptional blocks.

Fix an exceptional vertex `x` in fibre `F`.  Every disjoint ordinary fibre
contributes one neighbour to `x` by the one-sided `C4` lemma.  Subtract those
ordinary contributions and all saved internal/overlap edges from (2).  If
`n_G(x)` is the unknown degree from `x` to a disjoint exceptional fibre `G`,
the remaining seven equations are

```
sum_(G disjoint F, g in G) n_G(x) = residual_g(x),
0 <= n_G(x) <= 4.                                           (8)
```

There are only three variables in (8).  Direct enumeration of `[0,4]^3`
finds exactly one solution for every one of the 32 vertices in every one of
the 5,943 saved local orbits.  The four solutions at each end also sum to the
Gram-forced `D_FG`.  Consequently

```
q_x=sum_G n_G(x)v(G)                                        (9)
```

is fixed on all exceptional vertices without choosing any of the actual
`4 x 4` disjoint-block matrices.

## 4. Sum (6) over an exceptional fibre

For an exceptional fibre `F`, sum (6) over its four vertices.  If
`d_F(y)=|N(y) intersect F|`, this gives

```
sum_(x in F) q_x + sum_(exceptional y) d_F(y)q_y
 + sum_(ordinary y) d_F(y)q_y = 48v(F).                    (10)
```

The first two terms are fixed.  For internal and overlapping exceptional
blocks, `d_F(y)` is read from the saved graph; for a disjoint exceptional
block it is the unique target-side value from (8).  Define the required
ordinary load

```
T_F=48v(F)-sum_(x in F)q_x-sum_(exceptional y)d_F(y)q_y.    (11)
```

Now take one ordinary fibre `U`.  For `y in U`, equations (2), after
subtracting its two internal neighbours and its one neighbour in every
disjoint ordinary fibre, enumerate the possible vector

```
(n_F(y): F exceptional and disjoint from U).                (12)
```

Each coordinate lies in `[0,4]`.  The one-sided function property imposes

```
sum_(y in U)n_F(y)=4                                        (13)
```

for every disjoint exceptional `F`.  There are respectively 1, 3, or 7
possibilities for (12) at a vertex and only 1, 3, or 11 unordered
four-vertex configurations satisfying (13).  Such a configuration supplies

```
R_F(U)=sum_(y in U)n_F(y)q_y,
q_y=sum_G n_G(y)v(G).                                       (14)
```

Thus (10) is possible only if one configuration can be chosen in each of
the thirteen ordinary fibres so that

```
sum_U R_F(U)=T_F for all eight exceptional F.               (15)
```

This is a finite Minkowski-sum problem; no ordinary-to-exceptional labelled
map, and no two-sided matching assumption, enters (14)--(15).

If `H` is singular, equality of represented vectors is tested as
`H(left-right)=0`.  This is exact because every profile matrix is positive
semidefinite.  For (7), `H_*` is nonsingular.

## 5. A three-coordinate certificate for H_*

For (7), after multiplying vector rows by `H_*`, (11) is

```
A_2: ( 144,-24, 36)   A_3: (-156, 36,-24)
A_4: (  36,-36, 24)   A_5: ( -24, 24,-36)
B_i: the negative of the corresponding A_i row.             (16)
```

It suffices to retain coordinates `(A_2:0,A_2:1,A_3:0)`, whose target is

```
(144,-24,-156).                                              (17)
```

The exact projected option sets from (12)--(14) are below.  Four zero rows
are combined on the first line.

```
U                         projected options
{0,1},{0,6},{1,6},{2,3}   (0,0,0)
{2,4}                     (0,0,0/-16/-32)
{2,5}                     (0,0,0/-20/-40)
{2,6}                     (0,0,0/-16/-18/-20/-32/-36/-40)
{3,4}                     (0,0,0),(12,-4,0),(24,-8,0)
{3,5}                     (0,0,0),(8,8,0),(16,16,0)
{3,6}                     (0,0,0),(8,8,0),(10,2,0),(12,-4,0),
                            (16,16,0),(20,4,0),(24,-8,0)
{4,5}                     (0,0,0),(28,-4,-28),(56,-8,-56)
{4,6}                     (0,0,-32),(0,0,-16),(0,0,0),
                            (12,-4,-16),(12,-4,0),(20,-4,-22),
                            (24,-8,0),(28,-4,-44),(28,-4,-28),
                            (40,-8,-28),(56,-8,-56)
{5,6}                     (0,0,-40),(0,0,-20),(0,0,0),
                            (8,8,-20),(8,8,0),(16,16,0),
                            (18,2,-24),(28,-4,-48),(28,-4,-28),
                            (36,4,-28),(56,-8,-56).          (18)
```

Convolving the thirteen rows of (18), in the displayed support order,
produces respectively

```
1,1,1,1,1,3,9,31,93,279,961,2861,10638,31768               (19)
```

distinct partial/final triples.  Among final triples whose first two
coordinates equal `(144,-24)`, the possible third coordinates are

```
-246,-242,-238,-230,-226,-224,-222,-218,-214,-210,-208,
-206,-204,-202,-198,-194,-192,-190,-188,-186,-184,-182,
-174,-172,-170,-168,-166,-154,-152,-150,-134.               (20)
```

The required value `-156` is absent.  Hence (15), and therefore (6), is
impossible for `H_*`.

The machine-readable reconstruction of (18)--(20) is
`scratch_theory_e72_source150_recurrence_certificate.py/.json`.

## 6. Coverage and exact result

Every saved representative is classified by its internal edge set and all
overlapping exceptional block totals into one of the exact Gram rows.  The
two canonical rows with `H=H_*` are precisely

```
(0,2): 352 local orbits, labelled mass 131,072,
(3,2): 656 local orbits, labelled mass 262,144.              (21)
```

All 1,008 orbits in (21) fail the same three-coordinate certificate.  The
other 4,935 orbits, labelled mass 1,851,392, pass this necessary condition;
no existence claim is made for them.

The complete 24-coordinate census is reproduced by
`scratch_theory_e72_source150_fibre_recurrence_filter.py/.json`.  It uses
only Python's standard library and exact integers/rationals.  The weaker
norm/collision and separate-block graphical controls are recorded in
`scratch_theory_e72_source150_norm_collision_filter.py/.json` and
`scratch_theory_e72_source150_disjoint_graphical_filter.py/.json`; both keep
all 5,943 representatives, as they should after the omitted disjoint blocks
are handled correctly.

# Analytic exclusion of the dominant E72 K4-support Q=12 subbranch

This note concerns the selected-root `E0=72` compression row with six
deficit-two exceptional fibres supported on all six edges of a `K4`.  It
proves that the subbranch in which all six fibres are in their
two-diagonals state (`Q=12`) is impossible.  The mixed `Q=6` subbranch is
not excluded here.

The argument uses the PSD Gram circulation, the standard ordinary-`C4`
block lemma, exact common-neighbour counts, and the outer SRG matrix
identity.  It does not depend on a SAT/CP-SAT negative or on enumerating the
64 locally surviving `Q=12` graphs.

## 1. The K4 Gram vectors

Write the exceptional supports as the edges of the complete graph on core
groups `0,1,2,3`.  The unique Gram matrix has

```
Z_FF = 4,
Z_FG = -2  if F,G meet,
Z_FG =  4  if F,G are opposite K4 edges.                    (1)
```

Thus the two fibres in each of the three opposite-edge pairs have the same
Gram vector.  Call the three vectors `a,b,c`.  Then

```
||a||^2=||b||^2=||c||^2=4,
<a,b>=<b,c>=<c,a>=-2,
a+b+c=0.                                                    (2)
```

The three opposite exceptional blocks have total

```
D_F,Fbar = 4-Z_F,Fbar = 0,                                  (3)
```

whereas every pair of meeting exceptional supports has block total two.
All other 15 fibres are ordinary `C4`s.  An ordinary fibre has no edge to
an overlapping fibre and block total four to a disjoint fibre.  Its zero
external-collision budget implies that every vertex of the other fibre has
exactly one neighbour in it.

Give every outer vertex in exceptional fibre `F` the vector `v_F` from
(2), and every vertex in an ordinary fibre the zero vector.  Denote this
84-vertex vector-valued vector by `c_0`, and put

```
q = B c_0,                                                   (4)
```

where `B` is the outer adjacency matrix.  The circulation equations make
`c_0` orthogonal to the all-one and root-incidence spaces.  Matrix (1) has
nonzero eigenvalues `12,12`, so its range is the compression eigenspace
with eigenvalue zero.  Hence the outer SRG identity

```
B^2+B = 12I+2J-PP^T
```

gives, coordinate by coordinate,

```
(B+I)q = 12c_0.                                             (5)
```

## 2. Degrees and the local Q=12 residual

The 15 ordinary supports consist of 12 spokes (one core and one outside
group) and three outside supports (two of the three outside groups).

An exceptional support is disjoint from nine ordinary supports.  By the
ordinary-`C4` lemma, each of its vertices has one neighbour in each of
those fibres.  Since every outer vertex has outer degree 12, it has exactly
three exceptional neighbours.  A spoke vertex has exactly three
exceptional neighbours, and an outside vertex has exactly six; this follows
in the same way by counting its ordinary internal and disjoint-fibre
neighbours.

Now assume `Q=12`.  Every exceptional fibre consists of its two internal
diagonals.  Each exceptional vertex therefore has one internal neighbour,
of the same Gram-vector class, and two overlap neighbours.  Its two signed
root symbols require one side neighbour each, so the overlap neighbours use
the two endpoints of its support.  The forced ordinary-`C4` support balance,
together with (3), says that these two neighbours introduce the two
different complementary core groups.  Their supports are consequently
opposite K4 edges and carry the same one of the other two Gram vectors.
Thus every exceptional vertex has

```
q_x = a+2b, or a+2c, and cyclic variants,
||q_x||^2=12.                                               (6)
```

In particular, an exceptional vertex has at most one neighbour in any one
exceptional fibre.

## 3. Two exact collision counts

For every outer vertex `x` and exceptional fibre `F`, put

```
n_F(x) = number of neighbours of x in F.
```

Let

```
C = sum_x sum_F binom(n_F(x),2).                             (7)
```

In a two-diagonals fibre, the two adjacent diagonal pairs each require one
outer common neighbour, and the four nonadjacent side pairs each require
one outer common neighbour after their one inner common neighbour is
removed.  Therefore each exceptional fibre contributes exactly six to
(7), and

```
C=6*6=36.                                                   (8)
```

Equation (6) also shows that exceptional vertices contribute zero to `C`.

Fix an opposite pair `F,Fbar`.  Its block is empty by (3).  All 16
cross-pairs are nonadjacent, share no inner neighbour, and therefore have
two outer common neighbours.  Hence

```
sum_x n_F(x)n_Fbar(x)=32.                                   (9)
```

Exactly eight of these witnesses are exceptional.  Indeed, take one of
the four other exceptional fibres `G`.  Every vertex of `G` chooses one of
the two other opposite-edge classes for its two overlap neighbours.  The
two blocks from `G` to `F,Fbar` contain four edge incidences in total.  A
vertex choosing this class contributes two incidences and otherwise zero,
so exactly two vertices of `G` witness the pair.  Summing over the four
choices of `G` gives eight.  A spoke support cannot be disjoint from both
members of an opposite pair.  Thus the 12 vertices in the three outside
fibres supply exactly

```
sum_(x outside) n_F(x)n_Fbar(x)=24                           (10)
```

for each of the three opposite pairs.

For these 12 outside vertices write `u_x=n_F(x)` and
`v_x=n_Fbar(x)`.  Each exceptional--outside fibre block has total four, so

```
sum_x u_x=sum_x v_x=12.
```

Using (10),

```
sum_x (u_x-v_x)^2
 = 2( sum_x[binom(u_x,2)+binom(v_x,2)] - 12 ) >= 0.          (11)
```

Summing (11) over the three opposite pairs says that the outside vertices
contribute at least 36 to `C`.  Equations (8) and (6) force equality
everywhere.  Consequently

```
* every spoke has n_F(x) in {0,1} for every F;
* n_F(x)=n_Fbar(x) at every outside vertex and opposite pair. (12)
```

A spoke has total exceptional degree three and its three possible
exceptional fibres represent `a,b,c` once each.  Therefore (12) gives

```
q_x=a+b+c=0                  for every spoke vertex.         (13)
```

At an outside vertex write the three equal paired occupancies as
`m_1,m_2,m_3`.  Its exceptional degree six gives

```
m_1+m_2+m_3=3.                                             (14)
```

The only unordered profiles are `111`, `210`, and `300`, contributing
respectively `0,2,6` to (7).  If their numbers among the 12 outside
vertices are `N_111,N_210,N_300`, equality in (8) gives

```
N_111+N_210+N_300=12,
2N_210+6N_300=36.
```

It follows that `N_300>=3`.  At every `300` vertex, (2) and (4) give

```
q_x=6a, 6b, or 6c,              ||q_x||^2=144.              (15)
```

## 4. The spoke triangle-inequality contradiction

Choose an outside vertex `y` of type `300`.  Its ordinary outside fibre is
disjoint from four spoke fibres, and every such ordinary--ordinary block is
a perfect matching.  Choose a spoke neighbour `x` of `y`.

By (13), `c_0(x)=q_x=0`, so (5) says `(Bq)_x=0`.  Among the neighbours of
`x`, all internal and spoke vertices have `q=0`; exactly one lies in an
outside fibre, namely `y`; and its remaining three relevant neighbours are
exceptional.  Therefore

```
q_y = - sum_(z exceptional, z~x) q_z.                       (16)
```

There are three summands, and each has squared norm 12 by (6).  The triangle
inequality gives

```
||q_y||^2 <= (3*sqrt(12))^2=108,
```

contradicting (15).  Hence the K4-support `Q=12` subbranch is impossible.

The exact arithmetic checks in this note are independently reproduced by
`scratch_theory_e72_k4_q12_analytic_audit.py`.  The separate diagnostic
`scratch_theory_e72_k4_q12_csp_probe.py` confirms that the pre-existing
local machinery reduces the `16,777,216` Q12 overlap matchings to 64 pair-
and-BP-feasible local graphs in two orbits; the proof above excludes them
all simultaneously.

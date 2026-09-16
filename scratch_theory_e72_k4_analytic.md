# Analytic exclusion of the dominant E72 K4-support row

Assume a putative `srg(99,14,1,2)` and use the independently proved root
choice with `S<=69`.  This note excludes the `E0=72` compression row whose
12 units of fibre deficit are placed as `delta=2` on all six edges of a
`K4`.  This is source row 134, partition 27, compression orbit 1 in the
current exact census; before local filtering it accounts for `101,593,088`
overlap completions.

The proof is analytic after the support row is fixed.  It uses no negative
SAT/CP-SAT result and does not enumerate those completions.

## 1. Gram geometry and exact block totals

Call the four core root groups `0,1,2,3`.  The exceptional fibres are the
six edges of their `K4`; all other 15 fibres are ordinary `C4`s.  The unique
Gram-circulation matrix on the six exceptional supports is

```
Z_FF = 4,
Z_FG = -2  if F and G meet,
Z_FG =  4  if F and G are opposite K4 edges.                (1)
```

Thus opposite support pairs carry the same Gram vector.  Write the three
vectors as `a,b,c`.  They satisfy

```
||a||^2=||b||^2=||c||^2=4,
<a,b>=<b,c>=<c,a>=-2,
a+b+c=0.                                                    (2)
```

The entry formula for `Z` gives the exact exceptional block totals

```
D_FG = 2  for meeting supports,
D_F,Fbar = 0  for opposite supports.                        (3)
```

An ordinary `C4` fibre has no edge to an overlapping fibre and block total
four to a disjoint fibre.  Its zero external-collision budget implies the
standard stronger statement: every vertex in the other fibre has exactly
one neighbour in that ordinary fibre.

## 2. The only possible fibre-type patterns

Fix an exceptional vertex `x`, let `a_x` be its internal fibre degree, and
let `z_x` be its number of neighbours in the unique opposite exceptional
fibre.  The ordinary-`C4` support/degree balance is

```
z_x = r+a_x-2,                                               (4)
```

where here `r=1` is the number of exceptional supports disjoint from its
own.  Equation (3) gives `z_x=0`, so (4) forces `a_x=1` at every vertex.
For completeness, (4) is just the outer-degree count.  Of the ten supports
disjoint from the support of `x`, `10-r` are ordinary and contribute one
neighbour each.  If `s_x` is the overlap-exceptional degree, the exact two
root-symbol port count is `2a_x+s_x=4`.  Substitution in
`12=a_x+s_x+z_x+(10-r)` gives (4).
Consequently each deficit-two fibre is one of only two kinds:

* `D`: its two diagonals, contributing two to `Q`;
* `O`: one of the two opposite-side matchings, contributing zero to `Q`.

The adjacent-side `P3+K1` shapes are impossible because their internal
degrees are not all one.

There is also a useful support-level closure rule for `O`.  If its internal
side matching shares endpoint group `g`, then every vertex has its remaining
no-common-symbol overlap port at `g`.  Hence its four cross-diagonal edge
incidences can go only to other `O` supports through `g`.  Each meeting block
has total at most two by (3), so both other K4 edges at `g` must be `O`, and
both corresponding blocks are completely cross-diagonal.  Thus every
oriented `O` edge forces the full three-edge star at its orientation endpoint.

The selected-root bound gives `Q=E0-S>=3`; here `Q` is even, so `Q>=4`.
Therefore at least two of the six fibres are `D`, and at most four are `O`.
The star-closure rule leaves exactly two possibilities up to relabelling:

```
all six are D                                      (Q=12),
three O form one K4 star and the other three are D (Q=6).   (5)
```

In the second case all three `O` matchings are oriented toward the common
star centre.  Indeed, a nonempty `O` set contains a forced star; adding one
more edge would force a second star and at least five `O` edges.

## 3. A uniform local consequence of both patterns

Besides (4), the ordinary-`C4` group balance says the two overlap neighbours
of `x` introduce the two different core groups complementary to its support.
Here is a direct derivation.  For any root group `g` outside the support of
`x`, the two signed root neighbours in group `g` are both nonadjacent to
`x`.  Each has two common neighbours with `x`, all outer, so exactly four
neighbours of `x` have a fibre support containing `g`.  There are four
disjoint support fibres containing `g`.  If `t_g` of these are exceptional,
their `4-t_g` ordinary counterparts already contribute one neighbour each;
ordinary overlapping fibres contribute none.  Hence the number of
exceptional neighbours whose supports contain `g` is exactly `t_g`.  In the
K4 row, for each of the two complementary core groups `t_g=1`; the sole
disjoint exceptional block is empty, so one overlap neighbour introduces
each complementary group.

For a `D` fibre these two overlap edges are its two side-symbol edges.  For
an `O` fibre one is its remaining side-symbol edge and one is the cross-
diagonal edge at the star centre.  In either case they use the two different
endpoints of the support.  Their two supports are therefore opposite K4
edges and carry the same Gram vector.

Give every vertex in exceptional fibre `F` the vector `v_F` of (2), and
every ordinary-fibre vertex zero; call the resulting 84-vertex vector
`c_0`.  Put

```
q=Bc_0,                                                      (6)
```

where `B` is the outer adjacency matrix.  Every exceptional vertex has one
internal neighbour in its own vector class and two overlap neighbours in
one other class.  Hence

```
q_x = a+2b, or a+2c, and cyclic variants,
||q_x||^2=12.                                               (7)
```

It also has at most one neighbour in every individual exceptional fibre.

Matrix (1) has nonzero eigenvalues `12,12`, so its range is the normalized
compression eigenspace with eigenvalue zero.  Gram circulation makes `c_0`
orthogonal to the all-one and root-incidence spaces.  Applying the outer SRG
identity

```
B^2+B=12I+2J-PP^T
```

coordinate by coordinate gives

```
(B+I)q=12c_0.                                               (8)
```

## 4. Collision equality

For an outer vertex `x` and exceptional fibre `F`, put

```
n_F(x)=|N(x) intersect F|,
C=sum_x sum_F binom(n_F(x),2).                              (9)
```

Both allowed deficit-two shapes in (5) require exactly six outer common-
neighbour witnesses for their six internal vertex pairs:

* for `D`, two adjacent diagonals and four nonadjacent sides contribute
  `2*1+4*1=6` after inner witnesses are removed;
* for `O`, two adjacent sides, two nonadjacent sides and two nonadjacent
  diagonals contribute `2*0+2*1+2*2=6`.

Thus

```
C=6*6=36.                                                   (10)
```

The last sentence of Section 3 says exceptional vertices contribute zero
to `C`.

Fix one of the three opposite exceptional pairs `F,Fbar`.  By (3), all 16
cross-pairs are nonadjacent and have no inner common neighbour.  Hence

```
sum_x n_F(x)n_Fbar(x)=16*2=32.                              (11)
```

Exactly eight witnesses in (11) are exceptional.  For each of the four
other exceptional fibres `G`, its four vertices split between the two other
opposite-edge classes.  The blocks from `G` to `F` and `Fbar` have two edges
each.  A vertex whose two overlap supports choose this class supplies two
of those four incidences, and any other vertex supplies zero.  Exactly two
vertices of `G`, hence eight over the four choices of `G`, witness the pair.

A spoke support (one core and one outside group) cannot be disjoint from
both members of an opposite pair.  Therefore all remaining 24 witnesses in
(11) occur at the 12 vertices of the three outside fibres:

```
sum_(x outside) n_F(x)n_Fbar(x)=24.                          (12)
```

Over those 12 vertices write `u_x=n_F(x)`, `v_x=n_Fbar(x)`.
Each exceptional--outside block has total four, so
`sum u=sum v=12`.  Combining this with (12) gives the exact identity

```
sum_x (u_x-v_x)^2
 =2( sum_x[binom(u_x,2)+binom(v_x,2)]-12 ) >=0.              (13)
```

Summing (13) over the three opposite pairs shows that outside vertices
contribute at least 36 to `C`.  Equality (10) and zero exceptional
contribution force

```
* every spoke contributes zero to C;
* n_F(x)=n_Fbar(x) at every outside vertex.                  (14)
```

## 5. Forced outside concentration

A spoke vertex has exactly three exceptional neighbours.  Its three
possible exceptional fibres are one from each vector class.  The first part
of (14) makes all three occupancies one, and therefore

```
q_x=a+b+c=0             on every spoke.                      (15)
```

An outside vertex has exactly six exceptional neighbours.  By the second
part of (14), write its equal paired occupancies as `m_1,m_2,m_3`; then

```
m_1+m_2+m_3=3.                                             (16)
```

The possible unordered profiles `111,210,300` contribute respectively
`0,2,6` to `C`.  If their counts among the 12 outside vertices are
`N_111,N_210,N_300`, equations (10) and (14) give

```
N_111+N_210+N_300=12,
2N_210+6N_300=36.
```

Consequently `N_300>=3`.  At a `300` vertex `y`, both fibres of one opposite
class occur three times, so

```
q_y=6a, 6b, or 6c,                 ||q_y||^2=144.            (17)
```

## 6. Contradiction at an adjacent spoke

The outside ordinary fibre of `y` is disjoint from four spoke fibres.
Every ordinary--ordinary disjoint block is a perfect matching, so choose a
spoke neighbour `x` of `y`.  Equations (8) and (15), with `c_0(x)=0`, give
`(Bq)_x=0`.

All internal and spoke neighbours of `x` have `q=0`.  Its support is
disjoint from exactly one outside support, so `y` is its unique outside
neighbour.  The only remaining nonzero terms are its three exceptional
neighbours.  Therefore

```
q_y=-sum_(z exceptional, z~x) q_z.                           (18)
```

There are three summands, each of squared norm 12 by (7).  The triangle
inequality yields

```
||q_y||^2 <= (3 sqrt(12))^2=108,
```

contradicting (17).  This excludes the entire K4-support compression row,
including all of its `Q=6` and `Q=12` local branches.

`scratch_theory_e72_k4_analytic_audit.py` independently verifies the finite
support closure, Gram arithmetic, collision profiles, and final strict norm
inequality using only the Python standard library.  The local artifacts
`scratch_theory_e72_k4_q6_probe.json` and
`scratch_theory_e72_k4_q12_csp_probe.json` are consistent cross-checks, but
are not premises of the proof.

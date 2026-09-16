# Edge fibre codegrees: triangle moments, exact integer bounds, and boundary

Status: `EDGE_FIBRE_CODEGREE_MOMENT_INDEPENDENT_AUDIT_PASS`.

The producer is `scratch_theory_edge_fibre_codegree_moments.py`; the
independent replay is
`scratch_theory_edge_fibre_codegree_moments_audit.py`.  They use frozen
audited triangle-flag, augmented-relation, global fibre-Gram, and order-eight
shadow artifacts.  No order-eight classes are regenerated.

## 1. The edgewise identity

Every graph edge `e` belongs to a unique triangle `T=T(e)`.  Recall

```text
q(T)=12-a3(T),
```

where `a3(T)` is the number of triangles forming a triangular prism with
`T`.  Let

```text
p_e = number of roots at which e is a side edge of a fibre,
d_e = number of roots at which e is a diagonal edge of a fibre,
H_e = H_xy for e=xy.
```

In one triangular prism, every one of its six triangle edges is the side
edge for exactly one root in the opposite triangle.  Direct enumeration of
the nine-edge prism verifies this six-to-six bijection.  Hence

```text
p_e=a3(T(e))=12-q(T(e)).                                (1)
```

The side and diagonal positions partition the roots whose fibre contains
both endpoints of `e`, so

```text
H_e=p_e+d_e=12-q(T(e))+d_e.                             (2)
```

For the flag `(T,u)` opposite `e=T\{u}`, an entry equal to two in the
corresponding column of the old collapsed flag matrix `Y` is exactly a root
at which `e` is a fibre diagonal.  Since that column has sum `q(T)` and all
its entries lie in `{0,1,2}`,

```text
0<=d_e<=floor(q(T(e))/2).                               (3)
```

This proves conceptually, and sharply,

```text
H_e<=12.                                                (4)
```

The finite audit checks all 49 pairs
`0<=q<=12, 0<=d<=floor(q/2)`, the triangular prism, and the intrinsic
root/chord roles of the canonical `H_delta` mask `120568`.

Summing (1)--(2) gives, with `D_*=sum_r D(r)`,

```text
sum_e p_e = 6P = 8316-2n3,
sum_e d_e = D_* = n3-z11/4,
sum_e H_e = T = 8316-2n3+D_*.                           (5)
```

An optional parity refinement is also immediate.  If `O_q` is the number
of triangles with odd `q(T)`, then the three edges of each triangle give

```text
D_* <= n3-(3/2)O_q.                                    (6)
```

The complete scalar range of the second moment before graph-specific
compatibility is also explicit.  Here `n3` is a multiple of three,
`0<=n3<=4158`, and with `s=2n3/3`,

```text
sqmin(s,231) <= Q2 <= sqmax_cap12(s,231),
Q2 congruent to s modulo 2.                             (6a)
```

All 1,387 possible values of `n3` were checked; at `n3=4158`, (6a) forces
`q(T)=12` for every triangle and `Q2=33264`.

## 2. Exact formula and moment bounds for `K_edge`

Put

```text
Q2=sum_T q(T)^2,
K_edge=sum_(e edge) binom(H_e,2).
```

Expanding (2), using `sum_T q(T)=2n3/3`, gives the exact formula

```text
K_edge = 45738-23n3+(3/2)Q2
       + sum_e [(12-q(T(e)))d_e+binom(d_e,2)].           (7)
```

Let `cmin(S,m)` be the minimum of `sum binom(x_i,2)` over `m`
nonnegative integral cells of total `S`.  The 49-state table proves

```text
binom(d_e,2)
 <= (12-q)d_e+binom(d_e,2)
 <= 10d_e-3binom(d_e,2).
```

Consequently

```text
K_edge >= 45738-23n3+(3/2)Q2+cmin(D_*,693),             (8)

K_edge <= 45738-23n3+(3/2)Q2
                         +10D_*-3cmin(D_*,693).          (9)
```

Two other useful upper bounds follow from (3) and from the augmented flag
column.  Writing `cmax_c(S,m)` for the packed maximum with cell cap `c`,

```text
K_edge <= cmax_12(T,693),                               (10)
K_edge <= 45738-D_*,                                    (11)
K_edge <= 45738+n3-(3/2)Q2+cmax_6(D_*,693).             (12)
```

For (12), one augmented column has `p=12-q` bad/prism occurrences and `q`
good occurrences.  Its bad-containing pair count is
`binom(p,2)+pq`; meanwhile

```text
binom(p+d,2) <= binom(p,2)+pq+binom(d,2).
```

Summing the first two terms gives the already audited bad-mate identity
`45738+n3-3Q2/2`, and packing the last term gives (12).

## 3. The exact three-edge bundle refinement

The three edges of one triangle share the same `q`.  This adds a small but
exact integer refinement beyond treating all 693 edges independently.  If
`B(T)` denotes the minimum possible `K_edge` at fixed total `T` in the local
`(q,d)` relaxation, then

```text
B(T)=cmin(T,693),                         0<=T<=7623,
B(T)=cmin(T,693)+[2,1,0 by (T-7623) mod 3],
                                           7624<=T<=8313,
T=8314,8315 is impossible,
B(8316)=693 binom(12,2).                                (13)
```

The bracket means add 2 for residue 1, 1 for residue 2, and 0 for residue
0.  The reason is simple: `H_e=12` forces `q=0,d=0`, so all three edges of
that triangle have value 12.  Thus the number of 12-valued edges is a
multiple of three.  Conversely, explicit triangle types with `q=0` and
`q=2`, plus the states `d=(0,0,1),(0,1,1),(1,1,1)`, attain every value in
(13).  For `T<=7623`, balanced values `a,a+1` are obtained directly from
`q=12-a` and `d in {0,1}`; one harmless `q` parity flip supplies the global
triangle-pair parity.

All 8,317 values were checked.  Exactly 460 reachable `T` values have a
strict improvement over unbundled `cmin`, beginning with `T=7624` (extra
2) and ending with `T=8312` (extra 1).

## 4. Order-eight shadow connection

For edge `e`, the augmented column `Yhat[:,e]` contains `p_e` prism
singleton roots, `q(T)` good flag occurrences, and `d_e` doubled roots.
It therefore has off-diagonal root-pair mass

```text
66-d_e.
```

The roots counted by `H_e` are precisely the prism roots together with the
doubled roots.  Every pair of such roots contributes at least one to the
corresponding augmented Gram entry.  Splitting according as the two roots
are adjacent or nonadjacent gives

```text
K_edge^adj <= beta_e,
K_edge^non <= beta_n,
beta_e+beta_n=45738-D_*.                                (14)
```

Here `beta_e,beta_n` are exactly the sparse frozen order-eight shadow
functionals already recorded in
`scratch_theory_root_yyt_order8_shadow.json`.  The domination is only
one-sided: the shadow additionally counts singleton good roots which are
not fibre roots for `e`.  It supplies no lower bound on `K_edge` without a
new mate/double-root selector or an order-nine extension statistic.

## 5. Combining with the global collision floor

Use (13) on the edge relation and ordinary integer balancing on the 4,158
nonedges:

```text
K_fb >= B(T)+cmin(12474-T,4158).                         (15)
```

Exact minimization leaves

```text
min K_fb = 10395,
```

with the same equality interval `1386<=T<=2079` as before.  Thus the new
edge structure sharpens high-`T` profiles but does not improve the absolute
collision bound.

Nor can these scalar/order-eight-shadow consequences force `T>0` or
`n3<4158`.  The exact boundary point is

```text
n3=4158, z11=16632, q(T)=12 for all 231 triangles,
Q2=33264, D_*=0, T=0, K_edge=0.                         (16)
```

The frozen Wave159 order-eight pseudowitness satisfies all augmented shadow
inequalities at (16).  The integer PSD control
`H0=84I+3(J-I-A)` places all collision mass on nonedges and has

```text
K_nonedge=4158 binom(3,2)=12474>=10395.                 (17)
```

These are exact relaxation controls, not a claimed graph or binary
rooted-fibre factorization.

## Conclusion

The proposed identity and bound are correct:
`H_e=12-q(T(e))+d_e` and `2d_e<=q(T(e))`.  They explain the sharp edge
codegree cap 12 and yield exact first/second-moment bounds plus the small
three-edge bundle refinement (13).  They do not force positive `T` or a
strict upper bound on `n3`.  Further strength must couple the selected
prism/double-root set to the order-eight shadow from below, or constrain the
nonedge fibre-collision mass; neither statistic is present in the current
scalar projection.

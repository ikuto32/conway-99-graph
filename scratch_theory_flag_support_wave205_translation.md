# Triangle-flag support versus the Wave205 fourth-trace frontier

Status: `EXACT_BRIDGE_AND_SCOPED_T0_BOUNDARY_COMPLETE`.

Assume a putative `srg(99,14,1,2)`.  This note keeps the triangle-flag
notation of `scratch_theory_root_flag_union.md` and compares it with the
independently verified Wave205 variables.  The outcome is negative but
sharp: Wave205 determines the side term `S(r)`, not the flag-collision term
`D(r)`.  Its currently verified fourth-order factorization therefore gives
no pointwise lower bound on

```text
E0(r)=S(r)+D(r)=84-|supp Y[r,*]|.
```

## 1. The two matrices retain different information

Let `Q` be the `693 by 231` flag-to-triangle incidence, `F` the `693 by 99`
flag-to-point incidence, and `N=F^T Q` the point-to-triangle incidence.  Let
`X` be the unmatched-endpoint flag relation and

```text
K2=Q^T X Q,                 Y=F^T X.
```

Wave205's integer two-count matrix is

```text
t=N K2 N^T
 =F^T (Q Q^T) X (Q Q^T) F.                            (1)
```

Thus `t` replaces each unmatched flag at either end of an `X` edge by all
three vertices of its triangle.  One two-cross triangle pair contributes
nine point pairs to `t`: the two matching graph edges and seven graph
nonedges.  Only one of those seven is the unmatched-endpoint pair retained
by `F^T X F`; `Y` retains the target flag as well.  Consequently `t` is not
`YY^T`, nor does it determine the row support of `Y`.

## 2. Exact pointwise row bridge

Put

```text
u(r)=sum_(T containing r) q(T)=84-S(r).
```

For every source triangle through `r`, each of its three flags has `q(T)`
two-cross partners.  Hence there are `3u(r)` incident `K2` pairs: `u(r)`
leave `r` unmatched and `2u(r)` match `r`.  An unmatched source point is
nonadjacent to all three vertices of the target triangle.  A matched source
point is adjacent to one and nonadjacent to two.  Therefore

```text
sum_(y adjacent r)    t[r,y] = 2u(r)=2(84-S(r)),        (2)
sum_(y nonadjacent r) t[r,y] = 7u(r)=7(84-S(r)).        (3)
```

At the prism-free endpoint `S(r)=0`, these are `168` and `588`.  Wave205's
`t_xy>=6` and average seven are consistent with (3), but they contain no
`D(r)`.  In fact

```text
E0(r)=84-(1/7) sum_(y nonadjacent r)t[r,y]+D(r).        (4)
```

Thus an `E0(r)>=L` theorem obtained through this bridge still has to prove
the genuinely flagged collision inequality

```text
D(r) >= L-84+(1/7) sum_(y nonadjacent r)t[r,y].         (5)
```

Neither `t_xy>=6` nor its exact row average supplies (5).

There is a valid collision comparison in the opposite direction.  A doubled
entry `Y[r,(U,u)]=2` supplies one pair of `K2` incidences inside `t[r,y]` for
each of the three vertices `y` of `U`.  Hence

```text
3D(r) <= sum_(y nonadjacent r) binom(t[r,y],2).          (6)
```

This upper-controls `D(r)` from a second moment of `t`; it cannot prove
`S(r)+D(r)` large.

## 3. Why the fourth-trace factorization does not repair the loss

Wave205 works over `F_3` and proves

```text
H4=U K_D U^T,                   rank_F3(U)=99.           (7)
```

Here a column of `U` indexed by two distinct triangles through one point is
already the corresponding unit vector.  Full rank is therefore an
incidence theorem and gives no compression of the 99 root rows.  Moreover
`H4` is a finite-field fourth-trace matrix, not the real positive-semidefinite
Gram `YY^T`; there is no order relation between them.

The complete Wave205 two-star census reinforces the boundary.  A full-rank
local module exists at `t=6`, and at `t=7` all fourth traces `0,1,2` occur.
So even fixing the scalar two-count, pair trace, rank, and local code distance
does not define a scalar fourth-order quantity that can substitute for the
missing flag collision.

The useful Wave205 object is therefore its named missing localizer,

```text
K_D restricted to row(U),
Q_triangle o (D S_r D),
w_TU=N(D_T o D_U).
```

For the present goal it would have to be refined by the unmatched slots and
then shown to lower-bound `D(r)`.  No such flagged restriction or inequality
is presently verified.

## 4. A new exact `T=0` relaxation control

`scratch_theory_flag_support_endpoint_control.py` constructs a compact
control on

```text
points:       (a,j) in Z_3 x Z_33,
triangles:    T_(h,i)={(a,i+a*h):a=0,1,2},
              h=0,...,6, i in Z_33.
```

The 231 triples are distinct and linear; every point is in seven triples,
and their shadow is 14-regular.  A deterministic flag graph `X` has degree
12, its formal triangle quotient `K2` is simple and 36-regular, and its 99
seven-flag root blocks have disjoint `X` neighborhoods.  Exactly,

```text
Y=F^T X is binary,
every Y row has sum and support 84,
every Y column has sum 12,
formal E0(r)=0 for all 99 rows.                          (8)
```

The control also defines a symmetric integral matrix `M` with every row
profile

```text
M values (-1,0,+1,4): (36,162,32,1),
M 1=0,             diag(M^2)=84,
tr(M^2)=21 tr(M),
K2=(M o M o M+M o M-2M)/2-36I.                         (9)
```

It therefore closes a substantial relaxation: root/triple degrees,
linearity, flag matching degrees, binary `Y`, all support margins, the
formal endpoint relation profile, the Schur selector, and the scalar
projector row moments do not imply even `E0(r)>=1`, much less 71 or 72.

The scope wall is explicit.  The constructed `M` fails `M^2=21M` in 49,896
entries and fails the actual incidence transport

```text
N M N^T=27I-9A+J.                                      (10)
```

Its formal `K2` is not the actual two-cross-edge relation of its non-SRG
shadow: only 660 of the 4,158 formal `K2` edges have exactly two shadow
cross edges.  Its shadow also fails `lambda=1,mu=2`, and its Wave205
nonedge `t` row sums are `658,664,666`, not 588.  It is not a graph
candidate.  The independent audit reconstructs all of these pass/fail gates
without importing the construction script.

This control is complementary to the verified Wave205 hostile control.
Wave205 realizes a rank-11 square-zero centered Gram and a coupled
`99 by 231` linear incidence but does not impose the 32-regular selected
relation or an unmatched flag lift.  The new control realizes the latter
flag/support/Schur-row data but not the full projector or SRG transport.
Their currently missing intersection is exactly the graph-specific global
compatibility that a support bound must use.

A direct read-only projection of the frozen Wave205 certificate confirms
this separation.  In both hostile realizations, the degree of the
centered-Gram value-two relation ranges over

```text
21,24,30,33,39,48,66,96,108,
```

and it has 5,580 edges, rather than endpoint degree 36 and 4,158 edges.
Thus those controls cannot be endowed with the required `K2` quotient before
one even asks for an unmatched lift `X`.  This is a scope check, not a defect
in the Wave205 theorem.  A separate audit reconstructs the ambient Gram
matrix, the complete value-two degree histogram, and the 5,580-edge count
directly from the frozen certificate, without importing the projection
producer.

## 5. The cyclic repair is exactly closed

The control is translation invariant on its 231 triangle labels.  A rational
circulant rank-44 projector has Galois-stable Fourier support.  Exhausting
the cyclotomic orbit sizes for `Z_231` leaves the unique rank-44 union of
exact character orders

```text
3,11,21,33                 with sizes 2+10+12+20=44.
```

For `M=21P`, its exact Ramanujan-sum off-diagonal entries have distribution

```text
0^132, 1^10, (-3/11)^60, (-7/11)^22, (30/11)^6.
```

Thus no rational circulant repair makes `M` integral.  This excludes only
the cyclic repair, not a noncirculant endpoint projector.

## 6. Consequence for the lower-bound program

No pointwise support bound `|supp Y_r|<=13` or `<=12` follows from the
checked lanes.  A viable next lemma must mix all three pieces that remain
separate:

1. the off-diagonal projector equation and transport (10);
2. the *actual* two-cross matching and its unmatched-slot lift `X`; and
3. a collision-sensitive, preferably pointwise, restriction of the
   Wave205 kernel/localizer that lower-bounds `D(r)` as in (5).

This is a sharper boundary than another scalar `t` or fourth-trace moment:
those quantities recover `S(r)` after triangle inflation, while the desired
lower bound lives in the information discarded by that inflation.

## Reproduction artifacts

```text
scratch_theory_flag_support_endpoint_control.py/.json
scratch_theory_flag_support_endpoint_control_independent_audit.py/.json
scratch_theory_flag_support_wave205_bridge_audit.py/.json
scratch_theory_flag_support_wave205_control_projection.py/.json
scratch_theory_flag_support_wave205_control_projection_independent_audit.py/.json
scratch_theory_flag_support_cyclic_projector_search.py/.json
scratch_theory_flag_support_cyclic_projector_independent_audit.py/.json
```

No `submission.txt`, graph, endpoint exclusion, or Conway-99 resolution is
claimed.

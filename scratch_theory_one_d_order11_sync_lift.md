# Restricted one-D order-11 synchronization lift

Status: `ONE_D_ORDER11_SYNCHRONIZATION_LIFT_INDEPENDENT_AUDIT_PASS`.

Producer:

```text
scratch_theory_one_d_order11_sync_lift.py
scratch_theory_one_d_order11_sync_lift.json
```

Independent replay:

```text
scratch_theory_one_d_order11_sync_lift_audit.py
scratch_theory_one_d_order11_sync_lift_audit.json
```

No general order-11 graph class was generated.

## 1. The forced union

Use the canonical roles

```text
D root                 0
D source triangles     012, 034
other root/source      5 / 567
target triangle        8,9,10
target mate/edge       8 / 9--10.
```

The diagonal event forces the two aligned X matchings

```text
1--9, 2--10, 3--9, 4--10.
```

The other event is either

```text
G: 6--9, 7--10,
P: 6--9, 7--10, 5--8.
```

There are no edges between `{1,2}` and `{3,4}` because the neighbourhood of
root 0 is `7K2`.  Every remaining edge lies between source `567` and one of
`012,034`.  For either pair of disjoint source triangles the local
lambda/mu upper bounds force these cross edges to be a partial matching.

A `3 x 3` partial matching has 34 possibilities.  The shared edge `0--5`
belongs to 7 and is absent from 27.  Its membership must agree in the two
matchings, so the complete candidate count per state is

```text
27^2+7^2 = 778.                                          (1)
```

The forced role group has order four: swap the two D source triangles,
and/or simultaneously flip `9,10` and all three matched source pairs.

Exact pair-upper enumeration gives

| other state | feasible labelled patterns | rooted role types | edge/nonedge types |
|---|---:|---:|---:|
| G | 50 | 17 | 4 / 13 |
| P | 18 | 8 | 4 / 4 |

Every representative, optional edge set, exact order-11 mask, orbit size,
and deletion image is stored in the JSON.

## 2. Synchronizing the two order-9 occurrences

Let `Z_t^b` count a physical rooted union of type `t`, with the D root on
the left and the other root in state `b in {G,P}`.  Deleting the two
non-root vertices of one D source triangle retains the other D occurrence
and produces one marked order-9 cell.  Hence

```text
L_i,Db = sum_t c_it^b Z_t^b,                              (2)
```

where every column of `c^b` has sum two.  This is the missing Cartesian
packet synchronization:

```text
sum_i L_i,Db = 2 sum_t Z_t^b                              (3)
```

separately for adjacent and nonadjacent root pairs.  For `b=P`, the two
order-9 occurrence weights `1/2` therefore recover exactly one selected
physical pair.  Reversing the ordered roots gives the `GD` and `PD`
equations through the explicit row-transpose map in the artifact.

The connection to the frozen 916 columns is through the previously proved
11 deletion rows

```text
sum_ab L_i,ab = o_i x8[K_i].                              (4)
```

Thus (2) connects directly to the new marked order-9 variables and (4)
connects those variables to the nine nonzero frozen order-8 columns.

## 3. Exact dimensions, zero cells, and integer lattice

For D-left/G-right, `c^G` is `11 x 17`, has rational rank 8, and has active
rows

```text
E019O0 E515O0 E561O0 N057O0 N060O0 N442O0 N525O0 N593O0.
```

For D-left/P-right, `c^P` is `11 x 8`, has rational rank 6, and has active
rows

```text
E019O0 E515O0 E561O0 N060O0 N525O0 N593O0.
```

Together with left/right transpose, synchronization forces ten cells which
survived the order-9 pair-upper test to zero:

```text
DG: N057O1, N109O0, N442O1
GD: N057O0, N109O0, N442O0
DP: N057O1, N442O1
PD: N057O0, N442O0.                                     (5)
```

The full-rank-minor gcd is 4 for both matrices.  Their ranks fall by exactly
two modulo 2 and not modulo 3.  The Smith invariants on their active rows
are therefore

```text
G: 1,1,1,1,1,1,2,2,
P: 1,1,1,1,2,2.
```

Consequently the exact integer column lattice is characterized by the zero
rows plus two parity conditions: the sum of active edge-row occurrences is
even and the sum of active nonedge-row occurrences is even.  These are the
two relation-wise forms of (3), and are sufficient, not merely necessary,
for integer lattice membership.

## 4. Exact nonnegative/Farkas cone

The incidence columns also permit a complete elementary rational cone
description.  Apart from nonnegativity and the zero rows, the only
nontrivial facets for D-left/G-right are

```text
L[E019O0,DG] >= L[E515O0,DG],
L[N057O0,DG]+L[N060O0,DG] >= L[N525O0,DG].               (6)
```

For D-left/P-right they are

```text
L[E019O0,DP] >= L[E515O0,DP],
L[N060O0,DP] >= L[N525O0,DP].                            (7)
```

Completeness is direct from the generator list.  Every active coordinate
except `E515O0,N525O0` has a doubled unit column.  `E515O0` occurs only with
`E019O0`; `N525O0` occurs with `N057O0` or `N060O0` in (6), and only with
`N060O0` in (7).  After allocating those exceptional coordinates, all
remainders use doubled unit columns.  The independent audit reconstructed
every generator and checked this description.

## 5. T=0 boundary

Since `T=S_*+D_*`, the face `T=0` has neither P nor D states.  Assign all
order-8 deletion mass to `GG`, all other marked order-9 cells to zero, and
all 25 one-D variables to zero.  The exact nonnegative H9 solution from the
preceding lift closes the all-G order-9 equations.  This assignment satisfies
(2), (4), all pair-upper zero cells, (6)--(7), and the coarse state Gram

```text
diag(99792,0,0) >= 0.
```

For a wholly integral cone witness, multiply the Wave159 rational endpoint
and its H9 extension by

```text
1035043883553254636429284757016341633342.
```

All resulting extension variables and normalization coordinates are
integers, while every one-D variable and `T` remain zero.  This is an integer
point on the homogenized relaxation cone, not a claim that it is one
99-vertex graph.

Therefore Farkas duality closes this lane sharply: no nonnegative linear
combination of the frozen deletion rows, order-9 pair-upper zeros, one-D
synchronization equations, or cone facets can prove `D_*>0` or `T>0`, since
the displayed feasible point has both equal to zero.

The new exact information is (2), the ten zero cells (5), the parity
lattice, and facets (6)--(7).  A positive lower bound needs either two-D
order-13 packet synchronization or a separate global constraint which
prevents the all-G allocation.  No `submission.txt` was created.

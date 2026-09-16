# Independent audit of the E72 fibre-variance kernel

Let `M` be the `84 x 21` indicator matrix of the four-vertex outer fibres,
`B` the outer adjacency matrix, `P` the outer-to-root-neighbour incidence
matrix, `L` the unsigned `21 x 7` incidence matrix of the supports, and

```
C=M^T B M.
```

For `d=Mc`, the exact identities

```
M^T M=4I,
1^T Mc=4 sum(c),
||P^T Mc||^2=8||L^T c||^2,
d^T B d=c^T C c
```

and `B^2+B=12I+2J-PP^T` give

```
||BMc||^2
 =48||c||^2+32(sum c)^2-c^T Cc-8||L^Tc||^2.       (1)
```

The orthogonal projection of `BMc` onto the fibre-constant space is
`M(Cc/4)`, whose squared norm is `||Cc||^2/4`.  Therefore

```
sum_F sum_(x in F) ((BMc)_x-(Cc)_F/4)^2 = c^T Kc,
K=48I+32J-C-8LL^T-C^2/4.                            (2)
```

If a macro is realized by an actual graph and `c` lies in the exact kernel
of its `K`, the left side of (2) is a sum of squares equal to zero.  Hence

```
(BMc)_x=(Cc)_F/4 for every x in fibre F.             (3)
```

This implication needs neither a numerical eigenvalue calculation nor an
assumption that a candidate macro is realizable; realizability is only the
hypothesis under which its formal compression `C` is the graph's actual
compression.

The independent standard-library audit reconstructs every one of the 162
passing Gram-profile rows (160 canonical macros, with the parametric source
332 contributing three profiles), recomputes `C` and the integer-scaled
matrix

```
4K=192I+128J-4C-32LL^T-C^2,
```

and obtains the same exact ranks and histograms as
`scratch_theory_e72_equitable_kernel_census.json`.  It uses its own rational
Gaussian elimination and does not import the census implementation.

There is an important distinction in interpreting the dimensions.  Relative
only to the seven columns of `L`, all 160 macros have 10--13 further kernel
directions.  However, every ordinary-`C4` unit vector is itself a kernel
direction and its pointwise equation is already part of the existing local
model.  After adjoining those ordinary unit vectors, 132 profile rows have
no novel direction, 28 have one, and two have two.  Thus the new kernel rule
strictly strengthens 30 of 162 Gram profiles, not all 160 macros.

For source 133, all five macros have kernel dimension 19 and baseline rank
19, so their novel dimension is zero.  The signed vector used in
`scratch_theory_e72_k23_balance.md`,

```
c_d=+1 on A_i={0,i}, -1 on B_i={1,i}, 0 otherwise,
```

is nevertheless a useful kernel vector.  It decomposes as

```
c_d = L(1,-1,0,0,0,0,0)^T + e,
e=-1 on {0,5},{0,6}, +1 on {1,5},{1,6}, 0 otherwise,
```

where `e` is a combination of ordinary-fibre unit directions.  Formula (3)
then gives means `-3` on `{0,5},{0,6}`, `+3` on `{1,5},{1,6}`, and zero on
all other fibres.  This is exactly the pointwise `Bd=3e` saturation derived
there by the quadratic-form argument.


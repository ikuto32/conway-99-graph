# Pointwise spectral-projector leverage above the E71 defect Gram

Status: `INDEPENDENT_E71_PROJECTOR_LEVERAGE_AUDIT_PASS`.

This is a one-root necessary condition for a hypothetical
`srg(99,14,1,2)`.  It strengthens the rank-three defect-Gram row catalogue
without enumerating another `E0` layer and without regenerating any of the
frozen order-eight assets.  It removes nine integer row patterns from the
sharp source-724 boundary, but by itself does not exclude that macro or prove
an `E0` lower bound.

## Fixed cycle-space projectors

At a root, identify the 84 outer vertices with the edges of
`K14-7K2`.  Let `L` be their unsigned endpoint-incidence matrix and let `R0`
be the involution interchanging the two root-neighbour labels in each of the
seven pairs.  The exact-label line graph is `LL^T-2I`, and the rooted SRG
equations give

```text
B L = 2J-L(I+R0).
```

Put

```text
H = I-L(L^T L)^(-1)L^T.
```

This is the rank-70 cycle-space projector.  Since

```text
(L^T L)^(-1) = 11I/120-J/240+R0/120,
```

every diagonal of `H` is `5/6`.  The displayed action of `B` also gives
`diag((I-H)B)=0`.  On the cycle space, `B` has only eigenvalues `3,-4`, so

```text
E4 = H(3I-B)/7,       E3=H-E4
```

are the corresponding spectral projectors, with constant coordinate
diagonals

```text
diag(E4)=5/14,        diag(E3)=10/21.                 (1)
```

## The leverage inequalities

Let `U` be the normalized `84 by 21` coarse-fibre incidence, let
`K` be the rank-14 projector onto the cycle space of the coarse `K7` edge
coordinates, and use the established notation

```text
A0=U^T B U=C/4,
W=(I-UU^T)BU=R/8,
Z=C0-C,
R^T R=4Z(28I-Z).
```

The `E4` compression and cross block are exactly

```text
U^T E4 U=Z/28,
(I-UU^T)E4 U=-R/56.                                  (2)
```

For a coordinate `x` in fibre `G`, write `r=R[x,*]` and let `Z_G` be row
`G` of `Z`.  The standard-coordinate row of `E4 U` is

```text
v_x=(Z_G-r)/56.
```

The orthogonal projector onto `range(E4 U)` is

```text
(E4 U)(U^T E4 U)^+(E4 U)^T <= E4.
```

Taking its `x` diagonal and using (1) gives the pointwise rational
inequality

```text
(Z_G-r) Z^+ (Z_G-r)^T <= 40.                          (3)
```

Keeping the whole row `Z_G-r` is essential.  The superficially stronger
expression `r Z^+ r^T<=40` compares only the bottom cross block with the
wrong coordinate diagonal and is not valid.

The complementary projector gives a second exact condition.  Its
compression is `K-Z/28`, its cross block is `R/56`, and therefore

```text
s (28K-Z)^+ s^T <= 160/3,
s=28K_G-Z_G+r.                                        (4)
```

Equations (3)--(4) are leverage-score bounds: they retain the actual
coordinate placement of an integer defect row, which is lost from the
aggregate equality `R^T R=4Z(28-Z)`.

## Exact E71 evaluation

The already frozen rank-three probe contains three profiles and 219
integral row patterns.  Exact rational evaluation gives:

| profile | maximum in (3) | violations of (3) | maximum in (4) | violations of (4) |
|---|---:|---:|---:|---:|
| source 724, state 1 | `208/3` | 9 | `8440/267` | 0 |
| source 2601, state 1 | `32` | 0 | `6958/285` | 0 |
| source 2601, state 4 | `32` | 0 | `6958/285` | 0 |

All nine new exclusions occur in source 724.  They are:

```text
(1,3): pattern 3
(1,4): patterns 1,6
(1,5): pattern 0
(2,3): patterns 2,7,9
(2,4): patterns 0,3
```

Their left sides in (3) are `124/3`, `52`, or `208/3`, all strictly above
40.  The source-2601 rows were already excluded by the kernel-port theorem;
their passage here is a useful independence check.

## Boundary

This calculation proves a reusable pointwise projector condition and removes
nine rows before any common-neighbour search.  It has not yet shown that
every one of the 128 source-724 rank-three fibre configurations uses one of
those rows.  Until that configuration-level intersection is checked, no
source-724 coverage and no `E0=71` layer is declared excluded.

Artifacts:

```text
scratch_theory_e71_projector_leverage_probe.py/.json
scratch_theory_e71_projector_leverage_probe_audit.py/.json
```

The independent audit imports no producer code, reconstructs the rank-14
coarse-cycle projector, recomputes all 438 rational quadratic forms, and
checks the fixed diagonals in (1).  No graph, `submission.txt`, or Conway-99
resolution is claimed.

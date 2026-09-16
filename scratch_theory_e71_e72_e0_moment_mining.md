# E71/E72 E0 moment and Gram mining

Status: `EXACT_E71_E72_E0_MOMENT_MINING_COMPLETE`.

## Rootless interpretation of the missing diagonal term

A selected diagonal edge in a root fibre determines an induced seven-vertex
graph `H7`: two root triangles sharing their root, complementary spokes to
the diagonal endpoints, and the diagonal edge itself.  Its induced degree
sequence is `(4,3^6)`, so the root is unique.  Therefore

```
sum_r D(r) = N(H7),
N(H7) = z2 = n3-z11/4,
sum_r E0(r) = 6P + N(H7) = 8316-n3-z11/4.
```

Using unmatched flags of the `r=2` disjoint-triangle relation, let `X` be the
flag relation, `F` the flag-to-vertex incidence, and `Y=F^T X`.  Then every
entry of `Y` is `0,1,2`, with

```
#2 in row r       = D(r),
row sum           = 84-S(r),
row support       = 84-E0(r),
row square norm   = 84-E0(r)+3D(r).
```

The support indicator is the entrywise quadratic

```
U = 1_{Y>0} = (3Y-Y o Y)/2,
E0(r)=84-(U 1)_r.
```

Moreover each of the three columns belonging to a triangle `T` has sum
`q(T)`.  Hence

```
1^T YY^T 1 = 3 sum_T q(T)^2,
sum_{r<s} (YY^T)_{r,s}
  = (3 sum_T q(T)^2-2*n3-2*N(H7))/2.
```

Consequently `sum Y=2*n3`, `||Y||_F^2=2*n3+2*N(H7)`, and, with
`M2=sum_r binom(84-E0(r),2)`,

```
sum_r E0(r)^2 = 698544 - 334*n3 + 167*N(H7) + 2*M2.
```

Thus a useful theoretical lower-bound target is an upper bound on the row
support of `Y`, or a lower bound on `N(H7)`.  In particular average `E0>=72`
is equivalent to `N(H7)>=2*n3-1188`, or `n3+z11/4<=1188`; average `E0>=73`
is equivalent to `N(H7)>=2*n3-1089`, or `n3+z11/4<=1089`.

## Exact catalogue audit

| E0 | canonical macros | full-Gram profiles | Q range | full-Gram affine dimensions |
|---:|---:|---:|---:|---:|
| 71 | 180 | 165 | 2..8 | 0:147, 1:33 |
| 72 | 163 | 162 | 4..12 | 0:162, 1:1 |

Completing the 33 one-parameter E71 Gram systems is itself a safe new
filter: 23 of 180 canonical overlap macros have no integral PSD full-Gram
completion.  It leaves 157 macros, 165 full profiles, and rooted overlap
coverage 58,556,416
from 61,112,320.

Every retained full profile satisfies exactly

```
sum overlap D = 2*tau,
sum disjoint (4-D) = tau,
tr Z = 2*tau,
tr Z^2 = 4 sum(delta^2) + 2(overlap_square+x_square),
rank(Z) tr(Z^2) >= tr(Z)^2.
tr(Z^2) = 2*tau (mod 4).
```

The congruence follows because the diagonal contribution is divisible by
four, while squares of off-diagonal integers reduce to their values modulo
two; `sum overlap D=2*tau` and `sum disjoint (4-D)=tau`.  E71 therefore has
`tr(Z^2)=2 mod 4`, while E72 has `tr(Z^2)=0 mod 4`.  This explains the
smallest possible positive trace/rank slack of two at E71 (attained by
source 2601, rank three, `tr(Z^2)=226`).  It is a sharp arithmetic condition,
but does not exclude E71.

The E71 catalogue contains local Gram-feasible `E0=71,Q=2,S=69` macros.
Hence neither pointwise `E0>=72` nor `Q>=3` follows from the present
compression/port/overlap-Gram conditions.  Both catalogues happen to have
even `Q`, but E73 supplies exact odd-`Q` port states, so parity is not a
universal law.  The E72 catalogue has `Q=tau=12` rows at sources 133, 134,
and 137.  Sources 133 and 134 are separately excluded by stronger structural
arguments (source 134 is the K4 family), so pointwise moment equality alone
is not a realizability certificate.

The clean pointwise target is now explicit: `E0(r)>=72` is equivalent to
every row of `U=1_{F^T X>0}` having weight at most 12.  The 157 fully
Gram-completable E71 macros have the local surrogate weight 13, so such a
proof must use compatibility between different roots/triangle flags; no
inequality of the present one-root Gram moments can establish it.  The next
weaker candidate `E0(r)>=71` is consistent and tight on these data, but is
not proved because E70 is outside the two catalogues.

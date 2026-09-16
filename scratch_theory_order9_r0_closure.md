# Seven-mask `R0` closure on the Wave163 endpoint

## Exact outcome

Exactly the seven prescribed H9 masks were added to the preceding 28-column
universe:

```text
f0   1292419201
f1   3668590721
f2  13610256401
f3  14889779459
f4  24436319376
f5  32214460576
f6  35652157569
```

A direct glue scan verifies that their union is exactly the missing support
of

```text
R0-R0, R0-X_0, R0-X_1, R0-X_2, R0-P.
```

Thus `{R0,X_0,X_1,X_2,P}` is a closed principal Gram block on the 35
columns.  No general H9 census was performed.

## Frozen H8 deletion consistency

All `7*9=63` vertex-deletion slots lie in the frozen catalogue of 916 H8
classes.  They use 16 distinct H8 shadows.

Two shadows have zero count at the Wave163 point:

```text
58163201, 58167297.
```

Their nonnegative order-8-to-9 deletion equations force precisely

```text
f2=f3=0,
```

that is, H9 masks `13610256401` and `14889779459` have zero count.  The
closed Gram entry `R0-P=0` independently forces the same two zero cells,
because their coefficients there are respectively 6 and 12.

## Exact five-flag Gram

At `T=0`, every target triangle has

```text
(R0,X_0,X_1,X_2,P)=(32,12,12,12,0).
```

There are `231*6=1386` ordered target-triangle roots.  Therefore the exact
Gram is the outer product

```text
1386 * (32,12,12,12,0)^T (32,12,12,12,0)
```

or explicitly

```text
          R0      X_0      X_1      X_2    P
R0   1419264   532224   532224   532224    0
X_0   532224   199584   199584   199584    0
X_1   532224   199584   199584   199584    0
X_2   532224   199584   199584   199584    0
P          0        0        0        0    0
```

It is PSD of rank one.  Its nonzero eigenvalue is `2018016`; an integral
kernel basis is

```text
3R0-8X_0,  X_0-X_1,  X_0-X_2,  P.
```

There is no negative direction and hence no coefficient vector to translate
into an `E0` lower bound.

## Closed local identities and rank

The 35-column local extension scan touches

```text
56 unmarked rows, 192 marked-vertex rows, 561 ordered-pair rows.
```

Exactly 34 ordered-pair rows close; no unmarked or vertex-rooted row closes.
Relative to the 28-column stage, three more ordered-pair rows close, giving
two new independent equations.  In the variable order

```text
(e0,...,e8,f0,...,f6),
```

they are

```text
2f1 + 2f2 + 12f3 + 4f5 = 52372,                         (D1)
2e3 + 2f2 + f4          = 213740.                        (D2)
```

The closed-row coefficient rank is 7.  The Gram equations have rank 4, and
the combined rank is 9.  Only two Gram directions add rank to the closed
rows: `R0-R0` and `R0-P`.  Indeed,

```text
(D1) + 2(D2) = (R0-X equation) + (R0-P equation),
```

so the `R0-X` condition is redundant after imposing the two new deletion
rows and `R0-P=0`.  The previous distinct-`X` equation remains the half-sum
of the earlier five closed equations.

## Integral endpoint witness

The old nine added counts followed by the new seven counts can be chosen as

```text
(e0,...,e8)
 = (0,0,25986,36192,0,6792,10224,0,5922),

(f0,...,f6)
 = (0,26186,0,0,141356,0,103818).
```

This point is nonnegative and integral, evaluates the five-flag Gram exactly,
satisfies all 34 closed rows, and satisfies the upper bound for every open
row.  Congruence consequences are

```text
e2,e6,f1,f4 are even,
```

but there is no new congruence obstruction on the frozen Wave163 data.

As in the earlier targeted lifts, different open-row slacks are not asserted
to arise from one simultaneous ambient H9 distribution.  This is an exact
35-column projection certificate, not an ambient order-nine realization.

## Claim boundary and next lane

Among all 74 previously extracted triangle-rooted flags, the only diagonals
closed on the 35 columns are now exactly

```text
R0, X_0, X_1, X_2, P.
```

The smallest remaining diagonal support deficit is still two masks,

```text
46817920192, 56196485312,
```

shared by rooted flag masks

```text
24699, 24939, 25147, 25507, 27179, 27299.
```

The natural `R1_j` continuation is deliberately not selected: at this
endpoint the natural matching counts are triangle-wise uniform, so further
natural matching blocks are expected to continue producing outer-product
rank-one Grams.  The sharper bounded next question is whether the six
two-mask-diagonal flags contain a nontrivial closed clique of size at least
two after those two masks are supplied.

## Files and independent audit

The producer and certificate are

```text
scratch_theory_order9_r0_closure.py
scratch_theory_order9_r0_closure.json
```

The producer-independent replay is

```text
scratch_theory_order9_r0_closure_audit.py
scratch_theory_order9_r0_closure_audit.json
```

The audit imports no producer code and independently reconstructs all 63
deletions, five R0 glue products, 35 coefficient matrices, all 809 local
extension rows, and all 74 diagonal supports.  It passes.

The frozen order-8 assets were read only, no order-8 class was regenerated,
and `submission.txt` was not created.

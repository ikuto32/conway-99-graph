# Wave163 integral count-slack boundary

Status: `INDEPENDENT_EXACT_INTEGRAL_COMPRESSED_FEASIBILITY_PASS`.

This is a rigorous **integer pseudocount boundary** for the present 57-row
compressed lane.  It is not a graph and does not test the full four-root
covariance matrices.

## Exact integer lift

The frozen universal endpoint system parameterizes

```text
(1,x8[0],...,x8[915]) = N t
```

by eight free order-eight coordinates `t`.  Requiring all 916 order-eight
counts and all 208 deletion-induced order-seven counts to be integers gives
a full-rank sublattice of `Z^8` of exact index

```text
4,954,521,600 = 2^20 * 3^3 * 5^2 * 7.
```

After imposing the endpoint normalization and the active nonnegative face,

```text
-t2 + 3*t3 + t4 = 1,247,400,
t7 = 964,656,
```

the solution set is a nonempty rank-six affine lattice.  Exact LLL/Babai
reduction produces the nearby integer point

```text
t = (
  14,401,612,
  13,247,818,
     957,378,
     134,580,
   1,801,038,
   5,687,012,
   7,458,420,
     964,656
).
```

Direct exact reconstruction gives

```text
all 916 x8 counts are nonnegative integers,
all 208 x7 counts are nonnegative integers,
minimum positive x8 count = 762,
minimum positive x7 count = 3,465,
sum x8 = C(99,8) = 171,200,862,756,
sum x7 = C(99,7) = 14,887,031,544.
```

The zero supports are unchanged from the rational control: 26 order-eight
coordinates and four order-seven coordinates vanish.  The latter have masks

```text
43868, 43900, 111989, 120568.
```

In particular mask `120568` is `H_delta`, so its count is zero.  At the
imposed endpoint `n3=4158`, the exact identity `n3+3P=4158` gives `P=0` and
therefore

```text
sum_r E0(r) = 6P + N(H_delta) = 0.
```

Both exact compressed test matrices remain strictly positive definite: all
six rational LDL pivots for root 3 and all eight for root 12 are positive.

## Independent completeness audit

The clean-room verifier imports no discovery module.  It clears all 1,124
count forms with common denominator `50,400` and independently diagonalizes
the induced map prime by prime.  The nonzero Smith valuations are

```text
p=2, e=5: 0,1,2,2,3,4,4,4  -> image exponent 20
p=3, e=2: 0,1              -> image exponent 3
p=5, e=2: 0                -> image exponent 2
p=7, e=1: 0                -> image exponent 1.
```

Thus the independently computed kernel index is again `4,954,521,600`.
Every saved lattice basis column satisfies all 1,124 congruences, and its
absolute determinant equals that index, proving that the saved basis is the
full integrality kernel rather than a sublattice.

In coordinates of this full lattice, the six saved affine directions have
gcd one over all maximal minors.  Hence they are saturated and generate the
complete rank-six homogeneous solution lattice.  The verifier also checks
the displayed candidate decomposition, reconstructs every count, and uses
Sylvester's exact rational leading-principal-minor criterion for both
compressed blocks.

## Consequence and boundary

Adding integrality of every frozen order-seven and order-eight pseudocount
does **not** rescue the present compressed `U3/U12` lane: it still admits an
exact feasible point with `sum E0=0`.  Therefore a positive pointwise or
summed `E0` lower bound cannot follow from only

1. the universal endpoint equalities,
2. nonnegative integral `x7,x8` counts, and
3. the saved 57 compressed PSD rows.

A stronger argument must use information absent here, such as directions
outside `U3/U12`, the full four-root covariance blocks, higher-order
identities, or graph-realizability/factorization constraints.  Integer motif
counts alone are not a graph realization, and this result makes no existence
claim for the Conway 99-graph.

## Artifacts and replay

- `scratch_theory_wave163_integer_lattice.py`
- `scratch_theory_wave163_integer_lattice.json`
- `scratch_theory_wave163_integer_lattice_audit.py`
- `scratch_theory_wave163_integer_lattice_audit.json`

Replay with standard-library Python:

```powershell
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_wave163_integer_lattice.py
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_wave163_integer_lattice_audit.py
```

SHA-256 bindings at this audit are

```text
integer_lattice.py          5c4e0dc3b248f01647718e1848088a0dd588afd3ecee487cefc2fd1abe8a9243
integer_lattice.json        58c1bbe49d4d661045c0fa611cfc0a28b21d1f51390c3df707ed1f2c9fe84437
integer_lattice_audit.py    1db520c2223c185fcb14a7ff12d37d5f7c512b218d8a2dde28d1dbdaf240e83d
integer_lattice_audit.json  bbda31c1a39cd83ecd72e765cd2acf7e6998dc144613aa4dbdf437588d246f4f
```

# Exact integral boundary for the current frozen order-8 relaxation

## Bottom line

There is an explicit nonnegative **integral** order-7/order-8 pseudocount at
the endpoint `T=0` which simultaneously satisfies:

- the frozen universal affine equations, including all 208 ordinary deletion
  rows, 944 marked-vertex rows, and 4,440 marked-pair rows;
- the 57-row compressed four-root pencil, with both compressed matrices
  positive definite;
- both full Wave147 pair-root covariance blocks assembled from all 2,414
  frozen coefficient matrices; and
- all nine full Wave152 four-root covariance blocks.

Thus the complete *current frozen lane* consisting of these linear,
integrality/nonnegativity, pair-root PSD, and four-root PSD constraints has an
exact feasible boundary point with `T=0`.  A positive `E0` lower bound cannot
follow from this relaxation alone.  Any further exclusion must use additional
higher-order synchronization or graph-realizability information.

This is a boundary theorem about a relaxation, not a construction of the
Conway graph.

## Explicit pseudocount

The eight free integral coordinates are

```text
(14401612, 13247818, 957378, 134580,
 1801038, 5687012, 7458420, 964656).
```

The consolidated JSON contains all 208 pairs `(order7_mask,count)` and all
916 pairs `(order8_mask,count)`, so the point is explicit rather than merely
existential.  Their checksums and basic statistics are:

| vector | SHA-256 of canonical mask/count list | sum | zero entries | smallest positive |
|---|---|---:|---:|---:|
| order 7 | `a1a33e0d1beddf2a56443a81f33fdf7d6f01e2c78a8f0a4cbc860a322122ed4e` | 14,887,031,544 | 4 | 3,465 |
| order 8 | `cf4c72694b56c16ea4db09320d958e66ac039dfe636e418daf64679209f468c7` | 171,200,862,756 | 26 | 762 |

The sums are exactly `binom(99,7)` and `binom(99,8)`.  Every coordinate is a
nonnegative integer.  Independent lattice auditing also verifies the full
integrality lattice and the two endpoint/face equations.

At this point

```text
n3 = 4158,  P = 0,  N(H_delta) = 0,
sum_r E0(r) = 6P + N(H_delta) = 0.
```

Since every `E0(r)` is nonnegative, this gives pointwise `E0(r)=0` for every
root in the pseudocount interpretation.

## Frozen linear layer

No graph-class catalogue was regenerated.  The exact affine system uses the
already frozen assets:

| asset | count |
|---|---:|
| order-8 graph classes | 916 |
| ordinary order-7 deletion rows | 208 |
| marked-vertex rows | 944 |
| marked-pair rows | 4,440 |
| Wave147 pair-root class matrices | 2,414 |

After eliminating the 208 deletion pivots, the universal system has 917
coordinates and an eight-dimensional nullspace.  Independent modular checks
over `1,000,000,007` and `1,000,000,009` agree.  The 57 compressed pencil
rows comprise a `6 x 6` root-3 block and an `8 x 8` root-12 block; both are
exactly positive definite at the integral point.

## Wave147 pair-root PSD layer

All 2,414 frozen class-matrix records and all 272,054 nonzero upper-triangular
integer coefficients were consumed.

| family | dimension | exact rank | nullity | result |
|---|---:|---:|---:|---|
| ordered edge | 66 | 1 | 65 | PSD |
| ordered nonedge | 87 | 1 | 86 | PSD |

The independent audit proves rank one entrywise using
`M[p,p] M[i,j] = M[i,p] M[p,j]` for every pair `i,j`, with a positive pivot.

## Wave152 four-root PSD layer

The same integral point was evaluated against every locally admissible
four-root type, using the frozen 62/208/916 order-6/7/8 streams.

| root mask | dimension | exact rank | nullity |
|---:|---:|---:|---:|
| 0 | 224 | 38 | 186 |
| 1 | 201 | 27 | 174 |
| 3 | 155 | 15 | 140 |
| 7 | 99 | 3 | 96 |
| 11 | 69 | 3 | 66 |
| 12 | 178 | 16 | 162 |
| 13 | 125 | 6 | 119 |
| 15 | 60 | 0 | 60 |
| 30 | 70 | 0 | 70 |

All nine are exact PSD.  The last two are identically zero.  A clean-room
program, which does not import the matrix producer, restreamed every rooted
embedding, matched all 184,973 archived matrix entries, and independently
reconstructed every entry from the stored sparse rational LDL factors.

## What “complete” means here

The conclusion covers exactly the currently frozen collection listed above:
universal linear rows, nonnegative integral order-7/order-8 counts, the two
Wave147 pair-root blocks, and all nine Wave152 four-root blocks.  It does not
claim feasibility for every conceivable order-8 inequality, nor does it claim
that the integral pseudocount is realizable by a graph.  The Conway 99-graph
problem remains open.

## Consolidated artifacts

- `scratch_theory_wave163_integral_order8_boundary.py`
- `scratch_theory_wave163_integral_order8_boundary.json`
- `scratch_theory_wave163_integral_order8_boundary.md`

The JSON binds the exact count vectors, all upstream certificate hashes, the
pair-root matrix hashes, the nine four-root matrix hashes, and the full
matrix/LDL archive hashes.

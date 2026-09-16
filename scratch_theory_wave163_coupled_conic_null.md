# Wave163 compressed coupled-conic lane: exact null boundary

## Result

The previously unexecuted `attempts/wave163-coupled-conic-dual` first lane is
now decided exactly, without regenerating the frozen order-eight census or
the Wave147/Wave148 coefficient artifacts.

For the six stored root-mask-3 directions and eight stored root-mask-12
directions, the 57 upper-triangular compressed-pencil rows have exact rank

```text
rank(universal endpoint rows)                         = 1117 / 1125
dimension of the universal quotient                  =    8
rank(57 compressed rows modulo universal rows)        =    8
dimension of the compressed affine-identity kernel   =   49
```

The 49-dimensional affine kernel contains **no nonzero PSD multiplier
pair**.  An exact rational linear combination of its eight quotient
equations is positive definite in both blocks.  Thus this entire compressed
PSD multiplier family gives no exposing identity at the endpoint.

This is a scoped null result.  It does not exclude a dual using count
nonnegativity slacks, directions outside these two stored subspaces, other
covariance blocks, or higher-order variables.  It does not decide Conway's
99-graph problem.

## Frozen inputs and direction spaces

The calculation consumes, rather than regenerates:

- 916 stored order-eight classes;
- 208 ordinary deletion rows;
- 944 marked-vertex and 4,440 marked-pair rows;
- the 2,414 stored Wave147 pair-root matrices (used only as a frozen class
  stream and deletion archive, not confused with four-root matrices);
- five retained root-3 directions and seven retained root-12 directions;
- the post-fifteen-cut recurrent root-3 and root-12 negative directions.

The direction columns have exact ranks 6 and 8 over both
`1000000007` and `1000000009`.  No duplicate or dependent column is removed.
The four-root flag dimensions are 155 and 178.  Each root embedding count is
1,014,552.

The full four-root class matrices were not materialised.  If `u_i,u_j` are
two retained directions, direct induced embedding contraction gives

```text
C_tau(x)[i,j]
 = R_tau * sum_H q_H(u_i,u_j) x_H - s_tau(u_i)s_tau(u_j).
```

All 21 root-3 and 36 root-12 entries were accumulated simultaneously.  As a
control, every one of the twelve retained diagonal rows for roots 3 and 12
reproduces its stored primitive scalar cut coefficient-for-coefficient,
including the constant and gcd divisor.  Two root-12 cross entries,
`(1,3)` and `(1,5)`, are identically zero; they are retained as genuine
kernel coordinates rather than discarded.

The compressed coefficient payload has canonical SHA-256
`70085c2832b70b0cb6f5393bc7eb5cc927cc6dec2bd61ddcc62b1ccde0090765`
and gzip SHA-256
`42ec43f6658c0eca3de7a95ab9aae3041838b364614c8c130cf50a64401ba53f`.

## Universal endpoint affine space

The augmented coordinates are

```text
(1, x7[208], x8[916]).
```

Only the following graph-valid endpoint equalities are used:

1. two exact count normalisations;
2. 170 Wave44 rows, with the final `n3` coefficient specialised at
   `n3=4158`;
3. 208 ordinary deletion equations;
4. all 944 marked-vertex and 4,440 marked-pair equations.

Neither fixed `x7` nor the pair-root-zero face is used.  No nonnegativity
row is treated as an equality.

Deletion has the exact form

```text
92*x7_H = sum_K d(H,K)*x8_K.
```

It supplies 208 independent pivots.  Eliminating `x7` reduces the problem to
917 coordinates `(1,x8[916])`; 893 identically zero marked-pair records drop
out, leaving 4,663 stored nonzero reduced rows.  Their primitive-row hash is
`1a62d79e869fbd91f0601e4fdfeef8278ec22091dd4ec14d6d9b25dfe0b54f34`.

Sparse modular elimination gives reduced universal rank 909 for both primes,
with the same eight free columns

```text
211, 216, 291, 301, 373, 417, 480, 637.
```

The corresponding `x8` masks are

```text
56034368, 56296000, 58345536, 62542880,
94001168, 106059780, 120259104, 178690064.
```

The exact eight-vector nullspace was reconstructed by CRT over
`1000000007, 1000000009, 999999937` and rational reconstruction.  Every one
of the 4,663 integer rows was then multiplied by every recovered vector over
`Fraction`; all 37,304 products are exactly zero.  This supplies the matching
rational upper bound rank 909, so the modular rank is the exact rational
rank, not merely a lower bound.

## Exact quotient and PSD separator

Evaluating the 57 compressed rows on that exact nullspace gives a rational
`57 x 8` quotient map.  Exact RREF has pivot compressed coordinates

```text
0, 1, 2, 3, 4, 5, 21, 22,
```

hence rank 8 and a verified 49-vector rational kernel basis.

For PSD interpretation, an upper-triangular coefficient vector uses

```text
z_ii = Y_ii,       z_ij = 2 Y_ij  (i<j),
```

because `<Y,C>` counts off-diagonal entries twice.  Direction column `i` is
rescaled by the positive integer `s_i=max |u_i|`; this is an invertible
congruence and cannot change PSD feasibility.

Let `A_{tau,k}` be the resulting exact quotient matrices, so a compressed
PSD kernel element satisfies

```text
tr(Y3 A_{3,k}) + tr(Y12 A_{12,k}) = 0,  k=0,...,7.
```

The following exact rational coefficients were found:

```text
c = (
  1,
  869823/1000000,
  64241/1000000,
  9553/1000000,
  58629/500000,
  193079/500000,
  121737/250000,
  33021/500000
).
```

Define `H_tau=sum_k c_k A_{tau,k}`.  Fraction-only `LDL^T` elimination gives
six strictly positive pivots for `H_3` and eight strictly positive pivots for
`H_12`; the full matrices and every exact pivot are stored in
`scratch_theory_wave163_psd_exact.json`.  Therefore both `H_3` and `H_12`
are positive definite.

If `Y3,Y12` were PSD and belonged to the quotient kernel, then

```text
0 = tr(Y3 H3) + tr(Y12 H12).
```

Both summands are nonnegative and, because the corresponding `H` is positive
definite, each vanishes only when its `Y` is zero.  Hence the only PSD pair in
the 49-dimensional affine kernel is `(0,0)`.

The floating SCS/Clarabel run was used only to locate `c`.  The stored
certificate and its verification use exact rational coefficients and do not
depend on a solver status or numerical eigenvalue.

## Artifacts and replay

- `scratch_theory_wave163_coupled_pencil.py`
- `scratch_theory_wave163_coupled_pencil.json`
- `scratch_theory_wave163_coupled_pencil_coefficients.json.gz`
- `scratch_theory_wave163_coupled_kernel.py`
- `scratch_theory_wave163_coupled_kernel.json`
- `scratch_theory_wave163_coupled_kernel_basis.json.gz`
- `scratch_theory_wave163_psd_scout.py` and `.json` (diagnostic only)
- `scratch_theory_wave163_psd_exact.py` and `.json`

Replay with the standard-library Python (the exact stages have no third-party
dependency):

```powershell
C:\Users\ikuto\.local\bin\python3.12.exe -B scratch_theory_wave163_coupled_pencil.py
C:\Users\ikuto\.local\bin\python3.12.exe -B scratch_theory_wave163_coupled_kernel.py
C:\Users\ikuto\.local\bin\python3.12.exe -B scratch_theory_wave163_psd_exact.py
```

Every stage enforces an 18% free-physical-memory floor.  The observed minima
in the exact pencil and kernel stages were 66.433% and 65.481%, respectively.


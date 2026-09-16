# Wave163 compressed count-slack boundary

Status: `INDEPENDENT_EXACT_COMPRESSED_COUNT_SLACK_FEASIBILITY_PASS`.

This is a rigorous **null boundary for the present 57-row compressed lane**.
It is not a graph and does not test the full four-root covariance matrices.

## Exact rational control

The independently audited universal endpoint rowspace has coordinates

```text
(1,x8[0],...,x8[915])
```

after the 208 ordinary deletion equations eliminate the order-seven counts.
Its exact nullspace has dimension eight.  Write its free coordinates as
`t=1,247,400 z`.  The following rational point was recovered:

```text
z = (
  2886327/250000,
  10620341/1000000,
  767499/1000000,
  6743/62500,
  288767/200000,
  2279549/500000,
  1494793/250000,
  58/75
).
```

It satisfies the endpoint normalization exactly:

```text
-z2 + 3 z3 + z4 = 1.
```

The numerical Clarabel point had 26 apparently zero order-eight counts.  An
exact audit shows that 12 of those coordinates vanish identically throughout
the universal nullspace.  The remaining 14 coefficient rows have rank one;
on the normalized affine space their common face is exactly

```text
z7 = 58/75.
```

Pinning this equation before rational rounding removes the tiny negative
roundoff values.  Exact Fraction arithmetic then gives

```text
all 916 order-eight counts >= 0,
26 order-eight counts = 0,
minimum positive order-eight count = 476091/625,
sum x8 = C(99,8) = 171200862756.
```

Applying all 208 frozen deletion equations gives

```text
all 208 order-seven counts >= 0,
zero order-seven indices = 180,185,206,207,
zero order-seven masks   = 43868,43900,111989,120568,
sum x7 = C(99,7) = 14887031544.
```

Mask `120568` is `H_delta`, so its count is zero.  At the imposed endpoint
`n3=4158`, the exact identity `n3+3P=4158` gives `P=0`; hence

```text
sum_r E0(r) = 6P + N(H_delta) = 0.
```

The counts are rational pseudocounts.  No integrality or graph-realizability
claim is made.

## Exact compressed PSD check

The stored exact `57 x 8` quotient map evaluates all upper-triangular entries
of the two compressed blocks on the point above.  There are 21 entries for
the root-3 `6 x 6` block and 36 entries for the root-12 `8 x 8` block.
Positive diagonal rescaling by the stored direction column scales is an
invertible congruence.

Independent Fraction-only `LDL^T` reconstruction gives:

```text
root 3:  all 6 pivots strictly positive,
root 12: all 8 pivots strictly positive.
```

Thus both compressed blocks are actually positive definite, not merely
semidefinite.  The audit also checks the upper-triangle convention explicitly:
off-diagonal entries receive factor two in a Frobenius trace.

Consequently the system consisting of

1. the universal endpoint equalities with `n3=4158`,
2. all nonnegativity inequalities for the 916 order-eight counts and the 208
   induced order-seven counts, and
3. the two PSD blocks compressed to the saved `U3` and `U12` directions,

is exactly rationally feasible with `sum E0=0`.  Therefore no conic/Farkas
infeasibility certificate restricted to these ingredients can prove a
positive endpoint `E0` lower bound.

This does not cover directions outside `U3,U12`, the full four-root blocks,
additional higher-order identities, integer counts, or graph realization.

## Artifacts and replay

- `scratch_theory_wave163_count_slack_exact_control.py`
- `scratch_theory_wave163_count_slack_exact_control.json`
- `scratch_theory_wave163_count_slack_exact_control_audit.py`
- `scratch_theory_wave163_count_slack_exact_control_audit.json`

Replay with standard-library Python:

```powershell
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_wave163_count_slack_exact_control.py
C:\Users\ikuto\.local\bin\python3.12.exe scratch_theory_wave163_count_slack_exact_control_audit.py
```

Current SHA-256 bindings are

```text
control.py    b8a7709b74df7da400d57262552bdb7950fc6f75f9857c5293fc8e267be19f6e
control.json  9e34901d1d437f3e7f69c5a1faca3e55416775655e38d149a469fa7fb8d74012
audit.py      c209615716c58208940be9b63a8ef4a0b5f577dc2ec15c793fbb1826602fe7b9
audit.json    ee2d7f17f0e3be1da33f0a8591756486c4840145b7d0703a1cad33891fbe8691
```

The audit binds the exact control to the earlier clean-room Wave163 audit
(`scratch_theory_wave163_coupled_pencil_independent_audit.json`) and to the
independently verified universal nullspace/quotient artifact.

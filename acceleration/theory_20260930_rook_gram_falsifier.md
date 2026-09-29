# Exact Gram extension falsifier for a completed local window

Status: CANDIDATE tool and derivation, requiring separate review of any new
negative-direction or rank witness. A local graph may satisfy its CNF and
still fail a necessary condition for extension; these are different claims.

Every target has degree 14 and eigenvalues 14 (multiplicity 1), 3
(multiplicity 54), and -4 (multiplicity 44). This follows exactly from
`A^2=12I-A+2J`, the diagonal, connectedness forced by positive common-neighbor
counts, and `trace(A)=0`. Therefore

```
G = 27I - 9A + J
```

has eigenvalue zero on the constant and 3-eigenspaces and eigenvalue 63 on
the -4-eigenspace. It is PSD of rank 44. Likewise `A+4I` is PSD of rank 55.
Every principal submatrix preserves PSD and cannot increase rank. Thus any
completed induced 59-vertex local window must have its corresponding two
integer Gram matrices PSD, with ranks at most 44 and 55, respectively.

The proposed checker uses only rational congruence elimination. A negative
diagonal pivot directly supplies a negative direction in the original
coordinates. If the remaining diagonal is zero but an off-diagonal entry is
nonzero, one of the sum/difference of its two coordinate directions has
negative quadratic value. Scale by the denominator LCM and divide by the
integer GCD to emit a primitive integer vector. A verifier needs only the
raw local adjacency and that vector to check its negative integer quadratic
value; it need not trust the elimination implementation.

When elimination is PSD but the rank bound is exceeded, emit the first
`rank_bound+1` positive pivot indices and the exact determinant of their
principal submatrix. An independent determinant calculation supplies a
compact rank witness. Do not infer a rank violation from rounded eigenvalues.

Calibration precedes research inputs: positive identity and singular PSD
matrices, an ordinary negative diagonal, a zero-diagonal indefinite matrix,
a deliberately excessive rank, and the exact rook-nine Gram. The two tests
are deterministic, at most 59-by-59, with no solver, randomness or floating
arithmetic. Stop on a malformed input rather than repairing it. A passing
test is necessary only and is not a graph-construction certificate.

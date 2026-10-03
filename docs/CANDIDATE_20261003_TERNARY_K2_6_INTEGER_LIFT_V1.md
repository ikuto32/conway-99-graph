# Candidate: K2,6 cannot be the whole ternary residual support

Discovery author `/root`; source context
`63437c9b9fc2dd58b3bdfb51fc347b880b397503`. Status **CANDIDATE** pending
another author's complete exact written derivation and falsification.
Writing start time is unavailable; the later verification record supplies
its actual timestamp. This file is not asserted present in the context
commit. Computation, fixtures, formal proof and ledger changes: zero.

For any simple symmetric binary zero-diagonal 99-by-99 integer adjacency
matrix A with every degree 14, define R=A^2+A-12I-2J and M=R mod3.
The claim is that the whole nonzero off-diagonal support of M cannot be
K2,6. This permits empty support, does not exclude an arbitrary component
inside a larger support, and does not assert general nonexistence or a
twelve-defect realization. No automorphism of A is assumed.

The equal-outside/negative-budget filter is pinned revision1 of
`C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER`,
report `7d2ecc903415ecb66d5693891031d889e2862b05bfcf8d11b480fdda71344394`.
The needed identities are repeated. No defect-lower12 claim is a premise.

## Saturating the integer lift

Let a,b be the two high vertices and L the six low vertices, S={a,b} union L.
Zero field rows at each low give opposite signs at its two highs. Counting
residue-one labels c at a gives c+2(6-c)=12-c=0 mod3, so c=0,3 or6.
Every outside binary row lies in ker M_S by AM=MA and the entire support
premise; a low degree-two equation makes a,b have identical outside
neighborhoods. At m=8, CN(a,b)>=14-floor(8/2)=10, so its good integer
residual R_ab is at least nine after rounding to a multiple of three.

The row budgets are beta_a=6+c and beta_b=12-c. If c=0 or6 one budget
is six, already a contradiction. Therefore c=3, both budgets are nine
and R_ab=9. In each high row this single positive nine uses the entire
negative allowance of its three residue-one and three residue-two
support entries. Each such bad residual therefore equals its minimum
-2 or -1. No other good positive term can occur there.

Every R row outside S has only good entries, each nonnegative, and sum
zero. Thus its entire integer row vanishes. In each low row the two bad
high entries sum to -3. All its other entries are nonnegative multiples
of three and sum to three. Exactly one other low must have residual three.
By symmetry these positive low-low pairs form a perfect matching.

Writing P for its six-by-six matching adjacency, P^2=I and P1=1. Choose
a sign vector s with three +1 and three -1 so that the high-low block C
has rows -(3/2)1^T-(1/2)s^T and -(3/2)1^T+(1/2)s^T. Then exactly

    R_S = [[0,9,C_a], [9,0,C_b], [C_a^T,C_b^T,3P]],

with all outside rows/columns zero. Fractions here are a compact exact
description of the integer entries -2/-1; they introduce no relaxation.

## A simple rational eigenvalue that cannot lift to integer A

The two-dimensional subspace U of vectors constant on the highs and
constant on the six lows is invariant. On coordinates (x,y) for those
constant values, R maps (x,y) to (9x-9y,-3x+3y). Its eigenvalues are 0
and12. In particular the integer vector z, equal to -3 at a,b and +1
at all lows, zero outside S, satisfies Rz=12z and 1^Tz=0.

To show this eigenvalue is simple in the complete99 domain, consider
U's orthogonal complement within S. Its vectors have highs (x,-x) and
low vector l with sum zero. Symmetry and U invariance make this
complement invariant. Its exact quadratic form is

    -18 x^2 -2 x s^T l +3 l^T P l.

Since s^T s=6 and P is orthogonal, Cauchy's inequality and
(sqrt(6)|x|-||l||)^2>=0 bound this by

    -18x^2 +6x^2 +||l||^2 +3||l||^2
    = -12x^2 +4||l||^2 <=4(2x^2+||l||^2).

This is an exact symbolic norm inequality with integer coefficients,
not a floating eigenvalue estimate. Therefore every eigenvalue on that
complement is at most four, and outside S it is zero. The eigenvalue12
is consequently simple regardless of the matching P or its sign pattern.

A commutes with R because A is regular and symmetric. It therefore
preserves the one-dimensional12-eigenspace: Az=theta z. At any low
coordinate z_i=1, theta=(Az)_i is an integer. Since Jz=0, the defining
polynomial identity yields

    12z=Rz=(theta^2+theta-12)z,
    theta^2+theta-24=0.

Its discriminant97 lies strictly between9^2=81 and10^2=100, so this
quadratic has no integer root. This is a contradiction, proving the
candidate whole-K2,6 nonrealizability statement.

## Falsification requirements and limits

The verifier must check all c=0/3/6 cases, both saturated endpoints,
outside integer zero rows, completeness of the matching deduction,
both cross-block factors in the quadratic form, invariance and norm
bound on U's complement, simplicity in all99 dimensions, and integrality
of theta at a coordinate equal to one. The all-constant zero eigenvector
is distinct from z and does not create another12 eigenvector.

Field-level signed K2,6 can have zero rows and nilpotent cube; the proof
does not refute that separate field statement. Its obstruction is an
integer adjacency-polynomial lift. No numerical diagonalization, finite
matching catalogue, exact12-support coverage, sharpness, executed graph
fixture, formal proof, external review or target resolution is claimed.
This candidate changes no heuristic source, verifier gate or frozen371
publication. Its discovery author must not approve it.

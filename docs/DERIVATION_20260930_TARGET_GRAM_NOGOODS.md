# Exact target Gram positivity and support nogoods

This is an independent derivation of the Gram premise used by the rook-window
producer. It supplies a necessary property of every target, not a proof that
a target exists or does not exist. No automorphism is assumed.

## Universal matrix identity

Let `A` be any 99-by-99 symmetric binary matrix with zero diagonal satisfying

```text
A² = 12I - A + 2J.
```

On diagonal entry `i`, symmetry and binary entries give
`(A²)_ii = sum_j A_ij² = sum_j A_ij = 14`. Hence every row and every column
has sum 14, so `AJ = JA = 14J`. Also `J² = 99J`.

Set `G = 27I - 9A + J`. It is symmetric, and exact expansion gives

```text
G² = 729I + 81A² + J² - 486A + 54J - 9(AJ + JA)
   = 1701I - 567A + 63J
   = 63G.
```

For every real vector `x`, therefore,

```text
xᵀGx = xᵀG²x / 63 = (Gx)ᵀ(Gx) / 63 >= 0.
```

Thus `G` is positive semidefinite. This proof uses no approximate eigenvalues.
Every principal matrix `G[U,U]` is positive semidefinite: extend any vector on
`U` by zero outside `U` and apply the same inequality. In particular, a saved
integer vector with a strictly negative principal quadratic obstructs any
target extension of that principal adjacency.

## Exact support clause

Fix a labelled vertex set `U` and partition all its possible off-diagonal
adjacencies into fixed binary entries and distinct free Boolean variables
`t_e`, one per undirected free pair `e={u,v}`. Fix an integer vector `w` on
`U`. Its exact quadratic is affine in those variables:

```text
q(t) = wᵀ(27I - 9A[U,U](t) + J)w
     = c + sum_e c_e t_e,
c_e  = -18 w_u w_v,
c    = 27 sum_u w_u² + (sum_u w_u)²
       - 18 sum_{fixed edges {u,v}} w_u w_v.
```

Suppose an assignment `t*` gives `q(t*) < 0`. Let `K` contain exactly the
free pairs whose coefficients `c_e` are nonzero. Any assignment agreeing with
`t*` on every pair in `K` has the same negative quadratic, independently of
all other free variables and of all vertices outside `U`. It cannot be the
principal adjacency of a target. Consequently every target extension must
satisfy

```text
OR_{e in K} (t_e != t*_e).
```

In signed DIMACS notation this contributes `+id(e)` when `t*_e=0` and
`-id(e)` when `t*_e=1`. Every variable with nonzero coefficient must occur;
variables with zero coefficient may be omitted. If `K` is empty, the negative
constant obstructs the whole fixed principal family, and the corresponding
clause is empty.

This cut generally does not follow from the weaker local common-neighbor-cap
CNF. It adds a necessary condition for target extensions. A locally valid
SAT assignment may legitimately be rejected by this cut. Augmented-CNF UNSAT
can establish a conditional exclusion only if its exact proof is checked,
the initial encoding covers the declared family, and every appended cut is
independently justified for target extensions. No unrestricted coverage is
supplied merely by accumulating these cuts.

## Independent checking path

`acceleration/audit_20260930_gram_nogood_v1.py` imports no producer or numerical
eigensolver. It checks the target identity expansion using exact integer
coefficients of `I,A,J`. A separately constructed rook9 matrix supplies a
known-valid projector identity (`P=3I-3A+J`, `P²=9P`); a corrupted edge fails.

For each cut it directly evaluates the complete ordered integer matrix
quadratic, sets every variable edge to zero to independently reconstruct the
constant, checks every free-edge coefficient, and verifies every signed
literal, raw edge mapping, current value, and omitted zero coefficient.
Positive-certificate and nine deliberately corrupted certificate controls
are run. The specific initial 45-literal cut is checked in
`acceleration/results/20260930_rook_gram_minimized/independent_nogood.json`.
The general theorem does not require that vector support or clause length
be minimal, and the checker establishes no such optimization claim.

# Independent written audit: target affine obstruction and unbalanced circuit

Verifier `/root/native_driver`; discovery producer `/root/structural`.
The candidate read in full is
`docs/CANDIDATE_20261003_TARGET_TERNARY_AFFINE_OBSTRUCTION_UNBALANCED_CIRCUIT_V1.md`,
SHA256 1762ca0a315200745ad148e489f1f7b15ec6bfb457708910e72207e48e40e192.
The affine idea originated with ROOT; Structural wrote the complete candidate.
This audit separately reconstructs the exact identities, pairing and minimal
support argument, without code execution or using a numerical rank of P.

## Exact audited implication

For every simple degree-14 graph on 99 vertices with adjacent CN=1 and
nonadjacent CN=2, let B contain each actual triangle once. Over GF(3), no
point vector x satisfies B^T x=1. The right kernel of B contains a vector
of nonzero coordinate sum. A minimum-support such vector selects a genuine
column circuit of size at most 99.

This conditional statement asserts neither a target graph nor nonexistence,
nor an extra nonconstant left-kernel vector. It does not use a binary-rank
bound, the previously withdrawn rank-55 assertion for P, or an automorphism.

## Incidence and field identities reconstructed from the target

Each edge has its unique triangle completion. Distinct actual triangles
cannot share an edge. At a vertex the fourteen neighbors pair into seven
triangles, giving seven ones in each row of B and three in each column.
Thus B has 231 columns and, over the integers, BB^T=A+7I.

The target CN identity is A^2=12I-A+2J. Work now over GF(3) and define
N=A+I and P=N-J. Direct substitution gives

```
N^2 = A^2+2A+I = 13I+A+2J = N-J = P,
NJ=JN=15J=0,  J^2=99J=0,
P^2=(N-J)^2=N^2=P,  P1=(15-99)1=0,
BB^T=N,  B1=7*1=1,  B^T1=3*1=0.
```

No numerical rank of N or P occurs in any step.

## Affine obstruction

If B^T x=1, then Nx=BB^T x=B1=1. On the other hand,
1^T x=(B1)^T x=1^T B^T x=231=0, so Jx=0 and Px=1.
Idempotence gives P(Px)=Px=1, while P(Px)=P1=0, a contradiction.
The same obstruction holds for any nonzero constant right-hand side by
rescaling x, although the recorded statement needs only the constant one.

For the nondegenerate coordinate pairing, im(B^T) is contained in
ker(B)'s orthogonal complement, and both spaces have dimension rank(B),
so they are equal. Since the constant triangle vector is not in im(B^T),
it is not orthogonal to all of ker(B). Some z in the right kernel therefore
has nonzero coordinate sum. This is a vector in triangle coordinates;
the constant point vector being in ker(B^T) is a different fact.

## Why minimum unbalanced support is a circuit

Choose z among the unbalanced right-kernel vectors with minimum support.
Suppose a proper subset of its columns has a nonzero dependence h.
If h has nonzero sum, it is itself a smaller unbalanced vector. If h has
zero sum, choose a nonzero coordinate h_i and replace z by
z-(z_i/h_i)h. It stays in the right kernel with the same nonzero sum,
vanishes at i, and acquires no coordinate outside the original support.
Both cases contradict minimality.

Hence every proper subset of the selected columns is independent and the
whole set is dependent. Its rank is w-1. The nonzero constant point vector
lies in ker(B^T), so rank(B)<=98 without any finer rank statement. Therefore
w-1<=98 and w<=99. The dependency space on a circuit is one-dimensional;
its nonzero coefficients over GF(3) are +1 or -1.

The independent lower-twelve result can subsequently be combined with this
implication to obtain 12<=w<=99. It is not needed for this proof or this
claim's dependency list. The combination does not force any particular
twelve-column core, induced graph, symmetry, or target contradiction.

## Boundaries, premise checks and disclosure

The 99, 14 and 231 congruences are each used literally. For another order
or degree the vanishing J^2/NJ and row/column sums cannot be transferred.
Without idempotence, Px=1 and P1=0 alone do not yield this contradiction.
Without the minimum unbalanced-support choice, an arbitrary kernel word
need not be a circuit. These are written premise-sensitivity checks, not
executed countermodels or calibrated corruption tests.

No producer code, fixture, source parser, catalogue, solver, formal prover,
native search or external review was used. The historical ranks and archive
references in the discovery note are contextual only and were not imported
as mathematical dependencies. Shared ROOT-origin reasoning and ordinary
field/incidence definitions are explicit; novelty is unknown. The report
is an authentic Native independent written derivation of Structural's
candidate, with no ledger/index write or retrospective execution claim.

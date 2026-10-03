# Independent pair-cap reduction for the triangle core

Let n be positive and even. Take a named triangle t0,t1,t2 and three disjoint
n-vertex fibres Ai. Vertex ti joins every vertex of Ai and no other fibre.
The three internal adjacency matrices Mi are arbitrary perfect matchings.
The A0--A1 and A0--A2 matchings are identities; P[b,c]=1 means the edge
A1(b)--A2(c), with P an arbitrary permutation matrix. This completely
specifies a positive graph H on3+3n vertices. At n=12 it is the39-vertex core.

For every distinct pair x,y the local necessary condition is
Hxy+(H squared)xy<=2. This is only a principal pair-cap condition. It does
not require equality where neighbors outside the core may still be added.

Pairs of triangle vertices have value2. A triangle vertex and an own-fibre
vertex have value2, from its one internal mate plus their adjacency. For a
different fibre they have value2, from its triangle center and the unique
cross-matching neighbor. Distinct vertices within one fibre share their center
and no neighbor inside any fibre, hence have value1+Mi[x,y]<=2.

For the three cross-fibre blocks, direct expansion of adjacency and all
possible common-neighbor locations gives respectively

```
A0,A1: I + M0 + M1 + P transpose,
A0,A2: I + M0 + M2 + P,
A1,A2: I + P + M1 P + P M2.
```

There are no other pair types. In the first two blocks the diagonal is at
most2. Off diagonal, a cap can fail only where the two matching matrices
both have a1 and the P term also has a1. The common-matching relation is
symmetric, so the transpose in the first block gives exactly the unary rule

```
if M1(i)=M0(i) or M2(i)=M0(i), then P(i) != M0(i).
```

In the last block, P[b,c] and P[M1(b),c] cannot both be1: their row indices
differ, and a permutation column contains one1. Likewise P[b,c] and
P[b,M2(c)] cannot both be1 because their columns differ in one row. Therefore
off diagonal the total is at most2. On the diagonal the identity contributes
one; if P[b,b]=1 the other two terms vanish. Its only forbidden alternative is

```
P(M1(b))=b AND P(b)=M2(b).
```

Thus the two displayed reduced rules are necessary AND sufficient for all
principal pair caps in H. No parity, spectral, triangle-factor extension,
automorphism, or missing external-vertex assumption is used. This argument
holds for every even n and every three perfect matchings and permutation.

The conjunction in the last rule couples only the two rows in a single M1
edge. For such an unordered row pair {r,s}, form a polynomial whose monomials
Xx Xy range over allowed distinct column assignments r->x,s->y. Two
orientations contribute coefficient2 when both are allowed. Work in the
commutative squarefree ring with Xi squared=0. The coefficient of
X0 X1 ... X(n-1) in the product over all M1 row pairs counts exactly the
allowed permutations. Disjoint-column multiplication enforces bijectivity;
each permutation has a unique ordered assignment inside each row pair. The
independent checker uses decreasing row-pair order and its own coefficient
convolution, without importing the producer's DP or constraints.

Calibration enumerates all M1,M2 and all P for fixed canonical M0 at n=4
and n=6, independently builds the raw graph and checks literal pair
intersections. Counts are compared with both the reduced rules and polynomial
coefficient computation. These finite checks calibrate the implementations;
the preceding case proof supplies the universal theorem. Malformed matchings,
permutations and adjacency matrices are separately rejected.

For the3580 representative-pair count, the prior independent matching-pair
census is a declared premise. Its orbit sizes restore labelled (M1,M2)
choices. Simultaneous relabeling also conjugates P and preserves H, so the
per-representative allowed-P count is constant on its matching-pair orbit.
The weighted sum counts labelled triples for fixed M0 and named fibres only.
It is neither a P-orbit classification nor a count of full target graphs.

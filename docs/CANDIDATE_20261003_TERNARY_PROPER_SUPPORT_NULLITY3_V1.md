# Candidate: ternary nullity of a proper residual support

Discovery author: `/root/structural`. Written at actual UTC time
`2026-10-03T08:25:24+00:00`, in source context
`63437c9b9fc2dd58b3bdfb51fc347b880b397503`. This new working file is not
asserted to occur in that commit. Status: **CANDIDATE**, pending a different
author's complete written derivation and falsification review. Executed
mathematical commands, executable fixtures, ledger changes and index changes:
zero. There is no target resolution, novelty assertion or incidence-rank claim.

The preceding lift-parity candidate is
`docs/CANDIDATE_20261003_TERNARY_RESIDUE_LIFT_PARITY_GLOBAL_SUBCUBIC24_V1.md`,
SHA256 `6189d5c4014974eac958d1993d6f852dfc6bc3209c207361db15724494af7a2b`.
Its separate ROOT written audit is
`acceleration/audit_20261003_ternary_lift_parity_global_subcubic24_v1.md`,
SHA256 `b499e5f57712499bf55988af1c7b0043c36eb903cb4f6d9eaa80aca3474eea8a`.
These identify the earlier research context; neither parity nor the subcubic
bound is a premise below. All used adjacency, row-budget and commutation facts
are derived again. No earlier ledger theorem is imported.

## Exact candidate statements and domain

Let A be a symmetric binary 99-by-99 integer matrix with zero diagonal and
every integer row sum exactly 14. Over GF(3), put M=A^2+A+J. Let S be the
**whole** set of vertices incident with a nonzero off-diagonal entry of M,
let T be its complement, let m=|S|, and let M_S=M[S,S]. No connectivity,
maximum support degree, triangle decomposition or global lambda-one premise
is assumed. Nullity below is over GF(3).

1. If S is proper and 15<=m<=97, then nullity(M_S)>=3, equivalently
   rank(M_S)<=m-3.
2. If S is proper, m>14 and nullity(M_S)=2, then m=98. Its unique outside
   vertex z has a neighborhood P of size 14; P induces exactly a perfect
   matching; every vertex in Q=S\P, of size 84, has exactly two neighbors in
   P; every vertex in P has exactly 12 neighbors in Q; and Q induces a
   12-regular graph. The integer target identity is correct in the complete
   row of z. This is a necessary shape, not a realization of support size 98
   with nullity exactly 2, and not a target construction.

These constrain the residual matrix M_S, **not** a triangle-incidence matrix.
M=0 remains permitted. For a whole spanning support, T is empty and the
argument supplying an outside binary kernel vector is unavailable.

## Derived basic facts, including exact outside rows

Over the integers set R=A^2+A-12I-2J. Then R modulo 3 is M. The diagonal is
14-12-2=0, and every integer row sum is
14^2+14-12-2*99=0. Thus M is symmetric, has zero diagonal and M1=0. Since
A is regular and symmetric, AJ=JA, so AM=MA. All entries outside S vanish
in M, hence M has the block form diag(M_S,0) and M_S 1_S=0.

Every z in T has an integer-correct complete row, not merely a correct row
modulo 3. For each adjacent u, M_zu=0 says CN(z,u) is congruent to 1, hence
CN(z,u)>=1. For each nonadjacent u!=z it says CN(z,u) is congruent to 2,
hence CN(z,u)>=2. The sum of all off-diagonal CN(z,u) is exactly 14*13=182.
Its lower bound is also 14*1+84*2=182, so all these bounds are equalities:
CN(z,u)=1 on its 14 neighbors and CN(z,u)=2 on its 84 nonneighbors.
The diagonal CN(z,z)=14 also has the required integer value. No lambda-one
assumption on any other row was used.

Write X=A[T,S]. Commutation on the (T,S) block gives X M_S=0. Therefore
every outside neighborhood in S is a binary word in ker M_S, of Hamming
weight at most 14. X cannot be zero: if it were, both the adjacency and CN
of every pair in S times T would be zero. Their M entry would then be 1,
contradicting the zero outside rows. So at least one such word x is nonzero.

If m>14, this x cannot be 1_S. A nonzero binary vector proportional to 1_S
over GF(3) is exactly 1_S; the other nonzero scalar makes every coordinate 2.
Consequently 1_S and x are independent, proving nullity(M_S)>=2.

## Binary words when the nullity is exactly two

Assume m>14 and nullity(M_S)=2. Fix a nonzero outside word x and partition
S into its nonempty support P and complement Q, of sizes p and q. Then
ker M_S is span{1_S,x}. A vector a1_S+bx has a constant value a on Q and
a+b on P. Requiring both values to be in {0,1} gives exactly four words:
0, 1_S, 1_P and 1_Q. This classification is of binary words only; it does
not replace GF(3) by GF(2).

Because m>14, the all-S word cannot be an outside neighborhood. Every
outside vertex therefore has exactly one of the three patterns 0, P, Q.
Let their populations be n0,nP,nQ. Pattern P is impossible if p>14, and
pattern Q is impossible if q>14. A vertex of P is adjacent to every
pattern-P vertex and to no other outside vertex, so nP<=14. Likewise
nQ<=14. No zero-pattern vertex is silently omitted.

## Both classes at most 14 give a contradiction

Suppose p,q<=14. Then 15<=m<=28 and
n0=99-m-nP-nQ>=71-m.
Take any zero-pattern vertex z and any u in P. The common neighbors of z
and u can only be the neighbors of z in the pattern-P outside group:
z has no neighbor in S, and u's outside neighborhood is exactly that group.
The exact outside-row fact gives CN(z,u)=2. Therefore z has exactly two
neighbors in that group. It similarly has exactly two in the pattern-Q
group. These groups are disjoint. Counting the resulting four edges for
each zero-pattern vertex gives

  4n0 <= nP(14-p)+nQ(14-q) <= 14(28-m).

The first capacity bound uses the p or q mandatory S-neighbors of each
pattern-group vertex and retains all remaining edges as available capacity.
It is valid even if either group is empty. Combining it with n0>=71-m
gives 4(71-m)<=14(28-m), or 10m<=108, impossible for m>=15.

## One class larger than 14 gives the exceptional shape

Thus one class is larger than 14. Relabel so q>14. The other class satisfies
p<=14, because X has a nonzero row. Pattern Q is impossible. Hence every
Q vertex has no outside neighbor. A zero-pattern outside vertex z would
then have CN(z,u)=0 for every u in Q: z has no S-neighbor and u has no
T-neighbor. This contradicts the exact value 2. All outside vertices have
pattern P. Set t=|T|=99-m>=1. Every P vertex is adjacent to all t vertices
of T, so t<=14; T induces a (14-p)-regular graph.

For u in Q and z in T, CN(z,u) is the number of neighbors of u in P, hence
is exactly 2. The number of P-Q edges is therefore 2q.
For u in P and z in T, their common neighbors consist of u's P-neighbors
and z's T-neighbors. If h_u is u's degree within P, the exact adjacent
value 1 gives h_u+(14-p)=1, so h_u=p-13 for every u. Thus p is either 13
or 14. Summing the remaining degree available from P to Q gives

  2q = p[14-t-(p-13)] = p(27-t-p).

Substitute q=99-t-p to obtain

  t(p-2)=p(29-p)-198.

At p=13 this is 11t=10, impossible for an integer t. At p=14 it is
12t=12, so t=1 and m=98. Now P has degree 1 internally, giving a perfect
matching; Q has two P-neighbors and no T-neighbor, so its internal degree
is 12. Each P vertex uses one edge to T and one to its matching partner,
leaving exactly 12 to Q. This proves both candidate statements.

For the first statement, a proper support with 15<=m<=97 cannot have
nullity 1 by the independent binary outside word and cannot have nullity
2 by the classification above. Nullity is an integer, so it is at least 3.
The full 99-by-99 M has nullity |T|+nullity(M_S); this distinction must be
retained when reporting a rank bound.

## Written boundary and falsification checks

1. Empty support: M=0 is allowed. No nonzero support or kernel of triangle
   incidence is forced. The candidate does not exclude a target solution.
2. The 14-weight boundary: for m<=14 the outside word may be all of S,
   so independence from 1_S does not follow. For example the abstract
   four-vertex matrix J4-I4 over GF(3) has zero diagonal, row sums zero,
   one-dimensional kernel and a binary kernel word of weight 4. This
   illustrates that algebraic step only; it is not an actual lifted
   99-vertex graph or a counterexample to other support restrictions.
3. A spanning support m=99 has no outside rows. No outside binary-word
   argument, nullity>=3 assertion, or necessary exceptional shape is
   extended to it. This is a limitation, not a claimed spanning example.
4. In span{1_S,1_P}, enumerate the two constant coordinate values. The
   binary possibilities (Q,P)=(0,0),(0,1),(1,0),(1,1) give exactly
   0,1_P,1_Q,1_S. Vectors containing 2 are not binary adjacency words.
5. At m=15 in the both-small-class case, n0>=56 requires at least 224
   incident capacity while the bound permits at most 182. At m=28 it
   requires at least 172 while the bound is zero. The displayed linear
   inequality excludes every integer between these endpoints.
6. A class of size 15 is too large to be an outside neighborhood. Both
   classes larger than 14 would make X=0, already contradicted. These
   thresholds use exact integer degree 14, not only its residue 2.
7. In the exceptional case, p<=12 would require negative internal degree;
   p=13 would require the noninteger outside population 10/11; p=14 gives
   t=1. Neither t=0 nor an empty class is silently included.
8. The exceptional neighborhood geometry by itself is feasible in the
   stated degree domain and does not imply M=0. A written example has
   P={0,...,13} with matching {0,1},{2,3},...,{12,13}. Let Q be the 84
   nonmatching unordered pairs of P, each adjacent to its two endpoints.
   Add a root adjacent to all P. Order Q lexicographically and give it
   the circulant edges with offsets +/-1,...,+/-6 modulo 84. P has 12
   incident Q vertices, one matching edge and the root; every Q vertex
   has two endpoints and 12 Q-neighbors; the root has degree 14. The
   root has exactly one CN with each P vertex and two with each Q vertex.
   Yet the first two Q vertices {0,2},{0,3} have ten common Q-neighbors
   and their shared endpoint 0, so their adjacent integer residual is
   11+1-2=10, nonzero modulo 3. This verifies a proper, nonempty residual
   support with one good root on paper, but does not establish its exact
   support size or residual nullity. No graph file or fixture was run.
9. The polynomial lift matters. An arbitrary zero-row-sum signed block
   with A=0 can commute with A while its cross block is zero. It fails
   the actual M=A^2+A+J identity and degree domain, so it cannot falsify
   the cross-CN contradiction in this candidate.
10. On n=98 with the same degree, the lower CN budget would be
    14+83*2=180 rather than the complete count 182. The exact outside-row
    saturation used here is not asserted on that different order. Other
    degrees, directed/nonbinary matrices or another field require a
    new derivation.
11. These are exact written calculations and a specified graph family,
    not an executed enumeration, formal proof, independent verification,
    measured result or sufficiency claim. High support degree is allowed;
    no subcubic propagation assertion is reused or extended.

## Research use and limits

For any candidate proper whole residual support of size 15 through 97,
constant-only or two-dimensional ternary kernels are insufficient, even
when the support has degree 4 or higher. A viable signed support must have
at least three independent ternary kernel vectors and must contain the
actual binary outside-neighborhood words. This is a broad necessary filter,
not a large graph classification or an approved algorithm.

The polynomial lift also imposes the separately reviewed eigenvalue-1
parity constraints, but they are not used to prove this candidate and do
not manufacture a nonzero triangle-incidence kernel. Further consequences
for spanning supports, higher nullity, target nonexistence or a general
upper rank of triangle incidence remain UNKNOWN. No computational worker
was launched to prepare this note. No live worker state follows from its
timestamp or from historical receipts.

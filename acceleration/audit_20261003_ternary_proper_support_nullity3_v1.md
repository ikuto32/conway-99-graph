# Independent written derivation: proper residual support and ternary nullity

Verifier: `/root`; discovery author: `/root/structural`. Written review at
2026-10-03T08:32:48+00:00 in source context
63437c9b9fc2dd58b3bdfb51fc347b880b397503. The new files are LOCAL_ONLY and
outside the accepted371-claim publication cutoff. This is an independent
written derivation, not execution, formal verification or external review.

Raw claim source:
`docs/CANDIDATE_20261003_TERNARY_PROPER_SUPPORT_NULLITY3_V1.md`, SHA256
d4f08c8c5702045015265631e480c32b2cdb88cd7b082a3fec11e255cb400734.
Two separate statements are checked. For every simple99-vertex degree14
graph, with M=A^2+A+J over GF(3) and whole nonzero residual support S:
(i) proper15<=|S|<=97 implies nullity(M[S,S])>=3;
(ii) proper|S|>14 and nullity2 implies |S|=98 and the stated14/84 matching
neighborhood geometry. No symmetry, incidence or subcubic premise is used.

## Reconstructed argument

Let R=A^2+A-12I-2J over the integers. Its diagonal is14-12-2=0 and
its row sums are196+14-12-198=0. Reducing modulo3 gives M. In particular
M1=0 and all diagonal entries vanish. Regularity gives AJ=JA, so AM=MA.

For z outside S, all off-diagonal residues in its row vanish. Adjacent
common-neighbor counts are nonnegative integers congruent to1 modulo3;
nonadjacent counts are congruent to2. Their exact sum is14*13=182.
The fourteen adjacent and84 nonadjacent lower bounds already total
14+2*84=182. Therefore every one equals its lower bound. The entire
integer target row at z is correct, including its diagonal. This supplies
exact values1 and2 below, without a lambda-one assumption elsewhere.

Partition A by S,T. The residual has blocks diag(M_S,0). The lower-left
commutation equation is A[T,S]M_S=0. Every outside neighborhood in S is
thus a binary kernel vector of weight at most14. The cross block cannot
vanish: with no cross edge, every cross common-neighbor count is0,
contradicting the exact outside-row value2. Consequently there is a
nonzero binary kernel word x. When m=|S|>14, x cannot be1_S, and cannot
be the other nonzero scalar multiple2*1_S. Since1_S is also in the
kernel, its dimension is at least2.

Assume its dimension equals2. Put P=supp(x), Q=S minus P. Both are
nonempty. A kernel vector has two constant values, one on P and one
on Q. Requiring both to belong to{0,1} gives exactly0,1_P,1_Q,1_S.
The all-S neighborhood is too large. Let n0,nP,nQ count the remaining
outside patterns0,P,Q. A vertex in P has exactly nP neighbors in T;
a vertex in Q has nQ, whence each count is at most14.

If p=|P| and q=|Q| are both at most14, then15<=m<=28 and
n0=99-m-nP-nQ>=71-m. For a zero-pattern vertex z and any u in P,
CN(z,u) counts exactly z's neighbors in the pattern-P group, and is2.
The analogous Q count is2. These four edges per zero-pattern vertex
must fit the pattern groups' remaining degree capacities:

    4(71-m) <= 4n0 <= nP(14-p)+nQ(14-q) <= 14(28-m).

Rearrangement gives10m<=108, impossible for m>=15. This reasoning
keeps zero-pattern vertices and allows empty pattern groups; an empty
required group would itself contradict the exact count2.

One class must therefore have size>14. Name it Q. No outside vertex
has pattern Q. A zero-pattern vertex would have no common neighbor
with any Q vertex, since the former has no S neighbor and the latter
has no T neighbor. Thus every outside vertex has pattern P. Set
t=|T|>=1. We have p<=14 and t<=14, and T is(14-p)-regular.

For z in T and u in Q, exact CN(z,u)=2 says every Q vertex has two
P neighbors, giving2q P-Q edges. For u in P, CN(z,u)=1 is its degree
within P plus14-p. Thus that internal degree is p-13, and p is13
or14. The remaining P-to-Q capacity gives

    2q = p(27-t-p),  q=99-t-p,
    t(p-2)=p(29-p)-198.

For p13,11t=10 is impossible; for p14,12t=12 gives t1 and m98.
P then induces a1-regular graph, hence seven matching edges. Each
P vertex has12 Q neighbors. Each Q vertex has two P neighbors and
no T neighbor, hence twelve Q neighbors. This proves the exceptional
necessary geometry and excludes nullity2 for m15 through97. Combined
with the separately proved nullity>=2, it proves statement(i).

## Attempts to falsify the steps and exact limits

1. m<=14: x could be1_S, so the independence argument is deliberately
   restricted. No nullity>=3 statement is made for that boundary.
2. m99: there is no outside vertex or cross block. Neither statement
   extends to a spanning support.
3. M0: empty support remains allowed; the argument assumes a nonempty
   proper support and establishes no nonexistence of the target.
4. The binary classification enumerates the four possible constant
   coordinate pairs. Ternary vectors containing2 are not adjacency
   neighborhoods. No GF(2) nullity is substituted.
5. The both-small inequality at m15 is224<=182, already impossible;
   its contradiction becomes stronger as m increases to28.
6. p13 requires the noninteger t10/11. p14 gives t1 and the exact
   degree decomposition1+1+12 on P and2+12 on Q.
7. The stated necessary geometry is not sufficient for nullity2 or
   support98. In the paper's explicit matching/pair/circulant example,
   the first adjacent Q vertices have ten common Q neighbors and
   one common P endpoint, so their residual is11+1-2=10, nonzero
   modulo3. I checked this count directly from the twelve offsets;
   no99-by99 fixture or support/nullity calculation was executed.
8. Replacing order99 by98 makes the lower budget180 rather than182,
   so outside-row exactness cannot be transferred by this argument.
9. Residual and triangle-incidence ranks are different objects. No
   implication for a nonconstant triangle-incidence kernel is used.

Outcome: both exact scoped statements pass independent written derivation.
No computational commands, executed controls, exhaustive enumeration, graph
candidate or formal proof were used for this mathematical review. Shared
components are the stated graph axioms and ordinary exact integer/GF(3)
algebra. Metadata hashing commands identify files; they are not proof checks.
This report makes no novelty, public-replay or external-acceptance claim.

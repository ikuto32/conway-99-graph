# Candidate unrestricted triangle normalization and partial-factor theorem

This is a universal derivation submitted for independent review. Let A be
a symmetric binary zero-diagonal99x99matrix satisfying, over the integers,

`A^2 = 12I - A + 2J`.

No prism-free or automorphism assumption is made. The theorem below asserts
coverage of every such A up to vertex labels, not existence of any A.

## 1. A triangle and its three fibres

The diagonal identity gives degree14 at every vertex. Choose any edge
t0--t1; the off-diagonal identity gives exactly one common neighbour t2,
so T={t0,t1,t2} is a triangle. No other vertex can neighbour two vertices of
T: that edge's common neighbour quota is already occupied by the third
vertex of T. Let Ai be the outside neighbours of ti, and let Y be the
vertices with no neighbour in T. Then the three Ai are disjoint of size12,
and Y has size60.

For x in Ai, the edge x--ti must have one common neighbour. Neither other
root vertex neighbours x, so that neighbour lies in Ai. Each x has exactly
one neighbour in Ai; consequently the internal graph is a perfect matching
Mi. For j!=i, x and tj are nonadjacent and have exactly two common
neighbours. One is ti; the other is a unique neighbour of x in Aj. Applying
this at both ends shows that every Ai--Aj block is a perfect matching.

Thus every x in Ai has four neighbours in T union A0 union A1 union A2,
and ten in Y. For y in Y, the nonedge y--ti has its two common neighbours
inside Ai. Therefore every incidence column has exactly two ones in each
fibre, six in total; every y has eight neighbours in Y.

## 2. Complete coordinate normalization

Choose labels0..11 on A0 by listing the six pairs of M0, making the matching
`i <-> i xor1`. Label each A1 vertex by the label of its unique neighbour
in A0. Do the same for A2. The A0--A1 and A0--A2 blocks are now identity.
The two other internal matchings M1,M2 remain arbitrary fixed-point-free
involutions. Write the A1--A2 adjacency block as P: `P[i,j]=1` means that
label i in A1 is adjacent to label j in A2. P is an arbitrary permutation
matrix, and the reverse block is P^T. In particular P need not be an
involution or a derangement, and none of these permutations need commute.

This labels an arbitrary input target; it does not require the relabelling
to extend to a nonidentity automorphism. No restriction on M1,M2,P beyond
the stated types is imposed by the coordinate choice.

## 3. Canonical outside labels

Let Ci be the12x60Ai-to-Y incidence matrix. Every column of C0 has two ones.
Their two row labels cannot be matched by M0: an adjacent pair in A0
already has t0 as its unique common neighbour. If a,b are a nonmatching
pair in A0, they share t0 and no other vertex in T union A0 union A1 union
A2. Internally the matching has disjoint singleton neighbourhoods, and
each cross perfect matching sends distinct vertices to distinct neighbours.
Their required second common neighbour is therefore exactly one vertex of Y.

It follows that the columns of C0 biject with all unordered nonmatching
pairs of A0. There are `binom(12,2)-6=60` of them. Label Y by those pairs in
lexicographic order and fix `C0[a,e]=1 iff a in e`. This is only a permutation
of Y and is compatible with the preceding core coordinate choices. The
same reasoning applies separately to each Ci relative to Mi, but their
column orders remain coupled by the actual common Y labels.

## 4. Exact variable-core Gram blocks

Use the order T,A0,A1,A2,Y, and write

```text
C = [ M0  I   I ]       F = [ C0 ]
    [ I   M1  P ]           [ C1 ]
    [ I   P^T M2]           [ C2 ].
```

Let R be the36x3fibre-indicator matrix, so RR^T=diag(J12,J12,J12).
The X-by-Xblock of the target identity gives

`FF^T = 12I - C - C^2 + 2J - RR^T = G`.

Since each Mi squares to I and every cross block is a permutation,

```text
Gii = 9I + J - Mi,
G01 = 2J - I - M0 - M1 - P^T,
G02 = 2J - I - M0 - M2 - P,
G12 = 2J - I - P - M1 P - P M2.
```

The reverse blocks are transposes. The positions of P and P^T follow from
the declared row/column convention; replacing them silently is invalid.
The formulas are identities for arbitrary three matchings and P, whether
or not a particular core admits a binary factor.

## 5. Necessary column conditions and the precise converse boundary

Besides binary entries, row sums10, fibre-column sums2, canonical C0 and
the full Gram identity, a target factor obeys the following exact conditions.
For each column f_y, known common neighbours of x in X and y in Y are
`(C f_y)_x`. Thus

`(I+C)f_y <= 2*1`.

For different y,z in Y, their known common neighbours lie in X, giving

`f_y^T f_z <= 2`.

If a future residual edge D_yz is one, the stronger bound is
`f_y^T f_z<=1`. Equivalently intersection2 forces D_yz=0 in any completion.
These inequalities are necessary exact constraints, not numerical tests.

Conversely, data of the stated types satisfying the Gram, margins and both
column-cap inequalities define a symmetric partial99graph by leaving every
Y--Y off-diagonal entry unknown. Its T and X vertices have degree14, its Y
vertices have known degree6 and residual degree requirement8, every pair
inside T union X already has its exact target common count, T--Y pairs have
their exact count2, and all other known common-neighbour caps hold. This is
only a partial-factor specification. It does not claim a compatible D.
Completion additionally requires symmetric binary zero-diagonal D with

`F D = 2J-F-CF` and `D^2+F^TF=12I-D+2J`.

The earlier residual-equivalence theorem supplies the appropriate conditional
completion statement. A future UNSAT proof for a correctly covered arbitrary
M1/M2/P factor model could exclude all targets via the normalization above;
a SAT factor alone would not resolve the target.

## 6. Calibration and archive overlap

The written normalization and counting arguments provide universal coverage.
The controls only exercise its implementation. The valid rook9graph is
srg(9,4,1,2), with two-point fibres and an empty Y; its empty column
canonicalization is explicitly degenerate. Separate arbitrary12vertex core
fixtures check every algebraic coefficient, including nonsymmetric P and
noncommuting matchings, without claiming target feasibility. Scrambled
nonempty canonical incidence matrices exercise the Y-label bijection.

Pinned archive Wave149 already gives the general triangle partition and
block equations before specializing to a prism-free fixed example. Wave151
already explains the nonmatching-edge incidence bijection in that example's
factor setting. This package rederives the universal normalization and
variable-core scope explicitly. The archive-overlap record identifies exact
immutable paths and sections. Historical verification labels are not fresh
approval, and no novelty is claimed. The current result remains CANDIDATE
until a different reviewer checks the proof and raw artifacts.

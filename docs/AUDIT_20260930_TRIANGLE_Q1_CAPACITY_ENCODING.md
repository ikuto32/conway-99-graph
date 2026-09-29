# Independent Q1 capacity-projection audit

Start from the independently checked fixed 39-vertex core, its forced
36-by-36 Gram K, and the canonical lexicographic C0 column labels. Retain
only the first 24 rows (C0;C1). The full factor's restriction must satisfy
the corresponding 24-by-24 Gram, row margins ten and two ones per fibre
per column. The independently checked component balance says every full
column has exactly two ones in each of the three core components. Deleting
the nonnegative C2 rows therefore gives an upper bound of two on each
retained component-column sum. This implication is necessary only.

The projection leaves all 600 unforced entries of C1 free. The 120 folded
zeros are precisely those forced by zero C0-cross Gram entries; every other
position is retained. It adds 12 row equations, 60 column equations, 144
C0-cross Gram equations, 66 C1-pair Gram equations and 180 component caps.
The diagonal Gram follows from binary row sums; C0's own Gram is fixed.
Thus these equations and inequalities are exactly the declared projection.

As in the separately audited base checker, a bidirectional AND denotes its
literal incidence product and each bidirectional prefix state is the exact
prefix threshold. Equality k requires threshold k and forbids k+1; an upper
bound k forbids k+1. The complete independently reconstructed counter rows
and clauses establish both directions of satisfiability equivalence to this
24-row problem. They do not establish extension to C2 or a target graph.

Every C1 column has two ones. Its within-fibre Gram is zero on matching
partners and one on each other unordered pair. Consequently the sixty
columns are precisely the sixty distinct edges of K12 minus the canonical
matching, and their indices in the canonical edge list form the Q1
permutation. The raw checker constructs this permutation from the matrix,
checks bijectivity, and reconstructs every column from it.

The audit uses the prior independently authored raw-core/Gram builder,
component-kernel checking path and GateAudit helper with pinned source
identities. It does not import the producer. Every new clause and scope
entry is checked, with fresh threshold and corrupted scope controls.
Object controls include archived 24-row exact-Gram factors which must fail
the capacity test, and a separately labelled synthetic positive factor
whose own Gram is not the research Gram. No positive research projection
is assumed before its raw object is independently checked.

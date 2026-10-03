# Independent compact column-cap equivalence

The retained prefix imposes the same 25-row margins, all principal Gram
equalities and component capacities as the audited original formula. In
particular, each C1 column has exactly two ones. Its within-fibre Gram has
zero entries on matching partners and one on all other distinct row pairs.
Thus no two C1 columns can be the same pair: that would contribute at least
two to a Gram entry bounded by one. Consequently distinct C1 columns
intersect in at most one row. This argument uses retained equations, not a
target extension or an automorphism assumption.

For two outside columns d,e write k for their fixed C0 overlap, q for their
C1 overlap, and y_d,y_e for their selected C2 entries. Both k and q are zero
or one. The original cap is k+q+y_d*y_e<=2. If k=0 it is automatic. If k=1
it fails exactly when y_d=y_e=1 and the two C1 columns share a row r.
This is exactly the conjunction, for every C1 row r, of

    not C1[r,d] or not C1[r,e] or not y_d or not y_e.

If one of those entries is a frozen zero, the clause is a tautology and may
be omitted. Otherwise its four distinct negative literals must be emitted.
The audit reconstructs the whole population of 540 intersecting C0 column
pairs times twelve C1 rows: 6,480 templates, comprising 3,645 clauses and
2,835 fixed-zero tautologies. The other 1,230 C0 column pairs are covered
by the k=0 argument, not by a sampled omission test.

The new formula retains exactly the first 77,721 original body clauses and
their 22,379 variables, and appends those 3,645 clauses. All retained model
fields, row/product intervals and prefix bytes are checked against the
independently audited original. The discarded auxiliaries in the original
suffix have unique values determined by the primary incidences. Therefore
each compact model extends to an original model, and every original model
restricts to a compact model. The formulas have precisely the same primary
solutions; no new family restriction or coverage assertion is introduced.

Distinctness of C1 columns is essential. With k=0, two duplicate C1 columns
give q=2; setting both y entries to one violates the original cap while an
unguarded omission would accept. A corrupted-premise control records this
counterexample. Exhaustive small bitset and four-literal truth checks
calibrate the algebra and clause construction; the general argument above
establishes equivalence under the retained prefix.

No solver performance conclusion follows from the smaller formula. The
known original SAT assignment can be restricted to the retained variable
IDs and directly checked against the complete compact CNF, without a new
solver call. That is a derived assignment certificate, not another solve.

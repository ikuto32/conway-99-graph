# Independent full-factor column-cap review

This audit uses the frozen independent component-factor encoding gate as an
explicit premise. It checks byte identity of the complete base body and
independently reconstructs every new clause and every fixed-zero omission.
It reuses the independent raw-core/Gram constructor and component-kernel
checker, with exact source hashes, and imports no producer code.

The scope is the explicitly saved 39-vertex triangle core. A target containing
this core yields a binary 36 by 60 outside-incidence matrix C satisfying the
audited Gram and margin equations. The C0 column normalization is the already
audited relabelling of outside vertices; it assumes no automorphism of a
hypothetical target. Nothing here proves that every target contains this core.

In each fibre, each column has exactly two ones. Paired rows have scalar
product zero, so its two endpoints cannot be mates. Every other distinct row
pair has scalar product one, so no two columns can have the same endpoints.
There are exactly 60 nonmatching two-subsets and 60 columns, hence each fibre
is an ordering of these subsets. Two distinct columns therefore intersect
in at most one row of each fibre. This argument uses both margins and the
within-fibre Gram equations, which remain present in the base formula.

For distinct columns d,e, let k,q1,q2 denote these three intersections.
Each is zero or one. If k=0 then the desired total intersection is at most
two automatically. If k=1, that bound is equivalent to forbidding q1=q2=1.
The latter condition is exactly the conjunction, over all C1 rows r and C2
rows s, of

    -C[r,d] OR -C[r,e] OR -C[s,d] OR -C[s,e].

The two products can be simultaneously one precisely when some such pair
r,s exists. A fixed-zero entry makes a clause tautological; all other four
references are distinct primary variables. The independent checker enumerates
all 540 intersecting C0 pairs times 144 row pairs, authenticates every mapping,
and compares all emitted clause bytes. The 1,230 disjoint C0 pairs are omitted
by the proved bound, not by sampling. There are 43,740 emitted clauses and
34,020 fixed-zero tautologies.

Thus the new formula's primary solutions are exactly the base factor
solutions with all 1,770 column-overlap bounds. This is an exact equivalence
for the declared extended factor problem. These bounds are not claimed to
follow from the abstract Gram equations. They are necessary for a target:
the columns represent two distinct outside vertices, and their 36 recorded
common neighbours form a subset of their at most two total common neighbours.
Residual outside edges D are absent. SAT supplies only an incidence factor;
UNSAT would require a separately checked complete proof and would exclude
only targets containing the fixed core.

Controls independently exhaust all triples of distinct nonmatching pair
intersections for n=4 and n=6, check all four-literal Boolean assignments,
and exhibit the failure of the omission rule without column distinctness.
Changed references, omitted templates, wrong clause positions, false zero
reasons, changed fixed scope and changed CNF bytes must be rejected.

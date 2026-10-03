# Strengthen the balanced parity projection with support constraints

Question: does the necessary parity projection remain satisfiable after
requiring a constant group whenever a coordinate pair has zero parity
disagreements? The previous fixed parity assignment is not retried unchanged.
Preserve its valid projection witness and failed coloring lift.

Append exactly sixty clauses to the frozen 520-variable, 4,481-clause formula.
For each nonmatched coordinate pair, the clause contains its five difference
variables and the constant-pattern selector of each of its five containing
groups. It expresses: some disagreement or some constant group.

Necessity is conditional on balanced triplets of the exact saved support.
In a mixed balanced triplet all six S3 permutations occur once. Same-parity
coordinates have a nonidentity even relative permutation and contribute
zero to every same-fibre Gram entry. Five such co-occurrences would contradict
the required Gram entry one. Balance is not WLOG for arbitrary factors.
The prior formula's nonconstant clause additionally uses the checked cyclic
exclusion with outside-column caps. No target automorphism is assumed.

Build only, with no solver calls, in at most 60 seconds. Save exact prefix,
all sixty clauses, model metadata, old-witness falsification and truth controls.
No floating arithmetic is used. Independently check the lemma, full prefix
and clauses, and the object path before any native run. SAT is only a parity
projection witness. UNSAT needs full proof replay and verified coverage of
this conditional family; it is not an unrestricted target exclusion.

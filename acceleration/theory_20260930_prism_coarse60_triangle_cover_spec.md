# Coarse60 residual-triangle cover scout

Frozen before execution. Question: can the fixed 60 coarse columns be
partitioned into twenty triples that pass the necessary coarse disjointness
test for residual triangles? This is a necessary screen for target completions
of this fixed six-prism template, not a complete factor or graph search.

Pin the independent identity-P conditional triangle-partition lemma. In a
completed target every residual triangle has three pairwise disjoint incidence
columns: its adjacent pair already has its unique common neighbor at the third
triangle vertex. For one component, three columns in the same fibre would use
only two coordinate bits and cannot be pairwise disjoint. If exactly two have
the same fibre, those two bits must differ. If all three fibres differ there
is no disjointness restriction for that component. These conditions are also
sufficient for disjointness of just the three raw columns, ignoring all global
Gram constraints. They are not sufficient for extension to a factor or target.

Enumerate all choose(60,3)=34,220 triples lexicographically. Save every triple,
all components causing pigeonhole rejection, and all opposite-bit requirements
for admissible triples, with bit IDs looked up from the frozen model. Derive
the number of local bit assignments as 2^(18-r), where r is the number of
independent opposite-bit requirements, and calibrate by exhaustive three-column
component controls and deliberately corrupted classifications/bit witnesses.

On the resulting hypergraph, find the first exact cover with deterministic
Algorithm X: choose an uncovered column with fewest fully available triples,
tie by column index, and try triple IDs in increasing order. Save the complete
visited search tree and a literal twenty-triple witness if found. Bound total
wall time by 120 seconds and search nodes by 100,000. If exhausted without a
witness, a nonexistence result requires complete independently replayed search;
if either bound interrupts, status remains UNKNOWN and frontier records are
preserved. No SAT solver, random seed, source/input mutation or CNF construction.

Known-valid and impossible tiny exact-cover instances calibrate the traversal.
Explicitly distinguish a coarse cover witness, a compatible raw bit assignment,
a full factor, residual D and a target graph. A found coarse cover may be
lifted to independently chosen local bits to check only triangle disjointness;
those bits have no promised Gram or row margins. No auto/bit normalization is
assumed, and the scout does not exclude other coarse multiplicity templates.

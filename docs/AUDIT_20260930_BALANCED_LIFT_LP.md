# Independent selected-parity colouring-lift LP audit

This audit is restricted to the first independently checked parity assignment
on the saved six-prism Hadamard support. Its sixteen mixed groups and four
constant groups admit twelve and thirty unordered balanced local triples,
respectively: 312 selector columns. No other parity assignment, unbalanced
triple, different support, whole core or unrestricted graph is covered.

The independent checker generates balanced triples from colour words directly.
Choose a balanced first word; at each of its six coordinates choose one of the
other two colours for the second word, and let the third word be the unused
colour. Retain balanced second and third words, sort the three words, and
deduplicate. This exhausts all 150 unordered coordinatewise balanced triples
without importing the producer's domain code or its S3 classification routine.
The parity of the three colours at each coordinate is computed and gauged by
the first coordinate. Filtering by the authenticated twenty selected patterns
gives the exact 312-column domain.

For a selector belonging to group p, its first coefficient is the group
normalization row p. Each of the fifteen coordinate pairs in its support
contributes three colour-pair incidences from the three columns. Because every
coordinate takes every colour once, these incidences are distinct, so every
coefficient is zero or one and each selector has exactly 46 nonzero entries.
The row universe consists of twenty normalizations and nine ordered colour
pairs for each of sixty nonmatching coordinate pairs: 560 rows. Required
colour-pair values are one for equal colours and two for unequal colours.
All these coefficients are reconstructed from literal raw incidence rows.

These equalities are necessary for a full prescribed-Gram lift of the fixed
parity branch. Diagonal row counts and pairs from one matched coordinate pair
are automatic in these balanced domains. The LP imposes only nonnegative real
selector weights. It omits integrality, between-group outside-column caps,
and residual D. Consequently a nonnegative rational primal vector establishes
only relaxation feasibility. A vector y with every column product A^T y
nonnegative and y^T b strictly negative excludes this relaxation and therefore
every full factor in this one branch, without excluding other parity choices.

The principal positive control is the same raw twenty-group geometry with all
150 balanced triples allowed per group. Uniform rational weight 1/150 is
checked against all 560 reconstructed rows. It is a genuine exact LP control,
not an asserted integer factor. Tiny feasible/infeasible systems and corrupted
primal, dual, matrix and right-hand-side values supplement it.

Every accepted rational coefficient is parsed as an exact integer fraction.
For every saved integer repair trial the checker recomputes all 312 column
products and the right-hand-side product, including failed trials. It also
checks that each group-normalization increment equals the minimal nonnegative
integer that repairs its columns. Floating rays and solver statuses are
preserved provenance only; no numerical tolerance participates in certificate
acceptance. No LP or SAT solver is called by this audit.

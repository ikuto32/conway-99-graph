# Bounded triangle-factor continuation preflight

Frozen source: external_conway99_research at commit
85e705cc6c2a14d123120c93a847e30aaab1789e, waves149/151/154.
Do not change the archive or import its verification labels into current claims.
The two fixed-Q1 UNSAT diagnostics have no proof. Wave154 already attempted a
180-second CaDiCaL195 proof export without completing, so repeating that exact
search is not the selected next experiment.

Cheap question: do either displayed 24-by-60 partial factors already contradict
the necessary linear equations for the third incidence group, or those equations
together with the residual symmetric8regular block? Independently rebuild the
edge universe and target Gram formulas, compare all stored Gram entries, and
replay each Q1's exact two-group Gram before any feasibility tests.

First test C01*x=the prescribed third-row cross-Gram vector over primes
2,3,5,7,11,13. Then build the exact necessary linear system in720C2 entries and
1770symmetric D-edge entries: both known-group mixed block equations, C2 row/column
degrees, D degrees, both cross-Gram equations, and individually forced zero C2
entries. Check this system over GF(2) using exact elimination. Save all raw integer
equations, variable labels, and any explicit left-kernel contradiction for review.
This remains conditional on the particular root scaffold and Q1. It is not an
unrestricted normalization and assumes no target automorphism.

Budget:120seconds overall, no native SAT/MIP solver. Stop after both displayed Q1
cases. A modular contradiction is CANDIDATE until a separate checker reproduces
the raw row combination. Consistency is only failure of this necessary-condition
falsifier, not evidence of integer/binary feasibility. Calibrate elimination on
consistent and inconsistent systems and reject a deliberately corrupted witness.

Also census a prospective alternative row-incidence factor CNF: C2 row membership
variables, exact known-group intersections, exact two-per-column, and exact pair
intersections within C2. This is a distinct representation from the archived
1620edge-mapping variables. Estimate exact primary/product and row counts before
any costly solve; all eventual encoding equivalence and proof claims need fresh
independent gates.

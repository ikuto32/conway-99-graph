# E72 source150 synchronized-config independent audit

Status: **SOURCE150_SYNCHRONIZED_LOCALPAIR_AUDIT_PASS**.

The four ordinary global frontiers were reconstructed exactly, with solution counts 143, 64, 2,331, and 380. All reported configurations, solution paths, and forward/backward DP counts agree.

For macro `(3,0)`, 74 of 76 local orbits (mass 16,000 of 16,384) are exact local UNSAT. For macro `(8,0)`, 33 of 56 local orbits (mass 10,496 of 16,384) are exact local UNSAT. Combined, 107 orbits of labelled mass 26,496 are excluded and 25 orbits of mass 6,272 remain locally SAT; there are no UNKNOWN cases.

The audit independently rebuilt all labelled one-sided ordinary--E maps and all twelve disjoint E--E blocks with both margins, then used a different complete DFS order. All 132 statuses and 48 producer controls were reproduced.

Adding the residual-zero ordinary-local-pair condition excludes all 132 orbits / 32,768 mass in the two macros. The independent audit did not use the producer's quotient by equal-pattern U labels.

Boundary: these are exact executable local exclusions, not a formal proof-assistant certificate. A surviving local CSP witness is not a 99-vertex graph.

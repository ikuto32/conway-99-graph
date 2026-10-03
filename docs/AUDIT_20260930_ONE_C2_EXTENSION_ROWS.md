# Independent complete remaining-row exclusions for one fixed25-row object

Fix only the raw 39-vertex core, the canonical C0, the verified twelve C1
rows and the verified coordinate-zero C2 row. The audit reconstructs this
partial99matrix from the independently checked25-row incidence artifact.
The other660C2 incidences and1770outside-outside edges remain unknown.
No historical propagation assignments are used.

For each vertex u from28through38, its sixty unknown outside incidences are
binary variables. Its four known core neighbors leave row degree ten. Each
comparison vertex v from3through27 has a completely known adjacency row,
so the exact target common-neighbor identity becomes a linear equality in
the sixty variables, subtracting the literal already-known common neighbors.
For two outside columns whose already-known common-neighbor count is two,
u cannot be adjacent to both. Their mutual edge is still unknown, so using
the upper bound two is necessary in either eventual adjacency state.

These constraints are necessary for any target completion of this exact
partial graph. They need not suffice for a completion. The independent
checker reconstructs every variable and constraint from the raw graph and
uses a separately authored complete binary-tree verifier. Each forced bit
is justified by the impossible interval obtained from its opposite value;
every split covers both values exactly once, and each leaf has an exact
integer interval contradiction. All nodes are reached exactly once, so
neither omitted branches nor unreachable proof decorations are accepted.

Every one of the eleven supplied row trees is complete and contradictory.
Any one excludes completion of this fixed25-row object. This does not
exclude the same Q1 with a different selected C2 row, all Q1 choices, all
fixed-core incidence factors, or unrestricted Conway99.

The audit reruns the shared independent verifier's exact SAT/UNSAT and
masked-rook controls, and applies fresh wrong-force, missing-branch and
false-leaf corruptions to actual trees. Helper reuse is explicit; neither
the producer's constraint builder nor its search implementation is imported.

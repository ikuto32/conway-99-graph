# E72 source133 solver-free chain audit

Status: **SOLVER_FREE_CHAIN_AUDIT_PASS**.

The eight shard slices exactly partition all 5,138 regular-macro masks. The hash-bound finite-map chain is 5,138 -> 81 -> 1 -> 0 orbits, with labelled masses 1,129,056 -> 9,952 -> 16 -> 0. The independent 48-vertex SAT census also reports all 5,138 UNSAT.

The audit independently checked mask/pair indexing, local 00/01/10/11 labelling, all truth cases of the opposite/overlap collision rules, and every equation-(32) residual plus local/global same-fibre pair mapping.

Boundary: this is an exact executable standard-library enumeration, not a proof-assistant certificate; it depends on the separately audited frontier and H/F derivation. Macro 4 is covered separately by full-CNF DRUP.

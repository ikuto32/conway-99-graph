# Broader rook-star CNF with four internal matchings free

Status: CANDIDATE encoding, pending a fresh independent gate. No target
resolution, universal rook containment, or graph automorphism is assumed.

This strictly broadens the earlier fixed-star 600-edge model. It retains
only the central ten-vertex internal matching and the four ten-by-ten
central incidence blocks from the exact raw witness at
`results/20260930_rook_cell_factors/local_witness.json` (SHA-256
`da71c5381af0a68f8a7e7dea36535b92cbcfc67d95e3b57d6cc3591dd1dda33f`).
Its recorded `partner_matching` entries for the four right cells are ignored.

All 45 possible internal edges of each right cell become independent Boolean
variables, adding 180 variables. Every right-cell vertex gets internal degree
exactly one. The 600 cross-cell variables and their 120 exact degree rows are
unchanged: four adjacent cell-pair perfect matchings and two nonadjacent
cell-pair bipartite graphs of row/column degree two.

There are consequently 780 independent edge variables and 160 degree rows.
All 1,225 inequalities `same_cell + sum_w A_uw*A_vw + A_uv <= 2` are regenerated
with the new variable products. No right-cell internal matching is fixed or
normalized. The generic exact AND/direct-subset cardinality encoder is reused
from the frozen earlier producer with its exact source hash recorded; the
new known-adjacency mask and all degree groups need separate independent
checking. Existing independent approval of the 600-edge instance does not
approve this instance automatically.

Question: does any choice of the four right internal matchings and all six
right cross-cell blocks satisfy the necessary local window constraints for
this fixed central factor star? A decoded SAT assignment is only a local
window and must pass a separate literal graph check. A checked UNSAT proof
would exclude this broader fixed-central-star family, still only conditional
and far narrower than all targets with an induced rook.

Generation is finite and deterministic. The declared upper estimate is
32,000 total variables and 4,000,000 direct clauses; exceeding either is an
error requiring a new protocol rather than silently growing the experiment.
The first solve is capped at 300 seconds including parse/load/finalization
and 1,000,000 conflicts, after a fresh independent encoding gate. Preserve
caps/errors as UNKNOWN, and preserve the original instance and its evidence.

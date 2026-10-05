# Fixed-star 50-vertex window: SAT encoding specification

Status: CANDIDATE encoding; requires independent model review and controls
before the 300-second solver pilot. The encoded scope is strictly conditional.
It leaves four perfect-matchings and two bipartite 2-regular blocks free, while
fixing the exact central factor star and all five internal matchings from
`results/20260930_rook_cell_factors/local_witness.json`, SHA-256
`da71c5381af0a68f8a7e7dea36535b92cbcfc67d95e3b57d6cc3591dd1dda33f`.

Vertex labels are as in `theory_20260930_rook_followup.md`: five cells of ten,
attached to rook cells (0,0),(1,1),(1,2),(2,1),(2,2). All edges within each
cell and from cell 0 to another cell are fixed by the input. All 600 possible
edges between distinct cells in {1,2,3,4} are independent Boolean variables;
there are no additional identification or automorphism constraints.

Each of the four rook-adjacent cell pairs (1,2),(1,3),(2,4),(3,4) gets row and
column degree exactly one. The two remaining pairs (1,4),(2,3) get row and
column degree exactly two. These are complete labelled domains, with no
restriction to the prior sampled permutation lists.

For each unordered external vertex pair u,v, let a_uv be its fixed binary
adjacency or its edge variable. A vertex w contributes a_uw*a_vw to its known
common-neighbor count. A zero factor contributes zero. Two constant-one
factors contribute one. A variable and a constant one contribute that
variable. Two variables x,y are represented by a new z with exactly the
three defining clauses `(-z or x)`, `(-z or y)`, `(z or -x or -y)`.
There is no one-direction-only product relaxation.

The two vertices also have one common rook neighbor exactly when they lie in
the same cell. For **every** unordered pair u<v, encode

```
1[same cell] + sum_w a_uw*a_vw + a_uv <= 2.
```

These are all 1,225 known common-neighbor upper bounds. They are necessary
for any extension to the full target; omitted vertices can only add common
neighbors. They are not the complete common-neighbor equalities of the
99-vertex problem. No external-vertex degree 14 is imposed on this proper
window. Diagonal, binary, and symmetry conditions are built into edge IDs.

All cardinality constraints are generated directly: `sum(x)<=k` becomes one
all-negative clause for each (k+1)-subset; `sum(x)>=k` becomes one all-positive
clause for each (n-k+1)-subset. Constants are removed exactly. A negative
remaining upper bound emits the empty clause. This elementary encoding is
larger than a sequential counter but easy to audit. Variables inside each
cardinality constraint are distinct; a duplicate must be rejected by the
producer instead of accidentally treating it as an unweighted sum.

The producer will save the full known adjacency, 600 edge IDs, exact product
definitions, degree rows, all pair upper-bound descriptions, raw DIMACS CNF,
and hashes. It will use no solver-dependent encoder. Calibration will use
the same generic encoder on the known-valid rook-nine graph with all its
edges variable and degree-four constraints. A known adjacency assignment and
the exact products must satisfy every clause; a deliberately corrupted edge
assignment must fail. Direct at-most/exactly gates on small complete Boolean
domains will be checked against integer cardinalities.

Before expensive solving, a separate reviewer must check the claim that a
target extending the fixed star produces a satisfying assignment, and that
a satisfying assignment decodes to the stated local window. A SAT result
requires a separate direct check of the decoded raw adjacency. An UNSAT
result additionally needs its full raw proof, solver/checker versions,
input/proof hashes and independent proof replay. Even then it only excludes
this exact fixed-star family and says nothing about unrestricted existence.

Pilot resource limit: 300 seconds including parse/load/proof finalization,
and a separately recorded finite solver conflict cap. Preserve UNKNOWN on
caps/errors. No new dependency or uv.lock modification is authorized by this
specification; dependency coordination is handled with the root agent first.

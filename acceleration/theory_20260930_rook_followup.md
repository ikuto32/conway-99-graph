# Exact rook-cell follow-up: one relaxed witness fails completion

Discovery status: **CANDIDATE**, pending independent review. All results below
are restricted to induced-rook models or exact pinned local artifacts. None
constructs a 99-vertex target or excludes all targets containing a rook graph.
The discovery agent does not approve these claims.

The first stage is the conditional necessary two-factor condition proved in
`theory_20260930_rook_cell_factors.md`. It produced 89,000 distinct labelled
two-factors on one ten-vertex cell avoiding a fixed matching, and an explicit
four-factor partition of `K10 - F`. These outputs are saved in
`results/20260930_rook_cell_factors/`; their manifest freezes the exact input
hashes, source commit, command and scope. The partition is a positive control
for the single-cell diagonal-block condition, not a target graph.

## Frozen labels and off-diagonal test

The 50 external vertices use cells of ten consecutive labels. Cell 0 is
attached to rook vertex (0,0). Cells 1,2,3,4 are attached to (1,1), (1,2),
(2,1), (2,2), respectively. Each external vertex has its unique rook neighbor.
The source witness fixes each cell's internal matching and four incidence
blocks from cell 0 to cells 1 through 4. Thus each such incidence block has
row and column degree two. The unknown right-cell pairs (1,2),(1,3),(2,4),
(3,4) are rook-adjacent and must be perfect matchings. The remaining two pairs
(1,4),(2,3) must be 2-regular bipartite graphs.

For a three-cell window 0,Y,Z with fixed matrices C,D and internal matchings
F0,FY,FZ, let P be the unknown Y-Z permutation matrix. The common-neighbor
upper bounds involving different cells are exactly the entrywise inequalities

```
F0 C + C FY + D P^T <= 2J - C,
F0 D + D FZ + C P   <= 2J - D,
C^T D + FY P + P FZ <= 2J - P.
```

They are necessary upper bounds because omitted cells can add common
neighbors. They are not the full target equalities. The first two impose
unary allowed entries of P. Writing M=C^T D, a selected entry P[y,z]=1 must
have M[y,z], M[FY(y),z], M[y,FZ(z)] <= 1. The only remaining possible excess
occurs when a matching pair y,FY(y) maps to z,FZ(z); then require
M[y,FZ(z)]=M[FY(y),z]=0. Enumerating matching pairs with unused column labels
therefore covers the perfect matchings without any automorphism assumption.

The saved domain producer reports 30,344 permutations for each of the four
separate pair tests. Those exhaustive count claims remain CANDIDATE unless
independently reproduced. The raw lists are saved so that a checker need not
import the producer. Mere survival of all four separate tests does not imply
that a joint choice will survive.

## Joint relaxed witness, then exact obstruction

A predeclared deterministic sampler (Python Random seed 20260930, at most
100,000 draws and 120 seconds) selected one permutation from each domain.
Its 1,390th attempt passed all 1,225 unordered pair bounds among the 50
external vertices. The previous 1,389 attempts failed these bounds. These
are draw counts, not counts of distinct configurations. Including the rook
core, each pair within one cell has one additional known common neighbor;
other external pairs have none from the core.

Raw joint artifact:

- `results/20260930_rook_joint/joint_witness.json`
- SHA-256: `ada6539e1860952381337468e234602eeaf0c83af5ed0d7f5546538fde7cc817`

The next exact test tried each of the 200 potential new edges in the two
remaining degree-two blocks separately. It rejected 167 because that single
edge makes some pair exceed `common <= 2 - adjacency`. Only 33 edges remained.
Eight rows have fewer than their required two remaining neighbors. In
particular external vertex 12 has **no** possible neighbor among 40 through
49, although its cell pair requires exactly two. Hence this exact frozen
joint artifact has no completion in the target's rook representation.

This is a short monotonicity certificate: adding more edges cannot decrease
any already counted common-neighbor total, and can only maintain or decrease
the upper bound for a pair. Therefore no edge already rejected on the base
artifact can become allowed later. The ten rejected edges from vertex 12
alone suffice, after directly checking their violating pairs. The saved
certificate also records every other rejection and every deficient row.

- `results/20260930_rook_complete_window/single_edge_filter.json`
- SHA-256: `52827227f8188f86f82e0d3681f435e43d592930282e3d1a662e4e8abd97b556`

The bounded DFS was not entered (`dfs_nodes=0`); the row-degree obstruction
resolved the fixed artifact immediately. This leaves the preceding weaker
relaxation witness valid within its stated scope. It refutes its extendability,
not its previously checked upper-bound property. It does not exclude all
choices of the four perfect matchings, all central stars, or all induced
rook configurations. Overall target-wide coverage remains UNKNOWN.

The raw artifact and exact claim were sent to the separate state/literature
auditor for a direct 59-vertex adjacency-matrix reconstruction with positive
and corrupted controls. Until that review succeeds, the exclusion remains
CANDIDATE. The important reusable result is the cheap single-edge/row-capacity
test, which should precede expensive completion of future local witnesses.

## Reproduction

Use the pinned repository environment, with fresh output directories. These
are the executed commands; completed artifacts are never overwritten.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_rook_cell_factors.py --out acceleration/results/20260930_rook_cell_factors
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_rook_offdiagonal.py --input acceleration/results/20260930_rook_cell_factors/local_witness.json --out acceleration/results/20260930_rook_offdiagonal
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_rook_joint.py --star acceleration/results/20260930_rook_cell_factors/local_witness.json --pairs acceleration/results/20260930_rook_offdiagonal --out acceleration/results/20260930_rook_joint
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_rook_complete_window.py --input acceleration/results/20260930_rook_joint/joint_witness.json --out acceleration/results/20260930_rook_complete_window
```

Per-stage manifests preserve the actual source commit at execution; the branch
advanced during concurrent work. The exact producer source hashes identify
the code used even where those new files were not yet committed. Python was
3.12.10; all acceptance arithmetic used unbounded Python integers. No GPU,
floating-point tolerance or solver feasibility status is part of these claims.

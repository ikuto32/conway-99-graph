# Conditional rook-cell two-factor test

Status: CANDIDATE; discovery derivation and producer output require independent
review. This concerns a target **containing an induced rook-nine graph**. It
does not assume an automorphism, prove universal rook containment, construct a
target, or exclude the rook-containing family.

Dependency: `C-ROOK-NINE-REGULAR-SET-ENCODING` revision 1 in the root ledger,
independently checked by the fresh 2026-09-17 recheck. Its cell notation and
matrix equations are used here.

For a fixed ten-vertex external cell X_i, let F_i be its internal perfect
matching. Four other cells are rook-adjacent to i and their adjacency blocks
are permutation matrices; four are rook-nonadjacent, with binary row/column
degree-two matrices C_ij. The (i,i) block of the existing exact lower equation
`H^2 = 12I - H + 2J - T^T T` is

```
I + 4I + sum_j C_ij C_ij^T = 12I - F_i + J,
sum_j C_ij C_ij^T = 7I + J - F_i.
```

Each C_ij C_ij^T has diagonal 2. At distinct vertices its entries are
nonnegative integers. The right side has entry zero on matching pairs and
one on other pairs. Consequently each `C_ij C_ij^T - 2I` is a binary adjacency
matrix with zero diagonal, degree two, and disjoint from F_i. These four
simple spanning two-factors are edge-disjoint and partition `K10 - F_i`.
Equivalently, the bipartite graph of any C_ij has no four-cycle. A bipartite
cycle of length 2m induces an m-cycle in the left two-factor. Its half-cycle
partition must therefore be one of `10`, `3+7`, `4+6`, `5+5`, or `3+3+4`.

This necessary condition is cheap enough to test before constructing a full
rook-block SAT instance. The producer exhaustively enumerates all labelled
two-factors avoiding F_i={(0,1),(2,3),(4,5),(6,7),(8,9)}. It chooses each cycle
at the least unused vertex and one of the two directions, which gives each
labelled graph exactly once. Fixing this matching loses no local cases:
every perfect matching can be brought to these labels by a bijection, not
by a graph automorphism.

The producer also constructs four edge-disjoint factors and their 10-by-10
vertex-edge incidence matrices. For each right cell it gives a perfect
matching avoiding pairs with a common left neighbor. Thus the local witness
also obeys the basic no-triangle condition involving that right matching.
The output does **not** impose relations between different right cells,
off-diagonal blocks of H^2, the full diagonal equations for those cells,
or the target eigenvalue multiplicities. It is a witness that this single-cell
test alone is consistent, not evidence that the full target is feasible.

All arithmetic and acceptance tests are integer-exact. The protocol and
limits are frozen in `manifest.json` before enumeration. The finite domain is
at most 286884 unrestricted labelled two-factors: 181440 of cycle type 10,
43200 of type 3+7, 37800 of type 4+6, 18144 of type 5+5, and 6300 of type
3+3+4. These unrestricted numbers follow by selecting component vertex sets
and counting `(m-1)!/2` undirected labelled cycles per component; repeated
component lengths require the corresponding factorial divisor.

Run from the repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_rook_cell_factors.py --out acceleration/results/20260930_rook_cell_factors
```

Independent review should derive the block identity separately, check the
saved raw factor masks without importing this producer, verify the witness
and corrupted variants, and reproduce the census by an independently chosen
combinatorial method. A repeated execution is not that independent review.

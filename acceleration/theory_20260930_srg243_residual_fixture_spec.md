# Nonempty positive-control fixture from a ternary syndrome graph

This bounded producer constructs a graph with parameters(243,22,1,2) for
validation controls only. It is not a Conway-99 candidate, target exclusion,
novelty claim or independently approved result.

Enumerate every monic degree5 polynomial over GF(3), retaining divisors of
`x^11-1`. For each divisor compute the eleven syndromes `x^i mod g`, then
all243 syndromes of ternary errors of Hamming weight at most2: one zero,
22 signed single-coordinate errors and220 signed two-coordinate errors.
Retain a divisor only if every syndrome is distinct. Choose the first such
divisor in ascending coefficient-tuple order, preserving all divisor results.
On the243 vectors of GF(3)^5 connect differences in the22 signed coordinate
syndromes. Check the entire adjacency matrix with exact integers against
`A^2 = 20I-A+2J`, symmetry, binary entries, zero diagonal and degree22.

Choose the lexicographically first edge and its unique common neighbour.
Extract its root triangle, three disjoint20-vertex neighbour cells and180
remaining vertices. Relabel the first cell's perfect matching to standard,
the two cross matchings from it to identity, and the remaining vertices by
their unique pair of first-cell neighbours. Preserve all original-vertex
maps, raw63 core,60-by-180 F and180-by-180 D. Verify the exact nonempty block
equations `F D = 2J-F-CF` and `D^2+F^T F = 20I-D+2J`, with D row sum16,
F row sum18 and two entries per cell per column. These are parameter243
controls, not substitutions into the99-vertex residual theorem.

Before construction calibrate the integer SRG check on the known3-by-3 rook
graph and corrupted versions. All arithmetic is integral. The deterministic
run has a120-second wall limit, no solver, no random seed and no new Python
dependencies. Save raw artifacts, commands, tool/source hashes and limits.
An independent reviewer must check the raw graph and blocks before promotion.

Locked command from the repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260930_srg243_residual_fixture.py --out acceleration/results/20260930_srg243_residual_fixture
```

# CUDA initial pair support scores

Build `build_star_pair_gpu.ps1`. Run
`acceleration/build/star_pair_gpu.exe INPUT.bin OUTPUT.json [--flags]`.
The output must not already exist. Existing cut-evaluator sources are untouched.

The binary format has no padding and all integers are unsigned little endian:

1. Eight ASCII bytes `C99PAIR1`.
2. One u32 candidate count.
3. For each candidate: 84 u32 domain counts, then each vertex's domains in input
   order, each stored as two u64 words `(low, high)`.

Each domain row is the **full completed 99-vertex neighborhood**, including the
six fixed neighbors and eight chosen disjoint outer neighbors. Global vertices
are root 0, its neighbors 1..14, outer vertices 15..98. The low word covers bits
0..63 and the high word covers bits 64..98; high bits 35..63 are zero. Empty
vertex domains are permitted. Batch limits are 10,000 candidates and two million
total domain rows. All candidate offsets are processed in one kernel launch.

For a domain at u and another outer vertex v, support means some ORIGINAL domain
at v has symmetric u-v adjacency and intersection size exactly `2-adjacency`.
All 83 other outer vertices are tested, including fixed overlap edges, overlap
nonedges, and same-fibre nonedges. No propagation or deletion is performed.

JSON has `results` in input candidate order. Each result contains:

- `candidate_index`, `total_domains`, `domain_counts` (84 counts).
- `initial_pair_supported_domain_counts` (84 counts), also available under
  `per_vertex_initial_supported_domains`: choices supported on **all** 83 initial
  relations, independently against the original neighboring domains.
- `vertices_with_initial_pair_supported_domain`,
  `total_initial_pair_supported_domains`, and `total_unsupported_relations`.
- `unsupported_domain_counts_by_pair`: 84 by 84 counts; diagonal is zero.
- With `--flags`, `support_rows_bits`: one 84-character binary string per input
  domain, in vertex/domain order. The self bit is an ignored `1` sentinel.

Top-level `elapsed_seconds` covers transfers and kernel (excluding input parsing,
CUDA initialization, host aggregation, and JSON writing). `kernel_seconds` is
separate. Outputs are heuristic scores, not a proof or an arc-consistency result.
Callers bind the binary, original graph/domain inputs, executable, source and
output with hashes. `review_star_pair_gpu.py` supplies such a complete QA record.

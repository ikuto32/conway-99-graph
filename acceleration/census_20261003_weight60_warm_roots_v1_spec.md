# Complete two-graph warm-scaffold root census v1

Producer only, authored by the annealer producer. This source does not approve
its census and launches no solver or SAT instance. Frozen universe is exactly
the independently checked final-best and first retained lambda0 raw matrices,
each with 99 labelled roots, for 198 root records. Raw pins are respectively
`818314b75fccfa0f3fe702602afb02b6415f3138a770ef15ed0621d189d88836`
and `c95eff815f69c6d7c4122c5c0cde96d8c5124ffec892f3d8a4913ad0b1486f21`.
The independent saved-object report
`acceleration/results/20261003_independent_review/weight60_pilot01/summary.json`
is pinned at `a80ec86298ce13ae8fea44c118ebbe613dd4b55e4387ac49e39ec9b3d4cd40d2`
and must bind both exact raw inputs. No first-observation timing claim is added.

Before execution freeze this source/spec. Supported Linux invocation uses
`run_compute_command.py` with 120 seconds outer and 100 seconds worker,
20-second worker reserve, the existing native_budget_env_v1 pinned uv environment
with `uv run --locked --offline`. Tiny domain/common-neighbor controls and exact
matrix checks precede the full census in that invocation. Exact 99-root arithmetic
is a cheap finite calculation comparable to prior small root censuses, with no
unbounded search. Every computational phase shares that invocation's deadline.

Parser checks exact size, binary entries, zero diagonal, symmetry and degree14;
generic rook9 uses size9/degree4. Every one of 156,849 unordered vertex triples
per target-sized graph is visited, recording all actual triangles. Adjacency
bitsets compute exact integer intersections; each root records its 14 neighbors,
all induced matching edges and degrees, and every one of its 84 outsiders with
the exact common-neighbor vertices/count and CN2 eligibility. Record the complete
histogram including zero bins, eligible vertex list/count, and residual
`sum_outside (CN(root,v)-2)^2`. The row residuals sum to twice the global unordered
mu energy. No floating arithmetic or approximate acceptance threshold applies.

Selection predeclared: minimize the exact residual over all99 roots separately
for each graph, retain every tie, and select the smallest root label in that tie.
Global selection uses lexicographic(residual, graph_label, root_label); all roots
remain in full JSON census and resumable/preserved JSONL records. No favorable
case is omitted. CN2 eligibility alone is not a complete scaffold equivalence or
assignment certificate, and even a root with 84 eligible outsiders would require
additional checks before scaffold interpretation.

Before full production run known rook9 positive controls for all9 roots and its
literal root0 matching/outside counts. Deliberately corrupted diagonal, binary,
symmetry, degree, target99-scope, common-neighbor count and score controls must
reject at exact declared diagnostic stages; include actual99 diagonal/degree/
score mutations and a wrong-diagnostic control of the control harness. These are
producer-internal finite controls, not independent approval. Preserve every raw
fixture/report, failed output and source version. A separate root-authored dense
integer A-squared/root path must check all198 records, matrix domains, triangle
and minimum/tie calculations against exact raw bytes. No annealer/census imports
should provide the sole checking path. Success here means full raw census output
with exact input/output/source/version/command hashes; result stays CANDIDATE
until that independent check. No target resolution, target exclusion, graph
normalization certificate, coverage denominator, Git index or claim-ledger edit.

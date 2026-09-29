# Independent row-domain audit for the capacity-compatible Q1

The exact scope is one fixed 39-vertex triangle core, its canonical 12-by-60
incidence block C0, and the new 12-by-60 block C1 decoded from the native
capacity-projection SAT assignment. The independently checked SAT object has
SHA-256 `94904b766b487e579f656e685643449c23a6aabf07825cac17e9fd8e241427c5`.
That positive projection result is distinct from its extension question.
The present audit assumes no target automorphism, no universal occurrence of
the fixed core, and no earlier Q1's propagated zeros or exclusion.

The checker reconstructs all 9,801 entries of the partial graph from typed
vertices, literal core edges and raw 24-row incidence. All 720 C2-to-B entries
and all 1,770 unordered B-to-B entries initially remain unknown. It checks
the raw 24-row Gram by independently taking the core block of the target
identity, all row/column margins, every known pair cap and every degree
interval. It binds the exact prior independent SAT-object gate and raw input.

For any chosen C2 vertex u, every target extension supplies 60 binary choices
x_b for its B neighbours. Its four known neighbours force sum(x_b)=10. For
each completely known A0/A1 vertex v, the exact common-neighbour equation is

`sum_{b in B with v~b} x_b = 2 - A[u,v] - |N_known(u) intersect N_known(v)|`.

There are 24 such equations. For every pair b,c whose known common neighbours
excluding u already reach the cap 2-A[b,c], choosing both creates an excess;
hence x_b+x_c<=1. An unknown b--c edge uses cap 2, a valid necessary bound for
either eventual edge value. These are only necessary constraints, which is
sufficient for an exclusion if their complete finite binary domain is empty.

The independent checker imports no producer. It explicitly shares the frozen
independent constraint and tree verifier from
`audit_20260930_triangle_row29_obstruction.py`, SHA-256
`109671d882976ab68b350883340f3f0d7437571caa56b01d56a875f7897c4730`.
Its exact graph/truth-table controls are rerun. The new scope assembly and
literal raw-row checking do not use the producer's graph builder or search.

Every UNSAT tree must visit every supplied node exactly once, assign each
split variable both values, and end every leaf in an independently calculated
integer interval contradiction. Each forced bit is justified by setting its
opposite and checking the cited constraint becomes impossible. Changed
branches, forced values, leaf counters, raw entries and constraints are
deliberately rejected. For a SAT outcome the full literal assignment would
instead be checked against all reconstructed constraints and raw pair caps;
an early-stop search tree would not be described as exhaustive. UNKNOWN
would remain unresolved. The raw artifacts determine which cases apply.

All twelve C2 vertices form the declared row population. A complete empty
domain for even one row excludes the single recorded Q1 from a target graph
with this fixed core. Twelve empty rows are twelve explanations of that same
fixed-factor exclusion, not twelve disjoint excluded graph families. This is
not an exclusion of every capacity-compatible Q1. Individual SAT rows, if any,
would not establish a simultaneous C2, a full 36-row factor or a target graph.

Replay with a fresh output directory and the unchanged locked environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_triangle_capacity_q1_rows.py --run acceleration/results/20260930_capacity_q1_rows --summary-sha256 3e665beda8c3521b3fad27d1c31e52afe5be820476d5ba92950f58698d3593c3 --out build/capacity-q1-row-recheck
```

The checker allows 120 seconds; all arithmetic and comparisons are exact.
Its output includes source/input hashes, full tree-check receipts and control
results. No solver is launched. This written argument supplies the necessary
constraint justification; sampled tests do not replace it.

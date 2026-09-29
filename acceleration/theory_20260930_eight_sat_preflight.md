# Direct full99 SAT preflight for the eight-coordinate family

This is a producer engineering preflight, pending independent review. No research
CNF was written and no solver was invoked. Raw row counts, a prospective legacy
unit mapping and hashes are in `results/20260930_eight_sat_preflight/`.

## Existing path and completed work

`fixed_overlap_cnf.py` appends a complete168-edge K assignment to the frozen
`scratch_general_exact.cnf`. The legacy outer vertices are ordered by sorted
inner-symbol pairs, whereas current artifacts group supports first; 60 of84
positions move. Its companion audit checks the exact mapping, all3,486 outer
edge IDs and byte-identical base body. It explicitly leaves correctness of the
base CNF semantics conditional on the frozen model. The historical runner and
decoder require1806units,168presentedges and1680freeedges throughout and must
not be reused unchanged for the new scope.

The September16 continuation document records independently checked DRAT
contradictions for fixed candidates226and2700 and nine nearby fixed assignments.
Those results retain168specific K edges and do not exclude the120-fixed-K
eight-coordinate family. The saved general five-branch portfolio has four
UNKNOWN branches and one raw unproved UNSAT branch. Neither its branch units
nor an unrestricted exclusion is used in this proposed family experiment.

## Exact new scope and measured sizes

The pinned eight-coordinate manifest specifies120fixed outer K edges and
2160unknown outer edges:480released same-sign-coordinate edges and1680
disjoint-support edges. All other1206outer pairs are absent. The189 root-scaffold
edges are fixed. No target automorphism is assumed. This is a conditional
family of full99-vertex graphs, not a universal covering family.

The cheapest prospective adapter copies the old unrestricted CNF body and
appends1326units:120positive and1206negative. Its exact predicted size is
817278variables,1623828clauses and30190812bytes. The raw prospective CNF hash
is recorded without writing that CNF. No legacy branch/symmetry units are added.

A fresh constant-folded encoder can instead use2160edge variables. Counting
the actual pinned scope gives110640two-variable product terms,1176BP quota
equalities and3486outer-pair caps. Using disjoint sequential-counter auxiliary
IDs per row, a product helper for each two-variable product, and three clauses
for each exact AND gives321785totalvariables and866098clauses. These are counts
for a specified prospective encoding; the encoding has not been built or
verified. Reusing the old one-way product implication would reduce the clause
count to644818, but full equivalences simplify independent model checking.
No constant row contradiction was found by this census.

## Mathematical route requiring independent review

Write outer vertices as unordered two-subsets of inner symbols from distinct
root matching pairs. For each outer u and inner symbol s, impose

`sum(B[u,v] for v whose label contains s) = 1`

when s or its matching partner belongs to u's label; impose2otherwise. These
1176 equations settle inner/outer common-neighbor counts. Each outer edge is
counted twice when summing over symbols, and the right sides sum24, so each
outer degree is12 and each full graph degree14.

For each outer pair u,v require

`sum_w B[u,w]*B[v,w] + B[u,v] <= 2 - |label(u) intersect label(v)|`.

All3486left sides sum `84*C(12,2)+504 = 6048`: regularity fixes the sum of
common-outer-neighbor counts, and there are504outer edges. The right sides also
sum6048: each of14symbols lies in12outer labels, yielding
`2*C(84,2)-14*C(12,2)=6048`. Therefore every cap is tight. With the fixed scaffold,
all full99common-neighbor equations follow. This derivation uses exact integers;
it needs independent review tied to the actual clauses and scope before an
UNSAT exclusion could be promoted.

A SAT model must decode all2160free edges plus fixed scaffold/K values into an
explicit99-by99 binary symmetric zero-diagonal matrix. A separate full-graph
checker must verify `A^2=12I-A+2J` exactly, then separately check the declared
family scope. A rawSAT answer is not a target graph certificate. An UNSAT answer
requires the complete exact CNF, proof trace, checker provenance and independent
replay, and would exclude only this conditional120-fixed-K family.

## Replay of this preflight

```powershell
$env:UV_PROJECT_ENVIRONMENT=(Join-Path (Get-Location) 'build/rook-sat-venv')
uv run --project acceleration/environments/rook-sat --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_eight_sat_preflight.py --out acceleration/results/20260930_eight_sat_preflight_replay
```

The next concrete experiment is a new compact encoder with complete raw edge
and cardinality maps, then independent clause/semantic reconstruction and
known-valid/corrupted calibration before a bounded proof-producing solve.

# Independent audit of the local triangle-matching filter

Claim binding: `C-STAR-TRIANGLE-FILTER-18481`, revision 1. Reviewer:
`independent_verifier` agent, independent from the filter's discovery agent.
Source base: `7518ebcec78589fe7f8b068ee7a1dd87e8bf8d42`; exact checking source
and raw inputs are hash-bound in `triangle_matching/summary.json`.

## Necessary condition, independently derived

In an srg(99,14,1,2), choose any vertex x. Its neighborhood has 14 vertices.
For every y adjacent to x, the neighbors of y lying in N(x) are precisely the
common neighbors of x and y. Since lambda=1, there is exactly one such vertex.
Thus the graph induced on N(x) is 1-regular on 14 vertices: it is seven disjoint
edges. No automorphism assumption enters this argument.

Now fix the baseline18481 partial assignment and a complete local star at x.
All 14 neighbors of x are fixed. The already present edges inside this
neighborhood must remain in any extension. They must form a matching; the
complete local-star cap checks independently confirm this in every input.
Every already matched endpoint has its sole permitted neighborhood neighbor
and cannot receive another edge inside N(x).

Consequently the remaining unmatched neighborhood vertices must be perfectly
matched to one another. A prospective matching edge must belong to the allowed
unknown-edge universe (the 1,680 disjoint-support outer pairs), because the
omitted overlap and same-fiber edges are fixed absent. In addition, inserting
that edge by itself into the fixed completed star must preserve every partial
common-neighbor cap. Any edge in a genuine completion passes this individual
test: further insertions cannot decrease common-neighbor counts, and can only
lower a nonadjacent pair's allowed cap when that pair becomes adjacent. An
already invalid partial insertion cannot become valid later.

It follows that a perfect matching must exist in the graph of individually
permissible edges on the unmatched vertices. If this graph has no perfect
matching, the local star cannot occur in any completion of this fixed
assignment. If it does have a perfect matching, simultaneous insertion of its
edges may still violate caps, and global extension may still be impossible.
The test is necessary only. These removed local star choices are not new
fixed-assignment exclusions; this baseline assignment was already excluded.

## Independent reconstruction and exhaustive checking

The new auditor imports no producer helper or other project module. It builds
the complete 99-vertex known adjacency from the root-label convention and raw
overlap edges. Every original star is added directly, then all 4,851 unordered
partial vertex-pair caps and all 14 exact root-neighbor quotas are checked.
Forced internal matching edges and unmatched vertices are independently
reconstructed and compared to each raw record.

For each potentially allowed internal edge ab, the auditor mutates both full
adjacency rows. It recomputes the cap for every pair containing a or b, rather
than using the producer's old-neighbor shortcut. These are exactly the rows
that changed; every pair containing neither endpoint has unchanged adjacency
rows and hence unchanged common-neighbor count. All remaining caps already
passed the full completed-star check.

The producer counts matchings using a memoized recurrence on the least
unmatched vertex. The auditor instead enumerates every subset of allowed
edges having half as many edges as unmatched vertices, tests disjointness,
and checks full endpoint coverage. Each perfect matching is exactly one such
edge subset. Thus the counts, including every zero count, are exhaustively
checked using a separate algorithm. Every recorded positive witness is also
checked directly for allowed edges and exact endpoint coverage.

The checking record preserves per-vertex counts and input/source hashes.
The raw result is pinned to summary SHA256
`c827ac9b54efcbcab0927ed3c105fe2fae73b1d87225adc71221300b2ee27bba`.
The frozen universe is the 84 original baseline18481 star domains, with
original domain IDs retained; no post-outcome selection is made.

## Controls and trusted dependencies

Calibrated matching fixtures are K4 (3 matchings), K6 (15), seven prescribed
pairs (1), a prescribed pair deleted (0), and the empty matching (1).
A windmill fixture accepts its first internal edge and rejects an extra edge
incident to an already matched neighbor; the corrupted full graph also fails
the cap validator. Corrupted raw records bypass hashes and test an altered
matching count, omitted allowed edge, invalid witness, and changed domain ID.
Each must be rejected for the audit to finish successfully.

The prior independent complete-domain replay establishes that the original
star universe is complete for this fixed assignment. Its exact candidate and
domain hashes are checked again. This is a disclosed dependency on existing
independent enumeration code, whose soundness was reviewed in
`MATHEMATICAL_AUDIT.md`; it is not a second fresh enumeration in this audit.
The new checker otherwise trusts Python's standard integer/bitset operations.
`tqdm` displays progress only and has no role in acceptance.

## Claim boundary and reproduction

The claimed numerical partition is exactly 6,756 rejected and 19,494 surviving
local choices among 26,250 original choices, with no empty outer-vertex domain.
This is a conditional local filter result for the named fixed assignment.
There is no additional fixed-K exclusion, global coverage claim, graph
construction, or target-level nonexistence proof.

Use the locked project environment from the repository root:

    uv run --locked python acceleration/audit_20260917_triangle_matching.py --input acceleration/results/20260917_theory/matching_baseline18481 --out <fresh-output-directory> --seconds 600

Actual interpreter command, Python version, hashes, exhaustive subset counts,
controls, and elapsed time are preserved in the completed JSON report. The
auditor writes per-vertex checkpoints and can resume the same output directory
only when the checking source and raw vertex hashes match. A resource cap
returns an explicitly incomplete status and creates no final claim report.

Overall search coverage: UNKNOWN; no validated denominator.

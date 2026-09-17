# All matchings of one prescribed freed coordinate

Freeze the existing root_group0 same_0 twelve outer vertices and their60
legal edges (K2,2,2,2,2,2), all162 other prescribed K edges, root scaffold,
and prescribed absences. Enumerate every perfect matching by repeatedly
pairing the smallest unmatched vertex with each allowed unmatched partner in
ascending order. Every matching has exactly one recursive path because its
partner at each smallest unmatched vertex is unique. No automorphism or
isomorphism assumption is used. Assign consecutive IDs by this traversal.

The anticipated6040 count is not assumed, asserted, or used as a stopping
condition. Independent review will derive the count by inclusion-exclusion,
validate all listed matchings and uniqueness, and reconstruct each99x99
partial adjacency matrix with a separate exact integer multiplication path.

For each matching, add its six edges to the fixed partial graph. Check zero
diagonal, symmetry, degree at most14 and common neighbors at most2−edge
for every unordered pair. Save accepted and rejected IDs and the first
violating pair in lexicographic order, including actual count and allowed
cap. Passing is only local consistency of a partial graph. Rejection is a
necessary cap obstruction to its completion. It is not nonexistence of the
unrestricted target. The complete finite matching universe can support a
conditional family denominator after independent verification.

Preregistered bound:30seconds for enumeration and cap evaluation together.
At a cap, preserve all enumerated matchings and every completed evaluation,
explicit incomplete/pending fields, and do not claim full coverage. Save all
inputs/source/outputs hashes, exact command, source commit and tool version.
Use producer controls: valid rook SRG9, corrupted diagonal/asymmetry and an
added edge violating common-neighbor caps. These controls are not independent
verification. Exact bit operations only; no numerical acceptance threshold.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/enumerate_20260917_partial_coordinate_matchings.py --out acceleration/results/20260917_partial_coordinate_matchings
```

Overall search coverage: UNKNOWN; no validated denominator for Conway-99.

# Necessary matching filter for four freed coordinates

Prerequisite: independent complete-domain PASS for every one of the290,460
original localstar masks across84 centers, with144 fixedK edges,240 freed
same-sign edges at rootgroups0 and1, and1,680 disjoint-support unknowns.
All other prescribed absences remain fixed. Require the exact independent
report hash and all84 original domain hashes; producer completeness alone
does not authorize this run. This is a conditional configuration scope.

For a star at centeru, add its8,9 or10 indicated edges to the fixed99-vertex
scaffold, obtaining the full14-neighbor setN(u). Every target completion has
N(u)=7K2 because each adjacent pair has exactly one common neighbor. Existing
edges induced insideN(u) are forced; audited local caps ensure they form a
matching. Their incident vertices need no additional matching edge. On the
remaining vertices, retain only originally unknown edges whose individual
addition preserves every partial common-neighbor cap. A true completion's
remaining matching must lie in this permissive graph. Exact matching count
zero therefore rejects the localstar. A surviving matching need not pass
joint edge-addition caps or extend globally; there is no converse.

Reuse disclosed producer helpers from theory_20260917_triangle_matching.py:
full99 single-edge cap test and exact minimum-unmatched subset recurrence.
This is a separately named scope adapter and no frozen source is modified.
Independent verification must reconstruct every permissive graph and use a
different matching-checking path: explicit witnesses for positive existence,
independent exhaustive edge-processing DP for zero cases. Positive
multiplicities are producer counts unless separately recounted.

Frozen selection: centers0..83, originalIDs ascending within each original
sorted table; evaluate all choices with no outcome-driven skip.180seconds per
invocation, noLP/GPU, exact integer zero threshold. Timer includes checking
and writing completed center outputs, after input gating and controls. Save
every forced edge, unmatched vertex, allowed edge, matching count and witness,
plus explicit rejected/surviving originalIDs. At a cap save completed centers
and all completed records in the current partial center with exact hashes.
A fresh outputfolder plus --resume-checkpoint continues that exact state,
without overwriting any previous artifact or claiming partial coverage as full.

Controls: prescribed7-edge matching positive, deleted edge negative, K10
count945, valid windmill partialgraph, corrupted extra edge and rejected
single-edge cap. Full14-neighborhood size is checked for all real choices.
Controls are producer checks only, not independent verification.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_four_coordinate_matching_filter.py --out acceleration/results/20260917_four_coordinate_matching_filter/run01 --domain-audit AUDIT_PATH --domain-audit-sha256 EXACT_AUDIT_HASH
```

No automorphism assumption or ledger edits. Overall search coverage:
UNKNOWN; no validated denominator for Conway-99.

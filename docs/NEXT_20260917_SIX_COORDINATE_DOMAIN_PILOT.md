# Six-coordinate complete-domain tractability pilot

Free both same-sign coordinates at rootgroups0,1,2, extending the frozen
four-coordinate family. Construction from baseline18481 leaves132 fixedK
edges (all7cross matchings and8other same-sign matchings), removes36 baseline
edges and permits360 matching-coordinate edges plus1,680 disjoint-support
edges, total2,040 unknown edges. Every other prescribed absence is retained.
Twelve centers need10 additions,48 need9 and24 need8. No automorphism assumed.

Hash-gate the independent complete four-coordinate auditfb21f69b... and every
oldmanifest/domain. For each of all290,460 oldchoices, add the removed old
fixedneighbors to its mask and verify identical fullcenter neighborhood,
correct degree and allowededge membership. The resulting partialgraph plus
newstar is a subgraph of the oldpartialgraph plus oldstar with the centerrow
unchanged. Therefore all common-neighbor uppercaps remain valid (edge deletion
also weakens its paircap), and unchanged rootrows preserve exact rootquotas.
This gives an embedding into the new admissible universe even if new complete
enumeration later caps. Complete newdomains additionally locate every oldmask
by exact original-to-newID mapping. Save all embeddings, not a sample.

Frozen center order:0,4,24 (three double-freed support types),8 (single-freed),
60 (unaffected), then every remaining center ascending. At every center use
the disclosed exact rootquota/resource-cap/conflict recursion from the prior
producer, adapted in a new file to retain discovered masks and captriggers.
No originalsource is modified. New IDs are sorted integer masks and do not
reuse old IDs without an explicit map.

One invocation only:180seconds for full enumeration,20million searchnodes,
100,000 storedchoices percenter and1million storedchoices total. The timer
includes enumeration and saved completed-domain checkpoints; excludes input
hashing, oldembedding records and five tiny restricteduniverse controls.
The controls have a separate30second/1millionnode safetycap. A complete
domain is sealed only after exhaustive recursion. On anycap preserve prior
complete domains, discoveredpartialmasks and any triggering extra leaf.
Do not label a partialtable complete. No retries, LP build or solver.

Calibration: five prescribed centers use the first embeddedoldstar plus two
lowest additional allowedneighbors, comparing full restricted enumeration to
direct99-vertex brute subsets. Delete an edge to test degree failure. A
zero-domain-cap control must retain the triggering leaf and never report
completion. These are producer controls, not independent verification.
Only if all84 complete may the artifact be referred for a separate exhaustive
domain audit. A cap is an engineering tractability result, not an exclusion.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_partial_six_matchings.py --out acceleration/results/20260917_partial_six_matchings
```

No ledger changes. Overall search coverage: UNKNOWN; no validated denominator.

# Independent eight-coordinate matching-filter audit protocol

Auditor: Codex subagent `/root/state_literature_audit`. This protocol is saved
before the full filter audit. Producer source and recurrence are not imported.

Population: all 2,290,122 original local star choices at all 84 centers,
bound by `eight_domains_claim_binding.json`, SHA-256
`170871c99ed16a160bf1403e4f6443275ca00c3a6ce68775fb56ba5f02783302`.
The audited family retains 120 fixed K edges and all prescribed absences;
480 freed same-sign edges at root groups 0–3 and 1,680 disjoint-support
edges are unknown. No automorphism or unrestricted coverage assumption.

For every raw producer record, reconstruct the full 99-vertex star and all
forced matching edges. Independently mutate each prospective free edge and
check every affected common-neighbor upper cap using the prior independent
`audit_20260917_triangle_matching.permitted` implementation. Compare the
entire allowed-edge graph. Check every positive perfect-matching witness;
for every negative record use an edge-processing reachable-subset DP,
distinct from the producer's first-vertex matching recurrence. Acceptance
requires exact equality of the complete rejected/surviving original-ID
partition and saved summary counts.

Only matching existence is checked. Positive matching multiplicities are
not recounted, and individually permitted edges need not coexist jointly.
No exclusion follows unless a complete domain becomes empty and the full
soundness/dependency gates are separately checked. No LP is run here.

Controls: all prior independent mutation and exhaustive matching controls,
five direct edge-DP fixtures including two disjoint odd cycles, and positive
plus corrupted-CRC compressed-byte fixtures. All arithmetic is integral;
no tolerance, random seed or numerical library is used.

The new checker adapts the previous six-coordinate independent checker.
This shared checking implementation is disclosed; it is not a new
independent third verifier. The domain gate is an earlier independent
enumeration, explicitly reused rather than silently rerun.

Resource limit: 1,800 seconds per invocation, enforced between complete
centers; a single center may overrun the cap to preserve an exact checkpoint.
Output centers are created exclusively and may be reused only after source
and raw-input hash equality checks. Interrupted centers are retried entirely.
Compressed output is recovered with exact size/hash/CRC checks into the
unique audit output directory. Raw large producer output is not used when
a compressed companion is supplied.

Do not start the audit until the complete producer summary exists and all
84 center output hashes are bound. Invocation from repository root:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/audit_20260930_eight_coordinate_matching_filter.py
```

The checker writes detailed provenance and input hashes to
`acceleration/results/20260930_independent_review/eight_coordinate_matching_filter/summary.json`.
An incomplete audit is not a PASS and cannot promote a claim.

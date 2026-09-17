# Six-coordinate necessary neighborhood-matching filter

Require independent complete-domain PASS and an exact supplied audit hash for
all879,449 originalchoices across84 centers in the six-coordinate family.
Scope:132 fixedK edges,360 freed same-sign edges atrootgroups0,1,2 plus1,680
disjoint-support edges; all other prescribed absences retained. Twelvecenters
add10neighbors,48 add9,24 add8. No pair-consistency filter or LP is used.

For every star, construct its full14-neighborhood in the fixed99-vertex
scaffold. Targetlambda1 requires its induced graph to be7K2. Remove vertices
of already forced matching edges. Among remaining vertices retain only
originally unknown edges whose individual addition preserves all partial
common-neighbor uppercaps. A target completion's perfect matching must use
these edges. Exact matching count zero therefore rejects this localchoice;
positive existence does not establish jointcaps or global extendibility.

The separately named producer adapts the audited four-coordinate wrapper,
reusing the disclosed historical subset-matching and single-edge-cap helpers.
Its output remains CANDIDATE until a distinct independent checker reconstructs
every permissive graph, checks positive witnesses and exhaustively excludes
negative graphs with a different matching method. Positive multiplicities
are not promoted merely because a witness exists.

Preregister all originalIDs: center0..83 ascending, each sorted originaltable
ascending.300seconds perinvocation includes matching and raw/companion
serialization; excludes inputgating and producercontrols. Save every raw
forcededge/unmatchedvertex/allowedgraph/count/witness record with its exact
originalID andmask. No sampling, outcome-driven skipping or IDrenumbering.
At cap preserve all completecenters and the completed records of the current
partialcenter. Save their hashes and a checkpoint. A fresh outputfolder plus
--resume-checkpoint uses the bound partialstate; no oldevidence is overwritten.
Incomplete status is not a complete partition or exclusion.

Raw percenter JSON remains lossless and locally retained. Every raw witness
file exceeding10MiB also receives a gzip companion: fixedmtime0, emptyheader
filename, level9, streaming exactbytes. The schema1 compressed_artifacts.json
records raw/compressed paths, sizes andSHA256. The generic independent gzip
replay tool can recover these files for public review. A companion hash is
not mathematical verification, and raw evidence is never deleted.

Producercontrols: prescribed7edge matching positive, deletededge negative,
K10count945, windmill partialcaps, corruptedextraedge, plus positive gzip
recovery and corruptedCRC rejection. Full14-neighborhood degree is checked
on every actual input. Run only after the independent six-domain gate.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/theory_20260917_six_coordinate_matching_filter.py --out acceleration/results/20260917_six_coordinate_matching_filter/run01 --domain-audit AUDIT_PATH --domain-audit-sha256 EXACT_AUDIT_HASH
```

No nontrivial automorphism assumption, noLP, noledgeredits. Overall search
coverage: UNKNOWN; no validated denominator for Conway-99.

# Complete exact-eight count-table join, gated preparation

This new producer is prepared, not executed. Require an authenticated independent
gate with status `INDEPENDENT_EXACT_EIGHT_PROFILE_PREFLIGHT_PASS`, binding the
complete4184-subset preflight summary and inventory plus every coordinate-domain,
catalogue, support and retained-subset input in its manifest. No native SAT.

The exact scope is the baseline count-table relaxation with exactly eight
exceptional groups, restricted by the previously proved necessary kernel census.
The preflight partitions4184 distinct subsets into3847 activity-coverage failures,
270 count-table GAC failures and67 nonempty fixed points. Enumerate all67 in
lexicographic group-subset order. Do not subtract the first/second/third profile
exclusions, apply the540 scalar upper bounds, use AC-filtered local triples,
assume an orbit size or claim a full factor. This join inherits only the raw
local-triple table's within-group caps and Gram upper bounds.

Rebuild the6061 distinct six-by-three signatures from all31110 saved local
triples. Re-read all2226 complete coordinate choices. For each surviving subset,
use exactly its gate-bound retained coordinate domains and rebuild the compatible
signature bitsets; all other groups are forced balanced. DFS uses static ascending
(domain-size, coordinate) order, intersecting group signature bitsets on each
assigned coordinate. At a leaf, all20 signatures are unique, all twelve marginal
choices are retained, and exactly the nominated eight groups are unbalanced.
No multiple realizers of a count signature create duplicate count profiles.

Save every labelled profile in per-subset deterministic gzip JSONL, including
all12coordinate-choice IDs, all20signature IDs, the full12x20x3 integer counts,
the exact exceptional subset, count digest and canonical global-fibre digest.
Evaluate every one of six global fibre permutations; store a canonicalizing
permutation and the actual distinct-image count. Save per-subset complete orbit
membership and representative counts. For a completed subset, each orbit's
member count must equal its actual size and the total must equal its labelled
profile count. These are count-table orbits, not target automorphisms.

First run: at most120 wall seconds, checked during DFS. On expiry keep the
incomplete subset's partial file/record, and mark it incomplete. Only completely
enumerated subsets enter the exact aggregate. Resume is explicit in a NEW output
directory with `--resume-from PRIOR --resume-summary-sha256 SHA`; authenticate
the same producer/spec/gate and every completed profile/orbit record. Resume
reuses the completed prefix and restarts the previously incomplete subset; it
does not claim continuation of its internal DFS stack. No automatic retry.

Before any research enumeration, compare the actual DFS routine against all8
Cartesian assignments for all256 pairs of binary two-coordinate relations.
Check all three authentic count witnesses against the raw tables and conditional
coordinate domains. Reject changed count signatures, duplicate coordinate IDs,
bad activity/canonicalization and corrupted hash pins. Genuine count controls are
not full-factor controls. All outputs remain CANDIDATE until separate review.

CLI:
```text
--preflight-gate REPORT --preflight-gate-sha256 SHA --out NEW
[--resume-from PRIOR --resume-summary-sha256 SHA]
```

Use the locked uv Python environment. No ledger/Git/environment changes. The
runtime gate hash is supplied by root after independent review; no placeholder
gate is accepted. This source imports no repository producer or checker.

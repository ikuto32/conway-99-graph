# source150 macro (3,1) independent shard audit

Status: `SOURCE150_M31_INDEPENDENT_EXACT_SHARD_AUDIT_PASS`

The audit independently reconstructed macro `(3,1)` from the source150 local
representatives and Gram macro catalog. It checked each stored mask, `Q`, orbit
size, macro key, and input hash against seven contiguous direct exact shards.
The direct ordinary-local-pair layer has two SAT witnesses; these are not
credited as exclusions there. An uncapped exact synchronized labelled-map pair
supplement excludes precisely those two records.

| direct local status | orbits | labelled coverage |
|---|---:|---:|
| UNSAT | 394 | 130,688 |
| SAT | 2 | 384 |
| UNKNOWN | 0 | 0 |

After exact supplement: UNSAT 396 orbits / 131,072
labelled coverage, SAT 0, UNKNOWN 0. There are no gaps, duplicates, or
projection-derived exclusions. This is a macro-local finite CSP certificate
bridge, not a DRAT certificate or a complete exclusion of source150/E0=72.

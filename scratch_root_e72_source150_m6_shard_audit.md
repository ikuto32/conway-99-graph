# source150 macro (6,0) exact shard audit

Status: `SOURCE150_M6_EXACT_SHARD_AGGREGATE_AUDIT_PASS`

The 704 catalogued local-graph orbits of macro `(6,0)` were partitioned into
six contiguous, nonoverlapping shards. Their orbit mass is 262,144,
matching the catalog exactly. Each shard used the uncapped synchronized CSP
with exact ordinary-pair filtering and no projection.

| status | orbits | labelled coverage |
|---|---:|---:|
| UNSAT | 704 | 262,144 |
| SAT | 0 | 0 |
| UNKNOWN | 0 | 0 |

Only the UNSAT row is credited as excluded. SAT and UNKNOWN are never counted
as exclusions. Consequently `all_catalog_orbits_excluded` is
`true`. This is a finite local-CSP result, not
a DRAT certificate and not by itself a complete source150 or E0=72 exclusion.

The JSON binds the source catalog, input filters, solver, runner, checkpoint
manifest, and all six shard artifacts by SHA-256 and contains the per-record
coverage bridge.

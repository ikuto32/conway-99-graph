# Independent E0=75 fixed-local exact SAT summary

## Result

The independently built fixed-local portfolio reached solver-terminal
`UNSAT` on all **352/352** local graph representatives.  There were no `SAT`
or final `UNKNOWN` branches.

This eliminates the audited E0=75 local-representative catalog within the
encoded exact rooted SRG model.  It does **not** by itself constitute a
certificate-backed mathematical proof: CaDiCaL returned terminal `UNSAT`, but
no DRAT/LRAT certificate was generated or independently checked.

## Exhaustive input coverage

The only local-graph input to the independent model was
`scratch_general_e75_local_graph_reps.json`, guarded by the independent
edge-list reconstruction audit `scratch_general_e75_reps_check.json`
(`VERIFIED`).  The six rows cover 352 canonical orbits and 110,592 labelled
local graphs:

| source row | partition | compression orbit | representatives | labelled weight |
|---:|---|---:|---:|---:|
| 0 | `[2,1,1,1,1,1,1,1]` | 188 | 128 | 8,192 |
| 1 | `[2,1,1,1,1,1,1,1]` | 280 | 64 | 8,192 |
| 2 | `[1,1,1,1,1,1,1,1,1]` | 37 | 64 | 4,096 |
| 3 | `[1,1,1,1,1,1,1,1,1]` | 61 | 32 | 8,192 |
| 4 | `[1,1,1,1,1,1,1,1,1]` | 62 | 24 | 65,536 |
| 5 | `[1,1,1,1,1,1,1,1,1]` | 64 | 40 | 16,384 |

Every representative has total incident deficit 9 and exactly 18 fixed
overlap edges.  The eight-exceptional-fibre rows have 23 fixed internal edges;
the nine-exceptional-fibre rows have 27.

## Independent fixed CNF contract

Each representative was rebuilt as a fresh CNF from its explicit symbol-label
edge list.  The model does not read or import the shared incremental SAT
implementation.  Per branch it contains:

- all 1,680 disjoint-support outer-edge variables;
- all 1,176 exact `BP` equations;
- all 3,486 exact outer-pair equations;
- 65,520 product helpers, each encoded by a full three-clause AND equivalence;
- zero redundant support-aggregate rows.

Ordinary-C4 block constraints are applied in both directions for high-high
blocks, only on the rigorously forced high side for high-low blocks, and not
at all for low-low blocks.  All non-disjoint outer edges are fixed directly
from the local graph (with ordinary same-fibre C4 edges reconstructed from
the labels).

A SAT return would be expanded to all 99 vertices and passed through the full
SRG verifier before being recorded as valid.  No SAT return occurred.

## Staged solver results

CaDiCaL 1.9.5 was invoked through PySAT with four worker processes and a
per-branch checkpoint.

| pass | branches attempted | conflict budget | UNSAT | UNKNOWN | SAT |
|---|---:|---:|---:|---:|---:|
| first | 352 | 20,000 | 254 | 98 | 0 |
| second, first-pass UNKNOWN only | 98 | 200,000 | 98 | 0 | 0 |
| latest terminal state | 352 | — | **352** | **0** | **0** |

There are 450 preserved attempt records.  The largest terminal conflict count
was 120,951 (branch 289), whose solve time was also the maximum at 54.594 s.
Summed over concurrent attempts, recorded build time was 296.979 s and solve
time was 3,753.138 s.

## Cross-implementation catalog agreement

The final audit compares against the normalized catalog used by the shared
incremental implementation,
`scratch_general_e75_incremental_records.json`.  Matching on the intrinsic
triple `(partition, compression_orbit_index, canonical_local_mask_hex)` gives:

- cross-keys: 352/352;
- explicit local edge lists: 352/352;
- orbit weights: 352/352;
- per-row orbit counts and labelled weight sums: exact agreement.

The independent fixed-CNF terminal result also agrees with the shared
incremental sweep's 352/352 covered `UNSAT` result.  The two solver workflows
remain computational checks; neither has an independently verified UNSAT
certificate in these artifacts.

## Artifacts

- `scratch_e75_fixed_exact_sat.py`: independent model and staged runner
- `scratch_e75_fixed_exact_catalog.json`: flattened 352-branch catalog
- `scratch_e75_fixed_exact_checkpoint.json`: all 450 attempt records
- `scratch_e75_fixed_exact_portfolio.json`: final staged invocation and cumulative state
- `scratch_e75_fixed_exact_audit.py`: independent coverage/result cross-audit
- `scratch_e75_fixed_exact_audit.json`: `ok=true` machine-readable audit


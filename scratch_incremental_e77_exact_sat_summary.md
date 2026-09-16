# E77 validation of the incremental local-representative exact SAT base

Result: all three E77 orbit-22 local representatives are direct CaDiCaL UNSAT in one shared solver instance, agreeing branch-for-branch with both older independent portfolios.

| branch | orbit size | assumptions (+/-) | conflicts | solve s | core | status |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 256 | 35 / 167 | 17932 | 11.438 | 22 | UNSAT |
| 1 | 128 | 35 / 167 | 360 | 0.046 | 22 | UNSAT |
| 2 | 128 | 35 / 167 | 2592 | 0.891 | 23 | UNSAT |

The three orbit sizes 256, 128, 128 cover all 512 labelled local graphs retained by the separate E77 port audit.

Shared model: 361998 variables, 836316 clauses, 202 exceptional same/overlap edge variables, 1680 disjoint edge variables, 1176 BP equalities, and 3486 outer-pair equalities. Redundant support-aggregate rows: 0.

Every branch fixes all 202 local variables by 35 positive and 167 negative assumptions. The audit rebuilds their hashes and checks every returned assumption core is a subset of its full assignment.

Boundary: these are computational UNSAT answers without separately emitted and independently checked proof certificates.

Artifacts: `scratch_incremental_local_exact_sat.py`, `scratch_incremental_e77_exact_sat.json`, `scratch_incremental_e77_audit.json`, and this summary.

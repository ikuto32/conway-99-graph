# E75 incremental local exact-SAT audit

Result: **all 352 normalized local representatives are UNSAT**; SAT=0 and UNKNOWN=0.

| rec | orbit | reps | labelled | direct | core-covered | budget | solve s | vars | clauses |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 188 | 128 | 8192 | 74 | 54 | 200000 | 13.328 | 425464 | 981348 |
| 1 | 280 | 64 | 8192 | 26 | 38 | 100000 | 55.935 | 393496 | 907764 |
| 2 | 37 | 64 | 4096 | 58 | 6 | 100000 | 54.859 | 442034 | 1018784 |
| 3 | 61 | 32 | 8192 | 27 | 5 | 100000 | 26.578 | 409778 | 944720 |
| 4 | 62 | 24 | 65536 | 24 | 0 | 200000 | 106.500 | 425634 | 980616 |
| 5 | 64 | 40 | 16384 | 40 | 0 | 200000 | 22.375 | 401466 | 925620 |

Totals: 249 direct CaDiCaL UNSAT + 103 exact core-containment exclusions = 352 representatives, covering 110592 labelled local graphs. Aggregate branch solve time: 279.575s.

Records 1--3 are independently produced complete checkpoints and terminated under a 100,000-conflict limit. Records 0, 4, and 5 used 200,000. Since all branches returned terminal UNSAT, no UNKNOWN retry set remains.

The audit rebuilds all six CNFs, all representative IDs/orbit sizes/local edge sets, complete signed assumption vectors and hashes, and each literal core containment. Every CNF has 1,176 BP equalities, 3,486 outer-pair equalities, all 105 disjoint blocks (1,680 edge variables), and no redundant support-aggregate rows.

Boundary: the CaDiCaL UNSAT answers are computational and have no separately emitted, independently checked proof certificates.

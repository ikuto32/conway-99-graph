# E75 incremental normalization / probe audit

Status: **OK**. The six support records contain 352 orbit representatives covering 110592 labelled local graphs.

| rec | reps | labelled | local vars | vars | clauses | probe status | hash |
|---:|---:|---:|---:|---:|---:|---|---|
| 0 | 128 | 8192 | 336 | 425464 | 981348 | UNSAT | `9228B08C531F4B4D...` |
| 1 | 64 | 8192 | 272 | 393496 | 907764 | UNSAT | `958768B109577FD5...` |
| 2 | 64 | 4096 | 374 | 442034 | 1018784 | UNSAT | `F45306FB7EE719E2...` |
| 3 | 32 | 8192 | 310 | 409778 | 944720 | UNSAT | `D81399E5A2759C5D...` |
| 4 | 24 | 65536 | 342 | 425634 | 980616 | UNKNOWN | `F49B4F5214A35E32...` |
| 5 | 40 | 16384 | 294 | 401466 | 925620 | UNSAT | `C58DD2AC9ADB0F07...` |

For every record, rebuilding the one-representative probe reproduces its entire stored model metadata and assumption hash. Rebuilding the complete record has identical structural metadata; only the declared input and representative-summary fields differ.

All prerequisite reconstruction audits have their required COMPLETE/VERIFIED status. Every shared CNF has all 1,176 BP equalities, all 3,486 outer-pair equalities, 1,680 disjoint edge variables, and no redundant support rows.

Boundary: direct UNSAT results remain computational unless accompanied by a separately emitted and independently checked proof certificate.

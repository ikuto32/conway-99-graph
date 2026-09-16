# E73 Q>=4 incremental local exact-SAT audit

Status: **AUDIT_PASS**. SAT=0; UNKNOWN=0.

| rec | orbit | reps | labelled | direct | core-covered | vars | clauses |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 13 | 128 | 16384 | 128 | 0 | 361998 | 836316 |
| 1 | 21 | 1024 | 32768 | 372 | 652 | 425464 | 981348 |
| 2 | 42 | 512 | 32768 | 510 | 2 | 393496 | 907764 |
| 3 | 47 | 64 | 4096 | 51 | 13 | 442034 | 1018784 |
| 4 | 55 | 32 | 4096 | 30 | 2 | 409778 | 944720 |
| 5 | 70 | 44 | 8192 | 44 | 0 | 401466 | 925620 |

Totals: 1135 direct solver-terminal UNSAT plus 669 verified assumption-core containments cover all 1804 representatives (98304 labelled local graphs).

Boundary: no DRAT/LRAT certificate was emitted or independently checked, so this is a reproducible computational exclusion, not yet a formal proof.

# E75 first-representative exact-SAT probes

Five probes are computationally UNSAT and one reached the 100,000-conflict cap as UNKNOWN. No SAT branch was found.

| record | partition | compression orbit | full reps | status | solve s | conflicts | vars | clauses |
|---:|---|---:|---:|---|---:|---:|---:|---:|
| 0 | 2+1+1+1+1+1+1+1 | 188 | 128 | UNSAT | 5.937 | 7925 | 425464 | 981348 |
| 1 | 2+1+1+1+1+1+1+1 | 280 | 64 | UNSAT | 0.515 | 917 | 393496 | 907764 |
| 2 | 1+1+1+1+1+1+1+1+1 | 37 | 64 | UNSAT | 0.875 | 1223 | 442034 | 1018784 |
| 3 | 1+1+1+1+1+1+1+1+1 | 61 | 32 | UNSAT | 5.453 | 4352 | 409778 | 944720 |
| 4 | 1+1+1+1+1+1+1+1+1 | 62 | 24 | UNKNOWN | 48.563 | 100003 | 425634 | 980616 |
| 5 | 1+1+1+1+1+1+1+1+1 | 64 | 40 | UNSAT | 7.046 | 9398 | 401466 | 925620 |

Each probe uses the exact shared model with 1,176 BP equalities, 3,486 outer-pair equalities, all 105 disjoint blocks, and zero redundant support-aggregate rows. The signed assumptions exactly equal the first branch in the corresponding full normalized record.

This covers only 6 of 352 local representatives and is not an E75 exclusion. No UNSAT proof certificate was emitted.

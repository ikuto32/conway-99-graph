# E76 incremental local exact-SAT audit

Result: **all 311 normalized local representatives are UNSAT**. There are no SAT or UNKNOWN branches.

| rec | source row | compression orbit | reps | direct | core-covered | unknown | solve s | vars | clauses |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 1 | 58 | 52 | 6 | 0 | 54.685 | 314560 | 729124 |
| 1 | 4 | 20 | 52 | 52 | 0 | 0 | 86.607 | 353388 | 817044 |
| 2 | 8 | 6 | 16 | 13 | 3 | 0 | 48.688 | 392974 | 907564 |
| 3 | 12 | 87 | 6 | 6 | 0 | 0 | 10.719 | 361998 | 836316 |
| 4 | 15 | 1 | 40 | 35 | 5 | 0 | 234.172 | 425464 | 981348 |
| 5 | 16 | 13 | 74 | 73 | 1 | 0 | 276.108 | 408840 | 943148 |
| 6 | 18 | 15 | 12 | 11 | 1 | 0 | 88.017 | 409544 | 945004 |
| 7 | 23 | 20 | 28 | 23 | 5 | 0 | 99.049 | 393496 | 907764 |
| 8 | 27 | 88 | 13 | 13 | 0 | 0 | 49.469 | 378280 | 873276 |
| 9 | 28 | 89 | 12 | 12 | 0 | 0 | 10.017 | 369968 | 854176 |

Totals: 290 direct CaDiCaL UNSAT + 21 exact assumption-core containments = 311 excluded representatives; 957.531 aggregate branch solve seconds.
The orbit sizes cover 68864 labelled local graphs on the ten canonical support records.

For every support record the shared instance contains all 1,176 BP equalities, all 3,486 outer-pair equalities, all 105 disjoint blocks (1,680 edge variables), and zero redundant support-aggregate rows. Every local representative fixes every exceptional same/overlap edge variable by a complete signed assumption vector.

A `COVERED_UNSAT` row is used only when a previously returned UNSAT assumption core is literally a subset of the new complete assignment. The audit reconstructs and checks each such containment.

Fixed-CNF catalog crosswalk: all 311 keys `(source row, compression orbit, local representative ID)` match, including partition, ordered support/deficit data, orbit size, and local edge count. At audit time its portfolio statuses were {'UNSAT': 311}; every independently terminal fixed-CNF result agrees.

Boundary: direct UNSAT answers are computational CaDiCaL results without separately emitted and checked proof certificates.

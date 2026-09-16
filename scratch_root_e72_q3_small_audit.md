# E72 Q>=3 completed-small-partition audit

Status: **AUDIT_PASS**.

## Exact local coverage

| partitions | rows | states | completions | spectral | pair | forced BP | reps |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 11 | 68 | 2140 | 6926336 | 6926336 | 1714856 | 24576 | 584 |

All 584 stored edge-list representatives were reconstructed; their port matchings, pair upper bound, forced-C4 BP tests, spectral inequality, and full residual-symmetry orbits were independently checked. The three surviving support rows represent exactly 24,576 labelled local graphs.

## Exact-SAT coverage

| source | representatives | direct UNSAT | core-covered | UNKNOWN |
|---|---:|---:|---:|---:|
| initial record 0 | 224 | 222 | 1 | 1 |
| initial record 1 | 272 | 249 | 23 | 0 |
| initial record 2 | 88 | 82 | 6 | 0 |
| deep replacement for record 0 branch 2 | 1 | 1 | 0 | 0 |

The initial runs terminally covered 583 representatives. The sole UNKNOWN has the same rebuilt shared-CNF hash and complete-assumption hash as the 200,000-conflict deep run, which terminated UNSAT. Thus all 584 are computationally UNSAT (554 direct and 30 exact core containments).

Merged checkpoint: `scratch_general_e72_q3_small_record00_sat_merged.json`.

## Boundary

No DRAT/LRAT certificate was emitted or independently checked. This is a reproducible computational exclusion for the eleven listed partitions, not a formal proof and not a complete exclusion of the E72 branch.

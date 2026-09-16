# Complete E72 macro-coverage inventory

Status: **COMPLETE_E72_COVERAGE_INVENTORY_PASS**.

The canonical catalog coverage 141,545,472 is counted exactly once. Evidence classes are deliberately not conflated.

| bucket | coverage | status |
|:---|---:|:---|
| small_partitions | 45,056 | DRAT_BACKED_VIA_AUDITED_LOCAL_CENSUS |
| source134 | 101,593,088 | DRAT_VERIFIED_FULL_EXACT_CNF |
| source248 | 28,344,320 | DRAT_VERIFIED_FULL_EXACT_CNF |
| source133_regular | 2,490,368 | EXACT_SOLVER_FREE_ENUMERATION |
| source133_nonregular | 12,288 | DRAT_VERIFIED_FULL_EXACT_CNF |
| breadth_formal | 4,972,544 | DRAT_VERIFIED_FULL_EXACT_CNF |
| breadth_computational_only | 966,656 | TERMINAL_CADICAL_UNSAT_NO_CHECKED_PROOF_YET |
| source630 | 196,608 | TERMINAL_CADICAL_UNSAT_NO_CHECKED_PROOF_YET |
| other_zero_BP_rows | 65,536 | EXACT_LOCAL_BP_ENUMERATION_EMPTY |
| source150_recurrence_rejected | 393,216 | EXACT_SOLVER_FREE_RECURRENCE_ENUMERATION |
| source150_synchronized_localpair_rejected | 32,768 | EXACT_SOLVER_FREE_SYNCHRONIZED_LOCALPAIR_ENUMERATION |
| source150_synchronized_joint_map_m01_rejected | 65,536 | EXACT_SOLVER_FREE_SYNCHRONIZED_JOINT_MAP_ENUMERATION |
| source150_m47_exact_shards_rejected | 1,048,576 | EXACT_SOLVER_FREE_LOCAL_CSP_SHARDS |
| source150_m2_exact_shards_rejected | 262,144 | EXACT_SOLVER_FREE_LOCAL_CSP_SHARDS |
| source150_m6_exact_shards_rejected | 262,144 | EXACT_SOLVER_FREE_LOCAL_CSP_SHARDS |
| source150_m00_exact_rejected | 8,192 | EXACT_SOLVER_FREE_LOCAL_CSP_ENUMERATION |
| source150_m31_exact_shards_rejected | 131,072 | EXACT_SOLVER_FREE_LOCAL_CSP_PLUS_JOINT_MAP_SUPPLEMENT |
| source150_m10_joint_primary_rejected | 8,192 | EXACT_SOLVER_FREE_LOCAL_CSP_JOINT_MAP_PRIMARY |
| source150_open | 32,768 | OPEN |
| open_frontier_defect_rank_rejected | 61,440 | EXACT_POINTWISE_KERNEL_PORT_ENUMERATION |
| source332 | 131,072 | FORMAL_AUDIT_PASS |
| other_active_open_rows | 421,888 | OPEN |

Classified non-open: 141,090,816. Unresolved/pending: 454,656. Of the non-open coverage, 135,098,368 is DRAT-backed, 4,829,184 is covered by exact executable finite enumeration, and 1,163,264 currently has only a terminal CaDiCaL UNSAT result.

Source150 is split without overlap: the recurrence audit rejects 393,216, synchronized local-pair enumeration rejects a further 32,768, the synchronized joint-map `(0,1)` enumeration rejects 65,536, complete exact shards of `(4,0)` and `(7,0)` reject 1,048,576, complete exact shards of `(2,0)` reject another 262,144, and complete exact shards of `(6,0)` reject another 262,144, the complete exact `(0,0)` sweep rejects another 8,192, the complete exact `(3,1)` shards plus two exact joint-map supplements reject another 131,072, the complete `(1,0)` joint-primary shards reject another 8,192, and 32,768 remains open. Source133 is complete via the regular 5,138 -> 81 -> 1 -> 0 solver-free chain plus the nonregular DRAT proof.

The pointwise equitability-kernel/port census then rejects source rows 171, 1095, and 1119 (four macros, 61,440 coverage) by an independently replayed exact finite certificate.

Source332 has a completed three-profile formal bridge; its shared 131,072 coverage is counted once, not three times.

Boundary: this ledger is not a proof that the Conway 99-graph does not exist. Open/pending rows remain, and evidence classes retain their certificate qualifications.

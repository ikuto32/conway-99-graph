# Independent overlap two-edge trade audit

Status: `INDEPENDENT_FIVE_OVERLAP_TWO_EDGE_TRADE_AUDIT_PASS`.

All 135,240 alternate matchings of 67,620 disjoint source-edge pairs were independently enumerated. The legal sets match all 677 saved trades exactly, including every intermediate filter count.

| Source | Legal trades | Exact own-cut score range |
|---|---:|---:|
| scratch_resume_overlap_lift.json | 134 | -738 to -403 |
| scratch_next_overlap_alternatives_r0.json | 129 | -742 to -540 |
| scratch_next_overlap_alternatives_r1.json | 142 | -712 to -304 |
| scratch_next_overlap_alternatives_r2.json | 145 | -735 to -446 |
| scratch_next_overlap_alternatives_r3.json | 127 | -745 to -466 |

Each trade was rebuilt as a 99-vertex graph with 357 fixed edges, degrees 14 on 15 vertices and 6 on 84 vertices. All overlapping compression totals, label quotas, and all 4,851 pair capacities were checked directly. The audit derives each signed quota equality and nonnegative pair-cap inequality from actual adjacency and semantic certificate coordinates; it then computes the exact box lower bound over 1,680 unknown disjoint-support edges.

All 677 own-cut scores are negative. All five saved fixed-cut scores and all five scores after the recorded sign flip also match independent exact evaluation. All 677 sign-flipped assignments are outside the 640 saved sign images and pass the five fixed-index cuts. Reapplying the same sign flip returns each original rejected assignment, which supplies a conjugate own-cut obstruction for every one of these images. No producer or solver code was imported and no numerical solver was called.

This exhausts a one-switch neighborhood of five fixed assignments only. It does not exclude all overlap assignments, an E0 layer, or a Conway graph. Passing five fixed cuts does not establish disjoint completion or passage of their full relabeling families. The selected sign-flip candidate is audited separately by root. E72 processes and the ledger were untouched.

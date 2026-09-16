# E72 lean full-Gram breadth audit

Status: **BREADTH_AUDIT_PASS**.

At c100k, 23 source rows covering 5,939,200 labelled macro completions were screened: 6 terminal UNSAT (573,440 coverage), 17 UNKNOWN, and no SAT.

| seq | rank | source | macros | coverage | c100k | conflicts | latest | formal |
|---:|---:|---:|---:|---:|:---|---:|:---|:---|
| 1 | 3 | 181 | 1 | 1,048,576 | UNKNOWN | 100,003 | UNSAT | VERIFIED |
| 2 | 4 | 182 | 1 | 1,048,576 | UNKNOWN | 100,000 | UNSAT | VERIFIED |
| 3 | 6 | 194 | 1 | 524,288 | UNKNOWN | 100,000 | UNSAT | VERIFIED |
| 4 | 5 | 177 | 1 | 524,288 | UNKNOWN | 100,005 | UNSAT | VERIFIED |
| 5 | 7 | 524 | 5 | 442,368 | UNKNOWN | 100,004 | UNSAT | VERIFIED |
| 6 | 8 | 587 | 3 | 327,680 | UNKNOWN | 100,002 | UNSAT | VERIFIED |
| 7 | 9 | 195 | 1 | 262,144 | UNSAT | 79,136 | UNSAT | VERIFIED |
| 8 | 10 | 172 | 3 | 200,704 | UNKNOWN | 100,000 | UNSAT | VERIFIED |
| 9 | 11 | 193 | 3 | 200,704 | UNKNOWN | 100,000 | UNSAT | VERIFIED |
| 10 | 12 | 197 | 2 | 196,608 | UNKNOWN | 100,001 | UNSAT | VERIFIED |
| 11 | 14 | 562 | 2 | 196,608 | UNKNOWN | 100,002 | UNSAT | VERIFIED |
| 12 | 13 | 553 | 2 | 196,608 | UNKNOWN | 100,000 | UNSAT | - |
| 13 | 16 | 302 | 2 | 131,072 | UNKNOWN | 100,002 | UNSAT | - |
| 14 | extra | 162 | 2 | 98,304 | UNSAT | 514 | UNSAT | - |
| 15 | 18 | 611 | 6 | 98,304 | UNKNOWN | 100,000 | UNSAT | - |
| 16 | 20 | 291 | 1 | 65,536 | UNSAT | 23,743 | UNSAT | - |
| 17 | 19 | 137 | 4 | 65,536 | UNKNOWN | 100,000 | UNSAT | - |
| 18 | 22 | 335 | 1 | 65,536 | UNSAT | 85,469 | UNSAT | - |
| 19 | 21 | 331 | 2 | 65,536 | UNKNOWN | 100,000 | UNSAT | - |
| 20 | 23 | 610 | 4 | 57,344 | UNKNOWN | 100,000 | UNSAT | - |
| 21 | 26 | 196 | 8 | 40,960 | UNKNOWN | 100,000 | UNSAT | - |
| 22 | 24 | 159 | 4 | 40,960 | UNSAT | 10,944 | UNSAT | - |
| 23 | 25 | 168 | 6 | 40,960 | UNSAT | 70,532 | UNSAT | - |

Source332 was intentionally skipped: its one-dimensional Gram family has three admissible integral profiles (t=-1,0,1), which the unique-Gram builder cannot safely select.

Related source133 inventory (outside this c100k screen): regular macros 0--3 contribute 2,490,368 coverage and are excluded by an exact solver-free 5,138 -> 81 -> 1 -> 0 finite-map chain; nonregular macro 4 contributes 12,288 and has a DRAT-VERIFIED full exact-CNF certificate. These sum to the complete 2,502,656 source133 catalog coverage. The solver-free part is an executable enumeration, not a proof-assistant kernel certificate.

Boundary: UNKNOWN is not a feasibility result. A terminal search result is computational until its CNF proof is externally checked, and all CNF results remain conditional on the upstream semantic bridges.

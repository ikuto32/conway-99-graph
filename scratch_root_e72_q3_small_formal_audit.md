# E72 Q>=3 small-snapshot formal certificate audit

Status: **FORMAL_AUDIT_PASS**.

| record | branches | labelled | clauses | proof lines | checker |
|---:|---:|---:|---:|---:|---|
| 0 | 224 | 8192 | 822636 | 2680838 | DRAT_VERIFIED |
| 1 | 272 | 8192 | 916840 | 2289903 | DRAT_VERIFIED |
| 2 | 88 | 8192 | 839439 | 2131751 | DRAT_VERIFIED |

All 584 local representatives (24576 labelled local graphs) are covered. Each selector CNF was independently rebuilt byte for byte from the shared exact CNF and audited assumption cores before binding it to the checked proof hash.

The producer used the explicit UCRT flush and native CaDiCaL finalization; all proofs contained solver-emitted terminal empty clauses. The pinned checker is upstream commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` and returned `s VERIFIED` for all three formulas.

Boundary: this formally certifies the 584 exact-SAT branches in the eleven completed small partitions. It does not cover the remaining E72 partitions.

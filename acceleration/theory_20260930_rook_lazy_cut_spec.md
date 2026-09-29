# First exact Gram-support SAT refinement

Status: preregistered CANDIDATE experiment. Do not launch until the separate
direct integer/nogood audit accepts the exact certificate. The existing local
SAT witness and its certificates remain immutable.

Base: the independently audited 780-edge model, with CNF SHA-256
`ed9d0e102b16481fdbcecef34240b5be2b8a357af8c219606bb688dcb5fe9403`.
Retain its 30,420 variables and every one of its 3,689,820 clauses.
The first prospective extra clause is the 45-literal nogood in
`results/20260930_rook_gram_minimized/certificate.json`, SHA-256
`255560186ad410e57582ab34c1b7cb90b899b4d9656ce37285bc06ce98b1145a`.

The independent gate must establish from raw data that the certificate's
integer vector has negative `v^T(27I-9A+J)v`, that all variable coefficients
are included exactly, that all remaining terms are fixed by the model, and
that the clause blocks exactly simultaneous preservation of those variable
values. A target has G²=63G, hence G is PSD; therefore this nogood is sound
for every target extension in the current fixed-central-star scope.

Selection rule: add this single already-generated clause, without changing
the base constraints, variable IDs or known-adjacency mask. The exact next
DIMACS is obtained by replacing only its header clause count with 3,689,821
and appending the clause followed by `0` and newline. Save source hashes,
the ordered appended clauses and the resulting raw CNF hash. Public replay
may reconstruct it from the base gzip plus the small append record; storing
another copy of the 77.9 MB uncompressed base is unnecessary.

First refinement limit: one solver invocation, at most 300 seconds including
parse/load/proof finalization, and 1,000,000 conflicts. A SAT assignment needs
a separate all-clause and raw59 adjacency check before a new Gram test. An
UNSAT result needs the full raw proof checked against this exact augmented
CNF, plus the base-encoding and cut-soundness premises. Caps/errors remain
UNKNOWN. No conclusion applies to unrestricted existence or all rook stars.

Any later multi-cut loop requires an explicit ordered certificate list and
the same independent acceptance criterion for every new clause. This first
protocol does not authorize unreviewed learned mathematical cuts. Ordinary
solver-internal learned clauses remain handled by its proof checker.

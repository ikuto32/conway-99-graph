# The at-least-seven extension of the count master

The baseline count master is an exact coupling of necessary coordinate-marginal and local-triple-count tables. It does not enforce a full Gram, cross-group column caps or a residual completion. The all-balanced table is a known baseline solution. A new lower-bound suffix is therefore a necessary full-factor restriction, not a redundant consequence of the baseline formula.

Each group signature records all18 coordinate/fibre counts. A group is balanced precisely when every entry is1. The complete signature table contains exactly one such signature, and it survives unary filtering in each of the20 group domains. Let s_g be that group's balanced-signature selector. Because each group selects exactly one signature, s_g is true if and only if that group is balanced. Hence the number of unbalanced groups is20 minus sum_g s_g. The independently established at-most-six exclusion applies to binary factors on this literal fixed support having the full prescribed integer Gram and all outside-column caps. Every such factor's count table must satisfy

`sum_g s_g <= 13`.

This adds no assumption about an unknown graph's automorphism. It excludes no admissible factor in the scoped capped family. It does exclude some solutions of the weaker baseline count relaxation, including its explicit all-balanced and exactly-six-exception positives. The new model must state that distinction. The lower-bound theorem is not a theorem about arbitrary count tables or abstract uncapped Gram factors.

No separate activity variables are necessary. If desired, b_g for unbalanced can be defined by b_g iff not s_g using `(b_g OR s_g)` and `(not b_g OR not s_g)`, but directly bounding the20 balanced selectors is smaller. The independent preparation records the balanced signature's identity and its position in all20 initial group domains. Actual CNF selector IDs must be bound after build.

For prefix i and threshold j<=14, let t(i,j) mean that at least j of the first i balanced selectors are true. Boundaries are t(i,0)=true and t(i,j)=false for j>i, and the exact recurrence is

`t(i,j) iff t(i-1,j) OR (s_i AND t(i-1,j-1))`.

Induction on i proves every defined state has exactly this meaning when each gate is bidirectional. Forbid t(20,14) to enforce the bound13. There are sum(i=1..20) min(i,14)=189 states. With one maxterm for every falsifying valuation of each gate's distinct nonconstant variables, there are1378 gate clauses and one final unit: the first equality has2, the19 first-threshold OR boundaries have4 each, the13 diagonal AND boundaries have4 each, and156 interiors have8 each. The preflight predicts155939 variables and705833 clauses after appending to the unchanged baseline. These counts do not approve an actual output stream.

The independent preparation uses a separate algebraic CNF for the same Boolean gate: `(not q OR z)`, `(not x OR not r OR z)`, `(not z OR q OR x)`, `(not z OR q OR r)`, with constants folded. It exhaustively checks every local truth valuation and every primary assignment of complete prefixes n=1..6 with bounds0..n, checks each prefix auxiliary against literal counts, and rejects every single flipped auxiliary against the gate constraints. It also checks all2^20 activity masks for the balanced/unbalanced complement identity. Missing implications, flipped output polarity and a changed boundary constant are negative controls. The generic truth checker can later test the actual producer maxterm clauses without importing its constructor.

The future actual-CNF gate must reconstruct all group selectors and balanced references, every prefix state/constant, every clause and the final unit, and compare the exact baseline body retained in the augmented file. It must also calibrate actual native/JSON assignment parsing and count-table decoding. The present report approves only the mathematical interface and checking design; it does not permit a solver launch.

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_20260930_count_master_extension_design.py --out acceleration/results/20260930_independent_review/count_master_extension_design
```

The script imports no producer or previous checker. Use a fresh output directory for replay; the exact lower-bound gate, signature inventory, source and environment are recorded. No ledger or native action occurs.

# Independent finite GF(3) native gate, 2026-10-02

Question: do the frozen v2 wrapper and v1 native binary produce valid artifacts
on the declared finite controls, including packed arithmetic and weighted resume
checkpoints? This is an engineering gate, not approval of a full scientific run.
The independent checker imports only the separately authored and calibrated
scalar checker (698eb9bb..., calibration 8948291c...) and the deadline helper.
It neither imports nor executes producer code.

Frozen population: all 25 recorded native calls, all 99 arithmetic records,
all five independently specified raw fixture operators, and all 13 completed
positive/prefix checkpoint artifacts. Four-variable solution domains are
exhausted; the 130-column fixture is checked by all original scalar rows, not
exhaustive assignments. Every basis row is reconstructed from its original raw
row and weighted earlier dependency rows. Conversely, every completed prefix
row must reduce to zero using that reconstructed basis. Complete vector and
original-row relation certificates are checked with exact signed integer sums.
Every packed physical bit, including padding, is compared to scalar arithmetic.

Acceptance: all population counts and immutable source/build/input/output hashes
match, whole/resume certificate bytes match, every exact mathematical check
passes, and all strict native rejects have their predeclared stderr/exit stage.
Independent malformed controls must reject at syntax; syntactically valid wrong
basis, dependency and prefix controls must reject at the stated identity stage.
Vector, coefficient sign, RHS, relation weight and nondivisor corruptions must
reject. The content-three toy distinguishes original GF(3) from divided GF(3).
No missing control can be inferred successful from a manifest assertion.

Preserve and inspect the failed v1 run: its 13 completed calls do not constitute
the replacement 25-call gate. Its divided vector is checked for exact membership;
the old requirement of one chosen solution is explicitly falsified.

Allocation: 300 seconds outer, 260 worker, 40 seconds shutdown reserve, justified
by five small models and fewer than 200 tiny artifact records. No retry or native
solver invocation. Save success or failure and exact restart command in the
supervisor receipt. Any timeout means the audit was not completed within the
allocated budget. A PASS has no rank, integer feasibility, nonnegativity, graph
realizability, coverage or Conway-99 resolution interpretation.

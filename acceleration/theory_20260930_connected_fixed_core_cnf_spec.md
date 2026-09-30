# Four fixed connected-core necessary factor instances

Frozen preparation question: does the previously audited necessary factor CNF
admit a factor when its core is fixed to each of the four already selected
connected identity-P construction domains? These four cores are selected by
the prior deterministic census rule, not by the later GPU scores. They are
not an exhaustive cover of the target. No target automorphism is assumed.

For each core, append exactly 24 positive unit clauses to the authenticated
110904-variable, 518160-clause original variable-core instance: six edges of
M1, six edges of M2, and twelve entries of P. Obtain variable IDs from the
authenticated model metadata. All remaining matching/permutation entries are
then false by the base exactly-one constraints. Preserve every base clause
byte and use the header `p cnf 110904 518184`. Retain the chosen raw core,
unit-to-semantic mapping, exact input/output hashes and preparation manifest.

Success for preparation means four well-formed instances, each with the exact
base body followed by its recorded 24 units. No SAT solver is called here.
Independent encoding and complete decoded-object calibration gates are
required before research calls. A SAT factor is still missing the residual
60-vertex adjacency D. UNSAT with complete independently checked proof would
exclude only that fixed core, contingent on the audited necessary encoding.
Timeout/error/partial trace implies neither exclusion nor feasibility.

Before building, exhaust all three perfect matchings on four coordinates and
all six permutations on three coordinates to test that positive units plus
the exactly-one domain identify exactly the prescribed choice. Reject an
omitted unit, duplicated unit, wrong semantic edge and nonsymmetric matching
in the mapping controls. These are producer controls, not independent review.

Preparation resource limits: 120 seconds, 512 MiB output, four deterministic
instances, zero solver calls, no random seed, exact integer arithmetic only.
The program retains any partial outputs on failure and never overwrites a
previous run. No numerical acceptance threshold applies. Later search limits
must be recorded separately before execution.

```
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python acceleration/theory_20260930_connected_fixed_core_cnf.py --out acceleration/results/20260930_connected_fixed_core_cnf
```

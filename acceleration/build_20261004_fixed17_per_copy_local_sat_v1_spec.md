# Fixed-count exterior local SAT encoding, version 1

This is a **SOURCE_ONLY** new caller proposal. No import, AST extraction,
calibration, model computation, encoding build, native solver, proof check or
registry action has been performed by its author. Source author and discovery
producer are `/root/structural`. Root must authorize each actual invocation
after source review and fresh admission. Existing full99 CNF gates do not apply
to this changed caller. Research remains stopped outside specifically authorized
work under the current compute policy.

## Scope and inputs

The design premise is the frozen
`DESIGN_20261004_FIXED17_PER_COPY_LOCAL_SAT_FALLBACK_V1.md`, SHA256
`4fc65779421b01f886425cf9beb6b34f1b28c70c25917fddb5d76e32df0c3556`.
The independently checked copy-model prerequisite is a future genuine
`INDEPENDENT_FIXED17_PER_COPY_ADJACENCY_V1_COMPLETE_PASS`, implementation 1,
Checkpoint producer, Native verifier, `independent_artifact_check`, target NONE.
Its direct input map must bind the exact submitted profile and copy model.
This caller authenticates the submitted prerequisite/direct bytes and inherits
its qualified scope; it does not rewalk or independently authenticate that
prerequisite's full ancestor closure. Root acceptance remains a separate input.

The scientific domain is exactly n=99, k=14, m=17, 472 ordered type masks,
68 positive count types, 82 labelled outside copies, 3321 unordered copy pairs,
82 degree rows and 1394 support-incidence rows. The weighted type cardinality
is 166. A future configuration must bind the current caller/specification,
profile, complete copy model, prerequisite complete gate, Root acceptance,
genuine current author controls, a different-author applicable encoding-control
gate, and Root ONE authority. All actual endpoint references are null in the
initial configuration/proposal; no runnable build command exists yet.

The profile has precisely `target_order`, `target_degree`,
`support_adjacency`, `ordered_masks`, `counts`, `pair_bits`. All integer tests
exclude bool and float aliases. Pair rows are lexicographic combinations with
replacement and have literal bits [], [0], [1], or [0,1]. An occupied pair of
distinct copies may not have an empty allowed mask. A diagonal class with only
one copy creates no self-edge and need not have a nonempty allowed mask.
Generic engineering fixtures are bounded by n<=99, m<=17, <=472 types; the
separate scientific-scope guard rejects their use as the target input.

The caller independently reconstructs the entire exact
`FIXED17_COPY_ADJACENCY_MODEL_V1` from the profile. It compares types and values
recursively, not Python numerical equality alone. It retains the producer's
copy-major row order when checking this input, including every row's kind,
copy/type/support labels, RHS, and sorted unit-coefficient terms. It imports
neither the copy producer nor its numerical solver.

## Encoding

Canonical outside labels are [type_i, copy_c], ordered by type then copy.
Every x<y has a zero-based model variable v and SAT ID v+1. No diagonal
variable exists. An allowed mask lacking 1 fixes this edge to 0; [1] fixes it
to 1; [0,1] leaves it free. All fixed units are emitted once in pair order,
before row groups. Each variable-map entry records bounds and its unit clause
range (a zero range for a free edge).

The emitted group order is all 82 degree rows first, followed by all 1394
support rows in copy-major, support-coordinate order. This differs only in
presentation from the authenticated input's interleaved row order. Each
group explicitly records its original model-row index and complete row.

For each equality, fixed-1 terms are subtracted from the RHS; fixed-0 terms
are removed; surviving SAT inputs remain ordered and unique. The residual
is an unrestricted integer at this step. If it is negative or greater than
the number of surviving inputs, emit one empty clause. Keep the group,
original RHS, fixed terms, residual, empty states, null auxiliary fields and
one-clause range. Do not clamp, omit or weaken it. Empty input/residual 0 is
a valid constant equality and may emit no clauses; its group still exists.

For other residuals use the exact immutable `Encoder.counter(inputs,
residual, True, annotation)` threshold equivalence. Its recurrence is
z <=> a OR (b AND c), with boolean constant folding; states record every
[prefix length, threshold, bool-or-literal reference]. Both terminal
equality constraints are retained. The helper's clause emitter folds true
clauses, removes false constants, duplicate literals and tautologies, and
emits an actual empty clause when all literals are false. Thus every satisfying
formula assignment restricts to fixed pair bounds and all original equations,
and every satisfying local edge vector has a threshold extension. These are
local equations only: no outside-pair common-neighbor constraints are encoded.
No equitable partition, common same-type neighbor profile, graph automorphism
or uniform witness is assumed.

The immutable shared component is
`theory_20260930_eight_full99_cnf.py`, SHA256
`21c357543c9397456a911175b277da6e6caa769be31d18c12e034cc76d99074c`.
At a future authorized invocation, parse its authenticated text and compile
only the three definitions `negate`, `Clauses`, `Encoder` in source order.
Do not import that module, its graph validator, historical ResourceCap/main,
or any of its old input/gate/runtime machinery. A subclass adds deadline
ticks to recurrence calls; no logical helper method is rewritten. Clause
output is the helper's actual byte stream, not reconstructed reference output.
AST extraction has not been executed during this source preparation.

## Raw output and durability

Successful scientific build emits exactly 20 non-summary outputs and one
summary: `parsed_profile.json`, `encoding_model.json`, `groups.jsonl`,
`clauses.body`, `local.cnf`, and 15 checkpoints at completed groups
100,200,...,1400,1476. `encoding_model.json` includes the exact input model,
base-variable map, group order and total formula counts. The journal records
all 1476 complete groups, states, auxiliary intervals, clause intervals,
fixed terms and residuals. DIMACS has one exact final p-line followed by
the complete clause body and EOF. Summary input/output maps use workspace
relative POSIX paths and SHA256; the summary is excluded from its own map.

Each checkpoint first flushes/fsyncs both body and journal and records their
exact prefix bytes/SHA256, formula variables/clauses and completed groups.
Actual progress is tqdm over all 1476 groups. Pending rows can have partial
body output if stopped. Previously flushed prefixes persist; an unexpected
exception or hard kill cannot guarantee that a pending suffix is complete or
flushed. Preserve all partial files, `.writing` files and failures. The
256MiB body cap is a guard, not a predicted formula size. The design's
143289-variable/566145-clause upper bounds are paper size bounds, not measured
build counts or solver cost.

Input/output paths are confined to the workspace; links and junctions are
rejected. JSON refuses duplicate keys/nonfinite constants, requires exclusive
fresh output creation, and caps JSON bytes at 64MiB. Source/direct input
hashes, output hashes and summary serialization are all inside the deadline.
Every closing operation has a subsequent tick. A provisional success summary
may coexist with failure after a closing guard: clean supported terminal and
Root acceptance are mandatory. No automatic retry or internal solver exists.

## Finite author controls

The new author calibration has 29 cases: seven positive and 22 deliberately
corrupt cases. Every attempted case retains its payload, observed stage and
result, and the complete table is saved before checking overall agreement.
Success has 29 case JSON files + `controls.json` + `summary.json`: 31 physical
files/30 non-summary output hashes. Failure can add a separate failure object.

| Index | Case | Expected first stage |
|---:|---|---|
|0|Nine constant/input recurrence settings, all eight base assignments each|PASS|
|1|n=0..3, every bound 0..n, all 49 base assignments and all auxiliary assignments|PASS|
|2|Eight fixed-term/empty/impossible residual hand cases, all assignments|PASS|
|3|Rook9 known local encoding witness and all81 ordered CN entries|PASS|
|4|Switched rook passes local equations/encoding but first SRG failure(2,4), CN0 vs1|PASS|
|5|Rook with actual fixed-0 and fixed-1 pair masks|PASS|
|6|Synthetic applicable gate header/direct pins/exact local scope|PASS|
|7|Bool target order|PROFILE_TARGET|
|8|Float degree|PROFILE_TARGET|
|9|Asymmetric support graph|PROFILE_GRAPH|
|10|Bool type mask|PROFILE_MASKS|
|11|Bool count|PROFILE_COUNTS|
|12|Bool pair bit|PROFILE_PAIR_BITS|
|13|Incorrect pair-table ordinal|PROFILE_PAIR_ORDER|
|14|Empty allowed mask for two occupied copies|PROFILE_INCOMPATIBLE_PAIR|
|15|Changed shared variable endpoint|MODEL_VARIABLE_PAIRS|
|16|Missing exact row|MODEL_ROWS|
|17|Changed typed RHS|MODEL_RECONSTRUCTION|
|18|Bool coefficient|MODEL_ROW_DOMAIN|
|19|Bool binary bound|MODEL_BOUNDS|
|20|Duplicate term|MODEL_ROW_DOMAIN|
|21|Diagonal shared variable|MODEL_VARIABLE_PAIRS|
|22|False no-equitable flag|MODEL_FLAGS|
|23|Bool prerequisite implementation|GATE_HEADER|
|24|Changed direct prerequisite pin|GATE_PINS|
|25|Bool complete-equation count|GATE_SCOPE|
|26|Duplicate JSON key|JSON_DUPLICATE|
|27|Nonfinite JSON constant|JSON_NONFINITE|
|28|Rook passed to target scientific scope|SCIENTIFIC_SCOPE|

For recurrence/counter/residual cases every tiny auxiliary assignment is
evaluated. Raw cases retain clauses, states, base assignments and the complete
list of satisfying auxiliary extensions; rejected auxiliary assignments are
source-reproducible rather than separately saved. Rook extensions are derived
from prefix sums, checked for consistency at every literal/constant state,
and then evaluated against the actual complete helper clause list. All243
ordered CN entries for the three fixtures are saved. Those graph diagnostics
are control boundaries, not scientific target verification. The rook geometry
and switched-row boundary are shared with Root/Native/Checkpoint predecessors;
they are not claimed as independent fixture discovery.

The actual author gate would be
`FIXED17_PER_COPY_LOCAL_SAT_V1_AUTHOR_CONTROLS_PASS`, implementation1.
The proposed distinct encoding-control header is
`INDEPENDENT_FIXED17_PER_COPY_LOCAL_SAT_V1_AUTHOR_CONTROLS_PASS`, impl1,
Structural producer/Native verifier/artifact/NONE. Neither gate exists yet.
The proposed complete build status remains CANDIDATE, not mathematical approval.

## Independent verification and future interpretation

A different implementation must reconstruct the qualified profile/model,
canonical pair IDs, fixed units and every group, then independently reconstruct
every counter state and emitted clause. It must check all group/clause ranges,
all15 checkpoint prefixes, variable/clauses counts, full DIMACS through EOF,
the complete declared/physical file population and current source applicability.
Sharing the immutable logical component must be disclosed; the new caller's
finite controls alone cannot approve its scientific output.

This caller neither invokes a SAT solver nor verifies a SAT model or UNSAT proof.
Any subsequent SAT10 would require strict all-variable raw assignment/clause
verification and all3321 edge values/1476 rows. This proves only feasibility of
the exact local system. Full99 graph acceptance requires separate complete
degree/CN checking. SAT20 requires a complete proof and separately contained,
independently qualified proof replay; only then could this fixed count profile
be excluded. Timeout, incomplete encoding or proof, numeric infeasibility and
the earlier MIP UNKNOWN provide no exclusion. Actual build/solve/proof commands
are separately proposed and separately authorized, with no automatic chaining.

The proposed finite author command uses supported SUP2 suspended Windows Job
containment before locked/offline uv, 120outer/100worker/20save/20shutdown.
The future null build proposal uses 600outer/550worker/20save/20shutdown as an
allocation proposal, not old caps or a launch authority. Fresh process/resource,
source, plan, context and output-absence admission is required immediately before
any separately authorized invocation. Current ledger/index/HEAD stay unchanged.

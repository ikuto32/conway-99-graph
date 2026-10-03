# Generic one-instance native producer v2

This is a new generic producer alongside the frozen exact-eight v1 driver.
It shares explicitly listed v1 helpers (hashing, immutable saves, canonical paths,
current Linux process observations and deadline checks),
but uses new generic native command and receipt code. An independent new execution
gate is mandatory; v1 calibration is not transferred. Native binary and every
shared/new source/spec/environment artifact appear in the gate's hash closure.

`POLICY_NATIVE_SINGLE_PLAN_V2` fixes one exact CNF/model/scope and mathematical
checking gates. Required fields: question, scope, selection_rule, success_criterion,
falsification_criterion, independent_verification_criterion, allocation_reason,
numerical_acceptance, source_commit, baseline_and_uncertainty, variables, clauses,
inputs, mathematical_gates and configuration. Numerical acceptance is exactly
`EXACT_INTEGER_CNF_AND_RAW_PROOF_OR_COMPLETE_ASSIGNMENT`. Each input has role/path/
sha256/bytes. Each mathematical gate has path/sha256/expected_status and a
required_input_bindings mapping whose exact selected artifacts must occur both
in its historical inputs and the new producer's rehashed input set.

Configuration declares native_seconds, producer_seconds, address_space_bytes,
proof_file_bytes, shutdown_reserve_seconds, seed, conflict_limit (or explicit null with
conflict_limit_null_reason), host_free_reserve_bytes, ext4_free_reserve_bytes and
aggregate_retained_artifact_bytes. There is no inherited60- or300-second cutoff.
The native timeout dynamically respects the single internal immutable producer
deadline, retaining the explicitly planned shutdown/transfer reserve. All work is additionally
contained by the Linux `run_compute_command` invocation; its deadline includes
uv setup, plan reading, hashing, copying, checking and children. The same minimal
locked `native_budget_env_v1` environment is used. No WSL transport timeout is
treated as Linux containment. GNU foreground timeout children remain in the
enclosing native process group; observed supervisor cleanup is required.

Suggested first unrestricted follow-up, subject to root's frozen plan and fresh
calibration: native1800 seconds, producer2050 seconds, outer2100 seconds,8 GiB
address space,2 GiB proof cap,150-second shutdown/transfer reserve, no conflict cap with explicit reason, seed0 or a
preselected alternative,32 GiB host and8 GiB ext4 reserves,8 GiB artifact ceiling.
The allocation is grounded in a historical300-second unrestricted run yielding
UNKNOWN with346.6 MB partial trace and a strengthened a0 branch yielding434.9 MB.
Those partial traces establish neither SAT nor UNSAT nor a calibrated success
probability. Root must choose a concrete scope and continuation benefit relative
to structural alternatives. The producer asserts no target-wide search coverage.

Runs longer than1800 seconds need timely actual reassessment. An optional shared
review JSON has the supervisor's fields (invocation_id, observed_at_elapsed_seconds,
observations, remaining_cost, benefit_and_alternatives, uncertainty, decision), plus
`observed_at_producer_elapsed_seconds` derived from the producer progress record.
Both clocks must have observations no older than60 seconds; both components
validate independently. The producer saves reviews and renews only its review
cadence, never its hard deadline. A stop/change_method decision or missing/late
review stops further computation, retains raw outputs and asserts no exclusion.

Modes are controls, preflight and research. Controls produce exact tiny3-clause
SAT and4-clause UNSAT formulas with the planned seed/resource/conflict options;
their native time is shortened to10 seconds and shutdown reserve is bounded by
the shortened control allocation (explicitly recorded). A separate outer supervisor
descendant deadline control is required, as for v1. The new gate status is
`INDEPENDENT_POLICY_NATIVE_SINGLE_V2_DRIVER_PASS`; its `tested_configuration`
must equal all planned configuration fields except native_seconds/producer_seconds/
shutdown_reserve_seconds (the shorter control timers are explicitly recorded).
Independent controls require raw complete SAT checking, complete DRAT replay,
corrupt/wrong-CNF proofs and corrupted receipt failures. Any changed source or
configuration requires impact review and fresh applicable controls.

Receipt schema names are `POLICY_NATIVE_SINGLE_BATCH_V2`,
`POLICY_NATIVE_SINGLE_LAUNCH_V2`, `POLICY_NATIVE_SINGLE_RECEIPT_V2`,
`POLICY_NATIVE_SINGLE_CASE_V2` and `POLICY_NATIVE_SINGLE_BATCH_RESULT_V2`.
Launch records preserve exact argv, exact CNF hash, ext4 proof location, actual
dynamic timeout and configuration. Native receipts retain observed exit/time,
reaping and Linux current-process snapshot, complete stdout/stderr bytes and
hashes. Case summaries authenticate launch/receipt and full proof copy equality.
Raw SAT/UNSAT are pending independent validation, and UNKNOWN preserves its
partial trace. Ext4 workspaces are never silently deleted. No source/receipt
asserts independently approved mathematics or target resolution.

Manifest metadata records actual Python/platform and observed CaDiCaL, GNU
timeout, util-linux prlimit and uv version outputs. Their version probes are
separate from the reported count of CNF solver evaluations; they remain inside
the same producer/outer computation allowance.

Positive Conway-99 requires an independently validated complete99 graph.
UNSAT requires exact input, full trace and independent complete replay; a
target-level implication additionally requires encoding equivalence, exact
normalization/coverage and branch/pruning audits. This worker supplies raw
artifacts only. Ordinary completion, schema validation and process cleanup are
engineering statements with their stated scope.

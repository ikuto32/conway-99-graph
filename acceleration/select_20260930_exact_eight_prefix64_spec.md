# Reusable explicit first-unproved64 selector and strict four-part consolidation

This is a source-only wave29 preparation. It has no native, formula producer,
Git, registry, process-launch or automatic retry call. Nothing runs on import.
The root must first freeze a caller request, an authorization plan and their
hashes. Preparing this source does not choose or authorize a future population.
All earlier source versions and failed preparations remain unchanged.

The complete manifest is the existing ALL792 object SHA
e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba.
It includes the historical profiles; no prior orbit is silently subtracted.
The source checks all792 raw720-byte count identities and case/index order.
This is identity checking against an approved universe, not a new completeness
proof or new mathematical approval.

## Explicit future request

`select --request PATH --request-sha256 SHA --out NEW` accepts exactly these JSON
fields, with no default future gate paths, output names or case allocation:

* schema: `EXACT_EIGHT_PREFIX64_REQUEST_V1`;
* campaign_manifest_path, campaign_manifest_sha256;
* authorization_record_path, authorization_record_sha256 (the root-frozen plan);
* completed_proof_gates: ordered list of `{path, sha256, completed_cases?}`;
* selection_reason: nonempty root description;
* build_allocations: four ordered `{attempt_id, out}` records;
* recorded_source_commit: caller-recorded40hex metadata, explicitly not a query
  of current Git state or a claim that it describes every working-tree byte.

Recognized proof statuses are the frozen first12, next32 and generic explicit
batch LITERAL_PROOFS_PASS schemas. Their respective SAT_pending/SAT_verified
counts and UNKNOWN must be zero, pending_case_ids empty, completed count a
positive integer, and every selected row present in the identical order.
All direct inputs/outputs are rehashed. The bound original claim must be revision1
VERIFIED. Every skipped case must have UNSAT_VERIFIED, complete_proof=true,
actual replay integer exit0, accepted=true, expected_acceptance=true, and exact
CNF/proof hashes. The source links each row to one independently checked encoding,
matches its CNF/scope and full raw count table against the manifest, and freshly
hashes the retained complete trace including length. It does not replay DRAT.

Repeated proof-gate paths or repeated case IDs anywhere are rejected, including
identical repeated proofs. No deduplication, implication of unknown results,
generalization across orbits, or inferred batch completion is permitted. The
selected population is exactly the first64 manifest-ordered IDs outside that
disjoint literal union. Fewer than64 remaining is an error; final short batches
need a separately specified policy. The input gate list is explicit and finite,
not discovered by searching result directories.

Output selection.json retains the exact
EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1/FIRST_UNPROVED_MANIFEST_PREFIX_V1 fields
expected by frozen independent checker v3. Four partition files are exact parent
copies with only policy, reason, ordered16 IDs, selected_instances, parent
path/hash, partition index and offset changed. Launch_plan.json uses the existing
EXACT_EIGHT_FOUR_SERIAL_BUILD_PLAN_V1: four workers,120 seconds per chunk and
four `{path,sha256,attempt_id,out}` entries. Attempts/output directories must be
distinct, new and mutually disjoint, including from the selection output. This
is480 seconds of allocated build work, not a single global120-second deadline.
The existing independently calibrated suspended launcher consumes this plan;
the selector does not execute it. A separate summary records all exact pins,
the plan hash and every literal prior proof identity.

## Strict consolidation

`consolidate --selection PATH --selection-sha256 SHA --launch-plan PATH
--launch-plan-sha256 SHA --build-summary PATH SHA` (four ordered occurrences)
`--recorded-source-commit COMMIT --out NEW` consumes only four complete original
serial16-case invocations. It reauthenticates the selected parent proof union,
authorization, exact prefix, partitions, launch plan, all summary hash maps,
actual producer receipts, all16 immutable checkpoints per invocation and eight
named original files per formula. Every raw built count table must equal its
manifest record. Producer command, attempt, output folder, selection and120s
allocation must match. Each exit must be integer0, no outer timeout, no stop,
exactly16 producer calls and no native call. No partial or retry chain is merged.

The output retains EXACT_EIGHT_EXPLICIT_BUILD_CONSOLIDATION_V1 with ordered64
records, selected IDs, pending=[], producer_calls=64, native_calls=0, original
selection reference, four build summaries, four partition references and
automatic_resume/automatic_skip/independent_approval all false. Extra launch-plan
provenance is explicit. The frozen v3 independent checker derives source identity
from the saved command and accepts this schema; it does not hardcode60 prior
cases, a batch source filename or a particular collection of proof gates.

Both modes write only fresh caller-named output directories. Failures preserve
their exact input pins, source hash and traceback; no existing output is removed,
overwritten or retried. References use canonical repository paths and reject
protected files before content reads. Hashes are rechecked before a success
receipt. Missing historical raw proof bytes must be restored through prior
authenticated packages; no unavailable file is silently accepted.

## Preparation controls and limits of validation

The separate preparation-control source exercises synthetic ID populations,
duplicate/unknown/short remaining refusals, order independence, exact64/4x16
partitions, strict count-table bytes and accepted/corrupted literal proof rows.
It must never call select, consolidate, a producer, launcher or native solver,
nor construct a future real request. Source AST checks and these finite controls
do not approve future real proof gates, selections, formulas or mathematical
outcomes. Independent review precedes any real request invocation. Later actual
formulas still require the unchanged complete v3 encoding/object audits.

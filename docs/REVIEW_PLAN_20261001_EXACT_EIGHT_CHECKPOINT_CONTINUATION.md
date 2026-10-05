# Independent review plan: interrupted exact-eight build continuation

This is an engineering and encoding-review adapter, not a new mathematical
restriction or an authorization to execute a build. The original batch04
selection, four serial build allocations, launcher, checkpoints and unfinished
outputs remain immutable. No native solver or Git/ledger operation is permitted
in this reviewer.

## Observed boundary

The frozen batch04 launcher reports four roots stopped for `CHUNK_DEADLINE` at
their separately allocated 120 seconds, actual exit 1223, all roots reaped and
all Job objects observed empty. Each root has checkpoints 001 through 014 and
two pending IDs. Each also has a fifteenth producer receipt with exit 0 and a
child summary, but no fifteenth checkpoint or terminal serial summary. Therefore
the continuation retains 56 checkpointed records. Four additional outputs are
preserved and explicitly unaccepted. They are not silently promoted, discarded,
or counted as failed formula encodings.

There are 60 evidenced original producer invocations. Eight fresh pending-case
invocations would make 68 invocations and 64 accepted formula records, with four
repeated cases from the uncheckpointed boundary. These quantities must remain
separate. The old `producer_calls=14` field records checkpoint time, not the
eventual total number of original receipts.

## Minimal preparation and continuation contract

The parent64 selection is unchanged. A new request pins its path/hash, the old
launch plan, the interrupted launcher, all four retained checkpoint references,
a new explicit authorization and four new attempt IDs/output directories.

Each fresh child copies its old partition but uses
`AUTHORIZED_CHECKPOINT_SUFFIX_CONTINUATION_V1`, the literal two pending IDs,
`selected_instances=2`, the new authorization, `original_partition`,
`retained_checkpoint`, `interrupted_launcher`, and `retained_prefix_count=14`.
The old parent64 path/hash and partition index/offset remain explicit. No new
case selection, proof skip or domain pruning is inferred.

A fresh launcher validator recognizes this contract and reuses the frozen
`SuspendedTree`/`monitor` containment backend and unchanged serial builder. The
old launcher cannot be used directly because its validator requires four
16-case partitions. Reuse of the backend does not waive independent review of
the new validator, its source pins, allocation, output freshness and mandatory
prebuild gate. No automatic retry/resume is permitted.

The final candidate summary uses
`EXACT_EIGHT_CHECKPOINT_CONTINUATION_CONSOLIDATION_V1`, the ordinary complete
candidate status and ordered64 records, plus exact references to the original
selection/launch plan, interrupted launcher, retained checkpoints, continuation
launch plan/launcher and four new selections/summaries. Records are merged in
original parent order, with 14 old and two new records in each partition. It
records 60 original plus eight new producer calls and the four repeated
uncheckpointed IDs. There is no fabricated successful terminal summary for an
interrupted root.

## Independent verification

1. Reuse the frozen independent v3 population, proof-skip and parent-selection
   review; do not import producer or native modules.
2. Reconstruct the exact original four partitions and their commands. Check all
   original launcher source/input pins, process receipts, cleanup evidence,
   preserved-file hashes/sizes, and exact directory inventory.
3. Check every checkpoint prefix and each associated successful child receipt,
   all named formula artifacts, canonical case identity and attempt IDs. Pin
   the fifteenth receipt/output separately, require no later checkpoint, and
   never accept it as a retained record merely from its exit or summary.
4. Check new pending selections equal the literal checkpoint suffixes, with new
   disjoint outputs/attempts, exact authorization and four 120-second limits.
   The preparation report approves provenance/selection only, not CNFs.
5. After separately authorized execution, check all four new process receipts
   and both successful per-case receipts/checkpoints per invocation. Require
   exact64 ordered coverage, no overlaps or omitted cases, and honest 68-call
   accounting. All eight old/new launcher process receipts remain evidence.
6. A new v4 encoding wrapper dispatches this provenance schema to the new
   independent helper, retaining frozen v3 behavior for old schemas. It then
   independently reconstructs all64 initial domains, coefficients and every
   actual clause using the unchanged independent core. No checkpoint count is
   treated as mathematical verification. Fresh object calibration binds v4 and
   the unchanged generic native driver before any native launch.

## Controls and scope

Fresh negative controls must cover reordered/dropped/duplicate pending IDs,
reused outputs/attempts, modified checkpoint/record/artifact hash, wrong old
process exit or deadline, unreaped/nonempty Job, omitted fifteenth receipt,
incorrect 56/60/64/68 accounting, promoting an uncheckpointed record, wrong
new-source or authorization pin, incomplete new summaries and absent/duplicate
process receipts. Positive controls include the exact finite prefix arithmetic
and the full genuine raw-factor/codec controls reused transparently by v4.

The final encoding statement remains literal count profiles with full Gram and
within-triplicate caps. Cross-group caps and residual D remain unencoded. No
proof outcome or broader family exclusion follows from a build or encoding gate.

This document and the new reviewer are prepared before continuation execution.
Draft schema details may be aligned with the separately frozen producer
adapter before the reviewer is frozen; executed/frozen versions are preserved.

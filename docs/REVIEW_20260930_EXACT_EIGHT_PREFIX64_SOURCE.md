# Source-only review of the reusable explicit prefix selector

Reviewer: `/root/structural_attack`. Reviewed on 2026-09-30 at 15:07 UTC.
The producer source is `select_20260930_exact_eight_prefix64.py`, SHA256
16807bb5e5a9bcdb4fbadaa5b0f0ee69e360df46ac60664c0980540e0a891ce8;
its spec is fe04ab0a06577496ae024ec4102e0c6cc869e4bff58f0b3878b3375f3d7ddc27.
This review did not import or execute that module, its modes, or its controls.

The parent selection, partition, and consolidation structures are compatible
with frozen independent checker v3, SHA256
0387354132a3e72496cfc8e0c9a3bbe4216767ee68cbcb6b6de070f6314ece10.
No checker adapter is presently required. Compatibility does not authenticate
a future request or formula; actual hash-bound outputs still require review.

The source supports the first12 proof report's SAT_pending field and the next32
and generic explicit-batch reports' SAT_verified fields. It requires zero SAT
and UNKNOWN counts, no pending cases, all selected proof rows, an authenticated
revision1 VERIFIED binding, and an exact encoding/CNF/scope/raw-count match for
each literal case. It checks complete trace bytes and the accepted replay's
integer exit0 and exact CNF/proof identities. These are authenticated historical
proof premises; the selector does not perform a new proof replay.

Repeated gate paths, repeated literal case IDs, unknown IDs, and fewer than64
remaining members are rejected. The selected cases follow the original792
manifest order after the explicitly supplied disjoint literal skip union.
There is no orbit inference or silent deduplication. The intended current
four-gate premise is12+32+16+64=124 distinct literal IDs, leaving668; the completed
next64 proof gate separately records its disjointness from the prior60. This
source review does not authorize the next selection or add an exclusion.

The emitted selection has exactly the fields v3 reconstructs. Proof references
are normalized to include completed_cases; consolidation reconstructs that same
new selector serialization. It does not promise byte-for-structure compatibility
with arbitrary older selection objects whose optional fields differ.
Each child is an exact parent copy except the accepted partition policy, reason,
16 IDs, selected_instances, parent pins, index, and offset. The source requires
four disjoint fresh output directories and distinct attempt IDs.

Consolidation accepts four complete original16-case serial invocations only.
It checks original hash maps, the declared120-second allocations, exact producer
commands, successful non-timeout receipts, all64 prefix checkpoints, eight named
artifacts per formula, raw count identity, and the ordered64 union. The additional
launch_plan field is provenance accepted by v3; four120-second allocations are
not represented as a single120-second deadline. External launcher correctness
remains a separate engineering premise.

Both modes require explicit input hashes and new output directories. There is
no process launch, solver, producer call, Git query, ledger write, automatic
retry, or resume operation. Failures preserve records; no existing output is
removed. The recorded commit is explicitly caller-supplied metadata.

This is static source/schema review only. Producer preparation controls, actual
request identity, file availability, executions, complete encoding, object
calibration, native outcomes, and proofs are separate checks. It does not cover
the unrelated affine GF(3) work or any labelled-fibre expansion.

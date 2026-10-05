# Independent source review of the nine-record administrative comparison

Reviewer: /root/checkpoint_audit. This is a source-only engineering review of
Root's separate Python comparison of the CP-authored ordinary PowerShell
materializer. It approves no mathematics, execution, installation or availability.
No subject import or invocation occurred.

The whole V1 source and specification were read. The exact V1 source is
acc4c080b59b9a137a408d6cbc50c942f7823b74b2b3eb22661ddfa9f81c0a86;
the specification is 62f0d87d8265143fd22787574ad101d62e3780d9ecd5a2be3152d880ad2b55d3.
The comparison correctly preserves the ordered 435-claim and 23,695-artifact
prefixes, all other top-level fields except the permitted update timestamp,
and all 6,054 PUBLIC records. Recursive comparison distinguishes JSON booleans,
integers and floats. Duplicate keys and nonfinite JSON constants are rejected.

The 115 exact evidence rows are sorted by their path. Existing PUBLIC or
LOCAL_ONLY path/digest matches resolve to the lexicographically first ID;
otherwise the original path ordinal determines the new ID. The newly appended
artifact records are compared completely. Each of the nine complete new claim
objects is reconstructed from the separately reviewed immutable packet,
including exact evidence-ID projection, verification, unknowns, external-source
field and reproducibility. The eight written records have null manifests; the
computed dual29 record alone uses its declared actual computational report.
The candidate dimensions make both nine-object zip comparisons complete.
No identity or projection discrepancy was found.

V1 had a material closing-reserve gap: after the last remaining-time test it
serialized and saved a PASS summary without a new test before success output.
The output path also lacked an explicit containment assertion. These were
reported before any subject launch. This was a source veto, not a failed
administrative run or a mathematical refutation.

The whole V2 source/specification and the literal narrow change were then read.
V2 source 343687b94e63f33010a15c83a5277945eb69261d21b7fe6120f5aaaeae3207d1
and specification c8259e2eacc006a4a6700cca90c379d60d752de611e32c228d40304e20396833
add an absent output resolved within acceleration/results and a fresh
remaining_seconds > 20 assertion immediately after summary serialization,
before success output. The schema version is advanced and all checking
semantics above remain literal. Those changes repair the reported issues.
There is no remaining material static veto for the exact V2 path.

An interrupted or late V2 invocation may retain a provisional summary while
exiting nonzero; its actual clean contained terminal remains required. File
read/hash and JSON parse are finite atomic regions, not a hard real-time
promise. The frozen packet's mathematical statements were separately reviewed;
this subject deliberately checks their administrative preservation rather
than reconstructing their proofs. Generic schema validation and guarded live
installation are separate future operations.

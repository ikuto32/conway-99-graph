# Exact bound-claim registrar V11.2

This new source preserves failed V11 source
e853b9f882633c61f9a296f739c18edf7d7ab4fb63a8f01b0e007f09c6c5762a
and its failed author-controls01 receipts unchanged. V11 incorrectly demanded
boolean false in the reset report, whose pinned actual field is string NONE.
That was an adapter error, not a mathematical refutation. V11.2 changes only
this one exact predicate: report target_resolution is NONE, binding value false.

Underlying V10 cf6a12cee68ff206f6493953cd6ab8a07c1c8d04dbe1ad91d944694acb6d348d
remains byte-preserved and prior behavior is unchanged after the three declared
main changes and new constant/three exact helper functions are removed.

Only the same two immutable ROOT-verifier adapters are added: rooted8 divided
GF2 binding49f8/report410e with its exact necessary-model revision/dependency,
86434normalized rows/345736scalar components/651compatible profiles/zero
exclusions and calibration5positive15negative/fullcheck5positive16negative;
graph-only seed61 reset binding24bd/report23917 with exact four ordered objects,
39204scalar entries/lambda0mu3608/4934mismatches/exact stepzero settings,
source/reset hashes/no dependencies and calibration2positive15negative.

Both scope dictionaries require unrestricted_target false and target_resolution
NONE. Exact roles, revision/status/kind/basis/method, report and calibration
identities remain pinned. No generic ROOT permission, target promotion, rank
or scientific-warm outcome claim. No third conditional proof adapter here.

New author-helperV2 controls must pass, including explicitly corrupted false
reset-report value. They are preliminary only; separate ROOT/checkpoint
source/helper/protected-registration review is required before use. No live
ledger/index mutation or registrar main is authorized to this author.

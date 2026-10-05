# Proposed explicit batch04 checkpoint continuation

This is a preparation-only plan for root adoption and independent prebuild
review. It does not authorize execution merely by existing on disk. No build
may start before root's execution authorization and the fresh independent
continuation prebuild gate.

Preserve the original batch04 parent selection
`c37c5ce7b3be8b2629abde0d0a65a8f479f049953f04b232daebf99e8bffbfcc`,
launch plan `0db31ae7cf3756bf5a5d403829ec741e3a5b1f59c0f26600fab82f3f303c96b6`,
and interrupted launcher summary
`a9af4f12d632f62a1dd8607cb8b00289cf5aedfd6076af933899a93dc01b405f`.
All four original roots reached their120-second deadlines, exited1223, were
reaped, and had empty Jobs observed. Their original files are immutable.

Retain only the14 records in each original `checkpoint_014.json`:

- part00: `9e8962290834f7b4297f0271d893554761aa7201e2f3fc7d75b965a9f9c84f69`
- part01: `c762875f038cbc68310270fe93cf92aa5f0db107275ec30f3449255162b9b6a3`
- part02: `cbd77901c9a93d02062591a24c350ca9b523c96b102835f1108468912fd605ca`
- part03: `95c56dbd6a86f07c2678db0c99d2358475a76ff59d0f841c11f264f5bbd5ae3b`

Each original part also has an uncheckpointed fifteenth producer receipt with
exit0. Preserve those four extra outputs, without treating them as accepted
formula records. There were60 original producer invocations, not56. The new
allocation builds exactly the two saved pending IDs from each checkpoint in
their saved order. This means eight new producer invocations, including four
explicit repeats of uncheckpointed cases, and at most64 accepted formula
records after56 retained plus8 freshly completed. Total producer invocations
would then be68. No synthetic successful terminal summary is created for any
terminated original serial builder.

Use fresh paths `20261001_exact_eight_prefix64_batch04_continuation_cnfs_part00`
through `part03`, with attempts
`prefix64-batch04-continuation-part00-build-attempt01` through `part03`.
Use the unchanged serial builder and unchanged formula producer. Launch four
two-case selections via the frozen suspended-creation/Job backend; each gets a
separate120-second limit. Maximum concurrency4; total newly allocated work480
seconds; no single global120-second claim. Preserve every child file and all
cleanup receipts if any continuation is incomplete. No implicit retry.

The new adapter validates exactly this checkpoint continuation and reuses the
calibrated backend functions without modifying their code. The existing
engineering gate and a new independent source/plan gate are prerequisites.
After four complete new two-case summaries, a separately labelled consolidation
must authenticate the original56 checkpoint records, all60 old producer
receipts, the8 new receipts and every raw file. Its original parent64 list is
unchanged. The independent checker must reconstruct all64 actual formulas,
including the retained ones; source agreement is not mathematical approval.

Native preflight/search still requires fresh independent complete encoding and
object-calibration gates and root's already stated batch04 resource protocol.
This preparation does not execute native code, change the ledger or Git, or
satisfy the contingent batch05 proof prerequisite.

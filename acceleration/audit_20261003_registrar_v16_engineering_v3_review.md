# V16 engineering checker V3: source and array review only

Reviewer /root/checkpoint_audit authored the registrar subject. This paper
review does not independently approve that subject. Preserve prior V2 review
552b5177ddfa47d0563441bf2839ea30b4bc825ba312b56712989cfd93a4df6a
and unexecuted checker V2/source/plan unchanged.

Read the entire V3-versus-V2 source diff, complete V3 spec and whole new launch
plan. V3 source ea3b968bfd6b2589d15a0ecff228da5f7b77233eb324671732544035d32167d3;
spec0e6a5f01daba11b686433207d05ae951c098d711fdafd30690b759b91dc03aa9;
plan5ace534bf08a7d709a82bbbccc915d8e81353ba53b5466c90959d0db90b79bd3.

Exactly two source changes address the prior static veto: b.get is used only
for explicitly optional exact_certificate, while every other config key still
requires b[k]; the ordinary synthetic report's description now correctly names
the Checkpoint verifier. Literal original binding/report hashes and full subject
equality remain mandatory. No new generic missing-key or statement waiver is
introduced. The complete prior V2 reading plus this narrow diff exposed no
further static veto in the reviewed code paths.

The full plan starts supported Windows Job supervision before locked offline uv.
Outer180/worker150/shutdown20/internal-save20 include setup, evidence hashes,
helper/AST tests and three protected main copies. Exact author16525/terminalb2e,
source/spec/6525C4/dc079rank87 pins and current a4ledger/index8b observations are
declared. Fresh ownership/resources are still required by ROOT before dispatch.
The copied main projections stop at the authenticated final atomic-write
barrier; no live ledger/index or scientific mutation is in scope. ROOT must
inspect the actual outputs/terminal and separately review any actual registration.

No checker, controls or registrar main was executed by this review. No finite
engineering result, mathematical correctness, target resolution or availability
promotion is asserted. Independent execution/review is ROOT's next step.

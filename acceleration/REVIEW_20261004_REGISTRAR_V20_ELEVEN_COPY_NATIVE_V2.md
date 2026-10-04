# Native static review of the V2 eleven-copy checker

Whole-read the243-line Root checker `audit_20261004_registrar_v20_eleven_copy_v2.py`, SHA256 `244d7f8e0e06c6d1514a88bd3ac30d2a3af5e0fd074ce0170499d76853c5b822`; whole new spec `20ab66d04efbe45330b98c74d0cc9c118d1276510e08cd1cc249af9b3cd98e1f`; and whole literal plan `75b63756e82d09d14398f53aefc8a72b60732cf3cc6a0e6aeca3a9ffd6cbf504`. Compared the full V1-to-V2 source diff. This is source-only review, with no import, syntax test, checker/registrar invocation, mathematical replay, or ledger/index/Git mutation.

The V1 audit and veto remain preserved. No additional material static veto was found in this exact frozen V2 scope.

## Closing guards and failure semantics

The reserve check still requires more than20 seconds for normal work. `closing=True` permits consumption of the existing closing reserve only while the same deadline is unexpired; it constructs no new deadline and changes no550-second allocation. Digest now checks after its final hash work. Protected context checks are guarded before and after the raw ledger read, deadline-aware index hash and HEAD query. Success saves are guarded before and after JSON serialization and file closure.

Projection and controls are saved under ordinary reserve checks, then protected ledger/index/HEAD are checked before prospective PASS serialization and again after it. The final closing exception now reaches the failure handler, whose explicit `pass_summary_must_not_be_accepted` flag accompanies a nonzero worker. Finally restores only the process-local os.replace/sys.argv values; it no longer performs an unguarded hash or emits an exception outside the record path. Thus the observed closing criterion is checked after deadline-sensitive success work.

Failure output is deliberately best-effort and does not require remaining reserve. A failure.json, nonzero actual terminal, expired deadline or incomplete cleanup must veto acceptance even if a prospective PASS summary exists. The spec states this limitation. Guard sampling and supported containment do not prove a hard-real-time I/O or OS guarantee; a future authorized run still requires actual elapsed, genuine terminal and clean containment review. Initial argument parsing/output-directory creation/raw baseline parsing and inherited subject work are bounded by that command and checked before accepting success, not asserted to have instruction-level preemption.

## Exact maps and preserved source-specific barrier

V2 requires verification.artifact_hashes keys to equal the evidence IDs and requires the entire appended-artifact ID set to equal the union referenced by the eleven new claims. Together with duplicate artifact-ID rejection, duplicate evidence-path rejection, every path/hash comparison and LOCAL_ONLY availability, these close the two explicit V1 projection limitations for the frozen output.

The source-qualified unchanged V20 subject and exact eleven descriptor are unchanged. Its sole live-ledger replacement is still intercepted at the exact pending/live paths; the local prospective report is saved before the dedicated exception. All prior outputs stay under the fresh dest. The new digest optional closing argument is compatible with the subject's one-argument digest calls. No subject mathematical adapter, JSON/YAML acceptance branch or actual main command was bypassed.

The55 mutations retain their original stage order: each statement/Booleanrevision/status mutation reaches its NEW_CLAIM predicate, scope reaches NEW_SCOPE and dependencies reaches NEW_DEPENDENCIES. The extra map checks see pristine unchanged maps in these cases. V2 does not claim extra corrupt-map or simulated deadline controls were executed; source inspection of those branches is distinct from future actual-copy evidence.

## Literal plan and limits

The complete arrays are45 supervisor/29 child/23 worker words. Command and supervisor aliases are position-identical; the child is exactly the suffix after the sole '--'; the worker is exactly the script-and-options suffix of that child. The pinned593 Windows supervisor precedes locked offline UV with the declared research environment. The600/550/20save/20shutdown allocations, original eleven binding sequence,389 baseline and original subject remain unchanged. Only new checker/spec identity, output generation and preserved V1 review evidence alter applicability.

All19 small plan pins matched in this source-review observation and both proposed roots were absent. This observation is not launch admission: resources, scoped ownership and protected context must be freshly checked by the executor immediately before any separately authorized call. Bulk subject closure hashing remains inside the contained worker.

Root authored this engineering checker and will separately review an actual result; Native is the independent source reviewer. Shared YAML/schema validation and frozen V20 source qualification are disclosed common components. This source review approves no mathematics, target result, general corruption completeness, automatic live registration or native/scientific execution.

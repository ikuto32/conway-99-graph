# Independent restart-parser controls audit

The frozen candidate parser is calibrated within its exact stated text/profile
scope. This is an engineering result. It establishes neither validity of the
historical unrestricted proof prefix nor equisatisfiability of a substantial
derivative, and adds no mathematical exclusion.

The authoritative stage-one report is
`acceleration/results/20261002_drat_restart_controls_audit01/summary.json`,
SHA256 `0abe2311462f6821913231e42dbd0861c4fe3d2b75f2be1017af9c7e6fb34134`.
Its immutable invocation receipt is in the corresponding
`20261002_drat_restart_controls_audit_supervision01` directory. The verifier is
`/root/structural`; it did not produce the parser or import its implementation.
The report binds the exact C++, wrapper, specification, shared execution code,
native uv environment, pinned checker profile, compiled binary and build receipt.

`acceleration/audit_20261002_drat_restart_controls_v1.py` reconstructs the six
accepted fixtures with a separate tuple/Counter implementation, comparing the
complete deterministic DIMACS bytes, every retained proof byte and pivot order,
all recorded counters, and all assignments of the tiny variable universes. The
six malformed fixtures independently fail syntax checking and have no successful
parser summary. Eleven deliberately changed states, metadata and source
identities are rejected. These controls include preserved repeated occurrences,
single-copy deletion, ignored unit deletion, missing nonunit deletion, literal
normalization, an incomplete final tail and a complete record ending at EOF.

Eight actual complete DRAT replays use the separately frozen checker
authentication/replay path in
`acceleration/audit_20261002_policy_drat_core_v2.py`. The suffix on the derivative,
the concatenated proof on the original and the valid prefix alone are accepted.
The wrong suffix without the prefix, missing reasoning on the original, and
changed satisfiable original are rejected. Complete truth tables establish the
tiny original UNSAT and changed original SAT independently of the checker.

The supplied prefix `-2 0` already gives a sufficient proof of the four-clause
tiny UNSAT fixture; its derivative has an initial unit-propagation contradiction.
Consequently the supplied wrong suffix is accepted both after that sufficient
prefix and on that derivative. The audit records those actual outcomes rather
than treating the masked error as a checker failure. Observable negative proof
controls use the original without a valid prefix and the changed SAT original.
The original frozen producer/specification bytes remain preserved; this paragraph
records the deviation from their suggested negative-control expectation.

The compiled parser and checker/compiler/runtime remain trusted components.
Finite controls and source review do not constitute a formal proof of parser
correctness. A separate complete audit must reconstruct the substantial active
multiset and retained bytes before native use. A subsequent UNSAT result requires
independent replay of the entire combined trace against the original CNF and its
independently checked unrestricted encoding/coverage, regardless of successful
syntactic state extraction. A derivative SAT assignment requires independent
checking against the original CNF and complete SRG adjacency validator.

## Distinct streaming checker calibration

The substantial-artifact checker uses compact exact signed-32-bit byte keys in
an insertion-ordered Counter; it preserves keys whose multiplicity became zero.
It compares each emitted occurrence and each retained record without loading
either derivative file as a single byte array.

Its first calibration/source remains preserved as v1. Root review identified
that a broad caught `ValueError`/`KeyError` could let downstream mismatches stand
in for malformed-input rejection. The revised source
`acceleration/audit_20261002_drat_restart_artifact_v2.py` requires a distinct
`ParseSyntaxError` raised by lexical, literal-universe, zero-terminator or deletion
separator checks, and records the exact `INPUT_SYNTAX` rejection stage/reason.
The six malformed controls cannot pass solely by a derivative or summary mismatch.

The v2 calibration report is
`acceleration/results/20261002_drat_restart_stream_calibration02/summary.json`,
SHA256 `e4013fdff6233f36b603666fd846946e73b7b0a446e3c267b0b131b6fbb6f8f9`.
The frozen v2 source SHA256 is
`3693f1d77b60f9c095cd6afa0f6b67a9c048b4ad6336b9454f30ce459eb6156e`.
It checks six complete positive states, six explicit syntax-stage failures and
five derivative/prefix/profile/count corruptions. No substantial artifact was
checked during this calibration. The full audit has a separate invocation and
report, and its success must not be inferred from this engineering gate.

Independent source/profile/calibration review by `/root/checkpoint_audit` is
saved at
`acceleration/results/20261002_independent_review/restart_streaming_review01/summary.json`,
SHA256 `e8c8ae0c2ee9362da48bf610cf8c49f7da3fdf83f9ca55ae86b5d77e672f99b6`.
That review additionally used hand-derived duplicate/delete/restore/unit/missing
controls and explicit lexical/EOF corruptions. It did not duplicate the large
artifact replay or establish RAT/equisatisfiability.

## Complete substantial-artifact audit

The full syntactic-state audit subsequently passed at
`acceleration/results/20261002_drat_restart_artifact_audit01/summary.json`,
SHA256 `429026fd035e429ba8f16c0f92a02e9fdfab51cf2fb773321b112b95b3af2e89`.
Its exact command, source commit, complete input pins, Python version, calibration
outcomes and counter inventory are in that report. The supported Windows Job
invocation is preserved in
`acceleration/results/20261002_drat_restart_artifact_audit_supervision01`;
it completed in 90.390 observed seconds with exit zero, reaped children and an
observed empty job. The declared allocation was outer 1,200 / worker 1,140 seconds,
with orderly shutdown reserve. A live observation during the scan recorded a
443,052,032-byte working set; that sampled observation is not a peak-memory claim.

The independent Counter reconstructed all 4,136,454 original clause occurrences,
4,369,303 proof additions and 5,436,733 effective single-copy deletions. It kept
all 8,502,107 historically recorded unique keys, including keys at zero current
multiplicity, and compared every one of the 3,069,024 active derivative occurrences
in deterministic first-seen order. Every retained byte of the 346,616,796-byte
prefix was checked against the original 346,616,832-byte trace. Exactly 36 bytes
of its final unterminated record were dropped; no boundary LF was added. The
variable universe remains 1,186,500. This gate does not check historical RAT/RUP
validity or assert equisatisfiability; it remains an engineering verification of
an exact transformation, not a mathematical exclusion.

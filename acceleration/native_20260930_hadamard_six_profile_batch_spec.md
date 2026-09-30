# Gated native campaign for the remaining 54 six-exception profiles

Preparation only. No native preflight or research launch has been executed by
this preparation task. Root review and a fresh independent object calibration
gate are required before either mode. This is wave23, outside frozen wave22.

The immutable selection is
`results/20260930_hadamard_six_remaining_selection/selection.json`, SHA256
`64035c4d033c9b7d605f556bf69447780bb185ba7bd0fd0c7733ab9e1b0e741f`.
The complete formula batch is
`results/20260930_hadamard_six_remaining_cnfs/run01/summary.json`, SHA256
`a52427bce883858f43187d3916d172ac656afb6f6f60a7e0835ca5e8cb11be47`.
The independent encoding/selection gate is
`results/20260930_independent_review/hadamard_fiftyfour_profile_cnfs/summary.json`,
SHA256 `4fa50584776c9862e4e4c0286567b212b9a436c13a6cf0ebf0cd0b0ad751a6e5`.
Its exact status is `INDEPENDENT_HADAMARD_FIFTYFOUR_PROFILE_ENCODING_PASS`.

Use the frozen order of all 54 distinct string profile IDs. Omit only the already
attempted `rank4_00_profile_0000`; its omission is bookkeeping, not a new proof.
Every formula retains fourteen balanced domains of 150 choices and its six full
initial exceptional domains of 21 or 48 choices. There are 32 formulas with
2,334 selectors/10,048 variables/174,766 clauses and 22 with
2,388 selectors/10,156 variables/177,412 clauses. The wrapper checks each
individual selection/profile/model rather than assuming one dimension. The
scope is one literal six-exception profile's full prescribed integer Gram and
within-triplicate column caps. Cross-group caps and residual D are omitted.
No target automorphism is assumed. No assertion of whole-support coverage is
made by native outcomes alone.

Each profile gets at most one serial native CaDiCaL1.9.5 attempt: 60-second GNU
wall timeout, 1,000,000-conflict limit, 4GiB address-space, 10GiB individual
proof-file hard cap, zero core file, 5-second kill grace and 70-second outer
Windows guard. The whole campaign retains the prior 900-second accumulated
wrapped-call budget and requires a 70-second reserve before a new call. This
can stop before all 54 formulas. Transfer, hashing, process observation and
independent checker time are separate; no 900-second end-to-end guarantee.

The retained raw-trace soft budget remains 2GiB, counting both ext4 originals
and host copies. It is tested between calls; one call may overshoot this soft
budget within the individual 10GiB hard cap. No automatic file deletion. Require
21GiB host free space and 11GiB ext4 free space immediately before each call,
and verify the ext4 mount. Immediately preserve each complete proof on the host
and authenticate both raw copies. Missing complete trace identity, failed
process observation, or expired outer guard stops subsequent launches. Only
`ps -C cadical` is recorded; exit1 means no exact-named process.

Fail-closed preflight authenticates frozen source/tool/input pins, the exact
encoding gate above and a fresh gate with status
`INDEPENDENT_HADAMARD_FIFTYFOUR_PROFILE_OBJECT_CALIBRATION_PASS`. Both gates
must directly bind all 162 CNF/model/scope files, all 54 selected raw profiles,
the full initial local-domain files, selection, batch, raw support and producer
source/spec. The fresh object gate must additionally bind this new native
source/spec, all loaded local source dependencies (including the dynamically
used frozen balanced helper), the separate object checker and the same exact
encoding gate. The prior native CLI/ext4 calibrations and solver/checker binary
hashes are also checked. Per-profile raw CNF/model/scope hashes are rechecked
immediately before launch.

UNKNOWN and raw unchecked UNSAT are completed attempts, not exclusions.
Continue to the next never-attempted profile only if resources permit. UNSAT
requires a complete independent DRAT replay and separate scope/coverage review.
On SAT save the full native assignment, candidate decoded36x60 factor, all
1,296 Gram checks, 1,770 outside-column overlaps and 2,160 mixed-cap diagnostics;
invoke the separately frozen independent checker and stop the campaign pending
review regardless of its result. A failed producer decode does not prevent the
independent checker receiving the saved assignment. A Gram factor violating an
omitted cross-group cap remains a weaker partial candidate, never a target graph.

Output folders are named by the exact profile ID, with `main/solver.stdout.log`,
`main/parsed_model.json`, `main/decoded_Gram_factor.json` where available and
preserved proof/transfer records. Per-profile summary field `profile_id` is the
string identifier; the campaign uses `selected_profiles`, `profile_records`,
`unattempted_profiles`. Each completed attempt creates
`checkpoint_<profile_id>.json`. The immutable initial campaign manifest remains
authoritative across resumes.

Resumption uses a new output directory and explicit checkpoint path/SHA256.
Check exact input/source/gate/limit identity, the original manifest, the completed
selection prefix, every output hash, all ext4/host proofs, and accounting derived
from raw receipts. Completed UNKNOWN and UNSAT are skipped, never retried.
Reject omitted later/incomplete launch files, a preflight checkpoint, and any
SAT/trace-failure/process-uncertain stop. Preserve all completed records even
when resources stop the batch. A changed budget or post-SAT continuation needs
a separately reviewed protocol; this CLI cannot silently reset either.

Root-only CLI after the actual object gate is frozen:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/native_20260930_hadamard_six_profile_batch.py --preflight --out NEWDIR --encoding-gate acceleration/results/20260930_independent_review/hadamard_fiftyfour_profile_cnfs/summary.json --encoding-gate-sha256 4fa50584776c9862e4e4c0286567b212b9a436c13a6cf0ebf0cd0b0ad751a6e5 --object-gate PATH --object-gate-sha256 SHA --object-checker CHECKER.py
```

Replace `--preflight` with `--research` only after root authorizes launch. Optional
resume flags are `--resume-checkpoint PATH --resume-checkpoint-sha256 SHA`.
Independent SAT checker contract:
`sat --profile-id ID --encoding-gate PATH --encoding-gate-sha256 SHA --assignment JSON --native-output LOG [--decoded JSON] --out NEWDIR`.

Preparation validation is static parsing and read-only pin/shape review only.
Authenticated native/parser/ext4 helper reuse and the frozen producer decoder
are explicitly shared components, not independent discovery verification.

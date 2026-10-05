# Wave 29 explicit candidate inventory

This fresh source adapts the frozen wave28 inventory without changing it or either
wave29 seed. It performs metadata selection only. It does not run research,
replay proofs, certify recovery, approve mathematics, edit the registry, inspect
Git, stage files, or publish. Freeze this source/spec before its first execution.

Required CLI: `--checkpoint-sha256 SHA --ledger-sha256 SHA --out NEW`.
The checkpoint and immutable ledger paths are fixed under
`acceleration/results/20261001_resume/`; the caller supplies their exact hashes.
Require 300 claims, 293 VERIFIED, 3 CANDIDATE, 4 REFUTED, all CLEAR. Authenticate
the two exact registration transitions, initial20260930 then followup20261001,
whose six additions must all be VERIFIED/CLEAR. Their final bytes must equal
the supplied snapshot. The checkpoint's counts, new IDs and ledger hash must
agree. Never read current `CLAIMS.yaml`.

The source contains a literal allowlist for the first-next64 and batch02 builds,
receipts, native outputs and independent checks; suspended launcher preparations
and controls; reusable prefix selector and prebuild verification; GF3 witness
producer/reviewer; all792 uniform-Gram diagnostic producer/reviewer; the two
registrars and initial dry preparation; checkpoint/report/replay sources and
artifacts. Both original seed versions are included. The corrected actual proof
audit document replaces the original seed's nonexistent guessed spec. Named
source siblings are considered only at their exact `_spec.md` paths.

Batch03 and later work is outside this inventory. The reproduction guide, raw
recovery outputs and publication metadata audits will be later explicit
supplements after the recovery hashes are known. No recursive expansion from
references is allowed. Protected private process logs, PROMPT, tools/submodules,
secret-shaped paths and non-repository paths are refused before reads/hashes.

The prior wave28 catalog is authenticated at
`1dc941ddb899393f5d7d570f266cad6bc6205e64f3db13b4affe870f31de3586`.
Its authenticated catalog ancestry is used only for previous membership labels;
this is not a fresh public-availability or Git-blob check. Hash references outside
the allowlist are reported without opening their target files. Models and raw
initial-domain JSONs are hashed but not recursively parsed. Repository imports
are statically identified without executing those modules.

Reject selections over20,000 files or4GiB before payload hashing. Preserve a
partial inventory if the cooperative120-second limit is reached between files.
The limit is not an operating-system hard deadline for an individual hash or
JSON parse. Report all payloads over10MiB and existing recovery metadata; do not
claim that gzip bytes have been restored. Report every missing explicit path,
unselected dependency and conflicting historical hash. No missing report is
silently omitted. Failed runs preserve a new failure.json; no overwrite or retry.

Outputs in a fresh `twentyninth_candidate_inventory` directory are allowlist.json,
inventory.json and summary.json. The source contains no fixed runtime checkpoint
hash so that the actual frozen300-claim inputs can be supplied explicitly.
Initial validation is AST-only; actual execution requires root's frozen pins.

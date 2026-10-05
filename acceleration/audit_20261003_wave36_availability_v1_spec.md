# Wave36 independent availability-only checker v1

Scope: frozen 337 material claims at SHA-256
`8f8d39f5e4fcaf8cb8ec2681e0a9ec795439c80e2c8bd1d8a5903ef1087d342d`,
preserving every claim/verification/target field and all artifact records from
the 334-claim baseline `4b7470f6...`. No mathematical replay or target promotion.
Producer and live-ledger mutation belong to `/root`; this checker is read-only
and imports no publication producer or registrar.

Before a producer outcome, run `calibration --seconds 100 --out ...` under the
supported supervisor with 120 seconds outer. Success requires exact frozen
ledger/manifests, positive synthetic transitions, strict stage-specific corrupt
transition controls, literal tiny multi-part gzip controls, and immutable Git
archive reads of both new stage/finalizer anchors. Synthetic direct hash tables
exercise logic only and do not establish real publication. Complete raw member
count is calculated from the 334-to-337 ledger artifact difference, not guessed.

After calibration and root's separate publication producer, run `full` with
exact producer receipt/source/after hashes, producer supervision directory and
pre-output calibration report/hash. Proposed outer 300/internal 270 seconds,
20 seconds internal shutdown reserve, based prior ~9-second immutable audit and
1.75-second fresh six-input recovery. All hashing/transfers/children share the
one deadline. No mathematical solver is launched.

Full success requires exact immutable commit
`43175e0a96ed4abbf6b03e16b67adff6f6f40b20`, public GitHub repo/commit observation,
reachable remote branch, all 1,836 allowlist records and 24 finalizer records
(checked overlap), anchors and new ledger artifacts, separate Git archive hashes,
all six raw paths explicitly queried and absent, three pinned lossless packages
and all 32 compressed parts streamed to complete raw identities, 242,396,575 raw
bytes / 7,306,880 gzip bytes, prior independent full recovery records and the
fresh RESTORED_MISSING six-input receipt. No original raw overwrite. No whole
historical transitive closure or platform binary availability inference.

Old byte-recovery/reader algorithms are disclosed shared components. The prior
contained archive-pipe deadlock and its independently calibrated stdout-drain
correction remain preserved. The Wave36 policy-index EOL failure, exact byte
attribute correction, index02 and late replay document are authenticated as
evidence, not silently treated as mathematical verification.

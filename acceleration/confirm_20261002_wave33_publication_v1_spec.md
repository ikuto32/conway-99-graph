# Wave33 publication identity confirmation v1

Question: are the exact new wave33 artifact records available at the public,
immutable pushed commit? This command changes availability and retrieval metadata
only; the 324 claims, target, prior artifacts and verification records must remain
unchanged. No new mathematical result is produced.

Inputs are the explicitly supplied ledger hash and remote commit, the frozen
stage03 manifest, two literal-model package manifests, and their prior independent
fresh recovery reports. Every staged member and all 25 gzip parts must equal the
published Git blob. Decode and hash all five raw models (184,494,332 bytes), with
per-segment offset/length/hash checks. An unavailable unlisted artifact retains
its prior state; neither a hash nor a local file suffices for PUBLIC promotion.

Run through run_compute_command.py with 300 seconds, 10 seconds shutdown reserve,
and a 270-second internal deadline. Setup, transfers, hashing, decoding, validation
and child Git/gh processes share the command deadline. No automatic retry; retain
any failed receipt and use a new version for changed behavior. Atomic ledger
replacement occurs only after exact identity, public-hash schema validation and
concurrent-edit checks. Independent transition review must check unchanged claims,
prior artifacts, immutable bytes, recovery identities and corrupt promotions.

Limitations: remote advertising plus local immutable-object identity is not a
second network clean-clone recovery. Byte publication does not replay proof,
approve changed source, establish general coverage, or resolve Conway-99.

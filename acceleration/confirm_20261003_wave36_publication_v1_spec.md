# Wave36 immutable availability producer V1

New source, preserving the completed wave35 producer. Root owns this metadata
mutation; a separate agent/checker must independently inspect the resulting raw
before/after ledger, public Git bytes, lossless input streams and strict controls.
This source imports no independent availability checker or discovery algorithm.

Pin current337 ledger8f8d39...,334 baseline4b7470..., publication commit43175e0...
and remote branch/public-repository observations. Authenticate1836 allowlist
members83e995... plus24 exact late records/final receiptde677...; overlaps must
have identical hashes/sizes. Query every needed immutable Git blob, including
all six intentionally absent raw paths. The old five input models and new243
coupling control must recover exactly from three independently checked packages,
32parts/242396575rawbytes/7306880compressedbytes. Verify ordered segment hashes,
complete raw hashes and literal sizes; local compressed bytes must equal published
Git bytes before local decoding is accepted. A hash-only identity is insufficient.

Promote only artifact IDs newly added after the334 baseline when their exact
direct or package-backed bytes are authenticated. Require zero unverified new
artifacts; preserve every material claim, verification record, target field and
prior artifact field. This is availability metadata only, not mathematical
replay, a clean second network clone or a target resolution. Emit raw before/
after snapshots and a receipt before atomic ledger replacement. Refuse concurrent
ledger modification, changed remote HEAD, missing/changed payload or failed schema.

Allocation300outer270worker20reserve, based prior24.3-second producer and9.36-second
independent335-blob check; this payload has roughly1850 records/159MB plus32parts.
All hashes, Git child work, decoding and schema checks share the invocation.
Preserve failure/partial records, no retry or extension; new invocation requires
reassessment. Independent archive/scalar byte checking must be calibrated and
must not import this producer. No historical ledger bytes are rewritten.

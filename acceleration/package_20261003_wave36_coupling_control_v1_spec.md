# Wave36 coupling-control lossless payload v1

This engineering command packages exactly one original independent calibration
artifact, preserving its bytes. It clones the chunking/compression/record algorithm
of `package_20261002_wave33_models_v1.py`; the manifest schema remains
`WAVE33_LITERAL_MODELS_LOSSLESS_V1` for the unchanged recovery interface. This
version additionally authenticates the originating audit and its raw input pin.

Frozen population: `acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/srg243_all_primary_coupling_records.json`,
57,902,243 bytes, SHA256
`447d922b1a0ad28b3b7d459f84b8c02e55da7b9cc8da8615a5e882b6482d4919`.
The independent audit `summary.json` in the same directory has SHA256
`e7631851f9cc5716c9d8a1bf5b30f9a4644d8e2170f116d1bb30378fbeb16d70`
and records that exact raw pin. No recursive population or other raw file is
included. The artifact exceeds the publication staging bound of 50 MiB.

Before launch, freeze this source/spec. Use the existing pinned
`acceleration/native_budget_env_v1` uv.lock with `uv run --locked --offline`.
The Linux-contained `run_compute_command.py` allocation is 180 seconds, its
producer has 150 seconds, and the producer preserves a 20-second reserve before
each part. The allocation covers hashing, audit input authentication, compression
and producer round-trip checks. The smaller one-file population is 57.9 MB;
previous full lossless packaging handled a substantially larger finite population.
No native scientific solver runs and no computation deadline is extended.

Acceptance requires one record with exactly seven contiguous parts: six
8,388,608-byte chunks and a 7,570,595-byte tail. Gzip level 9 has mtime zero and
an empty stored filename. Each gzip part is decompressed and compared literally
with the original chunk by the producer; per-part compressed and raw hashes,
raw offsets, sizes, and the complete original SHA256/size are retained in the
manifest and `record_00.json`. Partial files remain preserved if a command fails.
The original file is never rewritten or removed. No numerical threshold applies.

Independent recovery is a separate required invocation of unchanged
`recover_20261001_twentyninth_raw_artifacts.py` with the exact completed manifest
hash, together with an independently authored full streaming/fresh-original
comparison where practical. This producer's checks cannot approve its own
recovery claim. No PUBLIC availability, fresh mathematical check, scientific
claim promotion, Git staging, or source execution-gate change follows from the
packaging run. Availability remains LOCAL_ONLY pending separate publication and
recovery checks. Existing weight60 scientific freezer bytes remain unchanged.

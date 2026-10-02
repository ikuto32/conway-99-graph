# Batch05 lossless direct replay publication v2

Version 1 stopped after successful per-record receipts when Windows denied atomic
replacement of progress.json while the supervisor concurrently read it. Preserve
all v1 source, receipts and partial payloads. Version 2 adds only explicit reuse
of those immutable receipts: authenticate the frozen v1 invocation, old inventory,
receipt identities and whole recovered bytes against the current frozen inventory.
Reuse does not imply independent approval. New source/spec and v1 source/spec are
included in the v2 population. Do not pass supervisor --progress-json on Windows;
observe immutable receipts or read progress between updates instead. No automatic
resume, retry or changed raw artifact is accepted.

This engineering invocation creates no mathematical result. The frozen population
is the union of direct authenticated inputs of the exact batch05 native manifest
and independent proof audit, plus those summaries and this source/spec, pinned
uv environment and old independent recovery implementation. It includes exactly
64 distinct ordered cases and all 64 proofs, CNFs, models and scopes. Historical
gate transitive inventories are not recursively copied. Native platform binaries
remain separately identified LOCAL_ONLY; source/build provenance is retained.

Freeze authenticates the exact saved proof gate and producer case identities,
then hashes every declared file. Originals are opened for read only. Packaging
uses the wave29 lossless algorithm: deterministic gzip (empty filename, mtime 0,
level 9), raw chunks at most 8 MiB, compressed parts at most 10 MiB. Existing
model gzip payloads may be reused only with pinned raw/package/payload identities.
Empty raw files receive one valid empty gzip part. No artifact is overwritten.

Producer acceptance requires exact part sizes and hashes, contiguous offsets,
bounded decompression, whole raw sizes/hashes and literal comparison of every
recovered byte with each original. These producer checks are not independent
approval. The output remains a LOCAL_ONLY candidate until another implementation
recovers every declared artifact, tests deliberately corrupted parts/manifests,
and binds its report to exact manifest/source/payload hashes. Actual PUBLIC
availability also requires that the payloads and recovery instructions are
published. Schema/engineering checks do not establish proof soundness or coverage.

Freeze and representative controls run separately under supported local
run_compute_command.py containment. Hashing, compression, verification and I/O
share each invocation's CommandDeadline. Allocate the actual packaging command
from observed representative proof/CNF/model compressor rates and frozen byte
counts, allowing for per-file overhead, verification, and orderly shutdown.
Producer allocation must be at most 1700 seconds so the first mandatory 1800s
review is not silently skipped. This is an engineering allocation, not a new
build/solver cap. Keep 32 GiB free on the host; one sequential compressor uses
8 MiB raw buffers plus bounded decompression and metadata.

Each successfully packaged raw file has an immutable records/raw_NNNN.json
receipt. Progress includes the complete-record count and deadline state. Stops
preserve all outputs and failure.json; incomplete work is not completed within
the allocated budget. There is no automatic retry/resume. A separately authorized
invocation may authenticate completed receipts and reuse their exact payloads
with a newly recorded inventory/version, rather than overwrite failed evidence.

Locked setup/execution uses UV_PROJECT_ENVIRONMENT=build/research-venv and
uv run --locked. The entire calculation is a local Windows Python process tree
inside suspended Windows Job containment; do not supervise wsl.exe from Windows.
The unchanged historical recovery program accepts records path/sha256/bytes/parts
and is retained as a separately authored checking path, with current supervision.

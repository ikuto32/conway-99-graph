# Independent Wave37 byte-recovery protocol V1

This new checker is authored by `/root/native_driver`, separate from ROOT's
Wave37 package producer. It imports no producer, old restorer, model builder,
or model-audit implementation. It shares Python's standard-library gzip/zlib,
hashlib and filesystem primitives and the pinned current deadline helper.
It establishes byte recovery only, not model semantics or public availability.

Frozen population: precisely the two manifest records in
`acceleration/results/20261003_wave37_rooted8_package01/manifest.json`, SHA256
`ea48c30dfa68fe70bad17edbfd3697d8a2dcf28f9ab24b63d0d66895e7eb9b14`.
They total 124,864,726 raw bytes and 16 gzip parts totaling 4,416,662 compressed
bytes. The exact independent model report, packager source and every raw member
identity are independently pinned by this checker's source. The report binds
the raw model and the independent reconstruction separately. A manifest hash
is an identity check; the actual local files must all be available and read.

Before the complete restoration, calibrate two known literal positive fixture
records with four gzip parts and twelve exact-stage rejection controls:
offset, part hash, whole hash, original hash, path traversal, duplicate part,
duplicate raw path, gzip hash, overlong decompression, invalid gzip stream,
literal original-byte corruption and existing destination. Each mutation and
partial failed restoration is preserved. The whole-hash and part-length
controls explicitly bypass only the fixture's preliminary original hash, so
the downstream intended diagnostic is reached. Production never bypasses it.

Production acceptance requires a fresh destination; safe distinct paths;
contiguous part offsets; exact aggregate counts; every actual compressed
length and hash; streaming gzip reads of at most one MiB, with an immediate
eight-MiB-per-part bound; every raw part length/hash; both complete recovered
lengths/hashes; a second independent restored-file hash; and a separate
blockwise comparison of every recovered byte against both immutable original
files, including matching EOF. No sampled checks. Partial outputs on veto
remain evidence and cannot be accepted as a complete recovery.

Supported allocation: 120-second Linux supervisor, 100-second Python worker,
20-second worker reserve, with all preprocessing, controls, hashing and
restoration sharing this invocation deadline. The recent independently checked
1.127-GB batch05 byte recovery took about four seconds; this 125-MB population
with small finite controls justifies the shorter allocation without assuming
a speed guarantee. No solver, GPU worker, scientific search, retry or deadline
extension is authorized. New output root:
`acceleration/results/20261003_independent_review/wave37_recovery01`;
fresh recovered subtree `recovered/` preserves both original relative paths.

Use unchanged `run_compute_command.py` inside Ubuntu-24.04 and the locked
`acceleration/native_budget_env_v1` uv environment. Exact source/spec hashes
are frozen before invocation and recorded in the outcome. Report actual
contained exit/empty-group observations separately. Outcome PASS approves
only these exact byte artifacts locally; immutable publication is separately
required for a PUBLIC claim. No mathematical replay or claim-ledger mutation.

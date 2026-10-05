# Transport of two saved direct-cell UNKNOWN traces

Selection is exactly the saved host `main/proof.drat` in `20260930_direct_cell_standalone_native_pilot` (403,055,631 bytes, SHA256 dc7fcd07a7628e41d9f2a0b437ca442b7c7c86191bc3869fe2409e240c4e262a) and `20260930_direct_cell_count_coupled_native_pilot` (745,721,856 bytes, SHA256 c82cdf7810730aedf163175e13b59a3a3a54fc56f3f0b1940f7e63e7eedf36d7). Both runs are UNKNOWN. Complete transport means all saved host bytes, not a complete UNSAT proof. No proof checker or native solver is invoked.

Freeze source, recovery helper and this protocol before running. Allocate 120 cooperative seconds and at most 512 MiB peak working set. Process standalone then at_least_seven, in original byte order, with 8 MiB raw parts and gzip parts at most 10 MiB. Use deterministic gzip level 1, empty filename, mtime 0; this level is selected before execution to keep the 1,148,777,487-byte transport within the bounded allocation. Record Python and zlib versions. Never remove or modify either raw host file, an earlier result, a ledger, index, or repository commit. A failure preserves its output and checkpoints; it is not a completed package.

Authenticate frozen run summaries, original tool manifests, historical transfer identities and every saved run-output hash, and rehash the host originals before and after packaging. Copy exact summary and manifest bytes into each package directory for provenance. Do not require or touch the original ext4 path: its current presence may differ from the historical successful transfer. The manifest explicitly reports that current ext4 availability was not checked by this packager. Outcome and later ext4 observations belong to the separate independent run audit.

Directly pin the independent standalone UNKNOWN audit `7a97722d...`, coupled UNKNOWN audit `677cd12a...`, and append-only availability clarification `322f0166...` (full hashes in source). Those records report both original ext4 paths absent at the later observation. Their host-only availability limitation is retained; this packager performs no new ext4 availability check and makes no claim that either original ext4 copy survives.

Every compressed part is immediately decompressed and compared literally with its source chunk. Record index, contiguous raw offset, raw and compressed lengths and hashes. Then independently traverse the complete package through the separate recovery helper, checking every part and whole hash and comparing streamed recovered bytes directly to the saved host file. Positive controls cover two-part recovery, actual restore output and deterministic gzip bytes. Deliberate changes to whole/part hashes, lengths, offsets, indices, order, missing parts, compressed identity, directory containment, scope flags and gzip CRC must be rejected. These are byte-transport controls, not mathematical verification.

Freeze command:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/package_20260930_direct_cell_unknown_trace_package.py --out acceleration/results/20260930_direct_cell_unknown_trace_package`

Use the locked research environment. A manifest-authenticated fresh-checkout check needs only package parts:

`uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/recover_20260930_direct_cell_unknown_trace_package.py --manifest PATH --manifest-sha256 SHA --verify-only`

Replace `--verify-only` with `--out NEW_DIRECTORY` to restore both saved UNKNOWN streams without their original host files. The helper refuses an existing output directory and never overwrites a raw trace. Public availability remains LOCAL_ONLY until separately confirmed by publication. No completeness, proof validity, target existence/nonexistence, or solver-performance conclusion follows from this package.

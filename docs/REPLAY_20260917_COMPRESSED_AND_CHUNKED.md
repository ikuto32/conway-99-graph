# Recover the compressed checkpoint and chunked moment matrices

Run from the existing repository root after obtaining the committed manifest
and every companion or part file it names. These commands verify local bytes;
they do not claim that publication or network retrieval has already occurred.
Use the pinned environment:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked --cache-dir .uv-cache-20260917
```

The binary-span checkpoint's original28,528,356 bytes are stored in the
2,334,554-byte gzip companion. Existing `restore_compressed_artifacts.py`
restores its canonical path and checks the recorded hash; an identical
already-present raw file is accepted, while differing bytes are refused:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/restore_compressed_artifacts.py acceleration/results/20260917_two_coordinate_binary_span/compressed_artifacts.json
```

For a separate streaming zlib audit into a fresh directory, without consulting
or modifying the original raw checkpoint:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/audit_compressed_artifact_manifest.py acceleration/results/20260917_two_coordinate_binary_span/compressed_artifacts.json --destination build/replay_binary_checkpoint_fresh --out build/replay_binary_checkpoint_audit_fresh.json
```

The old `audit_compressed_artifacts.py` intentionally requires its historical
three-file manifest. It was not modified. The new generic wrapper accepts any
nonempty schema1 file list and reuses that frozen independent streaming zlib
decoder, with positive and corruptCRC/truncation/hash/size/trailing-member/path
controls. Its audit is independent of the producer gzip restore path, but
shares zlib and the historical independent decoder; it is not a second
independent decompression library.

The unfiltered four-coordinate matrix uses five ordered raw byte parts,
total34,329,990 bytes. Restore to its canonical manifest-relative path on a
fresh checkout where the rawNPZ is absent:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/restore_chunked_artifacts.py acceleration/results/20260917_four_matching_moments/chunk_manifest.json --report build/four_moment_restore_fresh.json
```

The separately scoped matching-filtered matrix uses four parts, total
27,081,591 bytes, with a different full-file hash:

```powershell
uv run --locked --offline --cache-dir .uv-cache-20260917 python -B acceleration/restore_chunked_artifacts.py acceleration/results/20260917_four_matching_filtered_moments/chunk_manifest.json --report build/four_filtered_moment_restore_fresh.json
```

To test either matrix when its canonical rawNPZ already exists, add
`--destination build/SOME_FRESH_DIRECTORY`. The destination/report and all
source/target paths must resolve inside this repository. The chunk restorer
refuses every existing target, even one with identical bytes. It verifies
each part's hash and size before and during ordered streaming concatenation,
then verifies the whole-file hash and size before atomic exclusive publication.
It never edits availability metadata or deletes raw evidence. Failed staging
files are retained with a `.chunk-replay-` prefix and are not published as
the final artifact.

Actual local checks from this research session are recorded under
`acceleration/results/20260917_artifact_replay/`: gzip audit, ten chunk
positive/corrupt controls, and fresh five-part restoration. The controls
import the chunk restorer and therefore are producer engineering checks.
The separate mathematical model audit previously checked concatenated input
bytes independently. Byte recovery and schema acceptance are not mathematical
verification, and this tooling promotes no research claim.

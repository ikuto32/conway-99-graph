"""Independently recover gzip companions using streaming zlib, not restore code."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import zlib


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for data in iter(lambda: stream.read(65536), b""):
            h.update(data)
    return h.hexdigest()


def decode(chunks, sink, expected_size, expected_hash):
    decoder = zlib.decompressobj(31)
    h, size = hashlib.sha256(), 0
    for chunk in chunks:
        data = decoder.decompress(chunk)
        sink(data)
        size += len(data)
        h.update(data)
    data = decoder.flush()
    sink(data)
    size += len(data)
    h.update(data)
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError("Require exactly one complete gzip member without trailing bytes")
    if size != expected_size or h.hexdigest() != expected_hash:
        raise ValueError("Recovered size/hash mismatch")
    return size, h.hexdigest()


def safe_relative(root, name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or ":" in str(name):
        raise ValueError("Unsafe artifact path")
    result = (root / path).resolve()
    result.relative_to(root)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path)
    p.add_argument("--destination", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = args.destination.resolve()
    destination.relative_to(root)
    if destination.exists() or args.out.exists():
        raise ValueError("Preserve existing evidence; choose fresh output paths")
    manifest_hash = sha(args.manifest)
    manifest = json.loads(args.manifest.read_bytes())
    if manifest["schema_version"] != 1 or len(manifest["files"]) != 3:
        raise ValueError("Expected the frozen three-file companion manifest")
    fixture = b"independent gzip recovery control\n" * 3
    compressed = gzip.compress(fixture, mtime=0)  # Fixture generation only.
    fixture_hash = hashlib.sha256(fixture).hexdigest()
    controls = []
    decode([compressed], lambda data: None, len(fixture), fixture_hash)
    controls.append(dict(name="known_positive", outcome="PASS"))
    corrupt = bytearray(compressed)
    corrupt[-8] ^= 1  # corrupt the stored CRC, preserve deflate bytes
    for name, blob, size, expected in (
        ("corrupt_crc", bytes(corrupt), len(fixture), fixture_hash),
        ("truncated_footer", compressed[:-1], len(fixture), fixture_hash),
        ("wrong_hash", compressed, len(fixture), "0"*64),
        ("wrong_size", compressed, len(fixture)+1, fixture_hash),
        ("trailing_bytes", compressed+b"x", len(fixture), fixture_hash),
    ):
        try:
            decode([blob], lambda data: None, size, expected)
        except (ValueError, zlib.error) as exc:
            controls.append(dict(name=name, outcome="REJECT", reason=str(exc)))
        else:
            raise ValueError("Accepted corrupted fixture: " + name)
    for path in ("../escape", "Z:/other/escape"):
        try:
            safe_relative(destination, path)
        except ValueError:
            controls.append(dict(name="unsafe_path:" + path, outcome="REJECT"))
        else:
            raise ValueError("Accepted unsafe fixture")
    destination.mkdir()
    records = []
    for row in manifest["files"]:
        source = safe_relative(root, row["compressed_path"])
        target = safe_relative(destination, row["path"])
        if source.stat().st_size != row["compressed_size_bytes"] or sha(source) != row["compressed_sha256"]:
            raise ValueError("Compressed size/hash mismatch")
        target.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as input_stream, target.open("xb") as output_stream:
            size, recovered_hash = decode(iter(lambda: input_stream.read(65536), b""), output_stream.write, row["size_bytes"], row["sha256"])
        if sha(target) != recovered_hash or sha(source) != row["compressed_sha256"]:
            raise ValueError("Output/input changed during recovery")
        records.append(dict(path=row["path"], compressed_path=row["compressed_path"], compressed_sha256=sha(source), compressed_size_bytes=source.stat().st_size,
                            recovered_path=target.relative_to(root).as_posix(), recovered_sha256=recovered_hash, recovered_size_bytes=size, outcome="PASS"))
    if sha(args.manifest) != manifest_hash:
        raise ValueError("Manifest changed during audit")
    commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    report = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=commit,
                  source_dirty=bool(subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip()),
                  command_argv=[sys.executable, *sys.argv], working_directory=str(Path.cwd()),
                  python=platform.python_version(), zlib_compile_version=zlib.ZLIB_VERSION, zlib_runtime_version=zlib.ZLIB_RUNTIME_VERSION,
                  status="INDEPENDENT_THREE_GZIP_RECOVERIES_PASS", compressed_files=3,
                  total_compressed_bytes=sum(r["compressed_size_bytes"] for r in records), total_recovered_bytes=sum(r["recovered_size_bytes"] for r in records),
                  inputs_sha256={str(args.manifest).replace("\\", "/"): manifest_hash,
                                 "acceleration/audit_compressed_artifacts.py": sha(Path(__file__)),
                                 "acceleration/restore_compressed_artifacts.py": sha(root / "acceleration/restore_compressed_artifacts.py"),
                                 "uv.lock": sha(root / "uv.lock")},
                  records=records, controls=controls, originals_overwritten=False,
                  code_review=dict(producer_imported_or_executed=False,
                                   inspected="restore_compressed_artifacts.py", observations=[
                                       "Resolves both source/target paths and rejects escape outside repository.",
                                       "Checks compressed SHA-256 before gzip decompression, then recovered size/SHA-256 before writing.",
                                       "Existing raw file must be byte-identical; differing data is not overwritten. New files use exclusive creation.",
                                       "Does not separately check compressed_size_bytes, but compressed SHA-256 binds the entire bytes; this independent audit checks both.",
                                       "Producer recovery buffers entire raw object; largest manifest file is 124,683,908 bytes. Independent audit streams output."]),
                  shared_trusted_components=["Python hashlib/SHA-256", "zlib underlying gzip implementation", "same raw manifest and compressed bytes"],
                  limitations=["Engineering byte-recovery check only; no mathematical verification or claim promotion.",
                               "Recovery implementation is separate from producer but shares the underlying zlib decompression library.",
                               "Companions were read from the current workspace and pinned by hash; publication/network retrieval was not tested.",
                               "Original raw files were not consulted or overwritten; agreement is against the manifest's recorded raw hashes."],
                  mathematical_claim_promotion=False, target_resolution=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps(dict(status=report["status"], files=3, bytes=report["total_recovered_bytes"], controls=len(controls))))


if __name__ == "__main__":
    main()

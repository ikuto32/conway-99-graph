"""Create exact compressed public companions; does not verify mathematical proof."""
from datetime import datetime, timezone
from hashlib import sha256
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def main():
    proof = Path("acceleration/results/20260930_rook_sat_pilot/main/proof.drat")
    destination = proof.with_suffix(proof.suffix + ".gz")
    receipt = proof.parent / "compressed_proof.json"
    assert not destination.exists() and not receipt.exists()
    assert digest(proof) == "6378d40355ff016c3ac5a7434c98116b2c835390f0422539471b19322788aaaa"
    with proof.open("rb") as source, destination.open("xb") as target:
        with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as archive:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                archive.write(block)
    decoded = gzip.decompress(destination.read_bytes())
    assert sha256(decoded).hexdigest() == digest(proof)
    with receipt.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump({"timestamp": datetime.now(timezone.utc).isoformat(),
                   "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                   "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
                   "source": {"path": proof.as_posix(), "sha256": digest(proof), "bytes": proof.stat().st_size},
                   "compressed": {"path": destination.as_posix(), "sha256": digest(destination), "bytes": destination.stat().st_size},
                   "script_sha256": digest(Path(__file__)), "uv_lock_sha256": digest(Path("uv.lock")),
                   "roundtrip_exact": True, "compression_mtime": 0,
                   "mathematical_verification": False, "independent_proof_replay_pending": True,
                   "scope": "Byte-preserving compression only; no SAT or target-level claim."}, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"compressed_bytes": destination.stat().st_size, "sha256": digest(destination)}))


if __name__ == "__main__":
    main()

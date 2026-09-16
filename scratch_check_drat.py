"""Run the pinned local drat-trim binary and record a hash-bound audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time


CHECKER = Path("tools/drat-trim/drat-trim.exe")
CHECKER_SOURCE = Path("tools/drat-trim/drat-trim.c")
CHECKER_REPO = Path("tools/drat-trim")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def source_commit():
    return subprocess.check_output(
        ["git", "-C", str(CHECKER_REPO), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cnf", required=True)
    parser.add_argument("--proof", required=True)
    parser.add_argument("--meta", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=40000)
    args = parser.parse_args()
    cnf = Path(args.cnf)
    proof = Path(args.proof)
    meta_path = Path(args.meta)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    cnf_hash = sha256(cnf)
    proof_hash = sha256(proof)
    assert cnf_hash == meta["cnf_sha256"]
    assert proof_hash == meta["proof_sha256"]
    started = time.monotonic()
    completed = subprocess.run(
        [str(CHECKER), str(cnf), str(proof), "-t", str(args.timeout)],
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = time.monotonic() - started
    transcript = completed.stdout + completed.stderr
    verified = completed.returncode == 0 and "s VERIFIED" in transcript
    result = {
        "status": "DRAT_VERIFIED" if verified else "DRAT_NOT_VERIFIED",
        "ok": verified,
        "cnf": str(cnf),
        "cnf_sha256": cnf_hash,
        "proof": str(proof),
        "proof_sha256": proof_hash,
        "producer_metadata": str(meta_path),
        "producer_metadata_sha256": sha256(meta_path),
        "checker": str(CHECKER),
        "checker_sha256": sha256(CHECKER),
        "checker_source": str(CHECKER_SOURCE),
        "checker_source_sha256": sha256(CHECKER_SOURCE),
        "checker_upstream_commit": source_commit(),
        "checker_local_patch": (
            "Windows-only gettimeofday/getc_unlocked compatibility; proof logic unchanged"
        ),
        "return_code": completed.returncode,
        "elapsed_seconds": round(elapsed, 6),
        "transcript": transcript,
    }
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True), flush=True)
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

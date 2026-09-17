"""Extract hash-bound checker inputs exclusively from one published Git commit.

No untracked/local artifact fallback. Direct runtime dependencies are the paths
actually hash-bound by the saved independent checker reports. Recursive manifest
dependencies are recorded separately, since not all are read by those checkers.
"""
import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import time


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--commit", required=True)
    p.add_argument("--destination", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--max-files", type=int, default=2000)
    p.add_argument("--max-bytes", type=int, default=300_000_000)
    p.add_argument("--resume", action="store_true", help="Reuse only existing extracted files whose bytes match this commit")
    p.add_argument("--include-transitive-provenance", action="store_true", help="Also expand historical producer inventories that frozen checkers only hash, not execute")
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = args.destination.resolve()
    destination.relative_to(root)
    if destination.exists() and not args.resume:
        raise ValueError("Preserve prior extraction; destination must not exist")
    args.out.mkdir(parents=True, exist_ok=True)
    protocol = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=args.commit,
                    question="Can the published fresh16 checker and triangle checker obtain their exact hash-bound input bytes without inherited local caches?",
                    scope="Two saved independent checker runtime input inventories, then recursive inputs_sha256 provenance closure; no producer rerun",
                    selection_rule="All inputs_sha256 entries of batch_raw_review.json, baseline_and_matrix.json, and triangle_matching/summary.json at the pinned commit",
                    success="Every required path is a Git blob at this commit and exactly matches recorded SHA-256; subsequent isolated fresh16 arithmetic replay passes",
                    falsification="Any absent Git blob, digest mismatch, unsafe path, or failed isolated checker",
                    numerical_thresholds=None, numerical_thresholds_reason="Exact byte identities and rational arithmetic; no floating-point acceptance threshold",
                    resource_limits=dict(max_files=args.max_files, max_bytes=args.max_bytes),
                    include_unexecuted_transitive_provenance=args.include_transitive_provenance,
                    command_argv=[sys.executable, *sys.argv], working_directory=str(Path.cwd()),
                    python=platform.python_version(), helper_sha256=sha(Path(__file__).read_bytes()),
                    limitations=["Git object extraction confirms commit contents, not availability of public network retrieval.", "Python interpreter and pinned third-party packages are trusted execution environment, not repository artifacts.", "Saved checker inventories may omit undeclared runtime reads; isolated execution tests that risk only for actually executed commands."])
    write_new(args.out / "protocol.json", protocol)
    started = time.monotonic()
    def git(*argv):
        return subprocess.run(["git", "-C", str(root), *argv], capture_output=True, check=True).stdout
    actual = git("rev-parse", args.commit).decode().strip()
    if actual != args.commit:
        raise ValueError("Use the full immutable commit id")
    tree = {}
    for line in git("ls-tree", "-r", "-z", args.commit).split(b"\0"):
        if line:
            meta, name = line.split(b"\t", 1)
            mode, typ, oid = meta.decode().split()
            tree[name.decode()] = dict(mode=mode, type=typ, oid=oid)
    seeds = {
        "fresh16": "acceleration/results/20260917_independent_review/batch_raw_review.json",
        "baseline": "acceleration/results/20260917_independent_review/baseline_and_matrix.json",
        "triangle": "acceleration/results/20260917_independent_review/triangle_matching/summary.json",
    }
    queue, expectations, origins = deque(), {}, {}
    absolute_references = []
    transitive_references = []
    direct = {name: [] for name in seeds}
    def enqueue(path, expected, origin):
        normalized = str(path).replace("\\", "/")
        original_prefix = root.as_posix() + "/"
        if normalized.lower().startswith(original_prefix.lower()):
            mapped = normalized[len(original_prefix):]
            absolute_references.append(dict(original=normalized, mapped_git_path=mapped, origin=origin,
                                            note="Only extraction lookup is mapped; raw bytes are not rewritten and checker portability is not assumed"))
            normalized = mapped
        pp = PurePosixPath(normalized)
        if pp.is_absolute() or ".." in pp.parts or ":" in normalized:
            raise ValueError("Nonrelative dependency path: " + normalized)
        origins.setdefault(normalized, []).append(origin)
        if expected:
            expectations.setdefault(normalized, set()).add(expected)
        if normalized not in records and normalized not in queue:
            queue.append(normalized)
    records = {}
    for group, path in seeds.items():
        content = git("show", f"{args.commit}:{path}")
        report = json.loads(content)
        enqueue(path, sha(content), "inventory:" + group)
        for name, expected in report["inputs_sha256"].items():
            name = name.replace("\\", "/")
            direct[group].append(name)
            enqueue(name, expected, "direct:" + group)
    enqueue("pyproject.toml", None, "locked_environment")
    enqueue("uv.lock", None, "locked_environment")
    enqueue("acceleration/audit_20260917_matrix_controls.py", None, "baseline_source")
    total = 0
    destination.mkdir(exist_ok=args.resume)
    while queue:
        name = queue.popleft()
        if len(records) >= args.max_files:
            raise ValueError("File budget reached; extraction incomplete")
        entry = tree.get(name)
        if entry is None or entry["type"] != "blob" or entry["mode"] == "120000":
            records[name] = dict(availability="MISSING", reason="Not a regular file blob in the pinned commit", git_entry=entry)
            continue
        content = git("show", f"{args.commit}:{name}")
        total += len(content)
        if total > args.max_bytes:
            raise ValueError("Byte budget reached; extraction incomplete")
        output = destination / name
        output.resolve().relative_to(destination)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            if not args.resume or output.read_bytes() != content:
                raise ValueError("Existing extraction bytes disagree with immutable commit: " + name)
        else:
            with output.open("xb") as handle:
                handle.write(content)
        records[name] = dict(availability="EXTRACTED_FROM_COMMIT", git_blob=entry["oid"], sha256=sha(content), size=len(content))
        if len(records) % 25 == 0:
            print(json.dumps(dict(event="EXTRACTION_PROGRESS", unique_paths=len(records), bytes=total, pending=len(queue))), flush=True)
        if name.endswith(".json"):
            value = json.loads(content)
            def recurse(value):
                if isinstance(value, dict):
                    for field, child in value.items():
                        if field == "inputs_sha256" and isinstance(child, dict):
                            for dependency, expected in child.items():
                                transitive_references.append(dict(parent=name, dependency=dependency, sha256=expected))
                                if args.include_transitive_provenance:
                                    enqueue(dependency, expected, "transitive:" + name)
                        else:
                            recurse(child)
                elif isinstance(value, list):
                    for child in value:
                        recurse(child)
            recurse(value)
    for name, record in records.items():
        expected = sorted(expectations.get(name, []))
        record.update(expected_sha256=expected, origins=sorted(set(origins[name])))
        record["hashes_match"] = record.get("sha256") in expected if expected else None
        if len(expected) > 1:
            record["hashes_match"] = False
    groups = {}
    for group, names in direct.items():
        missing = [n for n in names if records[n]["availability"] == "MISSING"]
        mismatched = [n for n in names if records[n]["availability"] != "MISSING" and records[n]["hashes_match"] is False]
        groups[group] = dict(population="Unique paths in saved checker runtime hash inventory", required_paths=len(set(names)), missing=missing, mismatched=mismatched, closure_available=not missing and not mismatched)
    report = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=args.commit,
                  extraction_root=str(destination), protocol_sha256=sha((args.out / "protocol.json").read_bytes()),
                  direct_runtime_inventories=groups, total_unique_paths=len(records), extracted_bytes=total,
                  missing_paths=[n for n, r in records.items() if r["availability"] == "MISSING"],
                  absolute_original_workspace_references=absolute_references,
                  unexecuted_transitive_provenance_references=transitive_references,
                  provenance_scope="Actual saved checker runtime hash inventories; deeper producer-history reruns are not asserted" if not args.include_transitive_provenance else "Recursively expanded producer-history input inventories",
                  mismatched_paths=[n for n, r in records.items() if r["availability"] != "MISSING" and r["hashes_match"] is False],
                  files=records, elapsed_seconds=time.monotonic()-started,
                  mathematical_replay_performed=False, target_resolution=False)
    write_new(args.out / "extraction_manifest.json", report)
    print(json.dumps({k: report[k] for k in ("direct_runtime_inventories", "total_unique_paths", "extracted_bytes", "missing_paths", "mismatched_paths", "elapsed_seconds")}, indent=2))


if __name__ == "__main__":
    main()

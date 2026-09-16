"""Bounded native CLI checks; full enumeration semantics are audited separately."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "acceleration/build/overlap_matching_neighbors.exe"
SOURCE = ROOT / "acceleration/overlap_matching_neighbors.rs"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    edges = json.loads(args.candidate.read_text())["overlap_edges_outer_zero_based"]
    require(len(edges) == 168 and edges == sorted(edges), "Expected canonical168-edge seed")
    text = "C99OVERLAPS1 1\n" + "\n".join(f"{u} {v}" for u,v in edges) + "\n"
    inp = args.out / "input.txt"
    inp.write_text(text, encoding="ascii")
    output = args.out / "all.json"
    started = time.perf_counter()
    run = subprocess.run([str(NATIVE), str(inp), str(output)], capture_output=True, text=True, timeout=60)
    require(run.returncode == 0, run.stderr)
    elapsed = time.perf_counter() - started
    data = json.loads(output.read_text())
    require(data["status"] == "COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION", "Unexpected status")
    require(data["coordinate_count"] == 14 and data["raw_including_initial"] == 84560 and data["unchanged_count"] == 14,
            "Unexpected raw count")
    require(data["legal_count"] == len(data["moves"]) == len(data["overlap_candidates"]), "Alignment mismatch")
    require(data["legal_count"] + data["cap_rejected_count"] + 14 == 84560, "Count partition mismatch")
    seed = tuple(map(tuple, edges))
    signatures = [tuple(map(tuple, row)) for row in data["overlap_candidates"]]
    require(len(signatures) == len(set(signatures)) and seed not in signatures, "Duplicate or unchanged candidate")
    cases = [
        ("wrong_magic", text.replace("C99OVERLAPS1", "BAD", 1), "all"),
        ("wrong_count", text.replace("C99OVERLAPS1 1", "C99OVERLAPS1 2", 1), "all"),
        ("truncated", " ".join(text.split()[:-1]), "all"),
        ("trailing", text + "0\n", "all"),
        ("duplicate", "C99OVERLAPS1 1\n" + "\n".join(f"{u} {v}" for u,v in [edges[1], *edges[1:]]) + "\n", "all"),
        ("reversed", "C99OVERLAPS1 1\n" + f"{edges[0][1]} {edges[0][0]}\n" + "\n".join(f"{u} {v}" for u,v in edges[1:]), "all"),
        ("range", "C99OVERLAPS1 1\n0 84\n" + "\n".join(f"{u} {v}" for u,v in edges[1:]), "all"),
        ("nonoverlap", "C99OVERLAPS1 1\n0 1\n" + "\n".join(f"{u} {v}" for u,v in edges[1:]), "all"),
    ]
    cases.extend(("selector_" + str(i), text, mode) for i,mode in enumerate(["3", "7:0", "0:2", "-1:0", "0:0:0", "cross", "a:0"]))
    negative = []
    for name, contents, mode in cases:
        bad = args.out / (name + ".txt")
        bad.write_text(contents, encoding="ascii")
        target = args.out / (name + "_unexpected.json")
        proc = subprocess.run([str(NATIVE), str(bad), str(target), mode], capture_output=True, text=True, timeout=10)
        require(proc.returncode != 0 and not target.exists(), "Negative control accepted: " + name)
        negative.append(dict(name=name, rejected=True, returncode=proc.returncode, reason=proc.stderr.strip()))
    old_sha = digest(output)
    proc = subprocess.run([str(NATIVE), str(inp), str(output)], capture_output=True, text=True, timeout=10)
    require(proc.returncode != 0 and digest(output) == old_sha, "Existing output overwritten")
    negative.append(dict(name="existing_output", rejected=True, returncode=proc.returncode, reason=proc.stderr.strip()))
    histogram = Counter(str(move["changed_edges"]) for move in data["moves"])
    multiple = sum(len(move["alternating_cycles"]) > 1 for move in data["moves"])
    report = dict(status="WHOLE_MATCHING_NATIVE_CLI_AND_ALIGNMENT_QA_PASS", inputs_sha256={key(p):digest(p) for p in
                  [args.candidate, SOURCE, NATIVE, Path(__file__), inp]}, outputs_sha256={key(output):digest(output)},
                  coordinate_count=data["coordinate_count"], raw_including_initial=data["raw_including_initial"],
                  unchanged_count=data["unchanged_count"], legal_count=data["legal_count"],
                  cap_rejected_count=data["cap_rejected_count"], native_elapsed_seconds=data["elapsed_seconds"],
                  subprocess_elapsed_seconds=elapsed, changed_edges_histogram=dict(sorted(histogram.items())),
                  candidates_with_multiple_cycles=multiple, by_class=data["by_class"], negative_controls=negative,
                  native_stderr=run.stderr.strip(), independent_graph_or_completeness_audit_performed=False,
                  scope="Native generation plus input rejection/count/alignment/duplicate checks; full99 semantics and6040 exhaustive sets require the separate independent Python audit.")
    (args.out / "qa.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k:report[k] for k in ["status","raw_including_initial","legal_count","cap_rejected_count","native_elapsed_seconds","changed_edges_histogram","candidates_with_multiple_cycles"]}))


if __name__ == "__main__":
    main()

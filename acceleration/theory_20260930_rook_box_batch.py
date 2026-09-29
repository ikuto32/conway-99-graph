"""Generate boxed candidates from every accepted support cut in one checkpoint."""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def save(p, value):
    with Path(p).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def key(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    old = json.loads(args.checkpoint.read_text())["ordered_cuts"]
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "input_hashes": {key(p): digest(p) for p in (Path(__file__), args.checkpoint, ROOT / "acceleration/theory_20260930_rook_gram_box_cut.py", ROOT / "uv.lock")},
        "question": "How many literals can the same exact Gram vectors release under independent Boolean maximization?",
        "selection_rule": "Every accepted ordered support cut in the exact input checkpoint, in its recorded order; no candidate omitted.",
        "resource_limits": {"cut_count": len(old), "per_producer_seconds": 30},
        "scope": "Candidate shorter necessary clauses for one fixed central factor star; pending fresh independent checking.",
        "status": "CANDIDATE", "solver_launched": False})
    rows = []
    for number, item in enumerate(old):
        certificate = ROOT / item["certificate"]
        audit = ROOT / item["audit"]
        assert digest(certificate) == item["certificate_sha256"] and digest(audit) == item["audit_sha256"]
        prior = json.loads(audit.read_text())
        matching_graph_paths = sorted(path for path, h in prior["inputs_sha256"].items() if h == prior["graph_sha256"])
        assert matching_graph_paths
        graph = ROOT / matching_graph_paths[0]
        assert digest(graph) == prior["graph_sha256"]
        out = args.out / f"cut_{number:02d}"
        command = [sys.executable, "acceleration/theory_20260930_rook_gram_box_cut.py", "--certificate", key(certificate),
                   "--prior-audit", key(audit), "--out", key(out)]
        process = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
        (args.out / f"cut_{number:02d}.stdout.log").write_bytes(process.stdout)
        (args.out / f"cut_{number:02d}.stderr.log").write_bytes(process.stderr)
        assert process.returncode == 0, process.stderr.decode(errors="replace")
        boxed = json.loads((out / "certificate.json").read_text())
        rows.append({"index": number, "parent_certificate": key(certificate), "parent_certificate_sha256": digest(certificate),
                     "parent_audit": key(audit), "parent_audit_sha256": digest(audit),
                     "graph": key(graph), "graph_sha256": digest(graph), "certificate": key(out / "certificate.json"),
                     "certificate_sha256": digest(out / "certificate.json"), "clause": key(out / "nogood.clause"),
                     "parent_literals": boxed["parent_clause_length"], "box_literals": boxed["nogood_clause_length"],
                     "exact_box_upper_bound": boxed["global_boolean_box_upper_bound"],
                     "producer_command": command, "producer_exit_code": process.returncode})
        print(json.dumps({"index": number, "parent_literals": rows[-1]["parent_literals"], "box_literals": rows[-1]["box_literals"]}), flush=True)
    save(args.out / "index.json", {"status": "CANDIDATE", "independent_review_pending": True,
         "unit": "accepted support-cut certificate from the frozen input checkpoint", "selected": len(old),
         "completed_productions": len(rows), "records": rows, "solver_launched": False})


if __name__ == "__main__":
    main()

"""Materialize one reviewed Gram nogood without changing base CNF variable IDs."""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def save(p, data):
    with p.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--independent-audit", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    certificate = json.loads(args.certificate.read_text())
    assert digest(args.base) == certificate["base_cnf_sha256"]
    clause = certificate["nogood_clause"]
    assert isinstance(clause, list) and all(type(x) is int and x for x in clause)
    assert len(set(map(abs, clause))) == len(clause)
    inputs = [Path(__file__), Path("acceleration/theory_20260930_rook_lazy_cut_spec.md"),
              args.base, args.certificate, args.independent_audit, Path("uv.lock")]
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
         "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
         "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
         "input_hashes": {p.as_posix(): digest(p) for p in inputs},
         "scope": "Mechanical append only; independent audit acceptance must be assessed by orchestration before running this producer.",
         "question": "Does the current local model survive one independently sound Gram-support nogood?",
         "resource_limits": {"solver_invocations": 1, "wall_seconds": 300, "conflicts": 1000000},
         "status": "CANDIDATE", "independent_review_pending": True})
    target = args.out / "instance.cnf"
    with args.base.open("rb") as source, target.open("xb") as output:
        header = source.readline().decode("ascii").split()
        assert len(header) == 4 and header[:2] == ["p", "cnf"]
        variables, old_count = map(int, header[2:])
        assert all(abs(lit) <= variables for lit in clause)
        output.write(f"p cnf {variables} {old_count + 1}\n".encode("ascii"))
        for block in iter(lambda: source.read(1024 * 1024), b""):
            output.write(block)
        output.write((" ".join(map(str, clause)) + " 0\n").encode("ascii"))
    save(args.out / "append_record.json", {"base_sha256": digest(args.base),
         "base_variables": variables, "base_clause_count": old_count, "ordered_appended_clauses": [clause],
         "certificate_sha256": digest(args.certificate), "independent_audit_sha256": digest(args.independent_audit),
         "augmented_variables": variables, "augmented_clause_count": old_count + 1,
         "augmented_sha256": digest(target), "augmented_bytes": target.stat().st_size,
         "reconstruction": "Preserve base body bytes, increment only the DIMACS header clause count, then append each listed clause as ASCII space-separated integers followed by space-zero-newline."})
    print(json.dumps({"variables": variables, "clauses": old_count + 1, "sha256": digest(target)}))


if __name__ == "__main__":
    main()

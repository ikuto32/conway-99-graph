"""Invoke the separately authored box checker for every frozen batch candidate."""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def save(p, data):
    with Path(p).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.index.read_text())
    assert data["selected"] == data["completed_productions"] == len(data["records"])
    records = []
    for row in data["records"]:
        certificate = ROOT / row["certificate"]
        assert digest(certificate) == row["certificate_sha256"]
        out = certificate.parent / "independent_box_nogood.json"
        command = [sys.executable, "acceleration/audit_20260930_gram_box_nogood_v1.py",
            "--graph", row["graph"], "--certificate", row["certificate"], "--clause", row["clause"],
            "--expected-certificate-sha256", row["certificate_sha256"],
            "--model", "acceleration/results/20260930_rook_free_internal_sat/model.json",
            "--cnf", "acceleration/results/20260930_rook_free_internal_sat/instance.cnf",
            "--encoding-audit", "acceleration/results/20260930_rook_free_internal_sat/independent_cnf_encoding.json",
            "--encoding-audit-sha256", "a74e821f70680187e0ee14fb956d51928e6aa9517acc1bc0186448b32c985ba0",
            "--out", out.relative_to(ROOT).as_posix()]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=120)
        (certificate.parent / "checker.stdout.log").write_bytes(result.stdout)
        (certificate.parent / "checker.stderr.log").write_bytes(result.stderr)
        assert result.returncode == 0, result.stderr.decode(errors="replace")
        audit = json.loads(out.read_text())
        assert audit["status"] == "INDEPENDENT_TARGET_GRAM_BOX_NOGOOD_PASS"
        assert audit["certificate_sha256"] == row["certificate_sha256"]
        records.append({"certificate": row["certificate"], "certificate_sha256": row["certificate_sha256"],
                        "audit": out.relative_to(ROOT).as_posix(), "audit_sha256": digest(out), "clause": audit["verified_clause"]})
        print(json.dumps({"index": row["index"], "status": audit["status"], "literals": len(audit["verified_clause"])}), flush=True)
    save(args.index.parent / "accepted_checkpoint.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
         "status": "CHECKER_RECORDS_PENDING_INDEPENDENT_AGGREGATE_BINDING", "input_index_sha256": digest(args.index),
         "driver_sha256": digest(Path(__file__)), "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
         "ordered_cuts": records, "selected": len(records), "checker_passes": len(records), "sat_launched": False})


if __name__ == "__main__":
    main()

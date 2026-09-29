"""Preserve the checker's initial label-order failure and exact correction."""
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "acceleration/results/20260930_independent_review/unrestricted_star_matching/label_order_correction.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    model_path = ROOT/"acceleration/results/20260930_unrestricted_full99_cnf/model.json"
    labels = json.loads(model_path.read_bytes())["outer_labels"]
    original = [list(p) for p in combinations(range(14), 2) if p[0]//2 != p[1]//2]
    corrected = sorted(original, key=lambda p: (p[0]//2, p[1]//2, p[0]%2, p[1]%2))
    differences = [i for i,(a,b) in enumerate(zip(labels,original)) if a != b]
    assert differences and corrected == labels and set(map(tuple,labels)) == set(map(tuple,original))
    files = [model_path, ROOT/"acceleration/audit_20260930_unrestricted_star_matching.py",
             ROOT/"acceleration/audit_20260930_unrestricted_star_matching_v2.py",
             ROOT/"acceleration/results/20260930_independent_review/unrestricted_star_matching/summary.json",
             Path(__file__)]
    report = {
        "status": "CHECKER_LABEL_ORDER_CORRECTION_WITH_PRESERVED_ORIGINAL_SOURCE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "command": [sys.executable,*sys.argv], "working_directory": str(Path.cwd()), "python": platform.python_version(),
        "original_command": ["uv","run","--locked","--offline","--cache-dir",".uv-cache-20260917","python","-B","acceleration/audit_20260930_unrestricted_star_matching.py"],
        "original_result": "Exit1: ValueError: independent label order, before any sampled raw graph was checked or a verdict saved",
        "original_stdout_stderr_artifact": None,
        "original_stdout_stderr_null_reason": "Original traceback was visible in the tool transcript; no byte-for-byte standalone log was saved",
        "original_source_preserved": "acceleration/audit_20260930_unrestricted_star_matching.py",
        "corrected_source": "acceleration/audit_20260930_unrestricted_star_matching_v2.py",
        "fault": "Checker assigned outer vertices in ordinary symbol-pair lexicographic order; the saved model uses root-coordinate-pair order with its four sign choices.",
        "first_differing_outer_index": differences[0], "old_assumed_label": original[differences[0]], "actual_label": labels[differences[0]],
        "changed_index_count": len(differences), "label_sets_equal": True,
        "correction": "Independently sort the same combinatorial label set by coordinate pair and two endpoint signs; verify every raw fixed/free matrix entry against that derived scaffold before graph checks.",
        "fresh_falsification_of_old_order": True, "new_order_matches_all84labels": corrected == labels,
        "subsequent_status": "INDEPENDENT_UNRESTRICTED_ONE_STAR_MATCHING_REDUNDANCY_PASS",
        "mathematical_statement_changed": False, "theorem_refuted": False,
        "inputs_sha256": {p.relative_to(ROOT).as_posix():digest(p) for p in files},
        "limitations": ["This is a checker metadata correction, not a mathematical discovery or independent promotion beyond the separate bound audit."]
    }
    with OUT.open("x",encoding="utf-8") as stream: json.dump(report,stream,indent=2);stream.write("\n")
    print(json.dumps({"path":OUT.relative_to(ROOT).as_posix(),"sha256":digest(OUT)}))


if __name__ == "__main__":
    main()

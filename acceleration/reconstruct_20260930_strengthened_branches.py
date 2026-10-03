"""Reconstruct saved composed CNFs using only public bytes and stdlib; no solver."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open("rb") as stream:
        result = sha256()
        for block in iter(lambda: stream.read(1048576), b""):
            result.update(block)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    recipes = json.loads(args.recipes.read_bytes())
    if recipes["schema"] != "EQUALITY_STRENGTHENED_FOUR_BRANCH_RECIPES_V1":
        raise ValueError("unknown recipe schema")
    args.out.mkdir(parents=True, exist_ok=False)
    records = []
    for row in recipes["branches"]:
        sources = [(ROOT / row["base_cnf"], row["base_cnf_sha256"]),
                   (ROOT / row["equality_suffix"], row["equality_suffix_sha256"]),
                   (ROOT / row["original_branch_suffix"], row["original_branch_suffix_sha256"])]
        for path, expected in sources:
            if digest(path) != expected:
                raise ValueError("changed source bytes: " + str(path))
        output = args.out / (row["branch"] + ".cnf")
        with output.open("xb") as target, sources[0][0].open("rb") as base:
            if base.readline() != b"p cnf 1186500 4136454\n":
                raise ValueError("unexpected base header")
            target.write(f"p cnf {row['variables']} {row['clauses']}\n".encode("ascii"))
            shutil.copyfileobj(base, target, 1048576)
            for path, _ in sources[1:]:
                with path.open("rb") as suffix:
                    shutil.copyfileobj(suffix, target, 1048576)
        actual = digest(output)
        if actual != row["cnf_sha256"]:
            raise ValueError("reconstruction differs from saved exact CNF")
        records.append({"branch": row["branch"], "output": str(output), "sha256": actual,
                        "bytes": output.stat().st_size})
    report = {"timestamp": datetime.now(timezone.utc).isoformat(),
              "status": "EXACT_SAVED_RECIPE_RECONSTRUCTION_HASH_MATCH", "solver_calls": 0,
              "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()),
              "source_sha256": digest(Path(__file__)), "recipes_sha256": digest(args.recipes),
              "outputs": records, "independent_verification": False,
              "limitations": ["Byte reconstruction only; semantic verification remains in the independent input gates."]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "reconstructed_files": len(records), "solver_calls": 0}))


if __name__ == "__main__":
    main()

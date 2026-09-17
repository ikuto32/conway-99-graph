"""Exact small-graph calibration for a separately written normalization lemma."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/THEORY_20260917_ROOT_SCAFFOLD.md"


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj):
    with path.open("x", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def require(test, reason):
    if not test:
        raise ValueError(reason)


def exact_matrix(A, degree):
    n = len(A)
    require(all(len(row) == n for row in A), "square matrix")
    require(all(type(v) is int and v in (0, 1) for row in A for v in row), "binary integer entries")
    require(all(A[i][i] == 0 for i in range(n)), "zero diagonal")
    require(all(A[i][j] == A[j][i] for i in range(n) for j in range(n)), "symmetry")
    for i in range(n):
        for j in range(n):
            product_entry = sum(A[i][t]*A[t][j] for t in range(n))
            expected = (degree-2)*int(i == j) - A[i][j] + 2
            require(product_entry == expected, f"matrix equation at({i},{j}): {product_entry}!={expected}")
    return True


def normalized_map(A, root, ordered_pairs, flips):
    degree = sum(A[root])
    symbol_vertices = [pair[side ^ flips[g]] for g, pair in enumerate(ordered_pairs) for side in (0, 1)]
    inner = set(symbol_vertices)
    require(len(inner) == degree and inner == {v for v in range(len(A)) if A[root][v]}, "root-neighbor inventory")
    inverse_inner = {v: i for i, v in enumerate(symbol_vertices)}
    label_to_outside = {}
    for v in range(len(A)):
        if v == root or v in inner:
            continue
        pair = tuple(sorted(inverse_inner[u] for u in inner if A[v][u]))
        require(len(pair) == 2 and pair[0]//2 != pair[1]//2, "outside nonmatched pair")
        require(pair not in label_to_outside, "outside pair injective")
        label_to_outside[pair] = v
    labels = [(2*g+s, 2*h+t) for g, h in combinations(range(degree//2), 2) for s, t in product((0, 1), repeat=2)]
    require(set(label_to_outside) == set(labels), "outside pair surjective")
    new_to_old = [root] + symbol_vertices + [label_to_outside[label] for label in labels]
    return new_to_old, labels


def check_normalization(A, new_to_old, degree):
    n = len(A)
    require(sorted(new_to_old) == list(range(n)), "full vertex bijection")
    B = [[A[new_to_old[i]][new_to_old[j]] for j in range(n)] for i in range(n)]
    scaffold = {(0, r) for r in range(1, degree+1)}
    scaffold |= {(2*g+1, 2*g+2) for g in range(degree//2)}
    labels = [(a, b) for a in range(degree) for b in range(a+1, degree) if a//2 != b//2]
    # Distinct ordering implementation for checking the producing map.
    labels.sort(key=lambda pair: (pair[0]//2, pair[1]//2, pair[0]%2, pair[1]%2))
    for v, pair in enumerate(labels, degree+1):
        scaffold |= {(s+1, v) for s in pair}
    require(all(B[a][b] == 1 for a, b in scaffold), "positive scaffold incidence")
    require(all(sum(1 for a, b in scaffold if v in (a, b)) == degree for v in range(degree+1)), "root-inner degree saturation")
    require(all({u for u in range(degree+1) if B[v][u]} == {a for a, b in scaffold if b == v and a <= degree}
                for v in range(degree+1, n)), "exact outer root-label neighborhoods")
    exact_matrix(B, degree)
    return dict(scaffold_edges=[list(e) for e in sorted(scaffold)], scaffold_edge_count=len(scaffold),
                root_inner_saturated=True, outer_edges_not_fixed_by_normalization=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    require(not (args.out / "manifest.json").exists(), "fresh output directory")
    source_commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    inputs = {"acceleration/theory_20260917_root_scaffold.py": digest(__file__),
              "docs/THEORY_20260917_ROOT_SCAFFOLD.md": digest(DOCUMENT), "uv.lock": digest(ROOT / "uv.lock")}
    manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=source_commit,
                    command_argv=[sys.executable, *sys.argv], working_directory=str(Path.cwd()), python=platform.python_version(),
                    claim_id="C-ROOT-SCAFFOLD-NORMALIZATION", claim_revision=1,
                    question="Calibrate every-root normalization bookkeeping on known srg(9,4,1,2), separate from the99vertex derivation",
                    selection_rule="Every9 rook root and every2! times2^2 ordering/orientation; all18edge removals and18nonedge additions",
                    exact_acceptance="Integer matrix equation and full vertex/scaffold bijections; everydeliberate corruption rejected",
                    runtime_limit="Finite fixture population only; no target search", numerical_tolerance=None,
                    numerical_tolerance_reason="Exact arithmetic only", inputs_sha256=inputs,
                    mathematical_lemma_status="CANDIDATE", independent_derivation_review=False)
    save(args.out / "manifest.json", manifest)
    A = [[int(i != j and (i//3 == j//3 or i%3 == j%3)) for j in range(9)] for i in range(9)]
    exact_matrix(A, 4)
    fixture_path = args.out / "rook9_adjacency.json"
    save(fixture_path, dict(graph="3x3rook", parameters=[9, 4, 1, 2], equation="B^2=2I-B+2J", adjacency=A))
    records = []
    for root in range(9):
        inner = [u for u in range(9) if A[root][u]]
        pairs = [pair for pair in combinations(inner, 2) if A[pair[0]][pair[1]]]
        require(len(pairs) == 2 and sorted(v for pair in pairs for v in pair) == inner, "induced2K2")
        for ordered in permutations(pairs):
            for flips in product((0, 1), repeat=2):
                mapping, labels = normalized_map(A, root, ordered, flips)
                checked = check_normalization(A, mapping, 4)
                require(checked["scaffold_edge_count"] == 14, "rook scaffold edge count")
                records.append(dict(root=root, ordered_inner_pairs=ordered, pair_flips=flips,
                                    new_to_old_vertices=mapping, outside_root_symbol_labels=labels,
                                    result="PASS", **checked))
    require(len(records) == 72, "full fixture root/order/orientation population")
    corrupted = []
    for a, b in combinations(range(9), 2):
        bad = deepcopy(A)
        bad[a][b] = bad[b][a] = 1-A[a][b]
        try:
            exact_matrix(bad, 4)
        except ValueError as exc:
            corrupted.append(dict(kind="delete_edge" if A[a][b] else "add_nonedge", changed_pair=[a, b], outcome="REJECT", reason=str(exc)))
        else:
            raise ValueError("Corrupt symmetric edge toggle accepted")
    special = []
    asymmetric = deepcopy(A); asymmetric[0][1] = 0
    loop = deepcopy(A); loop[0][0] = 1
    nonbinary = deepcopy(A); nonbinary[0][1] = nonbinary[1][0] = 2
    switched = deepcopy(A)
    for a, b in ((0, 1), (3, 4), (0, 4), (1, 3)):
        switched[a][b] = switched[b][a] = 1-switched[a][b]
    require(all(sum(row) == 4 for row in switched), "two-switch degree-preserving control")
    for name, bad in (("asymmetry", asymmetric), ("diagonal_loop", loop), ("nonbinary", nonbinary), ("degree_preserving_two_switch", switched)):
        try:
            exact_matrix(bad, 4)
        except ValueError as exc:
            special.append(dict(name=name, outcome="REJECT", reason=str(exc)))
        else:
            raise ValueError("Corrupt matrix accepted: " + name)
    for name in ("duplicate_label_image", "wrong_outside_pair_label"):
        mapping = records[0]["new_to_old_vertices"][:]
        if name == "duplicate_label_image":
            mapping[8] = mapping[7]
        else:
            mapping[5], mapping[6] = mapping[6], mapping[5]
        try:
            check_normalization(A, mapping, 4)
        except ValueError as exc:
            special.append(dict(name=name, outcome="REJECT", reason=str(exc)))
        else:
            raise ValueError("Corrupt labeling accepted: " + name)
    require(all(digest(ROOT / name) == expected for name, expected in inputs.items()), "Inputs changed")
    summary = dict(timestamp=datetime.now(timezone.utc).isoformat(), status="CANDIDATE_ROOT_NORMALIZATION_CALIBRATION_PASS",
                   manifest_sha256=digest(args.out / "manifest.json"), fixture_sha256=digest(fixture_path),
                   fixture_parameters=[9, 4, 1, 2], roots_checked=9, ordered_oriented_labelings_checked=72,
                   records=records, symmetric_corruption_controls=corrupted, other_corruption_controls=special,
                   mathematical_lemma_status="CANDIDATE", independent_derivation_review=False,
                   limitations=["Calibration fixture is9vertices, not a target99vertex graph", "Executable controls do not establish the general lemma", "No claim of novelty or existence/nonexistence"],
                   target_resolution=False)
    save(args.out / "summary.json", summary)
    print(json.dumps(dict(status=summary["status"], roots=9, labelings=72, symmetric_corruptions=len(corrupted), other_corruptions=len(special))))


if __name__ == "__main__":
    main()

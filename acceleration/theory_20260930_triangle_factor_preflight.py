"""Exact cheap linear falsifiers and alternative encoding census, no SAT solver."""
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import gzip
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "external_conway99_research"
OUT = ROOT / "acceleration/results/20260930_triangle_factor_preflight"
SPEC = Path(__file__).with_name("theory_20260930_triangle_factor_preflight_spec.md")
PIN = "85e705cc6c2a14d123120c93a847e30aaab1789e"


def require(x, reason):
    if not x:
        raise ValueError(reason)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def prime_feasible(a, b, p):
    work = [[x % p for x in row] + [v % p] for row, v in zip(a, b)]
    transform = [[int(i == j) for j in range(len(a))] for i in range(len(a))]
    rank = 0
    for col in range(len(a[0])):
        found = next((r for r in range(rank, len(a)) if work[r][col]), None)
        if found is None:
            continue
        work[rank], work[found] = work[found], work[rank]
        transform[rank], transform[found] = transform[found], transform[rank]
        inv = pow(work[rank][col], -1, p)
        work[rank] = [v * inv % p for v in work[rank]]
        transform[rank] = [v * inv % p for v in transform[rank]]
        for row in range(len(a)):
            if row == rank or not work[row][col]:
                continue
            factor = work[row][col]
            work[row] = [(v - factor * w) % p for v, w in zip(work[row], work[rank])]
            transform[row] = [(v - factor * w) % p for v, w in zip(transform[row], transform[rank])]
        rank += 1
        if rank == len(a):
            break
    bad = next((row for row in range(len(a)) if not any(work[row][:-1]) and work[row][-1]), None)
    witness = transform[bad] if bad is not None else None
    if witness is not None:
        require(all(sum(witness[i] * a[i][j] for i in range(len(a))) % p == 0 for j in range(len(a[0]))), "annihilator witness")
        require(sum(witness[i] * b[i] for i in range(len(a))) % p != 0, "nonzero target witness")
    return {"prime": p, "rank": rank, "consistent": witness is None, "left_kernel_witness": witness,
            "witness_null_reason": "No inconsistent row found." if witness is None else None}


def binary_system(rows, variables):
    pivots = {}
    for index, row in enumerate(rows):
        vector = sum(1 << k for k, value in row["terms"] if value % 2) | ((row["rhs"] % 2) << variables)
        combination = 1 << index
        while vector & ((1 << variables) - 1):
            low = (vector & -vector).bit_length() - 1
            if low not in pivots:
                pivots[low] = (vector, combination)
                break
            previous, provenance = pivots[low]
            vector ^= previous
            combination ^= provenance
        else:
            if vector >> variables:
                chosen = [j for j in range(index + 1) if combination >> j & 1]
                return {"consistent": False, "rank_before_contradiction": len(pivots), "equation_indices": chosen,
                        "equations_processed": index + 1}
    return {"consistent": True, "rank": len(pivots), "equations_processed": len(rows), "equation_indices": None,
            "equation_indices_null_reason": "No GF2 contradiction; binary feasibility is still UNKNOWN."}


def contradiction_valid(rows, ids):
    totals = {}
    rhs = 0
    for i in ids:
        rhs ^= rows[i]["rhs"] % 2
        for k, value in rows[i]["terms"]:
            totals[k] = totals.get(k, 0) ^ (value % 2)
    return rhs == 1 and not any(totals.values())


def main():
    started = time.monotonic()
    require(subprocess.check_output(["git", "-C", str(ARCHIVE), "rev-parse", "HEAD"], text=True).strip() == PIN, "archive pin")
    OUT.mkdir(parents=True, exist_ok=False)
    paths = [ARCHIVE / "attempts" / name / "exact-results.json" for name in
             ["wave149-terwilliger-triple", "wave151-triangle-root-factor", "wave154-triangle-factor-portfolio"]]
    docs = [ARCHIVE / "attempts" / name / "derivation.md" for name in
            ["wave149-terwilliger-triple", "wave151-triangle-root-factor", "wave154-triangle-factor-portfolio"]]
    save(OUT / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "archive_repository": "https://github.com/YesterdaysLemon/conway-99-research", "archive_commit": PIN,
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "resource_seconds": 120,
        "inputs_sha256": {p.relative_to(ROOT).as_posix(): digest(p) for p in [*paths, *docs, Path(__file__), SPEC, ROOT / "uv.lock"]},
        "scope": "Two fixed triangle-root Q1 factors only; no unrestricted claim", "solver_calls": 0})
    controls = [prime_feasible([[1, 1], [1, 1]], [1, 1], 2), prime_feasible([[1, 1], [1, 1]], [0, 1], 2)]
    require(controls[0]["consistent"] and not controls[1]["consistent"], "prime positive/negative controls")
    fixture = [{"terms": [[0, 1], [1, 1]], "rhs": 0}, {"terms": [[0, 1], [1, 1]], "rhs": 1}]
    proof = binary_system(fixture, 2)
    require(not proof["consistent"] and contradiction_valid(fixture, proof["equation_indices"]), "GF2 negative control")
    require(not contradiction_valid(fixture, [0]), "corrupt witness rejection")
    require(binary_system(fixture[:1], 2)["consistent"], "GF2 positive control")
    save(OUT / "controls.json", {"prime_controls": controls, "gf2_contradiction": proof, "corrupt_witness_rejected": True})
    stored = [json.loads(p.read_bytes()) for p in paths]
    gram = stored[0]["minimal_surviving_witness"]["gram_rows"]
    derived = [[0] * 36 for _ in range(36)]
    for a in range(36):
        for b in range(36):
            i, u = divmod(a, 12)
            j, v = divmod(b, 12)
            if i == j:
                value = 9 * int(u == v) - int((u ^ 1) == v) + 1
            elif {i, j} == {1, 2}:
                value = 2 - int(u == v) - int((u + 6) % 12 == v) - 2 * int(((u ^ 1) + 6) % 12 == v)
            else:
                value = 2 - int(u == v) - 2 * int((u ^ 1) == v) - int((u + 6) % 12 == v)
            derived[a][b] = value
    require(derived == gram, "all1296 raw Gram entries equal fresh formula")
    edges = [(u, v) for u, v in combinations(range(12), 2) if (u ^ 1) != v]
    require(len(edges) == 60, "edge universe")
    c0 = [[int(u in edge) for edge in edges] for u in range(12)]
    cases = [("wave151", stored[1]["exact_partial_factor"]["Q1"]),
             ("wave154", stored[2]["second_exact_Q1_representative"]["Q1"])]
    outputs = []
    for name, q1 in cases:
        require(time.monotonic() - started < 120, "frozen overall budget")
        require(sorted(q1) == list(range(60)), "Q1 permutation")
        c1 = [[c0[u][q1[d]] for d in range(60)] for u in range(12)]
        c = c0 + c1
        require(all(sum(c[u][d] * c[v][d] for d in range(60)) == gram[u][v] for u in range(24) for v in range(24)), "exact two-group Gram replay")
        targets = [[gram[i][24 + j] for i in range(24)] for j in range(12)]
        modular = [{"third_group_row": j, **prime_feasible(c, targets[j], p)} for p in [2, 3, 5, 7, 11, 13] for j in range(12)]
        allowed = [[all(c[i][d] == 0 or targets[j][i] > 0 for i in range(24)) for d in range(60)] for j in range(12)]
        variables = [{"kind": "C2", "row": j, "column": d} for j in range(12) for d in range(60)]
        dindex = {}
        for u, v in combinations(range(60), 2):
            dindex[u, v] = len(variables)
            variables.append({"kind": "D", "u": u, "v": v})
        equations = []
        def append(label, terms, rhs):
            terms = [[k, v] for k, v in sorted(terms.items()) if v]
            equations.append({"label": label, "terms": terms, "rhs": rhs})
        for j in range(12):
            append(["C2_row_degree", j], {j * 60 + d: 1 for d in range(60)}, 10)
            for i in range(24):
                append(["cross_Gram", i, j], {j * 60 + d: c[i][d] for d in range(60)}, targets[j][i])
            for d in range(60):
                if not allowed[j][d]:
                    append(["forced_C2_zero", j, d], {j * 60 + d: 1}, 0)
        for d in range(60):
            append(["C2_column_degree", d], {j * 60 + d: 1 for j in range(12)}, 2)
            append(["D_degree", d], {dindex[min(d, b), max(d, b)]: 1 for b in range(60) if b != d}, 8)
            for i in range(12):
                for g, cg, other, third in [(0, c0, c1, i), (1, c1, c0, (i + 6) % 12)]:
                    terms = {dindex[min(d, b), max(d, b)]: cg[i][b] for b in range(60) if b != d}
                    terms[third * 60 + d] = 1
                    rhs = 2 - cg[i][d] - cg[i ^ 1][d] - other[i][d]
                    append(["known_group_mixed", g, i, d], terms, rhs)
        gf2 = binary_system(equations, len(variables))
        if not gf2["consistent"]:
            require(contradiction_valid(equations, gf2["equation_indices"]), "raw joint GF2 certificate")
        mappings = sum(all(allowed[j][d] for j in edge) for d in range(60) for edge in edges)
        pair_products = sum(allowed[u][d] and allowed[v][d] for u, v in edges for d in range(60))
        census = {"row_incidence_primary_bits": sum(map(sum, allowed)), "fixed_zero_C2_bits": 720 - sum(map(sum, allowed)),
            "nonmatching_pair_product_bits": pair_products, "old_edge_mapping_primary_bits": mappings,
            "row_degree_equalities": 12, "column_degree_equalities": 60, "cross_gram_equalities": 288,
            "internal_nonmatching_pair_equalities": 60, "internal_matching_zero_pairs": 6,
            "full_residual_graph_additional_edge_variables": 1770}
        payload = {"case": name, "Q1": q1, "edge_universe": edges, "C01": c,
            "third_row_targets": targets, "allowed_C2_entries": allowed, "small_prime_checks": modular,
            "joint_linear_variables": variables, "joint_linear_equations": equations, "joint_GF2": gf2,
            "alternative_encoding_census": census, "status": "CANDIDATE_PREFLIGHT_PENDING_INDEPENDENT_REVIEW",
            "limitations": ["Linear consistency is not binary feasibility.", "This one Q1 and fixed abstract root scaffold do not cover the target."]}
        path = OUT / (name + ".json")
        save(path, payload)
        with path.open("rb") as source, path.with_suffix(".json.gz").open("xb") as target:
            with gzip.GzipFile(fileobj=target, mode="wb", filename="", mtime=0) as zipped:
                zipped.write(source.read())
        outputs.append({"case": name, "artifact": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
            "factor_modular_inconsistencies": sum(not row["consistent"] for row in modular),
            "joint_GF2": gf2, "census": census})
    save(OUT / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "CANDIDATE_PREFLIGHT_COMPLETE",
        "outputs": outputs, "solver_calls": 0, "elapsed_seconds": time.monotonic() - started,
        "archive_imported_code": False, "independent_approval": False, "target_resolution": "UNKNOWN",
        "scope": "Two archived fixed-Q1 families only; no target automorphism or general coverage assumption."})
    print(json.dumps({"status": "CANDIDATE_PREFLIGHT_COMPLETE", "outputs": outputs, "elapsed_seconds": time.monotonic() - started}, indent=2))


if __name__ == "__main__":
    main()

"""Compare producer row assembly with independent full-graph constraints.

The producer's actual Python AST is executed only through its pure row-building
prefix. Matrix creation, solver calls and all producer imports are omitted.
This is a producer cross-check, separate from the producer-free certificate
auditor. Also exercises corruption rejection without creating modified files.
"""
import argparse
import ast
from collections import Counter
import copy
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from audit_certificate import audit, full_graph, graph_constraint, require


class MemoryPath:
    def __init__(self, value, name):
        self.data = json.dumps(value).encode()
        self.name = name

    def read_bytes(self):
        return self.data

    def __str__(self):
        return self.name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    producer = Path(__file__).with_name("linear_probe.py")
    checker = Path(__file__).with_name("audit_certificate.py")
    candidate = json.loads(args.candidate.read_bytes())
    tree = ast.parse(producer.read_text(encoding="utf-8"))
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "constraints")
    stop = next(i for i, node in enumerate(function.body)
                if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Tuple)
                and [x.id for x in node.targets[0].elts] == ["rr", "cc"])
    function.body = function.body[:stop] + [ast.Return(ast.Tuple(
        elts=[ast.Name(id=name, ctx=ast.Load()) for name in ("edges", "groups", "neq")], ctx=ast.Load()))]
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    namespace = {"combinations": combinations}
    exec(compile(module, str(producer), "exec"), namespace)
    edges, groups, neq = namespace["constraints"](set(map(tuple, candidate["overlap_edges_outer_zero_based"])))
    adjacency, unknown = full_graph(candidate)
    require({(u+15, v+15) for u, v in edges} == unknown, "Unknown variable domain mismatch")
    seen = set()
    for i, group in enumerate(groups):
        key = group["kind"], tuple(group["coordinate"])
        require(key not in seen, "Duplicate producer group")
        seen.add(key)
        terms, rhs = graph_constraint(adjacency, unknown, group["kind"], group["coordinate"])
        actual = Counter((edges[e][0]+15, edges[e][1]+15) for e in group["terms"])
        require(actual == terms and rhs == group["target"], f"Producer semantic row mismatch: {key}")
        require(group["equality"] == (group["kind"] == "label_quota") == (i < neq), "Equality partition mismatch")
    omitted = Counter()
    coordinates = [("label_quota", [u, s]) for u in range(84) for s in range(14)]
    coordinates += [("linear_pair_cap", list(pair)) for pair in combinations(range(84), 2)]
    for kind, coordinate in coordinates:
        if (kind, tuple(coordinate)) not in seen:
            terms, rhs = graph_constraint(adjacency, unknown, kind, coordinate)
            require(not terms and (rhs == 0 if kind == "label_quota" else rhs >= 0), "Nontrivial omitted row")
            omitted[kind] += 1
    original = json.loads(args.certificate.read_bytes())
    require(audit(args.candidate, args.certificate)["status"] == "INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS", "Baseline certificate failed")
    corruption_checks = []

    def reject(name, mutate):
        value = copy.deepcopy(original)
        mutate(value)
        try:
            audit(args.candidate, MemoryPath(value, name))
        except ValueError:
            corruption_checks.append(name)
        else:
            raise ValueError(f"Corrupted certificate accepted: {name}")

    reject("wrong_candidate_hash", lambda d: d.update(candidate_sha256="0"*64))
    reject("wrong_rhs", lambda d: d.update(combined_rhs=d["combined_rhs"]+1))
    reject("boolean_rhs", lambda d: d.update(combined_rhs=False))
    reject("negative_pair_weight", lambda d: next(r for r in d["group_multipliers"] if r["kind"] == "linear_pair_cap").update(multiplier=-1))
    reject("duplicate_group", lambda d: d["group_multipliers"].append(copy.deepcopy(d["group_multipliers"][0])))
    reject("negative_box_weight", lambda d: d["edge_upper_bound_multipliers"][0].update(multiplier=-1))
    reject("missing_box_corrections", lambda d: d.update(edge_upper_bound_multipliers=[]))
    reject("unsupported_disjoint_totals", lambda d: d.update(disjoint_block_totals_assumed=True))
    numeric = {"candidate_sha256": original["candidate_sha256"], "status": "NO_EXACT_CERTIFICATE"}
    require(audit(args.candidate, MemoryPath(numeric, "no-certificate"))["status"] == "NO_EXACT_CERTIFICATE_TO_AUDIT",
            "Missing certificate incorrectly promoted")
    result = {
        "status": "INDEPENDENT_LINEAR_MAPPING_AND_CERTIFICATE_CORRUPTION_CHECKS_PASS",
        "inputs_sha256": {str(p): sha256(p.read_bytes()).hexdigest() for p in (args.candidate, args.certificate, producer, checker, Path(__file__))},
        "constraints_compared": len(groups), "label_equalities": neq,
        "pair_caps": len(groups)-neq, "omitted_tautologies": dict(omitted),
        "all_semantic_coordinates_checked": len(coordinates),
        "corruption_rejections": corruption_checks, "missing_certificate_not_promoted": True,
        "solver_imported_or_used": False,
        "scope": "Producer pure row-building AST compared against independent full99 adjacency semantics for this candidate. Separate exact checker uses no producer code.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as output:
        output.write(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()

"""Real whole-matching controls for the frozen accepted-path geometry checker."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import time

from audit_matching_accepted import check_matching_geometry


ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def signature(move):
    return tuple(sorted(len(cycle)//2 for cycle in move["alternating_cycles"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--family-audit", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve previous QA report")
    started = time.perf_counter()
    sources = [Path(__file__), ROOT/"acceleration/audit_matching_accepted.py",
               ROOT/"acceleration/audit_certificate.py", ROOT/"acceleration/audit_phase1_kkt.py"]
    paths = [args.candidate, args.native, args.family_audit, *sources]
    bound = {key(path): digest(path) for path in paths}
    family = json.loads(args.family_audit.read_bytes())
    require(family["status"] == "INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS", "Unverified real family")
    bindings = {str(Path(name.replace("\\", "/")).resolve()): value for name,value in family["inputs_sha256"].items()}
    require(bindings[str(args.candidate.resolve())] == digest(args.candidate), "Family candidate hash mismatch")
    require(bindings[str(args.native.resolve())] == digest(args.native), "Family native hash mismatch")
    data = json.loads(args.native.read_bytes())
    candidate = json.loads(args.candidate.read_bytes())
    base = set(map(tuple, candidate["overlap_edges_outer_zero_based"]))
    expected = {(2,), (3,), (4,), (2,2), (5,), (2,3), (6,), (2,4), (3,3), (2,2,2)}
    representatives = {}
    for index,move in enumerate(data["moves"]):
        representatives.setdefault(signature(move), index)
    require(set(representatives) == expected, "Unexpected or missing real cycle partition")
    positives = []
    for shape,index in sorted(representatives.items(), key=lambda item:(sum(item[0]),item[0])):
        move = data["moves"][index]
        next_edges = set(map(tuple, data["overlap_candidates"][index]))
        check_matching_geometry(base, next_edges, move)
        positives.append(dict(native_candidate_index=index, changed_edges_per_cycle=list(shape),
                              changed_edges=move["changed_edges"], move=move,
                              next_edges_sha256=sha256(json.dumps(sorted(next_edges),separators=(",", ":")).encode()).hexdigest(),
                              status="REAL_FULL99_GEOMETRY_ACCEPTED"))

    controls = []

    def negative(name, shape, mutate, alter_next=None):
        index = representatives[shape]
        move = deepcopy(data["moves"][index])
        next_edges = set(map(tuple,data["overlap_candidates"][index]))
        mutate(move)
        if alter_next is not None:
            next_edges = alter_next(next_edges)
        try:
            check_matching_geometry(base,next_edges,move)
        except ValueError as exc:
            controls.append(dict(name=name, native_candidate_index=index, rejected=True,
                                 exception_type=type(exc).__name__, reason=str(exc), mutated_move=move,
                                 next_graph_changed=alter_next is not None))
        else:
            raise ValueError("Corruption accepted: " + name)

    negative("join_two_disjoint_cycles_with_false_bridges", (2,2),
             lambda m:m.update(alternating_cycles=[m["alternating_cycles"][0]+m["alternating_cycles"][1]]))
    negative("omit_one_required_cycle", (2,2), lambda m:m["alternating_cycles"].pop())
    negative("missing_all_cycles", (2,), lambda m:m.update(alternating_cycles=[]))
    negative("duplicate_vertex_inside_cycle", (3,), lambda m:m["alternating_cycles"][0].__setitem__(2,m["alternating_cycles"][0][0]))
    negative("repeat_whole_cycle", (2,), lambda m:m["alternating_cycles"].append(deepcopy(m["alternating_cycles"][0])))
    negative("noncanonical_cycle_start", (3,), lambda m:m.update(alternating_cycles=[m["alternating_cycles"][0][2:]+m["alternating_cycles"][0][:2]]))
    negative("noncanonical_cycle_order", (2,2), lambda m:m["alternating_cycles"].reverse())
    negative("changed_edge_size_too_small", (3,), lambda m:m.update(changed_edges=2))
    negative("changed_edge_size_too_large", (6,), lambda m:m.update(changed_edges=7))
    negative("boolean_edge_size", (2,), lambda m:m.update(changed_edges=True))
    negative("wrong_root_group", (2,), lambda m:m.update(root_group=(m["root_group"]+1)%7))
    negative("noninteger_root_group", (2,), lambda m:m.update(root_group=float(m["root_group"])))
    negative("opposite_same_sign_class", (2,), lambda m:m.update(matching_class="same_"+str(1-int(m["matching_class"][-1]))))
    negative("forbidden_cross_class", (2,), lambda m:m.update(matching_class="cross"))
    negative("missing_added_edge", (3,), lambda m:m["added"].pop())
    negative("duplicate_removed_edge", (3,), lambda m:m["removed"].__setitem__(1,list(m["removed"][0])))
    negative("removed_added_common_edge", (3,), lambda m:m["added"].__setitem__(0,list(m["removed"][0])))
    negative("unsorted_edge_list", (3,), lambda m:m["removed"].reverse())
    negative("reversed_edge_endpoints", (2,), lambda m:m["added"][0].reverse())
    negative("edge_endpoint_out_of_range", (2,), lambda m:m["added"][0].__setitem__(1,84))
    negative("wrong_next_graph", (2,), lambda m:None, lambda _next:base.copy())

    def invert(m):
        m["removed"],m["added"] = m["added"],m["removed"]
        m["alternating_cycles"] = [[cycle[0],*reversed(cycle[1:])] for cycle in m["alternating_cycles"]]
    negative("valid_inverse_difference_applied_to_wrong_base", (3,), invert)

    target_move = data["moves"][representatives[(2,)]]
    target_vertices = set(v for cycle in target_move["alternating_cycles"] for v in cycle)
    other_cycle = next(cycle for move in data["moves"] for cycle in move["alternating_cycles"]
                       if target_vertices.isdisjoint(cycle))
    def undeclared(m):
        m["alternating_cycles"].append(list(other_cycle))
        m["alternating_cycles"].sort(key=lambda cycle:cycle[0])
    negative("undeclared_disjoint_real_cycle", (2,), undeclared)

    require(all(digest(path)==bound[key(path)] for path in paths), "Input or auditor source changed during QA")
    report = dict(status="INDEPENDENT_MATCHING_ACCEPTED_GEOMETRY_REAL_AND_CORRUPTION_CONTROLS_PASS",
                  inputs_sha256=bound, positive_real_controls=len(positives), negative_controls=len(controls),
                  all_negative_controls_rejected=True, all_cycle_partitions_covered=[list(shape) for shape in sorted(expected)],
                  changed_edges_covered=[2,3,4,5,6], positive_controls=positives, corruption_controls=controls,
                  current_graph_is_authoritative_full99_seed=True, fabricated_graph_positive_controls=False,
                  full_native_completeness_audit_repeated=False, optimizer_or_producer_imported=False,
                  audited_function="audit_matching_accepted.check_matching_geometry",
                  elapsed_seconds=time.perf_counter()-started,
                  scope="Real full99-valid native representatives cover every occurring 2..6-edge cycle partition; semantic corruptions are rejected by the frozen geometry checker. This supplements its proof-path checks and the separate exhaustive family audit; no general software-correctness or graph-completion claim.")
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({k:report[k] for k in ("status","positive_real_controls","negative_controls","elapsed_seconds")}))


if __name__ == "__main__":
    main()

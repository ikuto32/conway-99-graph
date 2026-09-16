"""Exercise atomic audit geometry on an actual saved net3-cycle and corruptions."""
import argparse
import copy
from hashlib import sha256
import json
from pathlib import Path

from audit_atomic_accepted import check_alternating_cycle, check_atomic_geometry
from audit_certificate import require


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--two-trade-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve prior geometry controls")
    summary_path = args.two_trade_run / "summary.json"
    summary = json.loads(summary_path.read_bytes())
    record = next(row for row in summary["records"] if row["accepted"])
    initial_path = Path(record["previous_probe"]["candidate_path"])
    next_path = Path(record["chosen_probe"]["candidate_path"])
    require(digest(initial_path) == record["previous_probe"]["candidate_sha256"] and
            digest(next_path) == record["chosen_probe"]["candidate_sha256"], "Saved endpoint hash mismatch")
    before = set(map(tuple, json.loads(initial_path.read_bytes())["overlap_edges_outer_zero_based"]))
    after = set(map(tuple, json.loads(next_path.read_bytes())["overlap_edges_outer_zero_based"]))
    removed, added = before-after, after-before
    require(len(removed) == len(added) == 3, "Expected the saved net3-cycle control")
    old_partner = {u:v for edge in removed for u,v in (edge, edge[::-1])}
    new_partner = {u:v for edge in added for u,v in (edge, edge[::-1])}
    start = min(old_partner)
    cycle, u = [], start
    for _ in range(3):
        v = old_partner[u]
        cycle.extend((u,v))
        u = new_partner[v]
    require(u == start, "Saved net move is not closed")
    move = dict(removed=[list(edge) for edge in sorted(removed)], added=[list(edge) for edge in sorted(added)],
                root_group=3, matching_class="cross", cycle_size=3, alternating_cycle=cycle)
    check_atomic_geometry(before, after, move)
    rejected = []

    def reject(name, mutate, target=None):
        bad = copy.deepcopy(move)
        mutate(bad)
        try:
            check_atomic_geometry(before, after if target is None else target, bad)
        except ValueError as error:
            rejected.append(dict(name=name, reason=str(error)))
        else:
            raise ValueError("Corrupted atomic geometry accepted: " + name)

    reject("wrong_root_group", lambda m: m.update(root_group=4))
    reject("wrong_matching_class", lambda m: m.update(matching_class="same_0"))
    reject("repeated_cycle_vertex", lambda m: m["alternating_cycle"].__setitem__(-1, m["alternating_cycle"][0]))
    reject("wrong_removed_edge", lambda m: m["removed"].__setitem__(0, [0,1]))
    reject("wrong_added_edge", lambda m: m["added"].__setitem__(0, [28,65]))
    reject("noncanonical_edge", lambda m: m["removed"].__setitem__(0, list(reversed(m["removed"][0]))))
    reject("missing_added_edge", lambda m: m["added"].pop())
    reject("wrong_final_graph", lambda m: None, after-{next(iter(after-before))})
    reject("boolean_root_group", lambda m: m.update(root_group=True))
    abstract = dict(cycle_size=4, removed=[[0,1],[2,3],[4,5],[6,7]],
                    added=[[0,7],[1,2],[3,4],[5,6]], alternating_cycle=list(range(8)))
    check_alternating_cycle(abstract)
    disconnected = copy.deepcopy(abstract)
    disconnected["added"] = [[0,3],[1,2],[4,7],[5,6]]
    try:
        check_alternating_cycle(disconnected)
    except ValueError as error:
        rejected.append(dict(name="disconnected_two4cycles_in_k4", reason=str(error)))
    else:
        raise ValueError("Two disconnected alternating4-cycles were accepted as one8-cycle")
    result = dict(status="ATOMIC_GEOMETRY_AUDITOR_REAL_CONTROL_AND_CORRUPTION_CHECKS_PASS",
                  real_control_net_move=move, real_control_both_full99_partial_graphs_valid=True,
                  abstract_k4_cycle_structure_pass=True,
                  abstract_k4_control_is_not_claimed_as_a_valid_K_graph=True,
                  corruption_rejections=rejected,
                  inputs_sha256={str(path): digest(path) for path in (summary_path, initial_path, next_path)},
                  sources_sha256={str(path): digest(path) for path in
                                  (Path(__file__), Path(__file__).with_name("audit_atomic_accepted.py"),
                                   Path(__file__).with_name("audit_certificate.py"))},
                  scope="Tests actual saved legal net3-cycle geometry plus abstract cycle connectivity and ten corruptions. No new candidate search, pair-AC proof, or global exclusion.")
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(status=result["status"], corruptions=len(rejected), actual_cycle=cycle,
                          auditor_sha256=result["sources_sha256"][str(Path(__file__).with_name("audit_atomic_accepted.py"))])))


if __name__ == "__main__":
    main()

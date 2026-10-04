"""Candidate stronger exterior-type filter; no LP, primal solve or graph search."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + "_spec.md")
SOFTWARE = {
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
BASE = "acceleration/results/20261003_external_neighborhood_moment_seventeen_base01"
SUMMARY = BASE + "/summary.json"
MODEL = BASE + "/seventeen_base/model.json"
TYPES = BASE + "/seventeen_base/types.json"
RAW_INPUTS = {
    SUMMARY: "23fc6d633fe626a0a8141d3f974c415b6a559c6b67c60f231de8c412b63672d0",
    MODEL: "d5f1afaf937b75c22f6e5d5c376a36f55f9326dc131399011a5502598742a3f9",
    TYPES: "4799c4603dc949ace22184c5742816eb0dbfe1bd6ea9b2d0ff407678e13de46a",
}
LEMMA = "acceleration/audit_20261003_external_type_cross_cn_cap_native_v1.md"
LEMMA_SHA = "9336f741cb8088d09924de2074f70c3232d059ea387fc3f7f914fb67a75c3793"
TRIPLES = ((0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 7, 9), (1, 8, 10),
           (15, 11, 14), (16, 12, 13), (2, 15, 16), (3, 7, 11),
           (4, 8, 12), (5, 9, 13), (6, 10, 14))
FULL_HEADER = "INDEPENDENT_EXTERNAL_NEIGHBOR_MOMENTS_V1_COMPLETE_PASS"


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def same(left, right):
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)


def tick(deadline):
    snapshot = deadline.status()
    need(not snapshot["stop_required"] and snapshot["remaining_seconds"] > 20, "SAVE_RESERVE")


def strict_json(raw):
    need(type(raw) is bytes and len(raw) <= 64 * 1024 * 1024, "JSON_BYTES")
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "JSON_DUPLICATE")
            result[key] = value
        return result
    def nonfinite(_):
        raise ValueError("JSON_NONFINITE")
    return json.loads(raw.decode("utf8"), object_pairs_hook=pairs, parse_constant=nonfinite)


def graph(h):
    need(type(h) is list and h and all(type(row) is list and len(row) == len(h) for row in h), "GRAPH_SHAPE")
    need(all(type(value) is int and value in (0, 1) for row in h for value in row), "GRAPH_BINARY_INTEGER")
    need(all(h[u][u] == 0 for u in range(len(h))), "GRAPH_DIAGONAL")
    need(all(h[u][v] == h[v][u] for u in range(len(h)) for v in range(len(h))), "GRAPH_SYMMETRY")
    return [{v for v, value in enumerate(row) if value == 1} for row in h]


def fixed_graph():
    h = [[0] * 17 for _ in range(17)]
    for triple in TRIPLES:
        for u, v in itertools.combinations(triple, 2):
            h[u][v] = h[v][u] = 1
    return h


def coefficient(mask, m):
    need(type(mask) is int and 0 <= mask < 1 << m, "TYPE_MASK_INTEGER")
    bits = [(mask >> u) & 1 for u in range(m)]
    return [1, *bits, *[bits[u] * bits[v] for u, v in itertools.combinations(range(m), 2)]]


def validate_types(types, m, deadline):
    need(type(types) is list and types, "TYPE_POPULATION")
    previous = -1
    for record in types:
        tick(deadline)
        need(type(record) is dict and set(record) == {"mask", "coefficient"}, "TYPE_FIELDS")
        mask = record["mask"]
        need(type(mask) is int and 0 <= mask < 1 << m, "TYPE_MASK_INTEGER")
        need(previous < mask, "TYPE_MASK_ORDER")
        need(type(record["coefficient"]) is list
             and all(type(value) is int for value in record["coefficient"])
             and same(record["coefficient"], coefficient(mask, m)), "TYPE_COEFFICIENT")
        previous = mask


def point_caps(h, mask, deadline):
    """Every support point is checked, even after the first violation."""
    neighbors = graph(h)
    need(type(mask) is int and 0 <= mask < 1 << len(h), "TYPE_MASK_INTEGER")
    selected = {u for u in range(len(h)) if mask & (1 << u)}
    records = []
    for u, neighborhood in enumerate(neighbors):
        tick(deadline)
        witnesses = sorted(neighborhood & selected)
        inside = u in selected
        cap = 1 if inside else 2
        records.append({"u": u, "u_in_type": inside, "cn_in_induced_H": len(witnesses),
                        "necessary_cap": cap, "common_neighbor_witnesses": witnesses,
                        "passes": len(witnesses) <= cap})
    first = next((record for record in records if not record["passes"]), None)
    return {"mask": mask, "selected_vertices": sorted(selected), "eligible": first is None,
            "first_veto": first, "point_checks": records}


def rook_graph():
    return [[int(i != j and (i // 3 == j // 3 or i % 3 == j % 3)) for j in range(9)] for i in range(9)]


def own_controls(deadline, save, read):
    rook = rook_graph()
    rectangle = [0, 1, 3, 4]
    h4 = [[rook[u][v] for v in rectangle] for u in rectangle]
    h8 = [row[:8] for row in rook[:8]]
    cases = [
        ("rook_rectangle_five_exterior", {"h": h4, "masks": [3, 12, 5, 10, 0],
         "expected_h": [[1, 1, 1, 1]] * 4 + [[0, 0, 0, 0]]}, "PASS"),
        ("rook_eight_vertex_exterior", {"h": h8, "masks": [228],
         "expected_h": [[2, 2, 1, 2, 2, 1, 1, 1]]}, "PASS"),
        ("bad_mask44", {"h": fixed_graph(), "mask": 44,
         "expected_first_veto": {"u": 0, "u_in_type": False, "cn_in_induced_H": 3,
                                 "necessary_cap": 2, "common_neighbor_witnesses": [2, 3, 5], "passes": False}}, "OUTSIDE_CN_CAP"),
        ("bool_mask", {"h": h4, "mask": True}, "TYPE_MASK_INTEGER"),
        ("float_mask", {"h": h4, "mask": 3.0}, "TYPE_MASK_INTEGER"),
        ("unordered_types", {"types": [{"mask": 1, "coefficient": coefficient(1, 17)},
                                      {"mask": 0, "coefficient": coefficient(0, 17)}]}, "TYPE_MASK_ORDER"),
    ]
    records = []
    for label, payload, expected in cases:
        tick(deadline)
        save("control_" + label + ".json", payload)
        actual_payload = read(ROOT / save.output_relative / ("control_" + label + ".json"))
        actual = "PASS"
        results = None
        try:
            if label == "unordered_types":
                validate_types(actual_payload["types"], 17, deadline)
            elif label == "bad_mask44":
                results = point_caps(actual_payload["h"], actual_payload["mask"], deadline)
                need(same(results["first_veto"], actual_payload["expected_first_veto"]), "CONTROL_WITNESS")
                actual = "OUTSIDE_CN_CAP" if not results["eligible"] else "PASS"
            elif label in ("bool_mask", "float_mask"):
                point_caps(actual_payload["h"], actual_payload["mask"], deadline)
            else:
                results = [point_caps(actual_payload["h"], mask, deadline) for mask in actual_payload["masks"]]
                need(all(record["eligible"] for record in results), "CONTROL_ROOK_ELIGIBILITY")
                observed_h = [[record["cn_in_induced_H"] for record in result["point_checks"]] for result in results]
                need(same(observed_h, actual_payload["expected_h"]), "CONTROL_ROOK_COUNTS")
        except ValueError as error:
            actual = str(error)
        need(actual == expected, "CONTROL_STAGE:" + label)
        records.append({"case": label, "expected_stage": expected, "actual_stage": actual,
                        "actual_geometry": results})
    save("controls.json", {"positive": 2, "strict_negative": 4, "total": 6, "records": records,
                          "known_graph_exterior_types": 6, "known_graph_point_checks": 28,
                          "deliberately_bad_mask_point_checks": 17,
                          "known_realizations_are_rook9_only": True, "target_graph_realizations": 0})
    return {"positive": 2, "strict_negative": 4, "total": 6}


def filter_types(model, types, deadline, save):
    need(type(model) is dict and model.get("schema") == "EXTERIOR_NEIGHBOR_MOMENT_MODEL_V1", "MODEL_SCHEMA")
    for key, wanted in (("target_order", 99), ("target_degree", 14), ("adjacent_cn", 1),
                        ("nonadjacent_cn", 2), ("eligible_type_count", 534)):
        need(type(model.get(key)) is int and model[key] == wanted, "MODEL_PARAMETER:" + key)
    need(same(model.get("ordered_support_vertices"), list(range(17))), "MODEL_POINT_ORDER")
    h = model.get("induced_adjacency")
    graph(h)
    need(same(h, fixed_graph()), "FIXED_INDUCED_GRAPH")
    labels = [{"kind": "total"}] + [{"kind": "vertex", "vertex": u} for u in range(17)]
    labels += [{"kind": "pair", "vertices": [u, v]} for u, v in itertools.combinations(range(17), 2)]
    need(same(model.get("row_labels"), labels), "MODEL_ROW_ORDER")
    rhs = model.get("right_hand_side")
    need(type(rhs) is list and len(rhs) == 154 and all(type(value) is int and value >= 0 for value in rhs), "MODEL_RHS_INTEGER")
    need(type(types) is list and len(types) == 534, "TYPE_POPULATION")
    validate_types(types, 17, deadline)
    decisions, retained, retained_indices = [], [], []
    for index, record in enumerate(tqdm(types, total=534, desc="outside CN types", unit="type")):
        tick(deadline)
        result = point_caps(h, record["mask"], deadline)
        result["original_type_index"] = index
        decisions.append(result)
        if result["eligible"]:
            retained.append(record)
            retained_indices.append(index)
    need(len(decisions) == 534 and sum(len(record["point_checks"]) for record in decisions) == 9078, "COMPLETE_CAP_POPULATION")
    first_counts = Counter(str(record["first_veto"]["u"]) for record in decisions if not record["eligible"])
    # The new schema keeps the original154 labels/RHS and literal retained columns;
    # it does not relabel the old131072-mask census or alter the old model.
    filtered = {"schema": "OUTSIDE_VERTEX_CN_FILTERED_MOMENT_SYSTEM_V1", "target_order": 99,
                "target_degree": 14, "adjacent_cn": 1, "nonadjacent_cn": 2,
                "ordered_support_vertices": model["ordered_support_vertices"],
                "induced_adjacency": h, "row_labels": labels, "right_hand_side": rhs,
                "original_model_path": MODEL, "original_model_sha256": RAW_INPUTS[MODEL],
                "original_types_path": TYPES, "original_types_sha256": RAW_INPUTS[TYPES],
                "original_eligible_type_count": 534, "eligible_type_count": len(retained),
                "retained_original_type_indices": retained_indices,
                "retained_coefficients_are_literal_originals": True,
                "original_row_labels_rhs_unchanged": True,
                "additional_necessary_filter": "For everyu: |N_H(u) intersectT| <=1 insideT, <=2 outsideT",
                "feasibility_certificate": None, "feasibility_certificate_unavailable_reason": "No LP or primal reconstruction is run by this filter."}
    save("decisions.json", decisions)
    save("types.json", retained)
    save("filtered_system.json", filtered)
    return {"original_types": 534, "support_vertices": 17, "complete_point_checks": 9078,
            "retained_types": len(retained), "removed_types": 534 - len(retained),
            "first_veto_point_counts": dict(sorted(first_counts.items(), key=lambda item: int(item[0]))),
            "rows_unchanged": 154, "retained_coefficients_are_literal_originals": True,
            "all_point_witnesses_saved_even_after_first_veto": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["calibrate", "filter"])
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--spec-sha256", required=True)
    parser.add_argument("--full-gate", type=Path)
    parser.add_argument("--full-gate-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="Exact534x17 necessary outside-CN filter; all authentication, controls and preservation in one invocation")
    out = args.out.resolve()
    need(out.is_relative_to(ROOT / "acceleration/results") and not out.exists(), "FRESH_OUTPUT")
    out.mkdir(parents=True)
    pins = {}
    def digest(path):
        tick(deadline)
        sha = hashlib.sha256()
        with path.open("rb") as stream:
            while block := stream.read(1024 * 1024):
                sha.update(block)
                tick(deadline)
        tick(deadline)
        return sha.hexdigest()
    def pin(path, expected=None):
        path = Path(path).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), "INPUT_PATH")
        name = path.relative_to(ROOT).as_posix()
        need(name != "CLAIMS.yaml" and not name.startswith(".git/"), "MUTABLE_INPUT")
        observed = digest(path)
        need(expected is None or type(expected) is str and observed == expected, "INPUT_SHA:" + name)
        need(name not in pins or pins[name] == observed, "CONFLICTING_INPUT:" + name)
        pins[name] = observed
        return path
    def read(path, expected=None):
        value = strict_json(pin(path, expected).read_bytes())
        tick(deadline)
        return value
    def save(name, value):
        tick(deadline)
        raw = (json.dumps(value, allow_nan=False, indent=2) + "\n").encode("utf8")
        tick(deadline)
        with (out / name).open("xb") as stream:
            for start in range(0, len(raw), 1024 * 1024):
                stream.write(raw[start:start + 1024 * 1024])
                tick(deadline)
        tick(deadline)
    save.output_relative = out.relative_to(ROOT)
    try:
        for name, expected in SOFTWARE.items():
            pin(ROOT / name, expected)
        pin(SELF, args.source_sha256)
        pin(SPEC, args.spec_sha256)
        pin(ROOT / LEMMA, LEMMA_SHA)
        controls = own_controls(deadline, save, read)
        result = None
        if args.mode == "calibrate":
            need(args.full_gate is None and args.full_gate_sha256 is None, "CALIBRATION_NO_ORIGINAL_MODEL")
            status = "AUTHOR_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_CONTROLS_PASS"
        else:
            need(args.full_gate is not None and args.full_gate_sha256 is not None, "GENUINE_FULL_GATE_REQUIRED")
            gate = read(args.full_gate, args.full_gate_sha256)
            need(type(gate) is dict and gate.get("status") == FULL_HEADER
                 and gate.get("producer") == "/root" and gate.get("verifier") == "/root/native_driver"
                 and gate.get("method") == "independent_artifact_check" and gate.get("target_resolution") == "NONE"
                 and type(gate.get("checker_implementation_version")) is int
                 and gate["checker_implementation_version"] == 3, "FULL_GATE_ROLE_SCOPE")
            closure = gate.get("inputs_sha256")
            need(type(closure) is dict and closure, "FULL_GATE_INPUTS")
            for name, expected in closure.items():
                pin(ROOT / name, expected)
            need(all(closure.get(name) == expected for name, expected in RAW_INPUTS.items()), "FULL_GATE_LITERAL_INPUTS")
            packets = {name: read(ROOT / name, expected) for name, expected in RAW_INPUTS.items()}
            need(all(packets[SUMMARY]["outputs_sha256"].get(name) == RAW_INPUTS[name] for name in (MODEL, TYPES)), "ORIGINAL_OUTPUT_BINDING")
            result = filter_types(packets[MODEL], packets[TYPES], deadline, save)
            status = "CANDIDATE_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_PENDING_INDEPENDENT_CHECK"
        for name, expected in list(pins.items()):
            pin(ROOT / name, expected)
        outputs = {path.relative_to(ROOT).as_posix(): digest(path) for path in sorted(out.iterdir()) if path.is_file()}
        save("summary.json", {"status": status, "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_author": "/root/checkpoint_audit", "producer": "/root/checkpoint_audit",
            "independent_verifier_required": "/root/native_driver", "independent_approval": False,
            "mode": args.mode, "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
            "python": platform.python_version(), "inputs_sha256": pins, "outputs_sha256": outputs,
            "controls": controls, "filter_result": result, "LP_calls": 0, "primal_solves": 0,
            "original_universe_reenumerations": 0, "target_resolution": "NONE", "ledger_index_git_mutations": False,
            "shared_origins": ["ROOT proposed cap and mask44; Native independently derived lemma", "Common Python/SHA/strictJSON/deadline scaffolding preserved from da6e exact-support producer; no producer/checker imports"],
            "limitations": ["Necessary filter of original534 types for one fixed induced17 graph only", "Original weaker model and its exact candidate remain unmodified; no validity refutation inferred", "Retained types do not establish realizability or moment feasibility", "No target/family exclusion or primal/Farkas/integer certificate is obtained by filtering", "Counts and witnesses remain candidate until independent raw checking"],
            "deadline": deadline.status()})
        tick(deadline)
        return 0
    except BaseException as error:
        if (out / "summary.json").exists():
            (out / "summary.json").rename(out / "summary.not_approved.json")
        (out / "failure.json").write_text(json.dumps({"status": "FAILED_OR_NOT_COMPLETED_OUTSIDE_CN_FILTER",
            "error": repr(error), "inputs_sha256": pins, "deadline": deadline.status(),
            "partial_outputs_preserved": True, "automatic_retry": False, "target_resolution": "NONE",
            "feasibility_or_nonexistence_inferred": False}, allow_nan=False, indent=2) + "\n", encoding="utf8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())

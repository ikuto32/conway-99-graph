"""Positive singleton and deliberate-corruption controls for the family auditor."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import time

from audit_certificate import require
from audit_whole_matching_family import enumerate_family, audit_against_family, selected_coordinates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--full-audit", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve existing QA artifact")
    started = time.perf_counter()
    paths = [args.candidate, args.native, args.full_audit, Path(__file__),
             Path(__file__).with_name("audit_whole_matching_family.py"),
             Path(__file__).with_name("audit_certificate.py")]
    bindings = {str(p): sha256(p.read_bytes()).hexdigest() for p in paths}
    candidate, native, full = (json.loads(p.read_bytes()) for p in paths[:3])
    require(full["status"] == "INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS" and full["selector"] == "all",
            "Missing independent all-coordinate proof")
    for name, expected in full["inputs_sha256"].items():
        path = Path(name)
        require(sha256(path.read_bytes()).hexdigest() == expected, "Changed full-audit dependency")
        bindings[name] = expected
    require(native["selector"] == "0:0", "Expected independent singleton control")
    reference = enumerate_family(candidate, selected_coordinates(native["selector"]))
    baseline = audit_against_family(candidate, native, reference)
    controls = []

    def check(name, modified):
        try:
            audit_against_family(candidate, modified, reference)
        except (ValueError, KeyError, TypeError) as error:
            controls.append(dict(control=name, rejected=True, reason=str(error)))
        else:
            raise ValueError("Corrupted whole-matching artifact accepted: " + name)

    modified = dict(native)
    modified["moves"], modified["overlap_candidates"] = native["moves"][1:], native["overlap_candidates"][1:]
    check("missing_aligned_legal_final", modified)
    modified = dict(native)
    modified["moves"] = native["moves"] + native["moves"][:1]
    modified["overlap_candidates"] = native["overlap_candidates"] + native["overlap_candidates"][:1]
    check("duplicate_aligned_legal_final", modified)
    modified = dict(native)
    modified["overlap_candidates"] = list(native["overlap_candidates"])
    modified["overlap_candidates"][0], modified["overlap_candidates"][1] = modified["overlap_candidates"][1], modified["overlap_candidates"][0]
    check("legal_finals_attached_to_wrong_moves", modified)

    def move_variant(index):
        changed = dict(native)
        changed["moves"] = list(native["moves"])
        changed["moves"][index] = deepcopy(native["moves"][index])
        return changed

    modified = move_variant(0)
    modified["moves"][0]["root_group"] = 1
    check("wrong_matching_coordinate", modified)
    modified = move_variant(0)
    modified["moves"][0]["changed_edges"] = 1
    check("wrong_changed_edge_count", modified)
    modified = move_variant(0)
    cycle = modified["moves"][0]["alternating_cycles"][0]
    cycle[1] = cycle[0]
    check("repeated_cycle_vertex", modified)
    multiple = next(i for i, move in enumerate(native["moves"]) if len(move["alternating_cycles"]) > 1)
    modified = move_variant(multiple)
    modified["moves"][multiple]["alternating_cycles"].pop()
    check("omitted_component_of_multiple_cycles", modified)
    modified = move_variant(multiple)
    cycles = modified["moves"][multiple]["alternating_cycles"]
    cycles[0] = cycles[0] + cycles.pop(1)
    check("disconnected_cycles_falsely_joined", modified)
    modified = dict(native)
    modified["by_class"] = deepcopy(native["by_class"])
    modified["by_class"][0]["legal_count"] += 1
    modified["by_class"][0]["cap_rejected_count"] -= 1
    check("altered_partition_with_unchanged_total", modified)
    modified = dict(native)
    modified["status"] = "INCOMPLETE_ENUMERATION"
    check("incomplete_status_promoted_to_complete", modified)
    require(len(controls) == 10, "Wrong QA control count")
    result = dict(status="INDEPENDENT_WHOLE_MATCHING_FAMILY_AUDITOR_CONTROLS_PASS", inputs_sha256=bindings,
                  positive_singleton_full_family_audit=baseline,
                  negative_controls=controls, negative_controls_rejected=len(controls),
                  multi_cycle_positive_move_index=multiple,
                  scope="All14-coordinate proof is bound separately; singleton0:0 independently reenumerated for these corruption controls. No additional search or completion claim.",
                  elapsed_seconds=time.perf_counter() - started)
    require(all(sha256(p.read_bytes()).hexdigest() == bindings[str(p)] for p in paths), "Source/input changed during QA")
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("inputs_sha256", "positive_singleton_full_family_audit", "negative_controls")}))


if __name__ == "__main__":
    main()

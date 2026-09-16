"""Independent exhaustive auditor of whole same-sign matching replacements.

Enumerates all 10,395 unrestricted matchings on each 12-vertex cohort and
retains the 6,040 support-allowed matchings. Actual Python set neighborhoods
check the final partial graph. No Rust producer or graph model is imported.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from audit_certificate import full_graph, integer, require

ROOT = Path(__file__).resolve().parents[1]


def canonical(u, v):
    return (u, v) if u < v else (v, u)


def edge_set(value, count):
    require(type(value) is list and len(value) == count, "Wrong edge-list length")
    require(all(type(e) is list and len(e) == 2 and all(map(integer, e)) and
                0 <= e[0] < e[1] < 84 for e in value), "Invalid canonical edge")
    result = frozenset(map(tuple, value))
    require(len(result) == count and value == [list(e) for e in sorted(result)],
            "Repeated or unsorted edges")
    return result


def selected_coordinates(selector):
    require(type(selector) is str, "Selector must be a string")
    if selector == "all":
        return [(g, f"same_{s}") for g in range(7) for s in range(2)]
    pieces = selector.split(":")
    require(len(pieces) == 2 and pieces[0] in tuple(map(str, range(7))) and pieces[1] in ("0", "1"),
            "Invalid same-sign matching selector")
    return [(int(pieces[0]), "same_" + pieces[1])]


def unrestricted_matchings(vertices):
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for j in range(1, len(vertices)):
        second = vertices[j]
        remaining = vertices[1:j] + vertices[j + 1:]
        for tail in unrestricted_matchings(remaining):
            yield ((first, second),) + tail


def enumerate_family(candidate, coordinates):
    adjacency, _ = full_graph(candidate)
    original = edge_set(candidate["overlap_edges_outer_zero_based"], 168)
    labels = [{s - 1 for s in adjacency[u + 15] if 1 <= s <= 14} for u in range(84)]
    supports = [{s // 2 for s in row} for row in labels]
    for u in range(15, 99):
        for symbol in range(1, 15):
            if (symbol - 1) // 2 in supports[u - 15]:
                require(len(adjacency[u] & adjacency[symbol]) == (1 if symbol in adjacency[u] else 2),
                        "Initial own-label quota violated")
    legal, by_class = {}, []
    pair_checks, quota_checks = 0, 0
    for group, kind in coordinates:
        require(integer(group) and 0 <= group < 7 and kind in ("same_0", "same_1"), "Invalid coordinate")
        symbol = 2 * group + int(kind[-1])
        vertices = tuple(u for u in range(84) if symbol in labels[u])
        allowed = {e for e in combinations(vertices, 2) if supports[e[0]] & supports[e[1]] == {group}}
        require(len(vertices) == 12 and len(allowed) == 60, "Wrong same-sign matching domain")
        old_matching = original & allowed
        require(Counter(u for e in old_matching for u in e) == Counter({u: 1 for u in vertices}),
                "Initial matching does not cover its cohort")
        counts = dict(root_group=group, matching_class=kind, raw_including_initial=0,
                      unchanged_count=0, cap_rejected_count=0, legal_count=0)
        unrestricted_count = 0
        for matching in unrestricted_matchings(vertices):
            unrestricted_count += 1
            matching = frozenset(matching)
            if not matching <= allowed:
                continue
            counts["raw_including_initial"] += 1
            if matching == old_matching:
                counts["unchanged_count"] += 1
                continue
            removed, added = old_matching - matching, matching - old_matching
            changed = sorted({u + 15 for edge in removed for u in edge})
            require(Counter(u for e in removed for u in e) == Counter(u for e in added for u in e),
                    "Replacement is not degree preserving")
            rows = adjacency.copy()
            for u in changed:
                rows[u] = set(rows[u])
            for u, v in removed:
                rows[u + 15].remove(v + 15)
                rows[v + 15].remove(u + 15)
            for u, v in added:
                rows[u + 15].add(v + 15)
                rows[v + 15].add(u + 15)
            valid = True
            for u in changed:
                for v in range(99):
                    if u == v:
                        continue
                    pair_checks += 1
                    if len(rows[u] & rows[v]) > (1 if v in rows[u] else 2):
                        valid = False
                        break
                if not valid:
                    break
            if not valid:
                counts["cap_rejected_count"] += 1
                continue
            for u in changed:
                require(len(rows[u]) == 6, "Replacement changed partial degree")
                for own_symbol in range(1, 15):
                    if (own_symbol - 1) // 2 in supports[u - 15]:
                        quota_checks += 1
                        require(len(rows[u] & rows[own_symbol]) == (1 if own_symbol in rows[u] else 2),
                                "Own-label common-neighbor quota violated")
            signature = (tuple(sorted(removed)), tuple(sorted(added)))
            require(signature not in legal, "Duplicate independent whole-matching replacement")
            legal[signature] = (group, kind, len(removed))
            counts["legal_count"] += 1
        require(unrestricted_count == 10395 and counts["raw_including_initial"] == 6040 and
                counts["unchanged_count"] == 1, "Independent complete matching counts differ")
        require(sum(counts[k] for k in ("unchanged_count", "cap_rejected_count", "legal_count")) == 6040,
                "Matching partition count differs")
        by_class.append(counts)
    return dict(original=original, coordinates=tuple(coordinates), legal=legal, by_class=by_class,
                pair_checks=pair_checks, quota_checks=quota_checks)


def validate_cycles(move, removed, added):
    cycles = move["alternating_cycles"]
    require(type(cycles) is list and 1 <= len(cycles) <= 3, "Wrong number of alternating cycles")
    seen_vertices, cycle_removed, cycle_added, starts = set(), set(), set(), []
    for cycle in cycles:
        require(type(cycle) is list and len(cycle) in (4, 6, 8, 10, 12) and
                all(integer(u) and 0 <= u < 84 for u in cycle) and len(set(cycle)) == len(cycle),
                "Invalid alternating-cycle vertices")
        require(cycle[0] == min(cycle) and not seen_vertices & set(cycle),
                "Cycles overlap or have noncanonical starting vertex")
        starts.append(cycle[0])
        seen_vertices.update(cycle)
        cycle_removed.update(canonical(cycle[i], cycle[i + 1]) for i in range(0, len(cycle), 2))
        cycle_added.update(canonical(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(1, len(cycle), 2))
    require(starts == sorted(starts), "Alternating cycles are not sorted")
    require(cycle_removed == removed and cycle_added == added, "Alternating-cycle edge decomposition mismatch")
    return tuple(sorted(len(cycle) // 2 for cycle in cycles))


def audit_against_family(candidate, native, reference):
    require(native["status"] == "COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION", "Wrong native status")
    coordinates = selected_coordinates(native["selector"])
    require(integer(native["coordinate_count"]) and native["coordinate_count"] == len(coordinates),
            "Wrong coordinate count")
    original = edge_set(candidate["overlap_edges_outer_zero_based"], 168)
    require(original == reference["original"] and tuple(coordinates) == reference["coordinates"],
            "Independent family belongs to a different candidate or selector")
    expected, counts = reference["legal"], reference["by_class"]
    require(type(native["moves"]) is list and type(native["overlap_candidates"]) is list and
            len(native["moves"]) == len(native["overlap_candidates"]), "Misaligned native output")
    actual, shapes = set(), Counter()
    for move, final in zip(native["moves"], native["overlap_candidates"]):
        size, group, kind = move["changed_edges"], move["root_group"], move["matching_class"]
        require(integer(size) and 2 <= size <= 6 and integer(group) and (group, kind) in coordinates,
                "Invalid matching move coordinate or changed-edge count")
        removed, added = edge_set(move["removed"], size), edge_set(move["added"], size)
        require(removed <= original and not added & original, "Invalid edge toggles")
        signature = (tuple(sorted(removed)), tuple(sorted(added)))
        require(signature in expected, "Move is absent from independent legal family")
        require(expected[signature] == (group, kind, size), "Wrong move metadata")
        require(signature not in actual, "Duplicate native replacement")
        actual.add(signature)
        shape = validate_cycles(move, removed, added)
        shapes[shape] += 1
        result = edge_set(final, 168)
        require(result == (original - removed) | added and result != original, "Wrong final candidate")
    require(actual == set(expected), "Native whole-matching family is incomplete")
    require(type(native["by_class"]) is list and
            sorted(native["by_class"], key=lambda row: (row["root_group"], row["matching_class"])) ==
            sorted(counts, key=lambda row: (row["root_group"], row["matching_class"])), "Per-coordinate counts differ")
    for field in ("raw_including_initial", "unchanged_count", "cap_rejected_count", "legal_count"):
        require(integer(native[field]) and native[field] == sum(row[field] for row in counts), "Wrong total: " + field)
    return dict(status="INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS", selector=native["selector"],
                raw_including_initial=native["raw_including_initial"], unchanged_count=native["unchanged_count"],
                cap_rejected_count=native["cap_rejected_count"], legal_count=len(expected), by_class=counts,
                unrestricted_matchings_independently_enumerated=10395 * len(coordinates),
                initial_full99_pair_caps_checked=4851, initial_own_label_quotas_checked=336,
                changed_pair_constraints_checked=reference["pair_checks"],
                own_label_quotas_checked=reference["quota_checks"],
                alternating_cycle_shape_counts=[dict(changed_edges_per_cycle=list(shape), count=count)
                                                for shape, count in sorted(shapes.items())],
                final_labeled_edge_set_equality_checked=True,
                method="Independent unrestricted recursive perfect matchings, support-domain filtering, full99 Python set neighborhoods on affected pairs, exact own-label quotas, complete final-set equality, and alternating-cycle decomposition checks.",
                scope="Complete only for the selected same-sign coordinate replacements at this one labeled base K. Initial K omitted once per coordinate; multiple cycles and five/six changed edges included. No cross-coordinate changes, cross matchings, local-star/AC proof, LP feasibility, or completed graph claim.")


def audit(candidate, native):
    reference = enumerate_family(candidate, selected_coordinates(native["selector"]))
    return audit_against_family(candidate, native, reference)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--native-source", type=Path, default=ROOT / "acceleration/overlap_matching_neighbors.rs")
    parser.add_argument("--native-binary", type=Path, default=ROOT / "acceleration/build/overlap_matching_neighbors.exe")
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve prior audit")
    paths = (args.candidate, args.input, args.native, Path(__file__), ROOT / "acceleration/audit_certificate.py",
             args.native_source, args.native_binary)
    bindings = {str(path): sha256(path.read_bytes()).hexdigest() for path in paths}
    candidate, native = (json.loads(p.read_bytes()) for p in (args.candidate, args.native))
    tokens = args.input.read_text(encoding="ascii").split()
    require(len(tokens) == 338 and tokens[:2] == ["C99OVERLAPS1", "1"], "Wrong native input shape")
    input_edges = [list(map(int, tokens[i:i + 2])) for i in range(2, 338, 2)]
    require(edge_set(input_edges, 168) == edge_set(candidate["overlap_edges_outer_zero_based"], 168),
            "Candidate/input mismatch")
    started = time.perf_counter()
    result = audit(candidate, native)
    result.update(inputs_sha256=bindings, elapsed_seconds=time.perf_counter() - started)
    require(all(sha256(path.read_bytes()).hexdigest() == bindings[str(path)] for path in paths),
            "Input/source changed during audit")
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("inputs_sha256", "by_class")}))


if __name__ == "__main__":
    main()

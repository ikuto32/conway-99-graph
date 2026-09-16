"""Independent enumeration and semantic capacity-cut audit of 677 K trades.

Only Python's standard library is used. Neither trade/cut producers nor
solver/model builders are imported. Every inequality is reconstructed from
the actual 99-vertex fixed adjacency graph and semantic multiplier coordinates.
"""

from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time


TRADE_PATH = Path("scratch_follow_overlap_trades.json")
COMPRESSION_PATH = Path("scratch_resume_integral_compression.json")
SOURCE_PATHS = [Path("scratch_resume_overlap_lift.json")] + [
    Path(f"scratch_next_overlap_alternatives_r{i}.json") for i in range(4)
]
OUTPUT = Path("scratch_follow_overlap_trades_audit.json")
REPORT = Path("scratch_follow_overlap_trades_audit.md")
EXPECTED_COUNTS = [134, 129, 142, 145, 127]

# Derive the outer vertices from unordered pairs of root-neighborhood labels.
LABELS = sorted(((a, b) for a in range(14) for b in range(a + 1, 14)
                 if a // 2 != b // 2), key=lambda pair: (pair[0] // 2, pair[1] // 2, pair))
SUPPORTS = [frozenset(s // 2 for s in pair) for pair in LABELS]
FIBRES = sorted(set(tuple(sorted(support)) for support in SUPPORTS))
FIBRE_ID = [FIBRES.index(tuple(sorted(support))) for support in SUPPORTS]
LABEL_TO_VERTEX = {pair: i for i, pair in enumerate(LABELS)}
assert len(LABELS) == 84 and len(FIBRES) == 21
assert FIBRE_ID == [i // 4 for i in range(84)]
ALL_PAIRS = list(combinations(range(99), 2))
UNKNOWN = [(a + 15, b + 15) for a, b in combinations(range(84), 2)
           if SUPPORTS[a].isdisjoint(SUPPORTS[b])]
assert len(UNKNOWN) == 1680
UNKNOWN_ID = [[-1] * 99 for _ in range(99)]
for index, (u, v) in enumerate(UNKNOWN):
    UNKNOWN_ID[u][v] = UNKNOWN_ID[v][u] = index


def load(path):
    return json.loads(path.read_bytes())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def pair(u, v):
    return (u, v) if u < v else (v, u)


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def add(rows, u, v):
    rows[u] |= 1 << v
    rows[v] |= 1 << u


BASE = [0] * 99
for symbol in range(14):
    add(BASE, 0, symbol + 1)
for symbol in range(0, 14, 2):
    add(BASE, symbol + 1, symbol + 2)
for outer, labels in enumerate(LABELS):
    for symbol in labels:
        add(BASE, outer + 15, symbol + 1)
assert sum(row.bit_count() for row in BASE) // 2 == 189


def build_graph(edges):
    rows = BASE.copy()
    assert len(edges) == 168
    for u, v in edges:
        assert type(u) is int and type(v) is int and 0 <= u < v < 84
        assert len(SUPPORTS[u] & SUPPORTS[v]) == 1
        add(rows, u + 15, v + 15)
    assert Counter(row.bit_count() for row in rows) == {14: 15, 6: 84}
    assert sum(row.bit_count() for row in rows) // 2 == 357
    return rows


def block_totals(edges):
    return Counter(pair(FIBRE_ID[u], FIBRE_ID[v]) for u, v in edges)


def quotas_pass(rows):
    # Root-label vertices keep their complete neighborhoods in the partial
    # graph. Subtract the fixed root-label contribution to count K neighbors.
    for u in range(84):
        outer_neighbors = rows[u + 15] & ~((1 << 15) - 1)
        for symbol in range(14):
            count = (outer_neighbors & BASE[symbol + 1]).bit_count()
            if symbol // 2 in SUPPORTS[u]:
                if count != 1:
                    return False
            elif count > 2:
                return False
    return True


def caps_pass(rows):
    return all((rows[u] & rows[v]).bit_count() <= 2 - ((rows[u] >> v) & 1)
               for u, v in ALL_PAIRS)


def graph_hash(rows):
    edges = [[u, v] for u, v in ALL_PAIRS if (rows[u] >> v) & 1]
    assert len(edges) == 357
    return sha256(json.dumps(edges, separators=(",", ":")).encode()).hexdigest()


def flip(edges, mask):
    relabel = {u: LABEL_TO_VERTEX[tuple(sorted(s ^ ((mask >> (s // 2)) & 1)
                                              for s in labels))]
               for u, labels in enumerate(LABELS)}
    assert set(relabel.values()) == set(range(84))
    return frozenset(pair(relabel[u], relabel[v]) for u, v in edges)


def enumerate_trades(source):
    # Enumerate the three perfect matchings of the sorted four endpoints and
    # discard the original matching. Thus each disjoint edge pair has exactly
    # two independently generated alternatives.
    counters = Counter()
    legal = {}
    totals = block_totals(source)
    for left, right in combinations(sorted(source), 2):
        endpoints = sorted(set(left) | set(right))
        if len(endpoints) != 4:
            continue
        counters["disjoint_edge_pairs"] += 1
        removed = frozenset((left, right))
        alternatives = []
        for partner in endpoints[1:]:
            rest = [u for u in endpoints if u not in (endpoints[0], partner)]
            matching = frozenset((pair(endpoints[0], partner), pair(*rest)))
            if matching != removed:
                alternatives.append(matching)
        assert len(alternatives) == len(set(alternatives)) == 2
        for added in alternatives:
            if not source.isdisjoint(added):
                continue
            if any(len(SUPPORTS[u] & SUPPORTS[v]) != 1 for u, v in added):
                continue
            counters["overlap_and_absence_pass"] += 1
            candidate = (source - removed) | added
            if block_totals(candidate) != totals:
                continue
            counters["block_total_pass"] += 1
            rows = build_graph(candidate)
            if not quotas_pass(rows):
                continue
            counters["label_quota_pass"] += 1
            if not caps_pass(rows):
                continue
            counters["all_partial_caps_pass"] += 1
            key = (tuple(sorted(removed)), tuple(sorted(added)))
            assert key not in legal
            legal[key] = candidate
    assert counters["disjoint_edge_pairs"] == 168 * 167 // 2 - 84 * 6 == 13524
    return dict(counters), legal


def read_semantic_cuts():
    metadata_path = Path("scratch_next_overlap_semantic_map.json")
    original_path = Path("scratch_next_overlap_farkas.json")
    metadata, original = load(metadata_path), load(original_path)
    assert metadata["edge_variables"] == [[i + 1, u - 15, v - 15] for i, (u, v) in enumerate(UNKNOWN)]
    groups = []
    for number, multiplier in original["group_multipliers"].items():
        coordinate = metadata["groups"][int(number)]
        groups.append({"kind": coordinate["kind"], "coordinate": coordinate["coordinate"],
                       "multiplier": multiplier})
    specifications = [{"group_multipliers": groups,
                       "edge_upper_bound_multipliers": [
                           {"edge": [u - 15, v - 15], "multiplier": value}
                           for number, value in original["edge_upper_bound_multipliers"].items()
                           for u, v in [UNKNOWN[int(number) - 1]]]}]
    paths = [metadata_path, original_path]
    for i, source_path in enumerate(SOURCE_PATHS[1:]):
        path = Path(f"scratch_next_overlap_alternatives_r{i}_farkas.json")
        specification = load(path)
        assert specification["candidate_sha256"] == digest(source_path)
        specifications.append(specification)
        paths.append(path)
    cuts = []
    for specification in specifications:
        seen, semantic = set(), []
        for record in specification["group_multipliers"]:
            kind, coordinate, multiplier = record["kind"], record["coordinate"], record["multiplier"]
            assert len(coordinate) == 2 and all(type(value) is int for value in coordinate)
            a, b = coordinate
            assert type(multiplier) is int and multiplier != 0
            key = kind, a, b
            assert key not in seen
            seen.add(key)
            if kind == "label_quota":
                assert 0 <= a < 84 and 0 <= b < 14
                u, v = a + 15, b + 1
                # These equality coefficients are static: label-neighborhood
                # incidence is fixed before any outer-edge completion.
                terms = [UNKNOWN_ID[u][w] for w in bits(BASE[v]) if UNKNOWN_ID[u][w] >= 0]
                semantic.append((kind, u, v, multiplier, terms))
            else:
                assert kind == "linear_pair_cap" and 0 <= a < b < 84 and multiplier >= 0
                semantic.append((kind, a + 15, b + 15, multiplier, None))
        upper_seen = set()
        for record in specification["edge_upper_bound_multipliers"]:
            u, v = record["edge"]
            assert type(record["multiplier"]) is int and record["multiplier"] > 0
            assert 0 <= u < v < 84 and UNKNOWN_ID[u + 15][v + 15] >= 0
            assert (u, v) not in upper_seen
            upper_seen.add((u, v))
        cuts.append(semantic)
    return cuts, paths


def semantic_score(rows, cut):
    coefficients = [0] * len(UNKNOWN)
    rhs = 0
    for kind, u, v, weight, fixed_terms in cut:
        common = (rows[u] & rows[v]).bit_count()
        rhs += weight * (2 - ((rows[u] >> v) & 1) - common)
        if kind == "label_quota":
            for index in fixed_terms:
                coefficients[index] += weight
        else:
            index = UNKNOWN_ID[u][v]
            if index >= 0:
                coefficients[index] += weight
            for fixed, changing in ((u, v), (v, u)):
                for neighbor in bits(rows[fixed]):
                    index = UNKNOWN_ID[changing][neighbor]
                    if index >= 0:
                        coefficients[index] += weight
    lower = sum(value for value in coefficients if value < 0)
    return {"score": rhs - lower, "combined_rhs": rhs, "box_lower_bound": lower,
            "negative_coefficients": sum(value < 0 for value in coefficients)}


def main():
    started = time.monotonic()
    document, compression = load(TRADE_PATH), load(COMPRESSION_PATH)
    assert document["status"] == "FIVE_FIXED_OVERLAP_TWO_EDGE_TRADE_ENUMERATION_COMPLETE"
    assert [row["source"] for row in document["records"]] == [p.name for p in SOURCE_PATHS]
    assert compression["supports"] == [list(support) for support in FIBRES]
    c = compression["C"]
    sources = []
    for path in SOURCE_PATHS:
        assert document["input_sha256"][path.name] == digest(path)
        data = load(path)
        assert data["input_sha256"] == digest(COMPRESSION_PATH)
        listed = data["overlap_edges_outer_zero_based"]
        source = frozenset(tuple(edge) for edge in listed)
        assert len(source) == len(listed) == 168
        rows = build_graph(source)
        assert quotas_pass(rows) and caps_pass(rows)
        totals = block_totals(source)
        for f, h in combinations(range(21), 2):
            if set(FIBRES[f]) & set(FIBRES[h]):
                assert totals[f, h] == c[f][h]
        sources.append(source)
    forbidden = {flip(source, mask) for source in sources for mask in range(128)}
    assert len(forbidden) == 640
    cuts, certificate_paths = read_semantic_cuts()
    results, replayed = [], []
    passing_sign_flips = 0
    for source_index, (source, expected) in enumerate(zip(sources, document["records"])):
        counters, legal = enumerate_trades(source)
        assert counters == expected["counters"]
        assert len(legal) == expected["legal_trades"] == EXPECTED_COUNTS[source_index]
        saved_keys = []
        own_scores = []
        for outcome in expected["outcomes"]:
            removed = tuple(tuple(edge) for edge in outcome["removed"])
            added = tuple(tuple(edge) for edge in outcome["added"])
            assert tuple(sorted(removed)) == removed and tuple(sorted(added)) == added
            key = removed, added
            assert key in legal and key not in saved_keys
            saved_keys.append(key)
            candidate = legal[key]
            assert candidate == (source - frozenset(removed)) | frozenset(added)
            rows = build_graph(candidate)
            assert quotas_pass(rows) and caps_pass(rows)
            assert block_totals(candidate) == block_totals(source)
            assert (candidate in forbidden) == outcome["belongs_to_saved_sign_orbits"]
            scores = [semantic_score(rows, cut) for cut in cuts]
            assert [score["score"] for score in scores] == outcome["fixed_cut_scores"]
            own = scores[source_index]
            assert own["score"] < 0
            own_scores.append(own["score"])
            image = flip(candidate, 1)
            assert flip(image, 1) == candidate
            image_rows = build_graph(image)
            assert quotas_pass(image_rows) and caps_pass(image_rows)
            assert block_totals(image) == block_totals(source)
            image_scores = [semantic_score(image_rows, cut)["score"] for cut in cuts]
            assert image_scores == outcome["one_sign_flip_scores"]
            passing_sign_flips += image not in forbidden and min(image_scores) >= 0
            replayed.append({"source_index": source_index, "removed": removed, "added": added,
                             "partial_graph_sha256": graph_hash(rows), "partial_edges": 357,
                             "own_cut": own, "fixed_cut_scores": outcome["fixed_cut_scores"],
                             "one_sign_flip_scores": image_scores})
        assert set(saved_keys) == set(legal)
        assert expected["all_rejected_by_own_fixed_cut"] is True
        assert [min(own_scores), max(own_scores)] == expected["own_cut_score_range"]
        result = {"source": expected["source"], "full_enumeration_counters": counters,
                  "alternate_matchings_checked": 2 * counters["disjoint_edge_pairs"],
                  "legal_trades": len(legal), "exact_saved_trade_set_matched": True,
                  "own_cut_score_range": [min(own_scores), max(own_scores)],
                  "all_own_cut_scores_strictly_negative": True}
        results.append(result)
        print(json.dumps(result, separators=(",", ":")), flush=True)
    assert len(replayed) == sum(EXPECTED_COUNTS) == 677
    assert len({row["partial_graph_sha256"] for row in replayed}) == 677
    assert document["selected_fixed_cut_candidate"] == (passing_sign_flips > 0)
    paths = [TRADE_PATH, COMPRESSION_PATH, *SOURCE_PATHS, *certificate_paths, Path(__file__)]
    result = {
        "status": "INDEPENDENT_FIVE_OVERLAP_TWO_EDGE_TRADE_AUDIT_PASS",
        "inputs_sha256": {str(path): digest(path) for path in paths},
        "solver_or_producer_imported": False, "numerical_solver_used": False,
        "source_assignments": 5, "source_sign_images_checked": 640,
        "disjoint_source_edge_pairs_enumerated": 5 * 13524,
        "alternate_matchings_enumerated": 5 * 2 * 13524,
        "legal_trades": 677, "actual_99_vertex_partial_graphs_replayed": 677,
        "distinct_partial_graphs_replayed": 677,
        "edges_per_partial_graph": 357, "degree_histogram_per_graph": {"14": 15, "6": 84},
        "all_overlap_compression_totals_preserved": True,
        "all_label_quotas_checked": True, "pair_caps_checked_per_graph": len(ALL_PAIRS),
        "all_exact_saved_trade_sets_matched": True,
        "own_fixed_cut_negative_scores_replayed": 677,
        "all_five_fixed_cut_scores_replayed": 677 * 5,
        "all_five_one_sign_flip_cut_scores_replayed": 677 * 5,
        "semantic_cut_rows_derived_from_actual_99_vertex_adjacency": True,
        "cut_score_convention": "combined_rhs minus sum(min(0, coefficient)) over all 1680 disjoint unknowns; saved nonnegative upper-bound multipliers omitted",
        "one_sign_flip_trade_assignments_outside_saved_orbits_passing_five_fixed_cuts": passing_sign_flips,
        "one_sign_flip_assignments_excluded_by_conjugate_own_cut": 677,
        "sign_flip_involution_replayed_for_every_trade": True,
        "per_source": results, "replayed_records": replayed,
        "elapsed_seconds": time.monotonic() - started,
        "scope": "Complete enumeration only of one legal two-edge switch from each of five prescribed K assignments. Every original trade is rejected by its own valid fixed semantic cut. No enumeration of all K, full sign/permutation cut families, disjoint completions, E0, or Conway graphs is claimed. A sign-flipped assignment passing five fixed cuts is only a necessary-model witness; root audits the selected candidate separately.",
        "E72_processes_or_ledger_modified": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    table = "\n".join(f"| {row['source']} | {row['legal_trades']} | {row['own_cut_score_range'][0]} to {row['own_cut_score_range'][1]} |" for row in results)
    REPORT.write_text("\n".join([
        "# Independent overlap two-edge trade audit", "", f"Status: `{result['status']}`.", "",
        "All 135,240 alternate matchings of 67,620 disjoint source-edge pairs were independently enumerated. The legal sets match all 677 saved trades exactly, including every intermediate filter count.", "",
        "| Source | Legal trades | Exact own-cut score range |", "|---|---:|---:|", table, "",
        "Each trade was rebuilt as a 99-vertex graph with 357 fixed edges, degrees 14 on 15 vertices and 6 on 84 vertices. All overlapping compression totals, label quotas, and all 4,851 pair capacities were checked directly. The audit derives each signed quota equality and nonnegative pair-cap inequality from actual adjacency and semantic certificate coordinates; it then computes the exact box lower bound over 1,680 unknown disjoint-support edges.", "",
        "All 677 own-cut scores are negative. All five saved fixed-cut scores and all five scores after the recorded sign flip also match independent exact evaluation. All 677 sign-flipped assignments are outside the 640 saved sign images and pass the five fixed-index cuts. Reapplying the same sign flip returns each original rejected assignment, which supplies a conjugate own-cut obstruction for every one of these images. No producer or solver code was imported and no numerical solver was called.", "",
        "This exhausts a one-switch neighborhood of five fixed assignments only. It does not exclude all overlap assignments, an E0 layer, or a Conway graph. Passing five fixed cuts does not establish disjoint completion or passage of their full relabeling families. The selected sign-flip candidate is audited separately by root. E72 processes and the ledger were untouched.", "",
    ]), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in ("inputs_sha256", "per_source", "replayed_records")}, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()

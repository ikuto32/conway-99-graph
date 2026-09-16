"""Exact stronger local probe for the large E0=72 source row 248.

The existing disjoint-Gram filter coordinates the four forced-profile vectors
inside each exceptional fibre only through their column sums.  Here the
previously unmaterialized edges between *disjoint* exceptional fibres are
constructed explicitly.  A witness must simultaneously satisfy

* every unique full-Gram block total D_FG;
* one forced-C4 disjoint-neighbour profile at every low vertex;
* a simple bipartite 4 by 4 graph in every disjoint fibre block; and
* the induced-pair upper bound after all those edges have been added.

The search is finite and exact.  Passing is not an SRG construction; failure
would be a rigorous local obstruction.  Explicit passing edge witnesses are
stored so every positive result can be checked without trusting the DFS.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

import scratch_general_e79_local_audit as local79
from scratch_general_e72_q3_disjoint_gram_filter import (
    gram_disjoint_targets,
    overlap_key,
    row_geometry,
    vertex_z_options,
)


INPUT_PATH = Path("scratch_general_e72_q3_gram_fast_expansion_part_30.json")
OUTPUT_PATH = Path("scratch_general_e72_source248_local_probe.json")
SOURCE_ROW_INDEX = 248
COMPRESSION_ORBIT_INDEX = 18


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def normal_edge(left, right):
    return tuple(sorted((tuple(left), tuple(right))))


class PairUpperState:
    """Monotone exact induced-pair upper checker with rollback."""

    def __init__(self, vertices, base_edges):
        self.vertices = tuple(vertices)
        self.index = {vertex: i for i, vertex in enumerate(self.vertices)}
        self.n = len(self.vertices)
        self.adjacency = [0] * self.n
        for left, right in base_edges:
            x, y = self.index[left], self.index[right]
            assert x != y and not (self.adjacency[x] >> y) & 1
            self.adjacency[x] |= 1 << y
            self.adjacency[y] |= 1 << x
        self.target = [[0] * self.n for _ in range(self.n)]
        self.score = [[0] * self.n for _ in range(self.n)]
        for x, y in itertools.combinations(range(self.n), 2):
            target = 2 - len(set(self.vertices[x]) & set(self.vertices[y]))
            score = ((self.adjacency[x] >> y) & 1) + (
                self.adjacency[x] & self.adjacency[y]
            ).bit_count()
            assert score <= target
            self.target[x][y] = self.target[y][x] = target
            self.score[x][y] = self.score[y][x] = score

    @staticmethod
    def _pair(x, y):
        return (x, y) if x < y else (y, x)

    def add_edge(self, x: int, y: int):
        assert x != y and not (self.adjacency[x] >> y) & 1
        bumps = Counter({self._pair(x, y): 1})
        work = self.adjacency[x]
        while work:
            low = work & -work
            z = low.bit_length() - 1
            bumps[self._pair(y, z)] += 1
            work ^= low
        work = self.adjacency[y]
        while work:
            low = work & -work
            z = low.bit_length() - 1
            bumps[self._pair(x, z)] += 1
            work ^= low
        if any(
            self.score[left][right] + amount > self.target[left][right]
            for (left, right), amount in bumps.items()
        ):
            return None
        for (left, right), amount in bumps.items():
            self.score[left][right] += amount
            self.score[right][left] += amount
        self.adjacency[x] |= 1 << y
        self.adjacency[y] |= 1 << x
        return tuple(bumps.items())

    def remove_edge(self, x: int, y: int, bumps) -> None:
        assert (self.adjacency[x] >> y) & 1
        self.adjacency[x] ^= 1 << y
        self.adjacency[y] ^= 1 << x
        for (left, right), amount in bumps:
            self.score[left][right] -= amount
            self.score[right][left] -= amount

    def apply_edges(self, edges):
        trail = []
        for x, y in edges:
            bumps = self.add_edge(x, y)
            if bumps is None:
                self.rollback(trail)
                return None
            trail.append((x, y, bumps))
        return trail

    def rollback(self, trail) -> None:
        for x, y, bumps in reversed(trail):
            self.remove_edge(x, y, bumps)


def matrix_catalogue():
    """All 4 by 4 zero-one matrices, grouped by their number of ones."""

    answer = defaultdict(list)
    for mask in range(1 << 16):
        count = mask.bit_count()
        if not (2 <= count <= 5):
            continue
        row_degrees = tuple(
            ((mask >> (4 * row)) & 0xF).bit_count() for row in range(4)
        )
        column_degrees = tuple(
            sum((mask >> (4 * row + column)) & 1 for row in range(4))
            for column in range(4)
        )
        positions = tuple(
            (position // 4, position % 4)
            for position in range(16)
            if (mask >> position) & 1
        )
        answer[count].append((mask, row_degrees, column_degrees, positions))
    return {count: tuple(rows) for count, rows in answer.items()}


MATRICES = matrix_catalogue()
assert {count: len(rows) for count, rows in MATRICES.items()} == {
    2: 120,
    3: 560,
    4: 1820,
    5: 4368,
}


def vertex_profiles(
    supports,
    vertices_by_fibre,
    fibre_of,
    base_edges,
):
    neighbours = local79.neighbour_sets(tuple(fibre_of), base_edges)
    options = {}
    component = {}
    cache = {}
    for fibre, vertices in enumerate(vertices_by_fibre):
        for vertex in vertices:
            disjoint, rows = vertex_z_options(
                fibre,
                vertex,
                supports,
                vertices_by_fibre,
                fibre_of,
                neighbours,
                cache,
            )
            assert rows
            options[vertex] = tuple(rows)
            for position, other in enumerate(disjoint):
                component[(vertex, other)] = position
    return options, component


def candidate_domains(
    supports,
    vertices_by_fibre,
    vertices,
    profile_options,
    component,
    targets,
    pair_state,
):
    """Compile exact block matrices and their vertex-profile bit filters."""

    vertex_index = pair_state.index
    raw_domains = {}
    pair_domains = {}
    for (left, right), target in sorted(targets.items()):
        assert not (set(supports[left]) & set(supports[right]))
        assert target in MATRICES
        raw_candidates = []
        pair_candidates = []
        left_vertices = vertices_by_fibre[left]
        right_vertices = vertices_by_fibre[right]
        for mask, row_degrees, column_degrees, positions in MATRICES[target]:
            filters = []
            possible = True
            for vertex, other, degree in itertools.chain(
                ((left_vertices[i], right, row_degrees[i]) for i in range(4)),
                ((right_vertices[i], left, column_degrees[i]) for i in range(4)),
            ):
                position = component[(vertex, other)]
                allowed = sum(
                    1 << option_index
                    for option_index, option in enumerate(profile_options[vertex])
                    if option[position] == degree
                )
                if not allowed:
                    possible = False
                    break
                filters.append((vertex_index[vertex], allowed))
            if not possible:
                continue
            edges = tuple(
                (
                    vertex_index[left_vertices[i]],
                    vertex_index[right_vertices[j]],
                )
                for i, j in positions
            )
            candidate = (mask, edges, tuple(filters), row_degrees, column_degrees)
            raw_candidates.append(candidate)
            trail = pair_state.apply_edges(edges)
            if trail is not None:
                pair_candidates.append(candidate)
                pair_state.rollback(trail)
        key = (left, right)
        raw_domains[key] = tuple(raw_candidates)
        pair_domains[key] = tuple(pair_candidates)
    return raw_domains, pair_domains


def search_blocks(domains, profile_options, pair_state=None):
    """Find one globally profile-consistent block selection.

    With ``pair_state`` this also checks cross-block common-neighbour effects,
    not merely each block in isolation.
    """

    live = {
        pair_state.index[vertex] if pair_state is not None else vertex: (
            (1 << len(options)) - 1
        )
        for vertex, options in profile_options.items()
    }
    # In the profile-only search, candidates still use integer vertex indices.
    if pair_state is None:
        vertices = sorted(profile_options)
        index = {vertex: i for i, vertex in enumerate(vertices)}
        live = {index[vertex]: mask for vertex, mask in live.items()}

    nodes = 0

    def compatible_candidates(block, remaining_live):
        return tuple(
            candidate
            for candidate in domains[block]
            if all(remaining_live[vertex] & allowed for vertex, allowed in candidate[2])
        )

    def visit(remaining):
        nonlocal nodes
        nodes += 1
        if not remaining:
            return ()
        choices = []
        for block in remaining:
            candidates = compatible_candidates(block, live)
            if not candidates:
                return None
            choices.append((len(candidates), block, candidates))
        _, block, candidates = min(choices, key=lambda item: (item[0], item[1]))
        following = tuple(other for other in remaining if other != block)
        for candidate in candidates:
            old = []
            for vertex, allowed in candidate[2]:
                previous = live[vertex]
                updated = previous & allowed
                assert updated
                old.append((vertex, previous))
                live[vertex] = updated
            trail = ()
            if pair_state is not None:
                trail = pair_state.apply_edges(candidate[1])
            if trail is not None:
                suffix = visit(following)
                if suffix is not None:
                    if pair_state is not None:
                        pair_state.rollback(trail)
                    for vertex, previous in reversed(old):
                        live[vertex] = previous
                    return ((block, candidate),) + suffix
            if pair_state is not None and trail is not None:
                pair_state.rollback(trail)
            for vertex, previous in reversed(old):
                live[vertex] = previous
        return None

    witness = visit(tuple(sorted(domains, key=lambda block: (len(domains[block]), block))))
    return witness, nodes


def verify_witness(
    supports,
    vertices_by_fibre,
    fibre_of,
    vertices,
    base_edges,
    targets,
    profile_options,
    component,
    witness,
):
    index = {vertex: i for i, vertex in enumerate(vertices)}
    reverse = {i: vertex for vertex, i in index.items()}
    extra_edges = frozenset(
        normal_edge(reverse[x], reverse[y])
        for _, candidate in witness
        for x, y in candidate[1]
    )
    assert len(extra_edges) == sum(targets.values())
    counts = Counter()
    per_vertex = Counter()
    for left, right in extra_edges:
        f, g = fibre_of[left], fibre_of[right]
        assert f != g and not (set(supports[f]) & set(supports[g]))
        counts[tuple(sorted((f, g)))] += 1
        per_vertex[(left, g)] += 1
        per_vertex[(right, f)] += 1
    assert dict(counts) == targets
    for fibre, fibre_vertices in enumerate(vertices_by_fibre):
        disjoint = tuple(
            other
            for other in range(len(supports))
            if not (set(supports[fibre]) & set(supports[other]))
        )
        for vertex in fibre_vertices:
            degree_vector = tuple(per_vertex[(vertex, other)] for other in disjoint)
            assert degree_vector in profile_options[vertex]
            assert all(component[(vertex, other)] == i for i, other in enumerate(disjoint))
    graph = frozenset(base_edges) | extra_edges
    assert local79.induced_pair_upper(vertices, graph)
    return [
        [list(left), list(right)]
        for left, right in sorted(extra_edges)
    ]


def run(limit=None) -> None:
    document = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    assert document["status"] == "COMPLETE"
    row = next(
        row
        for row in document["rows"]
        if row["compression_orbit_index"] == COMPRESSION_ORBIT_INDEX
    )
    assert row["partition"] == [2, 2, 2, 1, 1, 1, 1, 1, 1]
    assert row["after_forced_C4_support_BP"] == 114_688
    assert row["local_graph_orbits"] == 338
    representatives = row["local_graph_representatives"]
    if limit is not None:
        representatives = representatives[:limit]

    supports, vertices_by_fibre, fibre_of, W = row_geometry(row)
    vertices = tuple(sorted(fibre_of))
    target_cache = {}
    profile_ids = {}
    results = []
    passed_profile = passed_pair = 0
    raw_profile = raw_pair = 0
    individual_pair_nonempty = individual_pair_raw = 0
    q_pair = Counter()
    for number, representative in enumerate(representatives):
        base_edges = frozenset(
            normal_edge(left, right) for left, right in representative["edges"]
        )
        key = overlap_key(supports, fibre_of, base_edges)
        if key not in target_cache:
            targets, detail = gram_disjoint_targets(
                row, representative, supports, W
            )
            assert targets not in (None, False)
            target_cache[key] = (targets, detail)
        targets, detail = target_cache[key]
        target_tuple = tuple((left, right, value) for (left, right), value in sorted(targets.items()))
        if target_tuple not in profile_ids:
            profile_ids[target_tuple] = len(profile_ids)

        profiles, component = vertex_profiles(
            supports, vertices_by_fibre, fibre_of, base_edges
        )
        pair_state = PairUpperState(vertices, base_edges)
        raw_domains, pair_domains = candidate_domains(
            supports,
            vertices_by_fibre,
            vertices,
            profiles,
            component,
            targets,
            pair_state,
        )
        raw_domain_sizes = {block: len(values) for block, values in raw_domains.items()}
        pair_domain_sizes = {block: len(values) for block, values in pair_domains.items()}
        profile_witness = profile_nodes = None
        if all(raw_domain_sizes.values()):
            profile_witness, profile_nodes = search_blocks(raw_domains, profiles)
        profile_pass = profile_witness is not None
        no_empty_block = all(pair_domain_sizes.values())
        if no_empty_block:
            individual_pair_nonempty += 1
            individual_pair_raw += representative["orbit_size"]
        witness = nodes = None
        if no_empty_block:
            witness, nodes = search_blocks(pair_domains, profiles, pair_state)
        pair_pass = witness is not None
        if pair_pass:
            assert profile_pass
            witness_edges = verify_witness(
                supports,
                vertices_by_fibre,
                fibre_of,
                vertices,
                base_edges,
                targets,
                profiles,
                component,
                witness,
            )
        else:
            witness_edges = None
        mass = representative["orbit_size"]
        if profile_pass:
            passed_profile += 1
            raw_profile += mass
        if pair_pass:
            passed_pair += 1
            raw_pair += mass
            q_pair[representative["Q"]] += mass
        results.append(
            {
                "representative_number": number,
                "mask_hex": representative["mask_hex"],
                "orbit_size": mass,
                "Q": representative["Q"],
                "Gram_D_profile_id": profile_ids[target_tuple],
                "forced_profile_option_counts": {
                    str(list(vertex)): len(options)
                    for vertex, options in sorted(profiles.items())
                },
                "block_matrix_counts_before_pair_upper": {
                    f"{left}-{right}": raw_domain_sizes[(left, right)]
                    for left, right in sorted(raw_domain_sizes)
                },
                "block_matrix_counts_after_individual_pair_upper": {
                    f"{left}-{right}": pair_domain_sizes[(left, right)]
                    for left, right in sorted(pair_domain_sizes)
                },
                "joint_profile_block_domains_nonempty": profile_pass,
                "profile_only_DFS_nodes": profile_nodes,
                "full_disjoint_exceptional_pair_upper_witness": pair_pass,
                "DFS_nodes": nodes,
                "base_local_edges": representative["edges"] if pair_pass else None,
                "witness_disjoint_exceptional_edges": witness_edges,
            }
        )

    profile_rows = [None] * len(profile_ids)
    for values, profile_id in profile_ids.items():
        profile_rows[profile_id] = {
            "profile_id": profile_id,
            "disjoint_D": [list(item) for item in values],
            "representative_orbits": sum(
                result["Gram_D_profile_id"] == profile_id for result in results
            ),
            "raw_orbit_mass": sum(
                result["orbit_size"]
                for result in results
                if result["Gram_D_profile_id"] == profile_id
            ),
        }

    complete = limit is None
    if complete:
        assert len(results) == 338
        assert sum(item["orbit_size"] for item in results) == 114_688
    output = {
        "status": "COMPLETE" if complete else "PARTIAL_PROBE",
        "scope": (
            "source row 248: explicit disjoint-exceptional realization of full "
            "Gram totals, forced vertex profiles, and induced-pair upper"
        ),
        "input": {"path": str(INPUT_PATH), "sha256": sha256(INPUT_PATH)},
        "source_row_index": SOURCE_ROW_INDEX,
        "partition_index": 30,
        "compression_orbit_index": COMPRESSION_ORBIT_INDEX,
        "partition": row["partition"],
        "exceptional_supports": row["exceptional_supports"],
        "claim_boundary": (
            "A passing witness proves only that these local necessary conditions "
            "do not exclude the representative; it does not construct the other "
            "63 low vertices or a 99-vertex SRG."
        ),
        "summary": {
            "representatives_checked": len(results),
            "input_raw_orbit_mass": sum(item["orbit_size"] for item in results),
            "distinct_full_Gram_D_profiles": len(profile_rows),
            "profile_block_nonempty_representatives": passed_profile,
            "profile_block_nonempty_raw_mass": raw_profile,
            "individual_block_pair_upper_nonempty_representatives": (
                individual_pair_nonempty
            ),
            "individual_block_pair_upper_nonempty_raw_mass": individual_pair_raw,
            "full_pair_upper_witness_representatives": passed_pair,
            "full_pair_upper_witness_raw_mass": raw_pair,
            "full_pair_upper_witness_Q_histogram": {
                str(q): value for q, value in sorted(q_pair.items())
            },
            "all_positive_results_independently_rechecked": True,
            "all_4_by_4_matrices_exhaustively_enumerated": True,
            "DFS_has_no_node_or_time_cutoff": True,
            "failure_breakdown": {
                "some_individual_disjoint_block_impossible": (
                    len(results) - individual_pair_nonempty
                ),
                "individual_blocks_possible_but_no_joint_realization": (
                    individual_pair_nonempty - passed_pair
                ),
            },
            "passing_orbit_size_histogram": {
                str(size): count
                for size, count in sorted(
                    Counter(
                        item["orbit_size"]
                        for item in results
                        if item["full_disjoint_exceptional_pair_upper_witness"]
                    ).items()
                )
            },
        },
        "Gram_D_profiles": profile_rows,
        "representatives": results,
    }
    atomic_json(OUTPUT_PATH, output)
    print(json.dumps({"status": output["status"], **output["summary"]}), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    run(args.limit)


if __name__ == "__main__":
    main()

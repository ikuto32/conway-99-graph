"""Exact local-representative audit of the source-133 sign condition (27)."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


INPUT = Path("scratch_general_e72_q3_fast_expansion_part_27.json")
OUTPUT = Path("scratch_theory_e72_k23_exception_sign_filter.json")
SUPPORTS = ((0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4))
FIBRE = {support: index for index, support in enumerate(SUPPORTS)}


def vertex_index(label):
    left, right = label
    support = (left // 2, right // 2)
    fibre = FIBRE[support]
    local = 2 * (left % 2) + right % 2
    return 4 * fibre + local


def adjacency(rep):
    result = [set() for _ in range(24)]
    for left, right in rep["edges"]:
        x, y = vertex_index(left), vertex_index(right)
        result[x].add(y)
        result[y].add(x)
    return result


def regular_signs(graph):
    epsilon = {}
    for x in range(24):
        fibre = x // 4
        bottom = fibre % 3
        internal = [y for y in graph[x] if y // 4 == fibre]
        same = [y for y in graph[x]
                if y // 4 != fibre and (y // 4 < 3) == (fibre < 3)]
        vertical_fibre = fibre + 3 if fibre < 3 else fibre - 3
        vertical = [y for y in graph[x] if y // 4 == vertical_fibre]
        if (len(internal), len(same), len(vertical)) != (1, 1, 1):
            return None
        same_bottom = (same[0] // 4) % 3
        # w_i=u_(i+1)-u_(i+2), cyclically.  On A_i, same target i+1
        # gives +w_i; on B_i the sign is reversed.
        positive_target = (bottom + 1) % 3
        sign = 1 if same_bottom == positive_target else -1
        epsilon[x] = sign if fibre < 3 else -sign
    assert all(sum(epsilon[x] for x in range(4 * f, 4 * f + 4)) == 0
               for f in range(6))
    return epsilon


def main():
    raw = INPUT.read_bytes()
    data = json.loads(raw)
    assert data["partition_index"] == 27
    row = data["rows"][0]
    assert row["compression_orbit_index"] == 0
    total_regular = Counter()
    total_regular_weight = Counter()
    passing = Counter()
    passing_weight = Counter()
    failing_vertex_histogram = Counter()
    controls = {}
    for rep_index, rep in enumerate(row["local_graph_representatives"]):
        graph = adjacency(rep)
        epsilon = regular_signs(graph)
        if epsilon is None:
            continue
        q_value = int(rep["Q"])
        total_regular[q_value] += 1
        total_regular_weight[q_value] += int(rep["orbit_size"])
        failures = []
        signed_sums = []
        for x in range(24):
            fibre = x // 4
            internal = next(y for y in graph[x] if y // 4 == fibre)
            vertical_fibre = fibre + 3 if fibre < 3 else fibre - 3
            vertical = next(y for y in graph[x] if y // 4 == vertical_fibre)
            value = epsilon[x] + epsilon[internal] + epsilon[vertical]
            signed_sums.append(value)
            if abs(value) != 1:
                failures.append(x)
        failing_vertex_histogram[len(failures)] += 1
        if failures:
            controls.setdefault(f"Q{q_value}_fail", {
                "representative_index": rep_index,
                "failing_vertices": failures,
                "signed_sums": signed_sums,
            })
            continue
        assert Counter(signed_sums) == Counter({-1: 12, 1: 12})
        passing[q_value] += 1
        passing_weight[q_value] += int(rep["orbit_size"])
        controls.setdefault(f"Q{q_value}_pass", {
            "representative_index": rep_index,
            "signed_sums": signed_sums,
        })

    assert sum(total_regular.values()) == 8004
    assert total_regular == Counter({12: 933, 6: 2047, 8: 2512, 4: 2512})
    assert passing == Counter({12: 90, 6: 354, 8: 230, 4: 259})
    assert passing_weight == Counter({12: 8000, 6: 93568, 8: 28800, 4: 34560})
    result = {
        "status": "EXACT_EXCEPTION_SIGN_FILTER_VERIFIED",
        "input": str(INPUT),
        "input_sha256": hashlib.sha256(raw).hexdigest().upper(),
        "condition": "abs(eps_x+eps_internal+eps_vertical)=1 at all 24 vertices",
        "regular_overlap_orbits": sum(total_regular.values()),
        "regular_labelled_overlap_mass": sum(total_regular_weight.values()),
        "passing_overlap_orbits": sum(passing.values()),
        "passing_labelled_overlap_mass": sum(passing_weight.values()),
        "rejected_overlap_orbits": sum(total_regular.values()) - sum(passing.values()),
        "by_Q": {
            str(q): {
                "input_orbits": total_regular[q],
                "input_labelled_mass": total_regular_weight[q],
                "passing_orbits": passing[q],
                "passing_labelled_mass": passing_weight[q],
            }
            for q in sorted(total_regular)
        },
        "failing_vertex_count_histogram": {
            str(key): value for key, value in sorted(failing_vertex_histogram.items())
        },
        "controls": controls,
        "claim_boundary": (
            "Exact filter of the stored exceptional internal/overlap graph orbits. "
            "It is a necessary consequence of the analytic q recurrence, not a "
            "full-graph exclusion."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(OUTPUT), **result}, sort_keys=True))


if __name__ == "__main__":
    main()

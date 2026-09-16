"""Normalize the independently generated E73 Q>=4 port census.

The output is a thin, assertion-heavy compatibility layer for the generic
completion/local-expansion engines.  It neither adds nor removes a feasible
state tuple: all 295 support rows are checked, and the 58 positive rows are
copied verbatim apart from field-name normalization.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path

from scratch_general_e75_local_counts import assignment_diagonal_count


INPUT = Path("scratch_root_e73_q4_port_census.json")
OUTPUT = Path("scratch_general_e73_q4_port_feasible_states.json")


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    raw = INPUT.read_bytes()
    source = json.loads(raw)
    assert source["status"] == "COMPLETE"
    assert len(source["rows"]) == source["summary"]["input_support_orbits"] == 295
    rows = []
    global_q = Counter()
    for source_row_index, row in enumerate(source["rows"]):
        states = row["feasible_state_indices"]
        feasible = int(row["locally_port_feasible_Q_at_least_4_assignments"])
        assert len(states) == feasible
        recomputed = Counter(
            assignment_diagonal_count(row["exceptional_supports"], state)
            for state in states
        )
        recorded = Counter(
            {int(key): int(value) for key, value in row["feasible_Q_histogram"].items()}
        )
        assert recomputed == recorded
        assert all(q >= 4 for q in recomputed)
        if not feasible:
            continue
        normalized = dict(row)
        normalized["source_row_index"] = source_row_index
        normalized["labelled_fibre_state_assignments_covered"] = row[
            "Q_at_least_4_assignments_covered"
        ]
        normalized["locally_port_feasible_assignments"] = feasible
        normalized["Q_by_feasible_state"] = [
            assignment_diagonal_count(row["exceptional_supports"], state)
            for state in states
        ]
        rows.append(normalized)
        global_q.update(recomputed)
    expected_q = Counter({4: 708, 5: 144, 6: 104, 7: 16, 8: 8})
    assert len(rows) == 58
    assert sum(len(row["feasible_state_indices"]) for row in rows) == 980
    assert global_q == expected_q
    result = {
        "status": "COMPLETE",
        "model": "exact E0=73 root-side Q>=4 port-state compatibility normalization",
        "inputs": [str(INPUT)],
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "scope": (
            "Q>=4 follows for the selected root from the separately proved and "
            "independently audited root-side bound C<=69 together with E0=C+Q=73"
        ),
        "coverage": {
            "input_support_rows": 295,
            "positive_support_rows": 58,
            "state_tuples_copied_exactly": 980,
            "no_WLOG_beyond_weighted_S7_quotient_in_input": True,
        },
        "summary": {
            "support_rows": 58,
            "feasible_state_assignments": 980,
            "feasible_Q_histogram": {
                str(key): value for key, value in sorted(global_q.items())
            },
        },
        "by_partition": source["by_partition"],
        "rows": rows,
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"status": "COMPLETE", **result["summary"]}))


if __name__ == "__main__":
    main()

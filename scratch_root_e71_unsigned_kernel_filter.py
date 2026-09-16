"""Exact support-diagonal Gram filter for normalized E0=71 port rows."""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path

from scratch_theory_unsigned_kernel_filter import analyze_support


INPUT = Path("scratch_root_e71_q2_port_feasible_states.json")
OUTPUT = Path("scratch_root_e71_unsigned_kernel_filter.json")


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    raw = INPUT.read_bytes()
    source = json.loads(raw)
    assert source["status"] == "COMPLETE"
    assert source["Q_condition"] == "Q>=2"
    assert source["coverage"]["positive_support_rows_copied"] == 3220
    assert source["coverage"]["state_tuples_copied_exactly"] == 599222
    rows = []
    for normalized_row_index, row in enumerate(source["rows"]):
        analysis = analyze_support(row["exceptional_supports"])
        analysis.update({
            "normalized_row_index": normalized_row_index,
            "source_row_index": row["source_row_index"],
            "partition": row["partition"],
            "compression_orbit_index": row["compression_orbit_index"],
            "support_orbit_size": row["support_orbit_size"],
            "port_feasible_state_assignments": row["locally_port_feasible_assignments"],
        })
        rows.append(analysis)
    passing = [row for row in rows if row["passes_exact_support_diagonal_psd_test"]]
    kernel_histogram = Counter(row["unsigned_incidence_kernel_dimension"] for row in rows)
    dimension_histogram = Counter(
        row["gram_diagonal_solution_dimension"] for row in rows
        if row["gram_diagonal_solution_dimension"] is not None
    )
    result = {
        "status": "COMPLETE",
        "model": "exact E0=71 support-diagonal PSD filter from Z=4(3P_f-R_f)",
        "input": str(INPUT),
        "input_sha256": hashlib.sha256(raw).hexdigest().upper(),
        "derivation": {
            "Z_diagonal": "2*delta_F",
            "Z_overlap": "-D_FG",
            "Z_disjoint": "4-D_FG",
            "psd": True,
            "kernel": "Z L=0 for the unsigned K7 edge--group incidence L",
            "factorization": "Z=W H W^T with H positive semidefinite",
        },
        "summary": {
            "input_support_rows": len(rows),
            "input_port_feasible_state_assignments": sum(
                row["port_feasible_state_assignments"] for row in rows
            ),
            "inconsistent_diagonal_systems": sum(
                not row["gram_diagonal_system_consistent"] for row in rows
            ),
            "unique_but_non_psd_systems": sum(
                row.get("unique_gram_parameter_matrix_psd") is False for row in rows
            ),
            "passing_support_rows": len(passing),
            "passing_port_feasible_state_assignments": sum(
                row["port_feasible_state_assignments"] for row in passing
            ),
            "passing_support_labelled_weight": sum(
                row["support_orbit_size"] for row in passing
            ),
            "kernel_dimension_histogram": {
                str(key): value for key, value in sorted(kernel_histogram.items())
            },
            "solution_dimension_histogram": {
                str(key): value for key, value in sorted(dimension_histogram.items())
            },
        },
        "rows": rows,
        "claim_boundary": (
            "Exact necessary support condition only. Underdetermined consistent "
            "Gram systems are retained; passage is not a graph completion."
        ),
    }
    assert result["summary"]["input_support_rows"] == 3220
    assert result["summary"]["input_port_feasible_state_assignments"] == 599222
    atomic_json(OUTPUT, result)
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()

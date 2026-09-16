"""Map the source-133 local frontier to full-SRG edge-literal assumptions."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

from scratch_general_exact_sat import coordinates


FRONTIER = Path("scratch_general_e72_source133_hf_exception_csp.json")
VERTICES = Path("scratch_general_e72_source133_pointwise_frontier.json")
FULL_BUILD = Path("scratch_root_e72_source133_balance_build.json")
LOCAL_UNSAT = Path("scratch_general_e72_source133_hf_pair_sat.json")
MACRO4_FORMAL = Path("scratch_root_e72_source133_macro4_formal_audit.json")
OUTPUT = Path("scratch_root_e72_source133_local_assumption_manifest.json")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def cnf_header(path):
    with Path(path).open("rb") as handle:
        fields = handle.readline().split()
    assert fields[:2] == [b"p", b"cnf"] and len(fields) == 4
    return int(fields[2]), int(fields[3])


def main():
    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    vertex_document = json.loads(VERTICES.read_text(encoding="utf-8"))
    full_build = json.loads(FULL_BUILD.read_text(encoding="utf-8"))
    local_unsat = json.loads(LOCAL_UNSAT.read_text(encoding="utf-8"))
    macro4 = json.loads(MACRO4_FORMAL.read_text(encoding="utf-8"))
    assert frontier["status"] == "COMPLETE"
    assert local_unsat["status"] == "COMPLETE"
    assert local_unsat["summary"]["SAT_orbits"] == 0
    assert macro4["status"] == "FORMAL_AUDIT_PASS"

    local_vertices = tuple(tuple(row) for row in vertex_document["vertex_order"])
    local_pairs = tuple(itertools.combinations(range(24), 2))
    labels, index, _variables, edge = coordinates()
    del labels
    full_vertex_indices = tuple(index[vertex] for vertex in local_vertices)
    literal_by_bit = tuple(
        edge(full_vertex_indices[left], full_vertex_indices[right])
        for left, right in local_pairs
    )
    assert len(literal_by_bit) == len(set(literal_by_bit)) == 276

    records = []
    macro_counts = Counter()
    macro_mass = Counter()
    for row in frontier["frontier"]:
        mask_hex, mass, q_value, macro = row[:4]
        mask = int(mask_hex, 16)
        assumptions = [
            variable if (mask >> bit) & 1 else -variable
            for bit, variable in enumerate(literal_by_bit)
        ]
        assert len(assumptions) == len(set(map(abs, assumptions))) == 276
        decoded = sum(1 << bit for bit, literal in enumerate(assumptions)
                      if literal > 0)
        assert decoded == mask
        disposition = (
            "LOCAL_48_VERTEX_UNSAT"
            if macro < 4 else "COVERED_BY_MACRO4_FULL_SRG_DRUP"
        )
        records.append([mask_hex, mass, q_value, macro, disposition, assumptions])
        macro_counts[macro] += 1
        macro_mass[macro] += mass

    assert sum(macro_counts[m] for m in range(4)) == 5_138
    assert sum(macro_mass[m] for m in range(4)) == 1_129_056
    assert macro_counts[4] == 148 and macro_mass[4] == 38_016
    full_cnf = Path(full_build["cnf"])
    assert sha256(full_cnf) == full_build["cnf_sha256"]
    full_variables, full_clauses = cnf_header(full_cnf)
    assert (full_variables, full_clauses) == (
        full_build["variables"], full_build["clauses"]
    )
    result = {
        "status": "FULL_SRG_ASSUMPTION_MANIFEST_COMPLETE",
        "model": "source133 canonical local masks as complete exceptional-edge assumptions",
        "inputs": {
            str(path): sha256(path)
            for path in (FRONTIER, VERTICES, FULL_BUILD, LOCAL_UNSAT, MACRO4_FORMAL)
        },
        "full_SRG_CNF": str(full_cnf),
        "full_SRG_CNF_sha256": sha256(full_cnf),
        "full_SRG_variables": full_variables,
        "full_SRG_clauses": full_clauses,
        "local_vertex_order": [list(row) for row in local_vertices],
        "local_mask_encoding": (
            "bit i corresponds to combinations(local_vertex_order,2)[i]"
        ),
        "full_edge_variable_by_local_mask_bit": list(literal_by_bit),
        "record_fields": [
            "canonical_mask_hex", "labelled_orbit_size", "Q",
            "state_macro_number", "disposition", "276_full_CNF_edge_literals",
        ],
        "summary": {
            "records": len(records),
            "orbit_mass": sum(row[1] for row in records),
            "regular_local_UNSAT_records": sum(macro_counts[m] for m in range(4)),
            "regular_local_UNSAT_mass": sum(macro_mass[m] for m in range(4)),
            "macro4_formally_excluded_records": macro_counts[4],
            "macro4_formally_excluded_mass": macro_mass[4],
            "per_macro_records": {
                str(macro): macro_counts[macro] for macro in sorted(macro_counts)
            },
            "per_macro_mass": {
                str(macro): macro_mass[macro] for macro in sorted(macro_mass)
            },
        },
        "records": records,
        "replay": (
            "For record r, solve full_SRG_CNF under assumptions r[5]. Any SAT "
            "model must be checked with scratch_general_exact_sat.verify. The "
            "current manifest has no unresolved source133 record: regular "
            "records fail a stronger local necessary CNF and macro4 has a "
            "checked full-SRG DRUP certificate."
        ),
    }
    OUTPUT.write_text(json.dumps(result, separators=(",", ":")) + "\n",
                      encoding="utf-8")
    print(json.dumps({"path": str(OUTPUT), **result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()

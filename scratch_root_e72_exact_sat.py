"""Build the exact selected-root E0=72 search CNF.

The base formula already imposes the self-contained root choice S<=69.
This adds E0=72 exactly over all 126 same-fibre edge variables.  A SAT
answer is an unconditional candidate and must still pass the 99-vertex
verifier.  An UNSAT certificate would exclude only the E0=72 branch.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scratch_general_exact_sat import coordinates
from scratch_root_side_bound_sat import header, sha256


INPUT_CNF = Path("scratch_root_side_le69.cnf")
INPUT_META = Path("scratch_root_side_le69_build.json")
OUTPUT_CNF = Path("scratch_root_side69_e0eq72.cnf")
OUTPUT_META = Path("scratch_root_side69_e0eq72_build.json")


def local_variables() -> list[int]:
    labels, _index, variables, _edge = coordinates()
    local = []
    for (u, v), variable in variables.items():
        support_u = tuple(sorted(symbol // 2 for symbol in labels[u]))
        support_v = tuple(sorted(symbol // 2 for symbol in labels[v]))
        if support_u == support_v:
            local.append(variable)
    assert len(local) == 126 and len(set(local)) == 126
    return sorted(local)


def main() -> None:
    from pysat.card import CardEnc, EncType

    input_meta = json.loads(INPUT_META.read_text(encoding="utf-8"))
    input_hash = sha256(INPUT_CNF)
    input_variables, input_clauses = header(INPUT_CNF)
    assert input_hash == input_meta["cnf_sha256"]
    assert (input_variables, input_clauses) == (
        input_meta["variables"], input_meta["clauses"]
    )
    local = local_variables()
    card = CardEnc.equals(
        local, bound=72, top_id=input_variables, encoding=EncType.seqcounter
    )
    variables = max(input_variables, card.nv)
    clauses = input_clauses + len(card.clauses)
    with OUTPUT_CNF.open("w", encoding="ascii", newline="\n") as target:
        target.write(f"p cnf {variables} {clauses}\n")
        with INPUT_CNF.open("r", encoding="ascii") as source:
            next(source)
            for line in source:
                target.write(line)
        for clause in card.clauses:
            target.write(" ".join(map(str, clause)) + " 0\n")
    assert header(OUTPUT_CNF) == (variables, clauses)
    assert sum(1 for _ in OUTPUT_CNF.open("r", encoding="ascii")) == clauses + 1

    side_audit = Path("scratch_root_side_bound_selfcontained_audit.json")
    side_payload = json.loads(side_audit.read_text(encoding="utf-8"))
    assert side_payload["ok"] is True
    assert "S(r)<=69" in side_payload["conclusion"]
    result = {
        "status": "BUILT_EXACT_SEARCH",
        "model": "exact rooted CNF with self-contained S<=69 and E0=72",
        "input_cnf": str(INPUT_CNF),
        "input_cnf_sha256": input_hash,
        "side_bound_audit": str(side_audit),
        "side_bound_audit_sha256": hashlib.sha256(side_audit.read_bytes()).hexdigest().upper(),
        "side_bound": 69,
        "e0_equality": 72,
        "implied_Q_lower_bound": 3,
        "e0_variable_count": len(local),
        "e0_variables": local,
        "cardinality_encoding": "PySAT sequential-counter equality",
        "added_variables": variables - input_variables,
        "added_clauses": len(card.clauses),
        "variables": variables,
        "clauses": clauses,
        "cnf_sha256": sha256(OUTPUT_CNF),
        "claim_boundary": (
            "SAT must be decoded and checked on all 99 vertices. UNSAT excludes "
            "only selected-root E0=72 and requires an independently checked proof."
        ),
    }
    OUTPUT_META.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

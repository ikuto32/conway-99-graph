"""Add propagation-complete AND definitions to the rooted search CNF.

The base exact encoding contains one helper z(u,v,w) for every potential
outer common neighbour and the implication

    edge(u,w) & edge(v,w) -> z(u,v,w).

Global row-count identities make the converse implications semantically
redundant in every satisfying edge assignment.  Adding ``z -> edge(u,w)``
and ``z -> edge(v,w)`` therefore preserves precisely the same graph models
while making unit propagation substantially stronger.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
import time

from scratch_general_exact_sat import coordinates
from scratch_root_side_bound_sat import header, sha256


INPUT = Path("scratch_root_side69_e0le73.cnf")
INPUT_META = Path("scratch_root_side69_e0le73_build.json")
BASE_META = Path("scratch_general_exact_build.json")
OUTPUT = Path("scratch_root_side69_e0le73_equiv.cnf")
OUTPUT_META = Path("scratch_root_side69_e0le73_equiv_build.json")


def build():
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    started = time.monotonic()
    input_meta = json.loads(INPUT_META.read_text(encoding="utf-8"))
    base_meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    assert sha256(INPUT) == input_meta["cnf_sha256"]
    input_variables, input_clauses = header(INPUT)
    assert (input_variables, input_clauses) == (
        input_meta["variables"], input_meta["clauses"]
    )

    labels, _index, variables, edge = coordinates()
    pool = IDPool(start_from=len(variables) + 1)

    # Replay the exact allocation order of scratch_general_exact_sat.py.
    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            lits = [
                edge(u, v)
                for v, other in enumerate(labels)
                if u != v and symbol in other
            ]
            target = 1 if symbol in own or (symbol ^ 1) in own else 2
            CardEnc.equals(lits, target, vpool=pool, encoding=EncType.seqcounter)

    product_count = 84 * 83 // 2 * 82
    added_clause_count = 2 * product_count
    output_clauses = input_clauses + added_clause_count
    temporary = OUTPUT.with_suffix(OUTPUT.suffix + ".tmp")
    seen_helpers = set()
    written = 0
    with temporary.open("w", encoding="ascii", newline="\n") as target_handle:
        target_handle.write(f"p cnf {input_variables} {output_clauses}\n")
        with INPUT.open("r", encoding="ascii") as source:
            next(source)
            for line in source:
                target_handle.write(line)
        for u, v in itertools.combinations(range(84), 2):
            terms = []
            for w in range(84):
                if w in (u, v):
                    continue
                a = edge(u, w)
                b = edge(v, w)
                z = pool.id(("and", u, v, w))
                assert z not in seen_helpers
                seen_helpers.add(z)
                target_handle.write(f"{-z} {a} 0\n")
                target_handle.write(f"{-z} {b} 0\n")
                written += 2
                terms.append(z)
            terms.append(edge(u, v))
            target_value = 2 - len(set(labels[u]).intersection(labels[v]))
            CardEnc.atmost(
                terms, target_value, vpool=pool, encoding=EncType.seqcounter
            )

    assert len(seen_helpers) == product_count == base_meta["product_variables"]
    assert written == added_clause_count
    assert pool.top == base_meta["variables"]
    assert pool.top < input_variables
    temporary.replace(OUTPUT)
    assert header(OUTPUT) == (input_variables, output_clauses)
    assert sum(1 for _ in OUTPUT.open("r", encoding="ascii")) == output_clauses + 1
    result = {
        "status": "BUILT_EQUIVALENT_PROPAGATION_STRENGTHENING",
        "model": "root S<=69,E0<=73 exact CNF with full AND equivalences",
        "input": str(INPUT),
        "input_sha256": input_meta["cnf_sha256"],
        "base_allocation_source": str(BASE_META),
        "base_allocation_source_sha256": hashlib.sha256(BASE_META.read_bytes()).hexdigest().upper(),
        "edge_variables": len(variables),
        "product_helpers_reconstructed": len(seen_helpers),
        "added_reverse_implication_clauses": written,
        "semantic_argument": (
            "Each helper already satisfies edge(u,w)&edge(v,w)->z. Outer degree "
            "12 makes the sum of actual pair left sides 6048, equal to the sum "
            "of all upper targets, so every pair inequality is tight and no z "
            "can be true unless both incident edges are true."
        ),
        "variables": input_variables,
        "clauses": output_clauses,
        "cnf_sha256": sha256(OUTPUT),
        "build_seconds": round(time.monotonic() - started, 6),
        "claim_boundary": (
            "The added clauses preserve edge models. The inherited E0<=73 "
            "restriction remains based on computational exclusions without "
            "proof logs; SAT still requires direct 99-vertex verification."
        ),
    }
    OUTPUT_META.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True), flush=True)

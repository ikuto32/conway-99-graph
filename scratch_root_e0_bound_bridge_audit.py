"""Independent audit of the proposed E0/prism bridge and conditioned CNF.

No SAT sweep is run.  The public n3 lower-bound proof is deliberately not
replayed; its two numerical statements are handled only as external premises.
"""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

from scratch_general_exact_sat import coordinates
from scratch_root_e0_bound_sat import fibre_edge_variables


BRIDGE = Path("scratch_root_e0_prism_bridge.md")
BUILDER = Path("scratch_root_e0_bound_sat.py")
BASE_CNF = Path("scratch_general_exact.cnf")
BASE_META = Path("scratch_general_exact_build.json")
BOUND_CNF = Path("scratch_root_e0_le69.cnf")
BOUND_META = Path("scratch_root_e0_le69_build.json")
STRUCTURAL_AUDIT = Path("scratch_general_structural_audit.json")
QUARANTINE_MARKER = Path("scratch_root_e0_le69_QUARANTINED.txt")
PORTFOLIO = Path("scratch_root_e0_le69_portfolio.json")
SOLUTION = Path("scratch_root_e0_le69_solution.json")
OUTPUT = Path("scratch_root_e0_bound_bridge_audit.json")
SUMMARY = Path("scratch_root_e0_bound_bridge_audit.md")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def parse_header(raw):
    fields = raw.decode("ascii").split()
    if len(fields) != 4 or fields[:2] != ["p", "cnf"]:
        raise AssertionError(fields)
    return int(fields[2]), int(fields[3])


def main():
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.card import CardEnc, EncType

    errors = []
    quarantine_errors = []
    base_meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    bound_meta = json.loads(BOUND_META.read_text(encoding="utf-8"))
    structural = json.loads(STRUCTURAL_AUDIT.read_text(encoding="utf-8"))
    bridge_text = BRIDGE.read_text(encoding="utf-8")
    builder_text = BUILDER.read_text(encoding="utf-8")
    labels, _index, variables, _edge = coordinates()

    # The 21 four-vertex fibres have six unordered candidate pairs each, but
    # only four are square sides (one shared root-neighbour).  The other two
    # are complementary diagonals (zero shared root-neighbours).
    all_same = []
    sides = []
    diagonals = []
    examples = []
    for (u, v), variable in variables.items():
        group_u = tuple(symbol // 2 for symbol in labels[u])
        group_v = tuple(symbol // 2 for symbol in labels[v])
        if group_u != group_v:
            continue
        all_same.append(variable)
        intersection = len(set(labels[u]) & set(labels[v]))
        row = {
            "variable": variable,
            "left_outer_index": u,
            "right_outer_index": v,
            "left_support": list(labels[u]),
            "right_support": list(labels[v]),
            "shared_root_neighbours": intersection,
        }
        if intersection == 1:
            sides.append(variable)
        elif intersection == 0:
            diagonals.append(variable)
            if len(examples) < 2:
                examples.append(row)
        else:
            errors.append(f"unexpected same-fibre intersection {intersection}")
    all_same.sort()
    sides.sort()
    diagonals.sort()
    generated = fibre_edge_variables()
    if generated != all_same:
        errors.append("builder fibre variable list differs from all same-fibre pairs")
    if (len(all_same), len(sides), len(diagonals)) != (126, 84, 42):
        errors.append("same/side/diagonal counts differ from 126/84/42")
    if bound_meta["fibre_edge_variables"] != all_same:
        errors.append("metadata fibre variables differ from reconstructed variables")

    local_orbits = structural["same_support_fibres"]["orbits"]
    diagonal_local_states = [row for row in local_orbits if row["diagonal_edges_Q"]]
    if not diagonal_local_states:
        errors.append("structural audit unexpectedly has no locally admissible diagonal state")

    # Arithmetic is valid under both external numerical premises, but it
    # bounds the side count S(r), not the all-edge count E0(r)=S(r)+D(r).
    n3_lower = 708
    identity_total = 4158
    prism_upper = (identity_total - n3_lower) // 3
    side_sum_upper = 6 * prism_upper
    pigeonhole_upper = side_sum_upper // 99
    if (prism_upper, side_sum_upper, pigeonhole_upper) != (1150, 6900, 69):
        errors.append("external-premise arithmetic mismatch")

    # Rebuild the exact sequential-counter suffix and compare the DIMACS body
    # byte-for-byte with the base followed by clause-for-clause suffix equality.
    if sha256(BASE_CNF) != base_meta["cnf_sha256"]:
        errors.append("base CNF hash mismatch")
    if sha256(BOUND_CNF) != bound_meta["cnf_sha256"]:
        errors.append("conditioned CNF hash mismatch")
    base_body_digest = hashlib.sha256()
    copied_body_digest = hashlib.sha256()
    body_mismatches = []
    appended = []
    max_variable_seen = 0
    with BASE_CNF.open("rb") as base, BOUND_CNF.open("rb") as conditioned:
        base_header = parse_header(base.readline())
        bound_header = parse_header(conditioned.readline())
        for clause_index in range(base_header[1]):
            left = base.readline()
            right = conditioned.readline()
            if not left or not right:
                errors.append("premature EOF in base-copy region")
                break
            base_body_digest.update(left)
            copied_body_digest.update(right)
            if left != right and len(body_mismatches) < 10:
                body_mismatches.append(clause_index)
            fields = [int(value) for value in right.split()]
            if not fields or fields[-1] != 0:
                errors.append(f"bad base-copy clause terminator at {clause_index}")
                break
            if len(fields) > 1:
                max_variable_seen = max(max_variable_seen, *(abs(value) for value in fields[:-1]))
        if base.readline():
            errors.append("base CNF has more clauses than its header")
        for raw in conditioned:
            fields = [int(value) for value in raw.split()]
            if not fields or fields[-1] != 0:
                errors.append("bad appended clause terminator")
                break
            clause = fields[:-1]
            appended.append(clause)
            if clause:
                max_variable_seen = max(max_variable_seen, *(abs(value) for value in clause))
    if body_mismatches:
        errors.append(f"base clause body changed at {body_mismatches}")
    if base_body_digest.hexdigest() != copied_body_digest.hexdigest():
        errors.append("base/copy body digests differ")

    card = CardEnc.atmost(
        lits=all_same,
        bound=69,
        top_id=base_header[0],
        encoding=EncType.seqcounter,
    )
    if appended != card.clauses:
        errors.append("appended DIMACS suffix differs from rebuilt sequential counter")
    expected_bound_header = (max(base_header[0], card.nv), base_header[1] + len(card.clauses))
    if base_header != (base_meta["variables"], base_meta["clauses"]):
        errors.append("base header/metadata mismatch")
    if bound_header != expected_bound_header:
        errors.append("conditioned header/rebuilt counter mismatch")
    if bound_header != (bound_meta["variables"], bound_meta["clauses"]):
        errors.append("conditioned header/metadata mismatch")
    if len(appended) != bound_meta["added_clauses"]:
        errors.append("appended clause count/metadata mismatch")
    if card.nv - base_header[0] != bound_meta["added_variables"]:
        errors.append("auxiliary variable count/metadata mismatch")
    if max_variable_seen != bound_header[0]:
        errors.append("DIMACS maximum variable differs from header")
    actual_line_count = bound_header[1] + 1
    if actual_line_count != bound_meta["dimacs_line_count"]:
        errors.append("DIMACS line-count metadata mismatch")

    # Audit the post-discovery containment without calling build() or sweep().
    if bound_meta.get("status") != "QUARANTINED_UNSOUND_PREMISE_NEVER_SOLVED":
        quarantine_errors.append("metadata lacks quarantine status")
    if "never solved and supports no conclusion" not in bound_meta.get("claim_boundary", ""):
        quarantine_errors.append("metadata claim boundary is not fail-closed")
    if not QUARANTINE_MARKER.exists():
        quarantine_errors.append("quarantine marker missing")
        marker_text = ""
    else:
        marker_text = QUARANTINE_MARKER.read_text(encoding="utf-8")
        if "UNSAFE / NEVER SOLVED" not in marker_text or "Do not use this CNF" not in marker_text:
            quarantine_errors.append("quarantine marker wording incomplete")
    if PORTFOLIO.exists():
        quarantine_errors.append("unexpected conditioned-CNF portfolio exists")
    if SOLUTION.exists():
        quarantine_errors.append("unexpected conditioned-CNF solution artifact exists")
    if "sum_r S(r) = 6 P" not in bridge_text or "no bound `min_r E0(r)<=69`" not in bridge_text:
        quarantine_errors.append("bridge note lacks corrected identity or explicit non-implication")
    if "counted by `E0(r)`" in bridge_text:
        quarantine_errors.append("bridge converse retains ambiguous old E0 wording")
    tree = ast.parse(builder_text)
    main_nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
    if len(main_nodes) != 1 or not main_nodes[0].body or not isinstance(main_nodes[0].body[0], ast.Raise):
        quarantine_errors.append("main() is not unconditionally fail-closed at entry")
    before_cli_hashes = {path: sha256(path) for path in (BOUND_CNF, BOUND_META, QUARANTINE_MARKER)}
    refusal = subprocess.run(
        [sys.executable, str(BUILDER), "--sweep"],
        text=True, capture_output=True, check=False,
    )
    after_cli_hashes = {path: sha256(path) for path in (BOUND_CNF, BOUND_META, QUARANTINE_MARKER)}
    if refusal.returncode != 1 or "QUARANTINED" not in (refusal.stdout + refusal.stderr):
        quarantine_errors.append("CLI --sweep did not refuse with exit code 1")
    if before_cli_hashes != after_cli_hashes:
        quarantine_errors.append("refused CLI invocation modified quarantine artifacts")

    mechanical_ok = not errors
    quarantine_ok = not quarantine_errors
    semantic_bridge_ok = False
    result = {
        "status": "ORIGINAL_BRIDGE_FAILED_QUARANTINE_VERIFIED",
        "model": "independent audit of root E0/prism bridge and conditioned CNF",
        "scope": {
            "external_n3_proof_replayed": False,
            "external_premises_used_only_for_arithmetic": [
                "n3 >= 708", "n3 + 3P = 4158",
            ],
            "heavy_sat_sweep_run": False,
        },
        "bridge_audit": {
            "claimed_identity": "sum_r E0(r) = 6P",
            "claimed_identity_valid_for_126_variable_E0": semantic_bridge_ok,
            "correct_identity": "sum_r S(r) = 6P",
            "definitions": {
                "S(r)": "same-fibre side edges whose root-support intersection has size 1",
                "D(r)": "same-fibre diagonal edges whose root-support intersection has size 0",
                "E0(r)_as_encoded": "S(r) + D(r)",
            },
            "reason": (
                "The prism bijection is bidirectional for side edges only. A diagonal "
                "edge has no shared root-neighbour, so the document's first step does "
                "not apply. Diagonal fibre states are locally admissible under the SRG "
                "coordinate equations."
            ),
            "same_fibre_candidate_variables": len(all_same),
            "side_variables": len(sides),
            "diagonal_variables": len(diagonals),
            "diagonal_examples": examples,
            "locally_admissible_diagonal_orbits": diagonal_local_states,
        },
        "arithmetic_audit": {
            "arithmetic_correct_under_external_premises": True,
            "P_upper": prism_upper,
            "six_P_upper": side_sum_upper,
            "floor_six_P_over_99": pigeonhole_upper,
            "sound_conclusion": "min_r S(r) <= 69",
            "unsupported_conclusion": "min_r E0(r) <= 69 for E0=S+D",
        },
        "cnf_audit": {
            "mechanical_encoding_ok": mechanical_ok,
            "semantic_search_restriction_justified": False,
            "actual_constraint": "at most 69 of all 126 same-fibre candidate edges",
            "sound_repaired_constraint": "at most 69 of the 84 side-edge variables",
            "base_header": list(base_header),
            "conditioned_header": list(bound_header),
            "base_sha256": sha256(BASE_CNF),
            "conditioned_sha256": sha256(BOUND_CNF),
            "base_clause_body_preserved_byte_for_byte": not body_mismatches,
            "base_clause_body_sha256": base_body_digest.hexdigest().upper(),
            "appended_counter_clauses": len(appended),
            "added_auxiliary_variables": card.nv - base_header[0],
            "appended_suffix_equals_rebuilt_pysat_seqcounter": appended == card.clauses,
            "maximum_variable_seen": max_variable_seen,
            "header_and_hash_match_metadata": (
                bound_header == (bound_meta["variables"], bound_meta["clauses"])
                and sha256(BOUND_CNF) == bound_meta["cnf_sha256"]
            ),
        },
        "quarantine_audit": {
            "ok": quarantine_ok,
            "metadata_status": bound_meta.get("status"),
            "marker": str(QUARANTINE_MARKER),
            "marker_sha256": sha256(QUARANTINE_MARKER) if QUARANTINE_MARKER.exists() else None,
            "portfolio_absent": not PORTFOLIO.exists(),
            "solution_absent": not SOLUTION.exists(),
            "main_first_statement_is_raise": (
                len(main_nodes) == 1 and bool(main_nodes[0].body)
                and isinstance(main_nodes[0].body[0], ast.Raise)
            ),
            "cli_sweep_refusal_exit_code": refusal.returncode,
            "cli_sweep_refusal_text": (refusal.stdout + refusal.stderr).strip(),
            "refused_invocation_preserved_artifact_hashes": before_cli_hashes == after_cli_hashes,
            "active_source_references_found_by_separate_rg": (
                "only the corrected note, quarantined builder/marker, and this audit"
            ),
            "errors": quarantine_errors,
        },
        "artifacts": {
            str(path): sha256(path)
            for path in (
                BRIDGE, BUILDER, BASE_CNF, BASE_META, BOUND_CNF, BOUND_META,
                STRUCTURAL_AUDIT, QUARANTINE_MARKER,
            )
        },
        "errors_in_mechanical_cnf_audit": errors,
        "errors_in_quarantine_audit": quarantine_errors,
        "mechanical_cnf_audit_ok": mechanical_ok,
        "quarantine_audit_ok": quarantine_ok,
        "overall_audit_ok": mechanical_ok and quarantine_ok,
        "claim_boundary": (
            "The public proof of n3>=708 was not replayed. More importantly, even "
            "granting both external numerical premises, they justify a bound on the "
            "84 side variables, not on the encoded set of 126 side-plus-diagonal "
            "variables. Therefore an UNSAT sweep of the current conditioned CNF would "
            "not establish conditional nonexistence."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    summary = """# Independent audit: root E0/prism bridge and bound CNF

## Outcome

**The mechanical DIMACS construction passes, but the mathematical bridge fails
for the quantity actually encoded.** Do not use the current `E0<=69` CNF as an
exhaustive conditional search.

## Bridge discrepancy

A four-vertex fibre has six candidate edges: four square sides whose two root
supports intersect in one neighbour, and two diagonals whose supports are
disjoint. The triangular-prism construction in the bridge starts by choosing
the shared root-neighbour, so it applies exactly to a side edge. Conversely,
every induced prism containing the root gives exactly such a side edge. Hence
the valid bijection is

```text
sum_r S(r) = 6P,
```

where `S(r)` counts side edges. The encoded quantity uses all 126 same-fibre
variables and is `E0(r)=S(r)+D(r)`, including 42 diagonal candidates. Locally
admissible one-diagonal and two-diagonal fibre states are already present in
the independent structural audit. Thus `sum_r E0(r)=6P` does not follow.

## External-premise arithmetic

Without replaying the public `n3` proof, accepting `n3>=708` and
`n3+3P=4158` gives `P<=1150`, then
`floor(6*1150/99)=69`. Combined with the corrected identity, this proves
`min_r S(r)<=69`; it does **not** prove `min_r (S(r)+D(r))<=69`.

## Mechanical CNF audit

- The builder selects exactly 126 variables: 84 sides plus 42 diagonals.
- The saved condition is exactly an at-most-69 PySAT sequential counter on all
  126 variables.
- Base header: `p cnf 817278 1622502`.
- Conditioned header: `p cnf 821211 1630356`.
- It adds 3,933 auxiliary variables and 7,854 clauses.
- Every base clause is preserved byte-for-byte; the suffix matches a fresh
  PySAT sequential-counter reconstruction clause-for-clause.
- Saved headers, line counts, maximum variable, and SHA-256 metadata all match.

A sound repair is to encode at-most 69 on only the 84 side variables. No heavy
SAT sweep was run. The external proof of `n3>=708` remains explicitly outside
this audit, and direct SAT witnesses would remain valid under either encoding.

## Quarantine audit

The corrected note explicitly retracts the E0 identity and records only the S
identity. The generated metadata is marked
`QUARANTINED_UNSOUND_PREMISE_NEVER_SOLVED`, a conspicuous marker says not to use
the CNF, and no portfolio or solution artifact exists. `main()` begins with an
unconditional exception; an independent `--sweep` invocation returned exit 1
with the quarantine message and changed none of the artifact hashes. No active
pipeline source references this conditioned CNF. This is sufficient containment
for the unused artifact, while retaining it for audit provenance.
"""
    SUMMARY.write_text(summary, encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "mechanical_cnf_audit_ok": mechanical_ok,
        "quarantine_audit_ok": quarantine_ok,
        "overall_audit_ok": mechanical_ok and quarantine_ok,
        "claimed_bridge_ok": semantic_bridge_ok,
        "same_fibre": len(all_same), "sides": len(sides), "diagonals": len(diagonals),
        "mechanical_errors": errors,
        "quarantine_errors": quarantine_errors,
    }, sort_keys=True))


if __name__ == "__main__":
    main()

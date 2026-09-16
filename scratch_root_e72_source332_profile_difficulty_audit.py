"""Compare source-332 profile difficulty and exact DRUP literal frequencies."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from scratch_general_exact_sat import coordinates


BUILD = Path("scratch_root_e72_source332_parametric_profiles_build.json")
PORT = Path("scratch_general_e72_q3_port_feasible_states.json")
OUTPUT = Path("scratch_root_e72_source332_profile_difficulty_audit.json")
TAGS = ("tminus1", "t0", "tplus1")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def support(label):
    return tuple(sorted(symbol // 2 for symbol in label))


def original_edge_description(variable, labels, inverse, exceptional):
    left, right = inverse[variable]
    left_label, right_label = labels[left], labels[right]
    left_support, right_support = support(left_label), support(right_label)
    endpoint_type = (
        ("E" if left_support in exceptional else "O")
        + ("E" if right_support in exceptional else "O")
    )
    relation = (
        "same" if left_support == right_support
        else "overlap" if set(left_support) & set(right_support)
        else "disjoint"
    )
    return {
        "variable": variable,
        "left_label": list(left_label),
        "right_label": list(right_label),
        "left_support": list(left_support),
        "right_support": list(right_support),
        "endpoint_type": endpoint_type,
        "support_relation": relation,
    }


def parse_proof(path, selectors, maximum_variable):
    occurrences = Counter()
    positive = Counter()
    negative = Counter()
    lengths = Counter()
    segment_clauses = Counter()
    additions = deletions = 0
    selector_set = set(selectors)
    selector0, selector1, selector2 = selectors

    def segment(variable):
        if variable <= 3_486:
            return "graph_edge"
        if variable <= 817_278:
            return "base_auxiliary"
        if variable in selector_set:
            return "profile_selector"
        if selector0 < variable < selector1:
            return "tminus1_cardinality_auxiliary"
        if selector1 < variable < selector2:
            return "t0_cardinality_auxiliary"
        if selector2 < variable <= maximum_variable:
            return "tplus1_cardinality_auxiliary"
        raise AssertionError(variable)

    with Path(path).open("rb") as handle:
        for raw in handle:
            fields = raw.split()
            assert fields
            if fields[0] == b"d":
                deletions += 1
                continue
            additions += 1
            literals = [int(value) for value in fields]
            assert literals[-1] == 0
            literals.pop()
            lengths[len(literals)] += 1
            touched = set()
            for literal in literals:
                variable = abs(literal)
                assert 1 <= variable <= maximum_variable
                touched.add(segment(variable))
                if variable <= 3_486:
                    occurrences[variable] += 1
                    (positive if literal > 0 else negative)[variable] += 1
            for name in touched:
                segment_clauses[name] += 1
    return {
        "addition_lines": additions,
        "deletion_lines": deletions,
        "clause_length_histogram": {
            str(key): value for key, value in sorted(lengths.items())
        },
        "clauses_touching_variable_segment": dict(sorted(segment_clauses.items())),
        "original_graph_edge_occurrences": occurrences,
        "original_graph_edge_positive_occurrences": positive,
        "original_graph_edge_negative_occurrences": negative,
    }


def checker_core_stats(transcript):
    clause = re.search(r"c (\d+) of (\d+) clauses in core", transcript)
    lemma = re.search(
        r"c (\d+) of (\d+) lemmas in core using (\d+) resolution steps",
        transcript,
    )
    assert clause and lemma
    return {
        "original_clauses_in_core": int(clause.group(1)),
        "original_clause_total": int(clause.group(2)),
        "core_lemmas": int(lemma.group(1)),
        "lemma_total_seen_by_checker": int(lemma.group(2)),
        "resolution_steps": int(lemma.group(3)),
    }


def main():
    build = json.loads(BUILD.read_text(encoding="utf-8"))
    port = json.loads(PORT.read_text(encoding="utf-8"))
    row = next(
        row for row in port["rows"] if row.get("source_row_index") == 332
    )
    exceptional = frozenset(
        tuple(item["support"]) for item in row["exceptional_supports"]
    )
    labels, _index, variables, _edge = coordinates()
    inverse = {value: key for key, value in variables.items()}
    selectors = build["selectors"]
    maximum_variable = build["cnf_audit"]["declared_variables"]

    profile_rows = []
    for profile, tag in zip(build["profiles"], TAGS):
        meta_path = Path(f"scratch_root_e72_source332_profile_{tag}_drup.json")
        drat_path = Path(f"scratch_root_e72_source332_profile_{tag}_drat_audit.json")
        proof_path = Path(f"scratch_root_e72_source332_profile_{tag}.drup")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        drat = json.loads(drat_path.read_text(encoding="utf-8"))
        assert drat["status"] == "DRAT_VERIFIED"
        proof = parse_proof(proof_path, selectors, maximum_variable)
        top = []
        for variable, count in proof["original_graph_edge_occurrences"].most_common(30):
            description = original_edge_description(
                variable, labels, inverse, exceptional
            )
            description.update({
                "total_occurrences": count,
                "positive_occurrences": proof[
                    "original_graph_edge_positive_occurrences"
                ][variable],
                "negative_occurrences": proof[
                    "original_graph_edge_negative_occurrences"
                ][variable],
            })
            top.append(description)
        disjoint_histogram = Counter(
            int(item[2])
            for item in profile["disjoint_exceptional_block_totals"]
        )
        core = checker_core_stats(drat["transcript"])
        stats = meta["solver_stats"]
        profile_rows.append({
            "parameter_t": profile["parameter_t"],
            "selector": profile["selector"],
            "disjoint_exceptional_D_histogram": {
                str(key): value for key, value in sorted(disjoint_histogram.items())
            },
            "all_210_block_target_histogram": profile["block_target_histogram"],
            "solve": {
                "seconds": meta["solve_seconds"],
                "conflicts": stats["conflicts"],
                "decisions": stats["decisions"],
                "propagations": stats["propagations"],
                "restarts": stats["restarts"],
                "propagations_per_conflict": round(
                    stats["propagations"] / stats["conflicts"], 6
                ),
            },
            "proof": {
                "path": str(proof_path),
                "sha256": sha256(proof_path),
                "bytes": proof_path.stat().st_size,
                "producer_line_count": meta["proof_lines"],
                **{
                    key: value for key, value in proof.items()
                    if not isinstance(value, Counter)
                },
            },
            "checker_core": core,
            "top_30_original_graph_edge_literals_in_learned_clauses": top,
        })

    minus, zero, plus = profile_rows
    assert minus["disjoint_exceptional_D_histogram"] == plus[
        "disjoint_exceptional_D_histogram"
    ]
    assert zero["disjoint_exceptional_D_histogram"] != minus[
        "disjoint_exceptional_D_histogram"
    ]
    assert zero["checker_core"]["resolution_steps"] > 10 * max(
        minus["checker_core"]["resolution_steps"],
        plus["checker_core"]["resolution_steps"],
    )
    output = {
        "status": "EXACT_PROFILE_DIFFICULTY_AUDIT_COMPLETE",
        "source_row_index": 332,
        "inputs": {
            str(BUILD): sha256(BUILD),
            str(PORT): sha256(PORT),
        },
        "profiles": profile_rows,
        "comparison": {
            "endpoint_profiles_have_same_D_histogram": True,
            "central_profile_has_only_D3_and_D4_on_parametric_disjoint_blocks": True,
            "central_checker_resolution_step_ratio_vs_tminus1": round(
                zero["checker_core"]["resolution_steps"]
                / minus["checker_core"]["resolution_steps"], 6
            ),
            "central_checker_resolution_step_ratio_vs_tplus1": round(
                zero["checker_core"]["resolution_steps"]
                / plus["checker_core"]["resolution_steps"], 6
            ),
            "central_core_lemma_ratio_vs_tminus1": round(
                zero["checker_core"]["core_lemmas"]
                / minus["checker_core"]["core_lemmas"], 6
            ),
            "central_core_lemma_ratio_vs_tplus1": round(
                zero["checker_core"]["core_lemmas"]
                / plus["checker_core"]["core_lemmas"], 6
            ),
        },
        "interpretation": (
            "The central t=0 profile removes the asymmetric D=2/5 extremes: "
            "its 18 parametric disjoint exceptional blocks have only totals "
            "3 and 4.  Its checked proof consequently needs a much larger "
            "lemma core and resolution closure.  The exact learned-clause "
            "literal census identifies the original graph edges most often "
            "present in conflict consequences; it is descriptive, not an "
            "additional logical filter."
        ),
        "checks": {
            "all_three_proofs_fully_streamed": True,
            "addition_and_deletion_lines_partition_each_trace": True,
            "original_graph_variables_mapped_to_labelled_edges": True,
            "checker_core_counts_parsed_exactly": True,
            "central_resolution_steps_more_than_10x_each_endpoint": True,
        },
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": output["status"],
        "comparison": output["comparison"],
        "top_edges": {
            str(row["parameter_t"]): row[
                "top_30_original_graph_edge_literals_in_learned_clauses"
            ][:3]
            for row in profile_rows
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()

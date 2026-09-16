"""Independent coverage and full-Gram D audit for the live E0=72 frontier.

The local expansion uses three different measures which must not be mixed:

* labelled macro coverage before the pair/BP filters;
* labelled (raw) mass after the pair/BP filters; and
* local graph orbit count.

This audit joins those layers by the immutable compression-row key, removes
the four formally excluded small partitions and the analytically excluded
K4 row (source row 134), and emits an exact SAT-priority catalogue.  Every
off-diagonal exceptional-fibre block total D_FG is included.  The sole
one-dimensional Gram family (source row 332) is expanded into its three
proved integral PSD cases.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path


MACRO_PATH = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
FRONTIER_PATH = Path("scratch_general_e72_q3_gram_frontier_local_graph_reps.json")
FULL_GRAM_PATH = Path("scratch_theory_e72_macro_full_gram.json")
PARAMETRIC_PATH = Path("scratch_theory_e72_source332_parametric_gram.json")
K4_AUDIT_PATH = Path("scratch_theory_e72_k4_analytic_audit.json")
SOURCE248_PROBE_PATH = Path("scratch_general_e72_source248_local_probe.json")
FRONTIER_D_PATH = Path("scratch_general_e72_frontier_d_profile_audit.json")
SOURCE133_BALANCE_PATH = Path("scratch_general_e72_source133_balance_crosscheck.json")
OUTPUT_PATH = Path("scratch_general_e72_remaining_frontier_audit.json")
TABLE_PATH = Path("scratch_general_e72_remaining_frontier_priority.md")

SMALL_FORMAL_PARTITIONS = frozenset((15, 19, 23, 24))
ANALYTICALLY_EXCLUDED_SOURCE_ROWS = frozenset((134,))


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def atomic_json(path: Path, value) -> None:
    atomic_text(path, json.dumps(value, indent=2) + "\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def q_json(counter: Counter) -> dict[str, int]:
    return {str(key): counter[key] for key in sorted(counter)}


def row_key(row) -> tuple[tuple[int, ...], int]:
    return tuple(row["partition"]), row["compression_orbit_index"]


def macro_gram_key(row) -> tuple:
    return (
        row["partition_index"],
        row["compression_orbit_index"],
        row["source_row_index"],
        row["state_orbit_number"],
        row["signature_stabilizer_orbit_number"],
        row["signature_stabilizer_canonical"],
    )


def pair_key(left: int, right: int) -> str:
    return f"{min(left, right)}-{max(left, right)}"


def full_d_profiles(macros, gram_rows, parametric):
    """Return complete D profiles for every raw macro entry.

    A raw entry is kept here even when it is not the stabilizer-canonical
    member: those entries certify the exact labelled D-value range.  Coverage
    is counted separately using the canonical signature-orbit entries.
    """

    grams_by_key = defaultdict(list)
    for row in gram_rows:
        grams_by_key[macro_gram_key(row)].append(row)

    param_macro = parametric["macro"]
    param_source = param_macro["source_row_index"]
    param_cases = parametric["feasible_parameters"]
    answer = defaultdict(list)
    for macro in macros:
        matches = grams_by_key[macro_gram_key(macro)]
        # A signature orbit can have several noncanonical labelled members;
        # the full-Gram producer preserves their macro-catalog order.
        assert matches, macro_gram_key(macro)
        gram = matches.pop(0)
        overlap = {
            pair_key(left, right): int(value)
            for left, right, value in macro["overlap_block_totals"]
        }
        alternatives = []
        rejected = gram["unique"] and not gram["passes_full_unique_gram_checks"]
        if rejected:
            # These are retained in the historical overlap-only macro census,
            # but the later exact full-Gram solve proves them impossible.
            # They belong only to the separately excluded small partitions.
            alternatives = []
        elif gram["unique"]:
            alternatives.append(
                {
                    pair_key(left, right): int(value)
                    for left, right, value in gram[
                        "disjoint_exceptional_block_totals"
                    ]
                }
            )
        else:
            assert macro["source_row_index"] == param_source == 332
            assert gram["solution_dimension"] == 1
            for case in param_cases:
                alternatives.append(
                    {
                        pair_key(left, right): int(value)
                        for left, right, value in case[
                            "disjoint_exceptional_block_totals"
                        ]
                    }
                )

        support_count = len(macro["exceptional_supports"])
        expected_pairs = support_count * (support_count - 1) // 2
        complete = []
        for case_number, disjoint in enumerate(alternatives):
            assert not (set(overlap) & set(disjoint))
            values = {**overlap, **disjoint}
            assert len(values) == expected_pairs
            complete.append(
                {
                    "case_number": case_number,
                    "D": {key: values[key] for key in sorted(values)},
                }
            )
        answer[macro["source_row_index"]].append(
            {
                "state_orbit_number": macro["state_orbit_number"],
                "signature_stabilizer_orbit_number": macro[
                    "signature_stabilizer_orbit_number"
                ],
                "signature_stabilizer_canonical": macro[
                    "signature_stabilizer_canonical"
                ],
                "Q": macro["Q"],
                "raw_entry_coverage": macro["labelled_state_matching_coverage"],
                "signature_orbit_coverage": (
                    macro["signature_orbit_labelled_coverage"]
                    if macro["signature_stabilizer_canonical"]
                    else 0
                ),
                "full_Gram_rejected": rejected,
                "alternatives": complete,
            }
        )
    assert all(not rows for rows in grams_by_key.values())
    return answer


def d_ranges(branches):
    values = defaultdict(set)
    for branch in branches:
        for alternative in branch["alternatives"]:
            for pair, value in alternative["D"].items():
                values[pair].add(value)
    return {
        pair: {
            "min": min(entries),
            "max": max(entries),
            "values": sorted(entries),
        }
        for pair, entries in sorted(values.items())
    }


def run() -> None:
    macro_doc = json.loads(MACRO_PATH.read_text(encoding="utf-8"))
    gram_doc = json.loads(FULL_GRAM_PATH.read_text(encoding="utf-8"))
    parametric = json.loads(PARAMETRIC_PATH.read_text(encoding="utf-8"))
    k4_audit = json.loads(K4_AUDIT_PATH.read_text(encoding="utf-8"))
    source248_probe = json.loads(SOURCE248_PROBE_PATH.read_text(encoding="utf-8"))
    frontier_d = json.loads(FRONTIER_D_PATH.read_text(encoding="utf-8"))
    source133_balance = json.loads(SOURCE133_BALANCE_PATH.read_text(encoding="utf-8"))
    # This is intentionally loaded independently from the producer summaries;
    # every representative mass identity below is recomputed from its edges.
    frontier_doc = json.loads(FRONTIER_PATH.read_text(encoding="utf-8"))

    assert macro_doc["status"] == "COMPLETE"
    assert frontier_doc["status"] == "COMPLETE"
    assert gram_doc["status"] == "COMPLETE"
    assert k4_audit["status"] == "EXACT_ARITHMETIC_VERIFIED"
    assert "source-row-134" in k4_audit["scope"]
    assert source248_probe["status"] == "COMPLETE"
    assert source248_probe["source_row_index"] == 248
    assert frontier_d["status"] == "EXACT_D_PROFILE_AGGREGATION_VERIFIED"
    assert source133_balance["status"] == "COMPLETE"
    assert source133_balance["source_row_index"] == 133

    macros = macro_doc["macro_entries"]
    assert len(macros) == macro_doc["summary"]["Gram_feasible_macro_entries"] == 177
    raw_macro_coverage = sum(
        row["labelled_state_matching_coverage"] for row in macros
    )
    canonical_macro_coverage = sum(
        row["signature_orbit_labelled_coverage"]
        for row in macros
        if row["signature_stabilizer_canonical"]
    )
    expected_macro_coverage = macro_doc["summary"]["labelled_state_matching_coverage"]
    assert raw_macro_coverage == canonical_macro_coverage == expected_macro_coverage

    key_to_sources = defaultdict(set)
    source_metadata = {}
    for row in macros:
        key_to_sources[row_key(row)].add(row["source_row_index"])
        source_metadata[row["source_row_index"]] = {
            "partition_index": row["partition_index"],
            "partition": row["partition"],
            "compression_orbit_index": row["compression_orbit_index"],
            "support_orbit_size": row["support_orbit_size"],
            "exceptional_supports": row["exceptional_supports"],
        }
    assert all(len(sources) == 1 for sources in key_to_sources.values())
    key_to_source = {key: next(iter(value)) for key, value in key_to_sources.items()}

    gram_profiles = full_d_profiles(macros, gram_doc["rows"], parametric)
    assert set(gram_profiles) == set(source_metadata)

    per_source_macro = defaultdict(lambda: {
        "raw_entries": 0,
        "canonical_macro_orbits": 0,
        "coverage": 0,
        "Q": Counter(),
    })
    for row in macros:
        item = per_source_macro[row["source_row_index"]]
        item["raw_entries"] += 1
        if row["signature_stabilizer_canonical"]:
            coverage = row["signature_orbit_labelled_coverage"]
            item["canonical_macro_orbits"] += 1
            item["coverage"] += coverage
            item["Q"][row["Q"]] += coverage

    frontier_raw = frontier_orbits = 0
    frontier_q = Counter()
    per_source_frontier = {}
    for row in frontier_doc["support_rows"]:
        source = key_to_source[row_key(row)]
        assert source not in per_source_frontier
        masks = [rep["mask_hex"] for rep in row["representatives"]]
        assert len(masks) == len(set(masks)) == row["orbit_count"]
        raw = sum(rep["orbit_size"] for rep in row["representatives"])
        q_mass = Counter()
        for rep in row["representatives"]:
            q_mass[rep["Q"]] += rep["orbit_size"]
        assert raw == row["raw_survivors"]
        assert q_json(q_mass) == row["Q_histogram"]
        per_source_frontier[source] = {
            "raw_BP_survivors": raw,
            "local_graph_orbits": row["orbit_count"],
            "Q_histogram": q_json(q_mass),
        }
        frontier_raw += raw
        frontier_orbits += row["orbit_count"]
        frontier_q.update(q_mass)
    frontier_summary = frontier_doc["summary"]
    assert frontier_raw == frontier_summary["raw_BP_survivors"]
    assert frontier_orbits == frontier_summary["local_graph_orbits"]
    assert q_json(frontier_q) == frontier_summary["Q_histogram"]
    assert frontier_d["summary"]["raw_BP_survivors"] == frontier_raw
    assert frontier_d["summary"]["local_graph_orbits"] == frontier_orbits
    surviving_d_by_source = {
        row["source_row_index"]: row for row in frontier_d["source_rows"]
    }
    assert set(surviving_d_by_source) == set(per_source_frontier)

    excluded_small_sources = {
        source
        for source, metadata in source_metadata.items()
        if metadata["partition_index"] in SMALL_FORMAL_PARTITIONS
    }
    live_sources = set(source_metadata) - excluded_small_sources
    pre_k4_sources = set(live_sources)
    live_sources -= ANALYTICALLY_EXCLUDED_SOURCE_ROWS
    assert ANALYTICALLY_EXCLUDED_SOURCE_ROWS <= pre_k4_sources
    assert all(
        branch["alternatives"]
        for source in live_sources | ANALYTICALLY_EXCLUDED_SOURCE_ROWS
        for branch in gram_profiles[source]
    )

    source_rows = []
    for source in sorted(live_sources):
        metadata = source_metadata[source]
        macro = per_source_macro[source]
        frontier = per_source_frontier.get(
            source,
            {"raw_BP_survivors": 0, "local_graph_orbits": 0, "Q_histogram": {}},
        )
        branches = gram_profiles[source]
        surviving_d = surviving_d_by_source.get(source)
        source_rows.append(
            {
                "source_row_index": source,
                **metadata,
                "raw_Gram_macro_entries": macro["raw_entries"],
                "signature_stabilizer_macro_orbits": macro[
                    "canonical_macro_orbits"
                ],
                "Gram_macro_labelled_coverage": macro["coverage"],
                "Gram_macro_Q_histogram": q_json(macro["Q"]),
                **frontier,
                "full_D_profile_alternatives": sum(
                    len(branch["alternatives"])
                    for branch in branches
                    if branch["signature_stabilizer_canonical"]
                ),
                "macro_complete_D_value_ranges": d_ranges(branches),
                "distinct_surviving_full_D_profiles": (
                    0
                    if surviving_d is None
                    else surviving_d["distinct_surviving_full_D_profiles"]
                ),
                "surviving_complete_D_value_ranges": (
                    {} if surviving_d is None else surviving_d[
                        "surviving_complete_D_value_ranges"
                    ]
                ),
                "full_D_branches": branches,
            }
        )
    source_rows.sort(
        key=lambda row: (
            -row["raw_BP_survivors"],
            -row["Gram_macro_labelled_coverage"],
            row["source_row_index"],
        )
    )

    def totals(sources):
        macro_q = Counter()
        bp_q = Counter()
        for source in sources:
            macro_q.update(per_source_macro[source]["Q"])
            bp_q.update(
                {
                    int(q): value
                    for q, value in per_source_frontier.get(source, {}).get(
                        "Q_histogram", {}
                    ).items()
                }
            )
        return {
            "source_rows": len(sources),
            "raw_Gram_macro_entries": sum(
                per_source_macro[source]["raw_entries"] for source in sources
            ),
            "signature_stabilizer_macro_orbits": sum(
                per_source_macro[source]["canonical_macro_orbits"]
                for source in sources
            ),
            "Gram_macro_labelled_coverage": sum(
                per_source_macro[source]["coverage"] for source in sources
            ),
            "Gram_macro_Q_histogram": q_json(macro_q),
            "BP_nonempty_source_rows": sum(source in per_source_frontier for source in sources),
            "raw_BP_survivors": sum(
                per_source_frontier.get(source, {}).get("raw_BP_survivors", 0)
                for source in sources
            ),
            "local_graph_orbits": sum(
                per_source_frontier.get(source, {}).get("local_graph_orbits", 0)
                for source in sources
            ),
            "BP_Q_histogram": q_json(bp_q),
        }

    k4 = totals(ANALYTICALLY_EXCLUDED_SOURCE_ROWS)
    assert k4["Gram_macro_labelled_coverage"] == 101_593_088
    assert k4["raw_BP_survivors"] == 832
    assert k4["local_graph_orbits"] == 8
    small_formal = totals(excluded_small_sources)
    assert small_formal["Gram_macro_labelled_coverage"] == 45_056
    assert small_formal["raw_Gram_macro_entries"] == 9
    assert small_formal["raw_BP_survivors"] == 0

    remaining = totals(live_sources)
    assert remaining["raw_BP_survivors"] == frontier_raw - 832
    assert remaining["local_graph_orbits"] == frontier_orbits - 8
    assert sum(row["Gram_macro_labelled_coverage"] for row in source_rows) == remaining[
        "Gram_macro_labelled_coverage"
    ]
    assert sum(row["raw_BP_survivors"] for row in source_rows) == remaining[
        "raw_BP_survivors"
    ]

    source248 = next(row for row in source_rows if row["source_row_index"] == 248)
    assert source248["Gram_macro_labelled_coverage"] == 28_344_320
    assert source248["raw_BP_survivors"] == 114_688
    assert source248["local_graph_orbits"] == 338
    probe_masks = {row["mask_hex"] for row in source248_probe["representatives"]}
    frontier248 = next(
        row
        for row in frontier_doc["support_rows"]
        if key_to_source[row_key(row)] == 248
    )
    assert probe_masks == {row["mask_hex"] for row in frontier248["representatives"]}
    probe_summary = source248_probe["summary"]
    assert probe_summary["input_raw_orbit_mass"] == source248["raw_BP_survivors"]
    assert probe_summary["representatives_checked"] == source248["local_graph_orbits"]
    source133 = next(row for row in source_rows if row["source_row_index"] == 133)
    assert source133["Gram_macro_labelled_coverage"] == 2_502_656
    assert source133["raw_BP_survivors"] == 2_502_656
    assert source133["local_graph_orbits"] == 8_060
    balance_summary = source133_balance["summary"]
    assert balance_summary["input_raw_orbit_mass"] == source133["raw_BP_survivors"]
    assert balance_summary["local_graph_orbits_checked"] == source133["local_graph_orbits"]
    assert balance_summary["counterexamples_to_macro_labelling_or_signed_edge_sum"] == 0
    assert balance_summary["balance_compatible_orbits"] == source133["local_graph_orbits"]
    assert balance_summary["balance_compatible_raw_mass"] == source133["raw_BP_survivors"]
    balance_masks = {row["mask_hex"] for row in source133_balance["representatives"]}
    frontier133 = next(
        row
        for row in frontier_doc["support_rows"]
        if key_to_source[row_key(row)] == 133
    )
    assert balance_masks == {row["mask_hex"] for row in frontier133["representatives"]}

    strong_filters = {
        133: {
            "status": "POINTWISE_BALANCE_PLUS_EXPLICIT_DISJOINT_PAIR_UPPER_CHECKED",
            "raw_survivors": balance_summary["balance_plus_pair_upper_raw_mass"],
            "local_graph_orbits": balance_summary["balance_plus_pair_upper_orbits"],
            "Q_histogram": balance_summary["balance_plus_pair_upper_Q_histogram"],
            "pointwise_balance_counterexamples": 0,
        },
        248: {
            "status": "EXPLICIT_DISJOINT_EXCEPTIONAL_PAIR_UPPER_CHECKED",
            "raw_survivors": probe_summary["full_pair_upper_witness_raw_mass"],
            "local_graph_orbits": probe_summary[
                "full_pair_upper_witness_representatives"
            ],
            "Q_histogram": probe_summary["full_pair_upper_witness_Q_histogram"],
        },
    }
    for row in source_rows:
        row["stronger_local_filter"] = strong_filters.get(
            row["source_row_index"], {"status": "NOT_RUN"}
        )
        row["current_SAT_raw_mass_upper_bound"] = (
            row["stronger_local_filter"].get("raw_survivors", row["raw_BP_survivors"])
        )
        row["current_SAT_graph_orbit_upper_bound"] = row[
            "stronger_local_filter"
        ].get("local_graph_orbits", row["local_graph_orbits"])
    source_rows.sort(
        key=lambda row: (
            -row["current_SAT_raw_mass_upper_bound"],
            -row["Gram_macro_labelled_coverage"],
            row["source_row_index"],
        )
    )

    after_source248 = {
        **remaining,
        "raw_BP_survivors": (
            remaining["raw_BP_survivors"]
            - source248["raw_BP_survivors"]
            + probe_summary["full_pair_upper_witness_raw_mass"]
        ),
        "local_graph_orbits": (
            remaining["local_graph_orbits"]
            - source248["local_graph_orbits"]
            + probe_summary["full_pair_upper_witness_representatives"]
        ),
    }
    after_q = Counter({int(q): value for q, value in remaining["BP_Q_histogram"].items()})
    after_q[6] -= source248["raw_BP_survivors"]
    after_q.update(
        {
            int(q): value
            for q, value in probe_summary["full_pair_upper_witness_Q_histogram"].items()
        }
    )
    after_source248["BP_Q_histogram"] = q_json(after_q)
    assert after_source248["raw_BP_survivors"] == 11_354_112
    assert after_source248["local_graph_orbits"] == 52_404

    current = {
        **remaining,
        "raw_BP_survivors": sum(
            row["current_SAT_raw_mass_upper_bound"] for row in source_rows
        ),
        "local_graph_orbits": sum(
            row["current_SAT_graph_orbit_upper_bound"] for row in source_rows
        ),
    }
    current_q = Counter(
        {int(q): value for q, value in remaining["BP_Q_histogram"].items()}
    )
    for source, strong in strong_filters.items():
        for q, value in per_source_frontier[source]["Q_histogram"].items():
            current_q[int(q)] -= value
        for q, value in strong["Q_histogram"].items():
            current_q[int(q)] += value
    current["BP_Q_histogram"] = q_json(current_q)
    assert current["raw_BP_survivors"] == 11_344_608
    assert current["local_graph_orbits"] == 52_370

    result = {
        "status": "EXACT_COVERAGE_VERIFIED",
        "scope": (
            "E0=72 Gram-macro and pair/BP frontier after removing formal "
            "partitions 15,19,23,24 and analytic source row 134"
        ),
        "inputs": {
            str(path): sha256(path)
            for path in (
                MACRO_PATH,
                FRONTIER_PATH,
                FULL_GRAM_PATH,
                PARAMETRIC_PATH,
                K4_AUDIT_PATH,
                SOURCE248_PROBE_PATH,
                FRONTIER_D_PATH,
                SOURCE133_BALANCE_PATH,
            )
        },
        "excluded": {
            "small_formal_partition_indices": sorted(SMALL_FORMAL_PARTITIONS),
            "small_formal_source_rows": sorted(excluded_small_sources),
            "small_formal_macro_crosscheck": small_formal,
            "analytic_source_rows": sorted(ANALYTICALLY_EXCLUDED_SOURCE_ROWS),
            "analytic_source_134_crosscheck": k4,
        },
        "global_crosschecks": {
            "all_macro_raw_coverage": raw_macro_coverage,
            "all_macro_canonical_coverage": canonical_macro_coverage,
            "all_frontier_raw_BP_survivors": frontier_raw,
            "all_frontier_local_graph_orbits": frontier_orbits,
            "all_frontier_Q_histogram": q_json(frontier_q),
            "all_macro_orbit_coverage_identities_verified": True,
            "all_frontier_row_mass_and_Q_identities_verified": True,
            "all_frontier_row_masks_unique": True,
            "all_full_D_profiles_complete": True,
        },
        "remaining_summary": remaining,
        "current_summary_after_source248_stronger_local_filter": after_source248,
        "current_summary_after_source133_and_source248_stronger_filters": current,
        "zero_BP_source_rows": sorted(live_sources - set(per_source_frontier)),
        "priority_order": (
            "descending strongest currently checked local survivor mass, then descending Gram "
            "macro coverage, then source row index"
        ),
        "source_rows": source_rows,
    }
    atomic_json(OUTPUT_PATH, result)

    active = [row for row in source_rows if row["raw_BP_survivors"]]
    lines = [
        "# E72 remaining local-frontier priority",
        "",
        "Exact ranking after formal partitions 15/19/23/24 and analytic source134 are removed.",
        "Coverage is labelled Gram-macro mass; BP mass is labelled pair∧BP survivor mass.",
        "",
        "| rank | source | part | orbit | Q | macro coverage | BP mass | current mass | current orbits | D range summary |",
        "|---:|---:|---:|---:|:---|---:|---:|---:|---:|:---|",
    ]
    for rank, row in enumerate(active, 1):
        q_values = ",".join(row["Q_histogram"].keys())
        ranges = row["surviving_complete_D_value_ranges"]
        value_sets = Counter(tuple(item["values"]) for item in ranges.values())
        d_summary = "; ".join(
            f"{list(values)}×{count}"
            for values, count in sorted(value_sets.items())
        )
        lines.append(
            "| {rank} | {source} | {part} | {orbit} | {q} | {macro:,} | "
            "{bp:,} | {current:,} | {orbits:,} | {d} |".format(
                rank=rank,
                source=row["source_row_index"],
                part=row["partition_index"],
                orbit=row["compression_orbit_index"],
                q=q_values,
                macro=row["Gram_macro_labelled_coverage"],
                bp=row["raw_BP_survivors"],
                current=row["current_SAT_raw_mass_upper_bound"],
                orbits=row["current_SAT_graph_orbit_upper_bound"],
                d=d_summary,
            )
        )
    lines.extend(
        [
            "",
            f"Active rows: {len(active)}; after the source133 and source248 stronger filters, "
            f"current raw mass: {current['raw_BP_survivors']:,}; local graph orbits: "
            f"{current['local_graph_orbits']:,}.",
            "",
            "The JSON companion contains every labelled macro branch, complete D_FG profile, "
            "and per-pair exact value set (including all three source332 parametric cases).",
        ]
    )
    atomic_text(TABLE_PATH, "\n".join(lines) + "\n")
    print(json.dumps({"status": result["status"], **remaining}), flush=True)


if __name__ == "__main__":
    run()

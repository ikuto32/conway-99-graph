"""Coverage and local-core audit for sampled source150 macros (4,0)/(7,0)."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import itertools
import json
import os
from pathlib import Path

import scratch_theory_e72_source150_norm_collision_filter as base
import scratch_theory_e72_source150_pointwise_recurrence_csp as relaxed
from scratch_general_exact_sat import coordinates


LOCAL = base.LOCAL
CATALOG = base.CATALOG
FIBRE_FILTER = relaxed.FIBRE_FILTER
M40_HEAD = Path("scratch_theory_e72_source150_sync_m40_probe16.json")
M40_TAIL = Path("scratch_theory_e72_source150_sync_m40_tail16.json")
M40_R1042 = Path("scratch_theory_e72_source150_sync_localpair_m40_r1042.json")
M40_R1052 = Path("scratch_theory_e72_source150_sync_localpair_m40_r1052.json")
M40_R16_48 = Path(
    "scratch_theory_e72_source150_sync_localpair_m40_r16_48.json"
)
M40_R48_112 = Path(
    "scratch_theory_e72_source150_sync_localpair_m40_r48_112.json"
)
M40_R112_240 = Path(
    "scratch_theory_e72_source150_sync_localpair_m40_r112_240.json"
)
M40_R240_304 = Path(
    "scratch_theory_e72_source150_sync_localpair_m40_r240_304.json"
)
M40_R304_368 = Path(
    "scratch_theory_e72_source150_sync_localpair_m40_r304_368.json"
)
M40_R368_432 = Path(
    "scratch_theory_e72_source150_sync_localpair_m40_r368_432.json"
)
M40_R432_560 = Path(
    "scratch_theory_e72_source150_sync_localpair_m40_r432_560.json"
)
M40_R560_688 = Path(
    "scratch_theory_e72_source150_sync_localpair_m40_r560_688.json"
)
M40_R688_816 = Path(
    "scratch_theory_e72_source150_sync_localpair_m40_r688_816.json"
)
M40_R816_944 = Path(
    "scratch_theory_e72_source150_sync_localpair_m40_r816_944.json"
)
M40_R944_1040 = Path(
    "scratch_theory_e72_source150_sync_localpair_m40_r944_1040.json"
)
M70_HEAD = Path("scratch_theory_e72_source150_sync_localpair_m70_probe10.json")
M70_R10_138 = Path(
    "scratch_theory_e72_source150_sync_localpair_m70_r10_138.json"
)
M70_R138_266 = Path(
    "scratch_theory_e72_source150_sync_localpair_m70_r138_266.json"
)
M70_PROJ_R266_522 = Path(
    "scratch_theory_e72_source150_sync_proj03_m70_r266_522.json"
)
M70_SUPP_R266_522 = Path(
    "scratch_theory_e72_source150_sync_localpair_m70_r266_522_projSAT.json"
)
M70_PROJ_R522_778 = Path(
    "scratch_theory_e72_source150_sync_proj03_m70_r522_778.json"
)
M70_SUPP_R522_778 = Path(
    "scratch_theory_e72_source150_sync_localpair_m70_r522_778_projSAT.json"
)
M70_PROJ_R778_1034 = Path(
    "scratch_theory_e72_source150_sync_proj03_m70_r778_1034.json"
)
M70_SUPP_R778_1034 = Path(
    "scratch_theory_e72_source150_sync_localpair_m70_r778_1034_projSAT.json"
)
M70_PROJ_R1034_1296 = Path(
    "scratch_theory_e72_source150_sync_proj03_m70_r1034_1296.json"
)
M70_SUPP_R1034_1296 = Path(
    "scratch_theory_e72_source150_sync_localpair_m70_r1034_1296_projSAT.json"
)
M70_TAIL = Path("scratch_theory_e72_source150_sync_m70_tail16.json")
CORE_M40 = Path("scratch_theory_e72_source150_sync_core_m40_r4.json")
CORE_M70 = Path("scratch_theory_e72_source150_sync_core_m70_r0.json")
OUTPUT = Path("scratch_root_e72_source150_m47_shard_audit.json")
FULL_BUILD = Path("scratch_root_e72_source150_full_gram_macro_build.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_records():
    document = load(LOCAL)
    row = next(
        item for item in document["support_rows"]
        if item["partition"] == [2, 2, 2, 2, 1, 1, 1, 1]
        and item["compression_orbit_index"] == 0
    )
    exceptional = tuple(tuple(item["support"])
                        for item in row["exceptional_supports"])
    support_to_fibre = {support: index for index, support in enumerate(exceptional)}
    overlap_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if set(exceptional[pair[0]]) & set(exceptional[pair[1]])
    )
    catalog = [entry for entry in load(CATALOG)["macro_entries"]
               if entry["source_row_index"] == 150]
    entry_by_key = {
        base.entry_key(entry, exceptional, overlap_pairs): entry
        for entry in catalog
    }
    survivor_masks = {item[0] for item in load(FIBRE_FILTER)["survivors"]}
    records = defaultdict(list)
    for representative in row["representatives"]:
        if representative["mask_hex"] not in survivor_masks:
            continue
        entry = entry_by_key[base.representative_key(
            representative["edges"], support_to_fibre, overlap_pairs
        )]
        macro = (int(entry["state_orbit_number"]),
                 int(entry["signature_stabilizer_orbit_number"]))
        records[macro].append(representative)
    assert len(records[(4, 0)]) == 1056
    assert len(records[(7, 0)]) == 1312
    return exceptional, records


def verify_artifact_inputs(document):
    for path in (LOCAL, CATALOG, FIBRE_FILTER):
        assert document["inputs"][str(path)] == sha256(path)


def result_map(document, macro, records):
    verify_artifact_inputs(document)
    assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
    assert document["summary"]["wanted_macros"] == [list(macro)]
    answer = {}
    for result in document["results"]:
        record, mask_hex, orbit_size, q, stored_macro, status = result[:6]
        representative = records[macro][record]
        assert tuple(stored_macro) == macro
        assert q == representative["Q"]
        assert mask_hex == representative["mask_hex"]
        assert orbit_size == representative["orbit_size"]
        answer[record] = result
    assert len(answer) == len(document["results"])
    return answer


def main() -> None:
    exceptional, records = source_records()
    full_build = load(FULL_BUILD)
    full_cnf = Path(full_build["cnf"])
    assert full_build["status"] == "BUILD_COMPLETE"
    assert full_build["cnf_audit"]["sha256"] == sha256(full_cnf)
    selector_by_macro = {
        (int(branch["state_orbit_number"]),
         int(branch["signature_stabilizer_orbit_number"])): int(branch["selector"])
        for branch in full_build["branches"]
    }
    branch_by_macro = {
        (int(branch["state_orbit_number"]),
         int(branch["signature_stabilizer_orbit_number"])): branch
        for branch in full_build["branches"]
    }
    _labels, vertex_index, _variables, edge_variable = coordinates()
    documents = {path: load(path) for path in (
        M40_HEAD, M40_TAIL, M40_R1042, M40_R1052,
        M40_R16_48, M40_R48_112, M40_R112_240, M40_R240_304,
        M40_R304_368, M40_R368_432, M40_R432_560,
        M40_R560_688, M40_R688_816, M40_R816_944, M40_R944_1040,
        M70_HEAD, M70_R10_138, M70_R138_266,
        M70_PROJ_R266_522, M70_SUPP_R266_522, M70_TAIL,
        M70_PROJ_R522_778, M70_SUPP_R522_778,
        M70_PROJ_R778_1034, M70_SUPP_R778_1034,
        M70_PROJ_R1034_1296, M70_SUPP_R1034_1296,
        CORE_M40, CORE_M70,
    )}
    mapped = {
        path: result_map(document, tuple(document["summary"]["wanted_macros"][0]),
                         records)
        for path, document in documents.items()
    }

    selected = {}
    for record, result in mapped[M40_HEAD].items():
        assert 0 <= record < 16 and result[5] == "UNSAT"
        selected[(4, 0, record)] = (result, M40_HEAD, "synchronized_recurrence")
    for path, expected in (
        (M40_R16_48, set(range(16, 48))),
        (M40_R48_112, set(range(48, 112))),
        (M40_R112_240, set(range(112, 240))),
        (M40_R240_304, set(range(240, 304))),
        (M40_R304_368, set(range(304, 368))),
        (M40_R368_432, set(range(368, 432))),
        (M40_R432_560, set(range(432, 560))),
        (M40_R560_688, set(range(560, 688))),
        (M40_R688_816, set(range(688, 816))),
        (M40_R816_944, set(range(816, 944))),
        (M40_R944_1040, set(range(944, 1040))),
    ):
        assert set(mapped[path]) == expected
        assert documents[path]["summary"]["ordinary_local_pair_filter_enabled"]
        for record, result in mapped[path].items():
            assert result[5] == "UNSAT"
            selected[(4, 0, record)] = (
                result, path, "synchronized_recurrence_plus_ordinary_pair"
            )
    assert set(mapped[M40_TAIL]) == set(range(1040, 1056))
    supplements = {1042: M40_R1042, 1052: M40_R1052}
    for record, result in mapped[M40_TAIL].items():
        if result[5] == "UNSAT":
            selected[(4, 0, record)] = (result, M40_TAIL,
                                         "synchronized_recurrence")
        else:
            assert result[5] == "SAT" and record in supplements
            path = supplements[record]
            supplement = mapped[path][record]
            assert supplement[1:5] == result[1:5]
            assert supplement[5] == "UNSAT"
            assert documents[path]["summary"][
                "ordinary_local_pair_filter_enabled"
            ]
            selected[(4, 0, record)] = (
                supplement, path, "synchronized_recurrence_plus_ordinary_pair"
            )

    for path, expected in ((M70_HEAD, set(range(10))),
                           (M70_R10_138, set(range(10, 138))),
                           (M70_R138_266, set(range(138, 266))),
                           (M70_TAIL, set(range(1296, 1312)))):
        assert set(mapped[path]) == expected
        if path in {M70_R10_138, M70_R138_266}:
            assert documents[path]["summary"][
                "ordinary_local_pair_filter_enabled"
            ]
        for record, result in mapped[path].items():
            assert result[5] == "UNSAT"
            reason = (
                "synchronized_recurrence_plus_ordinary_pair"
                if path in {M70_R10_138, M70_R138_266}
                else "synchronized_recurrence"
            )
            selected[(7, 0, record)] = (result, path, reason)

    for projection_path, supplement_path, expected in (
        (M70_PROJ_R266_522, M70_SUPP_R266_522, set(range(266, 522))),
        (M70_PROJ_R522_778, M70_SUPP_R522_778, set(range(522, 778))),
        (M70_PROJ_R778_1034, M70_SUPP_R778_1034, set(range(778, 1034))),
        (M70_PROJ_R1034_1296, M70_SUPP_R1034_1296,
         set(range(1034, 1296))),
    ):
        projection = mapped[projection_path]
        supplement = mapped[supplement_path]
        assert set(projection) == expected
        assert documents[projection_path]["summary"][
            "fixed_block_projection"
        ] == [0, 3]
        assert documents[projection_path]["checks"][
            "fixed_block_projection_is_existential_relaxation"
        ]
        projection_sat = {
            record for record, result in projection.items()
            if result[5] == "SAT"
        }
        assert set(supplement) == projection_sat
        assert documents[supplement_path]["summary"][
            "ordinary_local_pair_filter_enabled"
        ]
        for record, projected in projection.items():
            if projected[5] == "UNSAT":
                selected[(7, 0, record)] = (
                    projected, projection_path,
                    "exact_two_block_existential_projection",
                )
            else:
                assert projected[5] == "SAT"
                refined = supplement[record]
                assert refined[1:5] == projected[1:5]
                assert refined[5] == "UNSAT"
                selected[(7, 0, record)] = (
                    refined, supplement_path,
                    "synchronized_recurrence_plus_ordinary_pair",
                )

    assert len(selected) == 2368
    per_macro = defaultdict(lambda: {"orbits": 0, "coverage": 0})
    shard_rows = []
    for (state, signature, record), (result, path, reason) in sorted(selected.items()):
        per_macro[f"{state}:{signature}"]["orbits"] += 1
        per_macro[f"{state}:{signature}"]["coverage"] += int(result[2])
        macro = (state, signature)
        representative = records[macro][record]
        positive_edge_variables = sorted({
            edge_variable(vertex_index[tuple(left)], vertex_index[tuple(right)])
            for left, right in representative["edges"]
        })
        assert len(positive_edge_variables) == len(representative["edges"]) == 44
        # The mask contains all internal and overlap edges.  The macro selector
        # fixes internal edges and exact block cardinalities, so these positive
        # literals uniquely select the stored local overlap graph while leaving
        # the twelve disjoint E--E blocks free for the full CNF.
        local_index = {support: index for index, support in enumerate(exceptional)}
        observed_overlap = defaultdict(int)
        for left, right in representative["edges"]:
            left_support, right_support = base.support(tuple(left)), base.support(tuple(right))
            if left_support == right_support:
                continue
            pair = tuple(sorted((local_index[left_support], local_index[right_support])))
            observed_overlap[pair] += 1
        branch_targets = {
            tuple(sorted((int(left), int(right)))): int(target)
            for left, right, target in branch_by_macro[macro][
                "all_exceptional_block_totals"
            ]
        }
        for pair, target in branch_targets.items():
            if set(exceptional[pair[0]]) & set(exceptional[pair[1]]):
                assert observed_overlap[pair] == target
        selector = selector_by_macro[macro]
        shard_rows.append({
            "macro": [state, signature],
            "record_number": record,
            "mask_hex": result[1],
            "orbit_size": int(result[2]),
            "reason": reason,
            "evidence_artifact": str(path),
            "full_CNF_selector": selector,
            "positive_local_edge_variables": positive_edge_variables,
            "assumption_literals": [selector, *positive_edge_variables],
        })
    assert per_macro == {
        "4:0": {"orbits": 1056, "coverage": 524_288},
        "7:0": {"orbits": 1312, "coverage": 524_288},
    }

    causal_cores = []
    for path, macro, record in ((CORE_M40, (4, 0), 4),
                                (CORE_M70, (7, 0), 0)):
        document = documents[path]
        assert document["results"][0][5] == "UNSAT"
        core = document["small_block_cores"][0]
        assert core["record_number"] == record
        assert core["cardinality"] == 2
        assert core["block_indices"] == [0, 3]
        assert core["block_fibre_pairs"] == [[0, 5], [1, 4]]
        assert core["blocks_have_pairwise_disjoint_endpoint_fibres"]
        if macro == (7, 0):
            assert not core["common_global_config_indices_across_block_unions"]
            mechanism = "disjoint_global_ordinary_configuration_sets"
        else:
            viable = [row for row in core["block_option_diagnostics"]
                      if row["common_global_config_indices"]]
            assert len(viable) == 1
            assert viable[0]["block_option_indices"] == [1, 1]
            assert viable[0]["pair_upper_violations"]
            mechanism = "only_recurrence_compatible_options_force_pair_upper_C4"
        causal_cores.append({
            "macro": list(macro),
            "record_number": record,
            "mask_hex": records[macro][record]["mask_hex"],
            "orbit_size": records[macro][record]["orbit_size"],
            "block_support_pairs": [
                [list(exceptional[left]), list(exceptional[right])]
                for left, right in core["block_fibre_pairs"]
            ],
            "mechanism": mechanism,
            "core": core,
            "artifact": str(path),
        })

    result = {
        "status": "SOURCE150_M47_EXACT_SHARD_AUDIT_PASS",
        "inputs": {str(path): sha256(path) for path in (
            LOCAL, CATALOG, FIBRE_FILTER, M40_HEAD, M40_TAIL,
            M40_R1042, M40_R1052, M70_HEAD, M70_R10_138, M70_R138_266,
            M70_PROJ_R266_522, M70_SUPP_R266_522, M70_TAIL,
            M70_PROJ_R522_778, M70_SUPP_R522_778,
            M70_PROJ_R778_1034, M70_SUPP_R778_1034,
            M70_PROJ_R1034_1296, M70_SUPP_R1034_1296,
            CORE_M40, CORE_M70,
            M40_R16_48, M40_R48_112, M40_R112_240, M40_R240_304,
            M40_R304_368, M40_R368_432, M40_R432_560,
            M40_R560_688, M40_R688_816, M40_R816_944, M40_R944_1040,
            FULL_BUILD, full_cnf,
        )},
        "scope": {
            "source_row_index": 150,
            "macros": [[4, 0], [7, 0]],
            "full_macro_coverage_each": 524_288,
            "selected_orbits": len(shard_rows),
            "selected_coverage": sum(row["orbit_size"] for row in shard_rows),
            "this_is_not_a_full_macro_sweep": False,
        },
        "per_macro": dict(per_macro),
        "shards": shard_rows,
        "causal_cores": causal_cores,
        "evidence_class": "exact_solver_free_finite_local_CSP",
        "DRAT_ready_full_CNF_bridge": {
            "cnf": str(full_cnf),
            "cnf_sha256": sha256(full_cnf),
            "macro_selectors": {
                "4:0": selector_by_macro[(4, 0)],
                "7:0": selector_by_macro[(7, 0)],
            },
            "assumption_semantics": (
                "macro selector plus all 44 positive internal/overlap edge "
                "variables; exact selector-gated block cardinalities force "
                "the remaining local block literals"
            ),
        },
        "DRAT_certificate_present": False,
        "SAT_or_UNKNOWN_counted_as_excluded": False,
        "claim_boundary": (
            "All 1056 local-graph symmetry orbits of macro (4,0) and all "
            "1312 local-graph symmetry orbits of macro (7,0) are excluded."
        ),
    }
    assert result["scope"]["selected_coverage"] == 1_048_576
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), "status": result["status"],
                      **result["scope"]}, sort_keys=True))


if __name__ == "__main__":
    main()

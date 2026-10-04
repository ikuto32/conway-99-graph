"""SOURCE ONLY: new triple-capped moment LP and candidate exact certificates."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import sys

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + "_spec.md")
SOFTWARE = {
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
BASE = "acceleration/results/20261003_external_moment_outside_cn_filter01"
MODEL = BASE + "/filtered_system.json"
TYPES = BASE + "/types.json"
FIXED = {
    MODEL: "c628c76325d5b49106740bce7c6d3b72bc7728fdc78d85437ad484f3afbd7306",
    TYPES: "87d0272e244f60f1eefa06d3a0b2d0179a275791f7bb586992b16f648595bad2",
    BASE + "/summary.json": "89f8976ba3a18b52394417e58c9a0ce991cf1b4f4d41f14570079f8342ce3591",
    BASE + "/decisions.json": "1a48f95f646d0cea4191c43ac9b8e03a7fb0bbea05dc9bbccca68ef774ba0dc2",
}
FULL_HEADER = "INDEPENDENT_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_COMPLETE_PASS"


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def same(a, b):
    return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)


def tick(deadline):
    status = deadline.status()
    need(not status["stop_required"] and status["remaining_seconds"] > 20, "SAVE_RESERVE")
    return status


def strict_json(raw):
    need(type(raw) is bytes and len(raw) <= 64 * 1024 * 1024, "JSON_BYTES")
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "JSON_DUPLICATE")
            result[key] = value
        return result
    def nonfinite(_):
        raise ValueError("JSON_NONFINITE")
    return json.loads(raw.decode("utf8"), object_pairs_hook=pairs, parse_constant=nonfinite)


def system(a, rhs):
    need(type(a) is list and a and type(rhs) is list and len(rhs) == len(a), "SYSTEM_SHAPE")
    need(type(a[0]) is list and a[0], "SYSTEM_SHAPE")
    width = len(a[0])
    need(all(type(row) is list and len(row) == width for row in a), "SYSTEM_SHAPE")
    need(all(type(c) is int for row in a for c in row) and all(type(b) is int for b in rhs),
         "SYSTEM_INTEGER")
    return [[Fraction(c) for c in row] + [Fraction(b)] for row, b in zip(a, rhs)]


def fractions(raw, count):
    need(type(raw) is list and len(raw) == count, "FRACTION_SHAPE")
    result = []
    for text in raw:
        need(type(text) is str, "FRACTION_STRING")
        value = Fraction(text)
        need(str(value) == text, "FRACTION_CANONICAL")
        result.append(value)
    return result


def primal_receipt(a, rhs, raw, deadline):
    system(a, rhs)
    values = fractions(raw, len(a[0]))
    need(all(x >= 0 for x in values), "PRIMAL_NONNEGATIVE")
    records = []
    for i, (row, b) in enumerate(zip(a, rhs)):
        tick(deadline)
        lhs = sum(c * x for c, x in zip(row, values))
        need(lhs == b, "PRIMAL_MOMENTS")
        records.append(dict(row=i, lhs=str(lhs), rhs=str(b), equal=True))
    return records


def farkas_receipt(a, rhs, raw, deadline):
    system(a, rhs)
    y = fractions(raw, len(a))
    value = sum(b * q for b, q in zip(rhs, y))
    need(value < 0, "FARKAS_RHS_SIGN")
    columns = []
    for j in range(len(a[0])):
        tick(deadline)
        dot = sum(a[i][j] * y[i] for i in range(len(a)))
        need(dot >= 0, "FARKAS_COLUMN_SIGN")
        columns.append(dict(column=j, dot=str(dot), nonnegative=True))
    return dict(rhs_dot=str(value), negative=True, columns=columns)


def rref_solve(a, rhs, deadline, checkpoint=None, progress=False):
    # Preserved deterministic exact-Q algorithm from da6e, with fresh controls.
    reduced = system(a, rhs)
    count = len(a[0])
    row_order = list(range(len(a)))
    pivots, target = [], 0
    columns = range(count)
    if progress:
        columns = tqdm(columns, total=count, desc="filtered exact support", unit="column")
    for column in columns:
        tick(deadline)
        found = next((i for i in range(target, len(reduced)) if reduced[i][column]), None)
        if found is None:
            continue
        reduced[target], reduced[found] = reduced[found], reduced[target]
        row_order[target], row_order[found] = row_order[found], row_order[target]
        pivot = reduced[target][column]
        reduced[target][column:] = [v / pivot for v in reduced[target][column:]]
        for i, row in enumerate(reduced):
            tick(deadline)
            if i != target and row[column]:
                factor = row[column]
                row[column:] = [x - factor * q for x, q in zip(row[column:], reduced[target][column:])]
        pivots.append(dict(row=target, column=column, original_row=row_order[target],
                           pivot_before_normalization=str(pivot)))
        target += 1
        if checkpoint is not None and target % 10 == 0:
            checkpoint(reduced, pivots, row_order)
    need(not any(all(v == 0 for v in row[:-1]) and row[-1] != 0 for row in reduced),
         "INCONSISTENT_SUPPORT")
    answer = [Fraction(0) for _ in range(count)]
    for p in pivots:
        answer[p["column"]] = reduced[p["row"]][-1]
    need(all(x >= 0 for x in answer), "NEGATIVE_SOLUTION")
    primal_receipt(a, rhs, list(map(str, answer)), deadline)
    return answer, reduced, pivots, row_order


def masks(raw, count):
    need(type(raw) is list and len(raw) == count and count > 0, "TYPES_SHAPE")
    previous = -1
    for item in raw:
        need(type(item) is dict and set(item) == {"mask", "coefficient"}, "TYPE_FIELDS")
        mask = item["mask"]
        need(type(mask) is int and 0 <= mask < (1 << 17), "TYPE_MASK_INTEGER")
        need(mask > previous, "TYPE_MASK_ORDER")
        previous = mask
    return [item["mask"] for item in raw]


def typed_model(model, raw_types):
    need(type(model) is dict and model.get("schema") == "OUTSIDE_VERTEX_CN_FILTERED_MOMENT_SYSTEM_V1",
         "MODEL_SCHEMA")
    for key, value in [("target_order", 99), ("target_degree", 14), ("adjacent_cn", 1),
                       ("nonadjacent_cn", 2), ("original_eligible_type_count", 534),
                       ("eligible_type_count", 472)]:
        need(type(model.get(key)) is int and model[key] == value, "MODEL_DOMAIN")
    need(same(model.get("ordered_support_vertices"), list(range(17))), "MODEL_ORDER")
    h = model.get("induced_adjacency")
    need(type(h) is list and len(h) == 17 and all(type(row) is list and len(row) == 17 for row in h),
         "MODEL_GRAPH_SHAPE")
    need(all(type(v) is int and v in (0, 1) for row in h for v in row)
         and all(h[i][i] == 0 and h[i][j] == h[j][i] for i in range(17) for j in range(17)),
         "MODEL_GRAPH_DOMAIN")
    pairs = list(itertools.combinations(range(17), 2))
    labels = ([dict(kind="total")] + [dict(kind="vertex", vertex=i) for i in range(17)]
              + [dict(kind="pair", vertices=list(pair)) for pair in pairs])
    need(same(model.get("row_labels"), labels), "MODEL_LABELS")
    rhs = model.get("right_hand_side")
    need(type(rhs) is list and len(rhs) == 154 and all(type(b) is int for b in rhs), "MODEL_RHS")
    need(model.get("retained_coefficients_are_literal_originals") is True
         and model.get("original_row_labels_rhs_unchanged") is True, "MODEL_PROVENANCE")
    indices = model.get("retained_original_type_indices")
    need(type(indices) is list and len(indices) == 472 and all(type(i) is int and 0 <= i < 534 for i in indices)
         and indices == sorted(set(indices)), "MODEL_INDICES")
    mask_values = masks(raw_types, 472)
    columns = []
    for item, mask in zip(raw_types, mask_values):
        bits = [(mask >> i) & 1 for i in range(17)]
        expected = [1] + bits + [bits[i] * bits[j] for i, j in pairs]
        need(same(item["coefficient"], expected), "TYPE_COEFFICIENT")
        columns.append(expected)
    a = [[column[i] for column in columns] for i in range(154)]
    system(a, rhs)
    return a, rhs, mask_values


def numerical_search(a, rhs, deadline, save, prefix, checkpoint=None, progress=False, triple_block=None):
    system(a, rhs)
    tick(deadline)
    import numpy as np
    import scipy
    from scipy.optimize import linprog
    arrays = np.asarray(a, dtype=np.float64), np.asarray(rhs, dtype=np.float64)
    budget = min(180.0 if triple_block is not None else 120.0,
                 tick(deadline)["remaining_seconds"] - (300.0 if triple_block is not None else 70.0))
    need(budget > 0, "LP_RECONSTRUCTION_RESERVE")
    primal = linprog(np.zeros(len(a[0])), A_eq=arrays[0], b_eq=arrays[1],
                     bounds=(0, None), method="highs", options={"time_limit": budget})
    tick(deadline)
    x = None if primal.x is None else [float(v) for v in primal.x]
    need(x is None or (len(x) == len(a[0]) and all(math.isfinite(v) for v in x)), "NUMERIC_FINITE")
    guidance = dict(status=int(primal.status), success=bool(primal.success), message=str(primal.message),
                    x=x, floating_status_is_proof=False, method="scipy.optimize.linprog/highs",
                    time_limit=budget, scipy=scipy.__version__, numpy=np.__version__)
    save(prefix + "_primal_guidance.json", guidance)
    result = dict(LP_calls=1, certificate_kind=None, certificate=None,
                  certificate_unavailable_reason="Numerical result alone is not a certificate")
    if primal.status == 0:
        need(x is not None, "NUMERIC_PRIMAL_MISSING")
        support = [j for j, value in enumerate(x) if value > 0.0]
        save(prefix + "_support.json", dict(indices=support, rule="every numeric coordinate strictly >0.0; no tolerance",
                                            numerical_selection_only=True))
        try:
            need(support, "EMPTY_SUPPORT")
            if triple_block is None:
                restricted = [[row[j] for j in support] for row in a]
                exact, reduced, pivots, row_order = rref_solve(restricted, rhs, deadline, checkpoint, progress)
                values = [Fraction(0) for _ in a[0]]
                for j, value in zip(support, exact):
                    values[j] = value
            else:
                base_a, base_rhs, cut_rows = triple_block
                values, reduced, pivots, row_order = block_support_reconstruct(
                    base_a, base_rhs, cut_rows, x, deadline, checkpoint, progress)
            raw = list(map(str, values))
            rows = primal_receipt(a, rhs, raw, deadline)
            save(prefix + "_rref.json", dict(augmented_rref=[list(map(str, row)) for row in reduced],
                                           pivots=pivots, row_order=row_order, rank=len(pivots),
                                           free_variables_zero=True, rank_is_producer_metadata=True,
                                           structured_slack_elimination=triple_block is not None,
                                           rank_scope="restricted original variables after selected slack elimination"
                                           if triple_block is not None else "restricted full variables"))
            save(prefix + "_primal_rows.json", rows)
            certificate = dict(schema="TRIPLE_CAPPED_EXTERNAL_MOMENT_EXACT_PRIMAL_V1", values=raw,
                               nonnegative=True, rows_exact=True, integer=all(x.denominator == 1 for x in values))
            save(prefix + "_primal.json", certificate)
            result.update(certificate_kind="primal", certificate=certificate,
                          certificate_unavailable_reason=None)
        except ValueError as exc:
            if str(exc) == "SAVE_RESERVE":
                raise
            result["certificate_unavailable_reason"] = "Exact support attempt rejected: " + str(exc)
            save(prefix + "_exact_attempt_rejection.json", dict(stage=str(exc), infeasibility_inferred=False))
    elif primal.status == 2:
        # Infeasible is guidance only. A distinct dual feasibility LP searches for a checked Q witness.
        budget = min(180.0 if triple_block is not None else 120.0,
                     tick(deadline)["remaining_seconds"] - (60.0 if triple_block is not None else 45.0))
        need(budget > 0, "DUAL_CERTIFICATE_RESERVE")
        dual = linprog(np.zeros(len(a)), A_ub=-arrays[0].T, b_ub=np.zeros(len(a[0])),
                       A_eq=arrays[1].reshape(1, -1), b_eq=[-1.0], bounds=(None, None),
                       method="highs", options={"time_limit": budget})
        tick(deadline)
        y = None if dual.x is None else [float(v) for v in dual.x]
        need(y is None or (len(y) == len(a) and all(math.isfinite(v) for v in y)), "NUMERIC_FINITE")
        save(prefix + "_dual_guidance.json", dict(status=int(dual.status), success=bool(dual.success),
                                                message=str(dual.message), y=y, time_limit=budget,
                                                floating_status_is_proof=False))
        result["LP_calls"] = 2
        if dual.status == 0:
            need(y is not None, "NUMERIC_DUAL_MISSING")
            raw = [str(Fraction(v).limit_denominator(1_000_000_000)) for v in y]
            try:
                receipts = farkas_receipt(a, rhs, raw, deadline)
                save(prefix + "_farkas_checks.json", receipts)
                certificate = dict(schema="TRIPLE_CAPPED_EXTERNAL_MOMENT_EXACT_FARKAS_V1", values=raw,
                                   rhs_dot=receipts["rhs_dot"], all_column_inequalities_exact=True,
                                   candidate_rationalization_max_denominator=1_000_000_000)
                save(prefix + "_farkas.json", certificate)
                result.update(certificate_kind="farkas", certificate=certificate,
                              certificate_unavailable_reason=None)
            except ValueError as exc:
                if str(exc) == "SAVE_RESERVE":
                    raise
                result["certificate_unavailable_reason"] = "Exact dual rationalization rejected: " + str(exc)
                save(prefix + "_exact_attempt_rejection.json", dict(stage=str(exc), infeasibility_inferred=False))
    return result


def filter_gate_scope(gate):
    need(type(gate) is dict and gate.get("status") == FULL_HEADER
         and gate.get("producer") == "/root/checkpoint_audit"
         and gate.get("verifier") == "/root/native_driver"
         and gate.get("method") == "independent_artifact_check"
         and gate.get("target_resolution") == "NONE", "FILTER_GATE_SCOPE")


def preserved_controls(deadline, save):
    records = []
    # Synthetic header reproduces Native14d17's literal method field; no actual gate read.
    header = dict(status=FULL_HEADER, producer="/root/checkpoint_audit",
                  verifier="/root/native_driver", method="independent_artifact_check",
                  target_resolution="NONE", implementation_version=1)
    filter_gate_scope(header)
    save("control_genuine_method_header.json", header)
    records.append(dict(case="genuine_method_header", expected_stage="PASS", actual_stage="PASS"))
    obsolete_header = {key: value for key, value in header.items() if key != "method"}
    obsolete_header["verification_method"] = "independent_artifact_check"
    exact, _, _, _ = rref_solve([[1, 2], [2, 1]], [1, 1], deadline)
    need(list(map(str, exact)) == ["1/3", "1/3"], "CONTROL_RATIONAL")
    save("control_unique_rational.json", dict(a=[[1, 2], [2, 1]], rhs=[1, 1], values=list(map(str, exact))))
    records.append(dict(case="unique_rational", expected_stage="PASS", actual_stage="PASS"))
    feasible = numerical_search([[1, 0], [0, 1]], [1, 1], deadline, save, "control_lp_primal")
    need(feasible["certificate_kind"] == "primal"
         and feasible["certificate"]["values"] == ["1", "1"], "CONTROL_LP_PRIMAL")
    records.append(dict(case="tiny_lp_primal", expected_stage="PASS", actual_stage="PASS"))
    infeasible = numerical_search([[1]], [-1], deadline, save, "control_lp_dual")
    need(infeasible["certificate_kind"] == "farkas" and infeasible["certificate"]["values"] == ["1"],
         "CONTROL_LP_FARKAS")
    records.append(dict(case="tiny_lp_dual", expected_stage="PASS", actual_stage="PASS"))
    negative = [
        ("verification_method_only_header", "FILTER_GATE_SCOPE", obsolete_header,
         lambda: filter_gate_scope(obsolete_header)),
        ("inconsistent", "INCONSISTENT_SUPPORT", dict(a=[[1], [1]], rhs=[1, 2]),
         lambda: rref_solve([[1], [1]], [1, 2], deadline)),
        ("negative_rref", "NEGATIVE_SOLUTION", dict(a=[[1]], rhs=[-1]),
         lambda: rref_solve([[1]], [-1], deadline)),
        ("bool_coefficient", "SYSTEM_INTEGER", dict(a=[[True]], rhs=[1]), lambda: system([[True]], [1])),
        ("float_rhs", "SYSTEM_INTEGER", dict(a=[[1]], rhs=[1.0]), lambda: system([[1]], [1.0])),
        ("noncanonical_fraction", "FRACTION_CANONICAL", dict(values=["2/2"]), lambda: fractions(["2/2"], 1)),
        ("float_fraction", "FRACTION_STRING", dict(values=[1.0]), lambda: fractions([1.0], 1)),
        ("negative_primal", "PRIMAL_NONNEGATIVE", dict(a=[[1, 1]], rhs=[0], values=["-1", "1"]),
         lambda: primal_receipt([[1, 1]], [0], ["-1", "1"], deadline)),
        ("wrong_primal_row", "PRIMAL_MOMENTS", dict(a=[[1]], rhs=[1], values=["0"]),
         lambda: primal_receipt([[1]], [1], ["0"], deadline)),
        ("wrong_farkas_rhs", "FARKAS_RHS_SIGN", dict(a=[[1]], rhs=[-1], values=["-1"]),
         lambda: farkas_receipt([[1]], [-1], ["-1"], deadline)),
        ("wrong_farkas_column", "FARKAS_COLUMN_SIGN", dict(a=[[-1]], rhs=[-1], values=["1"]),
         lambda: farkas_receipt([[-1]], [-1], ["1"], deadline)),
        ("bool_mask", "TYPE_MASK_INTEGER", [dict(mask=True, coefficient=[1])],
         lambda: masks([dict(mask=True, coefficient=[1])], 1)),
        ("decreasing_masks", "TYPE_MASK_ORDER", [dict(mask=1, coefficient=[1]), dict(mask=0, coefficient=[1])],
         lambda: masks([dict(mask=1, coefficient=[1]), dict(mask=0, coefficient=[1])], 2)),
    ]
    for name, expected, payload, action in negative:
        tick(deadline)
        save("control_negative_" + name + ".json", payload)
        actual = "ACCEPTED"
        try:
            action()
        except ValueError as exc:
            actual = str(exc)
        need(actual == expected, "CONTROL_STAGE_" + name)
        records.append(dict(case=name, expected_stage=expected, actual_stage=actual))
    result = dict(positive=4, strict_negative=13, total=17, records=records,
                  tiny_fixture_LP_calls=3, target_model_read=False, target_LP_calls=0)
    save("controls.json", result)
    return result


PRIOR_PRIMAL = "acceleration/results/20261003_external_moment_filtered_lp02/filtered_primal.json"
PRIOR_PRIMAL_SHA = "772b5f1534de5bf37da578b2b7345db95795f80559fc7507d3a709be719b5f9d"
LEMMA_SOURCE = "docs/CANDIDATE_20261003_EXTERNAL_TYPE_PAIR_AND_TRIPLE_CAPS_V1.md"
LEMMA_SOURCE_SHA = "f7aefb0628c9da0741f0c8f43b444a30e5d5042eb60c1db23735f024286125a4"
PRIOR_HEADER = "INDEPENDENT_FILTERED_EXTERNAL_MOMENT_CERTIFICATE_V1_COMPLETE_PASS"
LEMMA_HEADER = "INDEPENDENT_EXTERNAL_TYPE_PAIR_AND_TRIPLE_CAPS_WRITTEN_PASS"
LEMMA_ID = "C-EXTERIOR-TYPE-PAIR-AND-TRIPLE-COMMON-NEIGHBOR-CAPS"


def triple_rows(mask_values, m, deadline):
    need(type(m) is int and 3 <= m <= 17, "TRIPLE_DOMAIN")
    need(type(mask_values) is list and mask_values, "TRIPLE_MASKS")
    need(all(type(v) is int and 0 <= v < (1 << m) for v in mask_values), "TRIPLE_MASK")
    need(mask_values == sorted(set(mask_values)), "TRIPLE_MASK_ORDER")
    triples, rows = [], []
    for points in itertools.combinations(range(m), 3):
        tick(deadline)
        q = sum(1 << point for point in points)
        triples.append(list(points))
        rows.append([int((mask & q) == q) for mask in mask_values])
    return triples, rows


def standard_form(base_a, base_rhs, cuts, deadline):
    system(base_a, base_rhs)
    n = len(base_a[0])
    need(type(cuts) is list and cuts and all(type(r) is list and len(r) == n for r in cuts),
         "TRIPLE_ROW_SHAPE")
    need(all(type(v) is int and v in (0, 1) for row in cuts for v in row), "TRIPLE_ROW_DOMAIN")
    k = len(cuts)
    a = []
    for row in base_a:
        tick(deadline)
        a.append(row[:] + [0] * k)
    for i, row in enumerate(cuts):
        tick(deadline)
        a.append(row[:] + [int(i == j) for j in range(k)])
    return a, base_rhs[:] + [1] * k


def block_support_reconstruct(base_a, base_rhs, cuts, numeric, deadline, checkpoint=None, progress=False):
    # Selected positive slack columns are eliminated algebraically, without tolerance.
    a, rhs = standard_form(base_a, base_rhs, cuts, deadline)
    n, k = len(base_a[0]), len(cuts)
    need(type(numeric) is list and len(numeric) == n + k and
         all(type(v) in (int, float) and math.isfinite(v) for v in numeric), "NUMERIC_FINITE")
    selected_n = [j for j in range(n) if numeric[j] > 0.0]
    selected_slacks = {i for i in range(k) if numeric[n+i] > 0.0}
    need(selected_n, "EMPTY_SUPPORT")
    reduced_a = [[row[j] for j in selected_n] for row in base_a]
    reduced_rhs = base_rhs[:]
    for i, row in enumerate(cuts):
        tick(deadline)
        if i not in selected_slacks:
            reduced_a.append([row[j] for j in selected_n])
            reduced_rhs.append(1)
    original, reduced, pivots, row_order = rref_solve(
        reduced_a, reduced_rhs, deadline, checkpoint, progress)
    values = [Fraction(0)] * n
    for j, value in zip(selected_n, original):
        values[j] = value
    slacks = []
    for i, row in enumerate(cuts):
        tick(deadline)
        slack = 1 - sum(c * v for c, v in zip(row, values))
        need(i in selected_slacks or slack == 0, "ZERO_SLACK_SUPPORT")
        slacks.append(slack)
    values.extend(slacks)
    primal_receipt(a, rhs, list(map(str, values)), deadline)
    return values, reduced, pivots, row_order


def prior_gate_scope(gate):
    need(type(gate) is dict and gate.get("status") == PRIOR_HEADER
         and gate.get("producer") == "/root/checkpoint_audit"
         and gate.get("verifier") == "/root/structural"
         and gate.get("method") == "independent_artifact_check"
         and gate.get("target_resolution") == "NONE"
         and type(gate.get("implementation_version")) is int
         and gate["implementation_version"] == 3, "PRIOR_PRIMAL_GATE_SCOPE")


def lemma_scope(report):
    need(type(report) is dict and report.get("status") == LEMMA_HEADER
         and report.get("claim_id") == LEMMA_ID
         and type(report.get("claim_revision")) is int and report["claim_revision"] == 1
         and report.get("producer") == "/root/checkpoint_audit"
         and report.get("verifier") == "/root/native_driver"
         and report.get("method") == "independent_derivation"
         and report.get("outcome") == "PASS"
         and report.get("target_resolution") == "NONE", "LEMMA_SCOPE")


def prior_diagnostic(base_a, base_rhs, cuts, raw, deadline):
    # A new bounded diagnostic, without transferring prior feasibility approval.
    primal_receipt(base_a, base_rhs, raw, deadline)
    values = fractions(raw, len(base_a[0]))
    rows = []
    for i, row in enumerate(cuts):
        tick(deadline)
        lhs = sum(c * v for c, v in zip(row, values))
        rows.append(dict(triple_row=i, lhs=str(lhs), upper="1", violated=lhs > 1))
    return dict(rows=rows, row_count=len(rows), violated_count=sum(r["violated"] for r in rows),
                maximum_lhs=str(max(Fraction(r["lhs"]) for r in rows)),
                original_rows_rechecked_exact=True, new_model_feasibility_inferred=False)


def own_controls(deadline, save):
    base = preserved_controls(deadline, lambda name, data:
        save("preserved_controls.json" if name == "controls.json" else name, data))
    records = list(base["records"])
    triples, cuts = triple_rows([0, 7], 17, deadline)
    need(len(triples) == 680 and triples[0] == [0, 1, 2] and triples[-1] == [14, 15, 16]
         and sum(row[1] for row in cuts) == 1 and all(row[0] == 0 for row in cuts), "CONTROL680")
    save("control_all680_order.json", dict(masks=[0, 7], triples=triples, rows=cuts))
    records.append(dict(case="all680_order", expected_stage="PASS", actual_stage="PASS"))
    # Known rook(3,3) exterior x=8 relative to S=0..7 has T={2,5,6,7}.
    rook = [[int(i != j and (i//3 == j//3 or i%3 == j%3)) for j in range(9)] for i in range(9)]
    mask = sum(1 << i for i in range(8) if rook[8][i])
    need(mask == 228, "CONTROL_ROOK_TYPE")
    qt, qc = triple_rows([mask], 8, deadline)
    need(len(qt) == 56 and sum(row[0] for row in qc) == 4 and all(row[0] <= 1 for row in qc),
         "CONTROL_ROOK_TRIPLES")
    save("control_rook_exterior_triples.json", dict(adjacency=rook, S=list(range(8)), outside=8,
         mask=mask, multiplicity=1, triples=qt, rows=qc, target99_realization=False))
    records.append(dict(case="rook_exterior_triples", expected_stage="PASS", actual_stage="PASS"))
    a, b, c = [[1, 2], [2, 1]], [1, 1], [[0, 1]]
    v, _, _, _ = block_support_reconstruct(a, b, c, [1/3, 1/3, 2/3], deadline)
    need(list(map(str, v)) == ["1/3", "1/3", "2/3"], "CONTROL_POSITIVE_SLACK")
    save("control_positive_slack.json", dict(a=a, rhs=b, cuts=c, numeric=[1/3,1/3,2/3], values=list(map(str,v))))
    records.append(dict(case="positive_slack", expected_stage="PASS", actual_stage="PASS"))
    v, _, _, _ = block_support_reconstruct([[0, 1]], [1], [[0, 1]], [0.0, 1.0, 0.0], deadline)
    need(list(map(str, v)) == ["0", "1", "0"], "CONTROL_ZERO_SLACK")
    save("control_zero_slack.json", dict(a=[[0,1]], rhs=[1], cuts=[[0,1]], numeric=[0.0,1.0,0.0], values=list(map(str,v))))
    records.append(dict(case="zero_slack", expected_stage="PASS", actual_stage="PASS"))
    lemma = dict(status=LEMMA_HEADER, claim_id=LEMMA_ID, claim_revision=1,
                 producer="/root/checkpoint_audit", verifier="/root/native_driver",
                 method="independent_derivation", outcome="PASS", target_resolution="NONE")
    prior = dict(status=PRIOR_HEADER, producer="/root/checkpoint_audit", verifier="/root/structural",
                 method="independent_artifact_check", target_resolution="NONE", implementation_version=3)
    lemma_scope(lemma)
    prior_gate_scope(prior)
    save("control_genuine_new_headers.json", dict(lemma=lemma, prior=prior))
    records.append(dict(case="genuine_new_headers", expected_stage="PASS", actual_stage="PASS"))
    wrong_method = {k: v for k, v in lemma.items() if k != "method"}
    wrong_method["verification_method"] = "independent_derivation"
    wrong_revision = {**lemma, "claim_revision": True}
    cases = [
        ("bool_support_size", "TRIPLE_DOMAIN", dict(m=True, masks=[0]), lambda: triple_rows([0], True, deadline)),
        ("float_support_size", "TRIPLE_DOMAIN", dict(m=3.0, masks=[0]), lambda: triple_rows([0], 3.0, deadline)),
        ("bool_triple_mask", "TRIPLE_MASK", dict(m=3,masks=[False]), lambda: triple_rows([False], 3, deadline)),
        ("float_triple_mask", "TRIPLE_MASK", dict(m=3,masks=[0.0]), lambda: triple_rows([0.0], 3, deadline)),
        ("duplicate_triple_mask", "TRIPLE_MASK_ORDER", dict(m=3,masks=[0,0]), lambda: triple_rows([0,0], 3, deadline)),
        ("unordered_triple_mask", "TRIPLE_MASK_ORDER", dict(m=3,masks=[7,0]), lambda: triple_rows([7,0], 3, deadline)),
        ("missing_original_support", "INCONSISTENT_SUPPORT", dict(a=[[0,1]],rhs=[1],cuts=[[0,1]],numeric=[1.0,0.0,0.0]),
         lambda: block_support_reconstruct([[0,1]], [1], [[0,1]], [1.0,0.0,0.0], deadline)),
        ("negative_derived_slack", "PRIMAL_NONNEGATIVE", dict(a=[[0,1]],rhs=[2],cuts=[[0,1]],numeric=[0.0,2.0,1.0]),
         lambda: block_support_reconstruct([[0,1]], [2], [[0,1]], [0.0,2.0,1.0], deadline)),
        ("obsolete_lemma_method", "LEMMA_SCOPE", wrong_method, lambda: lemma_scope(wrong_method)),
        ("bool_lemma_revision", "LEMMA_SCOPE", wrong_revision, lambda: lemma_scope(wrong_revision)),
    ]
    for name, expected, payload, action in cases:
        tick(deadline)
        save("control_negative_" + name + ".json", payload)
        actual = "ACCEPTED"
        try:
            action()
        except ValueError as exc:
            actual = str(exc)
        need(actual == expected, "CONTROL_STAGE_" + name)
        records.append(dict(case=name, expected_stage=expected, actual_stage=actual))
    result = dict(positive=9, strict_negative=23, total=32, records=records,
                  tiny_fixture_LP_calls=3, target_model_read=False, target_LP_calls=0,
                  new_triple_controls=15, known_rook9_exterior_fixture=1,
                  structured_elimination_is_proof=False, raw_full_identity_required=True)
    save("controls.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["calibrate", "solve"])
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--spec-sha256", required=True)
    parser.add_argument("--full-gate")
    parser.add_argument("--full-gate-sha256")
    parser.add_argument("--prior-gate")
    parser.add_argument("--prior-gate-sha256")
    parser.add_argument("--lemma-report")
    parser.add_argument("--lemma-report-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="New834eq1152var triple-capped LP and exact full rational checks, including authentication/own controls/preservation")
    out = Path(args.out).resolve()
    need(not out.exists(), "OUTPUT_FRESH")
    out.mkdir(parents=True)
    inputs, outputs = {}, {}
    def digest(path):
        tick(deadline)
        h = hashlib.sha256()
        with Path(path).open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                tick(deadline)
                h.update(chunk)
        tick(deadline)
        return h.hexdigest()
    def key(path):
        return Path(path).resolve().relative_to(ROOT).as_posix()
    def pin(path, expected):
        need(type(expected) is str and len(expected) == 64
             and all(c in "0123456789abcdef" for c in expected), "HASH_FORMAT")
        actual = digest(path)
        need(actual == expected, "INPUT_IDENTITY")
        inputs[key(path)] = actual
    def read(path):
        tick(deadline)
        value = strict_json(Path(path).read_bytes())
        tick(deadline)
        return value
    def save(name, value):
        tick(deadline)
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf8")
        with path.open("xb") as handle:
            handle.write(raw)
        tick(deadline)
        outputs[key(path)] = digest(path)
    try:
        pin(SELF, args.source_sha256)
        pin(SPEC, args.spec_sha256)
        for path, expected in SOFTWARE.items():
            pin(ROOT / path, expected)
        controls = own_controls(deadline, save)
        outcome = None
        if args.mode == "solve":
            need(args.full_gate is not None and args.full_gate_sha256 is not None, "FILTER_GATE_REQUIRED")
            gate_path = Path(args.full_gate).resolve()
            pin(gate_path, args.full_gate_sha256)
            gate = read(gate_path)
            filter_gate_scope(gate)
            closure = gate.get("inputs_sha256")
            need(type(closure) is dict and closure, "FILTER_GATE_INPUTS")
            for path, expected in FIXED.items():
                need(closure.get(path) == expected, "FILTER_GATE_DIRECT_PIN")
                pin(ROOT / path, expected)
            for path, expected in sorted(closure.items()):
                pin(ROOT / path, expected)
            need(args.prior_gate is not None and args.prior_gate_sha256 is not None
                 and args.lemma_report is not None and args.lemma_report_sha256 is not None,
                 "NEW_PREREQUISITES_REQUIRED")
            prior_path = Path(args.prior_gate).resolve()
            pin(prior_path, args.prior_gate_sha256)
            prior = read(prior_path)
            prior_gate_scope(prior)
            prior_closure = prior.get("inputs_sha256")
            need(type(prior_closure) is dict and prior_closure.get(PRIOR_PRIMAL) == PRIOR_PRIMAL_SHA,
                 "PRIOR_PRIMAL_DIRECT_PIN")
            for path, expected in sorted(prior_closure.items()):
                pin(ROOT / path, expected)
            lemma_path = Path(args.lemma_report).resolve()
            pin(lemma_path, args.lemma_report_sha256)
            lemma = read(lemma_path)
            lemma_scope(lemma)
            lemma_closure = lemma.get("inputs_sha256")
            need(type(lemma_closure) is dict and lemma_closure.get(LEMMA_SOURCE) == LEMMA_SOURCE_SHA,
                 "LEMMA_DIRECT_PIN")
            for path, expected in sorted(lemma_closure.items()):
                pin(ROOT / path, expected)
            base_a, base_rhs, mask_values = typed_model(read(ROOT / MODEL), read(ROOT / TYPES))
            triples, cuts = triple_rows(mask_values, 17, deadline)
            need(len(triples) == 680, "EXACT680_TRIPLES")
            a, rhs = standard_form(base_a, base_rhs, cuts, deadline)
            need(len(a) == 834 and len(a[0]) == 1152, "EXACT834_1152_MODEL")
            save("triple_system.json", dict(schema="TRIPLE_CAPPED_EXTERNAL_MOMENT_SYSTEM_V1",
                 original_model_path=MODEL, original_model_sha256=FIXED[MODEL],
                 types_path=TYPES, types_sha256=FIXED[TYPES], original_variables=472,
                 original_equations=154, support_vertices=list(range(17)), ordered_masks=mask_values,
                 ordered_triples=triples, triple_coefficients=cuts, slack_variables=680,
                 coefficient_matrix=a, right_hand_side=rhs, rows=834, variables=1152,
                 original154_literal_unchanged=True, new_inequality_rhs=1,
                 standard_form="[M 0; C I] [n;s] = [b;ones], n,s>=0"))
            save("model_receipt.json", dict(original_model_path=MODEL, original_model_sha256=FIXED[MODEL],
                 types_path=TYPES, types_sha256=FIXED[TYPES], rows=834, columns=1152,
                 original_columns=472, triple_rows=680, ordered_masks=mask_values,
                 lemma_source_path=LEMMA_SOURCE, lemma_source_sha256=LEMMA_SOURCE_SHA,
                 lemma_report_path=key(lemma_path), lemma_report_sha256=args.lemma_report_sha256,
                 old_feasibility_approval_transferred=False))
            pin(ROOT / PRIOR_PRIMAL, PRIOR_PRIMAL_SHA)
            prior_raw = read(ROOT / PRIOR_PRIMAL)
            need(prior_raw.get("schema") == "FILTERED_EXTERNAL_MOMENT_EXACT_PRIMAL_V1", "PRIOR_PRIMAL_SCHEMA")
            save("prior_primal_triple_diagnostic.json",
                 prior_diagnostic(base_a, base_rhs, cuts, prior_raw.get("values"), deadline))
            def checkpoint(reduced, pivots, row_order):
                save("checkpoints/pivot_%03d.json" % len(pivots),
                     dict(augmented_rref=[list(map(str, row)) for row in reduced],
                          pivots=pivots, row_order=row_order, unfinished=True))
            outcome = numerical_search(a, rhs, deadline, save, "triple", checkpoint, True,
                                       triple_block=(base_a, base_rhs, cuts))
            save("attempt.json", outcome)
        for path, expected in list(inputs.items()):
            pin(ROOT / path, expected)
        tick(deadline)
        status = "AUTHOR_TRIPLE_CAPPED_EXTERNAL_MOMENT_LP_V1_CONTROLS_PASS" if args.mode == "calibrate" else (
            "CANDIDATE_TRIPLE_CAPPED_EXTERNAL_MOMENT_EXACT_CERTIFICATE" if outcome["certificate_kind"] is not None
            else "CANDIDATE_TRIPLE_CAPPED_EXTERNAL_MOMENT_NUMERICAL_GUIDANCE_ONLY")
        summary = dict(status=status, timestamp=datetime.now(timezone.utc).isoformat(),
            source_author="/root/checkpoint_audit", producer="/root/checkpoint_audit",
            independent_verifier_required="/root/structural", independent_approval=False,
            implementation_version=1, mode=args.mode, command=[sys.executable] + sys.argv, cwd=str(ROOT), python=platform.python_version(),
            inputs_sha256=inputs.copy(), outputs_sha256=outputs.copy(), controls=controls,
            triple_result=outcome, target_LP_calls=0 if outcome is None else outcome["LP_calls"],
            tiny_fixture_LP_calls=3, original_model_changed=False, integer_search_calls=0,
            graph_completion_proved=False, target_resolution="NONE", whole_family_exclusion=False,
            prior_filtered_exact_primal_approval_transferred=False, ledger_index_git_mutations=False,
            shared_origins=["ROOT proposed cross-CN filter; Native independently derives/filter-checks prerequisite",
                            "Exact RREF copied from Checkpoint da6e source, fresh controls; no old gate transfer",
                            "Common Python/SHA/deadline and pinned NumPy/SciPy/HiGHS numerical libraries"],
            limitations=["One fixed induced17 graph; new834-equation1152-variable triple-capped necessary relaxation only",
                         "Floating optimizer statuses/values and positive support selection are not proof",
                         "Free-zero exact reconstruction can fail despite other feasible support assignments",
                         "Failed/unfinished rationalization is not infeasibility or impracticality evidence",
                         "Any saved rational certificate needs a separate Structural complete raw check",
                         "No integer realization, graph extension, global target or full-family conclusion"],
            deadline=tick(deadline))
        save("summary.json", summary)
        tick(deadline)
    except Exception as exc:
        failure = dict(status="FAILED_PRESERVED", timestamp=datetime.now(timezone.utc).isoformat(),
                       stage=str(exc), exception_type=type(exc).__name__, inputs_sha256=inputs,
                       outputs_sha256=outputs, no_infeasibility_inference=True, no_automatic_retry=True,
                       deadline=deadline.status(), target_resolution="NONE")
        (out / "failure.json").write_text(json.dumps(failure, indent=2, allow_nan=False) + "\n", encoding="utf8")
        raise


if __name__ == "__main__":
    main()

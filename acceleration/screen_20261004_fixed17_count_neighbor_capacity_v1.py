"""SOURCE ONLY: exact necessary row-capacity screens for one fixed count witness."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + "_spec.md")
MAX_BYTES = 64 * 1024 * 1024
SOFTWARE = {
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
COUNT_BASE = "acceleration/results/20261004_fixed17_integer_type_counts01/"
COUNT_PINS = {
    COUNT_BASE + "summary.json": "857dc4a986cf509e697bc61c79562adeec3f561aab827a6e54ad0dbe2e660ab3",
    COUNT_BASE + "exact_integer_candidate.json": "133097b6174aa1a4b1d327b5c72a727f8ad1ac6daeef0654b117a5f8b88de5b5",
    COUNT_BASE + "parsed_fixed_input.json": "cfe5003a2bd0ad4b2b979264c6e6d1648dc3cd67d1ebc03226d44998371b1248",
    COUNT_BASE + "integer_model.json": "3279f118e3bce092b61a3d6d3feb8eaa15ff9f9a6178d99f91ccf4183251ccdc",
    COUNT_BASE + "pair_rules.json": "ef52a35246c2ae9634f13284d4850da25f4b4f666f15fe0675284c168b03086c",
}
PAIR_GATE_PATH = "acceleration/results/20261004_independent_review/fixed17_dual_gram_pairs_full02/summary.json"
PAIR_GATE_SHA = "ee9fa8961415df0e5f0ca429c33fc95a1d6223b77ec68e2c9ec71cc1dec0e218"
PAIR_ROOT_PATH = "acceleration/results/20261004_fixed17_dual_gram_pairs_checker_root_actual_full_acceptance02.json"
PAIR_ROOT_SHA = "39a904ee2ec0bdb4b1a28678c1842794d2abe7d05150879517265a6e7f797586"
COUNT_GATE_PATH = "acceleration/results/20261004_independent_review/external_moment_integer_counts_full01/summary.json"
COUNT_GATE_SHA = "37bcf42a3b5e358c4306c642e152e3e605a07dc305de71b2272e455e377bd6b8"
COUNT_ROOT_PATH = "acceleration/results/20261004_integer_counts_independent_full_root_actual_acceptance01.json"
COUNT_ROOT_SHA = "3823dec446f661d87a27d2cad80b4c2f91883c786f30def4f43a25eb913bb10d"
PAIR_RAW = "acceleration/results/20261004_fixed17_dual_gram_pairs01/"
PAIR_FIELDS = ("proposal_id", "i", "j", "left_mask", "right_mask", "intersection",
    "upper_left_diagonal", "upper_right_diagonal", "upper_cross_0", "upper_cross_1",
    "lower_left_diagonal", "lower_right_diagonal", "lower_cross_0", "lower_cross_1",
    "upper_bits", "lower_bits", "cn_bits", "combined_bits", "classification")
CLASS_NAMES = {(): "incompatible", (0,): "forced_nonadjacent", (1,): "forced_adjacent", (0, 1): "either"}
CAL_STATUS = "FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_AUTHOR_CONTROLS_PASS"
CONTROL_COUNTS = dict(positive=8, negative=23, total=31)


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


class ScreenReject(ValueError):
    def __init__(self, stage, result):
        super().__init__(stage)
        self.result = result


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def budget_snapshot(raw):
    need(type(raw) is dict and raw.get("stop_required") is False
         and type(raw.get("remaining_seconds")) in (int, float)
         and math.isfinite(raw["remaining_seconds"]) and raw["remaining_seconds"] > 20, "SAVE_RESERVE")
    return raw


def tick(deadline):
    return budget_snapshot(deadline.status())


def safe(raw):
    need(type(raw) is str and raw and "\x00" not in raw, "PATH_STRING")
    path = Path(raw)
    path = ROOT / path if not path.is_absolute() else path
    resolved = path.resolve()
    need(resolved.is_relative_to(ROOT), "PATH_SCOPE")
    current = path
    while current != ROOT and current.is_relative_to(ROOT):
        need(not current.is_symlink() and not current.is_junction(), "PATH_LINK")
        current = current.parent
    return resolved


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "JSON_DUPLICATE")
            result[key] = value
        return result
    def nonfinite(_):
        raise ValueError("JSON_NONFINITE")
    return json.loads(raw.decode("utf8"), object_pairs_hook=pairs, parse_constant=nonfinite)


class Reader:
    def __init__(self, deadline):
        self.deadline, self.pins = deadline, {}

    def read(self, raw, expected, parse=True):
        need(type(expected) is str and re.fullmatch("[0-9a-f]{64}", expected), "SHA256_STRING")
        path = safe(raw)
        need(path.is_file() and path.stat().st_size <= MAX_BYTES, "FILE_BOUND")
        key = path.relative_to(ROOT).as_posix()
        need(key not in self.pins or self.pins[key] == expected, "PIN_CONFLICT")
        digest, blocks, size = hashlib.sha256(), [], 0
        with path.open("rb") as handle:
            while True:
                tick(self.deadline)
                block = handle.read(1024 * 1024)
                if not block:
                    break
                size += len(block)
                need(size <= MAX_BYTES, "FILE_BOUND")
                digest.update(block)
                if parse:
                    blocks.append(block)
        need(digest.hexdigest() == expected, "INPUT_HASH")
        self.pins[key] = expected
        tick(self.deadline)
        return strict_json(b"".join(blocks)) if parse else None

    def mapping(self, raw):
        need(type(raw) is dict and raw, "INPUT_MAP")
        for path, digest in raw.items():
            self.read(path, digest, False)

    def closing(self):
        self.mapping(dict(self.pins))


def save(path, value, deadline):
    tick(deadline)
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf8")
    need(len(raw) <= MAX_BYTES, "OUTPUT_BOUND")
    temporary = path.with_suffix(path.suffix + ".tmp")
    tick(deadline)
    with temporary.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    tick(deadline)
    os.replace(temporary, path)
    tick(deadline)


def q_universe(size):
    need(type(size) is int and 4 <= size <= 17, "SUPPORT_SIZE")
    return [list(q) for k in (1, 2, 3) for q in itertools.combinations(range(size), k)] + [list(range(size))]


def packet(raw):
    need(type(raw) is dict and set(raw) == {"target_order", "target_degree", "support_adjacency",
         "ordered_masks", "counts", "pair_bits"}, "PACKET_FIELDS")
    order, degree, h = raw["target_order"], raw["target_degree"], raw["support_adjacency"]
    need(type(order) is int and type(degree) is int and 0 <= degree < order, "TARGET_INTEGER")
    need(type(h) is list and 4 <= len(h) <= 17
         and all(type(row) is list and len(row) == len(h) for row in h), "GRAPH_SHAPE")
    m = len(h)
    need(order > m and all(type(x) is int and x in (0, 1) for row in h for x in row)
         and all(h[u][u] == 0 and h[u][v] == h[v][u] for u in range(m) for v in range(m)), "GRAPH_DOMAIN")
    masks = raw["ordered_masks"]
    need(type(masks) is list and masks and all(type(mask) is int and 0 <= mask < 1 << m for mask in masks), "TYPE_MASK_INTEGER")
    need(masks == sorted(set(masks)), "TYPE_MASK_ORDER")
    counts = raw["counts"]
    need(type(counts) is list and len(counts) == len(masks), "COUNT_SHAPE")
    need(all(type(x) is int for x in counts), "COUNT_INTEGER")
    need(all(0 <= x <= order-m for x in counts), "COUNT_BOUND")
    need(sum(counts) == order-m, "COUNT_SUM")
    table = raw["pair_bits"]
    n = len(masks)
    need(type(table) is list and len(table) == n*(n+1)//2, "PAIR_POPULATION")
    bits = {}
    for item, (i, j) in zip(table, itertools.combinations_with_replacement(range(n), 2)):
        need(type(item) is dict and set(item) == {"i", "j", "bits"}, "PAIR_KEYS")
        need(type(item["i"]) is int and type(item["j"]) is int and [item["i"], item["j"]] == [i, j], "PAIR_COORDINATES")
        value = item["bits"]
        need(type(value) is list and all(type(x) is int and x in (0, 1) for x in value)
             and value == sorted(set(value)), "PAIR_BITS")
        bits[i, j] = value
    # These are consequences of the qualified count premise, repeated for clear finite input failure semantics.
    for (i, j), value in bits.items():
        if not value and counts[i] and counts[j]:
            need(i == j, "INCOMPATIBLE_COEXISTENCE")
            need(counts[i] <= 1, "EQUAL_MULTIPLICITY")
    return h, masks, counts, bits


def screen(raw, deadline, out=None):
    h, masks, counts, bits = packet(raw)
    size = len(h)
    qs = q_universe(size)
    # Explicit distinct labels, not a uniform/equitable neighbor count assumption.
    pool = [[i, copy_index] for i, number in enumerate(counts) for copy_index in range(number)]
    positive = [i for i, number in enumerate(counts) if number]
    all_rows, first, failed_types = [], None, 0
    for i in positive:
        tick(deadline)
        focal = [i, 0]
        t = [(masks[i] >> u) & 1 for u in range(size)]
        required_degree = raw["target_degree"] - sum(t)
        b = [2-t[u]-sum(h[u][v]*t[v] for v in range(size)) for u in range(size)]
        eligible, mandatory, optional = [], [], []
        for label in pool:
            if label == focal:
                continue
            j = label[0]
            pair = bits[min(i, j), max(i, j)]
            if 1 in pair:
                eligible.append(label)
                (mandatory if pair == [1] else optional).append(label)
        free_degree = required_degree-len(mandatory)
        capacity_stage = ("MANDATORY_CAPACITY" if free_degree < 0 else
                          "NEIGHBOR_CAPACITY" if free_degree > len(optional) else None)
        rows = []
        for q_index, q in enumerate(qs):
            tick(deadline)
            qmask = sum(1 << u for u in q)
            demand = sum(b[u] for u in q)
            fixed_sum = sum((masks[j] & qmask).bit_count() for j, _ in mandatory)
            ranked = sorted([((masks[j] & qmask).bit_count(), j, c) for j, c in optional])
            if capacity_stage is None:
                low = ranked[:free_degree]
                high = ranked[len(ranked)-free_degree:] if free_degree else []
                minimum = fixed_sum+sum(value for value, _, _ in low)
                maximum = fixed_sum+sum(value for value, _, _ in high)
                holds = minimum <= demand <= maximum
                stage = None if holds else "ROW_BOUND"
                lower_witness = [[j, c] for _, j, c in low]
                upper_witness = [[j, c] for _, j, c in high]
            else:
                minimum = maximum = lower_witness = upper_witness = None
                holds, stage = False, capacity_stage
            row = dict(q_index=q_index, Q=q, required_sum=demand, mandatory_sum=fixed_sum,
                minimum_sum=minimum, maximum_sum=maximum, lower_optional_labels=lower_witness,
                upper_optional_labels=upper_witness, bounds_defined=capacity_stage is None,
                necessary_bound_holds=holds, violation_stage=stage)
            rows.append(row)
            if stage and first is None:
                first = dict(type_index=i, mask=masks[i], focal_label=focal, q_index=q_index, Q=q,
                    required_outside_degree=required_degree, eligible_count=len(eligible),
                    mandatory_count=len(mandatory), optional_count=len(optional), residual_degree=free_degree,
                    required_sum=demand, mandatory_sum=fixed_sum, minimum_sum=minimum,
                    maximum_sum=maximum, violation_stage=stage)
        failed = any(not row["necessary_bound_holds"] for row in rows)
        failed_types += int(failed)
        result = dict(schema="FIXED_COUNT_NEIGHBOR_CAPACITY_TYPE_ROWS_V1", type_index=i, mask=masks[i],
            count=counts[i], focal_label=focal, all_same_type_copies_have_identical_screen_inputs=True,
            required_outside_degree=required_degree, b=b, eligible_labels=eligible,
            mandatory_labels=mandatory, optional_labels=optional, residual_degree=free_degree,
            capacity_stage=capacity_stage, q_count=len(qs), failed=failed, rows=rows)
        all_rows.append(result if out is None else dict(type_index=i))
        if out is not None:
            save(out/("type_%03d.json" % i), result, deadline)
            save(out/("checkpoint_%03d.json" % i), dict(completed_positive_type_indices=[r["type_index"] for r in all_rows],
                 first_violation=first, screened_rows=len(all_rows)*len(qs), deadline=deadline.status()), deadline)
    return dict(schema="FIXED_COUNT_NEIGHBOR_CAPACITY_SCREEN_OUTCOME_V1", positive_type_indices=positive,
        positive_types=len(positive), labelled_outside_pool=pool, outside_copies=len(pool),
        q_universe=qs, q_per_positive_type=len(qs), complete_q_rows=len(positive)*len(qs),
        failed_positive_types=failed_types, first_violation=first, all_screens_pass=first is None,
        self_exclusion=True, mandatory_bit_one_enforced=True, no_uniform_profile_assumed=True,
        graph_completion=False, integer_witness_rejected_by_necessary_screen=first is not None,
        target_exclusion=False, rows=all_rows if out is None else None)


def count_gate(raw, required):
    need(type(raw) is dict and raw.get("status") == "INDEPENDENT_EXTERNAL_MOMENT_INTEGER_COUNTS_V1_COMPLETE_PASS"
         and raw.get("mode") == "full" and type(raw.get("implementation_version")) is int
         and raw["implementation_version"] == 1 and raw.get("producer") == "/root/checkpoint_audit"
         and raw.get("verifier") == "/root/native_driver" and raw.get("method") == "independent_artifact_check"
         and raw.get("target_resolution") == "NONE", "COUNT_GATE_HEADER")
    need(type(raw.get("inputs_sha256")) is dict and all(raw["inputs_sha256"].get(p) == digest
         for p, digest in required.items()), "COUNT_GATE_DIRECT_PINS")
    counts = dict(complete_count_variables=472, complete_presence_variables=472, complete_moment_rows=154,
        complete_common_Q_caps=680, complete_pair_records=111628, complete_pair_record_fields=19,
        complete_pair_read_checkpoints=23)
    outcome = raw.get("outcome")
    need(type(outcome) is dict and all(type(outcome.get(k)) is int and outcome[k] == v for k, v in counts.items())
         and outcome.get("candidate_exact_checked") is True and outcome.get("graph_completion") is False, "COUNT_GATE_SCOPE")


def raw_pairs(reader, masks, gate):
    need(type(gate) is dict and gate.get("status") == "INDEPENDENT_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE_PASS"
         and type(gate.get("implementation_version")) is int and gate["implementation_version"] == 2
         and gate.get("producer") == "/root/structural" and gate.get("verifier") == "/root/native_driver"
         and gate.get("method") == "independent_artifact_check" and gate.get("target_resolution") == "NONE", "PAIR_GATE_HEADER")
    pins = gate.get("inputs_sha256")
    need(type(pins) is dict and PAIR_RAW+"summary.json" in pins, "PAIR_RAW_SUMMARY_PIN")
    summary = reader.read(PAIR_RAW+"summary.json", pins[PAIR_RAW+"summary.json"])
    expected = {"scaled_input.json"} | {"%s_%03d.json" % (prefix, p) for prefix in ("part", "checkpoint") for p in range(23)}
    need(type(summary.get("outputs_sha256")) is dict and set(summary["outputs_sha256"]) == expected, "PAIR_RAW_POPULATION")
    for name, digest in summary["outputs_sha256"].items():
        need(pins.get(PAIR_RAW+name) == digest, "PAIR_RAW_DIRECT_PIN")
    table, index = [], 0
    labels = iter(itertools.combinations_with_replacement(range(472), 2))
    for p in range(23):
        tick(reader.deadline)
        raw = reader.read(PAIR_RAW+("part_%03d.json" % p), summary["outputs_sha256"]["part_%03d.json" % p])
        start, stop = p*5000, min((p+1)*5000, 111628)
        need(type(raw) is dict and raw.get("schema") == "DUAL_GRAM_PAIR_PART_V1"
             and all(type(raw.get(k)) is int and raw[k] == v for k, v in
                     dict(part_index=p, start=start, stop=stop, count=stop-start).items())
             and type(raw.get("records")) is list and len(raw["records"]) == stop-start, "PAIR_PART_HEADER")
        for row in raw["records"]:
            tick(reader.deadline)
            i, j = next(labels)
            need(type(row) is dict and set(row) == set(PAIR_FIELDS)
                 and all(type(row[k]) is int for k in PAIR_FIELDS[:14]), "PAIR_RECORD_FIELDS")
            need(same([row[k] for k in ("proposal_id", "i", "j", "left_mask", "right_mask")],
                      [index, i, j, masks[i], masks[j]]), "PAIR_RECORD_COORDINATES")
            for key in PAIR_FIELDS[14:18]:
                value = row[key]
                need(type(value) is list and all(type(x) is int and x in (0, 1) for x in value)
                     and value == sorted(set(value)), "PAIR_RECORD_BITS")
            joint = sorted(set(row["upper_bits"]) & set(row["lower_bits"]) & set(row["cn_bits"]))
            need(same(row["combined_bits"], joint) and row["classification"] == CLASS_NAMES[tuple(joint)], "PAIR_RECORD_INTERSECTION")
            table.append(dict(i=i, j=j, bits=list(joint)))
            index += 1
        reader.read(PAIR_RAW+("checkpoint_%03d.json" % p), summary["outputs_sha256"]["checkpoint_%03d.json" % p], False)
    reader.read(PAIR_RAW+"scaled_input.json", summary["outputs_sha256"]["scaled_input.json"], False)
    need(index == 111628 and next(labels, None) is None, "PAIR_EOF")
    return table


def qualify_calibration(reader, raw, required):
    need(type(raw) is dict and raw.get("status") == CAL_STATUS and raw.get("mode") == "calibrate"
         and raw.get("producer") == "/root/checkpoint_audit" and raw.get("independent_approval") is False,
         "AUTHOR_CALIBRATION_HEADER")
    need(type(raw.get("source_software")) is dict and all(raw["source_software"].get(p) == digest for p, digest in required.items()),
         "AUTHOR_CALIBRATION_SOURCE")
    need(same(raw.get("outcome", {}).get("counts"), CONTROL_COUNTS)
         and raw["outcome"].get("stage_mismatches") == [] and type(raw.get("outputs_sha256")) is dict,
         "AUTHOR_CALIBRATION_COUNTS")
    root = safe(raw["output_root"])
    need(set(path.name for path in root.iterdir()) == set(raw["outputs_sha256"]) | {"summary.json"}, "AUTHOR_CALIBRATION_POPULATION")
    for name, digest in raw["outputs_sha256"].items():
        need(type(name) is str and Path(name).name == name, "AUTHOR_CALIBRATION_NAME")
        reader.read(str(root/name), digest, False)


def scientific(reader, config, out, software):
    need(type(config) is dict and config.get("schema") == "FIXED17_COUNT_NEIGHBOR_CAPACITY_CONFIGURATION_V1"
         and type(config.get("inputs_sha256")) is dict and config.get("target_resolution") == "NONE", "CONFIGURATION_HEADER")
    need(all(config["inputs_sha256"].get(p) == digest for p, digest in {**COUNT_PINS,
         PAIR_GATE_PATH:PAIR_GATE_SHA, PAIR_ROOT_PATH:PAIR_ROOT_SHA,
         COUNT_GATE_PATH:COUNT_GATE_SHA, COUNT_ROOT_PATH:COUNT_ROOT_SHA}.items()), "CONFIGURATION_DIRECT_PINS")
    # The separately reviewed exact written proof is a hash-pinned premise. Its mathematical
    # acceptance is external to this discovery producer, not inferred from an arbitrary status string.
    proof = config.get("independent_row_bound_proof")
    need(type(proof) is dict and set(proof) == {"path", "sha256"}
         and type(proof["path"]) is str and config["inputs_sha256"].get(proof["path"]) == proof["sha256"],
         "WRITTEN_PROOF_DIRECT_PIN")
    reader.mapping(config["inputs_sha256"])
    reader.read(proof["path"], proof["sha256"], False)
    cal = reader.read(config["author_calibration_path"], config["author_calibration_sha256"])
    qualify_calibration(reader, cal, software)
    gate = reader.read(COUNT_GATE_PATH, COUNT_GATE_SHA)
    count_gate(gate, COUNT_PINS)
    # Complete fixed direct input artifacts and raw pair bits are authenticated here; no ancestor crawler or solver.
    parsed = reader.read(COUNT_BASE+"parsed_fixed_input.json", COUNT_PINS[COUNT_BASE+"parsed_fixed_input.json"])
    candidate = reader.read(COUNT_BASE+"exact_integer_candidate.json", COUNT_PINS[COUNT_BASE+"exact_integer_candidate.json"])
    need(type(candidate) is dict and set(candidate) == {"schema", "ordered_masks", "counts", "presence",
         "integer", "exact_constraints", "independent_approval", "graph_completion"}
         and candidate["schema"] == "FIXED17_EXACT_INTEGER_TYPE_COUNTS_V1"
         and candidate["integer"] is True and candidate["exact_constraints"] is True
         and candidate["independent_approval"] is False and candidate["graph_completion"] is False, "CANDIDATE_HEADER")
    masks = candidate["ordered_masks"]
    need(type(parsed) is dict and same(parsed.get("ordered_masks"), masks)
         and type(masks) is list and len(masks) == 472, "PARSED_COUNT_MASKS")
    presence = candidate["presence"]
    need(type(presence) is list and len(presence) == 472 and all(type(x) is int and x in (0, 1) for x in presence)
         and type(candidate["counts"]) is list and len(candidate["counts"]) == 472
         and all(type(x) is int for x in candidate["counts"])
         and presence == [int(x > 0) for x in candidate["counts"]], "CANDIDATE_PRESENCE")
    pairgate = reader.read(PAIR_GATE_PATH, PAIR_GATE_SHA)
    table = raw_pairs(reader, masks, pairgate)
    payload = dict(target_order=99, target_degree=14, support_adjacency=parsed["induced_adjacency"],
         ordered_masks=masks, counts=candidate["counts"], pair_bits=table)
    need(len(payload["support_adjacency"]) == 17, "FIXED17_SUPPORT")
    save(out/"parsed_screen_input.json", payload, reader.deadline)
    result = screen(payload, reader.deadline, out)
    need(result["q_per_positive_type"] == 834 and result["outside_copies"] == 82, "SCREEN_SCOPE")
    save(out/"screen_outcome.json", result, reader.deadline)
    return result


def rook_fixture(forced=False):
    h = [[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1], [0, 1, 1, 0]]
    masks = [0, 3, 5, 10, 12]
    adjacent = {(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 3)}
    table = [dict(i=i, j=j, bits=([int((i, j) in adjacent)] if forced and i != j else [0, 1]))
             for i, j in itertools.combinations_with_replacement(range(5), 2)]
    return dict(target_order=9, target_degree=4, support_adjacency=h, ordered_masks=masks, counts=[1]*5, pair_bits=table)


def controls(out, deadline):
    routes = []
    free, forced = rook_fixture(), rook_fixture(True)
    def checked(payload):
        result = screen(payload, deadline)
        if not result["all_screens_pass"]:
            raise ScreenReject(result["first_violation"]["violation_stage"], result)
        return result
    routes += [("known_rook_rectangle_free", "PASS", free, checked),
               ("known_rook_rectangle_forced", "PASS", forced, checked)]
    def pool_test(payload):
        result = screen(payload, deadline)
        row = result["rows"][0]
        need(row["focal_label"] not in row["eligible_labels"] and len(row["eligible_labels"]) == 4, "SELF_EXCLUSION_CONTROL")
        need(result["all_screens_pass"], "KNOWN_ROOK_SCREEN")
        return result
    routes.append(("self_is_excluded_from_five_copy_pool", "PASS", copy.deepcopy(free), pool_test))
    def mandatory_test(payload):
        result = screen(payload, deadline)
        need(result["all_screens_pass"] and all(r["residual_degree"] == 0 and len(r["mandatory_labels"]) == r["required_outside_degree"]
             and all(q["minimum_sum"] == q["required_sum"] == q["maximum_sum"] for q in r["rows"]) for r in result["rows"]), "FORCED_CONTROL")
        return result
    routes.append(("forced_one_slots_exactly_meet_every_Q", "PASS", copy.deepcopy(forced), mandatory_test))
    routes.append(("budget_above_save_reserve", "PASS", dict(stop_required=False, remaining_seconds=20.000001), budget_snapshot))
    gate = dict(status="INDEPENDENT_EXTERNAL_MOMENT_INTEGER_COUNTS_V1_COMPLETE_PASS", mode="full", implementation_version=1,
        producer="/root/checkpoint_audit", verifier="/root/native_driver", method="independent_artifact_check", target_resolution="NONE",
        inputs_sha256={"synthetic.json":"0"*64}, outcome=dict(complete_count_variables=472, complete_presence_variables=472,
            complete_moment_rows=154, complete_common_Q_caps=680, complete_pair_records=111628,
            complete_pair_record_fields=19, complete_pair_read_checkpoints=23, candidate_exact_checked=True, graph_completion=False))
    gatecheck = lambda p:count_gate(p, {"synthetic.json":"0"*64})
    routes.append(("genuine_shaped_count_gate", "PASS", gate, gatecheck))
    routes.append(("full_Q_is_separate_after_size_three", "PASS", dict(size=17),
        lambda p:need(len(q_universe(p["size"])) == 834 and q_universe(p["size"])[-1] == list(range(17)), "Q_UNIVERSE")))
    # A row-kernel boundary fixture, not a feasible complete target moment system: two copies,
    # full support in a matching H4, zero exterior degree, and no forced adjacency.
    repeated = dict(target_order=6, target_degree=4,
        support_adjacency=[[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
        ordered_masks=[15], counts=[2], pair_bits=[dict(i=0, j=0, bits=[0])])
    routes.append(("same_type_two_copies_zero_exterior_degree", "PASS", repeated, checked))
    def mutate(name, expected, original, change, action=checked):
        p = copy.deepcopy(original)
        change(p)
        routes.append((name, expected, p, action))
    mutate("count_bool", "COUNT_INTEGER", free, lambda p:p["counts"].__setitem__(0, True))
    mutate("count_float", "COUNT_INTEGER", free, lambda p:p["counts"].__setitem__(0, 1.0))
    mutate("count_negative", "COUNT_BOUND", free, lambda p:p["counts"].__setitem__(0, -1))
    mutate("count_missing", "COUNT_SHAPE", free, lambda p:p["counts"].pop())
    mutate("count_sum_changed", "COUNT_SUM", free, lambda p:p["counts"].__setitem__(0, 0))
    mutate("mask_bool", "TYPE_MASK_INTEGER", free, lambda p:p["ordered_masks"].__setitem__(0, False))
    mutate("mask_float", "TYPE_MASK_INTEGER", free, lambda p:p["ordered_masks"].__setitem__(0, 0.0))
    mutate("mask_order", "TYPE_MASK_ORDER", free, lambda p:p["ordered_masks"].reverse())
    mutate("graph_bool", "GRAPH_DOMAIN", free, lambda p:p["support_adjacency"][0].__setitem__(0, False))
    mutate("pair_label_bool", "PAIR_COORDINATES", free, lambda p:p["pair_bits"][0].__setitem__("i", False))
    mutate("pair_bits_bool", "PAIR_BITS", free, lambda p:p["pair_bits"][0].__setitem__("bits", [False, 1]))
    mutate("pair_bits_reordered", "PAIR_BITS", free, lambda p:p["pair_bits"][0].__setitem__("bits", [1, 0]))
    mutate("pair_missing", "PAIR_POPULATION", free, lambda p:p["pair_bits"].pop())
    mutate("incompatible_positive_types", "INCOMPATIBLE_COEXISTENCE", free, lambda p:p["pair_bits"][1].__setitem__("bits", []))
    isolated = dict(target_order=5, target_degree=1, support_adjacency=[[0]*4 for _ in range(4)],
        ordered_masks=[0], counts=[1], pair_bits=[dict(i=0, j=0, bits=[0, 1])])
    routes.append(("self_copy_cannot_supply_its_own_degree", "NEIGHBOR_CAPACITY", isolated, checked))
    mutate("eligible_pool_short", "NEIGHBOR_CAPACITY", free, lambda p:p.__setitem__("target_degree", 6))
    mutate("forced_one_exceeds_degree", "MANDATORY_CAPACITY", forced, lambda p:p.__setitem__("target_degree", 3))
    bad = copy.deepcopy(free)
    # The all-empty five-copy vector has valid slots and degree four, but each singleton demand two cannot be supplied.
    bad["ordered_masks"], bad["counts"] = [0], [5]
    bad["pair_bits"] = [dict(i=0, j=0, bits=[0, 1])]
    routes.append(("deliberately_bad_empty_type_vector", "ROW_BOUND", bad, checked))
    equal = copy.deepcopy(bad)
    equal["pair_bits"][0]["bits"] = []
    routes.append(("forbidden_equal_type_has_two_distinct_copies", "EQUAL_MULTIPLICITY", equal, checked))
    mutate("gate_unchecked_candidate", "COUNT_GATE_SCOPE", gate, lambda p:p["outcome"].__setitem__("candidate_exact_checked", False), gatecheck)
    mutate("gate_bool_count", "COUNT_GATE_SCOPE", gate, lambda p:p["outcome"].__setitem__("complete_count_variables", True), gatecheck)
    routes.append(("budget_at_save_reserve", "SAVE_RESERVE", dict(stop_required=False, remaining_seconds=20), budget_snapshot))
    routes.append(("budget_review_stop", "SAVE_RESERVE", dict(stop_required=True, remaining_seconds=100), budget_snapshot))
    need(len(routes) == CONTROL_COUNTS["total"] and sum(stage == "PASS" for _, stage, _, _ in routes) == CONTROL_COUNTS["positive"], "CONTROL_DECLARATION")
    table, mismatches = [], []
    for index, (name, expected, payload, action) in enumerate(routes):
        tick(deadline)
        save(out/("control_%02d_%s.json" % (index, name)), payload, deadline)
        value = None
        try:
            value, actual = action(payload), "PASS"
        except ValueError as exc:
            actual = str(exc)
            if isinstance(exc, ScreenReject):
                value = exc.result
        row = dict(index=index, name=name, expected_stage=expected, actual_stage=actual, matches=expected == actual)
        table.append(row)
        if expected != actual:
            mismatches.append(row)
        if value is not None:
            save(out/("result_%02d.json" % index), value, deadline)
    save(out/"controls.json", table, deadline)
    need(not mismatches, "AUTHOR_CONTROL_STAGE_MISMATCH")
    return dict(counts=CONTROL_COUNTS, stage_mismatches=mismatches, table=table,
        known_graph_fixture="nine-vertex rook graph, four-corner support, five actual exterior vertices",
        actual_count_witness_read=False, native_solver_calls=0)


def output_hashes(out, deadline):
    hashes = {}
    for path in sorted(out.iterdir()):
        tick(deadline)
        need(path.is_file() and not path.is_symlink() and path.suffix != ".tmp", "OUTPUT_POPULATION")
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                tick(deadline)
                block = handle.read(1024*1024)
                if not block:
                    break
                digest.update(block)
        hashes[path.name] = digest.hexdigest()
    return hashes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("calibrate", "screen"))
    for name in ("seconds", "out", "self-sha256", "spec-sha256", "executor"):
        parser.add_argument("--"+name, required=True, type=float if name == "seconds" else str)
    parser.add_argument("--configuration")
    parser.add_argument("--configuration-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="One exact necessary finite neighbor-capacity screen or fresh finite author qualification; all authentication and saves share this deadline")
    out = safe(args.out)
    need(out.is_relative_to(ROOT/"acceleration/results") and not out.exists(), "OUTPUT_FRESH_SCOPE")
    out.mkdir(parents=True)
    reader = Reader(deadline)
    software = {**SOFTWARE, SELF.relative_to(ROOT).as_posix():args.self_sha256, SPEC.relative_to(ROOT).as_posix():args.spec_sha256}
    try:
        reader.mapping(software)
        if args.mode == "calibrate":
            outcome, status = controls(out, deadline), CAL_STATUS
        else:
            need(args.configuration is not None and args.configuration_sha256 is not None, "CONFIGURATION_ARGUMENTS")
            config = reader.read(args.configuration, args.configuration_sha256)
            outcome = scientific(reader, config, out, software)
            status = "CANDIDATE_FIXED17_COUNT_NEIGHBOR_CAPACITY_SCREEN_V1"
        reader.closing()
        outputs = output_hashes(out, deadline)
        report = dict(schema="FIXED17_COUNT_NEIGHBOR_CAPACITY_PRODUCER_REPORT_V1", status=status, implementation_version=1,
            mode=args.mode, timestamp=datetime.now(timezone.utc).isoformat(), producer="/root/checkpoint_audit",
            source_author="/root/checkpoint_audit", executor_declaration=args.executor,
            executor_identity_requires_external_runtime_receipt=True, independent_approval=False,
            independent_verifier=None, independent_verifier_null_reason="Distinct source/control and complete raw screen verification required",
            target_resolution="NONE", source_software=software, inputs_sha256=dict(reader.pins),
            outputs_sha256=outputs, output_root=out.relative_to(ROOT).as_posix(), outcome=outcome,
            command=sys.argv, cwd=str(ROOT), deadline=deadline.status(), actual_count_witness_read=args.mode == "screen",
            scientific_solver_calls=0, automatic_retry=False, ledger_index_git_mutations=0,
            shared_components=["Pinned common Python/json/SHA/path and command_deadline conventions; no solver or producer/checker imports",
                "Root selected the finite screening question; Structural independently derived the block equation and necessary multiset bounds",
                "Qualified Native count/pair artifacts are immutable premises, not new Gram/count arithmetic approval"],
            limitations=["Failing a bound rejects only this literal count witness under the pinned necessary pair constraints",
                "Passing all selected 834 Q screens per positive type does not construct a graph or solve simultaneous neighbor constraints",
                "One labelled representative per positive type has identical candidate screen inputs for every same-type copy; no uniform actual neighbor profile is asserted",
                "Capacity failures retain every Q demand but min/max are null because no D-neighbor selection exists; they are not fabricated finite bounds",
                "Completed per-type files/checkpoints persist; a hard stop or unexpected exception can lose an in-memory type suffix",
                "Save guard and actual containment are observed engineering scope, not an OS/filesystem hard-real-time guarantee"])
        save(out/"summary.json", report, deadline)
        reader.closing()
        tick(deadline)
        print(json.dumps(dict(status=status, positive_types=outcome.get("positive_types"), first_violation=outcome.get("first_violation"))), flush=True)
    except Exception as exc:
        try:
            (out/"failure.json").write_text(json.dumps(dict(status="FAILED_PRESERVED", stage=str(exc), exception=type(exc).__name__,
                timestamp=datetime.now(timezone.utc).isoformat(), inputs_sha256=reader.pins, target_resolution="NONE",
                automatic_retry=False, deadline=deadline.status()), indent=2, allow_nan=False)+"\n", encoding="utf8")
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()

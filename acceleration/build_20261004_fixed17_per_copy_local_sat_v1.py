"""Source-only proposal: exact CNF for the fixed-count exterior local rows.

No solver is called. The historical module is not imported: a future authorized
invocation authenticates its bytes and extracts only negate/Clauses/Encoder.
"""
from __future__ import annotations

import argparse
import ast
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/build_20261004_fixed17_per_copy_local_sat_v1.py"
SPEC = "acceleration/build_20261004_fixed17_per_copy_local_sat_v1_spec.md"
HELPER = "acceleration/theory_20260930_eight_full99_cnf.py"
HELPER_SHA = "21c357543c9397456a911175b277da6e6caa769be31d18c12e034cc76d99074c"
PINS = {
    HELPER: HELPER_SHA,
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command_v2.py": "46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
AUTHOR_STATUS = "FIXED17_PER_COPY_LOCAL_SAT_V1_AUTHOR_CONTROLS_PASS"
BUILD_STATUS = "CANDIDATE_FIXED17_PER_COPY_LOCAL_SAT_V1_COMPLETE_ENCODING"
COPY_STATUS = "INDEPENDENT_FIXED17_PER_COPY_ADJACENCY_V1_COMPLETE_PASS"
ENCODING_CONTROL_STATUS = "INDEPENDENT_FIXED17_PER_COPY_LOCAL_SAT_V1_AUTHOR_CONTROLS_PASS"
MAX_JSON_BYTES = 64 * 1024 * 1024
MAX_BODY_BYTES = 256 * 1024 * 1024


class GuardError(RuntimeError):
    def __init__(self, stage: str, reason: str):
        super().__init__(reason)
        self.stage = stage


class SaveStop(RuntimeError):
    pass


def require(condition, stage, reason):
    if not condition:
        raise GuardError(stage, reason)


def integer(value):
    return type(value) is int


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return set(a) == set(b) and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


class Budget:
    def __init__(self, seconds):
        self.deadline = CommandDeadline(seconds, allocation_reason="New local CNF encoding or finite engineering controls; all preparation and closing hashes share this invocation.")

    def tick(self):
        status = self.deadline.status()
        if status["stop_required"] or status["remaining_seconds"] <= 20:
            raise SaveStop("not completed within the allocated budget; save reserve reached")

    def save_tick(self):
        if self.deadline.status()["remaining_seconds"] <= 0:
            raise SaveStop("save reserve exhausted")

    def check(self):
        self.tick()


def path_for(relative):
    require(type(relative) is str and relative and "\\" not in relative, "PATH", "relative POSIX path required")
    candidate = Path(relative)
    require(not candidate.is_absolute() and all(p not in ("", ".", "..") for p in candidate.parts), "PATH", "unconfined path")
    current = ROOT
    for part in candidate.parts:
        current /= part
        require(not current.is_symlink() and not (hasattr(current, "is_junction") and current.is_junction()), "PATH", "link or junction rejected")
    resolved = current.resolve()
    require(resolved.is_relative_to(ROOT), "PATH", "outside workspace")
    return resolved


def raw_read(path, budget, *, limit=MAX_JSON_BYTES):
    budget.tick()
    require(path.is_file(), "FILE", "missing regular file")
    require(path.stat().st_size <= limit, "FILE_SIZE", "bounded input size exceeded")
    data = bytearray()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            budget.tick()
            data.extend(chunk)
            require(len(data) <= limit, "FILE_SIZE", "input grew beyond bound")
    budget.tick()
    return bytes(data)


def hash_path(path, budget, *, limit=MAX_BODY_BYTES + MAX_JSON_BYTES):
    budget.tick()
    require(path.is_file() and path.stat().st_size <= limit, "FILE_SIZE", "bounded regular file required")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            budget.tick()
            digest.update(chunk)
    budget.tick()
    return digest.hexdigest()


def pairs_object(items):
    result = {}
    for key, value in items:
        require(key not in result, "JSON_DUPLICATE", "duplicate key")
        result[key] = value
    return result


def decode(data):
    def nonfinite(value):
        raise GuardError("JSON_NONFINITE", "nonfinite number: " + value)
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=pairs_object, parse_constant=nonfinite)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GuardError("JSON", str(exc)) from exc


def read_ref(ref, budget, inputs):
    require(type(ref) is dict and set(ref) == {"path", "sha256"}, "REFERENCE", "exact path/hash reference required")
    require(type(ref["sha256"]) is str and len(ref["sha256"]) == 64 and all(c in "0123456789abcdef" for c in ref["sha256"]), "REFERENCE", "canonical SHA256 required")
    data = raw_read(path_for(ref["path"]), budget)
    require(hashlib.sha256(data).hexdigest() == ref["sha256"], "INPUT_HASH", "input hash mismatch")
    require(ref["path"] not in inputs or inputs[ref["path"]] == ref["sha256"], "INPUT_ALIAS", "conflicting path identity")
    inputs[ref["path"]] = ref["sha256"]
    return decode(data)


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def save(path, value, budget, *, emergency=False):
    tick = budget.save_tick if emergency else budget.tick
    tick()
    require(not path.exists(), "OUTPUT_EXISTS", "fresh output required")
    temporary = path.with_name(path.name + ".writing")
    data = json_bytes(value)
    require(len(data) <= MAX_JSON_BYTES, "OUTPUT_SIZE", "bounded JSON output required")
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    tick()
    os.replace(temporary, path)
    tick()


def software(self_sha, spec_sha, budget):
    pins = dict(PINS, **{SELF: self_sha, SPEC: spec_sha})
    for name, expected in pins.items():
        require(hash_path(path_for(name), budget) == expected, "SOFTWARE_HASH", "source mismatch: " + name)
    return pins


def helper(budget):
    """Future execution only. No historical imports, top-level statements or cap."""
    data = raw_read(path_for(HELPER), budget)
    require(hashlib.sha256(data).hexdigest() == HELPER_SHA, "HELPER_HASH", "immutable helper mismatch")
    tree = ast.parse(data.decode("utf-8"), filename=HELPER)
    wanted = ["negate", "Clauses", "Encoder"]
    nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in wanted]
    require([node.name for node in nodes] == wanted, "HELPER_DEFINITIONS", "three exact helper definitions required")
    isolated = ast.Module(body=nodes, type_ignores=[])
    namespace = {}
    exec(compile(isolated, HELPER, "exec"), namespace)
    budget.tick()
    base = namespace["Encoder"]

    class TimedEncoder(base):
        def recurrence(self, a, b, c):
            budget.tick()
            return super().recurrence(a, b, c)

    namespace["Encoder"] = TimedEncoder
    return namespace


def profile(value, budget=None):
    if budget is not None:
        budget.tick()
    keys = {"target_order", "target_degree", "support_adjacency", "ordered_masks", "counts", "pair_bits"}
    require(type(value) is dict and set(value) == keys, "PROFILE_FIELDS", "profile fields differ")
    n, k, h, masks, counts, bit_rows = (value[name] for name in ("target_order", "target_degree", "support_adjacency", "ordered_masks", "counts", "pair_bits"))
    require(integer(n) and integer(k) and 0 < k < n - 1 and n <= 99, "PROFILE_TARGET", "bounded nontrivial typed target required")
    require(type(h) is list and 0 < len(h) < n and len(h) <= 17 and all(type(row) is list and len(row) == len(h) for row in h), "PROFILE_GRAPH", "bounded square support graph required")
    m = len(h)
    require(all(integer(h[u][v]) and h[u][v] in (0, 1) and h[u][v] == h[v][u] and (u != v or h[u][v] == 0) for u in range(m) for v in range(m)), "PROFILE_GRAPH", "binary symmetric zero diagonal required")
    require(type(masks) is list and 0 < len(masks) <= 472 and all(integer(t) and 0 <= t < 1 << m for t in masks) and all(a < b for a, b in zip(masks, masks[1:])), "PROFILE_MASKS", "bounded strictly increasing masks required")
    require(type(counts) is list and len(counts) == len(masks) and all(integer(c) and c >= 0 for c in counts) and sum(counts) == n - m, "PROFILE_COUNTS", "outside count population differs")
    q = len(masks)
    require(type(bit_rows) is list and len(bit_rows) == q * (q + 1) // 2, "PROFILE_PAIR_POPULATION", "complete pair table required")
    bits = {}
    for row, (i, j) in zip(bit_rows, itertools.combinations_with_replacement(range(q), 2)):
        if budget is not None:
            budget.tick()
        require(type(row) is dict and set(row) == {"i", "j", "bits"} and integer(row["i"]) and integer(row["j"]) and (row["i"], row["j"]) == (i, j), "PROFILE_PAIR_ORDER", "pair table order differs")
        require(type(row["bits"]) is list and all(integer(a) for a in row["bits"]) and row["bits"] in ([], [0], [1], [0, 1]), "PROFILE_PAIR_BITS", "literal allowed bits required")
        if counts[i] * counts[j] > 0 and (i != j or counts[i] >= 2):
            require(bool(row["bits"]), "PROFILE_INCOMPATIBLE_PAIR", "occupied distinct copies have no allowed adjacency")
        bits[i, j] = row["bits"]
    return n, k, h, masks, counts, bits


def reconstruct(value, budget=None):
    n, k, h, masks, counts, bits = profile(value, budget)
    m = len(h)
    labels = [[i, c] for i, count in enumerate(counts) for c in range(count)]
    pairs = [list(pair) for pair in itertools.combinations(range(len(labels)), 2)]
    incident = [[] for _ in labels]
    lower, upper = [], []
    for v, (x, y) in enumerate(pairs):
        if budget is not None:
            budget.tick()
        i, j = sorted((labels[x][0], labels[y][0]))
        allowed = bits[i, j]
        lower.append(int(allowed == [1]))
        upper.append(int(1 in allowed))
        incident[x].append((v, y))
        incident[y].append((v, x))
    rows = []
    for x, (i, _) in enumerate(labels):
        if budget is not None:
            budget.tick()
        rhs = k - masks[i].bit_count()
        rows.append(dict(kind="degree", copy_x=x, type_i=i, support_u=None, lower=rhs, upper=rhs, terms=[[v, 1] for v, _ in incident[x]]))
        for u in range(m):
            rhs = 2 - ((masks[i] >> u) & 1) - sum(h[u][w] * ((masks[i] >> w) & 1) for w in range(m))
            terms = [[v, 1] for v, y in incident[x] if (masks[labels[y][0]] >> u) & 1]
            rows.append(dict(kind="support_incidence", copy_x=x, type_i=i, support_u=u, lower=rhs, upper=rhs, terms=terms))
    return dict(schema="FIXED17_COPY_ADJACENCY_MODEL_V1", target_order=n, target_degree=k, support_order=m,
                ordered_masks=masks, counts=counts, copy_labels=labels, variable_pairs=pairs,
                variables=len(pairs), outside_copies=len(labels), lower=lower, upper=upper, rows=rows,
                no_equitable_profile_assumed=True, outside_pair_CN_equations_included=False)


def validate_model(value, submitted, budget=None):
    expected = reconstruct(value, budget)
    require(type(submitted) is dict and set(submitted) == set(expected), "MODEL_FIELDS", "model fields differ")
    require(submitted["schema"] == expected["schema"] and type(submitted["schema"]) is str, "MODEL_HEADER", "wrong model schema")
    require(all(integer(submitted[name]) and submitted[name] == expected[name] for name in ("target_order", "target_degree", "support_order", "variables", "outside_copies")), "MODEL_DIMENSIONS", "typed dimensions differ")
    require(submitted["no_equitable_profile_assumed"] is True and submitted["outside_pair_CN_equations_included"] is False, "MODEL_FLAGS", "scope flags differ")
    require(same(submitted["variable_pairs"], expected["variable_pairs"]), "MODEL_VARIABLE_PAIRS", "canonical x<y variables differ")
    require(type(submitted["lower"]) is list and type(submitted["upper"]) is list and len(submitted["lower"]) == expected["variables"] and len(submitted["upper"]) == expected["variables"] and all(integer(a) and integer(b) and 0 <= a <= b <= 1 for a, b in zip(submitted["lower"], submitted["upper"])), "MODEL_BOUNDS", "binary bound types or order differ")
    require(type(submitted["rows"]) is list and len(submitted["rows"]) == len(expected["rows"]), "MODEL_ROWS", "row population differs")
    for row in submitted["rows"]:
        if budget is not None:
            budget.tick()
        require(type(row) is dict and set(row) == set(expected["rows"][0]), "MODEL_ROW_DOMAIN", "row fields differ")
        require(type(row["kind"]) is str and row["kind"] in ("degree", "support_incidence") and integer(row["copy_x"]) and integer(row["type_i"]) and (row["support_u"] is None or integer(row["support_u"])) and integer(row["lower"]) and integer(row["upper"]) and row["lower"] == row["upper"], "MODEL_ROW_DOMAIN", "exact typed row domain differs")
        terms = row["terms"]
        require(type(terms) is list and all(type(term) is list and len(term) == 2 and integer(term[0]) and 0 <= term[0] < expected["variables"] and integer(term[1]) and term[1] == 1 for term in terms) and all(a[0] < b[0] for a, b in zip(terms, terms[1:])), "MODEL_ROW_DOMAIN", "typed sorted unit coefficients required")
    require(same(submitted, expected), "MODEL_RECONSTRUCTION", "full model does not equal reconstructed local rows")
    return expected


def scientific_scope(value, model, budget=None):
    n, k, h, masks, counts, _ = profile(value, budget)
    require((n, k, len(h), len(masks), sum(c > 0 for c in counts), model["outside_copies"], model["variables"], len(model["rows"])) == (99, 14, 17, 472, 68, 82, 3321, 1476) and sum(c * t.bit_count() for c, t in zip(counts, masks)) == 166, "SCIENTIFIC_SCOPE", "fixed17/472/82 local universe required")


def gate(value, model, refs):
    require(type(value) is dict and value.get("status") == COPY_STATUS and type(value.get("implementation_version")) is int and value["implementation_version"] == 1 and value.get("producer") == "/root/checkpoint_audit" and value.get("verifier") == "/root/native_driver" and value.get("method") == "independent_artifact_check" and value.get("target_resolution") == "NONE", "GATE_HEADER", "new applicable complete per-copy gate required")
    pins = value.get("inputs_sha256")
    require(type(pins) is dict and all(type(p) is str and type(s) is str and len(s) == 64 and all(c in "0123456789abcdef" for c in s) for p, s in pins.items()) and all(pins.get(ref["path"]) == ref["sha256"] for ref in refs), "GATE_PINS", "gate must bind same profile and model bytes")
    outcome = value.get("outcome")
    scope = dict(complete_input_type_count=len(model["ordered_masks"]), positive_types=sum(c > 0 for c in model["counts"]), outside_copies=model["outside_copies"], binary_edge_variables=model["variables"], complete_degree_rows=model["outside_copies"], complete_support_incidence_rows=model["outside_copies"] * model["support_order"], complete_equations=len(model["rows"]), no_equitable_profile_assumed=True, outside_pair_CN_model_equations_included=False, count_witness_excluded=False, numeric_status_is_proof=False)
    require(type(outcome) is dict and all(name in outcome and same(outcome[name], expected) for name, expected in scope.items()), "GATE_SCOPE", "complete local model scope differs")


def group_order(model):
    m, c = model["support_order"], model["outside_copies"]
    return [x * (m + 1) for x in range(c)] + [x * (m + 1) + u + 1 for x in range(c) for u in range(m)]


def encode_row(encoder, clauses, row, lower, upper, ordinal, original_index):
    variables = [term[0] for term in row["terms"]]
    true_ids = [v + 1 for v in variables if lower[v] == upper[v] == 1]
    false_ids = [v + 1 for v in variables if lower[v] == upper[v] == 0]
    free_ids = [v + 1 for v in variables if lower[v] != upper[v]]
    residual = row["lower"] - len(true_ids)
    annotation = dict(group_ordinal=ordinal, original_model_row=original_index, original_row=copy.deepcopy(row), fixed_true_inputs=true_ids, fixed_false_inputs=false_ids, residual=residual)
    if not 0 <= residual <= len(free_ids):
        first = clauses.count + 1
        clauses.emit()
        return dict(annotation, inputs=free_ids, bound=residual, equality=True, states=[], first_auxiliary_variable=None, last_auxiliary_variable=None, auxiliary_null_reason="IMPOSSIBLE_RESIDUAL", first_clause=first, clause_count=1)
    return encoder.counter(free_ids, residual, True, annotation)


def initial_units(model, clauses):
    variable_map = []
    for v, (pair, lo, hi) in enumerate(zip(model["variable_pairs"], model["lower"], model["upper"])):
        first = clauses.count + 1
        if lo == hi:
            clauses.emit(v + 1 if lo else -(v + 1))
        variable_map.append(dict(variable_index=v, sat_id=v + 1, copy_pair=pair, lower=lo, upper=hi, first_clause=first, clause_count=clauses.count - first + 1))
    return variable_map


def memory_encoding(model, helpers, budget):
    clauses = helpers["Clauses"](cap=budget)
    encoder = helpers["Encoder"](model["variables"], clauses)
    variable_map = initial_units(model, clauses)
    records = [encode_row(encoder, clauses, model["rows"][index], model["lower"], model["upper"], ordinal, index) for ordinal, index in enumerate(group_order(model))]
    return clauses, encoder, variable_map, records


def satisfies(rows, assignment):
    return all(any(assignment[abs(lit)] == (lit > 0) for lit in row) for row in rows)


def extensions(rows, top, base, budget):
    answers = []
    for bits in itertools.product((False, True), repeat=top - len(base)):
        budget.tick()
        assignment = dict(base, **{})
        assignment.update({len(base) + i + 1: bit for i, bit in enumerate(bits)})
        if satisfies(rows, assignment):
            answers.append(bits)
    return answers


def recurrence_tables(helpers, budget):
    observations = []
    for a_kind, c_kind in itertools.product((False, True, "input"), repeat=2):
        clauses = helpers["Clauses"](cap=budget)
        encoder = helpers["Encoder"](3, clauses)
        a = 1 if a_kind == "input" else a_kind
        c = 3 if c_kind == "input" else c_kind
        result = encoder.recurrence(a, 2, c)
        for bits in itertools.product((False, True), repeat=3):
            base = {i + 1: bit for i, bit in enumerate(bits)}
            lifted = extensions(clauses.rows, encoder.top, base, budget)
            expected = (bits[0] if a_kind == "input" else a_kind) or (bits[1] and (bits[2] if c_kind == "input" else c_kind))
            require(len(lifted) == 1, "RECURRENCE_TRUTH", "recurrence extension is not unique")
            full = dict(base)
            full.update({4 + i: bit for i, bit in enumerate(lifted[0])})
            observed = result if type(result) is bool else full[result]
            require(observed == expected, "RECURRENCE_TRUTH", "recurrence value differs")
            observations.append(dict(a=a_kind, c=c_kind, base=list(bits), result_ref=result, expected=expected, auxiliary=list(lifted[0]), clauses=clauses.rows))
    require(len(observations) == 72, "RECURRENCE_TRUTH", "complete 9 times 8 table required")
    return observations


def counter_tables(helpers, budget):
    observations = []
    for n in range(4):
        for bound in range(n + 1):
            clauses = helpers["Clauses"](cap=budget)
            encoder = helpers["Encoder"](n, clauses)
            record = encoder.counter(list(range(1, n + 1)), bound, True, {"n": n})
            for bits in itertools.product((False, True), repeat=n):
                base = {i + 1: bit for i, bit in enumerate(bits)}
                lifted = extensions(clauses.rows, encoder.top, base, budget)
                require(len(lifted) == int(sum(bits) == bound), "COUNTER_TRUTH", "counter has wrong extension count")
                observations.append(dict(n=n, bound=bound, base=list(bits), expected=sum(bits) == bound, satisfying_auxiliaries=[list(x) for x in lifted], record=record, clauses=clauses.rows))
    require(len(observations) == 49, "COUNTER_TRUTH", "complete n0 through n3 table required")
    return observations


def residual_tables(helpers, budget):
    cases = [([], [], 0), ([], [], -1), ([], [], 1), ([1, 0], [1, 0], 1), ([1, 0], [1, 0], 0), ([1, 0], [1, 0], 2), ([1, 0, 0], [1, 1, 1], 2), ([0, 0], [1, 1], 1)]
    observations = []
    for index, (lo, hi, rhs) in enumerate(cases):
        n = len(lo)
        clauses = helpers["Clauses"](cap=budget)
        encoder = helpers["Encoder"](n, clauses)
        for v in range(n):
            if lo[v] == hi[v]:
                clauses.emit(v + 1 if lo[v] else -(v + 1))
        row = dict(kind="degree", copy_x=0, type_i=0, support_u=None, lower=rhs, upper=rhs, terms=[[v, 1] for v in range(n)])
        record = encode_row(encoder, clauses, row, lo, hi, index, index)
        for bits in itertools.product((False, True), repeat=n):
            lifted = extensions(clauses.rows, encoder.top, {i + 1: bit for i, bit in enumerate(bits)}, budget)
            expected = all(lo[v] <= int(bits[v]) <= hi[v] for v in range(n)) and sum(bits) == rhs
            require(len(lifted) == int(expected), "RESIDUAL_TRUTH", "residual reduction differs from original row")
            observations.append(dict(case=index, lower=lo, upper=hi, rhs=rhs, base=list(bits), expected=expected, satisfying_auxiliaries=[list(x) for x in lifted], record=record, clauses=clauses.rows))
    return observations


def rook_fixture(*, switched=False, forced=False):
    value = dict(target_order=9, target_degree=4, support_adjacency=[[0, 1], [1, 0]], ordered_masks=[0, 1, 2, 3], counts=[2, 2, 2, 1], pair_bits=[dict(i=i, j=j, bits=[0, 1]) for i, j in itertools.combinations_with_replacement(range(4), 2)])
    if forced:
        only_one = {(0, 0), (1, 1), (2, 2), (0, 3)}
        only_zero = {(1, 3), (2, 3), (3, 3)}
        for row in value["pair_bits"]:
            pair = (row["i"], row["j"])
            row["bits"] = [1] if pair in only_one else [0] if pair in only_zero else [0, 1]
    edges = {(0, 1), (0, 2), (0, 4), (0, 6), (1, 3), (1, 5), (1, 6), (2, 3), (2, 4), (3, 5), (4, 5)}
    if switched:
        edges -= {(2, 4), (3, 5)}
        edges |= {(2, 5), (3, 4)}
    model = reconstruct(value)
    assignment = [int(tuple(pair) in edges) for pair in model["variable_pairs"]]
    return value, model, assignment


def rook_check(value, model, edge_assignment, helpers, budget, *, switched):
    validate_model(value, model, budget)
    require(all(model["lower"][v] <= a <= model["upper"][v] for v, a in enumerate(edge_assignment)) and all(sum(edge_assignment[v] for v, _ in row["terms"]) == row["lower"] for row in model["rows"]), "ROOK_LOCAL", "known local witness differs")
    clauses, encoder, variable_map, records = memory_encoding(model, helpers, budget)
    sat = {v + 1: bool(a) for v, a in enumerate(edge_assignment)}
    for record in records:
        for i, j, ref in record["states"]:
            truth = sum(sat[v] for v in record["inputs"][:i]) >= j
            if type(ref) is bool:
                require(ref == truth, "ROOK_EXTENSION", "folded constant differs")
            elif ref in sat:
                require(sat[ref] == truth, "ROOK_EXTENSION", "shared state differs")
            else:
                sat[ref] = truth
    require(set(sat) == set(range(1, encoder.top + 1)) and satisfies(clauses.rows, sat), "ROOK_EXTENSION", "complete deterministic extension fails")
    n, _, h, masks, _, _ = profile(value)
    m = len(h)
    adjacency = [[0] * n for _ in range(n)]
    for u in range(m):
        for v in range(m):
            adjacency[u][v] = h[u][v]
    for x, (i, _) in enumerate(model["copy_labels"]):
        for u in range(m):
            adjacency[u][m + x] = adjacency[m + x][u] = (masks[i] >> u) & 1
    for (x, y), a in zip(model["variable_pairs"], edge_assignment):
        adjacency[m + x][m + y] = adjacency[m + y][m + x] = a
    cn = [[sum(adjacency[u][w] * adjacency[w][v] for w in range(n)) for v in range(n)] for u in range(n)]
    first = next((dict(u=u, v=v, observed=cn[u][v], expected=4 if u == v else 1 if adjacency[u][v] else 2) for u in range(n) for v in range(n) if cn[u][v] != (4 if u == v else 1 if adjacency[u][v] else 2)), None)
    require(first == dict(u=2, v=4, observed=0, expected=1) if switched else first is None, "ROOK_GRAPH_BOUNDARY", "local/full graph boundary differs")
    return dict(profile=value, model=model, edge_assignment=edge_assignment, sat_assignment=[[v, int(sat[v])] for v in sorted(sat)], variable_map=variable_map, groups=records, clauses=clauses.rows, adjacency=adjacency, ordered_common_neighbors=cn, first_full_graph_failure=first, local_encoding_pass=True, full_graph_pass=first is None)


def synthetic_gate(model, refs):
    return dict(status=COPY_STATUS, implementation_version=1, producer="/root/checkpoint_audit", verifier="/root/native_driver", method="independent_artifact_check", target_resolution="NONE", inputs_sha256={ref["path"]: ref["sha256"] for ref in refs}, outcome=dict(complete_input_type_count=len(model["ordered_masks"]), positive_types=sum(c > 0 for c in model["counts"]), outside_copies=model["outside_copies"], binary_edge_variables=model["variables"], complete_degree_rows=model["outside_copies"], complete_support_incidence_rows=model["outside_copies"] * model["support_order"], complete_equations=len(model["rows"]), no_equitable_profile_assumed=True, outside_pair_CN_model_equations_included=False, count_witness_excluded=False, numeric_status_is_proof=False))


def calibrate(out, helpers, budget):
    results = []

    def case(name, expected, payload, action):
        budget.tick()
        actual, result, error = "PASS", None, None
        try:
            result = action()
        except GuardError as exc:
            actual, error = exc.stage, str(exc)
        except SaveStop:
            raise
        except Exception as exc:
            actual, error = "UNEXPECTED_EXCEPTION", repr(exc)
        row = dict(index=len(results), name=name, expected_stage=expected, actual_stage=actual, matched=actual == expected)
        save(out / f"case_{len(results):02d}.json", dict(row, payload=payload, result=result, error=error), budget)
        results.append(row)

    case("recurrence_complete_truth_table", "PASS", dict(base_bits=3, a_c_choices=9), lambda: recurrence_tables(helpers, budget))
    case("counter_complete_truth_tables", "PASS", dict(n_range=[0, 3], all_bounds=True), lambda: counter_tables(helpers, budget))
    case("residual_complete_truth_tables", "PASS", dict(hand_cases=8), lambda: residual_tables(helpers, budget))
    for name, switched, forced in (("rook_local_witness", False, False), ("switched_rook_local_only", True, False), ("forced_rook_bounds", False, True)):
        p, m, a = rook_fixture(switched=switched, forced=forced)
        case(name, "PASS", dict(profile=p, model=m, edges=a), lambda p=p, m=m, a=a, switched=switched: rook_check(p, m, a, helpers, budget, switched=switched))
    p, m, _ = rook_fixture()
    refs = [dict(path="synthetic/profile.json", sha256="1" * 64), dict(path="synthetic/model.json", sha256="2" * 64)]
    g = synthetic_gate(m, refs)
    case("input_gate_header_and_scope", "PASS", g, lambda: gate(g, m, refs))

    def profile_case(name, stage, edit):
        damaged = copy.deepcopy(p)
        edit(damaged)
        case(name, stage, damaged, lambda: profile(damaged, budget))

    profile_case("target_bool", "PROFILE_TARGET", lambda x: x.__setitem__("target_order", True))
    profile_case("degree_float", "PROFILE_TARGET", lambda x: x.__setitem__("target_degree", 4.0))
    profile_case("graph_asymmetric", "PROFILE_GRAPH", lambda x: x["support_adjacency"][0].__setitem__(1, 0))
    profile_case("mask_bool", "PROFILE_MASKS", lambda x: x["ordered_masks"].__setitem__(0, False))
    profile_case("count_bool", "PROFILE_COUNTS", lambda x: x["counts"].__setitem__(0, True))
    profile_case("pair_bit_bool", "PROFILE_PAIR_BITS", lambda x: x["pair_bits"][0].__setitem__("bits", [False, 1]))
    profile_case("pair_order", "PROFILE_PAIR_ORDER", lambda x: x["pair_bits"][0].__setitem__("j", 1))
    profile_case("occupied_empty_pair", "PROFILE_INCOMPATIBLE_PAIR", lambda x: x["pair_bits"][0].__setitem__("bits", []))

    def model_case(name, stage, edit):
        damaged = copy.deepcopy(m)
        edit(damaged)
        case(name, stage, damaged, lambda: validate_model(p, damaged, budget))

    model_case("variable_pair_changed", "MODEL_VARIABLE_PAIRS", lambda x: x["variable_pairs"][0].__setitem__(1, 2))
    model_case("row_missing", "MODEL_ROWS", lambda x: x["rows"].pop())
    model_case("rhs_changed", "MODEL_RECONSTRUCTION", lambda x: (x["rows"][0].__setitem__("lower", 3), x["rows"][0].__setitem__("upper", 3)))
    model_case("coefficient_bool", "MODEL_ROW_DOMAIN", lambda x: x["rows"][0]["terms"][0].__setitem__(1, True))
    model_case("bound_bool", "MODEL_BOUNDS", lambda x: x["lower"].__setitem__(0, False))
    model_case("term_duplicate", "MODEL_ROW_DOMAIN", lambda x: x["rows"][0]["terms"].__setitem__(1, list(x["rows"][0]["terms"][0])))
    model_case("diagonal_variable", "MODEL_VARIABLE_PAIRS", lambda x: x["variable_pairs"][0].__setitem__(1, 0))
    model_case("scope_flag_changed", "MODEL_FLAGS", lambda x: x.__setitem__("no_equitable_profile_assumed", False))
    for name, stage, edit in (("gate_implementation_bool", "GATE_HEADER", lambda x: x.__setitem__("implementation_version", True)), ("gate_pin_changed", "GATE_PINS", lambda x: x["inputs_sha256"].__setitem__(refs[0]["path"], "3" * 64)), ("gate_equations_bool", "GATE_SCOPE", lambda x: x["outcome"].__setitem__("complete_equations", True))):
        damaged = copy.deepcopy(g)
        edit(damaged)
        case(name, stage, damaged, lambda damaged=damaged: gate(damaged, m, refs))
    for name, stage, raw in (("json_duplicate", "JSON_DUPLICATE", b'{"x":1,"x":2}'), ("json_nonfinite", "JSON_NONFINITE", b'{"x":NaN}')):
        case(name, stage, dict(raw_utf8=raw.decode("ascii")), lambda raw=raw: decode(raw))
    case("tiny_fixture_is_not_science", "SCIENTIFIC_SCOPE", dict(profile=p, model=m), lambda: scientific_scope(p, m, budget))
    require(len(results) == 29 and sum(x["expected_stage"] == "PASS" for x in results) == 7, "CONTROL_POPULATION", "7 positive/22 negative controls required")
    save(out / "controls.json", results, budget)
    require(all(row["matched"] for row in results), "CONTROL_STAGE", "one or more expected stages differ; preserve all case bytes")
    return dict(positive_controls=7, negative_controls=22, total_controls=29, recurrence_observations=72, counter_observations=49, residual_hand_cases=8, full_rook_common_neighbor_entries=243, synthetic_gate_controls=True, actual_per_copy_gate_read=False, actual_profile_read=False, actual_model_read=False, solver_calls=0, inherited_helper_definitions_only=True, truth_table_controls_are_complete=True)


class BodySink:
    def __init__(self, stream, budget):
        self.stream, self.budget, self.bytes = stream, budget, 0
        self.digest = hashlib.sha256()

    def write(self, data):
        self.budget.tick()
        require(type(data) is bytes, "BODY_DOMAIN", "immutable helper emits bytes")
        require(self.bytes + len(data) <= MAX_BODY_BYTES, "BODY_SIZE", "encoding body exceeds declared byte cap")
        self.stream.write(data)
        self.digest.update(data)
        self.bytes += len(data)


def build(config, out, helpers, budget, inputs):
    fields = {"schema", "source", "specification", "input_profile", "copy_model", "per_copy_gate", "root_acceptance", "author_calibration", "independent_encoding_controls", "root_authority", "scope"}
    require(type(config) is dict and set(config) == fields and config["schema"] == "FIXED17_PER_COPY_LOCAL_SAT_CONFIGURATION_V1", "CONFIGURATION", "exact configuration required")
    require(config["scope"] == "FIXED17_82_COPY_LOCAL_ROWS_ONLY" and type(config["scope"]) is str, "CONFIGURATION_SCOPE", "local equations only")
    require(all(type(config[name]) is dict and set(config[name]) == {"path", "sha256"} for name in fields - {"schema", "scope"}), "CONFIGURATION_REFERENCES", "all prerequisite references must be actual path/hash objects")
    require(config["source"]["path"] == SELF and config["specification"]["path"] == SPEC and config["source"]["sha256"] == inputs[SELF] and config["specification"]["sha256"] == inputs[SPEC], "CONFIGURATION_SOURCE", "current caller/spec identity required")
    p = read_ref(config["input_profile"], budget, inputs)
    submitted = read_ref(config["copy_model"], budget, inputs)
    model = validate_model(p, submitted, budget)
    scientific_scope(p, model, budget)
    gate(read_ref(config["per_copy_gate"], budget, inputs), model, [config["input_profile"], config["copy_model"]])
    author = read_ref(config["author_calibration"], budget, inputs)
    require(type(author) is dict and author.get("status") == AUTHOR_STATUS and author.get("implementation_version") == 1 and type(author.get("implementation_version")) is int and author.get("source_sha256") == inputs[SELF] and author.get("specification_sha256") == inputs[SPEC] and all(same(author.get("outcome", {}).get(name), count) for name, count in (("positive_controls", 7), ("negative_controls", 22), ("total_controls", 29))), "AUTHOR_GATE", "current finite author gate required")
    controls = read_ref(config["independent_encoding_controls"], budget, inputs)
    require(type(controls) is dict and controls.get("status") == ENCODING_CONTROL_STATUS and type(controls.get("implementation_version")) is int and controls["implementation_version"] == 1 and controls.get("producer") == "/root/structural" and controls.get("verifier") == "/root/native_driver" and controls.get("method") == "independent_artifact_check" and controls.get("target_resolution") == "NONE" and controls.get("inputs_sha256", {}).get(SELF) == inputs[SELF] and controls.get("inputs_sha256", {}).get(SPEC) == inputs[SPEC], "ENCODING_GATE", "different-author current encoding controls required")
    read_ref(config["root_acceptance"], budget, inputs)
    read_ref(config["root_authority"], budget, inputs)
    save(out / "parsed_profile.json", p, budget)
    order = group_order(model)
    from tqdm import tqdm

    checkpoint_count = 0
    journal_hash = hashlib.sha256()
    journal_bytes = 0
    body_path, journal_path = out / "clauses.body", out / "groups.jsonl"
    with body_path.open("xb") as body, journal_path.open("xb") as journal:
        sink = BodySink(body, budget)
        clauses = helpers["Clauses"](stream=sink, cap=budget)
        encoder = helpers["Encoder"](model["variables"], clauses)
        variable_map = initial_units(model, clauses)
        for ordinal, index in enumerate(tqdm(order, total=1476, desc="local row groups", unit="group"), 0):
            budget.tick()
            record = encode_row(encoder, clauses, model["rows"][index], model["lower"], model["upper"], ordinal, index)
            line = (json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
            journal.write(line)
            journal_hash.update(line)
            journal_bytes += len(line)
            completed = ordinal + 1
            if completed % 100 == 0 or completed == len(order):
                for stream in (body, journal):
                    stream.flush()
                    os.fsync(stream.fileno())
                save(out / f"checkpoint_{completed:04d}.json", dict(schema="FIXED17_PER_COPY_LOCAL_SAT_CHECKPOINT_V1", completed_groups=completed, total_groups=len(order), clauses=clauses.count, variables=encoder.top, body_bytes=sink.bytes, body_prefix_sha256=sink.digest.hexdigest(), group_journal_bytes=journal_bytes, group_journal_prefix_sha256=journal_hash.hexdigest()), budget)
                checkpoint_count += 1
        for stream in (body, journal):
            stream.flush()
            os.fsync(stream.fileno())
        budget.tick()
    require(checkpoint_count == 15, "CHECKPOINT_POPULATION", "all 100-group boundaries plus final required")
    cnf_path = out / "local.cnf"
    with cnf_path.open("xb") as cnf, body_path.open("rb") as body:
        cnf.write(f"p cnf {encoder.top} {clauses.count}\n".encode("ascii"))
        while chunk := body.read(1024 * 1024):
            budget.tick()
            cnf.write(chunk)
        cnf.flush()
        os.fsync(cnf.fileno())
    budget.tick()
    save(out / "encoding_model.json", dict(schema="FIXED17_PER_COPY_LOCAL_SAT_ENCODING_MODEL_V1", source_model=model, variable_map=variable_map, group_order_model_rows=order, groups_file="groups.jsonl", clauses_file="clauses.body", dimacs_file="local.cnf", total_groups=1476, degree_groups=82, support_groups=1394, base_variables=3321, variables=encoder.top, clauses=clauses.count, fixed_units=sum(lo == hi for lo, hi in zip(model["lower"], model["upper"])), impossible_rows_possible_and_retained=True, outside_pair_CN_equations_included=False, no_equitable_profile_assumed=True), budget)
    return dict(base_variables=3321, variables=encoder.top, clauses=clauses.count, total_groups=1476, degree_groups=82, support_groups=1394, checkpoints=15, fixed_units=sum(lo == hi for lo, hi in zip(model["lower"], model["upper"])), solver_calls=0, independent_encoding_complete_check_performed=False, graph_object_approved=False, count_witness_excluded=False, target_resolution="NONE", prerequisite_complete_model_scope_inherited=True, prerequisite_bulk_closure_rehashed=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("calibrate", "build"))
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--self-sha256", required=True)
    parser.add_argument("--spec-sha256", required=True)
    parser.add_argument("--configuration")
    parser.add_argument("--configuration-sha256")
    args = parser.parse_args()
    budget = Budget(args.seconds)
    requested_out = Path(args.out).absolute()
    require(requested_out.is_relative_to(ROOT / "acceleration" / "results"), "OUTPUT_PATH", "confined output root required")
    out = path_for(requested_out.relative_to(ROOT).as_posix())
    require(not out.exists(), "OUTPUT_PATH", "fresh confined output root required")
    out.mkdir(parents=True)
    inputs = {}
    try:
        inputs.update(software(args.self_sha256, args.spec_sha256, budget))
        helpers = helper(budget)
        if args.mode == "calibrate":
            require(args.configuration is None and args.configuration_sha256 is None, "CALIBRATION_SCOPE", "author controls never read actual model/config")
            outcome = calibrate(out, helpers, budget)
            status = AUTHOR_STATUS
        else:
            require(args.configuration is not None and args.configuration_sha256 is not None, "CONFIGURATION", "future actual configuration required")
            config_path = Path(args.configuration).absolute()
            require(config_path.is_relative_to(ROOT), "PATH", "configuration outside workspace")
            config_path = path_for(config_path.relative_to(ROOT).as_posix())
            config = read_ref(dict(path=config_path.relative_to(ROOT).as_posix(), sha256=args.configuration_sha256), budget, inputs)
            outcome = build(config, out, helpers, budget, inputs)
            status = BUILD_STATUS
        for name, expected in inputs.items():
            require(hash_path(path_for(name), budget) == expected, "CLOSING_HASH", "closing source or direct input changed")
        outputs = {path.relative_to(ROOT).as_posix(): hash_path(path, budget) for path in sorted(out.iterdir()) if path.is_file()}
        expected_outputs = 30 if args.mode == "calibrate" else 20
        require(len(outputs) == expected_outputs, "OUTPUT_POPULATION", "complete successful output population differs")
        save(out / "summary.json", dict(status=status, implementation_version=1, producer="/root/structural", source_author="/root/structural", timestamp=datetime.now(timezone.utc).isoformat(), mode=args.mode, source_sha256=args.self_sha256, specification_sha256=args.spec_sha256, inputs_sha256=inputs, outputs_sha256=outputs, outcome=outcome, elapsed_seconds=budget.deadline.status()["elapsed_seconds"], target_resolution="NONE", limitations=["Source qualification and complete encoding require separate applicable independent checks; no old gate transfers.", "No solver, SAT witness, UNSAT proof, outside-pair common-neighbor equations or full graph verification performed.", "Previously flushed checkpoint prefixes persist; unexpected exception or hard kill does not guarantee pending suffix durability.", "Success summary is provisional until clean supported containment and closing guards are accepted."]), budget)
        budget.tick()
        return 0
    except BaseException as exc:
        try:
            if not (out / "failure.json").exists():
                save(out / "failure.json", dict(status="FAILED_OR_NOT_COMPLETED", stage=getattr(exc, "stage", None), error=repr(exc), unmet=["clean successful complete output and applicable independent encoding approval"], inputs_sha256=inputs, elapsed_seconds=budget.deadline.status()["elapsed_seconds"], target_resolution="NONE", automatic_retry=False), budget, emergency=True)
        except BaseException:
            pass
        raise


if __name__ == "__main__":
    sys.exit(main())

"""SOURCE_ONLY V2 triple/slack verifier; exact actual tiny-fixture route, no LP/RREF imports."""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import sys

import audit_20261003_filtered_external_moment_certificate_v3 as shared
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + "_spec.md")
PRODUCER = "acceleration/solve_20261003_external_moment_triple_lp_v1.py"
PRODUCER_SPEC = "acceleration/solve_20261003_external_moment_triple_lp_v1_spec.md"
CORE = "acceleration/audit_20261003_filtered_external_moment_certificate_v3.py"
CORE_SPEC = "acceleration/audit_20261003_filtered_external_moment_certificate_v3_spec.md"
PINS = {PRODUCER: "34438fbdadf39446f207822c423f8087a3ddf70b7ae61919b2e97f1ae8db17c2",
        PRODUCER_SPEC: "9a8a769ce9bd7f83551580ef338dc23542b394406f269851351c5ba967389070",
        CORE: "53508ec10024f8febafdb9962878fa14fe50341525d70c2bade0d2beed750db2",
        CORE_SPEC: "c2fc79169a02243b5b28d991c93bb10eb92f8a939f4f844d815d67ad12c75d87",
        **{k: v for k, v in shared.PINS.items() if k not in (shared.PRODUCER, shared.PRODUCER_SPEC)}}
MODEL, TYPES, FIXED = shared.MODEL, shared.TYPES, shared.FIXED
PRIOR = "acceleration/results/20261003_external_moment_filtered_lp02/filtered_primal.json"
PRIOR_SHA = "772b5f1534de5bf37da578b2b7345db95795f80559fc7507d3a709be719b5f9d"
LEMMA = "docs/CANDIDATE_20261003_EXTERNAL_TYPE_PAIR_AND_TRIPLE_CAPS_V1.md"
LEMMA_SHA = "f7aefb0628c9da0741f0c8f43b444a30e5d5042eb60c1db23735f024286125a4"
PROOF = "acceleration/audit_20261003_external_type_pair_triple_caps_native_v1.md"
PROOF_SHA = "d8f659709d4323e6b534e0cf0b3690c3cdf5096f81f8b593f7e21765c3f8446c"
CAL_STATUS = "INDEPENDENT_TRIPLE_CAPPED_EXTERNAL_MOMENT_CERTIFICATE_V1_CALIBRATION_PASS"
FULL_STATUS = "INDEPENDENT_TRIPLE_CAPPED_EXTERNAL_MOMENT_CERTIFICATE_V1_COMPLETE_PASS"
# These two actual producer fixtures are data pins, not software or scientific certificates.
AUTHOR_LP_FIXTURES = {
    "primal": ("acceleration/results/20261003_external_moment_triple_lp01/control_lp_primal_primal.json",
               "d124396c6dd837079c671a65277e0da53a4289acdff122f1ff01b6cfc331e502"),
    "farkas": ("acceleration/results/20261003_external_moment_triple_lp01/control_lp_dual_farkas.json",
               "cf0151e627cf6c1b563bac8abfcc1b384ffbeae5bec0bd21f08203dbd5e8ca21")}
need, same = shared.require, shared.equal


def caps(masks, m=17, guard=lambda: None):
    need(type(m) is int and 3 <= m <= 17, "CAP_DOMAIN")
    need(type(masks) is list and masks and all(type(v) is int and 0 <= v < 2**m for v in masks), "CAP_MASK_TYPE")
    need(masks == sorted(set(masks)), "CAP_MASK_ORDER")
    sets = [{i for i in range(m) if mask >> i & 1} for mask in masks]
    triples, rows = [], []
    for a in range(m - 2):
        for b in range(a + 1, m - 1):
            for c in range(b + 1, m):
                guard(); points = {a, b, c}
                triples.append([a, b, c]); rows.append([int(points <= s) for s in sets])
    return triples, rows


def standard(original, rhs, masks, m=17, guard=lambda: None):
    shared.integer_system(original, rhs)
    need(len(original[0]) == len(masks), "BASE_WIDTH")
    triples, cuts = caps(masks, m, guard)
    n, k = len(masks), len(triples)
    matrix = []
    for row in original:
        guard(); matrix.append(row[:] + [0] * k)
    for i, row in enumerate(cuts):
        guard(); slack = [0] * k; slack[i] = 1; matrix.append(row[:] + slack)
    return matrix, rhs[:] + [1] * k, triples, cuts


def standard_payload(original, rhs, masks, m=17, guard=lambda: None):
    matrix, rhs_full, triples, cuts = standard(original, rhs, masks, m, guard)
    return dict(schema="TRIPLE_CAPPED_EXTERNAL_MOMENT_SYSTEM_V1", original_model_path=MODEL,
        original_model_sha256=FIXED[MODEL], types_path=TYPES, types_sha256=FIXED[TYPES],
        original_variables=len(masks), original_equations=len(original), support_vertices=list(range(m)),
        ordered_masks=masks, ordered_triples=triples, triple_coefficients=cuts, slack_variables=len(cuts),
        coefficient_matrix=matrix, right_hand_side=rhs_full, rows=len(matrix), variables=len(matrix[0]),
        original154_literal_unchanged=True, new_inequality_rhs=1,
        standard_form="[M 0; C I] [n;s] = [b;ones], n,s>=0")


def model_payload(raw, original, rhs, masks, m=17, guard=lambda: None):
    expected = standard_payload(original, rhs, masks, m, guard)
    shared.fields(raw, list(expected), "STANDARD_FIELDS")
    for name in ["original_variables", "original_equations", "slack_variables", "rows", "variables", "new_inequality_rhs"]:
        need(type(raw[name]) is int, "STANDARD_INTEGER")
    need(same(raw, expected), "STANDARD_IDENTITY")
    return expected["coefficient_matrix"], expected["right_hand_side"], expected["triple_coefficients"]


def certificate(kind, raw, a, b, guard=lambda: None):
    need(type(raw) is dict, "CERTIFICATE_OBJECT")
    need(kind in ("primal", "farkas"), "CERTIFICATE_KIND")
    expected = "TRIPLE_CAPPED_EXTERNAL_MOMENT_EXACT_" + ("PRIMAL" if kind == "primal" else "FARKAS") + "_V1"
    need(raw.get("schema") == expected, "TRIPLE_CERTIFICATE_SCHEMA")
    translated = raw.copy()
    translated["schema"] = "FILTERED_EXTERNAL_MOMENT_EXACT_" + ("PRIMAL" if kind == "primal" else "FARKAS") + "_V1"
    return shared.certificate(kind, translated, a, b, guard)


def author_lp_fixture(kind, raw, guard=lambda: None):
    """Exact tiny author fixture only; scientific certificates retain their separate full-size route."""
    need(kind in ("primal", "farkas"), "AUTHOR_LP_FIXTURE_KIND")
    a, b = ([[1, 0], [0, 1]], [1, 1]) if kind == "primal" else ([[1]], [-1])
    # certificate() requires the triple header before translating a copy for shared exact arithmetic.
    return certificate(kind, raw, a, b, guard)

def primal(values):
    result = shared.primal(values); result["schema"] = "TRIPLE_CAPPED_EXTERNAL_MOMENT_EXACT_PRIMAL_V1"; return result


def dual(values, dot):
    result = shared.dual(values, dot); result["schema"] = "TRIPLE_CAPPED_EXTERNAL_MOMENT_EXACT_FARKAS_V1"; return result


def lemma_header(raw):
    need(type(raw) is dict and raw.get("status") == "INDEPENDENT_EXTERNAL_TYPE_PAIR_AND_TRIPLE_CAPS_WRITTEN_PASS"
        and raw.get("claim_id") == "C-EXTERIOR-TYPE-PAIR-AND-TRIPLE-COMMON-NEIGHBOR-CAPS"
        and type(raw.get("claim_revision")) is int and raw["claim_revision"] == 1
        and raw.get("producer") == "/root/checkpoint_audit" and raw.get("verifier") == "/root/native_driver"
        and raw.get("method") == "independent_derivation" and raw.get("outcome") == "PASS"
        and raw.get("target_resolution") == "NONE", "LEMMA_HEADER")
    closure = raw.get("inputs_sha256")
    need(type(closure) is dict and closure.get(LEMMA) == LEMMA_SHA and closure.get(PROOF) == PROOF_SHA, "LEMMA_DIRECT_PINS")
    return closure


def prior_header(raw):
    need(type(raw) is dict and raw.get("status") == shared.FULL_STATUS and raw.get("producer") == "/root/checkpoint_audit"
        and raw.get("verifier") == "/root/structural" and raw.get("method") == "independent_artifact_check"
        and raw.get("target_resolution") == "NONE" and type(raw.get("implementation_version")) is int
        and raw["implementation_version"] == 3, "PRIOR_HEADER")
    closure = raw.get("inputs_sha256")
    need(type(closure) is dict and closure.get(PRIOR) == PRIOR_SHA
         and closure.get(CORE) == PINS[CORE] and closure.get(CORE_SPEC) == PINS[CORE_SPEC], "PRIOR_DIRECT_PINS")
    return closure


def prior_diagnostic(raw, original, rhs, cuts, guard=lambda: None):
    checked = shared.certificate("primal", raw, original, rhs, guard)
    x = shared.vector(raw["values"], len(original[0])); rows = []
    for i, row in enumerate(cuts):
        guard(); lhs = sum((x[j] for j, v in enumerate(row) if v), Fraction(0))
        rows.append(dict(triple_row=i, lhs=str(lhs), upper="1", violated=lhs > 1))
    need(checked["rows"] == len(original), "PRIOR_EQUATIONS")
    return dict(rows=rows, row_count=len(rows), violated_count=sum(r["violated"] for r in rows),
                maximum_lhs=str(max(Fraction(r["lhs"]) for r in rows)),
                original_rows_rechecked_exact=True, new_model_feasibility_inferred=False)


def runtime(plan, manifest, terminal, subject):
    need(type(plan) is dict and plan.get("source") == PRODUCER and plan.get("source_sha256") == PINS[PRODUCER]
         and plan.get("spec_sha256") == PINS[PRODUCER_SPEC], "PLAN_SOURCE")
    science = plan.get("solve"); need(type(science) is dict, "PLAN_SOLVE")
    command = shared.path_words(science.get("command")); child = command[command.index("--") + 1:]
    need(len(command) == 44 and command.index("--") == 15 and len(child) == 28
         and same(shared.path_words(science.get("child_argv")), child), "PLAN_WORDS")
    py = ROOT / "build/research-venv/Scripts/python.exe"
    need(same(shared.path_words(science.get("supervisor_argv")), command), "PLAN_SUPERVISOR")
    worker = shared.path_words(science.get("worker_argv"))
    need(len(worker) == 24 and Path(worker[0]).resolve() == py.resolve() and worker[1] == "-B"
         and same(worker[2:], child[6:]), "PLAN_WORKER")
    need(Path(command[0]).resolve() == py.resolve() and command[1] == "-B"
         and Path(command[2]).resolve() == (ROOT / "acceleration/run_compute_command.py").resolve()
         and command[3:7] == ["--seconds", "900", "--shutdown-reserve-seconds", "20"]
         and command[7] == "--allocation-reason" and command[9] == "--success-criterion"
         and command[11] == "--verification-criterion" and command[13] == "--out"
         and Path(child[0]).resolve() == Path("C:/Users/ikuto/.local/bin/uv.exe").resolve()
         and child[1:6] == ["run", "--locked", "--offline", "python", "-B"]
         and Path(child[6]).resolve() == (ROOT / PRODUCER).resolve()
         and child[7:10] == ["solve", "--seconds", "840"] and child[10] == "--out"
         and child[12:16] == ["--source-sha256", PINS[PRODUCER], "--spec-sha256", PINS[PRODUCER_SPEC]], "PLAN_PROFILE")
    need(all(type(science.get("allocation", {}).get(k)) is int and science["allocation"][k] == v
             for k, v in [("outer", 900), ("worker", 840), ("save", 20), ("shutdown", 20)]), "PLAN_ALLOCATION")
    need(type(manifest) is dict and type(terminal) is dict and manifest.get("source_sha256") == PINS["acceleration/run_compute_command.py"]
         and type(manifest.get("schema_version")) is int and manifest["schema_version"] == 1
         and manifest.get("process_scope") == "Local non-escaping process tree only; remote/daemonized compute is unsupported", "RUNTIME_SOURCE")
    need(type(manifest.get("invocation_id")) is str and re.fullmatch(r"[0-9a-f]{32}", manifest["invocation_id"])
         and terminal.get("invocation_id") == manifest["invocation_id"], "RUNTIME_INVOCATION")
    need(same(shared.path_words(manifest.get("command")), child) and Path(manifest.get("cwd", "")).resolve() == ROOT,
         "RUNTIME_COMMAND")
    need(type(manifest.get("seconds")) in (int, float) and math.isfinite(manifest["seconds"]) and manifest["seconds"] == 900
         and manifest.get("automatic_retry") is False and manifest.get("cumulative_across_commands") is False, "RUNTIME_ALLOCATION")
    cleanup = terminal.get("cleanup")
    need(type(cleanup) is dict and all(cleanup.get(k) is True for k in ["created_suspended", "resumed", "reaped", "job_active_zero_observed"])
         and same(cleanup.get("cleanup_errors"), []), "RUNTIME_CLEANUP")
    need(type(terminal.get("command_exit_code")) is int and terminal["command_exit_code"] == 0
         and type(cleanup.get("actual_exit_code")) is int and cleanup["actual_exit_code"] == 0
         and terminal.get("stop_reason") == "COMMAND_EXITED" and terminal.get("status") == "COMMAND_COMPLETED_VERIFICATION_PENDING"
         and terminal.get("deadline_reached") is False and terminal.get("error") is None, "RUNTIME_EXIT")
    need(type(terminal.get("elapsed_seconds")) in (int, float) and math.isfinite(terminal["elapsed_seconds"])
         and 0 <= terminal["elapsed_seconds"] <= 900, "RUNTIME_ELAPSED")
    reported = shared.path_words(subject.get("command"))
    need(Path(reported[0]).resolve() == py.resolve() and same(reported[1:], child[6:])
         and Path(subject.get("cwd", "")).resolve() == ROOT and subject.get("python") == "3.12.10", "WORKER_ENVIRONMENT")
    return dict(invocation_id=manifest["invocation_id"], elapsed_seconds=terminal["elapsed_seconds"],
                observed_scope="LOCAL_WINDOWS_SUSPENDED_JOB_V1", reaped=True, empty_job=True), child, command


EXTRA_AUTHOR = [("bool_support_size", "TRIPLE_DOMAIN"), ("float_support_size", "TRIPLE_DOMAIN"),
    ("bool_triple_mask", "TRIPLE_MASK"), ("float_triple_mask", "TRIPLE_MASK"),
    ("duplicate_triple_mask", "TRIPLE_MASK_ORDER"), ("unordered_triple_mask", "TRIPLE_MASK_ORDER"),
    ("missing_original_support", "INCONSISTENT_SUPPORT"), ("negative_derived_slack", "PRIMAL_NONNEGATIVE"),
    ("obsolete_lemma_method", "LEMMA_SCOPE"), ("bool_lemma_revision", "LEMMA_SCOPE")]


def synthetic_runtime():
    """A source-shaped fixture, never represented as observed producer execution."""
    py = (ROOT / "build/research-venv/Scripts/python.exe").as_posix()
    child = ["C:/Users/ikuto/.local/bin/uv.exe", "run", "--locked", "--offline", "python", "-B", PRODUCER,
             "solve", "--seconds", "840", "--out", "acceleration/results/SYNTHETIC_TRIPLE_LP",
             "--source-sha256", PINS[PRODUCER], "--spec-sha256", PINS[PRODUCER_SPEC],
             "--full-gate", "acceleration/results/SYNTHETIC_FILTER.json", "--full-gate-sha256", "a" * 64,
             "--prior-gate", "acceleration/results/SYNTHETIC_PRIOR.json", "--prior-gate-sha256", "b" * 64,
             "--lemma-report", "acceleration/results/SYNTHETIC_LEMMA.json", "--lemma-report-sha256", "c" * 64]
    command = [py, "-B", (ROOT / "acceleration/run_compute_command.py").as_posix(), "--seconds", "900",
               "--shutdown-reserve-seconds", "20", "--allocation-reason", "synthetic finite fixture",
               "--success-criterion", "fixture only", "--verification-criterion", "fixture only", "--out",
               "acceleration/results/SYNTHETIC_TRIPLE_SUPERVISION", "--"] + child
    plan = dict(source=PRODUCER, source_sha256=PINS[PRODUCER], spec_sha256=PINS[PRODUCER_SPEC],
                solve=dict(command=command[:], supervisor_argv=command[:], child_argv=child[:],
                           worker_argv=[py, "-B"] + child[6:], allocation=dict(outer=900, worker=840, save=20, shutdown=20)))
    manifest = dict(schema_version=1, source_sha256=PINS["acceleration/run_compute_command.py"],
        process_scope="Local non-escaping process tree only; remote/daemonized compute is unsupported",
        invocation_id="d" * 32, command=child[:], cwd=str(ROOT), seconds=900.0,
        automatic_retry=False, cumulative_across_commands=False)
    terminal = dict(invocation_id="d" * 32, command_exit_code=0, stop_reason="COMMAND_EXITED",
        status="COMMAND_COMPLETED_VERIFICATION_PENDING", deadline_reached=False, error=None, elapsed_seconds=0.5,
        cleanup=dict(created_suspended=True, resumed=True, reaped=True, job_active_zero_observed=True,
                     cleanup_errors=[], actual_exit_code=0))
    subject = dict(command=[py] + child[6:], cwd=str(ROOT), python="3.12.10")
    return dict(plan=plan, manifest=manifest, terminal=terminal, subject=subject, synthetic=True,
                observed_producer_runtime=False)


def branch_inventory(kind, rank=0):
    names = shared.author_inventory(None) - {"controls.json"}
    names |= {"preserved_controls.json", "controls.json", "control_all680_order.json", "control_rook_exterior_triples.json",
              "control_positive_slack.json", "control_zero_slack.json", "control_genuine_new_headers.json"}
    names |= {"control_negative_" + name + ".json" for name, _ in EXTRA_AUTHOR}
    need(len(names) == 41, "INVENTORY_INTERNAL")
    names |= {"triple_system.json", "model_receipt.json", "prior_primal_triple_diagnostic.json", "attempt.json", "triple_primal_guidance.json"}
    if kind == "primal":
        names |= {"triple_" + suffix + ".json" for suffix in ["support", "rref", "primal_rows", "primal"]}
        names |= {"checkpoints/pivot_%03d.json" % i for i in range(10, rank + 1, 10)}
    else:
        need(kind == "farkas", "CERTIFICATE_KIND")
        names |= {"triple_" + suffix + ".json" for suffix in ["dual_guidance", "farkas_checks", "farkas"]}
    return names


def author_table(raw):
    expected = [("genuine_method_header", "PASS"), ("unique_rational", "PASS"), ("tiny_lp_primal", "PASS"), ("tiny_lp_dual", "PASS")]
    expected += shared.AUTHOR_STAGES
    expected += [(n, "PASS") for n in ["all680_order", "rook_exterior_triples", "positive_slack", "zero_slack", "genuine_new_headers"]]
    expected += EXTRA_AUTHOR
    need(type(raw) is dict and all(type(raw.get(k)) is int and raw[k] == v for k, v in
        [("positive", 9), ("strict_negative", 23), ("total", 32), ("tiny_fixture_LP_calls", 3), ("target_LP_calls", 0),
         ("new_triple_controls", 15), ("known_rook9_exterior_fixture", 1)])
        and raw.get("target_model_read") is False and raw.get("structured_elimination_is_proof") is False
        and raw.get("raw_full_identity_required") is True, "AUTHOR_COUNTS")
    need(same(raw.get("records"), [dict(case=n, expected_stage=s, actual_stage=s) for n, s in expected]), "AUTHOR_STAGES")


def own_controls(guard, save, read_author_fixture):
    rows = []
    def positive(name, payload, action):
        guard(); action(); save("positive_" + name + ".json", payload)
        rows.append(dict(case=name, expected_stage="PASS", actual_stage="PASS"))
    def negative(name, stage, payload, action):
        guard(); save("negative_" + name + ".json", payload); actual = "ACCEPTED"
        try: action()
        except ValueError as exc: actual = str(exc)
        rows.append(dict(case=name, expected_stage=stage, actual_stage=actual))
        need(actual == stage, "CONTROL_STAGE_" + name)
    tiny = standard_payload([[1, 2], [2, 1]], [1, 1], [0, 7], 3)
    a, b, _ = model_payload(tiny, [[1, 2], [2, 1]], [1, 1], [0, 7], 3)
    p = primal(["1/3", "1/3", "2/3"])
    positive("positive_slack", dict(model=tiny, certificate=p), lambda: certificate("primal", p, a, b, guard))
    az, bz, _, _ = standard([[0, 1]], [1], [0, 7], 3)
    positive("zero_slack", dict(a=az, rhs=bz, certificate=primal(["0", "1", "0"])),
             lambda: certificate("primal", primal(["0", "1", "0"]), az, bz, guard))
    positive("hand_farkas", dict(a=[[0, 0]], rhs=[-1], certificate=dual(["1"], "-1")),
             lambda: certificate("farkas", dual(["1"], "-1"), [[0, 0]], [-1], guard))
    qt, qc = caps([0, 7], 17, guard)
    positive("all680", dict(masks=[0, 7], triples=qt, rows=qc), lambda: need(len(qt) == 680 and qt[0] == [0, 1, 2]
        and qt[-1] == [14, 15, 16] and sum(row[1] for row in qc) == 1 and not any(row[0] for row in qc), "CONTROL680"))
    rook = [[int(i != j and (i // 3 == j // 3 or i % 3 == j % 3)) for j in range(9)] for i in range(9)]
    rqt, rqc = caps([228], 8, guard)
    positive("rook_exterior", dict(adjacency=rook, S=list(range(8)), exterior=8, masks=[228], triples=rqt, rows=rqc),
        lambda: need([i for i in range(8) if rook[8][i]] == [2, 5, 6, 7] and sum(r[0] for r in rqc) == 4, "ROOK_CAPS"))
    large, large_b, _, _ = standard([[1] + [0] * 471 for _ in range(154)], [1] * 154, list(range(472)), guard=guard)
    lp = primal(["1"] + ["0"] * 471 + ["1"] * 680)
    positive("full834_primal", dict(a=large, rhs=large_b, certificate=lp, synthetic=True),
             lambda: certificate("primal", lp, large, large_b, guard))
    fd, fb, _, _ = standard([[0] * 472 for _ in range(154)], [-1] + [0] * 153, list(range(472)), guard=guard)
    fy = dual(["1"] + ["0"] * 833, "-1")
    positive("full1152_dual", dict(a=fd, rhs=fb, certificate=fy, synthetic=True), lambda: certificate("farkas", fy, fd, fb, guard))
    positive("typed_standard", tiny, lambda: model_payload(tiny, [[1, 2], [2, 1]], [1, 1], [0, 7], 3, guard))
    for name, m, ms, stage in [("bool_m", True, [0], "CAP_DOMAIN"), ("float_m", 3.0, [0], "CAP_DOMAIN"),
        ("bool_mask", 3, [False], "CAP_MASK_TYPE"), ("float_mask", 3, [0.0], "CAP_MASK_TYPE"),
        ("duplicate_masks", 3, [0, 0], "CAP_MASK_ORDER"), ("reverse_masks", 3, [7, 0], "CAP_MASK_ORDER")]:
        negative(name, stage, dict(m=m, masks=ms), lambda m=m, ms=ms: caps(ms, m, guard))
    for name, field, value, stage in [("boolean_rows", "rows", True, "STANDARD_INTEGER"),
        ("float_width", "variables", 3.0, "STANDARD_INTEGER"), ("wrong_ordered_triple", "ordered_triples", [[0, 2, 1]], "STANDARD_IDENTITY"),
        ("wrong_cut", "triple_coefficients", [[1, 1]], "STANDARD_IDENTITY"), ("wrong_slack", "coefficient_matrix", [[1, 2, 0], [2, 1, 0], [0, 1, -1]], "STANDARD_IDENTITY"),
        ("bool_slack", "coefficient_matrix", [[1, 2, 0], [2, 1, 0], [0, 1, True]], "STANDARD_IDENTITY"),
        ("wrong_rhs", "right_hand_side", [1, 1, 0], "STANDARD_IDENTITY"), ("false_literal", "original154_literal_unchanged", False, "STANDARD_IDENTITY")]:
        bad = copy.deepcopy(tiny); bad[field] = value
        negative(name, stage, bad, lambda bad=bad: model_payload(bad, [[1, 2], [2, 1]], [1, 1], [0, 7], 3, guard))
    for name, mutate, stage in [("bool_fraction", lambda q: q["values"].__setitem__(0, True), "RATIONAL_TYPE"),
        ("noncanonical", lambda q: q["values"].__setitem__(0, "2/6"), "RATIONAL_CANONICAL"),
        ("negative_slack", lambda q: q["values"].__setitem__(2, "-1"), "PRIMAL_NONNEGATIVE"),
        ("wrong_slack_value", lambda q: q["values"].__setitem__(2, "1"), "PRIMAL_EQUATION"),
        ("integer_lie", lambda q: q.__setitem__("integer", True), "PRIMAL_INTEGER_FLAG"),
        ("old_schema", lambda q: q.__setitem__("schema", "FILTERED_EXTERNAL_MOMENT_EXACT_PRIMAL_V1"), "TRIPLE_CERTIFICATE_SCHEMA")]:
        bad = copy.deepcopy(p); mutate(bad)
        negative(name, stage, bad, lambda bad=bad: certificate("primal", bad, a, b, guard))
    bad = copy.deepcopy(lp); bad["values"][-1] = "0"
    negative("last_row834", "PRIMAL_EQUATION", dict(certificate=bad, matrix_from_positive="full834_primal"),
             lambda: certificate("primal", bad, large, large_b, guard))
    bad_dual = copy.deepcopy(fy); bad_dual["values"][-1] = "-1"; bad_dual["rhs_dot"] = "-2"
    negative("last_slack_column1152", "FARKAS_COLUMN_NONNEGATIVE", dict(certificate=bad_dual, matrix_from_positive="full1152_dual"),
             lambda: certificate("farkas", bad_dual, fd, fb, guard))
    rt = synthetic_runtime()
    def check_runtime(value): return runtime(value["plan"], value["manifest"], value["terminal"], value["subject"])
    positive("593_without_runtime_scope", rt, lambda: check_runtime(rt))
    runtime_mutations = [
        ("plan_source", "PLAN_SOURCE", lambda q: q["plan"].__setitem__("source_sha256", "0" * 64)),
        ("plan_words", "PLAN_WORDS", lambda q: q["plan"]["solve"]["command"].pop()),
        ("plan_supervisor", "PLAN_SUPERVISOR", lambda q: q["plan"]["solve"]["supervisor_argv"].pop()),
        ("plan_worker", "PLAN_WORKER", lambda q: q["plan"]["solve"]["worker_argv"].pop()),
        ("plan_profile", "PLAN_PROFILE", lambda q: q["plan"]["solve"]["command"].__setitem__(2, "acceleration/unsupported.py")),
        ("plan_bool_allocation", "PLAN_ALLOCATION", lambda q: q["plan"]["solve"]["allocation"].__setitem__("save", True)),
        ("runtime_source", "RUNTIME_SOURCE", lambda q: q["manifest"].__setitem__("source_sha256", "0" * 64)),
        ("runtime_bool_schema", "RUNTIME_SOURCE", lambda q: q["manifest"].__setitem__("schema_version", True)),
        ("runtime_scope", "RUNTIME_SOURCE", lambda q: q["manifest"].__setitem__("process_scope", "unknown")),
        ("runtime_invocation", "RUNTIME_INVOCATION", lambda q: q["terminal"].__setitem__("invocation_id", "e" * 32)),
        ("runtime_child", "RUNTIME_COMMAND", lambda q: q["manifest"]["command"].pop()),
        ("runtime_cwd", "RUNTIME_COMMAND", lambda q: q["manifest"].__setitem__("cwd", str(ROOT.parent))),
        ("runtime_bool_seconds", "RUNTIME_ALLOCATION", lambda q: q["manifest"].__setitem__("seconds", True)),
        ("runtime_retry_integer", "RUNTIME_ALLOCATION", lambda q: q["manifest"].__setitem__("automatic_retry", 0)),
        ("runtime_reaped_integer", "RUNTIME_CLEANUP", lambda q: q["terminal"]["cleanup"].__setitem__("reaped", 1)),
        ("runtime_cleanup_error", "RUNTIME_CLEANUP", lambda q: q["terminal"]["cleanup"].__setitem__("cleanup_errors", ["error"])),
        ("runtime_bool_exit", "RUNTIME_EXIT", lambda q: q["terminal"].__setitem__("command_exit_code", False)),
        ("runtime_bool_child_exit", "RUNTIME_EXIT", lambda q: q["terminal"]["cleanup"].__setitem__("actual_exit_code", False)),
        ("runtime_deadline", "RUNTIME_EXIT", lambda q: q["terminal"].__setitem__("deadline_reached", True)),
        ("runtime_elapsed", "RUNTIME_ELAPSED", lambda q: q["terminal"].__setitem__("elapsed_seconds", -0.5)),
        ("worker_python", "WORKER_ENVIRONMENT", lambda q: q["subject"].__setitem__("python", "unknown")),
        ("worker_command", "WORKER_ENVIRONMENT", lambda q: q["subject"]["command"].pop()),
        ("worker_bool_word", "COMMAND_TYPES", lambda q: q["subject"]["command"].__setitem__(0, False))]
    for name, stage, mutate in runtime_mutations:
        bad_rt = copy.deepcopy(rt); mutate(bad_rt)
        # Single command-profile corruption keeps the separately declared supervisor vector equal.
        if name == "plan_profile": bad_rt["plan"]["solve"]["supervisor_argv"] = bad_rt["plan"]["solve"]["command"][:]
        negative(name, stage, bad_rt, lambda bad_rt=bad_rt: check_runtime(bad_rt))
    lh = dict(status="INDEPENDENT_EXTERNAL_TYPE_PAIR_AND_TRIPLE_CAPS_WRITTEN_PASS",
        claim_id="C-EXTERIOR-TYPE-PAIR-AND-TRIPLE-COMMON-NEIGHBOR-CAPS", claim_revision=1,
        producer="/root/checkpoint_audit", verifier="/root/native_driver", method="independent_derivation",
        outcome="PASS", target_resolution="NONE", inputs_sha256={LEMMA: LEMMA_SHA, PROOF: PROOF_SHA})
    ph = dict(status=shared.FULL_STATUS, producer="/root/checkpoint_audit", verifier="/root/structural",
        method="independent_artifact_check", target_resolution="NONE", implementation_version=3,
        inputs_sha256={PRIOR: PRIOR_SHA, CORE: PINS[CORE], CORE_SPEC: PINS[CORE_SPEC]})
    positive("lemma_header", dict(header=lh, synthetic=True), lambda: lemma_header(lh))
    positive("prior_header", dict(header=ph, synthetic=True), lambda: prior_header(ph))
    for name, value, stage, action, mutate in [
        ("lemma_bool_revision", lh, "LEMMA_HEADER", lemma_header, lambda q: q.__setitem__("claim_revision", True)),
        ("lemma_legacy_method", lh, "LEMMA_HEADER", lemma_header, lambda q: q.__setitem__("method", "independent_artifact_check")),
        ("lemma_missing_proof", lh, "LEMMA_DIRECT_PINS", lemma_header, lambda q: q["inputs_sha256"].pop(PROOF)),
        ("prior_bool_version", ph, "PRIOR_HEADER", prior_header, lambda q: q.__setitem__("implementation_version", True)),
        ("prior_wrong_verifier", ph, "PRIOR_HEADER", prior_header, lambda q: q.__setitem__("verifier", "/root/native_driver")),
        ("prior_missing_primal", ph, "PRIOR_DIRECT_PINS", prior_header, lambda q: q["inputs_sha256"].pop(PRIOR))]:
        bad_header = copy.deepcopy(value); mutate(bad_header)
        negative(name, stage, dict(header=bad_header, synthetic=True), lambda bad_header=bad_header, action=action: action(bad_header))
    genuine_primal = read_author_fixture("primal")
    genuine_farkas = read_author_fixture("farkas")
    for kind, raw in [("primal", genuine_primal), ("farkas", genuine_farkas)]:
        path, sha = AUTHOR_LP_FIXTURES[kind]
        positive("actual_author_lp_" + kind,
                 dict(certificate=raw, source_path=path, source_sha256=sha, actual_producer_fixture=True,
                      scientific_certificate=False, synthetic_runtime=False),
                 lambda kind=kind, raw=raw: author_lp_fixture(kind, raw, guard))
    for name, kind, mutate, stage in [
        ("author_primal_old_schema", "primal", lambda q: q.__setitem__("schema", "FILTERED_EXTERNAL_MOMENT_EXACT_PRIMAL_V1"), "TRIPLE_CERTIFICATE_SCHEMA"),
        ("author_primal_bool_coordinate", "primal", lambda q: q["values"].__setitem__(1, True), "RATIONAL_TYPE"),
        ("author_primal_missing_coordinate", "primal", lambda q: q["values"].pop(), "VECTOR_LENGTH"),
        ("author_primal_wrong_second", "primal", lambda q: q["values"].__setitem__(1, "0"), "PRIMAL_EQUATION"),
        ("author_farkas_old_schema", "farkas", lambda q: q.__setitem__("schema", "FILTERED_EXTERNAL_MOMENT_EXACT_FARKAS_V1"), "TRIPLE_CERTIFICATE_SCHEMA"),
        ("author_farkas_bool_coordinate", "farkas", lambda q: q["values"].__setitem__(0, False), "RATIONAL_TYPE"),
        ("author_farkas_wrong_rhs_receipt", "farkas", lambda q: q.__setitem__("rhs_dot", "0"), "FARKAS_RHS_RECEIPT"),
        ("author_farkas_zero_coordinate", "farkas", lambda q: q["values"].__setitem__(0, "0"), "FARKAS_RHS_NEGATIVE")]:
        bad_fixture = copy.deepcopy(genuine_primal if kind == "primal" else genuine_farkas); mutate(bad_fixture)
        negative(name, stage, dict(certificate=bad_fixture, original_fixture_kind=kind,
                 original_source_path=AUTHOR_LP_FIXTURES[kind][0], synthetic_corruption_of_actual_fixture=True,
                 scientific_certificate=False),
                 lambda kind=kind, bad_fixture=bad_fixture: author_lp_fixture(kind, bad_fixture, guard))
    result = dict(positive=13, strict_negative=59, total=72, records=rows, LP_calls=0, RREF_calls=0,
                  actual_model_read=False, actual_producer_read=True, genuine_runtime_read=False,
                  actual_producer_read_scope="Exactly two pinned tiny author LP certificate payloads; no scientific model/vector/runtime",
                  actual_author_LP_fixture_payloads=2, scientific_certificate_read=False,
                  producer_outputs_checked_scope="Two archived tiny author certificates only")
    need(len(rows) == 72, "CONTROL_POPULATION"); save("controls.json", result); return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("mode", choices=["calibrate", "full"])
    for name in ["seconds", "out", "self-sha256", "spec-sha256"]: parser.add_argument("--" + name, required=True)
    names = ["calibration", "producer-summary", "producer-plan", "runtime-manifest", "runtime-summary", "filter-gate", "prior-gate", "lemma-report"]
    for name in names: parser.add_argument("--" + name); parser.add_argument("--" + name + "-sha256")
    args = parser.parse_args(); deadline = CommandDeadline(float(args.seconds), allocation_reason="Exact independent834x1152 triple/slack arithmetic and authenticated complete package")
    def guard():
        state = deadline.status(); need(not state["stop_required"] and state["remaining_seconds"] > 20, "SAVE_RESERVE"); return state
    out = Path(args.out).resolve(); need(not out.exists(), "OUTPUT_FRESH"); out.mkdir(parents=True)
    inputs, outputs = {}, {}
    def key(path): return Path(path).resolve().relative_to(ROOT).as_posix()
    def digest(path):
        guard(); h = hashlib.sha256()
        with Path(path).open("rb") as f:
            while block := f.read(1024 * 1024): guard(); h.update(block)
        guard(); return h.hexdigest()
    def pin(path, sha):
        need(type(sha) is str and re.fullmatch(r"[0-9a-f]{64}", sha), "HASH_FORMAT"); path = Path(path).resolve(); name = key(path)
        need(path.is_file() and not path.is_symlink(), "PIN_FILE"); actual = digest(path)
        need(actual == sha and (name not in inputs or inputs[name] == sha), "INPUT_IDENTITY"); inputs[name] = actual; return path
    def read(path): guard(); data = shared.parsed(Path(path).read_bytes()); guard(); return data
    def save(name, value):
        guard(); path = out / name; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as f: f.write((json.dumps(value, indent=2, allow_nan=False) + "\n").encode())
        guard(); outputs[key(path)] = digest(path)
    def mapped(raw, base=None):
        need(type(raw) is dict and raw, "PIN_MAP")
        for name, sha in raw.items():
            need(type(name) is str and name and "\\" not in name and ":" not in name and not name.startswith(".git/")
                 and name != "CLAIMS.yaml" and all(p not in ("", ".", "..") for p in name.split("/")), "PIN_MAP_PATH")
            path = (ROOT / name).resolve(); need(base is None or path.is_relative_to(base), "OUTPUT_MAP_SCOPE"); pin(path, sha)
    def parameter(name):
        path, sha = getattr(args, name.replace("-", "_")), getattr(args, name.replace("-", "_") + "_sha256")
        need(path is not None and sha is not None, "REQUIRED_" + name); return pin(path, sha)
    try:
        pin(SELF, args.self_sha256); pin(SPEC, args.spec_sha256)
        for name, sha in PINS.items(): pin(ROOT / name, sha)
        def read_author_fixture(kind):
            path, sha = AUTHOR_LP_FIXTURES[kind]; return read(pin(ROOT / path, sha))
        controls = own_controls(guard, save, read_author_fixture); actual = None
        if args.mode == "full":
            cal = read(parameter("calibration"))
            need(cal.get("status") == CAL_STATUS and type(cal.get("implementation_version")) is int and cal["implementation_version"] == 2
                 and same(cal.get("software"), {key(SELF): args.self_sha256, key(SPEC): args.spec_sha256, **PINS})
                 and same([cal.get("controls", {}).get(k) for k in ["positive", "strict_negative", "total"]], [13, 59, 72]), "CALIBRATION_SCOPE")
            mapped(cal["inputs_sha256"]); mapped(cal["outputs_sha256"])
            gate = read(parameter("filter-gate")); mapped(shared.filter_header(gate))
            prior = read(parameter("prior-gate")); mapped(prior_header(prior))
            lemma = read(parameter("lemma-report")); mapped(lemma_header(lemma))
            for name, sha in FIXED.items(): pin(ROOT / name, sha)
            original, base_rhs, masks = shared.model_system(read(ROOT / MODEL), read(ROOT / TYPES), guard)
            subject_path = parameter("producer-summary"); subject = read(subject_path); plan = read(parameter("producer-plan"))
            need(subject.get("status") == "CANDIDATE_TRIPLE_CAPPED_EXTERNAL_MOMENT_EXACT_CERTIFICATE" and subject.get("producer") == "/root/checkpoint_audit"
                 and subject.get("independent_verifier_required") == "/root/structural" and subject.get("mode") == "solve"
                 and type(subject.get("implementation_version")) is int and subject["implementation_version"] == 1
                 and subject.get("independent_approval") is False and subject.get("target_resolution") == "NONE", "PRODUCER_SCOPE")
            need(all(subject.get(k) is False for k in ["original_model_changed", "graph_completion_proved", "whole_family_exclusion",
                 "prior_filtered_exact_primal_approval_transferred", "ledger_index_git_mutations"])
                 and type(subject.get("tiny_fixture_LP_calls")) is int and subject["tiny_fixture_LP_calls"] == 3
                 and type(subject.get("integer_search_calls")) is int and subject["integer_search_calls"] == 0, "PRODUCER_LIMITS")
            mapped(subject.get("inputs_sha256")); mapped(subject.get("outputs_sha256"), subject_path.parent)
            for name, sha in {PRODUCER: PINS[PRODUCER], PRODUCER_SPEC: PINS[PRODUCER_SPEC], **FIXED,
                PRIOR: PRIOR_SHA, key(parameter("filter-gate")): args.filter_gate_sha256,
                key(parameter("prior-gate")): args.prior_gate_sha256, key(parameter("lemma-report")): args.lemma_report_sha256}.items():
                need(subject["inputs_sha256"].get(name) == sha, "PRODUCER_DIRECT_PINS")
            def payload(name):
                path = subject_path.parent / name; need(subject["outputs_sha256"].get(key(path)) == digest(path), "PAYLOAD_PIN"); return read(path)
            a, b, cuts = model_payload(payload("triple_system.json"), original, base_rhs, masks, guard=guard)
            need(len(a) == 834 and len(a[0]) == 1152, "FULL_DIMENSIONS")
            attempt = payload("attempt.json"); shared.attempt_header(attempt)
            need(same(subject.get("triple_result"), attempt) and type(subject.get("target_LP_calls")) is int
                 and subject["target_LP_calls"] == attempt["LP_calls"], "ATTEMPT_SUMMARY")
            kind = attempt["certificate_kind"]; raw = payload("triple_" + ("primal" if kind == "primal" else "farkas") + ".json")
            need(same(raw, attempt["certificate"]), "CERTIFICATE_DUPLICATE"); exact = certificate(kind, raw, a, b, guard)
            shared.exact_receipt(payload("triple_primal_rows.json" if kind == "primal" else "triple_farkas_checks.json"), exact["receipts"])
            pin(ROOT / PRIOR, PRIOR_SHA); diagnostic = prior_diagnostic(read(ROOT / PRIOR), original, base_rhs, cuts, guard)
            need(same(payload("prior_primal_triple_diagnostic.json"), diagnostic), "PRIOR_DIAGNOSTIC")
            expected_receipt = dict(original_model_path=MODEL, original_model_sha256=FIXED[MODEL], types_path=TYPES,
                types_sha256=FIXED[TYPES], rows=834, columns=1152, original_columns=472, triple_rows=680,
                ordered_masks=masks, lemma_source_path=LEMMA, lemma_source_sha256=LEMMA_SHA,
                lemma_report_path=key(parameter("lemma-report")), lemma_report_sha256=args.lemma_report_sha256,
                old_feasibility_approval_transferred=False)
            need(same(payload("model_receipt.json"), expected_receipt), "MODEL_RECEIPT")
            rank = 0
            if kind == "primal":
                xs = payload("triple_primal_guidance.json").get("x")
                need(type(xs) is list and len(xs) == 1152 and all(type(v) is float and math.isfinite(v) for v in xs), "GUIDANCE_SHAPE")
                support = payload("triple_support.json")
                need(same(support, dict(indices=[i for i, v in enumerate(xs) if v > 0],
                    rule="every numeric coordinate strictly >0.0; no tolerance", numerical_selection_only=True)), "SUPPORT_METADATA")
                need(all(raw["values"][i] == "0" for i in range(1152) if i not in support["indices"]), "SUPPORT_EXPANSION")
                rref = payload("triple_rref.json"); rank = rref.get("rank")
                need(type(rank) is int and 0 <= rank <= min(472, sum(i < 472 for i in support["indices"]))
                     and rref.get("free_variables_zero") is True and rref.get("rank_is_producer_metadata") is True
                     and rref.get("structured_slack_elimination") is True
                     and rref.get("rank_scope") == "restricted original variables after selected slack elimination", "RREF_METADATA_SCOPE")
            required = branch_inventory(kind, rank)
            declared = {str((ROOT / k).resolve().relative_to(subject_path.parent)).replace("\\", "/") for k in subject["outputs_sha256"]}
            physical = {p.relative_to(subject_path.parent).as_posix() for p in subject_path.parent.rglob("*") if p.is_file()}
            need(declared == required and physical == required | {"summary.json"}
                 and not any(p.is_symlink() for p in subject_path.parent.rglob("*")), "OUTPUT_POPULATION")
            author = payload("controls.json"); author_table(author); need(same(subject.get("controls"), author), "AUTHOR_SUMMARY")
            # Original optimizer/RREF negative stages are authenticated author observations, not recomputed proof.
            author_lp_fixture("primal", payload("control_lp_primal_primal.json"), guard)
            author_lp_fixture("farkas", payload("control_lp_dual_farkas.json"), guard)
            for name in ["positive_slack", "zero_slack"]:
                hand = payload("control_" + name + ".json")
                aa, bb, _, _ = standard(hand["a"], hand["rhs"], [0, 7], 3, guard)
                # Both raw fixtures have cut[0,1]; source-independent builder gives that exact row.
                need(same(hand["cuts"], [[0, 1]]), "AUTHOR_HAND_CUT")
                certificate("primal", primal(hand["values"]), aa, bb, guard)
            runtime_result, child, command = runtime(plan, read(parameter("runtime-manifest")), read(parameter("runtime-summary")), subject)
            for name in ["filter-gate", "prior-gate", "lemma-report"]:
                option = "--" + ("full-gate" if name == "filter-gate" else name)
                need(option in child and option + "-sha256" in child
                     and Path(child[child.index(option) + 1]).resolve() == parameter(name)
                     and child[child.index(option + "-sha256") + 1] == getattr(args, name.replace("-", "_") + "_sha256"), "PLAN_PREREQUISITE")
            need(Path(command[14]).resolve() == Path(args.runtime_manifest).resolve().parent
                 and Path(args.runtime_manifest).resolve().parent == Path(args.runtime_summary).resolve().parent
                 and Path(child[11]).resolve() == subject_path.parent, "PLAN_OUTPUT_ROOT")
            exact.pop("receipts")
            statement = ("The fixed triple-capped external-neighborhood moment standard form with 834 equations and 1152 nonnegative variables has the saved exact nonnegative rational feasible vector; all 834 equations hold." if kind == "primal" else
                "The fixed triple-capped external-neighborhood moment standard form with 834 equations and 1152 nonnegative variables has the saved exact rational Farkas vector: all 1152 column products are nonnegative and its RHS product is strictly negative; this fixed rational system is infeasible.")
            actual = dict(statement=statement, certificate_kind=kind, exact=exact, rows=834, variables=1152,
                original_variables=472, original_equations=154, triple_caps=680, producer_output_files=len(physical),
                prior_vector_diagnostic=diagnostic, runtime=runtime_result, rank_and_pivot_mathematics_checked=False,
                graph_completion_proved=False, integer_realization_proved=False)
            save("exact_certificate_outcome.json", actual)
        for name, sha in list(inputs.items()): pin(ROOT / name, sha)
        summary = dict(status=CAL_STATUS if args.mode == "calibrate" else FULL_STATUS, timestamp=datetime.now(timezone.utc).isoformat(),
            producer="/root/checkpoint_audit", verifier="/root/structural", method="independent_artifact_check", target_resolution="NONE",
            implementation_version=2, command=[sys.executable] + sys.argv, cwd=str(ROOT), python=platform.python_version(),
            software={key(SELF): args.self_sha256, key(SPEC): args.spec_sha256, **PINS}, inputs_sha256=inputs.copy(), outputs_sha256=outputs.copy(),
            controls=controls, outcome=actual, genuine_runtime_read=args.mode == "full", target_model_read=args.mode == "full",
            producer_outputs_checked=True, scientific_producer_outputs_checked=args.mode == "full",
            producer_outputs_checked_scope="Full producer package" if args.mode == "full" else "Two pinned tiny author LP certificate payloads only",
            actual_author_LP_fixture_payloads_read=2, actual99_adjacency_read=False, LP_calls=0, RREF_calls=0,
            scope=dict(description="Synthetic finite triple/slack/runtime controls plus two genuine tiny author certificates only" if args.mode == "calibrate" else
                "One exact fixed induced17 necessary triple-capped external moment relaxation; no whole family or global target conclusion", unrestricted=False, target_resolution="NONE"),
            shared_trust=["Shared Structural53508 strictJSON/base154 reconstruction/generalFraction arithmetic; no CP LP/RREF imports",
                "Python integer/Fraction/JSON/SHA/deadline/593Windows suspendedJob/lockedUV", "Native exactfilter and pair/triple proof are explicit distinct premises"],
            limitations=["Rational feasibility is not integer realization or graph completion", "Guidance-only output rejected; failure is not infeasibility",
                "Rank/pivots/support algorithm authenticated metadata only", "Author LP/RREF negative stages authenticated observations, not independent RREF replay"], deadline=guard())
        save("summary.json", summary); guard()
    except Exception as exc:
        (out / "failure.json").write_text(json.dumps(dict(status="FAILED_PRESERVED", stage=str(exc), exception_type=type(exc).__name__,
            timestamp=datetime.now(timezone.utc).isoformat(), inputs_sha256=inputs, outputs_sha256=outputs,
            no_infeasibility_inference=True, no_automatic_retry=True, deadline=deadline.status(), target_resolution="NONE"), indent=2) + "\n", encoding="utf8")
        raise


if __name__ == "__main__": main()

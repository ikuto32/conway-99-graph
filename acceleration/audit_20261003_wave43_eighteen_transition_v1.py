"""SOURCE ONLY: exact 371->389 metadata impact; no registrar/math imports.

Structural independently projects the eighteen frozen ordinary schema2 bindings
and eight explicit descriptor scopes. Some underlying papers have this verifier
as discovery author: this program checks bookkeeping only, not their mathematics.
"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import yaml
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/audit_20261003_wave43_eighteen_transition_v1.py"
SPEC = SELF.replace(".py", "_spec.md")
DESCRIPTOR = "acceleration/proposal_20261003_wave43_eighteen_written_bindings_v2.json"
DESCRIPTOR_SHA = "3f29f453813459d18740e5fb70fb7adddf56fed513db84f7598d4e4aeb1b331c"
PLAN = "acceleration/plan_20261003_wave43_eighteen_written_registration_v2.json"
PLAN_SHA = "0bfa921425b939536ef745c22869ce50191fb2e396a885f6f8d87254f05bb65e"
EIGHT = "acceleration/proposal_20261003_registrar_v18_exact_written_v1.json"
EIGHT_SHA = "2692248d4274793d5fb162503d1eb3b9e5b02a517ef13f5fd6080ffc80f49629"
BASE = "acceleration/results/20261003_wave42_publication01/CLAIMS.after.yaml"
BEFORE_SHA = "23ee170c0f7250843ec2852758f0dd7d1324e85647c44e1907a62f062db47da9"
REG = "acceleration/results/20261003_wave43_registration01"
SCOPED_EXCLUSION = "C-TARGET99-TWELVE-LINE-CAP-CORE-COMPLETION-EXCLUSION"
EXTERNAL_DEPENDENCY = "C-UNRESTRICTED-DEGREE14-TERNARY-CONNECTED-SUBCUBIC-SUPPORT-RESTRICTION"
CAL_PASS = "INDEPENDENT_WAVE43_EIGHTEEN_TYPED_METADATA_TRANSITION_V1_CALIBRATION_PASS"
PASS = "INDEPENDENT_WAVE43_EIGHTEEN_TYPED_METADATA_ACTUAL_TRANSITION_V1_PASS"
PINS = {
    DESCRIPTOR: DESCRIPTOR_SHA, PLAN: PLAN_SHA, EIGHT: EIGHT_SHA, BASE: BEFORE_SHA,
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command_v2.py": "46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17",
    "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
    "docs/COMPUTE_POLICY.md": "9d3f57e8e36376e71fe5fb2733d19d6c0eacf92c71f763e66224dda95f59e136",
}


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def typed(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def same(a, b):
    return typed(a) == typed(b)


def literal(a, b):
    """JSON contract equality also preserves nested key and array order."""
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return list(a) == list(b) and all(literal(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(literal(x, y) for x, y in zip(a, b))
    return a == b


def raw_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    def constant(value):
        raise ValueError("NONFINITE_JSON")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        need(type(key) is str and key not in result, "DUPLICATE_YAML_KEY")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def stamp(value):
    need(type(value) is str and len(value) > 0, "TIMESTAMP_TYPE")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("TIMESTAMP_PARSE") from None
    need(parsed.tzinfo is not None, "TIMESTAMP_ZONE")


def selected(contract, actual, stage):
    need(type(contract) is dict and type(actual) is dict
         and all(k in actual and literal(v, actual[k]) for k, v in contract.items()), stage)


def metadata(row, binding, report):
    selected(row["binding_contract"], binding, "META_BINDING_CONTRACT")
    selected(row["original_binding_reason_fields"], binding, "META_BINDING_REASONS")
    selected(row["explicit_binding_null_fields"], binding, "META_BINDING_NULLS")
    selected(row["original_report_contract"], report, "META_REPORT_CONTRACT")
    heads = row["original_report_headlines"]
    selected(heads["present"], report, "REPORT_HEADLINE_PRESENT")
    need(heads["absences_preserved"] is True and all(k not in report for k in heads["absent"]),
         "REPORT_HEADLINE_ABSENCE")
    need(literal(binding["inputs_sha256"], row["literal_input_pins"]), "META_INPUT_MAP")
    need(type(row["declared_input_count"]) is int
         and row["declared_input_count"] == len(binding["inputs_sha256"]), "META_COUNT")
    need(type(binding["revision"]) is int and binding["revision"] == 1
         and type(binding["claim_revision"]) is int and binding["claim_revision"] == 1
         and binding["producer"] != binding["verifier"]
         and binding["method"] == "independent_derivation", "META_ROLES")
    stamp(binding["verification_timestamp"])


def editorial(row, binding, report, eight):
    """Independently assembled schema receipt from literal descriptor data."""
    cid = binding["id"]
    item = eight[cid]
    need(literal(item["original_scope"], binding["scope"])
         and literal(item["schema_scope"], row["planned_schema_scope"]), "EIGHT_LITERAL_SCOPE")
    return dict(claim_id=cid, claim_revision=1,
        recorded_binding=row["binding_path"], recorded_binding_sha256=row["binding_sha256"],
        original_report=binding["report"], original_report_sha256=binding["report_sha256"],
        original_report_statement_field="statement", original_report_statement=report["statement"],
        recorded_binding_statement=binding["statement"], raw_statement_changed=False,
        original_report_scope=report["scope"], original_binding_scope=binding["scope"],
        schema_scope=row["planned_schema_scope"], original_report_headline_fields=item["report_headlines"]["present"],
        original_report_absent_headline_fields={k: None for k in item["report_headlines"]["absent"]},
        original_report_absent_headline_null_reason=item["missing_headline_mapping"],
        original_report_command=report["command"], original_report_command_null_reason=report["command_null_reason"],
        original_report_controls=item["written_control_fields"], original_independent_report_method=report["method"],
        schema_method=binding["method"], descriptor_path=EIGHT, descriptor_sha256=EIGHT_SHA,
        reason="Only the exact eight frozen written metadata bindings: keep literal statement equality, complete original scope, every conditional/whole-support premise and explicit raw report absences. Three schema-scope fields are projected in memory. No original report/binding is rewritten and no mathematics or target inference is performed.",
        mathematical_replays=0, target_resolution="NONE")


def projection(before, rows, bindings, reports, eight, generated):
    stamp(generated)
    need(type(before) is dict and len(before["claims"]) == 371, "BASE_POPULATION")
    out = copy.deepcopy(before)
    present = {c["id"]: c for c in before["claims"]}
    mapping_receipts = []
    for row, binding, report in zip(rows, bindings, reports):
        cid = binding["id"]
        need(cid not in present, "NEW_CLAIM_ID")
        paths = {row["binding_path"]: row["binding_sha256"], binding["report"]: binding["report_sha256"]}
        for name, identity in binding["inputs_sha256"].items():
            need(name not in paths or paths[name] == identity, "CLOSURE_CONFLICT")
            paths[name] = identity
        for collection in ("artifacts", "evidence"):
            records = binding.get(collection, [])
            if type(records) is dict:
                for key, name in records.items():
                    if not key.endswith("_sha256"):
                        identity = records[key + "_sha256"]
                        need(name not in paths or paths[name] == identity, "CLOSURE_CONFLICT")
                        paths[name] = identity
            else:
                need(type(records) is list, "BOUND_EVIDENCE_TYPE")
                for record in records:
                    if type(record) is dict and "path" in record:
                        need(record["path"] not in paths or paths[record["path"]] == record["sha256"], "CLOSURE_CONFLICT")
                        paths[record["path"]] = record["sha256"]
        aids, hashes = [], {}
        for index, (name, identity) in enumerate(sorted(paths.items())):
            aid = cid.lower() + "-r1-evidence-" + str(index)
            need(aid not in {a["id"] for a in out["artifacts"]}, "NEW_ARTIFACT_ID")
            aids.append(aid); hashes[aid] = identity
            out["artifacts"].append(dict(id=aid, path=name, sha256=identity, availability="LOCAL_ONLY",
                retrieval="Exact workspace path; checking reports give raw input and replay commands.",
                unavailable_reason="Immutable publication of this newly bound evidence has not yet been confirmed."))
        deps, notes = [], []
        for dependency in binding["dependencies"]:
            need(set(dependency) <= {"id", "revision", "relation", "reason"}
                 and type(dependency["revision"]) is int and dependency["revision"] == 1,
                 "DEPENDENCY_TYPE")
            need(dependency["id"] in present and present[dependency["id"]]["revision"] == 1
                 and present[dependency["id"]]["status"] == "VERIFIED"
                 and present[dependency["id"]]["review_state"] == "CLEAR", "DEPENDENCY_ORDER")
            deps.append({k: dependency[k] for k in ("id", "revision", "relation")})
            if "reason" in dependency:
                notes.append({k: dependency[k] for k in ("id", "revision", "reason")})
        is_eight = cid in eight
        scope = copy.deepcopy(row["planned_schema_scope"] if is_eight else binding["scope"])
        need(type(scope) is dict and set(scope) == {"description", "unrestricted_target", "target_resolution"}
             and type(scope["unrestricted_target"]) is bool and scope["target_resolution"] == "NONE", "SCHEMA_SCOPE")
        claim = {k: copy.deepcopy(binding[k]) for k in
            ("id", "revision", "statement", "kind", "basis", "status", "review_state", "assumptions", "limitations")}
        verification = dict(claim_revision=1, verifier=binding["verifier"], method=binding["method"],
            command_or_audit=binding["report"], timestamp=binding["verification_timestamp"], outcome="PASS",
            scope=scope["description"], artifact_hashes=hashes,
            shared_components=binding.get("shared_components", report.get("shared_components")),
            controls=[json.dumps(binding.get("controls", report.get("controls", report.get("corrupted_controls_rejected"))), sort_keys=True)],
            limitations=binding["limitations"])
        unknowns = dict(external_source="Internal scoped checking; no external or novelty status inferred.",
            premises=json.dumps(binding.get("premise_state", binding.get("mathematical_scope", {})), sort_keys=True),
            dependency_notes=json.dumps(notes, sort_keys=True), original_binding_method=binding["method"],
            original_binding_kind=binding["kind"], original_binding_scope=json.dumps(binding["scope"], sort_keys=True)
                if is_eight else "No schema projection; binding uses the schema scope fields directly.")
        if is_eight:
            mapping = editorial(row, binding, report, eight)
            unknowns["editorial_statement_mapping"] = json.dumps(mapping, sort_keys=True)
            mapping_receipts.append(mapping)
        manifest = next(aid for aid, (name, _) in zip(aids, sorted(paths.items())) if name == binding["report"])
        claim.update(dependencies=deps, scope=scope, evidence=aids, verification=[verification],
            created_at=generated, updated_at=generated, external_source=None, unknowns=unknowns,
            reproducibility=dict(manifest=manifest))
        out["claims"].append(claim); present[cid] = claim
    out["updated_at"] = generated
    return out, mapping_receipts


def check(after, before, expected):
    need(type(after) is dict and type(after.get("claims")) is list and len(after["claims"]) == 389,
         "AFTER_POPULATION")
    need([c["id"] for c in after["claims"]] == [c["id"] for c in expected["claims"]], "CLAIM_IDS")
    need(same(after["claims"][:371], before["claims"]), "OLD_CLAIMS_TYPED")
    need(type(after.get("artifacts")) is list and same(after["artifacts"][:len(before["artifacts"])], before["artifacts"]),
         "OLD_ARTIFACTS_TYPED")
    need(same({k: v for k, v in after.items() if k not in ("claims", "artifacts", "updated_at")},
              {k: v for k, v in before.items() if k not in ("claims", "artifacts", "updated_at")}), "TOP_LEVEL_TYPED")
    need(same(after["claims"][371:], expected["claims"][371:]), "NEW_CLAIMS_TYPED")
    need(same(after["artifacts"][len(before["artifacts"]):], expected["artifacts"][len(before["artifacts"]):]),
         "NEW_ARTIFACTS_TYPED")
    need(same(after, expected), "ENTIRE_TYPED_PROJECTION")
    need(Counter(c["status"] for c in after["claims"]) == {"VERIFIED": 381, "CANDIDATE": 3, "REFUTED": 5}
         and Counter(c["review_state"] for c in after["claims"]) == {"CLEAR": 389}, "COUNTS")


def synthetic_before():
    claims = [dict(id="SYNTHETIC-OLD-" + str(i), revision=1, status="VERIFIED" if i < 363 else "CANDIDATE" if i < 366 else "REFUTED",
        review_state="CLEAR", statement="Synthetic preserved claim", verification=[dict(verifier="synthetic")]) for i in range(371)]
    claims[0]["id"] = EXTERNAL_DEPENDENCY
    return dict(updated_at="2000-01-01T00:00:00+00:00", target=dict(status="UNKNOWN", reason="preserved"), claims=claims,
        artifacts=[dict(id="synthetic-artifact-" + str(i), path="synthetic/" + str(i), sha256="0" * 64,
            availability="PUBLIC", retrieval="literal synthetic immutable retrieval") for i in range(119)])


def controls(rows, bindings, reports, eight, tick):
    before = synthetic_before(); expected, _ = projection(before, rows, bindings, reports, eight, "2000-01-02T00:00:00+00:00")
    check(copy.deepcopy(expected), before, expected)
    mutations = [
        ("missing_all18", "AFTER_POPULATION", lambda x: x["claims"].__delitem__(slice(371, None))),
        ("missing_one", "AFTER_POPULATION", lambda x: x["claims"].pop()),
        ("new_id", "CLAIM_IDS", lambda x: x["claims"][-1].update(id="wrong")),
        ("old_statement", "OLD_CLAIMS_TYPED", lambda x: x["claims"][1].update(statement="changed")),
        ("old_bool_revision", "OLD_CLAIMS_TYPED", lambda x: x["claims"][1].update(revision=True)),
        ("old_float_revision", "OLD_CLAIMS_TYPED", lambda x: x["claims"][1].update(revision=1.0)),
        ("old_verifier", "OLD_CLAIMS_TYPED", lambda x: x["claims"][1]["verification"][0].update(verifier="changed")),
        ("public_retrieval", "OLD_ARTIFACTS_TYPED", lambda x: x["artifacts"][0].update(retrieval="different")),
        ("public_availability", "OLD_ARTIFACTS_TYPED", lambda x: x["artifacts"][0].update(availability="LOCAL_ONLY")),
        ("old_artifact_hash", "OLD_ARTIFACTS_TYPED", lambda x: x["artifacts"][0].update(sha256="f" * 64)),
        ("target", "TOP_LEVEL_TYPED", lambda x: x["target"].update(status="VERIFIED")),
        ("top_extra", "TOP_LEVEL_TYPED", lambda x: x.update(unbound=True)),
        ("target_numeric_alias", "TOP_LEVEL_TYPED", lambda x: x["target"].update(reason=False)),
        ("new_statement", "NEW_CLAIMS_TYPED", lambda x: x["claims"][-1].update(statement="broader")),
        ("new_dependency", "NEW_CLAIMS_TYPED", lambda x: x["claims"][-1]["dependencies"][0].update(revision=True)),
        ("dependency_reason", "NEW_CLAIMS_TYPED", lambda x: x["claims"][-1]["unknowns"].update(dependency_notes="[]")),
        ("verification_timestamp", "NEW_CLAIMS_TYPED", lambda x: x["claims"][-1]["verification"][0].update(timestamp="2000-01-02T09:00:00+09:00")),
        ("verifier", "NEW_CLAIMS_TYPED", lambda x: x["claims"][-1]["verification"][0].update(verifier="/root")),
        ("controls", "NEW_CLAIMS_TYPED", lambda x: x["claims"][-1]["verification"][0].update(controls=[])),
        ("evidence", "NEW_CLAIMS_TYPED", lambda x: x["claims"][-1]["evidence"].pop()),
        ("manifest", "NEW_CLAIMS_TYPED", lambda x: x["claims"][-1]["reproducibility"].update(manifest="wrong")),
        ("created_timestamp", "NEW_CLAIMS_TYPED", lambda x: x["claims"][-1].update(created_at="2000-01-02T09:00:00+09:00")),
        ("original_scope", "NEW_CLAIMS_TYPED", lambda x: x["claims"][371]["unknowns"].update(original_binding_scope="{}")),
        ("method", "NEW_CLAIMS_TYPED", lambda x: x["claims"][-1]["verification"][0].update(method="independent_artifact_check")),
        ("kind", "NEW_CLAIMS_TYPED", lambda x: x["claims"][-1].update(kind="computational observation")),
        ("mapping_bool_alias", "NEW_CLAIMS_TYPED", lambda x: x["claims"][371]["unknowns"].update(editorial_statement_mapping=x["claims"][371]["unknowns"]["editorial_statement_mapping"].replace('"raw_statement_changed": false', '"raw_statement_changed": 0'))),
        ("new_artifact_hash", "NEW_ARTIFACTS_TYPED", lambda x: x["artifacts"][-1].update(sha256="f" * 64)),
        ("top_timestamp", "ENTIRE_TYPED_PROJECTION", lambda x: x.update(updated_at="2000-01-02T09:00:00+09:00")),
    ]
    for index in range(8):
        mutations.append(("scope_projection_" + str(index), "NEW_CLAIMS_TYPED",
            lambda x, index=index: x["claims"][371 + index]["scope"].update(unrestricted_target=1)))
    observed = []
    for name, stage, mutate in mutations:
        tick(); damaged = copy.deepcopy(expected); mutate(damaged)
        try:
            check(damaged, before, expected)
        except ValueError as error:
            need(str(error) == stage, "CONTROL_STAGE:" + name)
            observed.append(dict(case=name, expected=stage, actual=str(error)))
        else:
            raise ValueError("CONTROL_ACCEPTED:" + name)
    for index in (6, 7, 8):
        tick(); damaged = copy.deepcopy(reports[index]); damaged["claim_status"] = "VERIFIED"
        try:
            metadata(rows[index], bindings[index], damaged)
        except ValueError as error:
            need(str(error) == "REPORT_HEADLINE_ABSENCE", "CONTROL_HEADLINE_STAGE")
            observed.append(dict(case="absent_headline_" + str(index), expected=str(error), actual=str(error)))
        else:
            raise ValueError("CONTROL_HEADLINE_ACCEPTED")
    for name, row, binding, report, stage in (
        ("bool_input_count", {**rows[0], "declared_input_count": True}, bindings[0], reports[0], "META_COUNT"),
        ("float_report_revision", rows[0], bindings[0], {**reports[0], "claim_revision": 1.0}, "META_REPORT_CONTRACT"),
    ):
        tick()
        try:
            metadata(row, binding, report)
        except ValueError as error:
            need(str(error) == stage, "CONTROL_META_STAGE:" + name)
            observed.append(dict(case=name, expected=stage, actual=str(error)))
        else:
            raise ValueError("CONTROL_META_ACCEPTED:" + name)
    need(len(observed) == 41, "CONTROL_POPULATION")
    return observed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("calibration", "check"))
    parser.add_argument("--out", type=Path, required=True); parser.add_argument("--seconds", type=float, required=True)
    for key in ("self-sha256", "spec-sha256", "expected-head", "protected-index-sha256"):
        parser.add_argument("--" + key, required=True)
    for key in ("calibration", "registration-summary", "runtime-manifest", "runtime-summary"):
        parser.add_argument("--" + key); parser.add_argument("--" + key + "-sha256")
    args = parser.parse_args(); deadline = CommandDeadline(args.seconds,
        allocation_reason="One complete eighteen-claim metadata projection and closure;20save; no mathematics or registrar invocation")
    out = args.out.resolve(); need(out.is_relative_to(ROOT) and not out.exists(), "FRESH_OUTPUT"); out.mkdir(parents=True)
    pins = {}
    def tick():
        state = deadline.status(); need(not state["stop_required"] and state["remaining_seconds"] > 20, "SAVE_RESERVE")
    def pin(name, identity):
        tick(); path = (ROOT / name).resolve()
        need(type(name) is str and type(identity) is str and len(identity) == 64
             and path.is_relative_to(ROOT) and path.is_file() and not name.startswith(".git/"), "PIN_PATH")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while raw := stream.read(1024 * 1024):
                tick(); digest.update(raw)
        tick(); value = digest.hexdigest(); need(value == identity, "PIN_IDENTITY:" + name)
        need(name not in pins or pins[name] == value, "PIN_CONFLICT"); pins[name] = value
        return path
    def read(name):
        tick(); value = raw_json((ROOT / name).read_bytes()); tick(); return value
    def save(name, value):
        tick(); path = out / name
        with path.open("x", encoding="utf8", newline="\n") as stream:
            json.dump(value, stream, indent=2, allow_nan=False); stream.write("\n")
        tick()
    try:
        for name, identity in {**PINS, SELF: args.self_sha256, SPEC: args.spec_sha256}.items():
            pin(name, identity)
        descriptor = read(DESCRIPTOR); plan = read(PLAN); eight_raw = read(EIGHT)
        rows = descriptor["records_in_dependency_order"]
        need(len(rows) == 18 and len(eight_raw["adapters"]) == 8, "DECLARED_POPULATION")
        eight = {r["id"]: r for r in eight_raw["adapters"]}
        need([r["binding_contract"]["id"] for r in rows[:8]] == list(eight), "EIGHT_ORDER")
        need([r["order"] for r in rows] == list(range(1, 19)), "BATCH_ORDER")
        for name, identity in descriptor["declared_binding_and_checking_closure"].items():
            pin(name, identity)
        for name, identity in plan["immutable_declared_inputs_sha256"].items():
            pin(name, identity)
        bindings, reports = [], []
        for row in rows:
            pin(row["binding_path"], row["binding_sha256"]); binding = read(row["binding_path"])
            pin(binding["report"], binding["report_sha256"]); report = read(binding["report"])
            metadata(row, binding, report); bindings.append(binding); reports.append(report)
        # Authenticate every path used by the independently projected additions,
        # including a declared artifact/evidence path absent from an input map.
        prototype, _ = projection(synthetic_before(), rows, bindings, reports, eight, "2000-01-02T00:00:00+00:00")
        for artifact in prototype["artifacts"][119:]:
            pin(artifact["path"], artifact["sha256"])
        before = yaml.load((ROOT / BASE).read_bytes(), Loader=UniqueLoader); tick()
        negatives = controls(rows, bindings, reports, eight, tick)
        if args.mode == "calibration":
            actual, mappings = projection(synthetic_before(), rows, bindings, reports, eight, "2000-01-02T00:00:00+00:00")
            save("synthetic_before.json", synthetic_before())
            save("synthetic_after.json", actual)
            status = CAL_PASS
        else:
            source_pins = pins.copy(); values = []
            for label in ("calibration", "registration_summary", "runtime_manifest", "runtime_summary"):
                name = getattr(args, label); identity = getattr(args, label + "_sha256")
                need(name is not None and identity is not None, "CHECK_ARGUMENTS"); pin(name, identity); values.append(read(name))
            cal, registration, runtime, terminal = values
            need(cal["status"] == CAL_PASS and type(cal["positive_controls"]) is int and cal["positive_controls"] == 1
                 and type(cal["strict_negative_controls"]) is int and cal["strict_negative_controls"] == 41
                 and cal["verifier"] == "/root/structural" and cal["method"] == "independent_engineering_artifact_check"
                 and cal["prior_claims_and_artifacts_checked"] is False
                 and cal["mathematical_replays"] == 0 and type(cal["mathematical_replays"]) is int
                 and cal["source_sha256"] == args.self_sha256 and cal["spec_sha256"] == args.spec_sha256,
                 "CALIBRATION_GATE")
            need(type(cal["inputs_sha256"]) is dict
                 and all(cal["inputs_sha256"].get(name) == identity for name, identity in source_pins.items()),
                 "CALIBRATION_INPUTS")
            for name, identity in cal["inputs_sha256"].items():
                pin(name, identity)
            for name, identity in cal["outputs_sha256"].items():
                pin(name, identity)
            need(same(runtime["command"], plan["child_argv"]) and type(runtime["seconds"]) in (int, float)
                 and runtime["seconds"] == 180 and type(runtime["shutdown_reserve_seconds"]) in (int, float)
                 and runtime["shutdown_reserve_seconds"] == 30 and runtime["cwd"] == str(ROOT)
                 and runtime["source_sha256"] == PINS["acceleration/run_compute_command.py"]
                 and runtime["automatic_retry"] is False and runtime["cumulative_across_commands"] is False,
                 "RUNTIME_COMMAND")
            need(type(terminal["invocation_id"]) is str and len(terminal["invocation_id"]) == 32
                 and all(c in "0123456789abcdef" for c in terminal["invocation_id"])
                 and terminal["invocation_id"] == runtime["invocation_id"] and type(terminal["command_exit_code"]) is int
                 and terminal["command_exit_code"] == 0 and terminal["error"] is None
                 and terminal["stop_reason"] == "COMMAND_EXITED" and terminal["deadline_reached"] is False
                 and terminal["hard_limit_observed"] is True
                 and terminal["cleanup"]["reaped"] is True and terminal["cleanup"]["job_active_zero_observed"] is True
                 and type(terminal["cleanup"]["actual_exit_code"]) is int and terminal["cleanup"]["actual_exit_code"] == 0
                 and terminal["cleanup"]["cleanup_errors"] == [], "TERMINAL")
            need(same(registration["command"], [str(Path(plan["worker_argv"][0])), *plan["worker_argv"][2:]])
                 and registration["source_commit"] == args.expected_head and registration["source_sha256"] == descriptor["registrar"]["sha256"]
                 and registration["status"] == "EXACT_BOUND_SCOPED_CLAIMS_REGISTERED" and registration["cwd"] == str(ROOT)
                 and registration["before_ledger_sha256"] == BEFORE_SHA
                 and type(registration["claim_records"]) is int and registration["claim_records"] == 389
                 and type(registration["new_exclusions"]) is int and registration["new_exclusions"] == 0
                 and registration["target_resolution"] == "UNKNOWN"
                 and type(registration["mathematical_replays"]) is int and registration["mathematical_replays"] == 0,
                 "REGISTRATION_SCOPE")
            need(same(registration["status_counts"], {"VERIFIED": 381, "CANDIDATE": 3, "REFUTED": 5})
                 and same(registration["review_state_counts"], {"CLEAR": 389}), "REGISTRATION_COUNTS")
            expected, mappings = projection(before, rows, bindings, reports, eight, registration["timestamp"])
            need(same(registration["editorial_statement_mappings"], mappings)
                 and registration["new_claim_ids"] == [b["id"] for b in bindings], "REGISTRATION_MAPPING")
            pin(REG + "/CLAIMS.before.yaml", BEFORE_SHA)
            pin(REG + "/CLAIMS.after.yaml", registration["ledger_sha256"]); pin("CLAIMS.yaml", registration["ledger_sha256"])
            actual = yaml.load((ROOT / REG / "CLAIMS.after.yaml").read_bytes(), Loader=UniqueLoader); tick()
            check(actual, before, expected); status = PASS
        need(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == args.expected_head, "CONTEXT_HEAD")
        need(hashlib.sha256((ROOT / ".git/index").read_bytes()).hexdigest() == args.protected_index_sha256, "CONTEXT_INDEX")
        expected_live = BEFORE_SHA if args.mode == "calibration" else registration["ledger_sha256"]
        need(hashlib.sha256((ROOT / "CLAIMS.yaml").read_bytes()).hexdigest() == expected_live, "CONTEXT_LEDGER")
        for name, identity in list(pins.items()):
            pin(name, identity)
        save("controls.json", negatives)
        save("mapping_receipts.json", mappings)
        outputs = {}
        for path in sorted(out.rglob("*")):
            if path.is_file():
                tick(); outputs[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest(); tick()
        save("summary.json", dict(status=status, timestamp=datetime.now(timezone.utc).isoformat(), verifier="/root/structural",
            method="independent_engineering_artifact_check", source_sha256=args.self_sha256, spec_sha256=args.spec_sha256,
            command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=pins,
            outputs_sha256=outputs,
            mode=args.mode, positive_controls=1, strict_negative_controls=41, claims_before=371, claims_after=len(actual["claims"]),
            status_counts=dict(Counter(c["status"] for c in actual["claims"])), review_state_counts=dict(Counter(c["review_state"] for c in actual["claims"])),
            prior_PUBLIC_preserved=sum(a["availability"] == "PUBLIC" for a in before["artifacts"]) if args.mode == "check" else None,
            prior_claims_and_artifacts_checked=args.mode == "check", exact_new_bindings=18, original_scope_projections=8,
            ordinary_routes=10, author_report_new_exclusions=0, independently_identified_scoped_configuration_exclusions=1,
            scoped_exclusion_id=SCOPED_EXCLUSION, target_exclusions=0, target_resolution="NONE",
            executed_mathematical_controls=0, formal_verification=False, external_review=False,
            synthetic_prior_PUBLIC_control_population=119, negative_payload_retention="In-memory metadata mutations are source-reproducible; precise41 stage rows and unmodified synthetic before/after payloads are durable.",
            ledger_mutations=0, index_mutations=0, mathematical_replays=0, deadline=deadline.status(),
            limitations=["Bookkeeping only; this reviewer authored some underlying mathematical papers and does not reapprove them here.",
                "No registrar mapping function, mathematical discovery program, native worker or old actual13 approval is imported.",
                "Entire old typed ledger and every new field/artifact are checked; author new_exclusions0 is retained separately from one finite scoped exclusion.",
                "Original report headline absences, literal verification timestamps/dependency reasons and eight original scopes are preserved."]))
    except BaseException as error:
        with (out / "failure.json").open("x", encoding="utf8") as stream:
            json.dump(dict(error=repr(error), inputs_sha256=pins, deadline=deadline.status(), automatic_retry=False,
                provisional_summary_is_approval=False, target_resolution="NONE"), stream, indent=2)
        raise


if __name__ == "__main__":
    main()

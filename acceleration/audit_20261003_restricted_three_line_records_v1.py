"""SOURCE ONLY: new own-calibration and finite Native raw-controls checker.

There is deliberately no target99/scientific replay mode. The complete raw core
can later support a separately reviewed caller and genuinely fixed graph input.
"""
import argparse
import copy
from dataclasses import replace
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys

import numpy as np
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/audit_20261003_restricted_three_line_records_v1.py"
SPEC = "acceleration/audit_20261003_restricted_three_line_records_v1_spec.md"
CORE = "acceleration/audit_20261003_restricted_three_line_raw_core_v1.py"
SCALAR = "acceleration/audit_20261003_restricted_three_line_core_v2.py"
PRODUCER = "acceleration/census_20261003_root_focused_restricted_three_line_v3.py"
PRODUCER_SPEC = "acceleration/census_20261003_root_focused_restricted_three_line_v3_spec.md"
STATIC = {
    SCALAR: "44cd8135f626420454d155bdd6cebcf2b1a0568e3faf06dfa1bad85f9fe746b2",
    "acceleration/results/20261003_independent_review/restricted_three_line_calibration01/summary.json": "61e29e2964ca8d5e09ea768e3c1d081886049aff875bae4ba7ed0c21fba0e2b5",
    PRODUCER: "493aeace43b91c755c2c038db0ab71fd61f4acbcf62d7a717b07894fb7f0f41e",
    PRODUCER_SPEC: "e2dcded34b2deb6f5eb0c326353487bb741e5b22eae9447d5216902982bc0164",
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command.py": "593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
PRODUCER_SOFTWARE = {
    "acceleration/census_20261003_root_focused_two_line_v1.py": "bbc91ed768a07b302e0e417e8c4415925ef6fac01bd14d78051a56b723419017",
    "acceleration/census_20261003_root_focused_two_line_v1_spec.md": "9b2fcfc0b330b9183a47c0f3888126ef8dfe8a8dbb4d41366c9adf11006cdcc8",
    "acceleration/command_deadline.py": STATIC["acceleration/command_deadline.py"],
    "acceleration/run_compute_command.py": STATIC["acceleration/run_compute_command.py"],
    "acceleration/native_budget_env_v1/pyproject.toml": "96f96d7345153b4bde50d7f4a640a33d43dfd6458c35f4e6a4ab798b11673782",
    "acceleration/native_budget_env_v1/uv.lock": "54ecb16b929dac1035b5a8691df419d58eab33dc3f07c76c5259094e265a4434",
    PRODUCER: STATIC[PRODUCER], PRODUCER_SPEC: STATIC[PRODUCER_SPEC],
}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    with path.open("x", encoding="utf8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False); stream.write("\n")


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def emit_part(core, directory, begin, records, filename=None, raw_override=None):
    target = directory / (filename or f"part_{begin:09d}.jsonl.gz")
    raw = b"".join(core.canonical(r) for r in records) if raw_override is None else raw_override
    with target.open("xb") as stream:
        with gzip.GzipFile(filename="", fileobj=stream, mode="wb", compresslevel=1, mtime=0) as writer:
            writer.write(raw)
    return dict(path=target.relative_to(ROOT).as_posix(), start=begin, end=begin + len(records),
                record_count=len(records), raw_bytes=len(raw), raw_sha256=hashlib.sha256(raw).hexdigest(),
                gzip_bytes=target.stat().st_size, gzip_sha256=sha(target))


def emit_synthetic_run(core, directory, d, records, identity, stop, prefix=None):
    """Crafted protocol fixtures, explicitly labelled synthetic by the caller.

    Literal producer strings inside the closed manifest are schema controls,
    not a claim that Native produced these crafted files.
    """
    directory.mkdir()
    aggregate, parts, cps = core.Aggregate(), [], []
    start = 0
    if prefix is not None:
        start = prefix["completed_proposals"]
        parts = list(prefix["parts"])
        for record in records[:start]:
            aggregate.add(record)
    at = start
    while at < stop:
        end = min(at + 50, stop)
        part = emit_part(core, directory, at, records[at:end]); parts.append(part)
        for record in records[at:end]:
            aggregate.add(record)
        at = end
        cp = directory / f"checkpoint_{at:09d}.json"
        save(cp, dict(schema="FROZEN_ROOT_RESTRICTED_THREE_LINE_CHECKPOINT_V1", identity=identity,
             next_proposal_id=at, parts=parts, aggregate=aggregate.snapshot()))
        cps.append(dict(path=cp.relative_to(ROOT).as_posix(), sha256=sha(cp)))
    if not cps:
        cp = directory / f"checkpoint_{at:09d}.json"
        save(cp, dict(schema="FROZEN_ROOT_RESTRICTED_THREE_LINE_CHECKPOINT_V1", identity=identity,
             next_proposal_id=at, parts=parts, aggregate=aggregate.snapshot()))
        cps.append(dict(path=cp.relative_to(ROOT).as_posix(), sha256=sha(cp)))
    selected = min(aggregate.pair_ties, key=lambda r: r["proposal_id"]) if aggregate.pair_ties else None
    for filename, tied, scope in [("minimum_root_ties.json", aggregate.root_ties,
          "All lambda-preserving proposals tied at minimum R_root among this saved role prefix; mu worsening remains eligible."),
          ("minimum_pair_ties.json", aggregate.pair_ties,
          "All lambda-preserving proposals tied at minimum (R_root,E_mu) among this saved role prefix.")]:
        save(directory / filename, dict(records=tied, scope=scope))
    if selected is not None:
        exact, adj, _ = core.expected_record(d, selected["proposal_id"])
        (directory / "selected_neighbor.adj").write_bytes(core.matrix_bytes(adj))
        b = d["base"]; rows = [list(row) for row in b.rows]
        for key, row in zip(("i", "j", "k"), exact["new_triples"]):
            rows[exact["role"][key]] = row
        save(directory / "selected_neighbor_triples.json", dict(n=b.n, degree=b.degree, root=b.root,
             frozen_rows=[list(row) for row in b.frozen], mutable_labels=list(b.mutable), triples=rows,
             proposal_id=selected["proposal_id"], historical_native_state_written=False))
    b = d["base"]
    value = dict(schema="FROZEN_ROOT_RESTRICTED_THREE_LINE_MANIFEST_V1", identity=identity, universe=d["universe"],
        population=len(records), completed_proposals=stop, starting_proposal_id=start,
        proposals_evaluated_this_invocation=stop - start, parts=parts, checkpoints=cps,
        status="CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK" if stop == len(records) else "UNKNOWN_PREFIX_ONLY",
        budget_stop=False, aggregate=aggregate.snapshot(), selected_proposal_id=None if selected is None else selected["proposal_id"],
        baseline=dict(E_lambda=b.E_lambda, E_mu=b.E_mu, R_root=b.R_root),
        selection_rule="Among valid lambda0 proposals minimize root R, then global E_mu, then role proposal ID; mu worsening remains eligible.",
        producer="/root/native_driver", independent_approval=False, target_resolution="NONE", historical_native_state_written=False,
        limitations=["ONE exact role-labelled CN1/CN3 oriented family on one frozen labelled graph only.",
                    "Not all three-line moves, all root-descent moves, a connected move space, or any target exclusion.",
                    "Incomplete raw prefix cannot establish absence; exact zero still requires independent full99 integer SRG validation."])
    save(directory / "manifest.json", value)
    return value


def scalar_comparison(core, scalar, d, pid, expected, adjacency, cn):
    b = d["base"]
    # Scalar input is independent and immutable to this dense path. The saved
    # calibration implementation's complete products include genuine diagonal.
    old = scalar.restricted_record(d["scalar_domain"], pid)
    core.need(expected["classification"] == old["classification"] and expected["valid"] is old["valid"]
              and expected["invalid_reason"] == old["invalid_reason"], "SCALAR_RECORD_STATUS")
    if not expected["valid"]:
        if expected["conflict_pair"] is not None:
            core.need(expected["conflict_pair"] in old["candidate"]["conflict_pairs"], "SCALAR_CONFLICT_PAIR")
        return
    candidate = old["candidate"]
    core.need(np.array_equal(adjacency, np.asarray(candidate["adjacency"], dtype=np.int64))
              and np.array_equal(cn, np.asarray(candidate["cn"], dtype=np.int64)), "SCALAR_COMPLETE_MATRICES")
    core.need(core.same(expected["new_triples"], candidate["changed_rows"])
              and (expected["new_lambda"], expected["new_mu"], expected["new_root_residual"], expected["root_residual_delta"]) ==
                  (candidate["E_lambda"], candidate["E_mu"], candidate["R_root"], candidate["root_delta"])
              and core.same(expected["changed_root_counts"], candidate["changed_root_counts"]), "SCALAR_COMPLETE_SCORES")
    scalar_edges = [[x, y] for x, y in __import__("itertools").combinations(range(b.n), 2)
                    if int(adjacency[x, y]) != int(b.adjacency[x, y])]
    core.need(core.same(expected["toggles"], scalar_edges), "SCALAR_COMPLETE_TOGGLES")


def calibration(core, scalar, out, reserve):
    save(out / "SYNTHETIC_PROTOCOL_FIXTURE_PROVENANCE.json", dict(author="/root/structural",
         producer_raw_outputs_read=False, purpose="Crafted Native-format protocol controls only; literal producer strings are test data, not an execution identity.",
         actual99_input_read=False, scientific_census=False))
    controls, populations, first_valid, models = [], {}, None, {}
    def reject(label, stage, call, raw=None):
        reserve()
        if raw is not None:
            save(out / (label + "_input.json"), raw)
        try:
            call()
        except core.AuditError as error:
            core.need(error.stage == stage, "CONTROL_STAGE", label + " got " + error.stage)
            controls.append(dict(case=label, expected_stage=stage, actual_stage=error.stage, diagnostic=str(error), outcome="REJECTED"))
            return
        raise core.AuditError("CONTROL_ACCEPTED", label)
    for name, fixture in scalar.fixtures().items():
        reserve()
        b = core.fixed_input(**fixture)
        d = core.domain(b)
        sb = scalar.base_graph(**fixture); sd = scalar.restricted_domain(sb)
        core.need(core.same(d["roles"], sd["roles"]), "SCALAR_COMPLETE_ROLE_UNIVERSE")
        d["scalar_domain"] = sd
        rows, counts = [], {}
        for pid in range(len(d["roles"])):
            if pid % 32 == 0:
                reserve()
            exact, adj, cn = core.expected_record(d, pid)
            scalar_comparison(core, scalar, d, pid, exact, adj, cn)
            rows.append(exact); counts[exact["classification"]] = counts.get(exact["classification"], 0) + 1
            if exact["valid"] and first_valid is None:
                first_valid = (d, pid, exact)
        save(out / (name + ".json"), fixture)
        identity = dict(synthetic_control_author="/root/structural", literal_input=fixture,
                        mathematical_scope="Finite crafted protocol model only", universe=d["universe"])
        whole = emit_synthetic_run(core, out / (name + "_whole"), d, rows, identity, len(rows))
        prefix = emit_synthetic_run(core, out / (name + "_prefix17"), d, rows, identity, min(17, len(rows)))
        resumed = emit_synthetic_run(core, out / (name + "_resumed"), d, rows, identity, len(rows), prefix)
        for suffix, model in (("whole", whole), ("prefix17", prefix), ("resumed", resumed)):
            result = core.audit_run(ROOT, out, d, model, identity, reserve)
            core.audit_ties(out / (name + "_" + suffix), d, result)
        core.need(core.same(whole["aggregate"], resumed["aggregate"]), "SYNTHETIC_WHOLE_RESUME")
        populations[name] = dict(n=b.n, role_population=len(rows), classifications=counts,
             complete_scalar_role_cross_checks=len(rows), dense_graph_check_unit="all adjacency and true A^2 cells of every valid role",
             whole_prefix_resume_replays=3)
        models[name] = (d, identity, whole)
    core.need(sum(x["role_population"] for x in populations.values()) == 4032 and first_valid is not None, "CONTROL_POPULATION")
    d, pid, exact = first_valid
    save(out / "known_complete_19_field_record.json", exact)
    changes = {
        "schema": lambda v: v.update(schema="WRONG"), "proposal_id": lambda v: v.update(proposal_id=True),
        "role": lambda v: v["role"].update(u=-1), "old_triples": lambda v: v["old_triples"][0].reverse(),
        "new_triples": lambda v: v["new_triples"][0].__setitem__(0, -1), "valid": lambda v: v.update(valid=1),
        "invalid_reason": lambda v: v.update(invalid_reason="WRONG"), "conflict_pair": lambda v: v.update(conflict_pair=[0, 1]),
        "toggles": lambda v: v["toggles"].pop(), "changed_root_counts": lambda v: v["changed_root_counts"].pop(),
        "delta_lambda": lambda v: v.update(delta_lambda=False), "delta_mu": lambda v: v.update(delta_mu=v["delta_mu"] + 1),
        "new_lambda": lambda v: v.update(new_lambda=v["new_lambda"] + 1), "new_mu": lambda v: v.update(new_mu=True),
        "new_root_residual": lambda v: v.update(new_root_residual=v["new_root_residual"] + 1),
        "root_residual_delta": lambda v: v.update(root_residual_delta=-4),
        "frozen_root_unchanged": lambda v: v.update(frozen_root_unchanged=1),
        "classification": lambda v: v.update(classification="WRONG"), "mu_direction": lambda v: v.update(mu_direction="WRONG")}
    for key, mutate in changes.items():
        bad = copy.deepcopy(exact); mutate(bad)
        reject("record_" + key, core.FIELD_STAGES[key], lambda v=bad: core.check_record(d, pid, v), bad)
    bad = copy.deepcopy(exact); bad["extra"] = 0
    reject("record_extra", "RECORD_SCHEMA", lambda: core.check_record(d, pid, bad), bad)
    lifted, identity, whole = models["doily_two_lift30"]
    part = whole["parts"][0]
    for label, key, value, stage in [
        ("part_start_bool", "start", False, "PART_TYPES"), ("part_end_float", "end", float(part["end"]), "PART_TYPES"),
        ("part_count_bool", "record_count", True, "PART_TYPES"), ("part_rawbytes_float", "raw_bytes", float(part["raw_bytes"]), "PART_TYPES"),
        ("part_path_parent", "path", "acceleration/../bad", "ARTIFACT_PATH"),
        ("part_path_absolute", "path", "C:/private/input", "ARTIFACT_PATH"),
        ("part_path_backslash", "path", "acceleration\\bad", "ARTIFACT_PATH"),
        ("part_gzip_hash", "gzip_sha256", "0" * 64, "PART_COMPRESSED_HASH"),
        ("part_raw_hash", "raw_sha256", "0" * 64, "PART_RAW_HASH")]:
        value_part = copy.deepcopy(part); value_part[key] = value
        reject(label, stage, lambda p=value_part: core.part_records(ROOT, out, p), value_part)
    shifted = copy.deepcopy(part); shifted["start"] += 1; shifted["end"] += 1
    reject("part_shifted_ids", "PART_SEQUENCE", lambda: core.part_records(ROOT, out, shifted), shifted)
    raw_records = core.part_records(ROOT, out, part)
    malformed = []
    malformed.append(("part_missing_lf", b"".join(core.canonical(r) for r in raw_records)[:-1], "PART_LENGTH"))
    for name, value in (("part_duplicate_id", 1), ("part_boolean_id", False), ("part_float_id", 0.0)):
        changed = copy.deepcopy(raw_records); changed[0]["proposal_id"] = value
        malformed.append((name, b"".join(core.canonical(r) for r in changed), "PART_SEQUENCE"))
    malformed.append(("part_noncanonical", b" " + b"".join(core.canonical(r) for r in raw_records), "PART_CANONICAL_JSON"))
    malformed.append(("part_duplicate_key", b'{"proposal_id":0,"proposal_id":0}\n' + b"".join(core.canonical(r) for r in raw_records[1:]), "JSON"))
    for label, raw, stage in malformed:
        p = emit_part(core, out, 0, raw_records, label + ".jsonl.gz", raw)
        reject(label, stage, lambda value=p: core.part_records(ROOT, out, value), p)
    cp_value = core.strict_json((ROOT / whole["checkpoints"][0]["path"]).read_bytes())
    end, cp_parts, cp_snapshot = cp_value["next_proposal_id"], cp_value["parts"], cp_value["aggregate"]
    cp_changes = [
        ("checkpoint_boolean_id", "CHECKPOINT_TYPES", lambda v: v.update(next_proposal_id=False)),
        ("checkpoint_float_id", "CHECKPOINT_TYPES", lambda v: v.update(next_proposal_id=float(end))),
        ("checkpoint_extra", "CHECKPOINT_TYPES", lambda v: v.update(extra=0)),
        ("checkpoint_identity", "CHECKPOINT_IDENTITY", lambda v: v["identity"].update(extra=0)),
        ("checkpoint_parts", "CHECKPOINT_PREFIX", lambda v: v.update(parts=[])),
        ("checkpoint_aggregate", "CHECKPOINT_AGGREGATE", lambda v: v["aggregate"].update(unique_valid_neighbor_graphs=-1)),
        ("checkpoint_boolean_count", "CHECKPOINT_AGGREGATE", lambda v: v["aggregate"].update(unique_valid_neighbor_graphs=False)),
        ("checkpoint_float_count", "CHECKPOINT_AGGREGATE", lambda v: v["aggregate"].update(unique_valid_neighbor_graphs=float(cp_snapshot["unique_valid_neighbor_graphs"]))),
        ("checkpoint_shifted_id", "CHECKPOINT_PREFIX", lambda v: v.update(next_proposal_id=end + 1))]
    for label, stage, mutate in cp_changes:
        v = copy.deepcopy(cp_value); mutate(v)
        reject(label, stage, lambda value=v: core.checkpoint(value, identity, cp_parts, end, cp_snapshot), v)
    for label, raw in (("json_duplicate", b'{"a":1,"a":2}'), ("json_nonfinite", b'{"a":NaN}'), ("json_syntax", b'{')):
        reject(label, "JSON", lambda value=raw: core.strict_json(value))
    b = d["base"]
    writable = replace(b, adjacency=b.adjacency.copy())
    reject("base_writable", "BASE_IMMUTABILITY", lambda: core.unchanged(writable))
    altered = b.adjacency.copy(); altered[0, 0] = 1; altered.setflags(write=False)
    changed_base = replace(b, adjacency=altered)
    reject("base_cell_mutation", "BASE_IMMUTABILITY", lambda: core.unchanged(changed_base))
    changed_type = replace(b, degree=True)
    reject("base_type_mutation", "BASE_IMMUTABILITY", lambda: core.unchanged(changed_type))
    rook = core.domain(core.fixed_input(**scalar.fixtures()["rook9"]))
    native = core.native_cache(rook)
    core.check_native_cache(rook, native)
    core.need(all(native["base"]["cn"][x][x] == 0 and int(rook["base"].cn[x, x]) == 4 for x in range(9)), "LEGACY_DIAGONAL_ADAPTER")
    adapter_changes = [
        ("legacy_CN_diag_boolean", "CN_CACHE", lambda v: v["base"]["cn"][0].__setitem__(0, False)),
        ("legacy_CN_diag_float", "CN_CACHE", lambda v: v["base"]["cn"][0].__setitem__(0, 0.0)),
        ("legacy_CN_true_diagonal", "CN_CACHE", lambda v: v["base"]["cn"][0].__setitem__(0, 4)),
        ("legacy_CN_one_boolean", "CN_CACHE", lambda v: v["base"]["cn"][0].__setitem__(1, True)),
        ("legacy_CN_one_float", "CN_CACHE", lambda v: v["base"]["cn"][0].__setitem__(1, 1.0)),
        ("legacy_E_lambda_boolean", "ENERGY_CACHE", lambda v: v["base"].update(lambda_energy=False)),
        ("legacy_E_lambda_float", "ENERGY_CACHE", lambda v: v["base"].update(lambda_energy=0.0)),
        ("legacy_mask_boolean", "ADJ_CACHE", lambda v: v["base"]["masks"].__setitem__(0, False)),
        ("legacy_mask_float", "ADJ_CACHE", lambda v: v["base"]["masks"].__setitem__(0, float(v["base"]["masks"][0])))]
    for label, stage, mutate in adapter_changes:
        altered = copy.deepcopy(native); mutate(altered)
        reject(label, stage, lambda value=altered: core.check_native_cache(rook, value), altered)
    reject("score_unsigned8", "SCORE_DOMAIN", lambda: core.score(rook["base"].adjacency.astype(np.uint8), 0))
    reject("score_float64", "SCORE_DOMAIN", lambda: core.score(rook["base"].adjacency.astype(np.float64), 0))
    core.need(len(controls) == 62, "CONTROL_POPULATION", "20 record+16 part+9 checkpoint+3 JSON+3 immutability+9 legacyadapter+2 dtype")
    # Complete synthetic n99 multiplication boundary; no actual99 graph read.
    nine = scalar.fixtures()["rook9"]["rows"]
    rows99 = [[x + 9 * block for x in row] for block in range(11) for row in nine]
    synthetic99 = core.fixed_input(99, 2, rows99, 0)
    reference = scalar.dense_score(synthetic99.adjacency.tolist(), 0)
    core.need(np.array_equal(synthetic99.cn, np.asarray(reference["cn"], dtype=np.int64))
              and (synthetic99.E_lambda, synthetic99.E_mu, synthetic99.R_root) ==
                  (reference["E_lambda"], reference["E_mu"], reference["R_root"]), "SYNTHETIC99_COMPLETE_PRODUCT")
    save(out / "synthetic99_product.json", dict(source="Eleven disjoint literal rook9 blocks; pointdegree2, nottargetdegree7",
         rows=rows99, cn=synthetic99.cn.tolist(), E_lambda=synthetic99.E_lambda, E_mu=synthetic99.E_mu, R_root=synthetic99.R_root))
    save(out / "strict_negative_controls.json", controls)
    return dict(populations=populations, complete_scalar_role_cross_checks=4032, complete_raw_model_fields=19,
                strict_negative_count=62, strict_negative_controls=controls, synthetic_whole_prefix_resume_fixture_equalities=3,
                synthetic99_product_cells=9801, actual99_input_read=False, producer_raw_outputs_read=False,
                future_target_replay_authorized=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["calibration"])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seconds", type=float, required=True)
    ap.add_argument("--self-sha256", required=True); ap.add_argument("--core-sha256", required=True)
    ap.add_argument("--spec-sha256", required=True); ap.add_argument("--source-commit", required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="New finite raw19field dense-int64 checker calibration; complete4032 scalar cross-checks, syntheticwhole-prefix-resume/parts/CP and62 strictcontrols, nottargetreplay")
    pins = dict(STATIC); pins.update({SELF: args.self_sha256, CORE: args.core_sha256, SPEC: args.spec_sha256})
    out = args.out.resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        raise ValueError("OUTPUT_PATH: fresh workspace output")
    out.mkdir(parents=True)
    def reserve():
        if deadline.status()["remaining_seconds"] <= 20 or deadline.status()["stop_required"]:
            raise ValueError("DEADLINE: orderly save reserve; not completed within allocated budget")
    try:
        for path, identity in pins.items():
            reserve()
            if sha(ROOT / path) != identity:
                raise ValueError("SOURCE_IDENTITY: " + path)
        if np.__version__ != "2.5.3":
            raise ValueError("DEPENDENCY_VERSION: numpy2.5.3")
        core = module(CORE, "independent_restricted_raw_core_v1")
        scalar = module(SCALAR, "independent_restricted_scalar_v2")
        result = calibration(core, scalar, out, reserve)
        outputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in out.rglob("*") if p.is_file()}
        save(out / "summary.json", dict(status="INDEPENDENT_RESTRICTED_THREE_LINE_RAW_V1_CHECKER_CALIBRATION_PASS",
             verifier="/root/structural", method="finite_checker_calibration", target_resolution="NONE", new_exclusions=0,
             timestamp=datetime.now(timezone.utc).isoformat(), source_commit=args.source_commit,
             command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), numpy=np.__version__,
             inputs_sha256=pins, outputs_sha256=outputs, result=result, deadline=deadline.status(),
             shared_components=["Unchanged independent scalarcore44cd for literal fixtures and complete finite cross-checks only; no producer imports.",
                                "Locked NumPy2.5.3 exactint64 A@A; Python JSON/gzip/SHA256/deadline; integer coefficient bounds checked."],
             limitations=["Finite own-calibration only; no Native raw artifacts independently approved.",
                          "No actual99 scientific input/read/replay, target exclusion, performance/ergodicity or target result.",
                          "No scientific CLI; prospective Native rawcontrols caller needs a new source and separate ROOT review."]))
        print(json.dumps(dict(status="INDEPENDENT_RESTRICTED_THREE_LINE_RAW_V1_CHECKER_CALIBRATION_PASS", roles=4032, strict_negative_controls=62)))
    except Exception as error:
        if not (out / "failure.json").exists():
            save(out / "failure.json", dict(status="UNKNOWN_FAILED_OR_INCOMPLETE", timestamp=datetime.now(timezone.utc).isoformat(),
                 error=repr(error), inputs_sha256=pins, deadline=deadline.status(), automatic_retry=False,
                 restart="Preserve every artifact; source or invocation correction needs fresh version/review/authorization.",
                 unmet_requirements=["Complete finite calibration", "No Native raw artifact gate or scientific replay has been established."]))
        raise


if __name__ == "__main__":
    main()

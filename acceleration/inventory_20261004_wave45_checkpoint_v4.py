"""Read-only config-frozen publication identity inventory and staged identity check; no math replay."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

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
CAL_STATUS = "WAVE45_EXPLICIT_PUBLICATION_INVENTORY_V4_CALIBRATION_PASS"
MAX_MEMBER = 50 * 1024**2
CONTROL_COUNTS = {"positive": 10, "negative": 29, "total": 39}


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def tick(deadline):
    value = deadline.status()
    need(not value["stop_required"] and value["remaining_seconds"] > 20, "SAVE_RESERVE")
    return value


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "JSON_DUPLICATE")
            result[key] = value
        return result
    def constant(_):
        raise ValueError("JSON_NONFINITE")
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("JSON_SYNTAX") from None


def save(path, value, deadline):
    tick(deadline)
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    need(len(raw) <= MAX_MEMBER, "OUTPUT_JSON_BOUND")
    path.write_bytes(raw)
    tick(deadline)


def valid_path(name):
    need(type(name) is str and name and name.isascii() and "\\" not in name and ":" not in name
         and not any(ord(c) < 32 for c in name) and not name.startswith("/")
         and all(p not in ("", ".", "..") for p in name.split("/")), "PATH_SCOPE")
    parts = PurePosixPath(name).parts
    need(not any(p.lower() in (".git", ".codex", ".venv", "build", "private", "__pycache__", "node_modules")
                 or p.lower().startswith(".env") for p in parts), "PATH_PRIVATE")
    need(PurePosixPath(name).suffix.lower() not in (".drat", ".proof", ".cnf", ".exe", ".dll", ".pyd"), "PATH_PROOF")
    return name


def safe(name):
    path = ROOT / valid_path(name)
    for part in (path, *path.parents):
        if part.exists():
            info = part.lstat()
            need(not part.is_symlink() and not getattr(info, "st_file_attributes", 0) & 0x400, "PATH_REPARSE")
        if part == ROOT:
            break
    need(path.resolve().is_relative_to(ROOT), "PATH_SCOPE")
    return path


def hash_file(path, deadline, maximum=MAX_MEMBER, collect=False):
    tick(deadline)
    need(path.is_file(), "MEMBER_MISSING")
    before = path.stat()
    need(before.st_size <= maximum, "MEMBER_BOUND")
    sha, git, blocks = hashlib.sha256(), hashlib.sha1(), []
    git.update(("blob %d\0" % before.st_size).encode("ascii"))
    with path.open("rb") as handle:
        while True:
            tick(deadline)
            block = handle.read(1024**2)
            if not block:
                break
            sha.update(block)
            git.update(block)
            if collect:
                blocks.append(block)
    after = path.stat()
    need(before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns, "MEMBER_CHANGED")
    result = {"sha256": sha.hexdigest(), "bytes": before.st_size, "working_raw_git_blob_oid": git.hexdigest(),
              "mtime_ns": after.st_mtime_ns}
    if collect:
        result["authenticated_bytes"] = b"".join(blocks)
    return result


class Reader:
    def __init__(self, deadline):
        self.deadline, self.pins = deadline, {}

    def read(self, name, digest, parsed=False, raw=False):
        need(not (parsed and raw), "READER_MODE")
        need(type(digest) is str and re.fullmatch("[0-9a-f]{64}", digest), "SHA_TYPE")
        path = safe(name)
        observed = hash_file(path, self.deadline, collect=parsed or raw)
        need(observed["sha256"] == digest, "INPUT_SHA")
        need(name not in self.pins or self.pins[name] == digest, "INPUT_IDENTITY")
        self.pins[name] = digest
        authenticated = observed.get("authenticated_bytes")
        tick(self.deadline)
        return decode(authenticated) if parsed else authenticated if raw else None

    def mapping(self, values):
        need(type(values) is dict and values, "INPUT_MAP")
        for name, digest in values.items():
            self.read(name, digest)

    def closing(self):
        for name, digest in list(self.pins.items()):
            self.read(name, digest)


def selected_paths(raw):
    need(type(raw) is bytes and raw.endswith(b"\0"), "SELECTED_NUL")
    try:
        names = raw[:-1].decode("utf-8").split("\0")
    except UnicodeDecodeError:
        raise ValueError("SELECTED_UTF8") from None
    need(names and all(names), "SELECTED_EMPTY")
    need(len(names) == len(set(names)), "SELECTED_UNIQUE")
    need(names == sorted(names), "SELECTED_ORDER")
    for name in names:
        valid_path(name)
    return names


def manifest(raw, names, expected, known_sizes=True):
    schema = "WAVE45_CHECKPOINT_READ_ONLY_PUBLICATION_CLOSURE_V5" if known_sizes else "WAVE45_EXPLICIT_PUBLICATION_IDENTITY_MANIFEST_V1"
    need(type(raw) is dict and raw.get("schema") == schema, "MANIFEST_SCHEMA")
    need(type(raw.get("safe_selected_distinct")) is int and raw["safe_selected_distinct"] == expected
         and type(raw.get("selected")) is list and len(raw["selected"]) == expected, "MANIFEST_COUNT")
    rows = raw["selected"]
    for row in rows:
        need(type(row) is dict and type(row.get("path")) is str, "MANIFEST_ROW")
        valid_path(row["path"])
        need((type(row.get("bytes")) is int and 0 <= row["bytes"] <= MAX_MEMBER)
             if known_sizes else "bytes" in row and row["bytes"] is None, "MANIFEST_BYTES")
        hashes = row.get("declared_sha256")
        need(type(hashes) is list and len(hashes) == 1 and type(hashes[0]) is str
             and re.fullmatch("[0-9a-f]{64}", hashes[0]) is not None, "MANIFEST_SHA")
    need(len({row["path"] for row in rows}) == expected, "MANIFEST_PATH_DUPLICATE")
    rows = sorted(rows, key=lambda row: row["path"])
    need([row["path"] for row in rows] == names, "SELECTED_MANIFEST")
    need((type(raw.get("selected_bytes")) is int and raw["selected_bytes"] == sum(row["bytes"] for row in rows))
         if known_sizes else "selected_bytes" in raw and raw["selected_bytes"] is None, "MANIFEST_TOTAL_BYTES")
    return rows


def member(row, deadline):
    observed = hash_file(safe(row["path"]), deadline)
    need(row["bytes"] is None or observed["bytes"] == row["bytes"], "MEMBER_BYTES")
    need(observed["sha256"] == row["declared_sha256"][0], "MEMBER_SHA")
    return {"path": row["path"], "declared_sha256": row["declared_sha256"][0], **observed}


def blob_identity(observed, tracked, require=False):
    matches = tracked is not None and tracked["index_blob_oid"] == observed["working_raw_git_blob_oid"]
    need(not require or matches, "GIT_BLOB_IDENTITY")
    return matches


def git_read(argv, deadline):
    remaining = tick(deadline)["remaining_seconds"] - 20
    result = subprocess.run(["git", *argv], cwd=ROOT, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=min(60, remaining))
    tick(deadline)
    need(type(result.returncode) is int and result.returncode == 0, "GIT_READ_EXIT")
    return result.stdout


def index_rows(raw, selected):
    need(type(raw) is bytes and (not raw or raw.endswith(b"\0")), "GIT_INDEX_NUL")
    entries, seen, gitlinks, outside = {}, set(), 0, []
    for item in raw.split(b"\0")[:-1]:
        try:
            prefix, name = item.split(b"\t", 1)
            mode, oid, stage = prefix.decode("ascii").split(" ")
            name = name.decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            raise ValueError("GIT_INDEX_ROW") from None
        need(re.fullmatch("[0-7]{6}", mode) and re.fullmatch("[0-9a-f]{40}", oid)
             and stage in ("0", "1", "2", "3"), "GIT_INDEX_ROW")
        need((name, stage) not in seen, "GIT_DUPLICATE")
        seen.add((name, stage))
        gitlinks += mode == "160000" and stage == "0"
        if name in selected:
            need(stage == "0", "GIT_SELECTED_STAGE")
            need(mode in ("100644", "100755"), "GIT_SELECTED_MODE")
            entries[name] = {"index_mode": mode, "index_blob_oid": oid}
        else:
            outside.append(item)
    outside_digest = hashlib.sha256(b"\0".join(sorted(outside)) + (b"\0" if outside else b"")).hexdigest()
    return {"selected": entries, "whole_index_rows": len(seen), "unselected_gitlinks": gitlinks,
            "unselected_index_rows": len(outside), "unselected_index_identity_sha256": outside_digest}


def unselected_stability(index, basis):
    need(type(basis) is dict and all(type(basis.get(k)) is type(index[k]) and index[k] == basis[k]
         for k in ("unselected_index_rows", "unselected_index_identity_sha256", "unselected_gitlinks")), "UNSELECTED_INDEX_CHANGED")
    return {k: index[k] for k in ("unselected_index_rows", "unselected_index_identity_sha256", "unselected_gitlinks")}


def protected(deadline):
    head = git_read(["rev-parse", "HEAD"], deadline).decode("ascii").strip()
    need(re.fullmatch("[0-9a-f]{40}", head), "HEAD_IDENTITY")
    index_name = git_read(["rev-parse", "--git-path", "index"], deadline).decode("utf-8").strip()
    index = Path(index_name)
    if not index.is_absolute():
        index = ROOT / index
    need(index.resolve().is_relative_to(ROOT / ".git") and not index.is_symlink(), "INDEX_SCOPE")
    return {"head": head, "index_sha256": hash_file(index, deadline)["sha256"],
            "ledger_sha256": hash_file(safe("CLAIMS.yaml"), deadline)["sha256"]}


def controls(out, deadline):
    abc, empty = out / "fixture_abc.txt", out / "fixture_empty.log"
    abc.write_bytes(b"abc")
    empty.write_bytes(b"")
    digest = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    names = ["docs/a.txt", "docs/b.txt"]
    raw = {"schema": "WAVE45_CHECKPOINT_READ_ONLY_PUBLICATION_CLOSURE_V5", "safe_selected_distinct": 2,
           "selected_bytes": 6, "selected": [{"path": name, "bytes": 3, "declared_sha256": [digest]} for name in names]}
    abc_row = {"path": abc.relative_to(ROOT).as_posix(), "bytes": 3, "declared_sha256": [digest]}
    empty_row = {"path": empty.relative_to(ROOT).as_posix(), "bytes": 0,
                 "declared_sha256": ["e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"]}
    rows = []
    def run(name, stage, payload, action):
        index = len(rows)
        save(out / ("control_%03d.json" % index), payload, deadline)
        try:
            result, actual = action(payload), "PASS"
        except ValueError as exc:
            if str(exc) == "SAVE_RESERVE":
                raise
            result, actual = None, str(exc)
        record = {"index": index, "name": name, "expected_stage": stage, "actual_stage": actual, "matches": stage == actual}
        rows.append(record)
        save(out / ("stage_%03d.json" % index), record, deadline)
        if stage == "PASS":
            save(out / ("result_%03d.json" % index), result, deadline)
        need(actual == stage, "CONTROL_STAGE:" + name + ":" + actual)
    def damage(name, stage, action):
        changed = copy.deepcopy(raw)
        action(changed)
        run(name, stage, changed, lambda value: manifest(value, names, 2))
    nul = lambda value: selected_paths(bytes.fromhex(value))
    run("canonical_nul", "PASS", b"docs/a.txt\0docs/b.txt\0".hex(), nul)
    run("complete_two_manifest", "PASS", raw, lambda value: manifest(value, names, 2))
    run("known_abc_hash", "PASS", abc_row, lambda value: member(value, deadline))
    run("empty_closed_log_hash", "PASS", empty_row, lambda value: member(value, deadline))
    index = ("100644 " + "0" * 40 + " 0\tdocs/a.txt\0" + "160000 " + "1" * 40 + " 0\tvendor/example\0").encode()
    run("selected_index_unselected_gitlink", "PASS", index.hex(), lambda value: index_rows(bytes.fromhex(value), set(names)))
    run("safe_gitignore", "PASS", ".gitignore", valid_path)
    for name, stage, data in (("nul_terminator", "SELECTED_NUL", b"docs/a.txt"),
            ("nul_duplicate", "SELECTED_UNIQUE", b"docs/a.txt\0docs/a.txt\0"),
            ("nul_order", "SELECTED_ORDER", b"docs/b.txt\0docs/a.txt\0"),
            ("nul_utf8", "SELECTED_UTF8", b"\xff\0"), ("nul_empty", "SELECTED_EMPTY", b"docs/a.txt\0\0")):
        run(name, stage, data.hex(), nul)
    for name, stage, value in (("parent_path", "PATH_SCOPE", "../x"), ("git_path", "PATH_PRIVATE", ".git/index"),
            ("environment_path", "PATH_PRIVATE", "docs/.env"), ("build_path", "PATH_PRIVATE", "build/x"),
            ("proof_path", "PATH_PROOF", "docs/x.drat")):
        run(name, stage, value, valid_path)
    damage("manifest_count_bool", "MANIFEST_COUNT", lambda value: value.__setitem__("safe_selected_distinct", True))
    damage("late_bytes_bool", "MANIFEST_BYTES", lambda value: value["selected"][1].__setitem__("bytes", True))
    damage("late_sha_bool", "MANIFEST_SHA", lambda value: value["selected"][1].__setitem__("declared_sha256", [True]))
    damage("late_conflicting_hashes", "MANIFEST_SHA", lambda value: value["selected"][1].__setitem__("declared_sha256", [digest, "0" * 64]))
    damage("manifest_path_difference", "SELECTED_MANIFEST", lambda value: value["selected"][1].__setitem__("path", "docs/c.txt"))
    bad = copy.deepcopy(abc_row)
    bad["declared_sha256"] = ["0" * 64]
    run("member_hash_mismatch", "MEMBER_SHA", bad, lambda value: member(value, deadline))
    run("raw_blob_mismatch", "GIT_BLOB_IDENTITY", {"index_blob_oid": "0" * 40},
        lambda value: blob_identity(member(abc_row, deadline), value, True))
    bad = copy.deepcopy(abc_row)
    bad["bytes"] = 2
    run("member_size_mismatch", "MEMBER_BYTES", bad, lambda value: member(value, deadline))
    damage("late_member_bound", "MANIFEST_BYTES", lambda value: value["selected"][1].__setitem__("bytes", MAX_MEMBER + 1))
    run("selected_gitlink", "GIT_SELECTED_MODE", index.replace(b"100644", b"160000").hex(), lambda value: index_rows(bytes.fromhex(value), set(names)))
    run("selected_unmerged", "GIT_SELECTED_STAGE", index.replace(b" 0\tdocs", b" 1\tdocs").hex(), lambda value: index_rows(bytes.fromhex(value), set(names)))
    run("index_duplicate", "GIT_DUPLICATE", (index + index.split(b"\0", 1)[0] + b"\0").hex(), lambda value: index_rows(bytes.fromhex(value), set(names)))
    bad = copy.deepcopy(abc_row)
    bad["path"] = (out / "absent_member.txt").relative_to(ROOT).as_posix()
    run("missing_member", "MEMBER_MISSING", bad, lambda value: member(value, deadline))
    fixture_json, fixture_nul, fixture_duplicate = out / "fixture_reader.json", out / "fixture_reader.paths0", out / "fixture_reader_duplicate.json"
    fixture_json.write_bytes(b'{"x":1}')
    fixture_nul.write_bytes(b"docs/a.txt\0docs/b.txt\0")
    fixture_duplicate.write_bytes(b'{"x":1,"x":2}')
    fixture_reader = Reader(deadline)
    fixture_names = [path.relative_to(ROOT).as_posix() for path in (fixture_json, fixture_nul, fixture_duplicate)]
    fixture_hashes = [hashlib.sha256(value).hexdigest() for value in (b'{"x":1}', b"docs/a.txt\0docs/b.txt\0", b'{"x":1,"x":2}')]
    def authenticated_helper(payload):
        value = fixture_reader.read(payload["json_path"], payload["json_sha"], parsed=True)
        paths = selected_paths(fixture_reader.read(payload["nul_path"], payload["nul_sha"], raw=True))
        need(value == {"x": 1} and paths == names, "AUTHENTICATED_HELPER_VALUE")
        return {"json": value, "selected_paths": paths, "same_hashed_bytes_decoded": True}
    run("authenticated_json_and_nul_helper", "PASS", {"json_path": fixture_names[0], "json_sha": fixture_hashes[0],
        "nul_path": fixture_names[1], "nul_sha": fixture_hashes[1]}, authenticated_helper)
    run("authenticated_reader_wrong_sha", "INPUT_SHA", {"path": fixture_names[0], "sha": "0" * 64},
        lambda payload: fixture_reader.read(payload["path"], payload["sha"], parsed=True))
    run("authenticated_parser_duplicate", "JSON_DUPLICATE", {"path": fixture_names[2], "sha": fixture_hashes[2]},
        lambda payload: fixture_reader.read(payload["path"], payload["sha"], parsed=True))
    reversed_manifest = copy.deepcopy(raw)
    reversed_manifest["selected"].reverse()
    run("reversed_manifest_exact_bijection", "PASS", reversed_manifest,
        lambda value: manifest(value, names, 2))
    duplicate_manifest = copy.deepcopy(raw)
    duplicate_manifest["selected"][1]["path"] = names[0]
    run("duplicated_manifest_path", "MANIFEST_PATH_DUPLICATE", duplicate_manifest,
        lambda value: manifest(value, names, 2))
    current = copy.deepcopy(raw)
    current["schema"] = "WAVE45_EXPLICIT_PUBLICATION_IDENTITY_MANIFEST_V1"
    current["selected_bytes"] = None
    for row in current["selected"]:
        row["bytes"] = None
    def hash_only_helper(value):
        checked = manifest(value, names, 2, False)
        unknown_size_row = {**abc_row, "bytes": None}
        observed = member(unknown_size_row, deadline)
        need(observed["bytes"] == 3 and observed["declared_sha256"] == digest, "HASH_ONLY_HELPER_VALUE")
        return {"manifest": checked, "actual_known_abc_member": observed}
    run("hash_only_union_manifest", "PASS", current, hash_only_helper)
    bad = copy.deepcopy(current)
    bad["selected"][1]["bytes"] = True
    run("hash_only_manifest_bytes_bool", "MANIFEST_BYTES", bad, lambda value: manifest(value, names, 2, False))
    bad = copy.deepcopy(current)
    bad["selected_bytes"] = 6
    run("hash_only_manifest_total_alias", "MANIFEST_TOTAL_BYTES", bad, lambda value: manifest(value, names, 2, False))
    original_index = index_rows(index, set(names))
    run("same_unselected_gitlink_identity", "PASS", original_index,
        lambda value: unselected_stability(index_rows(index, set(names)), value))
    altered_index = index_rows(index.replace(b"1" * 40, b"2" * 40), set(names))
    run("changed_unselected_gitlink_oid", "UNSELECTED_INDEX_CHANGED", altered_index,
        lambda value: unselected_stability(index_rows(index, set(names)), value))
    need(len(rows) == 39 and sum(row["expected_stage"] == "PASS" for row in rows) == 10, "CONTROL_POPULATION")
    save(out / "controls.json", rows, deadline)
    return {**CONTROL_COUNTS, "stage_mismatches": [], "actual_selected_input_read": False, "git_calls": 0}


def inventory(reader, config, out, software, staged=False):
    need(type(config) is dict and config.get("schema") == "WAVE45_EXPLICIT_PUBLICATION_INVENTORY_CONFIGURATION_V4", "CONFIG_SCHEMA")
    need(config.get("operation") == ("staged" if staged else "inventory"), "CONFIG_OPERATION")
    expected_count = config.get("selected_distinct")
    need(type(expected_count) is int and expected_count > 0 and type(config.get("frozen_claims")) is int
         and config["frozen_claims"] > 0 and type(config.get("new_claims")) is int
         and 0 <= config["new_claims"] <= config["frozen_claims"], "CONFIG_POPULATION")
    closure_path, closure_sha = config.get("manifest_path"), config.get("manifest_sha256")
    selected_path, selected_sha = config.get("selected_path"), config.get("selected_sha256")
    valid_path(closure_path)
    valid_path(selected_path)
    required = {**software, closure_path: closure_sha, selected_path: selected_sha}
    need(type(config.get("inputs_sha256")) is dict and all(config["inputs_sha256"].get(p) == h for p, h in required.items()), "CONFIG_PINS")
    reader.mapping(config["inputs_sha256"])
    cal = reader.read(config["calibration_path"], config["calibration_sha256"], True)
    need(cal.get("status") == CAL_STATUS and cal.get("mode") == "calibrate"
         and type(cal.get("implementation_version")) is int and cal["implementation_version"] == 4
         and cal.get("source_software") == software
         and type(cal.get("outcome")) is dict and all(type(cal["outcome"].get(k)) is int and cal["outcome"][k] == v for k, v in CONTROL_COUNTS.items()), "CALIBRATION_GATE")
    need(config["inputs_sha256"].get(config["calibration_path"]) == config["calibration_sha256"], "CALIBRATION_PIN")
    cal_outputs = cal.get("outputs_sha256")
    need(type(cal_outputs) is dict and len(cal_outputs) == 94 and "controls.json" in cal_outputs, "CALIBRATION_POPULATION")
    cal_base = PurePosixPath(config["calibration_path"]).parent
    need({p.name for p in safe(config["calibration_path"]).parent.iterdir()} == set(cal_outputs) | {"summary.json"},
         "CALIBRATION_DIRECTORY")
    for filename, digest in cal_outputs.items():
        need(type(filename) is str and PurePosixPath(filename).name == filename, "CALIBRATION_FILENAME")
        reader.read((cal_base / filename).as_posix(), digest)
    stages = reader.read((cal_base / "controls.json").as_posix(), cal_outputs["controls.json"], True)
    need(type(stages) is list and len(stages) == 39 and all(type(row) is dict and
         type(row.get("index")) is int and row["index"] == i and row.get("matches") is True and
         row.get("actual_stage") == row.get("expected_stage") for i, row in enumerate(stages)), "CALIBRATION_STAGES")
    expected = config.get("expected_protected_context")
    need(type(expected) is dict and set(expected) == {"head", "index_sha256", "ledger_sha256"}
         and type(expected["head"]) is str and re.fullmatch("[0-9a-f]{40}", expected["head"])
         and all(type(expected[k]) is str and re.fullmatch("[0-9a-f]{64}", expected[k])
                 for k in ("index_sha256", "ledger_sha256")), "FROZEN_CONFIG_CONTEXT")
    before = protected(reader.deadline)
    need(before == expected, "PROTECTED_CONTEXT")
    closure = reader.read(closure_path, closure_sha, True)
    names = selected_paths(reader.read(selected_path, selected_sha, raw=True))
    declared = manifest(closure, names, expected_count, False)
    claims = [row for row in declared if row["path"] == "CLAIMS.yaml"]
    need(len(claims) == 1 and claims[0]["declared_sha256"] == [expected["ledger_sha256"]], "FROZEN_CLOSURE_SCOPE")
    index = index_rows(git_read(["ls-files", "--stage", "-z"], reader.deadline), set(names))
    if staged:
        base_path, base_sha = config.get("baseline_inventory_path"), config.get("baseline_inventory_sha256")
        need(config["inputs_sha256"].get(base_path) == base_sha, "BASELINE_PIN")
        baseline = reader.read(base_path, base_sha, True)
        need(baseline.get("status") == "WAVE45_EXPLICIT_PUBLICATION_INVENTORY_V4_COMPLETE_PASS"
             and baseline.get("mode") == "inventory" and type(baseline.get("implementation_version")) is int
             and baseline["implementation_version"] == 4 and baseline.get("source_software") == software, "BASELINE_GATE")
        basis = baseline.get("outcome")
        need(type(basis) is dict and basis.get("all_identities_match") is True
             and type(basis.get("selected_distinct")) is int and basis["selected_distinct"] == expected_count
             and basis.get("manifest_sha256") == closure_sha and basis.get("selected_sha256") == selected_sha
             and basis.get("protected_after", {}).get("head") == expected["head"]
             and basis.get("protected_after", {}).get("ledger_sha256") == expected["ledger_sha256"], "BASELINE_SCOPE")
        unselected_stability(index, basis)
        need(len(index["selected"]) == expected_count, "STAGED_SELECTED_MISSING")
    records, errors = [], []
    from tqdm import tqdm
    for ordinal, row in enumerate(tqdm(declared, desc="publication identity")):
        tick(reader.deadline)
        try:
            observed = member(row, reader.deadline)
            tracked = index["selected"].get(row["path"])
            observed["current_index"] = tracked
            observed["working_raw_blob_matches_index_oid"] = blob_identity(observed, tracked, staged)
            observed["publication_availability_action"] = "NONE"
            records.append(observed)
        except ValueError as exc:
            if str(exc) == "SAVE_RESERVE":
                raise
            errors.append({"path": row["path"], "stage": str(exc)})
            records.append({"path": row["path"], "declared_sha256": row["declared_sha256"][0], "error": str(exc)})
        if (ordinal + 1) % 100 == 0 or ordinal + 1 == len(declared):
            save(out / ("checkpoint_%03d.json" % ((ordinal + 1 - 1) // 100)),
                 {"completed": ordinal + 1, "expected": expected_count, "errors": list(errors), "deadline": reader.deadline.status()}, reader.deadline)
    save(out / "member_inventory.json", records, reader.deadline)
    after = protected(reader.deadline)
    need(after == before, "CLOSING_PROTECTED_CONTEXT")
    return {"selected_distinct": expected_count, "complete_member_sha256_checks": len(records) - len(errors),
            "expected_bytes": None, "expected_bytes_null_reason": "Final hash-only manifest declares no prior payload-size observation; every actual member is capped and its bytes reported",
            "observed_bytes_matching_members": sum(row.get("bytes", 0) for row in records),
            "errors": errors, "missing": [row["path"] for row in errors if row["stage"] == "MEMBER_MISSING"],
            "extra_selected": [], "missing_selected": [], "all_identities_match": not errors,
            "tracked_current": len(index["selected"]), "untracked_current": expected_count - len(index["selected"]),
            "raw_working_blob_oid_matches": sum(row.get("working_raw_blob_matches_index_oid", False) for row in records),
            "whole_index_rows": index["whole_index_rows"], "unselected_gitlinks": index["unselected_gitlinks"],
            "unselected_index_rows": index["unselected_index_rows"], "unselected_index_identity_sha256": index["unselected_index_identity_sha256"],
            "manifest_path": closure_path, "manifest_sha256": closure_sha, "selected_path": selected_path, "selected_sha256": selected_sha,
            "protected_before": before, "protected_after": after, "frozen_claims": config["frozen_claims"], "new_claims": config["new_claims"],
            "old_PUBLIC_preserved_premise": 6054, "new_cutoff_artifact_availability_premise": "LOCAL_ONLY",
            "availability_mutated": False, "math_replays": 0,
            "git_mutations": 0, "staging": 0, "staged_raw_identity_required": staged, "physical_git_blob_replay": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("calibrate", "inventory", "staged"))
    for name in ("seconds", "out", "self-sha256", "spec-sha256", "executor"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--configuration")
    parser.add_argument("--configuration-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(float(args.seconds), allocation_reason="One configuration-frozen read-only publication identity invocation or fresh finite controls, including all hashes/Git children/output/closing context")
    need(args.executor == "/root", "EXECUTOR_DECLARATION")
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out = safe(out.relative_to(ROOT).as_posix())
    need(out.is_relative_to(ROOT / "acceleration/results") and not out.exists(), "OUTPUT_FRESH_SCOPE")
    out.mkdir(parents=True)
    software = {**SOFTWARE, SELF.relative_to(ROOT).as_posix(): args.self_sha256, SPEC.relative_to(ROOT).as_posix(): args.spec_sha256}
    reader = Reader(deadline)
    try:
        reader.mapping(software)
        if args.mode == "calibrate":
            outcome, status = controls(out, deadline), CAL_STATUS
        else:
            need(args.configuration is not None and args.configuration_sha256 is not None, "CONFIG_ARGUMENTS")
            config = reader.read(Path(args.configuration).relative_to(ROOT).as_posix() if Path(args.configuration).is_absolute() else args.configuration,
                                 args.configuration_sha256, True)
            outcome = inventory(reader, config, out, software, args.mode == "staged")
            status = "WAVE45_EXPLICIT_PUBLICATION_INVENTORY_V4_COMPLETE_PASS" if outcome["all_identities_match"] else "WAVE45_EXPLICIT_PUBLICATION_INVENTORY_V4_COMPLETE_FAILED_IDENTITIES"
        reader.closing()
        outputs = {path.name: hash_file(path, deadline)["sha256"] for path in sorted(out.iterdir())}
        need(len(outputs) == (94 if args.mode == "calibrate" else (outcome["selected_distinct"] + 99) // 100 + 1), "OUTPUT_POPULATION")
        summary = {"schema": "WAVE45_EXPLICIT_PUBLICATION_INVENTORY_REPORT_V1", "status": status, "implementation_version": 4,
            "mode": args.mode, "timestamp": datetime.now(timezone.utc).isoformat(), "source_author": "/root/checkpoint_audit",
            "executor_declaration": args.executor, "actual_executor_requires_external_receipt": True,
            "source_software": software, "inputs_sha256": reader.pins, "outputs_sha256": outputs,
            "outcome": outcome, "command": sys.argv, "target_resolution": "NONE", "mathematical_approval": False,
            "automatic_retry": False, "deadline": deadline.status(),
            "limitations": ["No mathematical or remote artifact replay and no new availability claim",
                "Tracked index OID versus raw-working Git SHA1 is metadata/identity comparison, not a physical cat-file replay",
                "One complete selected-member byte pass; direct/protected files may be rehashed, and closing metadata does not guarantee concurrent member-byte immutability",
                "No secret scan beyond frozen packaging audit and safe filename scope; no raw private process argv is read or emitted",
                "Completed checkpoints survive orderly failure; no hard-real-time or hardkill save guarantee"]}
        save(out / "summary.json", summary, deadline)
        reader.closing()
        tick(deadline)
        print(json.dumps({"status": status, "outcome": outcome}), flush=True)
        if args.mode != "calibrate" and not outcome["all_identities_match"]:
            raise ValueError("COMPLETE_FAILED_IDENTITIES")
    except Exception as exc:
        try:
            (out / "failure.json").write_text(json.dumps({"status": "FAILED_PRESERVED", "stage": str(exc),
                "inputs_sha256": reader.pins, "target_resolution": "NONE", "automatic_retry": False,
                "no_availability_mutation": True, "deadline": deadline.status()}, indent=2) + "\n", encoding="utf-8")
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()

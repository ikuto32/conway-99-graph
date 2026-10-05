"""Finite ordinary controls for literal copier/checker; synthetic JSON only, no ledger imports."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--configuration", required=True)
    parser.add_argument("--configuration-sha256", required=True)
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="Finite ordinary literal copy/type controls on small synthetic JSON.")
    inputs = {}

    def tick():
        assert deadline.status()["remaining_seconds"] > 20

    def safe(relative):
        assert type(relative) is str and ":" not in relative and "\\" not in relative
        assert all(p not in ("", ".", "..") for p in relative.split("/"))
        path = ROOT / relative
        assert path.resolve().is_relative_to(ROOT)
        return path

    def read(relative, expected=None):
        tick()
        raw = safe(relative).read_bytes()
        sha = digest(raw)
        assert expected is None or sha == expected, (relative, "input identity")
        inputs[relative] = sha
        return raw

    config = json.loads(read(args.configuration, args.configuration_sha256))
    assert config["schema"] == "BOUND_LITERAL_FINITE_CONTROLS_V1"
    for path, sha in config["inputs_sha256"].items():
        read(path, sha)
    copier, checker = config["copier"], config["checker"]
    pwsh = config["pwsh"]
    assert digest(Path(pwsh["path"]).read_bytes()) == pwsh["sha256"]
    assert digest(Path(sys.executable).read_bytes()) == config["python_sha256"]
    inputs[pwsh["path"]] = pwsh["sha256"]
    inputs[str(Path(sys.executable))] = config["python_sha256"]
    out = safe(args.out)
    assert out.resolve().is_relative_to(ROOT / "acceleration/results") and not out.exists()
    out.mkdir()

    def save(path, value):
        tick()
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf8")
        tick()

    def relative(path):
        return path.relative_to(ROOT).as_posix()

    def execute(command, stem):
        tick()
        result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                timeout=max(0.001, deadline.status()["remaining_seconds"] - 20))
        (stem.parent / (stem.name + ".stdout.txt")).write_bytes(result.stdout)
        (stem.parent / (stem.name + ".stderr.txt")).write_bytes(result.stderr)
        tick()
        return result

    controls = []
    for route in config["routes"]:
        tick()
        base = out / ("case_" + str(route["ordinal"]).zfill(2))
        base.mkdir()
        population = route["population"]
        evidence = {}
        for name, n in (("a.json", 1), ("b.json", 2), ("c.json", 3), ("d.json", 4)):
            leaf = base / name
            save(leaf, {"fixture": n})
            evidence[relative(leaf)] = digest(leaf.read_bytes())
        a, b, c, d = [relative(base / (x + ".json")) for x in "abcd"]
        artifact = lambda id_, path, availability: {"id": id_, "path": path, "sha256": evidence[path],
                                                  "availability": availability, "retrieval": path,
                                                  "unavailable_reason": None if availability == "PUBLIC" else "fixture"}
        artifacts = [artifact("A-Z", a, "PUBLIC"), artifact("A-A", a, "LOCAL_ONLY"),
                     artifact("A-B", b, "LOCAL_ONLY"), artifact("A-C", c, "MISSING")]
        old_count, new_count, prefix = (2, 1, "A-CAL-ONE-") if population == "one" else (3, 2, "A-CAL-TWO-")
        if population == "two":
            artifacts.append(artifact("A-D", d, "PUBLIC"))
        old_claims = [{"id": "C-OLD-" + str(i), "status": "VERIFIED", "review_state": "CLEAR",
                       "nested": {"ordinal": i, "literal_bool": False, "array": [i, True, None]}}
                      for i in range(old_count)]
        before = {"schema_version": 2, "updated_at": "2026-10-04T00:00:00+00:00",
                  "target_resolution": "UNKNOWN", "other_top": {"old": [True, 1, None]},
                  "claims": old_claims, "artifacts": artifacts}
        before_path = base / "before.json"
        save(before_path, before)
        union = {p: evidence[p] for p in (a, b, c)}
        items = []
        for i in range(new_count):
            items.append({"claim_core": {"id": "C-NEW-" + str(i), "revision": 1,
                                         "status": "VERIFIED", "review_state": "CLEAR",
                                         "statement": "Synthetic administrative fixture", "scope": {"n": i}},
                          "verification_core": {"timestamp": "2026-10-04T01:02:03+00:00",
                                                "outcome": "PASS", "artifact_hashes": None, "controls": []},
                          "evidence_identity_paths": list(union), "evidence_identity_sha256": dict(union),
                          "unknowns": ["synthetic only"], "external_source": None,
                          "reproducibility_manifest_path": None})
        packet = {"schema": "BOUND_LITERAL_APPEND_PACKET_V1",
                  "baseline": {"path": relative(before_path), "sha256": digest(before_path.read_bytes()),
                               "schema_version": 2, "claims": old_count, "artifact_records": len(artifacts),
                               "public_records": 1 if population == "one" else 2},
                  "claim_count": new_count, "expected_after_claims": old_count + new_count,
                  "claims": items, "evidence_union": union, "evidence_identity_count": 3,
                  "new_artifact_policy": {"artifact_prefix": prefix, "availability": "LOCAL_ONLY",
                                         "unavailable_reason": "Synthetic evidence remains LOCAL_ONLY."},
                  "validator": config["validator"], "schema_definition": config["schema_definition"]}
        action = route["mutation"]
        if action == "count_bool":
            packet["claim_count"] = True
        elif action == "after_mismatch":
            packet["expected_after_claims"] += 1
        elif action == "union_omit":
            del packet["evidence_union"][c]
        elif action == "map_hash":
            packet["claims"][-1]["evidence_identity_sha256"][c] = "0" * 64
        elif action == "prefix_invalid":
            packet["new_artifact_policy"]["artifact_prefix"] = "A-lower-"
        elif action == "public_bool":
            packet["baseline"]["public_records"] = True
        packet_path = base / "packet.json"
        save(packet_path, packet)
        copy_out = base / "copy"
        command = [pwsh["path"], "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(ROOT / copier["path"]),
                   "-Packet", relative(packet_path), "-PacketSha256", digest(packet_path.read_bytes()),
                   "-SourceSha256", copier["sha256"], "-SpecSha256", copier["spec_sha256"],
                   "-Out", relative(copy_out), "-Seconds", str(deadline.status()["remaining_seconds"]),
                   "-Executor", "/root"]
        copied = execute(command, base / "copier")
        if route["subject"] == "copier":
            assert copied.returncode == 1 and re.search(r"\b" + re.escape(route["expected_stage"]) + r"\b",
                                                       copied.stderr.decode("utf8", errors="replace"))
            observed = route["expected_stage"]
            result_code = copied.returncode
        else:
            assert copied.returncode == 0, copied.stderr.decode("utf8", errors="replace")
            candidate_path = copy_out / "CLAIMS.candidate.yaml"
            candidate = json.loads(candidate_path.read_bytes())
            resolution_path = copy_out / "evidence_resolution.json"
            resolution = json.loads(resolution_path.read_bytes())
            summary_path = copy_out / "summary.json"
            summary = json.loads(summary_path.read_bytes())
            if action == "late_old_claim":
                candidate["claims"][old_count - 1]["nested"]["ordinal"] = True
            elif action == "late_old_artifact":
                candidate["artifacts"][len(artifacts) - 1]["sha256"] = "0" * 64
            elif action == "top_field":
                candidate["other_top"]["old"][-1] = False
            elif action == "public":
                candidate["artifacts"][0]["availability"] = "LOCAL_ONLY"
            elif action == "core_bool":
                candidate["claims"][-1]["revision"] = True
            elif action == "ordinal_bool":
                resolution[-1]["ordinal"] = True
            elif action == "late_identity":
                with (base / "c.json").open("ab") as stream:
                    stream.write(b"\n")
            elif action == "wrong_reuse":
                resolution[0]["artifact_id"] = "A-Z"
            elif action == "wrong_reason":
                candidate["artifacts"][-1]["unavailable_reason"] = "different"
            elif action == "omission":
                candidate["claims"].pop()
            elif action == "summary_bool":
                summary["reused"] = True
            save(candidate_path, candidate)
            save(resolution_path, resolution)
            save(summary_path, summary)
            if action == "duplicate_json":
                raw = candidate_path.read_text(encoding="utf8")
                candidate_path.write_text(raw.replace("{\n", '{\n  "schema_version": 2,\n', 1), encoding="utf8")
            checked_out = base / "checked"
            if action == "existing_out":
                checked_out.mkdir()
            command = [sys.executable, "-B", str(ROOT / checker["path"]),
                       "--packet", relative(packet_path), "--packet-sha256", digest(packet_path.read_bytes()),
                       "--candidate-root", relative(copy_out), "--candidate-sha256", digest(candidate_path.read_bytes()),
                       "--out", relative(checked_out), "--seconds", str(deadline.status()["remaining_seconds"])]
            checked = execute(command, base / "checker")
            if route["positive"]:
                assert checked.returncode == 0, checked.stderr.decode("utf8", errors="replace")
                report = json.loads((checked_out / "summary.json").read_bytes())
                assert report["result"] == "PASS_ADMINISTRATIVE_ONLY" and report["new_claims"] == new_count
                assert report["old_claims_preserved"] == old_count and report["new_artifacts"] == 1
                observed = "PASS_ADMINISTRATIVE_ONLY"
            else:
                stderr = checked.stderr.decode("utf8", errors="replace")
                assert checked.returncode == 1 and re.search(
                    r'File ".*' + re.escape(Path(checker["path"]).name) + r'", line ' + str(route["expected_line"]) + r"\b", stderr)
                assert re.search(r"^" + re.escape(route["expected_exception"]) + r"(?:\:|$)", stderr, re.M), stderr
                observed = route["expected_exception"] + ":" + str(route["expected_line"])
            result_code = checked.returncode
        row = {"ordinal": route["ordinal"], "name": route["name"], "positive": route["positive"],
               "expected": route["expected_stage"] if route["subject"] == "copier" else
                           ("PASS_ADMINISTRATIVE_ONLY" if route["positive"] else route["expected_exception"] + ":" + str(route["expected_line"])),
               "observed": observed, "subject_exit_code": result_code, "PASS": True}
        save(base / "control.json", row)
        controls.append(row)
    save(out / "controls.json", controls)
    tick()
    outputs = {relative(p): digest(p.read_bytes()) for p in sorted(out.rglob("*")) if p.is_file()}
    assert len(controls) == 21 and sum(r["positive"] for r in controls) == 2 and len(outputs) == 290
    for path, sha in inputs.items():
        tick()
        raw = Path(path).read_bytes() if Path(path).is_absolute() else safe(path).read_bytes()
        assert digest(raw) == sha
    result = {"schema": "BOUND_LITERAL_FINITE_CONTROLS_V1", "status": "COMPLETE_FINITE_CONTROLS_PASS",
              "positive": 2, "negative": 19, "total": 21, "source_author": "/root/checkpoint_audit",
              "actual_executor": "/root", "shared_copier_checker_author": "/root/checkpoint_audit",
              "subject_imports": 0, "mathematical_replays": 0, "real_ledger_read": False,
              "inputs_sha256": inputs, "outputs_sha256": outputs, "deadline": deadline.status(),
              "target_resolution": "NONE", "physical_files_expected": 291}
    save(out / "summary.json", result)
    tick()
    print(json.dumps({k: v for k, v in result.items() if not k.endswith("_sha256")}))


if __name__ == "__main__":
    main()


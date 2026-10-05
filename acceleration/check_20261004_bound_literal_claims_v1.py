"""Parameterized literal administrative comparison; CP/Root ancestry, no mathematical replay."""
from pathlib import Path
import argparse
import hashlib
import json
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]


def unique(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def typed(value):
    if type(value) is dict:
        return ("object", tuple((k, typed(value[k])) for k in sorted(value)))
    if type(value) is list:
        return ("array", tuple(typed(v) for v in value))
    return (type(value).__name__, value)


def integer(value, minimum, maximum):
    assert type(value) is int and minimum <= value <= maximum
    return value


def main():
    parser = argparse.ArgumentParser()
    for flag in ("packet", "packet-sha256", "candidate-root", "candidate-sha256", "out"):
        parser.add_argument("--" + flag, required=True)
    parser.add_argument("--seconds", type=float, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="Typed parameterized literal administrative preservation and evidence comparison.")
    checked = {}

    def read(path, sha=None):
        assert deadline.status()["remaining_seconds"] > 20
        assert type(path) is str and "\\" not in path and ":" not in path
        assert all(part not in ("", ".", "..") for part in path.split("/"))
        actual = ROOT / path
        assert actual.resolve().is_relative_to(ROOT) and actual.is_file()
        raw = actual.read_bytes()
        got = hashlib.sha256(raw).hexdigest()
        if sha is not None:
            assert got == sha, (path, "identity")
        checked[path] = got
        return raw

    def load(path, sha=None):
        return json.loads(read(path, sha), object_pairs_hook=unique,
                          parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))

    packet = load(args.packet, args.packet_sha256)
    assert packet["schema"] == "BOUND_LITERAL_APPEND_PACKET_V1"
    schema = integer(packet["baseline"]["schema_version"], 2, 2)
    old_claims = integer(packet["baseline"]["claims"], 0, 100000)
    old_artifacts = integer(packet["baseline"]["artifact_records"], 0, 1000000)
    public = integer(packet["baseline"]["public_records"], 0, old_artifacts)
    new_claims = integer(packet["claim_count"], 1, 10000)
    evidence_count = integer(packet["evidence_identity_count"], 1, 100000)
    after_claims = integer(packet["expected_after_claims"], 1, 100000)
    assert after_claims == old_claims + new_claims
    policy = packet["new_artifact_policy"]
    prefix, reason = policy["artifact_prefix"], policy["unavailable_reason"]
    assert type(prefix) is str and prefix.startswith("A-") and prefix.endswith("-")
    assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-" for c in prefix)
    assert type(reason) is str and reason.strip() and policy["availability"] == "LOCAL_ONLY"
    base = args.candidate_root.rstrip("/")
    before = load(base + "/CLAIMS.before.yaml", packet["baseline"]["sha256"])
    candidate = load(base + "/CLAIMS.candidate.yaml", args.candidate_sha256)
    resolution = load(base + "/evidence_resolution.json")
    summary = load(base + "/summary.json")
    assert integer(before["schema_version"], 2, 2) == schema
    assert len(before["claims"]) == old_claims and len(before["artifacts"]) == old_artifacts
    assert sum(a["availability"] == "PUBLIC" for a in before["artifacts"]) == public
    assert len(candidate["claims"]) == after_claims and len(packet["claims"]) == new_claims
    assert typed(candidate["claims"][:old_claims]) == typed(before["claims"])
    assert typed(candidate["artifacts"][:old_artifacts]) == typed(before["artifacts"])
    assert set(before) == set(candidate)
    for key in set(before) - {"claims", "artifacts", "updated_at"}:
        assert typed(before[key]) == typed(candidate[key]), key
    assert type(candidate["updated_at"]) is str
    paths = sorted(packet["evidence_union"])
    assert type(packet["evidence_union"]) is dict and len(paths) == evidence_count and len(resolution) == len(paths)
    assert not any(p.lower().endswith((".drat", ".proof")) for p in paths)
    for item in packet["claims"]:
        evidence = item["evidence_identity_paths"]
        assert type(evidence) is list and evidence and len(evidence) == len(set(evidence))
        assert {p: packet["evidence_union"][p] for p in evidence} == item["evidence_identity_sha256"]
    assert set(paths) == {p for item in packet["claims"] for p in item["evidence_identity_paths"]}
    existing = {}
    for artifact in before["artifacts"]:
        if artifact["availability"] in ("PUBLIC", "LOCAL_ONLY"):
            key = (artifact["path"], artifact["sha256"])
            existing[key] = min(existing.get(key, artifact["id"]), artifact["id"])
    old_ids = [a["id"] for a in before["artifacts"]]
    old_claim_ids = [c["id"] for c in before["claims"]]
    assert len(old_ids) == len(set(old_ids)) and len(old_claim_ids) == len(set(old_claim_ids))
    new_claim_ids = [c["claim_core"]["id"] for c in packet["claims"]]
    assert len(new_claim_ids) == len(set(new_claim_ids)) and not set(new_claim_ids) & set(old_claim_ids)
    ids, added = {}, []
    for ordinal, (path, row) in enumerate(zip(paths, resolution), 1):
        sha = packet["evidence_union"][path]
        read(path, sha)
        key = (path, sha)
        reused = key in existing
        id_ = existing[key] if reused else f"{prefix}{ordinal:04d}"
        assert reused or id_ not in set(old_ids)
        expected = {"ordinal": ordinal, "path": path, "sha256": sha, "artifact_id": id_, "reused": reused}
        assert typed(row) == typed(expected)
        ids[path] = id_
        if not reused:
            added.append({"id": id_, "path": path, "sha256": sha, "availability": "LOCAL_ONLY", "retrieval": path,
                          "unavailable_reason": reason})
    assert typed(candidate["artifacts"][old_artifacts:]) == typed(added)
    for saved, item in zip(candidate["claims"][old_claims:], packet["claims"]):
        expected = dict(item["claim_core"])
        evidence = item["evidence_identity_paths"]
        assert {p: packet["evidence_union"][p] for p in evidence} == item["evidence_identity_sha256"]
        verification = dict(item["verification_core"])
        verification["artifact_hashes"] = {ids[p]: packet["evidence_union"][p] for p in evidence}
        manifest_path = item["reproducibility_manifest_path"]
        expected.update(evidence=[ids[p] for p in evidence], verification=[verification],
                        unknowns=item["unknowns"], external_source=item["external_source"],
                        reproducibility=None if manifest_path is None else {"manifest": ids[manifest_path]})
        assert typed(saved) == typed(expected), saved["id"]
    assert sum(a["availability"] == "PUBLIC" for a in candidate["artifacts"]) == public
    assert type(summary["candidate_claims"]) is int and summary["candidate_claims"] == after_claims and summary["candidate_artifacts"] == len(candidate["artifacts"])
    assert integer(summary["before_claims"], 0, 100000) == old_claims
    assert integer(summary["candidate_artifacts"], 0, 1000000) == len(candidate["artifacts"])
    assert integer(summary["evidence_identities"], 1, 100000) == len(paths)
    assert integer(summary["appended"], 0, 100000) == len(added)
    assert integer(summary["reused"], 0, 100000) == len(paths) - len(added)
    assert summary["schema"] == "BOUND_LITERAL_MATERIALIZATION_V2" and summary["status"] == "CANDIDATE_ADMINISTRATIVE_UNVERIFIED"
    assert deadline.status()["remaining_seconds"] > 20
    out = ROOT / args.out
    assert out.resolve().is_relative_to(ROOT / "acceleration/results") and not out.exists()
    out.mkdir(exist_ok=False)
    report = {"schema": "BOUND_LITERAL_TYPED_CHECK_V1", "result": "PASS_ADMINISTRATIVE_ONLY",
              "old_claims_preserved": old_claims, "old_artifacts_preserved": old_artifacts, "new_claims": new_claims,
              "new_artifacts": len(added), "public_records_unchanged": public,
              "fresh_inputs_sha256": checked, "deadline": deadline.status(),
              "source_author": "/root/checkpoint_audit", "copier_shared_adaptation_author": "/root/checkpoint_audit",
              "checking_path": "Separate deep-type JSON reconstruction, ordinal reuse and complete prefix comparison; no copier imports.",
              "mathematical_replays": 0, "target_resolution": "UNKNOWN"}
    (out / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    assert deadline.status()["remaining_seconds"] > 20
    print(json.dumps({k: v for k, v in report.items() if k != "fresh_inputs_sha256"}))


if __name__ == "__main__":
    main()


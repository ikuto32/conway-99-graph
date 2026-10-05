"""Independent typed administrative comparison; no mathematical replay."""
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


def main():
    parser = argparse.ArgumentParser()
    for flag in ("packet", "packet-sha256", "candidate-root", "candidate-sha256", "out"):
        parser.add_argument("--" + flag, required=True)
    parser.add_argument("--seconds", type=float, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason="Typed nine-claim administrative preservation and evidence comparison.")
    checked = {}

    def read(path, sha=None):
        assert deadline.status()["remaining_seconds"] > 20
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
    base = args.candidate_root.rstrip("/")
    before = load(base + "/CLAIMS.before.yaml", packet["baseline"]["sha256"])
    candidate = load(base + "/CLAIMS.candidate.yaml", args.candidate_sha256)
    resolution = load(base + "/evidence_resolution.json")
    summary = load(base + "/summary.json")
    assert len(before["claims"]) == 435 and len(before["artifacts"]) == 23695
    assert len(candidate["claims"]) == 444 and len(packet["claims"]) == 9
    assert typed(candidate["claims"][:435]) == typed(before["claims"])
    assert typed(candidate["artifacts"][:23695]) == typed(before["artifacts"])
    assert set(before) == set(candidate)
    for key in set(before) - {"claims", "artifacts", "updated_at"}:
        assert typed(before[key]) == typed(candidate[key]), key
    assert type(candidate["updated_at"]) is str
    paths = sorted(packet["evidence_union"])
    assert len(paths) == 115 and len(resolution) == 115
    existing = {}
    for artifact in before["artifacts"]:
        if artifact["availability"] in ("PUBLIC", "LOCAL_ONLY"):
            key = (artifact["path"], artifact["sha256"])
            existing[key] = min(existing.get(key, artifact["id"]), artifact["id"])
    ids, added = {}, []
    for ordinal, (path, row) in enumerate(zip(paths, resolution), 1):
        sha = packet["evidence_union"][path]
        read(path, sha)
        key = (path, sha)
        reused = key in existing
        id_ = existing[key] if reused else f"A-NINE-MATH-20261004-{ordinal:04d}"
        expected = {"ordinal": ordinal, "path": path, "sha256": sha, "artifact_id": id_, "reused": reused}
        assert typed(row) == typed(expected)
        ids[path] = id_
        if not reused:
            added.append({"id": id_, "path": path, "sha256": sha, "availability": "LOCAL_ONLY", "retrieval": path,
                          "unavailable_reason": "Exact mathematical evidence remains LOCAL_ONLY pending separate publication."})
    assert typed(candidate["artifacts"][23695:]) == typed(added)
    for saved, item in zip(candidate["claims"][435:], packet["claims"]):
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
    assert sum(a["availability"] == "PUBLIC" for a in candidate["artifacts"]) == 6054
    assert summary["candidate_claims"] == 444 and summary["candidate_artifacts"] == len(candidate["artifacts"])
    assert summary["appended"] == len(added) and summary["reused"] == 115 - len(added)
    assert deadline.status()["remaining_seconds"] > 20
    out = ROOT / args.out
    assert out.resolve().is_relative_to(ROOT / "acceleration/results") and not out.exists()
    out.mkdir(exist_ok=False)
    report = {"schema": "ROOT_NINE_MATHEMATICAL_TYPED_CHECK_V2", "result": "PASS_ADMINISTRATIVE_ONLY",
              "old_claims_preserved": 435, "old_artifacts_preserved": 23695, "new_claims": 9,
              "new_artifacts": len(added), "public_records_unchanged": 6054,
              "fresh_inputs_sha256": checked, "deadline": deadline.status(),
              "mathematical_replays": 0, "target_resolution": "UNKNOWN"}
    (out / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    assert deadline.status()["remaining_seconds"] > 20
    print(json.dumps({k: v for k, v in report.items() if k != "fresh_inputs_sha256"}))


if __name__ == "__main__":
    main()

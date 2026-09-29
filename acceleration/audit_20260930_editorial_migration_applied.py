"""Independently compare applied ledgers with exact approved editorial scope.

Imports neither the registrar nor registry validator. This authenticates
bookkeeping and preservation, not new mathematical results.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
B = "acceleration/results/20260930_independent_review/"
APPLIED = "acceleration/results/20260930_editorial_migration_applied/"
OUT = ROOT / (B + "editorial_migration_applied")
PINS = {
    B + "automorphism_assumption_editorial/summary.json": "1584c3c0ef52fdee47c056fec317260d6952fdbd46a9e47e0742ce1f6d711388",
    B + "editorial_dependent_impact/dual_gram.json": "b833aa2b8b444130b85119d1e753203882f962e3939e9bc3e9b197ea7ea94ef7",
    B + "editorial_dependent_impact/w81_nogood.json": "44e397965694458dfa45e6884f7ea0961de9c84c775c3806e20c15a39cc90564",
    B + "editorial_migration_corrected/summary.json": "6bfb4613a559e8c5e05e8f5d4022ce7a59e5b0b157c316cc00ceb736fe6a545c",
    "acceleration/results/20260930_editorial_migration_tooling/run01/dependency_plan.json": "e868bb645116db33fb48e8975e7aa353c445127afd9909f14597732a56b56e66",
    APPLIED + "CLAIMS.before.yaml": "20b3ee7d9c13c5142205492832a85ba877f35492ab26c0db1fdd5e3b9ba7e168",
    APPLIED + "CLAIMS.after.yaml": "aa648e4f9e7369aeff89c2e6ae06e45e978296c22b22c37da92e4d33bf5afeaa",
}


def need(test, message):
    if not test:
        raise ValueError(message)


class Loader(yaml.SafeLoader):
    pass


Loader.yaml_implicit_resolvers = {k: [(t, r) for t, r in rs if t != "tag:yaml.org,2002:timestamp"]
                                 for k, rs in Loader.yaml_implicit_resolvers.items()}


def mapping(loader, node, deep=False):
    result = {}
    for k, v in node.value:
        key = loader.construct_object(k, deep=deep)
        need(key not in result, "duplicate YAML key")
        result[key] = loader.construct_object(v, deep=deep)
    return result


Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check(before, after, editorial, dependents, plan, artifact_paths):
    old = {c["id"]: c for c in before["claims"]}
    new = {c["id"]: c for c in after["claims"]}
    need(len(old) == len(before["claims"]) and len(new) == len(after["claims"]), "unique claims")
    need([c["id"] for c in before["claims"]] == [c["id"] for c in after["claims"]], "same claims and order")
    reviewed = {r["claim_id"]: r for r in editorial["records"]}
    reviewed_dependencies = {r["claim_id"]: r for r in dependents}
    affected = set(reviewed) | set(reviewed_dependencies)
    need(len(reviewed) == 17 and len(reviewed_dependencies) == 2 and len(affected) == 19, "exact approved population")
    need(set(plan["topological_order"]) == affected, "plan affected population")
    need(set(after) == set(before) | {"editorial_migrations"}, "top-level keys")
    for key in before:
        if key not in {"schema_version", "updated_at", "artifacts", "claims"}:
            need(after[key] == before[key], "unrelated top-level change: " + key)
    need(before["schema_version"] == 1 and after["schema_version"] == 2, "schema version transition")
    now = datetime.fromisoformat(after["updated_at"])
    need(now.tzinfo is not None and now >= datetime.fromisoformat(before["updated_at"]), "updated timestamp")
    need(after["artifacts"][:len(before["artifacts"])] == before["artifacts"], "original artifact records preserved exactly")
    additions = after["artifacts"][len(before["artifacts"]):]
    need(len(additions) == 4 and {a["path"] for a in additions} == set(artifact_paths), "exact four evidence additions")
    all_artifacts = {a["id"]: a for a in after["artifacts"]}
    need(len(all_artifacts) == len(after["artifacts"]), "unique artifact IDs")
    added_by_path = {a["path"]: a for a in additions}
    for path, sha in artifact_paths.items():
        a = added_by_path[path]
        need(a["sha256"] == sha and a["availability"] == "LOCAL_ONLY"
             and a["retrieval"] and a["unavailable_reason"], "added artifact binding/availability")
    review_path = B + "automorphism_assumption_editorial/summary.json"
    snapshot_path = editorial["reviewed_ledger_snapshot"]
    review_artifact, snapshot_artifact = added_by_path[review_path], added_by_path[snapshot_path]
    touched_edges, preserved_checks = [], 0
    for cid, previous in old.items():
        current = new[cid]
        need(set(current) == set(previous), "claim field keys preserved")
        if cid not in affected:
            need(current == previous, "unaffected claim changed: " + cid)
            preserved_checks += len(previous["verification"])
            continue
        stable = set(previous)-{"revision", "updated_at", "assumptions", "dependencies", "evidence", "verification"}
        need(all(current[k] == previous[k] for k in stable), "unapproved claim field change: " + cid)
        need(current["revision"] == previous["revision"]+1 == 2, "exact claim revision increment")
        need(current["updated_at"] == after["updated_at"], "claim migration timestamp")
        expected_deps = []
        for d in previous["dependencies"]:
            expected = dict(d, revision=2) if d["id"] in affected else d
            expected_deps.append(expected)
            if expected != d:
                touched_edges.append({"claim_id": cid, "old": d, "new": expected})
        need(current["dependencies"] == expected_deps, "exact dependency pins/relations: " + cid)
        need(current["verification"][:len(previous["verification"])] == previous["verification"], "original verification prefix preserved")
        need(len(current["verification"]) == len(previous["verification"])+1, "one new verification per affected claim")
        preserved_checks += len(previous["verification"])
        v = current["verification"][-1]
        need(v["claim_revision"] == 2 and v["outcome"] == "PASS" and v["scope"] == previous["scope"]["description"], "current verification binding")
        need(v["shared_components"] and v["controls"] and v["limitations"], "review disclosures")
        if cid in reviewed:
            r = reviewed[cid]
            need(canonical(previous) == r["reviewed_claim_sha256"], "reviewed complete old claim")
            need(current["assumptions"] == r["recommended_assumptions"], "exact approved assumptions")
            ids = [review_artifact["id"], snapshot_artifact["id"]]
            need(current["evidence"] == previous["evidence"]+ids, "editorial evidence additions only")
            need(v["method"] == "editorial_impact_review" and v["verifier"] == editorial["verifier"]
                 and v["timestamp"] == editorial["timestamp"] and v["command_or_audit"] == review_path, "editorial review identity")
            need(v["artifact_hashes"] == {a["id"]: a["sha256"] for a in (review_artifact, snapshot_artifact)}, "editorial exact hashes")
        else:
            r = reviewed_dependencies[cid]
            path = next(p for p in artifact_paths if p.endswith("dual_gram.json" if cid.endswith("DUAL-GRAM-EXCLUSION") else "w81_nogood.json"))
            a = added_by_path[path]
            need(canonical(previous) == r["old_claim_sha256"] and current["assumptions"] == previous["assumptions"], "unchanged separately reviewed claim")
            need(current["dependencies"] == r["recommended_dependencies"], "separate review exact dependency recommendation")
            need(current["evidence"] == previous["evidence"]+[a["id"]], "separate review evidence only")
            need(v["method"] == "independent_artifact_check" and v["verifier"] == r["verifier"]
                 and v["timestamp"] == r["timestamp"] and v["command_or_audit"] == path, "dependent review identity")
            need(v["artifact_hashes"] == {a["id"]: a["sha256"]}, "dependent review exact hash")
    # All current pins, including those in unaffected claims, are checked.
    all_edges = sum(len(c["dependencies"]) for c in new.values())
    need(all(new[d["id"]]["revision"] == d["revision"] for c in new.values() for d in c["dependencies"]), "all dependency pins current")
    need(len(after["editorial_migrations"]) == 1, "one migration record")
    migration = after["editorial_migrations"][0]
    need(migration["id"] == "M-AUTOMORPHISM-ASSUMPTION-CLARIFICATION-20260930" and migration["version"] == 1
         and migration["kind"] == "REVIEWED_ASSUMPTION_CLARIFICATION", "migration identity")
    need(migration["review_artifact"] == {"artifact": review_artifact["id"], "sha256": review_artifact["sha256"]}
         and migration["snapshot_artifact"] == {"artifact": snapshot_artifact["id"], "sha256": snapshot_artifact["sha256"]}, "migration artifacts")
    need(len(migration["claims"]) == 17 and {r["claim_id"] for r in migration["claims"]} == set(reviewed), "migration member population")
    for row in migration["claims"]:
        c = old[row["claim_id"]]
        r = reviewed[c["id"]]
        expected = dict(claim_id=c["id"], from_revision=1, to_revision=2, old_claim_sha256=canonical(c),
                        old_assumptions=c["assumptions"], new_assumptions=r["recommended_assumptions"])
        need(row == expected, "exact migration member")
    return {"claim_population": len(old), "changed_claims": len(affected), "unchanged_claims": len(old)-len(affected),
            "editorial_changes": 17, "separate_dependency_reviews": 2, "original_verification_records_preserved": preserved_checks,
            "original_artifacts_preserved": len(before["artifacts"]), "new_review_artifacts": len(additions),
            "all_dependency_edges_checked": all_edges, "repinned_dependency_edges": len(touched_edges), "repinned_dependencies": touched_edges,
            "new_mathematical_claims": 0, "target_record_unchanged": before["target"] == after["target"]}


def main():
    need(not OUT.exists(), "refuse overwrite")
    bindings = {}
    def bind(path, expected=None):
        p = Path(path)
        if not p.is_absolute(): p = ROOT / p
        sha = digest(p)
        need(expected is None or sha == expected, "hash: " + str(path))
        bindings[p.relative_to(ROOT).as_posix()] = sha
        return p
    objects = {}
    for path, expected in PINS.items():
        p = bind(path, expected)
        objects[path] = yaml.load(p.read_text(encoding="utf-8"), Loader=Loader) if path.endswith(".yaml") else json.loads(p.read_text(encoding="utf-8"))
    before, after = objects[APPLIED+"CLAIMS.before.yaml"], objects[APPLIED+"CLAIMS.after.yaml"]
    bind("CLAIMS.yaml", PINS[APPLIED+"CLAIMS.after.yaml"])
    editorial = objects[B+"automorphism_assumption_editorial/summary.json"]
    deps = [objects[B+"editorial_dependent_impact/"+name] for name in ("dual_gram.json", "w81_nogood.json")]
    plan = objects["acceleration/results/20260930_editorial_migration_tooling/run01/dependency_plan.json"]
    artifact_paths = {B+"automorphism_assumption_editorial/summary.json": PINS[B+"automorphism_assumption_editorial/summary.json"],
                      editorial["reviewed_ledger_snapshot"]: editorial["reviewed_ledger_sha256"]}
    artifact_paths.update({B+"editorial_dependent_impact/"+name: PINS[B+"editorial_dependent_impact/"+name] for name in ("dual_gram.json", "w81_nogood.json")})
    for path, expected in artifact_paths.items(): bind(path, expected)
    engineering = objects[B+"editorial_migration_corrected/summary.json"]
    need(engineering["status"] == "INDEPENDENT_CORRECTED_EDITORIAL_MIGRATION_CHECKER_PASS", "engineering status")
    for path, expected in engineering["inputs_sha256"].items(): bind(path, expected)
    for r in deps:
        need(r["status"] == "INDEPENDENT_EDITORIAL_DEPENDENCY_IMPACT_PASS", "dependent impact status")
        for path, expected in r["inputs_sha256"].items(): bind(path, expected)
    result = check(before, after, editorial, deps, plan, artifact_paths)
    # Artifact identity checking is not a rerun of the underlying mathematics.
    checked_artifacts = []
    for a in after["artifacts"]:
        need(a["availability"] != "MISSING", "this actual migration has no missing required artifact")
        bind(a["path"], a["sha256"])
        checked_artifacts.append(a["id"])
    cases = {}
    first = next(c["id"] for c in after["claims"] if c["id"] in {r["claim_id"] for r in editorial["records"]})
    for label in ("limitations", "assumptions", "lost_old_verification", "stale_dependency", "wrong_review_hash", "unaffected_claim", "missing_migration_member", "old_artifact", "target_change"):
        bad = deepcopy(after)
        current = next(c for c in bad["claims"] if c["id"] == first)
        if label == "limitations": current["limitations"] = ["Restrictions deleted"]
        elif label == "assumptions": current["assumptions"].append("Assume target asymmetric")
        elif label == "lost_old_verification": current["verification"].pop(0)
        elif label == "stale_dependency": next(d for c in bad["claims"] for d in c["dependencies"] if d["revision"] == 2)["revision"] = 1
        elif label == "wrong_review_hash": current["verification"][-1]["artifact_hashes"][next(iter(current["verification"][-1]["artifact_hashes"]))] = "0"*64
        elif label == "unaffected_claim": next(c for c in bad["claims"] if c["revision"] == 1)["limitations"].append("unapproved")
        elif label == "missing_migration_member": bad["editorial_migrations"][0]["claims"].pop()
        elif label == "old_artifact": bad["artifacts"][0]["sha256"] = "0"*64
        else: bad["target"]["external_review"] = "Unapproved"
        try: check(before, bad, editorial, deps, plan, artifact_paths)
        except ValueError as exc: cases[label] = str(exc)
        else: raise ValueError("corruption accepted: " + label)
    receipt_path = bind(APPLIED+"summary.json")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    need(receipt["previous_sha256"] == PINS[APPLIED+"CLAIMS.before.yaml"] and receipt["ledger_sha256"] == PINS[APPLIED+"CLAIMS.after.yaml"], "receipt identities")
    bind("acceleration/apply_20260930_editorial_migration.py")
    bind(__file__)
    need(digest(ROOT/"CLAIMS.yaml") == PINS[APPLIED+"CLAIMS.after.yaml"], "live ledger unchanged during audit")
    report = {"status": "INDEPENDENT_APPLIED_EDITORIAL_MIGRATION_PASS", "timestamp": datetime.now(timezone.utc).isoformat(),
              "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "command": [sys.executable, *sys.argv], "working_directory": str(Path.cwd()),
              "python": platform.python_version(), "PyYAML": yaml.__version__,
              "verifier": "/root/state_literature_audit independent checker of root registrar output",
              "checking_method": "Separate complete field-by-field comparison, exact prior-record preservation, independently enumerated dependency pins, and actual artifact hashes; no registrar or registry-validator imports",
              "results": result, "artifact_ids_hashed": checked_artifacts, "inputs_sha256": bindings,
              "controls": {"actual_complete_transition_passed": True, "corrupt_transitions_rejected": cases},
              "approved_scope": "Exactly the17 independently approved assumption clarifications,2 separately approved dependency impacts, and associated revision/pin/evidence bookkeeping within the existing80claim ledger",
              "shared_components": ["PyYAML, Python JSON and SHA256", "Immutable semantic/editorial/dependent and engineering review artifacts",
                  "This reviewer authored the independent wording/dependent reports and migration tooling; root authored/applied the registrar and separately reviewed tooling"],
              "limitations": ["No new mathematical claim, computation search, SAT proof or target graph", "Mathematical historical checks are preserved and authenticated; this comparison is not their complete rerun",
                  "The report binds the exact before/after snapshots; subsequent ledger additions require their own checks"],
              "ledger_edited_by_this_checker": False, "target_resolution": False, "artifact_availability": "LOCAL_ONLY"}
    OUT.mkdir(parents=True, exist_ok=False)
    with (OUT/"summary.json").open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2); stream.write("\n")
    print(json.dumps({"status": report["status"], "sha256": digest(OUT/"summary.json"), "results": result}, indent=2))


if __name__ == "__main__":
    main()

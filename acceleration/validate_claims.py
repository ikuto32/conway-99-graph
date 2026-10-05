"""Validate registry syntax, evidence identity, and promotion bookkeeping.

This program does not establish mathematics or independence of human reviewers.
Run with the repository's locked uv environment; see docs/CLAIMS_SCHEMA.md.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys
import subprocess

import jsonschema
import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"duplicate YAML key {key!r} at line {key_node.start_mark.line + 1}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
# Preserve timestamps as strings for JSON Schema validation, not Python datetimes.
UniqueKeyLoader.yaml_implicit_resolvers = {
    key: [(tag, regex) for tag, regex in values if tag != "tag:yaml.org,2002:timestamp"]
    for key, values in UniqueKeyLoader.yaml_implicit_resolvers.items()
}


def read_ledger(path):
    return yaml.load(Path(path).read_text(encoding="utf-8"), Loader=UniqueKeyLoader)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


# This is a deliberately finite migration authorization, not a general trust
# policy for files bearing a reviewer name or a PASS string. New editorial
# classes/reviews require an explicit separately reviewed code change.
EDITORIAL_REVIEWS = {
    "1584c3c0ef52fdee47c056fec317260d6952fdbd46a9e47e0742ce1f6d711388": {
        "snapshot_sha256": "20b3ee7d9c13c5142205492832a85ba877f35492ab26c0db1fdd5e3b9ba7e168",
        "status": "INDEPENDENT_AUTOMORPHISM_ASSUMPTION_EDITORIAL_IMPACT_PASS",
        "verifier": "/root/state_literature_audit independent editorial impact reviewer",
        "claim_count": 17,
    }
}


def canonical_claim_digest(claim):
    """The serialization used by the immutable editorial review's claim hashes."""
    return hashlib.sha256(json.dumps(claim, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check_editorial_migrations(data, root, artifacts, claims):
    """Authenticate finite old/new approvals even when general hashes are skipped.

    A migration is evidence-preserving bookkeeping. It neither generates a
    verification record nor bypasses ordinary dependency-impact review.
    """
    errors, checked, approvals = [], [], {}
    seen_migrations = set()
    for migration in data.get("editorial_migrations", []):
        mid = migration["id"]
        if mid in seen_migrations:
            errors.append(f"editorial {mid}: duplicate migration id")
            continue
        seen_migrations.add(mid)
        try:
            def require(condition, message):
                if not condition:
                    raise ValueError(message)

            def authenticated(binding):
                aid = binding["artifact"]
                require(aid in artifacts, f"unknown artifact {aid}")
                artifact = artifacts[aid]
                require(artifact["sha256"] == binding["sha256"], f"artifact binding differs for {aid}")
                require(artifact["availability"] != "MISSING" and artifact["path"] is not None,
                        f"migration artifact {aid} must be available")
                path = Path(artifact["path"])
                if not path.is_absolute():
                    path = Path(root) / path
                require(path.is_file(), f"migration artifact {aid} must resolve locally")
                require(digest(path) == binding["sha256"], f"migration artifact {aid} SHA-256 mismatch")
                checked.append(aid)
                return path

            review_binding = migration["review_artifact"]
            require(review_binding["sha256"] in EDITORIAL_REVIEWS, "review is not an explicitly approved immutable editorial review")
            policy = EDITORIAL_REVIEWS[review_binding["sha256"]]
            review_path = authenticated(review_binding)
            review = json.loads(review_path.read_text(encoding="utf-8"))
            require(review["status"] == policy["status"] and review["verifier"] == policy["verifier"], "review identity/status mismatch")
            require(review["mathematical_claim_changed"] is False, "review does not certify an editorial-only change")
            snapshot_binding = migration["snapshot_artifact"]
            require(snapshot_binding["sha256"] == policy["snapshot_sha256"] == review["reviewed_ledger_sha256"], "reviewed ledger snapshot hash mismatch")
            snapshot_path = authenticated(snapshot_binding)
            require(snapshot_path.resolve() == (Path(root) / review["reviewed_ledger_snapshot"]).resolve(), "reviewed snapshot path differs")
            snapshot = read_ledger(snapshot_path)
            old_claims = {c["id"]: c for c in snapshot["claims"]}
            require(len(old_claims) == len(snapshot["claims"]), "duplicate old snapshot claim")
            reviewed = {r["claim_id"]: r for r in review["records"]}
            members = {r["claim_id"]: r for r in migration["claims"]}
            require(len(reviewed) == len(review["records"]) == policy["claim_count"], "reviewed claim population differs")
            require(len(members) == len(migration["claims"]) and set(members) == set(reviewed), "migration must name exactly every approved claim once")
            batch = {}
            for cid, member in members.items():
                require(cid in old_claims and cid in claims and cid not in approvals, f"unknown or multiply migrated claim {cid}")
                old, new, record = old_claims[cid], claims[cid], reviewed[cid]
                require(member["from_revision"] == old["revision"] == record["reviewed_revision"], f"{cid}: old revision mismatch")
                require(member["to_revision"] == member["from_revision"] + 1, f"{cid}: migration requires one revision increment")
                require(member["old_claim_sha256"] == record["reviewed_claim_sha256"] == canonical_claim_digest(old), f"{cid}: immutable old claim hash mismatch")
                require(member["old_assumptions"] == old["assumptions"] == record["original_assumptions"], f"{cid}: old assumptions mismatch")
                require(member["new_assumptions"] == record["recommended_assumptions"], f"{cid}: new assumptions not approved")
                require(member["new_assumptions"] == [review["approved_replacements"].get(x, x) for x in member["old_assumptions"]], f"{cid}: unrelated assumption edit")
                require(record["retain_prior_verification_for_exact_editorial_change"] is True, f"{cid}: no retention approval")
                require(new["revision"] >= member["to_revision"] and new["assumptions"] == member["new_assumptions"], f"{cid}: migration not applied at approved revision/assumptions")
                for field in ("statement", "scope", "kind"):
                    require(new[field] == old[field], f"{cid}: editorial migration cannot alter {field}")
                require(record["statement"] == old["statement"] and record["scope"] == old["scope"], f"{cid}: reviewed statement/scope mismatch")
                require(all(v in new["verification"] for v in old["verification"]), f"{cid}: old verification evidence not preserved")
                require(all(aid in new["evidence"] for aid in old["evidence"]), f"{cid}: old evidence not preserved")
                require(review_binding["artifact"] in new["evidence"] and snapshot_binding["artifact"] in new["evidence"], f"{cid}: migration artifacts must be claim evidence")
                approval = dict(migration_id=mid, member=member, old=old, review=review,
                                review_path=review_path, bindings={review_binding["artifact"]: review_binding["sha256"],
                                                                snapshot_binding["artifact"]: snapshot_binding["sha256"]})
                # The immutable snapshot is a mandatory comparison base for
                # the initial approved revision, even without --previous (or
                # when a PR base does not yet contain this claim). Otherwise
                # an unrelated field edit could piggyback on editorial PASS.
                if new["revision"] == member["to_revision"]:
                    require(editorial_change_allowed(old, new, approval),
                            f"{cid}: unapproved initial editorial fields requires new stable id or separate review")
                require(any(editorial_verification_matches(v, new, approval, root) for v in new["verification"]), f"{cid}: exact editorial review record missing")
                batch[cid] = approval
            approvals.update(batch)
        except (ValueError, KeyError, OSError, TypeError, yaml.YAMLError) as exc:
            errors.append(f"editorial {mid}: {exc}")
    return approvals, errors, checked


def editorial_verification_matches(record, claim, approval, root):
    path = Path(record["command_or_audit"])
    if not path.is_absolute():
        path = Path(root) / path
    return (record["method"] == "editorial_impact_review"
            and record["claim_revision"] == approval["member"]["to_revision"]
            and record["outcome"] == "PASS"
            and record["verifier"] == approval["review"]["verifier"]
            and record["scope"] == claim["scope"]["description"]
            and path.resolve() == approval["review_path"].resolve()
            and all(record["artifact_hashes"].get(aid) == sha for aid, sha in approval["bindings"].items()))


def editorial_change_allowed(old, new, approval):
    """Only exact assumptions plus strictly limited revision bookkeeping."""
    if approval is None or old != approval["old"]:
        return False
    member = approval["member"]
    if old["revision"] != member["from_revision"] or new["revision"] != member["to_revision"]:
        return False
    if old["assumptions"] != member["old_assumptions"] or new["assumptions"] != member["new_assumptions"]:
        return False
    allowed = {"assumptions", "revision", "updated_at", "evidence", "verification", "dependencies"}
    if any(new[field] != value for field, value in old.items() if field not in allowed):
        return False
    if any(aid not in old["evidence"] and aid not in approval["bindings"] for aid in new["evidence"]):
        return False
    # Updating pins is ordinary dependent-impact bookkeeping, not authority to
    # introduce/delete mathematical premises or change their relation.
    old_deps = {(d["id"], d["relation"]): d["revision"] for d in old["dependencies"]}
    new_deps = {(d["id"], d["relation"]): d["revision"] for d in new["dependencies"]}
    return old_deps.keys() == new_deps.keys() and all(new_deps[k] >= old_deps[k] for k in old_deps)


def validate(data, root, schema, hash_mode="available", previous=None):
    errors, skipped, checked = [], [], []
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for error in sorted(validator.iter_errors(data), key=lambda e: str(list(e.path))):
        errors.append(f"schema {list(error.path)}: {error.message}")
    if errors:
        return {"valid": False, "errors": errors, "skipped": skipped, "hashes_checked": checked,
                "progress": {"trusted": False, "reason": "Ledger failed schema validation; no claim totals generated"}}

    def indexed(items, label):
        result = {}
        for item in items:
            if item["id"] in result:
                errors.append(f"duplicate {label} id: {item['id']}")
            result[item["id"]] = item
        return result

    archives = indexed(data["archives"], "archive")
    artifacts = indexed(data["artifacts"], "artifact")
    claims = indexed(data["claims"], "claim")
    editorial, editorial_errors, editorial_hashes = check_editorial_migrations(data, root, artifacts, claims)
    errors.extend(editorial_errors)
    checked.extend(editorial_hashes)
    historical = [a for a in archives.values() if a["repository"].removesuffix(".git") == "https://github.com/YesterdaysLemon/conway-99-research" and a["commit"] == "85e705cc6c2a14d123120c93a847e30aaab1789e" and a["path"] == "CLAIMS.yaml"]
    if not historical:
        errors.append("archives: missing immutable historical registry repository/commit/path reference")
    for artifact in artifacts.values():
        aid = artifact["id"]
        if artifact["availability"] == "PUBLIC" and (not artifact["path"] or not artifact["sha256"] or not artifact["retrieval"]):
            errors.append(f"{aid}: PUBLIC requires path, hash, and retrieval instructions")
        if artifact["availability"] != "PUBLIC" and not artifact["unavailable_reason"]:
            errors.append(f"{aid}: nonpublic artifact requires unavailable_reason")
        if (artifact["path"] is None or artifact["sha256"] is None or artifact["retrieval"] is None) and not artifact["unavailable_reason"]:
            errors.append(f"{aid}: null artifact field requires unavailable_reason")
        if aid in editorial_hashes:
            # Mandatory migration authentication has already checked these bytes,
            # even in modes that would otherwise skip local or all hash checks.
            continue
        if hash_mode == "none":
            skipped.append(f"hash {aid}: hash verification disabled")
            continue
        if artifact["availability"] == "MISSING":
            skipped.append(f"hash {aid}: artifact declared MISSING")
            continue
        if hash_mode == "public" and artifact["availability"] != "PUBLIC":
            skipped.append(f"hash {aid}: LOCAL_ONLY excluded from public replay")
            continue
        path = Path(artifact["path"]) if artifact["path"] else None
        if path is not None and not path.is_absolute():
            path = Path(root) / path
        if path is None or not path.is_file():
            if artifact["availability"] == "PUBLIC":
                errors.append(f"{aid}: PUBLIC artifact not present; retrieve it before hash checking")
            else:
                skipped.append(f"hash {aid}: LOCAL_ONLY unavailable on this machine")
        elif artifact["sha256"] is None:
            errors.append(f"{aid}: present artifact has no expected hash")
        elif digest(path) != artifact["sha256"]:
            errors.append(f"{aid}: SHA-256 mismatch")
        else:
            checked.append(aid)

    aliases = set()
    for cid, claim in claims.items():
        if datetime.fromisoformat(claim["updated_at"].replace("Z", "+00:00")) < datetime.fromisoformat(claim["created_at"].replace("Z", "+00:00")):
            errors.append(f"{cid}: updated_at precedes created_at")
        for field in ("external_source", "reproducibility"):
            if claim[field] is None and not claim["unknowns"].get(field):
                errors.append(f"{cid}: null {field} requires unknowns.{field} reason (including not applicable)")
        source = claim["external_source"]
        if source is not None:
            if source["archive_id"] not in archives:
                errors.append(f"{cid}: unknown archive {source['archive_id']}")
            identity = (source["archive_id"], source["original_claim_id"])
            if identity in aliases:
                errors.append(f"{cid}: duplicate imported source alias {identity}")
            aliases.add(identity)
            if "@" not in cid or ":" not in cid:
                errors.append(f"{cid}: imported claim must use a namespaced id")
        for aid in claim["evidence"]:
            if aid not in artifacts:
                errors.append(f"{cid}: broken evidence reference {aid}")
        reproducibility = claim["reproducibility"]
        if "COMPUTED" in claim["basis"] and not reproducibility:
            errors.append(f"{cid}: COMPUTED basis requires a reproducibility manifest")
        if reproducibility and reproducibility["manifest"] not in claim["evidence"]:
            errors.append(f"{cid}: reproducibility manifest must be listed in evidence")
        seen_dependencies = set()
        for dependency in claim["dependencies"]:
            did = dependency["id"]
            identity = (did, dependency["relation"])
            if identity in seen_dependencies:
                errors.append(f"{cid}: duplicate dependency {identity}")
            seen_dependencies.add(identity)
            if did not in claims:
                errors.append(f"{cid}: broken dependency reference {did}")
            elif claims[did]["revision"] != dependency["revision"]:
                errors.append(f"{cid}: dependency revision does not match {did}")
            elif claim["status"] == "VERIFIED" and claim["review_state"] == "CLEAR":
                parent = claims[did]
                if parent["review_state"] != "CLEAR":
                    errors.append(f"{cid}: current VERIFIED use of {did} requiring impact review")
                if dependency["relation"] != "premise" and parent["status"] != "VERIFIED":
                    errors.append(f"{cid}: unestablished non-premise dependency {did}")
                if dependency["relation"] == "premise" and not claim["assumptions"]:
                    errors.append(f"{cid}: conditional premise must be explicit in assumptions")
        successful = []
        for verification in claim["verification"]:
            if verification["method"] == "editorial_impact_review" and not (
                    cid in editorial and editorial_verification_matches(verification, claim, editorial[cid], root)):
                errors.append(f"{cid}: editorial verification lacks exact authenticated migration approval")
            if verification["claim_revision"] > claim["revision"]:
                errors.append(f"{cid}: verification bound to a future revision")
            for aid, sha in verification["artifact_hashes"].items():
                if aid not in artifacts:
                    errors.append(f"{cid}: verification references unknown artifact {aid}")
                elif artifacts[aid]["sha256"] != sha:
                    errors.append(f"{cid}: verification hash differs from artifact {aid}; preserve old artifact identity separately")
            if verification["claim_revision"] == claim["revision"] and verification["outcome"] == "PASS" and verification["method"] != "repeated_execution":
                successful.append(verification)
        if claim["status"] == "VERIFIED" and claim["review_state"] == "CLEAR":
            if not successful:
                errors.append(f"{cid}: VERIFIED requires independent PASS bound to this revision")
            if "COMPUTED" in claim["basis"] and not any(v["artifact_hashes"] for v in successful):
                errors.append(f"{cid}: computed VERIFIED requires independently checked artifact hashes")
        if claim["status"] == "REFUTED" and not claim["evidence"]:
            errors.append(f"{cid}: REFUTED requires evidence against its exact statement")
        if claim["scope"]["target_resolution"] != "NONE" and not claim["scope"]["unrestricted_target"]:
            errors.append(f"{cid}: target resolution must cover unrestricted target")

    # Imported aliases are checked against the immutable Git blob, never against
    # historical labels as evidence of a new independent verification.
    for archive_id, original_id in aliases:
        archive = archives.get(archive_id)
        if archive not in historical:
            errors.append(f"archive alias {archive_id}:{original_id}: version 1 supports only the pinned historical source")
            continue
        try:
            result = subprocess.run(["git", "-C", str(Path(root) / "external_conway99_research"), "show", f"{archive['commit']}:{archive['path']}"], capture_output=True, text=True, encoding="utf-8", check=True)
            archived = yaml.load(result.stdout, Loader=UniqueKeyLoader)
            if sum(c["id"] == original_id for c in archived["claims"]) != 1:
                errors.append(f"archive alias {archive_id}:{original_id}: original id does not resolve uniquely")
        except (OSError, subprocess.CalledProcessError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"archive alias {archive_id}:{original_id}: immutable source unavailable: {exc}")

    colors = {}
    def visit(cid, trail):
        if colors.get(cid) == 1:
            errors.append("dependency cycle: " + " -> ".join(trail + [cid]))
            return
        if colors.get(cid) == 2:
            return
        colors[cid] = 1
        for dependency in claims[cid]["dependencies"]:
            if dependency["id"] in claims:
                visit(dependency["id"], trail + [cid])
        colors[cid] = 2
    for cid in claims:
        visit(cid, [])

    target = data["target"]
    for cid in target["supporting_claims"]:
        if cid not in claims:
            errors.append(f"target: broken supporting claim {cid}")
    if target["status"] != "UNKNOWN":
        direction = target["status"].removeprefix("CANDIDATE_")
        if not any(cid in claims and claims[cid]["status"] == "VERIFIED" and claims[cid]["review_state"] == "CLEAR" and claims[cid]["scope"]["target_resolution"] == direction for cid in target["supporting_claims"]):
            errors.append("target: candidate resolution requires current internally VERIFIED unrestricted supporting claim")
    if previous is not None:
        errors.extend(check_impact(previous, data, editorial))
    skipped.append("expensive mathematical replay, SAT/UNSAT proof checking, literature review, and reviewer-independence audit: not performed by registry validation")
    return {"valid": not errors, "errors": errors, "skipped": skipped, "hashes_checked": checked,
            "progress": progress(data, trusted=not errors)}


def check_impact(previous, current, editorial=None):
    """Conservative edit gate; previous revisions remain available in Git."""
    errors = []
    editorial = editorial or {}
    old_migrations = {m["id"]: m for m in previous.get("editorial_migrations", [])}
    new_migrations = {m["id"]: m for m in current.get("editorial_migrations", [])}
    for mid, old_migration in old_migrations.items():
        if new_migrations.get(mid) != old_migration:
            errors.append(f"impact editorial {mid}: preserve immutable migration record")
    old_claims = {c["id"]: c for c in previous["claims"]}
    new_claims = {c["id"]: c for c in current["claims"]}
    old_artifacts = {a["id"]: a for a in previous["artifacts"]}
    new_artifacts = {a["id"]: a for a in current["artifacts"]}
    changed_artifacts = {aid for aid, old in old_artifacts.items() if aid not in new_artifacts or old["sha256"] != new_artifacts[aid]["sha256"]}
    changed = set()
    for cid, old in old_claims.items():
        if cid not in new_claims:
            errors.append(f"impact {cid}: preserve existing claim records; do not delete")
            changed.add(cid)
            continue
        new = new_claims[cid]
        if new["revision"] < old["revision"]:
            errors.append(f"impact {cid}: revision decreased")
        mathematical_change = any(new[field] != old[field] for field in ("statement", "scope", "kind"))
        assumption_change = new["assumptions"] != old["assumptions"]
        if mathematical_change or (assumption_change and not editorial_change_allowed(old, new, editorial.get(cid))):
            errors.append(f"impact {cid}: changed mathematical statement/scope/assumptions requires new stable id (editorial corrections require manual migration)")
        material = any(new[field] != old[field] for field in ("dependencies", "basis", "evidence", "reproducibility", "external_source"))
        if material or any(aid in changed_artifacts for aid in old["evidence"]) or new["revision"] != old["revision"]:
            changed.add(cid)
        if material and new["revision"] == old["revision"]:
            errors.append(f"impact {cid}: changed evidence/dependencies requires revision increment")
        if any(record not in new["verification"] for record in old["verification"]):
            errors.append(f"impact {cid}: historical verification record removed or rewritten")
    affected = set(changed)
    while True:
        expanded = affected | {cid for cid, claim in new_claims.items() if any(d["id"] in affected for d in claim["dependencies"])}
        if expanded == affected:
            break
        affected = expanded
    for cid in affected & new_claims.keys():
        claim = new_claims[cid]
        old = old_claims.get(cid)
        def current_independent_pass(record):
            return any(v["claim_revision"] == record["revision"] and v["outcome"] == "PASS" and v["method"] != "repeated_execution" for v in record["verification"])
        if old is None:
            # A new statement has no previous revision to increment. Its first
            # current-revision review can establish it, provided changed inputs
            # are pinned to independently checked, current dependency records.
            fresh_check = current_independent_pass(claim) and all(
                d["id"] in new_claims and d["revision"] == new_claims[d["id"]]["revision"]
                and (d["id"] not in affected or (
                    new_claims[d["id"]]["status"] == "VERIFIED"
                    and new_claims[d["id"]]["review_state"] == "CLEAR"
                    and current_independent_pass(new_claims[d["id"]])))
                for d in claim["dependencies"])
        else:
            fresh_check = claim["revision"] > old["revision"] and any(v not in old["verification"] and v["claim_revision"] == claim["revision"] and v["outcome"] == "PASS" and v["method"] != "repeated_execution" for v in claim["verification"])
        if claim["status"] == "VERIFIED" and claim["review_state"] == "CLEAR" and not fresh_check:
            errors.append(f"impact {cid}: changed dependency/evidence requires NEEDS_RECHECK or new independently checked revision")
    return errors


def progress(data, trusted=False):
    counts = Counter(c["status"] for c in data["claims"])
    review = Counter(c["review_state"] for c in data["claims"])
    verified = [c["id"] for c in data["claims"] if c["status"] == "VERIFIED" and c["review_state"] == "CLEAR"]
    return {"trusted": trusted,
            "reason": "Registry bookkeeping validation passed; not mathematical verification" if trusted else "Invalid ledger; displayed counts are untrusted diagnostics and must not be reported as verified progress",
            "population": "current root ledger claim records (not graphs or search branches)",
            "claim_records": len(data["claims"]), "status_counts": dict(sorted(counts.items())),
            "review_state_counts": dict(sorted(review.items())), "current_verified_count": len(verified),
            "current_verified_claim_ids": verified, "target_resolution": data["target"]["status"],
            "external_review": data["target"]["external_review"],
            "coverage": "Overall search coverage: UNKNOWN; no validated denominator.",
            "execution_state": "UNKNOWN; registry inspection is not live process observation"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", nargs="?", default="CLAIMS.yaml")
    parser.add_argument("--schema", default="docs/claims.schema.json")
    parser.add_argument("--root", default=".")
    parser.add_argument("--hashes", choices=("none", "public", "available"), default="available")
    parser.add_argument("--previous", help="previous immutable ledger for conservative impact review")
    parser.add_argument("--out", help="write machine-readable validation/progress report")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    def rooted(value):
        path = Path(value)
        return path if path.is_absolute() else root / path
    ledger_path = rooted(args.ledger)
    schema_path = rooted(args.schema)
    previous_path = rooted(args.previous) if args.previous else None
    try:
        data = read_ledger(ledger_path)
        previous = read_ledger(previous_path) if previous_path else None
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        if previous is not None:
            prior_errors = list(jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(previous))
            if prior_errors:
                raise ValueError("previous ledger fails current schema; explicit migration is required")
        result = validate(data, root, schema, args.hashes, previous)
    except (ValueError, OSError, yaml.YAMLError) as exc:
        result = {"valid": False, "errors": [str(exc)], "progress": {"trusted": False, "reason": "Ledger could not be validated; no claim totals generated"}}
    provenance = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command_argv": [sys.executable, *sys.argv], "working_directory": str(Path.cwd()),
        "repository_root": str(root), "hash_mode": args.hashes,
        "tool_versions": {"python": platform.python_version(), "PyYAML": version("PyYAML"), "jsonschema": version("jsonschema")},
        "platform": platform.platform(), "source_commit": None, "source_dirty": None,
        "input_hashes": {}, "unknowns": {},
    }
    for label, path in (("ledger", ledger_path), ("schema", schema_path), ("checker", Path(__file__).resolve()), ("previous_ledger", previous_path)):
        if path is not None and path.is_file():
            provenance["input_hashes"][label] = {"path": str(path), "sha256": digest(path)}
        else:
            provenance["input_hashes"][label] = None
            provenance["unknowns"][label] = "Not supplied" if path is None else "File unavailable"
    try:
        provenance["source_commit"] = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        provenance["source_dirty"] = bool(subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip())
    except (OSError, subprocess.CalledProcessError) as exc:
        provenance["unknowns"]["source_commit_or_dirty"] = str(exc)
    result["provenance"] = provenance
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        try:
            with Path(args.out).open("x", encoding="utf-8") as handle:
                handle.write(rendered)
        except FileExistsError:
            print(f"Refusing to overwrite existing report: {args.out}", file=sys.stderr)
            return 2
    print(rendered, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())

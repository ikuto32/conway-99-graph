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
        errors.extend(check_impact(previous, data))
    skipped.append("expensive mathematical replay, SAT/UNSAT proof checking, literature review, and reviewer-independence audit: not performed by registry validation")
    return {"valid": not errors, "errors": errors, "skipped": skipped, "hashes_checked": checked,
            "progress": progress(data, trusted=not errors)}


def check_impact(previous, current):
    """Conservative edit gate; previous revisions remain available in Git."""
    errors = []
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
        if any(new[field] != old[field] for field in ("statement", "scope", "kind", "assumptions")):
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

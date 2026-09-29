"""Adversarial registry controls; these test bookkeeping, not Conway-99."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from validate_claims import read_ledger, validate, canonical_claim_digest


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "artifact.json").write_text('{"result": "fixture"}\n', encoding="utf-8")
        self.sha = hashlib.sha256((self.root / "artifact.json").read_bytes()).hexdigest()
        self.schema = json.loads((Path(__file__).resolve().parents[1] / "docs/claims.schema.json").read_text())
        self.claim = {
            "id": "C-FIXTURE-001", "revision": 1, "statement": "The fixture artifact has the recorded digest.",
            "kind": "empirical/engineering result", "basis": ["COMPUTED"], "status": "VERIFIED", "review_state": "CLEAR",
            "scope": {"description": "One test artifact only", "unrestricted_target": False, "target_resolution": "NONE"},
            "assumptions": [], "dependencies": [], "evidence": ["fixture"],
            "verification": [{"claim_revision": 1, "verifier": "synthetic independent test fixture", "method": "independent_artifact_check", "command_or_audit": "synthetic control, not a real verification record", "timestamp": "2026-09-17T00:00:00Z", "outcome": "PASS", "scope": "fixture bytes", "artifact_hashes": {"fixture": self.sha}, "shared_components": [], "controls": ["synthetic positive control"], "limitations": ["No mathematical claim"]}],
            "limitations": ["Synthetic test only"], "created_at": "2026-09-17T00:00:00Z", "updated_at": "2026-09-17T00:00:00Z",
            "unknowns": {"external_source": "Not imported"}, "external_source": None, "reproducibility": {"manifest": "fixture"}
        }
        self.data = {
            "schema_version": 1, "updated_at": "2026-09-17T00:00:00Z",
            "archives": [{"id": "legacy", "repository": "https://github.com/YesterdaysLemon/conway-99-research", "commit": "85e705cc6c2a14d123120c93a847e30aaab1789e", "path": "CLAIMS.yaml"}],
            "artifacts": [{"id": "fixture", "path": "artifact.json", "sha256": self.sha, "availability": "PUBLIC", "retrieval": "synthetic checked-in fixture", "unavailable_reason": None}],
            "claims": [self.claim], "target": {"status": "UNKNOWN", "supporting_claims": [], "external_review": "No resolution", "overall_search_coverage": None, "coverage_reason": "No frozen universe"}
        }

    def tearDown(self):
        self.temp.cleanup()

    def check(self, valid=False, contains=None, **kwargs):
        result = validate(self.data, self.root, self.schema, **kwargs)
        self.assertEqual(result["valid"], valid, result)
        if contains:
            self.assertTrue(any(contains in error for error in result["errors"]), result)
        return result

    def test_positive_fixture(self):
        result = self.check(valid=True)
        self.assertEqual(result["hashes_checked"], ["fixture"])
        self.assertEqual(result["progress"]["current_verified_count"], 1)
        self.assertEqual(result["progress"]["target_resolution"], "UNKNOWN")

    def test_duplicate_yaml_key(self):
        path = self.root / "bad.yaml"
        path.write_text("a: 1\na: 2\n")
        with self.assertRaisesRegex(ValueError, "duplicate YAML key"):
            read_ledger(path)

    def test_duplicate_ids(self):
        self.data["claims"].append(copy.deepcopy(self.claim))
        self.check(contains="duplicate claim id")

    def test_bad_state(self):
        self.claim["status"] = "PROVED"
        self.check(contains="schema")

    def test_timezone_required(self):
        self.claim["updated_at"] = "2026-09-17T00:00:00"
        self.check(contains="schema")

    def test_corrupt_artifact(self):
        (self.root / "artifact.json").write_bytes(b"corrupt")
        self.check(contains="SHA-256 mismatch")

    def test_missing_public_is_fatal(self):
        (self.root / "artifact.json").unlink()
        self.check(contains="PUBLIC artifact not present")

    def test_local_absence_explicit_skip(self):
        (self.root / "artifact.json").unlink()
        self.data["artifacts"][0].update(availability="LOCAL_ONLY", unavailable_reason="not published")
        result = self.check(valid=True)
        self.assertTrue(any("LOCAL_ONLY unavailable" in s for s in result["skipped"]))

    def test_missing_keeps_historical_verification(self):
        self.data["artifacts"][0].update(availability="MISSING", unavailable_reason="Lost after historical verification", path=None, retrieval=None)
        result = self.check(valid=True)
        self.assertTrue(any("declared MISSING" in s for s in result["skipped"]))

    def test_null_reason_required(self):
        self.claim["unknowns"] = {}
        self.check(contains="requires unknowns")

    def test_repeated_execution_cannot_promote(self):
        self.claim["verification"][0]["method"] = "repeated_execution"
        self.check(contains="requires independent PASS")

    def test_stale_revision_cannot_promote(self):
        self.claim["revision"] = 2
        self.check(contains="requires independent PASS")

    def test_quarantine_excluded_from_totals(self):
        self.claim["review_state"] = "QUARANTINED"
        self.assertEqual(self.check(valid=True)["progress"]["current_verified_count"], 0)

    def test_stale_verification_allowed_pending_impact_review(self):
        self.claim.update(revision=2, review_state="NEEDS_RECHECK")
        self.assertEqual(self.check(valid=True)["progress"]["current_verified_count"], 0)

    def test_hash_binding(self):
        self.claim["verification"][0]["artifact_hashes"]["fixture"] = "0" * 64
        self.check(contains="verification hash differs")

    def test_broken_dependency(self):
        self.claim["dependencies"] = [{"id": "absent", "revision": 1, "relation": "uses_result"}]
        self.check(contains="broken dependency reference")

    def test_revision_pin(self):
        self.claim["dependencies"] = [{"id": self.claim["id"], "revision": 2, "relation": "uses_result"}]
        self.check(contains="dependency revision does not match")

    def test_cycle(self):
        other = copy.deepcopy(self.claim)
        other["id"] = "C-FIXTURE-002"
        self.data["claims"].append(other)
        self.claim["dependencies"] = [{"id": other["id"], "revision": 1, "relation": "uses_result"}]
        other["dependencies"] = [{"id": self.claim["id"], "revision": 1, "relation": "uses_result"}]
        self.check(contains="dependency cycle")

    def test_conditional_premise_is_not_unconditional(self):
        premise = copy.deepcopy(self.claim)
        premise.update(id="C-PREMISE", status="UNKNOWN", verification=[])
        self.data["claims"].append(premise)
        self.claim["dependencies"] = [{"id": premise["id"], "revision": 1, "relation": "premise"}]
        self.check(contains="conditional premise must be explicit")
        self.claim["assumptions"] = ["If C-PREMISE holds"]
        self.check(valid=True)

    def test_refuted_needs_evidence(self):
        self.claim.update(status="REFUTED", evidence=[], reproducibility=None)
        self.check(contains="REFUTED requires evidence")

    def test_local_exclusion_cannot_resolve_target(self):
        self.data["target"].update(status="CANDIDATE_NEGATIVE", supporting_claims=[self.claim["id"]])
        self.check(contains="candidate resolution requires")

    def test_impact_artifact_change(self):
        previous = copy.deepcopy(self.data)
        (self.root / "artifact.json").write_bytes(b"new")
        sha = hashlib.sha256(b"new").hexdigest()
        self.data["artifacts"][0]["sha256"] = sha
        self.claim["verification"][0]["artifact_hashes"]["fixture"] = sha
        self.check(previous=previous, contains="requires NEEDS_RECHECK")

    def test_impact_dependency_requires_recheck(self):
        other = copy.deepcopy(self.claim)
        other["id"] = "C-FIXTURE-002"
        other["dependencies"] = [{"id": self.claim["id"], "revision": 1, "relation": "uses_result"}]
        self.data["claims"].append(other)
        previous = copy.deepcopy(self.data)
        self.claim["revision"] = 2
        self.claim["review_state"] = "NEEDS_RECHECK"
        other["dependencies"][0]["revision"] = 2
        other["revision"] = 2
        self.check(previous=previous, contains="changed dependency/evidence requires")

    def test_impact_preserves_checks(self):
        previous = copy.deepcopy(self.data)
        self.claim["verification"][0]["scope"] = "rewritten"
        self.check(previous=previous, contains="historical verification record removed or rewritten")

    def test_impact_scope_requires_new_claim(self):
        previous = copy.deepcopy(self.data)
        self.claim["scope"]["description"] = "All graphs"
        self.check(previous=previous, contains="requires new stable id")

    def test_unreviewed_assumption_edit_still_requires_new_claim(self):
        previous = copy.deepcopy(self.data)
        self.claim["assumptions"] = ["Assume an automorphism"]
        self.claim["revision"] = 2
        self.claim["review_state"] = "NEEDS_RECHECK"
        self.check(previous=previous, contains="requires new stable id")

    def new_dependent_fixture(self):
        previous = copy.deepcopy(self.data)
        self.claim["revision"] = 2
        current_check = copy.deepcopy(self.claim["verification"][0])
        current_check["claim_revision"] = 2
        self.claim["verification"].append(current_check)
        downstream = copy.deepcopy(self.claim)
        downstream.update(id="C-NEW-DEPENDENT", revision=1, verification=[copy.deepcopy(previous["claims"][0]["verification"][0])], dependencies=[{"id": self.claim["id"], "revision": 2, "relation": "uses_result"}])
        self.data["claims"].append(downstream)
        return previous, downstream

    def test_new_independently_verified_dependent_of_revised_claim(self):
        previous, _ = self.new_dependent_fixture()
        self.check(valid=True, previous=previous)

    def test_new_dependent_missing_independent_review(self):
        previous, downstream = self.new_dependent_fixture()
        downstream["verification"] = []
        self.check(previous=previous, contains="impact C-NEW-DEPENDENT")

    def test_new_dependent_of_unchecked_revised_claim(self):
        previous, _ = self.new_dependent_fixture()
        self.claim["verification"].pop()
        self.check(previous=previous, contains="impact C-NEW-DEPENDENT")

    def test_new_dependent_stale_revision_pin(self):
        previous, downstream = self.new_dependent_fixture()
        downstream["dependencies"][0]["revision"] = 1
        self.check(previous=previous, contains="impact C-NEW-DEPENDENT")

    def test_invalid_progress_is_explicitly_untrusted(self):
        self.claim["verification"] = []
        result = self.check(contains="requires independent PASS")
        self.assertFalse(result["progress"]["trusted"])

    def test_valid_progress_bookkeeping_flag(self):
        self.assertTrue(self.check(valid=True)["progress"]["trusted"])

    def test_output_does_not_overwrite_evidence(self):
        out = self.root / "existing-report.json"
        original = b"immutable historical report"
        out.write_bytes(original)
        ledger = self.root / "ledger.json"
        ledger.write_text(json.dumps(self.data))
        repo = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, str(repo / "acceleration/validate_claims.py"), str(ledger), "--root", str(self.root), "--schema", str(repo / "docs/claims.schema.json"), "--out", str(out)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Refusing to overwrite", result.stderr)
        self.assertEqual(out.read_bytes(), original)


class EditorialMigrationTests(unittest.TestCase):
    """Use the actual immutable17claim review, never a fake trusted-review flag.

    All mutation ledgers and artifacts live in a temporary directory. Extra
    dependents are quarantined, not promoted with invented independent checks.
    """
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.review_name = "acceleration/results/20260930_independent_review/automorphism_assumption_editorial/summary.json"
        cls.review_bytes = (cls.repo / cls.review_name).read_bytes()
        cls.review = json.loads(cls.review_bytes)
        cls.snapshot_name = cls.review["reviewed_ledger_snapshot"]
        cls.snapshot_bytes = (cls.repo / cls.snapshot_name).read_bytes()
        cls.previous_template = read_ledger(cls.repo / cls.snapshot_name)
        cls.schema = json.loads((cls.repo / "docs/claims.schema.json").read_text())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name, raw in ((self.review_name, self.review_bytes), (self.snapshot_name, self.snapshot_bytes)):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.previous = copy.deepcopy(self.previous_template)
        self.data = copy.deepcopy(self.previous)
        self.data["schema_version"] = 2
        self.review_id, self.snapshot_id = "editorial-review-fixture", "editorial-snapshot-fixture"
        self.review_sha = hashlib.sha256(self.review_bytes).hexdigest()
        self.snapshot_sha = hashlib.sha256(self.snapshot_bytes).hexdigest()
        for aid, name, sha in ((self.review_id, self.review_name, self.review_sha), (self.snapshot_id, self.snapshot_name, self.snapshot_sha)):
            self.data["artifacts"].append(dict(id=aid, path=name, sha256=sha, availability="LOCAL_ONLY",
                                             retrieval="Temporary exact copy of immutable review fixture", unavailable_reason="Synthetic migration ledger only"))
        self.migration = dict(id="M-EDITORIAL-FIXTURE", version=1, kind="REVIEWED_ASSUMPTION_CLARIFICATION",
            review_artifact=dict(artifact=self.review_id, sha256=self.review_sha),
            snapshot_artifact=dict(artifact=self.snapshot_id, sha256=self.snapshot_sha), claims=[])
        self.data["editorial_migrations"] = [self.migration]
        self.claims = {c["id"]: c for c in self.data["claims"]}
        self.old_claims = {c["id"]: c for c in self.previous["claims"]}
        self.selected = {r["claim_id"] for r in self.review["records"]}
        self.affected = set(self.selected)
        while True:
            expanded = self.affected | {cid for cid, c in self.claims.items() if any(d["id"] in self.affected for d in c["dependencies"])}
            if expanded == self.affected:
                break
            self.affected = expanded
        for record in self.review["records"]:
            cid = record["claim_id"]
            old, current = self.old_claims[cid], self.claims[cid]
            self.migration["claims"].append(dict(claim_id=cid, from_revision=old["revision"], to_revision=old["revision"]+1,
                old_claim_sha256=canonical_claim_digest(old), old_assumptions=copy.deepcopy(old["assumptions"]),
                new_assumptions=copy.deepcopy(record["recommended_assumptions"])))
            current["assumptions"] = copy.deepcopy(record["recommended_assumptions"])
            current["evidence"] += [self.review_id, self.snapshot_id]
            current["verification"].append(dict(claim_revision=old["revision"]+1, verifier=self.review["verifier"],
                method="editorial_impact_review", command_or_audit=self.review_name, timestamp="2026-09-30T00:00:00Z", outcome="PASS",
                scope=current["scope"]["description"], artifact_hashes={self.review_id:self.review_sha, self.snapshot_id:self.snapshot_sha},
                shared_components=["Immutable prior audits, not rerun"], controls=["Exact old/new approval binding"], limitations=["Editorial fixture only"]))
        for cid in self.affected:
            self.claims[cid]["revision"] += 1
            if cid not in self.selected:
                self.claims[cid]["review_state"] = "NEEDS_RECHECK"
        # A selected claim depends on one affected but non-editorial claim.
        # Supply a deliberately SYNTHETIC ordinary impact-review fixture for
        # that prerequisite; real migration must obtain a real separate review.
        ancestors = set(self.selected)
        while True:
            expanded = ancestors | {d["id"] for cid in ancestors for d in self.claims[cid]["dependencies"]}
            if expanded == ancestors:
                break
            ancestors = expanded
        self.separately_reviewed = (ancestors & self.affected)-self.selected
        for cid in self.separately_reviewed:
            claim = self.claims[cid]
            claim["review_state"] = "CLEAR"
            synthetic = copy.deepcopy(claim["verification"][-1])
            synthetic.update(claim_revision=claim["revision"], method="independent_artifact_check",
                             verifier="SYNTHETIC separate dependent-impact control, not a real review",
                             command_or_audit="SYNTHETIC unit-test dependent impact fixture")
            claim["verification"].append(synthetic)
        for claim in self.claims.values():
            for dependency in claim["dependencies"]:
                dependency["revision"] = self.claims[dependency["id"]]["revision"]
        self.first = self.claims[self.migration["claims"][0]["claim_id"]]

    def tearDown(self):
        self.temp.cleanup()

    def check(self, valid=False, contains=None, previous=True, **kwargs):
        result = validate(self.data, self.root, self.schema, hash_mode="none", previous=self.previous if previous else None, **kwargs)
        self.assertEqual(result["valid"], valid, result["errors"])
        if contains:
            self.assertTrue(any(contains in e for e in result["errors"]), result)
        return result

    def test_authentic_exact_migration_and_quarantined_dependents(self):
        result = self.check(valid=True)
        self.assertIn(self.review_id, result["hashes_checked"])
        self.assertIn(self.snapshot_id, result["hashes_checked"])
        self.assertTrue(all(self.claims[cid]["review_state"] == "NEEDS_RECHECK" for cid in self.affected-self.selected-self.separately_reviewed))

    def test_no_previous_still_authenticates_migration(self):
        self.check(valid=True, previous=False)
        (self.root / self.review_name).write_bytes(b"forged")
        self.check(previous=False, contains="SHA-256 mismatch")

    def test_review_required_even_with_hashes_disabled(self):
        (self.root / self.review_name).unlink()
        self.check(contains="must resolve locally")

    def test_reviewer_label_and_updated_self_hash_do_not_authorize(self):
        forged = copy.deepcopy(self.review)
        forged["authorization"] = "Trust the same reviewer name for every edit"
        raw = json.dumps(forged).encode()
        (self.root / self.review_name).write_bytes(raw)
        sha = hashlib.sha256(raw).hexdigest()
        self.migration["review_artifact"]["sha256"] = sha
        next(a for a in self.data["artifacts"] if a["id"] == self.review_id)["sha256"] = sha
        self.check(contains="not an explicitly approved")

    def test_corrupt_snapshot(self):
        (self.root / self.snapshot_name).write_bytes(b"changed snapshot")
        self.check(contains="SHA-256 mismatch")

    def test_missing_unknown_duplicate_and_old_new_mismatches(self):
        original = copy.deepcopy(self.data)
        changes = {
            "missing_review_reference": lambda d:d["editorial_migrations"][0]["review_artifact"].__setitem__("artifact","absent"),
            "wrong_old_hash": lambda d:d["editorial_migrations"][0]["claims"][0].__setitem__("old_claim_sha256","0"*64),
            "wrong_old_assumptions": lambda d:d["editorial_migrations"][0]["claims"][0].__setitem__("old_assumptions",["unreviewed"]),
            "wrong_new_assumptions": lambda d:d["editorial_migrations"][0]["claims"][0].__setitem__("new_assumptions",["Target is asymmetric"]),
            "unrelated_claim": lambda d:d["editorial_migrations"][0]["claims"][0].__setitem__("claim_id","C-UNRELATED"),
            "missing_member": lambda d:d["editorial_migrations"][0]["claims"].pop(),
            "duplicate_member": lambda d:d["editorial_migrations"][0]["claims"].append(copy.deepcopy(d["editorial_migrations"][0]["claims"][0])),
            "wrong_old_revision": lambda d:d["editorial_migrations"][0]["claims"][0].__setitem__("from_revision",2),
            "wrong_new_revision": lambda d:d["editorial_migrations"][0]["claims"][0].__setitem__("to_revision",3),
            "duplicate_migration": lambda d:d["editorial_migrations"].append(copy.deepcopy(d["editorial_migrations"][0])),
        }
        for name, mutation in changes.items():
            with self.subTest(name=name):
                self.data = copy.deepcopy(original)
                mutation(self.data)
                self.check(contains="editorial")

    def test_duplicate_claim_across_different_migrations(self):
        duplicate = copy.deepcopy(self.migration)
        duplicate["id"] = "M-ANOTHER-ID"
        self.data["editorial_migrations"].append(duplicate)
        self.check(contains="multiply migrated")

    def test_migration_record_edit_is_rejected_on_later_revision(self):
        self.previous = copy.deepcopy(self.data)
        self.migration["id"] = "M-REWRITTEN-ID"
        self.check(contains="preserve immutable migration record")

    def test_actual_claim_unapproved_assumption_rejected(self):
        self.first["assumptions"].append("A target is asymmetric")
        self.check(contains="migration not applied")

    def test_same_or_skipped_revision_rejected(self):
        for revision in (1,3):
            with self.subTest(revision=revision):
                self.first["revision"] = revision
                self.check(contains="editorial" if revision==1 else "requires new stable id")

    def test_unrelated_field_change_cannot_use_exception(self):
        for field,value in (("statement","A broader theorem"),("scope",dict(description="All target graphs",unrestricted_target=True,target_resolution="NONE")),
                            ("kind","literature finding"),("basis",["CITED"]),("limitations",["deleted restrictions"]),
                            ("created_at","2020-01-01T00:00:00Z")):
            with self.subTest(field=field):
                old = copy.deepcopy(self.first[field])
                self.first[field] = value
                self.check(contains="cannot alter" if field in ("statement","scope","kind") else "requires new stable id")
                self.first[field] = old

    def test_dependency_relation_not_just_revision_is_rejected(self):
        self.first["dependencies"][0]["relation"] = "derived_from"
        self.check(contains="requires new stable id")

    def test_old_claim_must_exactly_match_reviewed_snapshot(self):
        next(c for c in self.previous["claims"] if c["id"] == self.first["id"])["limitations"].append("Different earlier claim")
        self.check(contains="requires new stable id")

    def test_current_editorial_record_cannot_be_faked(self):
        for field,value in (("verifier","same reviewer label without review binding"),("method","independent_artifact_check"),
                            ("command_or_audit","some-other-review.json"),("scope","another scope"),("artifact_hashes",{})):
            with self.subTest(field=field):
                row = self.first["verification"][-1]
                old = copy.deepcopy(row[field]); row[field] = value
                self.check(contains="exact editorial review record missing")
                row[field] = old

    def test_no_dependent_automatic_promotion(self):
        dependent = next(iter(self.affected-self.selected-self.separately_reviewed))
        self.claims[dependent]["review_state"] = "CLEAR"
        self.check(contains="changed dependency/evidence requires")

    def test_required_noneditorial_prerequisite_needs_its_own_review(self):
        dependent = next(iter(self.separately_reviewed))
        self.claims[dependent]["verification"].pop()
        self.check(contains="changed dependency/evidence requires")

    def test_historical_checks_and_migration_are_immutable(self):
        self.first["verification"].pop(0)
        self.check(contains="old verification evidence not preserved")

    def test_migration_removal_is_rejected_on_later_edit(self):
        self.previous = copy.deepcopy(self.data)
        self.data["editorial_migrations"] = []
        self.check(contains="preserve immutable migration record")

    def test_v1_cannot_opt_into_v2_exception(self):
        self.data["schema_version"] = 1
        self.check(contains="schema")

    def test_archived_schema_is_exact_version_one(self):
        path = self.repo / "docs/claims.schema.v1.json"
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), "3925277499e54e1233097cf4a5c059198f515a5a3335baf258600a9603960a6f")


if __name__ == "__main__":
    unittest.main()

"""Adversarial registry controls; these test bookkeeping, not Conway-99."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from validate_claims import read_ledger, validate


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


if __name__ == "__main__":
    unittest.main()

"""Add independently checked small integer certificates without widening a claim."""
from datetime import datetime, timezone
import copy
import json
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry


def main():
    audit = 'acceleration/results/20260917_independent_review/two_coordinate_small_certificate.json'
    assert shared.digest(audit) == '8073e240451c3b10be063542def48e7a51dbb9023a8067610e6fbdc7c852ba09'
    review = shared.load(audit)
    for p, h in review['inputs_sha256'].items():
        assert shared.digest(p) == h, p
    assert review['claim_revision'] == 2 and not review['statement_and_scope_changed']
    assert review['positive_certificates'] == 9 and review['distinct_original_choices'] == 89308
    root = shared.ROOT
    lp = root / 'CLAIMS.yaml'
    old = lp.read_bytes()
    ledger = registry.read_ledger(lp)
    merged = copy.deepcopy(ledger)
    cid = review['claim_id']
    claim = next(c for c in merged['claims'] if c['id'] == cid)
    assert claim['revision'] == 1
    dependents = [c['id'] for c in ledger['claims'] if any(d['id'] == cid for d in c['dependencies'])]
    assert not dependents, 'Dependent claims require separate impact review'
    folder = 'acceleration/results/20260917_two_coordinate_small_certificate/'
    evidence = {'two-small-audit': audit, 'two-small-manifest': folder + 'manifest.json', 'two-small-summary': folder + 'summary.json'}
    evidence.update({'two-small-D' + str(d): folder + f'denominator_{d:03}.json' for d in (1,2,4,8,16,32,64,128,256)})
    aa = [dict(id=i, path=p, sha256=shared.digest(p), availability='LOCAL_ONLY', retrieval='Workspace relative path, exact certificates and raw-neighborhood audit retained.', unavailable_reason='Not yet assigned a confirmed public commit.') for i,p in evidence.items()]
    merged['artifacts'].extend(aa)
    now = datetime.now(timezone.utc).isoformat()
    claim['revision'] = 2
    claim['updated_at'] = now
    claim['evidence'].extend(evidence)
    claim['verification'].append(dict(claim_revision=2, verifier='independent_verifier agent',
        method='independent_artifact_check', command_or_audit=audit, timestamp=review['completed_at'], outcome='PASS',
        scope=claim['scope']['description'], artifact_hashes={a['id']:a['sha256'] for a in aa},
        shared_components=review['shared_components'], controls=['All 9 deterministic rounding cases checked; raw-neighborhood maxima for all 89,308 choices per case.', 'Rounding, corrupted certificate and known-valid rook controls recorded in the audit.'], limitations=review['limitations']))
    merged['updated_at'] = now
    validation = registry.validate(merged, root, shared.load('docs/claims.schema.json'), 'available', ledger)
    assert validation['valid'], validation['errors']
    resume = root / 'acceleration/results/20260917_resume'
    snapshot = resume / 'claims_before_small_certificate_evidence.yaml'
    receipt = resume / 'small_certificate_evidence_registration.json'
    assert not snapshot.exists() and not receipt.exists() and lp.read_bytes() == old
    snapshot.write_bytes(old)
    lp.write_text(yaml.safe_dump(merged, sort_keys=False, width=110), encoding='utf-8')
    shared.save(receipt, dict(timestamp=now, command=[sys.executable,*sys.argv], cwd=str(root), registrar_sha256=shared.digest(__file__),
        claim_id=cid, previous_revision=1, new_revision=2, statement_scope_dependencies_unchanged=True,
        impact_review=dict(dependent_claims=dependents, existing_artifacts_changed=False, old_successful_checks_preserved=True),
        previous_ledger_sha256=shared.sha256(old).hexdigest(), ledger_sha256=shared.digest(lp), validation=validation,
        registrar_performs_mathematical_verification=False))
    print(json.dumps(dict(claim=cid, revision=2, ledger_sha256=shared.digest(lp))))


if __name__ == '__main__':
    main()

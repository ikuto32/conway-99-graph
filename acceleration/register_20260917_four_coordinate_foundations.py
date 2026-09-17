"""Register independently audited four-coordinate domains and necessary models."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import yaml
import register_20260917_v3_calibration_partial_claims as shared
import validate_claims as registry

BASE = 'acceleration/results/20260917_'
REV = BASE + 'independent_review/'
SPECS = [
    ('four-domains', 'four_matchings/summary.json', 'fb21f69b6e5785e0897bccb6965bfea75c171aad2e685b7d60966bc5c8019e73', 'partial_four_matchings', 'manifest.json', 'encoding'),
    ('four-moment', 'four_matching_moments.json', '9a8a4d0aaaf7caf06f1df0a4704b6d0acb4dc9449e5639d34395542e0451ca92', 'four_matching_moments', 'build_manifest.json', 'encoding'),
    ('four-filter', 'four_coordinate_matching_filter/summary.json', '6ee0eea6854f8e82e4067f60225f6c897908d5824f5d71c7d4564e21e86738b3', 'four_coordinate_matching_filter/run01', 'manifest.json', 'exclusion'),
    ('four-filtered-moment', 'four_matching_filtered_moments.json', '472b7f332a99560fd961d7b6a411edd5db619504c21dd6285470f579e0ba2c51', 'four_matching_filtered_moments', 'build_manifest.json', 'encoding'),
]


def main():
    root = shared.ROOT
    lp = root / 'CLAIMS.yaml'
    old = lp.read_bytes()
    ledger = registry.read_ledger(lp)
    resume = root / (BASE + 'resume')
    snapshot = resume / 'claims_before_four_coordinate_foundations.yaml'
    receipt = resume / 'four_coordinate_foundations_registration.json'
    assert not snapshot.exists() and not receipt.exists()
    now = datetime.now(timezone.utc).isoformat()
    artifacts, claims = [], []
    for prefix, audit, expected, folder, manifest, kind in SPECS:
        path = REV + audit
        assert shared.digest(path) == expected
        r = shared.load(path)
        for p, h in r['inputs_sha256'].items():
            assert shared.digest(p) == h, p
        assert r['claim_revision'] == 1 and r['status'].endswith('PASS')
        evidence = {prefix + '-audit': path, prefix + '-manifest': BASE + folder + '/' + manifest}
        deps = r.get('dependencies', [r['dependency']] if 'dependency' in r else [])
        statement = r.get('statement')
        if prefix == 'four-filter':
            assert r['counts']['original_count'] == 290460 and r['counts']['rejected_count'] == 59581
            assert r['counts']['surviving_count'] == 230879 and r['empty_domains'] == 0
            statement = ('For the 290,460 original center/domain-ID choices in the exact four-coordinate partial-K family, the necessary neighborhood perfect-matching test rejects exactly 59,581 and retains exactly 230,879. All 84 domains remain nonempty. Each rejected choice has no perfect matching among individually cap-permissible remaining neighborhood edges; every retained choice has a checked matching witness. Positive matching multiplicities are not claimed.')
            deps = [dict(id='C-PARTIAL-K-FOUR-COORDINATE-DOMAINS', revision=1, relation='coverage')]
        if 'moment' in prefix:
            assert r['complete_augmented_matrix_and_bounds_checked'] and r['chunk_identity_checked']
            for name in ('model.json', 'chunk_manifest.json'):
                evidence[prefix + '-' + name.replace('.', '-')] = BASE + folder + '/' + name
        assert statement
        aa = [dict(id=i, path=p, sha256=shared.digest(p), availability='LOCAL_ONLY', retrieval='Workspace relative path; raw domains and exact chunk companions are indexed by the audit and manifest.', unavailable_reason='No confirmed public commit assigned yet.') for i, p in evidence.items()]
        artifacts.extend(aa)
        limitations = r['limitations']
        scope = r['scope']
        claims.append(dict(id=r['claim_id'], revision=1, statement=statement, kind=kind,
            basis=['DERIVED', 'COMPUTED'], status='VERIFIED', review_state='CLEAR',
            scope=dict(description=scope, unrestricted_target=False, target_resolution='NONE'),
            assumptions=['Exact frozen four-coordinate family: 144 fixed outer edges and the recorded prescribed absences; 1920 unknown edges.', 'No nontrivial automorphism assumption; no floating-point result is used as a proof premise.'],
            dependencies=deps, evidence=list(evidence), verification=[dict(claim_revision=1,
                verifier='independent_verifier agent', method='independent_artifact_check', command_or_audit=path,
                timestamp=r.get('timestamp', r.get('completed_at')), outcome='PASS', scope=scope,
                artifact_hashes={a['id']: a['sha256'] for a in aa}, shared_components=r['shared_components'],
                controls=['Complete independent checking and positive/corrupted controls are specified in the hash-bound audit.'], limitations=limitations)],
            limitations=limitations, created_at=now, updated_at=now, external_source=None,
            unknowns={'external_source': 'Current-project result; no external peer review claimed.'},
            reproducibility=dict(manifest=prefix + '-manifest')))
    merged = shared.merge(ledger, artifacts, claims, now)
    validation = registry.validate(merged, root, shared.load('docs/claims.schema.json'), 'available', ledger)
    assert validation['valid'], validation['errors']
    assert lp.read_bytes() == old
    snapshot.write_bytes(old)
    lp.write_text(yaml.safe_dump(merged, sort_keys=False, width=110), encoding='utf-8')
    shared.save(receipt, dict(timestamp=now, command=[sys.executable, *sys.argv], cwd=str(Path.cwd()),
        registrar_sha256=shared.digest(__file__), previous_ledger_sha256=shared.sha256(old).hexdigest(),
        ledger_sha256=shared.digest(lp), validation=validation, registered_claims=[c['id'] for c in claims],
        registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN'))
    print(json.dumps(dict(claims=[c['id'] for c in claims], ledger_sha256=shared.digest(lp))))


if __name__ == '__main__':
    main()

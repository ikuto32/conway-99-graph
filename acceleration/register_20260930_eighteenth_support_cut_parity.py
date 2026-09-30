"""Integrate only State's two approved support-cut parity claims, without new review."""
from datetime import datetime, timezone
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys
import yaml
import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
I = B + 'independent_review/'


def h(p):
    with (ROOT / p).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(p):
    return json.loads((ROOT / p).read_bytes())


def main():
    path = ROOT / 'CLAIMS.yaml'
    before = path.read_bytes()
    old = registry.read_ledger(path)
    data = copy.deepcopy(old)
    assert len(old['claims']) == 176
    binding = I + 'hadamard_parity_support_cuts_sat_outcome/claim_bindings.json'
    outcome = I + 'hadamard_parity_support_cuts_sat_outcome/summary.json'
    pins = {binding: 'bc3db0bb70b087488046ef438dfd44f2b25da13d3426ee2fbff21c863f793422',
            outcome: '66d21a6be04f471c870ab9fac40c0aaa8cd64717924582ae4520e0f2e3fadc39'}
    for p, sha in pins.items():
        assert h(p) == sha, p
    approved = read(binding)
    rows = [approved['encoding'], approved['projection_witness']]
    expected = ['C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-PROJECTION',
                'C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-SAT-WITNESS']
    assert [r['id'] for r in rows] == expected
    bindings = dict(pins)
    for row in rows:
        for e in row['evidence']:
            assert h(e['path']) == e['sha256'], e['path']
            audit = read(e['path'])
            assert audit['status'].endswith('_PASS'), e['path']
            bindings[e['path']] = e['sha256']
            for field in ('inputs_sha256', 'outputs_sha256'):
                for p, sha in audit.get(field, {}).items():
                    assert h(p) == sha, p
                    assert p not in bindings or bindings[p] == sha, p
                    bindings[p] = sha
    now = datetime.now(timezone.utc).isoformat()
    for index, row in enumerate(rows):
        assert row['recommendation'] == 'VERIFIED' and row['review_state'] == 'CLEAR'
        assert row['revision'] == 1
        assert row['id'] not in {c['id'] for c in data['claims']}
        evidence, hashes = [], {}
        for j, p in enumerate([binding, *[e['path'] for e in row['evidence']]]):
            aid = f'eighteenth-support-cut-parity-{index}-evidence{j}'
            assert aid not in {a['id'] for a in data['artifacts']}
            sha = h(p)
            assert bindings[p] == sha
            evidence.append(aid)
            hashes[aid] = sha
            data['artifacts'].append(dict(id=aid, path=p, sha256=sha, availability='LOCAL_ONLY',
                retrieval='Exact workspace path; frozen independent reports bind the raw artifacts and sources.',
                unavailable_reason='Eighteenth immutable evidence publication is not yet confirmed.'))
        v = row['verification_records'][0]
        audit = read(v['report_path'])
        assert h(v['report_path']) == v['report_sha256'] and v['outcome'] == 'PASS'
        assert v['claim_id'] == row['id'] and v['claim_revision'] == row['revision']
        verification = dict(claim_revision=1, verifier=v['verifier'], method='independent_artifact_check',
            command_or_audit=v['report_path'], timestamp=v['timestamp'], outcome='PASS',
            scope=v['scope'], artifact_hashes=hashes, shared_components=audit['shared_components'],
            controls=['All 4541 clauses, mapped sixty necessary support cuts and 25 recorded corruption controls.'
                      if index == 0 else 'All 520 native/JSON entries, 4541 actual clauses, twenty raw patterns, sixty disagreements and sixty support cuts; calibrated malformed-artifact controls and separate saved native-outcome audit.'],
            limitations=row['limitations'])
        data['claims'].append(dict(id=row['id'], revision=1, statement=row['statement'], kind=row['kind'],
            basis=row['basis'], status='VERIFIED', review_state='CLEAR',
            scope=dict(description=row['scope'], unrestricted_target=False, target_resolution='NONE'),
            assumptions=row['assumptions'], dependencies=row['dependencies'], evidence=evidence,
            verification=[verification], limitations=row['limitations'], created_at=row['created_at'],
            updated_at=row['updated_at'], external_source=None,
            unknowns={'external_source': 'Independent internal review only; no external acceptance or novelty claim.'},
            reproducibility=dict(manifest=evidence[0])))
    assert data['claims'][:len(old['claims'])] == old['claims']
    assert data['artifacts'][:len(old['artifacts'])] == old['artifacts']
    data['updated_at'] = now
    validation = registry.validate(data, ROOT, read('docs/claims.schema.json'), 'available', old)
    assert validation['valid'], validation['errors']
    counts = dict(claims=len(data['claims']),
                  verified_clear=sum(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in data['claims']),
                  candidate=sum(c['status'] == 'CANDIDATE' for c in data['claims']))
    assert counts == dict(claims=178, verified_clear=176, candidate=2)
    out = ROOT / (B + 'eighteenth_support_cut_parity_registration')
    out.mkdir(exist_ok=False)
    (out / 'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    assert path.read_bytes() == before, 'Concurrent ledger change; do not overwrite.'
    path.write_bytes(after)
    (out / 'CLAIMS.after.yaml').write_bytes(after)
    record = dict(timestamp=now,
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=sys.version,
        registrar_source_sha256=h(Path(__file__).relative_to(ROOT)), new_claim_ids=expected,
        checked_input_bindings=bindings, previous_ledger_sha256=hashlib.sha256(before).hexdigest(),
        ledger_sha256=hashlib.sha256(after).hexdigest(), validation=validation, counts=counts,
        existing_claim_records_unchanged=True, existing_artifact_records_unchanged=True,
        registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN')
    with (out / 'summary.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(new_verified=2, **counts, target_resolution='UNKNOWN')))


if __name__ == '__main__':
    main()

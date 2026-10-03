"""One-shot integration of two already independently approved scoped claims."""
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


def h(path):
    with (ROOT / path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def main():
    path = ROOT / 'CLAIMS.yaml'
    before = path.read_bytes()
    old = registry.read_ledger(path)
    data = copy.deepcopy(old)
    assert len(data['claims']) == 174
    gates = [I + 'balanced_lift_zero_rows/summary.json',
             I + 'hadamard_balanced_parity_cuts/summary.json']
    binding = I + 'hadamard_balanced_parity_cuts/claim_binding.json'
    pins = {
        gates[0]: 'a6b7b5fd408e694b12cc630cf0e53e89542b1fe304f2f9d23d94735abe45af7f',
        gates[1]: '31c47c1faccc8ae043433f814932e2d419e1c2a188ffc1bd54a53b21ceeca6c1',
        binding: '7da260d8fa89a13b58bed86097bdfaa5c9a4b9c738f43cb06336e476ccb583d5',
    }
    for p, sha in pins.items():
        assert h(p) == sha, p
    audits = [read(p) for p in gates]
    assert audits[0]['status'] == 'INDEPENDENT_SELECTED_PARITY_LIFT_ZERO_ROW_EXCLUSION_PASS'
    assert audits[1]['status'] == 'INDEPENDENT_HADAMARD_BALANCED_PARITY_CONSTANT_GROUP_CUTS_PASS'
    rows = [copy.deepcopy(audits[0]['claim']), read(binding)]
    expected = ['C-FIXED-HADAMARD-SIX-PRISM-FIRST-PARITY-LIFT-EXCLUSION',
                'C-FIXED-HADAMARD-BALANCED-PARITY-CONSTANT-GROUP-NECESSITY']
    assert [r['id'] for r in rows] == expected
    bindings = dict(pins)
    for audit in audits:
        for field in ('inputs_sha256', 'outputs_sha256'):
            for p, sha in audit[field].items():
                assert h(p) == sha, p
                assert p not in bindings or bindings[p] == sha, p
                bindings[p] = sha
    extras = [
        [I + 'balanced_lift_zero_rows/independent_matrix.json',
         I + 'balanced_lift_zero_rows/zero_row_certificate.json'],
        [binding, I + 'hadamard_balanced_parity_cuts/necessary_clauses.json'],
    ]
    controls = [
        ['Complete independent reconstruction of 312 domains and 560 equations; exact zero-row and 312 dual products; a genuine 3000-variable uniform rational feasible control; eight recorded corruptions.'],
        ['All 46656 S3 coordinate-permutation arrays, 150 balanced triples, 2250 local pair records, 36 relative permutation cases, 60 exact clauses, 1024 clause truth cases and eight recorded corruptions; 90 positive constant-coincidence cases.'],
    ]
    now = datetime.now(timezone.utc).isoformat()
    for index, (row, audit, gate) in enumerate(zip(rows, audits, gates, strict=True)):
        assert row['recommendation'] == 'VERIFIED' and row['review_state'] == 'CLEAR'
        assert row['revision'] == 1
        assert row['id'] not in {c['id'] for c in data['claims']}
        evidence, hashes = [], {}
        for j, p in enumerate([gate, *extras[index]]):
            aid = f'eighteenth-zero-row-constant-{index}-evidence{j}'
            assert aid not in {a['id'] for a in data['artifacts']}
            sha = h(p)
            assert bindings[p] == sha
            evidence.append(aid)
            hashes[aid] = sha
            data['artifacts'].append(dict(
                id=aid, path=p, sha256=sha, availability='LOCAL_ONLY',
                retrieval='Exact workspace path; independent audit pins source, raw inputs and outputs.',
                unavailable_reason='Eighteenth immutable evidence publication is not yet confirmed.'))
        verification = dict(
            claim_revision=1, verifier=audit['verifier'], method='independent_artifact_check',
            command_or_audit=gate, timestamp=audit['timestamp'], outcome='PASS', scope=row['scope'],
            artifact_hashes=hashes, shared_components=audit['shared_components'],
            controls=controls[index], limitations=row['limitations'])
        data['claims'].append(dict(
            id=row['id'], revision=1, statement=row['statement'], kind=row['kind'], basis=row['basis'],
            status='VERIFIED', review_state='CLEAR',
            scope=dict(description=row['scope'], unrestricted_target=False, target_resolution='NONE'),
            assumptions=row['assumptions'], dependencies=row['dependencies'], evidence=evidence,
            verification=[verification], limitations=row['limitations'],
            created_at=row['created_at'], updated_at=row['updated_at'], external_source=None,
            unknowns={'external_source': 'Independent internal checks only; no external acceptance or novelty claim.'},
            reproducibility=dict(manifest=evidence[0])))
    assert data['claims'][:len(old['claims'])] == old['claims']
    assert data['artifacts'][:len(old['artifacts'])] == old['artifacts']
    data['updated_at'] = now
    validation = registry.validate(data, ROOT, read('docs/claims.schema.json'), 'available', old)
    assert validation['valid'], validation['errors']
    counts = dict(claims=len(data['claims']),
                  verified_clear=sum(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in data['claims']),
                  candidate=sum(c['status'] == 'CANDIDATE' for c in data['claims']))
    assert counts == dict(claims=176, verified_clear=174, candidate=2)
    out = ROOT / (B + 'eighteenth_zero_row_and_constant_registration')
    out.mkdir(exist_ok=False)
    (out / 'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    assert path.read_bytes() == before, 'Concurrent ledger change; do not overwrite.'
    path.write_bytes(after)
    (out / 'CLAIMS.after.yaml').write_bytes(after)
    record = dict(
        timestamp=now, source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
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

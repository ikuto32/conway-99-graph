"""Register independently checked universal normalization and its necessary CNF."""
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
I = B+'independent_review/'


def h(p):
    with (ROOT/p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    path = ROOT/'CLAIMS.yaml'
    before = path.read_bytes()
    old = registry.read_ledger(path)
    data = copy.deepcopy(old)
    specs = [
        ('unrestricted-triangle-factor', I+'unrestricted_triangle_factor/summary.json',
         'a7d470ccf10df7dff77884c8bd1fe4784234ac80bc4e1b684e0050c3e33a4acd', 'independent_derivation',
         [B+'unrestricted_triangle_factor/manifest.json', B+'unrestricted_triangle_factor/summary.json',
          'docs/AUDIT_20260930_UNRESTRICTED_TRIANGLE_FACTOR.md']),
        ('variable-core-factor-cnf', I+'variable_core_factor_cnf_v2/summary.json',
         'ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0', 'independent_artifact_check',
         [B+'variable_core_factor_cnf/manifest.json', B+'variable_core_factor_cnf/instance.cnf',
          B+'variable_core_factor_cnf/model.json', I+'variable_core_factor_object_calibration/summary.json',
          I+'variable_core_factor_corruption_addendum/summary.json']),
    ]
    now = datetime.now(timezone.utc).isoformat()
    added, bindings = [], {}
    for label, pin, expected, method, extras in specs:
        assert h(pin) == expected, pin
        r = json.loads((ROOT/pin).read_bytes())
        assert r['status'].startswith('INDEPENDENT_') and r['status'].endswith('_PASS')
        assert r['recommendation'] == 'VERIFIED'
        for p, value in r['inputs_sha256'].items():
            assert h(p) == value, p
            bindings[p] = value
        evidence, hashes = [], {}
        for index, p in enumerate([pin, *extras]):
            aid = label+('-audit' if index == 0 else '-evidence'+str(index))
            assert aid not in {a['id'] for a in data['artifacts']}
            hashes[aid] = h(p)
            evidence.append(aid)
            data['artifacts'].append(dict(id=aid, path=p, sha256=hashes[aid], availability='LOCAL_ONLY',
                retrieval='Exact workspace path, with input closure, commands and checking records in the pinned report. Oversized model is losslessly recoverable using its artifact_packages.json.',
                unavailable_reason='This new cohort has not yet been bound to immutable public evidence.'))
        cid, revision = r['claim_id'], r['claim_revision']
        assert cid not in {c['id'] for c in data['claims']}
        data['claims'].append(dict(id=cid, revision=revision, statement=r['statement'], kind=r['kind'], basis=r['basis'],
            status='VERIFIED', review_state='CLEAR',
            scope=dict(description=r['scope'], unrestricted_target=True, target_resolution='NONE'),
            assumptions=['Symmetric binary zero-diagonal target matrix satisfies the exact integer identity A^2=12I-A+2J.',
                'Only coordinate relabellings established by the pinned derivation; no automorphism or core restriction.'],
            dependencies=r['dependencies'], evidence=evidence,
            verification=[dict(claim_revision=revision, verifier=r['verifier'], method=method, command_or_audit=pin,
                timestamp=r['timestamp'], outcome='PASS', scope=r['scope'], artifact_hashes=hashes,
                shared_components=r['shared_components'],
                controls=['Independent written universal derivation or complete encoding reconstruction; exact positive and corrupted calibration scopes appear in pinned reports.'],
                limitations=r['limitations'])],
            limitations=r['limitations'], created_at=now, updated_at=now, external_source=None,
            unknowns={'external_source': 'Internal independent review, not novelty or peer-review certification.'},
            reproducibility=dict(manifest=evidence[0])))
        added.append(cid)
    assert len(added) == 2
    data['updated_at'] = now
    result = registry.validate(data, ROOT, json.loads((ROOT/'docs/claims.schema.json').read_bytes()), 'available', old)
    assert result['valid'], result['errors']
    out = ROOT/(B+'twelfth_preparation_registration')
    out.mkdir(parents=True, exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    assert path.read_bytes() == before
    path.write_bytes(after)
    (out/'CLAIMS.after.yaml').write_bytes(after)
    record = dict(timestamp=now, source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), new_claim_ids=added, checked_input_bindings=bindings,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(), ledger_sha256=hashlib.sha256(after).hexdigest(),
        validation=result, registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(new_verified=2, claim_population=len(data['claims']), target_resolution='UNKNOWN')))


if __name__ == '__main__':
    main()

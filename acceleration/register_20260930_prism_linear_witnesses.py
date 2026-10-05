"""Register three independently checked linear-relaxation witnesses."""
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
    pin = I+'prism_column_modular/summary.json'
    assert h(pin) == '8c80a0c151e7362b4045e3527a072fddf60dfd5f7f7d87698cdb45c5dafbe9e1'
    r = json.loads((ROOT/pin).read_bytes())
    assert r['status'].startswith('INDEPENDENT_') and r['status'].endswith('_PASS')
    assert r['recommendation'] == 'VERIFIED'
    for p, expected in r['inputs_sha256'].items():
        assert h(p) == expected, p
    paths = [pin, B+'prism_column_modular/manifest.json', B+'prism_column_modular/uniform_rational_witness.json',
             B+'prism_column_modular/mod_2.json', B+'prism_column_modular/mod_3.json']
    evidence, hashes = [], {}
    for i, p in enumerate(paths):
        aid = 'six-prism-linear-witnesses-'+('audit' if i == 0 else 'evidence'+str(i))
        assert aid not in {a['id'] for a in data['artifacts']}
        hashes[aid] = h(p)
        evidence.append(aid)
        data['artifacts'].append(dict(id=aid, path=p, sha256=hashes[aid], availability='LOCAL_ONLY',
            retrieval='Exact workspace path; large CNF/model originals are losslessly recoverable from authenticated gzip parts in artifact_packages.json.',
            unavailable_reason='Not yet bound to immutable public evidence.'))
    now = datetime.now(timezone.utc).isoformat()
    cid, revision = r['claim_id'], r['claim_revision']
    assert cid not in {c['id'] for c in data['claims']}
    data['claims'].append(dict(id=cid, revision=revision, statement=r['statement'], kind=r['kind'], basis=r['basis'],
        status='VERIFIED', review_state='CLEAR', scope=dict(description=r['scope'], unrestricted_target=False, target_resolution='NONE'),
        assumptions=['Exactly the saved 540 linear equations on 5760 primary choices.',
                     'Each witness belongs to its separately stated rational or modular domain; integer feasibility is not inferred.'],
        dependencies=r['dependencies'], evidence=evidence,
        verification=[dict(claim_revision=revision, verifier=r['verifier'], method='independent_artifact_check',
            command_or_audit=pin, timestamp=r['timestamp'], outcome='PASS', scope=r['scope'], artifact_hashes=hashes,
            shared_components=r['shared_components'],
            controls=['Independent equation reconstruction and direct exact witness evaluation, with 14 fresh corrupted witnesses rejected; rank and elimination are not checked.'],
            limitations=r['limitations'])], limitations=r['limitations'], created_at=now, updated_at=now,
        external_source=None, unknowns={'external_source': 'Internal independent review only; no external acceptance asserted.'},
        reproducibility=dict(manifest=evidence[0])))
    data['updated_at'] = now
    result = registry.validate(data, ROOT, json.loads((ROOT/'docs/claims.schema.json').read_bytes()), 'available', old)
    assert result['valid'], result['errors']
    out = ROOT/(B+'prism_linear_witness_registration')
    out.mkdir(parents=True, exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    assert path.read_bytes() == before
    path.write_bytes(after)
    (out/'CLAIMS.after.yaml').write_bytes(after)
    record = dict(timestamp=now, source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), new_claim_ids=[cid], checked_input_bindings=r['inputs_sha256'],
        report_field_mapping={},
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(), ledger_sha256=hashlib.sha256(after).hexdigest(),
        validation=result, registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(new_verified=1, claim_population=len(data['claims']), target_resolution='UNKNOWN')))


if __name__ == '__main__':
    main()

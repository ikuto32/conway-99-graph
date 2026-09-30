"""Register three exact, separately checked modular claims with their conditional scopes."""
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
I = B + 'independent_review/five_core_modular_gram/'


def h(p):
    with (ROOT / p).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    path = ROOT / 'CLAIMS.yaml'
    before = path.read_bytes()
    old = registry.read_ledger(path)
    data = copy.deepcopy(old)
    assert len(data['claims']) == 143
    assert h(I + 'summary.json') == 'b5bf625c820b6cbae9779b7dd40e8263dada10dad54b36d433ffdcff7951b34e'
    assert h(I + 'claim_bindings.json') == '87540b6146218663e63e5fed12a2f480ae956235b9b70b91ac9669e6a73a774f'
    audit = json.loads((ROOT / (I + 'summary.json')).read_bytes())
    claims = json.loads((ROOT / (I + 'claim_bindings.json')).read_bytes())['claims']
    assert len(claims) == 3 and audit['status'].endswith('_PASS')
    bindings = dict(audit['inputs_sha256'])
    for p, sha in bindings.items(): assert h(p) == sha, p
    evidence, hashes = [], {}
    for i, p in enumerate([I + 'summary.json', I + 'claim_bindings.json',
                            'docs/AUDIT_20260930_FIVE_CORE_MODULAR_GRAM.md', B + 'five_core_modular_gram/summary.json']):
        aid = 'five-core-modular-evidence' + str(i)
        assert aid not in {a['id'] for a in data['artifacts']}
        evidence.append(aid)
        hashes[aid] = h(p)
        bindings[p] = h(p)
        data['artifacts'].append(dict(id=aid, path=p, sha256=h(p), availability='LOCAL_ONLY',
            retrieval='Exact workspace path and complete pinned independent review.',
            unavailable_reason='Fifteenth-cohort immutable publication is not yet confirmed.'))
    now = datetime.now(timezone.utc).isoformat()
    for r in claims:
        assert r['recommendation'] == 'VERIFIED' and r['review_state'] == 'CLEAR' and r['revision'] == 1
        assert r['id'] not in {c['id'] for c in data['claims']}
        verification = dict(claim_revision=1, verifier=r['verifier'],
            method='independent_derivation' if r['kind'] == 'mathematical result' else 'independent_artifact_check',
            command_or_audit=I + 'summary.json', timestamp=r['updated_at'], outcome='PASS', scope=r['scope'],
            artifact_hashes=hashes, shared_components=audit['shared_components'],
            controls=['Independent universal argument; all declared exact rank/kernel-action certificates and known positive/corrupted controls bound by the report.'],
            limitations=r['limitations'])
        data['claims'].append(dict(id=r['id'], revision=1, statement=r['statement'], kind=r['kind'], basis=r['basis'],
            status='VERIFIED', review_state='CLEAR', scope=dict(description=r['scope'], unrestricted_target=False, target_resolution='NONE'),
            assumptions=r['assumptions'], dependencies=r['dependencies'], evidence=evidence, verification=[verification],
            limitations=r['limitations'], created_at=now, updated_at=now, external_source=None,
            unknowns={'external_source': 'Internal independent review only; external acceptance and novelty are not claimed.'},
            reproducibility=dict(manifest=evidence[0])))
    data['updated_at'] = now
    result = registry.validate(data, ROOT, json.loads((ROOT / 'docs/claims.schema.json').read_bytes()), 'available', old)
    assert result['valid'], result['errors']
    out = ROOT / (B + 'fifteenth_modular_registration')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    assert path.read_bytes() == before
    path.write_bytes(after)
    (out / 'CLAIMS.after.yaml').write_bytes(after)
    receipt = dict(timestamp=now, source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), new_claim_ids=[r['id'] for r in claims], checked_input_bindings=bindings,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(), ledger_sha256=hashlib.sha256(after).hexdigest(), validation=result,
        registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN')
    with (out / 'summary.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(new_verified=3, claim_population=len(data['claims']), target_resolution='UNKNOWN')))


if __name__ == '__main__': main()

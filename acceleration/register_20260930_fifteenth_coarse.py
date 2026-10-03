"""Register the separately reviewed finite coarse-template local domains; the registrar performs no mathematical approval."""
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


def main():
    path = ROOT / 'CLAIMS.yaml'
    before = path.read_bytes()
    old = registry.read_ledger(path)
    data = copy.deepcopy(old)
    assert len(data['claims']) == 146
    specs = [
        ('prism-complement60-local-domains', I + 'prism_coarse_complement/summary.json',
         '7087ce1ff80ffd93e186c2e0d642bb99b1b003262f79bb19862e05015a8c590d',
         [B + 'prism_coarse_complement/summary.json'], 'independent_artifact_check'),
    ]
    added, bindings = [], {}
    now = datetime.now(timezone.utc).isoformat()
    for label, pin, expected, extras, method in specs:
        assert h(pin) == expected
        r = json.loads((ROOT / pin).read_bytes())
        assert r['recommendation'] == 'VERIFIED' and r['review_state'] == 'CLEAR' and r['claim_revision'] == 1
        audit = r if 'inputs_sha256' in r else json.loads((ROOT / extras[0]).read_bytes())
        for p, sha in audit['inputs_sha256'].items():
            assert h(p) == sha, p
            bindings[p] = sha
        for e in r.get('evidence', []):
            assert h(e['path']) == e['sha256']
            bindings[e['path']] = e['sha256']
        bindings[pin] = expected
        evidence, hashes = [], {}
        for i, p in enumerate([pin, *extras]):
            aid = label + '-evidence' + str(i)
            assert aid not in {a['id'] for a in data['artifacts']}
            hashes[aid] = h(p)
            evidence.append(aid)
            data['artifacts'].append(dict(id=aid, path=p, sha256=hashes[aid], availability='LOCAL_ONLY',
                retrieval='Exact current workspace path; immutable public publication has not yet been confirmed.',
                unavailable_reason='New fifteenth-cohort evidence is not yet published.'))
        cid = r['claim_id']
        assert cid not in {c['id'] for c in data['claims']}
        scope = r['scope']
        limitations = r['limitations']
        verification = dict(claim_revision=1, verifier=r['verifier'], method=method, command_or_audit=pin,
            timestamp=r.get('timestamp', r['updated_at']), outcome='PASS', scope=scope, artifact_hashes=hashes,
            shared_components=r['shared_components'],
            controls=['Exact populations, independently authored checking paths and positive/corrupted controls are specified by the bound reports.'],
            limitations=limitations)
        data['claims'].append(dict(id=cid, revision=1, statement=r['statement'], kind=r['kind'], basis=r['basis'],
            status='VERIFIED', review_state='CLEAR', scope=dict(description=scope, unrestricted_target=False, target_resolution='NONE'),
            assumptions=r['assumptions'], dependencies=r['dependencies'], evidence=evidence, verification=[verification],
            limitations=limitations, created_at=now, updated_at=now, external_source=None,
            unknowns={'external_source': 'Internal independent review only; no external acceptance or novelty claimed.'},
            reproducibility=dict(manifest=evidence[0])))
        added.append(cid)
    data['updated_at'] = now
    result = registry.validate(data, ROOT, json.loads((ROOT / 'docs/claims.schema.json').read_bytes()), 'available', old)
    assert result['valid'], result['errors']
    out = ROOT / (B + 'fifteenth_coarse_registration')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    assert path.read_bytes() == before
    path.write_bytes(after)
    (out / 'CLAIMS.after.yaml').write_bytes(after)
    receipt = dict(timestamp=now, source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), new_claim_ids=added, checked_input_bindings=bindings,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(), ledger_sha256=hashlib.sha256(after).hexdigest(),
        validation=result, registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN')
    with (out / 'summary.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(new_verified=len(added), claim_population=len(data['claims']), target_resolution='UNKNOWN')))


if __name__ == '__main__': main()

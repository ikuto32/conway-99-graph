"""Register five separately reviewed claims; the registrar performs no mathematical approval."""
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
    assert len(data['claims']) == 138
    specs = [
        ('triangle-gf2-maxrank', I + 'triangle_gf2_maxrank/summary.json',
         '229dfa1a24b3fa840965125c2efc7a017cd882fb77edd056cc714e4ca866d006',
         ['docs/AUDIT_20260930_TRIANGLE_GF2_MAXRANK.md'], 'independent_derivation'),
        ('connected-identity-portfolio', I + 'connected_identity_cores/summary.json',
         'efdcacb9130bf29a28ece4c07022bdab11ab953a862f117fc55f44bd5244d2b4',
         [B + 'connected_identity_cores/summary.json', 'docs/AUDIT_20260930_CONNECTED_IDENTITY_CORES.md'], 'independent_artifact_check'),
        ('connected-portfolio-calibration', I + 'factor_portfolio_v4/summary.json',
         'df3d3a9ef20c622ce9b529a1aabbba2df18e95ac3e17b1210a866d46657e3ae2',
         [B + 'factor_permutation_portfolio_calibration_v4/summary.json', 'docs/AUDIT_20260930_FACTOR_PORTFOLIO_V4.md'], 'independent_artifact_check'),
        ('connected-portfolio-saved-states', I + 'connected_core_portfolio_states/claim_binding.json',
         '95f071e2470b16dba3eb5b30dbe04cf5df500beae03740eadb7f41d82fda0ace',
         [I + 'connected_core_portfolio_states/summary.json', B + 'connected_core_portfolio_pilot/summary.json'], 'independent_artifact_check'),
        ('connected-fixed-core-cnf', I + 'connected_fixed_core_claim_binding/claim_binding.json',
         '4a0201b9ca0ec3d40a86c32a8e2c73b7279e36e3dbb34be10bb3b2ebfed8613d',
         [I + 'connected_fixed_core_cnf/summary.json', B + 'connected_fixed_core_cnf/summary.json'], 'independent_artifact_check'),
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
    out = ROOT / (B + 'fifteenth_preparation_registration')
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

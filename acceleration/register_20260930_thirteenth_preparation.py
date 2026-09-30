"""Bind four independently checked normalization/control/screen claims.

Explicitly map two gate-addressed M1 dependencies to already registered IDs.
Record the SRG243 verifier's standard-library-only implementation disclosure
and its use as a verification dependency of the dynamic screen. No new
mathematical checking is performed by this registry transaction.
"""
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
        ('srg243-positive', 'srg243_residual_fixture',
         '28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e', False,
         [B+'srg243_residual_fixture/manifest.json', B+'srg243_residual_fixture/adjacency243.json',
          B+'srg243_residual_fixture/triangle_blocks.json']),
        ('dynamic-residual-screen', 'dynamic_residual_screen',
         '9562eed1820c93583d0355e62f7c1fbba8c03aca9cf7f7f0ae02406f5d0d2102', False,
         [B+'variable_core_residual_screen_calibration/summary.json', 'docs/PLAN_20260930_ARBITRARY_CORE_RESIDUAL_OBJECT_AUDIT.md']),
        ('six-prism-first-choice', 'prism_first_choice_normalization',
         'c5963305cff69ef0242db04d373fdf7cba1339e547191554b64b319165bf8223', False,
         [B+'prism_first_choice_normalization/manifest.json', B+'prism_first_choice_normalization/instance.cnf',
          B+'prism_first_choice_normalization/summary.json', 'docs/AUDIT_20260930_PRISM_FIRST_CHOICE_NORMALIZATION.md']),
        ('variable-core-m1-orbits', 'variable_core_m1_orbits',
         'ef13877c79a1115cf34a105a9704bb58c0ad981189dfe6acda9b4de4a27d6584', True,
         [B+'variable_core_m1_orbits/manifest.json', B+'variable_core_m1_orbits/instance.cnf',
          B+'variable_core_m1_orbits/extension.json', I+'variable_core_m1_orbits_object_calibration/summary.json']),
    ]
    now = datetime.now(timezone.utc).isoformat()
    added, bindings, mappings = [], {}, {}
    for label, folder, expected, unrestricted, extras in specs:
        pin = I+folder+'/summary.json'
        assert h(pin) == expected, pin
        r = json.loads((ROOT/pin).read_bytes())
        assert r['status'].startswith('INDEPENDENT_') and r['status'].endswith('_PASS') and r['recommendation'] == 'VERIFIED'
        for p, value in r['inputs_sha256'].items():
            assert h(p) == value, p
            bindings[p] = value
        dependencies = copy.deepcopy(r['dependencies'])
        shared = r.get('shared_components')
        if label == 'srg243-positive':
            assert r['producer_imports'] is False
            shared = ['Python standard library and exact integer dot products; no producer imports. Source audit_20260930_srg243_residual_fixture.py is pinned by the report.']
            mappings[pin] = {'shared_components': 'Implementation disclosure from the pinned standard-library-only checker and producer_imports=false; report has no separate shared_components key.'}
        if label == 'dynamic-residual-screen':
            dependencies.append(dict(id='C-SRG243-NONEMPTY-RESIDUAL-POSITIVE-CONTROL', revision=1, relation='verification_dependency'))
            mappings[pin] = {'additional_verification_dependency': 'The report binds and exercises the separately checked SRG243 raw fixture; the mathematical necessity remains conditional on supplied F.'}
        if label == 'variable-core-m1-orbits':
            expected_gates = ['ecc6c2ee488e68826e790360f3d47d6b029ac33953806bdab530ba50394a6ea0',
                              '085748fd2ebb03bdb7ea6048d782be0c17ce8cadef4ea32028cb58ca6b0efb79']
            assert [d.get('gate_sha256') for d in dependencies[1:]] == expected_gates
            dependencies = [dependencies[0],
                dict(id='C-UNRESTRICTED-TRIANGLE-NECESSARY-FACTOR-CNF-ENCODING', revision=1, relation='encoding_equivalence'),
                dict(id='C-TRIANGLE-ORDERED-MATCHING-PAIR-CENSUS', revision=1, relation='coverage')]
            mappings[pin] = {'original_dependencies': r['dependencies'], 'resolved_dependencies': dependencies,
                             'reason': 'The two gate hashes uniquely bind the registered exact statements/revisions.'}
        evidence, hashes = [], {}
        for i,p in enumerate([pin,*extras]):
            aid = label+('-audit' if i == 0 else '-evidence'+str(i))
            assert aid not in {a['id'] for a in data['artifacts']}
            hashes[aid] = h(p)
            evidence.append(aid)
            data['artifacts'].append(dict(id=aid, path=p, sha256=hashes[aid], availability='LOCAL_ONLY',
                retrieval='Exact workspace path and pinned independent report; oversized CNF recovery is specified in its artifact_packages.json.',
                unavailable_reason='This new milestone has not yet been confirmed in immutable public evidence.'))
        cid, revision = r['claim_id'], r['claim_revision']
        assert cid not in {c['id'] for c in data['claims']}
        data['claims'].append(dict(id=cid, revision=revision, statement=r['statement'], kind=r['kind'], basis=r['basis'],
            status='VERIFIED', review_state='CLEAR', scope=dict(description=r['scope'], unrestricted_target=unrestricted, target_resolution='NONE'),
            assumptions=['Only the exact parameter family, supplied-factor premises and relabelling scope of the pinned independent audit.',
                         'No target automorphism, target existence or unrecorded universal core-containment premise is assumed.'],
            dependencies=dependencies, evidence=evidence,
            verification=[dict(claim_revision=revision, verifier=r['verifier'], method='independent_artifact_check',
                command_or_audit=pin, timestamp=r['timestamp'], outcome='PASS', scope=r['scope'], artifact_hashes=hashes,
                shared_components=shared, controls=['The exact independent checking paths, complete finite populations, positive and corrupted controls, and written universal arguments are specified in the pinned audit.'],
                limitations=r['limitations'])], limitations=r['limitations'], created_at=now, updated_at=now,
            external_source=None, unknowns={'external_source': 'Internal independent review only; no novelty or external acceptance claimed.'},
            reproducibility=dict(manifest=evidence[0])))
        added.append(cid)
    assert len(added) == 4
    data['updated_at'] = now
    result = registry.validate(data, ROOT, json.loads((ROOT/'docs/claims.schema.json').read_bytes()), 'available', old)
    assert result['valid'], result['errors']
    out = ROOT/(B+'thirteenth_preparation_registration')
    out.mkdir(parents=True, exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    assert path.read_bytes() == before
    path.write_bytes(after)
    (out/'CLAIMS.after.yaml').write_bytes(after)
    record = dict(timestamp=now, source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),new_claim_ids=added,checked_input_bindings=bindings,report_field_mappings=mappings,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(),ledger_sha256=hashlib.sha256(after).hexdigest(),validation=result,
        registrar_performs_mathematical_verification=False,target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(new_verified=4,claim_population=len(data['claims']),target_resolution='UNKNOWN')))


if __name__ == '__main__':
    main()

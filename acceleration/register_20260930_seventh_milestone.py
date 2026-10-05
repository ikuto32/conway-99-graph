"""Register ten independently checked seventh-wave statements; no discovery."""
from datetime import datetime, timezone
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import yaml
import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
A = B+'independent_review/'

def digest(path):
    with (ROOT/path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def read(path):
    return json.loads((ROOT/path).read_bytes())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--wave151-proof-gate', required=True)
    parser.add_argument('--wave151-proof-gate-sha256', required=True)
    args = parser.parse_args()
    ledger = ROOT/'CLAIMS.yaml'
    before = ledger.read_bytes()
    previous = registry.read_ledger(ledger)
    data = copy.deepcopy(previous)
    specs = [
        ('one-star-redundancy', A+'unrestricted_star_matching/summary.json', 'f8445dddc7deb5327681ad4a2d00c9c025465d4e903e1da295d19d6b834c76e6', True, None,
         [B+'unrestricted_star_matching_redundancy/run01/manifest.json']),
        ('two-star-witnesses', A+'joint_two_star_domains/summary.json', '1e86811939f29e06352987fd88d2925d274be2d08f0991ce2d55dd025b541f04', False, 0, []),
        ('two-star-individual-domains', A+'joint_two_star_domains/summary.json', '1e86811939f29e06352987fd88d2925d274be2d08f0991ce2d55dd025b541f04', False, 1, []),
        ('two-star-nogood36', A+'two_star_empty_domain_cut_v2/summary.json', 'e3aae7ba9b776e9382c1790c64f0e76be6f0497912a9e1440e43a7df959ce16c', True, None,
         [B+'two_star_empty_domain_cut/run01/certificate.json', B+'two_star_empty_domain_cut/run01/nogood.clause']),
        ('nogood36-transport192', A+'nogood36_anchor_transport/summary.json', '67a4d151a279589b440ac6961acb32e902c53c41f81255c1547be23b19e3c68c', True, None,
         [B+'two_star_nogood36_anchor_transport/run01/manifest.json', B+'two_star_nogood36_anchor_transport/run01/clauses.cnfpart']),
        ('triangle-q1-propagation', A+'triangle_q1_partial99/summary.json', 'bad7ddc51101377b8eaa284c650db8adcee5c261a0717073b90fc9e2347d7594', False, None,
         [B+'triangle_partial99/wave151.json', B+'triangle_partial99/wave154.json']),
        ('triangle-wave154-encoding', A+'triangle_full99_cnf/summary.json', '9b47af959088ef3a0eaf9f4e8d00181a5d86ff745f5efade002052cff51302c4', False, None,
         [B+'triangle_full99_cnf/manifest.json', B+'triangle_full99_cnf/artifact_packages.json']),
        ('triangle-wave154-exclusion', A+'triangle_wave154_unsat/summary.json', '479c07b21f5c264d658ad97e40194701a6c42b1f67f0ed1c3c3ba9d1252a87d3', False, None,
         [B+'triangle_native_pilot/manifest.json', B+'triangle_native_pilot/main/proof.drat']),
        ('triangle-wave151-encoding', A+'wave151_triangle_full99_cnf/summary.json', 'e981efe0e234f130cd5bd378a669219c1e793c234b6991779993d9a57d940430', False, None,
         [B+'triangle_wave151_full99_cnf/manifest.json', B+'triangle_wave151_full99_cnf/artifact_packages.json']),
        ('triangle-wave151-exclusion', args.wave151_proof_gate, args.wave151_proof_gate_sha256, False, None,
         [B+'wave151_triangle_native_pilot/manifest.json', B+'wave151_triangle_native_pilot/main/proof.drat']),
    ]
    now = datetime.now(timezone.utc).isoformat()
    added, bindings, metadata_clarifications = [], {}, []
    path_to_id = {a['path']: a['id'] for a in data['artifacts'] if a['path'] is not None}

    def artifact(aid, path):
        value = digest(path)
        if path in path_to_id:
            existing = next(a for a in data['artifacts'] if a['id'] == path_to_id[path])
            if existing['sha256'] != value:
                raise ValueError('existing artifact changed '+path)
            return existing['id'], value
        if aid in {a['id'] for a in data['artifacts']}:
            raise ValueError('duplicate artifact ID '+aid)
        data['artifacts'].append(dict(id=aid, path=path, sha256=value, availability='LOCAL_ONLY',
            retrieval='Workspace-relative exact artifact; bound reports and compressed recovery packages retain raw mathematical inputs.',
            unavailable_reason='Publication of this new evidence is not yet confirmed.'))
        path_to_id[path] = aid
        return aid, value

    for label, path, expected, unrestricted, subclaim, extras in specs:
        if digest(path) != expected:
            raise ValueError('audit identity changed '+path)
        report = read(path)
        if not report['status'].startswith('INDEPENDENT_') or not report['status'].endswith('_PASS'):
            raise ValueError('nonpassing independent gate '+path)
        for name, value in report['inputs_sha256'].items():
            if digest(name) != value:
                raise ValueError('checked input changed '+name)
            bindings[name] = value
        statement = copy.deepcopy(report if subclaim is None else report['claims'][subclaim])
        if subclaim is not None:
            statement['claim_id'] = statement['id']
            statement['claim_revision'] = statement['revision']
        if label == 'triangle-wave154-encoding':
            statement['dependencies'] = [dict(id='C-TRIANGLE-FIXED-Q1-PARTIAL99-PROPAGATION', revision=1, relation='uses_result')]
            metadata_clarifications.append(dict(claim=statement['claim_id'], field='dependencies',
                reason='The immutable encoding audit explicitly binds and relies on the independent propagation gate; register this existing premise as a ledger edge without modifying the report.'))
        if statement['claim_id'] in {c['id'] for c in data['claims']}:
            raise ValueError('claim already exists')
        audit_id, audit_hash = artifact(label+'-audit', path)
        evidence = [audit_id]
        bound = {audit_id: audit_hash}
        for index, extra in enumerate(extras):
            aid, value = artifact(label+'-evidence'+str(index+1), extra)
            evidence.append(aid)
            bound[aid] = value
        scope = statement['scope']
        limits = statement.get('limitations', report['limitations'])
        shared = report.get('shared_components', [])
        if not isinstance(shared, list):
            shared = [json.dumps(shared, sort_keys=True)]
        if not shared:
            shared = ['Exact shared scaffolds, independent checker helpers and trusted runtime components are disclosed in the pinned audit; no independent implementation of every trusted component is asserted.']
        revision = statement['claim_revision']
        claim = dict(id=statement['claim_id'], revision=revision, statement=statement['statement'],
            kind=statement['kind'], basis=statement['basis'], status='VERIFIED', review_state='CLEAR',
            scope=dict(description=scope, unrestricted_target=unrestricted, target_resolution='NONE'),
            assumptions=statement.get('assumptions', ['Exactly the frozen inputs and explicit hypotheses of the statement and bound audit.', 'No nontrivial target automorphism is assumed.']),
            dependencies=statement['dependencies'], evidence=evidence,
            verification=[dict(claim_revision=revision, verifier=report['verifier'],
                method='independent_derivation' if label == 'one-star-redundancy' else 'independent_artifact_check',
                command_or_audit=path, timestamp=report['timestamp'], outcome='PASS', scope=scope,
                artifact_hashes=bound, shared_components=shared,
                controls=['Exact positive/corrupted control populations and complete versus sampled checks are enumerated in the pinned audit.'],
                limitations=limits)], limitations=limits, created_at=now, updated_at=now,
            external_source=None, unknowns={'external_source': 'Independent internal checking; no external review is asserted.'},
            reproducibility=dict(manifest=audit_id))
        data['claims'].append(claim)
        added.append(claim['id'])
    data['updated_at'] = now
    result = registry.validate(data, ROOT, read('docs/claims.schema.json'), 'available', previous)
    if not result['valid']:
        raise ValueError(result['errors'])
    out = ROOT/(B+'seventh_registration')
    out.mkdir(parents=True, exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    if ledger.read_bytes() != before:
        raise ValueError('concurrent ledger change')
    ledger.write_bytes(after)
    (out/'CLAIMS.after.yaml').write_bytes(after)
    report = dict(timestamp=now, source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), new_claim_ids=added,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(), ledger_sha256=hashlib.sha256(after).hexdigest(),
        checked_input_bindings=bindings, registration_metadata_clarifications=metadata_clarifications,
        validation=result, registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'new_claims': len(added), 'claim_population': len(data['claims']), 'target_resolution': 'UNKNOWN'}))

if __name__ == '__main__':
    main()

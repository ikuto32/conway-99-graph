"""Register seven exact claims already bound to independent frozen audits.

This registrar checks identities and schema; it is not mathematical review.
Each audit author is distinct from the discovery author. Run only once.
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
A = B + 'independent_review/'


def digest(path):
    with (ROOT / path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def main():
    ledger = ROOT / 'CLAIMS.yaml'
    before = ledger.read_bytes()
    previous = registry.read_ledger(ledger)
    data = copy.deepcopy(previous)
    specs = [
        ('triangle-three-q1', A + 'triangle_q1_binary_scout/summary.json',
         '535b61f7a70e79169b1db21c5c5b3b833015fedc3691b8aa4aacaf797ef8ba39',
         'claims', [B + 'triangle_q1_binary_scout/manifest.json',
                    B + 'triangle_q1_binary_scout/supplemental_row_controls.json']),
        ('triangle-joint-factor', A + 'triangle_joint_factor_cnf/summary.json',
         '5a6ebade41cf1ab35796ca5d5ce3840c23b624ab06d0ed5a4ff327327ea2b97f',
         None, [B + 'triangle_joint_factor_cnf/manifest.json',
                B + 'triangle_joint_factor_cnf/scope.json',
                B + 'triangle_joint_factor_cnf/instance.cnf',
                B + 'triangle_joint_factor_cnf/model.json',
                A + 'triangle_joint_factor_object_calibration_v2/summary.json']),
        ('triangle-factor-components', A + 'triangle_factor_components/summary.json',
         '03d84677f34e0a209f9331c32efcd0b843dae60b97dbf9e9102b85171a5fef5b',
         'claim_records', [B + 'triangle_factor_components/manifest.json',
                           B + 'triangle_factor_components/kernel_certificate.json',
                           B + 'triangle_factor_components/five_Q1_diagnostic.json',
                           B + 'triangle_factor_components/instance.cnf',
                           B + 'triangle_factor_components/model.json',
                           A + 'triangle_component_factor_object_calibration/summary.json']),
    ]
    now = datetime.now(timezone.utc).isoformat()
    bindings = {}
    added = []
    for label, path, expected, field, extras in specs:
        assert digest(path) == expected, path
        report = read(path)
        assert report['status'].startswith('INDEPENDENT_') and report['status'].endswith('_PASS')
        for name, value in report['inputs_sha256'].items():
            assert digest(name) == value, name
            bindings[name] = value
        records = report[field] if field else [dict(
            id=report['claim_id'], revision=report['claim_revision'],
            statement=report['statement'], kind=report['kind'],
            dependencies=report['dependencies'])]
        evidence = []
        hashes = {}
        for index, name in enumerate([path, *extras]):
            aid = label + ('-audit' if index == 0 else '-evidence' + str(index))
            assert aid not in {a['id'] for a in data['artifacts']}
            value = digest(name)
            evidence.append(aid)
            hashes[aid] = value
            data['artifacts'].append(dict(
                id=aid, path=name, sha256=value, availability='LOCAL_ONLY',
                retrieval='Exact workspace-relative artifact; the independent audit pins the raw inputs, checking source, commands and controls.',
                unavailable_reason='This new milestone has not yet been confirmed in an immutable public commit.'))
        shared = report.get('shared_components') or [json.dumps(report['sharing'], sort_keys=True)]
        limits = report['limitations']
        for record in records:
            assert record.get('recommendation', report.get('recommendation')) == 'VERIFIED'
            cid = record['id']
            assert cid not in {c['id'] for c in data['claims']}, cid
            revision = record['revision']
            scope = record.get('scope', report.get('scope'))
            assert scope
            data['claims'].append(dict(
                id=cid, revision=revision, statement=record['statement'],
                kind=record['kind'], basis=record.get('basis', report.get('basis')),
                status='VERIFIED', review_state='CLEAR',
                scope=dict(description=scope, unrestricted_target=False, target_resolution='NONE'),
                assumptions=[
                    'Only the exact fixed triangle core, incidence margins and labelled artifacts specified in the pinned audit.',
                    'No nontrivial automorphism of a hypothetical target is assumed; no claim that every target contains this fixed core.'],
                dependencies=record['dependencies'], evidence=evidence,
                verification=[dict(
                    claim_revision=revision, verifier=report['verifier'],
                    method='independent_derivation' if cid == 'C-FIXED-TRIANGLE-FACTOR-COMPONENT-BALANCE' else 'independent_artifact_check',
                    command_or_audit=path, timestamp=report['timestamp'], outcome='PASS',
                    scope=scope, artifact_hashes=hashes, shared_components=shared,
                    controls=['The frozen independent report and its hashed controls distinguish full artifact checks from universal derivation, synthetic calibration, and unreplayed heuristic telemetry.'],
                    limitations=limits)],
                limitations=limits, created_at=now, updated_at=now,
                external_source=None,
                unknowns={'external_source': 'Internal independent checking only; no external review is asserted.'},
                reproducibility=dict(manifest=evidence[0])))
            added.append(cid)
    assert len(added) == 7
    data['updated_at'] = now
    validation = registry.validate(data, ROOT, read('docs/claims.schema.json'), 'available', previous)
    assert validation['valid'], validation['errors']
    out = ROOT / (B + 'ninth_registration')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    assert ledger.read_bytes() == before
    ledger.write_bytes(after)
    (out / 'CLAIMS.after.yaml').write_bytes(after)
    result = dict(
        timestamp=now, source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), new_claim_ids=added,
        checked_input_bindings=bindings, previous_ledger_sha256=hashlib.sha256(before).hexdigest(),
        ledger_sha256=hashlib.sha256(after).hexdigest(), validation=validation,
        registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN')
    (out / 'summary.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(new_verified_claims=len(added), claim_population=len(data['claims']), target_resolution='UNKNOWN')))


if __name__ == '__main__':
    main()

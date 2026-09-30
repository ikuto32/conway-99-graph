"""Register five exact independently reviewed statements; no producer self-approval."""
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


def sha(path):
    with (ROOT/path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads((ROOT/path).read_bytes())


def main():
    ledger = ROOT/'CLAIMS.yaml'
    before = ledger.read_bytes()
    old = registry.read_ledger(ledger)
    data = copy.deepcopy(old)
    assert len(data['claims']) == 148
    pins = {
        I+'identity_p_triangle_partition/summary.json': '15a32c8e4fb4928f78a6e931e09054ddcfd90c027717e8c0d0828c6f5406a516',
        I+'identity_p_triangle_partition/claim_bindings.json': '88b8834d2d21189f8d6d8d2b705487491dc9da69b0681c7fa8ccbe3d0a25441e',
        I+'identity_p_triangle_partition/claim_binding_editorial_addendum.json': '5b113e7bee53222a9b9d8a4665410744055329f549895725b0af4459c8a7e991',
        I+'prism_coarse60_bitflip/summary.json': 'ea41069f8bad705c1163e55d04735bca99c24276e447e1b1437ac7aa3d1b7123',
        I+'prism_coarse60_bitflip/claim_binding.json': 'ce4e835b64fa1853fbaaa5d986a68b7fcaef074306cae845daa4f6a72857dd55',
        I+'prism_coarse60_bitflip_object_calibration/summary.json': 'a0802564228f308fa925755f1ad1ad5b76409346a7889ecff3f9d46fe3b86254',
        I+'prism_coarse60_bitflip_native_outcome/summary.json': '64818d7ae4ea8ccf7dba08e88486bd1fb63ccd62507efad21b02180445c476f6',
        I+'prism_coarse60_arc_v2/summary.json': '04d85bcd864d7586074a68fa8637ec917ce42c93af1fa995fb9e2b5cac86db38',
        I+'prism_coarse60_triangle_cover/summary.json': '50add6b76aea5bade3d74cf56be71941aeed3587974efae2af8ebaf7db36754c',
    }
    for path, expected in list(pins.items()):
        assert sha(path) == expected, path
        for bound, value in read(path).get('inputs_sha256', {}).items():
            assert sha(bound) == value, bound
            assert bound not in pins or pins[bound] == value
            pins[bound] = value
    corrected = read(I+'identity_p_triangle_partition/claim_binding_editorial_addendum.json')
    assert corrected['status'].endswith('_PASS') and corrected['original_preserved']
    assert not corrected['statement_changed'] and not corrected['claim_revision_changed']
    groups = [
        ('identity-p', corrected['exact_corrected_claims'], I+'identity_p_triangle_partition/summary.json', [
            I+'identity_p_triangle_partition/claim_bindings.json', I+'identity_p_triangle_partition/claim_binding_editorial_addendum.json']),
        ('coarse60-bitflip', [read(I+'prism_coarse60_bitflip/claim_binding.json')], I+'prism_coarse60_bitflip/summary.json', [
            I+'prism_coarse60_bitflip/claim_binding.json', I+'prism_coarse60_bitflip_object_calibration/summary.json',
            I+'prism_coarse60_bitflip_native_outcome/summary.json', B+'prism_coarse60_bitflip_native_pilot/summary.json']),
    ]
    for name in ['prism_coarse60_arc_v2', 'prism_coarse60_triangle_cover']:
        path = I+name+'/summary.json'
        row = read(path)
        row['id'], row['revision'] = row['claim_id'], row['claim_revision']
        groups.append((name, [row], path, []))
    now = datetime.now(timezone.utc).isoformat()
    ids = []
    for label, claims, audit_path, extras in groups:
        audit = read(audit_path)
        assert audit['status'].endswith('_PASS')
        evidence, hashes = [], {}
        for number, path in enumerate([audit_path, *extras]):
            aid = 'sixteenth-'+label+'-evidence-'+str(number)
            assert aid not in {a['id'] for a in data['artifacts']}
            value = sha(path)
            assert path not in pins or pins[path] == value
            pins[path] = value
            evidence.append(aid)
            hashes[aid] = value
            data['artifacts'].append(dict(id=aid, path=path, sha256=value, availability='LOCAL_ONLY',
                retrieval='Exact workspace path; immutable source and raw-artifact bindings are recorded in the independent audit.',
                unavailable_reason='Sixteenth-cohort immutable publication has not been confirmed.'))
        for row in claims:
            assert row['recommendation'] == 'VERIFIED' and row['review_state'] == 'CLEAR' and row['revision'] == 1
            assert row['id'] not in {c['id'] for c in data['claims']}
            verification = dict(claim_revision=1, verifier=row['verifier'],
                method='independent_derivation' if row['kind']=='mathematical result' else 'independent_artifact_check',
                command_or_audit=audit_path, timestamp=row['updated_at'], outcome='PASS', scope=row['scope'],
                artifact_hashes=hashes, shared_components=audit['shared_components'],
                controls=['Exact written argument or raw-artifact reconstruction, with the positive and corrupted controls enumerated in the bound independent report.'],
                limitations=row['limitations'])
            data['claims'].append(dict(id=row['id'], revision=1, statement=row['statement'], kind=row['kind'], basis=row['basis'],
                status='VERIFIED', review_state='CLEAR', scope=dict(description=row['scope'], unrestricted_target=False, target_resolution='NONE'),
                assumptions=row['assumptions'], dependencies=row['dependencies'], evidence=evidence, verification=[verification],
                limitations=row['limitations'], created_at=now, updated_at=now, external_source=None,
                unknowns={'external_source': 'Internal independent verification; no novelty or external acceptance is asserted.'},
                reproducibility=dict(manifest=evidence[0])))
            ids.append(row['id'])
    assert len(ids) == 5 and len(data['claims']) == 153
    data['updated_at'] = now
    result = registry.validate(data, ROOT, read('docs/claims.schema.json'), 'available', old)
    assert result['valid'], result['errors']
    out = ROOT/(B+'sixteenth_preparation_registration')
    out.mkdir(parents=True, exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    assert ledger.read_bytes() == before
    ledger.write_bytes(after)
    (out/'CLAIMS.after.yaml').write_bytes(after)
    receipt = dict(timestamp=now, source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv], cwd=str(ROOT), new_claim_ids=ids, checked_input_bindings=pins,
        previous_ledger_sha256=hashlib.sha256(before).hexdigest(), ledger_sha256=hashlib.sha256(after).hexdigest(), validation=result,
        registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN',
        limitations=['The UNKNOWN normalized native outcome is evidence of execution only, not an exclusion or an additional mathematical claim.'])
    with (out/'summary.json').open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(new_verified=5, claim_population=153, target_resolution='UNKNOWN')))


if __name__ == '__main__':
    main()

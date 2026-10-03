"""One-shot integration of two already approved, distinct second-branch claims."""
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


def read(p):
    return json.loads((ROOT / p).read_bytes())


def main():
    path = ROOT / 'CLAIMS.yaml'
    before = path.read_bytes()
    old = registry.read_ledger(path)
    data = copy.deepcopy(old)
    assert len(data['claims']) == 178
    dirs = [I + 'hadamard_support_cut_lift_primal/', I + 'hadamard_f3_phase_obstruction/']
    pins = {
        dirs[0] + 'summary.json': '6ccae7d5f942948c10caf24eb246d436a5ae0ab3294de37f2aeb3647c85e3dc0',
        dirs[0] + 'claim_binding.json': 'c3f8177a82e423cb17359da4a78c2705698bfff7cd4a800be4275838a009fcb5',
        dirs[1] + 'summary.json': '0ccca8ba45e0ffa5ff0e1d8d7c051ffcbee3d9d30092fac5df33274d80dea346',
        dirs[1] + 'claim_binding.json': '1498efe4eb04c603bbf11af86ebca91cf0274fa8c0f70bcae35b9f57e51b9b6d',
        dirs[1] + 'registry_dependency_addendum.json': '4e8189fcb191e95f0ff8d267a3139ec03c641f0c9459ad7ce9bce0c3019635f2',
    }
    for p, sha in pins.items():
        assert h(p) == sha, p
    audits = [read(d + 'summary.json') for d in dirs]
    rows = [read(d + 'claim_binding.json') for d in dirs]
    expected = ['C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-LIFT-RATIONAL-PRIMAL',
                'C-FIXED-HADAMARD-SECOND-PARITY-GF3-PHASE-SCREEN']
    assert [r['id'] for r in rows] == expected
    assert audits[0]['status'] == 'INDEPENDENT_SUPPORT_CUT_PARITY_LIFT_RATIONAL_PRIMAL_PASS'
    assert audits[1]['status'] == 'INDEPENDENT_SELECTED_PARITY_GF3_PHASE_EXCLUSION_PASS'
    bindings = dict(pins)
    for audit in audits:
        for field in ['inputs_sha256', 'outputs_sha256']:
            for p, sha in audit[field].items():
                assert h(p) == sha, p
                assert p not in bindings or bindings[p] == sha, p
                bindings[p] = sha
    # The original artifact-reference dependencies stay in the immutable binding.
    # This separately approved registry addendum translates them to pinned IDs.
    mapping_path = dirs[1] + 'registry_dependency_addendum.json'
    mapping = read(mapping_path)
    assert mapping['claim_id'] == expected[1] and mapping['claim_revision'] == 1
    assert mapping['claim_binding_sha256'] == pins[dirs[1] + 'claim_binding.json']
    assert mapping['verifier'] == rows[1]['verifier'] and mapping['status'] == 'APPROVED_EDITORIAL_REGISTRY_MAPPING'
    assert mapping['original_dependencies'] == rows[1]['dependencies']
    rows[1]['dependencies'] = mapping['ledger_dependencies']
    bindings[mapping_path] = h(mapping_path)
    extras = [
        [dirs[0] + 'independent_matrix.json', dirs[0] + 'exact_primal_check.json'],
        [mapping_path, dirs[1] + 'minimal_obstruction.json', dirs[1] + 'independent_rank_certificate.json'],
    ]
    now = datetime.now(timezone.utc).isoformat()
    for index, (row, audit, directory) in enumerate(zip(rows, audits, dirs, strict=True)):
        assert row.get('recommendation', row.get('status')) == 'VERIFIED' and row['review_state'] == 'CLEAR'
        assert row['revision'] == 1 and row['id'] not in {c['id'] for c in data['claims']}
        evidence, hashes = [], {}
        for j, p in enumerate([directory + 'summary.json', directory + 'claim_binding.json', *extras[index]]):
            aid = f'nineteenth-selected-lift-{index}-evidence{j}'
            assert aid not in {a['id'] for a in data['artifacts']}
            sha = h(p)
            assert bindings[p] == sha
            evidence.append(aid)
            hashes[aid] = sha
            data['artifacts'].append(dict(id=aid, path=p, sha256=sha, availability='LOCAL_ONLY',
                retrieval='Exact workspace path; authenticated independent report binds raw artifacts and checking sources.',
                unavailable_reason='Nineteenth immutable evidence publication is not yet confirmed.'))
        verifier = audit['verifier'] if index == 0 else row['verifier']
        shared = audit['shared_components'] if index == 0 else mapping['shared_components']
        controls = ['All 117480 word triples, 240 option columns, 560 exact equations and 666 literal Gram products; genuine 3000-variable rational positive control and twelve corruptions.'
                    if index == 0 else 'Complete local permutation, affine-composition and 729 small-field rank controls; all 420 direct raw row-combination identities, alternate rank path, and ten corrupted cases.']
        verification = dict(claim_revision=1, verifier=verifier, method='independent_artifact_check',
            command_or_audit=directory + 'summary.json', timestamp=audit['timestamp'], outcome='PASS',
            scope=row['scope'], artifact_hashes=hashes, shared_components=shared,
            controls=controls, limitations=row['limitations'])
        data['claims'].append(dict(id=row['id'], revision=1, statement=row['statement'], kind=row['kind'],
            basis=row['basis'], status='VERIFIED', review_state='CLEAR',
            scope=dict(description=row['scope'], unrestricted_target=False, target_resolution='NONE'),
            assumptions=row['assumptions'], dependencies=row['dependencies'], evidence=evidence,
            verification=[verification], limitations=row['limitations'], created_at=row['created_at'],
            updated_at=row['updated_at'], external_source=None,
            unknowns={'external_source': 'Independent internal artifact checking only; no external acceptance or novelty claim.'},
            reproducibility=dict(manifest=evidence[0])))
    assert data['claims'][:len(old['claims'])] == old['claims']
    assert data['artifacts'][:len(old['artifacts'])] == old['artifacts']
    data['updated_at'] = now
    validation = registry.validate(data, ROOT, read('docs/claims.schema.json'), 'available', old)
    assert validation['valid'], validation['errors']
    counts = dict(claims=len(data['claims']),
                  verified_clear=sum(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in data['claims']),
                  candidate=sum(c['status'] == 'CANDIDATE' for c in data['claims']))
    assert counts == dict(claims=180, verified_clear=178, candidate=2)
    out = ROOT / (B + 'nineteenth_selected_lift_registration')
    out.mkdir(exist_ok=False)
    (out / 'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    assert path.read_bytes() == before, 'Concurrent ledger mutation; do not overwrite.'
    path.write_bytes(after)
    (out / 'CLAIMS.after.yaml').write_bytes(after)
    receipt = dict(timestamp=now,
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=sys.version,
        registrar_source_sha256=h(Path(__file__).relative_to(ROOT)), new_claim_ids=expected,
        checked_input_bindings=bindings, previous_ledger_sha256=hashlib.sha256(before).hexdigest(),
        ledger_sha256=hashlib.sha256(after).hexdigest(), validation=validation, counts=counts,
        existing_claim_records_unchanged=True, existing_artifact_records_unchanged=True,
        approved_dependency_translation=mapping,
        registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN',
        compatibility_note='A rational feasible relaxation and exclusion of its binary selected-parity branch are compatible; neither claim covers the whole support.')
    with (out / 'summary.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(new_verified=2, **counts, target_resolution='UNKNOWN')))


if __name__ == '__main__':
    main()

"""Register four already independently checked, explicitly scoped results.

The unpaired-design report uses exact_statement/trusted_components rather than
statement/shared_components. Map those fields without modifying frozen evidence.
This registrar checks bindings and schema; it performs no mathematical review.
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
I = B + 'independent_review/'


def h(p):
    with (ROOT / p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    path = ROOT / 'CLAIMS.yaml'
    before = path.read_bytes()
    old = registry.read_ledger(path)
    data = copy.deepcopy(old)
    specs = [
        ('one-c2-compact', I+'triangle_one_c2_compact/summary.json',
         'ea7d2ab3ea41118c6047261fc0dc7e6e7b23f667785cfec8d902c0fadc635a60',
         [B+'triangle_one_c2_compact/manifest.json', B+'triangle_one_c2_compact/instance.cnf',
          B+'triangle_one_c2_compact/model.json', I+'triangle_one_c2_compact_object_calibration/summary.json']),
        ('fixed25-row-exclusion', I+'one_c2_extension_rows/summary.json',
         '4b034eb6339d839cb86d7ac51d6b3b7c15db340061d197a4b2b7a34478cbd63b',
         [B+'one_c2_extension_rows/manifest.json', B+'one_c2_extension_rows/summary.json',
          'docs/AUDIT_20260930_ONE_C2_EXTENSION_ROWS.md']),
        ('six-prism-unpaired-kernel', I+'prism_unpaired_kernel/summary.json',
         'e6eab509282828851ceede47cb0ff710495e9e6102ca3f242f638781317310b1',
         [B+'prism_unpaired_kernel/manifest.json', B+'prism_unpaired_kernel/summary.json',
          'docs/AUDIT_20260930_PRISM_UNPAIRED_KERNEL.md']),
        ('full36-column-cap-encoding', I+'triangle_factor_column_caps/summary.json',
         '675dae8635175088bff026c59e171c1d2b2b66a4a880cd6a10500ae66bb74331',
         [B+'triangle_factor_column_caps/manifest.json', B+'triangle_factor_column_caps/instance.cnf',
          B+'triangle_factor_column_caps/model.json', I+'triangle_column_cap_factor_object_calibration/summary.json']),
    ]
    now = datetime.now(timezone.utc).isoformat()
    added, bindings, mappings = [], {}, {}
    for label, pin, expected, extras in specs:
        assert h(pin) == expected, pin
        r = json.loads((ROOT/pin).read_bytes())
        assert r['status'].startswith('INDEPENDENT_') and r['status'].endswith('_PASS')
        for p, value in r['inputs_sha256'].items():
            assert h(p) == value, p
            bindings[p] = value
        if label == 'six-prism-unpaired-kernel':
            assert r['status'] == 'INDEPENDENT_PRISM_UNPAIRED_FIVE_MATCHING_EXCLUSION_PASS'
            r['statement'] = r['exact_statement']
            r['shared_components'] = r['trusted_components']
            r['kind'] = 'exclusion'
            r['basis'] = ['DERIVED', 'COMPUTED']
            r['dependencies'] = []
            mappings[pin] = {'statement': 'exact_statement', 'shared_components': 'trusted_components',
                'kind': 'exclusion', 'basis': ['DERIVED', 'COMPUTED'], 'dependencies': [],
                'reason': 'Self-contained independent exact-rank and parity proof; native UNKNOWN run is not a premise.'}
        else:
            assert r['recommendation'] == 'VERIFIED'
        evidence, hashes = [], {}
        for index, p in enumerate([pin, *extras]):
            aid = label + ('-audit' if index == 0 else '-evidence'+str(index))
            assert aid not in {a['id'] for a in data['artifacts']}
            hashes[aid] = h(p)
            evidence.append(aid)
            data['artifacts'].append(dict(id=aid, path=p, sha256=hashes[aid], availability='LOCAL_ONLY',
                retrieval='Exact workspace path; pinned report and manifest identify source, commands and complete checking artifacts.',
                unavailable_reason='Not yet bound to a confirmed immutable public evidence commit.'))
        cid, revision = r['claim_id'], r['claim_revision']
        assert cid not in {c['id'] for c in data['claims']}
        method = 'independent_derivation' if label == 'six-prism-unpaired-kernel' else 'independent_artifact_check'
        data['claims'].append(dict(id=cid, revision=revision, statement=r['statement'], kind=r['kind'], basis=r['basis'],
            status='VERIFIED', review_state='CLEAR',
            scope=dict(description=r['scope'], unrestricted_target=False, target_resolution='NONE'),
            assumptions=r.get('assumptions') or ['Only the fixed core, incidence conditions and construction restrictions stated in the pinned audit.',
                'No nontrivial target automorphism or universal containment premise is assumed.'],
            dependencies=r['dependencies'], evidence=evidence,
            verification=[dict(claim_revision=revision, verifier=r['verifier'], method=method, command_or_audit=pin,
                timestamp=r['timestamp'], outcome='PASS', scope=r['scope'], artifact_hashes=hashes,
                shared_components=r['shared_components'],
                controls=['Exact checking scope, positive controls, deliberate corruptions and shared checking code are disclosed in the pinned report.'],
                limitations=r['limitations'])],
            limitations=r['limitations'], created_at=now, updated_at=now, external_source=None,
            unknowns={'external_source': 'Internal independent review only; no novelty or external acceptance asserted.'},
            reproducibility=dict(manifest=evidence[0])))
        added.append(cid)
    assert len(added) == 4
    data['updated_at'] = now
    result = registry.validate(data, ROOT, json.loads((ROOT/'docs/claims.schema.json').read_bytes()), 'available', old)
    assert result['valid'], result['errors']
    out = ROOT/(B+'eleventh_factor_registration')
    out.mkdir(parents=True, exist_ok=False)
    (out/'CLAIMS.before.yaml').write_bytes(before)
    after = yaml.safe_dump(data, sort_keys=False, width=110).encode()
    assert path.read_bytes() == before
    path.write_bytes(after)
    (out/'CLAIMS.after.yaml').write_bytes(after)
    receipt = dict(timestamp=now, source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), new_claim_ids=added, checked_input_bindings=bindings,
        report_field_mappings=mappings, previous_ledger_sha256=hashlib.sha256(before).hexdigest(),
        ledger_sha256=hashlib.sha256(after).hexdigest(), validation=result,
        registrar_performs_mathematical_verification=False, target_resolution='UNKNOWN')
    (out/'summary.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(new_verified=4, claim_population=len(data['claims']), target_resolution='UNKNOWN')))


if __name__ == '__main__':
    main()

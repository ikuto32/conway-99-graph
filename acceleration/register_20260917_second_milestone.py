"""Register reviewer-approved same13 and filtered-LP claims without rerunning discovery."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
REVIEW = 'acceleration/results/20260917_independent_review/'


def main():
    ledger_path = ROOT / 'CLAIMS.yaml'
    snapshot = ROOT / 'acceleration/results/20260917_resume/claims_before_second_milestone.yaml'
    if snapshot.exists():
        raise RuntimeError('One-time registration: snapshot already exists')
    ledger = yaml.safe_load(ledger_path.read_bytes())
    same = json.loads((ROOT / REVIEW / 'same13_scope.json').read_bytes())
    filtered = json.loads((ROOT / REVIEW / 'filtered_star_lp/audit.json').read_bytes())
    assert same['status'] == 'INDEPENDENT_SAME13_SELECTION_SCOPE_AND_INTERVAL_COMPARISON_PASS'
    assert filtered['status'] == 'INDEPENDENT_EXACT_FILTERED_STAR_MODEL_PRIMAL_DUAL_PASS'
    for report in (same, filtered):
        for path, expected in report['inputs_sha256'].items():
            assert sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    groups = {
        'same13': {
            'scope': REVIEW + 'same13_scope.json',
            'raw': REVIEW + 'same13_raw.json',
            'manifest': 'acceleration/results/20260917_same_execution/manifest.json',
            'checkpoint': 'acceleration/results/20260917_same_star_round/checkpoint.json',
        },
        'filtered-star': {
            'audit': REVIEW + 'filtered_star_lp/audit.json',
            'proof': REVIEW + 'FILTERED_STAR_LP_AUDIT.md',
            'certificate': REVIEW + 'filtered_star_lp/integer_certificate.json',
            'manifest': 'acceleration/results/20260917_theory/filtered_star_lp_baseline18481/manifest.json',
            'model': 'acceleration/results/20260917_theory/filtered_star_lp_baseline18481/exact_model.json.gz',
        },
    }
    for prefix, entries in groups.items():
        for name, path in entries.items():
            ledger['artifacts'].append(dict(id=prefix+'-'+name, path=path,
                sha256=sha256((ROOT/path).read_bytes()).hexdigest(), availability='LOCAL_ONLY',
                retrieval='Workspace relative path; awaiting next publication commit on draft PR1.',
                unavailable_reason='New local artifact, not yet published.'))
    hashes = {a['id']: a['sha256'] for a in ledger['artifacts']}
    now = datetime.now(timezone.utc).isoformat()
    items = []
    for binding in same['claim_bindings']:
        indices = ', '.join(map(str, binding['indices']))
        statement = ('For each of the 13 labeled assignments with family indices '+indices+
            ' in the hash-bound 20260917_same_star_round family, no srg(99,14,1,2) completion respects its prescribed present and absent edges.')
        if binding['id'].endswith('NO-IMPROVEMENT'):
            statement = ('For all 13 assignments with family indices '+indices+
                ', the exact original-domain STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS lower bound exceeds the independently verified upper bound for baseline18481; none improves that objective.')
        items.append((binding, statement, binding['scope'], same, 'same13',
            ['Independent raw full99 coefficient and exact rational checks; calibrated controls recorded in the prerequisite third-path audit.',
             'Frozen selection arithmetic and all13 interval comparisons checked.']))
    binding = filtered['claim_binding']
    items.append((binding, binding['statement'],
        'Only fixed baseline18481, using 15335 triangle/pair-filtered original-ID stars; exact rational endpoints are in filtered-star-audit. This assignment was already excluded.',
        filtered, 'filtered-star', [c['name']+': '+c['outcome'] for c in filtered['controls']]))
    for binding, statement, scope, report, group, controls in items:
        assert not any(c['id'] == binding['id'] for c in ledger['claims'])
        evidence = [group+'-'+name for name in groups[group]]
        ledger['claims'].append(dict(id=binding['id'], revision=1, statement=statement,
            kind='exclusion' if binding['id'].endswith('EXCLUSIONS') else 'mathematical result',
            basis=['DERIVED','COMPUTED'], status='VERIFIED', review_state='CLEAR',
            scope=dict(description=scope, unrestricted_target=False, target_resolution='NONE'),
            assumptions=['The hash-bound prescribed present/absent edges and disjoint-edge universe are fixed.',
                'No nontrivial automorphism is assumed.'],
            dependencies=binding.get('dependencies', []), evidence=evidence,
            verification=[dict(claim_revision=1, verifier='independent_verifier agent',
                method='independent_artifact_check', command_or_audit=groups[group].get('audit',groups[group].get('scope')),
                timestamp=report['timestamp'], outcome='PASS', scope=scope,
                artifact_hashes={name:hashes[name] for name in evidence},
                shared_components=report['shared_trusted_components'], controls=controls,
                limitations=['Prerequisite complete-domain or sound-filtered-domain audits are reused by immutable hashes.',
                    'No unrestricted target coverage established.'])],
            limitations=['No new target resolution; finite fixed assignments only.',
                'The filtered objective has a different feasible domain and is not directly compared to original-domain ranking values.'],
            created_at=now, updated_at=now, unknowns={'external_source':'New current-project claim, not an archive import.'},
            external_source=None, reproducibility={'manifest':group+'-manifest'}))
    snapshot.write_bytes(ledger_path.read_bytes())
    ledger['updated_at'] = now
    ledger_path.write_text(yaml.safe_dump(ledger, sort_keys=False, width=110), encoding='utf-8')


if __name__ == '__main__':
    main()

"""Integrate the separately signed-off exact claims without overwriting evidence."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
REVIEW='acceleration/results/20260917_independent_review'
RUN='acceleration/results/20260917_fresh_star_shortlist'


def main():
    ledger=yaml.safe_load((ROOT/'CLAIMS.yaml').read_text(encoding='utf-8'))
    report=json.loads((ROOT/REVIEW/'claim_bindings.json').read_bytes())
    raw=json.loads((ROOT/REVIEW/'batch_raw_review.json').read_bytes())
    assert report['status']=='INDEPENDENT_CLAIM_SCOPE_BINDING_PASS'
    assert report['distinct_selected']==report['independent_raw_passes']==16
    assert len(report['exact_intervals_strictly_above_incumbent_indices'])==16
    # No agent agreement substitutes for these preserved raw checking reports.
    for doc in (report,raw):
        for p,h in doc['inputs_sha256'].items():
            assert sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    def add(id,path):
        assert all(a['id']!=id for a in ledger['artifacts'])
        ledger['artifacts'].append(dict(id=id,path=path,sha256=sha256((ROOT/path).read_bytes()).hexdigest(),
            availability='LOCAL_ONLY',retrieval='Workspace relative path; publication pending on codex/fresh-star-audit-20260917.',unavailable_reason='New local artifact, not yet published.'))
        return id
    added=[add('fresh-independent-binding',REVIEW+'/claim_bindings.json'),
        add('fresh-independent-raw',REVIEW+'/batch_raw_review.json'),
        add('fresh-mathematical-audit',REVIEW+'/MATHEMATICAL_AUDIT.md'),
        add('fresh-wave-summary',RUN+'/summary.json'),
        add('fresh-wave-receipt','acceleration/results/20260917_resume/evaluation_receipt.json')]
    for row in json.loads((ROOT/RUN/'summary.json').read_bytes())['records']:
        # Explicit raw identities complement the recursively bound reports.
        for field in ('candidate','certificate','independent_pair_audit'):
            added.append(add(f"fresh-{field}-{row['proposal_index']}",row[field+'_path']))
    hashes={a['id']:a['sha256'] for a in ledger['artifacts']}
    fresh=next(c for c in ledger['claims'] if c['id']=='C-FRESH-STAR-16-EXCLUSIONS')
    assert fresh['revision']==1 and fresh['status']=='CANDIDATE'
    fresh.update(revision=2,status='VERIFIED',updated_at=datetime.now(timezone.utc).isoformat())
    fresh['unknowns'].pop('independent_verification')
    fresh['evidence']+=added
    def checking(revision,scope):
        return dict(claim_revision=revision,verifier=report['verifier'],method='independent_artifact_check',
            command_or_audit=REVIEW+'/claim_bindings.json; '+REVIEW+'/batch_raw_review.json; '+REVIEW+'/MATHEMATICAL_AUDIT.md',
            timestamp=report['timestamp'],outcome='PASS',scope=scope,
            artifact_hashes={id:hashes[id] for id in added},shared_components=report['shared_trusted_components'],
            controls=['Independent matrix coefficient derivation and four matrix fixtures','Historical positive and six corrupted certificate controls','Every selected raw rational interval and exact certificate checked','Union16 selection rebuilt; labeled edge-set uniqueness checked'],
            limitations=['Original domain completeness uses the reviewed independent enumerator, freshly run for each selected case.','No nontrivial automorphism, unrestricted normalization proof, exhaustive target coverage or peer review claimed.'])
    fresh['verification'].append(checking(2,'All16 fixed-K exclusions in the exact original statement.'))
    empirical=deepcopy(fresh)
    empirical.update(id='C-FRESH-STAR-16-NO-IMPROVEMENT',revision=1,
        statement='For each of the sixteen fixed labeled configurations in C-FRESH-STAR-16-EXCLUSIONS revision2, its exact lower bound for STAR_SIMPLEX_RECIPROCITY_PLUS_LINEAR_CAP_VIOLATIONS exceeds the exact incumbent18481 upper bound in C-STAR-BASELINE-18481 revision1; consequently none improves the optimum of this same continuous relaxation.',
        kind='empirical/engineering result',created_at=datetime.now(timezone.utc).isoformat(),
        dependencies=[dict(id='C-STAR-BASELINE-18481',revision=1,relation='uses_result'),dict(id=fresh['id'],revision=2,relation='verification_dependency')],
        verification=[checking(1,'Exact rational interval separation for all16, compared only with the same incumbent star objective.')])
    empirical['updated_at']=empirical['created_at']
    ledger['claims'].append(empirical)
    ledger['updated_at']=datetime.now(timezone.utc).isoformat()
    (ROOT/'CLAIMS.yaml').write_text(yaml.safe_dump(ledger,sort_keys=False,allow_unicode=True,width=110),encoding='utf-8')


if __name__=='__main__':
    main()

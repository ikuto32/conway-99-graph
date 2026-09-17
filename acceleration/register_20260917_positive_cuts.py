"""Register separately approved positive-only matching clauses, preserving prior ledger."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]


def main():
    ledger_path=ROOT/'CLAIMS.yaml'
    snapshot=ROOT/'acceleration/results/20260917_resume/claims_before_positive_cuts.yaml'
    assert not snapshot.exists()
    ledger=yaml.safe_load(ledger_path.read_bytes())
    review_path='acceleration/results/20260917_independent_review/matching_positive_cuts_recheck.json'
    review=json.loads((ROOT/review_path).read_bytes())
    assert review['status']=='INDEPENDENT_POSITIVE_MATCHING_CUTS_PASS'
    assert len(review['records'])==16
    for path,expected in review['inputs_sha256'].items():
        assert sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
    evidence={'positive-cuts-audit':review_path,
        'positive-cuts-proof':'acceleration/results/20260917_independent_review/MATCHING_POSITIVE_CUTS_AUDIT.md',
        'positive-cuts-manifest':'acceleration/results/20260917_matching_cut/manifest.json'}
    for path in review['inputs_sha256']:
        if path.startswith('acceleration/results/20260917_matching_cut/vertex_'):
            evidence['positive-cuts-'+Path(path).stem]=path
    assert len(evidence)==19
    for id,path in evidence.items():
        ledger['artifacts'].append(dict(id=id,path=path,sha256=sha256((ROOT/path).read_bytes()).hexdigest(),
            availability='LOCAL_ONLY',retrieval='Workspace relative path; awaiting publication on draft PR1.',
            unavailable_reason='New local artifact, not yet published.'))
    hashes={a['id']:a['sha256'] for a in ledger['artifacts']}
    now=datetime.now(timezone.utc).isoformat()
    scope='Sixteen exact positive-adjacency clauses conditional only on the 189 named positive root-scaffold edges; all other adjacencies, including same-fibre and unlisted overlap edges, are unrestricted.'
    assert not any(c['id']==review['claim_id'] for c in ledger['claims'])
    ledger['claims'].append(dict(id=review['claim_id'],revision=review['claim_revision'],statement=review['statement'],
        kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
        assumptions=review['assumptions']+['No nontrivial automorphism is assumed.'],dependencies=[],
        evidence=list(evidence),verification=[dict(claim_revision=1,verifier=review['verifier'],
            method='independent_artifact_check',command_or_audit=review_path+' and '+evidence['positive-cuts-proof'],
            timestamp=review['timestamp'],outcome='PASS',scope=scope,
            artifact_hashes={id:hashes[id] for id in evidence},shared_components=review['shared_trusted_components'],
            controls=[c['name']+': '+c['outcome'] for c in review['controls']],limitations=review['limitations'])],
        limitations=review['limitations']+['No complete coverage of labeled configurations is established.'],
        created_at=now,updated_at=now,unknowns={'external_source':'New current-project independently checked conditional result.'},
        external_source=None,reproducibility={'manifest':'positive-cuts-manifest'}))
    snapshot.write_bytes(ledger_path.read_bytes())
    ledger['updated_at']=now
    ledger_path.write_text(yaml.safe_dump(ledger,sort_keys=False,width=110),encoding='utf-8')


if __name__=='__main__':main()

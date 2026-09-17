"""Register the independent identity-cut union check; no discovery self-approval."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]


def main():
    ledger_path=ROOT/'CLAIMS.yaml'
    snapshot=ROOT/'acceleration/results/20260917_resume/claims_before_cut_application.yaml'
    assert not snapshot.exists()
    ledger=yaml.safe_load(ledger_path.read_bytes())
    review_path='acceleration/results/20260917_independent_review/matching_cut_application.json'
    review=json.loads((ROOT/review_path).read_bytes())
    assert review['status']=='INDEPENDENT_IDENTITY_CUT_APPLICATION_PASS'
    assert len(review['records'])==29 and not any(r['empty_domains'] for r in review['records'])
    for path,expected in review['inputs_sha256'].items():
        assert sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
    evidence={'identity-cuts-application-audit':review_path,
        'identity-cuts-application-source':'acceleration/audit_20260917_matching_cut_application.py',
        'identity-cuts-application-manifest':'acceleration/results/20260917_matching_cut_application/manifest.json',
        'identity-cuts-application-summary':'acceleration/results/20260917_matching_cut_application/summary.json'}
    for id,path in evidence.items():
        ledger['artifacts'].append(dict(id=id,path=path,sha256=sha256((ROOT/path).read_bytes()).hexdigest(),
            availability='LOCAL_ONLY',retrieval='Workspace relative path; awaiting publication on draft PR1.',
            unavailable_reason='New local artifact, not yet published.'))
    hashes={a['id']:a['sha256'] for a in ledger['artifacts']}
    now=datetime.now(timezone.utc).isoformat()
    scope=review['scope']+'; original ID tables are unchanged and all84 vertex domains remain nonempty in every record.'
    assert not any(c['id']==review['claim_id'] for c in ledger['claims'])
    ledger['claims'].append(dict(id=review['claim_id'],revision=1,
        statement='On the frozen 29 candidate records and their 747064 original (candidate, outer vertex, domain ID) choices, the union of the 16 identity-labeled positive matching clauses removes exactly 324 distinct choices, leaving 746740 choices and no empty vertex domain; the 324 clause hits do not overlap.',
        kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
        scope=dict(description=scope,unrestricted_target=False,target_resolution='NONE'),
        assumptions=['The exact frozen 29 candidate records, original domain tables, and identity-labeled 16 clause sets named by the audit.',
            'No nontrivial automorphism is assumed.'],dependencies=[review['dependency']],evidence=list(evidence),
        verification=[dict(claim_revision=1,verifier='independent_verifier agent',method='independent_artifact_check',
            command_or_audit=review_path,timestamp=review['timestamp'],outcome='PASS',scope=scope,
            artifact_hashes={id:hashes[id] for id in evidence},shared_components=review['shared_trusted_components'],
            controls=[c['name']+': '+c['outcome'] for c in review['controls']],limitations=review['limitations'])],
        limitations=review['limitations'],created_at=now,updated_at=now,
        unknowns={'external_source':'New current-project finite application claim.'},external_source=None,
        reproducibility={'manifest':'identity-cuts-application-manifest'}))
    snapshot.write_bytes(ledger_path.read_bytes())
    ledger['updated_at']=now
    ledger_path.write_text(yaml.safe_dump(ledger,sort_keys=False,width=110),encoding='utf-8')


if __name__=='__main__':main()

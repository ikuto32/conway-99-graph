"""Attach confirmed immutable Git pointers to unchanged first-milestone evidence."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml
import validate_claims as validator


def main():
    root=Path(__file__).resolve().parents[1]
    commit='eb627889e01318ed516b5b2e004434b4589ae116'
    assert subprocess.check_output(['git','rev-parse','origin/codex/eight-coordinate-continuation-20260930'],text=True).strip()==commit
    path=root/'CLAIMS.yaml';previous=validator.read_ledger(path);data=validator.read_ledger(path)
    changed=[]
    for artifact in data['artifacts']:
        if artifact['availability']!='LOCAL_ONLY' or '20260930' not in str(artifact['path']):continue
        blob=subprocess.check_output(['git','show',commit+':'+artifact['path']])
        assert sha256(blob).hexdigest()==artifact['sha256']==sha256((root/artifact['path']).read_bytes()).hexdigest()
        artifact.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{commit}/{artifact["path"]}',unavailable_reason=None)
        changed.append(artifact['id'])
    data['updated_at']=datetime.now(timezone.utc).isoformat()
    result=validator.validate(data,root,json.loads((root/'docs/claims.schema.json').read_bytes()),'available',previous)
    assert result['valid'],result['errors']
    before=sha256(path.read_bytes()).hexdigest()
    path.write_text(yaml.safe_dump(data,sort_keys=False,width=110),encoding='utf-8')
    receipt=dict(timestamp=data['updated_at'],published_commit=commit,artifact_ids=changed,artifacts_changed=len(changed),
        impact_review='Only availability and immutable retrieval metadata changed. Every artifact byte hash, claim statement/revision/dependency and verification record is unchanged. Historical first-milestone ledger bytes remain in claims_at_first_milestone.yaml and the published Git commit.',
        previous_ledger_sha256=before,ledger_sha256=sha256(path.read_bytes()).hexdigest(),validation=result,
        mathematical_claim_changes=[],target_resolution='UNKNOWN')
    with(root/'acceleration/results/20260930_resume/publication_pointer_receipt.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,indent=2)
    print(json.dumps({'published_evidence_artifacts':len(changed),'mathematical_claim_changes':[]}))


if __name__=='__main__':main()

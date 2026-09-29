"""Bind new eighth evidence to its observed immutable remote commit."""
from datetime import datetime,timezone
import hashlib,json,subprocess
from pathlib import Path
import yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1]
COMMIT='a25a913e3b568be4f60555b82a262d3d0531d836'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True).split()[0]
    assert remote==COMMIT
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();previous=registry.read_ledger(path);data=registry.read_ledger(path)
    changed=[];remaining=[]
    for a in data['artifacts']:
        if a['availability']!='LOCAL_ONLY'or not a['path']or'20260930'not in a['path']:continue
        blob=subprocess.run(['git','show',COMMIT+':'+a['path']],cwd=ROOT,capture_output=True)
        if blob.returncode:remaining.append(a['id']);continue
        assert sha(blob.stdout)==a['sha256']==sha((ROOT/a['path']).read_bytes())
        a.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{COMMIT}/{a["path"]}',unavailable_reason=None);changed.append(a['id'])
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',previous);assert result['valid'],result['errors']
    folder=ROOT/'acceleration/results/20260930_resume'
    with(folder/'claims_before_eighth_publication.yaml').open('xb')as f:f.write(before)
    assert path.read_bytes()==before;path.write_bytes(yaml.safe_dump(data,sort_keys=False,width=110).encode())
    receipt=dict(timestamp=now,published_commit=COMMIT,confirmed_remote_ref=remote,new_public_artifact_ids=changed,remaining_local_originals=remaining,
        previous_ledger_sha256=sha(before),ledger_sha256=sha(path.read_bytes()),validation=result,mathematical_claim_changes=[],target_resolution='UNKNOWN',
        scope='Artifact availability/retrieval only; all exact statements/revisions/dependencies/verification records and raw hashes unchanged.')
    with(folder/'eighth_publication_pointer_receipt.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps({'new_public_artifacts':len(changed),'remaining_local_originals':len(remaining),'mathematical_claim_changes':[]}))
if __name__=='__main__':main()

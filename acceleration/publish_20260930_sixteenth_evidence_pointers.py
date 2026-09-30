"""Bind sixteenth evidence to its observed immutable remote commit."""
from datetime import datetime, timezone
import hashlib, json, subprocess
from pathlib import Path
import yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1]
COMMIT='cfe289017758632d08bdc7166b1c95f74ff21b71'
def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True).split()[0]
    assert remote==COMMIT
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();previous=registry.read_ledger(path);data=registry.read_ledger(path)
    changed=[];remaining=[]
    for artifact in data['artifacts']:
        if artifact['availability']!='LOCAL_ONLY' or not artifact['path'] or '20260930' not in artifact['path']:continue
        blob=subprocess.run(['git','show',COMMIT+':'+artifact['path']],cwd=ROOT,capture_output=True)
        if blob.returncode:remaining.append(artifact['id']);continue
        assert sha(blob.stdout)==artifact['sha256']==sha((ROOT/artifact['path']).read_bytes())
        artifact.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{COMMIT}/{artifact["path"]}',unavailable_reason=None)
        changed.append(artifact['id'])
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',previous)
    assert result['valid'],result['errors']
    assert data['claims']==previous['claims']
    folder=ROOT/'acceleration/results/20260930_resume'
    with(folder/'claims_before_sixteenth_publication.yaml').open('xb')as stream:stream.write(before)
    assert path.read_bytes()==before;path.write_bytes(yaml.safe_dump(data,sort_keys=False,width=110).encode())
    receipt=dict(timestamp=now,published_commit=COMMIT,confirmed_remote_ref=remote,new_public_artifact_ids=changed,
        remaining_local_originals=remaining,previous_ledger_sha256=sha(before),ledger_sha256=sha(path.read_bytes()),validation=result,
        mathematical_claim_changes=[],target_resolution='UNKNOWN',
        scope='Availability and retrieval only; exact statements, revisions, dependencies, verification records and raw hashes unchanged.')
    with(folder/'sixteenth_publication_pointer_receipt.json').open('x',encoding='utf-8',newline='\n')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(new_public_artifacts=len(changed),remaining_local_originals=len(remaining),mathematical_claim_changes=[])))
if __name__=='__main__':main()

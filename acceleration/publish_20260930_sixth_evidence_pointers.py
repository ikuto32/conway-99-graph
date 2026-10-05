"""Confirm immutable pushed evidence before changing artifact availability."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
COMMIT='ade39777b7a970b6acfaa8011ce396578785c3e3'
def main():
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],text=True).split()[0]
    assert remote==COMMIT
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=registry.read_ledger(path)
    changed=[];local=[]
    for artifact in data['artifacts']:
        if artifact['availability']!='LOCAL_ONLY' or not artifact['path'] or '20260930' not in artifact['path']:continue
        blob=subprocess.run(['git','show',COMMIT+':'+artifact['path']],capture_output=True)
        if blob.returncode:
            local.append(artifact['id']);continue
        assert sha256(blob.stdout).hexdigest()==artifact['sha256']==sha256((ROOT/artifact['path']).read_bytes()).hexdigest()
        artifact.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{COMMIT}/{artifact["path"]}',unavailable_reason=None);changed.append(artifact['id'])
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old);assert result['valid'],result['errors']
    folder=ROOT/'acceleration/results/20260930_resume'
    with (folder/'claims_before_sixth_publication.yaml').open('xb') as f:f.write(before)
    assert path.read_bytes()==before
    path.write_bytes(yaml.safe_dump(data,sort_keys=False,width=110).encode())
    receipt=dict(timestamp=now,published_commit=COMMIT,confirmed_remote_ref=remote,new_public_artifact_ids=changed,remaining_local_originals=local,previous_ledger_sha256=sha256(before).hexdigest(),ledger_sha256=sha256(path.read_bytes()).hexdigest(),validation=result,mathematical_claim_changes=[],target_resolution='UNKNOWN',scope='Availability/retrieval metadata only; statements, revisions, dependency pins, verification records, and all artifact byte identities unchanged. Large originals retain their separate exact public recovery recipes; incomplete proof traces remain local and are not certificates.')
    with (folder/'sixth_publication_pointer_receipt.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(dict(new_public_artifacts=len(changed),remaining_local_originals=len(local),mathematical_claim_changes=[])))
if __name__=='__main__':main()

"""Availability-only updates after confirming the exact public evidence commit."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1];COMMIT='9125c523190464b147f67ec1eb58887ad8bb9295'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True).split()[0];assert remote==COMMIT
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=registry.read_ledger(path);changed=[];remaining=[]
    assert len(data['claims'])==267
    for a in data['artifacts']:
        if a['availability']!='LOCAL_ONLY'or not a['path']or'20260930'not in a['path']:continue
        blob=subprocess.run(['git','show',COMMIT+':'+a['path']],cwd=ROOT,capture_output=True)
        if blob.returncode:remaining.append(a['id']);continue
        assert sha(blob.stdout)==a['sha256']==sha((ROOT/a['path']).read_bytes())
        a.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{COMMIT}/{a["path"]}',unavailable_reason=None);changed.append(a['id'])
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now;assert data['claims']==old['claims']
    validation=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old);assert validation['valid'],validation['errors']
    folder=ROOT/'acceleration/results/20260930_resume'
    with(folder/'claims_before_twentyfifth_publication.yaml').open('xb')as stream:stream.write(before)
    assert path.read_bytes()==before;path.write_bytes(yaml.safe_dump(data,sort_keys=False,width=110).encode())
    receipt=dict(timestamp=now,command=[sys.executable,*sys.argv],cwd=str(ROOT),published_commit=COMMIT,confirmed_remote_ref=remote,
        new_public_artifact_ids=changed,remaining_local_originals=remaining,previous_ledger_sha256=sha(before),ledger_sha256=sha(path.read_bytes()),validation=validation,
        mathematical_claim_changes=[],target_resolution='UNKNOWN',scope='Artifact availability and immutable retrieval only; no claim, dependency or verification change.')
    with(folder/'twentyfifth_publication_pointer_receipt.json').open('x',encoding='utf8',newline='\n')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(new_public_artifacts=len(changed),remaining_local_originals=len(remaining),mathematical_claim_changes=[])))
if __name__=='__main__':main()

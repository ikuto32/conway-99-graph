"""Record immutable wave29 retrieval pointers only after remote confirmation."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--commit',required=True);a=ap.parse_args();assert re.fullmatch('[0-9a-f]{40}',a.commit)
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True).split()[0];assert remote==a.commit
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=registry.read_ledger(path)
    assert len(data['claims'])==300 and sha(before)=='297d6d915c244ccc6dd82c39939eef917a2b0ffa8a76126185b386774a097baf'
    changed=[];remaining=[]
    for artifact in data['artifacts']:
        if artifact['availability']!='LOCAL_ONLY' or not artifact['path']:continue
        blob=subprocess.run(['git','show',a.commit+':'+artifact['path']],cwd=ROOT,capture_output=True)
        if blob.returncode:remaining.append(artifact['id']);continue
        assert sha(blob.stdout)==artifact['sha256']==sha((ROOT/artifact['path']).read_bytes())
        artifact.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{a.commit}/{artifact["path"]}',unavailable_reason=None);changed.append(artifact['id'])
    assert len(changed)==12 and data['claims']==old['claims'];now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old);assert validation['valid'],validation['errors']
    folder=ROOT/'acceleration/results/20261001_resume'
    with(folder/'claims_before_twentyninth_publication.yaml').open('xb')as f:f.write(before)
    assert path.read_bytes()==before;path.write_bytes(yaml.safe_dump(data,sort_keys=False,width=110).encode())
    record=dict(timestamp=now,source_sha256=sha(Path(__file__).read_bytes()),command=[sys.executable,*sys.argv],cwd=str(ROOT),published_commit=a.commit,confirmed_remote_ref=remote,new_public_artifact_ids=changed,remaining_local_originals=remaining,previous_ledger_sha256=sha(before),ledger_sha256=sha(path.read_bytes()),validation=validation,mathematical_claim_changes=[],target_resolution='UNKNOWN',scope='Artifact availability/retrieval only; exact claims, dependencies and original checks unchanged.')
    with(folder/'twentyninth_publication_pointer_receipt.json').open('x',encoding='utf8',newline='\n')as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(dict(new_public_artifacts=len(changed),remaining_local_originals=len(remaining),mathematical_claim_changes=[])))
if __name__=='__main__':main()

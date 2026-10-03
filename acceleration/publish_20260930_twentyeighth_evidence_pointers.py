"""Availability-only wave28 update after exact remote evidence commit confirmation."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--commit',required=True);args=ap.parse_args();commit=args.commit;assert re.fullmatch('[0-9a-f]{40}',commit)
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True).split()[0];assert remote==commit
    path=ROOT/'CLAIMS.yaml';before=path.read_bytes();old=registry.read_ledger(path);data=registry.read_ledger(path);changed=[];remaining=[]
    assert len(data['claims'])==294 and sha(before)=='c2889537ea68b90736a5d51e13b6aafd6163b9a1e98d2f05eb1bd6e4331cf441'
    for a in data['artifacts']:
        if a['availability']!='LOCAL_ONLY'or not a['path']or'20260930'not in a['path']:continue
        blob=subprocess.run(['git','show',commit+':'+a['path']],cwd=ROOT,capture_output=True)
        if blob.returncode:remaining.append(a['id']);continue
        assert sha(blob.stdout)==a['sha256']==sha((ROOT/a['path']).read_bytes())
        a.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{commit}/{a["path"]}',unavailable_reason=None);changed.append(a['id'])
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now;assert data['claims']==old['claims']and len(changed)==16
    validation=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old);assert validation['valid'],validation['errors']
    folder=ROOT/'acceleration/results/20260930_resume'
    with(folder/'claims_before_twentyeighth_publication.yaml').open('xb')as stream:stream.write(before)
    assert path.read_bytes()==before;path.write_bytes(yaml.safe_dump(data,sort_keys=False,width=110).encode())
    receipt=dict(timestamp=now,source_sha256=sha(Path(__file__).read_bytes()),command=[sys.executable,*sys.argv],cwd=str(ROOT),published_commit=commit,confirmed_remote_ref=remote,new_public_artifact_ids=changed,remaining_local_originals=remaining,previous_ledger_sha256=sha(before),ledger_sha256=sha(path.read_bytes()),validation=validation,mathematical_claim_changes=[],target_resolution='UNKNOWN',scope='Artifact availability and immutable retrieval only; no statement, dependency or verification change.')
    with(folder/'twentyeighth_publication_pointer_receipt.json').open('x',encoding='utf8',newline='\n')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(new_public_artifacts=len(changed),remaining_local_originals=len(remaining),mathematical_claim_changes=[])))
if __name__=='__main__':main()

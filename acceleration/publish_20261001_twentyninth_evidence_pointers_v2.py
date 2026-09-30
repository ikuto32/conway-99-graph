"""Confirm exact published bytes and update only the fourteen declared artifact pointers."""
from datetime import datetime, timezone
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, sys, yaml
import validate_claims as registry
ROOT=Path(__file__).resolve().parents[1]
BEFORE='297d6d915c244ccc6dd82c39939eef917a2b0ffa8a76126185b386774a097baf'
EXPECTED={'large-gpu-gate-source','large-gpu-gate-build'} | {
    f'twentyninth-{cohort}-{i}-evidence{j}'
    for cohort in ('initial','followup') for i in range(3) for j in range(2)}
OUT=ROOT/'acceleration/results/20261001_twentyninth_publication_pointers_v2'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:
        json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--commit',required=True);a=ap.parse_args()
    assert re.fullmatch('[0-9a-f]{40}',a.commit)
    OUT.mkdir(exist_ok=False);path=ROOT/'CLAIMS.yaml';before=path.read_bytes();after=None
    try:
        assert sha(before)==BEFORE
        remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930'],cwd=ROOT,text=True).split()[0]
        assert remote==a.commit
        old=registry.read_ledger(path);data=registry.read_ledger(path);assert len(data['claims'])==300
        changed=[];remaining=[];checked=[]
        for artifact in data['artifacts']:
            if artifact['availability']!='LOCAL_ONLY' or not artifact['path']:continue
            blob=subprocess.run(['git','show',a.commit+':'+artifact['path']],cwd=ROOT,capture_output=True)
            if blob.returncode:remaining.append(artifact['id']);continue
            assert sha(blob.stdout)==artifact['sha256']==sha((ROOT/artifact['path']).read_bytes())
            checked.append(dict(id=artifact['id'],path=artifact['path'],sha256=artifact['sha256'],bytes=len(blob.stdout)))
            artifact.update(availability='PUBLIC',retrieval=f'https://github.com/ikuto32/conway-99-graph/blob/{a.commit}/{artifact["path"]}',unavailable_reason=None)
            changed.append(artifact['id'])
        assert set(changed)==EXPECTED and len(changed)==14 and data['claims']==old['claims']
        assert len(remaining)==14
        now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
        validation=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'available',old)
        assert validation['valid'],validation['errors']
        after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
        record=dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            source_sha256=sha(Path(__file__).read_bytes()),command=[sys.executable,*sys.argv],cwd=str(ROOT),
            published_commit=a.commit,confirmed_remote_ref=remote,new_public_artifact_ids=changed,
            prior_local_artifacts_now_public=['large-gpu-gate-source','large-gpu-gate-build'],
            remaining_local_originals=remaining,previous_ledger_sha256=sha(before),ledger_sha256=sha(after),
            checked_commit_blobs=checked,validation=validation,mathematical_claim_changes=[],target_resolution='UNKNOWN',
            scope='Availability/retrieval only. Twelve new claim evidence records and two older source/build records match the exact published commit. Original claims, dependencies, hashes and checks remain unchanged.')
        with(OUT/'CLAIMS.before.yaml').open('xb')as f:f.write(before)
        with(OUT/'CLAIMS.after.yaml').open('xb')as f:f.write(after)
        pending=OUT/'CLAIMS.pending.yaml'
        with pending.open('xb')as f:f.write(after);f.flush();os.fsync(f.fileno())
        pending_record=OUT/'receipt.pending.json';save(pending_record,record)
        save(OUT/'transaction.json',dict(status='PREPARED_NOT_COMMITTED',before_sha256=sha(before),after_sha256=sha(after),
            prepared_receipt_sha256=sha(pending_record.read_bytes()),
            recovery='If receipt.json is absent, compare live ledger with immutable before/after and preserve this transaction for separate audit. Do not rerun.',
            limitation='Relies on local same-volume atomic rename semantics; no universal power-loss or concurrent-writer guarantee.'))
        assert path.read_bytes()==before
        os.replace(pending,path);os.replace(pending_record,OUT/'receipt.json')
        print(json.dumps(dict(new_public_artifacts=len(changed),remaining_local_originals=len(remaining),ledger_sha256=sha(after),mathematical_claim_changes=[])))
    except BaseException as ex:
        observed=None;reason=None
        try:observed=sha(path.read_bytes())
        except BaseException as inner:reason=repr(inner)
        state='UNCHANGED_BEFORE' if observed==sha(before) else 'EXPECTED_AFTER' if after is not None and observed==sha(after) else 'UNKNOWN_OR_UNEXPECTED'
        save(OUT/'failure.json',dict(error=repr(ex),observed_ledger_sha256=observed,observation_unavailable_reason=reason,commit_state=state,recovery_required=state!='UNCHANGED_BEFORE'))
        raise
if __name__=='__main__':main()

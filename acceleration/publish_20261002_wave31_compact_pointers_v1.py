"""Confirm immutable compact artifacts, without asserting full proof recovery.

Only artifact availability/retrieval metadata changes; checking identities,
statements and verification records remain exactly unchanged.
"""
import argparse
import copy
from datetime import datetime,timezone
import hashlib,json,os,subprocess
from pathlib import Path
import yaml
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
COMMIT='28440b31f4effee3b25e30259110acc734695bf0'
ARCHIVE_COMMIT='85e705cc6c2a14d123120c93a847e30aaab1789e'
BEFORE='6c090aacc57bd7fce40c471603a7e9548a713ca14bef8ecfde68125b558f25b3'


def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    before=(ROOT/'CLAIMS.yaml').read_bytes()
    if hashlib.sha256(before).hexdigest()!=BEFORE:raise ValueError('Exact313-claim ledger required')
    remote=git('ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930').decode().strip()
    if remote.split()[0]!=COMMIT:raise ValueError('Expected immutable compact publication not observed at remote branch')
    old=registry.read_ledger(ROOT/'CLAIMS.yaml');data=copy.deepcopy(old);records=[]
    for artifact in data['artifacts']:
        if not artifact['id'].startswith('wave31-'):continue
        path=artifact['path']
        if path.startswith('external_conway99_research/'):
            relative=path.split('/',1)[1]
            raw=git('show',ARCHIVE_COMMIT+':'+relative,cwd=ROOT/'external_conway99_research')
            url='https://github.com/YesterdaysLemon/conway-99-research/blob/'+ARCHIVE_COMMIT+'/'+relative
            publication_commit=ARCHIVE_COMMIT
        else:
            raw=git('show',COMMIT+':'+path)
            url='https://github.com/ikuto32/conway-99-graph/blob/'+COMMIT+'/'+path
            publication_commit=COMMIT
        if hashlib.sha256(raw).hexdigest()!=artifact['sha256']:raise ValueError('Immutable publication identity '+path)
        artifact['availability']='PUBLIC';artifact['retrieval']=url+'; only this exact artifact is published. Full batch05 raw CNF/model/proof recovery remains separately LOCAL_ONLY.'
        artifact['unavailable_reason']=None
        records.append(dict(id=artifact['id'],path=path,sha256=artifact['sha256'],bytes=len(raw),publication_commit=publication_commit,retrieval=url))
    if len(records)!=14 or data['claims']!=old['claims']:raise ValueError('Exactly14 compact availability updates; no claim changes')
    now=datetime.now(timezone.utc).isoformat();data['updated_at']=now
    validation=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'public',old)
    if not validation['valid']:raise ValueError(repr(validation['errors']))
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    (out/'CLAIMS.before.yaml').write_bytes(before);(out/'CLAIMS.after.yaml').write_bytes(after)
    report=dict(timestamp=now,status='IMMUTABLE_WAVE31_COMPACT_POINTERS_CONFIRMED',source_commit=COMMIT,
        remote_observation=remote,records=records,before_ledger_sha256=BEFORE,after_ledger_sha256=hashlib.sha256(after).hexdigest(),
        changed_claims=0,mathematical_verification=False,
        impact_review='Every artifact hash and all313 claim statements/dependencies/verification records remain unchanged; only authenticated byte availability changes. No mathematics or old checking assumption is changed.',
        full_raw_closure_availability='LOCAL_ONLY; compact report publication does not establish raw formula/proof replay.',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),validation=validation)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    if (ROOT/'CLAIMS.yaml').read_bytes()!=before:raise ValueError('Concurrent ledger mutation')
    pending=out/'CLAIMS.pending.yaml';pending.write_bytes(after);os.replace(pending,ROOT/'CLAIMS.yaml')
    print(json.dumps(dict(status=report['status'],compact_artifacts=len(records),changed_claims=0,full_raw_closure='LOCAL_ONLY')))


if __name__=='__main__':main()

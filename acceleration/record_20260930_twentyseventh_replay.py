"""Publish a small completion receipt for actual frozen-auditor reruns."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'build/research-local/wave27-audit-replay';OUT=ROOT/'acceleration/results/20260930_twentyseventh_replay_validation'
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def main():
    r=json.loads((SRC/'summary.json').read_bytes());m=json.loads((SRC/'manifest.json').read_bytes());assert r['status']=='TWENTYSEVENTH_AUDIT_REPLAY_PASS'and r['completed']==10 and len(r['results'])==len(m['plan'])==10 and all(x['exit_code']==0 for x in r['results'])
    OUT.mkdir(exist_ok=False);records=[]
    paths=[SRC/n for n in['manifest.json','checkpoint.json','summary.json']]
    for item in m['plan']:
        p=SRC/item['name']/'summary.json';assert json.loads(p.read_bytes())['status']==item['expected_status'];paths.append(p)
        paths.extend(SRC/(item['name']+'.'+kind+'.log')for kind in['stdout','stderr'])
    for p in paths:
        q=OUT/p.relative_to(SRC);q.parent.mkdir(exist_ok=True,parents=True);raw=p.read_bytes();assert len(raw)<=10*1024**2
        with q.open('xb')as f:f.write(raw)
        assert sha(p)==sha(q);records.append(dict(source=key(p),path=key(q),sha256=sha(q),bytes=len(raw)))
    receipt=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=sha(Path(__file__)),completed=10,records=records,mathematical_claim_changes=0,checking_method='Repeated execution of frozen independent checkers, not a new independent implementation.',limitations=['Copied summaries retain references to fresh build/research-local artifacts. Those fresh artifacts remain LOCAL_ONLY; these completion receipts are not a replacement public mathematical evidence closure.','Original independent reports and original mathematical artifacts remain the authoritative proof package.'])
    with(OUT/'receipt.json').open('x',encoding='utf8',newline='\n')as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(dict(copied=len(records),receipt_sha256=sha(OUT/'receipt.json'))))
if __name__=='__main__':main()

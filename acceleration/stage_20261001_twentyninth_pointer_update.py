"""Stage only explicitly named publication metadata and authenticate exact index bytes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20261001_'
def h(raw):return hashlib.sha256(raw).hexdigest()
def git(*args,raw=None):return subprocess.check_output(['git',*args],cwd=ROOT,input=raw)
def main():
    paths=['CLAIMS.yaml','acceleration/publish_20261001_twentyninth_evidence_pointers.py',
        'acceleration/publish_20261001_twentyninth_evidence_pointers_v2.py',
        'acceleration/record_20261001_twentyninth_pointer_failure.py',
        'acceleration/audit_20261001_twentyninth_pointer_v2.py',
        'acceleration/audit_20261001_twentyninth_pointer_v2_spec.md',
        B+'twentyninth_publication_pointer_failure/summary.json',
        B+'independent_review/twentyninth_publication_pointer_v2/summary.json',
        B+'resume/twentyninth_pr_body.md',Path(__file__).relative_to(ROOT).as_posix()]
    paths += [B+'twentyninth_publication_pointers_v2/'+n for n in ['CLAIMS.before.yaml','CLAIMS.after.yaml','receipt.json','transaction.json']]
    gate=B+'independent_review/twentyninth_publication_pointer_v2/summary.json'
    assert h((ROOT/gate).read_bytes())=='b9a27d62570e726e9ff2cd946118af3e3c6d66f6233924d6f57ed2ca7376a4d1'
    assert h((ROOT/'CLAIMS.yaml').read_bytes())=='9d9d37c36a695bdfb4833311bdf649b4485ac87e6a185bf66790419afed3b3c2'
    assert not git('diff','--cached','--name-only').strip()
    pattern=re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    rows=[]
    for name in sorted(paths):
        raw=(ROOT/name).read_bytes();assert len(raw)<10*1024**2 and not pattern.search(raw)
        rows.append(dict(path=name,sha256=h(raw),bytes=len(raw)))
    git('add','-f','--pathspec-from-file=-','--pathspec-file-nul',raw=b'\0'.join(p.encode()for p in sorted(paths))+b'\0')
    for row in rows:
        blob=git('show',':'+row['path']);assert h(blob)==row['sha256'] and len(blob)==row['bytes']
    changed=git('diff','--cached','--name-only').decode().splitlines();assert set(changed)==set(paths)
    out=B+'resume/twentyninth_pointer_staging.json'
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=git('rev-parse','HEAD').decode().strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),status='EXACT_POINTER_UPDATE_INDEX_BYTES_PASS',
        checked_index_blobs=rows,source_sha256=h(Path(__file__).read_bytes()),mathematical_verification=False,
        scope='Only the exact14 metadata/source paths plus this receipt; no future batch/registrar work.',
        credential_scan='No stated token/private-key pattern matched; not a universal detector.')
    with(ROOT/out).open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
    git('add','--',out)
    print(json.dumps(dict(status=result['status'],staged_paths=len(paths)+1)))
if __name__=='__main__':main()

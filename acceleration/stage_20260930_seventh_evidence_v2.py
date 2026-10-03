"""Complete the preserved newline-byte veto correction without changing research bytes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
CAT=ROOT/(B+'seventh_artifact_packaging')
def read(p): return json.loads(p.read_bytes())
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    correction=read(ROOT/(B+'seventh_staging_correction/summary.json'))
    assert correction['status']=='PUBLICATION_BYTE_CHECK_VETO'
    assert digest(CAT/'catalog.json')=='150050d18fda0318e370566b253b8cf506c847fdd3c8b8fbb7d3be835f0ba756'
    frozen=read(CAT/'untracked_inventory.json')['entries']+read(CAT/'raw_logs_publication.json')['entries']
    for r in frozen:
        assert digest(ROOT/r['path'])==r['sha256'],r['path']
    paths=set(read(CAT/'stage_inventory.json')['paths'])
    paths.update(['.gitignore','.gitattributes','CLAIMS.yaml','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md',
        'docs/RESEARCH_20260930_SEVENTH_WAVE.md','docs/REPRODUCING_20260930_SEVENTH_WAVE.md',
        'acceleration/stage_20260930_seventh_evidence.py','acceleration/stage_20260930_seventh_evidence_v2.py',
        'acceleration/record_20260930_seventh_index_correction.py',B+'resume/seventh_milestone_checkpoint.json',
        B+'resume/claims_at_seventh_milestone.yaml',B+'resume/seventh_native_process_snapshot.stdout.log',
        B+'resume/seventh_native_process_snapshot.stderr.log',B+'resume/seventh_precommit_validation.json'])
    for directory in [CAT,ROOT/(B+'seventh_staging_correction')]:
        paths.update(p.relative_to(ROOT).as_posix() for p in directory.iterdir() if p.is_file())
    current=set(p for p in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0') if p)
    assert current<=paths,'unexpected existing staged changes'
    for name in paths:
        assert not any(x in name.lower() for x in ['matching_pair_census','proof_core','row_obstruction','p_core','core_permutation'])
        assert name!='PROMPT.md' and not name.startswith('tools/')
        assert (ROOT/name).is_file() and (ROOT/name).stat().st_size<=10*1024**2,name
    ordered=sorted(paths)
    for i in range(0,len(ordered),40):
        subprocess.run(['git','add','-f','--',*ordered[i:i+40]],cwd=ROOT,check=True,capture_output=True)
    staged=set(p for p in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0') if p)
    assert staged==paths,'stage population mismatch'
    raw=subprocess.run(['git','cat-file','--batch'],input=''.join(':'+p+'\n' for p in ordered).encode(),cwd=ROOT,capture_output=True,check=True).stdout
    offset=0; rows=[]
    secret=re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for name in ordered:
        end=raw.index(b'\n',offset);header=raw[offset:end].split();assert header[1]==b'blob'
        size=int(header[2]);blob=raw[end+1:end+1+size];offset=end+size+2
        value=hashlib.sha256(blob).hexdigest();assert value==digest(ROOT/name),name
        assert not secret.search(blob),'credential-shaped material '+name
        rows.append(dict(path=name,sha256=value,bytes=size,git_blob=header[0].decode()))
    assert offset==len(raw)
    doc='docs/AUDIT_20260930_WAVE151_TRIANGLE_FULL99_ENCODING.md'
    assert digest(ROOT/doc)=='9c661b8c92a35cdfe1d1ab2c82626e1fc2c6c555a2ab54780e8f49c6a5d61b62'
    assert b'\r\n' not in (ROOT/'.gitignore').read_bytes()
    check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check','--','.',':(exclude)*.log'],cwd=ROOT,capture_output=True,text=True)
    whitespace=check.stdout.splitlines()
    assert all('new blank line at EOF.' in line for line in whitespace),whitespace
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='SEVENTH_EXACT_INDEX_BYTES_PASS',command=[sys.executable,*sys.argv],cwd=str(ROOT),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        staged_paths=rows,checked_index_blobs=len(rows),frozen_inventory_entries_checked=len(frozen),
        correction='Current .gitignore normalized to LF; one exact frozen audit Markdown path marked -text. All research source/artifact bytes unchanged.',
        original_veto=B+'seventh_staging_correction/summary.json',original_veto_sha256=digest(ROOT/(B+'seventh_staging_correction/summary.json')),
        whitespace_warnings_preserved=whitespace,whitespace_reason='Only already-frozen trailing blank source/doc lines remain; changing them would invalidate bound source hashes. Raw logs are excluded from cosmetic whitespace checking.',
        credential_shape_scan='No matches for stated token/private-key patterns; not universal secret detection.',
        preserved_user_changes=['PROMPT.md','tools/drat-trim'],mathematical_verification=False)
    destination=ROOT/(B+'resume/seventh_staging_check.json')
    with destination.open('x',encoding='utf-8',newline='\n')as f:json.dump(report,f,indent=2);f.write('\n')
    subprocess.run(['git','add','--',destination.relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
    print(json.dumps({'status':report['status'],'index_blobs':len(rows),'receipt_added_separately':True,'preserved_eof_warnings':len(whitespace)}))

if __name__=='__main__':main()

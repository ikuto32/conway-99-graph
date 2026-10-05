"""Stage only the authenticated twentyfirst publication inventory and wrappers."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def git(*args,**kw):return subprocess.run(['git',*args],cwd=ROOT,capture_output=True,check=True,**kw)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--gate',required=True);ap.add_argument('--gate-sha256',required=True);ap.add_argument('--audit-source',required=True)
    ap.add_argument('--extra-file',action='append',default=[]);ap.add_argument('--extra-dir',action='append',default=[]);args=ap.parse_args()
    inv=B+'twentyfirst_artifact_packaging/stage_inventory.json';assert h(inv)=='1adf99d9726bd881d682d88f58262bddeed4d8eae513f15ce1577cbca802b815'
    data=read(inv)
    for row in data['entries']:assert h(row['path'])==row['sha256']and(ROOT/row['path']).stat().st_size==row['bytes'],row['path']
    assert h(args.gate)==args.gate_sha256
    gate=read(args.gate);assert gate['status']=='INDEPENDENT_TWENTYFIRST_CHECKPOINT_REPORT_CONSISTENCY_PASS'
    assert gate['inputs_sha256'][args.audit_source]==h(args.audit_source)
    for p,sha in gate['inputs_sha256'].items():assert h(p)==sha,p
    paths=set(data['paths']+data['wrapper_paths_to_add_separately'])
    paths.update(['CLAIMS.yaml','.gitattributes','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md',
        'docs/RESEARCH_20260930_TWENTYFIRST_WAVE.md','acceleration/stage_20260930_twentyfirst_evidence.py',
        'acceleration/record_20260930_twentyfirst_checkpoint.py',args.audit_source,args.gate,
        B+'resume/twentyfirst_milestone_checkpoint.json',B+'resume/claims_at_twentyfirst_milestone.yaml',
        B+'resume/twentyfirst_process_snapshot.stdout.log',B+'resume/twentyfirst_process_snapshot.stderr.log',B+'resume/twentyfirst_precommit_validation.json'])
    gate_dir=(ROOT/args.gate).parent
    paths.update(p.relative_to(ROOT).as_posix()for p in gate_dir.rglob('*')if p.is_file())
    paths.update(args.extra_file)
    for directory in args.extra_dir:
        folder=(ROOT/directory).resolve();assert folder.is_relative_to(ROOT)and folder.is_dir()
        paths.update(p.relative_to(ROOT).as_posix()for p in folder.rglob('*')if p.is_file())
    assert not any(p=='PROMPT.md'or p.startswith('tools/drat-trim')or 'four_profile_cnfs'in p or 'six_profile_local_domains'in p or 'input_relabeling'in p or 'phase_signed_graph'in p or p.endswith('hadamard_oriented_unknown/process.stdout.log') for p in paths)
    assert set(git('diff','--cached','--name-only',text=True).stdout.splitlines())<=paths
    for p in paths:assert(ROOT/p).is_file()and(ROOT/p).resolve().is_relative_to(ROOT)and(ROOT/p).stat().st_size<10*1024**2,p
    ordered=sorted(paths)
    for start in range(0,len(ordered),40):git('add','-f','--',*ordered[start:start+40])
    changed=[p for p in git('diff','--cached','--name-only','-z').stdout.decode().split('\0')if p];assert set(changed)<=paths
    raw=git('cat-file','--batch',input=''.join(':'+p+'\n'for p in ordered).encode()).stdout;offset=0;checked=[]
    secret=re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for p in ordered:
        end=raw.index(b'\n',offset);head=raw[offset:end].split();assert head[1]==b'blob';size=int(head[2]);blob=raw[end+1:end+1+size];offset=end+size+2
        sha=hashlib.sha256(blob).hexdigest();assert sha==h(p),p;assert not secret.search(blob),'credential-shaped content '+p
        checked.append(dict(path=p,sha256=sha,bytes=size,git_blob=head[0].decode()))
    assert offset==len(raw)
    result=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check','--','.',':(exclude)*.log'],cwd=ROOT,capture_output=True,text=True)
    warnings=result.stdout.splitlines();assert result.returncode in(0,2)and all('new blank line at EOF.'in line for line in warnings),warnings
    out=B+'resume/twentyfirst_staging_check.json'
    receipt=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='TWENTYFIRST_EXACT_INDEX_BYTES_PASS',command=[sys.executable,*sys.argv],cwd=str(ROOT),
        source_commit=git('rev-parse','HEAD',text=True).stdout.strip(),input_inventory=inv,input_inventory_sha256=h(inv),consistency_gate=args.gate,consistency_gate_sha256=h(args.gate),
        checked_index_blobs=checked,changed_paths=changed,cosmetic_eof_warnings_preserved=warnings,
        credential_shape_scan='No stated token/private-key pattern matched; not a universal secret detector.',preserved_user_changes=['PROMPT.md','tools/drat-trim'],
        excluded_future_work=['Wave22 remaining15-formula campaign, six-profile local domains and coordinate-input relabelling diagnostic.'],mathematical_verification=False)
    with(ROOT/out).open('x',encoding='utf8',newline='\n')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    git('add','--',out);print(json.dumps(dict(status=receipt['status'],checked_payload_paths=len(checked),changed_paths=len(changed),receipt_added_separately=True)))
if __name__=='__main__':main()

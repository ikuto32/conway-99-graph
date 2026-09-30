"""Stage the authenticated wave24 inventory and consistency-review supplement only."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gzip,hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
def h(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def git(*args,**kw):return subprocess.run(['git',*args],cwd=ROOT,capture_output=True,check=True,**kw)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inventory-sha256',required=True);ap.add_argument('--gate',required=True);ap.add_argument('--gate-sha256',required=True);ap.add_argument('--audit-source',required=True)
    ap.add_argument('--extra-file',action='append',default=[]);ap.add_argument('--extra-dir',action='append',default=[]);args=ap.parse_args()
    inv=B+'twentyfourth_artifact_packaging/stage_inventory.json';assert h(inv)==args.inventory_sha256
    data=read(inv)
    for row in data['entries']:assert h(row['path'])==row['sha256'] and (ROOT/row['path']).stat().st_size==row['bytes'],row['path']
    assert h(args.gate)==args.gate_sha256
    gate=read(args.gate);assert gate['status']=='INDEPENDENT_TWENTYFOURTH_CHECKPOINT_REPORT_CONSISTENCY_PASS'
    assert gate['inputs_sha256'][args.audit_source]==h(args.audit_source)
    assert gate['inputs_sha256'][inv]==args.inventory_sha256
    for p,sha in gate['inputs_sha256'].items():assert h(p)==sha,p
    paths=set(data['paths']+data['wrapper_paths_to_add_separately'])
    paths.update(['CLAIMS.yaml','.gitattributes','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md',
        'docs/RESEARCH_20260930_TWENTYFOURTH_WAVE.md','acceleration/stage_20260930_twentyfourth_evidence.py',
        'acceleration/record_20260930_twentyfourth_checkpoint.py',args.audit_source,args.gate,
        B+'resume/twentyfourth_milestone_checkpoint.json',B+'resume/claims_at_twentyfourth_milestone.yaml',
        B+'resume/twentyfourth_process_snapshot.stdout.log',B+'resume/twentyfourth_process_snapshot.stderr.log',B+'resume/twentyfourth_precommit_validation.json'])
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/args.gate).parent.rglob('*') if p.is_file())
    paths.update(args.extra_file)
    for directory in args.extra_dir:
        folder=(ROOT/directory).resolve();assert folder.is_relative_to(ROOT) and folder.is_dir()
        paths.update(p.relative_to(ROOT).as_posix() for p in folder.rglob('*') if p.is_file())
    forbidden=('count_master_eight_orbit_cut_native_', 'count_master_eight_orbit_cut_object', 'count_master_eight_orbit_cut_sat_outcome', 'eight_count_profile_lift_second', 'eight_count_profile_second', 'all_triple_count', 'direct_cell_count')
    assert not any(p=='PROMPT.md' or p.startswith('tools/drat-trim') or any(s in p for s in forbidden) or p.endswith('hadamard_oriented_unknown/process.stdout.log') for p in paths)
    assert set(git('diff','--cached','--name-only',text=True).stdout.splitlines())<=paths
    metadata={B+d+'/'+n for d in ('twentyfourth_preparation','twentyfourth_artifact_packaging') for n in ('catalog.json','stage_inventory.json','reference_checks.json.gz')}
    for p in paths:
        limit=32*1024**2 if p in metadata else 10*1024**2
        assert (ROOT/p).is_file() and (ROOT/p).resolve().is_relative_to(ROOT) and (ROOT/p).stat().st_size<=limit,p
        if p in metadata:assert gate['inputs_sha256'][p]==h(p),'independent exact metadata-wrapper identity'
    ordered=sorted(paths)
    git('add','-f','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(p.encode('utf8') for p in ordered)+b'\0')
    changed=[p for p in git('diff','--cached','--name-only','-z').stdout.decode().split('\0') if p];assert set(changed)<=paths
    secret=re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----');checked=[]
    for start in range(0,len(ordered),256):
        batch=ordered[start:start+256];raw=git('cat-file','--batch',input=''.join(':'+p+'\n' for p in batch).encode()).stdout;offset=0
        for p in batch:
            end=raw.index(b'\n',offset);head=raw[offset:end].split();assert head[1]==b'blob';size=int(head[2]);blob=raw[end+1:end+1+size];offset=end+size+2
            sha=hashlib.sha256(blob).hexdigest();assert sha==h(p),p;assert not secret.search(blob),'credential-shaped content '+p
            checked.append(dict(path=p,sha256=sha,bytes=size,git_blob=head[0].decode()))
        assert offset==len(raw)
    result=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check','--','.',':(exclude)*.log'],cwd=ROOT,capture_output=True,text=True)
    warnings=result.stdout.splitlines();assert result.returncode in (0,2) and all('new blank line at EOF.' in line for line in warnings),warnings
    out=B+'resume/twentyfourth_staging_check.json.gz'
    receipt=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='TWENTYFOURTH_EXACT_INDEX_BYTES_PASS',command=[sys.executable,*sys.argv],cwd=str(ROOT),
        source_commit=git('rev-parse','HEAD',text=True).stdout.strip(),input_inventory=inv,input_inventory_sha256=h(inv),consistency_gate=args.gate,consistency_gate_sha256=h(args.gate),
        checked_index_blobs=checked,changed_paths=changed,cosmetic_eof_warnings_preserved=warnings,
        credential_shape_scan='No stated token/private-key pattern matched; not a universal secret detector.',preserved_user_changes=['PROMPT.md','tools/drat-trim'],
        excluded_future_work=['Wave25 later six-cut native count witness, second full-Gram lift and joint-formulation inventories.'],metadata_wrapper_limit_bytes=32*1024**2,metadata_wrapper_exact_paths=sorted(metadata),research_payload_limit_bytes=10*1024**2,mathematical_verification=False)
    encoded=(json.dumps(receipt,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
    with (ROOT/out).open('xb') as stream:
        with gzip.GzipFile(filename='',mode='wb',fileobj=stream,compresslevel=9,mtime=0) as packed:packed.write(encoded)
    assert (ROOT/out).stat().st_size<10*1024**2
    git('add','--',out);print(json.dumps(dict(status=receipt['status'],checked_payload_paths=len(checked),changed_paths=len(changed),receipt_added_separately=True)))
if __name__=='__main__':main()

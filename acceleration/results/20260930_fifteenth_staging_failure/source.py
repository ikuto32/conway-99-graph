"""Stage the exact explicit fifteenth allowlist; check all index bytes before publication."""
from datetime import datetime,timezone
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
    initial_staged=set(subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).splitlines())
    inventory=B+'fifteenth_artifact_packaging/stage_inventory.json'
    assert h(inventory)=='356c78877dfb3119507177420c41d785ba383e3d007449c156d498d4837c6d72'
    data=json.loads((ROOT/inventory).read_bytes())
    for r in data['entries']:assert h(r['path'])==r['sha256']and(ROOT/r['path']).stat().st_size==r['bytes'],r['path']
    paths=set(data['paths']+data['wrapper_paths_to_add_separately'])
    paths.update(['CLAIMS.yaml','.gitignore','.gitattributes','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md',
        'docs/RESEARCH_20260930_FIFTEENTH_WAVE.md','docs/RESEARCH_20260930_FIFTEENTH_WAVE_CORRECTED.md','docs/REPRODUCING_20260930_FIFTEENTH_WAVE.md',B+'fifteenth_report_correction/correction.json',
        'acceleration/record_20260930_fifteenth_checkpoint.py','acceleration/record_20260930_fifteenth_checkpoint_v2.py','acceleration/stage_20260930_fifteenth_evidence.py',B+'fifteenth_checkpoint_failure/source.py',B+'fifteenth_checkpoint_failure/failure.json',
        'acceleration/audit_20260930_fifteenth_checkpoint.py','acceleration/audit_20260930_fifteenth_checkpoint_v2.py',B+'independent_review/fifteenth_checkpoint/failure.json',B+'independent_review/fifteenth_checkpoint_v2/summary.json',
        B+'resume/fifteenth_milestone_checkpoint.json',B+'resume/claims_at_fifteenth_milestone.yaml',
        B+'resume/fifteenth_process_snapshot.stdout.log',B+'resume/fifteenth_process_snapshot.stderr.log',B+'resume/fifteenth_precommit_validation.json'])
    assert all(not any(term in p for term in ('prism_coarse60_bitflip', 'prism_coarse60_arc', 'identity_p_triangle_partition', 'identity_p_mixed_redundancy', 'prism_coarse60_triangle_cover')) for p in paths)
    attributes=ROOT/'.gitattributes';old=attributes.read_bytes();add=[]
    for r in data['entries']:
        if r['path'].startswith('docs/')and r['path'].endswith('.md')and b'\r\n'in(ROOT/r['path']).read_bytes():
            rule='/'+r['path']+' -text'
            if rule not in old.decode().splitlines():add.append(rule)
    if add:attributes.write_bytes(old+b'\n# Preserve exact fifteenth-wave audit/derivation bytes.\n'+('\n'.join(add)+'\n').encode())
    for p in paths:assert(ROOT/p).is_file()and(ROOT/p).resolve().is_relative_to(ROOT)and(ROOT/p).stat().st_size<10*1024**2,p
    assert initial_staged<=paths,'unexpected existing index path'
    ordered=sorted(paths)
    for i in range(0,len(ordered),40):subprocess.run(['git','add','-f','--',*ordered[i:i+40]],cwd=ROOT,check=True,capture_output=True)
    # Some allowlisted dependencies were already published; only changed paths enter this commit.
    changed=[p for p in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0')if p]
    assert set(changed)<=paths
    raw=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=''.join(':'+p+'\n'for p in ordered).encode(),capture_output=True,check=True).stdout
    offset=0;checked=[];secret=re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for p in ordered:
        end=raw.index(b'\n',offset);header=raw[offset:end].split();assert header[1]==b'blob';size=int(header[2]);blob=raw[end+1:end+1+size];offset=end+size+2
        value=hashlib.sha256(blob).hexdigest();assert value==h(p),p
        assert not secret.search(blob),'credential-shaped content '+p
        checked.append(dict(path=p,sha256=value,bytes=size,git_blob=header[0].decode()))
    assert offset==len(raw)
    check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check','--','.',':(exclude)*.log'],cwd=ROOT,capture_output=True,text=True)
    warnings=check.stdout.splitlines();assert all('new blank line at EOF.'in s for s in warnings),warnings
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='FIFTEENTH_EXACT_INDEX_BYTES_PASS',command=[sys.executable,*sys.argv],cwd=str(ROOT),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_inventory=inventory,input_inventory_sha256=h(inventory),checked_index_blobs=checked,changed_paths=changed,
        attributes_before_sha256=hashlib.sha256(old).hexdigest(),attributes_after_sha256=h('.gitattributes'),exact_byte_override_rules_added=add,
        cosmetic_eof_warnings_preserved=warnings,reason='Bound research bytes are preserved; cosmetic EOF edits would invalidate evidence hashes.',
        credential_shape_scan='No stated token/private-key pattern matched; not a universal secret detector.',
        preserved_user_changes=['PROMPT.md','tools/drat-trim'],mathematical_verification=False)
    out=B+'resume/fifteenth_staging_check.json'
    with(ROOT/out).open('x',encoding='utf-8',newline='\n')as f:json.dump(report,f,indent=2);f.write('\n')
    subprocess.run(['git','add','--',out],cwd=ROOT,check=True)
    print(json.dumps({'status':report['status'],'checked_payload_paths':len(checked),'changed_paths':len(changed),'exact_doc_overrides':len(add),'receipt_added_separately':True}))
if __name__=='__main__':main()

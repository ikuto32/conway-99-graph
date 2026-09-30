"""Stage the exact explicit thirteenth allowlist; check all index bytes before publication."""
from datetime import datetime,timezone
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
    assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT).strip(),'index not empty'
    inventory=B+'thirteenth_artifact_packaging/stage_inventory.json'
    assert h(inventory)=='e455c3865a502824557b9a9584ba649362ce5bf1afa755125fe6a3a3cd12539e'
    data=json.loads((ROOT/inventory).read_bytes())
    for r in data['entries']:assert h(r['path'])==r['sha256']and(ROOT/r['path']).stat().st_size==r['bytes'],r['path']
    paths=set(data['paths']+data['wrapper_paths_to_add_separately'])
    paths.update(['CLAIMS.yaml','.gitignore','.gitattributes','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md',
        'docs/RESEARCH_20260930_THIRTEENTH_WAVE.md','docs/REPRODUCING_20260930_THIRTEENTH_WAVE.md',
        'acceleration/record_20260930_thirteenth_checkpoint.py','acceleration/stage_20260930_thirteenth_evidence.py',
        B+'resume/thirteenth_milestone_checkpoint.json',B+'resume/claims_at_thirteenth_milestone.yaml',
        B+'resume/thirteenth_process_snapshot.stdout.log',B+'resume/thirteenth_process_snapshot.stderr.log',B+'resume/thirteenth_precommit_validation.json'])
    assert all(not any(term in p for term in ('factor_permutation', 'factor_annealer', 'variable_core_pair_orbits', 'identity_endpoint', 'residual_spectrum', 'proof_core')) for p in paths)
    attributes=ROOT/'.gitattributes';old=attributes.read_bytes();add=[]
    for r in data['entries']:
        if r['path'].startswith('docs/')and r['path'].endswith('.md')and b'\r\n'in(ROOT/r['path']).read_bytes():
            rule='/'+r['path']+' -text'
            if rule not in old.decode().splitlines():add.append(rule)
    if add:attributes.write_bytes(old+b'\n# Preserve exact thirteenth-wave audit/derivation bytes.\n'+('\n'.join(add)+'\n').encode())
    for p in paths:assert(ROOT/p).is_file()and(ROOT/p).resolve().is_relative_to(ROOT)and(ROOT/p).stat().st_size<10*1024**2,p
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
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='THIRTEENTH_EXACT_INDEX_BYTES_PASS',command=[sys.executable,*sys.argv],cwd=str(ROOT),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_inventory=inventory,input_inventory_sha256=h(inventory),checked_index_blobs=checked,changed_paths=changed,
        attributes_before_sha256=hashlib.sha256(old).hexdigest(),attributes_after_sha256=h('.gitattributes'),exact_byte_override_rules_added=add,
        cosmetic_eof_warnings_preserved=warnings,reason='Bound research bytes are preserved; cosmetic EOF edits would invalidate evidence hashes.',
        credential_shape_scan='No stated token/private-key pattern matched; not a universal secret detector.',
        preserved_user_changes=['PROMPT.md','tools/drat-trim'],mathematical_verification=False)
    out=B+'resume/thirteenth_staging_check.json'
    with(ROOT/out).open('x',encoding='utf-8',newline='\n')as f:json.dump(report,f,indent=2);f.write('\n')
    subprocess.run(['git','add','--',out],cwd=ROOT,check=True)
    print(json.dumps({'status':report['status'],'checked_payload_paths':len(checked),'changed_paths':len(changed),'exact_doc_overrides':len(add),'receipt_added_separately':True}))
if __name__=='__main__':main()

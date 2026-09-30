"""Explicit seventeenth allowlist; authenticate every staged research byte."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def git(*args,**kwargs):return subprocess.run(['git',*args],cwd=ROOT,capture_output=True,check=True,**kwargs)
def main():
    inventory=B+'seventeenth_artifact_packaging/stage_inventory.json';assert h(inventory)=='7eb39450ec0d8dd74ea9ca4167f452db4b74b10dab42c381c73051869a2f7af4'
    data=read(inventory)
    for row in data['entries']:assert h(row['path'])==row['sha256']and(ROOT/row['path']).stat().st_size==row['bytes'],row['path']
    gate=B+'independent_review/seventeenth_checkpoint_final/summary.json';assert h(gate)=='783b99e22cd9bf79d0ade60ac15b07d6a625ed8910661a976b6b6115c416a736'
    assert read(gate)['status']=='INDEPENDENT_SEVENTEENTH_CHECKPOINT_REPORT_CONSISTENCY_PASS'
    clarification=B+'seventeenth_artifact_packaging/recovery_count_clarification.json';assert h(clarification)=='7d3191792a52e78af34b8667e8a86280c8db33aaff4f52b13b1b1588b1a1b331'
    paths=set(data['paths']+data['wrapper_paths_to_add_separately'])
    paths.update(['CLAIMS.yaml','.gitignore','.gitattributes','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md',
        'docs/RESEARCH_20260930_SEVENTEENTH_WAVE.md','acceleration/stage_20260930_seventeenth_evidence.py',
        'acceleration/record_20260930_seventeenth_checkpoint.py','acceleration/audit_20260930_seventeenth_checkpoint.py',
        B+'independent_review/seventeenth_checkpoint_precheck/summary.json',gate,clarification,
        B+'resume/seventeenth_milestone_checkpoint.json',B+'resume/claims_at_seventeenth_milestone.yaml',
        B+'resume/seventeenth_process_snapshot.stdout.log',B+'resume/seventeenth_process_snapshot.stderr.log',B+'resume/seventeenth_precommit_validation.json'])
    assert not any('binary_mip'in p or 'balanced_parity'in p or p=='PROMPT.md'or p.startswith('tools/drat-trim')for p in paths)
    assert set(git('diff','--cached','--name-only',text=True).stdout.splitlines())<=paths
    ignore=ROOT/'.gitignore';oldignore=ignore.read_bytes();proposals=read(B+'seventeenth_artifact_packaging/proposed_raw_ignore_paths.json')['paths'];assert len(proposals)==5
    additions=['/'+p for p in proposals if '/'+p not in oldignore.decode().splitlines()]
    if additions:ignore.write_bytes(oldignore+b'\n# Exact seventeenth raws: lossless packages or incomplete local trace.\n'+('\n'.join(additions)+'\n').encode())
    attrs=ROOT/'.gitattributes';oldattrs=attrs.read_bytes();rules=[]
    for p in paths:
        assert(ROOT/p).is_file()and(ROOT/p).resolve().is_relative_to(ROOT)and(ROOT/p).stat().st_size<10*1024**2,p
        if p.startswith('docs/')and p.endswith('.md')and b'\r\n'in(ROOT/p).read_bytes():
            rule='/'+p+' -text'
            if rule not in oldattrs.decode().splitlines():rules.append(rule)
    if rules:attrs.write_bytes(oldattrs+b'\n# Preserve exact seventeenth frozen document bytes.\n'+('\n'.join(sorted(rules))+'\n').encode())
    ordered=sorted(paths)
    for start in range(0,len(ordered),40):git('add','-f','--',*ordered[start:start+40])
    changed=[p for p in git('diff','--cached','--name-only','-z').stdout.decode().split('\0')if p];assert set(changed)<=paths
    raw=git('cat-file','--batch',input=''.join(':'+p+'\n'for p in ordered).encode()).stdout;offset=0;checked=[]
    secret=re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for p in ordered:
        end=raw.index(b'\n',offset);header=raw[offset:end].split();assert header[1]==b'blob';size=int(header[2]);blob=raw[end+1:end+1+size];offset=end+size+2
        sha=hashlib.sha256(blob).hexdigest();assert sha==h(p),p;assert not secret.search(blob),'credential-shaped content '+p
        checked.append(dict(path=p,sha256=sha,bytes=size,git_blob=header[0].decode()))
    assert offset==len(raw)
    check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check','--','.',':(exclude)*.log'],cwd=ROOT,capture_output=True,text=True)
    warnings=check.stdout.splitlines();assert check.returncode in(0,2)and all('new blank line at EOF.'in line for line in warnings),warnings
    out=B+'resume/seventeenth_staging_check.json'
    record=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='SEVENTEENTH_EXACT_INDEX_BYTES_PASS',command=[sys.executable,*sys.argv],cwd=str(ROOT),
        source_commit=git('rev-parse','HEAD',text=True).stdout.strip(),input_inventory=inventory,input_inventory_sha256=h(inventory),consistency_gate=gate,consistency_gate_sha256=h(gate),
        checked_index_blobs=checked,changed_paths=changed,raw_ignore_rules_added=additions,ignore_before_sha256=hashlib.sha256(oldignore).hexdigest(),ignore_after_sha256=h('.gitignore'),
        attributes_before_sha256=hashlib.sha256(oldattrs).hexdigest(),attributes_after_sha256=h('.gitattributes'),exact_byte_override_rules_added=rules,
        cosmetic_eof_warnings_preserved=warnings,credential_shape_scan='No stated token/private-key pattern matched; not a universal secret detector.',
        preserved_user_changes=['PROMPT.md','tools/drat-trim'],mathematical_verification=False)
    with(ROOT/out).open('x',encoding='utf-8',newline='\n')as stream:json.dump(record,stream,indent=2);stream.write('\n')
    git('add','--',out);print(json.dumps(dict(status=record['status'],checked_payload_paths=len(checked),changed_paths=len(changed),receipt_added_separately=True)))
if __name__=='__main__':main()

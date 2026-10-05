"""Stage a frozen explicit allowlist and verify exact Git bytes; never add all."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
def digest(path): return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path): return json.loads((ROOT/path).read_bytes())
def git(*args, **kwargs): return subprocess.run(['git',*args],cwd=ROOT,check=True,capture_output=True,**kwargs)

def main():
    inventory=B+'sixteenth_artifact_packaging/stage_inventory.json'
    assert digest(inventory)=='a05803bcb0a84e207ee93f82162a7adc15de8259317c6c56d099d284ceb07cd7'
    data=read(inventory)
    for row in data['entries']:
        assert digest(row['path'])==row['sha256'] and (ROOT/row['path']).stat().st_size==row['bytes'],row['path']
    gate=B+'independent_review/sixteenth_checkpoint_final/summary.json'
    assert digest(gate)=='f1927f66dbc324460af586566160ef4b4109f7923f33cbfdb5bd52397c2e37d0'
    assert read(gate)['status']=='INDEPENDENT_SIXTEENTH_CHECKPOINT_REPORT_CONSISTENCY_PASS'
    paths=set(data['paths']+data['wrapper_paths_to_add_separately'])
    paths.update(['CLAIMS.yaml','.gitignore','.gitattributes','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md',
        'docs/RESEARCH_20260930_SIXTEENTH_WAVE.md','acceleration/stage_20260930_sixteenth_evidence.py',
        'acceleration/record_20260930_sixteenth_checkpoint_v2.py','acceleration/record_20260930_sixteenth_checkpoint_v3.py',
        'acceleration/update_20260930_sixteenth_next_action.py','acceleration/audit_20260930_sixteenth_checkpoint_v2.py',
        'acceleration/audit_20260930_sixteenth_checkpoint_v3.py',
        B+'sixteenth_checkpoint_preexecution_update/update.json',B+'sixteenth_checkpoint_preexecution_update_v3/update.json',
        B+'independent_review/sixteenth_checkpoint_precheck_v2/summary.json',gate,
        B+'independent_review/hadamard_cyclic_unsat/summary.json',
        B+'resume/sixteenth_milestone_checkpoint.json',B+'resume/claims_at_sixteenth_milestone.yaml',
        B+'resume/sixteenth_process_snapshot.stdout.log',B+'resume/sixteenth_process_snapshot.stderr.log',
        B+'resume/sixteenth_precommit_validation.json'])
    assert 'PROMPT.md' not in paths and not any(p.startswith('tools/drat-trim') for p in paths)
    initial=set(git('diff','--cached','--name-only',text=True).stdout.splitlines())
    assert initial<=paths,'unrelated index content'
    ignore=ROOT/'.gitignore'; before_ignore=ignore.read_bytes()
    proposals=read(B+'sixteenth_artifact_packaging/proposed_raw_ignore_paths.json')['paths']
    assert len(proposals)==5
    additions=['/'+p for p in proposals if '/'+p not in before_ignore.decode().splitlines()]
    if additions: ignore.write_bytes(before_ignore+b'\n# Exact sixteenth raw artifacts: lossless packages or incomplete local trace.\n'+('\n'.join(additions)+'\n').encode())
    attrs=ROOT/'.gitattributes';before_attrs=attrs.read_bytes();rules=[]
    for p in paths:
        assert (ROOT/p).is_file() and (ROOT/p).resolve().is_relative_to(ROOT) and (ROOT/p).stat().st_size<10*1024**2,p
        if p.startswith('docs/') and p.endswith('.md') and b'\r\n' in (ROOT/p).read_bytes():
            rule='/'+p+' -text'
            if rule not in before_attrs.decode().splitlines():rules.append(rule)
    if rules:attrs.write_bytes(before_attrs+b'\n# Preserve exact sixteenth frozen document bytes.\n'+('\n'.join(sorted(rules))+'\n').encode())
    ordered=sorted(paths)
    for start in range(0,len(ordered),40):git('add','-f','--',*ordered[start:start+40])
    changed=[p for p in git('diff','--cached','--name-only','-z').stdout.decode().split('\0') if p]
    assert set(changed)<=paths
    raw=git('cat-file','--batch',input=''.join(':'+p+'\n' for p in ordered).encode()).stdout
    offset=0;checked=[]
    secret=re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for p in ordered:
        end=raw.index(b'\n',offset);header=raw[offset:end].split();assert header[1]==b'blob'
        size=int(header[2]);blob=raw[end+1:end+1+size];offset=end+size+2
        sha=hashlib.sha256(blob).hexdigest();assert sha==digest(p),p
        assert not secret.search(blob),'credential-shaped content in '+p
        checked.append(dict(path=p,sha256=sha,bytes=size,git_blob=header[0].decode()))
    assert offset==len(raw)
    check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check','--','.',':(exclude)*.log'],cwd=ROOT,capture_output=True,text=True)
    warnings=check.stdout.splitlines()
    assert check.returncode in (0,2) and all('new blank line at EOF.' in line for line in warnings),warnings
    out=B+'resume/sixteenth_staging_check.json'
    record=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='SIXTEENTH_EXACT_INDEX_BYTES_PASS',
        command=[sys.executable,*sys.argv],cwd=str(ROOT),source_commit=git('rev-parse','HEAD',text=True).stdout.strip(),
        input_inventory=inventory,input_inventory_sha256=digest(inventory),consistency_gate=gate,consistency_gate_sha256=digest(gate),
        checked_index_blobs=checked,changed_paths=changed,raw_ignore_rules_added=additions,
        ignore_before_sha256=hashlib.sha256(before_ignore).hexdigest(),ignore_after_sha256=digest('.gitignore'),
        attributes_before_sha256=hashlib.sha256(before_attrs).hexdigest(),attributes_after_sha256=digest('.gitattributes'),
        exact_byte_override_rules_added=rules,cosmetic_eof_warnings_preserved=warnings,
        later_cohort_supporting_receipt='Only a replay receipt supports the pre-execution next-action edit; later cyclic claims and work counts are not in this milestone.',
        credential_shape_scan='No stated token/private-key pattern matched; not a universal secret detector.',
        preserved_user_changes=['PROMPT.md','tools/drat-trim'],mathematical_verification=False)
    with(ROOT/out).open('x',encoding='utf-8',newline='\n')as stream:json.dump(record,stream,indent=2);stream.write('\n')
    git('add','--',out)
    print(json.dumps(dict(status=record['status'],checked_payload_paths=len(checked),changed_paths=len(changed),receipt_added_separately=True)))

if __name__=='__main__':main()

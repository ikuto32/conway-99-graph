"""Stage frozen fifth/sixth evidence, explicitly leaving later research separate."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_resume/sixth_staging_check.json'
def h(raw):return sha256(raw).hexdigest()
def main():
    if OUT.exists():raise ValueError('one-shot staging record already exists')
    inventory=json.loads((ROOT/'acceleration/results/20260930_sixth_artifact_packaging/untracked_inventory.json').read_bytes())
    selected={row['path'] for row in inventory['entries'] if row['bytes']<=10*1024*1024}
    selected.update(['.gitignore','README.md','ACTIVE_RESEARCH.md','CLAIMS.yaml','acceleration/validate_claims.py','acceleration/test_validate_claims.py','docs/claims.schema.json','docs/claims.schema.v1.json','docs/CLAIMS_SCHEMA.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md'])
    excluded=('star_matching_redundancy','two_star','joint_star','triangle_factor','triangle_modular','triangle_row')
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
    for name in untracked:
        p=Path(name)
        if any(token in name for token in excluded):continue
        if p.parent==Path('acceleration') and '20260930' in p.name:selected.add(name)
        if p.parent==Path('docs') and ('20260930' in p.name or p.name=='claims.schema.v1.json'):selected.add(name)
    extra_dirs=['20260930_editorial_migration_applied','20260930_sixth_registration','20260930_sixth_artifact_packaging','20260930_strengthened_four_branch_native_pilot']
    roots={ROOT/'acceleration/results'/name for name in extra_dirs}
    # Include exact logs even though the broad default ignores newly created logs.
    for name in selected.copy():
        parts=Path(name).parts
        if len(parts)>3 and parts[:2]==('acceleration','results'):
            roots.add(ROOT/Path(*parts[:4]) if parts[2]=='20260930_independent_review' else ROOT/Path(*parts[:3]))
    roots.add(ROOT/'acceleration/results/20260930_independent_review/editorial_migration_applied')
    for folder in roots:
        if not folder.is_dir():continue
        for p in folder.rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts:continue
            name=p.relative_to(ROOT).as_posix()
            if any(token in name for token in excluded):continue
            if p.stat().st_size<=10*1024*1024:selected.add(name)
    for p in (ROOT/'acceleration/results/20260930_resume').glob('*'):
        if p.is_file() and any(word in p.name for word in ('fifth','sixth')):selected.add(p.relative_to(ROOT).as_posix())
    selected=sorted(selected)
    assert 'PROMPT.md' not in selected and not any(x.startswith('tools/') for x in selected)
    for name in selected:assert (ROOT/name).stat().st_size<=10*1024*1024,name
    for i in range(0,len(selected),70):subprocess.run(['git','add','-f','--',*selected[i:i+70]],check=True)
    index={}
    for row in subprocess.check_output(['git','ls-files','--stage','-z'],text=True).split('\0'):
        if row:
            metadata,path=row.split('\t',1);index[path]=metadata.split()[1]
    cache={}
    def blob_digest(name):
        oid=index[name]
        if oid not in cache:cache[oid]=h(subprocess.check_output(['git','cat-file','blob',oid]))
        return cache[oid]
    stage_hashes={name:blob_digest(name) for name in selected}
    for name,value in stage_hashes.items():
        raw=(ROOT/name).read_bytes()
        if name in ('.gitignore','README.md') or name.startswith('docs/') and name.endswith('.md'):raw=raw.replace(b'\r\n',b'\n')
        assert h(raw)==value,('staged byte transformation',name)
    # Historical reports bind old versions by their original path. Their exact
    # snapshots must also be staged; never pretend the current source is old.
    historical={}
    for name,value in stage_hashes.items():historical.setdefault(value,[]).append(name)
    checked=0;recoveries=[];local=[]
    for name in selected:
        if not name.endswith('.json'):continue
        try:report=json.loads((ROOT/name).read_bytes())
        except (ValueError,UnicodeDecodeError):continue
        if not isinstance(report,dict):continue
        for path,expected in report.get('inputs_sha256',{}).items():
            path=path.replace('\\','/')
            if path not in index:
                local.append(dict(report=name,path=path,sha256=expected));continue
            observed=blob_digest(path)
            if observed!=expected:
                candidates=historical.get(expected,[])
                assert candidates,('unrecovered historical input',name,path,expected,observed)
                recoveries.append(dict(report=name,original_path=path,sha256=expected,exact_staged_snapshot=candidates[0]))
            checked+=1
    record=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),staged_paths=selected,staged_sha256=stage_hashes,hash_bound_index_checks=checked,historical_input_recovery=recoveries,unstaged_input_bindings=local,limitations=['Index-byte and preservation check only; mathematical replay not performed.','Unstaged bindings include large raw inputs recoverable by recipes, local binaries, and local original build paths; their availability is separately catalogued.','Later single-star/triangle/joint-star research excluded.'],unrelated_user_paths_staged=False)
    OUT.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    subprocess.run(['git','add','--',str(OUT.relative_to(ROOT))],check=True)
    print(json.dumps(dict(staged_paths=len(selected)+1,index_bindings_checked=checked,historical_snapshot_bindings=len(recoveries),unstaged_bindings=len(local))))
if __name__=='__main__':main()

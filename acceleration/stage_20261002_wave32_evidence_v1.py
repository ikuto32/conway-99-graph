"""Stage exact completed evidence plus a separately frozen lossless payload list.

Explicit research namespaces only; large partial traces remain local. This is
bookkeeping, not mathematical checking or a public-availability promotion.
"""
import argparse,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
import yaml
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
PUBLICATION='acceleration/results/20261002_batch05_publication01'
MANIFEST_SHA='4c68f6108a0327688c25d870a70497370b8924f787c335db87d38d09b7b28b19'
PATHS_SHA='474f846b01eea2cc95aeaccd50b09bdc2da793dce765bc2751a855a861337251'
BASE='acceleration/results/20261002_wave31_registration02/CLAIMS.after.yaml'


def need(ok,why):
    if not ok:raise ValueError(why)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    deadline=CommandDeadline(args.seconds,allocation_reason='Authenticate finite completed evidence and frozen936-part direct payload before exact staging')
    def digest(p):
        h=hashlib.sha256()
        with p.open('rb') as stream:
            for block in iter(lambda:stream.read(8*1024**2),b''):
                need(not deadline.status()['stop_required'],'staging deadline; retained manifest and index')
                h.update(block)
        return h.hexdigest()
    publication=ROOT/PUBLICATION
    need(digest(publication/'manifest.json')==MANIFEST_SHA and digest(publication/'stage_paths.nul')==PATHS_SHA,
         'exact separately frozen package staging identities')
    manifest=json.loads((publication/'manifest.json').read_bytes())
    rawpaths=(publication/'stage_paths.nul').read_bytes().split(b'\0')
    need(rawpaths[-1]==b'','complete NUL path list')
    paths=[x.decode('utf8') for x in rawpaths[:-1]]
    need(len(paths)==len(set(paths))==2306,'exact frozen payload staging population')
    expected={r['path']:r for r in manifest['records']}
    for name in paths:
        p=(ROOT/name).resolve()
        need(p.is_relative_to(ROOT/'acceleration') and p.is_file(),'explicit research payload path')
        if name in expected:
            row=expected[name];need(digest(p)==row['sha256'] and p.stat().st_size==row['bytes'],'frozen payload identity '+name)
    ledger=yaml.safe_load((ROOT/'CLAIMS.yaml').read_bytes())
    old=yaml.safe_load((ROOT/BASE).read_bytes());oldids={a['id'] for a in old['artifacts']}
    candidates={ROOT/name for name in ['CLAIMS.yaml','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md',
        'docs/REPRODUCING.md','docs/RESEARCH_20261002_THIRTYSECOND_WAVE.md',
        'docs/DERIVATION_20261002_ROOTED5_MOMENT_RIGIDITY.md','docs/AUDIT_20261002_DRAT_RESTART_CONTROLS.md']}
    candidates.update(ROOT/a['path'] for a in ledger['artifacts'] if a['id'] not in oldids and a['path'])
    prefixes=('audit_20261002_rooted5','audit_20261002_rooted6','audit_20261002_rooted7_catalogue',
        'audit_20261002_wave32','audit_20261002_drat_restart','assemble_20261002_drat_continuation',
        'prepare_20261002_drat_restart','drat_restart_20261002','freeze_20261002_drat_restart',
        'review_20261002_drat_restart','record_20261002_derivative_review','record_20261002_rooted5',
        'record_20261002_rooted6','record_20261002_rooted7_catalogue','register_20261002_bound_claims',
        'register_20261002_rooted5','record_20261002_wave32','publish_20261002_wave31_compact',
        'theory_20261002_rooted5','theory_20261002_rooted6','stage_20261002_wave32')
    candidates.update(p for p in (ROOT/'acceleration').iterdir() if p.is_file() and p.name.startswith(prefixes))
    result_prefixes=('20261002_drat_','20261002_rooted5','20261002_rooted6',
        '20261002_wave31_compact_pointer','20261002_wave32_registration','20261002_wave32_milestone',
        '20261002_wave32_registry','20261002_batch05_publication_supervision')
    audit_prefixes=('rooted5','rooted6','rooted7_catalogue','restart_streaming','drat_derivative','wave32_transition')
    folders=[p for p in (ROOT/'acceleration/results').iterdir() if p.is_dir() and p.name.startswith(result_prefixes)]
    folders += [p for p in (ROOT/'acceleration/results/20261002_independent_review').iterdir() if p.is_dir() and p.name.startswith(audit_prefixes)]
    for folder in folders:
        candidates.update(p for p in folder.rglob('*') if p.is_file() and p.suffix in {'.json','.jsonl','.yaml','.md','.log','.txt'})
    records=[];omitted=[]
    for p in sorted(candidates):
        p=p.resolve();need(p.is_relative_to(ROOT),'bounded compact evidence path')
        name=p.relative_to(ROOT).as_posix()
        if not p.is_file():omitted.append(dict(path=name,reason='Unavailable; no invented artifact'));continue
        if p.stat().st_size>8*1024**2:
            omitted.append(dict(path=name,bytes=p.stat().st_size,reason='Large literal scientific state/partial trace retained LOCAL_ONLY'))
            continue
        records.append(dict(path=name,sha256=digest(p),bytes=p.stat().st_size))
    allpaths=sorted(set(paths)|{r['path'] for r in records})
    for start in range(0,len(allpaths),100):
        need(not deadline.status()['stop_required'],'bounded staging invocation')
        subprocess.run(['git','add','--',*allpaths[start:start+100]],cwd=ROOT,check=True,capture_output=True)
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=__import__('sys').argv,cwd=str(ROOT),source_sha256=digest(Path(__file__)),
        exact_payload_manifest=PUBLICATION+'/manifest.json',exact_payload_manifest_sha256=MANIFEST_SHA,
        exact_payload_path_list_sha256=PATHS_SHA,compact_records=records,omitted=omitted,
        exact_staged_paths=allpaths,distinct_staged_paths=len(allpaths),
        public_availability_changed=False,mathematical_replay=False)
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    subprocess.run(['git','add','--',(out/'manifest.json').relative_to(ROOT).as_posix()],cwd=ROOT,check=True,capture_output=True)
    print(json.dumps(dict(status='EXACT_EVIDENCE_STAGED',distinct_paths=len(allpaths),large_omissions=len(omitted),availability_changed=False)))


if __name__=='__main__':main()

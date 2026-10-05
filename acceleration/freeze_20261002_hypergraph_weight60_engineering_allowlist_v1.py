"""Freeze exact weight60 engineering closure; no git index mutation or approval."""
import argparse,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
SOURCES=['acceleration/design_20261002_hypergraph_weight60_v2.md',
    'acceleration/plan_20261002_hypergraph_weight60_correction_v2.json',
    'acceleration/freeze_20261002_hypergraph_weight60_engineering_allowlist_v1.py']
for version in ['1','2']:
    SOURCES += ['acceleration/hypergraph_weight60_anneal_20261002_v'+version+'.cpp',
        'acceleration/prepare_20261002_hypergraph_weight60_v'+version+'.py',
        'acceleration/prepare_20261002_hypergraph_weight60_v'+version+'_spec.md',
        'acceleration/plan_20261002_hypergraph_weight60_engineering_v'+version+'.json']
SOURCES += ['acceleration/diagnose_20261002_weight60_fixture_v'+v+'.py' for v in ['1','2','3']]
DIRS=['acceleration/results/20261002_hypergraph_weight60_'+suffix+attempt
    for suffix in ['build','build_supervision','controls','controls_supervision'] for attempt in ['01','02']]
DIRS += ['acceleration/results/20261002_weight60_fixture_diagnosis'+suffix+attempt
    for suffix in ['','_supervision'] for attempt in ['01','02','03']]

def need(ok,message):
    if not ok:raise ValueError(message)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--seconds',type=float,required=True);a=p.parse_args()
    d=CommandDeadline(a.seconds,allocation_reason='Frozen source/tinycontrols/completepreservedfailure identity andallowlist metadata; no mathematical worker or indexmutation')
    out=a.out.resolve();need(out.is_relative_to(ROOT),'repository output');out.mkdir(parents=True,exist_ok=False)
    selected=set(SOURCES)
    for folder in DIRS:
        base=ROOT/folder;need(base.is_dir(),'every frozen engineering population exists')
        selected.update(x.relative_to(ROOT).as_posix() for x in base.rglob('*') if x.is_file())
    records=[]
    for name in sorted(selected):
        need(not d.status()['stop_required'] and d.status()['remaining_seconds']>10,'not completed within allocated budget')
        path=(ROOT/name).resolve();need(path.is_relative_to(ROOT) and path.is_file(),'exact raw source or receipt exists')
        need(path.stat().st_size<90*1024**2,'per-file publicGit preflight')
        records.append(dict(path=name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    metadata=[(out/'manifest.json').relative_to(ROOT).as_posix(),(out/'stage_paths.nul').relative_to(ROOT).as_posix()]
    names=sorted(selected|set(metadata));(out/'stage_paths.nul').write_bytes(b'\0'.join(x.encode('utf8') for x in names)+b'\0')
    m=dict(schema='WEIGHT60_ENGINEERING_EXACT_STAGING_ALLOWLIST_V1',timestamp=datetime.now(timezone.utc).isoformat(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),source_commit_reference=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        frozen_population=dict(sources=SOURCES,complete_engineering_roots=DIRS,preserved_failed_control_root='acceleration/results/20261002_hypergraph_weight60_controls01'),
        records=records,hashed_records=len(records),stage_paths_count=len(names),stage_paths_sha256=hashlib.sha256((out/'stage_paths.nul').read_bytes()).hexdigest(),
        self_metadata_paths=metadata,raw_bytes=sum(x['bytes'] for x in records),index_mutated=False,scientific_launched=False,independent_approval=False,target_resolution=False,
        limitations=['Exact staging candidates only, not publicavailability or mathematicalverification.',
          'Different-author independent controls/savedcheckers/gates not inthisallowlist; parent adds their exactclosure separately.',
          'ScientificGF3rawcheckpoint andoldweight6pilot omitted; they have distinct publication/recovery lanes.',
          'All failedsourceversions/control attempts andfixturediagnosis corrections remain explicit.'])
    with(out/'manifest.json').open('x',encoding='utf8') as f:json.dump(m,f,indent=2);f.write('\n')
    print(json.dumps(dict(manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),manifest_sha256=hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),
        stage_paths_sha256=m['stage_paths_sha256'],stage_paths_count=len(names),hashed_records=len(records),raw_bytes=m['raw_bytes'],git_index_changed=False)))

if __name__=='__main__':main()

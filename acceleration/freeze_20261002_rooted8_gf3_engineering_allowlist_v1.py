"""Freeze exact GF3 engineering source/receipt allowlist; never edit git index."""
import argparse,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
SOURCES=[
    'acceleration/design_20261002_rooted8_gf3_v1.md','acceleration/design_20261002_rooted8_gf3_v2.md',
    'acceleration/plan_20261002_rooted8_gf3_v1.json','acceleration/plan_20261002_rooted8_gf3_correction_v2.json',
    'acceleration/rooted8_gf3_20261002_v1.cpp','acceleration/prepare_20261002_rooted8_gf3_v1.py',
    'acceleration/prepare_20261002_rooted8_gf3_v1_spec.md','acceleration/prepare_20261002_rooted8_gf3_v2.py',
    'acceleration/prepare_20261002_rooted8_gf3_v2_spec.md','acceleration/freeze_20261002_rooted8_gf3_launch_v1.py',
    'acceleration/freeze_20261002_rooted8_gf3_launch_v1_spec.md',
    'acceleration/freeze_20261002_rooted8_gf3_engineering_allowlist_v1.py']
DIRS=['acceleration/results/20261002_rooted8_gf3_'+suffix+attempt for suffix in ['build','build_supervision','controls','controls_supervision']for attempt in ['01','02']]


def need(ok,message):
    if not ok:raise ValueError(message)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True);args=ap.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='Exact source/tiny-control receipts and preservedfailure identity/stagingallowlist metadata only; no solver or git mutation')
    out=args.out.resolve();need(out.is_relative_to(ROOT),'repository output');out.mkdir(parents=True,exist_ok=False)
    selected=set(SOURCES)
    for folder in DIRS:
        root=ROOT/folder;need(root.is_dir(),'all frozen engineering populations present')
        selected.update(p.relative_to(ROOT).as_posix()for p in root.rglob('*')if p.is_file())
    records=[]
    for name in sorted(selected):
        need(not deadline.status()['stop_required']and deadline.status()['remaining_seconds']>10,'not completed within allocated budget')
        path=(ROOT/name).resolve();need(path.is_relative_to(ROOT)and path.is_file(),'named raw source/receipt exists')
        need(path.stat().st_size<90*1024**2,'per-file publicGit rawsize preflight')
        records.append(dict(path=name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    metadata=[(out/'manifest.json').relative_to(ROOT).as_posix(),(out/'stage_paths.nul').relative_to(ROOT).as_posix()]
    names=sorted(selected|set(metadata));(out/'stage_paths.nul').write_bytes(b'\0'.join(name.encode('utf8')for name in names)+b'\0')
    manifest=dict(schema='GF3_ENGINEERING_EXACT_STAGING_ALLOWLIST_V1',timestamp=datetime.now(timezone.utc).isoformat(),source_commit_reference=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),records=records,hashed_records=len(records),stage_paths_count=len(names),
        stage_paths_sha256=hashlib.sha256((out/'stage_paths.nul').read_bytes()).hexdigest(),self_metadata_paths=metadata,
        frozen_population=dict(sources=SOURCES,direct_complete_engineering_roots=DIRS,preserved_failed_control_root='acceleration/results/20261002_rooted8_gf3_controls01'),
        raw_bytes=sum(record['bytes']for record in records),index_mutated=False,scientific_launched=False,independent_approval=False,target_resolution=False,
        limitations=['Staging candidates only, not publicavailability or mathematical verification.','Independent finite/endpoint gates notincluded here because owned byseparate author; rootmustaddexactsource/gate/checkerclosure separately.','Preservedv1failure and draftcount correction remainexplicit; no failedoutcome erased.'])
    with(out/'manifest.json').open('x',encoding='utf8')as f:json.dump(manifest,f,indent=2);f.write('\n')
    print(json.dumps(dict(manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),manifest_sha256=hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),stage_paths_sha256=manifest['stage_paths_sha256'],stage_paths_count=len(names),hashed_records=len(records),raw_bytes=manifest['raw_bytes'],git_index_changed=False)))


if __name__=='__main__':main()

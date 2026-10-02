"""Freeze exact small engineering publication allowlist without touching index."""
import argparse,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
SOURCES=['acceleration/rooted8_gf2_primal_20261002_v1.cpp',
    'acceleration/rooted8_normalized_gf2_20261002_v1.cpp','acceleration/rooted8_normalized_gf2_20261002_v2.cpp',
    'acceleration/prepare_20261002_rooted8_normalized_gf2_v1.py','acceleration/prepare_20261002_rooted8_normalized_gf2_v1_spec.md',
    'acceleration/prepare_20261002_rooted8_normalized_gf2_v2.py','acceleration/prepare_20261002_rooted8_normalized_gf2_v2_spec.md',
    'acceleration/plan_20261002_rooted8_normalized_gf2_v1.json','acceleration/plan_20261002_rooted8_normalized_gf2_v2.json']
DIRS=['acceleration/results/20261002_rooted8_normalized_gf2_build01','acceleration/results/20261002_rooted8_normalized_gf2_build02',
    'acceleration/results/20261002_rooted8_normalized_gf2_build_supervision01','acceleration/results/20261002_rooted8_normalized_gf2_build_supervision02',
    'acceleration/results/20261002_rooted8_normalized_gf2_controls01','acceleration/results/20261002_rooted8_normalized_gf2_controls_supervision01']


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True);a=ap.parse_args()
    deadline=CommandDeadline(a.seconds,allocation_reason='Small immutable engineering source/build/8tinycontrol allowlist hashing;10s reserve, no scientific work')
    out=a.out.resolve();assert out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    files={ROOT/name for name in SOURCES}|{Path(__file__).resolve()}
    for name in DIRS:files.update(p for p in (ROOT/name).rglob('*')if p.is_file())
    entries=[]
    for path in sorted(files):
        assert path.resolve().is_relative_to(ROOT)and deadline.status()['remaining_seconds']>10 and not deadline.status()['stop_required']
        entries.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size))
    metadata=[(out/name).relative_to(ROOT).as_posix()for name in ['manifest.json','stage_paths.nul']]
    paths=[r['path']for r in entries]+metadata
    (out/'stage_paths.nul').write_bytes(('\0'.join(paths)+'\0').encode())
    report=dict(schema='NORMALIZED_GF2_ENGINEERING_ALLOWLIST_V1',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),entries=entries,hashed_files=len(entries),self_metadata_paths=metadata,stage_paths_nul_sha256=hashlib.sha256((out/'stage_paths.nul').read_bytes()).hexdigest(),
        controls_gate=None,controls_gate_null_reason='Distinct-author structural gate pending; add its exact source/spec/report paths separately before scientific commit.',
        scope='Only prepared raw source, failed normalizedv1 source/compile evidence and successful normalizedv2 source/build/8tiny controls. No fullmodel calculation, ledger/index mutation or public availability assertion.',
        artifact_availability='LOCAL_ONLY',index_modified=False,independent_approval=False,target_resolution=False)
    with(out/'manifest.json').open('x',encoding='utf8',newline='\n')as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),sha256=hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),hashed_files=len(entries),stage_paths=len(paths))))


if __name__=='__main__':main()

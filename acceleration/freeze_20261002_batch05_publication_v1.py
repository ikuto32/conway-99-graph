"""Freeze exact batch05 publication paths; never stage, commit or publish."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, hashlib, json, subprocess, sys
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='acceleration/results/20261002_batch05_raw_package02/manifest.json'
MANIFEST_SHA='95307e8999e9f15880ca2d1f43370e215bc533b4eaa9e00ceca6c6b6b1be6329'
AUDIT='acceleration/results/20261002_independent_review/batch05_recovery01/summary.json'
AUDIT_SHA='5e6f232f1f22e18988d7ff6c2042ba00109290e0912bdea6643d3e80651ce48f'
ROOTS=[f'acceleration/results/20261002_batch05_raw_{s}' for s in
       ['inventory01','inventory02','inventory_supervision01','inventory_supervision02','inventory_supervision03',
        'controls01','controls02','controls_supervision01','controls_supervision02',
        'package01','package02','package_supervision01','package_supervision02']]
ROOTS += ['acceleration/results/20261002_independent_review/'+s for s in
          ['batch05_recovery01','batch05_recovery_controls01','batch05_recovery_supervision01','batch05_recovery_controls_supervision01']]
SOURCES=['acceleration/package_20261002_batch05_raw_v1.py','acceleration/package_20261002_batch05_raw_v1_spec.md',
         'acceleration/package_20261002_batch05_raw_v2.py','acceleration/package_20261002_batch05_raw_v2_spec.md',
         'acceleration/audit_20261002_batch05_raw_recovery_v1.py','acceleration/audit_20261002_batch05_raw_recovery_v1_spec.md',
         'acceleration/recover_20261001_twentyninth_raw_artifacts.py','acceleration/run_compute_command.py',
         'acceleration/command_deadline.py','acceleration/run_20260930_exact_eight_four_builds_v2.py',
         'acceleration/build_20260930_exact_eight_parallel_batch.py','pyproject.toml','uv.lock',
         'acceleration/native_budget_env_v1/pyproject.toml','acceleration/native_budget_env_v1/uv.lock',
         'acceleration/freeze_20261002_batch05_publication_v1.py']


def need(ok,message):
    if not ok: raise ValueError(message)


def safe(name):
    p=(ROOT/name).resolve()
    need(p.is_relative_to(ROOT) and p.relative_to(ROOT).as_posix()==name,'canonical repository path')
    need(not name.startswith(('tools/','external_conway99_research/')) and name!='PROMPT.md','protected path')
    return p


def sha(path,deadline):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024**2),b''):
            need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'not completed within allocated budget')
            h.update(b)
    return h.hexdigest()


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as f: json.dump(value,f,indent=2);f.write('\n')


GUIDE=r'''# Batch05 exact raw recovery

The published payload population is 936 exact gzip parts representing 934 raw
artifacts (1,127,340,761 bytes), including all64 proof/CNF/model/scope inputs.
Manifest SHA256: `95307e8999e9f15880ca2d1f43370e215bc533b4eaa9e00ceca6c6b6b1be6329`.
Independent byte-recovery report:
`acceleration/results/20261002_independent_review/batch05_recovery01/summary.json`,
SHA256 `5e6f232f1f22e18988d7ff6c2042ba00109290e0912bdea6643d3e80651ce48f`.
This is engineering recovery, not a new mathematical replay or unrestricted
exclusion. Native platform binaries remain separately LOCAL_ONLY; historical
gate transitive evidence is not recursively repackaged.

The manifest references parts in package02, preserved package01, and the64
original model.json.gz files. Keep those literal paths after checkout. The
separately authored historical recovery implementation accepts this manifest
format. It verifies every compressed/raw part and whole original hash and size,
enforces offsets/decompression bounds, and never overwrites a mismatching file.

From the repository root on Windows, with uv available:

```powershell
$env:UV_PROJECT_ENVIRONMENT='build/research-venv'
uv sync --locked
$taskPython=(Resolve-Path build/research-venv/Scripts/python.exe).Path
uv run --locked python acceleration/run_compute_command.py --seconds 600 --allocation-reason 'Recover the frozen1.13GB batch05 population; local complete byte audit took4s,600s allows fresh output IO and reserve' --success-criterion 'All934 exact raw identities restored into fresh destination' --verification-criterion 'Each compressed/raw part and original hash/size checked by separate historical recovery implementation; mathematical proof replay remains separate' --shutdown-reserve-seconds 10 --out build/batch05-recovery-supervision-v1 -- $taskPython acceleration/recover_20261001_twentyninth_raw_artifacts.py --manifest acceleration/results/20261002_batch05_raw_package02/manifest.json --manifest-sha256 95307e8999e9f15880ca2d1f43370e215bc533b4eaa9e00ceca6c6b6b1be6329 --destination-dir build/batch05-recovered-v1 --receipt build/batch05-recovered-v1.receipt.json
```

Use fresh supervisor/destination/receipt paths for each separate invocation.
`--verify-only` streams without restoration. To restore missing originals into
the checkout for later proof/encoding replay, use `--destination-dir .`; existing
files must already match exact recorded identities. The complete independent
local recovery auditor also compares every recovered byte against authenticated
originals and tests11 corrupt controls, using a different decompressor/scorer
path. Its local run requires the separately disclosed tool identities.

Preserved failure records describe the initial missing-Python launcher and the
Windows progress-file replacement race. The v2 package explicitly authenticated
and reused344 completed v1 receipts, preserving all old bytes. No scientific
solver was launched by packaging. Every payload is below10MiB (largest1,556,867
bytes). Publication readiness is independent of actual Git/public availability;
the prepared staging list never stages or commits automatically.
'''


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',required=True);ap.add_argument('--seconds',type=float,required=True)
    ap.add_argument('--source-commit',required=True);ap.add_argument('--allocation-reason',required=True)
    args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason=args.allocation_reason)
    out=safe(args.out);out.mkdir(parents=True,exist_ok=False)
    need(sha(safe(MANIFEST),deadline)==MANIFEST_SHA and sha(safe(AUDIT),deadline)==AUDIT_SHA,'exact package and independent recovery audit')
    manifest=json.loads(safe(MANIFEST).read_bytes());audit=json.loads(safe(AUDIT).read_bytes())
    need(audit['status']=='INDEPENDENT_BATCH05_COMPLETE_RAW_RECOVERY_V1_PASS','independent full byte recovery pass')
    parts=[p for r in manifest['records']for p in r['parts']]
    need(len(parts)==936==len({p['path']for p in parts}),'exact936distinct payload population')
    wanted={p['path']:'gzip_payload' for p in parts}
    for p in parts: need(sha(safe(p['path']),deadline)==p['gzip_sha256'] and safe(p['path']).stat().st_size==p['gzip_bytes']<=10*1024**2,'exact payload')
    for root in ROOTS:
        need(safe(root).is_dir(),'explicit immutable metadata root exists')
        for p in safe(root).rglob('*'):
            if p.is_file(): wanted.setdefault(p.relative_to(ROOT).as_posix(),'receipt_control_checkpoint_or_manifest')
    for name in SOURCES: need(safe(name).is_file(),'explicit source');wanted.setdefault(name,'source_or_locked_environment')
    guide=out/'REPLAY.md';guide.write_text(GUIDE,encoding='utf8',newline='\n');wanted[guide.relative_to(ROOT).as_posix()]='replay_guide'
    tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
    rows=[dict(path=name,sha256=sha(safe(name),deadline),bytes=safe(name).stat().st_size,kind=kind,already_tracked=name in tracked)
          for name,kind in sorted(wanted.items())]
    self_paths=[args.out+'/'+name for name in ['manifest.json','summary.json','stage_paths.nul']]
    stages=sorted([r['path']for r in rows]+self_paths)
    (out/'stage_paths.nul').write_bytes(b'\0'.join(p.encode('utf8')for p in stages)+b'\0')
    receipt=dict(schema='BATCH05_PUBLICATION_EXACT_STAGING_PATHS_V1',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=args.source_commit,command=[sys.executable,*sys.argv],cwd=str(ROOT),records=rows,
        payload_parts=936,payload_bytes=sum(p['gzip_bytes']for p in parts),raw_members=manifest['raw_artifacts'],
        raw_bytes=manifest['raw_bytes'],package_manifest=MANIFEST,package_manifest_sha256=MANIFEST_SHA,
        independent_recovery=AUDIT,independent_recovery_sha256=AUDIT_SHA,
        metadata_roots=ROOTS,stage_paths=stages,stage_paths_nul=args.out+'/stage_paths.nul',
        stage_paths_nul_sha256=sha(out/'stage_paths.nul',deadline),
        self_metadata=[dict(path=p,sha256=None,sha256_null_reason='Self/output identity recorded externally to avoid recursive self-hashing.')for p in self_paths],
        kind_counts=dict(Counter(r['kind']for r in rows)),stage_or_commit_performed=False,
        availability='LOCAL_ONLY',publication_pending=True,mathematical_verification=False)
    save(out/'manifest.json',receipt)
    summary=dict(status='EXACT_BATCH05_STAGING_LIST_READY_NOT_STAGED',timestamp=datetime.now(timezone.utc).isoformat(),
        manifest=args.out+'/manifest.json',manifest_sha256=sha(out/'manifest.json',deadline),
        stage_paths_nul=args.out+'/stage_paths.nul',stage_paths_nul_sha256=sha(out/'stage_paths.nul',deadline),
        hashed_existing_files=len(rows),exact_stage_paths=len(stages),payload_parts=936,
        elapsed_seconds=deadline.status()['elapsed_seconds'],git_index_modified_by_this_command=False)
    save(out/'summary.json',summary);print(json.dumps(summary),flush=True)


if __name__=='__main__':main()

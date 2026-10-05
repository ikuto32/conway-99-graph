"""Explicit post-batch trace archival; identity checks are not proof replay."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
import native_20260930_unrestricted_full99 as helper
import native_20260930_proof_location as ext4
ROOT=helper.ROOT
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--batch',type=Path,required=True);ap.add_argument('--summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    batch=args.batch.resolve();out=args.out.resolve();helper.require(batch.is_relative_to(ROOT)and out.is_relative_to(ROOT),'workspace-contained paths')
    source=batch/'summary.json';helper.require(helper.digest(source)==args.summary_sha256,'exact completed batch summary')
    summary=helper.read(source);helper.require(summary['schema']=='HADAMARD_PARITY_PHASE_BATCH_RESULT_V1','known batch schema')
    workspace=helper.read(batch/'workspace.json')['path'];helper.require(re.fullmatch(r'/tmp/conway99-parity-phase-batch-[A-Za-z0-9]+',workspace)is not None,'known exact ext4 workspace')
    helper.require(helper.digest(Path(ext4.__file__))=='ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854','frozen copy helper')
    helper.require(helper.digest(Path(helper.__file__))=='da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22','frozen native helper')
    out.mkdir(parents=True,exist_ok=False)
    helper.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        inputs_sha256={helper.key(source):args.summary_sha256,helper.key(batch/'workspace.json'):helper.digest(batch/'workspace.json'),helper.key(Path(__file__)):helper.digest(__file__),helper.key(Path(ext4.__file__)):helper.digest(Path(ext4.__file__)),helper.key(Path(helper.__file__)):helper.digest(Path(helper.__file__))},
        scope='Separate archival after completed native calls; not solver execution, mathematical verification, UNSAT proof checking or target coverage.',solver_calls=0,delete_originals=False))
    records=[]
    try:
        for item in summary['cases']:
            index=item['index'];helper.require(type(index)is int and 0<=index<16,'finite case index')
            folder=batch/f'case_{index:02d}';case_summary=helper.read(folder/'summary.json')
            helper.require(case_summary==item,'exact saved per-case outcome')
            helper.require(not item['receipt']['outer_windows_guard_expired'],'no final byte assertion for unknown process state')
            trace=item['trace'];expected=workspace+f'/case_{index:02d}.drat';helper.require(trace['linux_path']==expected,'exact retained raw trace path')
            helper.require(shutil.disk_usage(ROOT).free>=21*1024**3,'host reserve21GiB')
            target=out/f'case_{index:02d}.proof.drat';helper.require(not target.exists(),'never overwrite')
            copy=ext4.proof_copy(expected,target,out/f'case_{index:02d}_transfer')
            if trace.get('sha256')is not None:helper.require(copy['sha256']==trace['sha256'],'historical bounded hash agrees')
            if trace.get('bytes')is not None:helper.require(copy['bytes']==trace['bytes'],'historical bounded size agrees')
            records.append(dict(index=index,path=helper.key(target),sha256=copy['sha256'],bytes=copy['bytes'],transfer=copy,
                native_result=item['result'],availability='LOCAL_ONLY',proof_replayed=False))
            helper.save(out/f'checkpoint_{index:02d}.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),completed_archives=len(records),records=records.copy(),solver_calls=0,proofs_replayed=0))
            print(json.dumps(dict(case=index,archived_bytes=copy['bytes'])),flush=True)
        helper.save(out/'summary.json',dict(status='BATCH_TRACE_ARCHIVE_IDENTITY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),batch_summary_sha256=args.summary_sha256,
            records=records,trace_files=len(records),trace_bytes=sum(r['bytes']for r in records),solver_calls=0,proofs_replayed=0,target_resolution=False,
            scope='Exact copies only; SAT learned traces are not UNSAT proofs. A terminal UNSAT still requires complete separate independent replay and coverage.',outputs_sha256={helper.key(p):helper.digest(p)for p in out.iterdir()if p.is_file()}))
    except BaseException as error:helper.save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),error=repr(error),completed_archives=records,original_ext4_workspace_preserved=workspace));raise
if __name__=='__main__':main()

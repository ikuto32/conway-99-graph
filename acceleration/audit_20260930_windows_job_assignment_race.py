"""Harmless live assignment-order countercontrol; only exact owned handles."""
from pathlib import Path
from ctypes import wintypes
from datetime import datetime,timezone
import argparse,ctypes,hashlib,importlib.util,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration'
SOURCE=A/'build_20260930_exact_eight_parallel_batch.py';CANARY=A/'calibrate_20260930_parallel_build_canary_v3.py'
def need(x,msg):
    if not x:raise ValueError(msg)
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def waitfile(p,seconds=2):
    until=time.monotonic()+seconds
    while not p.exists()and time.monotonic()<until:time.sleep(0.01)
    need(p.exists(),'bounded owned marker '+p.name)
    # The file is small but creation can precede the last write.
    while True:
        try:return json.loads(p.read_bytes())
        except json.JSONDecodeError:
            need(time.monotonic()<until,'complete owned marker');time.sleep(0.01)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(exist_ok=False,parents=True);start=time.monotonic()
    need(os.name=='nt','Windows only');need(h(SOURCE)=='6b1b4c4f80a24e6851643032689df37a5a9641ee4c465ae04aab3f008ae8ec44','exact frozen backend')
    pins={p.relative_to(ROOT).as_posix():h(p)for p in [SOURCE,SOURCE.with_name(SOURCE.stem+'_spec.md'),SOURCE.with_name(SOURCE.stem+'_pins.json'),CANARY,Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']}
    for name,value in json.loads(SOURCE.with_name(SOURCE.stem+'_pins.json').read_bytes())['inputs_sha256'].items():need(h(ROOT/name)==value,'frozen import closure');pins[name]=value
    spec=importlib.util.spec_from_file_location('reviewed_assignment_backend',SOURCE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    api=ctypes.WinDLL('kernel32',use_last_error=True)
    for name,(args,result)in {'OpenProcess':([wintypes.DWORD,wintypes.BOOL,wintypes.DWORD],wintypes.HANDLE),'CloseHandle':([wintypes.HANDLE],wintypes.BOOL),'WaitForSingleObject':([wintypes.HANDLE,wintypes.DWORD],wintypes.DWORD),'IsProcessInJob':([wintypes.HANDLE,wintypes.HANDLE,ctypes.POINTER(wintypes.BOOL)],wintypes.BOOL),'TerminateProcess':([wintypes.HANDLE,wintypes.UINT],wintypes.BOOL)}.items():f=getattr(api,name);f.argtypes=args;f.restype=result
    owned={};job=None;proc=None;logs=[];record={}
    def op(pid):
        if pid not in owned:
            handle=api.OpenProcess(0x00100000|0x0400|0x0001,False,pid);need(bool(handle),'own PID open');owned[pid]=handle
        return owned[pid]
    def isin(pid):
        flag=wintypes.BOOL();need(api.IsProcessInJob(op(pid),job.handle,ctypes.byref(flag)),'exact membership API');return bool(flag.value)
    try:
        save(out/'manifest.json',dict(inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),allocation_seconds=15,real_process_scope='Only fresh dummy Python interpreter/writer tree; exact owned handles; no formula or native research command.'))
        logs=[(out/'stdout.log').open('xb'),(out/'stderr.log').open('xb')]
        cmd=[sys.executable,'-B',str(CANARY),'--out',str(out),'--level','0','--seconds','3','--root-seconds','3']
        proc=subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.PIPE,stdout=logs[0],stderr=logs[1],close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW);op(proc.pid)
        # Controlled delay until the Python application exists, while it remains
        # blocked on exactly the same RUN barrier used by the reviewed design.
        root=waitfile(out/'level0.startup.json');op(root['pid']);before=time.monotonic()-start
        need(not (out/'level0.json').exists(),'application still blocked on RUN')
        need(root['pid']==proc.pid or root['parent_pid']==proc.pid,'own interpreter launch relationship')
        job=m.WindowsJob();job.assign(proc.pid)
        before_membership={str(pid):isin(pid)for pid in owned};need(before_membership[str(proc.pid)],'Popen root is positively assigned')
        proc.stdin.write(b'RUN\n');proc.stdin.flush();proc.stdin.close()
        records=[waitfile(out/f'level{i}.json')for i in range(3)];spawns=[waitfile(out/f'level{i}.spawn.json')for i in range(2)]
        for r in records:op(r['pid'])
        for r in spawns:op(r['child_popen_pid'])
        need(all(spawns[i]['parent_application_pid']==records[i]['pid']for i in range(2)),'owned spawning identities')
        need(all(records[i+1]['pid']==spawns[i]['child_popen_pid']or records[i+1]['parent_pid']==spawns[i]['child_popen_pid']for i in range(2)),'owned child interpreter identities')
        membership={str(pid):isin(pid)for pid in owned};active=job.active();escaped=[r['pid']for r in records if not membership[str(r['pid'])]]
        record=dict(command=cmd,popen_pid=proc.pid,preRUN_application=root,seconds_before_assignment=before,preRUN_membership=before_membership,application_records=records,spawn_records=spawns,owned_membership=membership,job_active_before_termination=active,escaped_application_pids=escaped)
        job.terminate();proc.wait(timeout=2)
        until=time.monotonic()+2
        while job.active()and time.monotonic()<until:time.sleep(0.01)
        need(job.active()==0,'assigned job completely stopped')
        still_running=[pid for pid in escaped if api.WaitForSingleObject(op(pid),0)==258]
        heartbeat_before=[len((out/f'level{i}.heartbeat').read_bytes())for i in range(3)];time.sleep(0.10);heartbeat_after=[len((out/f'level{i}.heartbeat').read_bytes())for i in range(3)]
        record.update(job_active_zero_after_termination=True,escaped_running_after_job_termination=still_running,heartbeat_before=heartbeat_before,heartbeat_after=heartbeat_after)
        demonstrated=bool(escaped)and bool(still_running)and any(y>x for x,y in zip(heartbeat_before,heartbeat_after))
        if escaped:need(demonstrated,'escaped-runtime continuation confirmation')
        # Explicitly stop every known owned interpreter/launcher, including those
        # outside the job; never enumerate or signal an unrelated process.
        for pid,handle in owned.items():
            if api.WaitForSingleObject(handle,0)==258:need(api.TerminateProcess(handle,1223),'owned escape cleanup')
        need(all(api.WaitForSingleObject(handle,2000)==0 for handle in owned.values()),'all owned handles reaped/signalled')
        record['manual_exact_handle_cleanup_completed']=True;save(out/'observation.json',record)
        need(time.monotonic()-start<15,'allocation')
        status='INDEPENDENT_WINDOWS_JOB_PREASSIGNMENT_RACE_DEMONSTRATED'if demonstrated else'INDEPENDENT_WINDOWS_JOB_PREASSIGNMENT_RACE_NOT_OBSERVED'
        result=dict(status=status,created_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,source_scope='Exact reviewed WindowsJob.assign/terminate and Popen-then-assign order with RUN barrier; only the pre-assignment scheduling delay is controlled.',observed_escaped_applications=len(escaped),actual_owned_handles=len(owned),real_research_processes=0,native_calls=0,formula_builds=0,elapsed_seconds=time.monotonic()-start,limitations=['One explicit live scheduling countercontrol; not an estimate of occurrence frequency or evidence of an escaped prior research build.','Earlier immediate-assignment success was a finite timing sample, not a universal containment proof.','If demonstrated, the barrier prevents application work before RUN but does not retroactively assign an already-created interpreter descendant.'],outputs_sha256={p.relative_to(ROOT).as_posix():h(p)for p in out.iterdir()if p.is_file()})
        save(out/'summary.json',result);print(json.dumps(dict(status=status,summary_sha256=h(out/'summary.json'),escaped_applications=len(escaped))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),inputs_sha256=pins,observation=record,elapsed_seconds=time.monotonic()-start));raise
    finally:
        if job and job.handle:
            try:job.terminate()
            finally:job.close()
        for pid,handle in owned.items():
            if api.WaitForSingleObject(handle,0)==258:api.TerminateProcess(handle,1223)
            api.WaitForSingleObject(handle,2000);api.CloseHandle(handle)
        if proc:
            if proc.poll()is None:proc.kill()
            proc.wait(timeout=2)
        for f in logs:f.close()
if __name__=='__main__':main()

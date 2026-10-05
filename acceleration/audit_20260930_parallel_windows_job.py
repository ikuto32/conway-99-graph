"""Owned-process-only live Job Object calibration, not formula orchestration approval."""
from pathlib import Path
from ctypes import wintypes
import argparse,ctypes,hashlib,importlib.util,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration'
SOURCE=A/'build_20260930_exact_eight_parallel_batch.py';CANARY=A/'calibrate_20260930_parallel_build_canary.py'
PINS={SOURCE:'6b1b4c4f80a24e6851643032689df37a5a9641ee4c465ae04aab3f008ae8ec44',SOURCE.with_name(SOURCE.stem+'_spec.md'):'52d82fcbe56600b68d6e85d62bed983dad4859f1ad370a8a1899f9a139a95928',SOURCE.with_name(SOURCE.stem+'_pins.json'):'f93d4d0cee0240624f621eb5915e1e74d6b8ad9baa54a71fe71b6a242cb0d45d'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def h(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={};jobs=[];handles=[];children=[]
    need(os.name=='nt','Windows required')
    for p,v in PINS.items():need(h(p)==v,'frozen reviewed source');pins[p.relative_to(ROOT).as_posix()]=v
    for name,value in json.loads(SOURCE.with_name(SOURCE.stem+'_pins.json').read_bytes())['inputs_sha256'].items():need(h(ROOT/name)==value,'closure identity');pins[name]=value
    for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),CANARY,ROOT/'uv.lock',ROOT/'pyproject.toml']:pins[p.relative_to(ROOT).as_posix()]=h(p)
    spec=importlib.util.spec_from_file_location('reviewed_parallel_jobs',SOURCE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    api=ctypes.WinDLL('kernel32',use_last_error=True)
    for name,(args,ret)in {'OpenProcess':([wintypes.DWORD,wintypes.BOOL,wintypes.DWORD],wintypes.HANDLE),'CloseHandle':([wintypes.HANDLE],wintypes.BOOL),'WaitForSingleObject':([wintypes.HANDLE,wintypes.DWORD],wintypes.DWORD),'IsProcessInJob':([wintypes.HANDLE,wintypes.HANDLE,ctypes.POINTER(wintypes.BOOL)],wintypes.BOOL),'GetExitCodeProcess':([wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)],wintypes.BOOL)}.items():f=getattr(api,name);f.argtypes=args;f.restype=ret
    def opened(pid):
        handle=api.OpenProcess(0x00100000|0x0400,False,pid)
        need(bool(handle),'open only owned PID');handles.append(handle);return handle
    def member(handle,job):
        flag=wintypes.BOOL();need(api.IsProcessInJob(handle,job,ctypes.byref(flag)),'membership query');return bool(flag.value)
    def stopped(handle):return api.WaitForSingleObject(handle,2000)==0
    def exitcode(handle):
        result=wintypes.DWORD();need(api.GetExitCodeProcess(handle,ctypes.byref(result)),'exit query');return result.value
    def make(label,root_seconds=6):
        folder=out/label;folder.mkdir()
        obj=m.WindowsChild.__new__(m.WindowsChild);obj.index=0;obj.started=time.monotonic();obj.done=None;obj.logs=[]
        obj.job=m.WindowsJob();jobs.append(obj.job);obj.stdout=folder/'stdout.log';obj.stderr=folder/'stderr.log';obj.logs=[obj.stdout.open('xb'),obj.stderr.open('xb')];obj.receipt_path=folder/'receipt.json'
        command=[sys.executable,'-B',str(CANARY),'--out',str(folder),'--level','0','--seconds','6','--root-seconds',str(root_seconds)]
        obj.record=dict(command=command,case_id=label,attempt_id='harmless_calibration');obj.worker_command=command
        obj.process=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.PIPE,stdout=obj.logs[0],stderr=obj.logs[1],creationflags=subprocess.CREATE_NO_WINDOW,close_fds=True);children.append(obj.process)
        obj.job.assign(obj.process.pid);root_handle=opened(obj.process.pid)
        time.sleep(0.08);need(not list(folder.glob('level*.json')) and obj.job.active()==1,'unreleased stdin barrier has no descendants')
        obj.process.stdin.write(b'RUN\n');obj.process.stdin.flush();obj.process.stdin.close()
        until=time.monotonic()+2
        while len(list(folder.glob('level*.json')))<3 and time.monotonic()<until:time.sleep(0.01)
        need(len(list(folder.glob('level*.json')))==3,'three canary generations started')
        records=[json.loads((folder/f'level{i}.json').read_bytes())for i in range(3)]
        need(records[0]['pid']==obj.process.pid and records[1]['parent_pid']==records[0]['pid'] and records[2]['parent_pid']==records[1]['pid'],'literal owned tree identity')
        owned=[root_handle]+[opened(r['pid'])for r in records[1:]]
        need(len({r['pid']for r in records})==3 and all(member(x,obj.job.handle)for x in owned),'inherited membership all three generations')
        outside=opened(os.getpid());need(not member(outside,obj.job.handle),'outside process membership negative control')
        return obj,folder,records,owned
    results=[]
    try:
        save(out/'manifest.json',dict(inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),shared_tested_code='Imported frozen WindowsJob and WindowsChild.finish/poll/abort_launch under review; own canary replaces only producer launch. No formula or producer main executes.',allocation_seconds=40))
        for label,mode in [('terminate_tree','terminate'),('close_tree','close'),('normal_root_orphans','normal')]:
            obj,folder,records,owned=make(label,0.4 if mode=='normal' else 6)
            if mode=='normal':obj.process.wait(timeout=2);need(obj.job.active()>0,'descendants survive root exit until owned cleanup');receipt=obj.finish(False)
            elif mode=='terminate':receipt=obj.finish(True)
            else:
                obj.job.close();obj.process.wait(timeout=2)
                for f in obj.logs:f.close()
                receipt=dict(kill_on_close=True,reaped=True,actual_exit_code=obj.process.returncode)
            need(all(stopped(x)for x in owned),'every owned process handle signalled')
            first=[(folder/f'level{i}.heartbeat').read_bytes()for i in range(3)];time.sleep(0.08);need(first==[(folder/f'level{i}.heartbeat').read_bytes()for i in range(3)],'no further writes after cleanup')
            result=dict(label=label,owned_tree=records,exit_codes=[exitcode(x)for x in owned],all_handles_signalled=True,stable_heartbeat_bytes=[len(x)for x in first],receipt=receipt);results.append(result);save(folder/'check.json',result)
        # Exercise the literal WindowsChild constructor and actual frozen worker:
        # a deliberately invalid command is rejected before any producer call.
        folder=out/'invalid_producer_command';folder.mkdir();record=dict(command=[sys.executable,'-B',str(CANARY)],case_id='invalid-command',attempt_id='control')
        obj=m.WindowsChild(0,record,time.monotonic()+3,folder);jobs.append(obj.job);children.append(obj.process);obj.process.wait(timeout=3);need(obj.process.returncode!=0,'literal worker rejects nonproducer command');receipt=obj.finish(False);need(receipt['job_active_zero_observed']and receipt['reaped'],'rejected worker complete cleanup');results.append(dict(label='invalid_producer_command',receipt=receipt,producer_called=False))
        # Force assignment failure before RUN. The unreleased actual worker must
        # be killed/reaped by the frozen abort_launch method.
        folder=out/'assignment_failure';folder.mkdir();original=m.WindowsJob;failed_handles=[]
        class FailingAssignment(original):
            def assign(self,pid):failed_handles.append(opened(pid));raise OSError('calibration: refused assignment before release')
        m.WindowsJob=FailingAssignment
        try:
            try:m.WindowsChild(0,record,time.monotonic()+3,folder)
            except OSError:pass
            else:raise ValueError('assignment failure accepted')
        finally:m.WindowsJob=original
        need(len(failed_handles)==1 and stopped(failed_handles[0]),'assignment-failed worker terminated and reaped');failure=json.loads((folder/'child_000.launch_failure.json').read_bytes());need(failure['cleanup_errors']==[],'assignment-failure cleanup errors absent');results.append(dict(label='assignment_failure',owned_handle_signalled=True,cleanup_errors=[],producer_called=False))
        need(time.monotonic()-start<40,'calibration allocation')
        summary=dict(status='INDEPENDENT_PARALLEL_WINDOWS_JOB_COMPONENT_CALIBRATION_PASS',inputs_sha256=pins,results=results,real_canary_trees=3,real_canary_processes=9,real_rejected_workers=2,native_calls=0,formula_builds=0,source_closure_review='Reviewed import and dynamic producer-helper paths; no native/WSL/process inventory invoked.',limit='Only Job Object containment/cleanup component calibration. Full v1 orchestrator is NOT approved because separately preserved scheduler deadline counterexample exists.',elapsed_seconds=time.monotonic()-start,outputs_sha256={p.relative_to(ROOT).as_posix():h(p)for p in out.rglob('*')if p.is_file()})
        save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=h(out/'summary.json'),elapsed_seconds=summary['elapsed_seconds'])))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),inputs_sha256=pins,results=results,elapsed_seconds=time.monotonic()-start));raise
    finally:
        # Only jobs/process handles created by this calibrator, never a PID scan.
        for job in jobs:
            if job.handle:
                try:job.terminate()
                finally:job.close()
        for child in children:
            if child.poll()is None:child.kill()
            child.wait(timeout=3)
        for handle in handles:api.CloseHandle(handle)
if __name__=='__main__':main()

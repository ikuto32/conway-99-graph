"""Four separately budgeted serial builders; suspended Windows job containment."""
import argparse,ctypes,json,os,subprocess,sys,time,traceback
from ctypes import wintypes
from pathlib import Path
import build_20260930_exact_eight_explicit_batch_v2 as base
from build_20260930_exact_eight_parallel_batch import WindowsJob
ROOT=base.ROOT;A=base.A;SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
SERIAL=Path(base.__file__).resolve()
PINS={SERIAL:'c5acba24df4c224dce98510a6a77b4ca490ed0cd632f56d674fccffc0d0d7c2b',A/'build_20260930_exact_eight_parallel_batch.py':'6b1b4c4f80a24e6851643032689df37a5a9641ee4c465ae04aab3f008ae8ec44'}
PINS.update(base.PINS)
sha=base.sha;key=base.key;read=base.read;need=base.need;save=base.save

class StartupInfo(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('lpReserved',wintypes.LPWSTR),('lpDesktop',wintypes.LPWSTR),('lpTitle',wintypes.LPWSTR)]+[(x,wintypes.DWORD)for x in ['dwX','dwY','dwXSize','dwYSize','dwXCountChars','dwYCountChars','dwFillAttribute','dwFlags']]+[('wShowWindow',wintypes.WORD),('cbReserved2',wintypes.WORD),('lpReserved2',ctypes.POINTER(ctypes.c_ubyte)),('hStdInput',wintypes.HANDLE),('hStdOutput',wintypes.HANDLE),('hStdError',wintypes.HANDLE)]
class ProcessInfo(ctypes.Structure):
    _fields_=[('hProcess',wintypes.HANDLE),('hThread',wintypes.HANDLE),('dwProcessId',wintypes.DWORD),('dwThreadId',wintypes.DWORD)]

class SuspendedTree:
    """Prepare without executing any interpreter code; no Popen-assignment race."""
    def __init__(self,command,cwd,stdout,stderr):
        need(os.name=='nt','Windows-only contained launch')
        import msvcrt
        self.command=list(command);self.job=WindowsJob();self.api=self.job.api;self.pi=ProcessInfo();self.streams=[];self.resumed=False;self.stop_requested=False;self.stop_reason=None;self.started=None;self.deadline=None;self.observed_exit=None;self.created=False
        decl={'CreateProcessW':([wintypes.LPCWSTR,wintypes.LPWSTR,ctypes.c_void_p,ctypes.c_void_p,wintypes.BOOL,wintypes.DWORD,ctypes.c_void_p,wintypes.LPCWSTR,ctypes.POINTER(StartupInfo),ctypes.POINTER(ProcessInfo)],wintypes.BOOL),'ResumeThread':([wintypes.HANDLE],wintypes.DWORD),'WaitForSingleObject':([wintypes.HANDLE,wintypes.DWORD],wintypes.DWORD),'GetExitCodeProcess':([wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)],wintypes.BOOL),'TerminateProcess':([wintypes.HANDLE,wintypes.UINT],wintypes.BOOL)}
        for name,(args,result)in decl.items():f=getattr(self.api,name);f.argtypes=args;f.restype=result
        inherited=[]
        try:
            self.streams=[open(os.devnull,'rb'),Path(stdout).open('xb'),Path(stderr).open('xb')]
            inherited=[msvcrt.get_osfhandle(f.fileno())for f in self.streams]
            for handle in inherited:os.set_handle_inheritable(handle,True)
            si=StartupInfo();si.cb=ctypes.sizeof(si);si.dwFlags=0x100;si.hStdInput,si.hStdOutput,si.hStdError=inherited
            cmdline=ctypes.create_unicode_buffer(subprocess.list2cmdline(command))
            self.job.check(self.api.CreateProcessW(command[0],cmdline,None,None,True,0x00000004|0x08000000,None,str(cwd),ctypes.byref(si),ctypes.byref(self.pi)))
            self.created=True
            # The primary thread is still suspended; no venv redirector can spawn.
            self.job.check(self.api.AssignProcessToJobObject(self.job.handle,self.pi.hProcess))
            self.suspended_job_active=self.job.active();need(self.suspended_job_active==1,'exact suspended root in job')
        except BaseException:
            # No task has been resumed when preparation fails.
            if self.created:self.api.TerminateProcess(self.pi.hProcess,1223)
            try:self.request_stop('PREPARATION_FAILED')
            finally:self.cleanup()
            raise
        finally:
            for handle in inherited:
                try:os.set_handle_inheritable(handle,False)
                except OSError:pass
    def resume(self,seconds,clock=time.monotonic):
        need(not self.resumed and not self.stop_requested,'single release')
        self.started=clock();self.deadline=self.started+seconds
        previous=self.api.ResumeThread(self.pi.hThread)
        if previous==0xffffffff:raise ctypes.WinError(ctypes.get_last_error())
        need(previous==1,'exactly one initial suspend count')
        self.resumed=True;self.job.check(self.api.CloseHandle(self.pi.hThread));self.pi.hThread=None
    def poll(self):
        if not self.created:return None
        result=self.api.WaitForSingleObject(self.pi.hProcess,0)
        if result==258:return None
        need(result==0,'process poll result')
        code=wintypes.DWORD();self.job.check(self.api.GetExitCodeProcess(self.pi.hProcess,ctypes.byref(code)));self.observed_exit=int(code.value);return self.observed_exit
    def request_stop(self,reason):
        if self.stop_requested:return
        # TerminateJobObject requests termination; no wait/log read/hash here.
        try:self.job.terminate()
        except BaseException:
            # Kill-on-close is a nonblocking fallback. Losing the query handle
            # makes later independent active-zero observation unavailable/fatal.
            self.job.close()
        self.stop_requested=True;self.stop_reason=reason
    def cleanup(self):
        """Only after every peer has a stop request. May block; cannot hide work."""
        errors=[];active_zero=False;reaped=not self.created;code=self.observed_exit
        try:
            if not self.stop_requested:self.request_stop('CLEANUP_FALLBACK')
            if self.created:
                result=self.api.WaitForSingleObject(self.pi.hProcess,5000);need(result==0,'root process reap');reaped=True;code=self.poll()
            need(self.job.handle is not None,'job handle unavailable after kill-on-close fallback')
            until=time.monotonic()+5
            while self.job.active()and time.monotonic()<until:time.sleep(.01)
            active_zero=self.job.active()==0;need(active_zero,'zero runtime descendants after stop')
        except BaseException as ex:errors.append(repr(ex))
        finally:
            try:self.job.close()
            except BaseException as ex:errors.append(repr(ex))
            for name in ['hThread','hProcess']:
                handle=getattr(self.pi,name)
                if handle:
                    try:self.job.check(self.api.CloseHandle(handle))
                    except BaseException as ex:errors.append(repr(ex))
                    setattr(self.pi,name,None)
            for stream in self.streams:stream.close()
        return dict(pid=int(self.pi.dwProcessId),resumed=self.resumed,started_monotonic=self.started,deadline_monotonic=self.deadline,stop_requested=self.stop_requested,stop_reason=self.stop_reason,actual_exit_code=code,reaped=reaped,job_active_zero_observed=active_zero,cleanup_errors=errors,created_suspended=self.created,suspended_job_active=getattr(self,'suspended_job_active',None))

def monitor(trees,seconds=120,clock=time.monotonic,sleep=time.sleep):
    """Only release, poll and stop in active phase. Cleanup deferred for all peers."""
    need(len(trees)==4 and seconds==120,'four independent120-second allocations')
    events=[];stop_errors=[];failure=None
    try:
        for i,tree in enumerate(trees):tree.resume(seconds,clock);events.append(dict(kind='resumed',chunk=i,time=clock(),deadline=tree.deadline))
        while any(not t.stop_requested for t in trees):
            for i,tree in enumerate(trees):
                if tree.stop_requested:continue
                now=clock();code=tree.poll()
                if now>=tree.deadline:
                    tree.request_stop('CHUNK_DEADLINE');events.append(dict(kind='stop_requested',chunk=i,time=clock(),reason='CHUNK_DEADLINE'))
                elif code is not None:
                    tree.request_stop('SERIAL_ROOT_EXIT');events.append(dict(kind='stop_requested',chunk=i,time=clock(),reason='SERIAL_ROOT_EXIT',exit_code=code))
                    if code!=0:failure='SERIAL_NONZERO_EXIT';break
            if failure:break
            if any(not t.stop_requested for t in trees):sleep(.01)
    except BaseException as ex:failure=repr(ex)
    finally:
        # This complete nonblocking pass precedes every wait/active drain/hash.
        for i,tree in enumerate(trees):
            if not tree.stop_requested:
                try:tree.request_stop('PEER_FAILURE_OR_FINAL_STOP');events.append(dict(kind='stop_requested',chunk=i,time=clock(),reason='PEER_FAILURE_OR_FINAL_STOP'))
                except BaseException as ex:stop_errors.append(dict(chunk=i,error=repr(ex)))
        stop_phase_finished=clock();receipts=[]
        for i,tree in enumerate(trees):
            try:receipts.append(dict(chunk=i,**tree.cleanup()))
            except BaseException as ex:receipts.append(dict(chunk=i,cleanup_errors=[repr(ex)]))
    return dict(events=events,stop_phase_finished=stop_phase_finished,cleanup_finished=clock(),failure=failure,stop_errors=stop_errors,receipts=receipts)

def validate_plan(plan,load=read):
    need(plan['schema']=='EXACT_EIGHT_FOUR_SERIAL_BUILD_PLAN_V1'and plan['workers']==4 and plan['seconds_per_chunk']==120,'four separately budgeted chunks')
    parent_path=base.repo_file(plan['parent_selection_path']);need(sha(parent_path)==plan['parent_selection_sha256'],'exact parent selection')
    parent=load(parent_path);universe=load(base.MANIFEST);ids=base.selection_ids(parent,universe);need(len(ids)==64,'exact64 parent IDs')
    entries=plan['build_selections'];need(len(entries)==4,'exact4 partitions');seen=[];outs=[];attempts=[]
    for i,row in enumerate(entries):
        p=base.repo_file(row['path']);need(sha(p)==row['sha256'],'partition SHA');s=load(p);part=base.selection_ids(s,universe)
        need(s['selection_policy']=='AUTHORIZED_DISJOINT_BUILD_PARTITION_V1'and s['parent_selection_path']==plan['parent_selection_path']and s['parent_selection_sha256']==plan['parent_selection_sha256']and s['partition_index']==i and s['partition_offset']==16*i,'literal partition provenance')
        need(part==ids[16*i:16*i+16],'contiguous disjoint16 partition');seen+=part
        out=(ROOT/row['out']).resolve();need(type(row['out'])is str and key(out)==row['out']and out.is_relative_to(ROOT)and not out.exists(),'new repository chunk output')
        attempt=row['attempt_id'];need(type(attempt)is str and attempt and attempt.isascii()and all(c.isalnum()or c in '_-'for c in attempt),'safe unique attempt')
        outs.append(out);attempts.append(attempt)
    need(seen==ids and len(set(seen))==64 and len(set(outs))==len(set(attempts))==4,'no overlap or reused attempts')
    need(all(not a.is_relative_to(b)for a in outs for b in outs if a!=b),'output directories disjoint')
    return ids,entries,outs

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['plan','build']);ap.add_argument('--launch-plan',type=Path,required=True);ap.add_argument('--launch-plan-sha256',required=True);ap.add_argument('--engineering-gate',type=Path);ap.add_argument('--engineering-gate-sha256');ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={};trees=[];result=None
    try:
        for p,w in PINS.items():need(sha(p)==w,'frozen source/input');bindings[key(p)]=w
        for p in [Path(__file__),SPEC,A/'build_20260930_exact_eight_explicit_batch_v2_spec.md',A/'build_20260930_exact_eight_parallel_batch_spec.md']:bindings[key(p)]=sha(p)
        p=args.launch_plan.resolve();need(p.is_relative_to(ROOT)and sha(p)==args.launch_plan_sha256,'exact root launch plan');bindings[key(p)]=args.launch_plan_sha256;plan=read(p);ids,entries,folders=validate_plan(plan)
        need(all(not out.is_relative_to(f)and not f.is_relative_to(out)for f in folders),'launcher receipts separate from case outputs')
        for p in [base.repo_file(plan['parent_selection_path'])]+[base.repo_file(r['path'])for r in entries]:
            bindings[key(p)]=sha(p);selection=read(p);auth=base.repo_file(selection['authorization_record_path']);need(sha(auth)==selection['authorization_record_sha256'],'selection authority');bindings[key(auth)]=sha(auth)
        commands=[[sys.executable,'-B',str(SERIAL),'build','--selection',str(ROOT/r['path']),'--selection-sha256',r['sha256'],'--attempt-id',r['attempt_id'],'--seconds','120','--out',str(folder)]for r,folder in zip(entries,folders)]
        save(out/'prepared_commands.json',dict(inputs_sha256=bindings,selected_case_ids=ids,commands=commands,per_chunk_seconds=120,total_allocated_build_seconds=480,maximum_concurrent_serial_builders=4,automatic_resume=False,native_calls=0))
        if args.mode=='plan':save(out/'summary.json',dict(status='CANDIDATE_FOUR_SERIAL_BUILD_PLAN',inputs_sha256=bindings,selected_case_ids=ids,build_invocations=0,native_calls=0));return
        need(args.engineering_gate and args.engineering_gate_sha256,'independent engineering gate mandatory before any process creation')
        ep=args.engineering_gate.resolve();need(ep.is_relative_to(ROOT)and sha(ep)==args.engineering_gate_sha256,'exact independent engineering gate');eg=read(ep)
        need(eg['status']=='INDEPENDENT_FOUR_SERIAL_BUILD_ENGINEERING_PASS','independent suspended-backend/deadline review')
        for name,value in eg['inputs_sha256'].items():need(sha(base.repo_file(name))==value,'unchanged engineering dependency')
        for source in [Path(__file__),SPEC,SERIAL,A/'build_20260930_exact_eight_parallel_batch.py']:need(eg['inputs_sha256'].get(key(source))==sha(source),'direct engineering source binding')
        bindings[key(ep)]=args.engineering_gate_sha256
        for i,cmd in enumerate(commands):trees.append(SuspendedTree(cmd,ROOT,out/f'chunk_{i:02d}.stdout.log',out/f'chunk_{i:02d}.stderr.log'))
        result=monitor(trees)
        need(not result['stop_errors']and all(r.get('reaped')and r.get('job_active_zero_observed')and not r.get('cleanup_errors')for r in result['receipts']),'all four runtime trees reaped')
        chunks=[]
        for i,(entry,folder)in enumerate(zip(entries,folders)):
            s=folder/'summary.json';chunks.append(dict(chunk=i,selection=entry,process_receipt=result['receipts'][i],summary_path=key(s)if s.is_file()else None,summary_sha256=sha(s)if s.is_file()else None,output_directory=key(folder),preserved_files={key(p):dict(sha256=sha(p),bytes=p.stat().st_size)for p in folder.rglob('*')if p.is_file()}if folder.exists()else{}))
        save(out/'summary.json',dict(status='CANDIDATE_FOUR_SERIAL_BUILD_INVOCATIONS_RECORDED',inputs_sha256=bindings,selected_case_ids=ids,chunks=chunks,monitor=result,build_invocations=sum(t.resumed for t in trees),native_calls=0,automatic_resume=False,independent_approval=False,consolidation_required=True,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()}))
    except BaseException as ex:
        # Preparation fails while all existing roots are suspended. Monitor handles
        # resumed errors itself; idempotent stop requests avoid a cleanup race.
        if result is None:
            for t in trees:
                try:t.request_stop('LAUNCHER_FAILURE')
                except BaseException:pass
            cleanup=[]
            for t in trees:
                try:cleanup.append(t.cleanup())
                except BaseException as more:cleanup.append(dict(error=repr(more)))
        else:cleanup=result
        save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=bindings,cleanup=cleanup,native_calls=0));raise
if __name__=='__main__':main()

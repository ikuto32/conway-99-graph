"""Prepared Windows-only max-four Python builders; no native solver or auto-resume."""
import argparse,ctypes,hashlib,json,os,subprocess,sys,time,traceback
from ctypes import wintypes
from datetime import datetime,timezone
from pathlib import Path
import build_20260930_exact_eight_explicit_batch_v2 as base
ROOT=base.ROOT;A=base.A;SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
# Exact predecessor/source hashes are in the adjacent immutable pin file.
PINFILE=Path(__file__).with_name(Path(__file__).stem+'_pins.json')
sha=base.sha;key=base.key;read=base.read;need=base.need;save=base.save
MAX_WORKERS=4;MAX_CASES=64;MAX_SECONDS=120

def command_for(record,attempt,folder):
    return [sys.executable,'-B',str(base.PRODUCER),'build','--campaign-manifest',str(base.MANIFEST),'--campaign-manifest-sha256',base.PINS[base.MANIFEST],'--case-id',record['case_id'],'--attempt-id',attempt,'--out',str(folder)]

def supervise(plan,workers,deadline,launch,clock=time.monotonic,sleep=time.sleep,event=lambda x:None):
    """Single scheduler: no pipes or output hashing while any worker is active."""
    need(type(workers)is int and 1<=workers<=MAX_WORKERS,'workers1..4')
    need(1<=len(plan)<=MAX_CASES,'explicit plan1..64')
    active={};finished={};next_index=0;stop=None;cleanup_errors=[];peak=0
    try:
        while active or next_index<len(plan):
            for i,child in list(active.items()):
                code=child.poll()
                if code is not None:
                    try:receipt=child.finish(False)
                    except BaseException as ex:
                        cleanup_errors.append(dict(index=i,error=repr(ex)));stop='CHILD_CLEANUP_FAILED';continue
                    del active[i];finished[i]=receipt;event(dict(kind='child_reaped',index=i,receipt=receipt))
                    if code!=0:stop='PRODUCER_NONZERO_EXIT'
            if stop:break
            if clock()>=deadline:stop='ABSOLUTE_INVOCATION_BUILD_DEADLINE';break
            while next_index<len(plan)and len(active)<workers and clock()<deadline:
                i=next_index
                try:active[i]=launch(i,plan[i],deadline)
                except BaseException as ex:
                    stop='CHILD_LAUNCH_FAILED';event(dict(kind='launch_failed',index=i,error=repr(ex)));break
                next_index+=1;peak=max(peak,len(active));event(dict(kind='child_started',index=i))
            if stop:break
            if active:sleep(min(0.025,max(0,deadline-clock())))
    except BaseException as ex:
        stop='SUPERVISOR_EXCEPTION';event(dict(kind='supervisor_exception',error=repr(ex)))
    finally:
        # Attempt every cleanup even if an earlier worker cannot be reaped.
        for i,child in list(active.items()):
            try:finished[i]=child.finish(True);event(dict(kind='child_cancelled_and_reaped',index=i,receipt=finished[i]))
            except BaseException as ex:cleanup_errors.append(dict(index=i,error=repr(ex)))
        active.clear()
    return dict(receipts=finished,launched=next_index,peak_workers=peak,stop=stop or 'ALL_SELECTED_CHILDREN_EXITED',cleanup_errors=cleanup_errors,unlaunched_indices=list(range(next_index,len(plan))))

class BasicLimit(ctypes.Structure):
    _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
class IOCounters(ctypes.Structure):
    _fields_=[(n,ctypes.c_ulonglong)for n in ['ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount']]
class ExtendedLimit(ctypes.Structure):
    _fields_=[('BasicLimitInformation',BasicLimit),('IoInfo',IOCounters)]+[(n,ctypes.c_size_t)for n in ['ProcessMemoryLimit','JobMemoryLimit','PeakProcessMemoryUsed','PeakJobMemoryUsed']]
class Accounting(ctypes.Structure):
    _fields_=[(n,ctypes.c_longlong)for n in ['TotalUserTime','TotalKernelTime','ThisPeriodTotalUserTime','ThisPeriodTotalKernelTime']]+[(n,wintypes.DWORD)for n in ['TotalPageFaultCount','TotalProcesses','ActiveProcesses','TotalTerminatedProcesses']]

class WindowsJob:
    """No breakaway flag. Any API/assignment failure is fatal before release."""
    def __init__(self):
        need(os.name=='nt','Windows job-object backend required')
        self.api=ctypes.WinDLL('kernel32',use_last_error=True);self.handle=None
        declarations={'CreateJobObjectW':([ctypes.c_void_p,wintypes.LPCWSTR],wintypes.HANDLE),'SetInformationJobObject':([wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD],wintypes.BOOL),'AssignProcessToJobObject':([wintypes.HANDLE,wintypes.HANDLE],wintypes.BOOL),'TerminateJobObject':([wintypes.HANDLE,wintypes.UINT],wintypes.BOOL),'QueryInformationJobObject':([wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.c_void_p],wintypes.BOOL),'OpenProcess':([wintypes.DWORD,wintypes.BOOL,wintypes.DWORD],wintypes.HANDLE),'CloseHandle':([wintypes.HANDLE],wintypes.BOOL)}
        for name,(args,result)in declarations.items():f=getattr(self.api,name);f.argtypes=args;f.restype=result
        self.handle=self.api.CreateJobObjectW(None,None)
        if not self.handle:raise ctypes.WinError(ctypes.get_last_error())
        try:
            info=ExtendedLimit();info.BasicLimitInformation.LimitFlags=0x2000
            self.check(self.api.SetInformationJobObject(self.handle,9,ctypes.byref(info),ctypes.sizeof(info)))
        except BaseException:self.close();raise
    def check(self,ok):
        if not ok:raise ctypes.WinError(ctypes.get_last_error())
    def assign(self,pid):
        ph=self.api.OpenProcess(0x0100|0x0001,False,pid)
        if not ph:raise ctypes.WinError(ctypes.get_last_error())
        try:self.check(self.api.AssignProcessToJobObject(self.handle,ph))
        finally:self.api.CloseHandle(ph)
    def terminate(self):self.check(self.api.TerminateJobObject(self.handle,1223))
    def active(self):
        info=Accounting();self.check(self.api.QueryInformationJobObject(self.handle,1,ctypes.byref(info),ctypes.sizeof(info),None));return info.ActiveProcesses
    def close(self):
        if self.handle:
            old=self.handle;self.handle=None;self.check(self.api.CloseHandle(old))

class WindowsChild:
    def __init__(self,index,record,deadline,out):
        self.record=record;self.index=index;self.started=time.monotonic();self.job=None;self.process=None;self.logs=[];self.done=None
        self.receipt_path=out/f'child_{index:03d}.receipt.json';self.stdout=out/f'child_{index:03d}.stdout.log';self.stderr=out/f'child_{index:03d}.stderr.log'
        command_path=out/f'child_{index:03d}.command.json';save(command_path,dict(command=record['command'],case_id=record['case_id'],attempt_id=record['attempt_id']))
        self.worker_command=[sys.executable,'-B',str(Path(__file__).resolve()),'_worker','--command-file',str(command_path),'--command-sha256',sha(command_path)]
        try:
            self.job=WindowsJob();self.logs=[self.stdout.open('xb'),self.stderr.open('xb')]
            # Worker cannot launch the producer until assignment to its job succeeds.
            self.process=subprocess.Popen(self.worker_command,cwd=ROOT,stdin=subprocess.PIPE,stdout=self.logs[0],stderr=self.logs[1],close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
            self.job.assign(self.process.pid)
            need(time.monotonic()<deadline,'deadline before worker release')
            self.process.stdin.write(b'RUN\n');self.process.stdin.flush();self.process.stdin.close()
        except BaseException as ex:
            errors=self.abort_launch();save(out/f'child_{index:03d}.launch_failure.json',dict(error=repr(ex),cleanup_errors=errors,case_id=record['case_id'],worker_command=self.worker_command));raise
    def abort_launch(self):
        errors=[]
        if self.job:
            try:self.job.terminate()
            except BaseException as ex:errors.append(repr(ex))
        if self.process:
            try:
                if self.process.poll()is None:self.process.kill()
                self.process.wait(timeout=5)
            except BaseException as ex:errors.append(repr(ex))
        if self.job:
            try:self.job.close()
            except BaseException as ex:errors.append(repr(ex))
        for f in self.logs:f.close()
        return errors
    def poll(self):return self.process.poll()
    def finish(self,cancelled):
        if self.done is not None:return self.done
        exit_before=self.process.poll();errors=[];active_zero=False
        try:
            self.job.terminate()
            code=self.process.wait(timeout=5)
            until=time.monotonic()+5
            while self.job.active()and time.monotonic()<until:time.sleep(0.01)
            active_zero=self.job.active()==0
            need(active_zero,'job still has active descendants')
        except BaseException as ex:
            errors.append(repr(ex));code=self.process.poll()
            if code is None:
                try:self.process.kill();code=self.process.wait(timeout=5)
                except BaseException as more:errors.append(repr(more))
        finally:
            try:self.job.close()
            except BaseException as ex:errors.append(repr(ex))
            for f in self.logs:f.close()
        receipt=dict(command=self.record['command'],worker_command=self.worker_command,case_id=self.record['case_id'],attempt_id=self.record['attempt_id'],pid=self.process.pid,actual_exit_code=exit_before if exit_before is not None else code,cancelled=cancelled,wall_seconds=time.monotonic()-self.started,job_active_zero_observed=active_zero,reaped=self.process.returncode is not None,cleanup_errors=errors,stdout_path=key(self.stdout),stderr_path=key(self.stderr),stdout_sha256=sha(self.stdout),stderr_sha256=sha(self.stderr),native_calls=0)
        save(self.receipt_path,receipt);self.done=receipt
        need(not errors and active_zero and receipt['reaped'],'worker cleanup must be complete')
        return receipt

def worker(argv):
    ap=argparse.ArgumentParser();ap.add_argument('--command-file',type=Path,required=True);ap.add_argument('--command-sha256',required=True);args=ap.parse_args(argv)
    need(sys.stdin.buffer.readline()==b'RUN\n','parent job-assignment barrier')
    need(sha(args.command_file)==args.command_sha256,'literal worker command identity')
    cmd=read(args.command_file)['command'];need(cmd[:4]==[sys.executable,'-B',str(base.PRODUCER),'build'],'only frozen Python formula producer')
    return subprocess.call(cmd,cwd=ROOT,stdin=subprocess.DEVNULL,close_fds=True)

def verify_child(p,receipt,byid):
    need(not receipt['cancelled']and receipt['actual_exit_code']==0 and receipt['reaped']and receipt['job_active_zero_observed']and not receipt['cleanup_errors'],'normally completed child only')
    folder=ROOT/p['output_path'];s=read(folder/'summary.json');r=byid[p['case_id']]
    need(s['status']=='CANDIDATE_EXACT_EIGHT_CAMPAIGN_LITERAL_FULL_GRAM_BUILT'and s['case_id']==p['case_id']and s['attempt_id']==p['attempt_id']and s['native_calls']==0,'complete literal child')
    for name,value in {**s['inputs_sha256'],**s['outputs_sha256']}.items():need(sha(base.repo_file(name))==value,'every child input/output identity')
    need(s['case_index']==r['case_index']and s['selected_full_count_sha256']==r['full_count_profile_sha256'],'full-count identity')
    files={n:dict(path=key(folder/n),sha256=sha(folder/n),bytes=(folder/n).stat().st_size)for n in ['summary.json','instance.cnf','model.json','scope.json','selected_profile.json','initial_domains.json','selection.json','model_package.json']}
    return dict(case_id=p['case_id'],case_index=r['case_index'],subset_index=r['subset_index'],attempt_id=p['attempt_id'],full_count_profile_sha256=r['full_count_profile_sha256'],selectors=s['selectors'],variables=s['variables'],clauses=s['clauses'],initial_domain_sizes=s['initial_domain_sizes'],files=files)

def main(argv=None):
    if argv is None:argv=sys.argv[1:]
    if argv and argv[0]=='_worker':return worker(argv[1:])
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['plan','build']);ap.add_argument('--selection',type=Path,required=True);ap.add_argument('--selection-sha256',required=True);ap.add_argument('--attempt-id',required=True);ap.add_argument('--seconds',type=int,required=True);ap.add_argument('--workers',type=int,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args(argv)
    start=time.monotonic();deadline=start+args.seconds;out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={};records=[];plan=[];events=[];dispatch=None
    try:
        need(1<=args.seconds<=MAX_SECONDS and 1<=args.workers<=MAX_WORKERS,'seconds1..120/workers1..4')
        need(args.attempt_id and args.attempt_id.isascii()and all(x.isalnum()or x in '_-'for x in args.attempt_id),'literal safe attempt ID')
        def pin(p,w=None):
            v=sha(p);need(w is None or v==w,'unchanged '+key(p));bindings[key(p)]=v
        for name,value in read(PINFILE)['inputs_sha256'].items():pin(ROOT/name,value)
        for p,value in base.PINS.items():pin(p,value)
        for p in [Path(__file__),SPEC,PINFILE]:pin(p)
        sel=args.selection.resolve();need(sel.is_relative_to(ROOT),'selection within repository');pin(sel,args.selection_sha256);selection=read(sel);authority=base.repo_file(selection['authorization_record_path']);pin(authority,selection['authorization_record_sha256'])
        universe=read(base.MANIFEST);ids=base.selection_ids(selection,universe);need(1<=len(ids)<=MAX_CASES,'selected1..64')
        need(universe['universe_size']==792 and not universe['historical_profiles_subtracted']and not universe['prior_exclusions_used'],'complete unchanged universe')
        gate=read(base.POPULATION_GATE);need(gate['status']=='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_ENCODING_PASS'and gate['population_size']==792 and gate['inputs_sha256'][key(base.MANIFEST)]==base.PINS[base.MANIFEST],'existing population authentication only')
        byid={r['case_id']:r for r in universe['records']}
        for cid in ids:
            r=byid[cid];attempt=args.attempt_id+f"_case_{r['case_index']:04d}";folder=out/f"case_{r['case_index']:04d}";need(not folder.exists(),'fresh per-case directory')
            plan.append(dict(case_id=cid,case_index=r['case_index'],subset_index=r['subset_index'],attempt_id=attempt,output_path=key(folder),command=command_for(r,attempt,folder)))
        save(out/'plan.json',dict(schema='EXACT_EIGHT_PARALLEL_EXPLICIT_BUILD_PLAN_V1',inputs_sha256=bindings,ordered_case_ids=ids,commands=plan,workers=args.workers,invocation_build_budget_seconds=args.seconds,automatic_resume=False,automatic_skip=False,native_calls=0))
        if args.mode=='plan':save(out/'summary.json',dict(status='CANDIDATE_PARALLEL_EXPLICIT_BUILD_PLAN',inputs_sha256=bindings,selected_case_ids=ids,records=[],completed_formulas=0,pending_case_ids=ids,producer_calls=0,native_calls=0));return 0
        need(os.name=='nt','Windows-only build backend')
        def event(x):
            events.append(x);save(out/f'event_{len(events):04d}.json',x)
            if x['kind']in ['child_reaped','child_cancelled_and_reaped']:print(json.dumps(dict(state=x['kind'],case_id=plan[x['index']]['case_id'],active_limit=args.workers)),flush=True)
        dispatch=supervise(plan,args.workers,deadline,lambda i,p,d:WindowsChild(i,p,d,out),event=event)
        # All worker trees must be stopped before the potentially long complete hash walk.
        need(not dispatch['cleanup_errors'],'all launched children must be reaped')
        build_phase_seconds=time.monotonic()-start;verification_errors=[]
        for i,p in enumerate(plan):
            receipt=dispatch['receipts'].get(i)
            if not receipt or receipt['cancelled']or receipt['actual_exit_code']!=0:continue
            try:records.append(verify_child(p,receipt,byid))
            except BaseException as ex:verification_errors.append(dict(case_id=p['case_id'],error=repr(ex)))
            complete={r['case_id']for r in records};save(out/f'checkpoint_{i:03d}.json',dict(selected_case_ids=ids,completed_records=records,pending_case_ids=[cid for cid in ids if cid not in complete],native_calls=0,automatic_resume=False,automatic_skip=False))
        for name,value in bindings.items():need(sha(ROOT/name)==value,'post-build source/input unchanged')
        complete={r['case_id']for r in records};pending=[cid for cid in ids if cid not in complete]
        save(out/'summary.json',dict(status='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'if not pending and not verification_errors else'CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_PARTIAL',inputs_sha256=bindings,selected_case_ids=ids,records=records,completed_formulas=len(records),pending_case_ids=pending,dispatch=dispatch,verification_errors=verification_errors,build_phase_seconds=build_phase_seconds,receipt_verification_seconds=time.monotonic()-start-build_phase_seconds,elapsed_seconds=time.monotonic()-start,producer_calls=dispatch['launched'],native_calls=0,independent_approval=False,automatic_resume=False,automatic_skip=False,previous_outcomes_consumed=0,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()}));return 0
    except BaseException as ex:
        save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=bindings,dispatch=dispatch,completed_records=records,native_calls=0,automatic_resume=False,automatic_skip=False));raise
if __name__=='__main__':sys.exit(main())

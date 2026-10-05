"""Independent source review and harmless live tests of the suspended backend."""
from pathlib import Path
from ctypes import wintypes
from datetime import datetime,timezone
import argparse,ast,copy,ctypes,hashlib,importlib.util,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';B=A/'results/20260930_independent_review'
SOURCE=A/'run_20260930_exact_eight_four_builds_v2.py';SPEC=SOURCE.with_name(SOURCE.stem+'_spec.md');CANARY=A/'calibrate_20260930_suspended_tree_canary.py'
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def reject(f,label):
    try:f()
    except (ValueError,KeyError,TypeError,OSError):return label
    raise ValueError('corruption accepted '+label)
def mock_controls(m):
    results=[]
    for scenario in ['delayed_cleanup','normal','nonzero','resume_error','poll_error','stop_error']:
        now=[0.];events=[]
        class Fake:
            def __init__(self,i):self.i=i;self.stop_requested=False;self.started=None;self.deadline=None
            def resume(self,seconds,clock):
                if scenario=='resume_error'and self.i==2:raise OSError('injected resume')
                self.started=clock();self.deadline=self.started+seconds;now[0]+=.003
            def poll(self):
                if scenario=='poll_error'and self.i==1:raise OSError('injected poll')
                if scenario=='normal':return 0 if now[0]>.05*(4-self.i)else None
                if self.i==0 and now[0]>.02:return 7 if scenario=='nonzero'else 0
                return None
            def request_stop(self,reason):
                events.append(dict(kind='stop_attempt',i=self.i,time=now[0]))
                if scenario=='stop_error'and self.i==1:raise OSError('injected stop')
                self.stop_requested=True
            def cleanup(self):
                events.append(dict(kind='cleanup',i=self.i,time=now[0]));now[0]+=5
                return dict(reaped=True,job_active_zero_observed=self.stop_requested,cleanup_errors=[]if self.stop_requested else['stop failed'])
        trees=[Fake(i)for i in range(4)]
        r=m.monitor(trees,clock=lambda:now[0],sleep=lambda d:now.__setitem__(0,now[0]+d))
        first=next(i for i,e in enumerate(events)if e['kind']=='cleanup')
        need({e['i']for e in events[:first]}==set(range(4)),'complete stop pass before cleanup')
        if scenario=='delayed_cleanup':
            need(all(e['time']<=trees[e['i']].deadline+.011 for e in events[:first]),'no cleanup hides deadline')
            need(r['cleanup_finished']>=140 and r['stop_phase_finished']<120.03,'cleanup separately timed')
        if scenario in ['nonzero','resume_error','poll_error']:need(bool(r['failure']),'failure observed')
        if scenario=='stop_error':need(bool(r['stop_errors'])and not r['receipts'][1]['job_active_zero_observed'],'stop failure not approved')
        results.append(dict(scenario=scenario,result=r,events=events))
    reject(lambda:m.monitor([],clock=lambda:0),'not_four_trees');reject(lambda:m.monitor([None]*4,seconds=119),'wrong_allocation')
    return results
def plan_controls(m,out):
    d=out/'plan_controls';d.mkdir();u=read(m.base.MANIFEST);ids=[r['case_id']for r in u['records'][:64]]
    def selection(v):return dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',campaign_manifest_path=key(m.base.MANIFEST),campaign_manifest_sha256=sha(m.base.MANIFEST),ordered_case_ids=v,selection_reason='harmless command metadata control, no build')
    parent=d/'parent.json';save(parent,selection(ids));p=dict(schema='EXACT_EIGHT_FOUR_SERIAL_BUILD_PLAN_V1',workers=4,seconds_per_chunk=120,parent_selection_path=key(parent),parent_selection_sha256=sha(parent),build_selections=[])
    for i in range(4):
        s=selection(ids[16*i:16*i+16]);s.update(selection_policy='AUTHORIZED_DISJOINT_BUILD_PARTITION_V1',parent_selection_path=key(parent),parent_selection_sha256=sha(parent),partition_index=i,partition_offset=16*i)
        f=d/f'part{i}.json';save(f,s);p['build_selections'].append(dict(path=key(f),sha256=sha(f),attempt_id=f'control_{i}',out=key(d/f'uncreated_{i}')))
    actual,_,_=m.validate_plan(p);need(actual==ids,'literal four-part order')
    bad=[]
    for label,fn in [('wrong_workers',lambda q:q.update(workers=3)),('wrong_seconds',lambda q:q.update(seconds_per_chunk=119)),('reordered',lambda q:q['build_selections'].reverse()),('duplicate_partition',lambda q:q['build_selections'].__setitem__(1,q['build_selections'][0])),('duplicate_attempt',lambda q:q['build_selections'][1].update(attempt_id='control_0')),('same_output',lambda q:q['build_selections'][1].update(out=q['build_selections'][0]['out'])),('nested_output',lambda q:q['build_selections'][1].update(out=q['build_selections'][0]['out']+'/nested')),('wrong_parent_hash',lambda q:q.update(parent_selection_sha256='0'*64))]:
        q=copy.deepcopy(p);fn(q);bad.append(reject(lambda:m.validate_plan(q),label))
    for label,value in [('bool_ids',[True]),('duplicate_ids',ids[:1]*64),('outside_ids',['not-a-case']),('string_ids',ids[0])]:
        q=selection(value);bad.append(reject(lambda:m.base.selection_ids(q,u),label))
    save(d/'result.json',dict(positive_ids=actual,corruptions=bad,plan=p,build_calls=0));return bad
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={};trees=[];handles=[];results=[];api=None
    try:
        need(os.name=='nt','Windows live calibration');need(sha(SOURCE)=='11715c9438dc8749a80f62b5ee69646dbccee194c53a1a56ded1bff83a5601e8'and sha(SPEC)=='63941c78d5e60dd124b1ceb2a4ff6cb4ab1292712f7f312bb0f4ce2d82fbdc24','frozen target')
        src=SOURCE.read_text(encoding='utf8');ast.parse(src)
        old=A/'run_20260930_exact_eight_four_builds.py';oldtext=old.read_text(encoding='utf8');line="            need(self.job.handle is not None,'job handle unavailable after kill-on-close fallback')\n";need(src.replace(line,'')==oldtext,'sole defensive runtime change')
        need(src.index('self.api.CreateProcessW(command[0]')<src.index('self.api.AssignProcessToJobObject(self.job.handle,self.pi.hProcess)')<src.index('    def resume('),'suspended assignment precedes resume method')
        need('0x00000004|0x08000000'in src and 'subprocess.Popen('not in src,'suspended API, no Popen launch');need(src.index("need(args.engineering_gate")<src.index('trees.append(SuspendedTree'),'gate before process creation')
        spec=importlib.util.spec_from_file_location('tested_suspended_launcher',SOURCE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        for p,w in m.PINS.items():need(sha(p)==w,'exact transitive pinned input');pins[key(p)]=w
        closure=[SOURCE,SPEC,old,old.with_name(old.stem+'_spec.md'),CANARY,Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),A/'build_20260930_exact_eight_explicit_batch_v2_spec.md',A/'build_20260930_exact_eight_parallel_batch_spec.md',A/'theory_20260930_hadamard_four_profile_cnf_spec.md',A/'theory_20260930_hadamard_balanced_gram_cnf_spec.md',B/'parallel_build_deadline/summary.json',B/'windows_job_assignment_race/summary.json',B/'parallel_windows_job_v2/summary.json']
        for p in closure:pins[key(p)]=sha(p)
        save(out/'manifest.json',dict(inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),allocation_seconds=60,shared_components='Imports the exact launcher and its WindowsJob/serial selection helper under test; no scientific producer import or execution. Independent fake clocks, canary, owned-handle checks and negative controls.',formula_calls=0,native_calls=0))
        mocks=mock_controls(m);save(out/'mock_controls.json',mocks);planbad=plan_controls(m,out)
        api=ctypes.WinDLL('kernel32',use_last_error=True)
        for name,(a,r)in {'OpenProcess':([wintypes.DWORD,wintypes.BOOL,wintypes.DWORD],wintypes.HANDLE),'CloseHandle':([wintypes.HANDLE],wintypes.BOOL),'WaitForSingleObject':([wintypes.HANDLE,wintypes.DWORD],wintypes.DWORD),'IsProcessInJob':([wintypes.HANDLE,wintypes.HANDLE,ctypes.POINTER(wintypes.BOOL)],wintypes.BOOL),'GetProcessId':([wintypes.HANDLE],wintypes.DWORD),'TerminateProcess':([wintypes.HANDLE,wintypes.UINT],wintypes.BOOL)}.items():f=getattr(api,name);f.argtypes=a;f.restype=r
        def opened(pid):
            h=api.OpenProcess(0x00100000|0x0400|1,False,pid);need(bool(h),'exact owned process handle');handles.append(h);return h
        def signalled(h):return api.WaitForSingleObject(h,2500)==0
        def member(h,j):
            v=wintypes.BOOL();need(api.IsProcessInJob(h,j,ctypes.byref(v)),'membership API');return bool(v.value)
        def make(label,root_seconds=6):
            d=out/label;d.mkdir();cmd=[sys.executable,'-B',str(CANARY),'--out',str(d),'--level','0','--seconds','6','--root-seconds',str(root_seconds)];t=m.SuspendedTree(cmd,ROOT,d/'stdout.log',d/'stderr.log');trees.append(t);handle=opened(t.pi.dwProcessId);need(member(handle,t.job.handle)and t.job.active()==1,'suspended root already assigned');save(d/'command.json',dict(command=cmd,root_pid=t.pi.dwProcessId));return t,d,handle
        def collect(t,d,root):
            end=time.monotonic()+2
            while not all((d/f'level{i}.heartbeat').exists()for i in range(3))and time.monotonic()<end:time.sleep(.01)
            rr=[read(d/f'level{i}.json')for i in range(3)];ss=[read(d/f'level{i}.spawn.json')for i in range(2)]
            need(rr[0]['pid']==t.pi.dwProcessId or rr[0]['parent_pid']==t.pi.dwProcessId,'root redirector ownership')
            need(all(ss[i]['parent_application_pid']==rr[i]['pid']and (rr[i+1]['pid']==ss[i]['child_popen_pid']or rr[i+1]['parent_pid']==ss[i]['child_popen_pid'])for i in range(2)),'exact descendant chain')
            ids=sorted({t.pi.dwProcessId}|{r['pid']for r in rr}|{s['child_popen_pid']for s in ss});hh=[root]+[opened(p)for p in ids if p!=t.pi.dwProcessId];need(all(member(h,t.job.handle)for h in hh),'every owned descendant contained');rec=dict(pids=ids,records=rr,spawn=ss,all_members=True,active_processes=t.job.active());save(d/'membership.json',rec);return hh
        def stable(d,hh):
            need(all(signalled(h)for h in hh),'all owned handles signalled');first=[p.read_bytes()for p in sorted(d.glob('*.heartbeat'))];time.sleep(.06);need(first==[p.read_bytes()for p in sorted(d.glob('*.heartbeat'))],'no writes after cleanup')
        t,d,h=make('delayed_resume');time.sleep(.15);need(not list(d.glob('level*'))and t.job.active()==1,'no interpreter activity before resume');t.resume(120);hh=collect(t,d,h);outside=opened(os.getpid());need(not member(outside,t.job.handle),'outside membership negative');reject(lambda:t.resume(120),'double_resume');t.request_stop('CALIBRATION_DONE');r=t.cleanup();need(r['reaped']and r['job_active_zero_observed']and not r['cleanup_errors'],'complete delayed-tree cleanup');stable(d,hh);results.append(dict(label='delayed_resume',receipt=r,logical_generations=3,pre_resume_seconds=.15,pre_resume_active=1))
        # Monitor four actual trees; wrap only polling to capture independent
        # membership while all three generations are alive, before root exits.
        pack=[make(f'four_tree_{i}',.65+.15*i)for i in range(4)];owned={};original_polls=[]
        for i,(t,d,h)in enumerate(pack):
            original=t.poll;original_polls.append(original)
            def poll(i=i,t=t,d=d,h=h,original=original):
                if i not in owned and all((d/f'level{j}.heartbeat').exists()for j in range(3)):owned[i]=collect(t,d,h)
                return original()
            t.poll=poll
        rr=m.monitor([t for t,d,h in pack]);need(not rr['failure']and not rr['stop_errors']and len(owned)==4,'four normal trees observed')
        need(all(r['reaped']and r['job_active_zero_observed']and not r['cleanup_errors']for r in rr['receipts']),'four trees fully reaped')
        for i,(t,d,h)in enumerate(pack):stable(d,owned[i])
        results.append(dict(label='four_concurrent_normal_roots',result=rr,logical_generations=12))
        # Reject assignment before the suspended interpreter can execute.
        originaljob=m.WindowsJob;rejected=[]
        class RefuseAssignment(originaljob):
            def __init__(self):
                super().__init__()
                def refuse(job,process):rejected.append(opened(api.GetProcessId(process)));return False
                self.api.AssignProcessToJobObject=refuse
        m.WindowsJob=RefuseAssignment
        try:reject(lambda:make('assignment_failure'),'assignment_failure')
        finally:m.WindowsJob=originaljob
        need(len(rejected)==1 and signalled(rejected[0])and not list((out/'assignment_failure').glob('level*')),'rejected suspended root reaped without execution');results.append(dict(label='assignment_failure',owned_root_signalled=True,application_activity=False))
        pack=[make(f'resume_failure_{i}')for i in range(4)];pack[2][0].api.ResumeThread=lambda h:0xffffffff;rr=m.monitor([t for t,d,h in pack]);need(rr['failure']and all(r['reaped']and r['job_active_zero_observed']and not r['cleanup_errors']for r in rr['receipts']),'resume failure stops all jobs');need(all(signalled(h)for t,d,h in pack),'resume-failure root handles signalled');results.append(dict(label='resume_failure',result=rr))
        t,d,h=make('kill_on_close_failure_receipt');t.resume(120);hh=collect(t,d,h)
        def fail_stop():raise OSError('injected termination API failure')
        t.job.terminate=fail_stop;t.request_stop('CALIBRATION_FALLBACK');r=t.cleanup();need(r['reaped']and not r['job_active_zero_observed']and any('job handle unavailable'in e for e in r['cleanup_errors']),'fallback active-zero fail closed');stable(d,hh);results.append(dict(label='kill_on_close_failure_receipt',receipt=r,owned_handles_signalled=True))
        need(time.monotonic()-start<60,'bounded calibration');save(out/'live_results.json',results)
        for name,h in pins.items():need(sha(ROOT/name)==h,'frozen inputs after tests')
        summary=dict(status='INDEPENDENT_FOUR_SERIAL_BUILD_ENGINEERING_PASS',created_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,scope='Exact v2 launcher: source/API-order review and finite harmless Windows lifecycle calibration. Four separately budgeted120-second sequential builders,480s allocation; tested slow cleanup cannot delay peer stop requests. No formula/selection/solver approval or speedup claim.',limitations=['Live timing is a finite sample; OS scheduling and API failures are not assumed absent.','Kill-on-close fallback reaps owned processes but fails the active-zero receipt.','Scientific producer/helper sources authenticated but not imported or executed.','Future formula outputs require separate independent checks.'],mock_scenarios=len(mocks),plan_corruptions=len(planbad),live_results=results,formula_builds=0,native_calls=0,elapsed_seconds=time.monotonic()-start,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()});save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],sha256=sha(out/'summary.json'),seconds=summary['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=pins,live_results=results,elapsed_seconds=time.monotonic()-start));raise
    finally:
        for t in trees:
            if t.pi.hProcess:
                try:t.request_stop('AUDITOR_FINALLY')
                except BaseException:pass
        for t in trees:
            if t.pi.hProcess:
                try:t.cleanup()
                except BaseException:pass
        if api:
            for h in handles:
                if api.WaitForSingleObject(h,0)==258 and api.GetProcessId(h)!=os.getpid():api.TerminateProcess(h,1223);api.WaitForSingleObject(h,2500)
                api.CloseHandle(h)
if __name__=='__main__':main()

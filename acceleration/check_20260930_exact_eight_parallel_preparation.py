"""Source-only AST and deterministic lifecycle mocks. No process/OS job calls."""
import ast,ctypes,hashlib,json,sys
from ctypes import wintypes
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';OUT=A/'results/20260930_exact_eight_parallel_build_preparation'
SOURCE=A/'build_20260930_exact_eight_parallel_batch.py';SPEC=SOURCE.with_name(SOURCE.stem+'_spec.md');PINS=SOURCE.with_name(SOURCE.stem+'_pins.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,s):
    if not v:raise ValueError(s)
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    OUT.mkdir(exist_ok=False);text=SOURCE.read_text(encoding='utf8');tree=ast.parse(text);compile(text,str(SOURCE),'exec')
    need(sha(SOURCE)=='6b1b4c4f80a24e6851643032689df37a5a9641ee4c465ae04aab3f008ae8ec44','frozen source');need(sha(SPEC)=='52d82fcbe56600b68d6e85d62bed983dad4859f1ad370a8a1899f9a139a95928','frozen spec')
    controls=[];runs={}
    def check(name,value):need(value,name);controls.append(dict(name=name,passed=True))
    def rejects(name,fn):
        try:fn()
        except (ValueError,TypeError):controls.append(dict(name=name,rejected=True));return
        raise ValueError('bad control accepted '+name)
    ns=dict(need=need,MAX_WORKERS=4,MAX_CASES=64,ctypes=ctypes,wintypes=wintypes,time=SimpleNamespace(monotonic=lambda:0,sleep=lambda _:None),sys=SimpleNamespace(executable='python-pinned'),base=SimpleNamespace(PRODUCER=Path('frozen_producer.py'),MANIFEST=Path('manifest.json'),PINS={Path('manifest.json'):'a'*64}))
    names={'supervise','command_for','BasicLimit','IOCounters','ExtendedLimit','Accounting'}
    nodes=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))and x.name in names]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<isolated scheduling/structure controls>','exec'),ns)
    supervise=ns['supervise']
    class Clock:
        def __init__(self):self.t=0
        def now(self):return self.t
        def sleep(self,n):self.t+=n
    def run(name,n=8,workers=4,deadline=120,durations=None,nonzero=None,launch_error=None,poll_error=None,cleanup_error=None,event_error=False):
        clock=Clock();children={};events=[];made=[];active_peak=0
        class FakeChild:
            def __init__(self,i):self.i=i;self.end=clock.t+(durations[i]if durations else .1);self.reaped=False;self.killed=False;self.cleanup_calls=0
            def poll(self):
                if self.i==poll_error:raise RuntimeError('injected poll failure')
                return (7 if self.i==nonzero else 0)if clock.t>=self.end else None
            def finish(self,cancelled):
                self.cleanup_calls+=1;self.killed|=cancelled;self.reaped=True
                if self.i==cleanup_error:raise RuntimeError('injected cleanup failure after reap')
                return dict(index=self.i,cancelled=cancelled,actual_exit_code=7 if self.i==nonzero else 0,reaped=True)
        def launch(i,p,d):
            nonlocal active_peak
            need(clock.now()<d,'no late launch');made.append(i)
            if i==launch_error:raise RuntimeError('injected launch failure')
            c=FakeChild(i);children[i]=c;active_peak=max(active_peak,sum(not x.reaped for x in children.values()));return c
        def event(x):
            events.append(x)
            if event_error and x['kind']=='child_started':raise RuntimeError('injected callback failure')
        result=supervise([dict(index=i)for i in range(n)],workers,deadline,launch,clock.now,clock.sleep,event)
        record=dict(result=result,made=made,clock=clock.t,events=events,children={i:dict(reaped=c.reaped,killed=c.killed,cleanup_calls=c.cleanup_calls)for i,c in children.items()},observed_peak=active_peak)
        runs[name]=record;check(name+' reaps every started fake child',all(c.reaped for c in children.values()));check(name+' concurrency bound',active_peak<=workers)
        return result,children,events
    for w in [1,2,3,4]:
        r,c,e=run('success64_workers'+str(w),64,w,durations=[.01+(i%7)*.01 for i in range(64)])
        check('all64 complete at workers'+str(w),r['launched']==64 and sorted(r['receipts'])==list(range(64))and not r['cleanup_errors']and r['stop']=='ALL_SELECTED_CHILDREN_EXITED')
    r,c,e=run('out_of_order',4,4,durations=[.4,.3,.2,.1])
    check('out-of-order results preserve literal indices',[x['index']for x in e if x['kind']=='child_reaped']==[3,2,1,0]and sorted(r['receipts'])==[0,1,2,3])
    r,c,e=run('deadline',8,4,deadline=.05,durations=[100]*8)
    check('deadline kills all four and never starts fifth',r['launched']==4 and r['stop']=='ABSOLUTE_INVOCATION_BUILD_DEADLINE'and all(x.killed for x in c.values())and r['unlaunched_indices']==[4,5,6,7])
    r,c,e=run('already_expired',8,4,deadline=0)
    check('no launch after precheck exhausted deadline',r['launched']==0 and not c)
    r,c,e=run('nonzero',8,4,durations=[.01,100,100,100,1,1,1,1],nonzero=0)
    check('nonzero stops later launches and kills siblings',r['launched']==4 and r['stop']=='PRODUCER_NONZERO_EXIT'and all(c[i].killed for i in [1,2,3]))
    r,c,e=run('launch_failure',8,4,launch_error=2)
    check('launch failure cleans earlier siblings',r['launched']==2 and r['stop']=='CHILD_LAUNCH_FAILED'and all(x.killed for x in c.values()))
    r,c,e=run('poll_failure',8,4,poll_error=0)
    check('supervisor failure cleans every active child',r['stop']=='SUPERVISOR_EXCEPTION'and all(x.killed for x in c.values()))
    r,c,e=run('cleanup_failure',8,4,cleanup_error=0)
    check('cleanup failure recorded without bypassing siblings',bool(r['cleanup_errors'])and r['stop']=='CHILD_CLEANUP_FAILED'and all(x.reaped for x in c.values()))
    r,c,e=run('event_failure',8,4,event_error=True)
    check('event failure still cleans started worker',r['stop']=='SUPERVISOR_EXCEPTION'and len(c)==1 and c[0].killed)
    for n in [0,65]:rejects('invalid selected count '+str(n),lambda n=n:supervise([{}]*n,4,1,None))
    for w in [0,5,True,'4']:rejects('invalid worker count '+repr(w),lambda w=w:supervise([{}],w,1,None))
    cmd=ns['command_for']({'case_id':'literal-id'},'attempt_case_0001',Path('fresh_case'))
    check('exact unchanged producer command ABI',cmd==['python-pinned','-B','frozen_producer.py','build','--campaign-manifest','manifest.json','--campaign-manifest-sha256','a'*64,'--case-id','literal-id','--attempt-id','attempt_case_0001','--out','fresh_case'])
    sizes={name:ctypes.sizeof(ns[name])for name in ['BasicLimit','IOCounters','ExtendedLimit','Accounting']}
    check('Windows x64 structure sizes',ctypes.sizeof(ctypes.c_void_p)==8 and sizes==dict(BasicLimit=64,IOCounters=48,ExtendedLimit=144,Accounting=48))
    check('assignment barrier precedes release',text.index('self.job.assign(self.process.pid)')<text.index("self.process.stdin.write(b'RUN\\n')"))
    check('worker validates release before command',text.index("need(sys.stdin.buffer.readline()==b'RUN\\n'")<text.index('return subprocess.call(cmd'))
    check('file-backed logs and hidden subprocess',all(s in text for s in ['stdout=self.logs[0],stderr=self.logs[1]','creationflags=subprocess.CREATE_NO_WINDOW','close_fds=True','LimitFlags=0x2000','self.api.TerminateJobObject(self.handle,1223)']))
    check('no shell invocation or process-tree shell kill','shell=True'not in text and 'taskkill'not in text and 'cmd.exe'not in text)
    check('complete hash verification only after supervise returns',text.index('dispatch=supervise(')<text.index('records.append(verify_child('))
    check('partial pending uses actual ID complement',"pending=[cid for cid in ids if cid not in complete]"in text and 'ids[len(records):]'not in text)
    pins=read_pins=json.loads(PINS.read_bytes())['inputs_sha256']
    for name,w in pins.items():check('unchanged predecessor '+name,sha(ROOT/name)==w)
    files={SOURCE,SPEC,PINS,Path(__file__)}|{ROOT/name for name in pins}
    save(OUT/'mock_lifecycles.json',runs)
    save(OUT/'summary.json',dict(status='CANDIDATE_PARALLEL_BUILD_SOURCE_MOCK_PREPARATION_PASS',inputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in sorted(files)},outputs_sha256={(OUT/'mock_lifecycles.json').relative_to(ROOT).as_posix():sha(OUT/'mock_lifecycles.json')},controls=controls,ctypes_sizes=sizes,AST_compile_only=True,isolated_mock_runs=len(runs),runtime_repository_imports=0,Windows_job_API_calls=0,real_subprocess_calls=0,formula_builds=0,native_calls=0,independent_approval=False,limitations=['Windows job-object backend remains unexecuted and requires harmless live lifecycle calibration before real build use.','Mock timing is not a speedup measurement.','Deadline covers building; termination/reaping/full receipt verification can extend return time.']))
    print(json.dumps(dict(summary_sha256=sha(OUT/'summary.json'),controls=len(controls),mock_runs=len(runs),source_sha256=sha(SOURCE),spec_sha256=sha(SPEC))))
if __name__=='__main__':
    try:main()
    except BaseException as ex:
        if OUT.is_dir()and not(OUT/'failure.json').exists():save(OUT/'failure.json',dict(error=repr(ex),source_sha256=sha(Path(__file__)),real_subprocess_calls=0,native_calls=0,formula_builds=0))
        raise

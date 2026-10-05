"""Isolated monitor counterfactuals only; no Windows API/process/formula calls."""
import ast,ctypes,hashlib,json,time
from ctypes import wintypes
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';SOURCE=A/'run_20260930_exact_eight_four_builds_v2.py';SPEC=SOURCE.with_name(SOURCE.stem+'_spec.md');OUT=A/'results/20260930_exact_eight_four_builds_preparation_v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    OUT.mkdir(exist_ok=False);text=SOURCE.read_text(encoding='utf8');tree=ast.parse(text);compile(text,str(SOURCE),'exec')
    need(sha(SOURCE)=='11715c9438dc8749a80f62b5ee69646dbccee194c53a1a56ded1bff83a5601e8','frozen source');need(sha(SPEC)=='63941c78d5e60dd124b1ceb2a4ff6cb4ab1292712f7f312bb0f4ce2d82fbdc24','frozen spec')
    ns=dict(need=need,time=time,ctypes=ctypes,wintypes=wintypes);nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in ['monitor','StartupInfo','ProcessInfo']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'<isolated monitor/structures>','exec'),ns)
    monitor=ns['monitor'];controls=[];runs={}
    def check(name,truth):need(truth,name);controls.append(dict(name=name,passed=True))
    class Clock:
        def __init__(self):self.t=0
        def now(self):return self.t
        def sleep(self,x):self.t+=x
    def run(name,ends,cleanup_delay,nonzero=None,poll_error=None,resume_error=None):
        c=Clock();stop_times={};cleanup_times={};trees=[]
        class Fake:
            def __init__(self,i):self.i=i;self.stop_requested=False;self.resumed=False;self.deadline=None
            def resume(self,seconds,clock):
                if self.i==resume_error:raise RuntimeError('injected resume error')
                self.resumed=True;self.deadline=clock()+seconds
            def poll(self):
                if self.i==poll_error:raise RuntimeError('injected poll error')
                return (7 if self.i==nonzero else 0)if c.t>=ends[self.i]else None
            def request_stop(self,reason):self.stop_requested=True;stop_times.setdefault(self.i,c.t)
            def cleanup(self):
                need(all(t.stop_requested for t in trees),'no blocking cleanup until every peer stopped');cleanup_times[self.i]=c.t;c.t+=cleanup_delay[self.i]
                return dict(reaped=True,job_active_zero_observed=True,cleanup_errors=[])
        trees=[Fake(i)for i in range(4)];result=monitor(trees,120,c.now,c.sleep);runs[name]=dict(result=result,stop_times=stop_times,cleanup_times=cleanup_times,final_clock=c.t)
        check(name+' all stops before first cleanup',len(stop_times)==4 and min(cleanup_times.values())>=max(stop_times.values()))
        check(name+' all cleanup receipts',len(result['receipts'])==4)
        return result,stop_times
    r,st=run('five_second_cleanup_counterfactual',[.025,1000,1000,1000],[5,0,0,0])
    check('delayed first cleanup does not postpone peer deadlines',all(120<=st[i]<120.011 for i in [1,2,3])and st[0]<.04 and r['cleanup_finished']>=125)
    r,st=run('extreme_cleanup_1000_seconds',[.025,1000,1000,1000],[1000]*4)
    check('extreme cleanup also leaves work deadline unchanged',all(120<=st[i]<120.011 for i in [1,2,3])and r['cleanup_finished']>=4120)
    r,st=run('normal_out_of_order',[4,3,2,1],[5]*4)
    check('normal exits stopped individually promptly',all(ends<=st[i]<ends+.011 for i,ends in enumerate([4,3,2,1])))
    r,st=run('nonzero_stops_all',[.025,1000,1000,1000],[5]*4,nonzero=0)
    check('nonzero peers terminated before any wait',r['failure']=='SERIAL_NONZERO_EXIT'and max(st.values())<.04)
    r,st=run('poll_failure_stops_all',[1000]*4,[5]*4,poll_error=0)
    check('poll error complete stop pass',r['failure']and max(st.values())==0)
    r,st=run('resume_failure_stops_prepared_roots',[1000]*4,[5]*4,resume_error=2)
    check('resume error also terminates unreleased roots',r['failure']and max(st.values())==0)
    check('suspended create flag and hidden launch',"True,0x00000004|0x08000000"in text)
    check('actual process handle assignment before any ResumeThread',text.index('self.api.AssignProcessToJobObject(self.job.handle,self.pi.hProcess)')<text.index('previous=self.api.ResumeThread(self.pi.hThread)'))
    check('no Popen worker or stdin barrier',not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='Popen'for n in ast.walk(tree))and 'RUN\\n'not in text)
    check('explicit null job handle refusal',"need(self.job.handle is not None,'job handle unavailable after kill-on-close fallback')"in text)
    check('real process handles and layouts',ctypes.sizeof(ns['StartupInfo'])==104 and ctypes.sizeof(ns['ProcessInfo'])==24)
    monitor_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='monitor');active_loop=next(n for n in monitor_node.body if isinstance(n,ast.Try)).body[1]
    attrs={n.func.attr for n in ast.walk(active_loop)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)}
    check('active loop contains no blocking cleanup/wait/hash',not(attrs&{'cleanup','wait','finish','sha','read_bytes','close'}))
    check('mandatory engineering gate before real creation',text.index("need(eg['status']=='INDEPENDENT_FOUR_SERIAL_BUILD_ENGINEERING_PASS'")<text.index('trees.append(SuspendedTree('))
    plan=A/'results/20260930_exact_eight_four_builds_plan_v2/summary.json';p=json.loads(plan.read_bytes())
    check('authorized plan-only completion with zero builds',p['status']=='CANDIDATE_FOUR_SERIAL_BUILD_PLAN'and len(p['selected_case_ids'])==64 and p['build_invocations']==p['native_calls']==0)
    files=[SOURCE,SPEC,Path(__file__),plan,A/'results/20260930_exact_eight_four_builds_plan_v2/prepared_commands.json',A/'results/20260930_exact_eight_next64_launch_preparation/launch_plan.json',A/'results/20260930_independent_review/parallel_build_deadline/summary.json',A/'results/20260930_independent_review/windows_job_assignment_race/summary.json']
    save(OUT/'mock_lifecycles.json',runs);save(OUT/'summary.json',dict(status='CANDIDATE_FOUR_SERIAL_BUILD_PREPARATION_PASS',inputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in files},controls=controls,mock_runs=len(runs),source_AST_only=True,real_subprocess_calls=0,Windows_API_calls=0,formula_builds=0,native_calls=0,independent_approval=False,limitation='Only isolated mocks and parent-authorized plan mode. Independent live harmless suspended-launch review is still mandatory before build mode.'))
    print(json.dumps(dict(summary_sha256=sha(OUT/'summary.json'),controls=len(controls),mock_runs=len(runs),plan_summary_sha256=sha(plan))))
if __name__=='__main__':
    try:main()
    except BaseException as ex:
        if OUT.is_dir()and not(OUT/'failure.json').exists():save(OUT/'failure.json',dict(error=repr(ex),source_sha256=sha(Path(__file__)),formula_builds=0,native_calls=0))
        raise

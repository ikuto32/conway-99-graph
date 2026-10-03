"""Only AST and isolated functions; never import or invoke native driver."""
import ast,copy,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';B=A/'results';DRIVER=A/'native_20260930_exact_eight_next32_v2.py';SPEC=DRIVER.with_name(DRIVER.stem+'_spec.md');OUT=B/'20260930_exact_eight_next32_native_preparation'
UNIVERSE=B/'20260930_exact_eight_campaign_preparation/campaign_manifest.json';SELECTION=B/'20260930_exact_eight_next32_selection/selection.json';NEXT_PLAN=A/'theory_20260930_exact_eight_next32_plan.md';PRIOR_PROOFS=B/'20260930_independent_review/exact_eight_first12_proofs/summary.json'
PINS={UNIVERSE:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',SELECTION:'b906256dcf706c7d03360cc2cb7e31e5dd09b52cec3ba994ae9600954aeb88cd',NEXT_PLAN:'b91ff543c53b223b8db55d03d04a9266ffaca71b43bdbca10d85ddfa607bbd42',PRIOR_PROOFS:'a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def require(x,m):
    if not x:raise ValueError(m)
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    OUT.mkdir(exist_ok=False);text=DRIVER.read_text(encoding='utf8');tree=ast.parse(text);compile(text,str(DRIVER),'exec');controls=[]
    for p,w in PINS.items():require(sha(p)==w,'frozen source-control input')
    ns=dict(re=re,UNIVERSE=UNIVERSE,SELECTION=SELECTION,NEXT_PLAN=NEXT_PLAN,PRIOR_PROOFS=PRIOR_PROOFS,PINS=PINS,h=SimpleNamespace(require=require,key=key));nodes=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='LIMITS'for t in n.targets)or isinstance(n,ast.FunctionDef)and n.name in['validate_next32','observed_result','command']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'<isolated controls only>','exec'),ns);limits=ns['LIMITS'];validate=ns['validate_next32'];u=read(UNIVERSE);sel=read(SELECTION);p0=read(PRIOR_PROOFS);prior={k:p0[k]for k in['status','completed_proof_replays','completed_attempts','SAT_pending','UNKNOWN','pending_case_ids','case_records','selected_case_ids']};expected=validate(u,sel,prior);require(expected==sel['ordered_case_ids']and len(expected)==32,'genuine fixed selection control');controls.append(dict(name='actual verified12 removal and literal next32 order',passed=True))
    def bad(name,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,AssertionError):controls.append(dict(name=name,rejected=True));return
        raise ValueError('bad control accepted '+name)
    for field,value in [('status','UNSAT_CANDIDATE'),('completed_proof_replays',11),('completed_attempts',13),('SAT_pending',1),('UNKNOWN',1),('pending_case_ids',[expected[0]])]:
        x=copy.deepcopy(prior);x[field]=value;bad('prior '+field,lambda x=x:validate(u,sel,x))
    for kind in['not accepted','not complete proof','changed count digest','wrong case index','raw native outcome only']:
        x=copy.deepcopy(prior)
        if kind=='not accepted':x['case_records'][0]['replay']['accepted']=False
        elif kind=='not complete proof':x['case_records'][0]['trace']['complete_proof']=False
        elif kind=='changed count digest':x['case_records'][0]['full_count_profile_sha256']='0'*64
        elif kind=='wrong case index':x['case_records'][0]['case_index']+=1
        else:x['case_records'][0]['outcome']='UNSAT_TRACE_PENDING_COMPLETE_REPLAY'
        bad(kind,lambda x=x:validate(u,sel,x))
    for field,value in [('ordered_case_ids',expected[::-1]),('ordered_case_ids',expected[:-1]),('ordered_case_ids',[expected[0]]*32),('skipped_verified_case_ids',sel['skipped_verified_case_ids']+[expected[0]]),('completed_proof_gate_sha256','0'*64),('authorization_record_sha256','0'*64),('unresolved_before_batch',779)]:
        x=copy.deepcopy(sel);x[field]=value;bad('selection '+field,lambda x=x:validate(u,x,prior))
    require(limits['maximum_cases']==32 and limits['first_batch_allocated_native_wall_seconds']==1920 and limits['native_wall_seconds_per_attempt']==60 and limits['conflicts_per_attempt']==1000000 and limits['address_space_bytes']==4*1024**3 and limits['proof_file_bytes']==256*1024**2 and limits['aggregate_retained_artifact_bytes']==64*1024**3 and limits['host_free_reserve_bytes']==32*1024**3 and limits['ext4_free_reserve_bytes']==2*1024**3 and not limits['automatic_resume']and not limits['automatic_retry'],'literal next32 resource controls')
    result=ns['observed_result'];outcomes=[(10,False,'s SATISFIABLE\n',0,'SAT_RAW_OBJECT_PENDING_REVIEW'),(20,False,'s UNSATISFIABLE\n',1,'UNSAT_TRACE_PENDING_COMPLETE_REPLAY'),(20,False,'s UNSATISFIABLE\n',None,'UNSAT_TRACE_UNAVAILABLE_UNKNOWN'),(124,False,'s UNKNOWN\n',50,'UNKNOWN_WALL_LIMIT'),(153,False,'',limits['proof_file_bytes'],'UNKNOWN_FILE_LIMIT_OR_FULL_TRACE_CAP'),(0,False,'c conflicts: 1,000,002 10 /s\ns UNKNOWN\n',100,'UNKNOWN_CONFLICT_LIMIT'),(137,False,'',100,'UNKNOWN_SIGNAL_OR_RESOURCE_TERMINATION'),(None,True,'',None,'OUTER_GUARD_PROCESS_STATE_UNKNOWN'),(10,False,'s UNSATISFIABLE\n',0,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'),(20,False,'s SATISFIABLE\n',1,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'),(20,False,'s UNSATISFIABLE\ns UNSATISFIABLE\n',1,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME')]
    for code,guard,stdout,size,want in outcomes:require(result(dict(actual_exit_code=code,outer_windows_guard_expired=guard),stdout,size)['interpretation']==want,'exact outcome label');controls.append(dict(name='native outcome '+str(code),expected=want,passed=True))
    calls=[]
    def capture(seconds,args,**kw):calls.append(dict(seconds=seconds,args=args,**kw));return calls[-1]
    ns['h']=SimpleNamespace(NATIVE='pinned-cadical',linux=lambda p:str(p));ns['e']=SimpleNamespace(command=capture);cmd=ns['command']('test.cnf','/tmp/proof.drat');require(cmd==dict(seconds=60,args=['pinned-cadical','--no-binary','--seed=0','-c','1000000','test.cnf','/tmp/proof.drat'],file_limit=256*1024**2),'actual command control')
    require("BATCH=None"in text and "BATCH=args.batch_summary.resolve()"in text and "'batch-summary-sha256'"in text and "'--case-id',cid"in text and 'preserved=True'not in text and "future_availability='UNKNOWN'"in text,'consolidated input/SAT/workspace ABI')
    closure={DRIVER,SPEC,A/'theory_20260930_exact_eight_campaign_spec.md'};todo=[DRIVER]
    while todo:
        p=todo.pop()
        for n in ast.walk(ast.parse(p.read_text(encoding='utf8'))):
            names=[x.name for x in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[]
            for name in names:
                q=A/f'{name}.py'
                if q.exists()and q not in closure:closure.add(q);todo.append(q)
    closure.add(A/'theory_20260930_hadamard_balanced_gram_cnf.py');require(len([p for p in closure if p.suffix=='.py'])==6,'six local runtime sources')
    files=closure|set(PINS)|{Path(__file__),A/'native_20260930_exact_eight_next32.py',A/'prepare_20260930_exact_eight_next32_native_source.py',A/'prepare_20260930_exact_eight_next32_consolidated_source.py'}
    save(OUT/'summary.json',dict(status='EXACT_EIGHT_NEXT32_NATIVE_SOURCE_PREPARATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256={key(p):sha(p)for p in sorted(files)},native_source_closure=sorted(map(key,closure)),limits=limits,seed=0,controls=controls,command_control=cmd,selected_case_ids=expected,AST_compile_only=True,runtime_repository_imports=0,preflight_calls=0,native_calls=0,independent_approval=False,unexecuted_draft_preserved=True,consolidated_build_summary_required_at_runtime=True,limitation='Static and isolated control preparation only; actual consolidated32 encoding/object gates and root preflight are mandatory before native invocation.'))
    print(json.dumps(dict(driver_sha256=sha(DRIVER),spec_sha256=sha(SPEC),summary_sha256=sha(OUT/'summary.json'),controls=len(controls),native_source_closure=sorted(map(key,closure)))))
if __name__=='__main__':
    try:main()
    except BaseException as ex:
        if OUT.is_dir()and not(OUT/'failure.json').exists():save(OUT/'failure.json',dict(error=repr(ex),source_sha256=sha(Path(__file__)),native_calls=0,preflight_calls=0))
        raise

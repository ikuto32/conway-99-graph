"""AST and isolated engineering controls only; no native wrapper imports/calls."""
import ast,copy,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';B=A/'results'
DRIVER=A/'native_20260930_exact_eight_explicit_batch.py';SPEC=DRIVER.with_name(DRIVER.stem+'_spec.md')
OUT=B/'20260930_exact_eight_explicit_native_preparation'
UNIVERSE=B/'20260930_exact_eight_campaign_preparation/campaign_manifest.json'
SELECTION=B/'20260930_exact_eight_sizeclass16_selection/selection.json'
BUILD=B/'20260930_exact_eight_sizeclass16_cnfs/summary.json'
PINS={DRIVER:'5362d31514a4e8bc0458c345f5324e776946b819cf7e5e89c09c20c3e1626169',UNIVERSE:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',SELECTION:'9e8bb4c4347cd90d1f6a61f7a6cbdde4bc3a6d86fbb3307cc9015b0b53f20b06',BUILD:'5d6c7359b09f233979e8a7563c9b615d9e7e9d905bab39d8a5b173f74c82d6d4'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def require(x,m):
    if not x:raise ValueError(m)
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    OUT.mkdir(exist_ok=False);text=DRIVER.read_text(encoding='utf8');tree=ast.parse(text);compile(text,str(DRIVER),'exec');controls=[]
    for p,w in PINS.items():require(sha(p)==w,'frozen source/control input '+key(p))
    ns=dict(re=re,Path=Path,ROOT=ROOT,UNIVERSE=UNIVERSE,PINS=PINS,h=SimpleNamespace(require=require,key=key))
    names={'allocation_seconds','validate_selection','selection_authorization','observed_result','command'}
    nodes=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='LIMITS'for t in n.targets)or isinstance(n,ast.FunctionDef)and n.name in names]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<isolated controls only>','exec'),ns)
    limits=ns['LIMITS'];allocation=ns['allocation_seconds'];validate=ns['validate_selection'];authorize=ns['selection_authorization'];u=read(UNIVERSE);sel=read(SELECTION);built=read(BUILD)
    def good(name,test):
        require(test,name);controls.append(dict(name=name,passed=True))
    def bad(name,fn):
        try:fn()
        except(ValueError,KeyError,IndexError,AssertionError,TypeError):controls.append(dict(name=name,rejected=True));return
        raise ValueError('malformed control accepted '+name)
    actual=validate(u,sel);auth,authsha=authorize(sel)
    good('actual sizeclass16 selection ordered members',actual==sel['ordered_case_ids']and len(actual)==16 and allocation(len(actual))==960)
    good('literal authorization hash',sha(auth)==authsha)
    good('actual complete16 build receipt matches explicit selection',built['selected_case_ids']==actual==[r['case_id']for r in built['records']]and built['completed_formulas']==16 and not built['pending_case_ids']and built['native_calls']==0 and built['inputs_sha256'][key(SELECTION)]==PINS[SELECTION])
    allids=[r['case_id']for r in u['records']]
    allocations=[]
    for n in range(1,65):
        x=copy.deepcopy(sel);x['ordered_case_ids']=allids[:n];x['selected_instances']=n
        good('synthetic ordered boundary/count '+str(n),validate(u,x)==allids[:n]and allocation(n)==60*n);allocations.append(dict(selected=n,seconds=allocation(n)))
    x=copy.deepcopy(sel);x['ordered_case_ids']=actual[::-1]
    good('preserves explicit caller order without reselecting',validate(u,x)==actual[::-1])
    for n in [0,65,-1,True,1.0,'1',None]:bad('invalid allocation '+repr(n),lambda n=n:allocation(n))
    modifications=[('ordered_case_ids',[]),('ordered_case_ids',allids[:65]),('ordered_case_ids',[actual[0]]*16),('ordered_case_ids',['not-a-case']),('ordered_case_ids',tuple(actual)),('ordered_case_ids',[None]),('campaign_manifest_path','acceleration/wrong.json'),('campaign_manifest_sha256','0'*64),('selection_reason','  '),('selection_reason',None),('schema','wrong'),('selected_instances',17)]
    for field,value in modifications:
        x=copy.deepcopy(sel);x[field]=value;bad('selection '+field+' '+str(value)[:50],lambda x=x:validate(u,x))
    for field,value in [('historical_profiles_subtracted',True),('prior_exclusions_used',True),('universe_size',791)]:
        x=copy.deepcopy(u);x[field]=value;bad('population '+field,lambda x=x:validate(x,sel))
    x=copy.deepcopy(u);x['records'][0]['case_id']=x['records'][1]['case_id'];bad('duplicated population member',lambda:validate(x,sel))
    for field,value in [('authorization_record_path','../outside.md'),('authorization_record_path',str(auth)),('authorization_record_path','acceleration/nonexistent-authorization.md'),('authorization_record_sha256','abc'),('authorization_record_sha256','G'*64)]:
        x=copy.deepcopy(sel);x[field]=value;bad('authorization '+field,lambda x=x:authorize(x))
    good('literal generic resource limits',limits['maximum_cases']==64 and limits['native_wall_seconds_per_attempt']==60 and limits['conflicts_per_attempt']==1000000 and limits['address_space_bytes']==4*1024**3 and limits['proof_file_bytes']==256*1024**2 and limits['aggregate_retained_artifact_bytes']==64*1024**3 and limits['host_free_reserve_bytes']==32*1024**3 and limits['ext4_free_reserve_bytes']==2*1024**3 and not limits['automatic_resume']and not limits['automatic_retry'])
    result=ns['observed_result'];outcomes=[(10,False,'s SATISFIABLE\n',0,'SAT_RAW_OBJECT_PENDING_REVIEW'),(20,False,'s UNSATISFIABLE\n',1,'UNSAT_TRACE_PENDING_COMPLETE_REPLAY'),(20,False,'s UNSATISFIABLE\n',None,'UNSAT_TRACE_UNAVAILABLE_UNKNOWN'),(124,False,'s UNKNOWN\n',50,'UNKNOWN_WALL_LIMIT'),(153,False,'',limits['proof_file_bytes'],'UNKNOWN_FILE_LIMIT_OR_FULL_TRACE_CAP'),(0,False,'c conflicts: 1,000,002 10 /s\ns UNKNOWN\n',100,'UNKNOWN_CONFLICT_LIMIT'),(137,False,'',100,'UNKNOWN_SIGNAL_OR_RESOURCE_TERMINATION'),(None,True,'',None,'OUTER_GUARD_PROCESS_STATE_UNKNOWN'),(10,False,'s UNSATISFIABLE\n',0,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'),(20,False,'s SATISFIABLE\n',1,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'),(20,False,'s UNSATISFIABLE\ns UNSATISFIABLE\n',1,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'),(20,False,'s UNSATISFIABLE\ns SATISFIABLE\n',1,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME')]
    for code,guard,stdout,size,want in outcomes:good('outcome '+str(code)+' '+want,result(dict(actual_exit_code=code,outer_windows_guard_expired=guard),stdout,size)['interpretation']==want)
    calls=[]
    def capture(seconds,args,**kw):calls.append(dict(seconds=seconds,args=args,**kw));return calls[-1]
    ns['h']=SimpleNamespace(NATIVE='pinned-cadical',linux=lambda p:str(p));ns['e']=SimpleNamespace(command=capture);cmd=ns['command']('test.cnf','/tmp/proof.drat')
    good('isolated command seed/conflict/wall/file limits',cmd==dict(seconds=60,args=['pinned-cadical','--no-binary','--seed=0','-c','1000000','test.cnf','/tmp/proof.drat'],file_limit=256*1024**2))
    good('parameterized CLI SAT and workspace protocol',all(s in text for s in ["BATCH=args.batch_summary.resolve();SELECTION=args.selection.resolve()","'selection-sha256'","'batch-summary-sha256'","'--case-id',cid","future_availability='UNKNOWN'","allocated_limit=allocation_seconds(len(selection))"])and 'preserved=True'not in text and 'first_batch_allocated_native_wall_seconds'not in text)
    good('explicit next32 path/case count removed','20260930_exact_eight_next32'not in text and "'maximum_cases':32"not in text)
    closure={DRIVER,SPEC,A/'theory_20260930_exact_eight_campaign_spec.md'};todo=[DRIVER]
    while todo:
        p=todo.pop()
        for n in ast.walk(ast.parse(p.read_text(encoding='utf8'))):
            names=[x.name for x in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[]
            for name in names:
                q=A/f'{name}.py'
                if q.exists()and q not in closure:closure.add(q);todo.append(q)
    closure.add(A/'theory_20260930_hadamard_balanced_gram_cnf.py')
    good('six local runtime Python sources plus two specs',len([p for p in closure if p.suffix=='.py'])==6 and len(closure)==8)
    files=closure|set(PINS)|{auth,Path(__file__),A/'native_20260930_exact_eight_next32_v2.py',A/'native_20260930_exact_eight_next32_v2_spec.md',A/'prepare_20260930_exact_eight_explicit_native_source.py'}
    save(OUT/'summary.json',dict(status='EXACT_EIGHT_EXPLICIT_NATIVE_SOURCE_PREPARATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256={key(p):sha(p)for p in sorted(files)},native_source_closure=sorted(map(key,closure)),limits=limits,seed=0,controls=controls,allocations=allocations,command_control=cmd,control_selection=key(SELECTION),control_selected_case_ids=actual,AST_compile_only=True,runtime_repository_imports=0,preflight_calls=0,native_calls=0,new_formula_builds=0,independent_approval=False,limitation='Static/isolated preparation only. Genuine sizeclass16 selection/build are input-identity controls, not a separate proof or formula review. Fresh per-batch encoding/object gates and root preflight remain mandatory.'))
    print(json.dumps(dict(driver_sha256=sha(DRIVER),spec_sha256=sha(SPEC),summary_sha256=sha(OUT/'summary.json'),controls=len(controls),native_source_closure=sorted(map(key,closure)))))
if __name__=='__main__':
    try:main()
    except BaseException as ex:
        if OUT.is_dir()and not(OUT/'failure.json').exists():save(OUT/'failure.json',dict(error=repr(ex),source_sha256=sha(Path(__file__)),native_calls=0,preflight_calls=0))
        raise

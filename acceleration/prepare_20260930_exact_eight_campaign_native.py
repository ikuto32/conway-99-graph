"""Static/isolated controls only. Never imports the native driver or invokes native tools."""
import ast,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];DRIVER=ROOT/'acceleration/native_20260930_exact_eight_campaign.py';SPEC=DRIVER.with_name(DRIVER.stem+'_spec.md');OUT=ROOT/'acceleration/results/20260930_exact_eight_campaign_native_preparation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def main():
    OUT.mkdir(exist_ok=False);text=DRIVER.read_text();tree=ast.parse(text);compile(text,str(DRIVER),'exec')
    limits_node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='LIMITS'for t in n.targets));ns={'dict':dict};exec(compile(ast.Module(body=[limits_node],type_ignores=[]),'<isolated constants>','exec'),ns);limits=ns['LIMITS']
    assert limits['proof_file_bytes']==256*1024**2 and limits['address_space_bytes']==4*1024**3 and limits['aggregate_retained_artifact_bytes']==64*1024**3 and limits['host_free_reserve_bytes']==32*1024**3 and limits['ext4_free_reserve_bytes']==2*1024**3 and not limits['automatic_resume']and not limits['automatic_retry']
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='observed_result');ns={'re':re,'LIMITS':limits};exec(compile(ast.Module(body=[node],type_ignores=[]),'<isolated outcome parser>','exec'),ns);fn=ns['observed_result'];checks=[]
    cases=[(10,False,'s SATISFIABLE\n',0,'SAT_RAW_OBJECT_PENDING_REVIEW'),(20,False,'s UNSATISFIABLE\n',100,'UNSAT_TRACE_PENDING_COMPLETE_REPLAY'),(20,False,'s UNSATISFIABLE\n',None,'UNSAT_TRACE_UNAVAILABLE_UNKNOWN'),(124,False,'s UNKNOWN\n',50,'UNKNOWN_WALL_LIMIT'),(153,False,'',limits['proof_file_bytes'],'UNKNOWN_FILE_LIMIT_OR_FULL_TRACE_CAP'),(0,False,'c conflicts: 1,000,002 10 /s\ns UNKNOWN\n',100,'UNKNOWN_CONFLICT_LIMIT'),(137,False,'',100,'UNKNOWN_SIGNAL_OR_RESOURCE_TERMINATION'),(None,True,'',None,'OUTER_GUARD_PROCESS_STATE_UNKNOWN'),(10,False,'s UNSATISFIABLE\n',0,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'),(20,False,'s SATISFIABLE\n',1,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'),(20,False,'s UNSATISFIABLE\ns UNSATISFIABLE\n',1,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'),(0,False,'s UNKNOWN\n',0,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME')]
    for code,guard,stdout,size,want in cases:
        got=fn(dict(actual_exit_code=code,outer_windows_guard_expired=guard),stdout,size);assert got['interpretation']==want;(checks.append(dict(exit_code=code,outer_guard=guard,stdout=stdout,trace_bytes=size,result=got)))
    cmd_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='command');calls=[]
    def capture(seconds,args,**kwargs):calls.append(dict(seconds=seconds,args=args,**kwargs));return calls[-1]
    ns={'e':SimpleNamespace(command=capture),'h':SimpleNamespace(NATIVE='pinned-cadical',linux=lambda x:str(x)),'LIMITS':limits};exec(compile(ast.Module(body=[cmd_node],type_ignores=[]),'<isolated command>','exec'),ns);got=ns['command']('test.cnf','/tmp/test.drat')
    assert got==dict(seconds=60,args=['pinned-cadical','--no-binary','--seed=0','-c','1000000','test.cnf','/tmp/test.drat'],file_limit=256*1024**2)
    assert 'resume-checkpoint'not in text and 'preserved=True'not in text and "future_availability='UNKNOWN'"in text and "'--case-id',cid"in text
    closure={DRIVER,SPEC,ROOT/'acceleration/theory_20260930_exact_eight_campaign_spec.md'};todo=[DRIVER]
    while todo:
        p=todo.pop();t=ast.parse(p.read_text())
        for n in ast.walk(t):
            names=[x.name for x in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[]
            for name in names:
                q=ROOT/'acceleration'/f'{name}.py'
                if q.exists()and q not in closure:closure.add(q);todo.append(q)
    closure.add(ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py');assert len([p for p in closure if p.suffix=='.py'])==6
    seed=ROOT/'acceleration/results/20260930_native_cli_calibration/native_full_help.stdout.log';assert sha(seed)=='4958e610188eb62780aceb78bb466b98fb265dfd4c16553150a6b4c4aadd5c08';assert '--seed=0..2e9              random seed [0]'in seed.read_text()
    inputs=closure|{seed,Path(__file__),ROOT/'acceleration/theory_20260930_exact_eight_campaign_plan.md',ROOT/'acceleration/results/20260930_exact_eight_first12_cnfs/summary.json',ROOT/'acceleration/results/20260930_exact_eight_campaign_preparation/campaign_manifest.json'}
    result=dict(status='EXACT_EIGHT_CAMPAIGN_NATIVE_SOURCE_PREPARATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256={key(p):sha(p)for p in sorted(inputs)},native_source_closure=sorted(map(key,closure)),AST_compile_only=True,outcome_controls=checks,command_control=got,limits=limits,actual_seed=0,seed_evidence_line='--seed=0..2e9 random seed [0]',runtime_repository_imports=0,preflight_calls=0,native_calls=0,independent_approval=False,limitations=['Isolated synthetic parser/command controls and source inspection only.','The first12 aggregate object calibration and root native engineering review are separate.','No automatic resume; verified independent outcome gates are required before a separately planned continuation skips completed attempts.'])
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(dict(driver_sha256=sha(DRIVER),spec_sha256=sha(SPEC),summary_sha256=sha(OUT/'summary.json'),native_source_closure=sorted(map(key,closure)))))
if __name__=='__main__':main()

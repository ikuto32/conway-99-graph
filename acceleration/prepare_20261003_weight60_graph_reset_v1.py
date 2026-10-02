"""Producer-only graph reset derivative and unlaunched SAME-V2 warm protocol.

Validates old objects, preserves ordered current triples, and explicitly resets
configuration/RNG/counters. This is not continuation of the old RNG trajectory.
"""
import argparse,copy,hashlib,itertools,json,math,platform,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
BASE='43175e0a96ed4abbf6b03e16b67adff6f6f40b20'
SOURCE='acceleration/results/20261002_hypergraph_weight60_pilot01/native/final.state'
SOURCE_SHA='0dc37fdc2dd58fb78f55b88fd8e2ee7c43a83d32d1cc7897591151d5aca6a1bb'
AUDIT='acceleration/results/20261003_independent_review/weight60_pilot01/summary.json'
AUDIT_SHA='a80ec86298ce13ae8fea44c118ebbe613dd4b55e4387ac49e39ec9b3d4cd40d2'
ROOK='acceleration/results/20261002_hypergraph_weight60_controls02/rook9_positive/final.state'
ROOK_SHA='d85463e5fedfa03f62f4ef1719e2dd2198eb8f53d57139d5ad51b8daae806814'
CHECKER='acceleration/audit_20261003_weight60_reset_state_v1.py'
CHECKER_SHA='078524dd42270f10ee7ea42616101dc9d2e1e09bdfabc2ff654a2ec78655f7c8'
CHECKER_SPEC='acceleration/audit_20261003_weight60_reset_state_v1_spec.md'
CHECKER_SPEC_SHA='786db20566be2fee302ab30b288f077ba048c857676d2e5aac1ac76a6df05237'
CHECKER_CAL='acceleration/results/20261003_independent_review/weight60_reset_calibration01/summary.json'
CHECKER_CAL_SHA='5e93291da1bf0b3acecc4549a8a631e682c2a6e835e695a42a0a40cd19a17d23'
OLD_PLAN='acceleration/results/20261003_weight60_pilot_freeze01/plan.json'
OLD_PLAN_SHA='53cd5567151b9d7cf433bce0eaff80e266a4dcb4c69e99e4e1ca7f5a05a76f12'
DESIGN='docs/DESIGN_20261003_WEIGHT60_WARM_CONTINUATION_V1.md'
DESIGN_SHA='eafb38b9146c53aa621e3bc8f4f3308701571b7563b64cfad09b3e4914e314eb'
SCALARS='n degree seed mix_steps schedule_steps t_start t_end forced step admissible accepted best_updates weighted_energy base_energy lambda_energy mu_energy best_weighted_energy best_base_energy best_lambda_energy best_mu_energy'.split()
FLOATS={'t_start','t_end'};MASK=(1<<64)-1
RESET=dict(seed=99032061,mix_steps=0,schedule_steps=80000000,t_start=8.0,t_end=.1,forced=0,step=0,admissible=0,accepted=0,best_updates=0)
class ResetError(ValueError):pass
def need(ok,stage):
    if not ok:raise ResetError(stage)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')
def words(seed):
    result=[]
    for _ in range(4):
        seed=(seed+0x9e3779b97f4a7c15)&MASK;z=seed
        z=((z^(z>>30))*0xbf58476d1ce4e5b9)&MASK;z=((z^(z>>27))*0x94d049bb133111eb)&MASK
        result.append(z^(z>>31))
    return result
def graph(n,degree,triples):
    need(type(n)is int and type(degree)is int and ((n==99 and degree==7) or(n==9 and degree==2)),'DOMAIN')
    need(len(triples)==n*degree//3,'DOMAIN');a=[[0]*n for _ in range(n)];counts=[0]*n
    for t in triples:
        need(len(t)==3 and all(type(v)is int and 0<=v<n for v in t) and len(set(t))==3,'DOMAIN')
        for v in t:counts[v]+=1
        for u,v in itertools.combinations(t,2):need(a[u][v]==0,'DOMAIN');a[u][v]=a[v][u]=1
    need(counts==[degree]*n and all(sum(row)==2*degree for row in a),'DOMAIN')
    bits=[sum(x<<j for j,x in enumerate(row)) for row in a];cn=[];el=em=0
    for i in range(n):
        for j in range(i+1,n):
            c=(bits[i]&bits[j]).bit_count();cn.append(c);res=c+a[i][j]-2
            if a[i][j]:el+=res*res
            else:em+=res*res
    mismatches=sum((sum(a[i][k]*a[k][j] for k in range(n))!=(2*degree if i==j else 1 if a[i][j] else 2)) for i in range(n) for j in range(n))
    return dict(rows=a,cn=cn,lambda_energy=el,mu_energy=em,base_energy=el+em,weighted_energy=60*el+em,identity_mismatches=mismatches)
def parse(raw):
    try:tokens=raw.decode('ascii').split()
    except UnicodeDecodeError:raise ResetError('FORMAT')
    i=0
    def take():
        nonlocal i
        need(i<len(tokens),'FORMAT');value=tokens[i];i+=1;return value
    def integer():
        value=take();need(re.fullmatch(r'0|[1-9][0-9]*',value)is not None,'FORMAT');return int(value)
    def tag(name):need(take()==name,'FORMAT')
    tag('HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2');tag('objective');tag('SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2');tag('lambda_weight');tag('60');tag('move_kernel');tag('LINEAR_TRIPLE_EXCLUSIVE_SWAP_V2')
    state={}
    for name in SCALARS:
        tag(name)
        if name in FLOATS:
            try:state[name]=float(take())
            except ValueError:raise ResetError('FORMAT')
        else:state[name]=integer()
    tag('rng');state['rng']=[integer() for _ in range(4)]
    def triples(name):
        tag(name);count=integer();need(count==state['n']*state['degree']//3,'DOMAIN');return[[integer() for _ in range(3)] for _ in range(count)]
    state['current']=triples('current');state['best']=triples('best');tag('cn');count=integer();need(count==state['n']*(state['n']-1)//2,'CACHE');state['cn']=[integer() for _ in range(count)]
    tag('first_lambda0');state['first_lambda0']=integer();need(state['first_lambda0']in[0,1],'SNAPSHOT')
    if state['first_lambda0']:
        for key in ['step','admissible','accepted','best_updates']:tag('first_'+key);state['first_'+key]=integer()
        tag('first_rng');state['first_rng']=[integer() for _ in range(4)];state['first_current']=triples('first_current');state['first_best']=triples('first_best')
    tag('END');need(i==len(tokens),'FORMAT');return state
def validate(state,reset=False,source=None):
    n=state['n'];degree=state['degree'];c=graph(n,degree,state['current']);b=graph(n,degree,state['best'])
    need(all(math.isfinite(state[x]) and 0<=state[x]<=1000 for x in FLOATS) and state['schedule_steps']>0 and state['forced']in[0,1] and 0<=state['seed']<=MASK,'CONFIG')
    need(all(0<=state[x]<=MASK for x in ['step','admissible','accepted','best_updates','mix_steps','schedule_steps']),'COUNTERS')
    need(state['best_updates']<=state['accepted']<=state['admissible']<=state['step'],'COUNTERS')
    need(len(state['rng'])==4 and all(type(x)is int and 0<=x<=MASK for x in state['rng']) and any(state['rng']),'RNG')
    for key in ['lambda_energy','mu_energy','base_energy','weighted_energy']:
        need(state[key]==c[key] and state['best_'+key]==b[key],'SCORE')
    need(b['weighted_energy']<=c['weighted_energy'],'SCORE');need(state['cn']==c['cn'],'CACHE')
    need(state['first_lambda0']in[0,1] and (c['lambda_energy']!=0 or state['first_lambda0']==1),'SNAPSHOT')
    if state['first_lambda0']:
        fc=graph(n,degree,state['first_current']);fb=graph(n,degree,state['first_best'])
        need(fc['lambda_energy']==0 and fb['weighted_energy']<=fc['weighted_energy'],'SNAPSHOT')
        need(any(state['first_rng']) and all(type(x)is int and 0<=x<=MASK for x in state['first_rng']),'RNG')
        need(state['first_best_updates']<=state['first_accepted']<=state['first_admissible']<=state['first_step'] and all(state['first_'+key]<=state[key] for key in ['step','admissible','accepted','best_updates']),'SNAPSHOT')
    if reset:
        need(source is not None and all(state[key]==value for key,value in RESET.items()),'RESET')
        need(state['rng']==words(RESET['seed']),'RESET')
        need(state['current']==state['best']==state['first_current']==state['first_best']==source['current'],'RESET')
        need(state['first_lambda0']==1 and all(state['first_'+key]==0 for key in ['step','admissible','accepted','best_updates']) and state['first_rng']==state['rng'],'RESET')
    return c
def make_reset(source):
    obj=graph(source['n'],source['degree'],source['current']);need(obj['lambda_energy']==0,'RESET_SOURCE_LAMBDA')
    state=dict(n=source['n'],degree=source['degree'],**RESET,rng=words(RESET['seed']),current=copy.deepcopy(source['current']),best=copy.deepcopy(source['current']),cn=obj['cn'],first_lambda0=1)
    for key in ['weighted_energy','base_energy','lambda_energy','mu_energy']:state[key]=state['best_'+key]=obj[key]
    for key in ['step','admissible','accepted','best_updates']:state['first_'+key]=0
    state['first_rng']=list(state['rng']);state['first_current']=copy.deepcopy(source['current']);state['first_best']=copy.deepcopy(source['current']);return state
def serialize(state):
    lines=['HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2','objective SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V2','lambda_weight 60','move_kernel LINEAR_TRIPLE_EXCLUSIVE_SWAP_V2']
    for key in SCALARS:lines.append(key+' '+(format(state[key],'.17g') if key in FLOATS else str(state[key])))
    lines.append('rng '+' '.join(map(str,state['rng'])))
    for key in ['current','best']:
        lines.append(key+' '+str(len(state[key])));lines.extend(' '.join(map(str,t)) for t in state[key])
    lines.append('cn '+str(len(state['cn'])));lines.extend(map(str,state['cn']));lines.append('first_lambda0 '+str(state['first_lambda0']))
    if state['first_lambda0']:
        for key in ['step','admissible','accepted','best_updates']:lines.append('first_'+key+' '+str(state['first_'+key]))
        lines.append('first_rng '+' '.join(map(str,state['first_rng'])))
        for key in ['first_current','first_best']:
            lines.append(key+' '+str(len(state[key])));lines.extend(' '.join(map(str,t)) for t in state[key])
    return ('\n'.join(lines+['END'])+'\n').encode('ascii')
def reject(call,stage):
    try:call()
    except ResetError as error:need(str(error)==stage,'CONTROL_WRONG_STAGE');return stage
    raise ResetError('CONTROL_MISSING_VETO')
def controls(out,fixture):
    validate(fixture);need(graph(9,2,fixture['current'])['identity_mismatches']==0 and fixture['rng']==words(fixture['seed']),'KNOWN_ROOK_RNG_IDENTITY')
    reset=make_reset(fixture);validate(reset,True,fixture);need(parse(serialize(reset))==reset,'SERIALIZED_ROUNDTRIP');(out/'rook9_source.state').write_bytes(serialize(fixture));(out/'rook9_reset.state').write_bytes(serialize(reset))
    negatives=[]
    changes=[('duplicate_triple','DOMAIN',lambda s:s['current'].__setitem__(1,list(s['current'][0]))),('score','SCORE',lambda s:s.__setitem__('weighted_energy',1)),('cache','CACHE',lambda s:s['cn'].__setitem__(0,s['cn'][0]+1)),('counter','COUNTERS',lambda s:s.__setitem__('accepted',1)),('zero_rng','RNG',lambda s:s.__setitem__('rng',[0,0,0,0])),('config','CONFIG',lambda s:s.__setitem__('t_start',-1.0)),('reset_seed','RESET',lambda s:s.__setitem__('seed',99032062)),('reset_rng','RESET',lambda s:s['rng'].__setitem__(0,s['rng'][0]^1)),('first_rng','RESET',lambda s:s['first_rng'].__setitem__(0,s['first_rng'][0]^1))]
    for label,stage,mutate in changes:
        bad=copy.deepcopy(reset);mutate(bad);save(out/(label+'.json'),bad);negatives.append(dict(label=label,expected_stage=stage,actual_stage=reject(lambda:validate(bad,True,fixture),stage)))
    broken=serialize(reset).replace(b'HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2',b'WRONG_STATE',1);(out/'wrong_format.state').write_bytes(broken);negatives.append(dict(label='wrong_format',expected_stage='FORMAT',actual_stage=reject(lambda:parse(broken),'FORMAT')))
    report=dict(status='PRODUCER_WEIGHT60_GRAPH_RESET_V1_CALIBRATION_COMPLETE',positive_generic_rook9_objects=2,strict_negative_controls=negatives,independent_approval=False,scope='Own finite producer controls; not target99 approval or engine execution approval.');save(out/'summary.json',report);return report
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--seconds',type=float,required=True);a=p.parse_args()
    deadline=CommandDeadline(a.seconds,allocation_reason='Frozen explicit graph-only V2 reset derivative and draft warm plan; knownvalid/corrupt controls before actual derivative100worker20reserve no nativecall')
    out=a.out.resolve();need(out.is_relative_to(ROOT),'OUTPUT');out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(name,wanted):
        need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'NOT_COMPLETED_WITHIN_ALLOCATED_BUDGET');need(sha(ROOT/name)==wanted,'PIN');pins[name]=wanted;return json.loads((ROOT/name).read_bytes()) if name.endswith('.json') else None
    try:
        for name,digest in [(SOURCE,SOURCE_SHA),(ROOK,ROOK_SHA),(CHECKER,CHECKER_SHA),(CHECKER_SPEC,CHECKER_SPEC_SHA),(DESIGN,DESIGN_SHA)]:pin(name,digest)
        report=pin(AUDIT,AUDIT_SHA);cal=pin(CHECKER_CAL,CHECKER_CAL_SHA);old=pin(OLD_PLAN,OLD_PLAN_SHA)
        need(report['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_PASS' and report['inputs_sha256'][SOURCE]==SOURCE_SHA,'SOURCE_AUDIT')
        need(cal['status']=='INDEPENDENT_WEIGHT60_GRAPH_ONLY_RESET_CALIBRATION_V1_PASS' and cal['inputs_sha256'][CHECKER]==CHECKER_SHA,'PREOUTPUT_CHECKER_CALIBRATION')
        need(old['source_commit']==BASE and old['lambda_weight']==60,'UNCHANGED_BASE')
        reusable={}
        wanted_paths=[x for x in old['inputs_sha256'] if x in ['acceleration/prepare_20261002_hypergraph_weight60_v2.py','acceleration/hypergraph_weight60_anneal_20261002_v2.cpp','acceleration/prepare_20261002_hypergraph_weight60_v2_spec.md','acceleration/design_20261002_hypergraph_weight60_v2.md','acceleration/plan_20261002_hypergraph_weight60_engineering_v2.json','acceleration/plan_20261002_hypergraph_weight60_correction_v2.json','acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/native_budget_env_v1/pyproject.toml','acceleration/native_budget_env_v1/uv.lock','acceleration/results/20261002_hypergraph_weight60_build02/hypergraph_weight60_anneal','acceleration/results/20261002_hypergraph_weight60_build02/build_manifest.json']]
        need(len(wanted_paths)==12,'UNCHANGED_CLOSURE_POPULATION')
        for name in wanted_paths:
            digest=old['inputs_sha256'][name];pin(name,digest);blob=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT);need(hashlib.sha256(blob).hexdigest()==digest,'UNCHANGED_COMMITTED_ENGINE');reusable[name]=digest
        for name in ['acceleration/results/20261002_independent_review/weight60_controls01/summary.json','acceleration/results/20261003_independent_review/weight60_saved_calibration03/summary.json']:pin(name,old['inputs_sha256'][name])
        controls_dir=out/'controls';controls_dir.mkdir();fixture=parse((ROOT/ROOK).read_bytes());calibration=controls(controls_dir,fixture)
        source=parse((ROOT/SOURCE).read_bytes());validate(source);reset=make_reset(source);obj=validate(reset,True,source);need((obj['lambda_energy'],obj['mu_energy'],obj['weighted_energy'],obj['identity_mismatches'])==(0,3608,3608,4934),'ACTUAL_SOURCE_COMPONENTS')
        reset_path=out/'reset.state';reset_path.write_bytes(serialize(reset));need(parse(reset_path.read_bytes())==reset,'ACTUAL_SERIALIZED_ROUNDTRIP')
        (out/'reset_current.adj').write_text(str(reset['n'])+'\n'+'\n'.join(''.join(map(str,row)) for row in obj['rows'])+'\n',encoding='ascii',newline='\n')
        sourcekey=Path(__file__).resolve().relative_to(ROOT).as_posix();pins[sourcekey]=sha(Path(__file__));spec=sourcekey.replace('.py','_spec.md');pins[spec]=sha(ROOT/spec)
        artifacts={x.relative_to(ROOT).as_posix():dict(sha256=sha(x),bytes=x.stat().st_size) for x in out.rglob('*') if x.is_file()}
        summary=dict(status='WEIGHT60_GRAPH_ONLY_RESET_V1_OUTPUT_PENDING_INDEPENDENT_CHECK',timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',source_commit=BASE,observed_git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            source_state=dict(path=SOURCE,sha256=SOURCE_SHA,selected='ordered_current',old_seed=source['seed'],old_step=source['step'],old_first_lambda0_step=source['first_step']),
            reset_state=dict(path=reset_path.relative_to(ROOT).as_posix(),sha256=sha(reset_path)),parameters=RESET,reset_rng=reset['rng'],components={k:obj[k] for k in ['lambda_energy','mu_energy','weighted_energy','base_energy','identity_mismatches']},
            inputs_sha256=pins,artifacts=artifacts,reusable_engine_hashes=reusable,pre_output_independent_checker=dict(path=CHECKER,sha256=CHECKER_SHA,calibration=CHECKER_CAL,calibration_sha256=CHECKER_CAL_SHA),
            producer_calibration=dict(path=(controls_dir/'summary.json').relative_to(ROOT).as_posix(),sha256=sha(controls_dir/'summary.json'),positive_generic_rook9_objects=2,strict_negative_controls=len(calibration['strict_negative_controls'])),
            uncommitted_derivative_closure=[dict(path=name,sha256=digest,reason='New engineering adapter/reset artifact source or saved graph object/report; exact identities separate from committed unchanged engine') for name,digest in pins.items() if name not in reusable],
            interface_limitation='Unchanged wrapper graphimport supports only frozen oldweight6pilot. Native resume uses checkpoint config, so resettingCLIflags alone would not work. This explicit stepzero derivative uses existing --resume with newconfig/RNG/counters, not oldtrajectory continuation.',
            shared_components=['V2 serialized format and splitmix64 seed expansion are shared with unchanged native engine; same Python integer and deadline runtime.','Producer bitset CN scorer is not independent validation; ROOT dense checker was calibrated before output and must check every derivative object.'],
            independent_approval=False,scientific_launched=False,target_resolution=False,limitations=['Reset derivative is CANDIDATE pending ROOT full dense audit.','Original savedcurrent/best/firstlambda0/RNG/counters remain immutable; newfirstlambda0 snapshot is initial step0 of newgraphreset.','No graph normalization, trajectory equivalence, performance or target certificate.'])
        save(out/'summary.json',summary)
        cmd=list(old['command']);science_out='acceleration/results/20261003_hypergraph_weight60_warm01';outer='acceleration/results/20261003_hypergraph_weight60_warm_supervision01'
        for flag in ['--import-weight6','--import-weight6-sha256','--import-select']:
            i=cmd.index(flag);del cmd[i:i+2]
        def setting(flag,value):i=cmd.index(flag);cmd[i+1]=str(value)
        for flag,value in [('--seed',99032061),('--temperature-start',8)]:setting(flag,value)
        cmd=[outer if x=='acceleration/results/20261002_hypergraph_weight60_pilot_supervision01' else science_out if x=='acceleration/results/20261002_hypergraph_weight60_pilot01' else x for x in cmd]
        indices=[i for i,x in enumerate(cmd) if x=='--allocation-reason'];cmd[indices[0]+1]='Exactlyone SAME V2 graph-onlyreset warm100m seed99032061 T8to.1/80m mix0; previous100m239.7native seconds;600outer550worker450guard445cooperative, no retries or throughput guarantee.';cmd[indices[1]+1]='Newindependentlychecked stepzero graphreset through existingresume; sameV2F60/binary/wrapper, seed61 T8to.1/80m100m mix0;450guard445cooperative2GiBAS1GiBfile.'
        setting('--success-criterion','Complete100millionproposals or orderlycheckpoint; independentlychecked savedlambda0 graph withmu<3608 is comparablepartial improvement; preserve current/best/initial firstlambda0/rawmatrices/RNG/counters; anyzero full99validator.')
        setting('--verification-criterion','ROOT exactreset derivative pass and frozen calibrated unchangedengine/savedchecker; differentauthor full savedobjects/literal99 matrix outcome audit, sparsehistory unknown; no ownapproval or targetcoverage.')
        cmd+=['--resume',reset_path.relative_to(ROOT).as_posix(),'--resume-sha256',sha(reset_path)]
        plan=dict(schema='PROSPECTIVE_SAME_V2_GRAPH_RESET_WARM_COMMAND_V1',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=BASE,observed_git_head=summary['observed_git_head'],command=cmd,cwd=str(ROOT),source_state=summary['source_state'],reset_state=summary['reset_state'],reset_producer_report=dict(path=(out/'summary.json').relative_to(ROOT).as_posix(),sha256=sha(out/'summary.json')),pre_output_checker=summary['pre_output_independent_checker'],
            independent_reset_report=None,independent_reset_report_reason='Not produced yet; exact ROOT full derivative report/pass must be appended in a new immutable final preflight plan before launch.',
            parameters=dict(seed=99032061,proposals=100000000,temperature_start=8,temperature_end=.1,cooling_proposals=80000000,mix_steps=0,lambda_weight=60,forced=False),allocation=old['allocation'],reusable_engine_hashes=reusable,
            scientific_launched=False,launch_admission=['ROOT independent derivative report PASS binds exact source/reset/producer hashes and pre-output calibration.','Exactengine/wrapper/binary/gates and all savedchecker dependency closure remain unchanged and committed; newadapter/source/output closure published or explicitly pinned separately.','ROOT reviews exact final frozencommand/hash with fresh source/resource/emptyworker observations.','Default science UID1000 and supported insideLinux supervisor; no retry/extensions.'],
            interface='Existing --resume consumes explicitly graph-reset stepzero V2 record. It is not old RNG/counter/config continuation; original rawstate andfirstlambda0 remain evidence.',success='Compare exact E_mu among independentlychecked SAVEDlambda0 objects to baseline3608; F60 alone orlower ordinaryEwithpositive lambda does not satisfy this criterion.',
            limitations=['No complete trajectory checking from sparse moves; better unsaved lambda0 graphs cannot be inferred.','Firstlambda0 in this run is input atstep0; original firststep29380701 is historical saved evidence, earliestselection still UNKNOWN.','Warmcommand is not executable approval before ROOT derivative/finalpreflight review.','No target coverage denominator, exclusions or normalization certificate.'])
        save(out/'warm_plan_draft.json',plan);print(json.dumps(dict(reset_state_sha256=sha(reset_path),summary_sha256=sha(out/'summary.json'),plan_sha256=sha(out/'warm_plan_draft.json'),scientific_launched=False)))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),timestamp=datetime.now(timezone.utc).isoformat(),scientific_launched=False));raise
if __name__=='__main__':main()

"""Independent weight60 V2 saved-object/scalar/sparse-trace endpoint checks V3.

Saved snapshots are fully checked; sparse missing trajectory segments remain
unknown. An earliest first-lambda0 claim needs complete replay, not this receipt.
"""
import argparse
import copy
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
from command_deadline import CommandDeadline
import audit_20261002_weight60_scalar_v1 as C

ROOT=Path(__file__).resolve().parents[1]
GATE='acceleration/results/20261002_independent_review/weight60_controls01/summary.json'
GATE_SHA='05a8c1e5b0d2df3d937cd1ab47961b17ff37ec2f3d9952a5db0feaf5178ac9f3'
CONFIG=('objective','lambda_weight','move_kernel','n','degree','seed','mix_steps','schedule_steps','t_start','t_end','forced')
COUNTERS=('step','admissible','accepted','best_updates')
FIELDS={'trace_schema','move_kernel','step','ti','tj','pi','pj','old_triples','proposed_triples','disjoint','new_pairs_absent','selected_points_exclusive','new_pairs_absent_after_old_removal','admissible','accepted','mixing','temperature','objective','lambda_weight','delta','weighted_energy_before','weighted_energy_after','lambda_energy_before','mu_energy_before','lambda_energy_after','mu_energy_after','best_weighted_energy','first_lambda0_before','first_lambda0_after','first_lambda0_step','draw','rng_before','rng_after'}


def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')


def safe(name):
    C.need(type(name)is str and name and '\\'not in name,'canonical POSIX repository path','IDENTITY');p=(ROOT/name).resolve();C.need(p.is_relative_to(ROOT)and p.relative_to(ROOT).as_posix()==name,'literal repository path','IDENTITY');return p


def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()


def linux(name):return'/mnt/c/'+str(safe(name))[3:].replace('\\','/')


def local_path(name):
    prefix=linux('acceleration')[:-len('acceleration')]
    return name[len(prefix):]if name.startswith(prefix)else name


def options(values):
    result={};at=0
    while at<len(values):
        name=values[at];at+=1;C.need(name.startswith('--')and name not in result,'unique native options','RECEIPT')
        if name in['--forced','--stop-at-zero','--emit-pair-costs']:result[name]=True
        else:C.need(at<len(values),'option value','RECEIPT');result[name]=values[at];at+=1
    return result


def scalar_matrix(matrix,n,k,deadline=None):
    if type(matrix)is not list or len(matrix)!=n or any(type(row)is not list or len(row)!=n for row in matrix):return dict(domain_valid=False,srg_valid=False,reason='shape',ordered_entries_checked=0)
    if any(type(v)is not int or v not in[0,1]for row in matrix for v in row):return dict(domain_valid=False,srg_valid=False,reason='binary',ordered_entries_checked=0)
    columns=list(zip(*matrix));errors=[];mismatches=[];adj=Counter();nonadj=Counter();el=em=0
    for u,row in enumerate(matrix):
        if deadline is not None:C.need(not deadline.status()['stop_required'],'not completed within the allocated budget','DEADLINE')
        if row[u]!=0 or sum(row)!=k:errors.append(['diagonal_degree',u])
        for v,col in enumerate(columns):
            if row[v]!=matrix[v][u]:errors.append(['symmetry',u,v])
            actual=sum(a*b for a,b in zip(row,col));expected=k if u==v else 2-row[v]
            if actual!=expected:mismatches.append([u,v,actual,expected])
            if u<v:
                if row[v]:el+=(actual-1)**2;adj[actual]+=1
                else:em+=(actual-2)**2;nonadj[actual]+=1
    return dict(domain_valid=not errors,srg_valid=not errors and not mismatches,domain_errors=len(errors),identity_mismatches=len(mismatches),examples=mismatches[:8],ordered_entries_checked=n*n,lambda_energy=el,mu_energy=em,base_energy=el+em,weighted_energy=60*el+em,adjacent_pairs=sum(adj.values()),nonadjacent_pairs=sum(nonadj.values()),adjacent_cn_histogram={str(v):adj[v]for v in sorted(adj)},nonadjacent_cn_histogram={str(v):nonadj[v]for v in sorted(nonadj)},arithmetic='Exact complete Python scalar row-column integer multiplication',parameters=[n,k,1,2])


def object_check(s,deadline):
    reports={}
    for selector in['current','best']:
        bits,_,score=C.score(s[selector],s['n'],s['degree']);matrix=[[int(bits[u]>>v&1)for v in range(s['n'])]for u in range(s['n'])];report=scalar_matrix(matrix,s['n'],2*s['degree'],deadline)
        C.need(report['domain_valid']and report['ordered_entries_checked']==s['n']**2 and all(report[k]==score[k]==s[('best_'if selector=='best'else'')+k]for k in C.KEYS),'independent scalar full square versus fullgraph/state components','MATRIX')
        reports[selector]=report
    return reports


def target_zero(matrix,claimed):
    C.need(type(claimed)is int and claimed==0,'exact integer zero claim','TARGET_ZERO');report=scalar_matrix(matrix,99,14);C.need(report['srg_valid']and report['ordered_entries_checked']==9801,'complete99 exact SRG identity','TARGET_ZERO');return report


def local_trace(record,initial):
    C.need(type(record)is dict and set(record)==FIELDS,'complete literal V2 fields','LOCAL_TRACE')
    C.need(record['trace_schema']=='HYPERGRAPH_WEIGHT60_MOVE_V2'and record['move_kernel']==C.KERNEL,'fixed V2 trace/kernel','KERNEL');C.need(record['objective']==C.OBJECTIVE and type(record['lambda_weight'])is int and record['lambda_weight']==60,'fixed60 local weight','WEIGHT')
    for name in['step','ti','tj','pi','pj','delta','weighted_energy_before','weighted_energy_after','lambda_energy_before','mu_energy_before','lambda_energy_after','mu_energy_after','best_weighted_energy']:C.need(type(record[name])is int,'exact integer '+name,'LOCAL_TRACE')
    size=len(initial['current']);C.need(record['step']>=0 and 0<=record['ti']<size and 0<=record['tj']<size and record['ti']!=record['tj']and record['pi']in range(3)and record['pj']in range(3),'bounded indices','LOCAL_TRACE')
    for name in['disjoint','new_pairs_absent','selected_points_exclusive','new_pairs_absent_after_old_removal','admissible','accepted','mixing','first_lambda0_before','first_lambda0_after']:C.need(type(record[name])is bool,'exact boolean '+name,'LOCAL_TRACE')
    for name in['old_triples','proposed_triples']:C.need(type(record[name])is list and len(record[name])==2 and all(type(t)is list and len(t)==3 and all(type(v)is int and 0<=v<initial['n']for v in t)for t in record[name]),'local literal triples','LOCAL_TRACE')
    t,q=record['old_triples'];C.need(len(set(t))==len(set(q))==3 and len(set(t)&set(q))<=1,'local linear distinct old lines','LOCAL_TRACE');pt=t[:];pq=q[:];pt[record['pi']],pq[record['pj']]=q[record['pj']],t[record['pi']]
    exclusive=t[record['pi']]not in q and q[record['pj']]not in t
    C.need(record['proposed_triples']==[pt,pq]and record['disjoint']==(not bool(set(t)&set(q)))and record['selected_points_exclusive']==exclusive and record['admissible']==(exclusive and record['new_pairs_absent_after_old_removal']),'local exact selected-point predicate','LOCAL_TRACE')
    if exclusive and not record['disjoint']:C.need(not record['new_pairs_absent'],'shared incoming pairs were previously present','LOCAL_TRACE')
    for suffix in['before','after']:
        el,em=record['lambda_energy_'+suffix],record['mu_energy_'+suffix];C.need(el>=0 and em>=0 and record['weighted_energy_'+suffix]==60*el+em,'exact local category decomposition','COMPONENT')
    C.need(0<=record['best_weighted_energy']<=record['weighted_energy_after'],'local best/order','COMPONENT')
    for field in['rng_before','rng_after']:C.need(type(record[field])is list and len(record[field])==4 and all(type(v)is str for v in record[field]),'literal four-word decimal RNG arrays','LOCAL_RNG')
    before=[C.U.natural(v,'LOCAL_RNG')for v in record['rng_before']];after=[C.U.natural(v,'LOCAL_RNG')for v in record['rng_after']]
    C.need(len(before)==len(after)==4 and all(0<=v<=C.U.M for v in before+after)and any(before)and any(after),'local bounded nonzero RNG','LOCAL_RNG')
    words=before[:];ti=C.U.rng_next(words)%size;tj=C.U.rng_next(words)%(size-1)
    if tj>=ti:tj+=1
    pi=C.U.rng_next(words)%3;pj=C.U.rng_next(words)%3;draw=C.U.rng_next(words)if record['admissible']else 0
    C.need([ti,tj,pi,pj]==[record[k]for k in['ti','tj','pi','pj']]and words==after and type(record['draw'])is str and str(draw)==record['draw'],'exact local RNG transition','LOCAL_RNG')
    temp=initial['t_start']+(initial['t_end']-initial['t_start'])*min(1,float(max(0,record['step']-initial['mix_steps']))/initial['schedule_steps'])
    C.need(type(record['temperature'])in[int,float]and math.isfinite(record['temperature'])and abs(record['temperature']-temp)<=C.U.TOL,'scheduled temperature tolerance','LOCAL_TEMPERATURE');C.need(record['mixing']==(record['step']<initial['mix_steps']),'mixingstage','LOCAL_TRACE')
    expected=False
    if record['admissible']:
        if initial['forced']or record['mixing']or record['delta']<=0:expected=True
        elif temp>0:
            threshold=math.exp(-float(record['delta'])/temp);uniform=(draw>>11)/2**53;C.need(abs(uniform-threshold)>C.U.TOL,'local acceptance margin','FLOAT');expected=uniform<threshold
    C.need(record['accepted']==expected,'local recorded acceptance','LOCAL_TRACE')
    if record['accepted']:C.need(record['weighted_energy_after']-record['weighted_energy_before']==record['delta'],'accepted local weighted delta','COMPONENT')
    else:C.need(all(record[k+'_after']==record[k+'_before']for k in['weighted_energy','lambda_energy','mu_energy']),'rejected local score rollback','COMPONENT')
    if not record['admissible']:C.need(record['delta']==0 and record['draw']=='0','invalid local zero delta/draw','LOCAL_TRACE')
    C.need(not record['first_lambda0_before']or record['first_lambda0_after'],'first selection retained','LOCAL_FIRST')
    if not record['first_lambda0_before']:
        C.need(record['first_lambda0_after']==(record['lambda_energy_after']==0),'local first observation flag','LOCAL_FIRST')
        if record['first_lambda0_after']:C.need(record['first_lambda0_step']==record['step']+1,'first completed step','LOCAL_FIRST')
    C.need((type(record['first_lambda0_step'])is int and 0<=record['first_lambda0_step']<=record['step']+1)if record['first_lambda0_after']else record['first_lambda0_step']is None,'local snapshot step/null','LOCAL_FIRST')


def trace_population(records,start,end,maximum,stride):
    chosen=set(range(start,min(end,start+maximum)))
    if stride:chosen.update(range(((start+stride-1)//stride)*stride,end,stride))
    C.need([r['step']for r in records]==sorted(chosen),'complete frozen sparse trace selection','POPULATION')


def anchored(records,initial,by_step,deadline):
    frontier=None;checked=[];unknown=[]
    for record in records:
        C.need(not deadline.status()['stop_required'],'not completed within the allocated budget','DEADLINE');local_trace(record,initial)
        if frontier is not None and frontier['step']==record['step']:state=frontier
        elif record['step']in by_step:state=copy.deepcopy(by_step[record['step']])
        else:unknown.append(record['step']);frontier=None;continue
        C.replay(state,record);checked.append(record['step']);frontier=state
        if state['step']in by_step:C.need(state==by_step[state['step']],'next anchored complete saved state','ANCHOR')
    return checked,unknown


def run(args):
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='New fixed60/overlap persistent-first saved-object/scalar/sparse checker; finite calibration120outer100worker or fullendpoint evidence-based allocation');out=safe(args.out);out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(name,wanted=None,size=None):
        C.need(not deadline.status()['stop_required']and deadline.status()['remaining_seconds']>20,'not completed within the allocated budget','DEADLINE');p=safe(name);C.need(p.is_file(),'artifact exists','IDENTITY');actual=sha(p);C.need(wanted is None or actual==wanted,'exact hash '+name,'IDENTITY');C.need(size is None or size==p.stat().st_size,'exact byte count','IDENTITY');pins[name]=actual;return p
    def read(name):return json.loads(safe(name).read_bytes())
    try:
        pin(GATE,GATE_SHA);gate=read(GATE);C.need(gate['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_ANNEAL_V2_CONTROLS_PASS','fresh exact V2 engineering gate','IDENTITY')
        for p in[Path(C.__file__),Path(C.U.__file__),Path(C.W.__file__)]:pin(key(p),gate['inputs_sha256'][key(p)])
        for p in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'acceleration/audit_20261003_weight60_saved_objects_v1_spec.md',ROOT/'acceleration/audit_20261003_weight60_saved_objects_v2_spec.md',Path(C.__file__).with_name(Path(C.__file__).stem+'_spec.md'),ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(key(p))
        if args.mode=='calibrate':
            base=ROOT/'acceleration/results/20261002_hypergraph_weight60_controls02';controls=[]
            for name in['rook9_positive','target99_greedy','prism9_whole','cube12_whole']:
                raw=base/name/'initial.state';pin(key(raw),gate['inputs_sha256'][key(raw)]);s=C.parse_state(raw.read_bytes());controls.append(dict(fixture=name,full_scalar_objects=object_check(s,deadline)))
                traces=base/name/'moves.jsonl';pin(key(traces),gate['inputs_sha256'][key(traces)]);records=[json.loads(line)for line in traces.read_bytes().splitlines()][:3]
                for row in records:local_trace(row,s)
                if records:
                    completed,unknown=anchored(records,s,{s['step']:s},deadline);C.need(completed==[r['step']for r in records]and not unknown,'three complete anchored records','CONTROL')
                    for field,stage in[('move_kernel','KERNEL'),('lambda_weight','WEIGHT'),('selected_points_exclusive','LOCAL_TRACE'),('first_lambda0_after','LOCAL_FIRST')]:
                        bad=copy.deepcopy(records[0]);bad[field]=not bad[field]if type(bad[field])is bool else'OLD'if type(bad[field])is str else bad[field]+1
                        # first flag corruption can meet earlier local semantics;
                        # all other fields retain independently valid surroundings.
                        controls.append(dict(mutated_field=field,fixture=name,diagnostic=C.U.reject(lambda:local_trace(bad,s),stage)))
                    missing=records[:-1];controls.append(dict(missing_trace=C.U.reject(lambda:trace_population(missing,s['step'],s['step']+3,3,0),'POPULATION')))
                    wrong=copy.deepcopy(s);wrong['rng'][0]^=1;controls.append(dict(wrong_anchor=C.U.reject(lambda:anchored(records,s,{s['step']:wrong},deadline),'REPLAY')))
                    for field,mutation in[('rng_before',['0']*4),('rng_after',[0]*4),('rng_after',['0']*3)]:
                        bad=copy.deepcopy(records[0]);bad[field]=mutation;controls.append(dict(mutated_rng=field,fixture=name,diagnostic=C.U.reject(lambda:local_trace(bad,s),'LOCAL_RNG')))
            rook=C.parse_state((base/'rook9_positive/initial.state').read_bytes());matrix_path=base/'rook9_positive/current.adj';pin(key(matrix_path),gate['inputs_sha256'][key(matrix_path)]);matrix=C.raw_matrix(matrix_path.read_bytes(),9);controls.append(dict(scope=C.U.reject(lambda:target_zero(matrix,0),'TARGET_ZERO')))
            for kind in['loop','edge','asymmetry','binary','shape']:
                bad=copy.deepcopy(matrix)
                if kind=='loop':bad[0][0]=1
                elif kind=='edge':bad[0][1]=bad[1][0]=0
                elif kind=='asymmetry':bad[0][1]=0
                elif kind=='binary':bad[0][1]=2
                else:bad.pop()
                C.need(not scalar_matrix(bad,9,4)['srg_valid'],'changed matrix exact veto','CONTROL');controls.append(dict(corrupt_matrix=kind,rejected=True))
            for name in['prism9_whole','cube12_whole']:
                p=base/name/'first_lambda0.state';pin(key(p),gate['inputs_sha256'][key(p)]);selected=C.parse_state(p.read_bytes());controls.append(dict(first=name,complete_snapshot_scalar=object_check(selected,deadline)))
                matrix_path=base/name/'first_lambda0.adj';pin(key(matrix_path),gate['inputs_sha256'][key(matrix_path)]);first=C.raw_matrix(matrix_path.read_bytes(),selected['n']);C.matrix_matches(first,selected['current'],selected['n'],selected['degree'])
                if name=='cube12_whole':C.need(scalar_matrix(first,12,4)['lambda_energy']==0 and scalar_matrix(first,12,4)['mu_energy']==48,'partial lambda0 fullscalar control','CONTROL');controls.append(dict(partial_lambda0_target=C.U.reject(lambda:target_zero(first,0),'TARGET_ZERO')))
            save(out/'controls.json',dict(controls=controls,known_valid_target99_fixture=None,null_reason='No known targetgraph; generic rook/prism and full99valid domain nonSRG controls only.'))
            result=dict(status='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_CALIBRATION_PASS',inputs_sha256=pins,controls=len(controls),scope='Changed60weight/overlap state/firstselection/scalar/sparse checker calibration only, no scientific endpoint or native scientific calls.',new_native_calls=0,target_resolution=False)
        else:
            C.need(args.run_summary and args.run_summary_sha256 and args.calibration and args.calibration_sha256,'exact endpoint/pre-output calibration hashes','IDENTITY');source_pins=dict(pins);pin(args.calibration,args.calibration_sha256);cal=read(args.calibration);C.need(cal['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_CALIBRATION_PASS'and all(cal['inputs_sha256'].get(k)==v for k,v in source_pins.items()),'unchanged complete source/helper/preoutput calibration closure','IDENTITY')
            pin(args.run_summary,args.run_summary_sha256);summary=read(args.run_summary);base=safe(args.run_summary).parent;protocol_name=key(base/'protocol.json');invocation_name=key(base/'invocation.json');pin(protocol_name);pin(invocation_name);protocol,invocation=read(protocol_name),read(invocation_name)
            C.need(summary['status']=='HYPERGRAPH_WEIGHT60_RESEARCH_OUTPUT_PENDING_INDEPENDENT_SAVED_STATE_CHECK'and summary['target_resolution']is False and summary['independent_approval']is False and protocol['inputs_sha256']==summary['inputs_sha256']and protocol['objective']==C.OBJECTIVE and protocol['lambda_weight']==60,'exact unapproved research scope/source','RECEIPT')
            for name,wanted in summary['inputs_sha256'].items():pin(name,wanted)
            for name,wanted in invocation['inputs_sha256'].items():C.need(summary['inputs_sha256'].get(name)==wanted,'same invocation closure','IDENTITY')
            for name in['acceleration/prepare_20261002_hypergraph_weight60_v2.py','acceleration/hypergraph_weight60_anneal_20261002_v2.cpp','acceleration/prepare_20261002_hypergraph_weight60_v2_spec.md','acceleration/design_20261002_hypergraph_weight60_v2.md','acceleration/plan_20261002_hypergraph_weight60_engineering_v2.json','acceleration/plan_20261002_hypergraph_weight60_correction_v2.json','acceleration/command_deadline.py','acceleration/run_compute_command.py','acceleration/native_budget_env_v1/pyproject.toml','acceleration/native_budget_env_v1/uv.lock','acceleration/results/20261002_hypergraph_weight60_build02/hypergraph_weight60_anneal','acceleration/results/20261002_hypergraph_weight60_build02/build_manifest.json']:C.need(summary['inputs_sha256'].get(name)==gate['inputs_sha256'].get(name),'new engine gate exact CODE closure','IDENTITY')
            C.need(summary['inputs_sha256'].get(GATE)==GATE_SHA,'exact native admission gate','IDENTITY')
            outer=protocol['supervision'];pin(outer['path'],outer['sha256']);om=read(outer['path']);osname=str(Path(outer['path']).parent/'summary.json').replace('\\','/');pin(osname);os=read(osname)
            C.need(om['invocation_id']==os['invocation_id']==outer['invocation_id']and 0<om['seconds']<=21600 and om['automatic_retry']is False and om['cumulative_across_commands']is False and os['command_exit_code']==0 and os['cleanup']['reaped']is True and os['cleanup']['job_active_zero_observed']is True and os['cleanup']['process_group_live_pids']==[]and os['cleanup']['cleanup_errors']==[],'actual complete contained endpoint','RECEIPT')
            C.need(outer['guard_argv'][:2]==['/usr/bin/timeout','--signal=KILL']and outer['guard_argv'][3:5]==['/usr/bin/env','UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv']and outer['guard_argv'][5:9]==['/root/.local/bin/uv','run','--locked','--offline'],'actual Linux hard guard and locked runtime','RECEIPT')
            row=summary['run'];pin(row['receipt'],row['receipt_sha256']);receipt=read(row['receipt'])
            for channel in['stdout','stderr']:pin(receipt[channel],receipt[channel+'_sha256'])
            C.need(receipt['actual_exit_code']==row['actual_exit_code']==receipt['expected_exit_code']==0 and receipt['reaped']is True and receipt['process_group']==outer['group']and row['options']==protocol['options']and receipt['command'][14:]==row['options'],'native exact command/outcome/inputs','RECEIPT')
            opts=options(row['options']);C.need(opts['--fixture']=='target99'and opts.get('--stop-at-zero')is True,'scientific full99scope','RECEIPT');native=base/'native';C.need({key(p)for p in native.iterdir()if p.is_file()}==set(row['artifacts']),'complete saved output population','POPULATION')
            command=receipt['command'];C.need(command[:4]==['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s']and command[4].endswith('s'),'exact native GNU guard syntax','RECEIPT');seconds=float(command[4][:-1]);C.need(math.isfinite(seconds)and 0<seconds<=outer['producer_seconds'],'shared native guard allocation','RECEIPT')
            expected=['/usr/bin/prlimit',f"--as={invocation['address_space_bytes']}:{invocation['address_space_bytes']}",f"--fsize={invocation['file_bytes']}:{invocation['file_bytes']}",'--core=0:0',linux('acceleration/results/20261002_hypergraph_weight60_build02/hypergraph_weight60_anneal'),'--out',linux(key(native)),'--seconds',f'{max(.001,seconds-5):.6f}']
            C.need(command[5:14]==expected and receipt['cwd']==linux('acceleration')[:-len('/acceleration')],'exact gatedbinary/output/resources/workingdirectory','RECEIPT')
            for name,item in row['artifacts'].items():pin(name,item['sha256'],item['bytes'])
            states={};object_reports=[];configs=None;zero=[]
            for p in sorted(native.glob('*.state')):
                s=C.parse_state(p.read_bytes());C.need((s['n'],s['degree'])==(99,7),'complete targetdomain saved graph','DOMAIN');reports=object_check(s,deadline);object_reports.append(dict(path=key(p),step=s['step'],objects=reports))
                if p.name=='first_lambda0.state':continue
                C.need(p.name in['initial.state','final.state']or p.name=='checkpoint_'+str(s['step'])+'.state','exact completed-step statefilename','POPULATION')
                if s['step']in states:C.need(states[s['step']]==s,'duplicate complete saved-step equality','CHECKPOINT')
                states[s['step']]=s
                if configs is None:configs={k:s[k]for k in CONFIG}
                C.need(all(s[k]==configs[k]for k in CONFIG),'fixed exact saved config','CHECKPOINT')
                for selector in['current','best']:
                    if reports[selector]['weighted_energy']==0:
                        bits=C.score(s[selector],99,7)[0];matrix=[[int(bits[u]>>v&1)for v in range(99)]for u in range(99)];zero.append(dict(path=key(p),selector=selector,full_target=target_zero(matrix,0),pending_external_review=True))
            initial=C.parse_state((native/'initial.state').read_bytes());final=C.parse_state((native/'final.state').read_bytes());ordered=[states[j]for j in sorted(states)];C.need(ordered[0]==initial and ordered[-1]==final,'complete saved initial/final range','CHECKPOINT')
            for before,after in zip(ordered,ordered[1:]):
                C.need(all(before[k]<=after[k]for k in COUNTERS)and before['best_weighted_energy']>=after['best_weighted_energy'],'monotone observed saved counters/best','CHECKPOINT')
                if before['first']is not None:C.need(before['first']==after['first'],'immutable retained first snapshot','FIRST_SNAPSHOT')
            interval=int(opts['--checkpoint-every']);C.need(set(range(((initial['step']//interval)+1)*interval,final['step']+1,interval))<=set(states),'every scheduled integer checkpoint present','POPULATION')
            if '--resume'in opts:
                original=local_path(opts['--resume']);pin(original,summary['inputs_sha256'][original]);C.need(safe(original).read_bytes()==(native/'initial.state').read_bytes(),'complete exact resume bytes','RESUME')
            elif '--import-weight6'in opts:
                original=local_path(opts['--import-weight6']);pin(original,summary['inputs_sha256'][original]);C.import_initial(initial,safe(original).read_bytes(),opts['--import-select'],opts)
            else:C.config(initial,opts);C.need(initial['current']==initial['best']==C.initial('target99')and initial['rng']==C.U.seed_words(int(opts['--seed']))and all(initial[k]==0 for k in COUNTERS),'fresh exact initialization','INITIAL')
            for selector in['current','best']:
                matrix=C.raw_matrix((native/(selector+'.adj')).read_bytes(),99);C.matrix_matches(matrix,final[selector],99,7)
            C.selection(final,initial,opts,read(key(native/'lambda0_selection.json')))
            if final['first']is not None:
                first=C.parse_state((native/'first_lambda0.state').read_bytes());C.need(first==C.first_state(final),'complete first exported state/config/scores/RNG/counters','FIRST_SNAPSHOT');C.matrix_matches(C.raw_matrix((native/'first_lambda0.adj').read_bytes(),99),first['current'],99,7)
                for s in states.values():
                    if s['first']is not None:C.need(s['first']==final['first'],'same exact first snapshot in all savedstates','FIRST_SNAPSHOT')
            else:C.need(not(native/'first_lambda0.state').exists()and not(native/'first_lambda0.adj').exists(),'missingselection has no first exports','FIRST_COMPLETENESS')
            result=read(key(native/'result.json'));facts=dict(objective=C.OBJECTIVE,lambda_weight=60,n=99,point_degree=7,triple_count=231,starting_step=initial['step'],ending_step=final['step'],proposals_this_invocation=final['step']-initial['step'],admissible_total=final['admissible'],accepted_total=final['accepted'],best_updates_total=final['best_updates'],first_lambda0_found=final['first']is not None,first_lambda0_step=None if final['first']is None else final['first']['step'],target_resolution=False,independent_approval=False)
            for prefix,s,isbest in[('initial',initial,False),('current',final,False),('best',final,True)]:
                for k in C.KEYS:facts[prefix+'_'+k]=s[('best_'if isbest else'')+k]
            C.need(all(result[k]==v for k,v in facts.items())and result['proposals_this_invocation']<=int(opts['--steps'])and result['stop_reason']in['REQUESTED_STEPS_COMPLETE','ALLOCATED_NATIVE_BUDGET_REACHED','RAW_ZERO_PENDING_INDEPENDENT_SRG_VALIDATOR']and 0<=result['elapsed_seconds']<=receipt['wall_seconds'],'raw result exact saved-object consistency','RESULT')
            C.need(safe(receipt['stderr']).read_bytes()==b''and safe(receipt['stdout']).read_bytes()==f"NATIVE_RESULT_PRESERVED 99 {final['weighted_energy']} {final['best_weighted_energy']}\n".encode('ascii'),'exact native success logs','RECEIPT')
            records=[json.loads(line)for line in(native/'moves.jsonl').read_bytes().splitlines()];trace_population(records,initial['step'],final['step'],int(opts['--trace-max']),int(opts['--trace-stride']));replayed,unknown=anchored(records,initial,states,deadline)
            save(out/'object_checks.json',dict(all_saved_objects=object_reports,target_zero_candidates=zero,raw_current_best_first_matrices_complete=True,first_snapshot_integrity=True,first_selection_earliest_over_entire_trajectory=False,earliest_null_reason='Sparse trace intervals are unobserved; complete checkpoint snapshot integrity does not prove absence of earlierlambda0.'))
            save(out/'sparse_trace_checks.json',dict(selected_records=len(records),full_anchored_proposals=len(replayed),unanchored_steps=unknown,full_trajectory_checked=False,limitation='Unanchored records check recorded local fields/RNG/component/config only. Full graph admissibility/actualdelta/earliestcapture unknown through unlogged gaps.'))
            result=dict(status='INDEPENDENT_HYPERGRAPH_WEIGHT60_SAVED_OBJECTS_V2_PASS',inputs_sha256=pins,saved_main_steps=len(states),saved_state_files=len(object_reports),complete_integer_saved_current_best_objects=2*len(object_reports),final_current_diagnostics=object_check(final,deadline)['current'],final_best_diagnostics=object_check(final,deadline)['best'],first_lambda0_found=final['first']is not None,first_lambda0_step=None if final['first']is None else final['first']['step'],first_graph_diagnostics=None if final['first']is None else object_check(C.first_state(final),deadline)['current'],first_selection_earliest_full_trajectory=False,sparse_records=len(records),full_anchored_proposals=len(replayed),unanchored_records=len(unknown),native_observed_counters={k:final[k]for k in COUNTERS},target_zero_candidates=len(zero),target_resolution=False,new_native_calls=0,scope='Complete saved99point graphs/state/CN/fullscalar component checks and immutable selectedsnapshot integrity; sparse full-anchor replay only. No complete history/counter/earliestselection/exhaustivecoverage claim.')
        result.update(timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',verifier='/root/structural',command=[sys.executable,*sys.argv],cwd=str(ROOT),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),tool_versions=dict(python=platform.python_version(),platform=platform.platform()),outputs_sha256={p.name:sha(p)for p in out.iterdir()if p.is_file()},elapsed_seconds=time.monotonic()-start,deadline=deadline.status());save(out/'summary.json',result)
    except Exception as error:save(out/'failure.json',dict(status='INDEPENDENT_CHECK_FAILED',error=repr(error),inputs_sha256=pins,elapsed_seconds=time.monotonic()-start,target_resolution=False));raise


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=['calibrate','check']);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',required=True);ap.add_argument('--run-summary');ap.add_argument('--run-summary-sha256');ap.add_argument('--calibration');ap.add_argument('--calibration-sha256');run(ap.parse_args())

"""Saved-object checking via independently authored helpers; no producer imports.

This adapter author also authored the annealer producer. Its own executions are
preliminary, never independent approval. Another agent must review/execute it and
own any scientific verification record. No complete sparse-trajectory claim.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, copy, hashlib, json, math, platform, subprocess, sys, time
from command_deadline import CommandDeadline
import audit_20261002_hypergraph_controls_v2 as independent

ROOT=Path(__file__).resolve().parents[1]
GATE='acceleration/results/20261002_independent_review/hypergraph_controls02/summary.json'
GATE_SHA='81aa0427d80d66b45ae48d47cea98c02de02bc4ae096d5a0bcc688d6df2bacb3'
HELPER_SHA='0084ee10f2833b57a5fc8928718e8457e216fd88f6aebdc0686c34ef3d7171ac'
HELPER_SPEC_SHA='9e08c7d0c800cc853c078380e4f03df2dc8d50439962c739a7670cc972be5bde'
CONFIG=('n','degree','seed','mix_steps','schedule_steps','t_start','t_end','forced')
COUNTERS=('step','admissible','accepted','best_updates')
FIELDS={'step','ti','tj','pi','pj','old_triples','proposed_triples','disjoint','new_pairs_absent',
        'admissible','accepted','mixing','temperature','delta','energy_before','energy_after','best_energy',
        'draw','rng_before','rng_after'}


def need(value,message):
    if not value:raise ValueError(message)


def stamp():return datetime.now(timezone.utc).isoformat()


def safe(name):
    need(isinstance(name,str) and name and '\\' not in name,'literal POSIX repository path')
    p=(ROOT/name).resolve();need(p.is_relative_to(ROOT) and p.relative_to(ROOT).as_posix()==name,'canonical repository path')
    return p


def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()


def linux(name):
    path=str(safe(name)).replace('\\','/')
    return '/mnt/'+path[0].lower()+path[2:] if len(path)>2 and path[1]==':' else path


def recorded_repository_path(value):
    prefix=str(ROOT.resolve()).replace('\\','/')
    if len(prefix)>2 and prefix[1]==':':prefix='/mnt/'+prefix[0].lower()+prefix[2:]
    if value.startswith(prefix+'/'):return value[len(prefix)+1:]
    safe(value)
    return value


def tick(deadline):
    s=deadline.status();need(not s['stop_required'] and s['remaining_seconds']>20,'not completed within allocated budget')


def sha(path,deadline):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024**2),b''):tick(deadline);h.update(b)
    return h.hexdigest()


def pin(name,pins,deadline,wanted=None,size=None):
    p=safe(name);need(p.is_file(),'raw artifact exists: '+name)
    digest=sha(p,deadline);need(wanted is None or digest==wanted,'exact SHA256: '+name)
    need(size is None or p.stat().st_size==size,'exact byte count: '+name)
    need(name not in pins or pins[name]==digest,'unchanged artifact pin: '+name);pins[name]=digest
    return p


def read(name):return json.loads(safe(name).read_bytes())


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')


def authority(pins,deadline):
    pin(GATE,pins,deadline,GATE_SHA);gate=read(GATE)
    need(gate['status']=='INDEPENDENT_HYPERGRAPH_ANNEAL_V1_CONTROLS_PASS','finite independent control gate')
    helper=Path(independent.__file__).resolve();spec=helper.with_name(helper.stem+'_spec.md')
    pin(key(helper),pins,deadline,HELPER_SHA);pin(key(spec),pins,deadline,HELPER_SPEC_SHA)
    need(gate['inputs_sha256'][key(helper)]==HELPER_SHA and gate['inputs_sha256'][key(spec)]==HELPER_SPEC_SHA,'gate binds separately authored helpers')
    for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',ROOT/'pyproject.toml',ROOT/'uv.lock']:
        pin(key(p),pins,deadline)
    return gate


def dense(adj):return [[int(v in adj[u])for v in range(len(adj))]for u in range(len(adj))]


def matrix_check(matrix,n,k,deadline=None):
    """Separate scalar matrix product; generic lambda1/mu2 fixture or target."""
    if type(matrix) is not list or len(matrix)!=n or any(type(row) is not list or len(row)!=n for row in matrix):
        return dict(domain_valid=False,srg_valid=False,reason='shape',ordered_entries_checked=0)
    if any(type(x) is not int or x not in [0,1]for row in matrix for x in row):
        return dict(domain_valid=False,srg_valid=False,reason='nonbinary',ordered_entries_checked=0)
    errors=[];identity=[];energy=0
    for u in range(n):
        if deadline is not None:tick(deadline)
        if matrix[u][u]!=0:errors.append(['diagonal',u])
        if sum(matrix[u])!=k:errors.append(['degree',u,sum(matrix[u])])
        for v in range(n):
            if matrix[u][v]!=matrix[v][u]:errors.append(['asymmetry',u,v])
            common=sum(matrix[u][w]*matrix[w][v] for w in range(n))
            expected=(k-2 if u==v else 0)-matrix[u][v]+2
            if common!=expected:identity.append([u,v,common,expected])
            if u<v:energy+=(common+matrix[u][v]-2)**2
    return dict(domain_valid=not errors,domain_error_count=len(errors),domain_examples=errors[:8],
                exact_pair_residual_energy=energy,srg_valid=not errors and not identity,
                identity_mismatch_count=len(identity),identity_examples=identity[:8],ordered_entries_checked=n*n,
                parameters=[n,k,1,2],arithmetic='Python integer scalar matrix multiplication')


def raw_matrix(data,n):
    lines=data.decode('ascii').splitlines()
    need(lines and lines[0]==str(n) and len(lines)==n+1,'raw adjacency exact dimensions/header')
    need(all(len(row)==n and set(row)<=set('01')for row in lines[1:]),'raw adjacency literal binary rows')
    return [[int(x)for x in row]for row in lines[1:]]


def export_matrix(path,matrix):
    with path.open('x',encoding='ascii',newline='\n') as f:
        f.write(str(len(matrix))+'\n');f.writelines(''.join(map(str,r))+'\n'for r in matrix)


def target_zero(matrix,claimed_energy,deadline=None):
    need(type(claimed_energy) is int and claimed_energy==0,'target candidate exact zero claim')
    report=matrix_check(matrix,99,14,deadline)
    need(report['srg_valid'] and report['ordered_entries_checked']==9801,'full99 integer SRG identity veto')
    return report


def rejection(label,call):
    try:call()
    except (ValueError,UnicodeError) as error:return dict(label=label,rejected=True,diagnostic=str(error))
    raise ValueError('corrupt control accepted: '+label)


def calibrate(args,out,pins,deadline,gate):
    names=['rook9_positive','target99_greedy']
    objects={}
    for label in names:
        name='acceleration/results/20261002_hypergraph_controls01/'+label+'/initial.state'
        p=pin(name,pins,deadline,gate['inputs_sha256'][name]);objects[label]=independent.parse_state(p.read_bytes())
    rook=objects['rook9_positive'];adj,cn,e=independent.graph(rook['current'],9,2);matrix=dense(adj)
    expected=[[int(u!=v and (u//3==v//3 or u%3==v%3))for v in range(9)]for u in range(9)]
    need(matrix==expected and e==0 and matrix_check(matrix,9,4,deadline)['srg_valid'],'known rook9 exact positive')
    controls=[dict(label='known_rook9_positive',accepted=True,full_matrix=matrix_check(matrix,9,4,deadline)),
              rejection('rook9_zero_rejected_as_target99',lambda:target_zero(matrix,0,deadline))]
    for kind in ['loop','edge_flip','asymmetry','nonbinary','shape']:
        bad=copy.deepcopy(matrix)
        if kind=='loop':bad[0][0]=1
        elif kind=='edge_flip':bad[0][1]=bad[1][0]=1-bad[0][1]
        elif kind=='asymmetry':bad[0][1]=1-bad[0][1]
        elif kind=='nonbinary':bad[0][1]=2
        else:bad.pop()
        result=matrix_check(bad,9,4,deadline);need(not result['srg_valid'],'corrupt matrix veto')
        controls.append(dict(label='corrupted_matrix_'+kind,rejected=True,result=result))
    target=objects['target99_greedy'];ta,_,te=independent.graph(target['current'],99,7)
    complete=matrix_check(dense(ta),99,14,deadline)
    need(complete['domain_valid'] and complete['ordered_entries_checked']==9801 and complete['exact_pair_residual_energy']==te==19800 and not complete['srg_valid'],'full99 non-SRG positive-domain fixture')
    controls.append(dict(label='valid99_domain_nonzero_object',accepted_as_domain=True,accepted_as_srg=False,result=complete))
    controls.append(rejection('nonzero99_matrix_with_corrupt_zero_label',lambda:target_zero(dense(ta),0,deadline)))
    raw=safe('acceleration/results/20261002_hypergraph_controls01/target99_greedy/initial.state').read_text().splitlines()
    for kind in ['triple','score','cache','counter','rng']:
        lines=raw[:]
        if kind=='triple':i=next(i for i,x in enumerate(lines)if x.startswith('current '));lines[i+2]=lines[i+1]
        elif kind=='score':i=next(i for i,x in enumerate(lines)if x.startswith('energy '));lines[i]='energy 19801'
        elif kind=='cache':i=next(i for i,x in enumerate(lines)if x.startswith('cn '));lines[i+1]=str(int(lines[i+1])+1)
        elif kind=='counter':i=next(i for i,x in enumerate(lines)if x.startswith('accepted '));lines[i]='accepted 1'
        else:i=next(i for i,x in enumerate(lines)if x.startswith('rng '));lines[i]='rng 0 0 0 0'
        data=('\n'.join(lines)+'\n').encode('ascii');path=out/(kind+'_corrupt.state');path.write_bytes(data)
        controls.append(rejection('corrupted_state_'+kind,lambda:independent.parse_state(data)))
    matrix_text=('9\n'+'\n'.join(''.join(map(str,r))for r in matrix)+'\n').encode('ascii')
    need(raw_matrix(matrix_text,9)==matrix,'complete raw binary parser positive')
    controls.append(rejection('corrupt_raw_binary_character',lambda:raw_matrix(matrix_text.replace(b'010',b'020',1),9)))
    export_matrix(out/'known_rook9.adj',matrix);save(out/'controls.json',dict(controls=controls,target_valid99_fixture=None,
         target_valid99_fixture_null_reason='No independently verified99 target graph available; rook9 is a different parameter control.'))
    return dict(status='HYPERGRAPH_SAVED_OBJECT_AUDITOR_CALIBRATION_V2_PASS_PENDING_INDEPENDENT_REVIEW',
                source_author='/root/native_driver',producer_author='/root/native_driver',verifier=args.verifier,
                independent_approval=False,calibration_control_count=len(controls),helper_author='/root/checkpoint_audit',
                inputs_sha256=pins,controls=key(out/'controls.json'),controls_sha256=sha(out/'controls.json',deadline),
                same_author_limitation='Adapter/annealer producer share an author; this preliminary execution cannot independently approve scientific producer outcomes.')


def parse_options(options):
    result={};i=0
    while i<len(options):
        k=options[i];i+=1;need(k.startswith('--') and k not in result,'unique native option')
        if k in ['--forced','--stop-at-zero']:result[k]=True
        else:need(i<len(options),'native value');result[k]=options[i];i+=1
    return result


def local_trace(record,state):
    """Syntax/local RNG consistency, not validity against an unknown state."""
    need(set(record)==FIELDS,'trace fields')
    for k in ['step','ti','tj','pi','pj','delta','energy_before','energy_after','best_energy']:
        need(type(record[k]) is int,'integer trace '+k)
    need(0<=record['ti']<231 and 0<=record['tj']<231 and record['ti']!=record['tj'] and
         record['pi'] in range(3) and record['pj'] in range(3),'trace indices')
    for k in ['disjoint','new_pairs_absent','admissible','accepted','mixing']:need(type(record[k]) is bool,'boolean trace '+k)
    need(min(record[k]for k in ['energy_before','energy_after','best_energy'])>=0 and record['best_energy']<=record['energy_after'],'trace score ordering')
    for k in ['old_triples','proposed_triples']:
        need(type(record[k]) is list and len(record[k])==2 and all(type(t) is list and len(t)==3 and all(type(v)is int and 0<=v<99 for v in t)for t in record[k]),'literal trace triples')
    before=[independent.natural(x,'RNG')for x in record['rng_before']];after=[independent.natural(x,'RNG')for x in record['rng_after']]
    need(len(before)==len(after)==4 and all(0<=x<=independent.M for x in before+after),'trace uint64 RNG words')
    words=before[:];ti=independent.rng_next(words)%231;tj=independent.rng_next(words)%230
    if tj>=ti:tj+=1
    pi=independent.rng_next(words)%3;pj=independent.rng_next(words)%3
    draw=independent.rng_next(words)if record['admissible']else 0
    need((ti,tj,pi,pj)==tuple(record[k]for k in ['ti','tj','pi','pj']) and words==after and str(draw)==record['draw'],'local recorded RNG transition')
    elapsed=max(0,record['step']-state['mix_steps']);f=min(1.0,float(elapsed)/state['schedule_steps'])
    expected=state['t_start']+(state['t_end']-state['t_start'])*f
    need(type(record['temperature']) in [int,float] and math.isfinite(record['temperature']) and abs(record['temperature']-expected)<=independent.TOL,
         'trace temperature schedule')
    need(record['mixing']==(record['step']<state['mix_steps']),'trace mixing stage')


def verify(args,out,pins,deadline,gate):
    need(args.run_summary and args.run_summary_sha256 and args.calibration and args.calibration_sha256,'exact run and calibration pins')
    pin(args.calibration,pins,deadline,args.calibration_sha256);cal=read(args.calibration)
    need(cal['status']=='HYPERGRAPH_SAVED_OBJECT_AUDITOR_CALIBRATION_V2_PASS_PENDING_INDEPENDENT_REVIEW','preliminary calibration identity')
    for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),Path(independent.__file__)]:
        need(cal['inputs_sha256'][key(p)]==pins[key(p)],'calibration exact adapter/helper bytes')
    pin(args.run_summary,pins,deadline,args.run_summary_sha256);summary=read(args.run_summary);base=safe(args.run_summary).parent
    need(summary['status']=='HYPERGRAPH_RESEARCH_OUTPUT_PENDING_INDEPENDENT_SAVED_STATE_CHECK' and summary['target_resolution'] is False and summary['independent_approval'] is False,'raw scientific pending result')
    protocol_name=key(base/'protocol.json');invocation_name=key(base/'invocation.json')
    protocol=read(protocol_name);invocation=read(invocation_name);pin(protocol_name,pins,deadline);pin(invocation_name,pins,deadline)
    need(protocol['inputs_sha256']==summary['inputs_sha256'],'same scientific input closure')
    for name,digest in summary['inputs_sha256'].items():pin(name,pins,deadline,digest)
    for name,digest in invocation['inputs_sha256'].items():need(summary['inputs_sha256'].get(name)==digest,'invocation source subset')
    for name,digest in gate['inputs_sha256'].items():
        if name in summary['inputs_sha256']:need(summary['inputs_sha256'][name]==digest,'finite controls bind execution source/binary')
    required=['acceleration/prepare_20261002_hypergraph_anneal_v1.py','acceleration/hypergraph_anneal_20261002_v1.cpp',
              'acceleration/prepare_20261002_hypergraph_anneal_v1_spec.md','acceleration/command_deadline.py',
              'acceleration/run_compute_command.py','acceleration/native_budget_env_v1/pyproject.toml','acceleration/native_budget_env_v1/uv.lock',
              'acceleration/results/20261002_hypergraph_build01/hypergraph_anneal',
              'acceleration/results/20261002_hypergraph_build01/build_manifest.json']
    for name in required:need(summary['inputs_sha256'].get(name)==gate['inputs_sha256'][name],'complete exact frozen execution identity')
    need(summary['inputs_sha256'].get(GATE)==GATE_SHA,'scientific admission gate is pinned')
    outer=protocol['supervision'];pin(outer['path'],pins,deadline,outer['sha256']);outer_manifest=read(outer['path'])
    stop_name=str(Path(outer['path']).parent/'summary.json').replace('\\','/');pin(stop_name,pins,deadline);stop=read(stop_name)
    need(stop['invocation_id']==outer_manifest['invocation_id']==outer['invocation_id'] and stop['command_exit_code']==0 and stop['cleanup']['reaped']
         and stop['cleanup']['job_active_zero_observed'] and not stop['cleanup']['cleanup_errors'],'recorded completed contained producer invocation')
    need(not outer_manifest['automatic_retry'] and not outer_manifest['cumulative_across_commands'] and outer_manifest['seconds']<=21600,'fixed noncumulative invocation')
    row=summary['run'];pin(row['receipt'],pins,deadline,row['receipt_sha256']);receipt=read(row['receipt'])
    for channel in ['stdout','stderr']:pin(receipt[channel],pins,deadline,receipt[channel+'_sha256'])
    need(receipt['actual_exit_code']==row['actual_exit_code']==receipt['expected_exit_code']==0 and receipt['reaped'],'successful native result')
    need(row['options']==protocol['options'] and receipt['command'][14:]==row['options'],'raw exact native options')
    need(receipt['command'][:4]==['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s'] and receipt['command'][5]=='/usr/bin/prlimit','native contained guard profile')
    opts=parse_options(row['options']);need(opts['--fixture']=='target99' and opts.get('--stop-at-zero') is True,'full99 scientific domain')
    native_dir=base/'native';actual={key(p)for p in native_dir.iterdir()if p.is_file()}
    guard=receipt['command'][4];need(guard.endswith('s'),'native guard seconds syntax');guard_seconds=float(guard[:-1])
    need(math.isfinite(guard_seconds) and guard_seconds>0 and guard_seconds<=outer['producer_seconds'],'native allocated seconds')
    expected_middle=[f"--as={invocation['address_space_bytes']}:{invocation['address_space_bytes']}",
                     f"--fsize={invocation['file_bytes']}:{invocation['file_bytes']}",'--core=0:0',
                     linux('acceleration/results/20261002_hypergraph_build01/hypergraph_anneal'),'--out',linux(key(native_dir)),
                     '--seconds',f'{max(.001,guard_seconds-5):.6f}']
    need(receipt['command'][6:14]==expected_middle,'exact native binary/output/resource profile')
    need(actual==set(row['artifacts']),'frozen complete native file population')
    for name,descriptor in row['artifacts'].items():pin(name,pins,deadline,descriptor['sha256'],descriptor['bytes'])
    state_paths=sorted(native_dir.glob('*.state'));need(native_dir/'initial.state' in state_paths and native_dir/'final.state' in state_paths,'initial and final saved states')
    states=[];by_step={};object_checks=[];zero_checks=[]
    for p in state_paths:
        tick(deadline);s=independent.parse_state(p.read_bytes());need((s['n'],s['degree'])==(99,7),'scientific full99 state')
        if p.name.startswith('checkpoint_'):need(p.name=='checkpoint_'+str(s['step'])+'.state','checkpoint filename/step')
        else:need(p.name in ['initial.state','final.state'],'unrecognized saved state')
        if s['step'] in by_step:need(s==by_step[s['step']],'duplicate-step exact state agreement')
        by_step[s['step']]=s;states.append((p,s))
        checked={}
        for which in ['current','best']:
            adj,cn,energy=independent.graph(s[which],99,7);matrix=dense(adj);m=matrix_check(matrix,99,14,deadline)
            need(m['domain_valid'] and m['exact_pair_residual_energy']==s['energy'if which=='current'else'best_energy']==energy,'separate scalar matrix/full set energy agreement')
            if energy==0:zero_checks.append(dict(state=key(p),which=which,matrix_validation=target_zero(matrix,energy,deadline),candidate_pending_external_review=True))
            checked[which]=dict(exact_energy=energy,full_pair_counts=len(cn),integer_matrix=m)
        object_checks.append(dict(path=key(p),sha256=pins[key(p)],step=s['step'],rng_words_wellformed=True,
              counter_order_checked=True,current_cn_cache_entries_checked=4851,objects=checked))
    initial=independent.parse_state((native_dir/'initial.state').read_bytes());final=independent.parse_state((native_dir/'final.state').read_bytes())
    ordered=[by_step[step]for step in sorted(by_step)]
    need(ordered[0]==initial and ordered[-1]==final,'saved range initial/final coverage')
    for before,after in zip(ordered,ordered[1:]):
        need(all(before[k]<=after[k]for k in COUNTERS),'monotone saved counters')
        need(before['best_energy']>=after['best_energy'],'monotone saved best energy')
    need(all(all(s[k]==initial[k]for k in CONFIG)for s in ordered),'unchanged saved schedule/domain/seed')
    if '--resume' not in opts:
        need(initial['step']==initial['admissible']==initial['accepted']==initial['best_updates']==0 and initial['rng']==independent.seed_words(int(opts['--seed']))
             and initial['current']==initial['best']==independent.initial(99),'fresh exact initial graph/RNG')
        for field,option in [('seed','--seed'),('mix_steps','--mix-steps'),('schedule_steps','--schedule-steps')]:need(initial[field]==int(opts[option]),'fresh configured '+field)
        need(initial['t_start']==float(opts['--temperature-start']) and initial['t_end']==float(opts['--temperature-end']) and initial['forced']==0,'fresh temperature/forced configuration')
    else:
        original=safe(recorded_repository_path(opts['--resume']));pin(key(original),pins,deadline)
        need(original.read_bytes()==(native_dir/'initial.state').read_bytes(),'exact restored checkpoint bytes')
    result=read(key(native_dir/'result.json'))
    facts=dict(objective='SRG_SQUARED_PAIR_RESIDUAL_V1',n=99,point_degree=7,triple_count=231,
        initial_energy=initial['energy'],current_energy=final['energy'],best_energy=final['best_energy'],starting_step=initial['step'],ending_step=final['step'],
        proposals_this_invocation=final['step']-initial['step'],admissible_total=final['admissible'],accepted_total=final['accepted'],best_updates_total=final['best_updates'],
        target_resolution=False,independent_approval=False)
    need(all(result[k]==v for k,v in facts.items()),'native result matches exact saved scalar objects')
    need(result['proposals_this_invocation']<=int(opts['--steps']) and result['stop_reason'] in ['REQUESTED_STEPS_COMPLETE','ALLOCATED_NATIVE_BUDGET_REACHED','RAW_ZERO_PENDING_INDEPENDENT_SRG_VALIDATOR'],'native stopping scope')
    need(0<=result['elapsed_seconds']<=receipt['wall_seconds'],'native observed timing boundary')
    raw_matrices={}
    for which in ['current','best']:
        adj,_,_=independent.graph(final[which],99,7);matrix=dense(adj);p=native_dir/(which+'.adj')
        if p.exists():need(raw_matrix(p.read_bytes(),99)==matrix,'raw '+which+' matrix matches final triples');raw_matrices[which]=dict(path=key(p),sha256=pins[key(p)],availability='LOCAL_ONLY',literal_binary_matrix_checked=True)
        else:raw_matrices[which]=dict(path=None,path_null_reason='Frozen producer v1 exports best.adj only; current adjacency is exactly reconstructed from final labelled triples.',availability='MISSING')
        exported=out/('checked_final_'+which+'.adj');export_matrix(exported,matrix)
        raw_matrices[which]['independently_reconstructed_export']=key(exported);raw_matrices[which]['export_sha256']=sha(exported,deadline)
    need(raw_matrices['best']['availability']=='LOCAL_ONLY','required saved best raw matrix')
    records=[json.loads(line)for line in (native_dir/'moves.jsonl').read_text().splitlines()]
    start,end=initial['step'],final['step'];maximum=int(opts['--trace-max']);stride=int(opts['--trace-stride'])
    expected=set(range(start,min(end,start+maximum)))
    if stride:expected.update(range(((start+stride-1)//stride)*stride,end,stride))
    need([r['step']for r in records]==sorted(expected),'exact predeclared sparse trace selection')
    frontier=None;replayed=[];unchecked=[]
    for record in records:
        tick(deadline);local_trace(record,initial)
        if frontier is not None and frontier['step']==record['step']:state=frontier
        elif record['step'] in by_step:state=copy.deepcopy(by_step[record['step']])
        else:unchecked.append(record['step']);frontier=None;continue
        independent.replay(state,record);replayed.append(record['step']);frontier=state
        if state['step'] in by_step:need(state==by_step[state['step']],'anchored replay agrees with complete saved next state')
    save(out/'object_checks.json',dict(saved_objects=object_checks,raw_final_matrices=raw_matrices,zero_score_full99_checks=zero_checks))
    save(out/'sparse_trace_checks.json',dict(records=len(records),selection_checked=True,all_records_local_rng_and_syntax_checked=True,
        full_proposals_replayed_from_complete_anchors=len(replayed),replayed_steps=replayed,unreplayed_sparse_steps=unchecked,
        limitations=['Unanchored records have only syntax/local RNG/schedule checks.','Gaps are not bridged by assuming producer transitions.','Saved monotone counters are not a complete independently replayed trajectory.']))
    return dict(status='HYPERGRAPH_SCIENTIFIC_SAVED_OBJECTS_V2_CHECKED_PENDING_INDEPENDENT_REVIEW',verifier=args.verifier,
        source_author='/root/native_driver',producer_author='/root/native_driver',helper_author='/root/checkpoint_audit',
        same_author_limitation='Adapter and producer share an author; native_driver execution is preliminary. Another agent must independently execute/review this path and own claim approval.',
        inputs_sha256=pins,saved_state_files=len(states),saved_unique_steps=len(by_step),
        final_current_energy=final['energy'],final_best_energy=final['best_energy'],complete_saved_object_checking=True,
        sparse_trace_records=len(records),full_anchored_proposals_replayed=len(replayed),unreplayed_sparse_records=len(unchecked),
        full_trajectory_checked=False,target_zero_candidates=len(zero_checks),target_resolution=False,independent_approval=False,
        raw_final_matrices=raw_matrices,native_counters_observed={k:final[k]for k in COUNTERS},
        native_counters_limitation='Syntax/order/monotonicity and native result agreement checked; whole-trajectory counts not independently replayed.',
        outputs_sha256={p.name:sha(p,deadline)for p in out.iterdir()if p.is_file()},
        limitations=['No exhaustive coverage or search-space connectedness assertion.','Score objective/domain differs from fixed-core factor Gram searches.',
                     'A target-zero matrix is internally checked but still requires independent additional path/external review.','No currently running process inferred from historical receipts.'])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=['calibrate','verify'])
    ap.add_argument('--out',required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--allocation-reason',required=True)
    ap.add_argument('--verifier',required=True)
    for name in ['run-summary','calibration']:ap.add_argument('--'+name);ap.add_argument('--'+name+'-sha256')
    args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason=args.allocation_reason);out=safe(args.out);out.mkdir(parents=True,exist_ok=False)
    pins={}
    try:
        gate=authority(pins,deadline)
        result=dict(calibrate=calibrate,verify=verify)[args.mode](args,out,pins,deadline,gate)
        result.update(timestamp=stamp(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),elapsed_seconds=deadline.status()['elapsed_seconds'],
            artifact_availability='LOCAL_ONLY',ledger_or_git_index_modified=False)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json',deadline))),flush=True)
    except BaseException as error:
        save(out/'failure.json',dict(timestamp=stamp(),error=repr(error),inputs_sha256=pins,verifier=args.verifier,independent_approval=False,target_resolution=False,
             outputs_preserved=True,deadline=deadline.status()));raise


if __name__=='__main__':main()

"""Independent weighted saved objects v2; complete imported helper byte closure."""
from __future__ import annotations
import argparse,copy,hashlib,json,math,platform,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
import audit_20261002_hypergraph_weighted_controls_v1 as independent

ROOT=Path(__file__).resolve().parents[1]
GATE='acceleration/results/20261002_independent_review/hypergraph_weighted_controls01/summary.json'
GATE_SHA='464a90e4093194ac59c4bdba3c19da661f7eabde52806307b37dbd33a7249f57'
HELPER_SHA='9029183c33dd05147dce44f5d295e5fe3b68caebfcc624e53d77e062d735b79a'
HELPER_SPEC_SHA='69589337884489fd22ea51f3b52ac424432a5260ad29f689ac9633de0e1355c9'
CONFIG=('objective','lambda_weight','n','degree','seed','mix_steps','schedule_steps','t_start','t_end','forced')
COUNTERS=('step','admissible','accepted','best_updates')
SCORES=('weighted_energy','base_energy','lambda_energy','mu_energy')
FIELDS={'step','ti','tj','pi','pj','old_triples','proposed_triples','disjoint','new_pairs_absent','admissible','accepted','mixing','temperature','objective','lambda_weight','delta',
        'weighted_energy_before','weighted_energy_after','lambda_energy_before','mu_energy_before','lambda_energy_after','mu_energy_after','best_weighted_energy','draw','rng_before','rng_after'}
need=independent.need;CheckError=independent.CheckError


def safe(name):
    need(isinstance(name,str) and name and '\\' not in name,'literal POSIX repository path','PATH')
    path=(ROOT/name).resolve();need(path.is_relative_to(ROOT) and path.relative_to(ROOT).as_posix()==name,'canonical repository path','PATH');return path


def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()


def linux(name):return '/mnt/c/'+str(safe(name))[3:].replace('\\','/')


def repository_path(name):
    prefix='/mnt/c/'+str(ROOT.resolve())[3:].replace('\\','/')
    if name.startswith(prefix+'/'):return name[len(prefix)+1:]
    safe(name);return name


def tick(deadline):need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'not completed within the allocated budget','DEADLINE')


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def matrix_check(matrix,n,k,deadline=None):
    """Fresh scalar row/column multiplication, independently of graph-set scorer."""
    if type(matrix) is not list or len(matrix)!=n or any(type(row) is not list or len(row)!=n for row in matrix):return dict(domain_valid=False,srg_valid=False,reason='shape',ordered_entries_checked=0)
    if any(type(value) is not int or value not in [0,1] for row in matrix for value in row):return dict(domain_valid=False,srg_valid=False,reason='nonbinary',ordered_entries_checked=0)
    errors=[];mismatches=[];el=em=0;adjacent=Counter();nonadjacent=Counter()
    columns=list(zip(*matrix))
    for u,row in enumerate(matrix):
        if deadline is not None:tick(deadline)
        if row[u]!=0:errors.append(['diagonal',u])
        if sum(row)!=k:errors.append(['degree',u,sum(row)])
        for v,column in enumerate(columns):
            if row[v]!=matrix[v][u]:errors.append(['asymmetry',u,v])
            actual=sum(a*b for a,b in zip(row,column));expected=(k if u==v else 2-row[v])
            if actual!=expected:mismatches.append([u,v,actual,expected])
            if u<v:
                if row[v]:adjacent[actual]+=1;el+=(actual-1)**2
                else:nonadjacent[actual]+=1;em+=(actual-2)**2
    return dict(domain_valid=not errors,domain_error_count=len(errors),domain_examples=errors[:8],srg_valid=not errors and not mismatches,
        identity_mismatch_count=len(mismatches),identity_examples=mismatches[:8],ordered_entries_checked=n*n,parameters=[n,k,1,2],arithmetic='Exact Python integer full scalar row-column multiplication',
        weighted_energy=6*el+em,base_energy=el+em,lambda_energy=el,mu_energy=em,adjacent_pairs=sum(adjacent.values()),nonadjacent_pairs=sum(nonadjacent.values()),
        adjacent_common_neighbor_histogram={str(c):adjacent[c] for c in sorted(adjacent)},nonadjacent_common_neighbor_histogram={str(c):nonadjacent[c] for c in sorted(nonadjacent)})


def matrix_from_sets(adj):return [[int(v in adj[u]) for v in range(len(adj))] for u in range(len(adj))]


def raw_matrix(data,n):
    lines=data.decode('ascii').splitlines();need(len(lines)==n+1 and lines[0]==str(n),'exact raw header/dimensions','RAW_MATRIX')
    need(all(len(row)==n and set(row)<=set('01') for row in lines[1:]),'literal raw binary rows','RAW_MATRIX');return [[int(x) for x in row] for row in lines[1:]]


def export_matrix(path,matrix):
    with path.open('x',encoding='ascii',newline='\n') as stream:stream.write(str(len(matrix))+'\n');stream.writelines(''.join(map(str,row))+'\n' for row in matrix)


def target_zero(matrix,claimed_F,deadline=None):
    need(type(claimed_F) is int and claimed_F==0,'exact integer weighted zero claim','TARGET_ZERO');report=matrix_check(matrix,99,14,deadline)
    need(report['srg_valid'] and report['ordered_entries_checked']==9801,'complete99 integer SRG identity','TARGET_ZERO');return report


def reject(label,call,stage,message=None):
    try:call()
    except CheckError as error:
        need(error.stage==stage and (message is None or str(error)==stage+': '+message),'exact intended negative diagnostic','CONTROL')
        return dict(label=label,rejected=True,expected_stage=stage,expected_message=message,diagnostic=str(error))
    raise CheckError('CONTROL','corrupted control accepted:'+label)


def local_trace(record,state):
    """Check conditional recorded scalars/RNG; unknown full graph remains unknown."""
    need(type(record) is dict and set(record)==FIELDS,'exact weighted trace fields','LOCAL_TRACE')
    need(record['objective']==independent.OBJECTIVE and type(record['lambda_weight']) is int and record['lambda_weight']==6,'fixed trace objective/weight','WEIGHT')
    for field in ['step','ti','tj','pi','pj','delta','weighted_energy_before','weighted_energy_after','lambda_energy_before','mu_energy_before','lambda_energy_after','mu_energy_after','best_weighted_energy']:
        need(type(record[field]) is int,'integer trace '+field,'LOCAL_TRACE')
    population=len(state['current']);n=state['n']
    need(record['step']>=0 and 0<=record['ti']<population and 0<=record['tj']<population and record['ti']!=record['tj'] and record['pi'] in range(3) and record['pj'] in range(3),'trace index bounds','LOCAL_TRACE')
    for field in ['disjoint','new_pairs_absent','admissible','accepted','mixing']:need(type(record[field]) is bool,'boolean trace '+field,'LOCAL_TRACE')
    for field in ['old_triples','proposed_triples']:need(type(record[field]) is list and len(record[field])==2 and all(type(row) is list and len(row)==3 and all(type(v) is int and 0<=v<n for v in row) for row in record[field]),'literal trace triples','LOCAL_TRACE')
    t,q=record['old_triples'];pt=t[:];pq=q[:];pt[record['pi']],pq[record['pj']]=q[record['pj']],t[record['pi']]
    need(record['proposed_triples']==[pt,pq] and record['disjoint']==(not bool(set(t)&set(q))) and record['admissible']==(record['disjoint'] and record['new_pairs_absent']),'local labelled trade facts','LOCAL_TRACE')
    for suffix in ['before','after']:
        el,em=record['lambda_energy_'+suffix],record['mu_energy_'+suffix];need(el>=0 and em>=0 and record['weighted_energy_'+suffix]==6*el+em,'local exact component decomposition','COMPONENT')
    need(0<=record['best_weighted_energy']<=record['weighted_energy_after'],'local weighted best order','COMPONENT')
    for field in ['rng_before','rng_after']:need(type(record[field]) is list and len(record[field])==4 and all(type(x) is str for x in record[field]),'trace RNG arrays','LOCAL_RNG')
    before=[independent.old.natural(x,'LOCAL_RNG') for x in record['rng_before']];after=[independent.old.natural(x,'LOCAL_RNG') for x in record['rng_after']]
    need(all(0<=word<=independent.M for word in before+after) and any(before) and any(after),'nonzero bounded local RNG','LOCAL_RNG')
    words=before[:];ti=independent.old.rng_next(words)%population;tj=independent.old.rng_next(words)%(population-1)
    if tj>=ti:tj+=1
    pi=independent.old.rng_next(words)%3;pj=independent.old.rng_next(words)%3;draw=independent.old.rng_next(words) if record['admissible'] else 0
    need((ti,tj,pi,pj)==tuple(record[k] for k in ['ti','tj','pi','pj']) and words==after and str(draw)==record['draw'],'exact local RNG transition','LOCAL_RNG')
    elapsed=max(0,record['step']-state['mix_steps']);fraction=min(1.0,float(elapsed)/state['schedule_steps']);temperature=state['t_start']+(state['t_end']-state['t_start'])*fraction
    need(type(record['temperature']) in [int,float] and math.isfinite(record['temperature']) and abs(record['temperature']-temperature)<=independent.TOL,'exact scheduled temperature tolerance','LOCAL_TEMPERATURE')
    need(record['mixing']==(record['step']<state['mix_steps']),'recorded mixing stage','LOCAL_TRACE')
    if not record['accepted']:need(record['weighted_energy_after']==record['weighted_energy_before'] and record['lambda_energy_after']==record['lambda_energy_before'] and record['mu_energy_after']==record['mu_energy_before'],'recorded rejected component rollback','COMPONENT')
    else:need(record['admissible'] and record['weighted_energy_after']-record['weighted_energy_before']==record['delta'],'recorded accepted weighted delta','COMPONENT')
    if not record['admissible']:need(record['delta']==0 and record['draw']=='0' and not record['accepted'],'invalid trade local zero facts','LOCAL_TRACE')


def trace_population(records,start,end,maximum,stride):
    need(all(type(x) is int and x>=0 for x in [start,end,maximum,stride]) and end>=start,'finite trace selection configuration','POPULATION')
    selected=set(range(start,min(end,start+maximum)))
    if stride:selected.update(range(((start+stride-1)//stride)*stride,end,stride))
    need([record['step'] for record in records]==sorted(selected),'exact predeclared sparse step selection','POPULATION')


def anchored_replay(records,initial,by_step,deadline):
    frontier=None;replayed=[];gaps=[]
    for record in records:
        tick(deadline);local_trace(record,initial)
        if frontier is not None and frontier['step']==record['step']:state=frontier
        elif record['step'] in by_step:state=copy.deepcopy(by_step[record['step']])
        else:gaps.append(record['step']);frontier=None;continue
        independent.replay(state,record);replayed.append(record['step']);frontier=state
        if state['step'] in by_step:need(state==by_step[state['step']],'complete next state matches anchored replay','ANCHOR')
    return replayed,gaps


def parse_options(options):
    values={};at=0
    while at<len(options):
        name=options[at];at+=1;need(name.startswith('--') and name not in values,'unique native option','RECEIPT')
        if name in ['--forced','--stop-at-zero','--emit-pair-costs']:values[name]=True
        else:need(at<len(options),'native option value','RECEIPT');values[name]=options[at];at+=1
    return values


def run(args):
    started=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason=args.allocation_reason);out=safe(args.out);out.mkdir(exist_ok=False);pins={}
    def pin(name,wanted=None,size=None):
        tick(deadline);path=safe(name);need(path.is_file(),'raw artifact exists:'+name,'IDENTITY');actual=sha(path)
        need(wanted is None or actual==wanted,'exact input SHA:'+name,'IDENTITY');need(size is None or path.stat().st_size==size,'exact input bytes:'+name,'IDENTITY');pins[name]=actual;return path
    def read(name):return json.loads(safe(name).read_bytes())
    try:
        pin(GATE,GATE_SHA);gate=read(GATE);need(gate['status']=='INDEPENDENT_HYPERGRAPH_WEIGHTED_ANNEAL_V1_CONTROLS_PASS','exact finite weighted gate','IDENTITY')
        helper=key(Path(independent.__file__));spec=key(Path(independent.__file__).with_name(Path(independent.__file__).stem+'_spec.md'));pin(helper,HELPER_SHA);pin(spec,HELPER_SPEC_SHA)
        need(gate['inputs_sha256'][helper]==HELPER_SHA and gate['inputs_sha256'][spec]==HELPER_SPEC_SHA,'gate binds weighted helpers','IDENTITY')
        old_helper=key(Path(independent.old.__file__));old_spec=key(Path(independent.old.__file__).with_name(Path(independent.old.__file__).stem+'_spec.md'))
        pin(old_helper,'0084ee10f2833b57a5fc8928718e8457e216fd88f6aebdc0686c34ef3d7171ac')
        pin(old_spec,'9e08c7d0c800cc853c078380e4f03df2dc8d50439962c739a7670cc972be5bde')
        need(gate['inputs_sha256'][old_helper]==pins[old_helper],'fresh transitive independent helper byte closure','IDENTITY')
        for name in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',ROOT/'pyproject.toml',ROOT/'uv.lock']:pin(key(name))
        if args.mode=='calibrate':
            controls=[];base='acceleration/results/20261002_hypergraph_weighted_controls01/'
            states={}
            for label in ['rook9_positive','target99_greedy']:
                name=base+label+'/initial.state';path=pin(name,gate['inputs_sha256'][name]);states[label]=independent.parse_state(path.read_bytes())
            rook=states['rook9_positive'];adj,_,scores=independent.score(rook['current'],9,2);matrix=matrix_from_sets(adj);report=matrix_check(matrix,9,4,deadline)
            need(report['srg_valid'] and report['weighted_energy']==0 and matrix==[[int(u!=v and (u//3==v//3 or u%3==v%3)) for v in range(9)] for u in range(9)],'known rook full scalar positive','CONTROL')
            controls.append(dict(label='known_rook9',accepted=True,all81_integer_entries=report));controls.append(reject('rook9_not_target99',lambda:target_zero(matrix,0,deadline),'TARGET_ZERO','complete99 integer SRG identity'))
            for kind in ['loop','edge','asymmetry','binary','shape']:
                bad=copy.deepcopy(matrix)
                if kind=='loop':bad[0][0]=1
                elif kind=='edge':bad[0][1]=bad[1][0]=1-bad[0][1]
                elif kind=='asymmetry':bad[0][1]=1-bad[0][1]
                elif kind=='binary':bad[0][1]=2
                else:bad.pop()
                result=matrix_check(bad,9,4,deadline);need(not result['srg_valid'],'corrupted matrix veto','CONTROL');controls.append(dict(label='matrix_'+kind,rejected=True,report=result))
            target=states['target99_greedy'];ta,_,values=independent.score(target['current'],99,7);tm=matrix_from_sets(ta);full=matrix_check(tm,99,14,deadline)
            need(full['domain_valid'] and not full['srg_valid'] and full['ordered_entries_checked']==9801 and all(full[k]==values[k] for k in SCORES) and full['adjacent_pairs']==693 and full['nonadjacent_pairs']==4158,'scalar/set exact99 nonzero agreement','CONTROL')
            controls.append(dict(label='known99_domain_positive_nonSRG',accepted_as_domain=True,srg=False,report=full));controls.append(reject('false99zero',lambda:target_zero(tm,0,deadline),'TARGET_ZERO','complete99 integer SRG identity'))
            lines=safe(base+'target99_greedy/initial.state').read_text().splitlines()
            mutations=[('weight','lambda_weight','WEIGHT'),('F','weighted_energy','WEIGHTED'),('bestF','best_weighted_energy','BEST_WEIGHTED'),('base','base_energy','COMPONENT'),('lambda','lambda_energy','COMPONENT'),('mu','mu_energy','COMPONENT'),('triple',None,'DOMAIN'),('cache',None,'CACHE'),('counter',None,'COUNTERS'),('rng',None,'RNG')]
            for label,field,stage in mutations:
                bad=lines[:]
                if field:i=next(i for i,line in enumerate(bad) if line.startswith(field+' '));bad[i]=field+' '+str(int(bad[i].split()[1])+1)
                elif label=='triple':i=next(i for i,line in enumerate(bad) if line.startswith('current '));bad[i+2]=bad[i+1]
                elif label=='cache':i=next(i for i,line in enumerate(bad) if line.startswith('cn '));bad[i+1]=str(int(bad[i+1])+1)
                elif label=='counter':i=next(i for i,line in enumerate(bad) if line.startswith('accepted '));bad[i]='accepted 1'
                else:i=next(i for i,line in enumerate(bad) if line.startswith('rng '));bad[i]='rng 0 0 0 0'
                raw=('\n'.join(bad)+'\n').encode('ascii');(out/(label+'_corrupt.state')).write_bytes(raw);controls.append(reject('state_'+label,lambda:independent.parse_state(raw),stage))
            raw=('9\n'+'\n'.join(''.join(map(str,row)) for row in matrix)+'\n').encode('ascii');need(raw_matrix(raw,9)==matrix,'raw binary positive','CONTROL')
            controls.append(reject('raw_binary',lambda:raw_matrix(raw.replace(b'010',b'020',1),9),'RAW_MATRIX','literal raw binary rows'))
            trace_name=base+'target99_greedy/moves.jsonl';trace=pin(trace_name,gate['inputs_sha256'][trace_name]);records=[json.loads(line) for line in trace.read_text().splitlines()][:3]
            for record in records:local_trace(record,target)
            for label,mutate,stage,message in [('zero_before_rng',lambda row:row.update(rng_before=['0']*4),'LOCAL_RNG','nonzero bounded local RNG'),('zero_after_rng',lambda row:row.update(rng_after=['0']*4),'LOCAL_RNG','nonzero bounded local RNG'),('wrong_after_rng',lambda row:row['rng_after'].__setitem__(0,str(int(row['rng_after'][0])^1)),'LOCAL_RNG','exact local RNG transition'),
                ('temperature',lambda row:row.update(temperature=row['temperature']+1),'LOCAL_TEMPERATURE','exact scheduled temperature tolerance'),('weight',lambda row:row.update(lambda_weight=5),'WEIGHT','fixed trace objective/weight'),
                ('component',lambda row:row.update(lambda_energy_after=row['lambda_energy_after']+1),'COMPONENT','local exact component decomposition')]:
                bad=copy.deepcopy(records[0]);mutate(bad);save(out/(label+'_trace_corrupt.json'),bad);controls.append(reject('local_'+label,lambda:local_trace(bad,target),stage,message))
            trace_population(records,0,3,3,0)
            for label,bad in [('missing',records[:-1]),('duplicate',records+[records[-1]]),('out_of_range',[records[0],records[1],dict(records[2],step=3)])]:controls.append(reject('population_'+label,lambda:trace_population(bad,0,3,3,0),'POPULATION','exact predeclared sparse step selection'))
            replayed,gaps=anchored_replay(records,target,{0:target},deadline);need(replayed==[0,1,2] and not gaps,'all complete finite anchor proposals','CONTROL');controls.append(dict(label='complete_anchor_positive',replayed=replayed))
            wrong=copy.deepcopy(target);wrong['rng'][0]^=1;controls.append(reject('wrong_rng_anchor',lambda:anchored_replay(records,target,{0:wrong},deadline),'REPLAY'))
            need(records[0]['accepted'],'accepted known anchored corruption fixture','CONTROL')
            bad=copy.deepcopy(records[0]);bad['delta']+=6;bad['weighted_energy_after']+=6;bad['lambda_energy_after']+=1
            controls.append(reject('anchored_delta',lambda:anchored_replay([bad],target,{0:target},deadline),'REPLAY'))
            replayed,gaps=anchored_replay([records[0],records[2]],target,{0:target},deadline);need(replayed==[0] and gaps==[2],'unanchored gap explicitly unreplayed','CONTROL');controls.append(dict(label='gap_positive',replayed=replayed,gaps=gaps))
            def unrelated():raise CheckError('LOCAL_RNG','unrelated')
            controls.append(dict(label='unrelated_stage_not_calibration',diagnostic=reject('outer',lambda:reject('wrong',unrelated,'DOMAIN'),'CONTROL')))
            save(out/'controls.json',dict(controls=controls,valid_target99_positive_fixture=None,null_reason='No known verified99target graph; rook9 is a different-parameter exact positive fixture.'))
            result=dict(status='INDEPENDENT_HYPERGRAPH_WEIGHTED_SAVED_OBJECTS_V2_CALIBRATION_PASS',verifier='/root/checkpoint_audit',producer='/root/native_driver',calibration_control_count=len(controls),inputs_sha256=pins,
                controls=key(out/'controls.json'),controls_sha256=sha(out/'controls.json'),scope='Finite independent weighted saved-object/scalar/sparse selection calibration only; no scientific native call.',target_resolution=False,new_native_calls=0)
        else:
            need(args.run_summary and args.run_summary_sha256 and args.calibration and args.calibration_sha256,'exact run/calibration pins','IDENTITY');pin(args.calibration,args.calibration_sha256);cal=read(args.calibration)
            need(cal['status']=='INDEPENDENT_HYPERGRAPH_WEIGHTED_SAVED_OBJECTS_V2_CALIBRATION_PASS','fresh saved-object calibration gate','IDENTITY')
            for name in [key(Path(__file__)),key(Path(__file__).with_name(Path(__file__).stem+'_spec.md')),helper,spec,old_helper,old_spec]:need(cal['inputs_sha256'][name]==pins[name],'calibration binds unchanged source/helper closure','IDENTITY')
            pin(args.run_summary,args.run_summary_sha256);summary=read(args.run_summary);base=safe(args.run_summary).parent
            need(summary['status']=='HYPERGRAPH_WEIGHTED_RESEARCH_OUTPUT_PENDING_INDEPENDENT_SAVED_STATE_CHECK' and summary['target_resolution'] is False and summary['independent_approval'] is False,'raw pending weighted science outcome','RECEIPT')
            protocol_name,invocation_name=key(base/'protocol.json'),key(base/'invocation.json');pin(protocol_name);pin(invocation_name);protocol,invocation=read(protocol_name),read(invocation_name)
            need(protocol['inputs_sha256']==summary['inputs_sha256'] and protocol['objective']==independent.OBJECTIVE and protocol['lambda_weight']==6,'same weighted protocol/input scope','RECEIPT')
            for name,digest in summary['inputs_sha256'].items():pin(name,digest)
            for name,digest in invocation['inputs_sha256'].items():need(summary['inputs_sha256'].get(name)==digest,'invocation source closure','IDENTITY')
            required=['acceleration/prepare_20261002_hypergraph_weighted_v1.py','acceleration/hypergraph_weighted_anneal_20261002_v1.cpp','acceleration/prepare_20261002_hypergraph_weighted_v1_spec.md','acceleration/design_20261002_hypergraph_weighted_v1.md','acceleration/command_deadline.py','acceleration/run_compute_command.py',
                'acceleration/native_budget_env_v1/pyproject.toml','acceleration/native_budget_env_v1/uv.lock','acceleration/results/20261002_hypergraph_weighted_build01/hypergraph_weighted_anneal','acceleration/results/20261002_hypergraph_weighted_build01/build_manifest.json']
            for name in required:need(summary['inputs_sha256'].get(name)==gate['inputs_sha256'][name],'complete gated changed execution identity','IDENTITY')
            need(summary['inputs_sha256'].get(GATE)==GATE_SHA,'weighted admission gate pinned','IDENTITY')
            outer=protocol['supervision'];pin(outer['path'],outer['sha256']);om=read(outer['path']);stop_name=str(Path(outer['path']).parent/'summary.json').replace('\\','/');pin(stop_name);stop=read(stop_name)
            need(stop['invocation_id']==om['invocation_id']==outer['invocation_id'] and stop['command_exit_code']==0 and stop['cleanup']['reaped'] is True and stop['cleanup']['job_active_zero_observed'] is True and stop['cleanup']['process_group_live_pids']==[] and stop['cleanup']['cleanup_errors']==[],'actual completed Linux containment','RECEIPT')
            need(not om['automatic_retry'] and not om['cumulative_across_commands'] and 0<om['seconds']<=21600,'fixed single invocation ceiling','RECEIPT')
            row=summary['run'];pin(row['receipt'],row['receipt_sha256']);receipt=read(row['receipt'])
            for channel in ['stdout','stderr']:pin(receipt[channel],receipt[channel+'_sha256'])
            need(receipt['actual_exit_code']==row['actual_exit_code']==receipt['expected_exit_code']==0 and receipt['reaped'] is True and receipt['process_group']==outer['group'],'successful native outcome/group','RECEIPT')
            need(row['options']==protocol['options'] and receipt['command'][14:]==row['options'] and receipt['command'][:4]==['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s'],'exact options/GNU guard','RECEIPT')
            opts=parse_options(row['options']);need(opts['--fixture']=='target99' and opts.get('--stop-at-zero') is True,'full target scientific domain','RECEIPT');native=base/'native'
            guard=receipt['command'][4];need(guard.endswith('s'),'guard syntax','RECEIPT');seconds=float(guard[:-1]);need(math.isfinite(seconds) and 0<seconds<=outer['producer_seconds'],'native budget allocation','RECEIPT')
            expected=['/usr/bin/prlimit',f"--as={invocation['address_space_bytes']}:{invocation['address_space_bytes']}",f"--fsize={invocation['file_bytes']}:{invocation['file_bytes']}",'--core=0:0',linux(required[-2]),'--out',linux(key(native)),'--seconds',f'{max(.001,seconds-5):.6f}']
            need(receipt['command'][5:14]==expected,'exact binary/output/resource profile','RECEIPT')
            actual={key(path) for path in native.iterdir() if path.is_file()};need(actual==set(row['artifacts']),'complete saved scientific file population','POPULATION')
            for name,descriptor in row['artifacts'].items():pin(name,descriptor['sha256'],descriptor['bytes'])
            files=sorted(native.glob('*.state'));need(native/'initial.state' in files and native/'final.state' in files,'initial/final objects','POPULATION');by_step={};checks=[];zero_checks=[]
            for path in files:
                tick(deadline);state=independent.parse_state(path.read_bytes());need((state['n'],state['degree'])==(99,7),'full99 scientific state','DOMAIN')
                need(path.name in ['initial.state','final.state'] or path.name=='checkpoint_'+str(state['step'])+'.state','saved filename/step','POPULATION')
                if state['step'] in by_step:need(state==by_step[state['step']],'duplicate-step full-state agreement','CHECKPOINT')
                by_step[state['step']]=state;objects={}
                for selector in ['current','best']:
                    adj,cn,components=independent.score(state[selector],99,7);matrix=matrix_from_sets(adj);full=matrix_check(matrix,99,14,deadline)
                    need(full['domain_valid'] and full['ordered_entries_checked']==9801 and all(full[k]==components[k]==state[('best_' if selector=='best' else '')+k] for k in SCORES),'independent scalar/set/fullstate scores','MATRIX')
                    need(full['adjacent_pairs']==693 and full['nonadjacent_pairs']==4158,'complete unordered pair partition','MATRIX')
                    if components['weighted_energy']==0:zero_checks.append(dict(state=key(path),selector=selector,matrix=target_zero(matrix,0,deadline),candidate_pending_external_review=True))
                    objects[selector]=dict(full_integer_matrix=full,all_pair_counts=len(cn),scores=components)
                checks.append(dict(path=key(path),sha256=pins[key(path)],step=state['step'],current_CN_cache_entries_checked=4851,objects=objects))
            initial=independent.parse_state((native/'initial.state').read_bytes());final=independent.parse_state((native/'final.state').read_bytes());ordered=[by_step[step] for step in sorted(by_step)]
            need(ordered[0]==initial and ordered[-1]==final and all(all(s[k]==initial[k] for k in CONFIG) for s in ordered),'full saved range/fixedconfig','CHECKPOINT')
            for before,after in zip(ordered,ordered[1:]):need(all(before[k]<=after[k] for k in COUNTERS) and before['best_weighted_energy']>=after['best_weighted_energy'],'monotone saved counters/Fbest','CHECKPOINT')
            interval=int(opts['--checkpoint-every']);required_steps=set(range(((initial['step']//interval)+1)*interval,final['step']+1,interval));need(required_steps<=set(by_step),'every scheduled integer checkpoint present','POPULATION')
            if '--resume' in opts:
                original=repository_path(opts['--resume']);pin(original,summary['inputs_sha256'][original]);need(safe(original).read_bytes()==(native/'initial.state').read_bytes(),'exact weighted resume initial bytes','RESUME')
            elif '--import-v1' in opts:
                original=repository_path(opts['--import-v1']);pin(original,summary['inputs_sha256'][original]);independent.imported_initial(initial,safe(original).read_bytes(),opts['--import-select'],opts)
            else:
                need(initial['current']==initial['best']==independent.old.initial(99) and initial['rng']==independent.old.seed_words(int(opts['--seed'])) and all(initial[k]==0 for k in COUNTERS),'fresh initial graph/RNG/counters','INITIAL');independent.config(initial,opts)
            result=read(key(native/'result.json'));facts=dict(objective=independent.OBJECTIVE,lambda_weight=6,n=99,point_degree=7,triple_count=231,starting_step=initial['step'],ending_step=final['step'],proposals_this_invocation=final['step']-initial['step'],admissible_total=final['admissible'],accepted_total=final['accepted'],best_updates_total=final['best_updates'],target_resolution=False,independent_approval=False)
            for prefix,state in [('initial',initial),('current',final),('best',final)]:
                for field in SCORES:facts[prefix+'_'+field]=state[('best_' if prefix=='best' else '')+field]
            need(all(result[k]==value for k,value in facts.items()) and result['proposals_this_invocation']<=int(opts['--steps']) and result['stop_reason'] in ['REQUESTED_STEPS_COMPLETE','ALLOCATED_NATIVE_BUDGET_REACHED','RAW_ZERO_PENDING_INDEPENDENT_SRG_VALIDATOR'] and 0<=result['elapsed_seconds']<=receipt['wall_seconds'],'result agrees with actual full saved objects','RESULT')
            raw={}
            for selector in ['current','best']:
                name=key(native/(selector+'.adj'));need(name in row['artifacts'],'required raw current and best exports','RAW_MATRIX');matrix=matrix_from_sets(independent.score(final[selector],99,7)[0])
                need(raw_matrix(safe(name).read_bytes(),99)==matrix,'raw export matches final labelled triples','RAW_MATRIX');export=out/('checked_final_'+selector+'.adj');export_matrix(export,matrix);raw[selector]=dict(path=name,sha256=pins[name],checked_export=key(export),checked_export_sha256=sha(export))
            records=[json.loads(line) for line in (native/'moves.jsonl').read_text().splitlines()];trace_population(records,initial['step'],final['step'],int(opts['--trace-max']),int(opts['--trace-stride']));replayed,gaps=anchored_replay(records,initial,by_step,deadline)
            save(out/'object_checks.json',dict(all_saved_objects=checks,raw_final_matrices=raw,target_zero_checks=zero_checks))
            save(out/'sparse_trace_checks.json',dict(selected_records=len(records),full_anchored_proposals=len(replayed),replayed_steps=replayed,unreplayed_steps=gaps,full_trajectory_checked=False,
                 limitation='Unanchored records have local recorded-value/RNG/component/config checks only; graph validity/actual proposed delta requires an exact complete anchor. Gaps are never bridged.'))
            final_checks=next(entry['objects'] for entry in checks if entry['path']==key(native/'final.state'))
            result=dict(status='INDEPENDENT_HYPERGRAPH_WEIGHTED_SAVED_OBJECTS_V2_PASS',verifier='/root/checkpoint_audit',producer='/root/native_driver',inputs_sha256=pins,saved_state_files=len(files),saved_unique_steps=len(by_step),complete_integer_saved_objects=len(files)*2,
                final_current_diagnostics=final_checks['current']['full_integer_matrix'],final_best_diagnostics=final_checks['best']['full_integer_matrix'],raw_final_matrices=raw,
                sparse_selected_records=len(records),full_anchored_proposals_replayed=len(replayed),unreplayed_sparse_records=len(gaps),full_trajectory_checked=False,native_counters_observed={k:final[k] for k in COUNTERS},target_zero_candidates=len(zero_checks),
                target_resolution=False,outputs_sha256={path.name:sha(path) for path in out.iterdir() if path.is_file()},scope='All exact weighted saved current/best objects and raw complete99matrices; sparse complete-anchor replay only.',new_native_calls=0,
                limitations=['No complete trajectory, throughput, ergodicity or exhaustive coverage assertion.','Observed counters are saved syntax/order/result-consistency checks, not independently replayed entire run counts.','Any targetzero survives this internal integer checker only as a candidate pending another checking path and external review.','Historical completed receipt/group observations do not assert a currently running process.'])
        result.update(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),elapsed_seconds=time.monotonic()-started,
             shared_components=['Own pinned independently calibrated weighted full graph/RNG/state helper; no producer imports.','Separate fresh integer scalar row-column matrix path, Python/JSON/SHA-256 and locked supported runtime/deadline/containment.'],artifact_availability='LOCAL_ONLY',deadline=deadline.status())
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],sha256=sha(out/'summary.json'),elapsed_seconds=result['elapsed_seconds'])))
    except Exception as error:
        save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),error=repr(error),inputs_sha256=pins,elapsed_seconds=time.monotonic()-started,target_resolution=False,outputs_preserved=True));raise


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=['calibrate','verify']);ap.add_argument('--out',required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--allocation-reason',required=True)
    for name in ['run-summary','calibration']:ap.add_argument('--'+name);ap.add_argument('--'+name+'-sha256')
    run(ap.parse_args())

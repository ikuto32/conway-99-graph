"""Independent weighted scorer/import/RNG complete finite native-control replay."""
from __future__ import annotations
import argparse,copy,hashlib,json,math,platform,re,subprocess,sys,time
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261002_hypergraph_controls_v2 as old

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261002_hypergraph_weighted_controls01'
MANIFEST=BASE+'/controls_manifest.json'
MANIFEST_SHA='ab04dbaf727bf237192200175d3780b8cae355a32cb69ac15ef990ec69631e67'
OBJECTIVE='SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V1'
SCALARS=old.SCALARS[:-2]+('weighted_energy','base_energy','lambda_energy','mu_energy','best_weighted_energy','best_base_energy','best_lambda_energy','best_mu_energy')
need=old.need;CheckError=old.CheckError;TOL=old.TOL;M=old.M


def score(triples,n,degree):
    adj,cn,base=old.graph(triples,n,degree)
    # No incremental-toggle formula or producer import. Category sets come
    # directly from the complete graph reconstructed from labelled triples.
    el=sum((len(adj[u]&adj[v])-1)**2 for u,v in combinations(range(n),2) if v in adj[u])
    em=sum((len(adj[u]&adj[v])-2)**2 for u,v in combinations(range(n),2) if v not in adj[u])
    need(base==el+em,'exact unweighted/category decomposition','SCORER')
    return adj,cn,dict(weighted_energy=6*el+em,base_energy=el+em,lambda_energy=el,mu_energy=em)


def parse_state(data):
    tokens=data.decode('ascii').split();at=0
    def take():
        nonlocal at
        need(at<len(tokens),'complete token stream','SYNTAX');value=tokens[at];at+=1;return value
    def field(name):need(take()==name,'ordered field '+name,'SYNTAX');return take()
    need(take()=='HYPERGRAPH_WEIGHTED_ANNEAL_STATE_V1','weighted state version','SYNTAX')
    s={'objective':field('objective'),'lambda_weight':old.natural(field('lambda_weight'))}
    need(s['objective']==OBJECTIVE and s['lambda_weight']==6,'exact objective and fixed weight','WEIGHT')
    for name in SCALARS:
        raw=field(name);s[name]=float(raw) if name in ['t_start','t_end'] else old.natural(raw)
    need((s['n'],s['degree']) in [(99,7),(9,2)],'exact target or control domain','DOMAIN')
    need(all(math.isfinite(s[k]) and 0<=s[k]<=1000 for k in ['t_start','t_end']) and s['schedule_steps']>0,'bounded temperature schedule','SCHEDULE')
    need(all(0<=s[k]<=M for k in ['seed','mix_steps','schedule_steps','step','admissible','accepted','best_updates']) and s['forced'] in [0,1],'uint64 counters/config','COUNTERS')
    need(take()=='rng','RNG tag','SYNTAX');s['rng']=[old.natural(take(),'RNG') for _ in range(4)]
    need(all(0<=x<=M for x in s['rng']) and any(s['rng']),'nonzero uint64 RNG','RNG')
    for name in ['current','best']:
        count=old.natural(field(name));need(count==s['n']*s['degree']//3,name+' triple count','DOMAIN')
        s[name]=[[old.natural(take()) for _ in range(3)] for _ in range(count)]
    _,cn,current=score(s['current'],s['n'],s['degree']);_,_,best=score(s['best'],s['n'],s['degree'])
    need(current['weighted_energy']==s['weighted_energy'],'exact current weighted score','WEIGHTED')
    need(best['weighted_energy']==s['best_weighted_energy'] and best['weighted_energy']<=current['weighted_energy'],'exact best weighted score/order','BEST_WEIGHTED')
    need(all(s[key]==value and s['best_'+key]==best[key] for key,value in current.items() if key!='weighted_energy'),'all exact base/lambda/mu components','COMPONENT')
    count=old.natural(field('cn'));need(count==len(cn),'cache population','CACHE');need([old.natural(take()) for _ in range(count)]==cn,'all exact CN cache entries','CACHE')
    need(take()=='END' and at==len(tokens),'exact record end','SYNTAX')
    need(0<=s['best_updates']<=s['accepted']<=s['admissible']<=s['step'],'counter order','COUNTERS')
    return s


def replay(s,record):
    before=s['rng'][:];size=len(s['current']);ti=old.rng_next(s['rng'])%size;tj=old.rng_next(s['rng'])%(size-1)
    if tj>=ti:tj+=1
    pi=old.rng_next(s['rng'])%3;pj=old.rng_next(s['rng'])%3;t=s['current'][ti][:];q=s['current'][tj][:]
    x=t[pi];y=q[pj];a=t[(pi+1)%3];b=t[(pi+2)%3];c=q[(pj+1)%3];d=q[(pj+2)%3]
    adj,_,current=score(s['current'],s['n'],s['degree']);need(all(s[key]==value for key,value in current.items()),'all complete scores before every proposal')
    disjoint=not bool(set(t)&set(q));absent=all(v not in adj[u] for u,v in [(y,a),(y,b),(x,c),(x,d)]);valid=disjoint and absent
    pt=t[:];pq=q[:];pt[pi]=y;pq[pj]=x;elapsed=max(0,s['step']-s['mix_steps']);fraction=min(1.0,float(elapsed)/float(s['schedule_steps']))
    temperature=s['t_start']+(s['t_end']-s['t_start'])*fraction;mixing=s['step']<s['mix_steps'];draw=0;delta=0;accepted=False;margin=None
    if valid:
        proposal=[row[:] for row in s['current']];proposal[ti]=pt;proposal[tj]=pq;_,_,proposed=score(proposal,s['n'],s['degree']);delta=proposed['weighted_energy']-current['weighted_energy']
        draw=old.rng_next(s['rng']);uniform=(draw>>11)/2**53
        if s['forced'] or mixing or delta<=0:accepted=True
        elif temperature>0:
            threshold=math.exp(-float(delta)/temperature);margin=abs(uniform-threshold);need(margin>TOL,'unambiguous floating acceptance margin','FLOAT');accepted=uniform<threshold
        s['admissible']+=1
        if accepted:
            s['current']=proposal;s.update(proposed);s['accepted']+=1
            if proposed['weighted_energy']<s['best_weighted_energy']:
                s['best']=copy.deepcopy(proposal);s.update({'best_'+key:value for key,value in proposed.items()});s['best_updates']+=1
    expected=dict(step=s['step'],ti=ti,tj=tj,pi=pi,pj=pj,old_triples=[t,q],proposed_triples=[pt,pq],disjoint=disjoint,new_pairs_absent=absent,
         admissible=valid,accepted=accepted,mixing=mixing,objective=OBJECTIVE,lambda_weight=6,delta=delta,
         weighted_energy_before=current['weighted_energy'],weighted_energy_after=s['weighted_energy'],lambda_energy_before=current['lambda_energy'],mu_energy_before=current['mu_energy'],
         lambda_energy_after=s['lambda_energy'],mu_energy_after=s['mu_energy'],best_weighted_energy=s['best_weighted_energy'],draw=str(draw),rng_before=[str(w) for w in before],rng_after=[str(w) for w in s['rng']])
    need(set(record)==set(expected)|{'temperature'},'exact weighted trace fields')
    for name,value in expected.items():need(type(record[name]) is type(value) and record[name]==value,'raw weighted transition '+name)
    need(type(record['temperature']) in [int,float] and math.isfinite(record['temperature']) and abs(temperature-record['temperature'])<=TOL,'temperature numeric tolerance','FLOAT')
    s['step']+=1;return valid,accepted,delta,margin


def pair_costs():
    rows=[]
    def costs(c,a):return ((c-1)**2,0) if a else (0,(c-2)**2)
    for common in range(15):
        for adjacent in range(2):
            changes=[('CN',delta,common+delta,adjacent) for delta in [-1,1] if 0<=common+delta<=14]+[('EDGE',1-2*adjacent,common,1-adjacent)]
            for kind,delta,new_c,new_a in changes:
                ol,om=costs(common,adjacent);nl,nm=costs(new_c,new_a)
                rows.append(dict(kind=kind,c=common,a=adjacent,delta=delta,new_c=new_c,new_a=new_a,old_lambda=ol,old_mu=om,new_lambda=nl,new_mu=nm,delta_F=(6*nl+nm)-(6*ol+om)))
    need(len(rows)==86 and Counter(row['kind'] for row in rows)=={'CN':56,'EDGE':30},'complete finite pair-cost universe','PAIR')
    return rows


def check_pair_table(rows):need(rows==pair_costs(),'every weighted category pair cost','PAIR')


def config(s,opts):
    need(s['seed']==int(opts['--seed']) and s['mix_steps']==int(opts['--mix-steps']) and s['schedule_steps']==int(opts['--schedule-steps'])
       and s['t_start']==float(opts['--temperature-start']) and s['t_end']==float(opts['--temperature-end']) and s['forced']==int('--forced' in opts),'new exact initial configuration','INITIAL')


def imported_initial(s,data,selector,opts):
    original=old.parse_state(data);need(selector in ['current','best'],'explicit valid graph selector','IMPORT')
    need(s['current']==s['best']==original[selector],'exact selected imported labelled graph','IMPORT')
    need(s['step']==s['admissible']==s['accepted']==s['best_updates']==0,'import counters reset','IMPORT')
    need(s['rng']==old.seed_words(int(opts['--seed'])),'import new exact RNG','IMPORT');config(s,opts)


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def run(args):
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Exact independent32-control weighted component/scorer/RNG/import/whole-split replay;20sreserve')
    out=args.out.resolve();out.mkdir(exist_ok=False);pins={};checked=[];controls=[]
    def tick():need(deadline.status()['remaining_seconds']>20 and not deadline.status()['stop_required'],'not completed within the allocated budget','DEADLINE')
    def path(name):
        value=(ROOT/name).resolve();need(value.is_relative_to(ROOT) and value.is_file(),'local repository artifact','IDENTITY');return value
    def pin(name,wanted=None,size=None):
        tick();value=path(name);digest=hashlib.sha256(value.read_bytes()).hexdigest();need(wanted is None or wanted==digest,'hash '+name,'IDENTITY');need(size is None or size==value.stat().st_size,'size '+name,'IDENTITY')
        need(name not in pins or pins[name]==digest,'consistent raw pin','IDENTITY');pins[name]=digest;return value
    def read(name):return json.loads(path(name).read_bytes())
    def linux(name):return '/mnt/c/'+str((ROOT/name).resolve())[3:].replace('\\','/')
    def opts_list(fixture='target99',steps=2048,seed=99032020,temp=16,end=None,mix=0,forced=False,resume=None,imported=None,select='current'):
        if end is None:end=temp
        result=['--fixture',fixture,'--steps',str(steps),'--seed',str(seed),'--mix-steps',str(mix),'--temperature-start',str(temp),'--temperature-end',str(end),'--schedule-steps','1024','--verify-every','1','--checkpoint-every','64','--checkpoint-seconds','15','--trace-max',str(steps),'--emit-pair-costs']
        if forced:result+=['--forced']
        if resume:result+=['--resume',linux(resume)]
        if imported:result+=['--import-v1',linux(imported),'--import-select',select]
        return result
    try:
        pin(MANIFEST,MANIFEST_SHA);manifest=read(MANIFEST)
        need(manifest['schema']=='HYPERGRAPH_WEIGHTED_ANNEAL_CONTROLS_V1' and manifest['objective']==OBJECTIVE and manifest['lambda_weight']==6 and manifest['target_resolution'] is False and manifest['independent_approval'] is False,'raw unapproved weighted scope','RECEIPT')
        for name,digest in manifest['inputs_sha256'].items():pin(name,digest)
        pin('acceleration/audit_20261002_hypergraph_controls_v2.py','0084ee10f2833b57a5fc8928718e8457e216fd88f6aebdc0686c34ef3d7171ac')
        for name in [Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),'uv.lock','pyproject.toml']:pin(name)
        build_name='acceleration/results/20261002_hypergraph_weighted_build01/build_manifest.json';build=read(build_name)
        need(build['schema']=='HYPERGRAPH_WEIGHTED_ANNEAL_NATIVE_BUILD_V1' and build['source_cpp_sha256']==pins['acceleration/hypergraph_weighted_anneal_20261002_v1.cpp'] and build['binary_sha256']==pins[build['binary_path']]
           and build['compiler_sha256']=='1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769','exact changed source/binary/compiler','RECEIPT')
        pin(build['receipt'],build['receipt_sha256']);br=read(build['receipt']);need(br['command']==build['command'] and br['actual_exit_code']==0 and br['reaped'] is True and build['command'][1:6]==['-std=c++17','-O3','-Wall','-Wextra','-Werror'],'actual native build receipt','RECEIPT')
        for channel in ['stdout','stderr']:pin(br[channel],br[channel+'_sha256'])
        outer=manifest['supervision'];pin(outer['path'],outer['sha256']);sm=read(outer['path']);ss_name=str(Path(outer['path']).parent/'summary.json').replace('\\','/');pin(ss_name);ss=read(ss_name)
        need(sm['invocation_id']==ss['invocation_id']==outer['invocation_id'] and sm['seconds']==outer['outer_seconds']==600 and outer['producer_seconds']==540
            and sm['cumulative_across_commands'] is False and sm['automatic_retry'] is False,'frozen contained invocation','RECEIPT')
        need(ss['command_exit_code']==0 and ss['cleanup']['reaped'] is True and ss['cleanup']['job_active_zero_observed'] is True and ss['cleanup']['process_group_live_pids']==[] and ss['cleanup']['cleanup_errors']==[],'actual complete Linux cleanup observation','RECEIPT')
        need(outer['guard_argv'][:2]==['/usr/bin/timeout','--signal=KILL'] and outer['guard_argv'][3:5]==['/usr/bin/env','UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv']
           and outer['guard_argv'][5:9]==['/root/.local/bin/uv','run','--locked','--offline'],'contained GNU guard and locked runtime','RECEIPT')
        import_name='acceleration/results/20261002_hypergraph_controls01/target99_mixed/final.state';import_bytes=path(import_name).read_bytes();import_state=old.parse_state(import_bytes)
        need(import_state['energy']==5304 and import_state['best_energy']==5248 and import_state['current']!=import_state['best'],'distinct independently checked old import graphs','IMPORT')
        old_gate=read('acceleration/results/20261002_independent_review/hypergraph_controls02/summary.json');need(old_gate['status']=='INDEPENDENT_HYPERGRAPH_ANNEAL_V1_CONTROLS_PASS' and old_gate['inputs_sha256'][import_name]==pins[import_name],'old gate approves raw source only','IMPORT')
        population=[('rook9_positive',opts_list(fixture='rook9',steps=0,temp=0)),('rook9_forced',opts_list(fixture='rook9',temp=0,forced=True)),('target99_forced',opts_list(temp=0,forced=True)),('target99_greedy',opts_list(temp=0)),
          ('target99_anneal',opts_list()),('target99_cooling',opts_list(temp=48,end=.2)),('target99_warming',opts_list(temp=.2,end=48)),('target99_mixed',opts_list(temp=24,mix=256)),
          ('resume_whole',opts_list(steps=256,seed=99032021,temp=16,mix=64)),('resume_first',opts_list(steps=73,seed=99032021,temp=16,mix=64)),('resume_second',opts_list(steps=183,seed=99032021,temp=16,mix=64,resume=BASE+'/resume_first/final.state')),
          ('import_v1_current',opts_list(seed=99032022,temp=24,end=.2,mix=64,imported=import_name)),('import_v1_best',opts_list(seed=99032022,temp=24,end=.2,mix=64,imported=import_name,select='best')),
          ('import_resume_whole',opts_list(steps=256,seed=99032022,temp=24,end=.2,mix=64,resume=BASE+'/import_v1_best/initial.state')),('import_resume_first',opts_list(steps=73,seed=99032022,temp=24,end=.2,mix=64,resume=BASE+'/import_v1_best/initial.state')),
          ('import_resume_second',opts_list(steps=183,seed=99032022,temp=24,end=.2,mix=64,resume=BASE+'/import_resume_first/final.state'))]
        diagnostics={'lambda_weight':('checkpoint exact objective/weight','WEIGHT'),'weighted_energy':('checkpoint exact weighted current/best scores','WEIGHTED'),'best_weighted_energy':('checkpoint exact weighted current/best scores','BEST_WEIGHTED'),
            'lambda_energy':('checkpoint exact component/base scores','COMPONENT'),'mu_energy':('checkpoint exact component/base scores','COMPONENT'),'base_energy':('checkpoint exact component/base scores','COMPONENT'),
            'cn':('checkpoint exact CN cache','CACHE'),'duplicate_triple':('linear hypergraph pair multiplicity','DOMAIN'),'zero_rng':('nonzero RNG state','RNG'),'counter':('checkpoint counter consistency','COUNTERS'),
            'import_energy':('import v1 exact base current/best scores','ENERGY'),'import_cn':('import v1 exact CN cache','CACHE'),'import_triple':('linear hypergraph pair multiplicity','DOMAIN'),'import_counter':('import v1 counters','COUNTERS'),'import_zero_rng':('import v1 nonzero RNG','RNG')}
        need([item['type'] for item in manifest['corruptions']]==list(diagnostics),'exact15corrupted raw inputs','POPULATION')
        for item in manifest['corruptions']:
            label=item['type'];p=pin(item['path'],item['sha256']);need(item['expected_exit_code']==2,'expected corrupted exit','CONTROL')
            parser=old.parse_state if label.startswith('import_') else parse_state;controls.append(dict(raw_corruption=label,independent_diagnostic=old.reject(lambda:parser(p.read_bytes()),diagnostics[label][1])))
            population.append(('reject_'+label,opts_list(steps=1,imported=item['path'],select='best') if label.startswith('import_') else opts_list(steps=1,resume=item['path'])))
        population.append(('reject_import_selector',opts_list(steps=1,imported=import_name,select='wrong')))
        need([(row['label'],row['options']) for row in manifest['runs']]==population,'complete independently frozen32command population','POPULATION')
        successes={};traces={};all_checkpoints=full_proposals=valid_proposals=pair_records=0;minimum_margin=None
        for row in tqdm(manifest['runs'],desc='independent weighted finite control replay',unit='call',mininterval=5):
            tick();label=row['label'];pin(row['receipt'],row['receipt_sha256']);receipt=read(row['receipt']);native_out=BASE+'/'+label
            command=['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s','30.000000s','/usr/bin/prlimit','--as=2147483648:2147483648','--fsize=1073741824:1073741824','--core=0:0',linux(build['binary_path']),
                     '--out',linux(native_out),'--seconds','25.000000',*row['options']];expected_exit=2 if label.startswith('reject_') else 0
            need(receipt['command']==command and receipt['cwd']==linux('') and receipt['actual_exit_code']==row['actual_exit_code']==expected_exit and receipt['expected_exit_code']==expected_exit and receipt['reaped'] is True
               and receipt['process_group']==outer['group'] and receipt['independent_approval'] is False,'exact native command/outcome/containment','RECEIPT')
            for channel in ['stdout','stderr']:pin(receipt[channel],receipt[channel+'_sha256'])
            for name,descriptor in row['artifacts'].items():pin(name,descriptor['sha256'],descriptor['bytes'])
            directory=ROOT/native_out;need({p.relative_to(ROOT).as_posix() for p in directory.iterdir() if p.is_file()}==set(row['artifacts']),'complete saved artifact population','POPULATION')
            if expected_exit:
                diagnostic='import v1 graph selector' if label=='reject_import_selector' else diagnostics[label[7:]][0]
                need(row['artifacts']=={} and path(receipt['stderr']).read_text().splitlines()==[diagnostic] and path(receipt['stdout']).read_bytes()==b'','exact native corruption diagnostic, empty stdout/no artifacts','CONTROL');continue
            data=(directory/'initial.state').read_bytes();s=parse_state(data);initial=copy.deepcopy(s);options=row['options'];opts={};at=0
            while at<len(options):
                name=options[at];at+=1
                if name in ['--forced','--emit-pair-costs']:opts[name]=True;continue
                need(at<len(options),'option value','SYNTAX');opts[name]=options[at];at+=1
            steps=int(opts['--steps']);need(int(opts['--trace-max'])==steps and opts['--verify-every']=='1','complete control traces/full producer verification','POPULATION')
            if '--resume' in opts:
                relative=opts['--resume'][len(linux(''))+1:];need(data==path(relative).read_bytes(),'resume whole initial raw byte identity','RESUME')
            elif '--import-v1' in opts:imported_initial(s,import_bytes,opts['--import-select'],opts)
            else:
                need(s['current']==s['best']==old.initial(s['n']) and s['step']==s['admissible']==s['accepted']==s['best_updates']==0 and s['rng']==old.seed_words(int(opts['--seed'])),'fresh labelled graph/RNG/counters','INITIAL');config(s,opts)
            snapshots={}
            for file in sorted(directory.glob('checkpoint_*.state')):
                snap=parse_state(file.read_bytes());need(file.name=='checkpoint_'+str(snap['step'])+'.state' and snap['step'] not in snapshots,'unique step checkpoint','CHECKPOINT');snapshots[snap['step']]=snap
            records=[json.loads(line) for line in (directory/'moves.jsonl').read_text().splitlines()];need(len(records)==steps,'full trace population','POPULATION');traces[label]=records
            for index,record in enumerate(records):
                if index%128==0:tick()
                valid,accepted,delta,margin=replay(s,record);full_proposals+=1;valid_proposals+=int(valid)
                if margin is not None:minimum_margin=margin if minimum_margin is None else min(minimum_margin,margin)
                if s['step'] in snapshots:need(s==snapshots.pop(s['step']),'every saved full checkpoint independently replayed','CHECKPOINT');all_checkpoints+=1
            need(not snapshots,'no unvisited checkpoint','CHECKPOINT');final=parse_state((directory/'final.state').read_bytes());need(final==s,'complete final state replay','CHECKPOINT')
            for selector in ['current','best']:
                adj,_,components=score(s[selector],s['n'],s['degree']);matrix=[[int(v in adj[u]) for v in range(s['n'])] for u in range(s['n'])]
                need((directory/(selector+'.adj')).read_text().splitlines()==[str(s['n'])]+[''.join(map(str,value)) for value in matrix],'complete raw '+selector+' matrix','MATRIX')
                if components['weighted_energy']==0:
                    old.matrix_claim(matrix,s['n'],2*s['degree'])
                    if s['n']==99:raise CheckError('RESOLUTION','raw target zero requires separate research target certificate review')
            table=[json.loads(line) for line in (directory/'pair_costs.jsonl').read_text().splitlines()];check_pair_table(table);pair_records+=len(table)
            result=json.loads((directory/'result.json').read_bytes());facts=dict(objective=OBJECTIVE,lambda_weight=6,n=s['n'],point_degree=s['degree'],triple_count=len(s['current']),starting_step=initial['step'],ending_step=s['step'],proposals_this_invocation=steps,
                admissible_total=s['admissible'],accepted_total=s['accepted'],best_updates_total=s['best_updates'],stop_reason='REQUESTED_STEPS_COMPLETE',target_resolution=False,independent_approval=False)
            for prefix,state in [('initial',initial),('current',s),('best',s)]:
                for key in ['weighted_energy','lambda_energy','mu_energy','base_energy']:facts[prefix+'_'+key]=state[('best_' if prefix=='best' else '')+key]
            need({key:value for key,value in result.items() if key!='elapsed_seconds'}==facts and 0<=result['elapsed_seconds']<=receipt['wall_seconds'],'every result field independently replayed','RESULT')
            if label=='rook9_positive':
                need(initial['weighted_energy']==0 and matrix==[[int(u!=v and (u//3==v//3 or u%3==v%3)) for v in range(9)] for u in range(9)],'known exact rook positive','CONTROL')
                controls.append(dict(known_rook_zero=True,scope_rejection=old.reject(lambda:old.matrix_claim(matrix,99,14),'MATRIX')));damaged=copy.deepcopy(matrix);damaged[0][1]=damaged[1][0]=0
                controls.append(dict(corrupted_rook_rejected=old.reject(lambda:old.matrix_claim(damaged,9,4),'MATRIX')))
            successes[label]=dict(initial=initial,final=final);checked.append(dict(label=label,full_proposals=steps,admissible_full_rescored=sum(record['admissible'] for record in records),initial_scores={key:initial[key] for key in ['weighted_energy','base_energy','lambda_energy','mu_energy']},
                current_scores={key:s[key] for key in ['weighted_energy','base_energy','lambda_energy','mu_energy']},best_scores={key:s['best_'+key] for key in ['weighted_energy','base_energy','lambda_energy','mu_energy']},receipt_sha256=row['receipt_sha256']))
        need(full_proposals==19456 and len(successes)==16 and pair_records==1376,'complete successful proposal/pairtable population','POPULATION')
        for prefix in ['resume','import_resume']:
            need((ROOT/BASE/(prefix+'_whole/final.state')).read_bytes()==(ROOT/BASE/(prefix+'_second/final.state')).read_bytes(),'whole/split final bytes '+prefix,'RESUME')
            need(traces[prefix+'_whole']==traces[prefix+'_first']+traces[prefix+'_second'],'whole/split all trace records '+prefix,'RESUME')
        # Independent counterexamples to accidentally retaining an unweighted
        # formula, prior import trajectory, wrong source selection or trace.
        for field in ['delta','weighted_energy_after','lambda_energy_after','mu_energy_after','rng_after','accepted','lambda_weight']:
            bad=copy.deepcopy(traces['target99_greedy'][0])
            if field=='rng_after':bad[field][0]=str(int(bad[field][0])^1)
            elif field=='accepted':bad[field]=not bad[field]
            else:bad[field]+=1
            controls.append(dict(mutated_trace=field,diagnostic=old.reject(lambda:replay(copy.deepcopy(successes['target99_greedy']['initial']),bad),'REPLAY')))
        for label,mutate in [('retained_old_counters',lambda s:s.update(step=import_state['step'])),('wrong_source_graph',lambda s:s.update(current=copy.deepcopy(import_state['current']))),('old_rng',lambda s:s.update(rng=import_state['rng'][:]))]:
            bad=copy.deepcopy(successes['import_v1_best']['initial']);mutate(bad);opts={'--seed':'99032022','--mix-steps':'64','--schedule-steps':'1024','--temperature-start':'24','--temperature-end':'.2'}
            controls.append(dict(mutated_import=label,diagnostic=old.reject(lambda:imported_initial(bad,import_bytes,'best',opts),'IMPORT')))
        controls.append(dict(invalid_selector=old.reject(lambda:imported_initial(successes['import_v1_best']['initial'],import_bytes,'wrong',opts),'IMPORT')))
        controls.append(dict(unweighted_resume_rejected=old.reject(lambda:parse_state(import_bytes),'SYNTAX')))
        for field in ['delta_F','old_lambda','new_mu']:
            table=pair_costs();table[1][field]+=1;controls.append(dict(mutated_pair_cost=field,diagnostic=old.reject(lambda:check_pair_table(table),'PAIR')))
        table=pair_costs();table[1]['delta_F']=2*(table[1]['c']+table[1]['a']-2)*table[1]['delta']+table[1]['delta']**2
        controls.append(dict(old_unweighted_toggle_rejected=old.reject(lambda:check_pair_table(table),'PAIR')))
        zero=score(old.initial(9),9,2)[2];nonzero=score(old.initial(99),99,7)[2];need(zero==dict(weighted_energy=0,base_energy=0,lambda_energy=0,mu_energy=0) and nonzero==dict(weighted_energy=54450,base_energy=19800,lambda_energy=6930,mu_energy=12870),'exact scorer controls','CONTROL')
        detail=dict(runs=checked,checking_controls=controls,all_saved_checkpoints=all_checkpoints,full_proposals=full_proposals,admissible_full_rescored=valid_proposals,pair_table_records=pair_records,minimum_probabilistic_margin=minimum_margin,
            zero_equivalence_derivation='On a binary simple symmetric graph of degree k=2d, F=6*sum_adj(CN-1)^2+sum_nonadj(CN-2)^2. All integer summands nonnegative and weights positive: F=0 iff each offdiagonal CN=2-A. The diagonal A^2 is k by binary regularity. Thus A^2=(k-2)I-A+2J exactly, and conversely. For n99,d7 this is12I-A+2J; a9vertex control cannot certify99.')
        save(out/'checked_controls.json',detail)
        summary=dict(status='INDEPENDENT_HYPERGRAPH_WEIGHTED_ANNEAL_V1_CONTROLS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/checkpoint_audit',producer='/root/native_driver',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),producer_source_commit=manifest['source_commit'],
            command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,outputs_sha256={'checked_controls.json':hashlib.sha256((out/'checked_controls.json').read_bytes()).hexdigest()},native_calls_observed=32,new_native_calls=0,successful_calls_completely_replayed=16,rejected_corrupt_calls=16,full_proposals=19456,
            admissible_proposals_full_rescored=valid_proposals,all_saved_intermediate_checkpoints=all_checkpoints,pair_table_records=pair_records,independent_calibrated_controls=len(controls),objective=OBJECTIVE,lambda_weight=6,
            scope='Frozen32native finite engineering controls only, including complete fresh/imported trajectories, all states/cache/component scores/matrices, cost tables and both whole/split resumes.',
            numerical_acceptance=dict(scores_deltas_counts_rng_cache='EXACT_INTEGERS',temperature_absolute_tolerance=TOL,required_probabilistic_margin=TOL,actual_minimum_probabilistic_margin=minimum_margin),
            comparison='Separate complete adjacency-set rescoring/category sums versus native incremental bitset toggle caches; imported source selection/counters/new RNG independently checked.',
            shared_trusted_components=['Earlier independent unweighted domain/parsing/RNG and exact matrix checker pinned; no producer imports.','Python exact integer/set/JSON/SHA-256, libm only for heuristic acceptance, locked uv and supported containment/deadline.'],
            limitations=['Finite engineering controls prove no general trajectory, ergodicity, performance or exhaustive coverage guarantee.','Native compiler/build are hash/receipt bound, not independently rebuilt.','WeightedF and unweightedE are distinct metrics; best minimizesF, not necessarilyE.','Imports reset state and are not continuations of the old trajectory.','Heuristic acceptance uses recorded tolerance/margin; raw integer zero requires independent full target matrix certificate.','Historical process cleanup does not assert current liveness.'],
            mathematical_target_resolution=False,target_resolution=False,overall_search_coverage='UNKNOWN; no validated denominator.',tool_versions=dict(python=platform.python_version(),platform=platform.platform()),elapsed_seconds=time.monotonic()-start,deadline=deadline.status())
        save(out/'summary.json',summary);print(json.dumps({key:summary[key] for key in ['status','full_proposals','admissible_proposals_full_rescored','all_saved_intermediate_checkpoints','elapsed_seconds']}))
    except Exception as error:
        save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),status='INDEPENDENT_CHECK_FAILED',error=repr(error),inputs_sha256=pins,completed_calls=checked,controls=controls,elapsed_seconds=time.monotonic()-start,target_resolution=False));raise


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);run(ap.parse_args())

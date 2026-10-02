"""Independent complete57-call weight60 overlap-kernel engineering audit."""
import argparse
import copy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261002_weight60_scalar_v1 as C

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20261002_hypergraph_weight60_controls02'
MANIFEST=BASE+'/controls_manifest.json'
MANIFEST_SHA='92beb153d4d2abc1a93da1ef29d583153c411668916336fe366f41d05525f43f'
BUILD='acceleration/results/20261002_hypergraph_weight60_build02/build_manifest.json'
OLD='acceleration/results/20261002_hypergraph_weighted_controls01/target99_warming/final.state'
ROOK='acceleration/results/20261002_hypergraph_weighted_controls01/rook9_positive/final.state'
PILOT='acceleration/results/20261002_hypergraph_weighted_pilot02/native/final.state'
SHARED={'acceleration/audit_20261002_hypergraph_controls_v2.py':'0084ee10f2833b57a5fc8928718e8457e216fd88f6aebdc0686c34ef3d7171ac','acceleration/audit_20261002_hypergraph_weighted_controls_v1.py':'9029183c33dd05147dce44f5d295e5fe3b68caebfcc624e53d77e062d735b79a'}
D={
 'lambda_weight':('checkpoint exact objective/weight','WEIGHT'),'weighted_energy':('checkpoint exact weighted current/best scores','WEIGHTED'),'best_weighted_energy':('checkpoint exact weighted current/best scores','BEST_WEIGHTED'),
 'lambda_energy':('checkpoint exact component/base scores','COMPONENT'),'mu_energy':('checkpoint exact component/base scores','COMPONENT'),'base_energy':('checkpoint exact component/base scores','COMPONENT'),
 'cn':('checkpoint exact CN cache','CACHE'),'duplicate_triple':('linear hypergraph pair multiplicity','DOMAIN'),'zero_rng':('nonzero RNG state','RNG'),'counter':('checkpoint counter consistency','COUNTERS'),'objective':('checkpoint exact objective/weight','WEIGHT'),'version':('checkpoint version','SYNTAX'),'kernel':('checkpoint exact move kernel','KERNEL'),
 'import_energy':('import weight6 exact weighted current/best scores','WEIGHTED'),'import_cn':('import weight6 exact CN cache','CACHE'),'import_triple':('linear hypergraph pair multiplicity','DOMAIN'),'import_counter':('import weight6 counters','COUNTERS'),'import_zero_rng':('import weight6 nonzero RNG','RNG'),'import_objective':('import weight6 exact objective/weight','WEIGHT'),'import_weight':('import weight6 exact objective/weight','WEIGHT'),'import_lambda':('import weight6 exact component/base scores','COMPONENT'),'import_base':('import weight6 exact component/base scores','COMPONENT'),
 'first_flag':('checkpoint first lambda0 flag','FIRST_FLAG'),'first_rng':('checkpoint first lambda0 nonzero RNG','FIRST_RNG'),'first_counter':('checkpoint first lambda0 counters','FIRST_COUNTER'),'first_triple':('linear hypergraph pair multiplicity','DOMAIN'),'missing_first':('checkpoint lambda0 selection completeness','FIRST_COMPLETENESS')}


def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')


def linux(name):return'/mnt/c/'+str((ROOT/name).resolve())[3:].replace('\\','/')


def repo_from_linux(name):
    prefix=linux('')+'/';C.need(name.startswith(prefix),'repository-relative Linux artifact','IDENTITY');return ROOT/name[len(prefix):]


def opts(fixture='target99',steps=2048,seed=99032020,temp=16,end=None,mix=0,forced=False,resume=None,imported=None,select='current'):
    if end is None:end=temp
    result=['--fixture',fixture,'--steps',str(steps),'--seed',str(seed),'--mix-steps',str(mix),'--temperature-start',str(temp),'--temperature-end',str(end),'--schedule-steps','1024','--verify-every','1','--checkpoint-every','64','--checkpoint-seconds','15','--trace-max',str(steps),'--emit-pair-costs']
    if forced:result+=['--forced']
    if resume:result+=['--resume',linux(resume)]
    if imported:result+=['--import-weight6',linux(imported),'--import-select',select]
    return result


def parse_opts(values):
    out={};at=0
    while at<len(values):
        key=values[at];at+=1;C.need(key not in out,'unique option','SYNTAX')
        if key in['--forced','--emit-pair-costs']:out[key]=True
        else:C.need(at<len(values),'option value','SYNTAX');out[key]=values[at];at+=1
    return out


def population(corruptions):
    result=[('rook9_positive',opts(fixture='rook9',steps=0,temp=0)),('rook9_forced',opts(fixture='rook9',temp=0,forced=True)),('target99_forced',opts(temp=0,forced=True)),('target99_greedy',opts(temp=0)),('target99_anneal',opts()),('target99_cooling',opts(temp=48,end=.2)),('target99_warming',opts(temp=.2,end=48)),('target99_mixed',opts(temp=24,mix=256)),('resume_whole',opts(steps=256,seed=99032021,temp=16,mix=64)),('resume_first',opts(steps=73,seed=99032021,temp=16,mix=64)),('resume_second',opts(steps=183,seed=99032021,temp=16,mix=64,resume=BASE+'/resume_first/final.state'))]
    result.extend(('import_weight6_'+selector,opts(seed=99032060,temp=60,end=.1,imported=OLD,select=selector))for selector in['current','best'])
    result.extend([('import_resume_whole',opts(steps=256,seed=99032022,temp=24,end=.2,mix=64,resume=BASE+'/import_weight6_best/initial.state')),('import_resume_first',opts(steps=73,seed=99032022,temp=24,end=.2,mix=64,resume=BASE+'/import_weight6_best/initial.state')),('import_resume_second',opts(steps=183,seed=99032022,temp=24,end=.2,mix=64,resume=BASE+'/import_resume_first/final.state')),('rook_resume_whole',opts(fixture='rook9',steps=256,seed=99032060,temp=60)),('rook_resume_first',opts(fixture='rook9',steps=73,seed=99032060,temp=60)),('rook_resume_second',opts(fixture='rook9',steps=183,resume=BASE+'/rook_resume_first/final.state')),('import_weight6_rook',opts(fixture='rook9',steps=0,seed=99032060,temp=60,end=.1,imported=ROOK,select='best')),('import_weight6_pilot_best',opts(steps=0,seed=99032060,temp=60,end=.1,imported=PILOT,select='best')),('prism9_initial',opts(fixture='prism9',steps=0,temp=0)),('prism9_whole',opts(fixture='prism9',steps=256,seed=181,temp=0)),('prism9_first',opts(fixture='prism9',steps=73,seed=181,temp=0)),('prism9_second',opts(fixture='prism9',steps=183,resume=BASE+'/prism9_first/final.state')),('cube12_initial',opts(fixture='cube12_defect',steps=0,seed=149,temp=0)),('cube12_whole',opts(fixture='cube12_defect',steps=256,seed=149,temp=0)),('cube12_first',opts(fixture='cube12_defect',steps=73,seed=149,temp=0)),('cube12_second',opts(fixture='cube12_defect',steps=183,resume=BASE+'/cube12_first/final.state'))])
    for item in corruptions:
        kind=item['type'];entry=('reject_'+kind,opts(steps=1,imported=item['path'],select='best')if kind.startswith('import_')else opts(steps=1,resume=item['path']))
        if kind=='first_flag':result.append(('reject_import_selector',opts(steps=1,imported=OLD,select='wrong')))
        result.append(entry)
    return result


def run(args):
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Complete new57native finite controls/20992proposals; previous independent weighted full19456replay110.86sec;360outer320worker30reserve exact complete bitmask rescoring')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};checked=[];controls=[]
    def tick():C.need(not deadline.status()['stop_required']and deadline.status()['remaining_seconds']>30,'not completed within the allocated budget','DEADLINE')
    def path(name):
        p=(ROOT/name).resolve();C.need(p.is_relative_to(ROOT)and p.is_file(),'local repository artifact','IDENTITY');return p
    def pin(name,wanted=None,size=None):
        tick();p=path(name);digest=sha(p);C.need(wanted is None or wanted==digest,'hash '+name,'IDENTITY');C.need(size is None or size==p.stat().st_size,'size '+name,'IDENTITY');C.need(name not in pins or pins[name]==digest,'consistent hash','IDENTITY');pins[name]=digest;return p
    def read(name):return json.loads(path(name).read_bytes())
    try:
        pin(MANIFEST,MANIFEST_SHA);manifest=read(MANIFEST)
        C.need(manifest['schema']=='HYPERGRAPH_WEIGHT60_ANNEAL_CONTROLS_V2'and manifest['objective']==C.OBJECTIVE and manifest['lambda_weight']==60 and manifest['independent_approval']is False and manifest['target_resolution']is False,'exact unapproved finite manifest','RECEIPT')
        for name,digest in manifest['inputs_sha256'].items():pin(name,digest)
        for name,digest in SHARED.items():pin(name,digest)
        for p in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),Path(C.__file__),Path(C.__file__).with_name(Path(C.__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p.relative_to(ROOT).as_posix())
        for row in manifest['runs']:
            for name,item in row['artifacts'].items():pin(name,item['sha256'],item['bytes'])
        controls+=C.calibration(ROOT/BASE)
        if args.calibrate_only:
            save(out/'checked_controls.json',dict(controls=controls,complete_native_population_replayed=False))
            save(out/'summary.json',dict(status='INDEPENDENT_HYPERGRAPH_WEIGHT60_SCALAR_V1_CALIBRATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',verifier='/root/structural',inputs_sha256=pins,controls=len(controls),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),scope='Pre-science scalar/state/first-selection/move checker calibration only; no full57control approval or pilot endpoint approval.',target_resolution=False,elapsed_seconds=time.monotonic()-start));return
        C.need(args.calibration is not None,'exact pre-output calibration required','CALIBRATION');calpath=args.calibration.resolve();C.need(calpath.is_relative_to(ROOT),'local calibration','IDENTITY');pin(calpath.relative_to(ROOT).as_posix());cal=json.loads(calpath.read_bytes());C.need(cal['status']=='INDEPENDENT_HYPERGRAPH_WEIGHT60_SCALAR_V1_CALIBRATION_PASS'and all(cal['inputs_sha256'].get(k)==v for k,v in pins.items()if k in cal['inputs_sha256']),'same frozen checker/input calibration','CALIBRATION')
        build=read(BUILD);C.need(build['schema']=='HYPERGRAPH_WEIGHT60_ANNEAL_NATIVE_BUILD_V2'and build['binary_sha256']==pins[build['binary_path']]and build['source_cpp_sha256']==pins['acceleration/hypergraph_weight60_anneal_20261002_v2.cpp']and build['compiler_sha256']=='1353e9bdd29a7295c7226bf6c63abccce056d8cac31f112e5cdbecc3f28c2769','new source/binary/compiler exact','RECEIPT')
        pin(build['receipt'],build['receipt_sha256']);br=read(build['receipt']);C.need(br['command']==build['command']and br['actual_exit_code']==0 and br['reaped']is True,'actual new build receipt','RECEIPT')
        for channel in['stdout','stderr']:pin(br[channel],br[channel+'_sha256'])
        outer=manifest['supervision'];pin(outer['path'],outer['sha256']);sm=read(outer['path']);sspath=str(Path(outer['path']).parent/'summary.json').replace('\\','/');pin(sspath);ss=read(sspath)
        C.need(sm['invocation_id']==ss['invocation_id']==outer['invocation_id']and sm['seconds']==outer['outer_seconds']==300 and outer['producer_seconds']==270 and sm['cumulative_across_commands']is False and sm['automatic_retry']is False,'exact supported invocation','RECEIPT')
        C.need(ss['command_exit_code']==0 and ss['cleanup']['reaped']is True and ss['cleanup']['job_active_zero_observed']is True and ss['cleanup']['process_group_live_pids']==[]and ss['cleanup']['cleanup_errors']==[],'historical complete Linux process cleanup','RECEIPT')
        C.need(outer['guard_argv'][:2]==['/usr/bin/timeout','--signal=KILL']and outer['guard_argv'][3:5]==['/usr/bin/env','UV_PROJECT_ENVIRONMENT=build/native-budget-linux-venv']and outer['guard_argv'][5:9]==['/root/.local/bin/uv','run','--locked','--offline'],'Linux hard guard/locked runtime','RECEIPT')
        C.need([r['type']for r in manifest['corruptions']]==list(D),'all27frozen malformed input artifacts','POPULATION')
        for item in manifest['corruptions']:
            pin(item['path'],item['sha256']);parser=C.W.parse_state if item['type'].startswith('import_')else C.parse_state;controls.append(dict(raw_corruption=item['type'],diagnostic=C.U.reject(lambda:parser(path(item['path']).read_bytes()),D[item['type']][1])))
        C.need([(r['label'],r['options'])for r in manifest['runs']]==population(manifest['corruptions']),'all57independently reconstructed raw commands','POPULATION')
        successes={};traces={};rawtraces={};full=valid=accepted=paircases=checkpoint_count=overlap_valid=overlap_accepted=overlap_rejected=0;minimum_margin=None
        for row in tqdm(manifest['runs'],desc='complete weight60 V2 engineering replay',unit='call',mininterval=5):
            tick();label=row['label'];pin(row['receipt'],row['receipt_sha256']);receipt=read(row['receipt']);directory=ROOT/BASE/label;expected_exit=2 if label.startswith('reject_')else 0
            command=['/usr/bin/timeout','--foreground','--signal=TERM','--kill-after=5s','30.000000s','/usr/bin/prlimit','--as=2147483648:2147483648','--fsize=1073741824:1073741824','--core=0:0',linux(build['binary_path']),'--out',linux(BASE+'/'+label),'--seconds','25.000000',*row['options']]
            C.need(receipt['command']==command and receipt['cwd']==linux('')and receipt['actual_exit_code']==row['actual_exit_code']==expected_exit and receipt['expected_exit_code']==expected_exit and receipt['reaped']is True and receipt['process_group']==outer['group']and receipt['independent_approval']is False,'exact native command/outcome/group','RECEIPT')
            for channel in['stdout','stderr']:pin(receipt[channel],receipt[channel+'_sha256'])
            C.need({p.relative_to(ROOT).as_posix()for p in directory.iterdir()if p.is_file()}==set(row['artifacts']),'complete directory inventory','POPULATION')
            if expected_exit:
                diagnostic='import weight6 graph selector'if label=='reject_import_selector'else D[label[7:]][0]
                C.need(row['artifacts']=={}and path(receipt['stderr']).read_bytes()==(diagnostic+'\n').encode('ascii')and path(receipt['stdout']).read_bytes()==b'','strict diagnostic/empty stdout/no artifacts','CONTROL');continue
            options=parse_opts(row['options']);s=C.parse_state((directory/'initial.state').read_bytes());initial=copy.deepcopy(s)
            if '--resume'in options:C.need((directory/'initial.state').read_bytes()==repo_from_linux(options['--resume']).read_bytes(),'unchanged complete resume input bytes','RESUME')
            elif '--import-weight6'in options:C.import_initial(s,repo_from_linux(options['--import-weight6']).read_bytes(),options['--import-select'],options)
            else:
                C.config(s,options);C.need(s['current']==s['best']==C.initial(options['--fixture'])and s['rng']==C.U.seed_words(int(options['--seed']))and s['step']==s['admissible']==s['accepted']==s['best_updates']==0,'fresh exact labelled fixture/RNG/counters','INITIAL')
                expected=copy.deepcopy(s);expected['first']=None;C.capture(expected,0);C.need(expected==s,'fresh earliest initial lambda0 snapshot','INITIAL')
            checkpoints={}
            for p in directory.glob('checkpoint_*.state'):
                step=int(p.stem.split('_')[1]);C.need(step not in checkpoints,'unique checkpoint completed step','POPULATION');checkpoints[step]=C.parse_state(p.read_bytes())
            C.need(set(range(((s['step']//64)+1)*64,s['step']+int(options['--steps'])+1,64))<=set(checkpoints),'every scheduled64step checkpoint preserved','POPULATION')
            data=(directory/'moves.jsonl').read_bytes();records=[json.loads(line)for line in data.splitlines()];steps=int(options['--steps']);C.need(len(records)==steps,'every finite proposal logged','POPULATION')
            for record in records:
                tick();result,_=C.replay(s,record);full+=1;valid+=int(result['valid']);accepted+=int(result['accepted']);overlap_valid+=int(result['valid']and result['overlap']);overlap_accepted+=int(result['accepted']and result['overlap']);overlap_rejected+=int(result['valid']and result['overlap']and not result['accepted'])
                if result['margin']is not None:minimum_margin=result['margin']if minimum_margin is None else min(minimum_margin,result['margin'])
                if s['step']in checkpoints:C.need(s==checkpoints[s['step']],'complete intermediate raw checkpoint equality','CHECKPOINT');checkpoint_count+=1
            final=C.parse_state((directory/'final.state').read_bytes());C.need(s==final,'complete independently replayed final raw state','CHECKPOINT')
            for object_name,triples in[('current',s['current']),('best',s['best'])]:
                matrix=C.raw_matrix((directory/(object_name+'.adj')).read_bytes(),s['n']);C.matrix_matches(matrix,triples,s['n'],s['degree'])
                if C.score(triples,s['n'],s['degree'])[2]['weighted_energy']==0:
                    C.U.matrix_claim(matrix,s['n'],2*s['degree']);C.need(s['n']!=99,'target zero demands separate discovery review','RESOLUTION')
            C.selection(s,initial,options,json.loads((directory/'lambda0_selection.json').read_bytes()))
            if s['first']is not None:
                C.need(C.parse_state((directory/'first_lambda0.state').read_bytes())==C.first_state(s),'complete exactly resumable earliest snapshot','FIRST_SNAPSHOT');C.matrix_matches(C.raw_matrix((directory/'first_lambda0.adj').read_bytes(),s['n']),s['first']['current'],s['n'],s['degree'])
            else:C.need(not(directory/'first_lambda0.state').exists()and not(directory/'first_lambda0.adj').exists(),'absent selection has no first object','FIRST_COMPLETENESS')
            table=[json.loads(line)for line in(directory/'pair_costs.jsonl').read_bytes().splitlines()];C.need(table==C.pair_costs(),'all86exact weight60 category costs','PAIR');paircases+=len(table)
            result=json.loads((directory/'result.json').read_bytes());facts=dict(objective=C.OBJECTIVE,lambda_weight=60,n=s['n'],point_degree=s['degree'],triple_count=len(s['current']),starting_step=initial['step'],ending_step=s['step'],proposals_this_invocation=steps,admissible_total=s['admissible'],accepted_total=s['accepted'],best_updates_total=s['best_updates'],first_lambda0_found=s['first']is not None,first_lambda0_step=None if s['first']is None else s['first']['step'],stop_reason='REQUESTED_STEPS_COMPLETE',target_resolution=False,independent_approval=False)
            for prefix,state,best in[('initial',initial,False),('current',s,False),('best',s,True)]:
                for key in C.KEYS:facts[prefix+'_'+key]=state[('best_'if best else'')+key]
            C.need({k:v for k,v in result.items()if k!='elapsed_seconds'}==facts and 0<=result['elapsed_seconds']<=receipt['wall_seconds'],'every raw result field independently checked','RESULT')
            C.need(path(receipt['stderr']).read_bytes()==b''and path(receipt['stdout']).read_bytes()==f"NATIVE_RESULT_PRESERVED {s['n']} {s['weighted_energy']} {s['best_weighted_energy']}\n".encode('ascii'),'exact success stdout/no stderr','RECEIPT')
            successes[label]=dict(initial=initial,final=final);traces[label]=records;rawtraces[label]=data;checked.append(dict(label=label,full_proposals=steps,actual_saved_checkpoints=len(checkpoints),current_scores={k:s[k]for k in C.KEYS},best_scores={k:s['best_'+k]for k in C.KEYS},first_step=None if s['first']is None else s['first']['step'],receipt_sha256=row['receipt_sha256']))
        C.need(len(successes)==29 and full==20992 and paircases==2494,'complete29positive finite population/proposals/cost records','POPULATION')
        C.need(overlap_valid>0 and overlap_accepted>0 and overlap_rejected>0,'bothaccepted and rejected valid overlap proposals checked','CONTROL')
        for family in['resume','import_resume','rook_resume','prism9','cube12']:
            C.need(rawtraces[family+'_whole']==rawtraces[family+'_first']+rawtraces[family+'_second'],'complete whole/split raw trace identity','RESUME')
            for name in['final.state','first_lambda0.state','first_lambda0.adj']:
                left=ROOT/BASE/(family+'_whole')/name;right=ROOT/BASE/(family+'_second')/name
                C.need(left.exists()==right.exists()and(not left.exists()or left.read_bytes()==right.read_bytes()),'whole/split raw object bytes '+name,'RESUME')
        for family,em in[('prism9',0),('cube12',48)]:
            first=successes[family+'_whole']['final']['first'];C.need(first is not None and first['step']==1 and C.score(first['current'],9 if family=='prism9'else 12,2)[2]['mu_energy']==em,'known first overlap/disjoint exactcapture and partial distinction','CONTROL')
        for key in['delta','weighted_energy_after','lambda_energy_after','mu_energy_after','rng_after','accepted','lambda_weight','move_kernel','selected_points_exclusive','new_pairs_absent_after_old_removal']:
            bad=copy.deepcopy(traces['target99_greedy'][0]);bad[key]=[str(int(bad[key][0])^1),*bad[key][1:]]if key=='rng_after'else(not bad[key]if type(bad[key])is bool else'WRONG'if type(bad[key])is str else bad[key]+1)
            controls.append(dict(mutated_trace=key,diagnostic=C.U.reject(lambda:C.replay(copy.deepcopy(successes['target99_greedy']['initial']),bad),'REPLAY')))
        original=C.W.parse_state((ROOT/OLD).read_bytes());options=parse_opts(dict(population(manifest['corruptions']))['import_weight6_best'])
        for label,mutation in[('old_counters',lambda s:s.update(step=original['step'])),('wrong_source_graph',lambda s:s.update(current=copy.deepcopy(original['current']))),('old_rng',lambda s:s.update(rng=original['rng'][:]))]:
            bad=copy.deepcopy(successes['import_weight6_best']['initial']);mutation(bad);controls.append(dict(mutated_import=label,diagnostic=C.U.reject(lambda:C.import_initial(bad,(ROOT/OLD).read_bytes(),'best',options),'IMPORT')))
        controls.append(dict(wrong_selector=C.U.reject(lambda:C.import_initial(successes['import_weight6_best']['initial'],(ROOT/OLD).read_bytes(),'wrong',options),'IMPORT')))
        table=C.pair_costs();table[1]['delta_F']+=1;controls.append(dict(pair_cost=C.U.reject(lambda:C.need(table==C.pair_costs(),'completepair cost','PAIR'),'PAIR')))
        wrong=MANIFEST_SHA[:-1]+('0'if MANIFEST_SHA[-1]!='0'else'1');controls.append(dict(input_hash=C.U.reject(lambda:pin(MANIFEST,wrong),'IDENTITY')))
        save(out/'checked_controls.json',dict(runs=checked,corruption_controls=controls,full_proposals=full,admissible_full_rescored=valid,accepted_proposals=accepted,valid_overlap_proposals=overlap_valid,accepted_overlap_proposals=overlap_accepted,rejected_overlap_proposals=overlap_rejected,all_actual_saved_intermediate_checkpoints=checkpoint_count,pair_cost_records=paircases,minimum_acceptance_margin=minimum_margin))
        save(out/'summary.json',dict(status='INDEPENDENT_HYPERGRAPH_WEIGHT60_ANNEAL_V2_CONTROLS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),verifier='/root/structural',producer='/root/native_driver',inputs_sha256=pins,outputs_sha256={'checked_controls.json':sha(out/'checked_controls.json')},source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),producer_source_commit=manifest['source_commit'],command=[sys.executable,*sys.argv],cwd=str(ROOT),tool_versions=dict(python=platform.python_version(),platform=platform.platform()),native_calls_observed=57,new_native_calls=0,successful_calls_completely_replayed=29,strict_negative_calls_checked=28,full_proposals=full,all_saved_intermediate_checkpoints=checkpoint_count,pair_table_records=paircases,overlap_valid=overlap_valid,overlap_accepted=overlap_accepted,overlap_rejected=overlap_rejected,minimum_acceptance_margin=minimum_margin,objective=C.OBJECTIVE,lambda_weight=60,move_kernel=C.KERNEL,shared_components=SHARED,checking_method='Independent complete adjacency reconstruction/full pair-count/category scoring, raw57command population, every finite proposal/RNG/import/reset/checkpoint/matrix/first-selection; no native/producer imports.',scope='Frozen57native finite ENGINEERING cases only, including generic rook9/prism9/cube12 and target99 trajectories, five whole/split paths; no general ergodicity, performance, graph existence or target-wide exclusion.',limitations=['First selection earliest only established over complete finite traces; saved checkpoint alone has no earlier-history guarantee.','Producer finite fixture diagnosis/cubic catalogue not independently exhaustively reproduced by this gate.','V1failed25positive/no27negative receipts preserved; no old gate transfers.','Native compiler hash/receipt bound rather than independently rebuilt.','All graph/count/RNG values exact; heuristic exp/schedule with1e-12 tolerance/margin only.','Generic lambda0 includingcube12mu48 is not a target graph.'],target_resolution=False,overall_search_coverage='UNKNOWN; no validated denominator.',elapsed_seconds=time.monotonic()-start,deadline=deadline.status()))
    except Exception as error:save(out/'failure.json',dict(status='INDEPENDENT_CHECK_FAILED',error=repr(error),timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,completed_calls=checked,controls=controls,elapsed_seconds=time.monotonic()-start,target_resolution=False));raise


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--calibrate-only',action='store_true');ap.add_argument('--calibration',type=Path);run(ap.parse_args())
